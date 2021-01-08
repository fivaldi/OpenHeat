import pytest

from openheat.exceptions import ConfigError


def test_load_config():
    from openheat.config import config

    assert config


def test_load_controllers():
    from openheat.controller import Controllers

    dummy_openheat_data = {}
    controllers = Controllers(dummy_openheat_data)
    assert controllers


def test_load_sensors():
    from openheat.sensor import Sensors

    dummy_openheat_data = {}
    try:
        sensors = Sensors(dummy_openheat_data)
        assert sensors
    except Exception as e:
        if 'Cannot load w1 therm kernel modules' in e.args:
            pytest.xfail("1-Wire kernel modules not loaded. Expected for hardware-less tests.")
        else:
            raise


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
