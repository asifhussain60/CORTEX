"""
Unit tests for Refinement Orchestrator
Tests RED→GREEN→REFACTOR TDD cycle enforcement.

Author: GitHub Copilot (Asif Hussain)
Created: January 4, 2026
Part of: CORTEX-5.0 Sub-Plan C50-01
"""

import pytest
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from src.orchestrators.refinement_orchestrator import (
    RefinementOrchestrator,
    RefactoringSeverity,
    TDDViolation,
    refine_code
)
from src.orchestrators.base.base_orchestrator_v4_1 import (
    PhaseStatus,
    PhaseResult,
    OrchestratorStatus
)


class TestRefinementOrchestrator:
    """Test suite for RefinementOrchestrator class."""
    
    @pytest.fixture
    def mock_state_db(self):
        """Mock PlanningStateDB."""
        db = Mock()
        db.create_plan.return_value = "test-plan-id"
        db.update_phase_status.return_value = None
        db.get_plan_state.return_value = {"status": "active"}
        return db
    
    @pytest.fixture
    def mock_config(self):
        """Mock configuration."""
        return {
            "analysis_tools": {
                "complexity": "radon",
                "coverage": "coverage.py"
            },
            "validation": {
                "coverage_threshold": 80,
                "complexity_threshold": 10
            },
            "tdd_enforcement": True
        }
    
    @pytest.fixture
    def orchestrator(self, mock_state_db, mock_config):
        """Create RefinementOrchestrator with mocked dependencies."""
        with patch.object(RefinementOrchestrator, 'load_config', return_value=mock_config):
            orch = RefinementOrchestrator(state_db=mock_state_db)
            orch.config = mock_config
            return orch
    
    def test_initialization(self, orchestrator):
        """Test orchestrator initialization."""
        assert orchestrator.tdd_enforcement is True
        assert orchestrator.code_analysis == {}
        assert orchestrator.identified_issues == []
        assert orchestrator.impact_matrix == {}
    
    def test_execute_dry_run(self, orchestrator):
        """Test dry run execution (no changes)."""
        result = orchestrator.execute(
            user_request="refine test module",
            target_path=Path("tests/"),
            dry_run=True
        )
        
        assert result.success is True
        assert result.status == OrchestratorStatus.COMPLETED
        # Dry run should still execute all phases
        assert "code_analysis" in result.data
        assert "refactoring_plan" in result.data
        assert "validation_report" in result.data
        # Check that refactoring plan has tasks
        assert "tasks" in result.data["refactoring_plan"]
    
    @patch.object(RefinementOrchestrator, '_analyze_complexity')
    @patch.object(RefinementOrchestrator, '_detect_anti_patterns')
    @patch.object(RefinementOrchestrator, '_analyze_test_coverage')
    def test_phase_1_code_analysis(
        self,
        mock_coverage,
        mock_patterns,
        mock_complexity,
        orchestrator
    ):
        """Test Phase 1: Code Analysis."""
        # Setup mocks
        mock_complexity.return_value = {
            "authenticate": {"cyclomatic": 12, "file": "auth.py"}
        }
        mock_patterns.return_value = [
            {"name": "God Object", "severity": "high"}
        ]
        mock_coverage.return_value = {"percentage": 75.0}
        
        result = orchestrator._phase_1_code_analysis({
            "target_path": Path("src/auth")
        })
        
        assert result.status == PhaseStatus.COMPLETED
        assert len(result.errors) == 0
        assert orchestrator.code_analysis["health_score"] is not None
        assert "complexity" in orchestrator.code_analysis
        assert "coverage" in orchestrator.code_analysis
    
    def test_phase_2_issue_identification(self, orchestrator):
        """Test Phase 2: Issue Identification."""
        # Setup code analysis results
        orchestrator.code_analysis = {
            "complexity": {
                "complex_function": {"cyclomatic": 15, "file": "test.py"}
            },
            "anti_patterns": [
                {
                    "name": "Long Method",
                    "description": "Method too long",
                    "location": "test.py:10",
                    "effort": 2.0
                }
            ],
            "coverage": {"percentage": 65.0}
        }
        
        result = orchestrator._phase_2_issue_identification({
            "severity_threshold": RefactoringSeverity.MEDIUM,
            "target_path": Path("src/")
        })
        
        assert result.status == PhaseStatus.COMPLETED
        assert len(result.errors) == 0
        assert len(orchestrator.identified_issues) > 0
        # Should have: complexity issue, coverage issue, anti-pattern
        assert any(issue["id"].startswith("COMPLEX-") for issue in orchestrator.identified_issues)
        assert any(issue["id"].startswith("COV-") for issue in orchestrator.identified_issues)
    
    def test_issue_prioritization(self, orchestrator):
        """Test issues are prioritized by severity then effort."""
        orchestrator.code_analysis = {
            "complexity": {
                "func_a": {"cyclomatic": 15, "file": "a.py"},
                "func_b": {"cyclomatic": 12, "file": "b.py"}
            },
            "anti_patterns": [],
            "coverage": {"percentage": 85.0}
        }
        
        orchestrator._phase_2_issue_identification({
            "severity_threshold": RefactoringSeverity.LOW
        })
        
        # Critical/High severity should come first
        severities = [issue["severity"] for issue in orchestrator.identified_issues]
        assert severities == sorted(severities, key=lambda s: -orchestrator._severity_to_int(s))
    
    def test_phase_3_impact_assessment(self, orchestrator):
        """Test Phase 3: Impact Assessment."""
        orchestrator.identified_issues = [
            {
                "id": "TEST-1",
                "severity": RefactoringSeverity.HIGH,
                "effort_hours": 2.0,
                "category": "performance"
            },
            {
                "id": "TEST-2",
                "severity": RefactoringSeverity.MEDIUM,
                "effort_hours": 1.0,
                "category": "maintainability"
            }
        ]
        
        result = orchestrator._phase_3_impact_assessment({
            "target_path": Path("src/")
        })
        
        assert result.status == PhaseStatus.COMPLETED
        assert len(result.errors) == 0
        assert len(orchestrator.impact_matrix["matrix"]) == 2
        assert orchestrator.impact_matrix["total_effort_hours"] == 3.0
        # Higher priority should be first
        assert orchestrator.impact_matrix["matrix"][0]["priority"] >= orchestrator.impact_matrix["matrix"][1]["priority"]
    
    def test_phase_4_refactoring_plan(self, orchestrator):
        """Test Phase 4: Refactoring Plan."""
        orchestrator.identified_issues = [
            {
                "id": "TEST-1",
                "title": "Fix complexity",
                "description": "Reduce cyclomatic complexity",
                "category": "maintainability"
            }
        ]
        orchestrator.impact_matrix = {
            "matrix": [
                {
                    "issue_id": "TEST-1",
                    "risk_score": 5,
                    "effort_hours": 2.0,
                    "priority": 7.5,
                    "recommended_action": "Fix soon"
                }
            ]
        }
        
        result = orchestrator._phase_4_refactoring_plan({
            "target_path": Path("src/")
        })
        
        assert result.status == PhaseStatus.COMPLETED
        assert len(result.errors) == 0
        assert len(orchestrator.refactoring_plan["tasks"]) == 1
        assert orchestrator.refactoring_plan["tasks"][0]["task_id"] == "TASK-1"
        assert "success_criteria" in orchestrator.refactoring_plan
        assert orchestrator.refactoring_plan["success_criteria"]["test_coverage"] == "≥80%"
    
    @patch.object(RefinementOrchestrator, '_enforce_tdd_cycle')
    def test_phase_5_implementation_tdd(self, mock_tdd, orchestrator):
        """Test Phase 5: Implementation with TDD enforcement."""
        orchestrator.refactoring_plan = {
            "tasks": [
                {
                    "task_id": "TASK-1",
                    "title": "Fix issue",
                    "effort_hours": 1.0
                }
            ]
        }
        
        result = orchestrator._phase_5_implementation({
            "tdd_strict": True,
            "dry_run": False
        })
        
        assert result.status == PhaseStatus.COMPLETED
        assert len(result.errors) == 0
        assert mock_tdd.called
        assert orchestrator.implementation_result["tasks_completed"] == 1
        assert orchestrator.implementation_result["tdd_enforced"] is True
    
    @patch.object(RefinementOrchestrator, '_implement_task')
    def test_phase_5_implementation_no_tdd(self, mock_implement, orchestrator):
        """Test Phase 5: Implementation without TDD enforcement."""
        orchestrator.refactoring_plan = {
            "tasks": [
                {
                    "task_id": "TASK-1",
                    "title": "Fix issue",
                    "effort_hours": 1.0
                }
            ]
        }
        
        result = orchestrator._phase_5_implementation({
            "tdd_strict": False,
            "dry_run": False
        })
        
        assert result.status == PhaseStatus.COMPLETED
        assert len(result.errors) == 0
        assert mock_implement.called
        assert orchestrator.implementation_result["tdd_enforced"] is False
    
    @patch.object(RefinementOrchestrator, '_enforce_tdd_cycle')
    def test_phase_5_tdd_violation(self, mock_tdd, orchestrator):
        """Test TDD violation in strict mode fails fast."""
        mock_tdd.side_effect = TDDViolation("Tests didn't fail before implementation")
        
        orchestrator.refactoring_plan = {
            "tasks": [
                {
                    "task_id": "TASK-1",
                    "title": "Fix issue",
                    "effort_hours": 1.0
                }
            ]
        }
        
        with pytest.raises(TDDViolation):
            orchestrator._phase_5_implementation({
                "tdd_strict": True,
                "dry_run": False
            })
    
    @patch.object(RefinementOrchestrator, '_run_validation_suite')
    def test_phase_6_validation_success(self, mock_validate, orchestrator):
        """Test Phase 6: Validation (all criteria met)."""
        mock_validate.return_value = {
            "test_coverage": 85.0,
            "tests_passed": True,
            "complexity_delta": -25.0,
            "performance_regression": False
        }
        
        orchestrator.refactoring_plan = {
            "success_criteria": {
                "test_coverage": "≥80%",
                "all_tests_pass": True,
                "complexity_reduction": "≥20%",
                "no_regressions": True
            }
        }
        
        result = orchestrator._phase_6_validation({
            "target_path": Path("src/")
        })
        
        assert result.status == PhaseStatus.COMPLETED
        assert len(result.errors) == 0
        assert orchestrator.validation_report["all_criteria_met"] is True
        assert all(orchestrator.validation_report["checks"].values())
    
    @patch.object(RefinementOrchestrator, '_run_validation_suite')
    def test_phase_6_validation_failure(self, mock_validate, orchestrator):
        """Test Phase 6: Validation (criteria not met)."""
        mock_validate.return_value = {
            "test_coverage": 70.0,  # Below 80%
            "tests_passed": True,
            "complexity_delta": -10.0,  # Below -20%
            "performance_regression": False
        }
        
        orchestrator.refactoring_plan = {
            "success_criteria": {
                "test_coverage": "≥80%",
                "all_tests_pass": True,
                "complexity_reduction": "≥20%",
                "no_regressions": True
            }
        }
        
        result = orchestrator._phase_6_validation({
            "target_path": Path("src/")
        })
        
        assert result.status == PhaseStatus.FAILED
        assert orchestrator.validation_report["all_criteria_met"] is False
    
    @patch.object(RefinementOrchestrator, '_generate_completion_report')
    @patch.object(RefinementOrchestrator, '_update_documentation')
    def test_phase_7_documentation(self, mock_update_docs, mock_report, orchestrator):
        """Test Phase 7: Documentation."""
        mock_report.return_value = {
            "refinement_id": "test-id",
            "issues_fixed": 5
        }
        mock_update_docs.return_value = ["README.md", "CHANGELOG.md"]
        
        result = orchestrator._phase_7_documentation({
            "target_path": Path("src/")
        })
        
        assert result.status == PhaseStatus.COMPLETED
        assert len(result.errors) == 0
        assert len(result.artifacts) == 3  # completion_report.md + 2 updated docs
        assert mock_report.called
        assert mock_update_docs.called
    
    def test_severity_comparison(self, orchestrator):
        """Test severity comparison logic."""
        assert orchestrator._compare_severity(
            RefactoringSeverity.CRITICAL,
            RefactoringSeverity.HIGH
        ) > 0
        
        assert orchestrator._compare_severity(
            RefactoringSeverity.LOW,
            RefactoringSeverity.MEDIUM
        ) < 0
        
        assert orchestrator._compare_severity(
            RefactoringSeverity.HIGH,
            RefactoringSeverity.HIGH
        ) == 0
    
    def test_severity_to_int(self, orchestrator):
        """Test severity weight conversion."""
        assert orchestrator._severity_to_int(RefactoringSeverity.CRITICAL) == 4
        assert orchestrator._severity_to_int(RefactoringSeverity.HIGH) == 3
        assert orchestrator._severity_to_int(RefactoringSeverity.MEDIUM) == 2
        assert orchestrator._severity_to_int(RefactoringSeverity.LOW) == 1
    
    def test_risk_assessment(self, orchestrator):
        """Test risk scoring logic."""
        issue_critical = {
            "severity": RefactoringSeverity.CRITICAL,
            "category": "security"
        }
        
        issue_low = {
            "severity": RefactoringSeverity.LOW,
            "category": "style"
        }
        
        risk_critical = orchestrator._assess_risk(issue_critical, Path("src/"))
        risk_low = orchestrator._assess_risk(issue_low, Path("src/"))
        
        assert risk_critical > risk_low
        assert 1 <= risk_critical <= 10
        assert 1 <= risk_low <= 10
    
    def test_health_score_calculation(self, orchestrator):
        """Test code health score calculation."""
        score = orchestrator._calculate_health_score(
            complexity={"func1": {"cyclomatic": 15}},  # 1 complex function = -5
            anti_patterns=[{"name": "Pattern1"}],      # 1 pattern = -3
            coverage={"percentage": 90.0}              # Base 90
        )
        
        # 90 - 5 - 3 = 82
        assert score == 82
    
    def test_test_strategy_definition(self, orchestrator):
        """Test strategy varies by issue category."""
        security_issue = {"category": "security"}
        performance_issue = {"category": "performance"}
        testing_issue = {"category": "testing"}
        
        assert "Security" in orchestrator._define_test_strategy(security_issue)
        assert "Performance" in orchestrator._define_test_strategy(performance_issue)
        assert "coverage" in orchestrator._define_test_strategy(testing_issue)
    
    def test_action_recommendation(self, orchestrator):
        """Test action recommendation logic."""
        # High risk + high severity = immediate
        action1 = orchestrator._recommend_action(risk=9, severity=4, effort=2.0)
        assert "immediately" in action1.lower()
        
        # Low risk + low effort = quick win
        action2 = orchestrator._recommend_action(risk=2, severity=1, effort=0.5)
        assert "quick win" in action2.lower()
        
        # Medium risk/severity = schedule
        action3 = orchestrator._recommend_action(risk=6, severity=3, effort=3.0)
        assert "schedule" in action3.lower() or "sprint" in action3.lower()


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    @patch.object(RefinementOrchestrator, 'execute')
    def test_refine_code_function(self, mock_execute):
        """Test refine_code() convenience function."""
        mock_execute.return_value = Mock(success=True)
        
        result = refine_code(
            target_path="src/module.py",
            severity_threshold="high",
            tdd_strict=True,
            dry_run=False
        )
        
        assert mock_execute.called
        call_kwargs = mock_execute.call_args[1]
        assert call_kwargs["target_path"] == "src/module.py"
        assert call_kwargs["severity_threshold"] == "high"
        assert call_kwargs["tdd_strict"] is True
        assert call_kwargs["dry_run"] is False


