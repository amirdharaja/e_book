import os
import sys

from dotenv import load_dotenv
from pathlib import Path


env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

ADMINS = os.getenv('ADMINS').split(', ')
USER = os.getenv('USER')
MODE = os.getenv('MODE')

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'e_book.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

if USER in ADMINS:
    print('************************************')
    print('\n\t{}\n'.format(MODE))
    print('************************************')

    if __name__ == '__main__':
        main()

else:
    print('************************************')
    print("\n\tUnauthorized access\n")
    print('************************************')