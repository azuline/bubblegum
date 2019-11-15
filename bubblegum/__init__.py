from pathlib import Path

from appdirs import user_data_dir

from bubblegum.errors import BubblegumError

__version__ = '0.5.0'

BG_PATH = Path(user_data_dir('bubblegum', 'azuline'))

try:
    BG_PATH.mkdir(mode=0o700, parents=True, exist_ok=True)
except FileNotFoundError:
    raise BubblegumError(
        'The user running bubblegum must have a data directory.'
    )
