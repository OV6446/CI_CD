#!/usr/bin/env python
"""Точка входа: миграции и запуск сервера Django."""
import os
import sys


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

    from django.core.management import execute_from_command_line

    if len(sys.argv) > 1:
        execute_from_command_line(['manage.py', *sys.argv[1:]])
        return

    execute_from_command_line(['manage.py', 'migrate', '--noinput'])
    execute_from_command_line(['manage.py', 'runserver', '0.0.0.0:8000'])


if __name__ == '__main__':
    main()
