"""
Configuration settings.
"""

from __future__ import annotations

from dataclasses import dataclass, field


def _default_avatar_sizes() -> dict[str, str]:
    """Default avatar sizes for different types."""
    return {
        "headshot": "48x48",
        "bust": "48x48",
        "full_body": "150x150",
    }


@dataclass
class OptimizationConfig:
    """
    Configuration for umbral(s) performance optimizations.

    I'll be changing these accordingly between updates.
    """

    connection_pool_size: int = 100
    connections_per_host: int = 30
    dns_cache_ttl: int = 300
    keepalive_timeout: int = 30
    request_timeout: int = 30

    cache_ttl: int = 300
    cache_max_size: int = 1000

    default_rate_limit: int = 120
    aggressive_rate_limit: int = 180
    conservative_rate_limit: int = 60

    max_batch_size: int = 100
    optimal_batch_size: int = 50

    max_metrics_stored: int = 1000

    default_avatar_sizes: dict[str, str] = field(
        default_factory=_default_avatar_sizes
    )

    def __post_init__(self) -> None:
        # field(default_factory)
        pass

    @classmethod
    def high_performance(
        cls,
    ) -> OptimizationConfig:
        """
        Configuration optimized for maximum performance.
        """
        return cls(
            connection_pool_size=200,
            connections_per_host=50,
            dns_cache_ttl=600,
            cache_ttl=600,
            cache_max_size=2000,
            default_rate_limit=180,
            optimal_batch_size=75,
            default_avatar_sizes={
                "headshot": "48x48",
                "bust": "48x48",
                "full_body": "150x150",
            },
        )

    @classmethod
    def low_bandwidth(
        cls,
    ) -> OptimizationConfig:
        """
        Configuration optimized for low bandwidth usage.
        """
        return cls(
            connection_pool_size=50,
            connections_per_host=10,
            cache_ttl=900,  # This may not be suitable for all use cases, but it helps reduce API calls etc.
            cache_max_size=500,
            default_rate_limit=60,
            optimal_batch_size=25,
            default_avatar_sizes={
                "headshot": "30x30",
                "bust": "30x30",
                "full_body": "48x48",
            },
        )

    @classmethod
    def balanced(cls) -> OptimizationConfig:
        """
        Balanced configuration for general use.
        """
        return cls()


default_config = OptimizationConfig.balanced()
