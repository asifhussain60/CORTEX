"""
Onboarding Step Base Classes

Extensible step architecture for onboarding flows.
Each step is self-contained and can be easily added/removed.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class StepStatus(Enum):
    """Step execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class StepDisplayFormat(Enum):
    """How step output should be displayed"""
    PROGRESS_BAR = "progress_bar"
    ANIMATED_DIAGRAM = "animated_diagram"
    SPLIT_DIAGRAM = "split_diagram"
    CHECKLIST = "checklist"
    STATUS_REPORT = "status_report"
    ANIMATED_CARDS = "animated_cards"
    TABLE = "table"
    TREE_VIEW = "tree_view"
    INTERACTIVE_DASHBOARD = "interactive_dashboard"
    LIVE_RENDER = "live_render"
    TEXT_ONLY = "text_only"


@dataclass
class StepResult:
    """Result of step execution"""
    success: bool
    status: StepStatus
    message: str
    data: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    duration_seconds: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class OnboardingStep(ABC):
    """
    Base class for all onboarding steps.
    
    Steps are self-contained units of work that can be:
    - Added/removed easily
    - Executed independently
    - Skipped based on conditions
    - Reordered without breaking dependencies
    
    Example:
    ```python
    class EnvironmentDetectionStep(OnboardingStep):
        def __init__(self):
            super().__init__(
                step_id="detect_environment",
                name="Environment Detection",
                description="Detect platform, shell, paths, and tools",
                display_format=StepDisplayFormat.PROGRESS_BAR,
                estimated_duration=30,
                skippable=False,
                required_for_profiles=["quick", "standard", "comprehensive"]
            )
        
        def execute(self, context: Dict[str, Any]) -> StepResult:
            # Step implementation
            return StepResult(
                success=True,
                status=StepStatus.COMPLETED,
                message="Environment detected successfully",
                data={"platform": "Windows", "python_version": "3.11.5"}
            )
        
        def validate_prerequisites(self, context: Dict[str, Any]) -> bool:
            # Check if step can run
            return True
    ```
    """
    
    def __init__(
        self,
        step_id: str,
        name: str,
        description: str,
        display_format: StepDisplayFormat = StepDisplayFormat.TEXT_ONLY,
        estimated_duration: int = 60,  # seconds
        skippable: bool = True,
        required_for_profiles: Optional[List[str]] = None,
        dependencies: Optional[List[str]] = None,
        display_options: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize onboarding step.
        
        Args:
            step_id: Unique identifier for step
            name: Human-readable step name
            description: What this step does
            display_format: How to display step output
            estimated_duration: Expected duration in seconds
            skippable: Whether step can be skipped on error
            required_for_profiles: Which profiles require this step (None = all)
            dependencies: List of step_ids that must complete first
            display_options: Additional display configuration
        """
        self.step_id = step_id
        self.name = name
        self.description = description
        self.display_format = display_format
        self.estimated_duration = estimated_duration
        self.skippable = skippable
        self.required_for_profiles = required_for_profiles or ["quick", "standard", "comprehensive"]
        self.dependencies = dependencies or []
        self.display_options = display_options or {}
        
        self.status = StepStatus.PENDING
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.result: Optional[StepResult] = None
        
        self.logger = logging.getLogger(f"epm.step.{step_id}")
    
    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> StepResult:
        """
        Execute the step.
        
        Args:
            context: Execution context with:
                - profile: "quick", "standard", or "comprehensive"
                - previous_results: Results from completed steps
                - user_preferences: User configuration
                - project_root: Project root path
                - Additional context data
        
        Returns:
            StepResult with execution outcome
        """
        pass
    
    @abstractmethod
    def validate_prerequisites(self, context: Dict[str, Any]) -> bool:
        """
        Check if prerequisites for step execution are met.
        
        Args:
            context: Execution context
        
        Returns:
            True if step can run, False otherwise
        """
        pass
    
    def can_skip(self, context: Dict[str, Any]) -> bool:
        """
        Determine if step should be skipped.
        
        Args:
            context: Execution context
        
        Returns:
            True if step should be skipped
        """
        # Check if step is required for current profile
        profile = context.get("profile", "standard")
        if profile not in self.required_for_profiles:
            return True
        
        # Check prerequisites
        if not self.validate_prerequisites(context):
            return not self.skippable
        
        return False
    
    def get_display_title(self) -> str:
        """Get formatted display title for step"""
        icons = {
            "detect_environment": "🔍",
            "install_dependencies": "📦",
            "initialize_brain": "🧠",
            "configure_agents": "🤖",
            "setup_integrations": "🔗",
            "validate_installation": "✅"
        }
        icon = icons.get(self.step_id, "▶️")
        return f"{icon} {self.name}"
    
    def get_info(self) -> Dict[str, Any]:
        """Get step information"""
        return {
            "step_id": self.step_id,
            "name": self.name,
            "description": self.description,
            "display_format": self.display_format.value,
            "estimated_duration": self.estimated_duration,
            "skippable": self.skippable,
            "required_for_profiles": self.required_for_profiles,
            "dependencies": self.dependencies,
            "status": self.status.value
        }
    
    def reset(self) -> None:
        """Reset step state for re-execution"""
        self.status = StepStatus.PENDING
        self.start_time = None
        self.end_time = None
        self.result = None
