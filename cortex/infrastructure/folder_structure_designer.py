"""Folder Structure Designer.

Provides folder structure planning and design for project organization.

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass
class FolderNode:
    """Represents a folder in the structure.
    
    Attributes:
        name: Folder name.
        path: Full path to folder.
        purpose: Purpose/description of the folder.
        parent: Parent folder path.
        child_folders: List of child folder names.
    """
    name: str
    path: str
    purpose: str
    parent: Optional[str] = None
    child_folders: List[str] = field(default_factory=list)


class FolderStructureDesigner:
    """Designer for nested folder structures.
    
    Organizes code by domain and responsibility with clear
    separation of concerns.
    """
    
    def __init__(self) -> None:
        """Initialize the folder structure designer."""
        self.structure: Dict[str, FolderNode] = {}
        self.organization_rationale: Dict[str, str] = {}
    
    def add_folder(
        self,
        name: str,
        path: str,
        purpose: str,
        parent: Optional[str] = None,
    ) -> None:
        """Add a folder to the structure.
        
        Args:
            name: Folder name.
            path: Full path to folder.
            purpose: Purpose/description.
            parent: Optional parent folder path.
        """
        node = FolderNode(
            name=name,
            path=path,
            purpose=purpose,
            parent=parent,
        )
        self.structure[path] = node
        
        # Update parent's children if parent exists
        if parent and parent in self.structure:
            self.structure[parent].child_folders.append(name)
    
    def get_depth(self, path: str) -> int:
        """Get the depth of a folder path.
        
        Args:
            path: Folder path.
            
        Returns:
            Depth level (0 for root).
        """
        return path.count('/')
    
    def validate_uniqueness(self) -> bool:
        """Validate that all paths are unique.
        
        Returns:
            True if all paths unique.
        """
        paths = list(self.structure.keys())
        return len(paths) == len(set(paths))
    
    def validate_coverage(self, required: List[str]) -> bool:
        """Validate that all required folders are present.
        
        Args:
            required: List of required folder paths.
            
        Returns:
            True if all required folders present.
        """
        return all(r in self.structure for r in required)
    
    def add_rationale(self, folder: str, rationale: str) -> None:
        """Add organization rationale for a folder.
        
        Args:
            folder: Folder path.
            rationale: Rationale text.
        """
        self.organization_rationale[folder] = rationale
    
    def validate_rationale_complete(self) -> bool:
        """Validate that all folders have documented rationale.
        
        Returns:
            True if all folders have rationale.
        """
        return all(path in self.organization_rationale for path in self.structure)
    
    def get_all_paths(self) -> List[str]:
        """Get all folder paths in the structure.
        
        Returns:
            List of all folder paths.
        """
        return list(self.structure.keys())
    
    def create_migration_plan(self) -> Dict[str, Any]:
        """Create a migration plan for the folder structure.
        
        Creates a phased migration plan with validation steps
        and rollback strategy.
        
        Returns:
            Dictionary with phases, validation_steps, and rollback_strategy.
        """
        # Build phases - one phase per depth level
        phases: List[Dict[str, Any]] = []
        paths_by_depth: Dict[int, List[str]] = {}
        
        for path in self.structure:
            depth = self.get_depth(path)
            if depth not in paths_by_depth:
                paths_by_depth[depth] = []
            paths_by_depth[depth].append(path)
        
        # Create phases by depth
        for depth in sorted(paths_by_depth.keys()):
            phase = {
                "phase": depth + 1,
                "name": f"Level {depth} folders",
                "folders": paths_by_depth[depth],
                "description": f"Create depth-{depth} folders"
            }
            phases.append(phase)
        
        # Validation steps
        validation_steps = [
            "Verify all folders created",
            "Run import validation tests",
            "Execute unit test suite",
            "Check file permissions",
            "Validate folder structure integrity"
        ]
        
        # Rollback strategy
        rollback_strategy = [
            "Revert folder creation in reverse phase order",
            "Restore original file locations from backup",
            "Reset import paths to original",
            "Verify system stability after rollback"
        ]
        
        return {
            "phases": phases,
            "validation_steps": validation_steps,
            "rollback_strategy": rollback_strategy,
            "total_folders": len(self.structure),
            "documented_folders": len(self.organization_rationale)
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert structure to dictionary.
        
        Returns:
            Dictionary representation.
        """
        return {
            "structure": {
                path: {
                    "name": node.name,
                    "purpose": node.purpose,
                    "parent": node.parent,
                    "children": node.child_folders,
                }
                for path, node in self.structure.items()
            },
            "rationale": self.organization_rationale,
        }


class Structure:
    """Structure container for folder design."""
    
    def __init__(self) -> None:
        """Initialize structure."""
        self.data: Dict[str, Any] = {}


__all__ = ['FolderStructureDesigner', 'FolderNode', 'Structure']