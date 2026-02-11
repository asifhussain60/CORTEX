"""
Load Test Scenarios: Concurrent User Load Testing.

Provides load testing scenarios for validating MCP/SaaS performance
under various concurrent user loads (10, 50, 100 users) with different
request patterns and thresholds.

AC_START: AC-PHASE38-S9-003
Phase: 38 | Stage: 9 | Priority: P0
Description: Load testing scenario implementation
Requirements: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

import asyncio
import statistics
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

import httpx


class RequestType(Enum):
    """Type of request for load testing."""
    TOOL_DISCOVERY = "tool_discovery"
    TOOL_EXECUTION = "tool_execution"
    STREAMING = "streaming"
    HEALTH_CHECK = "health_check"


@dataclass
class LoadTestScenario:
    """Load test scenario configuration.

    Attributes:
        name: Scenario name
        concurrent_users: Number of concurrent users
        duration_seconds: Test duration in seconds
        request_types: List of request types to execute
        ramp_up_seconds: Time to ramp up to full load
        think_time_ms: Delay between requests per user
    """
    name: str
    concurrent_users: int
    duration_seconds: int
    request_types: List[RequestType]
    ramp_up_seconds: int = 0
    think_time_ms: int = 100


@dataclass
class LoadTestResult:
    """Load test execution result.

    Attributes:
        success: Whether load test passed thresholds
        scenario_name: Name of executed scenario
        total_requests: Total requests executed
        successful_requests: Number of successful requests
        failed_requests: Number of failed requests
        success_rate: Success rate (0.0-1.0)
        p50_latency_ms: Median latency
        p95_latency_ms: 95th percentile latency
        p99_latency_ms: 99th percentile latency
        min_latency_ms: Minimum latency
        max_latency_ms: Maximum latency
        errors: List of error messages
        duration_seconds: Actual test duration
    """
    success: bool
    scenario_name: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    success_rate: float
    p50_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float = 0.0
    min_latency_ms: float = 0.0
    max_latency_ms: float = 0.0
    errors: List[str] = field(default_factory=list)
    duration_seconds: float = 0.0


@dataclass
class RequestMetrics:
    """Metrics for a single request.

    Attributes:
        success: Whether request succeeded
        latency_ms: Request latency in milliseconds
        status_code: HTTP status code
        error_message: Error message if failed
    """
    success: bool
    latency_ms: float
    status_code: int = 0
    error_message: str = ""


class UserSimulator:
    """Simulates a single user making requests.

    Coordinates request execution, timing, and metrics collection
    for a simulated user during load testing.
    """

    def __init__(
        self,
        user_id: int,
        endpoint: str,
        request_types: List[RequestType],
        think_time_ms: int = 100
    ) -> None:
        """Initialize UserSimulator.

        Args:
            user_id: Unique user identifier
            endpoint: Target endpoint URL
            request_types: List of request types to execute
            think_time_ms: Delay between requests in milliseconds
        """
        self.user_id = user_id
        self.endpoint = endpoint
        self.request_types = request_types
        self.think_time_ms = think_time_ms
        self.metrics: List[RequestMetrics] = []

    async def execute_request(
        self,
        client: httpx.AsyncClient,
        request_type: RequestType
    ) -> RequestMetrics:
        """Execute a single request and record metrics.

        Args:
            client: httpx AsyncClient
            request_type: Type of request to execute

        Returns:
            RequestMetrics with execution results
        """
        start_time = time.time()

        try:
            if request_type == RequestType.TOOL_DISCOVERY:
                resp = await client.post(
                    f"{self.endpoint}/mcp/tools",
                    json={
                        "jsonrpc": "2.0",
                        "method": "tools/list",
                        "id": f"user-{self.user_id}-{int(start_time)}"
                    }
                )
                latency_ms = (time.time() - start_time) * 1000
                return RequestMetrics(
                    success=resp.status_code == 200,
                    latency_ms=latency_ms,
                    status_code=resp.status_code
                )

            elif request_type == RequestType.TOOL_EXECUTION:
                resp = await client.post(
                    f"{self.endpoint}/mcp/execute",
                    json={
                        "jsonrpc": "2.0",
                        "method": "tools/call",
                        "params": {
                            "name": "cortex_process_request",
                            "arguments": {"request": "test"}
                        },
                        "id": f"user-{self.user_id}-{int(start_time)}"
                    }
                )
                latency_ms = (time.time() - start_time) * 1000
                return RequestMetrics(
                    success=resp.status_code == 200,
                    latency_ms=latency_ms,
                    status_code=resp.status_code
                )

            elif request_type == RequestType.HEALTH_CHECK:
                resp = await client.get(f"{self.endpoint}/health")
                latency_ms = (time.time() - start_time) * 1000
                return RequestMetrics(
                    success=resp.status_code == 200,
                    latency_ms=latency_ms,
                    status_code=resp.status_code
                )

            elif request_type == RequestType.STREAMING:
                # Simulate streaming request (simplified)
                resp = await client.post(
                    f"{self.endpoint}/mcp/stream",
                    json={
                        "jsonrpc": "2.0",
                        "method": "tools/stream",
                        "params": {"data": "test"},
                        "id": f"user-{self.user_id}-{int(start_time)}"
                    }
                )
                latency_ms = (time.time() - start_time) * 1000
                return RequestMetrics(
                    success=resp.status_code == 200,
                    latency_ms=latency_ms,
                    status_code=resp.status_code
                )

            else:
                latency_ms = (time.time() - start_time) * 1000
                return RequestMetrics(
                    success=False,
                    latency_ms=latency_ms,
                    error_message=f"Unknown request type: {request_type}"
                )

        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            return RequestMetrics(
                success=False,
                latency_ms=latency_ms,
                error_message=str(e)
            )

    async def run_until_stopped(
        self,
        client: httpx.AsyncClient,
        stop_event: asyncio.Event
    ) -> List[RequestMetrics]:
        """Run user simulation until stop event is set.

        Args:
            client: httpx AsyncClient
            stop_event: Event to signal stop

        Returns:
            List of RequestMetrics collected
        """
        request_count = 0

        while not stop_event.is_set():
            # Select request type (round-robin)
            request_type = self.request_types[request_count % len(self.request_types)]

            # Execute request
            metrics = await self.execute_request(client, request_type)
            self.metrics.append(metrics)
            request_count += 1

            # Think time
            await asyncio.sleep(self.think_time_ms / 1000.0)

        return self.metrics


class LoadTestRunner:
    """Executes load test scenarios and collects results.

    Coordinates multiple user simulators, manages test lifecycle,
    and aggregates metrics across all simulated users.
    """

    def __init__(
        self,
        endpoint: str,
        max_concurrent_users: int = 100,
        timeout: int = 30
    ) -> None:
        """Initialize LoadTestRunner.

        Args:
            endpoint: Target endpoint URL
            max_concurrent_users: Maximum concurrent users supported
            timeout: Request timeout in seconds
        """
        self.endpoint = endpoint
        self.max_concurrent_users = max_concurrent_users
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create httpx client.

        Returns:
            httpx AsyncClient instance
        """
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=self.timeout,
                limits=httpx.Limits(max_connections=self.max_concurrent_users)
            )
        return self._client

    async def _execute_request(
        self,
        request_type: RequestType
    ) -> Dict[str, Any]:
        """Execute a single request (for testing/mocking).

        Args:
            request_type: Type of request to execute

        Returns:
            Dict with request results
        """
        client = await self._get_client()
        simulator = UserSimulator(
            user_id=0,
            endpoint=self.endpoint,
            request_types=[request_type]
        )
        metrics = await simulator.execute_request(client, request_type)
        return {
            "status": "success" if metrics.success else "failed",
            "latency_ms": metrics.latency_ms
        }

    async def run_scenario(self, scenario: LoadTestScenario) -> LoadTestResult:
        """Execute load test scenario.

        Args:
            scenario: LoadTestScenario to execute

        Returns:
            LoadTestResult with aggregated metrics
        """
        start_time = time.time()
        client = await self._get_client()
        stop_event = asyncio.Event()

        # Create user simulators
        simulators = [
            UserSimulator(
                user_id=i,
                endpoint=self.endpoint,
                request_types=scenario.request_types,
                think_time_ms=scenario.think_time_ms
            )
            for i in range(scenario.concurrent_users)
        ]

        # Start all users
        tasks = [
            asyncio.create_task(sim.run_until_stopped(client, stop_event))
            for sim in simulators
        ]

        # Run for specified duration
        await asyncio.sleep(scenario.duration_seconds)

        # Stop all users
        stop_event.set()
        await asyncio.gather(*tasks, return_exceptions=True)

        # Collect and aggregate metrics
        all_metrics: List[RequestMetrics] = []
        for sim in simulators:
            all_metrics.extend(sim.metrics)

        # Calculate statistics
        total_requests = len(all_metrics)
        successful_requests = sum(1 for m in all_metrics if m.success)
        failed_requests = total_requests - successful_requests
        success_rate = successful_requests / total_requests if total_requests > 0 else 0.0

        latencies = [m.latency_ms for m in all_metrics]
        if latencies:
            latencies_sorted = sorted(latencies)
            p50_latency = statistics.median(latencies_sorted)
            p95_idx = int(len(latencies_sorted) * 0.95)
            p95_latency = latencies_sorted[p95_idx] if p95_idx < len(latencies_sorted) else latencies_sorted[-1]
            p99_idx = int(len(latencies_sorted) * 0.99)
            p99_latency = latencies_sorted[p99_idx] if p99_idx < len(latencies_sorted) else latencies_sorted[-1]
            min_latency = min(latencies)
            max_latency = max(latencies)
        else:
            p50_latency = p95_latency = p99_latency = min_latency = max_latency = 0.0

        # Collect errors
        errors = [m.error_message for m in all_metrics if not m.success and m.error_message]

        duration = time.time() - start_time

        # Determine success based on thresholds
        success = self._evaluate_success(
            scenario.concurrent_users,
            success_rate,
            p95_latency
        )

        return LoadTestResult(
            success=success,
            scenario_name=scenario.name,
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            success_rate=success_rate,
            p50_latency_ms=p50_latency,
            p95_latency_ms=p95_latency,
            p99_latency_ms=p99_latency,
            min_latency_ms=min_latency,
            max_latency_ms=max_latency,
            errors=errors[:10],  # Limit to first 10 errors
            duration_seconds=duration
        )

    def _evaluate_success(
        self,
        concurrent_users: int,
        success_rate: float,
        p95_latency: float
    ) -> bool:
        """Evaluate if load test passed success criteria.

        Args:
            concurrent_users: Number of concurrent users
            success_rate: Success rate (0.0-1.0)
            p95_latency: 95th percentile latency

        Returns:
            True if test passed, False otherwise
        """
        if concurrent_users <= 10:
            return success_rate >= 0.99 and p95_latency <= 200
        elif concurrent_users <= 50:
            return success_rate >= 0.95 and p95_latency <= 500
        elif concurrent_users <= 100:
            return success_rate >= 0.90 and p95_latency <= 1000
        else:
            return False

    async def close(self) -> None:
        """Close load test runner and cleanup resources."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None


# AC_COMPLETE: AC-PHASE38-S9-003 ✅ Load test scenarios implemented
# Next: Run test suite to verify implementation
