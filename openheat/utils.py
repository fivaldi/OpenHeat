from datetime import timedelta

from openheat.exceptions import ConfigError


def clamp(n, minn, maxn):
    return minn if n < minn else maxn if n > maxn else n


def config_str_to_timedelta(config_str):
    try:
        kwarg_name, kwarg_value = config_str.split('=')
        kwarg_value = float(kwarg_value)
        return timedelta(**{kwarg_name: kwarg_value})
    except Exception:
        raise ConfigError(f"Error while converting configuration value {config_str} to timedelta.")
