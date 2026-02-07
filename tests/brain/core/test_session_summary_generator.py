"""
Tests for Session Summary Generator.

Governance:
- CORE-008: TDD mandatory
- CORE-011: Type hints on all functions
- CORE-012: Google-style docstrings
- ENH-048: Response format standards compliance

Author: Asif Hussain
Date: 2026-02-07
"""

import pytest
from cortex.brain.core.session_summary_generator import (
    format_session_summary,
    generate_continuation_checkpoint,
    get_token_status,
    SessionMetrics,
    StageResult,
)


class TestTokenStatus:
    """Test token status indicator generation."""
    
    def test_excellent_low(self):
        """Test excellent status at <15% usage."""
        status = get_token_status(10.0)
        assert "Excellent!" in status
        assert "Massive runway" in status
    
    def test_excellent_medium(self):
        """Test excellent status at 15-30% usage."""
        status = get_token_status(20.0)
        assert "Excellent!" in status
        assert "Healthy runway" in status
    
    def test_good_low(self):
        """Test good status at 30-50% usage."""
        status = get_token_status(40.0)
        assert "Good" in status
        assert "Ample" in status
    
    def test_good_medium(self):
        """Test good status at 50-70% usage."""
        status = get_token_status(60.0)
        assert "Good" in status
        assert "Sufficient" in status
    
    def test_moderate(self):
        """Test moderate status at 70-85% usage."""
        status = get_token_status(75.0)
        assert "Moderate" in status
        assert "checkpoint" in status
    
    def test_high_warning(self):
        """Test high warning at 85-95% usage."""
        status = get_token_status(90.0)
        assert "⚠️ High" in status
        assert "continuation" in status
    
    def test_critical(self):
        """Test critical status at >95% usage."""
        status = get_token_status(96.0)
        assert "🔴 Critical" in status
        assert "NOW" in status


class TestSessionSummaryFormatting:
    """Test session summary generation."""
    
    def test_basic_summary(self):
        """Test basic session summary with completed stages."""
        stages = [
            StageResult(
                stage_number=1,
                stage_name="Brain Health Monitor",
                files_created=["cortex/orchestrators/support/brain_health_orchestrator.py"],
                tests_passing="16/16",
                duration_minutes=25
            ),
            StageResult(
                stage_number=2,
                stage_name="Capability Mesh",
                files_created=["cortex/orchestrators/registry/capability_mesh.py"],
                tests_passing="17/17",
                duration_minutes=30
            ),
        ]
        
        metrics = SessionMetrics(
            token_used_k=84,
            token_total_k=1000,
            implementation_time_minutes=55,
            total_tests_passing="33/33"
        )
        
        summary = format_session_summary(
            session_title="Phase 38 Stages 1-2",
            completed_stages=stages,
            remaining_stages=[],
            metrics=metrics
        )
        
        # Verify structure
        assert "## 🎯 Session Summary: Phase 38 Stages 1-2" in summary
        assert "### ✅ Status Overview" in summary
        assert "### 📦 Completed Stages & Deliverables" in summary
        assert "### 📊 Final Metrics" in summary
        
        # Verify token budget is FIRST in metrics (right after the header)
        metrics_section = summary.split("### 📊 Final Metrics")[1]
        lines = [line.strip() for line in metrics_section.split("\n") if line.strip()]
        
        # First non-empty line must be Token Budget
        assert lines[0].startswith("**Token Budget:**"), \
            f"Token budget not first! Found: {lines[0]}"
        
        # Verify token percentage and status
        assert "84k/1000k" in summary
        assert "(8%)" in summary
        assert "Excellent!" in summary
        
        # Verify stages appear
        assert "Brain Health Monitor" in summary
        assert "Capability Mesh" in summary
        assert "16/16" in summary
        assert "17/17" in summary
    
    def test_summary_with_remaining_stages(self):
        """Test summary including remaining stages."""
        stages = [
            StageResult(1, "Stage 1", ["file1.py"], "10/10", 20)
        ]
        
        remaining = [
            {"number": 2, "name": "Stage 2", "tests": "15", "estimate": "2 days", "priority": "P0"},
            {"number": 3, "name": "Stage 3", "tests": "20", "estimate": "3 days", "priority": "P1"},
        ]
        
        metrics = SessionMetrics(50, 1000, 20, "10/10")
        
        summary = format_session_summary(
            session_title="Test Session",
            completed_stages=stages,
            remaining_stages=remaining,
            metrics=metrics
        )
        
        assert "### 🔮 Remaining Stages" in summary
        assert "Stage 2" in summary
        assert "Stage 3" in summary
    
    def test_summary_with_governance_notes(self):
        """Test summary with governance notes."""
        stages = [
            StageResult(1, "Stage 1", ["file1.py"], "10/10", 20)
        ]
        
        metrics = SessionMetrics(30, 1000, 20, "10/10")
        governance_notes = [
            "All CORE rules applied",
            "Audit trail complete (AC_START → AC_COMPLETE)",
            "Type hints: 100%, Docstrings: 100%"
        ]
        
        summary = format_session_summary(
            session_title="Test Session",
            completed_stages=stages,
            remaining_stages=[],
            metrics=metrics,
            governance_notes=governance_notes
        )
        
        assert "### 📋 Governance Notes" in summary
        assert "All CORE rules applied" in summary
        assert "Audit trail complete" in summary


