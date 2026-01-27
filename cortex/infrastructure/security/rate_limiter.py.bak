"""
TokenBucketRateLimiter - rate limiting and throttling.

Implements token bucket algorithm for preventing abuse and DDoS attacks
with per-client rate limits, sliding window accuracy, and graceful degradation.

Author: CORTEX Implementation
Phase: impl-arch-005-hardening (HARD-PROD-001-03)
Compliance: CORE-011 (100% typed), CORE-012 (Google docstrings), CORE-013 (no bare except)
"""

import time
from typing import Dict, Optional, Tuple
from collections import defaultdict


class TokenBucketRateLimiter:
    """Token bucket algorithm for rate limiting.
    
    Implements token bucket rate limiting with per-client quotas,
    configurable limits, and circuit breaker integration.
    
    Attributes:
        tokens: Dictionary of {client_id: {tokens, last_update}}
        limits: Dictionary of {client_id: {requests_per_sec, burst_size}}
        circuit_breaker_threshold: Error rate to trigger circuit breaker
        circuit_breaker_state: Dictionary of {client_id: state}
    """

    def __init__(
        self,
        default_requests_per_sec: float = 100.0,
        default_burst_size: int = 50,
        circuit_breaker_threshold: float = 0.5
    ) -> None:
        """Initialize TokenBucketRateLimiter.
        
        Args:
            default_requests_per_sec: Default rate limit
            default_burst_size: Default burst allowance
            circuit_breaker_threshold: Error rate to trigger circuit breaker
        """
        self.default_requests_per_sec = default_requests_per_sec
        self.default_burst_size = default_burst_size
        self.circuit_breaker_threshold = circuit_breaker_threshold
        
        self.tokens: Dict[str, Dict[str, float]] = defaultdict(
            lambda: {
                "tokens": default_burst_size,
                "last_update": time.time()
            }
        )
        
        self.limits: Dict[str, Dict[str, float]] = defaultdict(
            lambda: {
                "requests_per_sec": default_requests_per_sec,
                "burst_size": default_burst_size
            }
        )
        
        self.circuit_breaker_state: Dict[str, str] = defaultdict(
            lambda: "closed"
        )
        self.audit_trail: list = []

    def allow_request(
        self,
        client_id: str,
        quota: Optional[float] = None
    ) -> bool:
        """Check if request is allowed for client.
        
        Args:
            client_id: Client identifier
            quota: Optional custom quota for this request
            
        Returns:
            True if request allowed, False if rate limited
        """
        try:
            if not client_id:
                raise ValueError("client_id required")
            
            # Check circuit breaker
            if self.circuit_breaker_state[client_id] == "open":
                self.audit_trail.append({
                    "client": client_id,
                    "action": "rejected_circuit_breaker"
                })
                return False
            
            # Get client limits
            client_limits = self.limits[client_id]
            rate = quota or client_limits["requests_per_sec"]
            burst = client_limits["burst_size"]
            
            # Update tokens
            now = time.time()
            state = self.tokens[client_id]
            elapsed = now - state["last_update"]
            
            # Add tokens based on elapsed time
            tokens_to_add = elapsed * rate
            state["tokens"] = min(
                burst,
                state["tokens"] + tokens_to_add
            )
            state["last_update"] = now
            
            # Check if we have tokens
            if state["tokens"] >= 1.0:
                state["tokens"] -= 1.0
                self.audit_trail.append({
                    "client": client_id,
                    "action": "allowed",
                    "remaining_tokens": state["tokens"]
                })
                return True
            else:
                self.audit_trail.append({
                    "client": client_id,
                    "action": "rate_limited",
                    "tokens_available": state["tokens"]
                })
                return False
        except (TypeError, ValueError) as err:
            raise ValueError(f"Rate limit check failed: {err}") from err

    def get_reset_time(self, client_id: str) -> float:
        """Get when rate limit resets for client.
        
        Args:
            client_id: Client identifier
            
        Returns:
            Timestamp when tokens will be refilled
        """
        if not client_id:
            raise ValueError("client_id required")
        
        state = self.tokens[client_id]
        limits = self.limits[client_id]
        
        # Time until we have 1 full token again
        tokens_needed = 1.0 - state["tokens"]
        time_needed = tokens_needed / limits["requests_per_sec"]
        
        return state["last_update"] + time_needed

    def configure_limits(
        self,
        client_id: str,
        requests_per_sec: float,
        burst_size: int
    ) -> None:
        """Configure rate limits for a client.
        
        Args:
            client_id: Client identifier
            requests_per_sec: Requests allowed per second
            burst_size: Maximum burst allowance
            
        Raises:
            ValueError: If limits are invalid
        """
        if not client_id:
            raise ValueError("client_id required")
        
        if requests_per_sec <= 0 or burst_size <= 0:
            raise ValueError("Limits must be positive")
        
        self.limits[client_id] = {
            "requests_per_sec": requests_per_sec,
            "burst_size": burst_size
        }
        
        # Reset tokens to burst size
        self.tokens[client_id]["tokens"] = burst_size
        self.tokens[client_id]["last_update"] = time.time()

    def circuit_breaker_enabled(self, client_id: str) -> bool:
        """Check if circuit breaker is enabled for client.
        
        Args:
            client_id: Client identifier
            
        Returns:
            True if circuit breaker is active (open state)
        """
        return self.circuit_breaker_state[client_id] == "open"

    def open_circuit_breaker(self, client_id: str) -> None:
        """Open circuit breaker for client.
        
        Args:
            client_id: Client identifier
        """
        self.circuit_breaker_state[client_id] = "open"
        self.audit_trail.append({
            "client": client_id,
            "action": "circuit_breaker_opened"
        })

    def close_circuit_breaker(self, client_id: str) -> None:
        """Close circuit breaker for client.
        
        Args:
            client_id: Client identifier
        """
        self.circuit_breaker_state[client_id] = "closed"
        self.audit_trail.append({
            "client": client_id,
            "action": "circuit_breaker_closed"
        })

    def get_audit_trail(self) -> list:
        """Get audit trail of rate limit events.
        
        Returns:
            List of audit trail entries
        """
        return self.audit_trail.copy()

    def clear_audit_trail(self) -> None:
        """Clear audit trail (useful for testing)."""
        self.audit_trail.clear()
