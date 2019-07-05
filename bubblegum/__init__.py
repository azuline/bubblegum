from pathlib import Path

from bubblegum.errors import BubblegumError

__version__ = '0.3.0'

BG_PATH = Path.home() / '.bubblegum'

try:
    BG_PATH.mkdir(0o755, exist_ok=True)
except FileNotFoundError:
    raise BubblegumError(
        'The user running bubblegum must have a home directory.'
    )
