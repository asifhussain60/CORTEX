"""
CORTEX Phase Tracker Plugin

Extensible phase tracking system for work planning, multi-track development,
and progress monitoring.

Architecture:
- Tracks work phases with dependencies, estimates, and acceptance criteria
- Supports multi-track development (parallel work on multiple machines)
- Integrates with Work Planner, Design Sync, Conversation Vault
- YAML-based persistence with JSON Schema validation

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import os
import yaml
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
import logging

from .base_plugin import (
    BasePlugin,
    PluginMetadata,
    PluginCategory,
    PluginPriority,
    HookPoint
)
from .command_registry import CommandMetadata, CommandCategory

logger = logging.getLogger(__name__)


class PhaseTrackerPlugin(BasePlugin):
    """
    Phase tracking plugin for CORTEX workflow management.
    
    Features:
    - Create and manage phase tracking for projects
    - Track progress, blockers, time estimates
    - Support multi-track development
    - Integration with CORTEX agents and operations
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize phase tracker plugin."""
        super().__init__(config)
        
        # Storage paths
        self.cortex_root = Path(os.environ.get("CORTEX_ROOT", Path.cwd()))
        self.tracking_dir = self.cortex_root / "cortex-brain" / "documents" / "tracking"
        self.tracking_dir.mkdir(parents=True, exist_ok=True)
        
        # In-memory cache
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_ttl = 300  # 5 minutes
    
    def _get_metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        return PluginMetadata(
            plugin_id="phase_tracker",
            name="CORTEX Phase Tracker",
            version="1.0.0",
            category=PluginCategory.WORKFLOW,
            priority=PluginPriority.HIGH,
            description="Extensible phase tracking for work planning and multi-track development",
            author="Asif Hussain",
            dependencies=["yaml", "jsonschema"],
            hooks=[
                HookPoint.ON_WORKFLOW_START.value,
                HookPoint.ON_WORKFLOW_END.value,
                HookPoint.ON_BRAIN_UPDATE.value
            ],
            natural_language_patterns=[
                "track progress",
                "show phase status",
                "initialize phase tracking",
                "mark phase complete",
                "update task status"
            ]
        )
    
    def register_commands(self) -> List[CommandMetadata]:
        """Register plugin commands."""
        return [
            CommandMetadata(
                command="/track",
                natural_language_equivalent="track progress",
                plugin_id=self.metadata.plugin_id,
                description="Create or update phase tracking for current work",
                category=CommandCategory.WORKFLOW,
                aliases=["/progress", "/phases"],
                examples=[
                    "@cortex /track",
                    "track progress on implementation"
                ]
            ),
            CommandMetadata(
                command="/track-status",
                natural_language_equivalent="show phase status",
                plugin_id=self.metadata.plugin_id,
                description="Display current phase tracking status",
                category=CommandCategory.WORKFLOW,
                aliases=["/phases-status"],
                examples=[
                    "@cortex /track-status",
                    "show phase status"
                ]
            ),
            CommandMetadata(
                command="/track-init",
                natural_language_equivalent="initialize phase tracking",
                plugin_id=self.metadata.plugin_id,
                description="Set up new phase tracking for a project",
                category=CommandCategory.WORKFLOW,
                examples=[
                    "@cortex /track-init authentication feature",
                    "initialize phase tracking for new dashboard"
                ]
            )
        ]
    
    def initialize(self) -> bool:
        """Initialize plugin resources."""
        try:
            # Verify tracking directory exists
            if not self.tracking_dir.exists():
                self.logger.error(f"Tracking directory not found: {self.tracking_dir}")
                return False
            
            # Verify dependencies
            try:
                import yaml
                import jsonschema
            except ImportError as e:
                self.logger.error(f"Missing dependency: {e}")
                return False
            
            self.logger.info("Phase Tracker plugin initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Phase Tracker plugin: {e}")
            return False
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute phase tracking operation.
        
        Args:
            context: Execution context
                - action: "create", "update", "status", "complete"
                - project_name: Name of project
                - Additional context-specific parameters
        
        Returns:
            Execution results
        """
        action = context.get("action", "status")
        
        try:
            if action == "create":
                return self._create_tracking(context)
            elif action == "update":
                return self._update_tracking(context)
            elif action == "status":
                return self._get_status(context)
            elif action == "complete":
                return self._mark_complete(context)
            else:
                return {
                    "success": False,
                    "error": f"Unknown action: {action}"
                }
        
        except Exception as e:
            self.logger.error(f"Error executing phase tracker: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def cleanup(self) -> bool:
        """Cleanup plugin resources."""
        try:
            # Clear cache
            self._cache.clear()
            self.logger.info("Phase Tracker plugin cleaned up successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error cleaning up Phase Tracker plugin: {e}")
            return False
    
    # ========================================================================
    # Phase Tracking Methods
    # ========================================================================
    
    def create_tracking(
        self,
        project_name: str,
        description: str,
        phases: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create new phase tracking file.
        
        Args:
            project_name: Name of project
            description: Project description
            phases: List of phase definitions
            metadata: Optional metadata
        
        Returns:
            Tracking ID (filename without extension)
        """
        # Generate tracking ID
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        project_slug = project_name.lower().replace(" ", "-")
        tracking_id = f"{project_slug}-{timestamp}"
        
        # Create tracking structure
        tracking = {
            "version": "1.0",
            "project": {
                "name": project_name,
                "description": description,
                "started": datetime.now().isoformat(),
                "target_completion": None,
                "tags": metadata.get("tags", []) if metadata else []
            },
            "phases": phases,
            "metadata": metadata or {}
        }
        
        # Save to file
        tracking_file = self.tracking_dir / f"{tracking_id}.yaml"
        with open(tracking_file, "w") as f:
            yaml.dump(tracking, f, default_flow_style=False, sort_keys=False)
        
        self.logger.info(f"Created phase tracking: {tracking_id}")
        return tracking_id
    
    def update_phase_status(
        self,
        tracking_id: str,
        phase_id: str,
        status: str,
        notes: Optional[str] = None
    ) -> bool:
        """
        Update phase status.
        
        Args:
            tracking_id: Tracking file ID
            phase_id: Phase ID to update
            status: New status
            notes: Optional notes
        
        Returns:
            True if successful
        """
        tracking = self._load_tracking(tracking_id)
        if not tracking:
            return False
        
        # Find and update phase
        for phase in tracking.get("phases", []):
            if phase.get("phase_id") == phase_id:
                phase["status"] = status
                
                if status == "in-progress" and not phase.get("started"):
                    phase["started"] = datetime.now().isoformat()
                elif status == "completed" and not phase.get("completed"):
                    phase["completed"] = datetime.now().isoformat()
                
                if notes:
                    phase["notes"] = notes
                
                # Save updated tracking
                self._save_tracking(tracking_id, tracking)
                return True
        
        return False
    
    def get_status(self, tracking_id: str) -> Dict[str, Any]:
        """
        Get phase tracking status.
        
        Args:
            tracking_id: Tracking file ID
        
        Returns:
            Status information
        """
        tracking = self._load_tracking(tracking_id)
        if not tracking:
            return {
                "success": False,
                "error": f"Tracking not found: {tracking_id}"
            }
        
        phases = tracking.get("phases", [])
        total_phases = len(phases)
        completed_phases = sum(1 for p in phases if p.get("status") == "completed")
        
        return {
            "success": True,
            "tracking_id": tracking_id,
            "project": tracking.get("project", {}),
            "progress": {
                "total_phases": total_phases,
                "completed_phases": completed_phases,
                "percentage": round((completed_phases / total_phases * 100) if total_phases > 0 else 0, 1)
            },
            "phases": phases
        }
    
    def validate_dependencies(self, phases: List[Dict[str, Any]]) -> List[str]:
        """
        Validate phase dependencies.
        
        Args:
            phases: List of phases
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        phase_ids = {p.get("phase_id") for p in phases}
        
        for phase in phases:
            phase_id = phase.get("phase_id")
            dependencies = phase.get("dependencies", [])
            
            # Check dependencies exist
            for dep in dependencies:
                if dep not in phase_ids:
                    errors.append(
                        f"Phase {phase_id} depends on non-existent phase: {dep}"
                    )
        
        return errors
    
    def calculate_completion_percentage(self, phases: List[Dict[str, Any]]) -> float:
        """
        Calculate overall completion percentage.
        
        Args:
            phases: List of phases
        
        Returns:
            Completion percentage (0-100)
        """
        if not phases:
            return 0.0
        
        completed = sum(1 for p in phases if p.get("status") == "completed")
        return round((completed / len(phases)) * 100, 1)
    
    def detect_blockers(self, phases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detect active blockers across phases.
        
        Args:
            phases: List of phases
        
        Returns:
            List of active blockers
        """
        blockers = []
        
        for phase in phases:
            phase_blockers = phase.get("blockers", [])
            for blocker in phase_blockers:
                if not blocker.get("resolved"):
                    blockers.append({
                        "phase_id": phase.get("phase_id"),
                        "phase_name": phase.get("name"),
                        "blocker": blocker
                    })
        
        return blockers
    
    # ========================================================================
    # Private Helper Methods
    # ========================================================================
    
    def _create_tracking(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create tracking from context."""
        project_name = context.get("project_name")
        description = context.get("description", "")
        phases = context.get("phases", [])
        metadata = context.get("metadata", {})
        
        if not project_name:
            return {
                "success": False,
                "error": "project_name required"
            }
        
        tracking_id = self.create_tracking(
            project_name=project_name,
            description=description,
            phases=phases,
            metadata=metadata
        )
        
        return {
            "success": True,
            "tracking_id": tracking_id,
            "file": str(self.tracking_dir / f"{tracking_id}.yaml")
        }
    
    def _update_tracking(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Update tracking from context."""
        tracking_id = context.get("tracking_id")
        phase_id = context.get("phase_id")
        status = context.get("status")
        notes = context.get("notes")
        
        if not all([tracking_id, phase_id, status]):
            return {
                "success": False,
                "error": "tracking_id, phase_id, and status required"
            }
        
        success = self.update_phase_status(
            tracking_id=tracking_id,
            phase_id=phase_id,
            status=status,
            notes=notes
        )
        
        return {
            "success": success,
            "tracking_id": tracking_id,
            "phase_id": phase_id
        }
    
    def _get_status(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get status from context."""
        tracking_id = context.get("tracking_id")
        
        if not tracking_id:
            # Find most recent tracking
            tracking_files = sorted(self.tracking_dir.glob("*.yaml"), reverse=True)
            if tracking_files:
                tracking_id = tracking_files[0].stem
            else:
                return {
                    "success": False,
                    "error": "No tracking files found"
                }
        
        return self.get_status(tracking_id)
    
    def _mark_complete(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Mark phase complete from context."""
        tracking_id = context.get("tracking_id")
        phase_id = context.get("phase_id")
        
        if not all([tracking_id, phase_id]):
            return {
                "success": False,
                "error": "tracking_id and phase_id required"
            }
        
        success = self.update_phase_status(
            tracking_id=tracking_id,
            phase_id=phase_id,
            status="completed"
        )
        
        return {
            "success": success,
            "tracking_id": tracking_id,
            "phase_id": phase_id,
            "status": "completed"
        }
    
    def _load_tracking(self, tracking_id: str) -> Optional[Dict[str, Any]]:
        """Load tracking from file."""
        tracking_file = self.tracking_dir / f"{tracking_id}.yaml"
        
        if not tracking_file.exists():
            self.logger.warning(f"Tracking file not found: {tracking_id}")
            return None
        
        try:
            with open(tracking_file, "r") as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.error(f"Error loading tracking {tracking_id}: {e}")
            return None
    
    def _save_tracking(self, tracking_id: str, tracking: Dict[str, Any]) -> bool:
        """Save tracking to file."""
        tracking_file = self.tracking_dir / f"{tracking_id}.yaml"
        
        try:
            with open(tracking_file, "w") as f:
                yaml.dump(tracking, f, default_flow_style=False, sort_keys=False)
            
            # Invalidate cache
            if tracking_id in self._cache:
                del self._cache[tracking_id]
            
            return True
        except Exception as e:
            self.logger.error(f"Error saving tracking {tracking_id}: {e}")
            return False


def register() -> BasePlugin:
    """Register plugin with CORTEX."""
    return PhaseTrackerPlugin()
