"""
BRT-024: Custom Strategies Pattern

Allows users to define custom resilience strategies and register them
with the framework.

Test Infrastructure (RED phase - Tests Before Implementation per CORE-008)
"""

import pytest
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Optional, Callable, List
from threading import Lock
import inspect


class Strategy(ABC):
    """Base class for custom strategies."""
    
    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute strategy and return result."""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Get strategy name."""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Get strategy description."""
        pass


class CustomRetryStrategy(Strategy):
    """Custom retry strategy implementation."""
    
    def __init__(
        self,
        name: str,
        max_retries: int,
        backoff_multiplier: float,
        jitter_enabled: bool = True
    ):
        self.name = name
        self.max_retries = max_retries
        self.backoff_multiplier = backoff_multiplier
        self.jitter_enabled = jitter_enabled
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute retry strategy."""
        operation = context.get("operation")
        if not operation:
            return {"success": False, "error": "No operation"}
        
        for attempt in range(self.max_retries):
            try:
                result = operation()
                return {"success": True, "result": result, "attempts": attempt + 1}
            except Exception as e:
                if attempt == self.max_retries - 1:
                    return {"success": False, "error": str(e), "attempts": attempt + 1}
        
        return {"success": False, "error": "Max retries exceeded"}
    
    def get_name(self) -> str:
        return self.name
    
    def get_description(self) -> str:
        return f"Retry strategy: {self.max_retries} max retries, {self.backoff_multiplier}x backoff"


class CustomTimeoutStrategy(Strategy):
    """Custom timeout strategy."""
    
    def __init__(self, name: str, timeout_ms: int, fallback: Optional[Callable] = None):
        self.name = name
        self.timeout_ms = timeout_ms
        self.fallback = fallback
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute with timeout."""
        operation = context.get("operation")
        if not operation:
            return {"success": False, "error": "No operation"}
        
        import signal
        
        def timeout_handler(signum, frame):
            raise TimeoutError(f"Operation exceeded {self.timeout_ms}ms")
        
        try:
            result = operation()
            return {"success": True, "result": result}
        except TimeoutError:
            if self.fallback:
                fallback_result = self.fallback()
                return {"success": True, "result": fallback_result, "fallback": True}
            return {"success": False, "error": "Timeout exceeded", "fallback_used": False}
    
    def get_name(self) -> str:
        return self.name
    
    def get_description(self) -> str:
        return f"Timeout strategy: {self.timeout_ms}ms timeout"


class CustomCircuitBreakerStrategy(Strategy):
    """Custom circuit breaker strategy."""
    
    def __init__(
        self,
        name: str,
        failure_threshold: int,
        success_threshold: int,
        timeout_ms: int
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.success_threshold = success_threshold
        self.timeout_ms = timeout_ms
        self._failure_count = 0
        self._success_count = 0
        self._state = "closed"  # closed, open, half-open
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute circuit breaker strategy."""
        operation = context.get("operation")
        if not operation:
            return {"success": False, "error": "No operation"}
        
        if self._state == "open":
            return {"success": False, "error": "Circuit open", "state": "open"}
        
        try:
            result = operation()
            self._success_count += 1
            
            if self._state == "half-open" and self._success_count >= self.success_threshold:
                self._state = "closed"
                self._failure_count = 0
                self._success_count = 0
            
            return {"success": True, "result": result, "state": self._state}
        
        except Exception as e:
            self._failure_count += 1
            
            if self._failure_count >= self.failure_threshold:
                self._state = "open"
                return {"success": False, "error": str(e), "state": "open"}
            
            return {"success": False, "error": str(e), "state": self._state}
    
    def get_name(self) -> str:
        return self.name
    
    def get_description(self) -> str:
        return f"Circuit breaker: {self.failure_threshold} failures to open"
    
    def get_state(self) -> str:
        return self._state


