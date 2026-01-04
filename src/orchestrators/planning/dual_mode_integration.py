"""
CORTEX 5.0 Dual-Mode Planning Integration

Purpose: Integration layer between Planning Orchestrator and Epic/Feature planners.
         Routes plan operations to appropriate planner based on detected mode.

Version: 5.0.0
Author: Asif Hussain
Created: January 4, 2026

Features:
- Automatic mode detection and routing
- HTML viewer auto-generation on updates
- Progress tracking synchronization
- Backward compatibility with Planning Orchestrator 4.0
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from src.orchestrators.planning.planner_mode_detector import (
    PlannerMode,
    detect_planner_mode,
    validate_epic_structure,
    validate_feature_structure
)
from src.orchestrators.planning.epic_planner import (
    EpicPlanner,
    ChildPlan,
    Milestone,
    PlanStatus as EpicPlanStatus
)
from src.orchestrators.planning.feature_planner import (
    FeaturePlanner,
    Phase,
    PhaseStatus
)
from src.orchestrators.planning.html_viewer_generator import (
    HTMLViewerGenerator,
    ViewerConfig,
    ViewerStyle
)

logger = logging.getLogger(__name__)


class DualModePlanningOrchestrator:
    """
    Orchestrates dual-mode planning (Epic and Feature).
    
    Responsibilities:
    - Detect plan mode automatically
    - Route operations to appropriate planner
    - Generate/regenerate HTML viewers
    - Maintain progress tracking
    - Ensure consistency across modes
    """
    
    def __init__(self, plan_path: Path):
        """
        Initialize dual-mode orchestrator.
        
        Args:
            plan_path: Path to plan directory (epic or feature)
        """
        self.plan_path = plan_path
        self.mode = detect_planner_mode(plan_path)
        
        # Initialize appropriate planner
        if self.mode == PlannerMode.EPIC:
            self.epic_planner = EpicPlanner(plan_path)
            self.feature_planner = None
        elif self.mode == PlannerMode.FEATURE:
            self.feature_planner = FeaturePlanner(plan_path)
            self.epic_planner = None
        else:
            raise ValueError(f"Cannot determine planner mode for {plan_path}")
        
        logger.info(f"Initialized {self.mode.value} mode planner for {plan_path}")
    
    def get_mode(self) -> PlannerMode:
        """Get current planner mode."""
        return self.mode
    
    def validate_structure(self) -> Tuple[bool, List[str]]:
        """
        Validate plan directory structure.
        
        Returns:
            Tuple of (is_valid, list of validation errors)
        """
        if self.mode == PlannerMode.EPIC:
            return validate_epic_structure(self.plan_path)
        elif self.mode == PlannerMode.FEATURE:
            return validate_feature_structure(self.plan_path)
        else:
            return False, ["Unknown planner mode"]
    
    def update_progress(
        self,
        plan_id: str,
        progress: float,
        **kwargs
    ) -> None:
        """
        Update progress for a plan or phase.
        
        For Epic mode: Updates child plan progress
        For Feature mode: Updates phase progress
        
        Args:
            plan_id: ID of plan/phase to update (child plan ID or phase number)
            progress: Progress percentage (0-100)
            **kwargs: Additional mode-specific parameters
        """
        if self.mode == PlannerMode.EPIC:
            self.epic_planner.update_child_plan_progress(
                plan_id,
                progress,
                kwargs.get('phases_complete')
            )
            self.epic_planner.save_tracker()
        elif self.mode == PlannerMode.FEATURE:
            phase_number = int(plan_id) if isinstance(plan_id, str) and plan_id.isdigit() else plan_id
            self.feature_planner.update_phase_progress(
                phase_number,
                progress,
                kwargs.get('tasks_complete'),
                kwargs.get('actual_hours')
            )
            self.feature_planner.save_tracker()
        
        # Regenerate HTML viewer
        self.generate_html_viewer()
        
        logger.info(f"Updated {plan_id} progress to {progress}%")
    
    def start_plan(self, plan_id: str) -> None:
        """
        Start a plan or phase.
        
        For Epic mode: Marks child plan as in progress
        For Feature mode: Starts a phase
        
        Args:
            plan_id: ID of plan/phase to start
        """
        if self.mode == PlannerMode.EPIC:
            plan = self.epic_planner._get_child_plan(plan_id)
            if plan:
                plan.status = EpicPlanStatus.IN_PROGRESS
                plan.status_emoji = "🔄"
                from datetime import datetime
                if not plan.start_date:
                    plan.start_date = datetime.now().isoformat()
                self.epic_planner._recalculate_progress()
                self.epic_planner.save_tracker()
        elif self.mode == PlannerMode.FEATURE:
            phase_number = int(plan_id) if isinstance(plan_id, str) and plan_id.isdigit() else plan_id
            self.feature_planner.start_phase(phase_number)
        
        self.generate_html_viewer()
        logger.info(f"Started {plan_id}")
    
    def complete_plan(self, plan_id: str) -> None:
        """
        Mark a plan or phase as complete.
        
        Args:
            plan_id: ID of plan/phase to complete
        """
        if self.mode == PlannerMode.EPIC:
            self.epic_planner.mark_plan_complete(plan_id)
            self.epic_planner.save_tracker()
        elif self.mode == PlannerMode.FEATURE:
            phase_number = int(plan_id) if isinstance(plan_id, str) and plan_id.isdigit() else plan_id
            self.feature_planner.complete_phase(phase_number)
            self.feature_planner.save_tracker()
        
        self.generate_html_viewer()
        logger.info(f"Completed {plan_id}")
    
    def get_progress_summary(self) -> Dict:
        """
        Get progress summary for the plan.
        
        Returns:
            Dictionary containing progress metrics
        """
        if self.mode == PlannerMode.EPIC:
            tracker = self.epic_planner.tracker
            return {
                "mode": "epic",
                "overall_progress": tracker.overall_progress,
                "total_plans": tracker.total_plans,
                "completed_plans": tracker.completed_plans,
                "total_phases": tracker.total_phases,
                "completed_phases": tracker.completed_phases,
                "status": tracker.status.value,
                "plan_name": tracker.plan_name
            }
        elif self.mode == PlannerMode.FEATURE:
            tracker = self.feature_planner.tracker
            return {
                "mode": "feature",
                "overall_progress": tracker.overall_progress,
                "current_phase": tracker.current_phase,
                "total_phases": tracker.total_phases,
                "completed_phases": tracker.completed_phases,
                "estimated_hours": tracker.estimated_hours,
                "actual_hours": tracker.actual_hours,
                "status": tracker.status,
                "plan_name": tracker.plan_name
            }
        else:
            return {"mode": "unknown", "error": "Cannot determine planner mode"}
    
    def get_next_available(self) -> Optional[Dict]:
        """
        Get next available plan/phase to work on.
        
        Returns:
            Dictionary with next item details or None if nothing available
        """
        if self.mode == PlannerMode.EPIC:
            next_plans = self.epic_planner.get_next_available_plans()
            if next_plans:
                plan = next_plans[0]  # Return first available
                return {
                    "type": "child_plan",
                    "id": plan.id,
                    "order": plan.order,
                    "name": plan.name,
                    "status": plan.status.value
                }
        elif self.mode == PlannerMode.FEATURE:
            next_phase = self.feature_planner.get_next_phase()
            if next_phase:
                return {
                    "type": "phase",
                    "phase_number": next_phase.phase_number,
                    "phase_name": next_phase.phase_name,
                    "status": next_phase.status.value
                }
        
        return None
    
    def generate_html_viewer(self) -> Path:
        """
        Generate or regenerate HTML plan viewer.
        
        Returns:
            Path to generated HTML file
        """
        try:
            if self.mode == PlannerMode.EPIC:
                tracker_data = self.epic_planner.tracker.to_dict()
                plan_id = tracker_data["plan_id"] or "epic-plan"
                tracker_relative_path = "tracking/epic-progress-tracker.json"
            elif self.mode == PlannerMode.FEATURE:
                tracker_data = self.feature_planner.tracker.to_dict()
                plan_id = tracker_data["plan_id"] or "feature-plan"
                tracker_relative_path = "tracking/progress-tracker.json"
            else:
                raise ValueError(f"Cannot generate viewer for mode: {self.mode}")
            
            # Configure viewer
            config = ViewerConfig(
                plan_name=tracker_data["plan_name"] or "Untitled Plan",
                plan_type=self.mode.value,
                tracker_path=tracker_relative_path,
                refresh_interval=30,
                enable_auto_refresh=True
            )
            
            # Generate HTML
            generator = HTMLViewerGenerator(config, ViewerStyle())
            output_path = self.plan_path / f"{plan_id}-plan-viewer.html"
            generator.generate(tracker_data, output_path)
            
            logger.info(f"Generated HTML viewer: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to generate HTML viewer: {e}")
            raise
    
    def sync_from_planning_orchestrator(self, plan_data: Dict) -> None:
        """
        Synchronize tracker from Planning Orchestrator 4.0 plan data.
        
        Enables migration from existing plans to new tracking system.
        
        Args:
            plan_data: Plan data from Planning Orchestrator
        """
        if self.mode == PlannerMode.FEATURE:
            self.feature_planner.initialize_from_plan_data(plan_data)
            self.generate_html_viewer()
            logger.info("Synchronized feature planner from plan data")
        else:
            logger.warning("Sync from planning orchestrator only supported for feature mode")
    
    def export_tracker(self) -> Dict:
        """
        Export current tracker data.
        
        Returns:
            Dictionary containing tracker data
        """
        if self.mode == PlannerMode.EPIC:
            return self.epic_planner.tracker.to_dict()
        elif self.mode == PlannerMode.FEATURE:
            return self.feature_planner.tracker.to_dict()
        else:
            return {}


# Convenience functions for common operations

def create_epic_plan(
    epic_path: Path,
    plan_name: str,
    plan_id: str,
    child_plans: List[Dict]
) -> DualModePlanningOrchestrator:
    """
    Create a new epic plan with child plans.
    
    Args:
        epic_path: Path to epic root directory
        plan_name: Name of the epic
        plan_id: Unique identifier
        child_plans: List of child plan definitions
        
    Returns:
        Initialized DualModePlanningOrchestrator
    """
    # Create directory structure
    epic_path.mkdir(parents=True, exist_ok=True)
    (epic_path / "tracking").mkdir(exist_ok=True)
    
    # Initialize epic planner
    planner = EpicPlanner(epic_path)
    planner.tracker.plan_name = plan_name
    planner.tracker.plan_id = plan_id
    
    # Add child plans
    for cp_data in child_plans:
        child_plan = ChildPlan(
            order=cp_data["order"],
            id=cp_data["id"],
            name=cp_data["name"],
            folder=cp_data["folder"],
            total_phases=cp_data.get("total_phases", 0),
            duration=cp_data.get("duration", ""),
            dependencies=cp_data.get("dependencies", []),
            dependency_rule=cp_data.get("dependency_rule", ""),
            viewer_url=f"{cp_data['folder']}/{cp_data['id']}-plan-viewer.html"
        )
        planner.add_child_plan(child_plan)
    
    planner.save_tracker()
    
    # Create orchestrator and generate viewer
    orchestrator = DualModePlanningOrchestrator(epic_path)
    orchestrator.generate_html_viewer()
    
    logger.info(f"Created epic plan: {plan_name}")
    return orchestrator


def create_feature_plan(
    feature_path: Path,
    plan_name: str,
    plan_id: str,
    phases: List[Dict]
) -> DualModePlanningOrchestrator:
    """
    Create a new feature plan with phases.
    
    Args:
        feature_path: Path to feature root directory
        plan_name: Name of the feature
        plan_id: Unique identifier
        phases: List of phase definitions
        
    Returns:
        Initialized DualModePlanningOrchestrator
    """
    # Create directory structure
    feature_path.mkdir(parents=True, exist_ok=True)
    (feature_path / "tracking").mkdir(exist_ok=True)
    (feature_path / "context").mkdir(exist_ok=True)
    (feature_path / "artifacts").mkdir(exist_ok=True)
    (feature_path / "reports").mkdir(exist_ok=True)
    
    # Initialize feature planner
    planner = FeaturePlanner(feature_path)
    planner.tracker.plan_name = plan_name
    planner.tracker.plan_id = plan_id
    
    # Add phases
    for phase_data in phases:
        phase = Phase(
            phase_number=phase_data["phase_number"],
            phase_name=phase_data["phase_name"],
            estimated_hours=phase_data.get("estimated_hours", 0.0),
            total_tasks=phase_data.get("total_tasks", 0)
        )
        planner.add_phase(phase)
    
    planner.save_tracker()
    
    # Create orchestrator and generate viewer
    orchestrator = DualModePlanningOrchestrator(feature_path)
    orchestrator.generate_html_viewer()
    
    logger.info(f"Created feature plan: {plan_name}")
    return orchestrator


# Export public API
__all__ = [
    "DualModePlanningOrchestrator",
    "create_epic_plan",
    "create_feature_plan"
]
