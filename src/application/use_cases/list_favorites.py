from src.application.ports.favorite_repository import FavoriteRepositoryPort
from src.domain.models import Favorite


class ListFavoritesUseCase:
    def __init__(self, favorites: FavoriteRepositoryPort) -> None:
        self._favorites = favorites

    def execute(self) -> list[Favorite]:
        return self._favorites.list_all()
