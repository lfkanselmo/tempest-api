from typing import Annotated

from fastapi import APIRouter, Depends

from src.application.use_cases.reverse_geocode import ReverseGeocodeUseCase
from src.application.use_cases.search_location import SearchLocationUseCase
from src.domain.value_objects import Coordinates
from src.infrastructure.api.dependencies import (
    get_reverse_geocode_use_case,
    get_search_location_use_case,
)
from src.infrastructure.api.v1.mappers import to_location_out
from src.infrastructure.api.v1.schemas import LocationOut
from src.infrastructure.api.v1.weather import Latitude, Longitude

router = APIRouter(prefix="/locations", tags=["locations"])


@router.get("/search")
async def search_locations(
    q: str,
    use_case: Annotated[SearchLocationUseCase, Depends(get_search_location_use_case)],
) -> list[LocationOut]:
    locations = await use_case.execute(q)
    return [to_location_out(location) for location in locations]


@router.get("/reverse")
async def reverse_geocode(
    lat: Latitude,
    lon: Longitude,
    use_case: Annotated[ReverseGeocodeUseCase, Depends(get_reverse_geocode_use_case)],
) -> LocationOut:
    location = await use_case.execute(Coordinates(latitude=lat, longitude=lon))
    return to_location_out(location)
