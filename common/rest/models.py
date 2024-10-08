from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.db import models


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class TGUser(models.Model):
    class Meta:
        db_table = 'common_tguser'

    name = models.TextField(unique=True, blank=True, null=True)
    value = models.TextField(default="", null=False)

    def __str__(self):
        return str(self.name)