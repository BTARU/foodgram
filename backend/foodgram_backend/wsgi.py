"""WSGI конфигурация для проекта foodgram_backend."""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodgram_backend.settings')

application = get_wsgi_application()
