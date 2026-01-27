"""
Tests for ComprehensionSession - Multi-turn conversation state machine.

AC-ID: AC-INTENT-001-01, AC-INTENT-001-02, AC-INTENT-001-03
Phase: REMEDIATION-INTENT-001-COMPREHENSION-SESSION
Tests: 24 covering state transitions, revisions, approval workflows
"""

import pytest
from datetime import datetime
from dataclasses import asdict
from cortex.orchestrators.core.comprehension_session import (
    ComprehensionSession,
    ApprovalStatus,
    BrainTier,
)
from cortex.brain.core.intent.comprehension_yaml import (
    ComprehensionYAML,
    IntentSection,
)


class TestComprehensionSessionInitialization:
    """AC-INTENT-001-01: Session initialized with UUID and defaults."""

    def test_session_created_with_uuid(self):
        """Session ID should be generated via uuid.uuid4()."""
        session = ComprehensionSession()
        assert session.session_id is not None
        assert len(session.session_id) == 36  # UUID4 format
        assert "-" in session.session_id

    def test_created_at_timestamp_captured(self):
        """created_at should capture current timestamp."""
        before = datetime.now().isoformat()
        session = ComprehensionSession()
        after = datetime.now().isoformat()
        
        assert session.created_at is not None
        assert before <= session.created_at <= after

    def test_approval_status_defaults_to_pending(self):
        """approval_status should default to PENDING."""
        session = ComprehensionSession()
        assert session.approval_status == ApprovalStatus.PENDING

    def test_revision_count_starts_at_zero(self):
        """revision_count should initialize to 0."""
        session = ComprehensionSession()
        assert session.revision_count == 0

    def test_revision_history_empty_initially(self):
        """revision_history should be empty list initially."""
        session = ComprehensionSession()
        assert session.revision_history == []

    def test_temp_files_empty_initially(self):
        """temp_files should be empty list initially."""
        session = ComprehensionSession()
        assert session.temp_files == []

    def test_knowledge_graph_none_initially(self):
        """knowledge_graph should be None until set."""
        session = ComprehensionSession()
        assert session.knowledge_graph is None

    def test_current_comprehension_none_initially(self):
        """current_comprehension should be None until set."""
        session = ComprehensionSession()
        assert session.current_comprehension is None

    def test_target_tier_none_initially(self):
        """target_tier should be None until set."""
        session = ComprehensionSession()
        assert session.target_tier is None


class BaseComprehensionTest:
    """Base class with helper methods for comprehension tests."""

    def _create_test_comprehension(self) -> ComprehensionYAML:
        """Create a test ComprehensionYAML object."""
        intent = IntentSection(
            type="IMPLEMENT",
            scope={"target_type": "module", "target_name": "test"},
            confidence=0.85,
            keywords=["test", "module"]
        )
        
        return ComprehensionYAML(
            metadata={
                "version": "1.0",
                "generated_at": datetime.now().isoformat(),
                "tool": "CORTEX-LENS",
                "phase": "TEST",
                "schema": "cortex-comprehension-v1"
            },
            intent=intent,
            challenges={},
            recommendations={}
        )


