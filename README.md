# Tempest API

[![CI](https://github.com/lfkanselmo/tempest-api/actions/workflows/ci.yml/badge.svg)](https://github.com/lfkanselmo/tempest-api/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.12%2B-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-async-009688?logo=fastapi&logoColor=white)
![License](https://img.shields.io/badge/license-proprietary-lightgrey)

Backend de [Tempest](../SAD_Tempest_Motor_Meteorologico_Adaptativo.md), la app del clima. Expone
clima actual, pronóstico y búsqueda de ubicaciones sobre un dominio desacoplado del proveedor
climático (Open-Meteo) vía Arquitectura Hexagonal (Ports & Adapters). Python 3.12 + FastAPI.

Estado actual: **Sprint S2** — dominio, adapter de clima, caché con resiliencia y los dos adapters
de geocodificación listos y probados contra las APIs reales; todavía sin exponer por HTTP
(`/api/v1/health` es el único endpoint). El resto de rutas y la persistencia de favoritos llegan en
el Sprint S3 (ver roadmap en el SAD).

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

Ver `.env.example`. Centralizadas en `Settings` (`pydantic-settings`, `src/infrastructure/config.py`).

---

## Ejecución

### Local

```bash
uv sync
uv run uvicorn src.infrastructure.api.main:app --reload
```

La API queda disponible en `http://localhost:8000`. Documentación interactiva en `/docs`.

### Docker

```bash
docker build -t tempest-api -f docker/Dockerfile .
docker run -p 8000:8000 tempest-api
```

Para el stack completo (API + SPA) ver [`docker-compose.yml`](../docker-compose.yml) en la raíz de
`tempest/` (se agrega en el Sprint S8).

---

## Tests

```bash
uv run pytest                     # unitarios (dominio + adapters, con MockTransport de httpx)
uv run pytest -m integration      # contra Open-Meteo y Nominatim reales (sin mocks)
uv run mypy src                    # tipado estricto
uv run ruff check .                # lint
```

Cobertura exigida: **100% en `src/domain`** (`--cov-fail-under=100`). Cada adapter externo se prueba
con `httpx.MockTransport` (sin red) más un test de integración que sí llama a la API real, para
detectar si el proveedor cambia de forma sin depender solo de la memoria de lo que devuelve.

---

## Arquitectura

```text
src/
├── domain/            # Entidades, value objects — cero dependencias externas
│   ├── models.py        (Location, CurrentConditions, Forecast, HourlyForecastEntry, DailyForecastEntry)
│   ├── value_objects.py  (Coordinates, WeatherCondition)
│   └── exceptions.py     (ProviderUnavailableException, LocationNotFoundException)
├── application/        # Casos de uso y puertos (Protocols)
│   └── ports/
│       ├── weather_provider.py    (WeatherProviderPort)
│       ├── location_search.py      (LocationSearchPort)
│       ├── reverse_geocoding.py     (ReverseGeocodingPort)
│       └── cache.py                  (CachePort)
└── infrastructure/     # Adaptadores: FastAPI, proveedores externos, caché, persistencia
    ├── api/
    ├── cache/
    │   └── in_memory_ttl_cache.py     (implementa CachePort, TTL por entrada)
    └── providers/
        ├── open_meteo_adapter.py            (implementa WeatherProviderPort)
        ├── open_meteo_geocoding_adapter.py    (implementa LocationSearchPort)
        ├── nominatim_adapter.py                (implementa ReverseGeocodingPort)
        ├── cached_weather_provider.py            (decora WeatherProviderPort, resiliencia RNF-05)
        ├── cached_location_search_provider.py     (decora LocationSearchPort)
        └── open_meteo_condition_mapper.py          (código WMO → WeatherCondition)
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

### Caché con TTL y resiliencia (RNF-04, RNF-05)

`InMemoryTTLCache` guarda cada entrada con su propio vencimiento (sin dependencia externa como
Redis — un solo proceso alcanza para esta app). `CachedWeatherProvider` decora `OpenMeteoAdapter`
implementando el mismo `WeatherProviderPort` (Decorator sobre Adapter): clima actual con TTL de 10
minutos, pronóstico con 30. Si el proveedor falla y hay una entrada vencida en caché, la sirve
igual marcada con `is_stale=True` en vez de romper la respuesta — solo propaga la excepción si no
hay nada que servir. `CachedLocationSearchProvider` aplica el mismo patrón de caché a las búsquedas
de ubicación, con TTL de 30 días (una ciudad no cambia de coordenadas) y sin la lógica de
resiliencia, que no aplica a una búsqueda activa del usuario.

### Geocodificación: dos proveedores, dos puertos

Búsqueda directa (nombre → coordenadas) usa el geocoder de Open-Meteo, que ya se consume para el
clima. Geocodificación inversa (coordenadas → ciudad, para "usar mi ubicación") usa Nominatim de
OpenStreetMap, que Open-Meteo no ofrece. Son dos puertos separados (`LocationSearchPort`,
`ReverseGeocodingPort`) en vez de uno solo con dos métodos, para que cada adapter siga
representando un único proveedor externo.

---

## Tecnologías

FastAPI · Pydantic v2 · httpx · pytest · pytest-asyncio · mypy (`--strict`) · ruff · uv

---

## Roadmap

Detalle completo en [`SAD_Tempest_Motor_Meteorologico_Adaptativo.md`](../SAD_Tempest_Motor_Meteorologico_Adaptativo.md).
