"""
Nested Folder Structure Planning & Design Implementation.

Provides the FolderStructureDesigner class that designs and validates
a comprehensive nested folder structure for the CORTEX project.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass
class FolderNode:
    """Represents a folder in the nested structure."""
    name: str
    path: str
    purpose: str
    parent: Optional[str] = None
    child_folders: List[str] = field(default_factory=list)
    files: List[str] = field(default_factory=list)


class FolderStructureDesigner:
    """Designs and validates nested folder structure for projects."""
    
    def __init__(self):
        """Initialize the folder structure designer."""
        self.structure: Dict[str, FolderNode] = {}
        self.organization_rationale: Dict[str, str] = {}
    
    def add_folder(
        self,
        name: str,
        path: str,
        purpose: str,
        parent: Optional[str] = None
    ) -> FolderNode:
        """
        Add a folder node to the structure.
        
        Args:
            name: Folder name
            path: Full path to folder
            purpose: Purpose of this folder
            parent: Path to parent folder (optional)
            
        Returns:
            The created FolderNode
        """
        node = FolderNode(name=name, path=path, purpose=purpose, parent=parent)
        self.structure[path] = node
        
        if parent and parent in self.structure:
            self.structure[parent].child_folders.append(name)
        
        return node
    
    def add_rationale(self, folder_path: str, rationale: str) -> None:
        """
        Document the organization rationale for a folder.
        
        Args:
            folder_path: Path to the folder
            rationale: Description of why this folder is organized this way
        """
        self.organization_rationale[folder_path] = rationale
    
    def get_depth(self, folder_path: str) -> int:
        """
        Get the depth of a folder in the hierarchy.
        
        Args:
            folder_path: Path to the folder
            
        Returns:
            Number of levels deep (1 for root, 2 for root/sub, etc.)
        """
        return folder_path.count('/')
    
    def get_all_paths(self) -> List[str]:
        """
        Get all folder paths in the structure.
        
        Returns:
            List of all folder paths
        """
        return list(self.structure.keys())
    
    def validate_uniqueness(self) -> bool:
        """
        Validate that all folder paths are unique.
        
        Returns:
            True if all paths are unique, False otherwise
        """
        paths = list(self.structure.keys())
        return len(paths) == len(set(paths))
    
    def validate_coverage(self, required_folders: List[str]) -> bool:
        """
        Validate that all required folders are present.
        
        Args:
            required_folders: List of folder paths that must exist
            
        Returns:
            True if all required folders exist, False otherwise
        """
        paths = set(self.structure.keys())
        return all(folder in paths for folder in required_folders)
    
    def validate_rationale_complete(self) -> bool:
        """
        Validate that all folders have documented rationale.
        
        Returns:
            True if all folders have rationale, False otherwise
        """
        return len(self.organization_rationale) == len(self.structure)
    
    def create_migration_plan(self) -> Dict[str, Any]:
        """
        Create a comprehensive migration plan from flat to nested structure.
        
        Returns:
            Dictionary containing migration plan with phases, validation steps,
            and rollback strategy
        """
        plan: Dict[str, Any] = {
            'phases': [],
            'source_folders': [],
            'target_structure': {},
            'validation_steps': [],
            'rollback_strategy': ''
        }
        
        # Build target structure
        for path, node in self.structure.items():
            plan['target_structure'][path] = {
                'purpose': node.purpose,
                'rationale': self.organization_rationale.get(path, ''),
                'files': node.files,
                'child_folders': node.child_folders
            }
        
        # Define migration phases (shallow to deep)
        sorted_paths = sorted(
            self.structure.keys(),
            key=lambda p: p.count('/')
        )
        for i, path in enumerate(sorted_paths):
            plan['phases'].append({
                'phase_num': i + 1,
                'folder': path,
                'action': 'Create' if i == 0 else 'Migrate'
            })
        
        # Define validation steps
        plan['validation_steps'] = [
            'Verify no files lost during migration',
            'Check all imports resolve correctly',
            'Run full test suite',
            'Verify documentation updates'
        ]
        
        plan['rollback_strategy'] = (
            'Keep original flat structure in git history for 30 days'
        )
        
        return plan
