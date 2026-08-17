import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from src.domain.exceptions import FavoriteNotFoundException
from src.domain.models import Location
from src.domain.value_objects import Coordinates
from src.infrastructure.persistence.orm_models import Base
from src.infrastructure.persistence.sqlite_favorite_repository import SqliteFavoriteRepository

BOGOTA = Location(name="Bogotá", country="Colombia", coordinates=Coordinates(4.7110, -74.0721))


@pytest.fixture
def repository() -> SqliteFavoriteRepository:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return SqliteFavoriteRepository(Session(engine))


def test_list_all_returns_empty_when_no_favorites(repository: SqliteFavoriteRepository) -> None:
    assert repository.list_all() == []


def test_add_persists_and_returns_favorite(repository: SqliteFavoriteRepository) -> None:
    favorite = repository.add(BOGOTA)

    assert favorite.location == BOGOTA
    assert repository.list_all() == [favorite]


def test_remove_deletes_existing_favorite(repository: SqliteFavoriteRepository) -> None:
    favorite = repository.add(BOGOTA)

    repository.remove(favorite.id)

    assert repository.list_all() == []


def test_remove_raises_when_favorite_does_not_exist(repository: SqliteFavoriteRepository) -> None:
    favorite = repository.add(BOGOTA)
    repository.remove(favorite.id)

    with pytest.raises(FavoriteNotFoundException):
        repository.remove(favorite.id)
