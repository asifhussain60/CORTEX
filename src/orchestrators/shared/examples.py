"""
Shared Orchestrator Library - Usage Examples

Demonstrates how to use the shared infrastructure for Planning and ADO orchestrators.

Author: Asif Hussain
Version: 1.0.0
"""

from pathlib import Path
from src.orchestrators.shared import (
    ProgressTracker,
    ProgressState,
    PhaseProgress,
    HTMLViewerGenerator,
    ViewerMode,
    ViewerConfig,
    DependencyResolver,
    DependencyGraph,
    ValidationPipeline,
    create_plan_validation_pipeline,
    create_phase_validation_pipeline,
    PhaseManager,
    PhaseState as PMPhaseState
)


# ==============================================================================
# Example 1: Feature Plan Progress Tracking
# ==============================================================================

def example_feature_plan_tracking():
    """Example: Track progress for a feature plan."""
    
    # Initialize tracker
    tracking_file = Path("cortex-brain/documents/planning/active/test-feature/tracking/progress-tracker.json")
    tracker = ProgressTracker(tracking_file, plan_type="feature")
    
    # Add phases
    tracker.add_phase(PhaseProgress(
        phase_number=0,
        phase_name="Context Discovery",
        status=ProgressState.NOT_STARTED,
        estimated_hours=2.0,
        tasks_total=5
    ))
    
    tracker.add_phase(PhaseProgress(
        phase_number=1,
        phase_name="Architecture Analysis",
        status=ProgressState.NOT_STARTED,
        estimated_hours=3.0,
        tasks_total=8,
        dependencies=[0]  # Depends on phase 0
    ))
    
    tracker.add_phase(PhaseProgress(
        phase_number=2,
        phase_name="Implementation",
        status=ProgressState.NOT_STARTED,
        estimated_hours=8.0,
        tasks_total=15,
        dependencies=[1]  # Depends on phase 1
    ))
    
    # Start phase 0
    tracker.update_phase(0, status=ProgressState.IN_PROGRESS, progress=50)
    
    # Complete tasks
    tracker.update_phase(0, tasks_completed=3)
    
    # Complete phase 0
    tracker.update_phase(0, status=ProgressState.COMPLETED, progress=100)
    
    # Get summary
    summary = tracker.get_summary()
    print(f"Progress: {summary['overall_progress']}%")
    print(f"Progress Bar: {summary['progress_bar']}")


# ==============================================================================
# Example 2: Epic Plan with Child Plans
# ==============================================================================

def example_epic_plan_tracking():
    """Example: Track progress for an epic with child plans."""
    
    # Initialize epic tracker
    epic_file = Path("cortex-brain/documents/planning/active/CORTEX-5.0/tracking/epic-progress-tracker.json")
    epic_tracker = ProgressTracker(epic_file, plan_type="epic")
    
    # Add child plans
    child1 = ProgressTracker(
        Path("cortex-brain/documents/planning/active/CORTEX-5.0/00A-epic-structure-cleanup/tracking/progress-tracker.json"),
        plan_type="feature"
    )
    child1.progress.plan_name = "Epic Structure Cleanup"
    child1.progress.overall_progress = 100
    child1.progress.status = ProgressState.COMPLETED
    
    child2 = ProgressTracker(
        Path("cortex-brain/documents/planning/active/CORTEX-5.0/00B-epic-feature-planner/tracking/progress-tracker.json"),
        plan_type="feature"
    )
    child2.progress.plan_name = "Epic & Feature Planner"
    child2.progress.overall_progress = 0
    child2.progress.status = ProgressState.NOT_STARTED
    
    epic_tracker.add_child_plan(child1.progress)
    epic_tracker.add_child_plan(child2.progress)
    
    # Recalculate epic progress (aggregate child plans)
    total_progress = sum(c.overall_progress for c in epic_tracker.progress.child_plans)
    epic_tracker.progress.overall_progress = total_progress // len(epic_tracker.progress.child_plans)
    
    epic_tracker.save()


# ==============================================================================
# Example 3: Generate HTML Viewers
# ==============================================================================

