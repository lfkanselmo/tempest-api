from collections.abc import Iterator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from src.domain.value_objects import UnitSystem
from src.infrastructure.persistence.orm_models import Base
from src.infrastructure.persistence.sqlite_preferences_repository import (
    SqlitePreferencesRepository,
)


@pytest.fixture
def repository() -> Iterator[SqlitePreferencesRepository]:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = Session(engine)
    try:
        yield SqlitePreferencesRepository(session)
    finally:
        session.close()
        engine.dispose()


def test_get_unit_system_defaults_to_metric(repository: SqlitePreferencesRepository) -> None:
    assert repository.get_unit_system() == UnitSystem.METRIC


def test_set_unit_system_persists_new_value(repository: SqlitePreferencesRepository) -> None:
    repository.set_unit_system(UnitSystem.IMPERIAL)

    assert repository.get_unit_system() == UnitSystem.IMPERIAL


def test_set_unit_system_overwrites_previous_value(repository: SqlitePreferencesRepository) -> None:
    repository.set_unit_system(UnitSystem.IMPERIAL)
    repository.set_unit_system(UnitSystem.METRIC)

    assert repository.get_unit_system() == UnitSystem.METRIC
