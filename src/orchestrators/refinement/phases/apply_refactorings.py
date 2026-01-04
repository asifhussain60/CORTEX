"""
Phase 6: Apply Refactorings

Applies automated refactorings and generates manual refactoring checklist.

Author: Asif Hussain
Created: January 3, 2026
"""

import logging
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class ApplyRefactoringsPhase:
    """Phase 6: Apply automated refactorings."""
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.target_path = orchestrator.target_path
    
    def execute(self, auto_apply: bool = False) -> Dict[str, Any]:
        """
        Execute refactoring application.
        
        Args:
            auto_apply: If True, automatically applies safe refactorings
            
        Returns:
            Dictionary containing applied refactorings and manual checklist
        """
        logger.info(f"Phase 6: Applying refactorings (auto_apply={auto_apply})")
        
        results = {
            "auto_applied": [],
            "manual_checklist": [],
            "git_checkpoint": None,
            "applied_count": 0,
            "manual_count": 0
        }
        
        try:
            # Create git checkpoint
            if auto_apply:
                results["git_checkpoint"] = self._create_git_checkpoint()
            
            # Get refactoring plan
            phase_results = self.orchestrator.state.get("results", {})
            refactoring_plan = phase_results.get("RefactoringPlan", {})
            tasks = refactoring_plan.get("refactoring_tasks", [])
            
            for task in tasks:
                if auto_apply and self._is_safe_automation(task):
                    # Apply automated refactoring
                    result = self._apply_automated_refactoring(task)
                    if result["success"]:
                        results["auto_applied"].append(result)
                        results["applied_count"] += 1
                else:
                    # Add to manual checklist
                    checklist_item = self._create_checklist_item(task)
                    results["manual_checklist"].append(checklist_item)
                    results["manual_count"] += 1
            
            logger.info(f"Refactoring application complete: {results['applied_count']} automated, "
                       f"{results['manual_count']} manual")
            
        except Exception as e:
            logger.error(f"Refactoring application failed: {e}", exc_info=True)
            results["error"] = str(e)
        
        return results
    
    def _create_git_checkpoint(self) -> str:
        """Create git checkpoint before applying changes."""
        try:
            checkpoint_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            branch_name = f"refinement-checkpoint-{checkpoint_id}"
            
            subprocess.run(
                ["git", "checkout", "-b", branch_name],
                capture_output=True,
                check=True,
                cwd=self.target_path.parent
            )
            
            logger.info(f"Created git checkpoint: {branch_name}")
            return branch_name
            
        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to create git checkpoint: {e}")
            return "no-checkpoint"
    
    def _is_safe_automation(self, task: Dict[str, Any]) -> bool:
        """Determine if task can be safely automated."""
        # Only automate low-risk tasks
        safe_types = ["quality"]  # Quality fixes with formatters
        safe_priorities = ["low", "medium"]
        
        task_type = task.get("type", "")
        priority = task.get("priority", "high")
        
        return task_type in safe_types and priority in safe_priorities
    
    def _apply_automated_refactoring(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Apply an automated refactoring."""
        result = {
            "task_id": task.get("id"),
            "title": task.get("title"),
            "success": False,
            "changes": []
        }
        
        try:
            task_type = task.get("type")
            
            if task_type == "quality":
                # Apply formatting and linting fixes
                file_path = task.get("file")
                if file_path:
                    changes = self._apply_quality_fixes(Path(file_path))
                    result["changes"] = changes
                    result["success"] = True
            
            logger.info(f"Applied automated refactoring: {task.get('id')}")
            
        except Exception as e:
            logger.error(f"Failed to apply refactoring {task.get('id')}: {e}")
            result["error"] = str(e)
        
        return result
    
    def _apply_quality_fixes(self, file_path: Path) -> List[str]:
        """Apply quality fixes to a file."""
        changes = []
        
        try:
            # Run black formatter
            result = subprocess.run(
                ["black", str(file_path)],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                changes.append("Applied black formatter")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        try:
            # Run isort for import sorting
            result = subprocess.run(
                ["isort", str(file_path)],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                changes.append("Sorted imports with isort")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        return changes
    
    def _create_checklist_item(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Create manual refactoring checklist item."""
        return {
            "id": task.get("id"),
            "title": task.get("title"),
            "type": task.get("type"),
            "priority": task.get("priority"),
            "description": task.get("description"),
            "estimated_hours": task.get("effort_hours", 1),
            "steps": task.get("steps", []),
            "files": task.get("files", [task.get("file")] if task.get("file") else []),
            "status": "pending"
        }
