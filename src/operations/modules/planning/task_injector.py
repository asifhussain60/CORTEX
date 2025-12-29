"""
Task Injector - Standard Task Auto-Injection for Worker Plans

Automatically injects standard tasks into all worker plans:
- Git checkpoints (start/end of phase)
- AST/Lens analysis
- Documentation updates
- TDD validation
- DoD validation

Author: Asif Hussain
Date: December 17, 2025
Version: 1.0.0
"""

import logging
from typing import List, Dict, Any
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class StandardTask:
    """Standard task definition."""
    task_id: str
    title: str
    description: str
    category: str  # git, analysis, documentation, tdd, dod
    position: str  # start, middle, end
    required: bool = True


class TaskInjector:
    """
    Injects standard tasks into worker plans.
    
    Ensures consistency across all plans with:
    - Git checkpoints for rollback capability
    - AST/Lens analysis for context
    - Documentation updates for synchronization
    - TDD validation for quality
    - DoD validation for completeness
    """
    
    # Standard tasks catalog
    STANDARD_TASKS = [
        # Git checkpoints
        StandardTask(
            task_id="GIT_CHECKPOINT_START",
            title="📌 Git Checkpoint - Phase Start",
            description="Create git checkpoint before phase work begins (enable rollback)",
            category="git",
            position="start",
            required=True
        ),
        StandardTask(
            task_id="GIT_CHECKPOINT_END",
            title="📌 Git Checkpoint - Phase Complete",
            description="Create git checkpoint after phase work complete (track progress)",
            category="git",
            position="end",
            required=True
        ),
        
        # Analysis
        StandardTask(
            task_id="AST_LENS_ANALYSIS",
            title="🔍 AST/Lens Analysis",
            description="Run AST and Cortex Lens analysis to verify code structure and dependencies",
            category="analysis",
            position="middle",
            required=True
        ),
        
        # Documentation
        StandardTask(
            task_id="UPDATE_DOCUMENTATION",
            title="📝 Update Documentation",
            description="Update relevant documentation (README, API docs, code comments)",
            category="documentation",
            position="middle",
            required=True
        ),
        
        # TDD validation
        StandardTask(
            task_id="TDD_VALIDATION",
            title="✅ TDD Validation",
            description="Verify RED→GREEN→REFACTOR cycle completed for all new code",
            category="tdd",
            position="middle",
            required=True
        ),
        
        # DoD validation
        StandardTask(
            task_id="DOD_VALIDATION",
            title="🎯 DoD Validation",
            description="Validate all Definition of Done criteria met for this phase",
            category="dod",
            position="end",
            required=True
        )
    ]
    
    def __init__(self):
        """Initialize task injector."""
        logger.info("✅ TaskInjector initialized")
    
    def inject_standard_tasks(
        self,
        phase_tasks: List[Dict[str, Any]],
        phase_number: int,
        phase_name: str
    ) -> List[Dict[str, Any]]:
        """
        Inject standard tasks into phase task list.
        
        Args:
            phase_tasks: Existing phase tasks
            phase_number: Phase number (1-indexed)
            phase_name: Phase name
            
        Returns:
            Updated task list with standard tasks injected
        """
        injected_tasks = []
        
        # Start tasks (git checkpoint)
        for task in self.STANDARD_TASKS:
            if task.position == "start":
                injected_tasks.append(self._create_task_dict(task, phase_number, phase_name))
        
        # Middle tasks (analysis, docs, tdd)
        middle_tasks = []
        for task in self.STANDARD_TASKS:
            if task.position == "middle":
                middle_tasks.append(self._create_task_dict(task, phase_number, phase_name))
        
        # Insert middle tasks at appropriate positions
        if len(phase_tasks) > 0:
            # Insert analysis at start
            analysis_tasks = [t for t in middle_tasks if t["category"] == "analysis"]
            injected_tasks.extend(analysis_tasks)
            
            # Add original phase tasks
            injected_tasks.extend(phase_tasks)
            
            # Insert docs and TDD after phase tasks
            other_middle_tasks = [t for t in middle_tasks if t["category"] != "analysis"]
            injected_tasks.extend(other_middle_tasks)
        else:
            # No phase tasks, just add all middle tasks
            injected_tasks.extend(middle_tasks)
        
        # End tasks (git checkpoint, DoD)
        for task in self.STANDARD_TASKS:
            if task.position == "end":
                injected_tasks.append(self._create_task_dict(task, phase_number, phase_name))
        
        logger.info(f"✅ Injected {len(injected_tasks) - len(phase_tasks)} standard tasks into phase {phase_number}")
        
        return injected_tasks
    
    def _create_task_dict(
        self,
        task: StandardTask,
        phase_number: int,
        phase_name: str
    ) -> Dict[str, Any]:
        """
        Create task dictionary from standard task template.
        
        Args:
            task: Standard task definition
            phase_number: Phase number
            phase_name: Phase name
            
        Returns:
            Task dictionary for plan
        """
        return {
            "id": f"WP{phase_number:02d}-{task.task_id}",
            "title": task.title,
            "description": task.description,
            "category": task.category,
            "required": task.required,
            "standard_task": True,  # Mark as auto-injected
            "estimated": "15m" if task.category == "git" else "30m",
            "status": "pending"
        }
    
    def get_standard_task_checklist(
        self,
        phase_number: int
    ) -> List[str]:
        """
        Get markdown checklist of standard tasks for phase.
        
        Args:
            phase_number: Phase number
            
        Returns:
            List of markdown checkbox items
        """
        checklist = []
        
        for task in self.STANDARD_TASKS:
            checklist.append(f"- [ ] {task.title}: {task.description}")
        
        return checklist
    
    def validate_standard_tasks_present(
        self,
        phase_tasks: List[Dict[str, Any]]
    ) -> tuple[bool, List[str]]:
        """
        Validate that all required standard tasks are present.
        
        Args:
            phase_tasks: Phase task list
            
        Returns:
            Tuple of (all_present: bool, missing_tasks: List[str])
        """
        present_task_ids = {task.get("id", "") for task in phase_tasks}
        missing_tasks = []
        
        for standard_task in self.STANDARD_TASKS:
            if standard_task.required:
                # Check if any task ID contains the standard task ID
                if not any(standard_task.task_id in task_id for task_id in present_task_ids):
                    missing_tasks.append(standard_task.title)
        
        all_present = len(missing_tasks) == 0
        
        if not all_present:
            logger.warning(f"⚠️ Missing standard tasks: {', '.join(missing_tasks)}")
        
        return (all_present, missing_tasks)
