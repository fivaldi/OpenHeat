from datetime import datetime
from statistics import mean

import requests

from openheat.config import config
from openheat.exceptions import ConfigError
from openheat.logger import log
from openheat.utils import clamp

OPENWEATHER_BASIC_API_URL = 'https://api.openweathermap.org/data/2.5/weather'
OPENWEATHER_ONECALL_API_URL = 'https://api.openweathermap.org/data/2.5/onecall'


class Weather:
    def __init__(self):
        self.lon_lat = None
        self.weather_forecast_data = {}

        params = {'q': config.openweather_settings['location'],
                  'appid': config.openweather_settings['api_key'],
                  'units': 'metric'}

        try:
            data = requests.get(OPENWEATHER_BASIC_API_URL, params=params)
            data.raise_for_status()
            self.lon_lat = (data.json()['coord']['lon'], data.json()['coord']['lat'])
            log.debug(f"OpenWeather data: {data.json()}")
        except requests.exceptions.HTTPError:
            msg = f"OpenWeather responded with HTTP status code {data.status_code}."
            if data.status_code == 404:
                msg += f" Maybe unknown location '{config.openweather_settings['location']}'?"
            log.error(msg)
        except requests.exceptions.RequestException:
            log.exception("Couldn't get data from OpenWeather.")

        if not self.lon_lat:
            raise ConfigError("Couldn't init weather location.")

    def get_weather(self, hourly_forecast=False):
        excludes = 'minutely,daily,alerts' if hourly_forecast else 'minutely,hourly,daily,alerts'

        params = {'appid': config.openweather_settings['api_key'],
                  'lon': self.lon_lat[0], 'lat': self.lon_lat[1],
                  'exclude': excludes,
                  'units': 'metric'}
        weather = {}
        try:
            data = requests.get(OPENWEATHER_ONECALL_API_URL, params=params)
            data.raise_for_status()
            weather = data.json()
            log.debug(f"OpenWeather data: {data.json()}")
        except requests.exceptions.RequestException:
            log.exception("Couldn't get data from OpenWeather.")

        return weather

    def forecast_and_assess_weather_index(self, hours_from_now=0):
        weather = self.get_weather(hourly_forecast=True)
        if not weather:
            return

        current = self.weather_forecast_data['current'] = weather['current']
        hourly = self.weather_forecast_data['hourly'] = weather['hourly']

        if hours_from_now + config.weather_hourly_forecast_hrs > len(hourly):
            raise ValueError("Can't go beyond forecast data. Please lower the hours offset.")

        if hours_from_now >= 1:
            current = self.weather_forecast_data['current'] = weather['hourly'][hours_from_now - 1]
            hourly = self.weather_forecast_data['hourly'] = weather['hourly'][hours_from_now:]

        averages = {}

        for value in 'temp', 'humidity', 'clouds', 'wind_speed':
            mean_forecast_value = mean([v[value] for v
                                        in hourly[0:config.weather_hourly_forecast_hrs]])
            averages[value] = (
                (config.weather_weight_current * current[value]
                 + config.weather_weight_hourly_forecast * mean_forecast_value)
                / (config.weather_weight_current + config.weather_weight_hourly_forecast))

        weather_index_highest = 4
        self.weather_forecast_data['as_of_datetime'] = datetime.now()
        if (averages['temp'] >= config.weather_baselines['max_avg_temp']
                and averages['clouds'] <= config.weather_baselines['clouds_few']
                and averages['wind_speed'] <= config.weather_baselines['wind_light']):
            weather_index = weather_index_highest
        else:
            temp_index = ((averages['temp'] - config.weather_baselines['max_avg_temp'])
                          / (config.weather_baselines['min_avg_temp']
                             - config.weather_baselines['max_avg_temp']))
            if temp_index < 0:
                temp_index *= config.weather_baselines['negative_temp_index_factor']
            temp_index = clamp(temp_index, -weather_index_highest, 1)
            humidity_index = clamp(
                (averages['humidity'] - config.weather_baselines['humidity_base'])
                / (100 - config.weather_baselines['humidity_base']), 0, 1)
            clouds_index = clamp(averages['clouds'] / 100, 0, 1)
            wind_index = clamp(averages['wind_speed'] / config.weather_baselines['wind_max'], 0, 1)
            weather_index = (
                weather_index_highest - (temp_index + humidity_index + clouds_index + wind_index))
            log.info(f"Weather data: <temp: {temp_index}, humidity: {humidity_index},"
                     f" clouds: {clouds_index}, wind: {wind_index}>")

        weather_index_clamped = clamp(weather_index, 0, 4)
        log.info(f"Weather index for location {config.openweather_settings['location']}:"
                 f" {weather_index_clamped}")

        self.weather_forecast_data['index'] = weather_index_clamped
