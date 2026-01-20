"""Tests for analytics service."""
import pytest
from cortex.core.knowledge.analytics import AnalyticsService, MetricSnapshot

@pytest.fixture
def analytics_service():
    backends = {"backend_a": {}, "backend_b": {}}
    return AnalyticsService(backends)

def test_record_query(analytics_service):
    """Test query recording."""
    analytics_service.record_query("backend_a", "select", 45.2)
    assert "backend_a_select" in analytics_service.usage_stats

def test_multiple_queries(analytics_service):
    """Test multiple query recording."""
    analytics_service.record_query("backend_a", "select", 45.2)
    analytics_service.record_query("backend_a", "select", 52.1)
    analytics_service.record_query("backend_a", "insert", 30.0)
    assert analytics_service.usage_stats["backend_a_select"] == 2
    assert analytics_service.usage_stats["backend_a_insert"] == 1

def test_get_usage_metrics(analytics_service):
    """Test usage metrics retrieval."""
    analytics_service.record_query("backend_a", "select", 45.0)
    analytics_service.record_query("backend_a", "select", 50.0)
    metrics = analytics_service.get_usage_metrics("backend_a")
    assert metrics["total_queries"] == 2
    assert metrics["query_types"]["select"] == 2

def test_usage_metrics_multiple_types(analytics_service):
    """Test usage metrics with multiple query types."""
    analytics_service.record_query("backend_a", "select", 45.0)
    analytics_service.record_query("backend_a", "insert", 30.0)
    analytics_service.record_query("backend_a", "update", 35.0)
    metrics = analytics_service.get_usage_metrics("backend_a")
    assert metrics["total_queries"] == 3
    assert len(metrics["query_types"]) == 3

def test_get_effectiveness_report(analytics_service):
    """Test effectiveness report."""
    analytics_service.record_query("backend_a", "select", 45.0)
    analytics_service.record_query("backend_a", "select", 55.0)
    analytics_service.record_query("backend_a", "select", 40.0)
    report = analytics_service.get_effectiveness_report("backend_a")
    assert "avg_response_time" in report
    assert report["avg_response_time"] == pytest.approx(46.67, abs=0.1)
    assert report["min_time"] == 40.0
    assert report["max_time"] == 55.0

def test_effectiveness_report_empty(analytics_service):
    """Test effectiveness report on empty backend."""
    report = analytics_service.get_effectiveness_report("backend_a")
    assert report["avg_response_time"] == 0

def test_get_optimization_insights(analytics_service):
    """Test optimization insights."""
    # Record slow queries
    for _ in range(10):
        analytics_service.record_query("backend_a", "select", 150.0)
    insights = analytics_service.get_optimization_insights()
    assert isinstance(insights, dict)

def test_optimization_insights_slow_backend(analytics_service):
    """Test insights identify slow backends."""
    for _ in range(150):
        analytics_service.record_query("backend_a", "select", 120.0)
    insights = analytics_service.get_optimization_insights()
    slow_keys = [k for k in insights.keys() if "slow" in k]
    assert len(slow_keys) > 0

def test_optimization_insights_optimization_opportunity(analytics_service):
    """Test insights identify optimization opportunities."""
    for _ in range(150):
        analytics_service.record_query("backend_a", "select", 75.0)
    insights = analytics_service.get_optimization_insights()
    opportunity_keys = [k for k in insights.keys() if "opportunity" in k]
    assert len(opportunity_keys) > 0

def test_generate_report(analytics_service):
    """Test comprehensive report generation."""
    analytics_service.record_query("backend_a", "select", 45.0)
    analytics_service.record_query("backend_b", "insert", 30.0)
    report = analytics_service.generate_report()
    assert "timestamp" in report
    assert "backends" in report
    assert "insights" in report
    assert "backend_a" in report["backends"]
    assert "backend_b" in report["backends"]

def test_report_structure(analytics_service):
    """Test report structure completeness."""
    analytics_service.record_query("backend_a", "select", 45.0)
    report = analytics_service.generate_report()
    backend_report = report["backends"]["backend_a"]
    assert "usage" in backend_report
    assert "effectiveness" in backend_report

def test_performance_data_tracking(analytics_service):
    """Test performance data is tracked."""
    analytics_service.record_query("backend_a", "select", 45.0)
    analytics_service.record_query("backend_a", "select", 55.0)
    assert len(analytics_service.performance_data["backend_a"]) == 2
    assert analytics_service.performance_data["backend_a"][0] == 45.0

def test_multiple_backends_isolation(analytics_service):
    """Test metrics isolated between backends."""
    analytics_service.record_query("backend_a", "select", 45.0)
    analytics_service.record_query("backend_b", "select", 60.0)
    metrics_a = analytics_service.get_usage_metrics("backend_a")
    metrics_b = analytics_service.get_usage_metrics("backend_b")
    assert metrics_a["total_queries"] == 1
    assert metrics_b["total_queries"] == 1

def test_query_count_accuracy(analytics_service):
    """Test query count accuracy."""
    for i in range(25):
        analytics_service.record_query("backend_a", "select", 40.0 + i)
    metrics = analytics_service.get_usage_metrics("backend_a")
    assert metrics["total_queries"] == 25

def test_response_time_statistics(analytics_service):
    """Test response time statistics computation."""
    times = [30.0, 40.0, 50.0, 60.0, 70.0]
    for t in times:
        analytics_service.record_query("backend_a", "query", t)
    report = analytics_service.get_effectiveness_report("backend_a")
    assert report["avg_response_time"] == pytest.approx(50.0)
    assert report["min_time"] == 30.0
    assert report["max_time"] == 70.0
    assert report["query_count"] == 5
