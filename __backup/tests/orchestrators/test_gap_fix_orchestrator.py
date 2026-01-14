"""
Gap-Fix Orchestrator Tests - AC-GAPFIX-001 to AC-GAPFIX-003.

Tests for the 14-phase gap-fix pipeline orchestrator.

Acceptance Criteria Coverage:
- AC-GAPFIX-001: Gap detection via canonical source comparison
- AC-GAPFIX-002: Remediation plan generation (snowball strategy)
- AC-GAPFIX-003: Plan synchronization via MCP align_plan_sync

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
import tempfile
from pathlib import Path
from typing import Dict, Any, Generator
from unittest.mock import Mock, MagicMock, patch

from src.orchestrators.gap_fix.gap_fix_orchestrator import (
    GapFixOrchestrator,
    GapFixConfig,
    GapFixResult,
    GapFinding,
    SearchPhaseResult,
    AlignPhaseResult,
    SnowballStrategy,
)


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def temp_workspace(tmp_path: Path) -> Path:
    """Create temporary workspace with canonical sources."""
    # Create cortex-brain structure
    brain_dir = tmp_path / "cortex-brain"
    brain_dir.mkdir()
    
    # Create documents/planning structure
    planning_dir = brain_dir / "documents" / "planning" / "active" / "cortex6"
    planning_dir.mkdir(parents=True)
    
    # Create requirements folder (NEW STRUCTURE)
    requirements_dir = planning_dir / "requirements"
    requirements_dir.mkdir()
    
    # Create canonical source: CX6-requirements.yaml
    requirements_content = """
metadata:
  version: 1.1.0
  status: ACTIVE
requirements:
  - id: SR-001
    name: Test Requirement
    status: IMPLEMENTED
"""
    (requirements_dir / "CX6-requirements.yaml").write_text(requirements_content)
    
    # Create canonical source: CX6-acceptance-criteria.yaml
    ac_content = """
metadata:
  version: 17.1.0
acceptance_criteria:
  - id: AC-TEST-001
    criterion: Test criterion
    status: PENDING
