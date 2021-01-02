import logging
import time

import click
from systemd.journal import JournalHandler
from w1thermsensor import W1ThermSensor

log = logging.getLogger('openheat')
log.addHandler(JournalHandler())
log.setLevel(logging.INFO)


def main():
    sensor = W1ThermSensor()
    while True:
        log.info(sensor.get_temperature())
        time.sleep(60)


@click.group()
def cli():
    pass


@cli.command()
def run():
    main()


if __name__ == '__main__':
    cli()
