import json

from bubblegum import BG_PATH
from bubblegum.errors import BubblegumError

CONFIG_FILE = BG_PATH / 'config.json'

CONFIG_TEMPLATE = {
    'default_host': 'vgy.me',
    'copy_to_clipboard': False,
    'imgur_client_id': None,
    'vgyme_userkey': None,
    'max_workers': 4,
    'ua_override': None,
    'profiles': [],
}


class Config:
    def __init__(self):
        if not CONFIG_FILE.exists():
            self.write_default_config_file()
        self.config = self.load_config_file()
        self.update_config()

    def __getattr__(self, name):
        try:
            return self.config[name]
        except KeyError:
            try:
                return CONFIG_TEMPLATE[name]
            except KeyError:
                try:
                    return super().__getattr__(name)
                except AttributeError:
                    return None

    def load_config_file(self):
        with CONFIG_FILE.open('r') as f:
            try:
                return json.load(f)
            except json.decoder.JSONDecodeError:
                raise BubblegumError('Config file is not valid JSON.')

    def write_default_config_file(self):
        with CONFIG_FILE.open('w') as f:
            json.dump(CONFIG_TEMPLATE, f, indent=4, separators=(',', ': '))

    def update_config(self):
        new_config = {**CONFIG_TEMPLATE, **self.config}
        if new_config != self.config:
            self.config = new_config
            with CONFIG_FILE.open('w') as f:
                json.dump(self.config, f, indent=4, separators=(',', ': '))


conf = Config()
