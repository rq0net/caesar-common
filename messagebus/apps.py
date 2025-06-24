from django.apps import AppConfig

class MessageBusConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'messagebus'

    def ready(self):
        """Import signals to register them during app initialization."""
        import messagebus.signals