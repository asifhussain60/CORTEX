import pytest

from src.operations.data_collectors.real_time_collectors import (
    DataCollectionCoordinator,
)


@pytest.mark.unit
def test_coordinator_includes_core_collectors():
    coord = DataCollectionCoordinator()
    keys = set(coord.collectors.keys())
    assert {"brain_metrics", "workspace_health", "performance"}.issubset(keys)
    # New collectors added in Phase 3.2
    assert {"token_usage", "conversation_quality"}.issubset(keys)


@pytest.mark.unit
def test_token_usage_collector_returns_expected_fields():
    coord = DataCollectionCoordinator()
    res = coord.collectors["token_usage"].collect_with_cache(force_refresh=True)
    assert res.success
    data = res.data
    assert {
        "tokens_used_recent", "avg_tokens_per_response", "template_hit_rate_percent",
        "response_template_efficiency", "optimization_opportunities"
    }.issubset(set(data.keys()))


@pytest.mark.unit
def test_conversation_quality_collector_returns_quality_metrics():
    coord = DataCollectionCoordinator()
    res = coord.collectors["conversation_quality"].collect_with_cache(force_refresh=True)
    assert res.success
    data = res.data
    assert {
        "avg_turns", "technical_depth_score", "learning_value_score",
        "quality_score", "capture_recommendation"
    }.issubset(set(data.keys()))
