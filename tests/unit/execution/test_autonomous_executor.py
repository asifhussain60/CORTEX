"""
Tests for Autonomous Execution Engine (ENH-067)

Validates:
- Single and multi-stage plan execution
- Silent execution (no mid-execution prompts)
- Token budget monitoring and checkpointing
- Error recovery and continuation

Author: Asif Hussain
"""

import pytest

from cortex.core.execution.autonomous_executor import (
    AutonomousExecutor,
    ExecutionResult,
    ExecutionStatus,
    Plan,
    Stage,
    StageStatus,
    execute_plan_autonomously,
)
from cortex.models.canonical_enums import IntentType


class TestStage:
    """Tests for Stage model."""
    
    def test_stage_duration_calculation(self):
        """Test stage duration calculation."""
        stage = Stage(
            id="S1",
            name="Test Stage",
            description="Test",
            intent=IntentType.IMPLEMENT
        )
        
        # No timing yet
        assert stage.duration() == 0.0
        
        # Set timing
        stage.start_time = 100.0
        stage.end_time = 105.5
        assert stage.duration() == 5.5
    
    def test_stage_default_status(self):
        """Test stage starts with NOT_STARTED status."""
        stage = Stage(
            id="S1",
            name="Test",
            description="Test",
            intent=IntentType.FIX
        )
        assert stage.status == StageStatus.NOT_STARTED


class TestPlan:
    """Tests for Plan model."""
    
    def test_total_estimated_tokens(self):
        """Test calculation of total estimated tokens."""
        plan = Plan(
            id="P1",
            name="Test Plan",
            description="Test",
            stages=[
                Stage("S1", "Stage 1", "Test", IntentType.IMPLEMENT, estimated_tokens=5000),
                Stage("S2", "Stage 2", "Test", IntentType.TEST, estimated_tokens=3000),
                Stage("S3", "Stage 3", "Test", IntentType.REFACTOR, estimated_tokens=4000),
            ]
        )
        
        assert plan.total_estimated_tokens() == 12000
    
    def test_completed_stages_filter(self):
        """Test filtering of completed stages."""
        stage1 = Stage("S1", "Stage 1", "Test", IntentType.IMPLEMENT)
        stage1.status = StageStatus.COMPLETED
        
        stage2 = Stage("S2", "Stage 2", "Test", IntentType.TEST)
        stage2.status = StageStatus.IN_PROGRESS
        
        stage3 = Stage("S3", "Stage 3", "Test", IntentType.REFACTOR)
        stage3.status = StageStatus.COMPLETED
        
        plan = Plan(
            id="P1",
            name="Test Plan",
            description="Test",
            stages=[stage1, stage2, stage3]
        )
        
        completed = plan.completed_stages()
        assert len(completed) == 2
        assert completed[0].id == "S1"
        assert completed[1].id == "S3"
    
    def test_failed_stages_filter(self):
        """Test filtering of failed stages."""
        stage1 = Stage("S1", "Stage 1", "Test", IntentType.IMPLEMENT)
        stage1.status = StageStatus.COMPLETED
        
        stage2 = Stage("S2", "Stage 2", "Test", IntentType.TEST)
        stage2.status = StageStatus.FAILED
        
        stage3 = Stage("S3", "Stage 3", "Test", IntentType.REFACTOR)
        stage3.status = StageStatus.NOT_STARTED
        
        plan = Plan(
            id="P1",
            name="Test Plan",
            description="Test",
            stages=[stage1, stage2, stage3]
        )
        
        failed = plan.failed_stages()
        assert len(failed) == 1
        assert failed[0].id == "S2"
    
    def test_pending_stages_filter(self):
        """Test filtering of pending stages."""
        stage1 = Stage("S1", "Stage 1", "Test", IntentType.IMPLEMENT)
        stage1.status = StageStatus.COMPLETED
        
        stage2 = Stage("S2", "Stage 2", "Test", IntentType.TEST)
        stage2.status = StageStatus.NOT_STARTED
        
        stage3 = Stage("S3", "Stage 3", "Test", IntentType.REFACTOR)
        stage3.status = StageStatus.NOT_STARTED
        
        plan = Plan(
            id="P1",
            name="Test Plan",
            description="Test",
            stages=[stage1, stage2, stage3]
        )
        
        pending = plan.pending_stages()
        assert len(pending) == 2
        assert pending[0].id == "S2"
        assert pending[1].id == "S3"


