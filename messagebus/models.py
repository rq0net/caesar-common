from django.db import models
from django.core.exceptions import ValidationError
import re
from common.rest.models import TGUser
from messagebus.alert_names import AlertName

def validate_chat_id(value):
    """Validate that the chat_id is a valid Telegram chat ID (numeric, optionally negative)."""
    if not re.match(r'^-?\d+$', value):
        raise ValidationError('Invalid Telegram chat ID format')

def validate_alert_name(value):
    """Validate that the alert name is a valid AlertName enum value."""
    if value not in [name.value for name in AlertName]:
        raise ValidationError(f"Invalid alert name: {value}")

class TelegramBot(models.Model):
    class Meta:
        app_label = 'messagebus'
        verbose_name = "Telegram Bot"
        verbose_name_plural = "Telegram Bots"

    name = models.CharField(max_length=50, unique=True)
    token = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Alert(models.Model):
    class Meta:
        app_label = 'messagebus'
        verbose_name = "Alert"
        verbose_name_plural = "Alerts"
        indexes = [models.Index(fields=['name'])]

    bot = models.ForeignKey(TelegramBot, on_delete=models.PROTECT)
    name = models.CharField(max_length=50, unique=True, validators=[validate_alert_name])
    title = models.CharField(max_length=200)
    chat_id = models.CharField(max_length=100, validators=[validate_chat_id])
    tagged_user = models.ForeignKey(TGUser, on_delete=models.PROTECT, null=True, blank=True)

    def __str__(self):
        return self.name