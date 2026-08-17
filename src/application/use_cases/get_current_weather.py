from src.application.ports.weather_provider import WeatherProviderPort
from src.domain.models import CurrentConditions
from src.domain.value_objects import Coordinates


class GetCurrentWeatherUseCase:
    def __init__(self, weather_provider: WeatherProviderPort) -> None:
        self._weather_provider = weather_provider

    async def execute(self, coordinates: Coordinates) -> CurrentConditions:
        return await self._weather_provider.get_current(coordinates)
