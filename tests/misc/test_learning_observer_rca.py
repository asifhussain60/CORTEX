"""
Test suite for LearningObserver RCA query interface.

Tests convenience methods for querying bug patterns from orchestrator context.

Author: Asif Hussain
Created: 2025-12-09
Phase: TDD Mastery Phase 5.1 (Task 5.1.6b)
"""

import pytest
from pathlib import Path
import tempfile
import shutil

from src.orchestrators.learning_observer import LearningObserver
from src.tier2.knowledge_graph import KnowledgeGraph


@pytest.fixture
def temp_db_path():
    """Create temporary database path for testing."""
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / "test_kg.db"
    yield db_path
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def kg(temp_db_path):
    """Create KnowledgeGraph with temporary database."""
    kg_instance = KnowledgeGraph(db_path=temp_db_path)
    yield kg_instance
    if hasattr(kg_instance, 'connection_manager'):
        kg_instance.connection_manager.close()


@pytest.fixture
def observer(kg):
    """Create LearningObserver with test KnowledgeGraph."""
    return LearningObserver(kg)


@pytest.fixture
def sample_bugs(kg):
    """Store sample bug patterns for testing."""
    bugs = [
        {
            "pattern_id": "bug_001",
            "title": "Session Timeout Issue",
            "content": "Users unexpectedly logged out",
            "pattern_type": "bug_resolution",
            "confidence": 0.9,
            "metadata": {
                "symptom": "Users logged out after 5 minutes",
                "root_cause": "Session timeout too aggressive",
                "fix_applied": "Increased timeout to 30 minutes",
                "prevention": "Add session activity monitoring",
                "recurrence_risk": "low",
                "affected_features": ["authentication", "sessions"]
            }
        },
        {
            "pattern_id": "bug_002",
            "title": "Memory Leak in Worker",
            "content": "Worker memory grows unbounded",
            "pattern_type": "bug_resolution",
            "confidence": 0.95,
            "metadata": {
                "symptom": "Server crashes after 24 hours",
                "root_cause": "Event listeners not cleaned up",
                "fix_applied": "Added cleanup in worker shutdown",
                "prevention": "Memory profiling in CI",
                "recurrence_risk": "high",
                "affected_features": ["workers", "background_jobs"]
            }
        },
        {
            "pattern_id": "bug_003",
            "title": "API Rate Limit False Positives",
            "content": "Valid requests rejected",
            "pattern_type": "bug_resolution",
            "confidence": 0.85,
            "metadata": {
                "symptom": "429 errors on valid API calls",
                "root_cause": "Rate limiter counter overflow",
                "fix_applied": "Fixed counter reset logic",
                "prevention": "Add rate limiter integration tests",
                "recurrence_risk": "medium",
                "affected_features": ["api", "rate_limiting"]
            }
        },
        {
            "pattern_id": "bug_004",
            "title": "Authentication Token Refresh",
            "content": "Token refresh fails intermittently",
            "pattern_type": "bug_resolution",
            "confidence": 0.88,
            "metadata": {
                "symptom": "Users logged out unexpectedly",
                "root_cause": "Race condition in token refresh",
                "fix_applied": "Added token refresh lock",
                "prevention": "Add concurrency tests",
                "recurrence_risk": "high",
                "affected_features": ["authentication", "api"]
            }
        }
    ]
    
    for bug in bugs:
        kg.store_pattern(**bug)
    
    return bugs


