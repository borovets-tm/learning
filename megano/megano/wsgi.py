"""
WSGI config for megano project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/wsgi/
"""

import os
from pathlib import Path

from django.core.wsgi import get_wsgi_application

"""Run administrative tasks."""
if os.path.isfile(os.path.join(Path(__file__).resolve().parent.parent.parent, 'local_settings.py')):
	# Если рядом с manage.py лежит local_settings.py — используем его
	os.environ.setdefault("DJANGO_SETTINGS_MODULE", "local_settings")
else:
	# Если нет — используем стандартные настройки без секретов
	os.environ.setdefault("DJANGO_SETTINGS_MODULE", "megano.settings.production")

application = get_wsgi_application()
