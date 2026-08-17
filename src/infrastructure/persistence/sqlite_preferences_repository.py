from sqlalchemy.orm import Session

from src.domain.value_objects import UnitSystem
from src.infrastructure.persistence.orm_models import PreferencesORM

DEFAULT_ROW_ID = "default"


class SqlitePreferencesRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_unit_system(self) -> UnitSystem:
        row = self._session.get(PreferencesORM, DEFAULT_ROW_ID)
        if row is None:
            return UnitSystem.METRIC
        return UnitSystem(row.unit_system)

    def set_unit_system(self, unit_system: UnitSystem) -> None:
        row = self._session.get(PreferencesORM, DEFAULT_ROW_ID)
        if row is None:
            self._session.add(PreferencesORM(id=DEFAULT_ROW_ID, unit_system=unit_system.value))
        else:
            row.unit_system = unit_system.value
        self._session.commit()
