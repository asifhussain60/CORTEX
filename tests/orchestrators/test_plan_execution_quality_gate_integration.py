"""
Integration Test: PlanExecutionOrchestrator + PhaseQualityGate

Validates that Planning System 3.0 quality gate integration works correctly.

Author: Asif Hussain
Version: 3.9.0
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock


class TestPlanExecutionQualityGateIntegration:
    """Integration tests for quality gate in plan execution."""
    
    def test_quality_gate_integration_exists(self):
        """Should have _run_post_execution_quality_gate method."""
        from src.orchestrators.plan_execution_orchestrator import PlanExecutionOrchestrator
        
        orchestrator = PlanExecutionOrchestrator(cortex_root="d:/PROJECTS/CORTEX")
        
        assert hasattr(orchestrator, "_run_post_execution_quality_gate")
        assert callable(orchestrator._run_post_execution_quality_gate)
    
    def test_quality_gate_executes_after_phase_completion(self):
        """Should execute quality gate after successful phase."""
        from src.orchestrators.plan_execution_orchestrator import PlanExecutionOrchestrator
        
        orchestrator = PlanExecutionOrchestrator(cortex_root="d:/PROJECTS/CORTEX")
        
        # Mock phase data
        phase = {
            "phase_number": 1,
            "phase_name": "Test Phase",
            "quality_gate_enabled": True,
            "tasks": []
        }
        
        # Mock quality gate execution
        with patch.object(orchestrator, '_run_post_execution_quality_gate') as mock_gate:
            mock_gate.return_value = {
                "success": True,
                "score": 85,
                "validation_passed": True,
                "should_block_checkpoint": False,
                "findings": [],
                "bypassed": False,
                "message": "Quality gate passed"
            }
            
            result = orchestrator._execute_phase(phase, dry_run=False)
            
            # Quality gate should be called
            mock_gate.assert_called_once_with(phase)
            
            # Result should include quality gate data
            assert "quality_gate" in result
            assert result["quality_gate"]["score"] == 85
            assert result["quality_gate"]["validation_passed"] is True
    
    def test_quality_gate_blocks_checkpoint_on_low_score(self):
        """Should block git checkpoint when score below threshold."""
        from src.orchestrators.plan_execution_orchestrator import PlanExecutionOrchestrator
        
        orchestrator = PlanExecutionOrchestrator(cortex_root="d:/PROJECTS/CORTEX")
        
        phase = {
            "phase_number": 1,
            "phase_name": "Test Phase",
            "quality_gate_enabled": True,
            "tasks": []
        }
        
        # Mock quality gate with low score
        with patch.object(orchestrator, '_run_post_execution_quality_gate') as mock_gate:
            mock_gate.return_value = {
                "success": True,
                "score": 65,  # Below 70 threshold
                "validation_passed": False,
                "should_block_checkpoint": True,
                "findings": [{"severity": "HIGH", "title": "Code smell"}],
                "bypassed": False,
                "message": "Score 65 below threshold 70"
            }
            
            result = orchestrator._execute_phase(phase, dry_run=False)
            
            # Checkpoint should be blocked
            assert result.get("checkpoint_blocked") is True
            assert "checkpoint_blocked_reason" in result
    
    def test_quality_gate_respects_disabled_flag(self):
        """Should skip quality gate when disabled in phase config."""
        from src.orchestrators.plan_execution_orchestrator import PlanExecutionOrchestrator
        
        orchestrator = PlanExecutionOrchestrator(cortex_root="d:/PROJECTS/CORTEX")
        
        phase = {
            "phase_number": 1,
            "phase_name": "Test Phase",
            "quality_gate_enabled": False,  # Disabled
            "tasks": []
        }
        
        with patch.object(orchestrator, '_run_post_execution_quality_gate') as mock_gate:
            result = orchestrator._execute_phase(phase, dry_run=False)
            
            # Quality gate should NOT be called
            mock_gate.assert_not_called()
            
            # No quality gate data in result
            assert "quality_gate" not in result
    
    def test_quality_gate_helper_method_creates_gate_correctly(self):
        """Should create PhaseQualityGate with correct configuration."""
        from src.orchestrators.plan_execution_orchestrator import PlanExecutionOrchestrator
        
        orchestrator = PlanExecutionOrchestrator(cortex_root="d:/PROJECTS/CORTEX")
        
        phase = {
            "quality_gate_threshold": 80,
            "quality_gate_timeout": 90
        }
        
        with patch('src.orchestrators.phase_quality_gate.PhaseQualityGate') as mock_gate_class:
            mock_gate_instance = Mock()
            mock_gate_instance.execute_full_workflow.return_value = Mock(
                success=True,
                score=85,
                validation_passed=True,
                should_block_checkpoint=False,
                findings=[],
                bypassed=False,
                message="Passed"
            )
            mock_gate_class.return_value = mock_gate_instance
            
            result = orchestrator._run_post_execution_quality_gate(phase)
            
            # PhaseQualityGate created with correct config
            mock_gate_class.assert_called_once_with(
                workspace_path=Path("d:/PROJECTS/CORTEX"),
                threshold=80,
                timeout_seconds=90,
                enabled=True
            )
            
            # Result contains score
            assert result["score"] == 85
            assert result["validation_passed"] is True
    
    def test_quality_gate_uses_default_threshold_when_not_specified(self):
        """Should use default threshold of 70 when not in phase config."""
        from src.orchestrators.plan_execution_orchestrator import PlanExecutionOrchestrator
        
        orchestrator = PlanExecutionOrchestrator(cortex_root="d:/PROJECTS/CORTEX")
        
        phase = {}  # No configuration
        
        with patch('src.orchestrators.phase_quality_gate.PhaseQualityGate') as mock_gate_class:
            mock_gate_instance = Mock()
            mock_gate_instance.execute_full_workflow.return_value = Mock(
                success=True, score=75, validation_passed=True, should_block_checkpoint=False,
                findings=[], bypassed=False, message="Passed"
            )
            mock_gate_class.return_value = mock_gate_instance
            
            orchestrator._run_post_execution_quality_gate(phase)
            
            # Should use default threshold=70
            call_args = mock_gate_class.call_args
            assert call_args.kwargs["threshold"] == 70