class TestComprehensionSessionRevisionTracking(BaseComprehensionTest):
    """Test revision history tracking across iterations."""

    def test_record_revision_increments_count(self):
        """record_revision() should increment revision_count."""
        session = ComprehensionSession()
        assert session.revision_count == 0
        
        session.record_revision(
            comprehension=self._create_test_comprehension(),
            notes="Initial comprehension"
        )
        
        assert session.revision_count == 1

    def test_record_revision_adds_to_history(self):
        """record_revision() should add timestamped entry to history."""
        session = ComprehensionSession()
        comp = self._create_test_comprehension()
        
        session.record_revision(
            comprehension=comp,
            notes="First revision"
        )
        
        assert len(session.revision_history) == 1
        assert session.revision_history[0]["notes"] == "First revision"
        assert "timestamp" in session.revision_history[0]

    def test_record_multiple_revisions(self):
        """Multiple revisions should be tracked with correct order."""
        session = ComprehensionSession()
        comp1 = self._create_test_comprehension()
        comp2 = self._create_test_comprehension()
        
        session.record_revision(comp1, "First")
        session.record_revision(comp2, "Second")
        
        assert session.revision_count == 2
        assert session.revision_history[0]["notes"] == "First"
        assert session.revision_history[1]["notes"] == "Second"

    def test_revision_history_includes_comprehension_snapshot(self):
        """Revision should store full comprehension snapshot."""
        session = ComprehensionSession()
        comp = self._create_test_comprehension()
        
        session.record_revision(comp, "Test revision")
        
        revision = session.revision_history[0]
        assert "comprehension" in revision
        assert revision["comprehension"] == asdict(comp)

    def test_comprehension_updated_on_revision(self):
        """current_comprehension should be updated to latest revision."""
        session = ComprehensionSession()
        comp1 = self._create_test_comprehension()
        comp2 = self._create_test_comprehension()
        
        session.record_revision(comp1, "First")
        assert session.current_comprehension.metadata["version"] == comp1.metadata["version"]
        
        session.record_revision(comp2, "Second")
        assert session.current_comprehension.metadata["version"] == comp2.metadata["version"]


class TestComprehensionSessionStateTransitions(BaseComprehensionTest):
    """AC-INTENT-001-02: State transitions enforced correctly."""

    def test_pending_to_approved_transition(self):
        """PENDING → APPROVED with timestamp should succeed."""
        session = ComprehensionSession()
        assert session.approval_status == ApprovalStatus.PENDING
        
        session.set_approval_status(ApprovalStatus.APPROVED)
        
        assert session.approval_status == ApprovalStatus.APPROVED
        assert session.approval_timestamp is not None

    def test_pending_to_rejected_transition(self):
        """PENDING → REJECTED with reason should succeed."""
        session = ComprehensionSession()
        session.set_approval_status(ApprovalStatus.REJECTED, reason="Test rejection")
        
        assert session.approval_status == ApprovalStatus.REJECTED
        assert session.rejection_reason == "Test rejection"

    def test_pending_to_needs_clarification_transition(self):
        """PENDING → NEEDS_CLARIFICATION should succeed."""
        session = ComprehensionSession()
        session.set_approval_status(ApprovalStatus.NEEDS_CLARIFICATION)
        
        assert session.approval_status == ApprovalStatus.NEEDS_CLARIFICATION

    def test_approved_to_rejected_transition(self):
        """APPROVED → REJECTED should succeed (revision workflow)."""
        session = ComprehensionSession()
        session.set_approval_status(ApprovalStatus.APPROVED)
        session.set_approval_status(ApprovalStatus.NEEDS_CLARIFICATION)
        
        assert session.approval_status == ApprovalStatus.NEEDS_CLARIFICATION

    def test_rejection_reason_captured(self):
        """rejection_reason should be stored when rejecting."""
        session = ComprehensionSession()
        reason = "User requested changes"
        session.set_approval_status(ApprovalStatus.REJECTED, reason=reason)
        
        assert session.rejection_reason == reason

    def test_approval_timestamp_set_on_approved(self):
        """approval_timestamp should be set when approved."""
        session = ComprehensionSession()
        before = datetime.now().isoformat()
        
        session.set_approval_status(ApprovalStatus.APPROVED)
        
        after = datetime.now().isoformat()
        assert session.approval_timestamp is not None
        assert before <= session.approval_timestamp <= after

    def test_approval_timestamp_not_set_on_other_transitions(self):
        """approval_timestamp should only be set on APPROVED."""
        session = ComprehensionSession()
        session.set_approval_status(ApprovalStatus.REJECTED)
        
        assert session.approval_timestamp is None