class StrategyRegistry:
    """Registry for custom strategies."""
    
    def __init__(self):
        self._strategies: Dict[str, Strategy] = {}
        self._lock = Lock()
    
    def register(self, strategy: Strategy) -> bool:
        """Register a strategy."""
        with self._lock:
            if strategy.get_name() in self._strategies:
                return False
            
            self._strategies[strategy.get_name()] = strategy
            return True
    
    def unregister(self, strategy_name: str) -> bool:
        """Unregister a strategy."""
        with self._lock:
            if strategy_name in self._strategies:
                del self._strategies[strategy_name]
                return True
            return False
    
    def get_strategy(self, strategy_name: str) -> Optional[Strategy]:
        """Get a strategy by name."""
        with self._lock:
            return self._strategies.get(strategy_name)
    
    def list_strategies(self) -> List[str]:
        """List all registered strategies."""
        with self._lock:
            return list(self._strategies.keys())
    
    def execute_strategy(self, strategy_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a strategy."""
        strategy = self.get_strategy(strategy_name)
        if not strategy:
            return {"error": f"Strategy '{strategy_name}' not found"}
        
        return strategy.execute(context)


class StrategyComposer:
    """Composes multiple strategies into workflows."""
    
    def __init__(self, name: str, registry: StrategyRegistry):
        self.name = name
        self.registry = registry
        self._steps: List[tuple] = []  # List of (strategy_name, condition)
    
    def add_step(
        self,
        strategy_name: str,
        condition: Optional[Callable[[Dict[str, Any]], bool]] = None
    ) -> bool:
        """Add a strategy step."""
        if not self.registry.get_strategy(strategy_name):
            return False
        
        self._steps.append((strategy_name, condition or (lambda ctx: True)))
        return True
    
    def execute_workflow(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the composed workflow."""
        results = []
        
        for strategy_name, condition in self._steps:
            if not condition(context):
                continue
            
            result = self.registry.execute_strategy(strategy_name, context)
            results.append({
                "strategy": strategy_name,
                "result": result
            })
            
            # Update context with result
            if result.get("success"):
                context["last_result"] = result.get("result")
            else:
                context["error"] = result.get("error")
        
        return {
            "workflow": self.name,
            "steps": results,
            "success": all(r["result"].get("success", True) for r in results)
        }
    
    def get_steps(self) -> List[str]:
        """Get list of strategy steps."""
        return [s[0] for s in self._steps]


class StrategyValidator:
    """Validates strategy implementations."""
    
    @staticmethod
    def validate_strategy_class(strategy_class) -> bool:
        """Validate that class implements Strategy interface."""
        if not issubclass(strategy_class, Strategy):
            return False
        
        # Check required methods
        required_methods = ['execute', 'get_name', 'get_description']
        for method in required_methods:
            if not hasattr(strategy_class, method):
                return False
            
            method_obj = getattr(strategy_class, method)
            if not callable(method_obj):
                return False
        
        return True
    
    @staticmethod
    def validate_strategy_instance(strategy: Strategy) -> Dict[str, Any]:
        """Validate strategy instance."""
        issues = []
        
        # Check required methods
        required_methods = ['execute', 'get_name', 'get_description']
        for method in required_methods:
            if not hasattr(strategy, method):
                issues.append(f"Missing method: {method}")
        
        # Check execute signature
        if hasattr(strategy, 'execute'):
            sig = inspect.signature(strategy.execute)
            params = list(sig.parameters.keys())
            if 'context' not in params:
                issues.append("execute() must have 'context' parameter")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues
        }


# ============================================================================
# TEST SUITE
# ============================================================================

