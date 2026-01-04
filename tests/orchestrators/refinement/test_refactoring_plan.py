"""
Tests for Phase 5: Refactoring Plan.

Author: Asif Hussain
Created: January 3, 2026
"""

import pytest
from src.orchestrators.refinement.phases.refactoring_plan import RefactoringPlanPhase


class MockOrchestrator:
    """Mock orchestrator for testing."""
    def __init__(self):
        self.state = {
            "results": {
                "QualityAssessment": {
                    "issues": [
                        {"file": "test.py", "severity": "error", "message": "Syntax error"},
                        {"file": "test.py", "severity": "warning", "message": "Unused import"}
                    ]
                },
                "DuplicateDetection": {
                    "consolidation_suggestions": [
                        {
                            "duplicate_count": 3,
                            "block_type": "function",
                            "refactoring_steps": ["Step 1", "Step 2"]
                        }
                    ]
                },
                "PerformanceAnalysis": {
                    "hotspots": [
                        {"type": "nested_loops", "file": "test.py", "severity": "high"}
                    ]
                },
                "SecurityAudit": {
                    "remediation_plan": [
                        {"type": "sql_injection", "count": 2, "priority": "high", "files": ["test.py"]}
                    ]
                }
            }
        }


class TestRefactoringPlanPhase:
    """Test refactoring plan phase."""
    
    @pytest.fixture
    def phase(self):
        """Create refactoring plan phase."""
        orchestrator = MockOrchestrator()
        return RefactoringPlanPhase(orchestrator)
    
    def test_execute(self, phase):
        """Test phase execution."""
        results = phase.execute()
        
        assert "refactoring_tasks" in results
        assert "priority_high" in results
        assert "priority_medium" in results
        assert "priority_low" in results
        assert "estimated_effort_hours" in results
    
    def test_create_quality_tasks(self, phase):
        """Test quality task creation."""
        results = phase.execute()
        tasks = results["refactoring_tasks"]
        
        quality_tasks = [t for t in tasks if t.get("type") == "quality"]
        assert len(quality_tasks) > 0
    
    def test_create_security_tasks(self, phase):
        """Test security task creation."""
        results = phase.execute()
        tasks = results["refactoring_tasks"]
        
        security_tasks = [t for t in tasks if t.get("type") == "security"]
        assert len(security_tasks) > 0
    
    def test_task_prioritization(self, phase):
        """Test task prioritization."""
        results = phase.execute()
        tasks = results["refactoring_tasks"]
        
        # High priority tasks should come first
        for i in range(len(tasks) - 1):
            curr_priority = {"high": 3, "medium": 2, "low": 1}[tasks[i].get("priority", "low")]
            next_priority = {"high": 3, "medium": 2, "low": 1}[tasks[i+1].get("priority", "low")]
            assert curr_priority >= next_priority
    
    def test_effort_estimation(self, phase):
        """Test effort estimation."""
        results = phase.execute()
        
        assert results["estimated_effort_hours"] > 0
        
        # Each task should have effort estimate
        for task in results["refactoring_tasks"]:
            assert "effort_hours" in task
            assert task["effort_hours"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
