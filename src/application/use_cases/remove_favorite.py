from uuid import UUID

from src.application.ports.favorite_repository import FavoriteRepositoryPort


class RemoveFavoriteUseCase:
    def __init__(self, favorites: FavoriteRepositoryPort) -> None:
        self._favorites = favorites

    def execute(self, favorite_id: UUID) -> None:
        self._favorites.remove(favorite_id)
