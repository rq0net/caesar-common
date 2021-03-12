"""
ASGI entrypoint. Configures Django and then runs the application
defined in the ASGI_APPLICATION setting.
"""

import os
from django.core.asgi import get_asgi_application

# Fetch Django ASGI application early to ensure AppRegistry is populated
# before importing consumers and AuthMiddlewareStack that may import ORM
# models.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "common.config.common")
application = get_asgi_application()
