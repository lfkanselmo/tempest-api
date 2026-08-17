from typing import Protocol

from src.domain.models import Location


class LocationSearchPort(Protocol):
    async def search(self, query: str) -> list[Location]: ...
