from typing import Annotated

from fastapi import APIRouter, Depends, Query

from src.application.use_cases.get_current_weather import GetCurrentWeatherUseCase
from src.application.use_cases.get_forecast import GetForecastUseCase
from src.domain.value_objects import Coordinates
from src.infrastructure.api.dependencies import (
    get_current_weather_use_case,
    get_forecast_use_case,
)
from src.infrastructure.api.v1.mappers import to_current_conditions_out, to_forecast_out
from src.infrastructure.api.v1.schemas import CurrentConditionsOut, ForecastOut

router = APIRouter(prefix="/weather", tags=["weather"])

Latitude = Annotated[float, Query(ge=-90, le=90)]
Longitude = Annotated[float, Query(ge=-180, le=180)]


@router.get("/current")
async def get_current_weather(
    lat: Latitude,
    lon: Longitude,
    use_case: Annotated[GetCurrentWeatherUseCase, Depends(get_current_weather_use_case)],
) -> CurrentConditionsOut:
    conditions = await use_case.execute(Coordinates(latitude=lat, longitude=lon))
    return to_current_conditions_out(conditions)


@router.get("/forecast")
async def get_forecast(
    lat: Latitude,
    lon: Longitude,
    use_case: Annotated[GetForecastUseCase, Depends(get_forecast_use_case)],
) -> ForecastOut:
    forecast = await use_case.execute(Coordinates(latitude=lat, longitude=lon))
    return to_forecast_out(forecast)
