"""
Core utilities.
"""

from __future__ import annotations

import time
from asyncio import sleep
from collections import deque
from contextlib import suppress
from functools import lru_cache, wraps
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
)

if TYPE_CHECKING:
    from collections.abc import (
        Awaitable,
        Callable,
    )

from ..exceptions import RateLimitError

T = TypeVar("T")


def rate_limit(
    calls_per_minute: int = 60,
) -> Callable[
    [Callable[..., Awaitable[T]]],
    Callable[..., Awaitable[T]],
]:
    """
    Rate limiting decorator for API methods with optimized data structure.

    Args:
        calls_per_minute: Maximum calls allowed per minute

    Returns:
        Decorated function with rate limiting
    """

    def decorator(
        func: Callable[..., Awaitable[T]],
    ) -> Callable[..., Awaitable[T]]:
        call_times: deque[float] = deque()

        @wraps(func)
        async def wrapper(
            *args: Any,  # noqa: ANN401
            **kwargs: Any,  # noqa: ANN401
        ) -> T:
            now = time.time()

            while (
                call_times
                and now - call_times[0] >= 60
            ):
                call_times.popleft()

            if (
                len(call_times)
                >= calls_per_minute
            ):
                sleep_time = 60 - (
                    now - call_times[0]
                )
                raise RateLimitError(
                    int(sleep_time)
                )

            call_times.append(now)
            return await func(*args, **kwargs)

        return wrapper

    return decorator


def retry_on_failure(
    max_retries: int = 3,
    backoff_factor: float = 1.0,
) -> Callable[
    [Callable[..., Awaitable[T]]],
    Callable[..., Awaitable[T]],
]:
    """
    Retry decorator with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        backoff_factor: Multiplier for delay between retries

    Returns:
        Decorated function with retry logic
    """

    def decorator(
        func: Callable[..., Awaitable[T]],
    ) -> Callable[..., Awaitable[T]]:
        @wraps(func)
        async def wrapper(
            *args: Any,  # noqa: ANN401
            **kwargs: Any,  # noqa: ANN401
        ) -> T:
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return await func(
                        *args, **kwargs
                    )
                except Exception as e:
                    last_exception = e
                    if attempt == max_retries:
                        break

                    delay = backoff_factor * (
                        2**attempt
                    )
                    await sleep(delay)

            if last_exception:
                raise last_exception

            # Realistically this should never happen, unless there's a bug in the retry logic.
            raise RuntimeError(
                "[E] / Retry logic failed unexpectedly."
            )

        return wrapper

    return decorator


@lru_cache(maxsize=128)
def get_api_endpoint(
    endpoint_type: str,
) -> str:
    """
    Get API endpoint URL for different service types.

    Args:
        endpoint_type: Type of API endpoint

    Returns:
        Base URL for the specified endpoint type
    """
    endpoints = {
        "users": "https://users.roblox.com",
        "thumbnails": "https://thumbnails.roblox.com",
        "games": "https://games.roblox.com",
        "badges": "https://badges.roblox.com",
        "friends": "https://friends.roblox.com",
        "presence": "https://presence.roblox.com",
    }

    return endpoints.get(
        endpoint_type,
        "https://api.roblox.com",
    )


class APICache:
    """
    In-memory cache for API responses with LRU eviction. (Hard time limit on cache entries.)
    """

    def __init__(
        self,
        ttl: int = 300,
        max_size: int = 1000,
    ) -> None:
        """
        Initialise the cache.

        Args:
            ttl: Time to live for cache entries in seconds
            max_size: Maximum number of cache entries
        """
        self._cache: dict[
            str, dict[str, Any]
        ] = {}
        self._access_order: deque[str] = deque()
        self._ttl = ttl
        self._max_size = max_size

    def get(self, key: str) -> Any | None:  # noqa: ANN401
        """
        Get a value from the cache.
        """
        if key not in self._cache:
            return None

        entry = self._cache[key]
        if (
            time.time() - entry["timestamp"]
            > self._ttl
        ):
            self._remove_key(key)
            return None

        self._access_order.remove(key)
        self._access_order.append(key)

        return entry["value"]

    def set(self, key: str, value: Any) -> None:  # noqa: ANN401
        """
        Set a value in the cache.
        """
        if key in self._cache:
            self._access_order.remove(key)

        while len(self._cache) >= self._max_size:
            lru_key = self._access_order.popleft()
            self._cache.pop(lru_key, None)

        self._cache[key] = {
            "value": value,
            "timestamp": time.time(),
        }
        self._access_order.append(key)

    def _remove_key(self, key: str) -> None:
        """
        Remove a key from cache and access order.
        """
        self._cache.pop(key, None)
        with suppress(ValueError):
            self._access_order.remove(key)

    def clear(self) -> None:
        """
        Clear all cache entries.
        """
        self._cache.clear()
        self._access_order.clear()

    def get_stats(self) -> dict[str, int]:
        """
        Get cache statistics.
        """
        return {
            "size": len(self._cache),
            "max_size": self._max_size,
            "ttl": self._ttl,
        }
