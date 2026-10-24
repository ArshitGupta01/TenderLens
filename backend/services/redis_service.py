"""
TenderLens - Redis Atomic Cache & Task Broker Service
=====================================================
Provides low-latency atomic caching for tender discovery, TinyFetch ETag caches,
and task state coordination with fallback to local in-memory TTL store.
"""

import os
import json
import logging
from typing import Any, Optional, Dict
import redis

logger = logging.getLogger("tenderlens.redis")


class RedisService:
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self._client: Optional[redis.Redis] = None
        self._memory_cache: Dict[str, tuple[Any, float]] = {}
        self._is_connected = False
        self._init_connection()

    def _init_connection(self):
        try:
            self._client = redis.from_url(
                self.redis_url,
                socket_connect_timeout=2.0,
                decode_responses=True
            )
            self._client.ping()
            self._is_connected = True
            logger.info("Connected to Redis at %s", self.redis_url)
        except Exception as e:
            self._is_connected = False
            self._client = None
            logger.info("Redis not reachable (%s); activating in-memory caching fallback.", e)

    @property
    def is_connected(self) -> bool:
        return self._is_connected

    def get(self, key: str) -> Optional[Any]:
        if self._is_connected and self._client:
            try:
                val = self._client.get(key)
                if val:
                    try:
                        return json.loads(val)
                    except json.JSONDecodeError:
                        return val
            except Exception as e:
                logger.warning("Redis get error for %s: %s", key, e)

        # In-memory fallback
        import time
        if key in self._memory_cache:
            val, expiry = self._memory_cache[key]
            if expiry == 0 or time.time() < expiry:
                return val
            else:
                del self._memory_cache[key]
        return None

    def set(self, key: str, value: Any, ttl_seconds: int = 3600) -> bool:
        serialized = json.dumps(value) if not isinstance(value, str) else value
        if self._is_connected and self._client:
            try:
                self._client.set(key, serialized, ex=ttl_seconds)
                return True
            except Exception as e:
                logger.warning("Redis set error for %s: %s", key, e)

        # In-memory fallback
        import time
        expiry = (time.time() + ttl_seconds) if ttl_seconds > 0 else 0
        self._memory_cache[key] = (value, expiry)
        return True

    def delete(self, key: str) -> bool:
        if self._is_connected and self._client:
            try:
                self._client.delete(key)
            except Exception:
                pass
        self._memory_cache.pop(key, None)
        return True

    def cache_search_results(self, portal: str, query: str, results: list) -> bool:
        key = f"search:{portal}:{query.strip().lower()}"
        return self.set(key, results, ttl_seconds=1800)

    def get_cached_search_results(self, portal: str, query: str) -> Optional[list]:
        key = f"search:{portal}:{query.strip().lower()}"
        return self.get(key)


# Global singleton
redis_service = RedisService()
