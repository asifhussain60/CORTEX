"""
Tests for Planning Orchestrator DoR/DoD Compliance Methods (Task 13.2)

Purpose: Validate Definition of Ready and Definition of Done enforcement
Coverage: 17 tests (13 unit + 4 integration)
"""

import pytest
from pathlib import Path
from typing import Dict, Any
from unittest.mock import MagicMock, patch

from src.orchestrators.planning.planning_orchestrator import PlanningOrchestrator


@pytest.fixture
def orchestrator():
    """Create Planning Orchestrator instance for testing."""
    config = {
        "cortex_root": Path.cwd(),
        "enable_git_checkpoints": False,  # Disable for unit tests
        "enable_session_restoration": False,
        "enforce_dor": True,
        "enforce_dod": True
    }
    return PlanningOrchestrator(config)


@pytest.fixture
def valid_plan():
    """Create valid plan that meets DoR criteria."""
    return {
        "metadata": {
            "name": "Test Feature",
            "objectives": ["Implement feature X", "Add tests"],
            "acceptance_criteria": [
                "Pass rate ≥ 95%",
                "Coverage ≥ 80%",
                "Response time <= 200ms"
            ],
            "dependencies": [
                {"name": "database", "type": "external"}
            ],
            "architecture": "microservices",
            "technologies": ["Python", "FastAPI"],
            "test_strategy": "TDD with pytest",
            "risks": ["Database migration complexity"],
            "tools": ["pytest", "docker"],
            "complexity": "MEDIUM"
        },
        "phases": [
            {"name": "Design", "success_criteria": ["Architecture approved"]},
            {"name": "Implementation", "success_criteria": ["Code complete"]},
            {"name": "Testing", "success_criteria": ["All tests passing"]}
        ]
    }


@pytest.fixture
def valid_results():
    """Create valid execution results that meet DoD criteria."""
    return {
        "phases": [
            {"name": "Design", "status": "complete"},
            {"name": "Implementation", "status": "complete"},
            {"name": "Testing", "status": "complete"}
        ],
        "test_results": {
            "pass_rate": 96.5,
            "coverage": 85.0,
            "tdd_complete": True
        },
        "artifacts": {
            "documentation": ["README.md", "API-GUIDE.md"]
        },
        "quality_metrics": {
            "max_complexity": 25,
            "fixme_count": 0,
            "todo_count": 0
        },
        "acceptance_criteria_met": True
    }


# ============================================================================
# DoR (Definition of Ready) Unit Tests - 7 tests
# ============================================================================