class TestComprehensionSessionTempFileManagement:
    """Test temporary file tracking and cleanup."""

    def test_add_temp_file(self):
        """Temp files should be tracked."""
        session = ComprehensionSession()
        
        session.add_temp_file("/tmp/test1.yaml")
        session.add_temp_file("/tmp/test2.yaml")
        
        assert len(session.temp_files) == 2
        assert "/tmp/test1.yaml" in session.temp_files
        assert "/tmp/test2.yaml" in session.temp_files

    def test_cleanup_temp_files_clears_list(self):
        """cleanup_temp_files() should clear temp_files list."""
        session = ComprehensionSession()
        session.add_temp_file("/tmp/test.yaml")
        
        assert len(session.temp_files) == 1
        session.cleanup_temp_files()
        assert len(session.temp_files) == 0

    def test_cleanup_removes_actual_files(self, tmp_path):
        """cleanup_temp_files() should delete actual files."""
        session = ComprehensionSession()
        
        # Create actual temp file
        temp_file = tmp_path / "test.yaml"
        temp_file.write_text("test content")
        
        session.add_temp_file(str(temp_file))
        assert temp_file.exists()
        
        session.cleanup_temp_files()
        assert not temp_file.exists()


class TestComprehensionSessionTargetTier:
    """Test target brain tier selection."""

    def test_set_target_tier_tier0(self):
        """Should be able to set target_tier to TIER0."""
        session = ComprehensionSession()
        session.set_target_tier(BrainTier.TIER0)
        
        assert session.target_tier == BrainTier.TIER0

    def test_set_target_tier_tier1(self):
        """Should be able to set target_tier to TIER1."""
        session = ComprehensionSession()
        session.set_target_tier(BrainTier.TIER1)
        
        assert session.target_tier == BrainTier.TIER1

    def test_set_target_tier_tier2(self):
        """Should be able to set target_tier to TIER2."""
        session = ComprehensionSession()
        session.set_target_tier(BrainTier.TIER2)
        
        assert session.target_tier == BrainTier.TIER2

    def test_set_target_tier_tier3(self):
        """Should be able to set target_tier to TIER3."""
        session = ComprehensionSession()
        session.set_target_tier(BrainTier.TIER3)
        
        assert session.target_tier == BrainTier.TIER3


class TestComprehensionSessionSerialization:
    """Test serialization to dict for YAML output."""

    def test_to_dict_includes_all_fields(self):
        """to_dict() should include all essential fields."""
        session = ComprehensionSession()
        session.set_approval_status(ApprovalStatus.APPROVED)
        
        result = session.to_dict()
        
        assert "session_id" in result
        assert "created_at" in result
        assert "approval_status" in result
        assert "approval_timestamp" in result
        assert "revision_count" in result
        assert "revision_history" in result
        assert "target_tier" in result

    def test_to_dict_approval_status_serialized(self):
        """Approval status should be serialized as string."""
        session = ComprehensionSession()
        session.set_approval_status(ApprovalStatus.APPROVED)
        
        result = session.to_dict()
        
        assert result["approval_status"] == "approved"
        assert isinstance(result["approval_status"], str)

    def test_to_dict_target_tier_serialized(self):
        """Target tier should be serialized as string."""
        session = ComprehensionSession()
        session.set_target_tier(BrainTier.TIER1)
        
        result = session.to_dict()
        
        assert result["target_tier"] == "tier1"
        assert isinstance(result["target_tier"], str)

    def test_to_dict_with_rejection_reason(self):
        """to_dict() should include rejection reason if present."""
        session = ComprehensionSession()
        session.set_approval_status(ApprovalStatus.REJECTED, reason="Invalid intent")
        
        result = session.to_dict()
        
        assert result["rejection_reason"] == "Invalid intent"


