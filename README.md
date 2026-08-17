# Tempest API

Backend de [Tempest](../SAD_Tempest_Motor_Meteorologico_Adaptativo.md), la app del clima. Expone
clima actual, pronóstico y búsqueda de ubicaciones sobre un dominio desacoplado del proveedor
climático (Open-Meteo) vía Arquitectura Hexagonal (Ports & Adapters). Python 3.12 + FastAPI.

Estado actual: **Sprint S1** — dominio y `OpenMeteoAdapter` listos y probados contra la API real;
todavía sin exponer por HTTP (`/api/v1/health` es el único endpoint). Caché, geocodificación y el
resto de rutas llegan en los sprints S2-S4 (ver roadmap en el SAD).

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
uv run pytest                     # unitarios (dominio + adapter, con MockTransport de httpx)
uv run pytest -m integration      # contra la API real de Open-Meteo (sin mocks)
uv run mypy src                    # tipado estricto
uv run ruff check .                # lint
```

Cobertura exigida: **100% en `src/domain`** (`--cov-fail-under=100`). El adapter se prueba con
`httpx.MockTransport` (sin red) más un test de integración que sí llama a Open-Meteo de verdad, para
detectar si la API externa cambia de forma sin depender solo de la memoria de lo que devuelve.

---

## Arquitectura

```text
src/
├── domain/            # Entidades, value objects — cero dependencias externas
│   ├── models.py        (CurrentConditions, Forecast, HourlyForecastEntry, DailyForecastEntry)
│   ├── value_objects.py  (Coordinates, WeatherCondition)
│   └── exceptions.py     (ProviderUnavailableException)
├── application/        # Casos de uso y puertos (Protocols)
│   └── ports/
│       └── weather_provider.py  (WeatherProviderPort)
└── infrastructure/     # Adaptadores: FastAPI, proveedor climático, caché, persistencia
    ├── api/
    └── providers/
        ├── open_meteo_adapter.py            (implementa WeatherProviderPort)
        ├── open_meteo_schemas.py             (DTOs Pydantic del JSON crudo)
        └── open_meteo_condition_mapper.py     (código WMO → WeatherCondition)
```

### Adapter Pattern sobre el proveedor climático

`OpenMeteoAdapter` es la única pieza del sistema que sabe que existe Open-Meteo. Traduce su JSON
(vía los DTOs de `open_meteo_schemas.py`) a los value objects del dominio, y convierte cualquier
error HTTP o de red en `ProviderUnavailableException` — el dominio nunca ve un `httpx.HTTPError`.
Sumar un proveedor de respaldo en el futuro es implementar `WeatherProviderPort` de nuevo, sin tocar
`domain/` ni `application/`.

El mapeo de los ~28 códigos WMO a los 11 valores de `WeatherCondition` vive en una tabla de
despacho (`_CONDITION_BY_WMO_CODE`), no en una cadena de `if/elif` — agregar o corregir un código es
una línea en el diccionario.

---

## Tecnologías

FastAPI · Pydantic v2 · httpx · pytest · pytest-asyncio · mypy (`--strict`) · ruff · uv

---

## Roadmap

Detalle completo en [`SAD_Tempest_Motor_Meteorologico_Adaptativo.md`](../SAD_Tempest_Motor_Meteorologico_Adaptativo.md).
