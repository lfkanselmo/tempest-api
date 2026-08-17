from src.application.ports.preferences_repository import PreferencesRepositoryPort
from src.domain.value_objects import UnitSystem


class SetPreferencesUseCase:
    def __init__(self, preferences: PreferencesRepositoryPort) -> None:
        self._preferences = preferences

    def execute(self, unit_system: UnitSystem) -> None:
        self._preferences.set_unit_system(unit_system)