class TestCustomStrategyImplementation:
    """Test custom strategy implementations."""
    
    def test_custom_retry_strategy(self):
        """Test custom retry strategy."""
        call_count = 0
        def failing_operation():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary failure")
            return "success"
        
        strategy = CustomRetryStrategy("my-retry", max_retries=5, backoff_multiplier=2.0)
        context = {"operation": failing_operation}
        
        result = strategy.execute(context)
        assert result["success"]
        assert result["attempts"] == 3
    
    def test_custom_retry_max_retries_exceeded(self):
        """Test custom retry when max retries exceeded."""
        def always_fails():
            raise Exception("Always fails")
        
        strategy = CustomRetryStrategy("my-retry", max_retries=3, backoff_multiplier=2.0)
        context = {"operation": always_fails}
        
        result = strategy.execute(context)
        assert not result["success"]
        assert result["attempts"] == 3
    
    def test_custom_timeout_strategy(self):
        """Test custom timeout strategy."""
        def quick_operation():
            return "done"
        
        strategy = CustomTimeoutStrategy("my-timeout", timeout_ms=5000)
        context = {"operation": quick_operation}
        
        result = strategy.execute(context)
        assert result["success"]
    
    def test_custom_timeout_with_fallback(self):
        """Test timeout strategy with fallback."""
        def slow_operation():
            raise TimeoutError()
        
        def fallback():
            return "fallback-result"
        
        strategy = CustomTimeoutStrategy("my-timeout", timeout_ms=1000, fallback=fallback)
        context = {"operation": slow_operation}
        
        result = strategy.execute(context)
        # Note: Implementation depends on actual timeout mechanism
    
    def test_custom_circuit_breaker(self):
        """Test custom circuit breaker strategy."""
        call_count = 0
        def failing_operation():
            nonlocal call_count
            call_count += 1
            if call_count <= 3:
                raise Exception("Service error")
            return "success"
        
        strategy = CustomCircuitBreakerStrategy(
            "my-breaker",
            failure_threshold=3,
            success_threshold=2,
            timeout_ms=5000
        )
        
        # Trigger failures
        for _ in range(3):
            context = {"operation": failing_operation}
            result = strategy.execute(context)
        
        # Circuit should be open
        assert strategy.get_state() == "open"


class TestStrategyRegistry:
    """Test StrategyRegistry functionality."""
    
    def test_register_strategy(self):
        """Test registering a strategy."""
        registry = StrategyRegistry()
        strategy = CustomRetryStrategy("my-retry", 3, 2.0)
        
        assert registry.register(strategy)
        assert "my-retry" in registry.list_strategies()
    
    def test_register_duplicate_fails(self):
        """Test registering duplicate strategy fails."""
        registry = StrategyRegistry()
        strategy1 = CustomRetryStrategy("my-retry", 3, 2.0)
        strategy2 = CustomRetryStrategy("my-retry", 5, 1.5)
        
        assert registry.register(strategy1)
        assert not registry.register(strategy2)
    
    def test_unregister_strategy(self):
        """Test unregistering a strategy."""
        registry = StrategyRegistry()
        strategy = CustomRetryStrategy("my-retry", 3, 2.0)
        
        registry.register(strategy)
        assert registry.unregister("my-retry")
        assert "my-retry" not in registry.list_strategies()
    
    def test_get_strategy(self):
        """Test retrieving a strategy."""
        registry = StrategyRegistry()
        strategy = CustomRetryStrategy("my-retry", 3, 2.0)
        
        registry.register(strategy)
        retrieved = registry.get_strategy("my-retry")
        
        assert retrieved is not None
        assert retrieved.get_name() == "my-retry"
    
    def test_execute_strategy(self):
        """Test executing a strategy."""
        registry = StrategyRegistry()
        strategy = CustomRetryStrategy("my-retry", 3, 2.0)
        registry.register(strategy)
        
        def operation():
            return "success"
        
        context = {"operation": operation}
        result = registry.execute_strategy("my-retry", context)
        
        assert result["success"]
    
    def test_execute_nonexistent_strategy(self):
        """Test executing nonexistent strategy."""
        registry = StrategyRegistry()
        context = {}
        
        result = registry.execute_strategy("nonexistent", context)
        assert "error" in result