def example_generate_html_viewers():
    """Example: Generate epic and feature HTML viewers."""
    
    # Generate epic viewer
    epic_config = ViewerConfig(
        mode=ViewerMode.EPIC,
        plan_name="CORTEX v5 Gap Remediation",
        plan_id="cortex-v5-gap-remediation",
        output_path=Path("cortex-brain/documents/planning/active/CORTEX-5.0/CORTEX-5.0-plan-viewer.html"),
        tracking_json_path="tracking/epic-progress-tracker.json",
        auto_refresh_seconds=5
    )
    
    epic_generator = HTMLViewerGenerator(epic_config)
    epic_generator.save()
    print(f"Generated epic viewer: {epic_config.output_path}")
    
    # Generate feature viewer
    feature_config = ViewerConfig(
        mode=ViewerMode.FEATURE,
        plan_name="Test Coverage Sprint",
        plan_id="test-coverage-sprint",
        output_path=Path("cortex-brain/documents/planning/active/CORTEX-5.0/00C-test-coverage-sprint/test-coverage-sprint-plan-viewer.html"),
        tracking_json_path="tracking/progress-tracker.json",
        auto_refresh_seconds=5
    )
    
    feature_generator = HTMLViewerGenerator(feature_config)
    feature_generator.save()
    print(f"Generated feature viewer: {feature_config.output_path}")


# ==============================================================================
# Example 4: Dependency Resolution
# ==============================================================================

def example_dependency_resolution():
    """Example: Resolve phase dependencies."""
    
    phases = [
        {"phase_number": 0, "phase_name": "Discovery", "status": "completed", "dependencies": []},
        {"phase_number": 1, "phase_name": "Analysis", "status": "completed", "dependencies": [0]},
        {"phase_number": 2, "phase_name": "Design", "status": "not-started", "dependencies": [1]},
        {"phase_number": 3, "phase_name": "Implementation", "status": "not-started", "dependencies": [2]},
        {"phase_number": 4, "phase_name": "Testing", "status": "not-started", "dependencies": [3]},
    ]
    
    # Create dependency graph
    graph = DependencyResolver.create_phase_graph(phases)
    
    # Validate graph
    is_valid, errors = graph.validate()
    if not is_valid:
        print(f"Dependency errors: {errors}")
        return
    
    # Get execution order
    order = graph.topological_sort()
    print(f"Execution order: {' -> '.join(order)}")
    
    # Check what's ready to execute
    completed = {"0", "1"}  # Phases 0 and 1 are complete
    ready = graph.get_ready_nodes(completed)
    print(f"Ready to execute: {ready}")
    
    # Calculate critical path
    durations = {str(p["phase_number"]): 2.0 for p in phases}  # All 2 hours
    critical_path, total_duration = graph.calculate_critical_path(durations)
    print(f"Critical path: {' -> '.join(critical_path)}")
    print(f"Total duration: {total_duration} hours")


# ==============================================================================
# Example 5: Validation Pipeline
# ==============================================================================

def example_validation_pipeline():
    """Example: Validate plan and phase data."""
    
    # Validate plan metadata
    plan_data = {
        "plan_id": "test-feature",
        "plan_name": "Test Feature",
        "plan_type": "feature",
        "created_at": "2026-01-04T10:00:00"
    }
    
    plan_pipeline = create_plan_validation_pipeline()
    plan_report = plan_pipeline.validate(plan_data)
    
    print("Plan Validation:")
    print(f"  Valid: {plan_report.is_valid}")
    print(f"  Errors: {len([e for e in plan_report.errors if not e.passed])}")
    print(f"  Warnings: {len([w for w in plan_report.warnings if not w.passed])}")
    
    # Validate phase data
    phase_data = {
        "phase_number": 0,
        "phase_name": "Context Discovery",
        "status": "in-progress",
        "progress_percentage": 50
    }
    
    phase_pipeline = create_phase_validation_pipeline()
    phase_report = phase_pipeline.validate(phase_data)
    
    print("\nPhase Validation:")
    print(f"  Valid: {phase_report.is_valid}")
    for error in phase_report.errors:
        if not error.passed:
            print(f"  Error: {error.message}")


# ==============================================================================
# Example 6: Phase Manager
# ==============================================================================

def example_phase_manager():
    """Example: Manage phase lifecycle."""
    
    # Initialize manager
    manager = PhaseManager("PlanningOrchestrator")
    
    # Register phases
    manager.register_phase(0, "Context Discovery")
    manager.register_phase(1, "Architecture Analysis")
    manager.register_phase(2, "Implementation")
    
    # Register hooks
    def on_phase_start(phase):
        print(f"Starting phase {phase.phase_number}: {phase.phase_name}")
    
    def on_phase_complete(phase):
        print(f"Completed phase {phase.phase_number}: {phase.phase_name}")
    
    manager.register_hook("before_phase", on_phase_start)
    manager.register_hook("after_phase", on_phase_complete)
    
    # Execute phases
    manager.start_phase(0, "Beginning context discovery")
    manager.complete_phase(0, "Discovery complete")
    
    manager.start_phase(1, "Beginning architecture analysis")
    manager.complete_phase(1, "Analysis complete")
    
    # Get summary
    summary = manager.get_summary()
    print(f"\nProgress: {summary['progress_percentage']}%")
    print(f"Completed phases: {summary['phase_states']['completed']}/{summary['total_phases']}")


