"""
ASGI config for GHOST project.
Exposes the ASGI application with Django Channels for WebSocket support.
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ghost_project.settings')
django.setup()

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from ghost_app.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": URLRouter(websocket_urlpatterns),
})