class TestContinuationCheckpoint:
    """Test continuation checkpoint generation."""
    
    def test_high_usage_checkpoint(self):
        """Test checkpoint at high (85-95%) usage."""
        checkpoint = generate_continuation_checkpoint(
            session_id="Phase 38 Stage 4",
            last_completed="capability_mesh.py",
            next_action="Implement company domain pipeline",
            token_percentage=90.0,
            branch="CORTEX"
        )
        
        assert "### 🔄 Continuation Checkpoint Required" in checkpoint
        assert "**Token Budget:** 90% used - ⚠️ High" in checkpoint
        assert "**#file:cortex-architect.prompt.md**" in checkpoint
        assert "**Session:** Phase 38 Stage 4" in checkpoint
        assert "**Branch:** CORTEX" in checkpoint
        assert "**Checkpoint:** capability_mesh.py ✅" in checkpoint
        assert "**Next:** Implement company domain pipeline" in checkpoint
    
    def test_critical_usage_checkpoint(self):
        """Test checkpoint at critical (>95%) usage."""
        checkpoint = generate_continuation_checkpoint(
            session_id="Phase 38 Stage 5",
            last_completed="domain_pipeline.py",
            next_action="Continue with rollout monitoring",
            token_percentage=96.0,
            branch="CORTEX"
        )
        
        assert "96% used - 🔴 Critical" in checkpoint
        assert "Copy this prompt to new Copilot Chat session" in checkpoint


class TestTokenBudgetPlacement:
    """Test critical requirement: Token budget must be FIRST in metrics."""
    
    def test_token_budget_appears_first(self):
        """Verify token budget is the FIRST item in Final Metrics section."""
        stages = [
            StageResult(1, "Test Stage", ["file.py"], "10/10", 15)
        ]
        
        metrics = SessionMetrics(85, 1000, 15, "10/10")
        
        summary = format_session_summary(
            session_title="Test",
            completed_stages=stages,
            remaining_stages=[],
            metrics=metrics
        )
        
        # Split at Final Metrics section
        parts = summary.split("### 📊 Final Metrics")
        assert len(parts) == 2, "Final Metrics section not found"
        
        metrics_section = parts[1]
        lines = [line.strip() for line in metrics_section.split("\n") if line.strip()]
        
        # First non-empty line after header must be Token Budget
        first_content_line = lines[0]
        assert first_content_line.startswith("**Token Budget:**"), \
            f"Token budget not first! Found: {first_content_line}"
        
        # Verify it comes before Implementation Time
        assert "**Implementation Time:**" in metrics_section
        token_budget_pos = metrics_section.index("**Token Budget:**")
        impl_time_pos = metrics_section.index("**Implementation Time:**")
        assert token_budget_pos < impl_time_pos, \
            "Token Budget must appear before Implementation Time"
    
    def test_token_budget_visibility_at_85_percent(self):
        """Test high-visibility warning at 85%+ usage."""
        stages = [
            StageResult(1, "Test", ["file.py"], "10/10", 20)
        ]
        
        metrics = SessionMetrics(850, 1000, 20, "10/10")
        
        summary = format_session_summary(
            session_title="Test",
            completed_stages=stages,
            remaining_stages=[],
            metrics=metrics
        )
        
        # Should have warning in token budget line
        assert "⚠️" in summary or "High" in summary
        
        # Footer should recommend checkpoint
        assert "Consider continuation checkpoint" in summary