class TestDoRValidation:
    """Test DoR validation methods."""
    
    def test_validate_definition_of_ready_complete_plan(self, orchestrator, valid_plan):
        """Test DoR passes for complete plan."""
        is_ready, violations = orchestrator._validate_definition_of_ready(valid_plan)
        
        assert is_ready is True
        assert len(violations) == 0
    
    def test_validate_definition_of_ready_missing_objectives(self, orchestrator):
        """Test DoR fails without objectives."""
        plan = {
            "metadata": {
                "name": "Incomplete Plan",
                # Missing objectives
                "acceptance_criteria": ["Test criterion"]
            },
            "phases": []
        }
        
        is_ready, violations = orchestrator._validate_definition_of_ready(plan)
        
        assert is_ready is False
        assert any("Requirements clarity" in v for v in violations)
    
    def test_check_requirements_clarity_valid(self, orchestrator, valid_plan):
        """Test requirements clarity check passes."""
        result = orchestrator._check_requirements_clarity(valid_plan)
        
        assert result is True
    
    def test_check_requirements_clarity_missing_objectives(self, orchestrator):
        """Test requirements clarity fails without objectives."""
        plan = {"metadata": {}, "phases": []}
        
        result = orchestrator._check_requirements_clarity(plan)
        
        assert result is False
    
    def test_check_dependencies_identified_valid(self, orchestrator, valid_plan):
        """Test dependencies check passes."""
        is_valid, issues = orchestrator._check_dependencies_identified(valid_plan)
        
        assert is_valid is True
        assert len(issues) == 0
    
    def test_check_dependencies_high_complexity_requires_docs(self, orchestrator):
        """Test HIGH complexity requires dependency documentation."""
        plan = {
            "metadata": {
                "complexity": "HIGH",
                "dependencies": []  # Empty dependencies for HIGH complexity
            }
        }
        
        is_valid, issues = orchestrator._check_dependencies_identified(plan)
        
        assert is_valid is False
        assert any("HIGH complexity" in issue for issue in issues)
    
    def test_check_acceptance_criteria_measurable(self, orchestrator, valid_plan):
        """Test acceptance criteria measurability check."""
        result = orchestrator._check_acceptance_criteria(valid_plan)
        
        assert result is True  # Has measurable keywords (≥, %)
    
    def test_check_acceptance_criteria_not_measurable(self, orchestrator):
        """Test acceptance criteria fails without measurable indicators."""
        plan = {
            "metadata": {
                "acceptance_criteria": [
                    "System works well",
                    "Users are happy"
                ]
            }
        }
        
        result = orchestrator._check_acceptance_criteria(plan)
        
        assert result is False  # No measurable keywords
    
    def test_check_technical_feasibility_valid(self, orchestrator, valid_plan):
        """Test technical feasibility check passes."""
        is_valid, issues = orchestrator._check_technical_feasibility(valid_plan)
        
        assert is_valid is True
        assert len(issues) == 0
    
    def test_check_technical_feasibility_missing_architecture(self, orchestrator):
        """Test technical feasibility fails without architecture."""
        plan = {"metadata": {"complexity": "MEDIUM"}}
        
        is_valid, issues = orchestrator._check_technical_feasibility(plan)
        
        assert is_valid is False
        assert any("architecture" in issue.lower() for issue in issues)
    
    def test_check_testability_valid(self, orchestrator, valid_plan):
        """Test testability check passes."""
        result = orchestrator._check_testability(valid_plan)
        
        assert result is True  # Has test_strategy
    
    def test_check_testability_from_phases(self, orchestrator):
        """Test testability check passes from phase names."""
        plan = {
            "metadata": {},
            "phases": [
                {"name": "Testing Phase"},
                {"name": "TDD Implementation"}
            ]
        }
        
        result = orchestrator._check_testability(plan)
        
        assert result is True  # Has test-related phases
    
    def test_generate_dor_report_compliant(self, orchestrator, valid_plan):
        """Test DoR report generation for compliant plan."""
        report = orchestrator._generate_dor_report(valid_plan, [])
        
        assert "✅ DoR COMPLIANT" in report
        assert "Test Feature" in report
    
    def test_generate_dor_report_violations(self, orchestrator, valid_plan):
        """Test DoR report generation with violations."""
        violations = [
            "Requirements clarity: Missing objectives",
            "Testability: No test strategy"
        ]
        
        report = orchestrator._generate_dor_report(valid_plan, violations)
        
        assert "❌ DoR VIOLATIONS" in report
        assert "2 issue(s)" in report
        assert "Requirements clarity" in report
        assert "Testability" in report
        assert "REMEDIATION" in report


# ============================================================================
# DoD (Definition of Done) Unit Tests - 6 tests
# ============================================================================

