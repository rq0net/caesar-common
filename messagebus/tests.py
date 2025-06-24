from django.test import TestCase
from django.core.cache import cache
from unittest.mock import patch, Mock
from messagebus.models import TelegramBot, Alert
from messagebus.service import SlackBus, telegram_bus
from messagebus.utils import split_message
from messagebus.alert_names import AlertName

class MessageBusTests(TestCase):
    def setUp(self):
        self.bot = TelegramBot.objects.create(name="TestBot", token="test_token")
        self.alert = Alert.objects.create(
            bot=self.bot,
            name=AlertName.CERT_ISSUE_SUCCESS.value,
            title="Test Alert",
            chat_id="-123456789"
        )
        cache.clear()

    @patch('messagebus.service.Bot')
    def test_telegram_bus_send_success(self, mock_bot):
        mock_bot_instance = Mock()
        mock_bot_instance.send_message.return_value = Mock(message_id=123)
        mock_bot.return_value = mock_bot_instance

        telegram_bus._bot_cache = {}
        result = telegram_bus.send(AlertName.CERT_ISSUE_SUCCESS.value, "Test message")
        self.assertEqual(result, 123)
        mock_bot_instance.send_message.assert_called_once()

    @patch('messagebus.service.requests.post')
    def test_slack_bus_send_success(self, mock_post):
        mock_post.return_value = Mock(status_code=200)
        slack_bus = SlackBus(webhook_url="https://example.com")
        result = slack_bus._send("Test message")
        self.assertTrue(result)
        mock_post.assert_called_once_with("https://example.com", json={"text": "Test message"})

    @patch('messagebus.service.requests.post')
    def test_slack_bus_rate_limit_retry(self, mock_post):
        mock_post.side_effect = [
            Mock(status_code=429, headers={'Retry-After': '1'}),
            Mock(status_code=200)
        ]
        slack_bus = SlackBus(webhook_url="https://example.com")
        result = slack_bus._send("Test message")
        self.assertTrue(result)
        self.assertEqual(mock_post.call_count, 2)

    def test_split_message_single(self):
        message = "Short message"
        result = split_message(message, max_length=3900)
        self.assertEqual(result, ["Short message"])

    def test_split_message_multiple(self):
        message = "Line1\n" + "a" * 3900 + "\nLine2"
        result = split_message(message, max_length=3900)
        self.assertEqual(len(result), 2)
        self.assertTrue(result[0].startswith("[1/2]\nLine1"))
        self.assertTrue(result[1].startswith("[2/2]\nLine2"))

    def test_alert_cache_signal(self):
        cache_key = f"alert:{self.alert.name}"
        self.assertIsNone(cache.get(cache_key))
        self.alert.save()
        self.assertEqual(cache.get(cache_key), self.alert)

    def test_bot_cache_invalidation(self):
        telegram_bus._bot_cache[self.bot.token] = Mock()
        self.bot.save()
        self.assertNotIn(self.bot.token, telegram_bus._bot_cache)