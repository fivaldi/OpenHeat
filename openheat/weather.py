import sys
from datetime import datetime
from statistics import mean

import requests

from openheat.config import (
    openweather_settings, openweather_basic_api_url, openweather_onecall_api_url,
    weather_hourly_forecast_hrs, weather_weight_current, weather_weight_hourly_forecast,
    weather_max_avg_temp, weather_clouds_few, weather_wind_light, weather_min_avg_temp,
    weather_negative_temp_index_factor, weather_humidity_base, weather_wind_max)
from openheat.logger import log
from openheat.utils import clamp

weather_forecast_data = {}


def init_weather_lon_lat():
    params = {'q': openweather_settings['location'],
              'appid': openweather_settings['api_key'],
              'units': 'metric'}

    lon_lat = None
    try:
        data = requests.get(openweather_basic_api_url, params=params)
        data.raise_for_status()
        lon_lat = (data.json()['coord']['lon'], data.json()['coord']['lat'])
        log.debug(f"OpenWeather data: {data.json()}")
    except requests.exceptions.HTTPError:
        msg = f"OpenWeather responded with HTTP status code {data.status_code}."
        if data.status_code == 404:
            msg += f" Maybe unknown location '{openweather_settings['location']}'?"
        log.error(msg)
    except requests.exceptions.RequestException:
        log.exception("Couldn't get data from OpenWeather.")

    if not lon_lat:
        log.error("Couldn't init weather location. Exiting...")
        sys.exit(1)
    openweather_settings['lon_lat'] = lon_lat


def get_weather(hourly_forecast=False):
    if not openweather_settings.get('lon_lat'):
        init_weather_lon_lat()

    excludes = 'minutely,daily,alerts' if hourly_forecast else 'minutely,hourly,daily,alerts'

    params = {'appid': openweather_settings['api_key'],
              'lon': openweather_settings['lon_lat'][0],
              'lat': openweather_settings['lon_lat'][1],
              'exclude': excludes,
              'units': 'metric'}
    weather = {}
    try:
        data = requests.get(openweather_onecall_api_url, params=params)
        data.raise_for_status()
        weather = data.json()
        log.debug(f"OpenWeather data: {data.json()}")
    except requests.exceptions.RequestException:
        log.exception("Couldn't get data from OpenWeather.")

    return weather


def forecast_and_assess_weather_index(hours_from_now=0):
    weather = get_weather(hourly_forecast=True)
    if not weather:
        return

    current = weather_forecast_data['current'] = weather['current']
    hourly = weather_forecast_data['hourly'] = weather['hourly']

    if hours_from_now + weather_hourly_forecast_hrs > len(hourly):
        raise ValueError("Can't go beyond forecast data. Please lower the hours offset.")

    if hours_from_now >= 1:
        current = weather_forecast_data['current'] = weather['hourly'][hours_from_now - 1]
        hourly = weather_forecast_data['hourly'] = weather['hourly'][hours_from_now:]

    averages = {}

    for value in 'temp', 'humidity', 'clouds', 'wind_speed':
        averages[value] = (
            (weather_weight_current * current[value]
             + weather_weight_hourly_forecast * mean([v[value] for v  # noqa: W503
                                                     in hourly[0:weather_hourly_forecast_hrs]]))
            / (weather_weight_current + weather_weight_hourly_forecast))  # noqa: W503

    weather_index_highest = 4
    weather_forecast_data['as_of_datetime'] = datetime.now()
    if (averages['temp'] >= weather_max_avg_temp and averages['clouds'] <= weather_clouds_few
            and averages['wind_speed'] <= weather_wind_light):  # noqa: W503
        weather_index = weather_index_highest
    else:
        temp_index = ((averages['temp'] - weather_max_avg_temp)
                      / (weather_min_avg_temp - weather_max_avg_temp))  # noqa: W503
        if temp_index < 0:
            temp_index *= weather_negative_temp_index_factor
        temp_index = clamp(temp_index, -weather_index_highest, 1)
        humidity_index = clamp(
            (averages['humidity'] - weather_humidity_base) / (100 - weather_humidity_base), 0, 1)
        clouds_index = clamp(averages['clouds'] / 100, 0, 1)
        wind_index = clamp(averages['wind_speed'] / weather_wind_max, 0, 1)
        weather_index = (
            weather_index_highest - (temp_index + humidity_index + clouds_index + wind_index))
        log.info(f"Weather data: <temp: {temp_index}, humidity: {humidity_index},"
                 f" clouds: {clouds_index}, wind: {wind_index}>")

    weather_index_clamped = clamp(weather_index, 0, 4)
    log.info(f"Weather index for location {openweather_settings['location']}:"
             f" {weather_index_clamped}")

    weather_forecast_data['index'] = weather_index_clamped
