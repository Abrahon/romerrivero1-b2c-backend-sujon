"""
WSGI config for romerrivero1 project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

# romerrivero1/wsgi.py

# romerrivero1/wsgi.py

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'romerrivero1.settings')

application = get_wsgi_application()

