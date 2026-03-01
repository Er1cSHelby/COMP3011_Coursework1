"""
WSGI config for pokevault project.
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pokevault.settings')
application = get_wsgi_application()
