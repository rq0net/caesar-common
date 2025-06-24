from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Alert, TelegramBot
from .service import telegram_bus
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Alert)
def update_alert_cache(sender, instance, **kwargs):
    """Update cache for an Alert instance."""
    try:
        key = f"alert:{instance.name}"
        cache.set(key, instance)
    except Exception as e:
        logger.exception(f"Failed to update cache for alert {instance.name}: {e}")

@receiver(post_delete, sender=Alert)
def delete_alert_cache(sender, instance, **kwargs):
    """Delete cache for an Alert instance."""
    try:
        key = f"alert:{instance.name}"
        cache.delete(key)
    except Exception as e:
        logger.exception(f"Failed to delete cache for alert {instance.name}: {e}")

@receiver(post_save, sender=TelegramBot)
def update_bot_related_alerts_cache(sender, instance, **kwargs):
    """Update cache for all Alerts related to a TelegramBot."""
    try:
        alerts = Alert.objects.filter(bot=instance)
        cache.set_many({f"alert:{alert.name}": alert for alert in alerts})
        with telegram_bus._lock:
            telegram_bus._bot_cache.pop(instance.token, None)
    except Exception as e:
        logger.exception(f"Failed to update cache for bot {instance.name}: {e}")

@receiver(post_delete, sender=TelegramBot)
def delete_bot_related_alerts_cache(sender, instance, **kwargs):
    """Delete cache for all Alerts related to a TelegramBot."""
    try:
        alerts = Alert.objects.filter(bot=instance)
        cache.delete_many([f"alert:{alert.name}" for alert in alerts])
        with telegram_bus._lock:
            telegram_bus._bot_cache.pop(instance.token, None)
    except Exception as e:
        logger.exception(f"Failed to delete cache for bot {instance.name}: {e}")