"""
Tests for IntelligenceOrchestrator

Comprehensive integration tests for intelligence orchestration including
all adapters, workflows, and documentation generation.
"""

import pytest
import asyncio
from pathlib import Path
from src.orchestrators.planning.intelligence.intelligence_orchestrator import (
    IntelligenceOrchestrator,
    IntelligenceMode,
    IntelligenceReport
)


class TestIntelligenceOrchestratorInit:
    """Test IntelligenceOrchestrator initialization."""
    
    def test_init_full_mode(self):
        """Test initialization in FULL mode."""
        orchestrator = IntelligenceOrchestrator(
            project_root=Path.cwd(),
            mode=IntelligenceMode.FULL
        )
        
        assert orchestrator.mode == IntelligenceMode.FULL
        assert orchestrator.test_intelligence is not None
        assert orchestrator.tdd_intelligence is not None
        assert orchestrator.validation_framework is not None
        assert orchestrator.manifest_validator is not None
    
    def test_init_validation_only_mode(self):
        """Test initialization in VALIDATION_ONLY mode."""
        orchestrator = IntelligenceOrchestrator(
            project_root=Path.cwd(),
            mode=IntelligenceMode.VALIDATION_ONLY
        )
        
        assert orchestrator.mode == IntelligenceMode.VALIDATION_ONLY
        assert orchestrator.test_intelligence is None
        assert orchestrator.tdd_intelligence is None
        assert orchestrator.validation_framework is not None
        assert orchestrator.manifest_validator is not None
    
    def test_init_advisory_only_mode(self):
        """Test initialization in ADVISORY_ONLY mode."""
        orchestrator = IntelligenceOrchestrator(
            project_root=Path.cwd(),
            mode=IntelligenceMode.ADVISORY_ONLY
        )
        
        assert orchestrator.mode == IntelligenceMode.ADVISORY_ONLY
        assert orchestrator.test_intelligence is not None
        assert orchestrator.tdd_intelligence is not None
        assert orchestrator.validation_framework is None
        assert orchestrator.manifest_validator is None


class TestPlanAnalysis:
    """Test comprehensive plan analysis."""
    
    @pytest.mark.asyncio
    async def test_analyze_valid_plan(self):
        """Test analysis of valid plan."""
        orchestrator = IntelligenceOrchestrator(
            project_root=Path.cwd(),
            mode=IntelligenceMode.FULL
        )
        
        plan_data = {
            "metadata": {
                "plan_name": "Test Plan",
                "version": "1.0",
                "complexity": "low",
                "estimated_hours": 10,
                "created_at": "2025-12-24"
            },
            "definition_of_ready": {
                "requirements_clear": "Yes",
                "acceptance_criteria_defined": "Yes",
                "dependencies_identified": "Yes"
            },
            "definition_of_done": {
                "code_complete": "Yes",
                "tests_passing": "Yes",
                "documentation_updated": "Yes"
            },
            "phases": [
                {
                    "phase_number": 1,
                    "phase_name": "Phase 1",
                    "tasks": [
                        {
                            "task_id": "T1",
                            "task_name": "Task 1",
                            "estimated_hours": 10,
                            "acceptance_criteria": ["AC1"]
                        }
                    ],
                    "dor": "Complete",
                    "dod": "Complete"
                }
            ]
        }
        
        report = await orchestrator.analyze_plan(plan_data, "Test feature")
        
        assert isinstance(report, IntelligenceReport)
        assert report.mode == IntelligenceMode.FULL
        assert report.overall_score > 0
    
    @pytest.mark.asyncio
    async def test_analyze_plan_with_errors(self):
        """Test analysis of plan with validation errors."""
        orchestrator = IntelligenceOrchestrator(
            project_root=Path.cwd(),
            mode=IntelligenceMode.FULL
        )
        
        plan_data = {
            "metadata": {
                "plan_name": "Invalid Plan",
                "complexity": "invalid_complexity"
            },
            "phases": []
        }
        
        report = await orchestrator.analyze_plan(plan_data)
        
        assert len(report.blocking_issues) > 0
        assert not report.is_ready_for_execution()
    
    @pytest.mark.asyncio
    async def test_analyze_plan_missing_dor(self):
        """Test analysis of plan missing DoR."""
        orchestrator = IntelligenceOrchestrator(
            project_root=Path.cwd(),
            mode=IntelligenceMode.FULL
        )
        
        plan_data = {
            "metadata": {"plan_name": "Test"},
            "phases": []
        }
        
        report = await orchestrator.analyze_plan(plan_data)
        
        # Should have blocking issue for missing DoR
        assert any("definition_of_ready" in issue.lower() for issue in report.blocking_issues)


