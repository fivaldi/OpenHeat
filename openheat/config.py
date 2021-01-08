import os
import re
import yaml
from textwrap import indent

from openheat.exceptions import ConfigError

raw_config = None
system_wide_config = '/etc/openheat/config.yaml'
local_configs = [
    '~/.openheat/config.yaml',
    '~/openheat/config.yaml',
]


class Config:
    def load_from_file(self):
        if self.custom_config:
            try:
                with open(self.custom_config) as f:
                    self.raw_config = yaml.safe_load(f)
            except FileNotFoundError:
                pass

        try:
            with open(system_wide_config) as f:
                self.raw_config = yaml.safe_load(f)
        except FileNotFoundError:
            pass

        for local_config in local_configs:
            try:
                with open(os.path.expanduser(local_config)) as f:
                    self.raw_config = yaml.safe_load(f)
            except FileNotFoundError:
                pass

    def __init__(self, custom_config=None):
        self.custom_config = os.environ.get('OPENHEAT_CONFIG', custom_config)
        self.raw_config = None
        self.load_from_file()

        if not self.raw_config:
            raise ConfigError(
                "No configuration found. Paths checked:\n"
                + indent(system_wide_config + '\n' + '\n'.join(local_configs), 4 * ' '))

        for k, v in self.raw_config.items():
            if k.startswith('_') or k.endswith('_'):
                # Underscore prefixed/suffixed keys are not allowed -> ignoring...
                continue

            if k in ('controllers', 'sensors'):
                registered_names = []
                for item in self.raw_config[k]:
                    if item['name'] in registered_names:
                        raise ConfigError(f"Already registered name {item['name']} while scanning"
                                          f" {k} configuration key. Names must be unique.")
                    registered_names.append(item['name'])

            if k == 'weather_index_to_program':
                self.weather_index_to_program = dict()
                for index, program in self.raw_config[k].items():
                    if isinstance(index, str):
                        interval = re.search(r'\((\d+\.?\d*), (\d+\.?\d*)\)', index)
                        if not interval:
                            raise ConfigError(f"Not recognized index interval {index}"
                                              f" while scanning {k} configuration key.")
                        self.weather_index_to_program[(float(interval.group(1)),
                                                       float(interval.group(2)))] = program
                    else:
                        self.weather_index_to_program[float(index)] = program

            else:
                setattr(self, k, v)


config = Config()
