import warnings

import RPi.GPIO

from openheat.config import config
from openheat.logger import log

warnings.filterwarnings('ignore', message='This channel is already in use, continuing anyway.')


class GPIO:
    def __init__(self):
        RPi.GPIO.setmode(RPi.GPIO.BCM)
        for pin in [c['gpio_pin'] for c in config.controllers]:
            RPi.GPIO.setup(pin, RPi.GPIO.OUT)

    def output(self, pin, out):
        if out not in ('LOW', 'HIGH'):
            log.exception(f"Not allowed output {out} for GPIO pin {pin}.")
            return
        RPi.GPIO.output(pin, getattr(RPi.GPIO, out))
        return True
