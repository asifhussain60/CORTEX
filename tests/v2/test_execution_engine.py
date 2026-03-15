"""TDD tests for phase-m2-c ExecutionEngine."""

import pytest

from cortex.core.execution_engine import ExecutionEngine


def test_execution_engine_dispatches_to_registered_handler() -> None:
    engine = ExecutionEngine()
    engine.register_handler("IMPLEMENT", lambda payload: {"handled": payload["request_id"]})

    result = engine.execute("IMPLEMENT", {"request_id": "req-1"})

    assert result["route"] == "IMPLEMENT"
    assert result["status"] == "executed"
    assert result["result"]["handled"] == "req-1"


def test_execution_engine_raises_for_missing_route() -> None:
    engine = ExecutionEngine()

    with pytest.raises(KeyError):
        engine.execute("AUDIT", {"request_id": "req-2"})


def test_execution_engine_accepts_constructor_handlers() -> None:
    engine = ExecutionEngine(handlers={"QUERY": lambda payload: {"echo": payload["message"]}})

    result = engine.execute("QUERY", {"message": "ok"})

    assert result["result"]["echo"] == "ok"
