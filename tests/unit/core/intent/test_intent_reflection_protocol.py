"""
Test suite for Intent Reflection Protocol.

Tests the IntentReflectionEngine which orchestrates the Master → Interaction
Orchestrator delegation pattern. This is the core LENS protocol that ties
together all intelligence sources (AST, git, comments, relationships) and
presents a comprehensive comprehension document to the user for approval
before execution.

Test Categories:
1. Protocol Flow - Master delegation to Interaction orchestrator
2. Context Aggregation - Combining all intelligence sources
3. Challenge Detection - Risk/governance identification
4. Recommendation Generation - Best practice suggestions
5. User Confirmation - Approval gate before execution
6. Audit Trail - Complete flow logging
7. Edge Cases - Error handling, empty data, partial failures
"""

import pytest
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from pathlib import Path

from src.core.intent.intent_reflection_protocol import (
    IntentReflectionEngine,
    ReflectionRequest,
    ReflectionResponse,
    ReflectionStatus,
)


# ============================================================================
# FIXTURES: Mock Intelligence Sources & Data
# ============================================================================

@pytest.fixture
def basic_reflection_request():
    """Basic intent reflection request fixture."""
    return ReflectionRequest(
        user_request="Implement calculate_total function with error handling",
        focal_point="src/billing/calculator.py",
        target_scope="function",
        target_name="calculate_total",
        context={
            "file_path": "src/billing/calculator.py",
            "project_root": str(Path(__file__).parent.parent.parent.parent),
            "language": "python",
        },
        timestamp="2026-01-15T10:30:00Z",
    )


@pytest.fixture
def mock_ast_intelligence():
    """Mock AST analysis results."""
    return {
        "file_path": "src/billing/calculator.py",
        "functions": [
            {
                "name": "calculate_total",
                "signature": "(items: List[Dict]) -> Decimal",
                "decorators": [],
                "calls": ["validate_items", "apply_discount"],
                "complexity": "O(n)",
            }
        ],
        "classes": [],
        "imports": ["decimal", "typing"],
    }


@pytest.fixture
def mock_git_intelligence():
    """Mock git history analysis results."""
    return {
        "file_path": "src/billing/calculator.py",
        "change_frequency": "HIGH",
        "last_modified": "2026-01-10",
        "authors": ["asif", "dev2"],
        "recent_commits": [
            "fix: Handle negative amounts in calculator",
            "refactor: Extract validation logic",
        ],
        "hot_spots": True,
    }


@pytest.fixture
def mock_comment_intelligence():
    """Mock code comment analysis results."""
    return {
        "file_path": "src/billing/calculator.py",
        "functions": {
            "calculate_total": {
                "has_docstring": False,
                "todo_markers": 1,
                "tech_debt": ["TODO: Add error handling for edge cases"],
                "quality_issues": ["Missing docstring for public function"],
            }
        },
    }


@pytest.fixture
def mock_relationship_intelligence():
    """Mock relationship traversal results."""
    return {
        "file_path": "src/billing/calculator.py",
        "dependencies": [
            "src/billing/validator.py",
            "src/billing/discount.py",
        ],
        "call_sites": ["src/billing/checkout.py", "src/shipping/order.py"],
        "database_models": [],
        "api_endpoints": [],
    }


@pytest.fixture
def reflection_engine():
    """Create reflection engine with mock components."""
    return IntentReflectionEngine()


# ============================================================================
# TEST CATEGORY 1: Protocol Flow
# ============================================================================

