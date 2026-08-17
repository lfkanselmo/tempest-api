from datetime import date, datetime

from pydantic import BaseModel


class OpenMeteoCurrent(BaseModel):
    time: datetime
    temperature_2m: float
    apparent_temperature: float
    relative_humidity_2m: int
    is_day: int
    precipitation: float
    weather_code: int
    wind_speed_10m: float
    surface_pressure: float


class OpenMeteoCurrentDaily(BaseModel):
    sunrise: list[datetime]
    sunset: list[datetime]
    uv_index_max: list[float]


class OpenMeteoCurrentResponse(BaseModel):
    current: OpenMeteoCurrent
    daily: OpenMeteoCurrentDaily


class OpenMeteoHourly(BaseModel):
    time: list[datetime]
    temperature_2m: list[float]
    precipitation_probability: list[int]
    weather_code: list[int]


class OpenMeteoDaily(BaseModel):
    time: list[date]
    temperature_2m_max: list[float]
    temperature_2m_min: list[float]
    precipitation_probability_max: list[int]
    weather_code: list[int]


class OpenMeteoForecastResponse(BaseModel):
    hourly: OpenMeteoHourly
    daily: OpenMeteoDaily
