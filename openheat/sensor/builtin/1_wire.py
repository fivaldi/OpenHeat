from datetime import datetime

from w1thermsensor import W1ThermSensor

from openheat.sensor import GenericSensor


class OneWire(GenericSensor):
    def __init__(self, config, openheat_data):
        super().__init__(config, openheat_data)
        self.sensor = W1ThermSensor()

    def _store_data(self):
        self.openheat_data['sensors'][self.config['name']] = (datetime.now(),
                                                              self.sensor.get_temperature())


_sensor_class = OneWire