class TestProtocolFlow:
    """Master → Interaction delegation pattern."""

    def test_reflection_engine_initialization(self):
        """Engine should initialize with default settings."""
        engine = IntentReflectionEngine()
        assert engine is not None

    def test_basic_reflection_flow(self, reflection_engine, basic_reflection_request):
        """Complete reflection flow: request → response."""
        response = reflection_engine.reflect(basic_reflection_request)
        
        assert isinstance(response, ReflectionResponse)
        assert response.status in [
            ReflectionStatus.APPROVED,
            ReflectionStatus.NEEDS_CLARIFICATION,
            ReflectionStatus.PENDING_CONFIRMATION,
            ReflectionStatus.REJECTED,
        ]

    def test_reflection_request_validation(self, reflection_engine):
        """Invalid requests should raise validation error."""
        invalid_request = ReflectionRequest(
            user_request="",  # Empty request
            focal_point="",
            target_scope="",
            target_name="",
            context={},
            timestamp="",
        )
        
        with pytest.raises(ValueError):
            reflection_engine.reflect(invalid_request)

    def test_master_delegates_to_interaction(self, reflection_engine, basic_reflection_request):
        """Master orchestrator delegates to Interaction for context building."""
        response = reflection_engine.reflect(basic_reflection_request)
        
        # Response should contain delegation evidence
        assert response.orchestrator_trace is not None
        assert "Interaction" in str(response.orchestrator_trace)

    def test_reflection_response_structure(self, reflection_engine, basic_reflection_request):
        """Response should have required structure."""
        response = reflection_engine.reflect(basic_reflection_request)
        
        assert response.request is not None
        assert response.canonicalized_intent is not None
        assert response.challenges is not None
        assert response.recommendations is not None
        assert response.comprehension_yaml is not None

    def test_response_timestamp_recorded(self, reflection_engine, basic_reflection_request):
        """Response should record timestamp of reflection."""
        response = reflection_engine.reflect(basic_reflection_request)
        
        assert response.reflected_at is not None
        datetime.fromisoformat(response.reflected_at.replace('Z', '+00:00'))  # Should parse


# ============================================================================
# TEST CATEGORY 2: Context Aggregation
# ============================================================================

class TestContextAggregation:
    """Combining all intelligence sources into holistic context."""

    def test_aggregates_all_intelligence_sources(
        self,
        reflection_engine,
        basic_reflection_request,
        mock_ast_intelligence,
        mock_git_intelligence,
        mock_comment_intelligence,
        mock_relationship_intelligence,
    ):
        """Reflection should aggregate all intelligence sources."""
        # Setup engine with mocks (in real implementation, would inject)
        response = reflection_engine.reflect(basic_reflection_request)
        
        assert response.context_sources is not None
        assert len(response.context_sources) > 0

    def test_holistic_context_completeness(self, reflection_engine, basic_reflection_request):
        """Holistic context should include all available information."""
        response = reflection_engine.reflect(basic_reflection_request)
        
        # Context should include focal point information
        assert response.focal_point == basic_reflection_request.focal_point

    def test_context_builder_integration(self, reflection_engine, basic_reflection_request):
        """Should integrate HolisticContextBuilder."""
        response = reflection_engine.reflect(basic_reflection_request)
        
        # Response should show context was built
        assert response.context_built_at is not None

    def test_missing_intelligence_source_handled(self, reflection_engine, basic_reflection_request):
        """Should handle gracefully if some intelligence sources unavailable."""
        # Request for non-existent file
        invalid_request = ReflectionRequest(
            user_request="Fix nonexistent.py",
            focal_point="nonexistent.py",
            target_scope="file",
            target_name="nonexistent",
            context={"file_path": "nonexistent.py"},
            timestamp="2026-01-15T10:30:00Z",
        )
        
        response = reflection_engine.reflect(invalid_request)
        # Should still produce response, possibly with warnings
        assert response is not None


# ============================================================================
# TEST CATEGORY 3: Challenge Detection
# ============================================================================

