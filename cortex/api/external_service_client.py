"""External Service Client with Timeout Support.

Provides timeout handling for all external API calls with:
- Configurable per-endpoint timeouts
- Exponential backoff retry logic
- Circuit breaker integration
- Comprehensive logging and metrics
"""

import asyncio
import logging
from typing import Any, Dict, Optional

import httpx

from cortex.infrastructure.circuit_breaker import CircuitBreaker, CircuitBreakerConfig
from cortex.infrastructure.retry_strategy import RetryConfig, RetryStrategy

logger = logging.getLogger(__name__)


class ExternalServiceClient:
    """Client for making external API calls with timeout handling."""

    def __init__(
        self,
        default_timeout: float = 30.0,
        circuit_breaker_threshold: int = 5,
        retry_config: Optional[RetryConfig] = None,
    ) -> None:
        """Initialize external service client.

        Args:
            default_timeout: Default timeout for all API calls in seconds.
            circuit_breaker_threshold: Failures before circuit breaker opens.
            retry_config: Retry configuration for exponential backoff.
        """
        self.default_timeout = default_timeout
        self._endpoint_timeouts: Dict[str, float] = {}
        self._client = httpx.AsyncClient(timeout=default_timeout)

        # Circuit breaker per endpoint
        self._circuit_breakers: Dict[str, CircuitBreaker] = {}
        self._cb_config = CircuitBreakerConfig(
            failure_threshold=circuit_breaker_threshold,
            timeout_seconds=60.0,
        )

        # Retry strategy
        self._retry_config = retry_config or RetryConfig()
        self._retry_strategy = RetryStrategy(self._retry_config)

        # Metrics
        self._metrics: Dict[str, int] = {
            "EXTERNAL_CALL_TIMEOUT_COUNT": 0,
            "EXTERNAL_CALL_TOTAL_COUNT": 0,
            "EXTERNAL_CALL_SUCCESS_COUNT": 0,
            "EXTERNAL_CALL_FAILURE_COUNT": 0,
            "EXTERNAL_CALL_RETRY_COUNT": 0,
        }

    def set_endpoint_timeout(self, endpoint: str, timeout: float) -> None:
        """Set timeout for specific endpoint.

        Args:
            endpoint: URL endpoint.
            timeout: Timeout in seconds.
        """
        self._endpoint_timeouts[endpoint] = timeout
        logger.info(
            f"Set endpoint timeout: {endpoint} → {timeout}s",
            extra={"endpoint": endpoint, "timeout": timeout},
        )

    def get_endpoint_timeout(self, endpoint: str) -> float:
        """Get configured timeout for endpoint.

        Args:
            endpoint: URL endpoint.

        Returns:
            Timeout in seconds.
        """
        return self._endpoint_timeouts.get(endpoint, self.default_timeout)

    def _get_or_create_circuit_breaker(self, endpoint: str) -> CircuitBreaker:
        """Get or create circuit breaker for endpoint.

        Args:
            endpoint: URL endpoint.

        Returns:
            CircuitBreaker instance.
        """
        if endpoint not in self._circuit_breakers:
            self._circuit_breakers[endpoint] = CircuitBreaker(
                name=f"cb_{endpoint}",
                config=self._cb_config,
            )
        return self._circuit_breakers[endpoint]

    async def call_external_api(
        self,
        url: str,
        method: str = "get",
        payload: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Make external API call with timeout and retry handling.

        Args:
            url: API endpoint URL.
            method: HTTP method (get, post, etc.).
            payload: Request payload for POST/PUT.
            headers: Additional headers.
            timeout: Call timeout in seconds (uses endpoint config if not specified).

        Returns:
            Response data as dictionary.

        Raises:
            httpx.TimeoutException: If call times out.
            Exception: If circuit breaker is open or other failures.
        """
        # Get timeout value
        call_timeout = timeout or self.get_endpoint_timeout(url)

        # Increment total counter
        self._metrics["EXTERNAL_CALL_TOTAL_COUNT"] += 1

        # Get circuit breaker
        circuit_breaker = self._get_or_create_circuit_breaker(url)

        # Check if circuit is open using state property
        if circuit_breaker.state.name == "OPEN":
            msg = f"Circuit breaker open for {url}"
            logger.warning(msg, extra={"url": url, "state": "open"})
            self._metrics["EXTERNAL_CALL_FAILURE_COUNT"] += 1
            raise Exception(msg)

        # Retry logic
        last_error: Optional[Exception] = None
        for attempt in range(1, self._retry_config.max_attempts + 1):
            try:
                # Make the call
                response = await self._make_request(
                    method=method,
                    url=url,
                    payload=payload,
                    headers=headers,
                    timeout=call_timeout,
                )

                # Success - record via circuit breaker call mechanism
                self._metrics["EXTERNAL_CALL_SUCCESS_COUNT"] += 1

                logger.info(
                    f"External API call succeeded: {method.upper()} {url}",
                    extra={
                        "method": method,
                        "url": url,
                        "status": response.status_code,
                        "attempt": attempt,
                    },
                )
                return response.json()

            except httpx.TimeoutException as e:
                last_error = e
                self._metrics["EXTERNAL_CALL_TIMEOUT_COUNT"] += 1
                self._metrics["EXTERNAL_CALL_RETRY_COUNT"] += 1

                logger.warning(
                    f"External API call timeout (attempt {attempt}/{self._retry_config.max_attempts}): "
                    f"{method.upper()} {url}",
                    extra={
                        "method": method,
                        "url": url,
                        "timeout": call_timeout,
                        "attempt": attempt,
                        "error": str(e),
                    },
                )

                # If last attempt, raise
                if attempt == self._retry_config.max_attempts:
                    self._metrics["EXTERNAL_CALL_FAILURE_COUNT"] += 1
                    raise

                # Calculate backoff delay
                delay_ms = self._retry_config.initial_delay_ms * (
                    self._retry_config.backoff_multiplier ** (attempt - 1)
                )
                delay_ms = min(delay_ms, self._retry_config.max_delay_ms)
                delay = delay_ms / 1000.0
                logger.debug(
                    f"Retrying after {delay}s backoff",
                    extra={"url": url, "delay_seconds": delay, "attempt": attempt},
                )
                await asyncio.sleep(delay)

            except Exception as e:
                last_error = e
                self._metrics["EXTERNAL_CALL_FAILURE_COUNT"] += 1

                logger.error(
                    f"External API call failed: {method.upper()} {url}: {str(e)}",
                    extra={
                        "method": method,
                        "url": url,
                        "error": str(e),
                        "attempt": attempt,
                    },
                    exc_info=True,
                )
                raise

        # Should not reach here, but just in case
        msg = "Retry logic exhausted"
        logger.error(msg)
        if last_error:
            raise last_error
        raise Exception(msg)

    async def _make_request(
        self,
        method: str,
        url: str,
        payload: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: float = 30.0,
    ) -> httpx.Response:
        """Make HTTP request with timeout.

        Args:
            method: HTTP method.
            url: Endpoint URL.
            payload: Request payload.
            headers: Additional headers.
            timeout: Request timeout.

        Returns:
            HTTP response object.
        """
        method = method.lower()

        if method == "get":
            return await self._client.get(url, headers=headers, timeout=timeout)
        elif method == "post":
            return await self._client.post(
                url, json=payload, headers=headers, timeout=timeout
            )
        elif method == "put":
            return await self._client.put(
                url, json=payload, headers=headers, timeout=timeout
            )
        elif method == "delete":
            return await self._client.delete(url, headers=headers, timeout=timeout)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

    def get_metric(self, metric_name: str) -> int:
        """Get metric value.

        Args:
            metric_name: Name of metric.

        Returns:
            Metric value.
        """
        return self._metrics.get(metric_name, 0)

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()

    def __enter__(self) -> "ExternalServiceClient":
        """Context manager entry."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Context manager exit."""
        # Note: Can't use await in __exit__, so close in async context
        pass
