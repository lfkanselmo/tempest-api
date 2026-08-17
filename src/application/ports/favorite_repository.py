from typing import Protocol
from uuid import UUID

from src.domain.models import Favorite, Location


class FavoriteRepositoryPort(Protocol):
    def list_all(self) -> list[Favorite]: ...

    def add(self, location: Location) -> Favorite: ...

    def remove(self, favorite_id: UUID) -> None: ...
