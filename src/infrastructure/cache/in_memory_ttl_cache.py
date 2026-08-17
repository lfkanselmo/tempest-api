import time
from dataclasses import dataclass


@dataclass
class _CacheEntry:
    value: object
    expires_at: float


class InMemoryTTLCache:
    def __init__(self) -> None:
        self._store: dict[str, _CacheEntry] = {}

    async def get(self, key: str) -> object | None:
        entry = self._store.get(key)
        if entry is None or time.monotonic() > entry.expires_at:
            return None
        return entry.value

    async def get_stale(self, key: str) -> object | None:
        entry = self._store.get(key)
        return entry.value if entry is not None else None

    async def set(self, key: str, value: object, ttl_seconds: int) -> None:
        self._store[key] = _CacheEntry(value=value, expires_at=time.monotonic() + ttl_seconds)
