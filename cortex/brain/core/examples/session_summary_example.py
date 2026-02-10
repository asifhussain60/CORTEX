"""
Example: Using Session Summary Generator in Orchestrators

This demonstrates how orchestrators should generate session summaries
during autonomous multi-stage implementations.

Author: Asif Hussain
Date: 2026-02-07
"""

from cortex.brain.core.session_summary_generator import (
    format_session_summary,
    generate_continuation_checkpoint,
    SessionMetrics,
    StageResult,
)


def autonomous_implementation_example():
    """
    Example of an orchestrator tracking stages and generating summary.
    
    This would typically be in MasterOrchestrator or PlanOrchestrator.
    """
    # Track completed stages during autonomous execution
    completed_stages = [
        StageResult(
            stage_number=1,
            stage_name="Brain Health Monitor",
            files_created=[
                "cortex/orchestrators/support/brain_health_orchestrator.py",
                "cortex/infrastructure/brain_health_metrics.py",
                "tests/orchestrators/support/test_brain_health_orchestrator.py",
            ],
            tests_passing="16/16",
            duration_minutes=25,
            status="✅"
        ),
        StageResult(
            stage_number=2,
            stage_name="Orchestrator Capability Mesh",
            files_created=[
                "cortex/orchestrators/registry/capability_mesh.py",
                "cortex/orchestrators/registry/capability_discovery.py",
                "tests/orchestrators/registry/test_capability_mesh.py",
            ],
            tests_passing="17/17",
            duration_minutes=30,
            status="✅"
        ),
        StageResult(
            stage_number=3,
            stage_name="Context-Aware Governance",
            files_created=[
                "cortex/governance/context_aware_governance.py",
                "cortex/governance/rule_weight_calculator.py",
                "tests/governance/test_context_aware_governance.py",
            ],
            tests_passing="13/13",
            duration_minutes=20,
            status="✅"
        ),
    ]
    
    # Define remaining stages
    remaining_stages = [
        {
            "number": 4,
            "name": "Company Domain Enhancement Pipeline",
            "tests": "30",
            "estimate": "3 days",
            "priority": "P0"
        },
        {
            "number": 5,
            "name": "Production Rollout Monitoring",
            "tests": "18",
            "estimate": "2 days",
            "priority": "P0"
        },
        # ... more stages
    ]
    
    # Calculate metrics
    metrics = SessionMetrics(
        token_used_k=84,
        token_total_k=1000,
        implementation_time_minutes=75,
        total_tests_passing="46/46",
        type_hint_coverage="100%",
        docstring_coverage="100%",
        next_stage_preview="Stage 4 ready (30 tests, 3 days estimate)"
    )
    
    # Add governance notes
    governance_notes = [
        "All CORE rules applied (CORE-008 TDD, CORE-011 type hints, CORE-012 docstrings)",
        "Audit trail complete: AC_START → AC_COMPLETE markers in all files",
        "EnforcementOrchestrator validation: PASSED (7-agent gate)",
        "Git checkpoints at stage boundaries (CORE-026)",
    ]
    
    # Generate session summary
    summary = format_session_summary(
        session_title="Phase 38 Stages 1-3",
        completed_stages=completed_stages,
        remaining_stages=remaining_stages,
        metrics=metrics,
        governance_notes=governance_notes,
        next_command="continue with stage 4: Company Domain Enhancement Pipeline"
    )
    
    # Output to chat (not file - CORE-002)
    print(summary)
    
    # If token budget high, generate continuation checkpoint
    token_percentage = (metrics.token_used_k / metrics.token_total_k) * 100
    if token_percentage >= 85:
        checkpoint = generate_continuation_checkpoint(
            session_id="Phase 38 Stage 4",
            last_completed="Context-Aware Governance",
            next_action="Implement Company Domain Enhancement Pipeline (30 tests)",
            token_percentage=token_percentage,
            branch="CORTEX"
        )
        print("\n" + checkpoint)


def high_token_usage_example():
    """
    Example when token budget is high (>85%).
    
    Orchestrator should generate continuation checkpoint.
    """
    completed_stages = [
        StageResult(1, "Stage 1", ["file1.py"], "10/10", 20),
        StageResult(2, "Stage 2", ["file2.py"], "15/15", 25),
        StageResult(3, "Stage 3", ["file3.py"], "20/20", 30),
        StageResult(4, "Stage 4", ["file4.py"], "25/25", 35),
    ]
    
    metrics = SessionMetrics(
        token_used_k=920,  # 92% used!
        token_total_k=1000,
        implementation_time_minutes=110,
        total_tests_passing="70/70"
    )
    
    summary = format_session_summary(
        session_title="Phase 40 Stages 1-4",
        completed_stages=completed_stages,
        remaining_stages=[
            {"number": 5, "name": "Stage 5", "tests": "30", "estimate": "2 days", "priority": "P0"}
        ],
        metrics=metrics,
        next_command="continue with stage 5"
    )
    
    print(summary)
    
    # High usage - generate checkpoint
    checkpoint = generate_continuation_checkpoint(
        session_id="Phase 40 Stage 5",
        last_completed="Stage 4 implementation",
        next_action="Continue with Stage 5 (30 tests)",
        token_percentage=92.0,
        branch="CORTEX"
    )
    
    print("\n" + checkpoint)


if __name__ == "__main__":
    print("=== Autonomous Implementation Example ===\n")
    autonomous_implementation_example()
    
    print("\n\n=== High Token Usage Example ===\n")
    high_token_usage_example()
