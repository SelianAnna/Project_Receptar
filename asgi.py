import os
from django.core.asgi import get_asgi_application

# Plochá štruktúra
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
application = get_asgi_application()