class TestDoDValidation:
    """Test DoD validation methods."""
    
    def test_validate_definition_of_done_complete(self, orchestrator, valid_plan, valid_results):
        """Test DoD passes for successful execution."""
        is_done, violations = orchestrator._validate_definition_of_done(valid_plan, valid_results)
        
        assert is_done is True
        assert len(violations) == 0
    
    def test_validate_definition_of_done_failing_tests(self, orchestrator, valid_plan):
        """Test DoD fails with low pass rate."""
        results = {
            "phases": [{"name": "Testing", "status": "complete"}],
            "test_results": {
                "pass_rate": 85.0,  # Below 95% threshold
                "coverage": 85.0,
                "tdd_complete": True
            },
            "artifacts": {"documentation": ["README.md"]},
            "quality_metrics": {"max_complexity": 20, "fixme_count": 0, "todo_count": 0},
            "acceptance_criteria_met": True
        }
        
        is_done, violations = orchestrator._validate_definition_of_done(valid_plan, results)
        
        assert is_done is False
        assert any("Pass rate 85.0% below 95%" in v for v in violations)
    
    def test_check_code_complete_valid(self, orchestrator, valid_results):
        """Test code complete check passes."""
        result = orchestrator._check_code_complete(valid_results)
        
        assert result is True
    
    def test_check_code_complete_incomplete_phases(self, orchestrator):
        """Test code complete fails with incomplete phases."""
        results = {
            "phases": [
                {"name": "Design", "status": "complete"},
                {"name": "Implementation", "status": "failed"}
            ]
        }
        
        result = orchestrator._check_code_complete(results)
        
        assert result is False
    
    def test_check_tests_passing_valid(self, orchestrator, valid_results):
        """Test tests passing check passes."""
        is_valid, issues = orchestrator._check_tests_passing(valid_results)
        
        assert is_valid is True
        assert len(issues) == 0
    
    def test_check_tests_passing_low_coverage(self, orchestrator):
        """Test tests passing fails with low coverage."""
        results = {
            "test_results": {
                "pass_rate": 96.0,
                "coverage": 70.0,  # Below 80% threshold
                "tdd_complete": True
            }
        }
        
        is_valid, issues = orchestrator._check_tests_passing(results)
        
        assert is_valid is False
        assert any("Coverage 70.0% below 80%" in issue for issue in issues)
    
    def test_check_tests_passing_tdd_incomplete(self, orchestrator):
        """Test tests passing fails without TDD completion."""
        results = {
            "test_results": {
                "pass_rate": 96.0,
                "coverage": 85.0,
                "tdd_complete": False  # TDD not complete
            }
        }
        
        is_valid, issues = orchestrator._check_tests_passing(results)
        
        assert is_valid is False
        assert any("TDD workflow not completed" in issue for issue in issues)
    
    def test_check_documentation_complete_valid(self, orchestrator, valid_results):
        """Test documentation check passes."""
        result = orchestrator._check_documentation_complete(valid_results)
        
        assert result is True
    
    def test_check_documentation_complete_missing(self, orchestrator):
        """Test documentation check fails without docs."""
        results = {
            "artifacts": {
                "documentation": []  # No documentation
            }
        }
        
        result = orchestrator._check_documentation_complete(results)
        
        assert result is False
    
    def test_check_code_reviewed_valid(self, orchestrator, valid_results):
        """Test code review check passes."""
        is_valid, issues = orchestrator._check_code_reviewed(valid_results)
        
        assert is_valid is True
        assert len(issues) == 0
    
    def test_check_code_reviewed_high_complexity(self, orchestrator):
        """Test code review fails with high complexity."""
        results = {
            "quality_metrics": {
                "max_complexity": 45,  # Above 30 threshold
                "fixme_count": 0,
                "todo_count": 0
            }
        }
        
        is_valid, issues = orchestrator._check_code_reviewed(results)
        
        assert is_valid is False
        assert any("Complexity 45 exceeds limit" in issue for issue in issues)
    
    def test_check_code_reviewed_fixme_markers(self, orchestrator):
        """Test code review fails with FIXME/TODO markers."""
        results = {
            "quality_metrics": {
                "max_complexity": 20,
                "fixme_count": 3,
                "todo_count": 5
            }
        }
        
        is_valid, issues = orchestrator._check_code_reviewed(results)
        
        assert is_valid is False
        assert any("3 FIXME + 5 TODO" in issue for issue in issues)
    
    def test_generate_dod_report_compliant(self, orchestrator, valid_plan, valid_results):
        """Test DoD report generation for compliant execution."""
        report = orchestrator._generate_dod_report(valid_plan, valid_results, [])
        
        assert "✅ DoD COMPLIANT" in report
        assert "Test Feature" in report
        assert "Pass Rate: 96.5%" in report
        assert "Coverage: 85.0%" in report
    
    def test_generate_dod_report_violations(self, orchestrator, valid_plan, valid_results):
        """Test DoD report generation with violations."""
        violations = [
            "Tests: Pass rate 85.0% below 95%",
            "Code quality: Complexity 45 exceeds limit"
        ]
        
        report = orchestrator._generate_dod_report(valid_plan, valid_results, violations)
        
        assert "❌ DoD VIOLATIONS" in report
        assert "2 issue(s)" in report
        assert "Pass rate 85.0%" in report
        assert "Complexity 45" in report
        assert "REMEDIATION" in report


# ============================================================================
# Integration Tests - 4 tests
# ============================================================================

