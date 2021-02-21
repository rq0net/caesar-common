#!/usr/bin/env python
import os
import sys
from dotenv import load_dotenv
from pathlib import Path  # python3 only

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'common.config.common')

    env_path = Path('..') / '.env'
    load_dotenv(dotenv_path=env_path)

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
