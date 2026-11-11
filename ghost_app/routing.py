"""
GHOST Django Channels WebSocket URL Routing
"""

from django.urls import re_path
from ghost_app import consumers

websocket_urlpatterns = [
    re_path(r'^ws$', consumers.GhostConsumer.as_asgi()),
    re_path(r'^ws/$', consumers.GhostConsumer.as_asgi()),
]
