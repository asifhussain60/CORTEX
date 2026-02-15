# Tutorial: Error Handling and Resilience

**Time:** 30 minutes | **Level:** Intermediate  
**Goal:** Implement robust error recovery and resilience patterns

## Overview

Production orchestrators must handle failures gracefully. This tutorial covers error handling, circuit breakers, retries, and fallback mechanisms.

## Prerequisites

- [Multi-step Workflow](2-multi-step-workflow.md) completed
- Understanding of exception handling

## Error Handling Patterns

### 1. Try-Catch Pattern

```python
from cortex.orchestrators.base import OrchestratorBase
from cortex.types import Intent, Response

class ResilientOrchestrator(OrchestratorBase):
    async def process(self, intent: Intent) -> Response:
        try:
            result = await self._call_external_service(intent)
            return Response(status="success", content=result)
        except TimeoutError:
            return Response(
                status="error",
                content="Service timeout",
                metadata={"error_type": "timeout"}
            )
        except Exception as e:
            return Response(
                status="error",
                content=f"Unexpected error: {str(e)}",
                metadata={"error_type": type(e).__name__}
            )
```

### 2. Circuit Breaker Pattern

```python
from cortex.resilience.circuit_breaker import CircuitBreaker

class SmartOrchestrator(OrchestratorBase):
    def __init__(self):
        super().__init__()
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60
        )
    
    async def process(self, intent: Intent) -> Response:
        if self.circuit_breaker.is_open():
            return Response(
                status="degraded",
                content="Service temporarily unavailable"
            )
        
        try:
            result = await self.circuit_breaker.call(
                self._risky_operation,
                intent
            )
            return Response(status="success", content=result)
        except Exception:
            return self._fallback_response(intent)
```

### 3. Retry with Exponential Backoff

```python
import asyncio
from cortex.resilience.retry import retry_async

class RetryingOrchestrator(OrchestratorBase):
    @retry_async(
        max_attempts=3,
        initial_delay=1,
        backoff_factor=2,
        jitter=True
    )
    async def _call_service(self, intent: Intent):
        # Automatically retried on failure
        return await external_service.call(intent)
```

### 4. Fallback Mechanism

```python
class FallbackOrchestrator(OrchestratorBase):
    async def process(self, intent: Intent) -> Response:
        try:
            return await self._primary_service(intent)
        except Exception:
            self.logger.warning("Primary service failed, using fallback")
            return await self._fallback_service(intent)
    
    async def _primary_service(self, intent: Intent) -> Response:
        # Could fail
        raise Exception("Service unavailable")
    
    async def _fallback_service(self, intent: Intent) -> Response:
        # Graceful degradation
        return Response(
            status="degraded",
            content="Using cached response",
            metadata={"service": "fallback"}
        )
```

## Best Practices

1. **Fail fast** - Don't retry indefinitely
2. **Log errors** - Capture error context for debugging
3. **Expose errors** - Return meaningful error messages to users
4. **Monitor** - Track error rates and patterns
5. **Test failures** - Include error scenarios in tests

## Testing Error Cases

```python
import pytest
from cortex.types import Intent, Response

@pytest.mark.asyncio
async def test_timeout_handling():
    orchestrator = ResilientOrchestrator()
    intent = Intent(content="test", user_id="user1")
    
    # Simulate timeout
    response = await orchestrator.process(intent)
    assert response.status == "error"
    assert "timeout" in response.metadata["error_type"]
```

## Next Steps

- [Knowledge Integration](4-knowledge-integration.md) - Error handling with knowledge
- [Complex Domain](5-complex-domain.md) - Enterprise-grade resilience