class TestValidationAPI:
    """Test validation API methods."""
    
    @pytest.mark.asyncio
    async def test_validate_plan_success(self):
        """Test plan validation success."""
        orchestrator = IntelligenceOrchestrator(
            project_root=Path.cwd(),
            mode=IntelligenceMode.VALIDATION_ONLY
        )
        
        plan_data = {
            "metadata": {
                "plan_name": "Valid Plan",
                "version": "1.0",
                "complexity": "low",
                "estimated_hours": 5,
                "created_at": "2025-12-24"
            },
            "definition_of_ready": {
                "requirements_clear": "Yes",
                "acceptance_criteria_defined": "Yes",
                "dependencies_identified": "Yes"
            },
            "definition_of_done": {
                "code_complete": "Yes",
                "tests_passing": "Yes",
                "documentation_updated": "Yes"
            },
            "phases": [
                {
                    "phase_number": 1,
                    "phase_name": "Phase 1",
                    "tasks": [
                        {
                            "task_id": "T1",
                            "task_name": "Task 1",
                            "estimated_hours": 5,
                            "acceptance_criteria": ["AC1"]
                        }
                    ],
                    "dor": "Complete",
                    "dod": "Complete"
                }
            ]
        }
        
        is_valid, errors = await orchestrator.validate_plan(plan_data)
        
        assert is_valid is True
        assert len(errors) == 0
    
    @pytest.mark.asyncio
    async def test_validate_plan_failure(self):
        """Test plan validation failure."""
        orchestrator = IntelligenceOrchestrator(
            project_root=Path.cwd(),
            mode=IntelligenceMode.VALIDATION_ONLY
        )
        
        plan_data = {
            "phases": []  # Missing metadata and DoR/DoD
        }
        
        is_valid, errors = await orchestrator.validate_plan(plan_data)
        
        assert is_valid is False
        assert len(errors) > 0


class TestTDDRequirements:
    """Test TDD requirement enforcement."""
    
    @pytest.mark.asyncio
    async def test_tdd_required_for_medium_complexity(self):
        """Test TDD requirement for medium complexity."""
        orchestrator = IntelligenceOrchestrator(
            project_root=Path.cwd(),
            mode=IntelligenceMode.FULL
        )
        
        plan_data = {
            "metadata": {
                "plan_name": "Medium Complexity Plan",
                "complexity": "medium"
            },
            "definition_of_ready": {"requirements_clear": "Yes"},
            "definition_of_done": {"code_complete": "Yes"},
            "phases": []
        }
        
        report = await orchestrator.analyze_plan(plan_data)
        
        # Should have blocking issue for missing TDD workflow
        assert any("TDD workflow" in issue for issue in report.blocking_issues)
    
    @pytest.mark.asyncio
    async def test_tdd_not_required_for_low_complexity(self):
        """Test TDD not required for low complexity."""
        orchestrator = IntelligenceOrchestrator(
            project_root=Path.cwd(),
            mode=IntelligenceMode.FULL
        )
        
        plan_data = {
            "metadata": {
                "plan_name": "Low Complexity Plan",
                "version": "1.0",
                "complexity": "low",
                "estimated_hours": 5,
                "created_at": "2025-12-24"
            },
            "definition_of_ready": {
                "requirements_clear": "Yes",
                "acceptance_criteria_defined": "Yes",
                "dependencies_identified": "Yes"
            },
            "definition_of_done": {
                "code_complete": "Yes",
                "tests_passing": "Yes",
                "documentation_updated": "Yes"
            },
            "phases": [
                {
                    "phase_number": 1,
                    "phase_name": "Phase 1",
                    "tasks": [
                        {
                            "task_id": "T1",
                            "task_name": "Task 1",
                            "estimated_hours": 5,
                            "acceptance_criteria": ["AC1"]
                        }
                    ],
                    "dor": "Complete",
                    "dod": "Complete"
                }
            ]
        }
        
        report = await orchestrator.analyze_plan(plan_data)
        
        # Should NOT have TDD blocking issue for low complexity
        tdd_issues = [issue for issue in report.blocking_issues if "TDD workflow" in issue]
        assert len(tdd_issues) == 0


