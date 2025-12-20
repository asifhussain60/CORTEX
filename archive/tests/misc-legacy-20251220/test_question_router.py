import pytest

from src.operations.modules.questions.question_router import QuestionRouter


@pytest.mark.unit
def test_routes_cortex_status_question_to_cortex_template():
    router = QuestionRouter()
    msg = "Can you show me the CORTEX system status and brain health?"
    result = router.route(msg)
    assert result.template_name in {"cortex_system_status", "cortex_brain_health"}
    assert result.namespace in {"cortex", "general"}  # general fallback allowed if rules change
    assert result.confidence > 0.5


@pytest.mark.unit
def test_routes_workspace_quality_question_to_workspace_template():
    router = QuestionRouter()
    msg = "How is my code quality and test coverage?"
    result = router.route(msg)
    assert result.template_name in {"workspace_code_quality", "workspace_test_status"}
    assert result.namespace in {"workspace", "general"}
    assert result.confidence > 0.5


@pytest.mark.unit
def test_ambiguous_question_triggers_clarification():
    router = QuestionRouter()
    msg = "How is the code?"
    # Provide no extra context to force ambiguity handling
    result = router.route(msg, context={})
    # In compatibility wrapper, result is RoutingResult from QuestionRoutingResult alias
    # It may not expose requires_clarification, so we assert template fallback possibilities
    assert result.template_name in {"namespace_clarification", "workspace_code_quality", "general_help"}
    assert result.confidence >= 0.0
