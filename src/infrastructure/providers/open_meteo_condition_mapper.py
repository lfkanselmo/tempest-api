from src.domain.value_objects import WeatherCondition

_CONDITION_BY_WMO_CODE: dict[int, WeatherCondition] = {
    0: WeatherCondition.CLEAR,
    1: WeatherCondition.CLEAR,
    2: WeatherCondition.PARTLY_CLOUDY,
    3: WeatherCondition.CLOUDY,
    45: WeatherCondition.FOG,
    48: WeatherCondition.FOG,
    51: WeatherCondition.DRIZZLE,
    53: WeatherCondition.DRIZZLE,
    55: WeatherCondition.DRIZZLE,
    56: WeatherCondition.FREEZING_RAIN,
    57: WeatherCondition.FREEZING_RAIN,
    61: WeatherCondition.RAIN,
    63: WeatherCondition.RAIN,
    65: WeatherCondition.RAIN,
    66: WeatherCondition.FREEZING_RAIN,
    67: WeatherCondition.FREEZING_RAIN,
    71: WeatherCondition.SNOW,
    73: WeatherCondition.SNOW,
    75: WeatherCondition.SNOW,
    77: WeatherCondition.SNOW,
    80: WeatherCondition.RAIN_SHOWERS,
    81: WeatherCondition.RAIN_SHOWERS,
    82: WeatherCondition.RAIN_SHOWERS,
    85: WeatherCondition.SNOW_SHOWERS,
    86: WeatherCondition.SNOW_SHOWERS,
    95: WeatherCondition.THUNDERSTORM,
    96: WeatherCondition.THUNDERSTORM,
    99: WeatherCondition.THUNDERSTORM,
}


def map_wmo_code(code: int) -> WeatherCondition:
    try:
        return _CONDITION_BY_WMO_CODE[code]
    except KeyError:
        raise ValueError(f"Codigo WMO desconocido: {code}") from None