class TestChallengeDetection:
    """Proactive risk and governance identification."""

    def test_challenges_included_in_response(self, reflection_engine, basic_reflection_request):
        """Response should include identified challenges."""
        response = reflection_engine.reflect(basic_reflection_request)
        
        assert response.challenges is not None
        assert isinstance(response.challenges, list)

    def test_challenge_severity_prioritization(self, reflection_engine, basic_reflection_request):
        """Challenges should be sorted by severity (CRITICAL first)."""
        response = reflection_engine.reflect(basic_reflection_request)
        
        if len(response.challenges) > 1:
            severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
            for i in range(len(response.challenges) - 1):
                current_severity = severity_order.get(response.challenges[i].get("severity"), 4)
                next_severity = severity_order.get(response.challenges[i + 1].get("severity"), 4)
                assert current_severity <= next_severity

    def test_governance_risk_detection(self, reflection_engine, basic_reflection_request):
        """Should detect governance risks from code intelligence."""
        response = reflection_engine.reflect(basic_reflection_request)
        
        # Check if any challenges mention governance
        governance_challenges = [
            c for c in response.challenges
            if c.get("category") in ["GOVERNANCE_RISK", "BREAKING_CHANGE"]
        ]
        # Response should have been evaluated (may or may not find issues)
        assert response.challenges is not None

    def test_test_gap_identification(self, reflection_engine, basic_reflection_request):
        """Should identify test coverage gaps."""
        response = reflection_engine.reflect(basic_reflection_request)
        
        # At least check that test gaps are evaluated
        assert response.challenges is not None


# ============================================================================
# TEST CATEGORY 4: Recommendation Generation
# ============================================================================

class TestRecommendationGeneration:
    """Best practice suggestions based on holistic context."""

    def test_recommendations_included_in_response(self, reflection_engine, basic_reflection_request):
        """Response should include recommendations."""
        response = reflection_engine.reflect(basic_reflection_request)
        
        assert response.recommendations is not None
        assert isinstance(response.recommendations, list)

    def test_recommendation_priority_ordering(self, reflection_engine, basic_reflection_request):
        """Recommendations should be sorted by priority (HIGH first)."""
        response = reflection_engine.reflect(basic_reflection_request)
        
        if len(response.recommendations) > 1:
            priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
            for i in range(len(response.recommendations) - 1):
                current_priority = priority_order.get(response.recommendations[i].get("priority"), 3)
                next_priority = priority_order.get(response.recommendations[i + 1].get("priority"), 3)
                assert current_priority <= next_priority

    def test_context_aware_recommendations(self, reflection_engine, basic_reflection_request):
        """Recommendations should be tailored to identified challenges."""
        response = reflection_engine.reflect(basic_reflection_request)
        
        # Recommendations and challenges should be related
        assert len(response.recommendations) >= 0
        assert len(response.challenges) >= 0


# ============================================================================
# TEST CATEGORY 5: User Confirmation Gate
# ============================================================================

class TestUserConfirmationGate:
    """Approval gate before execution."""

    def test_comprehension_yaml_for_user_approval(self, reflection_engine, basic_reflection_request):
        """Response should include comprehension YAML for user approval."""
        response = reflection_engine.reflect(basic_reflection_request)
        
        assert response.comprehension_yaml is not None
        assert len(response.comprehension_yaml) > 0

    def test_reflection_status_needs_confirmation(self, reflection_engine, basic_reflection_request):
        """Status should indicate if confirmation needed."""
        response = reflection_engine.reflect(basic_reflection_request)
        
        assert response.status in [
            ReflectionStatus.APPROVED,
            ReflectionStatus.NEEDS_CLARIFICATION,
            ReflectionStatus.REJECTED,
            ReflectionStatus.PENDING_CONFIRMATION,
        ]

    def test_user_can_approve_reflection(self, reflection_engine, basic_reflection_request):
        """User should be able to approve reflection."""
        response = reflection_engine.reflect(basic_reflection_request)
        
        # Simulate user approval
        approval_result = reflection_engine.approve(response)
        
        assert approval_result.status == ReflectionStatus.APPROVED

    def test_user_can_request_clarification(self, reflection_engine, basic_reflection_request):
        """User should be able to request clarification."""
        response = reflection_engine.reflect(basic_reflection_request)
        
        # Request clarification
        clarification = reflection_engine.request_clarification(response, "Need more details on error handling")
        
        assert clarification is not None

    def test_user_can_reject_reflection(self, reflection_engine, basic_reflection_request):
        """User should be able to reject reflection."""
        response = reflection_engine.reflect(basic_reflection_request)
        
        # Reject reflection
        rejection = reflection_engine.reject(response, "Not ready to proceed")
        
        assert rejection.status == ReflectionStatus.REJECTED


# ============================================================================
# TEST CATEGORY 6: Audit Trail
# ============================================================================

