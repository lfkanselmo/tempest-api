# Tempest API

[![CI](https://github.com/lfkanselmo/tempest-api/actions/workflows/ci.yml/badge.svg)](https://github.com/lfkanselmo/tempest-api/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.12%2B-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-async-009688?logo=fastapi&logoColor=white)
![License](https://img.shields.io/badge/license-proprietary-lightgrey)

Backend de [Tempest](../SAD_Tempest_Motor_Meteorologico_Adaptativo.md), la app del clima. Expone
clima actual, pronóstico, búsqueda de ubicaciones, favoritos y preferencias sobre un dominio
desacoplado de sus proveedores externos (Open-Meteo, Nominatim) vía Arquitectura Hexagonal
(Ports & Adapters). Python 3.12 + FastAPI.

Estado actual: **Sprint S3** — API REST completa (clima, ubicaciones, favoritos, preferencias),
persistencia en SQLite vía SQLAlchemy + Alembic, documentación OpenAPI en `/docs`. El motor de
alertas configurables (Fase 2, Sprint S4) es lo único que falta antes del frontend.

---

## Requisitos

- Python 3.12+
- [`uv`](https://docs.astral.sh/uv/)
- Docker (opcional, para correr el servicio contenerizado)

---

## Configuración

| Variable | Ejemplo | Descripción |
| --- | --- | --- |
| `CORS_ORIGINS` | `["http://localhost:4200"]` | Orígenes permitidos para el SPA |
| `DATABASE_URL` | `sqlite:///./data/tempest.db` | Conexión SQLite (SQLAlchemy 2.0 síncrono) |
| `NOMINATIM_USER_AGENT` | `tempest-app (tu-email@ejemplo.com)` | Header exigido por la política de uso de Nominatim/OpenStreetMap al geocodificar |

Ver `.env.example`. Centralizadas en `Settings` (`pydantic-settings`, `src/infrastructure/config.py`).

### Migraciones (Alembic)

```bash
uv run alembic upgrade head                          # aplica migraciones pendientes
uv run alembic revision --autogenerate -m "mensaje"  # genera una nueva migración
```

La migración inicial crea `favorites` (ubicaciones guardadas) y `preferences` (una sola fila,
`id="default"`, con la unidad de medida elegida — no hay multiusuario en el MVP).

---

## Ejecución

### Local

```bash
uv sync
uv run alembic upgrade head
uv run uvicorn src.infrastructure.api.main:app --reload
```

La API queda disponible en `http://localhost:8000`. Documentación interactiva en `/docs`.

### Docker

```bash
docker build -t tempest-api -f docker/Dockerfile .
docker run -p 8000:8000 tempest-api
```

Corre `alembic upgrade head` automáticamente antes de levantar `uvicorn` — el contenedor nunca
arranca con una base de datos sin migrar. Para el stack completo (API + SPA) ver
[`docker-compose.yml`](../docker-compose.yml) en la raíz de `tempest/`.

---

## Tests

```bash
uv run pytest                     # unitarios (dominio, adapters con MockTransport, repos con SQLite en memoria, routers con TestClient)
uv run pytest -m integration      # contra Open-Meteo y Nominatim reales (sin mocks)
uv run mypy src                    # tipado estricto
uv run ruff check .                # lint
```

Cobertura exigida: **100% en `src/domain`** (`--cov-fail-under=100`). Cada adapter externo se prueba
con `httpx.MockTransport` (sin red) más un test de integración que sí llama a la API real. Los
repositorios SQLite se prueban contra una base en memoria real (sin mocks de SQLAlchemy). Los
routers se prueban con `TestClient` sustituyendo el caso de uso por un doble de prueba
(`app.dependency_overrides`), sin tocar red ni disco.

---

## Documentación de la API

Todas las rutas responden en `/api/v1`. Documentación interactiva completa en `/docs`.

| Método | Ruta | Descripción |
| --- | --- | --- |
| `GET` | `/health` | Healthcheck |
| `GET` | `/locations/search?q=` | Geocodificación directa (autocompletado) |
| `GET` | `/locations/reverse?lat=&lon=` | Geocodificación inversa (`404` si no se encuentra) |
| `GET` | `/weather/current?lat=&lon=` | Condiciones actuales (incluye presión, UV, amanecer y atardecer del día en curso) |
| `GET` | `/weather/forecast?lat=&lon=` | Pronóstico horario + semanal |
| `GET` | `/favorites` | Lista las ubicaciones favoritas |
| `POST` | `/favorites` | Guarda una ubicación como favorita |
| `DELETE` | `/favorites/{id}` | Elimina un favorito (`404` si no existe) |
| `GET` | `/preferences` | Unidad de medida actual (`metric` por default) |
| `PUT` | `/preferences` | Actualiza la unidad de medida |

`lat`/`lon` se validan en la capa HTTP (`Query(ge=-90, le=90)` / `Query(ge=-180, le=180)`) antes de
llegar al dominio — devuelven `422` automático de FastAPI, no una excepción de dominio. Si el
proveedor climático no responde y no hay nada que servir desde caché, cualquier ruta de `/weather/*`
devuelve `503`.

---

## Arquitectura

```text
src/
├── domain/            # Entidades, value objects — cero dependencias externas
│   ├── models.py        (Location, Favorite, CurrentConditions, Forecast, HourlyForecastEntry, DailyForecastEntry)
│   ├── value_objects.py  (Coordinates, WeatherCondition, UnitSystem)
│   └── exceptions.py     (ProviderUnavailableException, LocationNotFoundException, FavoriteNotFoundException)
├── application/
│   ├── ports/           (Protocols: WeatherProviderPort, LocationSearchPort, ReverseGeocodingPort,
│   │                      CachePort, FavoriteRepositoryPort, PreferencesRepositoryPort)
│   └── use_cases/         (un caso de uso por operación: GetCurrentWeatherUseCase, GetForecastUseCase,
│                            SearchLocationUseCase, ReverseGeocodeUseCase, ListFavoritesUseCase,
│                            AddFavoriteUseCase, RemoveFavoriteUseCase, GetPreferencesUseCase,
│                            SetPreferencesUseCase)
└── infrastructure/
    ├── api/
    │   ├── main.py           (app factory, lifespan, CORS, exception handlers)
    │   ├── dependencies.py    (wiring de FastAPI: providers, repos y casos de uso vía Depends)
    │   └── v1/                 (routers: health, weather, locations, favorites, preferences; schemas.py; mappers.py)
    ├── cache/
    │   └── in_memory_ttl_cache.py     (implementa CachePort, TTL por entrada)
    ├── persistence/
    │   ├── database.py                 (engine + sesión SQLAlchemy)
    │   ├── orm_models.py                (FavoriteORM, PreferencesORM)
    │   ├── sqlite_favorite_repository.py
    │   └── sqlite_preferences_repository.py
    └── providers/
        ├── open_meteo_adapter.py            (implementa WeatherProviderPort)
        ├── open_meteo_geocoding_adapter.py    (implementa LocationSearchPort)
        ├── nominatim_adapter.py                (implementa ReverseGeocodingPort)
        ├── cached_weather_provider.py            (decora WeatherProviderPort, resiliencia RNF-05)
        ├── cached_location_search_provider.py     (decora LocationSearchPort)
        ├── cached_reverse_geocoding_provider.py    (decora ReverseGeocodingPort)
        └── open_meteo_condition_mapper.py           (código WMO → WeatherCondition)
alembic/                # Migraciones (favorites, preferences)
```

### Adapter Pattern sobre los proveedores externos

`OpenMeteoAdapter`, `OpenMeteoGeocodingAdapter` y `NominatimAdapter` son las únicas piezas del
sistema que saben qué proveedor hay detrás de cada uno. Cada uno traduce su JSON (vía sus propios
DTOs Pydantic) a los value objects del dominio, y convierte cualquier error HTTP o de red en
`ProviderUnavailableException` — el dominio nunca ve un `httpx.HTTPError`. Sumar un proveedor de
respaldo en el futuro es implementar el puerto correspondiente de nuevo, sin tocar `domain/` ni
`application/`.

El mapeo de los ~28 códigos WMO a los 11 valores de `WeatherCondition` vive en una tabla de
despacho (`_CONDITION_BY_WMO_CODE`), no en una cadena de `if/elif` — agregar o corregir un código es
una línea en el diccionario.

`get_current` le pide a Open-Meteo el bloque `current` (temperatura, condición, presión...) y el
`daily` (amanecer, atardecer, UV máximo) en una sola llamada — amanecer/atardecer son técnicamente
un dato "del día", no "del instante", pero viven en `CurrentConditions` porque el frontend los
necesita junto al resto del clima actual para calcular el fondo dinámico (`ThemeEngine`, RF-10) sin
pedir el pronóstico completo solo para eso.

### Caché con TTL y resiliencia (RNF-04, RNF-05)

`InMemoryTTLCache` guarda cada entrada con su propio vencimiento (sin dependencia externa como
Redis — un solo proceso alcanza para esta app). `CachedWeatherProvider` decora `OpenMeteoAdapter`
implementando el mismo `WeatherProviderPort` (Decorator sobre Adapter): clima actual con TTL de 10
minutos, pronóstico con 30. Si el proveedor falla y hay una entrada vencida en caché, la sirve
igual marcada con `is_stale=True` en vez de romper la respuesta — solo propaga la excepción si no
hay nada que servir. `CachedLocationSearchProvider` y `CachedReverseGeocodingProvider` aplican el
mismo patrón de caché a la geocodificación, con TTL de 30 días (una ciudad no cambia de
coordenadas) y sin la lógica de resiliencia, que no aplica a una búsqueda activa del usuario.

### Geocodificación: dos proveedores, dos puertos

Búsqueda directa (nombre → coordenadas) usa el geocoder de Open-Meteo, que ya se consume para el
clima. Geocodificación inversa (coordenadas → ciudad, para "usar mi ubicación") usa Nominatim de
OpenStreetMap, que Open-Meteo no ofrece. Son dos puertos separados (`LocationSearchPort`,
`ReverseGeocodingPort`) en vez de uno solo con dos métodos, para que cada adapter siga
representando un único proveedor externo.

### Persistencia: SQLAlchemy síncrono + SQLite

Igual que en Fiscus: esta es una app de un solo usuario/dispositivo por instancia, así que async no
aporta frente a la complejidad que añade. `favorites` guarda una copia plana de cada `Location`
guardada (no una referencia); `preferences` es una tabla de una sola fila (`id="default"`) porque no
hay multiusuario en el MVP — `GET /preferences` sin fila creada responde `metric` por defecto en
vez de `404`.

### Wiring de FastAPI

`app.state` guarda, por el tiempo de vida del proceso (`lifespan`), el único `InMemoryTTLCache` y
los dos `httpx.AsyncClient` (uno genérico para Open-Meteo, otro con el `User-Agent` exigido por
Nominatim) — así ninguna request abre una conexión nueva. `dependencies.py` arma cada caso de uso
por request componiendo estos objetos vía `Depends()`; los tests sustituyen directamente la
dependencia del caso de uso (`app.dependency_overrides`), sin necesitar red ni base de datos real.

---

## Tecnologías

FastAPI · Pydantic v2 · SQLAlchemy 2.0 · Alembic · SQLite · httpx · pytest · pytest-asyncio ·
mypy (`--strict`) · ruff · uv

---

## Roadmap

Detalle completo en [`SAD_Tempest_Motor_Meteorologico_Adaptativo.md`](../SAD_Tempest_Motor_Meteorologico_Adaptativo.md).
