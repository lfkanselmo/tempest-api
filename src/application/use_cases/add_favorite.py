from src.application.ports.favorite_repository import FavoriteRepositoryPort
from src.domain.models import Favorite, Location


class AddFavoriteUseCase:
    def __init__(self, favorites: FavoriteRepositoryPort) -> None:
        self._favorites = favorites

    def execute(self, location: Location) -> Favorite:
        return self._favorites.add(location)
