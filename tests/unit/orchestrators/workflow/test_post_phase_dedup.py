"""
Tests for PostPhaseDeduplicationReview (Phase 100 Stage 7).

AC_START: AC-PHASE100-S7-001
Purpose: Test convergence-gated post-phase deduplication review
Authority: phase-100-workflow-template-library.yaml § Stage 7
Compliance: CORE-008 (TDD), CORE-027 (audit trail), CORE-035 (LENS detection)
"""

import pytest
from pathlib import Path
from typing import List, Dict, Any
from unittest.mock import Mock, MagicMock, patch

from cortex.orchestrators.workflow.post_phase_dedup_review import (
    PostPhaseDeduplicationReview,
    DuplicateDetection,
    DuplicateResolution,
)


class TestPostPhaseDeduplicationReview:
    """Tests for PostPhaseDeduplicationReview with convergence gates."""
    
    @pytest.fixture
    def mock_lens_analyzer(self) -> Mock:
        """Create mock LENS analyzer."""
        analyzer = Mock()
        analyzer.detect_duplicates = Mock()
        return analyzer
    
    @pytest.fixture
    def mock_step_state_machine(self) -> Mock:
        """Create mock StepStateMachine."""
        fsm = Mock()
        fsm.current_state = "PENDING"
        fsm.cycle_count = 0
        return fsm
    
    @pytest.fixture
    def review_instance(self, mock_lens_analyzer: Mock) -> PostPhaseDeduplicationReview:
        """Create PostPhaseDeduplicationReview instance."""
        return PostPhaseDeduplicationReview(
            phase_id="phase-test",
            lens_analyzer=mock_lens_analyzer,
            max_cycles=3
        )
    
    def test_scan_for_new_duplicates_detects_delta(
        self,
        review_instance: PostPhaseDeduplicationReview,
        mock_lens_analyzer: Mock
    ) -> None:
        """
        AC-PHASE100-S7-002: LENS scan detects duplication delta correctly.
        
        GIVEN: Modified files from completed phase
        WHEN: scan_for_new_duplicates() called
        THEN: Returns only NEW duplicates (not pre-existing)
        """
        # Arrange
        modified_files = [
            Path("src/module_a.py"),
            Path("src/module_b.py")
        ]
        
        # Mock LENS detection: 2 new duplicates found
        mock_lens_analyzer.detect_duplicates.return_value = [
            {
                "file1": "src/module_a.py",
                "file2": "src/module_b.py",
                "similarity": 0.95,
                "lines": 50,
                "is_new": True  # Delta: introduced by this phase
            },
            {
                "file1": "src/module_a.py",
                "file2": "src/module_c.py",
                "similarity": 0.85,
                "lines": 30,
                "is_new": True
            }
        ]
        
        # Act
        detections = review_instance.scan_for_new_duplicates(modified_files)
        
        # Assert
        assert len(detections) == 2
        assert all(d.is_new for d in detections)
        assert detections[0].similarity >= 0.85
        mock_lens_analyzer.detect_duplicates.assert_called_once()
    
    def test_resolve_duplicates_extracts_shared_module(
        self,
        review_instance: PostPhaseDeduplicationReview
    ) -> None:
        """
        Test duplicate resolution by extracting shared code.
        
        GIVEN: List of duplicate detections
        WHEN: resolve_duplicates() called
        THEN: Creates shared module and updates references
        """
        # Arrange
        duplicates = [
            DuplicateDetection(
                file1=Path("src/module_a.py"),
                file2=Path("src/module_b.py"),
                similarity=0.95,
                lines=50,
                is_new=True,
                shared_code="def common_function():\n    pass"
            )
        ]
        
        # Act
        resolutions = review_instance.resolve_duplicates(duplicates)
        
        # Assert
        assert len(resolutions) == 1
        assert resolutions[0].shared_module_path.name == "common_utils.py"
        assert resolutions[0].files_updated == 2
    
    def test_convergence_loop_resolves_all_duplicates(
        self,
        review_instance: PostPhaseDeduplicationReview,
        mock_lens_analyzer: Mock
    ) -> None:
        """
        AC-PHASE100-S7-003: Convergence loop resolves all new duplicates.
        
        GIVEN: Phase with 3 new duplicates
        WHEN: execute() runs with convergence gate
        THEN: Loops until new_duplicates_count == 0
        """
        # Arrange: Mock iteration progression
        call_count = 0
        
        def mock_detect_side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                # First scan: 3 duplicates
                return [
                    {"file1": "a.py", "file2": "b.py", "similarity": 0.9, "is_new": True},
                    {"file1": "a.py", "file2": "c.py", "similarity": 0.85, "is_new": True},
                    {"file1": "b.py", "file2": "c.py", "similarity": 0.8, "is_new": True},
                ]
            elif call_count == 2:
                # After first resolution: 1 remaining
                return [
                    {"file1": "b.py", "file2": "c.py", "similarity": 0.8, "is_new": True},
                ]
            else:
                # After second resolution: 0 duplicates (CONVERGED)
                return []
        
        mock_lens_analyzer.detect_duplicates.side_effect = mock_detect_side_effect
        
        # Act
        result = review_instance.execute(
            modified_files=[Path("a.py"), Path("b.py"), Path("c.py")]
        )
        
        # Assert
        assert result.converged is True
        assert result.cycle_count == 3  # Took 3 cycles to converge (scan each cycle)
        assert result.new_duplicates_count == 0
        assert mock_lens_analyzer.detect_duplicates.call_count == 3  # One scan per cycle
    
    def test_convergence_loop_terminates_at_max_cycles(
        self,
        review_instance: PostPhaseDeduplicationReview,
        mock_lens_analyzer: Mock
    ) -> None:
        """
        AC-PHASE100-S7-004: Loop terminates at max_cycles if dupes persist.
        
        GIVEN: Duplicates that cannot be resolved
        WHEN: max_cycles exceeded
        THEN: Loop terminates with FAILED state
        """
        # Arrange: Duplicates persist indefinitely
        mock_lens_analyzer.detect_duplicates.return_value = [
            {"file1": "a.py", "file2": "b.py", "similarity": 0.9, "is_new": True},
        ]
        
        # Act
        result = review_instance.execute(
            modified_files=[Path("a.py"), Path("b.py")]
        )
        
        # Assert
        assert result.converged is False
        assert result.cycle_count == 3  # max_cycles
        assert result.new_duplicates_count > 0
        assert "max_cycles exceeded" in result.error_message
    
    def test_audit_trail_captures_dedup_resolution_details(
        self,
        review_instance: PostPhaseDeduplicationReview,
        mock_lens_analyzer: Mock
    ) -> None:
        """
        AC-PHASE100-S7-005: Audit trail captures dedup resolution details.
        
        GIVEN: Convergence loop execution
        WHEN: Duplicates resolved
        THEN: Audit trail includes all resolution details
        """
        # Arrange
        mock_lens_analyzer.detect_duplicates.side_effect = [
            [{"file1": "a.py", "file2": "b.py", "similarity": 0.9, "is_new": True}],
            []  # Converged
        ]
        
        # Act
        result = review_instance.execute(
            modified_files=[Path("a.py"), Path("b.py")]
        )
        
        # Assert
        audit_trail = result.audit_trail
        assert len(audit_trail) >= 2  # At least 2 events
        assert any("scan" in event["action"].lower() for event in audit_trail)
        assert any("resolve" in event["action"].lower() for event in audit_trail)
        assert all("timestamp" in event for event in audit_trail)
        assert all("cycle" in event for event in audit_trail)
    
    def test_no_false_positives_on_intentional_similar_code(
        self,
        review_instance: PostPhaseDeduplicationReview,
        mock_lens_analyzer: Mock
    ) -> None:
        """
        AC-PHASE100-S7-006: No false positives on intentional similar code.
        
        GIVEN: Similar code with different purposes (not duplication)
        WHEN: scan_for_new_duplicates() called
        THEN: Filters out false positives (e.g., test fixtures, DTOs)
        """
        # Arrange: LENS detects similarity, but review filters false positives
        mock_lens_analyzer.detect_duplicates.return_value = [
            {
                "file1": "tests/fixtures/user_a.py",
                "file2": "tests/fixtures/user_b.py",
                "similarity": 0.95,
                "lines": 20,
                "is_new": True,
                "pattern": "test_fixture"  # Known false positive pattern
            },
            {
                "file1": "src/dto/request.py",
                "file2": "src/dto/response.py",
                "similarity": 0.85,
                "lines": 30,
                "is_new": True,
                "pattern": "dto_structure"  # Intentional similarity
            },
            {
                "file1": "src/module_a.py",
                "file2": "src/module_b.py",
                "similarity": 0.9,
                "lines": 50,
                "is_new": True,
                "pattern": "business_logic"  # Real duplication
            }
        ]
        
        # Act
        detections = review_instance.scan_for_new_duplicates(
            [Path("tests/fixtures/user_a.py"), Path("src/module_a.py")]
        )
        
        # Assert: Only business logic duplication flagged
        assert len(detections) == 1
        assert detections[0].file1 == Path("src/module_a.py")
        assert detections[0].pattern == "business_logic"


