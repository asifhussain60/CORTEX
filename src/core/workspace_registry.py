"""
Workspace Registry for CORTEX 4.0 Phase 11

Central registry of all known workspaces with automatic discovery and persistence.
Enables one CORTEX installation to serve multiple user repositories.

Author: Asif Hussain
Copyright: © 2025 Asif Hussain. All rights reserved.
Version: 1.0.0
"""

import os
import uuid
import yaml
import logging
from pathlib import Path
from typing import Optional, Dict, List
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

from src.core.workspace_detector import WorkspaceInfo, WorkspaceDetector

logger = logging.getLogger(__name__)


class WorkspaceStatus(Enum):
    """Status of workspace initialization."""
    ACTIVE = "active"  # Fully initialized
    PENDING = "pending"  # Discovered but not initialized
    ARCHIVED = "archived"  # No longer active


@dataclass
class RegisteredWorkspace:
    """Registered workspace with metadata."""
    workspace_id: str  # UUID v4
    path: str  # Absolute path
    name: str  # Display name
    project_type: str  # python, csharp, etc.
    status: WorkspaceStatus
    first_seen: str  # ISO timestamp
    last_accessed: str  # ISO timestamp
    cortex_min_version: Optional[str] = None  # Min CORTEX version required
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for YAML serialization."""
        data = asdict(self)
        data['status'] = self.status.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'RegisteredWorkspace':
        """Create from dictionary loaded from YAML."""
        data['status'] = WorkspaceStatus(data['status'])
        return cls(**data)


class WorkspaceRegistry:
    """
    Central registry of all workspaces known to CORTEX.
    
    Features:
    - Auto-discovery of workspaces on first access
    - Persistent storage in cortex-brain/config/workspace-registry.yaml
    - UUID generation for new workspaces
    - Last accessed tracking
    - Version compatibility checking
    
    Usage:
        registry = WorkspaceRegistry()
        
        # Register current workspace
        workspace = registry.register_current_workspace()
        
        # Get all workspaces
        all_workspaces = registry.list_workspaces()
        
        # Find workspace by path
        workspace = registry.get_by_path("/path/to/repo")
    """
    
    def __init__(self, cortex_root: Optional[Path] = None):
        """
        Initialize workspace registry.
        
        Args:
            cortex_root: Path to CORTEX installation (auto-detected if None)
        """
        self.cortex_root = cortex_root or self._find_cortex_root()
        self.registry_file = self.cortex_root / "cortex-brain" / "config" / "workspace-registry.yaml"
        self.workspaces: Dict[str, RegisteredWorkspace] = {}
        self._load_registry()
    
    def register_current_workspace(self) -> RegisteredWorkspace:
        """
        Register the currently active workspace.
        
        Returns:
            RegisteredWorkspace with UUID and metadata
        """
        detector = WorkspaceDetector(self.cortex_root)
        workspace_info = detector.detect_active_workspace()
        
        return self.register_workspace(workspace_info)
    
    def register_workspace(self, workspace_info: WorkspaceInfo) -> RegisteredWorkspace:
        """
        Register a workspace in the registry.
        
        Args:
            workspace_info: Detected workspace information
            
        Returns:
            RegisteredWorkspace with UUID assigned
        """
        workspace_path = str(workspace_info.path)
        
        # Check if already registered
        existing = self.get_by_path(workspace_path)
        if existing:
            # Update last accessed
            existing.last_accessed = datetime.now().isoformat()
            self._save_registry()
            logger.debug(f"Updated last_accessed for workspace: {existing.name}")
            return existing
        
        # Generate new UUID
        workspace_uuid = str(uuid.uuid4())
        
        # Create .cortex directory if needed
        cortex_dir = workspace_info.path / ".cortex"
        cortex_dir.mkdir(exist_ok=True)
        
        # Write workspace ID file
        workspace_id_file = cortex_dir / "workspace-id.txt"
        workspace_id_file.write_text(workspace_uuid)
        
        # Write config pointing to CORTEX installation
        config_file = cortex_dir / "config.json"
        if not config_file.exists():
            import json
            config_data = {
                "cortex_installation": str(self.cortex_root),
                "workspace_id": workspace_uuid,
                "created": datetime.now().isoformat()
            }
            config_file.write_text(json.dumps(config_data, indent=2))
        
        # Create registered workspace entry
        now = datetime.now().isoformat()
        registered = RegisteredWorkspace(
            workspace_id=workspace_uuid,
            path=workspace_path,
            name=workspace_info.name,
            project_type=workspace_info.project_type,
            status=WorkspaceStatus.ACTIVE,
            first_seen=now,
            last_accessed=now
        )
        
        self.workspaces[workspace_uuid] = registered
        self._save_registry()
        
        logger.info(f"Registered new workspace: {registered.name} ({workspace_uuid})")
        return registered
    
    def get_by_path(self, path: str) -> Optional[RegisteredWorkspace]:
        """
        Get workspace by path.
        
        Args:
            path: Absolute path to workspace
            
        Returns:
            RegisteredWorkspace or None
        """
        normalized_path = str(Path(path).resolve())
        for workspace in self.workspaces.values():
            if Path(workspace.path).resolve() == Path(normalized_path):
                return workspace
        return None
    
    def get_by_id(self, workspace_id: str) -> Optional[RegisteredWorkspace]:
        """
        Get workspace by UUID.
        
        Args:
            workspace_id: Workspace UUID
            
        Returns:
            RegisteredWorkspace or None
        """
        return self.workspaces.get(workspace_id)
    
    def list_workspaces(self, status: Optional[WorkspaceStatus] = None) -> List[RegisteredWorkspace]:
        """
        List all registered workspaces.
        
        Args:
            status: Filter by status (None = all)
            
        Returns:
            List of RegisteredWorkspace
        """
        workspaces = list(self.workspaces.values())
        if status:
            workspaces = [w for w in workspaces if w.status == status]
        
        # Sort by last accessed (most recent first)
        workspaces.sort(key=lambda w: w.last_accessed, reverse=True)
        return workspaces
    
    def archive_workspace(self, workspace_id: str) -> bool:
        """
        Mark workspace as archived (no longer active).
        
        Args:
            workspace_id: Workspace UUID
            
        Returns:
            True if archived, False if not found
        """
        workspace = self.get_by_id(workspace_id)
        if workspace:
            workspace.status = WorkspaceStatus.ARCHIVED
            self._save_registry()
            logger.info(f"Archived workspace: {workspace.name}")
            return True
        return False
    
    def auto_discover_workspace(self, workspace_path: Path) -> Optional[WorkspaceInfo]:
        """
        Discover and register a single workspace.
        
        Args:
            workspace_path: Path to workspace to discover and register
            
        Returns:
            WorkspaceInfo if successful, None otherwise
        """
        try:
            detector = WorkspaceDetector(self.cortex_root)
            workspace_info = detector.detect_workspace(workspace_path)
            
            if workspace_info:
                # Register the workspace
                self.register_workspace(workspace_info)
                return workspace_info
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to discover workspace at {workspace_path}: {e}")
            return None
    
    def auto_discover_workspaces(self, search_paths: List[Path]) -> int:
        """
        Auto-discover workspaces in given paths.
        
        Args:
            search_paths: List of directories to search
            
        Returns:
            Number of new workspaces discovered
        """
        discovered = 0
        detector = WorkspaceDetector(self.cortex_root)
        
        for search_path in search_paths:
            if not search_path.exists():
                continue
            
            # Look for workspace markers
            for candidate in search_path.iterdir():
                if not candidate.is_dir():
                    continue
                
                # Check if it looks like a workspace
                has_git = (candidate / ".git").exists()
                has_cortex = (candidate / ".cortex").exists()
                has_project = self._has_project_markers(candidate)
                
                if has_cortex or (has_git and has_project):
                    # Check if already registered
                    if not self.get_by_path(str(candidate)):
                        try:
                            # Build workspace info manually
                            from src.core.workspace_detector import WorkspaceInfo, WorkspaceDetectionMethod
                            from src.core.ide_detector import IDEType
                            
                            workspace_info = WorkspaceInfo(
                                workspace_id=f"pending-{candidate.name}",
                                path=candidate,
                                name=candidate.name,
                                project_type=detector._detect_project_type(candidate),
                                ide_type=IDEType.UNKNOWN,
                                detection_method=WorkspaceDetectionMethod.CWD_SEARCH
                            )
                            
                            self.register_workspace(workspace_info)
                            discovered += 1
                        except Exception as e:
                            logger.debug(f"Failed to register {candidate.name}: {e}")
        
        if discovered > 0:
            logger.info(f"Auto-discovered {discovered} new workspaces")
        
        return discovered
    
    def _has_project_markers(self, path: Path) -> bool:
        """Check if directory has project markers."""
        markers = [
            "pyproject.toml", "setup.py", "requirements.txt",
            "package.json", "*.sln", "*.csproj",
            "Cargo.toml", "go.mod", "pom.xml"
        ]
        
        for marker in markers:
            if "*" in marker:
                if list(path.glob(marker)):
                    return True
            elif (path / marker).exists():
                return True
        
        return False
    
    def _load_registry(self):
        """Load registry from YAML file."""
        if not self.registry_file.exists():
            logger.debug("No existing registry found - creating new")
            self._ensure_config_directory()
            return
        
        try:
            with open(self.registry_file, 'r') as f:
                data = yaml.safe_load(f) or {}
            
            workspaces_data = data.get('workspaces', {})
            self.workspaces = {
                ws_id: RegisteredWorkspace.from_dict(ws_data)
                for ws_id, ws_data in workspaces_data.items()
            }
            
            logger.debug(f"Loaded {len(self.workspaces)} workspaces from registry")
            
        except Exception as e:
            logger.error(f"Failed to load registry: {e}")
            self.workspaces = {}
    
    def _save_registry(self):
        """Save registry to YAML file."""
        self._ensure_config_directory()
        
        data = {
            'version': '1.0',
            'cortex_root': str(self.cortex_root),
            'updated': datetime.now().isoformat(),
            'workspaces': {
                ws_id: workspace.to_dict()
                for ws_id, workspace in self.workspaces.items()
            }
        }
        
        try:
            with open(self.registry_file, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.debug(f"Saved registry with {len(self.workspaces)} workspaces")
            
        except Exception as e:
            logger.error(f"Failed to save registry: {e}")
    
    def _ensure_config_directory(self):
        """Ensure config directory exists."""
        self.registry_file.parent.mkdir(parents=True, exist_ok=True)
    
    def _find_cortex_root(self) -> Path:
        """Find CORTEX installation root."""
        current = Path(__file__).parent
        
        while current != current.parent:
            if (current / "cortex-brain").exists():
                return current
            current = current.parent
        
        raise RuntimeError("CORTEX installation not found")


# Global registry instance
_registry: Optional[WorkspaceRegistry] = None


def get_workspace_registry() -> WorkspaceRegistry:
    """
    Get global workspace registry instance.
    
    Usage:
        from src.core.workspace_registry import get_workspace_registry
        
        registry = get_workspace_registry()
        workspace = registry.register_current_workspace()
    """
    global _registry
    
    if _registry is None:
        _registry = WorkspaceRegistry()
    
    return _registry