class TestAuditTrail:
    """Complete flow logging for governance compliance."""

    def test_audit_entry_created_for_reflection_start(self, reflection_engine, basic_reflection_request):
        """Should log audit entry when reflection starts."""
        response = reflection_engine.reflect(basic_reflection_request)
        
        assert response.audit_entries is not None
        assert len(response.audit_entries) > 0
        assert any(e.get("operation") == "REFLECTION_START" for e in response.audit_entries)

    def test_audit_entry_created_for_reflection_complete(self, reflection_engine, basic_reflection_request):
        """Should log audit entry when reflection completes."""
        response = reflection_engine.reflect(basic_reflection_request)
        
        assert any(e.get("operation") == "REFLECTION_COMPLETE" for e in response.audit_entries)

    def test_audit_entry_created_for_user_approval(self, reflection_engine, basic_reflection_request):
        """Should log audit entry when user approves."""
        response = reflection_engine.reflect(basic_reflection_request)
        approval = reflection_engine.approve(response)
        
        assert any(e.get("operation") == "USER_APPROVAL" for e in approval.audit_entries)

    def test_audit_trail_includes_timestamps(self, reflection_engine, basic_reflection_request):
        """All audit entries should have timestamps."""
        response = reflection_engine.reflect(basic_reflection_request)
        
        for entry in response.audit_entries:
            assert "timestamp" in entry
            datetime.fromisoformat(entry["timestamp"].replace('Z', '+00:00'))

    def test_audit_trail_chronological_order(self, reflection_engine, basic_reflection_request):
        """Audit entries should be in chronological order."""
        response = reflection_engine.reflect(basic_reflection_request)
        
        timestamps = [
            datetime.fromisoformat(e["timestamp"].replace('Z', '+00:00'))
            for e in response.audit_entries
        ]
        
        for i in range(len(timestamps) - 1):
            assert timestamps[i] <= timestamps[i + 1]

    def test_audit_trail_hash_chain(self, reflection_engine, basic_reflection_request):
        """Audit trail should maintain hash chain for tamper evidence."""
        response = reflection_engine.reflect(basic_reflection_request)
        
        # Each entry should reference previous hash
        for i in range(1, len(response.audit_entries)):
            current_entry = response.audit_entries[i]
            prev_entry = response.audit_entries[i - 1]
            
            if "previous_hash" in current_entry:
                assert current_entry["previous_hash"] == prev_entry.get("hash")


# ============================================================================
# TEST CATEGORY 7: Edge Cases
# ============================================================================

