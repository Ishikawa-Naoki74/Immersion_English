"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
# TODO 開発環境は、manage.pyに設定して、本番環境はここ、ステージング環境はどうするか？
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

application = get_wsgi_application()
