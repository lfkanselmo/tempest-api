from typing import Annotated

from fastapi import APIRouter, Depends

from src.application.use_cases.get_preferences import GetPreferencesUseCase
from src.application.use_cases.set_preferences import SetPreferencesUseCase
from src.infrastructure.api.dependencies import (
    get_get_preferences_use_case,
    get_set_preferences_use_case,
)
from src.infrastructure.api.v1.schemas import PreferencesOut, UpdatePreferencesIn

router = APIRouter(prefix="/preferences", tags=["preferences"])


@router.get("")
def get_preferences(
    use_case: Annotated[GetPreferencesUseCase, Depends(get_get_preferences_use_case)],
) -> PreferencesOut:
    return PreferencesOut(unit_system=use_case.execute())


@router.put("")
def update_preferences(
    payload: UpdatePreferencesIn,
    use_case: Annotated[SetPreferencesUseCase, Depends(get_set_preferences_use_case)],
) -> PreferencesOut:
    use_case.execute(payload.unit_system)
    return PreferencesOut(unit_system=payload.unit_system)
