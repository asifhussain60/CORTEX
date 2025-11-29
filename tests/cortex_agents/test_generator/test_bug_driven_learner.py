"""
Tests for Bug-Driven Learning System (Phase 5.1)

Tests bug detection, pattern extraction, and storage in Tier 2 KG.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

from src.cortex_agents.test_generator.bug_driven_learner import (
    BugDrivenLearner,
    BugCategory,
    BugSeverity,
    BugEvent,
    BugPattern
)


@pytest.fixture
def mock_tier2():
    """Mock Tier 2 Knowledge Graph"""
    return Mock()


@pytest.fixture
def mock_pattern_store():
    """Mock Pattern Store"""
    store = Mock()
    store.store_pattern = Mock(return_value={"pattern_id": "test_pattern_id"})
    store.get_pattern = Mock(return_value={
        "pattern_id": "test_pattern_id",
        "confidence": 0.70,
        "metadata": {"bug_count": 1}
    })
    store.update_pattern = Mock(return_value=True)
    return store


@pytest.fixture
def learner(mock_tier2, mock_pattern_store):
    """Bug-Driven Learner instance"""
    return BugDrivenLearner(
        tier2_kg=mock_tier2,
        pattern_store=mock_pattern_store
    )


class TestBugEventCapture:
    """Test bug event capture functionality"""
    
    def test_capture_bug_event_creates_event(self, learner):
        """Test that bug event is created with correct fields"""
        bug = learner.capture_bug_event(
            test_name="test_jwt_expiration",
            test_file="tests/test_auth.py",
            bug_category=BugCategory.SECURITY,
            bug_severity=BugSeverity.CRITICAL,
            description="JWT tokens not expiring",
            expected_behavior="401 after 1 hour",
            actual_behavior="200 indefinitely",
            test_code="def test_jwt_expiration(): ...",
            root_cause="Missing expiration check"
        )
        
        assert bug.test_name == "test_jwt_expiration"
        assert bug.bug_category == BugCategory.SECURITY
        assert bug.bug_severity == BugSeverity.CRITICAL
        assert bug.root_cause == "Missing expiration check"
        assert "bug_" in bug.bug_id
    
    def test_capture_bug_event_with_metadata(self, learner):
        """Test bug event with custom metadata"""
        metadata = {"environment": "production", "user_id": "123"}
        
        bug = learner.capture_bug_event(
            test_name="test_payment_processing",
            test_file="tests/test_payments.py",
            bug_category=BugCategory.LOGIC,
            bug_severity=BugSeverity.HIGH,
            description="Payment processing failure",
            expected_behavior="Payment succeeds",
            actual_behavior="Payment fails",
            test_code="def test_payment(): ...",
            metadata=metadata
        )
        
        assert bug.metadata == metadata
    
    def test_bug_id_includes_timestamp(self, learner):
        """Test that bug ID includes timestamp for uniqueness"""
        bug = learner.capture_bug_event(
            test_name="test_example",
            test_file="tests/test.py",
            bug_category=BugCategory.EDGE_CASE,
            bug_severity=BugSeverity.LOW,
            description="Test bug",
            expected_behavior="Expected",
            actual_behavior="Actual",
            test_code="def test(): ..."
        )
        
        # Bug ID format: bug_YYYYMMDD_HHMMSS_test_name
        assert bug.bug_id.startswith("bug_")
        assert "test_example" in bug.bug_id


class TestPatternExtraction:
    """Test pattern extraction from bug events"""
    
    def test_extract_pattern_from_critical_bug(self, learner):
        """Test pattern extraction from CRITICAL bug"""
        bug = BugEvent(
            bug_id="bug_123",
            test_name="test_sql_injection",
            test_file="tests/test_security.py",
            bug_category=BugCategory.SECURITY,
            bug_severity=BugSeverity.CRITICAL,
            description="SQL injection vulnerability",
            expected_behavior="Parameterized query",
            actual_behavior="String concatenation",
            root_cause="Unsanitized user input",
            test_code='assert "SELECT * FROM users" not in query',
            timestamp=datetime.now().isoformat(),
            metadata={}
        )
        
        pattern = learner.extract_pattern_from_bug(bug)
        
        assert pattern.confidence == 0.95  # CRITICAL = 0.95
        assert pattern.bug_category == BugCategory.SECURITY
        assert "sql_injection" in pattern.title.lower()
        assert pattern.bug_count == 1
    
    def test_extract_pattern_from_medium_bug(self, learner):
        """Test pattern extraction from MEDIUM severity bug"""
        bug = BugEvent(
            bug_id="bug_456",
            test_name="test_empty_list",
            test_file="tests/test_utils.py",
            bug_category=BugCategory.EDGE_CASE,
            bug_severity=BugSeverity.MEDIUM,
            description="Empty list not handled",
            expected_behavior="Return 0 for empty list",
            actual_behavior="Index error",
            root_cause="No length check",
            test_code="assert sum_list([]) == 0",
            timestamp=datetime.now().isoformat(),
            metadata={}
        )
        
        pattern = learner.extract_pattern_from_bug(bug)
        
        assert pattern.confidence == 0.70  # MEDIUM = 0.70
        assert pattern.bug_category == BugCategory.EDGE_CASE
    
    def test_pattern_includes_namespace(self, learner):
        """Test that pattern includes correct namespace"""
        bug = BugEvent(
            bug_id="bug_789",
            test_name="test_bug",
            test_file="tests/test.py",
            bug_category=BugCategory.LOGIC,
            bug_severity=BugSeverity.HIGH,
            description="Logic error",
            expected_behavior="Correct result",
            actual_behavior="Wrong result",
            root_cause="Wrong operator",
            test_code="assert result == expected",
            timestamp=datetime.now().isoformat(),
            metadata={}
        )
        
        pattern = learner.extract_pattern_from_bug(bug, namespace="workspace.myapp")
        
        assert "workspace.myapp" in pattern.namespaces


class TestPatternStorage:
    """Test pattern storage in Tier 2 KG"""
    
    def test_store_bug_pattern_success(self, learner, mock_pattern_store):
        """Test successful pattern storage"""
        pattern = BugPattern(
            pattern_id="pattern_123",
            title="Test Pattern",
            bug_category=BugCategory.SECURITY,
            test_template="def test(): assert condition",
            assertion_pattern="assert result == expected",
            confidence=0.95,
            bug_count=1,
            similar_patterns=[],
            namespaces=["cortex.learned"],
            metadata={}
        )
        
        result = learner.store_bug_pattern(pattern)
        
        assert result is True
        mock_pattern_store.store_pattern.assert_called_once()
    
    def test_store_bug_pattern_pins_high_confidence(self, learner, mock_pattern_store):
        """Test that high-confidence patterns are pinned"""
        pattern = BugPattern(
            pattern_id="pattern_456",
            title="High Confidence Pattern",
            bug_category=BugCategory.SECURITY,
            test_template="def test(): ...",
            assertion_pattern="assert condition",
            confidence=0.95,  # >= 0.90 should be pinned
            bug_count=1,
            similar_patterns=[],
            namespaces=["cortex.learned"],
            metadata={}
        )
        
        learner.store_bug_pattern(pattern)
        
        # Check that is_pinned=True was passed
        call_kwargs = mock_pattern_store.store_pattern.call_args[1]
        assert call_kwargs["is_pinned"] is True
    
    def test_store_bug_pattern_without_pattern_store(self, mock_tier2):
        """Test storage falls back to tier2 if no pattern_store"""
        learner = BugDrivenLearner(tier2_kg=mock_tier2, pattern_store=None)
        
        pattern = BugPattern(
            pattern_id="pattern_789",
            title="Test Pattern",
            bug_category=BugCategory.LOGIC,
            test_template="def test(): ...",
            assertion_pattern="assert condition",
            confidence=0.70,
            bug_count=1,
            similar_patterns=[],
            namespaces=["cortex.learned"],
            metadata={}
        )
        
        # Should not fail, uses legacy tier2
        result = learner.store_bug_pattern(pattern)
        assert result is True


class TestConfidenceUpdates:
    """Test confidence score updates"""
    
    def test_update_confidence_on_bug_caught(self, learner, mock_pattern_store):
        """Test confidence increases when pattern catches another bug"""
        result = learner.update_pattern_confidence(
            pattern_id="test_pattern_id",
            bug_caught=True,
            confidence_boost=0.05
        )
        
        assert result is True
        mock_pattern_store.update_pattern.assert_called_once()
        
        # Verify confidence increased: 0.70 + 0.05 = 0.75
        call_kwargs = mock_pattern_store.update_pattern.call_args[1]
        assert call_kwargs["confidence"] == 0.75
    
    def test_update_confidence_on_false_positive(self, learner, mock_pattern_store):
        """Test confidence decreases on false positive"""
        result = learner.update_pattern_confidence(
            pattern_id="test_pattern_id",
            bug_caught=False,
            confidence_boost=0.05
        )
        
        assert result is True
        
        # Verify confidence decreased: 0.70 - 0.05 = 0.65 (with float tolerance)
        call_kwargs = mock_pattern_store.update_pattern.call_args[1]
        assert abs(call_kwargs["confidence"] - 0.65) < 0.001  # Floating point tolerance
    
    def test_confidence_capped_at_1_0(self, learner, mock_pattern_store):
        """Test confidence doesn't exceed 1.0"""
        mock_pattern_store.get_pattern.return_value = {
            "pattern_id": "test_pattern_id",
            "confidence": 0.98,
            "metadata": {}
        }
        
        learner.update_pattern_confidence(
            pattern_id="test_pattern_id",
            bug_caught=True,
            confidence_boost=0.05
        )
        
        call_kwargs = mock_pattern_store.update_pattern.call_args[1]
        assert call_kwargs["confidence"] == 1.0  # Capped at 1.0, not 1.03
    
    def test_confidence_floored_at_0_0(self, learner, mock_pattern_store):
        """Test confidence doesn't go below 0.0"""
        mock_pattern_store.get_pattern.return_value = {
            "pattern_id": "test_pattern_id",
            "confidence": 0.02,
            "metadata": {}
        }
        
        learner.update_pattern_confidence(
            pattern_id="test_pattern_id",
            bug_caught=False,
            confidence_boost=0.05
        )
        
        call_kwargs = mock_pattern_store.update_pattern.call_args[1]
        assert call_kwargs["confidence"] == 0.0  # Floored at 0.0, not -0.03


