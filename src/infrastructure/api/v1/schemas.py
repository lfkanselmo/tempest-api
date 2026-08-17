from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel

from src.domain.value_objects import UnitSystem, WeatherCondition


class LocationOut(BaseModel):
    name: str
    country: str
    latitude: float
    longitude: float


class CurrentConditionsOut(BaseModel):
    temperature_celsius: float
    apparent_temperature_celsius: float
    condition: WeatherCondition
    is_day: bool
    humidity_percent: int
    wind_speed_kmh: float
    precipitation_mm: float
    observed_at: datetime
    is_stale: bool


class HourlyForecastEntryOut(BaseModel):
    timestamp: datetime
    temperature_celsius: float
    condition: WeatherCondition
    precipitation_probability_percent: int


class DailyForecastEntryOut(BaseModel):
    date: date
    temperature_min_celsius: float
    temperature_max_celsius: float
    condition: WeatherCondition
    precipitation_probability_percent: int


class ForecastOut(BaseModel):
    hourly: list[HourlyForecastEntryOut]
    daily: list[DailyForecastEntryOut]
    is_stale: bool


class FavoriteOut(BaseModel):
    id: UUID
    name: str
    country: str
    latitude: float
    longitude: float
    created_at: datetime


class CreateFavoriteIn(BaseModel):
    name: str
    country: str
    latitude: float
    longitude: float


class PreferencesOut(BaseModel):
    unit_system: UnitSystem


class UpdatePreferencesIn(BaseModel):
    unit_system: UnitSystem
