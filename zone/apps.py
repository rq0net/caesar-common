from django.apps import AppConfig

class ZoneConfig(AppConfig):
    name = 'zone'

    def ready(self):
        import common.rest.signals.receivers