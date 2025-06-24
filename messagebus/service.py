import time
import logging
import threading
import traceback
import requests
from django.conf import settings
from django.core.cache import cache
from telegram import Bot
from telegram.error import RetryAfter, TelegramError
from messagebus.models import Alert
from messagebus.utils import split_message

logger = logging.getLogger(__name__)

# Configurable settings
ALERT_CACHE_TIMEOUT = 600
SLACK_MAX_RETRIES = 3
SLACK_RETRY_WAIT = 5
TELEGRAM_MAX_RETRIES = 3

class SlackBus:
    def __init__(self, webhook_url=None):
        self.webhook_url = webhook_url or settings.SLACK_WEBHOOK_URL
        if not self.webhook_url:
            raise ValueError("Slack webhook URL is not configured")

    def slack_fallback(self, original_text, exception):
        """
        Sends a detailed error message to Slack when a Telegram alert fails.
        """
        try:
            tb = traceback.extract_tb(exception.__traceback__)[-1]
            trace = ''.join(traceback.format_exception(type(exception), exception, exception.__traceback__))
            message = (
                "*⚠️ Telegram Alert Failed*\n\n"
                f"*Message Attempted:*\n{original_text}\n\n"
                f"*Error:*\n• `{str(exception)}`\n"
                f"*Location:*\n• File: `{tb.filename}`\n• Line: `{tb.lineno}`\n• Function: `{tb.name}`\n\n"
                f"*Traceback:*\n```{trace}```"
            )
            return self._send(message)
        except Exception as e:
            logger.exception(f"SlackBus internal failure: {e}")
            return False

    def _send(self, message):
        """
        Sends a raw message to the Slack webhook with retry logic for rate limits.
        """
        retries = 0
        while retries < SLACK_MAX_RETRIES:
            try:
                response = requests.post(self.webhook_url, json={"text": message})
                if response.status_code == 200:
                    return True
                elif response.status_code == 429:
                    wait_time = int(response.headers.get('Retry-After', SLACK_RETRY_WAIT))
                    logger.warning(f"Slack rate limit hit, retrying in {wait_time}s")
                    time.sleep(wait_time)
                    retries += 1
                else:
                    logger.error(f"Slack responded with {response.status_code}: {response.text}")
                    return False
            except Exception as e:
                logger.exception(f"Error sending Slack message: {e}")
                return False
        logger.error(f"Failed to send Slack message after {SLACK_MAX_RETRIES} retries")
        return False

slack_bus = SlackBus()

class TelegramBus:
    def __init__(self):
        self._bot_cache = {}
        self._lock = threading.Lock()

    def _get_cached_bot(self, token):
        """
        Retrieve or create a Telegram Bot instance with thread-safe caching.
        """
        with self._lock:
            if token not in self._bot_cache:
                self._bot_cache[token] = Bot(token=token)
            return self._bot_cache[token]

    def _build_message(self, alert, msg):
        """
        Build the formatted message with alert title and optional tagged user.
        """
        base = f"<b>{alert.title}</b>\n\n{msg}"
        if alert.tagged_user:
            base += f"\n\n<b>Tagging:</b> {alert.tagged_user.value}"
        return base

    def _send_with_retry(self, bot, chat_id, text, reply_to_message_id, alert_name, max_retries):
        """
        Send a Telegram message with retry logic for rate limits.
        """
        retries = 0
        while retries < max_retries:
            try:
                return bot.send_message(
                    chat_id=chat_id,
                    text=text,
                    parse_mode='HTML',
                    reply_to_message_id=reply_to_message_id
                )
            except RetryAfter as e:
                wait_time = min(30, float(e.retry_after) * (2 ** retries))
                logger.warning(f"TG Rate limit hit for {alert_name}, retrying in {wait_time:.1f}s")
                time.sleep(wait_time)
                retries += 1
            except TelegramError as e:
                logger.exception(f"Failed to send TG alert {alert_name}: {e}")
                slack_bus.slack_fallback(text, e)
                return None

        error = TelegramError(f"Failed to send message after {max_retries} retries")
        logger.error(f"Failed to send alert {alert_name} after {max_retries} retries")
        slack_bus.slack_fallback(text, error)
        return None

    def send(self, alert_name, content, previous_message_id=None, max_retries=TELEGRAM_MAX_RETRIES):
        """
        Send an alert message via Telegram, using cached alert data and retry logic.
        """
        cache_key = f"alert:{alert_name}"
        alert = cache.get(cache_key)

        if alert is None:
            try:
                alert = Alert.objects.select_related('bot', 'tagged_user').get(name=alert_name)
                cache.set(cache_key, alert, timeout=ALERT_CACHE_TIMEOUT)
            except Alert.DoesNotExist:
                logger.error(f"Alert with name '{alert_name}' not found")
                slack_bus.slack_fallback(
                    f"Alert '{alert_name}' triggered, but does not exist in DB",
                    Exception("Alert not found")
                )
                return None

        messages = split_message(content, max_length=3900)
        bot = self._get_cached_bot(alert.bot.token)

        for msg in messages:
            full_message = self._build_message(alert, msg)
            result = self._send_with_retry(
                bot=bot,
                chat_id=alert.chat_id,
                text=full_message,
                reply_to_message_id=previous_message_id,
                alert_name=alert_name,
                max_retries=max_retries
            )
            previous_message_id = result.message_id if result else None

        return previous_message_id

telegram_bus = TelegramBus()