from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.domain.exceptions import (
    FavoriteNotFoundException,
    LocationNotFoundException,
    ProviderUnavailableException,
)
from src.infrastructure.api.v1.favorites import router as favorites_router
from src.infrastructure.api.v1.health import router as health_router
from src.infrastructure.api.v1.locations import router as locations_router
from src.infrastructure.api.v1.preferences import router as preferences_router
from src.infrastructure.api.v1.weather import router as weather_router
from src.infrastructure.cache.in_memory_ttl_cache import InMemoryTTLCache
from src.infrastructure.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.state.cache = InMemoryTTLCache()
    app.state.open_meteo_client = httpx.AsyncClient()
    app.state.nominatim_client = httpx.AsyncClient(
        headers={"User-Agent": settings.nominatim_user_agent}
    )
    yield
    await app.state.open_meteo_client.aclose()
    await app.state.nominatim_client.aclose()


app = FastAPI(title="Tempest API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(ProviderUnavailableException)
async def provider_unavailable_handler(
    request: Request, exc: ProviderUnavailableException
) -> JSONResponse:
    return JSONResponse(status_code=503, content={"detail": "El proveedor climático no responde"})


@app.exception_handler(LocationNotFoundException)
async def location_not_found_handler(
    request: Request, exc: LocationNotFoundException
) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": "Ubicación no encontrada"})


@app.exception_handler(FavoriteNotFoundException)
async def favorite_not_found_handler(
    request: Request, exc: FavoriteNotFoundException
) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": "Favorito no encontrado"})


app.include_router(health_router, prefix="/api/v1")
app.include_router(weather_router, prefix="/api/v1")
app.include_router(locations_router, prefix="/api/v1")
app.include_router(favorites_router, prefix="/api/v1")
app.include_router(preferences_router, prefix="/api/v1")
