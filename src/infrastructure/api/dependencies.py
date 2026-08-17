from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from src.application.ports.cache import CachePort
from src.application.ports.location_search import LocationSearchPort
from src.application.ports.reverse_geocoding import ReverseGeocodingPort
from src.application.ports.weather_provider import WeatherProviderPort
from src.application.use_cases.add_favorite import AddFavoriteUseCase
from src.application.use_cases.get_current_weather import GetCurrentWeatherUseCase
from src.application.use_cases.get_forecast import GetForecastUseCase
from src.application.use_cases.get_preferences import GetPreferencesUseCase
from src.application.use_cases.list_favorites import ListFavoritesUseCase
from src.application.use_cases.remove_favorite import RemoveFavoriteUseCase
from src.application.use_cases.reverse_geocode import ReverseGeocodeUseCase
from src.application.use_cases.search_location import SearchLocationUseCase
from src.application.use_cases.set_preferences import SetPreferencesUseCase
from src.infrastructure.persistence.database import get_session
from src.infrastructure.persistence.sqlite_favorite_repository import SqliteFavoriteRepository
from src.infrastructure.persistence.sqlite_preferences_repository import (
    SqlitePreferencesRepository,
)
from src.infrastructure.providers.cached_location_search_provider import (
    CachedLocationSearchProvider,
)
from src.infrastructure.providers.cached_reverse_geocoding_provider import (
    CachedReverseGeocodingProvider,
)
from src.infrastructure.providers.cached_weather_provider import CachedWeatherProvider
from src.infrastructure.providers.nominatim_adapter import NominatimAdapter
from src.infrastructure.providers.open_meteo_adapter import OpenMeteoAdapter
from src.infrastructure.providers.open_meteo_geocoding_adapter import OpenMeteoGeocodingAdapter

SessionDep = Annotated[Session, Depends(get_session)]


def get_cache(request: Request) -> CachePort:
    cache: CachePort = request.app.state.cache
    return cache


CacheDep = Annotated[CachePort, Depends(get_cache)]


def get_weather_provider(request: Request, cache: CacheDep) -> WeatherProviderPort:
    adapter = OpenMeteoAdapter(request.app.state.open_meteo_client)
    return CachedWeatherProvider(adapter, cache)


def get_location_search(request: Request, cache: CacheDep) -> LocationSearchPort:
    adapter = OpenMeteoGeocodingAdapter(request.app.state.open_meteo_client)
    return CachedLocationSearchProvider(adapter, cache)


def get_reverse_geocoding(request: Request, cache: CacheDep) -> ReverseGeocodingPort:
    adapter = NominatimAdapter(request.app.state.nominatim_client)
    return CachedReverseGeocodingProvider(adapter, cache)


def get_current_weather_use_case(
    weather_provider: Annotated[WeatherProviderPort, Depends(get_weather_provider)],
) -> GetCurrentWeatherUseCase:
    return GetCurrentWeatherUseCase(weather_provider)


def get_forecast_use_case(
    weather_provider: Annotated[WeatherProviderPort, Depends(get_weather_provider)],
) -> GetForecastUseCase:
    return GetForecastUseCase(weather_provider)


def get_search_location_use_case(
    location_search: Annotated[LocationSearchPort, Depends(get_location_search)],
) -> SearchLocationUseCase:
    return SearchLocationUseCase(location_search)


def get_reverse_geocode_use_case(
    reverse_geocoding: Annotated[ReverseGeocodingPort, Depends(get_reverse_geocoding)],
) -> ReverseGeocodeUseCase:
    return ReverseGeocodeUseCase(reverse_geocoding)


def get_list_favorites_use_case(session: SessionDep) -> ListFavoritesUseCase:
    return ListFavoritesUseCase(SqliteFavoriteRepository(session))


def get_add_favorite_use_case(session: SessionDep) -> AddFavoriteUseCase:
    return AddFavoriteUseCase(SqliteFavoriteRepository(session))


def get_remove_favorite_use_case(session: SessionDep) -> RemoveFavoriteUseCase:
    return RemoveFavoriteUseCase(SqliteFavoriteRepository(session))


def get_get_preferences_use_case(session: SessionDep) -> GetPreferencesUseCase:
    return GetPreferencesUseCase(SqlitePreferencesRepository(session))


def get_set_preferences_use_case(session: SessionDep) -> SetPreferencesUseCase:
    return SetPreferencesUseCase(SqlitePreferencesRepository(session))
