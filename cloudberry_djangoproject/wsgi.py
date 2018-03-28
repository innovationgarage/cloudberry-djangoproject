"""
WSGI config for cloudberry_djangoproject project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/howto/deployment/wsgi/
"""

import os, sys

from django.core.wsgi import get_wsgi_application

sys.path[0:0] = [os.path.dirname(os.path.dirname(os.path.abspath(__file__)))]

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cloudberry_djangoproject.settings")

application = get_wsgi_application()
