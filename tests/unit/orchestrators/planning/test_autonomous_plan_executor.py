"""Tests for AutonomousPlanExecutor.

Author: Asif Hussain
Version: 1.0
"""

import pytest
from pathlib import Path
from cortex.orchestrators.planning.autonomous_plan_executor import (
    AutonomousPlanExecutor,
    ContinuationContext,
    PhaseStatus,
    check_autonomous_continuation
)


@pytest.fixture
def sample_registry():
    """Sample registry data for testing."""
    return {
        "version": "1.0",
        "active_phases": [
            {
                "id": "phase-21",
                "name": "JSON-First Rewrite",
                "file": "phases/active/phase-21.yaml",
                "status": "in-progress",
                "priority": "P0",
                "started": "2026-02-01"
            },
            {
                "id": "phase-22",
                "name": "ASK Mode System",
                "file": "phases/active/phase-22.yaml",
                "status": "planned",
                "priority": "P0"
            }
        ],
        "completed_phases_2026": {
            "count": 5,
            "phases": [
                "phase-19-lens-unified.yaml",
                "phase-20-instrumentation.yaml"
            ]
        }
    }


class TestContinuationDetection:
    """Test continuation intent detection."""
    
    def test_detect_continue_keyword(self):
        """Should detect 'continue' keyword."""
        executor = AutonomousPlanExecutor()
        assert executor.detect_continuation_intent("continue with phase 2")
    
    def test_detect_proceed_keyword(self):
        """Should detect 'proceed' keyword."""
        executor = AutonomousPlanExecutor()
        assert executor.detect_continuation_intent("proceed to next phase")
    
    def test_detect_phase_number(self):
        """Should detect phase number references."""
        executor = AutonomousPlanExecutor()
        assert executor.detect_continuation_intent("implement phase 2")
        assert executor.detect_continuation_intent("start phase 3")
    
    def test_detect_autonomous_keyword(self):
        """Should detect 'autonomously' keyword."""
        executor = AutonomousPlanExecutor()
        assert executor.detect_continuation_intent("proceed autonomously")
    
    def test_detect_bypass_challenge(self):
        """Should detect 'bypass challenge' phrase."""
        executor = AutonomousPlanExecutor()
        assert executor.detect_continuation_intent("bypass challenge and continue")
    
    def test_no_continuation_exploratory(self):
        """Should NOT detect continuation for exploratory requests."""
        executor = AutonomousPlanExecutor()
        assert not executor.detect_continuation_intent("what should we do next?")
        assert not executor.detect_continuation_intent("how does this work?")
        assert not executor.detect_continuation_intent("explain the architecture")


class TestContextAnalysis:
    """Test continuation context analysis."""
    
    def test_analyze_with_in_progress_phase(self, sample_registry):
        """Should identify in-progress phase as next."""
        executor = AutonomousPlanExecutor()
        context = executor.analyze_continuation_context(
            "continue with phase 2",
            sample_registry
        )
        
        assert context.should_continue
        assert context.next_phase == "phase-21"
        assert len(context.active_phases) == 2
        assert "Continuation intent detected" in context.continuation_reason
    
    def test_analyze_with_planned_phase_only(self, sample_registry):
        """Should identify planned phase when no in-progress."""
        # Remove in-progress status
        sample_registry["active_phases"][0]["status"] = "completed"
        
        executor = AutonomousPlanExecutor()
        context = executor.analyze_continuation_context(
            "proceed to next phase",
            sample_registry
        )
        
        assert context.should_continue
        assert context.next_phase == "phase-22"
    
    def test_analyze_no_continuation_intent(self, sample_registry):
        """Should not continue for exploratory request."""
        executor = AutonomousPlanExecutor()
        context = executor.analyze_continuation_context(
            "what is the architecture?",
            sample_registry
        )
        
        assert not context.should_continue
        assert "No continuation intent" in context.continuation_reason
    
    def test_analyze_no_next_phase(self, sample_registry):
        """Should not continue when no phases available."""
        # Mark all phases as completed
        sample_registry["active_phases"] = []
        
        executor = AutonomousPlanExecutor()
        context = executor.analyze_continuation_context(
            "continue",
            sample_registry
        )
        
        assert not context.should_continue
        assert context.next_phase is None
    
    def test_last_completed_phase_extraction(self, sample_registry):
        """Should extract last completed phase correctly."""
        executor = AutonomousPlanExecutor()
        context = executor.analyze_continuation_context(
            "continue",
            sample_registry
        )
        
        assert context.last_completed_phase == "phase-20-instrumentation"


class TestPhaseStatusMapping:
    """Test phase status extraction."""
    
    def test_phase_status_all_fields(self, sample_registry):
        """Should map all phase fields correctly."""
        executor = AutonomousPlanExecutor()
        context = executor.analyze_continuation_context(
            "continue",
            sample_registry
        )
        
        phase = context.active_phases[0]
        assert phase.phase_id == "phase-21"
        assert phase.name == "JSON-First Rewrite"
        assert phase.status == "in-progress"
        assert phase.priority == "P0"
        assert phase.started == "2026-02-01"
        assert phase.file_path == "phases/active/phase-21.yaml"
    
    def test_phase_status_defaults(self, sample_registry):
        """Should use defaults for missing fields."""
        # Remove optional fields
        del sample_registry["active_phases"][1]["priority"]
        
        executor = AutonomousPlanExecutor()
        context = executor.analyze_continuation_context(
            "continue",
            sample_registry
        )
        
        phase = context.active_phases[1]
        assert phase.priority == "P2"  # Default
        assert phase.started is None
        assert phase.completed is None