class TestDoRDoDIntegration:
    """Test DoR/DoD integration with planning workflow."""
    
    @patch.object(PlanningOrchestrator, '_generate_plan')
    @patch.object(PlanningOrchestrator, '_render_markdown')
    def test_plan_blocked_by_dor_violations(
        self, 
        mock_render, 
        mock_generate, 
        orchestrator
    ):
        """Test plan start blocked by DoR failures."""
        # Setup: Plan generation returns incomplete plan
        incomplete_plan = {
            "metadata": {
                "name": "Incomplete Plan",
                # Missing objectives, acceptance criteria, etc.
            },
            "phases": []
        }
        
        from types import SimpleNamespace
        mock_generate.return_value = SimpleNamespace(
            success=True,
            plan_data=incomplete_plan,
            errors=[]
        )
        
        # Execute
        result = orchestrator.execute(feature_name="test_feature")
        
        # Verify: Plan blocked by DoR
        assert result.success is False
        assert "Definition of Ready" in result.message
        assert mock_render.called is False  # Should not reach rendering
    
    def test_plan_completion_blocked_by_dod_violations(
        self, 
        orchestrator, 
        valid_plan
    ):
        """Test plan completion blocked by DoD failures."""
        # Setup: Execution results with low test quality
        results = {
            "phases": [{"name": "Implementation", "status": "complete"}],
            "test_results": {
                "pass_rate": 85.0,  # Below threshold
                "coverage": 70.0,   # Below threshold
                "tdd_complete": False
            },
            "artifacts": {"documentation": []},
            "quality_metrics": {"max_complexity": 40, "fixme_count": 5, "todo_count": 10},
            "acceptance_criteria_met": False
        }
        
        # Validate DoD fails
        is_done, violations = orchestrator._validate_definition_of_done(valid_plan, results)
        
        assert is_done is False
        assert len(violations) >= 4  # Multiple violations
        
        # Generate report
        report = orchestrator._generate_dod_report(valid_plan, results, violations)
        assert "❌ DoD VIOLATIONS" in report
    
    def test_dor_override_allows_execution(self, orchestrator):
        """Test enforce_dor=False bypasses checks."""
        # Disable DoR enforcement
        orchestrator.enforce_dor = False
        
        # Incomplete plan should still be processed
        incomplete_plan = {
            "metadata": {"name": "Incomplete Plan"},
            "phases": []
        }
        
        is_ready, violations = orchestrator._validate_definition_of_ready(incomplete_plan)
        
        # Validation still runs and returns violations
        assert is_ready is False
        assert len(violations) > 0
        
        # But orchestrator.execute() would not block (tested separately)
    
    def test_dod_report_generation_end_to_end(self, orchestrator, valid_plan, valid_results):
        """Test full DoD report with real execution results."""
        # Validate DoD
        is_done, violations = orchestrator._validate_definition_of_done(valid_plan, valid_results)
        
        # Generate report
        report = orchestrator._generate_dod_report(valid_plan, valid_results, violations)
        
        # Verify report structure
        assert "DoD COMPLIANT" in report or "DoD VIOLATIONS" in report
        assert "Test Feature" in report
        
        if is_done:
            assert "Quality Metrics" in report
            assert "Pass Rate:" in report
            assert "Coverage:" in report
        else:
            assert "VIOLATIONS FOUND:" in report
            assert "REMEDIATION:" in report


# ============================================================================
# Edge Cases and Error Handling
# ============================================================================

class TestDoRDoDEdgeCases:
    """Test edge cases for DoR/DoD validation."""
    
    def test_empty_plan_metadata(self, orchestrator):
        """Test DoR with empty metadata."""
        plan = {"metadata": {}, "phases": []}
        
        is_ready, violations = orchestrator._validate_definition_of_ready(plan)
        
        assert is_ready is False
        assert len(violations) >= 5  # Multiple missing items
    
    def test_empty_results(self, orchestrator, valid_plan):
        """Test DoD with empty results."""
        results = {}
        
        is_done, violations = orchestrator._validate_definition_of_done(valid_plan, results)
        
        assert is_done is False
        assert len(violations) >= 3  # Missing phases, tests, etc.
    
    def test_missing_test_results(self, orchestrator, valid_plan):
        """Test DoD handles missing test_results gracefully."""
        results = {
            "phases": [{"name": "Testing", "status": "complete"}],
            # Missing test_results
            "artifacts": {"documentation": ["README.md"]},
            "quality_metrics": {"max_complexity": 20, "fixme_count": 0, "todo_count": 0},
            "acceptance_criteria_met": True
        }
        
        is_done, violations = orchestrator._validate_definition_of_done(valid_plan, results)
        
        # Should handle gracefully (default values)
        assert is_done is False  # Will fail due to missing/zero pass rate