"""
    (requirements_dir / "CX6-acceptance-criteria.yaml").write_text(ac_content)
    
    # Create src directory
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "__init__.py").touch()
    
    return tmp_path


@pytest.fixture
def orchestrator(temp_workspace: Path) -> GapFixOrchestrator:
    """Create Gap-Fix orchestrator instance."""
    return GapFixOrchestrator(
        workspace_path=temp_workspace,
        brain_path=temp_workspace / "cortex-brain"
    )


# =============================================================================
# AC-GAPFIX-001: Gap Detection
# =============================================================================

class TestGapDetection:
    """Tests for AC-GAPFIX-001: Gap detection via canonical source comparison."""
    
    def test_loads_canonical_sources(self, orchestrator: GapFixOrchestrator, temp_workspace: Path):
        """
        AC-GAPFIX-001: Loads canonical sources for comparison.
        
        GIVEN: A workspace with CX6-requirements.yaml and CX6-acceptance-criteria.yaml
        WHEN: Gap-Fix loads canonical sources
        THEN: Both files are loaded and parsed
        """
        # Act
        sources = orchestrator.load_canonical_sources()
        
        # Assert
        assert sources.requirements is not None
        assert sources.acceptance_criteria is not None
        assert sources.requirements_version == "1.1.0"
        assert sources.ac_version == "17.1.0"
    
    def test_detects_implementation_gaps(self, orchestrator: GapFixOrchestrator, temp_workspace: Path):
        """
        AC-GAPFIX-001: Detects gaps between requirements and implementation.
        
        GIVEN: Canonical sources and implementation files
        WHEN: Gap-Fix scans for gaps
        THEN: Returns list of identified gaps
        """
        # Act
        findings = orchestrator.detect_gaps()
        
        # Assert
        assert isinstance(findings, list)
        for finding in findings:
            assert isinstance(finding, GapFinding)
            assert finding.gap_id is not None
            assert finding.severity in ["critical", "high", "medium", "low"]
    
    def test_filters_completed_work_from_progress_tracker(
        self, orchestrator: GapFixOrchestrator, temp_workspace: Path
    ):
        """
        AC-GAPFIX-001: Filters out completed work based on progress tracker.
        
        GIVEN: Progress tracker with completed AC IDs
        WHEN: Gap-Fix detects gaps
        THEN: Skips AC IDs marked complete in progress tracker
        """
        # Arrange: Create progress tracker with completed work (NEW STRUCTURE)
        tracker_dir = temp_workspace / "cortex-brain/documents/planning/active/cortex6/execution/tracking"
        tracker_dir.mkdir(parents=True)
        
        tracker_content = {
            "stages": [
                {
                    "status": "COMPLETE",
                    "tasks": [
                        {
                            "status": "COMPLETE",
                            "evidence": {
                                "ac_validated": ["AC-TEST-001"]
                            }
                        }
                    ]
                }
            ]
        }
        
        import json
        (tracker_dir / "progress-tracker.json").write_text(json.dumps(tracker_content))
        
        # Act
        findings = orchestrator.detect_gaps()
        
        # Assert: AC-TEST-001 should be filtered out
        gap_ids = [f.source_reference for f in findings]
        assert "AC-TEST-001" not in gap_ids
    
    def test_categorizes_gap_severity(self, orchestrator: GapFixOrchestrator):
        """
        AC-GAPFIX-001: Categorizes gaps by severity.
        
        GIVEN: A list of detected gaps
        WHEN: Gaps are categorized
        THEN: Each gap has severity: critical, high, medium, or low
        """
        # Arrange
        gap = GapFinding(
            gap_id="GAP-001",
            category="missing_implementation",
            description="Missing orchestrator",
            severity="critical",
            source_reference="AC-TDD-MASTER-001",
            affected_files=[]
        )
        
        # Act
        severity = orchestrator.categorize_severity(gap)
        
        # Assert
        assert severity in ["critical", "high", "medium", "low"]


# =============================================================================
# AC-GAPFIX-002: Remediation Plan Generation
# =============================================================================

class TestRemediationPlan:
    """Tests for AC-GAPFIX-002: Remediation plan generation."""
    
    def test_generates_snowball_strategy(self, orchestrator: GapFixOrchestrator, temp_workspace: Path):
        """
        AC-GAPFIX-002: Generates snowball strategy from gaps.
        
        GIVEN: A list of detected gaps
        WHEN: Gap-Fix generates remediation plan
        THEN: Returns SnowballStrategy with prioritized layers
        """
        # Arrange
        gaps = [
            GapFinding(
                gap_id="GAP-001",
                category="missing_implementation",
                description="Test gap",
                severity="critical",
                source_reference="AC-TEST-001",
                affected_files=[]
            )
        ]
        
        # Act
        strategy = orchestrator.generate_snowball_strategy(gaps)
        
        # Assert
        assert isinstance(strategy, SnowballStrategy)
        assert len(strategy.layers) >= 1
        assert strategy.total_effort_hours >= 0
    
    def test_prioritizes_blocking_gaps(self, orchestrator: GapFixOrchestrator):
        """
        AC-GAPFIX-002: Blocking gaps are prioritized first.
        
        GIVEN: Gaps with different severities
        WHEN: Snowball strategy is generated
        THEN: Critical/blocking gaps are in Layer 1
        """
        # Arrange
        gaps = [
            GapFinding(gap_id="GAP-001", category="missing", description="Low priority",
                      severity="low", source_reference="", affected_files=[]),
            GapFinding(gap_id="GAP-002", category="missing", description="Critical",
                      severity="critical", source_reference="", affected_files=[], blocking=True),
        ]
        
        # Act
        strategy = orchestrator.generate_snowball_strategy(gaps)
        
        # Assert
        layer1_tasks = strategy.layers[0].tasks
        assert any(t.gap_id == "GAP-002" for t in layer1_tasks)
    
    def test_estimates_effort_hours(self, orchestrator: GapFixOrchestrator):
        """
        AC-GAPFIX-002: Estimates effort hours for remediation.
        
        GIVEN: A gap finding
        WHEN: Effort is estimated
        THEN: Returns reasonable hour estimate
        """
        # Arrange
        gap = GapFinding(
            gap_id="GAP-001",
            category="missing_orchestrator",
            description="Implement orchestrator",
            severity="high",
            source_reference="",
            affected_files=[]
        )
        
        # Act
        hours = orchestrator.estimate_effort(gap)
        
        # Assert
        assert isinstance(hours, (int, float))
        assert hours > 0
        assert hours <= 100  # Reasonable upper bound


# =============================================================================
# AC-GAPFIX-003: Plan Synchronization
# =============================================================================

class TestPlanSynchronization:
    """Tests for AC-GAPFIX-003: Plan synchronization via MCP."""
    
    def test_generates_align_plan_request(self, orchestrator: GapFixOrchestrator):
        """
        AC-GAPFIX-003: Generates MCP align_plan_sync request.
        
        GIVEN: A snowball strategy
        WHEN: Gap-Fix prepares sync request
        THEN: Valid MCP request is generated
        """
        # Arrange
        strategy = SnowballStrategy(
            generated_at="2026-01-10",
            total_issues=5,
            layers=[],
            total_effort_hours=20
        )
        
        # Act
        request = orchestrator.generate_sync_request(strategy)
        
        # Assert
        assert request is not None
        assert "strategy" in request or "plan" in request
    
    def test_validates_no_conflicts(self, orchestrator: GapFixOrchestrator, temp_workspace: Path):
        """
        AC-GAPFIX-003: Validates no conflicts with existing plans.
        
        GIVEN: A remediation strategy
        WHEN: Gap-Fix validates against existing plans
        THEN: Returns conflict report (empty if no conflicts)
        """
        # Arrange
        strategy = SnowballStrategy(
            generated_at="2026-01-10",
            total_issues=1,
            layers=[],
            total_effort_hours=4
        )
        
        # Act
        conflicts = orchestrator.validate_conflicts(strategy)
        
        # Assert
        assert isinstance(conflicts, list)
        # No conflicts expected in empty workspace


# =============================================================================
# PHASE EXECUTION TESTS
# =============================================================================

class TestPhaseExecution:
    """Tests for 14-phase pipeline execution."""
    
    def test_execute_search_phases(self, orchestrator: GapFixOrchestrator, temp_workspace: Path):
        """
        Phases 0-4 (SEARCH): Canonical loading and gap detection.
        
        GIVEN: A configured orchestrator
        WHEN: Search phases execute
        THEN: SearchPhaseResult with findings is returned
        """
        # Act
        result = orchestrator.execute_search_phases()
        
        # Assert
        assert isinstance(result, SearchPhaseResult)
        assert result.canonical_sources_loaded is True
        assert isinstance(result.findings, list)
    
    def test_execute_align_phases(self, orchestrator: GapFixOrchestrator, temp_workspace: Path):
        """
        Phases 6-11 (ALIGN): Strategy generation and validation.
        
        GIVEN: Search phase results
        WHEN: Align phases execute
        THEN: AlignPhaseResult with strategy is returned
        """
        # Arrange
        search_result = orchestrator.execute_search_phases()
        
        # Act
        result = orchestrator.execute_align_phases(search_result)
        
        # Assert
        assert isinstance(result, AlignPhaseResult)
        assert result.strategy_generated is True
        assert result.conflicts_validated is True


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestFullPipeline:
    """Integration tests for complete 14-phase pipeline."""
    
    def test_full_pipeline_execution(self, orchestrator: GapFixOrchestrator, temp_workspace: Path):
        """
        Full 14-phase pipeline completes successfully.
        
        GIVEN: A workspace with canonical sources
        WHEN: Full pipeline executes
        THEN: GapFixResult indicates success with artifacts
        """
        # Act
        result = orchestrator.execute()
        
        # Assert
        assert isinstance(result, GapFixResult)
        assert result.success is True
        assert result.phases_completed >= 12  # At least main phases
        assert "search_findings" in result.artifacts
        assert "snowball_strategy" in result.artifacts
