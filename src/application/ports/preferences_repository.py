from typing import Protocol

from src.domain.value_objects import UnitSystem


class PreferencesRepositoryPort(Protocol):
    def get_unit_system(self) -> UnitSystem: ...

    def set_unit_system(self, unit_system: UnitSystem) -> None: ...
