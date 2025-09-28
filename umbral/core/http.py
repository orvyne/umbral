"""
HTTP client.
"""

from __future__ import annotations

import builtins
from asyncio import sleep
from json import JSONDecodeError
from typing import TYPE_CHECKING, Any, Self

if TYPE_CHECKING:
    from types import TracebackType

from aiohttp import (
    ClientError,
    ClientResponse,
    ClientSession,
    ClientTimeout,
    ContentTypeError,
    TCPConnector,
)

from ..exceptions import (
    NetworkError,
    RateLimitError,
    RobloxAPIError,
    UserNotFoundError,
)
from .utils import APICache, get_api_endpoint


class HTTPClient:
    """
    Asynchronous HTTP client for Roblox API requests.
    """

    def __init__(
        self,
        timeout: int = 30,
        cache_ttl: int = 300,
    ) -> None:
        """
        Initialise the HTTP client.

        Args:
            timeout: Request timeout in seconds
            cache_ttl: Cache time-to-live in seconds
        """
        self._session: ClientSession | None = None
        self._timeout = ClientTimeout(
            total=timeout
        )
        self._cache = APICache(ttl=cache_ttl)
        self._headers = {
            "User-Agent": "Umbral/1.0.0 (+https://github.com/orvyne/umbral)",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Accept-Encoding": "gzip, deflate, br",
        }

        self._connector = TCPConnector(
            limit=100,
            limit_per_host=30,
            ttl_dns_cache=300,
            use_dns_cache=True,
            keepalive_timeout=30,
            enable_cleanup_closed=True,
        )

    @property
    def session(self) -> ClientSession:
        """
        Get or create the aiohttp session.
        """
        if (
            self._session is None
            or self._session.closed
        ):
            self._session = ClientSession(
                timeout=self._timeout,
                headers=self._headers,
                connector=self._connector,
            )
        return self._session

    async def close(self) -> None:
        """
        Close the HTTP session and connector.
        """
        if (
            self._session
            and not self._session.closed
        ):
            await self._session.close()
        if (
            hasattr(self, "_connector")
            and not self._connector.closed
        ):
            await self._connector.close()

        await sleep(0.1)

    async def __aenter__(self) -> Self:
        """
        Async context manager entry.
        """
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """
        Async context manager exit.
        """
        await self.close()

    async def request(
        self,
        method: str,
        endpoint_type: str,
        path: str,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        use_cache: bool = True,
    ) -> dict[str, Any]:
        """
        Make an HTTP request to a Roblox API endpoint.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint_type: Type of API endpoint
            path: API path
            params: Query parameters
            data: Request body data
            use_cache: Whether to use response caching

        Returns:
            JSON response data

        Raises:
            RobloxAPIError: For API-related errors
            NetworkError: For network-related errors
        """
        base_url = get_api_endpoint(endpoint_type)
        url = f"{base_url}{path}"

        cache_key = f"{method}:{url}:{params!s}"
        if method == "GET" and use_cache:
            cached_response = self._cache.get(
                cache_key
            )
            if cached_response is not None:
                return cached_response

        try:
            async with self.session.request(
                method=method,
                url=url,
                params=params,
                json=data,
            ) as response:
                await (
                    self._handle_response_errors(
                        response
                    )
                )

                response_data = (
                    await response.json()
                )

                if method == "GET" and use_cache:
                    self._cache.set(
                        cache_key,
                        response_data,
                    )

                return response_data

        except ClientError as e:
            raise NetworkError(e) from e
        except builtins.TimeoutError as e:
            raise NetworkError(e) from e

    async def _handle_response_errors(
        self,
        response: ClientResponse,
    ) -> None:
        """
        Handle HTTP response errors.

        Args:
            response: aiohttp response object

        Raises:
            UserNotFoundError: For 404 errors on user endpoints
            RateLimitError: For 429 rate limit errors
            RobloxAPIError: For other API errors
        """
        if response.status == 200:
            return

        if response.status == 404:
            if "/users/" in str(response.url):
                raise UserNotFoundError(
                    "[A] / User unable to be found."
                )
            raise RobloxAPIError(
                "[A] / Roblox(s) API unable to be reached.",
                response.status,
            )

        if response.status == 429:
            retry_after = response.headers.get(
                "Retry-After"
            )
            retry_seconds = (
                int(retry_after)
                if retry_after
                else None
            )
            raise RateLimitError(retry_seconds)

        try:
            error_data = await response.json()
            error_message = error_data.get(
                "message",
                f"HTTP / {response.status}",
            )
        except (
            JSONDecodeError,
            ContentTypeError,
        ):
            error_message = (
                f"HTTP / {response.status}"
            )

        raise RobloxAPIError(
            error_message, response.status
        )

    async def get(
        self,
        endpoint_type: str,
        path: str,
        params: dict[str, Any] | None = None,
        use_cache: bool = True,
    ) -> dict[str, Any]:
        """
        Make a GET request.
        """
        return await self.request(
            "GET",
            endpoint_type,
            path,
            params=params,
            use_cache=use_cache,
        )

    async def post(
        self,
        endpoint_type: str,
        path: str,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Make a POST request.
        """
        return await self.request(
            "POST",
            endpoint_type,
            path,
            params=params,
            data=data,
            use_cache=False,
        )
