from pathlib import Path

from appdirs import user_data_dir

from bubblegum.errors import BubblegumError

__version__ = '0.4.1'

BG_PATH = Path(user_data_dir('bubblegum', 'dazzler'))

try:
    BG_PATH.mkdir(0o700, exist_ok=True)
except FileNotFoundError:
    raise BubblegumError(
        'The user running bubblegum must have a data directory.'
    )
