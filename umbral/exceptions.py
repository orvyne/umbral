"""
Custom exceptions.
"""

from __future__ import annotations


class RobloxAPIError(Exception):
    """
    Base exception class for all Roblox API errors.
    """

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
    ) -> None:
        """Initialise a Roblox API error.

        Args:
            message: Error description
            status_code: HTTP status code if applicable
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class UserNotFoundError(RobloxAPIError):
    """
    Raised when a requested user cannot be found.
    """

    def __init__(
        self, user_identifier: str
    ) -> None:
        """
        Initialise a user not found error.

        Args:
            user_identifier: The user ID or username
        """
        message = f"[NOT FOUND] / {user_identifier} could not be found."
        super().__init__(message)
        self.user_identifier = user_identifier


class RateLimitError(RobloxAPIError):
    """
    Raised when API rate limits are exceeded.
    """

    def __init__(
        self,
        retry_after: int | None = None,
    ) -> None:
        """
        Initialise a rate limit error.

        Args:
            retry_after: Seconds to wait before retrying
        """
        message = "[API] / rate limited"
        if retry_after:
            message += f", retry after / {retry_after} seconds."
        super().__init__(message)
        self.retry_after = retry_after


class NetworkError(RobloxAPIError):
    """
    Raised when network-related errors occur.
    """

    def __init__(
        self,
        original_error: Exception,
    ) -> None:
        """
        Initialise a network-error, if it (ever) occurs.

        Args:
            original_error: The underlying network exception
        """
        message = (
            f"[Network] / {original_error!s}."
        )
        super().__init__(message)
        self.original_error = original_error
