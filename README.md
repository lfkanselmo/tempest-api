# Tempest API

Backend de [Tempest](../SAD_Tempest_Motor_Meteorologico_Adaptativo.md), la app del clima. Expone
clima actual, pronóstico y búsqueda de ubicaciones sobre un dominio desacoplado del proveedor
climático (Open-Meteo) vía Arquitectura Hexagonal (Ports & Adapters). Python 3.12 + FastAPI.

Estado actual: **Sprint S0 (scaffolding)** — solo `/api/v1/health`. El motor de dominio, el adapter
de Open-Meteo y el resto de endpoints llegan en los sprints S1-S4 (ver roadmap en el SAD).

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
uv run pytest          # unitarios
uv run mypy src         # tipado estricto
uv run ruff check .     # lint
```

---

## Arquitectura

```text
src/
├── domain/            # Entidades, value objects — cero dependencias externas (S1)
├── application/        # Casos de uso y puertos (Protocols)
│   ├── ports/
│   └── use_cases/
└── infrastructure/     # Adaptadores: FastAPI, proveedor climático, caché, persistencia
    └── api/
```

---

## Tecnologías

FastAPI · Pydantic v2 · pytest · mypy (`--strict`) · ruff · uv

---

## Roadmap

Detalle completo en [`SAD_Tempest_Motor_Meteorologico_Adaptativo.md`](../SAD_Tempest_Motor_Meteorologico_Adaptativo.md).
