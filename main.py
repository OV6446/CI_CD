#!/usr/bin/env python
"""Точка входа: миграции, статика и Gunicorn."""
import os
import sys


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

    from django.core.management import execute_from_command_line

    if len(sys.argv) > 1:
        execute_from_command_line(['manage.py', *sys.argv[1:]])
        return

    execute_from_command_line(['manage.py', 'migrate', '--noinput'])
    execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])

    os.execvp(
        'gunicorn',
        [
            'gunicorn',
            'myproject.wsgi:application',
            '--bind',
            '0.0.0.0:8000',
            '--workers',
            '2',
            '--timeout',
            '120',
        ],
    )


if __name__ == '__main__':
    main()