class TestIntegration:
    """Integration tests (full workflow)."""
    
    @pytest.fixture
    def full_orchestrator(self, tmp_path):
        """Create orchestrator with real database."""
        from src.database.planning_state_db import PlanningStateDB
        
        db_path = tmp_path / "test_refinement.db"
        state_db = PlanningStateDB(str(db_path))
        
        with patch.object(RefinementOrchestrator, 'load_config', return_value={}):
            orch = RefinementOrchestrator(state_db=state_db)
            orch.config = {
                "analysis_tools": {},
                "validation": {},
                "tdd_enforcement": False  # Disable for integration test
            }
            return orch
    
    @patch.object(RefinementOrchestrator, '_analyze_complexity')
    @patch.object(RefinementOrchestrator, '_detect_anti_patterns')
    @patch.object(RefinementOrchestrator, '_analyze_test_coverage')
    @patch.object(RefinementOrchestrator, '_run_validation_suite')
    @patch.object(RefinementOrchestrator, '_generate_completion_report')
    @patch.object(RefinementOrchestrator, '_update_documentation')
    def test_full_workflow_dry_run(
        self,
        mock_docs,
        mock_report,
        mock_validate,
        mock_coverage,
        mock_patterns,
        mock_complexity,
        full_orchestrator
    ):
        """Test complete refinement workflow (dry run)."""
        # Setup mocks
        mock_complexity.return_value = {}
        mock_patterns.return_value = []
        mock_coverage.return_value = {"percentage": 85.0}
        mock_validate.return_value = {
            "test_coverage": 85.0,
            "tests_passed": True,
            "complexity_delta": -25.0,
            "performance_regression": False
        }
        mock_report.return_value = {"issues_fixed": 0}
        mock_docs.return_value = []
        
        result = full_orchestrator.execute(
            user_request="refine test module",
            target_path=Path("tests/"),
            dry_run=True
        )
        
        assert result.success is True
        assert result.status == OrchestratorStatus.COMPLETED
        # Dry run executes all phases
        assert "code_analysis" in result.data
        assert "refactoring_plan" in result.data
        assert "validation_report" in result.data
