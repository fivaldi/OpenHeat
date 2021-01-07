import time

from openheat.logger import log


class OnOff:
    def __init__(self, config, openheat_data):
        self.config = config
        self.openheat_data = openheat_data

    def start(self):
        while True:
            log.info(self.config)
            time.sleep(600)


_controller_class = OnOff