class TestCompleteWorkflow:
    """Test complete bug-driven learning workflow"""
    
    def test_learn_from_bug_complete_workflow(self, learner, mock_pattern_store):
        """Test full learning workflow from bug to stored pattern"""
        result = learner.learn_from_bug(
            test_name="test_jwt_expiration",
            test_file="tests/test_auth.py",
            bug_category=BugCategory.SECURITY,
            bug_severity=BugSeverity.CRITICAL,
            description="JWT tokens not expiring",
            expected_behavior="401 after 1 hour",
            actual_behavior="200 indefinitely",
            test_code="def test_jwt_expiration(): assert is_expired(token)",
            root_cause="Missing expiration check"
        )
        
        # Verify workflow completed
        assert "bug_event" in result
        assert "pattern" in result
        assert "similar_patterns" in result
        assert result["stored"] is True
        
        # Verify bug event
        bug = result["bug_event"]
        assert bug["test_name"] == "test_jwt_expiration"
        assert bug["bug_category"] == BugCategory.SECURITY  # Enum comparison
        
        # Verify pattern
        pattern = result["pattern"]
        assert pattern["confidence"] == 0.95  # CRITICAL
        assert pattern["bug_count"] == 1
        
        # Verify storage was called
        mock_pattern_store.store_pattern.assert_called_once()
    
    def test_learn_from_bug_with_custom_namespace(self, learner, mock_pattern_store):
        """Test learning with custom namespace"""
        result = learner.learn_from_bug(
            test_name="test_custom",
            test_file="tests/test.py",
            bug_category=BugCategory.EDGE_CASE,
            bug_severity=BugSeverity.MEDIUM,
            description="Custom bug",
            expected_behavior="Expected",
            actual_behavior="Actual",
            test_code="def test(): ...",
            namespace="workspace.myapp.auth"
        )
        
        pattern = result["pattern"]
        assert "workspace.myapp.auth" in pattern["namespaces"]
    
    def test_learn_from_bug_includes_summary(self, learner, mock_pattern_store):
        """Test that result includes learning summary"""
        result = learner.learn_from_bug(
            test_name="test_example",
            test_file="tests/test.py",
            bug_category=BugCategory.LOGIC,
            bug_severity=BugSeverity.HIGH,
            description="Test bug",
            expected_behavior="Expected",
            actual_behavior="Actual",
            test_code="def test(): ..."
        )
        
        summary = result["learning_summary"]
        assert "confidence" in summary
        assert "similar_count" in summary
        assert "namespace" in summary