# ==============================================================================
# Example 7: Complete Integration (Planning Orchestrator Pattern)
# ==============================================================================

def example_complete_integration():
    """Example: Complete workflow using all shared components."""
    
    plan_id = "refactoring-sprint"
    plan_path = Path(f"cortex-brain/documents/planning/active/{plan_id}")
    
    # 1. Initialize progress tracker
    tracker = ProgressTracker(
        plan_path / "tracking" / "progress-tracker.json",
        plan_type="feature"
    )
    
    # 2. Setup phase manager
    manager = PhaseManager("PlanningOrchestrator")
    
    # 3. Define phases
    phases_config = [
        {"number": 0, "name": "Context Discovery", "hours": 2, "tasks": 5},
        {"number": 1, "name": "Code Analysis", "hours": 3, "tasks": 8},
        {"number": 2, "name": "Refactoring", "hours": 8, "tasks": 15},
        {"number": 3, "name": "Testing", "hours": 4, "tasks": 10},
        {"number": 4, "name": "Documentation", "hours": 2, "tasks": 5},
    ]
    
    # 4. Register phases with both tracker and manager
    for config in phases_config:
        tracker.add_phase(PhaseProgress(
            phase_number=config["number"],
            phase_name=config["name"],
            status=ProgressState.NOT_STARTED,
            estimated_hours=config["hours"],
            tasks_total=config["tasks"]
        ))
        manager.register_phase(config["number"], config["name"])
    
    # 5. Setup dependency graph
    phases_data = [
        {"phase_number": i, "phase_name": c["name"], "dependencies": [i-1] if i > 0 else []}
        for i, c in enumerate(phases_config)
    ]
    dep_graph = DependencyResolver.create_phase_graph(phases_data)
    
    # 6. Validate dependencies
    is_valid, errors = dep_graph.validate()
    if not is_valid:
        print(f"Dependency validation failed: {errors}")
        return
    
    # 7. Execute phases in order
    execution_order = dep_graph.topological_sort()
    completed = set()
    
    for phase_num_str in execution_order:
        phase_num = int(phase_num_str)
        
        # Check dependencies
        is_ready, blocking = dep_graph.nodes[phase_num_str].is_ready(completed)
        if not is_ready:
            print(f"Phase {phase_num} blocked by: {blocking}")
            tracker.update_phase(phase_num, status=ProgressState.BLOCKED)
            continue
        
        # Start phase
        manager.start_phase(phase_num)
        tracker.update_phase(phase_num, status=ProgressState.IN_PROGRESS)
        
        # Simulate work (in real orchestrator, call phase execution logic)
        print(f"Executing phase {phase_num}...")
        
        # Complete phase
        manager.complete_phase(phase_num)
        tracker.update_phase(phase_num, status=ProgressState.COMPLETED, progress=100)
        completed.add(phase_num_str)
    
    # 8. Generate HTML viewer
    viewer_config = ViewerConfig(
        mode=ViewerMode.FEATURE,
        plan_name="Refactoring Sprint",
        plan_id=plan_id,
        output_path=plan_path / f"{plan_id}-plan-viewer.html",
        tracking_json_path="tracking/progress-tracker.json"
    )
    
    generator = HTMLViewerGenerator(viewer_config)
    generator.save()
    
    # 9. Final summary
    print(f"\nPlan Complete!")
    print(f"Progress: {tracker.get_progress_bar()} {tracker.progress.overall_progress}%")
    print(f"HTML Viewer: {viewer_config.output_path}")


if __name__ == "__main__":
    print("=== Shared Orchestrator Library Examples ===\n")
    
    print("1. Feature Plan Tracking")
    example_feature_plan_tracking()
    
    print("\n2. Epic Plan Tracking")
    example_epic_plan_tracking()
    
    print("\n3. HTML Viewer Generation")
    example_generate_html_viewers()
    
    print("\n4. Dependency Resolution")
    example_dependency_resolution()
    
    print("\n5. Validation Pipeline")
    example_validation_pipeline()
    
    print("\n6. Phase Manager")
    example_phase_manager()
    
    print("\n7. Complete Integration")
    example_complete_integration()