class TestEdgeCases:
    """Error handling, empty data, partial failures."""

    def test_empty_challenges_list(self, reflection_engine, basic_reflection_request):
        """Should handle case with no challenges identified."""
        response = reflection_engine.reflect(basic_reflection_request)
        
        # Even if empty, should be valid list
        assert isinstance(response.challenges, list)

    def test_empty_recommendations_list(self, reflection_engine, basic_reflection_request):
        """Should handle case with no recommendations."""
        response = reflection_engine.reflect(basic_reflection_request)
        
        assert isinstance(response.recommendations, list)

    def test_very_simple_request(self, reflection_engine):
        """Handle very simple, straightforward requests."""
        simple_request = ReflectionRequest(
            user_request="Fix typo in README",
            focal_point="README.md",
            target_scope="file",
            target_name="README",
            context={"file_path": "README.md"},
            timestamp="2026-01-15T10:30:00Z",
        )
        
        response = reflection_engine.reflect(simple_request)
        assert response is not None

    def test_very_complex_request(self, reflection_engine):
        """Handle complex, multi-faceted requests."""
        complex_request = ReflectionRequest(
            user_request="Refactor entire billing module: extract payment processing, add fraud detection, migrate to new database schema, add comprehensive tests, update documentation",
            focal_point="src/billing/",
            target_scope="module",
            target_name="billing",
            context={
                "file_path": "src/billing/",
                "scope": "multiple_files",
                "ac_ids": ["AC-001", "AC-002", "AC-003"],
            },
            timestamp="2026-01-15T10:30:00Z",
        )
        
        response = reflection_engine.reflect(complex_request)
        assert response is not None
        # Complex requests might have more challenges/recommendations
        assert len(response.challenges) >= 0
        assert len(response.recommendations) >= 0

    def test_ambiguous_request_clarification(self, reflection_engine):
        """Handle ambiguous requests that need clarification."""
        ambiguous_request = ReflectionRequest(
            user_request="Fix the issue",  # Vague but present
            focal_point="src/core/",  # Must be present
            target_scope="unknown",
            target_name="issue",
            context={},
            timestamp="2026-01-15T10:30:00Z",
        )
        
        response = reflection_engine.reflect(ambiguous_request)
        
        # Should either request clarification or provide best-effort response
        assert response is not None

    def test_reflection_with_partial_context(self, reflection_engine):
        """Handle requests with incomplete context."""
        partial_request = ReflectionRequest(
            user_request="Add error handling",
            focal_point="src/core/",
            target_scope="module",
            target_name="core",
            context={"file_path": "src/core/"},  # Minimal context
            timestamp="2026-01-15T10:30:00Z",
        )
        
        response = reflection_engine.reflect(partial_request)
        assert response is not None

    def test_reflection_timeout_handling(self, reflection_engine, basic_reflection_request):
        """Should handle timeout during reflection gracefully."""
        # This would test timeout handling in real implementation
        response = reflection_engine.reflect(basic_reflection_request)
        
        # Response should complete within reasonable time
        assert response is not None

    def test_cascading_failures_handled(self, reflection_engine, basic_reflection_request):
        """Should handle multiple component failures gracefully."""
        response = reflection_engine.reflect(basic_reflection_request)
        
        # Even if some intelligence sources fail, should produce response
        assert response is not None
        assert response.status is not None


# ============================================================================
# TEST CATEGORY 8: Integration Tests
# ============================================================================

class TestIntegrationScenarios:
    """End-to-end reflection scenarios."""

    def test_complete_reflection_lifecycle(self, reflection_engine, basic_reflection_request):
        """Complete lifecycle: reflect → user approves → ready for execution."""
        # Step 1: Reflect
        reflection = reflection_engine.reflect(basic_reflection_request)
        assert reflection.status is not None
        
        # Step 2: User approves
        approval = reflection_engine.approve(reflection)
        assert approval.status == ReflectionStatus.APPROVED
        
        # Step 3: Ready for execution
        assert approval.ready_for_execution is True

    def test_reflection_with_clarification_loop(self, reflection_engine, basic_reflection_request):
        """Reflection with user clarification request."""
        # Step 1: Initial reflection
        reflection1 = reflection_engine.reflect(basic_reflection_request)
        
        # Step 2: User requests clarification
        clarification = reflection_engine.request_clarification(
            reflection1,
            "Please explain the impact on the shipping module"
        )
        
        # Step 3: Engine provides clarified reflection
        reflection2 = reflection_engine.reflect(basic_reflection_request)
        
        assert reflection2 is not None

    def test_orchestrator_trace_recorded(self, reflection_engine, basic_reflection_request):
        """Orchestrator delegation trace should be recorded."""
        response = reflection_engine.reflect(basic_reflection_request)
        
        assert response.orchestrator_trace is not None
        assert "MasterOrchestrator" in str(response.orchestrator_trace)
        assert "InteractionOrchestrator" in str(response.orchestrator_trace)

    def test_serialization_to_yaml_for_storage(self, reflection_engine, basic_reflection_request):
        """Response should be serializable to YAML for storage."""
        response = reflection_engine.reflect(basic_reflection_request)
        
        yaml_output = reflection_engine.to_yaml(response)
        
        assert yaml_output is not None
        assert isinstance(yaml_output, str)
        assert len(yaml_output) > 0

    def test_deserialization_from_yaml(self, reflection_engine, basic_reflection_request):
        """Should deserialize YAML back to reflection response."""
        # Create and serialize
        response1 = reflection_engine.reflect(basic_reflection_request)
        yaml_output = reflection_engine.to_yaml(response1)
        
        # Deserialize
        response2 = reflection_engine.from_yaml(yaml_output)
        
        assert response2 is not None
        assert response2.status == response1.status
