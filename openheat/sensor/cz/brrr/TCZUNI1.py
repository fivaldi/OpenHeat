from datetime import datetime

import requests

from openheat.logger import log
from openheat.sensor import GenericSensor


class TCZUNI1(GenericSensor):
    def _store_temperature_to_data(self):
        try:
            r = requests.get(self.config['url'])
            self.openheat_data['sensors'][self.config['name']] = (datetime.now(), r.json())
        except requests.exceptions.RequestException:
            log.exception(f"Couldn't get data from sensor {self.config['name']}.")


_sensor_class = TCZUNI1
