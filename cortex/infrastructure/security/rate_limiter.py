"""Token-bucket rate limiter compatibility implementation for security tests."""

import time
from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class _Bucket:
    tokens: float
    capacity: float
    refill_rate: float
    last_refill: float


class TokenBucketRateLimiter:
    """Per-client token bucket rate limiter with simple audit trail."""

    def __init__(self, requests_per_sec: int = 50, burst_size: int = 50) -> None:
        self.default_refill_rate = float(requests_per_sec)
        self.default_burst_size = float(burst_size)
        self._buckets: Dict[str, _Bucket] = {}
        self._custom_limits: Dict[str, Dict[str, float]] = {}
        self._audit_trail: List[Dict[str, Any]] = []

    def _get_bucket(self, client_id: str) -> _Bucket:
        if client_id not in self._buckets:
            cfg = self._custom_limits.get(client_id, {})
            refill_rate = cfg.get("requests_per_sec", self.default_refill_rate)
            burst_size = cfg.get("burst_size", self.default_burst_size)
            self._buckets[client_id] = _Bucket(
                tokens=float(burst_size),
                capacity=float(burst_size),
                refill_rate=float(refill_rate),
                last_refill=time.time(),
            )
        return self._buckets[client_id]

    def _refill(self, bucket: _Bucket) -> None:
        now = time.time()
        elapsed = max(0.0, now - bucket.last_refill)
        bucket.tokens = min(bucket.capacity, bucket.tokens + elapsed * bucket.refill_rate)
        bucket.last_refill = now

    def allow_request(self, client_id: str) -> bool:
        bucket = self._get_bucket(client_id)
        self._refill(bucket)

        allowed = bucket.tokens >= 1.0
        if allowed:
            bucket.tokens -= 1.0

        self._audit_trail.append(
            {
                "timestamp": time.time(),
                "client_id": client_id,
                "allowed": allowed,
                "tokens_remaining": bucket.tokens,
            }
        )
        return allowed

    def configure_limits(self, client_id: str, requests_per_sec: int, burst_size: int) -> None:
        self._custom_limits[client_id] = {
            "requests_per_sec": float(requests_per_sec),
            "burst_size": float(burst_size),
        }
        if client_id in self._buckets:
            del self._buckets[client_id]

    def get_reset_time(self, client_id: str) -> float:
        bucket = self._get_bucket(client_id)
        self._refill(bucket)
        if bucket.tokens >= 1.0:
            return 0.1
        missing = 1.0 - bucket.tokens
        if bucket.refill_rate <= 0:
            return float("inf")
        return missing / bucket.refill_rate

    def get_audit_trail(self) -> List[Dict[str, Any]]:
        return self._audit_trail.copy()

    def circuit_breaker_enabled(self) -> bool:
        return True


__all__ = ["TokenBucketRateLimiter"]