class TestUtilityMethods:
    """Test utility methods"""
    
    def test_generalize_test_code_replaces_strings(self, learner):
        """Test that string literals are generalized"""
        test_code = 'assert user_email == "test@example.com"'
        
        template = learner._generalize_test_code(test_code)
        
        assert "{string_value}" in template
        assert "test@example.com" not in template
    
    def test_generalize_test_code_replaces_numbers(self, learner):
        """Test that numeric literals are generalized"""
        test_code = "assert age == 42"
        
        template = learner._generalize_test_code(test_code)
        
        assert "{number_value}" in template
        assert "42" not in template
    
    def test_extract_assertion_pattern_finds_assert(self, learner):
        """Test assertion pattern extraction"""
        test_code = """
        def test_example():
            result = calculate(10, 20)
            assert result == 30
        """
        
        pattern = learner._extract_assertion_pattern(test_code)
        
        assert "assert result == 30" in pattern
    
    def test_extract_assertion_pattern_finds_pytest_raises(self, learner):
        """Test pytest.raises pattern extraction"""
        test_code = """
        def test_exception():
            with pytest.raises(ValueError):
                do_something()
        """
        
        pattern = learner._extract_assertion_pattern(test_code)
        
        assert "pytest.raises" in pattern


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_capture_bug_without_root_cause(self, learner):
        """Test bug capture without root cause is optional"""
        bug = learner.capture_bug_event(
            test_name="test_example",
            test_file="tests/test.py",
            bug_category=BugCategory.EDGE_CASE,
            bug_severity=BugSeverity.LOW,
            description="Test bug",
            expected_behavior="Expected",
            actual_behavior="Actual",
            test_code="def test(): ..."
            # root_cause omitted
        )
        
        assert bug.root_cause is None
    
    def test_find_similar_patterns_handles_no_tier2(self):
        """Test similar pattern search when tier2 is None"""
        learner = BugDrivenLearner(tier2_kg=None, pattern_store=None)
        
        pattern = BugPattern(
            pattern_id="pattern_123",
            title="Test",
            bug_category=BugCategory.LOGIC,
            test_template="def test(): ...",
            assertion_pattern="assert True",
            confidence=0.70,
            bug_count=1,
            similar_patterns=[],
            namespaces=["cortex.learned"],
            metadata={}
        )
        
        similar = learner.find_similar_patterns(pattern)
        
        assert similar == []  # Empty list when tier2 is None
    
    def test_get_learning_statistics_returns_structure(self, learner):
        """Test statistics structure is correct"""
        stats = learner.get_learning_statistics()
        
        assert "total_patterns" in stats
        assert "patterns_by_category" in stats
        assert "avg_confidence" in stats
        assert "high_confidence_patterns" in stats