class TestComprehensionSessionIntegration(BaseComprehensionTest):
    """Integration tests for full session workflow."""

    def test_full_session_workflow_approved(self):
        """Complete workflow: create → record revision → approve."""
        session = ComprehensionSession()
        comp = self._create_test_comprehension()
        
        # Record initial comprehension
        session.record_revision(comp, "Initial intent analysis")
        assert session.revision_count == 1
        assert session.approval_status == ApprovalStatus.PENDING
        
        # Approve
        session.set_approval_status(ApprovalStatus.APPROVED)
        assert session.approval_status == ApprovalStatus.APPROVED
        assert session.approval_timestamp is not None
        
        # Verify serialization
        result = session.to_dict()
        assert result["approval_status"] == "approved"

    def test_full_session_workflow_rejected_and_revised(self):
        """Workflow: create → record → reject → revise → approve."""
        session = ComprehensionSession()
        comp1 = self._create_test_comprehension()
        comp2 = self._create_test_comprehension()
        
        # Initial comprehension
        session.record_revision(comp1, "First attempt")
        session.set_approval_status(ApprovalStatus.REJECTED, reason="Needs refinement")
        assert session.approval_status == ApprovalStatus.REJECTED
        
        # Revise and re-attempt
        session.set_approval_status(ApprovalStatus.PENDING)
        session.record_revision(comp2, "Refined comprehension")
        session.set_approval_status(ApprovalStatus.APPROVED)
        
        # Verify final state
        assert session.revision_count == 2
        assert session.approval_status == ApprovalStatus.APPROVED
        assert len(session.revision_history) == 2

    def test_multi_turn_context_preservation(self):
        """Session should preserve context across multiple revisions."""
        session = ComprehensionSession()
        
        # Turn 1
        comp1 = self._create_test_comprehension()
        session.record_revision(comp1, "Turn 1: Initial intent")
        
        # Turn 2
        comp2 = self._create_test_comprehension()
        session.record_revision(comp2, "Turn 2: Refined intent")
        
        # Turn 3
        comp3 = self._create_test_comprehension()
        session.record_revision(comp3, "Turn 3: Final intent")
        
        # Verify all turns tracked
        assert len(session.revision_history) == 3
        assert session.revision_history[0]["notes"] == "Turn 1: Initial intent"
        assert session.revision_history[1]["notes"] == "Turn 2: Refined intent"
        assert session.revision_history[2]["notes"] == "Turn 3: Final intent"


class TestComprehensionSessionEdgeCases(BaseComprehensionTest):
    """Test edge cases and error conditions."""

    def test_record_revision_with_none_comprehension_raises(self):
        """record_revision() with None comprehension should raise."""
        session = ComprehensionSession()
        
        with pytest.raises(ValueError):
            session.record_revision(None, "Test")

    def test_set_approval_with_reason_on_non_rejection(self):
        """Setting reason on non-REJECTED status should not raise."""
        session = ComprehensionSession()
        
        # Should not raise
        session.set_approval_status(ApprovalStatus.APPROVED, reason="Some reason")
        assert session.approval_status == ApprovalStatus.APPROVED

    def test_cleanup_with_no_temp_files(self):
        """cleanup_temp_files() with no files should not raise."""
        session = ComprehensionSession()
        
        # Should not raise
        session.cleanup_temp_files()
        assert len(session.temp_files) == 0

    def test_cleanup_with_nonexistent_file(self):
        """cleanup_temp_files() should handle nonexistent files gracefully."""
        session = ComprehensionSession()
        session.add_temp_file("/nonexistent/path/file.yaml")
        
        # Should not raise
        session.cleanup_temp_files()
        assert len(session.temp_files) == 0

    def test_multiple_sessions_independent(self):
        """Multiple sessions should be independent."""
        session1 = ComprehensionSession()
        session2 = ComprehensionSession()
        
        # Modify session1
        session1.set_approval_status(ApprovalStatus.APPROVED)
        
        # session2 should be unaffected
        assert session2.approval_status == ApprovalStatus.PENDING
        assert session1.session_id != session2.session_id
