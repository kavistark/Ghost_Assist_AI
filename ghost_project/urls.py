"""
GHOST URL Configuration
Root URL config — includes all ghost_app URL patterns.
"""

from django.urls import path, include

urlpatterns = [
    path('', include('ghost_app.urls')),
]
