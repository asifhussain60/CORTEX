import pytest

from src.operations.modules.questions.question_router import QuestionRouter


@pytest.mark.integration
def test_router_parameters_include_brain_metrics_when_cortex_status():
    router = QuestionRouter()
    msg = "Show CORTEX system status and brain health"
    res = router.route(msg)
    params = res.parameters
    # Expect at least one known brain metric from collectors OR fallback mock
    assert any(k in params for k in [
        "brain_health_score",  # collectors
        "pattern_accuracy_percent",
        "memory_usage_mb",  # fallback mock path may use this name
    ])


@pytest.mark.integration
def test_router_parameters_include_workspace_metrics_when_tests():
    router = QuestionRouter()
    msg = "How is my code quality and test coverage?"
    res = router.route(msg)
    params = res.parameters
    assert any(k in params for k in [
        "code_quality_score",
        "test_coverage_percent",
        "coverage_percent",
    ])
