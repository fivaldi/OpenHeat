import pytest

from openheat.exceptions import ConfigError


def test_load_config():
    from openheat.config import config

    assert config


def test_load_sensors():
    from openheat.sensor import Sensors

    dummy_openheat_data = {}
    sensors = Sensors(dummy_openheat_data)
    assert sensors


def test_load_weather(caplog):
    from openheat.weather import Weather

    try:
        weather = Weather()
        assert weather
    except ConfigError:
        if 'OpenWeather responded with HTTP status code 401.' in caplog.text:
            pytest.xfail("Check api_key in openweather_settings of your configuration.")
        else:
            raise
