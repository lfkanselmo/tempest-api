import pytest
from src.infrastructure.cache.in_memory_ttl_cache import InMemoryTTLCache


@pytest.mark.asyncio
async def test_returns_none_for_missing_key() -> None:
    cache = InMemoryTTLCache()

    assert await cache.get("missing") is None


@pytest.mark.asyncio
async def test_returns_value_before_expiry() -> None:
    cache = InMemoryTTLCache()

    await cache.set("key", "value", ttl_seconds=60)

    assert await cache.get("key") == "value"


@pytest.mark.asyncio
async def test_get_returns_none_after_expiry() -> None:
    cache = InMemoryTTLCache()

    await cache.set("key", "value", ttl_seconds=-1)

    assert await cache.get("key") is None


@pytest.mark.asyncio
async def test_get_stale_returns_value_even_after_expiry() -> None:
    cache = InMemoryTTLCache()

    await cache.set("key", "value", ttl_seconds=-1)

    assert await cache.get_stale("key") == "value"


@pytest.mark.asyncio
async def test_get_stale_returns_none_for_missing_key() -> None:
    cache = InMemoryTTLCache()

    assert await cache.get_stale("missing") is None
