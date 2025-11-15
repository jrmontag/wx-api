"""Simple TTL (Time-To-Live) cache implementation."""

import logging
import time
from typing import Any, Optional


class SimpleTTLCache:
    """Simple in-memory cache with TTL support."""

    def __init__(self, ttl_seconds: int = 3600):
        self._cache: dict[str, tuple[Any, float]] = {}
        self._ttl = ttl_seconds

    def get(self, key: str) -> Optional[Any]:
        """Retrieve a value from the cache if it hasn't expired."""
        if key in self._cache:
            value, timestamp = self._cache[key]
            if time.time() - timestamp < self._ttl:
                logging.debug(f"Cache hit for key: {key}")
                return value
            del self._cache[key]
        return None

    def set(self, key: str, value: Any) -> None:
        """Store a value in the cache."""
        self._cache[key] = (value, time.time())

    def clear(self) -> None:
        """Clear all entries from the cache."""
        self._cache.clear()

    def size(self) -> int:
        """Return the current number of entries in the cache."""
        return len(self._cache)
