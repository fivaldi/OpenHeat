import importlib.util
import os
import threading

from openheat.config import config
from openheat.exceptions import ConfigError


class Sensors:
    def __init__(self, openheat_data):
        self.openheat_data = openheat_data
        self.sensors = []
        self._sensor_modules = {}

        for sensor_config in config.sensors:

            sensor_type = sensor_config['type']

            if sensor_type in self._sensor_modules:
                continue

            sensor_base_dir = os.path.dirname(os.path.abspath(__file__))
            sensor_module_name = 'openheat.sensor.' + sensor_type.replace('/', '.')
            sensor_module_file = os.path.join(sensor_base_dir, sensor_type + '.py')

            if not os.path.isfile(sensor_module_file):
                raise ConfigError(f"Unknown sensor type {sensor_type} or module file"
                                  f" {sensor_module_file} doesn't exist.")

            spec = importlib.util.spec_from_file_location(sensor_module_name, sensor_module_file)
            sensor_module = importlib.util.module_from_spec(spec)
            self._sensor_modules[sensor_type] = sensor_module
            spec.loader.exec_module(sensor_module)

    def start(self):
        sensor_counter = 1
        for sensor_config in config.sensors:

            sensor_type = sensor_config['type']

            def target(sensor_config, openheat_data):
                sensor_obj = self._sensor_modules[sensor_type]._sensor_class(sensor_config,
                                                                             openheat_data)
                sensor_obj.start()

            thread = threading.Thread(
                target=target,
                name='Sensor' + str(sensor_counter) + '-' + sensor_type.split('/')[-1],
                args=(sensor_config, self.openheat_data))
            thread.start()
            self.sensors.append(thread)

            sensor_counter += 1
