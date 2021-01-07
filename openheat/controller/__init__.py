import importlib.util
import os
import threading

from openheat.config import config
from openheat.exceptions import ConfigError


class Controllers:
    def __init__(self, openheat_data):
        self.openheat_data = openheat_data
        self.controllers = []
        self._controller_modules = {}

        for controller_config in config.controllers:

            controller_type = controller_config['type']

            if controller_type in self._controller_modules:
                continue

            controller_base_dir = os.path.dirname(os.path.abspath(__file__))
            controller_module_name = 'openheat.controller.' + controller_type.replace('/', '.')
            controller_module_file = os.path.join(controller_base_dir, controller_type + '.py')

            if not os.path.isfile(controller_module_file):
                raise ConfigError(f"Unknown controller type {controller_type} or module file"
                                  f" {controller_module_file} doesn't exist.")

            spec = importlib.util.spec_from_file_location(controller_module_name,
                                                          controller_module_file)
            controller_module = importlib.util.module_from_spec(spec)
            self._controller_modules[controller_type] = controller_module
            spec.loader.exec_module(controller_module)

    def start(self):
        controller_counter = 1
        for controller_config in config.controllers:

            controller_type = controller_config['type']

            def target(controller_config, openheat_data):
                controller_obj = self._controller_modules[controller_type]._controller_class(
                    controller_config, openheat_data)
                controller_obj.start()

            thread = threading.Thread(
                target=target,
                name='Ctrl' + str(controller_counter) + '-' + controller_type.split('/')[-1],
                args=(controller_config, self.openheat_data))
            thread.start()
            self.controllers.append(thread)

            controller_counter += 1
