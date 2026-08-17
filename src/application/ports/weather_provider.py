from typing import Protocol

from src.domain.models import CurrentConditions, Forecast
from src.domain.value_objects import Coordinates


class WeatherProviderPort(Protocol):
    async def get_current(self, coordinates: Coordinates) -> CurrentConditions: ...

    async def get_forecast(self, coordinates: Coordinates) -> Forecast: ...
