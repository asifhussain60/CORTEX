"""Phase-m2 consumer migration tests for stage strategies."""

from cortex.orchestrators.core.pipeline_stage_strategy import StageContext
from cortex.orchestrators.core.stage234_strategies import (
    Stage2IntentClassificationStrategy,
    Stage4DomainExecutionStrategy,
)


class _GatewayResult:
    def __init__(self) -> None:
        self.intent = "FIX"
        self.confidence = 0.93
        self.route = "FIX"


class _FakeGateway:
    def process(self, request_text: str) -> _GatewayResult:
        _ = request_text
        return _GatewayResult()


class _FakeResult:
    def __init__(self, payload):
        self._payload = payload

    def is_ok(self) -> bool:
        return True

    def unwrap(self):
        return self._payload


class _FakeTDDOrchestrator:
    def execute_operation(self, operation_name: str, parameters: dict):
        return _FakeResult({"operation": operation_name, "parameters": parameters})


class _FakeExecutionEngine:
    def __init__(self) -> None:
        self._handlers = {}

    def register_handler(self, route: str, handler):
        self._handlers[route] = handler

    def execute(self, route: str, payload: dict):
        return {"route": route, "status": "executed", "result": self._handlers[route](payload)}


def test_stage2_prefers_intent_gateway_when_available() -> None:
    strategy = Stage2IntentClassificationStrategy(dependencies={"intent_gateway": _FakeGateway()})
    context = StageContext(operation_name="fix_bug", parameters={"request": "fix this bug"})

    result = strategy.execute(context)

    assert result.is_ok()
    updated = result.unwrap()
    assert updated.metadata["intent_classification"]["classified_intent"] == "FIX"
    assert updated.metadata["intent_classification"]["routing_target"] == "TDDOrchestrator"


def test_stage4_uses_execution_engine_dispatch_layer() -> None:
    execution_engine = _FakeExecutionEngine()
    strategy = Stage4DomainExecutionStrategy(
        dependencies={
            "execution_engine": execution_engine,
            "tddorchestrator": _FakeTDDOrchestrator(),
        }
    )
    context = StageContext(
        operation_name="fix_bug",
        parameters={"request": "fix this bug"},
        metadata={"intent_classification": {"routing_target": "TDDOrchestrator"}},
    )

    result = strategy.execute(context)

    assert result.is_ok()
    updated = result.unwrap()
    assert updated.metadata["execution"]["dispatch_layer"] == "execution_engine"
    assert updated.metadata["execution"]["orchestrator"] == "TDDOrchestrator"
