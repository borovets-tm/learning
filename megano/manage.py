#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    if os.path.isfile(os.path.join(os.path.dirname(__file__), 'megano', 'local_settings.py')):
        # Если есть local_settings.py — используем его
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "megano.local_settings")
    else:
        # Если нет — используем стандартные настройки
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "megano.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
