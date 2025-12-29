"""
Plan file organizer for status-based directory structure.

This module organizes plan files into status-specific directories and handles
auto-move operations when plan status changes.
"""

from pathlib import Path
from typing import Optional


class PlanOrganizerError(Exception):
    """Exception raised for plan organizer errors."""
    pass


class PlanOrganizer:
    """
    Organizes plan files into status-based directory structure.
    
    Directory structure:
        planning/features/active/     - in-progress plans
        planning/features/completed/  - completed plans
        planning/features/           - proposed/approved/cancelled plans
    """
    
    def __init__(self, brain_path: Path):
        """
        Initialize plan organizer.
        
        Args:
            brain_path: Path to cortex-brain directory
        """
        self.brain_path = Path(brain_path)
        self.planning_dir = self.brain_path / "documents" / "planning"
        self.features_dir = self.planning_dir / "features"
        
        # Create status directories
        self._init_directories()
    
    def _init_directories(self):
        """Create status-based directory structure."""
        (self.features_dir / "active").mkdir(parents=True, exist_ok=True)
        (self.features_dir / "completed").mkdir(parents=True, exist_ok=True)
    
    def move_to_status_dir(self, file_path: Path, new_status: str) -> Path:
        """
        Move plan file to appropriate status directory.
        
        Args:
            file_path: Current file path
            new_status: New plan status
            
        Returns:
            New file path after move
            
        Raises:
            PlanOrganizerError: If move fails
        """
        file_path = Path(file_path)
        
        # Determine target directory based on status
        if new_status == "in-progress":
            target_dir = self.features_dir / "active"
        elif new_status == "completed":
            target_dir = self.features_dir / "completed"
        else:
            # proposed, approved, cancelled stay in features/
            target_dir = self.features_dir
        
        # Handle filename collisions
        new_path = self._get_unique_path(target_dir, file_path.name)
        
        # Move file
        try:
            file_path.rename(new_path)
            return new_path
        except Exception as e:
            raise PlanOrganizerError(f"Failed to move {file_path} to {new_path}: {e}")
    
    def _get_unique_path(self, directory: Path, filename: str) -> Path:
        """
        Get unique file path, adding numeric suffix if needed.
        
        Args:
            directory: Target directory
            filename: Desired filename
            
        Returns:
            Unique file path
        """
        target = directory / filename
        
        if not target.exists():
            return target
        
        # Add numeric suffix
        stem = Path(filename).stem
        suffix = Path(filename).suffix
        counter = 1
        
        while True:
            new_name = f"{stem}-{counter}{suffix}"
            target = directory / new_name
            if not target.exists():
                return target
            counter += 1
    
    def update_registry_after_move(
        self,
        plan_id: str,
        new_path: Path,
        registry
    ) -> None:
        """
        Update plan registry with new file path after move.
        
        Args:
            plan_id: Plan identifier
            new_path: New file path
            registry: PlanRegistry instance
        """
        from src.workflows.plan_metadata import PlanMetadataExtractor
        
        # Extract metadata from new location
        extractor = PlanMetadataExtractor()
        metadata = extractor.extract(new_path)
        
        # Update registry (add_plan handles relative path conversion)
        registry.add_plan(metadata, new_path)
