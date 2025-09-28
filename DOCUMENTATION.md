# Umbral Documentation

<div align="center">

**Roblox API wrapper wrritten in Python (this documentation took me 2 hours and a half).**
In the eternal struggle between human creativity and the structured demands of documentation, one must acknowledge that the art of documenting code is but a necessary burden on the path to enlightenment

</div>

---

## Quick Start

### Installation

```bash
pip install git+ssh://git@github.com/orvyne/umbral.git
```

### Basic Usage

```python
from asyncio import run
from umbral import UmbralClient

async def main():
    async with UmbralClient() as client:

        user = await client.get_user(555)
        print(f"G'day {user.display_name}!")

run(main())
```

---

## Table of Contents

- [Client Setup](#client-setup)
- [User Operations](#user-operations)
- [Avatar Management](#avatar-management)
- [Social Features](#social-features)
- [Performance & Caching](#performance--caching)
- [Error Handling](#error-handling)
- [Configuration](#configuration)
- [Examples & Patterns](#examples--patterns)

---

## Client Setup

### Basic Client Initialisation

```python
from umbral import UmbralClient

# The default client with it's default settings.
async with UmbralClient() as client:
    # code
    pass
```

### Advanced Configuration

```python
# Customised with timeout and cache settings ()
client = UmbralClient(
    timeout=60,        # Request timeout in seconds..
    cache_ttl=600      # Cache time-to-live in seconds..
)

# Don't forget to close when you're done! (or you're fucked).
await client.close()
```

### Context Manager (Recommended)

```python
# It automatically handles the cleanuo.
async with UmbralClient(timeout=30) as client:
    user = await client.get_user(1)
```

---

## User Operations

### Getting User Information

#### By User ID

```python
async with UmbralClient() as client:
    user = await client.get_user(555)
    
    print(f"Username | {user.username}")
    print(f"Display  | {user.display_name}")
    print(f"Bio      |{user.description}")
    print(f"Created  | {user.created_date}")
    print(f"Followers| {user.follower_count:,}")
    print(f"Following| {user.following_count:,}")
    print(f"Friends  | {user.friend_count:,}")
    print(f"Verified | {'Yes' if user.is_verified else 'No'}")
```

#### By Username

```python
async with UmbralClient() as client:
    try:
        user = await client.get_user_by_username("umbral")
        print(f"[F] {user.display_name} / ID - ({user.id})")
    except UserNotFoundError:
        print("That user doesn't exist, mate!")

#### Batch User Retrieval
```

#### Batch User Retrieval

```python
async with UmbralClient() as client:
    user_ids = [1, 2, 3, 261]  # I added batch to be 100 users at once. (I may increase).
    users = await client.get_users_batch(user_ids)
    
    for user in users:
        print(f"{user.username} / {user.follower_count} followers")
```

### User Properties

The `UserProfile` object contains these properties:

| Property | Type | Description |
|----------|------|-------------|
| `id` | `int` | Unique user identifier |
| `username` | `str` | Current username |
| `display_name` | `str` | Display name shown to others |
| `description` | `str` | User's bio/description |
| `created_date` | `datetime` | Account creation date |
| `follower_count` | `int` | Number of followers |
| `following_count` | `int` | Number of users being followed |
| `friend_count` | `int` | Number of friends |
| `is_verified` | `bool` | Whether user has verified badge |

#### Computed Properties

```python
user = await client.get_user(1)

#profile URL
print(f"Profile / {user.profile_url}")

# Check premium status (placeholder for future implementation).
# I have to study their api again for this, which will be in next update.
print(f"Premium / {user.is_premium}")
```

---

## Avatar Management

### Basic Avatar Retrieval

```python
async with UmbralClient() as client:
    avatar = await client.get_user_avatar(555)
    
    print(f"Headshot / {avatar.headshot_url}")
    print(f"Bust / {avatar.bust_url}")
    print(f"Full Body / {avatar.full_body_url}")
    
    # Default image (same as headshot).
    print(f"Default: {avatar.image_url}")
```

### Optimised Avatar Sizes

```python
async with UmbralClient() as client:
    # I implemented custom sizes to use.
    avatar = await client.get_user_avatar_optimized(
        user_id=5555,
        headshot_size="150x150",    #larger headshot
        bust_size="100x100",        #medium bust
        full_body_size="420x420"    #high-res full body
    )
    
```

### Available Avatar Sizes

| Size | Use Case | Quality |
|------|----------|---------|
| `30x30` | Tiny icons | Low |
| `48x48` | Standard thumbnails | Low |
| `60x60` | Small avatars | Low |
| `75x75` | Medium icons | Medium |
| `100x100` | Large thumbnails | Medium |
| `150x150` | Profile pictures | High |
| `180x180` | Large profiles | High |
| `352x352` | High-resolution | Very High |
| `420x420` | Maximum quality | Ultra High |

---

## Social Features

### Followers Management

```python
async with UmbralClient() as client:
    # Pull the followers (only).
    count = await client.get_user_follower_count(555)
    print(f"This user has {count:,} followers")
    
    # Pull the actual follower profiles (limited).
    followers = await client.get_user_followers(555, limit=20)
    for follower in followers:
        print(f"- {follower.display_name} (@{follower.username})")
```

### Following Management

```python
async with UmbralClient() as client:
    # Following ()
    count = await client.get_user_following_count(555)
    
    # Pull the complete list of users someone is following. I actually like that I made this, lol.

    following = await client.get_user_following(555, limit=50)
    print(f"Following ({len(following)}) users /")
    for user in following:
        print(f"- {user.display_name}")
```

### Friends Management

```python
async with UmbralClient() as client:
    # Pull user(S) friend count./
    friend_count = await client.get_user_friend_count(955)
    
    # Pull user(s) friend list.
    friends = await client.get_user_friends(5654654, limit=30)
    print(f"Friends ({len(friends)}/{friend_count}):")
    for friend in friends:
        print(f"- {friend.username}")
```

---

## Performance & Caching

### Cache Warming

Pre-load frequently accessed users into cache:

```python
async with UmbralClient() as client:
    # Warm cache with popular users.
    popular_users = [1, 2, 3, 156, 261]
    await client.warm_cache(popular_users)
    
    # These requests will now be lightning fast!
    for user_id in popular_users:
        user = await client.get_user(user_id)
        print(f"cached {user.username}")
```

### Performance Monitoring

```python
from umbral.core import performance_monitor

async with UmbralClient() as client:
    await client.get_user(1)
    await client.get_user(2)
    
    # I added a built-in performance monitor, so you can viewthe speed.
    stats = performance_monitor.get_stats()
    print(f"Average response time: {stats['avg_duration']}s")
    print(f"Success rate: {stats['success_rate']}%")
    print(f"Cache hit rate: {stats['cache_hit_rate']}%")
```

### Rate Limiting

Umbral automatically handles rate limiting:

```python
# I implemented these decorators into umbral, for automation.
@rate_limit(calls_per_minute=120)
@retry_on_failure(max_retries=3)
async def get_user(self, user_id: int):
    pass
```

---

## Error Handling

### Exception Types

```python
from umbral.exceptions import (
    RobloxAPIError,      # Base exception..
    UserNotFoundError,   # User doesn't exist..
    RateLimitError,      # Rate limit exceeded..
    NetworkError         # Network issues..
)
```

### Comprehensive Error Handling

```python
async with UmbralClient() as client:
    try:
        user = await client.get_user(999999999999)
        
    except UserNotFoundError as e:
        print(f"[U] {e.user_identifier}")
        
    except RateLimitError as e:
        print(f"[R] {e.retry_after}s")
        
    except NetworkError as e:
        print(f"[N] {e.original_error}")
        
    except RobloxAPIError as e:
        print(f"[A] {e.message} ({e.status_code})")
        
    except Exception as e:
        print(f"[E] {e}")
```

### Graceful Degradation

```python
async def get_user_safely(client, user_id):
    """
    Get user with fallback handling.
    """
    try:
        return await client.get_user(user_id)
    except UserNotFoundError:
        return None
    except (RateLimitError, NetworkError):
        return create_placeholder_user(user_id)
```

---

## Configuration

### Client Configuration

```python
client = UmbralClient(
    timeout=30,         # Request timeout (seconds).
    cache_ttl=300       # Cache expiry (seconds).
)
```

### Environment Variables

Create a `.env` file:

```env
UMBRAL_TIMEOUT=60
UMBRAL_CACHE_TTL=600
UMBRAL_DEBUG=true
```

Load in your application:

```python
import os
from dotenv import load_dotenv

load_dotenv()

client = UmbralClient(
    timeout=int(os.getenv('UMBRAL_TIMEOUT', 30)),
    cache_ttl=int(os.getenv('UMBRAL_CACHE_TTL', 300))
)
```

---

## Examples & Patterns

### Bulk User Analysis

```python
async def analyse_user_group(user_ids):
    """
    Analyse a group of users efficiently.
    """
    async with UmbralClient() as client:
        # Batch fetch for efficiency, this is a bad example, but oh well  guess
        users = await client.get_users_batch(user_ids)
        
        total_followers = sum(user.follower_count for user in users)
        verified_count = sum(1 for user in users if user.is_verified)
        avg_followers = total_followers / len(users) if users else 0
        
        print(f"Group Analysis Results")
        print(f"Users analysed/ {len(users)}")
        print(f"Total followers/ {total_followers:,}")
        print(f"Average followers/ {avg_followers:,.1f}")
        print(f"Verified users/ {verified_count} ({verified_count/len(users)*100:.1f}%)")
        
        # Top users by followers. ()
        top_users = sorted(users, key=lambda u: u.follower_count, reverse=True)[:5]
        print(f"\nTop Users |")
        for i, user in enumerate(top_users, 1):
            print(f"{i}. {user.display_name} / {user.follower_count:,} followers")

# usagee
user_ids = [1, 2, 3, 156, 261, 5299]
await analyse_user_group(user_ids)
```

### Caching Strategy

```python
class UserService:
    """
    Service class with intelligent caching.
    """
    
    def __init__(self):
        self.client = UmbralClient(cache_ttl=1800)  # 30 min cache
        self._user_cache = {}
    
    async def get_user_with_fallback(self, user_id: int):
        """
        Get user with multiple fallback strategies.
        """
        try:
            user = await self.client.get_user(user_id)
            self._user_cache[user_id] = user
            return user
            
        except (RateLimitError, NetworkError):
            if user_id in self._user_cache:
                return self._user_cache[user_id]
            raise
    
    async def warm_popular_users(self):
        """
        Pre-load popular users.
        """
        popular_ids = [1, 2, 3, 156, 261]  # Well-known users
        await self.client.warm_cache(popular_ids)
```

### CLI Tool Pattern

```python
"""
Custom CLI tool using Umbral.
"""

from asyncio import run
import argparse
from umbral import UmbralClient

async def search_users(pattern: str, limit: int = 5):
    """
    Search for users matching a pattern.
    """
    async with UmbralClient() as client:
        # This would be implemented when search is available.
        print(f"Searching for users matching '{pattern}'...")
        # For now, demonstrate with known users.
        known_users = [1, 2, 3, 156, 261]
        users = await client.get_users_batch(known_users[:limit])
        
        for user in users:
            if pattern.lower() in user.username.lower():
                print(f"{user.display_name} (@{user.username})")

def main():
    parser = argparse.ArgumentParser(description="Roblox user Search")
    parser.add_argument("pattern", help="Search pattern")
    parser.add_argument("--limit", type=int, default=5, help="Max results")
    
    args = parser.parse_args()
    run(search_users(args.pattern, args.limit))

if __name__ == "__main__":
    main()
```


---

## API Reference

### UmbralClient

#### Constructor
```python
UmbralClient(timeout: int = 30, cache_ttl: int = 300)
```

#### User Methods
- `get_user(user_id: int) -> UserProfile`
- `get_user_by_username(username: str) -> UserProfile`
- `get_users_batch(user_ids: List[int]) -> List[UserProfile]`

#### Avatar Methods
- `get_user_avatar(user_id: int) -> UserAvatar`
- `get_user_avatar_optimized(user_id: int, **sizes) -> UserAvatar`

#### Social Methods
- `get_user_followers(user_id: int, limit: int = 10) -> List[UserProfile]`
- `get_user_following(user_id: int, limit: int = 10) -> List[UserProfile]`
- `get_user_friends(user_id: int, limit: int = 10) -> List[UserProfile]`
- `get_user_follower_count(user_id: int) -> int`
- `get_user_following_count(user_id: int) -> int`
- `get_user_friend_count(user_id: int) -> int`

#### Utility Methods
- `warm_cache(user_ids: List[int]) -> None`
- `close() -> None`

---
