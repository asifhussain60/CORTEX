"""
BRT-025: Pattern Composition

Enables composing multiple resilience patterns together to form
sophisticated behavior for complex scenarios.

Test Infrastructure (RED phase - Tests Before Implementation per CORE-008)
"""

import pytest
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Callable
from threading import Lock, Event as ThreadEvent
import time
from enum import Enum


class PatternType(Enum):
    """Types of resilience patterns."""
    RATE_LIMITING = "rate_limiting"
    CIRCUIT_BREAKER = "circuit_breaker"
    RETRY = "retry"
    TIMEOUT = "timeout"
    BULKHEAD = "bulkhead"
    GRACEFUL_DEGRADATION = "graceful_degradation"
    HEALTH_CHECK = "health_check"
    ADAPTIVE_TIMEOUT = "adaptive_timeout"


@dataclass
class PatternConfig:
    """Configuration for a pattern."""
    pattern_type: PatternType
    name: str
    settings: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    priority: int = 100


class ComposablePattern(ABC):
    """Base class for composable patterns."""
    
    def __init__(self, config: PatternConfig):
        self.config = config
        self._metrics = {"executions": 0, "successes": 0, "failures": 0}
    
    @abstractmethod
    def apply(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply pattern to context."""
        pass
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get pattern metrics."""
        return self._metrics.copy()


class RateLimitPattern(ComposablePattern):
    """Rate limiting pattern."""
    
    def __init__(self, config: PatternConfig):
        super().__init__(config)
        self.max_requests = config.settings.get("max_requests", 100)
        self.window_size_ms = config.settings.get("window_size_ms", 1000)
        self.request_times: List[float] = []
        self._lock = Lock()
    
    def apply(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply rate limiting."""
        self._metrics["executions"] += 1
        
        with self._lock:
            now = time.time() * 1000
            self.request_times = [
                t for t in self.request_times
                if now - t < self.window_size_ms
            ]
            
            if len(self.request_times) >= self.max_requests:
                self._metrics["failures"] += 1
                return {
                    "allowed": False,
                    "reason": "rate_limit_exceeded",
                    "current_rate": len(self.request_times)
                }
            
            self.request_times.append(now)
            self._metrics["successes"] += 1
            return {
                "allowed": True,
                "current_rate": len(self.request_times)
            }


class CircuitBreakerPattern(ComposablePattern):
    """Circuit breaker pattern."""
    
    def __init__(self, config: PatternConfig):
        super().__init__(config)
        self.failure_threshold = config.settings.get("failure_threshold", 5)
        self.success_threshold = config.settings.get("success_threshold", 2)
        self.timeout_ms = config.settings.get("timeout_ms", 60000)
        self._state = "closed"
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time = 0
        self._lock = Lock()
    
    def apply(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply circuit breaker."""
        self._metrics["executions"] += 1
        
        with self._lock:
            now = time.time() * 1000
            
            if self._state == "open":
                if now - self._last_failure_time > self.timeout_ms:
                    self._state = "half-open"
                    self._success_count = 0
                else:
                    self._metrics["failures"] += 1
                    return {"state": "open", "allowed": False}
            
            result = context.get("operation_result", {})
            
            if result.get("success", False):
                self._success_count += 1
                if self._state == "half-open" and self._success_count >= self.success_threshold:
                    self._state = "closed"
                    self._failure_count = 0
                self._metrics["successes"] += 1
                return {"state": self._state, "allowed": True}
            else:
                self._failure_count += 1
                if self._failure_count >= self.failure_threshold:
                    self._state = "open"
                    self._last_failure_time = now
                    self._metrics["failures"] += 1
                    return {"state": "open", "allowed": False}
                
                self._metrics["failures"] += 1
                return {"state": self._state, "allowed": False}


class RetryPattern(ComposablePattern):
    """Retry pattern."""
    
    def __init__(self, config: PatternConfig):
        super().__init__(config)
        self.max_retries = config.settings.get("max_retries", 3)
        self.backoff_multiplier = config.settings.get("backoff_multiplier", 2.0)
        self.initial_delay_ms = config.settings.get("initial_delay_ms", 100)
    
    def apply(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply retry pattern."""
        self._metrics["executions"] += 1
        
        operation = context.get("operation")
        if not operation:
            self._metrics["failures"] += 1
            return {"retries": 0, "success": False, "reason": "no_operation"}
        
        for attempt in range(self.max_retries):
            try:
                result = operation()
                self._metrics["successes"] += 1
                return {
                    "success": True,
                    "result": result,
                    "retries": attempt
                }
            except Exception as e:
                if attempt == self.max_retries - 1:
                    self._metrics["failures"] += 1
                    return {
                        "success": False,
                        "error": str(e),
                        "retries": attempt + 1
                    }
                
                # Exponential backoff
                delay = self.initial_delay_ms * (self.backoff_multiplier ** attempt)
                time.sleep(delay / 1000)
        
        self._metrics["failures"] += 1
        return {"success": False, "retries": self.max_retries}


class TimeoutPattern(ComposablePattern):
    """Timeout pattern."""
    
    def __init__(self, config: PatternConfig):
        super().__init__(config)
        self.timeout_ms = config.settings.get("timeout_ms", 5000)
    
    def apply(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply timeout pattern."""
        self._metrics["executions"] += 1
        
        operation = context.get("operation")
        if not operation:
            self._metrics["failures"] += 1
            return {"timed_out": True, "reason": "no_operation"}
        
        import threading
        result_container = {}
        exception_container = {}
        
        def operation_wrapper():
            try:
                result_container["result"] = operation()
            except Exception as e:
                exception_container["error"] = e
        
        thread = threading.Thread(target=operation_wrapper)
        thread.daemon = True
        thread.start()
        thread.join(timeout=self.timeout_ms / 1000)
        
        if thread.is_alive():
            self._metrics["failures"] += 1
            return {"timed_out": True, "timeout_ms": self.timeout_ms}
        
        if "error" in exception_container:
            self._metrics["failures"] += 1
            return {
                "timed_out": False,
                "success": False,
                "error": str(exception_container["error"])
            }
        
        self._metrics["successes"] += 1
        return {
            "timed_out": False,
            "success": True,
            "result": result_container.get("result")
        }


class PatternCompositionBuilder:
    """Builds pattern compositions."""
    
    def __init__(self, name: str):
        self.name = name
        self._patterns: List[ComposablePattern] = []
        self._lock = Lock()
    
    def add_pattern(self, pattern: ComposablePattern) -> bool:
        """Add a pattern to composition."""
        if not pattern.config.enabled:
            return False
        
        with self._lock:
            self._patterns.append(pattern)
            # Sort by priority (higher first)
            self._patterns.sort(key=lambda p: p.config.priority, reverse=True)
            return True
    
    def remove_pattern(self, pattern_name: str) -> bool:
        """Remove a pattern from composition."""
        with self._lock:
            initial_len = len(self._patterns)
            self._patterns = [
                p for p in self._patterns
                if p.config.name != pattern_name
            ]
            return len(self._patterns) < initial_len
    
    def get_patterns(self) -> List[str]:
        """Get list of pattern names."""
        with self._lock:
            return [p.config.name for p in self._patterns]
    
    def execute_composition(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute patterns in composition."""
        results = []
        current_context = context.copy()
        
        with self._lock:
            patterns = self._patterns.copy()
        
        for pattern in patterns:
            result = pattern.apply(current_context)
            results.append({
                "pattern": pattern.config.name,
                "pattern_type": pattern.config.pattern_type.value,
                "result": result
            })
            
            # Stop if critical failure
            if not result.get("allowed", True):
                if result.get("state") == "open" or result.get("rate_limit_exceeded"):
                    break
            
            current_context["pattern_result"] = result
        
        return {
            "composition": self.name,
            "patterns": results,
            "success": all(r["result"].get("allowed", True) for r in results)
        }


class PatternCompositionTemplate:
    """Pre-built pattern composition templates."""
    
    @staticmethod
    def high_reliability_template() -> PatternCompositionBuilder:
        """Template for high-reliability scenarios."""
        builder = PatternCompositionBuilder("high-reliability")
        
        # Rate limiting
        rate_config = PatternConfig(
            pattern_type=PatternType.RATE_LIMITING,
            name="rate-limit",
            settings={"max_requests": 1000, "window_size_ms": 1000},
            priority=300
        )
        builder.add_pattern(RateLimitPattern(rate_config))
        
        # Circuit breaker
        cb_config = PatternConfig(
            pattern_type=PatternType.CIRCUIT_BREAKER,
            name="circuit-breaker",
            settings={"failure_threshold": 5, "success_threshold": 2},
            priority=200
        )
        builder.add_pattern(CircuitBreakerPattern(cb_config))
        
        # Retry
        retry_config = PatternConfig(
            pattern_type=PatternType.RETRY,
            name="retry",
            settings={"max_retries": 3, "backoff_multiplier": 2.0},
            priority=100
        )
        builder.add_pattern(RetryPattern(retry_config))
        
        return builder
    
    @staticmethod
    def fast_fail_template() -> PatternCompositionBuilder:
        """Template for fail-fast scenarios."""
        builder = PatternCompositionBuilder("fast-fail")
        
        # Tight timeout
        timeout_config = PatternConfig(
            pattern_type=PatternType.TIMEOUT,
            name="timeout",
            settings={"timeout_ms": 1000},
            priority=300
        )
        builder.add_pattern(TimeoutPattern(timeout_config))
        
        # Circuit breaker with aggressive failure threshold
        cb_config = PatternConfig(
            pattern_type=PatternType.CIRCUIT_BREAKER,
            name="circuit-breaker",
            settings={"failure_threshold": 2, "success_threshold": 1},
            priority=200
        )
        builder.add_pattern(CircuitBreakerPattern(cb_config))
        
        return builder


class PatternCompositionAnalyzer:
    """Analyzes pattern compositions."""
    
    @staticmethod
    def get_composition_metrics(builder: PatternCompositionBuilder) -> Dict[str, Any]:
        """Get metrics for entire composition."""
        metrics = {}
        
        for pattern_name in builder.get_patterns():
            # Would get pattern metrics from builder
            pass
        
        return metrics
    
    @staticmethod
    def validate_composition(builder: PatternCompositionBuilder) -> Dict[str, Any]:
        """Validate pattern composition."""
        issues = []
        patterns = builder.get_patterns()
        
        # Check for circular dependencies
        if len(patterns) != len(set(patterns)):
            issues.append("Duplicate patterns detected")
        
        # Check for conflicting patterns
        if "circuit-breaker" in patterns and "retry" in patterns:
            # This is actually good - usually want together
            pass
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "pattern_count": len(patterns)
        }


# ============================================================================
# TEST SUITE
# ============================================================================

class TestPatternConfigs:
    """Test pattern configuration."""
    
    def test_pattern_config_creation(self):
        """Test creating pattern config."""
        config = PatternConfig(
            pattern_type=PatternType.RATE_LIMITING,
            name="test-rate-limit",
            settings={"max_requests": 100}
        )
        
        assert config.name == "test-rate-limit"
        assert config.enabled is True
        assert config.settings["max_requests"] == 100
    
    def test_pattern_config_priority(self):
        """Test pattern config priority."""
        config = PatternConfig(
            pattern_type=PatternType.CIRCUIT_BREAKER,
            name="test",
            priority=50
        )
        
        assert config.priority == 50


class TestRateLimitPattern:
    """Test rate limiting pattern."""
    
    def test_rate_limit_within_threshold(self):
        """Test request within rate limit."""
        config = PatternConfig(
            pattern_type=PatternType.RATE_LIMITING,
            name="rate-limit",
            settings={"max_requests": 10, "window_size_ms": 1000}
        )
        pattern = RateLimitPattern(config)
        
        result = pattern.apply({})
        assert result["allowed"] is True
    
    def test_rate_limit_exceeded(self):
        """Test rate limit exceeded."""
        config = PatternConfig(
            pattern_type=PatternType.RATE_LIMITING,
            name="rate-limit",
            settings={"max_requests": 2, "window_size_ms": 1000}
        )
        pattern = RateLimitPattern(config)
        
        # Fill up the limit
        pattern.apply({})
        pattern.apply({})
        
        # Third request should be rejected
        result = pattern.apply({})
        assert result["allowed"] is False


class TestCircuitBreakerPattern:
    """Test circuit breaker pattern."""
    
    def test_circuit_breaker_closed(self):
        """Test circuit breaker in closed state."""
        config = PatternConfig(
            pattern_type=PatternType.CIRCUIT_BREAKER,
            name="breaker",
            settings={"failure_threshold": 5}
        )
        pattern = CircuitBreakerPattern(config)
        
        context = {"operation_result": {"success": True}}
        result = pattern.apply(context)
        
        assert result["state"] == "closed"
        assert result["allowed"] is True
    
    def test_circuit_breaker_opens_on_failures(self):
        """Test circuit breaker opens on failures."""
        config = PatternConfig(
            pattern_type=PatternType.CIRCUIT_BREAKER,
            name="breaker",
            settings={"failure_threshold": 2}
        )
        pattern = CircuitBreakerPattern(config)
        
        # Trigger failures
        for _ in range(2):
            pattern.apply({"operation_result": {"success": False}})
        
        # Should be open now
        result = pattern.apply({"operation_result": {"success": True}})
        assert result["state"] == "open"


class TestRetryPattern:
    """Test retry pattern."""
    
    def test_retry_succeeds_eventually(self):
        """Test retry succeeds on later attempt."""
        call_count = 0
        def operation():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise Exception("Fail")
            return "success"
        
        config = PatternConfig(
            pattern_type=PatternType.RETRY,
            name="retry",
            settings={"max_retries": 3, "initial_delay_ms": 1}
        )
        pattern = RetryPattern(config)
        
        result = pattern.apply({"operation": operation})
        assert result["success"] is True
    
    def test_retry_exhausted(self):
        """Test retry exhausted."""
        def operation():
            raise Exception("Always fails")
        
        config = PatternConfig(
            pattern_type=PatternType.RETRY,
            name="retry",
            settings={"max_retries": 2, "initial_delay_ms": 1}
        )
        pattern = RetryPattern(config)
        
        result = pattern.apply({"operation": operation})
        assert result["success"] is False


class TestTimeoutPattern:
    """Test timeout pattern."""
    
    def test_timeout_operation_completes(self):
        """Test operation completes within timeout."""
        def quick_op():
            return "done"
        
        config = PatternConfig(
            pattern_type=PatternType.TIMEOUT,
            name="timeout",
            settings={"timeout_ms": 5000}
        )
        pattern = TimeoutPattern(config)
        
        result = pattern.apply({"operation": quick_op})
        assert result["success"] is True


class TestPatternCompositionBuilder:
    """Test pattern composition builder."""
    
    def test_add_pattern(self):
        """Test adding patterns."""
        builder = PatternCompositionBuilder("test-composition")
        
        config = PatternConfig(
            pattern_type=PatternType.RATE_LIMITING,
            name="rate-limit"
        )
        pattern = RateLimitPattern(config)
        
        assert builder.add_pattern(pattern)
        assert "rate-limit" in builder.get_patterns()
    
    def test_remove_pattern(self):
        """Test removing patterns."""
        builder = PatternCompositionBuilder("test-composition")
        
        config = PatternConfig(
            pattern_type=PatternType.RATE_LIMITING,
            name="rate-limit"
        )
        pattern = RateLimitPattern(config)
        builder.add_pattern(pattern)
        
        assert builder.remove_pattern("rate-limit")
        assert "rate-limit" not in builder.get_patterns()
    
    def test_pattern_priority_ordering(self):
        """Test patterns ordered by priority."""
        builder = PatternCompositionBuilder("test")
        
        # Add with lower priority
        config1 = PatternConfig(
            pattern_type=PatternType.RATE_LIMITING,
            name="rate-limit",
            priority=100
        )
        builder.add_pattern(RateLimitPattern(config1))
        
        # Add with higher priority
        config2 = PatternConfig(
            pattern_type=PatternType.CIRCUIT_BREAKER,
            name="breaker",
            priority=200
        )
        builder.add_pattern(CircuitBreakerPattern(config2))
        
        patterns = builder.get_patterns()
        assert patterns[0] == "breaker"  # Higher priority first
        assert patterns[1] == "rate-limit"


class TestPatternCompositionExecution:
    """Test pattern composition execution."""
    
    def test_execute_simple_composition(self):
        """Test executing simple composition."""
        builder = PatternCompositionBuilder("test-composition")
        
        config = PatternConfig(
            pattern_type=PatternType.RATE_LIMITING,
            name="rate-limit",
            settings={"max_requests": 100}
        )
        builder.add_pattern(RateLimitPattern(config))
        
        result = builder.execute_composition({})
        assert result["success"] is True
    
    def test_execute_multi_pattern_composition(self):
        """Test executing composition with multiple patterns."""
        builder = PatternCompositionBuilder("multi-pattern")
        
        # Add rate limit
        rl_config = PatternConfig(
            pattern_type=PatternType.RATE_LIMITING,
            name="rate-limit",
            settings={"max_requests": 100},
            priority=200
        )
        builder.add_pattern(RateLimitPattern(rl_config))
        
        # Add circuit breaker
        cb_config = PatternConfig(
            pattern_type=PatternType.CIRCUIT_BREAKER,
            name="breaker",
            settings={"failure_threshold": 5},
            priority=100
        )
        builder.add_pattern(CircuitBreakerPattern(cb_config))
        
        result = builder.execute_composition({"operation_result": {"success": True}})
        assert len(result["patterns"]) == 2


class TestPatternTemplates:
    """Test pre-built pattern templates."""
    
    def test_high_reliability_template(self):
        """Test high reliability template."""
        builder = PatternCompositionTemplate.high_reliability_template()
        patterns = builder.get_patterns()
        
        assert "rate-limit" in patterns
        assert "circuit-breaker" in patterns
        assert "retry" in patterns
    
    def test_fast_fail_template(self):
        """Test fast-fail template."""
        builder = PatternCompositionTemplate.fast_fail_template()
        patterns = builder.get_patterns()
        
        assert "timeout" in patterns
        assert "circuit-breaker" in patterns


class TestPatternAnalyzer:
    """Test pattern composition analyzer."""
    
    def test_validate_valid_composition(self):
        """Test validating valid composition."""
        builder = PatternCompositionBuilder("test")
        
        config = PatternConfig(
            pattern_type=PatternType.RATE_LIMITING,
            name="rate-limit"
        )
        builder.add_pattern(RateLimitPattern(config))
        
        validation = PatternCompositionAnalyzer.validate_composition(builder)
        assert validation["valid"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
