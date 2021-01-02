import sys
import time

import RPi.GPIO as GPIO
import click
from w1thermsensor import W1ThermSensor

from openheat.config import openweather_settings, relay_to_gpio_pin
from openheat.logger import log
from openheat.weather import forecast_and_assess_weather_index


def gpio_setup():
    GPIO.setmode(GPIO.BCM)
    for _, pin in relay_to_gpio_pin.items():
        GPIO.setup(pin, GPIO.OUT)


def boiler_temp_out():
    sensor = W1ThermSensor()
    while True:
        log.info(sensor.get_temperature())
        time.sleep(60)


def main():
    pass


@click.group()
def cli():
    pass


@cli.command()
def test_relay():
    gpio_setup()
    for _, pin in relay_to_gpio_pin.items():
        GPIO.output(pin, GPIO.LOW)
        time.sleep(4)
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(1)


@cli.command()
@click.option('--location', default=openweather_settings['location'], show_default=True)
@click.option('--hours-from-now', default=0, help='Based on forecast data, compute weather index'
                                                  ' in the future time (hours offset).')
def weather_index(location, hours_from_now):
    openweather_settings['location'] = location
    try:
        forecast_and_assess_weather_index(hours_from_now)
    except ValueError as e:
        log.error(str(e).rstrip('. ') + '. Exiting...')
        sys.exit(1)


@cli.command()
def run():
    main()


if __name__ == '__main__':
    cli()
