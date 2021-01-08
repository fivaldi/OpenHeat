import sched
import time
from datetime import datetime, timedelta

from w1thermsensor import W1ThermSensor

from openheat.logger import log


class OneWire:
    def __init__(self, config, openheat_data):
        self.config = config
        self.openheat_data = openheat_data
        self.scheduler = sched.scheduler(time.time, time.sleep)
        self.sensor = W1ThermSensor()

    def _store_temperature_to_data(self):
        self.openheat_data['sensors'][self.config['name']] = (datetime.now(),
                                                              self.sensor.get_temperature())

    def start(self):
        self.scheduler.enter(0, 1, self._store_temperature_to_data)
        self.scheduler.run(blocking=True)
        while True:
            self.scheduler.enter(timedelta(self.config['interval']).total_seconds(), 1,
                                 self._store_temperature_to_data)
            log.info(self.openheat_data)


_sensor_class = OneWire