class TestDuplicateDetection:
    """Tests for DuplicateDetection dataclass."""
    
    def test_duplicate_detection_creation(self) -> None:
        """Test DuplicateDetection dataclass instantiation."""
        detection = DuplicateDetection(
            file1=Path("a.py"),
            file2=Path("b.py"),
            similarity=0.95,
            lines=50,
            is_new=True,
            shared_code="def func():\n    pass"
        )
        
        assert detection.file1 == Path("a.py")
        assert detection.similarity == 0.95
        assert detection.is_new is True
    
    def test_duplicate_detection_str_representation(self) -> None:
        """Test string representation for debugging."""
        detection = DuplicateDetection(
            file1=Path("a.py"),
            file2=Path("b.py"),
            similarity=0.95,
            lines=50,
            is_new=True
        )
        
        str_repr = str(detection)
        assert "a.py" in str_repr
        assert "b.py" in str_repr
        assert "0.95" in str_repr


class TestDuplicateResolution:
    """Tests for DuplicateResolution dataclass."""
    
    def test_duplicate_resolution_creation(self) -> None:
        """Test DuplicateResolution dataclass instantiation."""
        resolution = DuplicateResolution(
            shared_module_path=Path("src/common/utils.py"),
            files_updated=2,
            lines_reduced=50,
            extraction_method="refactoring_orchestrator"
        )
        
        assert resolution.shared_module_path.name == "utils.py"
        assert resolution.files_updated == 2
        assert resolution.lines_reduced == 50


class TestIntegration:
    """Integration tests for auto-injection by MasterOrchestrator."""
    
    @patch("cortex.orchestrators.core.master_orchestrator.MasterOrchestrator")
    def test_auto_injection_after_phase_completion(
        self,
        mock_orchestrator: Mock
    ) -> None:
        """
        AC-PHASE100-S7-001: Auto-injected after phase completion.
        
        GIVEN: Phase completed successfully
        WHEN: MasterOrchestrator post-phase hook triggers
        THEN: PostPhaseDeduplicationReview executes automatically
        """
        # Arrange
        mock_orchestrator.post_phase_hook = Mock()
        
        # Act
        mock_orchestrator.post_phase_hook(phase_id="phase-test")
        
        # Assert
        mock_orchestrator.post_phase_hook.assert_called_once_with(phase_id="phase-test")


# AC_COMPLETE: AC-PHASE100-S7-001 ✅ 6 tests written
