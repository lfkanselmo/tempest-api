from src.application.ports.location_search import LocationSearchPort
from src.domain.models import Location


class SearchLocationUseCase:
    def __init__(self, location_search: LocationSearchPort) -> None:
        self._location_search = location_search

    async def execute(self, query: str) -> list[Location]:
        return await self._location_search.search(query)
