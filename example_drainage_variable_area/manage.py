#!/usr/bin/env python
"""Cacao command-line utility for administrative tasks."""
#import os
import sys

# workaround for testing
from context import cacao


def main():
    """Run administrative tasks."""
    #os.environ.setdefault('CACAO_MODEL', 'smartCity.settings')
    try:
        from cacao.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Cacao. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()