class TestHeaderGeneration:
    """Test autonomous execution header."""
    
    def test_format_header_with_phase(self, sample_registry):
        """Should format header with phase information."""
        executor = AutonomousPlanExecutor()
        context = executor.analyze_continuation_context(
            "continue",
            sample_registry
        )
        
        header = executor.format_autonomous_header(context)
        
        assert "CORTEX Architect (Autonomous)" in header
        assert "phase-21" in header
        assert "Challenge bypassed" in header
        assert "🔵 Executing" in header
    
    def test_format_header_no_phase(self):
        """Should handle missing next phase."""
        executor = AutonomousPlanExecutor()
        context = ContinuationContext(
            last_completed_phase=None,
            next_phase=None,
            active_phases=[],
            registry_path=Path("."),
            should_continue=False,
            continuation_reason="No phases"
        )
        
        header = executor.format_autonomous_header(context)
        assert "unknown" in header


class TestBypassDecision:
    """Test challenge bypass decision logic."""
    
    def test_bypass_decision_continue(self, sample_registry, monkeypatch):
        """Should decide to bypass challenge for continuation."""
        executor = AutonomousPlanExecutor()
        
        # Mock load_registry
        monkeypatch.setattr(executor, "load_registry", lambda: sample_registry)
        
        decision = executor.should_bypass_challenge("continue with phase 2")
        
        assert decision["bypass"] is True
        assert decision["next_phase"] == "phase-21"
        assert "Continuation intent detected" in decision["reason"]
        assert isinstance(decision["context"], ContinuationContext)
    
    def test_bypass_decision_exploratory(self, sample_registry, monkeypatch):
        """Should NOT bypass challenge for exploratory request."""
        executor = AutonomousPlanExecutor()
        monkeypatch.setattr(executor, "load_registry", lambda: sample_registry)
        
        decision = executor.should_bypass_challenge("what is the best approach?")
        
        assert decision["bypass"] is False
        assert "No continuation intent" in decision["reason"]
    
    def test_bypass_decision_no_phases(self, sample_registry, monkeypatch):
        """Should NOT bypass when no next phase."""
        sample_registry["active_phases"] = []
        executor = AutonomousPlanExecutor()
        monkeypatch.setattr(executor, "load_registry", lambda: sample_registry)
        
        decision = executor.should_bypass_challenge("continue")
        
        assert decision["bypass"] is False
        assert decision["next_phase"] is None


class TestConvenienceFunction:
    """Test convenience function for prompt integration."""
    
    def test_check_autonomous_continuation(self, monkeypatch, sample_registry):
        """Should provide simple API for prompts."""
        # Mock the executor's load_registry
        def mock_load():
            return sample_registry
        
        from cortex.orchestrators.planning import autonomous_plan_executor
        monkeypatch.setattr(
            autonomous_plan_executor.AutonomousPlanExecutor,
            "load_registry",
            lambda self: sample_registry
        )
        
        result = check_autonomous_continuation("continue with implementation")
        
        assert isinstance(result, dict)
        assert "bypass" in result
        assert "reason" in result
        assert "next_phase" in result
        assert "context" in result


class TestTemplateGeneration:
    """Test execution template generation."""
    
    def test_generate_template_with_phase(self, sample_registry, monkeypatch, tmp_path):
        """Should generate full execution template."""
        # Create mock phase file
        phase_content = """
phase_id: "phase-21"
title: "JSON-First Rewrite"
objectives:
  - "Implement JSON data model"
  - "Create template rendering"
estimated_hours: 8
"""
        phase_dir = tmp_path / "phases" / "active"
        phase_dir.mkdir(parents=True)
        phase_file = phase_dir / "phase-21.yaml"
        phase_file.write_text(phase_content)
        
        # Mock registry path
        executor = AutonomousPlanExecutor(registry_path=tmp_path)
        context = ContinuationContext(
            last_completed_phase=None,
            next_phase="phase-21",
            active_phases=[],
            registry_path=tmp_path,
            should_continue=True,
            continuation_reason="Test"
        )
        
        template = executor.generate_exec_template(context)
        
        assert "JSON-First Rewrite" in template
        assert "phase-21" in template
        assert "Implement JSON data model" in template
        assert "8h" in template
        assert "TDD-First" in template
    
    def test_generate_template_no_phase(self, sample_registry):
        """Should handle missing next phase."""
        executor = AutonomousPlanExecutor()
        context = ContinuationContext(
            last_completed_phase=None,
            next_phase=None,
            active_phases=[],
            registry_path=Path("."),
            should_continue=False,
            continuation_reason="Test"
        )
        
        template = executor.generate_exec_template(context)
        assert "No next phase available" in template