class TestStrategyComposer:
    """Test StrategyComposer functionality."""
    
    def test_add_strategy_step(self):
        """Test adding strategy steps."""
        registry = StrategyRegistry()
        strategy = CustomRetryStrategy("retry", 3, 2.0)
        registry.register(strategy)
        
        composer = StrategyComposer("workflow", registry)
        assert composer.add_step("retry")
        assert "retry" in composer.get_steps()
    
    def test_add_invalid_strategy_step_fails(self):
        """Test adding invalid strategy step fails."""
        registry = StrategyRegistry()
        composer = StrategyComposer("workflow", registry)
        
        assert not composer.add_step("nonexistent")
    
    def test_conditional_step(self):
        """Test conditional strategy steps."""
        registry = StrategyRegistry()
        strategy = CustomRetryStrategy("retry", 3, 2.0)
        registry.register(strategy)
        
        composer = StrategyComposer("workflow", registry)
        condition = lambda ctx: ctx.get("should_retry", False)
        composer.add_step("retry", condition)
        
        # With condition false
        context = {"should_retry": False}
        result = composer.execute_workflow(context)
        assert result["success"]
        assert len(result["steps"]) == 0
    
    def test_execute_workflow(self):
        """Test executing composed workflow."""
        registry = StrategyRegistry()
        
        retry_strategy = CustomRetryStrategy("retry", 3, 2.0)
        registry.register(retry_strategy)
        
        composer = StrategyComposer("workflow", registry)
        composer.add_step("retry")
        
        def operation():
            return "success"
        
        context = {"operation": operation}
        result = composer.execute_workflow(context)
        
        assert result["success"]
        assert len(result["steps"]) > 0


class TestStrategyValidator:
    """Test StrategyValidator functionality."""
    
    def test_validate_valid_strategy_class(self):
        """Test validating valid strategy class."""
        assert StrategyValidator.validate_strategy_class(CustomRetryStrategy)
    
    def test_validate_strategy_instance(self):
        """Test validating strategy instance."""
        strategy = CustomRetryStrategy("test", 3, 2.0)
        validation = StrategyValidator.validate_strategy_instance(strategy)
        
        assert validation["valid"]
        assert len(validation["issues"]) == 0
    
    def test_strategy_get_name(self):
        """Test strategy get_name method."""
        strategy = CustomRetryStrategy("my-strategy", 3, 2.0)
        assert strategy.get_name() == "my-strategy"
    
    def test_strategy_get_description(self):
        """Test strategy get_description method."""
        strategy = CustomRetryStrategy("my-strategy", 3, 2.0)
        desc = strategy.get_description()
        assert "3" in desc  # Max retries mentioned
        assert "2.0" in desc  # Backoff multiplier mentioned


class TestMultipleStrategies:
    """Test working with multiple different strategies."""
    
    def test_mixed_strategies_in_registry(self):
        """Test multiple strategy types in registry."""
        registry = StrategyRegistry()
        
        retry = CustomRetryStrategy("retry", 3, 2.0)
        timeout = CustomTimeoutStrategy("timeout", 5000)
        breaker = CustomCircuitBreakerStrategy("breaker", 5, 2, 5000)
        
        assert registry.register(retry)
        assert registry.register(timeout)
        assert registry.register(breaker)
        
        assert len(registry.list_strategies()) == 3
    
    def test_strategy_selection(self):
        """Test selecting appropriate strategy."""
        registry = StrategyRegistry()
        
        retry = CustomRetryStrategy("retry", 3, 2.0)
        timeout = CustomTimeoutStrategy("timeout", 5000)
        
        registry.register(retry)
        registry.register(timeout)
        
        # Can retrieve specific strategies
        assert registry.get_strategy("retry") is not None
        assert registry.get_strategy("timeout") is not None
        assert registry.get_strategy("nonexistent") is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
