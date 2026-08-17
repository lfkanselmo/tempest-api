from src.application.ports.weather_provider import WeatherProviderPort
from src.domain.models import Forecast
from src.domain.value_objects import Coordinates


class GetForecastUseCase:
    def __init__(self, weather_provider: WeatherProviderPort) -> None:
        self._weather_provider = weather_provider

    async def execute(self, coordinates: Coordinates) -> Forecast:
        return await self._weather_provider.get_forecast(coordinates)