class TestExecutionResult:
    """Tests for ExecutionResult model."""
    
    def test_success_rate_calculation(self):
        """Test success rate calculation."""
        result = ExecutionResult(
            plan_id="P1",
            status=ExecutionStatus.COMPLETED,
            completed_stages=8,
            total_stages=10,
            token_usage=50000
        )
        
        assert result.success_rate() == 80.0
    
    def test_success_rate_zero_stages(self):
        """Test success rate with no stages."""
        result = ExecutionResult(
            plan_id="P1",
            status=ExecutionStatus.FAILED,
            completed_stages=0,
            total_stages=0,
            token_usage=0
        )
        
        assert result.success_rate() == 0.0


class TestAutonomousExecutor:
    """Tests for AutonomousExecutor."""
    
    def test_execute_empty_plan_fails(self):
        """Test execution of plan with no stages fails gracefully."""
        executor = AutonomousExecutor()
        plan = Plan(
            id="P1",
            name="Empty Plan",
            description="Test",
            stages=[]
        )
        
        result = executor.execute_plan(plan)
        
        assert result.status == ExecutionStatus.FAILED
        assert result.completed_stages == 0
        assert result.total_stages == 0
        assert result.error_message is not None
        assert "no stages" in result.error_message.lower()
    
    def test_execute_single_stage_plan_success(self):
        """Test successful execution of single-stage plan."""
        executor = AutonomousExecutor()
        plan = Plan(
            id="P1",
            name="Single Stage",
            description="Test",
            stages=[
                Stage("S1", "Implement feature", "Test", IntentType.IMPLEMENT, estimated_tokens=5000)
            ]
        )
        
        result = executor.execute_plan(plan)
        
        assert result.status == ExecutionStatus.COMPLETED
        assert result.completed_stages == 1
        assert result.total_stages == 1
        assert result.success_rate() == 100.0
        assert plan.stages[0].status == StageStatus.COMPLETED
    
    def test_execute_multi_stage_plan_no_prompts(self):
        """Test multi-stage plan executes without prompts (CORE-049)."""
        executor = AutonomousExecutor()
        plan = Plan(
            id="P1",
            name="Multi Stage",
            description="Test",
            stages=[
                Stage("S1", "Implement", "Test", IntentType.IMPLEMENT, estimated_tokens=3000),
                Stage("S2", "Test", "Test", IntentType.TEST, estimated_tokens=2000),
                Stage("S3", "Refactor", "Test", IntentType.REFACTOR, estimated_tokens=2500),
            ]
        )
        
        result = executor.execute_plan(plan, silent=True)
        
        assert result.status == ExecutionStatus.COMPLETED
        assert result.completed_stages == 3
        assert result.total_stages == 3
        assert result.success_rate() == 100.0
        
        # Verify all stages completed
        for stage in plan.stages:
            assert stage.status == StageStatus.COMPLETED
            assert stage.start_time is not None
            assert stage.end_time is not None
    
    def test_token_budget_checkpoint_at_75_percent(self):
        """Test checkpoint creation at 75% token budget."""
        executor = AutonomousExecutor()
        
        # Create plan that will exceed 75% budget after stage 2
        plan = Plan(
            id="P1",
            name="Large Plan",
            description="Test",
            stages=[
                Stage("S1", "Stage 1", "Test", IntentType.IMPLEMENT, estimated_tokens=300000),
                Stage("S2", "Stage 2", "Test", IntentType.TEST, estimated_tokens=300000),
                Stage("S3", "Stage 3", "Test", IntentType.REFACTOR, estimated_tokens=300000),  # Would exceed 750k
            ]
        )
        
        result = executor.execute_plan(plan, auto_checkpoint=True)
        
        # Should stop at checkpoint before S3
        assert result.status == ExecutionStatus.CHECKPOINT
        assert result.completed_stages == 2
        assert result.total_stages == 3
        assert result.continuation_prompt is not None
        assert "checkpoint" in result.continuation_prompt.lower()
    
    def test_error_recovery_continues_next_stage(self):
        """Test execution continues to next stage after non-critical error."""
        executor = AutonomousExecutor()
        
        # Create plan with middle stage that will fail (unsupported intent)
        plan = Plan(
            id="P1",
            name="Error Recovery",
            description="Test",
            stages=[
                Stage("S1", "Stage 1", "Test", IntentType.IMPLEMENT, estimated_tokens=3000),
                Stage("S2-noncritical", "Stage 2", "Test", IntentType.UNKNOWN, estimated_tokens=2000),  # Will fail
                Stage("S3", "Stage 3", "Test", IntentType.REFACTOR, estimated_tokens=2500),
            ]
        )
        
        result = executor.execute_plan(plan)
        
        # Should complete S1, skip S2, complete S3
        assert result.status == ExecutionStatus.COMPLETED
        assert result.completed_stages == 2  # S1 and S3
        assert plan.stages[0].status == StageStatus.COMPLETED
        assert plan.stages[1].status == StageStatus.SKIPPED
        assert plan.stages[2].status == StageStatus.COMPLETED
    
    def test_error_recovery_stops_on_critical_error(self):
        """Test execution stops on critical stage failure."""
        executor = AutonomousExecutor()
        
        # Create plan with critical middle stage that will fail
        plan = Plan(
            id="P1",
            name="Critical Error",
            description="Test",
            stages=[
                Stage("S1", "Stage 1", "Test", IntentType.IMPLEMENT, estimated_tokens=3000),
                Stage("S2-critical", "Critical Stage", "Test", IntentType.UNKNOWN, estimated_tokens=2000),  # Will fail
                Stage("S3", "Stage 3", "Test", IntentType.REFACTOR, estimated_tokens=2500),
            ]
        )
        
        result = executor.execute_plan(plan)
        
        # Should complete S1, fail at S2, never reach S3
        assert result.status == ExecutionStatus.FAILED
        assert result.completed_stages == 1
        assert plan.stages[0].status == StageStatus.COMPLETED
        assert plan.stages[1].status == StageStatus.FAILED
        assert plan.stages[2].status == StageStatus.NOT_STARTED
        assert result.error_message is not None
    
    def test_token_usage_tracking(self):
        """Test token usage is tracked across stages."""
        executor = AutonomousExecutor()
        plan = Plan(
            id="P1",
            name="Token Tracking",
            description="Test",
            stages=[
                Stage("S1", "Stage 1", "Test", IntentType.IMPLEMENT, estimated_tokens=5000),
                Stage("S2", "Stage 2", "Test", IntentType.TEST, estimated_tokens=3000),
                Stage("S3", "Stage 3", "Test", IntentType.REFACTOR, estimated_tokens=4000),
            ]
        )
        
        result = executor.execute_plan(plan)
        
        assert result.status == ExecutionStatus.COMPLETED
        assert result.token_usage == 12000  # Sum of all stages
    
    def test_continuation_prompt_generation(self):
        """Test continuation prompt contains necessary information."""
        executor = AutonomousExecutor()
        plan = Plan(
            id="WAVE-N",
            name="Test Plan",
            description="Test",
            stages=[
                Stage("S1", "Stage 1", "Test", IntentType.IMPLEMENT, estimated_tokens=300000),
                Stage("S2", "Stage 2", "Test", IntentType.TEST, estimated_tokens=300000),
                Stage("S3", "Stage 3", "Test", IntentType.REFACTOR, estimated_tokens=300000),
            ]
        )
        
        result = executor.execute_plan(plan)
        
        assert result.status == ExecutionStatus.CHECKPOINT
        prompt = result.continuation_prompt
        assert prompt is not None
        assert "WAVE-N" in prompt
        assert "Checkpoint" in prompt
        assert "2/3 stages" in prompt or "2" in prompt
        assert "✅" in prompt  # Completed marker
        assert "⚪" in prompt  # Pending marker


class TestExecutePlanAutonomously:
    """Tests for convenience function."""
    
    def test_convenience_function_executes_plan(self):
        """Test convenience function works correctly."""
        plan = Plan(
            id="P1",
            name="Test",
            description="Test",
            stages=[
                Stage("S1", "Stage 1", "Test", IntentType.IMPLEMENT, estimated_tokens=5000)
            ]
        )
        
        result = execute_plan_autonomously(plan)
        
        assert result.status == ExecutionStatus.COMPLETED
        assert result.completed_stages == 1
    
    def test_convenience_function_silent_by_default(self):
        """Test convenience function uses silent execution by default."""
        plan = Plan(
            id="P1",
            name="Test",
            description="Test",
            stages=[
                Stage("S1", "Stage 1", "Test", IntentType.IMPLEMENT, estimated_tokens=5000),
                Stage("S2", "Stage 2", "Test", IntentType.TEST, estimated_tokens=3000),
            ]
        )
        
        result = execute_plan_autonomously(plan)
        
        # Should complete without prompts
        assert result.status == ExecutionStatus.COMPLETED
        assert result.completed_stages == 2
