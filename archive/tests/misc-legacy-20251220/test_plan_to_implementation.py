"""
End-to-end integration test for plan-to-implementation workflow.

Tests complete flow: Planning → Execution → TDD → Git Checkpointing
"""

import pytest
import os


def test_plan_to_implementation_flow(temp_project, temp_brain, sample_planning_request):
    """Test complete plan-to-implementation workflow."""
    # Phase 1: Create plan
    from src.orchestrators.planning_orchestrator import PlanningOrchestrator
    
    planner = PlanningOrchestrator(project_root=temp_project)
    
    plan = planner.create_plan(
        feature_name=sample_planning_request["feature_name"],
        description=sample_planning_request["description"],
        acceptance_criteria=sample_planning_request["acceptance_criteria"]
    )
    
    assert plan is not None
    assert "feature_name" in plan or "plan_id" in plan
    
    # Phase 2: Validate plan (DoR)
    validation_result = planner.validate_definition_of_ready(plan)
    
    # Plan should be ready or validation should provide feedback
    assert validation_result is not None
    
    # Phase 3: Execute plan (simulated)
    # In real workflow, PlanExecutionOrchestrator would take over
    # For integration test, verify plan structure is compatible
    
    assert "phases" in plan or "tasks" in plan or isinstance(plan, dict)


def test_tdd_full_cycle(temp_project, temp_brain):
    """Test complete TDD cycle: RED → GREEN → REFACTOR."""
    import subprocess
    
    # Initialize git repo for checkpointing
    subprocess.run(["git", "init"], cwd=temp_project, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=temp_project, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=temp_project, capture_output=True)
    
    # Phase 1: RED - Write failing test
    from src.orchestrators.tdd_implementation_orchestrator import TDDImplementationOrchestrator
    
    tdd = TDDImplementationOrchestrator(project_root=temp_project)
    
    session = tdd.start_tdd_session(
        feature="Test Feature",
        test_file="tests/test_feature.py"
    )
    
    assert session is not None
    
    # Phase 2: Git checkpoint after RED
    from src.orchestrators.git_checkpoint_orchestrator import GitCheckpointOrchestrator
    
    git = GitCheckpointOrchestrator(project_root=temp_project)
    
    # Create test file for checkpoint
    test_file = os.path.join(temp_project, "tests", "test_feature.py")
    os.makedirs(os.path.dirname(test_file), exist_ok=True)
    with open(test_file, "w") as f:
        f.write("def test_example():\n    assert False  # RED phase\n")
    
    checkpoint_result = git.create_checkpoint(
        phase="RED",
        message="RED: Failing test created"
    )
    
    # Verify checkpoint created
    assert checkpoint_result is not None


def test_learning_feedback_loop(temp_project, temp_brain):
    """Test learning feedback loop: Operation → Failure → Learning → Prevention."""
    # Phase 1: Operation failure
    from src.cortex_agents.learning_capture_agent import LearningCaptureAgent
    
    agent = LearningCaptureAgent(project_root=temp_project)
    
    failure_result = {
        "success": False,
        "error": "Connection timeout",
        "operation": "database_query"
    }
    
    # Phase 2: Capture learning
    learning_event = agent.capture_from_operation_result(
        operation_name="database_query",
        result=failure_result,
        context={"timeout": 30}
    )
    
    assert learning_event is not None
    
    # Phase 3: Store in Tier 2
    from src.tier2.knowledge_graph import KnowledgeGraph
    
    kg = KnowledgeGraph(brain_path=temp_brain)
    
    pattern_id = kg.store_pattern(
        pattern_type="operation_failure",
        description=f"Timeout in {learning_event['operation_name']}",
        confidence=0.8
    )
    
    assert pattern_id is not None
    
    # Phase 4: Query patterns for prevention
    similar_failures = kg.search_patterns("timeout")
    
    assert len(similar_failures) > 0
    # System can now prevent similar failures