class TestRCAQueryInterface:
    """Test RCA query convenience methods."""
    
    def test_query_similar_bugs(self, observer, sample_bugs):
        """Test finding similar bugs by symptom."""
        results = observer.query_similar_bugs("logged out")
        
        assert len(results) >= 2
        # Should find bugs with "logged out" in symptom
        symptoms = [r.get("metadata", {}).get("symptom", "") for r in results]
        assert any("logged out" in s.lower() for s in symptoms)
    
    def test_get_high_risk_bugs_all(self, observer, sample_bugs):
        """Test getting all high-risk bugs."""
        results = observer.get_high_risk_bugs()
        
        assert len(results) == 2  # bug_002 and bug_004
        for bug in results:
            metadata = bug.get("metadata", {})
            if isinstance(metadata, str):
                import json
                metadata = json.loads(metadata)
            assert metadata.get("recurrence_risk") == "high"
    
    def test_get_high_risk_bugs_filtered_by_feature(self, observer, sample_bugs):
        """Test getting high-risk bugs for specific feature."""
        results = observer.get_high_risk_bugs(feature="authentication")
        
        assert len(results) >= 1
        # Should find bug_004 (high risk, affects authentication)
        found = any(r.get("pattern_id") == "bug_004" for r in results)
        assert found
    
    def test_get_feature_bug_report(self, observer, sample_bugs):
        """Test generating bug report for a feature."""
        report = observer.get_feature_bug_report("authentication")
        
        assert report["feature"] == "authentication"
        assert report["total_bugs"] >= 2  # bug_001 and bug_004
        assert "risk_distribution" in report
        assert report["risk_distribution"]["high"] >= 1  # bug_004
        assert report["risk_distribution"]["low"] >= 1  # bug_001
        assert "prevention_strategies" in report
        assert len(report["prevention_strategies"]) > 0
        assert "top_bugs" in report
    
    def test_generate_rca_summary_report(self, observer, sample_bugs):
        """Test generating comprehensive RCA summary."""
        report = observer.generate_rca_summary_report()
        
        assert "total_patterns" in report
        assert report["total_patterns"] == 4
        assert "by_risk" in report
        assert report["by_risk"]["high"] == 2
        assert report["by_risk"]["medium"] == 1
        assert report["by_risk"]["low"] == 1
        assert "top_affected_features" in report
        assert len(report["top_affected_features"]) > 0


class TestRCAReportFormat:
    """Test RCA report format and content quality."""
    
    def test_feature_report_includes_prevention_strategies(self, observer, sample_bugs):
        """Test that feature report includes actionable prevention strategies."""
        report = observer.get_feature_bug_report("api")
        
        assert len(report["prevention_strategies"]) > 0
        # Should include prevention strategies from api-related bugs
        strategies = report["prevention_strategies"]
        assert any(len(s) > 0 for s in strategies)
    
    def test_feature_report_risk_distribution_sums_correctly(self, observer, sample_bugs):
        """Test that risk distribution adds up to total bugs."""
        report = observer.get_feature_bug_report("authentication")
        
        total = sum(report["risk_distribution"].values())
        assert total == report["total_bugs"]
    
    def test_summary_report_top_features_sorted(self, observer, sample_bugs):
        """Test that top affected features are sorted by impact."""
        report = observer.generate_rca_summary_report()
        
        top_features = report["top_affected_features"]
        if len(top_features) > 1:
            # Verify descending order by rca_count
            counts = [f["rca_count"] for f in top_features]
            assert counts == sorted(counts, reverse=True)


class TestRCAQueryEdgeCases:
    """Test edge cases for RCA queries."""
    
    def test_query_similar_bugs_no_results(self, observer, sample_bugs):
        """Test symptom query with no matches."""
        results = observer.query_similar_bugs("nonexistent symptom xyz")
        
        assert len(results) == 0
    
    def test_get_high_risk_bugs_feature_not_found(self, observer, sample_bugs):
        """Test feature filter with no matching bugs."""
        results = observer.get_high_risk_bugs(feature="nonexistent_feature")
        
        assert len(results) == 0
    
    def test_get_feature_bug_report_no_bugs(self, observer, sample_bugs):
        """Test feature report with no bugs."""
        report = observer.get_feature_bug_report("nonexistent_feature")
        
        assert report["total_bugs"] == 0
        assert report["risk_distribution"]["high"] == 0
        assert report["risk_distribution"]["medium"] == 0
        assert report["risk_distribution"]["low"] == 0
        assert len(report["prevention_strategies"]) == 0
    
    def test_query_similar_bugs_limit_respected(self, observer, sample_bugs):
        """Test that limit parameter is respected."""
        results = observer.query_similar_bugs("logged out", limit=1)
        
        assert len(results) <= 1
