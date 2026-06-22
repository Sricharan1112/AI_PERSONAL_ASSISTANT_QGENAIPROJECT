"""
WSGI config for the core project.
Used by production WSGI servers (e.g. gunicorn) to serve Django.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

application = get_wsgi_application()
