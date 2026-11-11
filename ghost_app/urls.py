"""
GHOST App URL Configuration
Defines all URL patterns matching the original FastAPI routes.
"""

from django.urls import path
from ghost_app import views

urlpatterns = [
    # Page routes
    path('', views.root, name='root'),
    path('health', views.health_check, name='health_check'),
    path('alpha', views.alpha_command_ui, name='alpha_command'),
    path('dashboard', views.dashboard_ui, name='dashboard'),
    path('voice', views.voice_assistant_ui, name='voice_assistant'),

    # API routes
    path('api/telemetry', views.get_telemetry, name='api_telemetry'),
    path('api/command', views.execute_command, name='api_command'),
    path('api/missions', views.list_missions, name='api_missions'),
    path('api/missions/authorize', views.authorize_level3, name='api_authorize'),
    path('api/missions/<str:mission_id>', views.get_mission_detail, name='api_mission_detail'),
    path('api/mobile/register', views.register_mobile, name='api_mobile_register'),
    path('api/mobile/notification', views.receive_notification, name='api_mobile_notification'),
    path('api/security/sweep', views.run_security_sweep, name='api_security_sweep'),
    path('api/tts', views.text_to_speech_endpoint, name='api_tts'),
]
