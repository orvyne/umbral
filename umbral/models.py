"""
Data models.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime


@dataclass(frozen=True)
class UserProfile:
    """
    Represents a Roblox user's profile information.
    """

    id: int
    username: str
    display_name: str
    description: str
    created_date: datetime
    follower_count: int
    following_count: int
    friend_count: int
    is_verified: bool

    @property
    def profile_url(self) -> str:
        """
        Get the user's profile URL.
        """
        return f"https://www.roblox.com/users/{self.id}/profile"

    @property
    def is_premium(self) -> bool:
        """
        Check if user has premium status.
        """
        return False  # Placeholder for implementation,
        # I will update this in the future accordingly to the API response.


@dataclass(frozen=True)
class UserAvatar:
    """
    Represents a user's avatar image information.
    """

    user_id: int
    headshot_url: str
    bust_url: str  # Do not ask my why I named it this, lol (please).
    full_body_url: str

    @property
    def image_url(self) -> str:
        """
        Get the default avatar image URL (headshot).
        """
        return self.headshot_url

    @property
    def thumbnail_url(self) -> str:
        """Get a smaller thumbnail version."""
        return self.headshot_url.replace(
            "48x48", "30x30"
        )


@dataclass(frozen=True)
class UserConnection:
    """
    Represents a user's social connections.

    In the documentation, I have it set to [friends],
    but whenever Roblox updates their API, I will then edit it to use [connections].
    """

    user_id: int
    connection_type: str  # "follower" or "following" I probably should implement a proper enum for this...sigh.
    connected_user_id: int
    connected_username: str
    connected_display_name: str
    connection_date: datetime | None = None


@dataclass(frozen=True)
class Badge:
    """
    Represents a Roblox badge.

    Future additions will use this as a base class.
    """

    id: int
    name: str
    description: str
    icon_url: str
    rarity: str
    awarded_date: datetime | None = None

    @property
    def badge_url(self) -> str:
        """
        Get the badge's URL.
        """
        return f"https://www.roblox.com/badges/{self.id}"
