from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.application.use_cases.add_favorite import AddFavoriteUseCase
from src.application.use_cases.list_favorites import ListFavoritesUseCase
from src.application.use_cases.remove_favorite import RemoveFavoriteUseCase
from src.domain.models import Location
from src.domain.value_objects import Coordinates
from src.infrastructure.api.dependencies import (
    get_add_favorite_use_case,
    get_list_favorites_use_case,
    get_remove_favorite_use_case,
)
from src.infrastructure.api.v1.mappers import to_favorite_out
from src.infrastructure.api.v1.schemas import CreateFavoriteIn, FavoriteOut

router = APIRouter(prefix="/favorites", tags=["favorites"])


@router.get("")
def list_favorites(
    use_case: Annotated[ListFavoritesUseCase, Depends(get_list_favorites_use_case)],
) -> list[FavoriteOut]:
    return [to_favorite_out(favorite) for favorite in use_case.execute()]


@router.post("", status_code=status.HTTP_201_CREATED)
def add_favorite(
    payload: CreateFavoriteIn,
    use_case: Annotated[AddFavoriteUseCase, Depends(get_add_favorite_use_case)],
) -> FavoriteOut:
    location = Location(
        name=payload.name,
        country=payload.country,
        coordinates=Coordinates(latitude=payload.latitude, longitude=payload.longitude),
    )
    return to_favorite_out(use_case.execute(location))


@router.delete("/{favorite_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_favorite(
    favorite_id: UUID,
    use_case: Annotated[RemoveFavoriteUseCase, Depends(get_remove_favorite_use_case)],
) -> None:
    use_case.execute(favorite_id)
