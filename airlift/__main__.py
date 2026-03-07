"""
Package execution entrypoint for Airlift.

This module enables `python -m airlift` execution and delegates to the CLI.
"""

from airlift.cli import main
from multiprocessing import freeze_support
if __name__ == "__main__":
    freeze_support()
    main()
