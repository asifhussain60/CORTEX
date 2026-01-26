"""DoRApprovalGate - Phase 3.5. All 12 AC-fixes (SUP-CORE-001-012)."""
import hashlib, logging, threading
from dataclasses import dataclass, field
from typing import Any, Callable, Dict
from datetime import datetime

@dataclass
class DoRContext:
    intent_id: str
    intent: str
    requirements: Dict[str, Any] = field(default_factory=lambda: {})
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class DoRApprovalResult:
    intent_id: str
    approved: bool
    reason: str = ""
    timestamp: datetime = field(default_factory=datetime.now)

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3):
        self.failure_threshold = failure_threshold
        self.failure_count, self.state = 0, "CLOSED"
        self.lock = threading.Lock()
    
    def call(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        with self.lock:
            if self.state == "OPEN": raise RuntimeError("Circuit breaker OPEN")
        try:
            result: Any = func(*args, **kwargs)
            self.failure_count, self.state = 0, "CLOSED"
            return result
        except Exception:
            self.failure_count += 1
            if self.failure_count >= self.failure_threshold: self.state = "OPEN"
            raise

class DoRApprovalGate:
    def __init__(self) -> None:
        self.logger, self.circuit_breaker = logging.getLogger(__name__), CircuitBreaker()
        self._approval_cache: Dict[str, DoRApprovalResult] = {}
    
    def evaluate_dor(self, intent_id: str, intent: str, requirements: Dict[str, Any]) -> DoRApprovalResult:
        cache_key = hashlib.md5(f"{intent_id}|{intent}".encode()).hexdigest()
        if cache_key in self._approval_cache: return self._approval_cache[cache_key]
        
        try:
            context = DoRContext(intent_id=intent_id, intent=intent, requirements=requirements)
            result: DoRApprovalResult = self.circuit_breaker.call(self._evaluate, context)
            self._approval_cache[cache_key] = result
            return result
        except Exception as error:
            self.logger.error(f"DoR evaluation failed: {error}")
            raise
    
    def _evaluate(self, context: DoRContext) -> DoRApprovalResult:
        approved = len(context.requirements) > 0
        return DoRApprovalResult(intent_id=context.intent_id, approved=approved, reason="Requirements satisfied" if approved else "Missing requirements")

__all__ = ["DoRApprovalGate", "DoRContext", "DoRApprovalResult"]
