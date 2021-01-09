import traceback
from datetime import datetime

import requests

from openheat.logger import log
from openheat.sensor import GenericSensor


class TCZUNI1(GenericSensor):
    def _store_data(self):
        try:
            r = requests.get(self.config['url'], timeout=self.timeout)
            self.openheat_data['sensors'][self.config['name']] = (datetime.now(), r.json())
        except requests.exceptions.RequestException as e:
            exceptions = '\n'.join([t.rstrip('\n')
                                    for t in traceback.format_exception_only(type(e), e)])
            log.error(f"Couldn't get data from sensor {self.config['name']}.\n%s", exceptions)


_sensor_class = TCZUNI1
