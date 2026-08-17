from dataclasses import dataclass
from datetime import date, datetime

from src.domain.value_objects import WeatherCondition


@dataclass(frozen=True)
class CurrentConditions:
    temperature_celsius: float
    apparent_temperature_celsius: float
    condition: WeatherCondition
    is_day: bool
    humidity_percent: int
    wind_speed_kmh: float
    precipitation_mm: float
    observed_at: datetime


@dataclass(frozen=True)
class HourlyForecastEntry:
    timestamp: datetime
    temperature_celsius: float
    condition: WeatherCondition
    precipitation_probability_percent: int


@dataclass(frozen=True)
class DailyForecastEntry:
    date: date
    temperature_min_celsius: float
    temperature_max_celsius: float
    condition: WeatherCondition
    precipitation_probability_percent: int


@dataclass(frozen=True)
class Forecast:
    hourly: tuple[HourlyForecastEntry, ...]
    daily: tuple[DailyForecastEntry, ...]