class TestIntelligenceMode:
    """Test intelligence mode switching."""
    
    def test_set_mode(self):
        """Test changing intelligence mode."""
        orchestrator = IntelligenceOrchestrator(
            project_root=Path.cwd(),
            mode=IntelligenceMode.FULL
        )
        
        # Verify FULL mode
        assert orchestrator.test_intelligence is not None
        assert orchestrator.validation_framework is not None
        
        # Switch to VALIDATION_ONLY
        orchestrator.set_mode(IntelligenceMode.VALIDATION_ONLY)
        
        assert orchestrator.mode == IntelligenceMode.VALIDATION_ONLY
        assert orchestrator.test_intelligence is None
        assert orchestrator.validation_framework is not None
    
    def test_enable_disable_adapter(self):
        """Test enabling/disabling individual adapters."""
        orchestrator = IntelligenceOrchestrator(
            project_root=Path.cwd(),
            mode=IntelligenceMode.MINIMAL
        )
        
        # Minimal mode: validation only
        assert orchestrator.test_intelligence is None
        
        # Enable test intelligence
        orchestrator.enable_adapter("test")
        assert orchestrator.test_intelligence is not None
        
        # Disable validation
        orchestrator.disable_adapter("validation")
        assert orchestrator.validation_framework is None


class TestIntelligenceReport:
    """Test IntelligenceReport functionality."""
    
    def test_report_ready_for_execution(self):
        """Test execution readiness check."""
        report = IntelligenceReport()
        report.execution_approved = True
        report.blocking_issues = []
        
        assert report.is_ready_for_execution() is True
    
    def test_report_not_ready_with_blocking_issues(self):
        """Test execution blocked by issues."""
        report = IntelligenceReport()
        report.execution_approved = True
        report.blocking_issues = ["Critical error"]
        
        assert report.is_ready_for_execution() is False
    
    def test_report_summary(self):
        """Test report summary generation."""
        report = IntelligenceReport()
        report.overall_score = 85.0
        report.execution_approved = True
        report.warnings = ["Warning 1", "Warning 2"]
        
        summary = report.get_summary()
        assert "✅" in summary
        assert "85" in summary
        assert "2 warnings" in summary


class TestAdvisoryAPI:
    """Test advisory API methods."""
    
    @pytest.mark.asyncio
    async def test_get_test_strategy(self):
        """Test getting test strategy."""
        orchestrator = IntelligenceOrchestrator(
            project_root=Path.cwd(),
            mode=IntelligenceMode.ADVISORY_ONLY
        )
        
        strategy = await orchestrator.get_test_strategy("Authentication feature")
        
        # Verify strategy structure
        assert isinstance(strategy, dict)
        assert "target_coverage" in strategy or "reasoning" in strategy
    
    @pytest.mark.asyncio
    async def test_get_tdd_recommendations(self):
        """Test getting TDD recommendations."""
        orchestrator = IntelligenceOrchestrator(
            project_root=Path.cwd(),
            mode=IntelligenceMode.ADVISORY_ONLY
        )
        
        recommendations = await orchestrator.get_tdd_recommendations(
            feature_scope={"feature_type": "api", "description": "API feature"},
            complexity="medium"
        )
        
        assert "recommendations" in recommendations
    
    def test_get_coverage_gaps(self):
        """Test getting coverage gaps."""
        orchestrator = IntelligenceOrchestrator(
            project_root=Path.cwd(),
            mode=IntelligenceMode.FULL
        )
        
        gaps = orchestrator.get_coverage_gaps()
        
        assert isinstance(gaps, list)


class TestErrorHandling:
    """Test error handling in intelligence orchestrator."""
    
    @pytest.mark.asyncio
    async def test_analyze_with_invalid_data(self):
        """Test analysis with completely invalid data."""
        orchestrator = IntelligenceOrchestrator(
            project_root=Path.cwd(),
            mode=IntelligenceMode.FULL
        )
        
        plan_data = {}  # Empty plan
        
        report = await orchestrator.analyze_plan(plan_data)
        
        # Should still return report (with many errors)
        assert isinstance(report, IntelligenceReport)
        assert len(report.blocking_issues) > 0
    
    @pytest.mark.asyncio
    async def test_disabled_adapter_graceful_handling(self):
        """Test graceful handling when adapter is disabled."""
        orchestrator = IntelligenceOrchestrator(
            project_root=Path.cwd(),
            mode=IntelligenceMode.MINIMAL
        )
        
        # Test intelligence disabled in MINIMAL mode
        strategy = await orchestrator.get_test_strategy("Feature")
        
        assert "error" in strategy
        assert "not enabled" in strategy["error"]
