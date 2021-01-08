import click

from openheat.config import config

openheat_data = {
    'controllers': {},
    'sensors': {},
}


def main():
    from openheat.controller import Controllers
    from openheat.sensor import Sensors

    controllers = Controllers(openheat_data)
    sensors = Sensors(openheat_data)
    sensors.start()
    controllers.start()


@click.group()
@click.option('--log-level', type=click.Choice(['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG']),
              default=config.log_level)
def cli(log_level):
    config.log_level = log_level


@cli.command()
def test_relay():
    import time

    from openheat.logger import log
    from openheat.gpio import GPIO

    gpio = GPIO()

    for controller in config.controllers:
        if 'on_off' not in controller['type']:
            log.debug(f"Controller {controller['name']} doesn't use ON-OFF relay. Skipping...")
            continue
        for out in ('LOW', 'HIGH'):
            log.info(f"Setting GPIO pin for {controller['name']} to {out}")
            gpio.output(controller['gpio_pin'], out)
            time.sleep(4 if out == 'LOW' else 1)


@cli.command()
@click.option('--location', default=config.openweather_settings['location'], show_default=True)
@click.option('--hours-from-now', default=0, help='Based on forecast data, compute weather index'
                                                  ' in the future time (hours offset).')
def weather_index(location, hours_from_now):
    import sys

    from openheat.logger import log
    from openheat.weather import Weather

    config.openweather_settings['location'] = location
    weather = Weather()

    try:
        weather.forecast_and_assess_weather_index(hours_from_now)
    except ValueError as e:
        log.error(str(e).rstrip('. ') + '. Exiting...')
        sys.exit(1)


@cli.command()
def run():
    main()


if __name__ == '__main__':
    cli()
