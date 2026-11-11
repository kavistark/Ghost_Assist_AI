import sys
import os

# Project root directory
project_home = '/home/GhostAssist/Ghost_Assist_AI'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# WSGI bridge for FastAPI
from a2wsgi import ASGIMiddleware
from main import app as asgi_app

application = ASGIMiddleware(asgi_app)

