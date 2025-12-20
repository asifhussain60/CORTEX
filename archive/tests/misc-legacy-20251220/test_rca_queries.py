"""
Test suite for RCA (Root Cause Analysis) query methods in Tier 2.

Tests bug_resolution pattern queries by symptom, root cause,
recurrence risk, and affected features.

Author: Asif Hussain
Created: 2025-12-09
Phase: TDD Mastery Phase 5.1 (Task 5.1.6)
"""

import pytest
from pathlib import Path
import tempfile
import shutil

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
def sample_rca_patterns(kg):
    """Create sample RCA patterns for testing."""
    patterns = [
        {
            "pattern_id": "rca_auth_001",
            "title": "Authentication Token Expiry",
            "content": "Token refresh fails when server time differs from client",
            "pattern_type": "bug_resolution",
            "confidence": 0.9,
            "metadata": {
                "symptom": "Users logged out unexpectedly",
                "root_cause": "Server time drift caused token validation failure",
                "fix_applied": "Added 30-second clock skew tolerance",
                "prevention": "Monitor server time drift with alerting",
                "recurrence_risk": "low",
                "affected_features": ["authentication", "session_management"]
            }
        },
        {
            "pattern_id": "rca_memory_001",
            "title": "Memory Leak in Background Worker",
            "content": "Worker process memory grows unbounded",
            "pattern_type": "bug_resolution",
            "confidence": 0.95,
            "metadata": {
                "symptom": "Server crashes after 24 hours",
                "root_cause": "Event listeners not unregistered on worker shutdown",
                "fix_applied": "Added cleanup in worker lifecycle",
                "prevention": "Add memory profiling to CI pipeline",
                "recurrence_risk": "high",
                "affected_features": ["background_jobs", "workers", "event_system"]
            }
        },
        {
            "pattern_id": "rca_api_001",
            "title": "API Rate Limiting Issue",
            "content": "Rate limiter incorrectly counting requests",
            "pattern_type": "bug_resolution",
            "confidence": 0.85,
            "metadata": {
                "symptom": "Valid requests rejected with 429",
                "root_cause": "Redis counter keys not expiring correctly",
                "fix_applied": "Fixed TTL on Redis keys",
                "prevention": "Add integration tests for rate limiter",
                "recurrence_risk": "medium",
                "affected_features": ["api", "rate_limiting"]
            }
        },
        {
            "pattern_id": "rca_db_001",
            "title": "Database Connection Pool Exhaustion",
            "content": "Connection pool runs out of connections",
            "pattern_type": "bug_resolution",
            "confidence": 0.92,
            "metadata": {
                "symptom": "Timeouts during peak load",
                "root_cause": "Long-running transactions holding connections",
                "fix_applied": "Implemented connection timeout and monitoring",
                "prevention": "Add connection pool metrics to dashboard",
                "recurrence_risk": "medium",
                "affected_features": ["database", "api", "workers"]
            }
        }
    ]
    
    for pattern in patterns:
        kg.store_pattern(**pattern)
    
    return patterns


class TestRCAQueryBySymptom:
    """Test querying RCA patterns by symptom."""
    
    def test_query_by_symptom_exact_match(self, kg, sample_rca_patterns):
        """Test finding RCA by exact symptom description."""
        results = kg.query_rca_by_symptom("Users logged out unexpectedly")
        
        assert len(results) > 0
        assert results[0]['pattern_id'] == 'rca_auth_001'
        assert results[0]['metadata']['symptom'] == "Users logged out unexpectedly"
    
    def test_query_by_symptom_partial_match(self, kg, sample_rca_patterns):
        """Test finding RCA by partial symptom keyword."""
        results = kg.query_rca_by_symptom("crashes")
        
        assert len(results) > 0
        # Should find memory leak pattern
        found = any(r['pattern_id'] == 'rca_memory_001' for r in results)
        assert found
    
    def test_query_by_symptom_no_results(self, kg, sample_rca_patterns):
        """Test symptom query with no matches."""
        results = kg.query_rca_by_symptom("nonexistent symptom xyz")
        
        assert len(results) == 0


class TestRCAQueryByRootCause:
    """Test querying RCA patterns by root cause."""
    
    def test_query_by_root_cause(self, kg, sample_rca_patterns):
        """Test finding RCA by root cause keywords."""
        results = kg.query_rca_by_root_cause("time drift")
        
        assert len(results) > 0
        assert results[0]['pattern_id'] == 'rca_auth_001'
    
    def test_query_by_root_cause_multiple_results(self, kg, sample_rca_patterns):
        """Test root cause query returning multiple patterns."""
        # "not" appears in multiple root causes
        results = kg.query_rca_by_root_cause("not")
        
        assert len(results) >= 2  # memory and api patterns


