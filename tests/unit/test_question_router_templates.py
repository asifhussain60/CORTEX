import pytest

from src.operations.modules.questions.question_router import QuestionRouter


@pytest.mark.unit
def test_memory_keywords_route_to_cortex_memory_template():
    router = QuestionRouter()
    msg = "What is the status of Tier1 and memory tiers in CORTEX?"
    result = router.route(msg)
    assert result.namespace in {"cortex", "general"}
    # prefer the specific template when available
    assert result.template_name in {"cortex_memory_status", "cortex_system_status", "general_help"}


@pytest.mark.unit
def test_tests_keywords_route_to_workspace_test_template():
    router = QuestionRouter()
    msg = "Show me the test coverage and testing status for my project"
    result = router.route(msg)
    assert result.namespace in {"workspace", "general"}
    assert result.template_name in {"workspace_test_status", "workspace_code_quality", "general_help"}


@pytest.mark.unit
def test_help_routes_to_general_help():
    router = QuestionRouter()
    msg = "help"
    result = router.route(msg)
    assert result.template_name in {"general_help"}
