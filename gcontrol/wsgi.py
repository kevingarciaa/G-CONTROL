"""
WSGI config for GControl project.
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gcontrol.settings')
application = get_wsgi_application()
