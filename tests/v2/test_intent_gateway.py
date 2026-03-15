"""TDD tests for phase-m2-b IntentGateway."""

import pytest

from cortex.core.intent_gateway import IntentGateway


@pytest.fixture()
def gateway() -> IntentGateway:
    return IntentGateway()


def test_intent_gateway_classifies_fix_request(gateway: IntentGateway) -> None:
    result = gateway.process("Please fix the failing authentication bug")

    assert result.intent == "FIX"
    assert result.route == "FIX"
    assert isinstance(result.confidence, float)


def test_intent_gateway_routes_unknown_to_query() -> None:
    gateway = IntentGateway(route_map={"QUERY": "QUERY"})

    result = gateway.process("Can you explain the architecture")

    assert result.route == "QUERY"


def test_intent_gateway_provides_structured_context(gateway: IntentGateway) -> None:
    result = gateway.process("Implement caching in the workflow module")

    assert "intent_type" in result.context
    assert "urgency" in result.context


def test_intent_gateway_rejects_empty_request(gateway: IntentGateway) -> None:
    with pytest.raises(ValueError):
        gateway.process("   ")