class TestRCAQueryByRecurrenceRisk:
    """Test querying RCA patterns by recurrence risk level."""
    
    def test_query_high_risk_patterns(self, kg, sample_rca_patterns):
        """Test finding high-risk RCA patterns."""
        results = kg.query_rca_by_risk("high")
        
        assert len(results) > 0
        assert all(r['metadata']['recurrence_risk'] == 'high' for r in results)
        # Memory leak should be high risk
        assert any(r['pattern_id'] == 'rca_memory_001' for r in results)
    
    def test_query_medium_risk_patterns(self, kg, sample_rca_patterns):
        """Test finding medium-risk RCA patterns."""
        results = kg.query_rca_by_risk("medium")
        
        assert len(results) >= 2  # api and db patterns
        assert all(r['metadata']['recurrence_risk'] == 'medium' for r in results)
    
    def test_query_low_risk_patterns(self, kg, sample_rca_patterns):
        """Test finding low-risk RCA patterns."""
        results = kg.query_rca_by_risk("low")
        
        assert len(results) > 0
        assert all(r['metadata']['recurrence_risk'] == 'low' for r in results)


class TestRCAQueryByAffectedFeatures:
    """Test querying RCA patterns by affected features."""
    
    def test_query_by_single_feature(self, kg, sample_rca_patterns):
        """Test finding RCA affecting specific feature."""
        results = kg.query_rca_by_feature("authentication")
        
        assert len(results) > 0
        assert all('authentication' in r['metadata']['affected_features'] for r in results)
    
    def test_query_by_common_feature(self, kg, sample_rca_patterns):
        """Test finding RCA affecting commonly impacted feature."""
        results = kg.query_rca_by_feature("api")
        
        # Should find multiple patterns affecting API
        assert len(results) >= 2
        assert all('api' in r['metadata']['affected_features'] for r in results)
    
    def test_query_feature_returns_sorted_by_confidence(self, kg, sample_rca_patterns):
        """Test that results are sorted by confidence."""
        results = kg.query_rca_by_feature("workers")
        
        # Should find memory and db patterns
        assert len(results) >= 2
        # Verify descending confidence order
        confidences = [r['confidence'] for r in results]
        assert confidences == sorted(confidences, reverse=True)


class TestRCAComplexQueries:
    """Test complex RCA queries with multiple criteria."""
    
    def test_high_risk_affecting_specific_feature(self, kg, sample_rca_patterns):
        """Test finding high-risk RCA affecting specific feature."""
        results = kg.query_rca_by_risk_and_feature("high", "workers")
        
        assert len(results) > 0
        assert all(r['metadata']['recurrence_risk'] == 'high' for r in results)
        assert all('workers' in r['metadata']['affected_features'] for r in results)
    
    def test_get_prevention_strategies(self, kg, sample_rca_patterns):
        """Test extracting prevention strategies from RCA patterns."""
        results = kg.get_rca_prevention_strategies("api")
        
        # Should get prevention strategies for API-related RCA
        assert len(results) > 0
        assert all('prevention' in r for r in results)
    
    def test_get_all_affected_features(self, kg, sample_rca_patterns):
        """Test getting list of all affected features across RCA patterns."""
        features = kg.get_all_rca_affected_features()
        
        # Should find all unique features
        assert 'authentication' in features
        assert 'workers' in features
        assert 'api' in features
        assert 'database' in features


class TestRCAReportGeneration:
    """Test RCA report generation functionality."""
    
    def test_generate_rca_summary_report(self, kg, sample_rca_patterns):
        """Test generating summary report of all RCA patterns."""
        report = kg.generate_rca_summary()
        
        assert 'total_patterns' in report
        assert report['total_patterns'] == 4
        assert 'by_risk' in report
        assert report['by_risk']['high'] >= 1
        assert report['by_risk']['medium'] >= 2
        assert report['by_risk']['low'] >= 1
    
    def test_generate_feature_impact_report(self, kg, sample_rca_patterns):
        """Test generating report of RCA impact by feature."""
        report = kg.generate_feature_impact_report()
        
        assert len(report) > 0
        # API should be impacted by multiple RCA
        api_entry = next((r for r in report if r['feature'] == 'api'), None)
        assert api_entry is not None
        assert api_entry['rca_count'] >= 2
    
    def test_generate_risk_distribution_report(self, kg, sample_rca_patterns):
        """Test generating report of risk distribution."""
        report = kg.generate_risk_distribution()
        
        assert 'high' in report
        assert 'medium' in report
        assert 'low' in report
        assert report['high'] >= 1
        assert report['medium'] >= 2
