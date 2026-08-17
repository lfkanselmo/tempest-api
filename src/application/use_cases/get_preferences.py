from src.application.ports.preferences_repository import PreferencesRepositoryPort
from src.domain.value_objects import UnitSystem


class GetPreferencesUseCase:
    def __init__(self, preferences: PreferencesRepositoryPort) -> None:
        self._preferences = preferences

    def execute(self) -> UnitSystem:
        return self._preferences.get_unit_system()
