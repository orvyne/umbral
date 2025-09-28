"""
Main client.
"""

from __future__ import annotations

from asyncio import gather
from datetime import datetime
from functools import lru_cache
from typing import Any, Self, cast

from .core import (
    HTTPClient,
    rate_limit,
    retry_on_failure,
)
from .exceptions import UserNotFoundError
from .models import UserAvatar, UserProfile


class UmbralClient:
    """
    Primary client for interacting with the Roblox API.

    This class provides methods to retrieve user profiles,
    avatars, experiences, and other Roblox data through
    a clean, asynchronous interface.
    """

    def __init__(
        self,
        timeout: int = 30,
        cache_ttl: int = 300,
    ) -> None:
        """
        Initialise the Umbral client.

        Args:
            timeout: Request timeout in seconds
            cache_ttl: Cache time-to-live in seconds
        """
        self._http = HTTPClient(
            timeout=timeout,
            cache_ttl=cache_ttl,
        )

    async def close(self) -> None:
        """
        Close the client and cleanup resources.
        """
        await self._http.close()

    async def __aenter__(self) -> Self:
        """
        Async context manager entry.
        """
        return self

    async def __aexit__(
        self, *args: object
    ) -> None:
        """
        Async context manager exit.
        """
        await self.close()

    async def warm_cache(
        self,
        user_ids: list[int],
    ) -> None:
        """
        Pre-warm cache with commonly requested user data.

        Args:
            user_ids: List of user IDs to pre-fetch
        """
        if not user_ids:
            return

        # Batch processing 50 user(s) at once, took me 30 minutes to implement,
        # because I wanted to optimise API calls, and I was very tired (high).
        chunk_size = 50
        tasks = []

        for i in range(
            0, len(user_ids), chunk_size
        ):
            chunk = user_ids[i : i + chunk_size]
            tasks.append(
                self.get_users_batch(chunk)
            )

        await gather(
            *tasks, return_exceptions=True
        )

    @rate_limit(calls_per_minute=120)
    @retry_on_failure(max_retries=3)
    async def get_user(
        self,
        user_id: int,
    ) -> UserProfile:
        """
        Get user profile information by user ID.

        Args:
            user_id: The Roblox user ID

        Returns:
            UserProfile object containing user information

        Raises:
            UserNotFoundError: If the user doesn't exist
        """
        response = await self._http.get(
            "users", f"/v1/users/{user_id}"
        )

        user_profile = self._parse_user_profile(
            response
        )

        try:
            count_tasks = [
                self.get_user_follower_count(
                    user_id
                ),
                self.get_user_following_count(
                    user_id
                ),
                self.get_user_friend_count(
                    user_id
                ),
            ]
            (
                follower_count,
                following_count,
                friend_count,
            ) = await gather(
                *count_tasks,
                return_exceptions=True,
            )

            # Convert any exception results to int to satisfy type checker
            follower_count_val = cast(
                "int",
                follower_count
                if not isinstance(
                    follower_count, Exception
                )
                else 0,
            )
            following_count_val = cast(
                "int",
                following_count
                if not isinstance(
                    following_count,
                    Exception,
                )
                else 0,
            )
            friend_count_val = cast(
                "int",
                friend_count
                if not isinstance(
                    friend_count, Exception
                )
                else 0,
            )

            user_profile = UserProfile(
                id=user_profile.id,
                username=user_profile.username,
                display_name=user_profile.display_name,
                description=user_profile.description,
                created_date=user_profile.created_date,
                follower_count=follower_count_val,
                following_count=following_count_val,
                friend_count=friend_count_val,
                is_verified=user_profile.is_verified,
            )
        except Exception as e:
            print(f"[E] {e}")

        return user_profile

    @rate_limit(calls_per_minute=120)
    @retry_on_failure(max_retries=3)
    async def get_users_batch(
        self,
        user_ids: list[int],
    ) -> list[UserProfile]:
        """
        Get multiple user profiles efficiently in batch.

        Args:
            user_ids: List of Roblox user IDs (max 100)

        Returns:
            List of UserProfile objects

        Raises:
            ValueError: If more than 100 user IDs provided
        """
        if len(user_ids) > 100:
            raise ValueError(
                "[L] / Batch cannot do more than 100 users at once."
            )

        if not user_ids:
            return []

        response = await self._http.post(
            "users",
            "/v1/users",
            data={
                "userIds": user_ids,
                "excludeBannedUsers": True,
            },
        )

        users = []
        for user_data in response.get("data", []):
            if "created" in user_data:
                user_profile = (
                    self._parse_user_profile(
                        user_data
                    )
                )
            else:
                user_profile = UserProfile(
                    id=user_data["id"],
                    username=user_data["name"],
                    display_name=user_data.get(
                        "displayName",
                        user_data["name"],
                    ),
                    description=user_data.get(
                        "description", ""
                    ),
                    created_date=datetime.now(),
                    follower_count=0,
                    following_count=0,
                    friend_count=0,
                    is_verified=user_data.get(
                        "hasVerifiedBadge",
                        False,
                    ),
                )
            users.append(user_profile)

        return users

    @rate_limit(calls_per_minute=120)
    @retry_on_failure(max_retries=3)
    async def get_user_by_username(
        self,
        username: str,
    ) -> UserProfile:
        """
        Get user profile information by username.

        Args:
            username: The Roblox username

        Returns:
            UserProfile object containing user information

        Raises:
            UserNotFoundError: If the user doesn't exist
        """
        response = await self._http.post(
            "users",
            "/v1/usernames/users",
            data={
                "usernames": [username],
                "excludeBannedUsers": True,
            },
        )

        if (
            not response.get("data")
            or len(response["data"]) == 0
        ):
            raise UserNotFoundError(username)

        user_data = response["data"][0]
        user_id = user_data["id"]

        return await self.get_user(user_id)

    @rate_limit(calls_per_minute=180)
    @retry_on_failure(max_retries=3)
    async def get_user_avatar(
        self,
        user_id: int,
    ) -> UserAvatar:
        """
        Get user's avatar image information.

        Args:
            user_id: The Roblox user ID

        Returns:
            UserAvatar object containing avatar URLs
        """
        avatar_tasks = [
            self._http.get(
                "thumbnails",
                "/v1/users/avatar-headshot",
                params={
                    "userIds": str(user_id),
                    "size": "48x48",
                    "format": "Png",
                },
            ),
            self._http.get(
                "thumbnails",
                "/v1/users/avatar-bust",
                params={
                    "userIds": str(user_id),
                    "size": "48x48",
                    "format": "Png",
                },
            ),
            self._http.get(
                "thumbnails",
                "/v1/users/avatar",
                params={
                    "userIds": str(user_id),
                    "size": "420x420",
                    "format": "Png",
                },
            ),
        ]

        (
            headshot_response,
            bust_response,
            full_body_response,
        ) = await gather(
            *avatar_tasks,
            return_exceptions=True,
        )

        headshot_response_val = (
            headshot_response
            if not isinstance(
                headshot_response, Exception
            )
            else {}
        )
        bust_response_val = (
            bust_response
            if not isinstance(
                bust_response, Exception
            )
            else {}
        )
        full_body_response_val = (
            full_body_response
            if not isinstance(
                full_body_response, Exception
            )
            else {}
        )

        headshot_url = (
            self._extract_thumbnail_url(
                cast(
                    "dict[str, Any]",
                    headshot_response_val,
                )
            )
        )
        bust_url = self._extract_thumbnail_url(
            cast(
                "dict[str, Any]",
                bust_response_val,
            )
        )
        full_body_url = (
            self._extract_thumbnail_url(
                cast(
                    "dict[str, Any]",
                    full_body_response_val,
                )
            )
        )

        return UserAvatar(
            user_id=user_id,
            headshot_url=headshot_url,
            bust_url=bust_url,
            full_body_url=full_body_url,
        )

    @rate_limit(calls_per_minute=180)
    @retry_on_failure(max_retries=3)
    async def get_user_avatar_optimized(
        self,
        user_id: int,
        headshot_size: str = "48x48",
        bust_size: str = "48x48",
        full_body_size: str = "150x150",
    ) -> UserAvatar:
        """
        Get user's avatar with configurable sizes for bandwidth optimization.

        Args:
            user_id: The Roblox user ID
            headshot_size: Size for headshot (e.g., "48x48", "150x150", "420x420")
            bust_size: Size for bust image
            full_body_size: Size for full body image

        Returns:
            UserAvatar object containing avatar URLs
        """
        avatar_tasks = [
            self._http.get(
                "thumbnails",
                "/v1/users/avatar-headshot",
                params={
                    "userIds": str(user_id),
                    "size": headshot_size,
                    "format": "Png",
                },
            ),
            self._http.get(
                "thumbnails",
                "/v1/users/avatar-bust",
                params={
                    "userIds": str(user_id),
                    "size": bust_size,
                    "format": "Png",
                },
            ),
            self._http.get(
                "thumbnails",
                "/v1/users/avatar",
                params={
                    "userIds": str(user_id),
                    "size": full_body_size,
                    "format": "Png",
                },
            ),
        ]

        (
            headshot_response,
            bust_response,
            full_body_response,
        ) = await gather(
            *avatar_tasks,
            return_exceptions=True,
        )

        headshot_url = (
            self._extract_thumbnail_url(
                cast(
                    "dict[str, Any]",
                    headshot_response
                    if not isinstance(
                        headshot_response,
                        Exception,
                    )
                    else {},
                )
            )
        )
        bust_url = self._extract_thumbnail_url(
            cast(
                "dict[str, Any]",
                bust_response
                if not isinstance(
                    bust_response, Exception
                )
                else {},
            )
        )
        full_body_url = (
            self._extract_thumbnail_url(
                cast(
                    "dict[str, Any]",
                    full_body_response
                    if not isinstance(
                        full_body_response,
                        Exception,
                    )
                    else {},
                )
            )
        )

        return UserAvatar(
            user_id=user_id,
            headshot_url=headshot_url,
            bust_url=bust_url,
            full_body_url=full_body_url,
        )

    @rate_limit(calls_per_minute=120)
    @retry_on_failure(max_retries=3)
    async def get_user_followers(
        self,
        user_id: int,
        limit: int = 10,
    ) -> list[UserProfile]:
        """
        Get user's followers.

        Args:
            user_id: The Roblox user ID
            limit: Maximum number of followers to return

        Returns:
            List of UserProfile objects for followers
        """
        response = await self._http.get(
            "friends",
            f"/v1/users/{user_id}/followers",
            params={
                "limit": min(limit, 100),
                "sortOrder": "Desc",
            },
        )

        followers = []
        for follower_data in response.get(
            "data", []
        ):
            follower = (
                self._parse_user_profile_simple(
                    follower_data
                )
            )
            followers.append(follower)

        return followers

    @rate_limit(calls_per_minute=120)
    @retry_on_failure(max_retries=3)
    async def get_user_following(
        self,
        user_id: int,
        limit: int = 10,
    ) -> list[UserProfile]:
        """
        Get users that this user is following.

        Args:
            user_id: The Roblox user ID
            limit: Maximum number of following to return

        Returns:
            List of UserProfile objects for users being followed
        """
        response = await self._http.get(
            "friends",
            f"/v1/users/{user_id}/followings",
            params={
                "limit": min(limit, 100),
                "sortOrder": "Desc",
            },
        )

        following = []
        for following_data in response.get(
            "data", []
        ):
            user = (
                self._parse_user_profile_simple(
                    following_data
                )
            )
            following.append(user)

        return following

    @rate_limit(calls_per_minute=120)
    @retry_on_failure(max_retries=3)
    async def get_user_friends(
        self,
        user_id: int,
        limit: int = 10,
    ) -> list[UserProfile]:
        """
        Get user's friends.

        Args:
            user_id: The Roblox user ID
            limit: Maximum number of friends to return

        Returns:
            List of UserProfile objects for friends
        """
        response = await self._http.get(
            "friends",
            f"/v1/users/{user_id}/friends",
            params={"limit": min(limit, 100)},
        )

        friends = []
        for friend_data in response.get(
            "data", []
        ):
            friend = (
                self._parse_user_profile_simple(
                    friend_data
                )
            )
            friends.append(friend)

        return friends

    @rate_limit(calls_per_minute=60)
    @retry_on_failure(max_retries=3)
    async def get_user_follower_count(
        self,
        user_id: int,
    ) -> int:
        """
        Get user's follower count.

        Args:
            user_id: The Roblox user ID

        Returns:
            Number of followers
        """
        response = await self._http.get(
            "friends",
            f"/v1/users/{user_id}/followers/count",
        )

        return response.get("count", 0)

    @rate_limit(calls_per_minute=60)
    @retry_on_failure(max_retries=3)
    async def get_user_following_count(
        self,
        user_id: int,
    ) -> int:
        """
        Get count of users this user is following.

        Args:
            user_id: The Roblox user ID

        Returns:
            Number of users being followed
        """
        response = await self._http.get(
            "friends",
            f"/v1/users/{user_id}/followings/count",
        )

        return response.get("count", 0)

    @rate_limit(calls_per_minute=60)
    @retry_on_failure(max_retries=3)
    async def get_user_friend_count(
        self,
        user_id: int,
    ) -> int:
        """
        Get user's friend count.

        Args:
            user_id: The Roblox user ID

        Returns:
            Number of friends
        """
        response = await self._http.get(
            "friends",
            f"/v1/users/{user_id}/friends/count",
        )

        return response.get("count", 0)

    @staticmethod
    def _parse_user_profile(
        data: dict,
    ) -> UserProfile:
        """
        Parse API response into UserProfile object.
        """
        created_date = datetime.fromisoformat(
            data["created"].replace("Z", "+00:00")
        )
        # Everything here is populated seperatly.
        return UserProfile(
            id=data["id"],
            username=data["name"],
            display_name=data["displayName"],
            description=data.get(
                "description", ""
            ),
            created_date=created_date,
            follower_count=0,
            following_count=0,
            friend_count=0,
            is_verified=data.get(
                "hasVerifiedBadge", False
            ),
        )

    @staticmethod
    def _parse_user_profile_simple(
        data: dict,
    ) -> UserProfile:
        """
        Parse simple API response into UserProfile object.
        """
        return UserProfile(
            id=data["id"],
            username=data["name"],
            display_name=data["displayName"],
            description="",
            created_date=datetime.now(),
            follower_count=0,
            following_count=0,
            friend_count=0,
            is_verified=data.get(
                "hasVerifiedBadge", False
            ),
        )

    @staticmethod
    def _extract_thumbnail_url(
        response: dict[str, Any],
    ) -> str:
        """
        Extract thumbnail URL from API response.
        """
        if (
            not response.get("data")
            or len(response.get("data", [])) == 0
        ):
            return ""

        return response.get("data", [{}])[0].get(
            "imageUrl", ""
        )

    @staticmethod
    @lru_cache(maxsize=64)
    def _get_default_avatar_url(
        size: str = "48x48",
    ) -> str:
        """
        Get default avatar URL for fallback cases.
        """
        return f"https://tr.rbxcdn.com/default-avatar-{size}.png"
