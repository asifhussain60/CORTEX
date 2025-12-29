"""
Workspace Detection Utility for CORTEX 4.0 Phase 11

Provides cross-IDE workspace detection with automatic context switching.
Supports VSCode, Visual Studio 2019+, and graceful fallbacks.

Author: Asif Hussain
Copyright: © 2025 Asif Hussain. All rights reserved.
Version: 1.0.0
"""

import os
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum

from src.core.ide_detector import IDEDetector, IDEType

logger = logging.getLogger(__name__)


class WorkspaceDetectionMethod(Enum):
    """Method used to detect workspace."""
    VSCODE_API = "vscode_api"
    VISUAL_STUDIO_API = "visual_studio_api"
    COPILOT_CONTEXT = "copilot_context"
    CWD_SEARCH = "cwd_search"
    FALLBACK = "fallback"


@dataclass
class WorkspaceInfo:
    """Information about detected workspace."""
    workspace_id: str  # UUID from .cortex/workspace-id.txt
    path: Path  # Absolute path to workspace root
    name: str  # Human-readable name (directory name)
    project_type: str  # python, csharp, typescript, etc.
    ide_type: IDEType  # VSCode, Visual Studio, or Unknown
    detection_method: WorkspaceDetectionMethod
    active_file: Optional[Path] = None  # Currently active file in IDE


class WorkspaceDetector:
    """
    Cross-IDE workspace detector with automatic context switching.
    
    Detection Priority:
    1. VSCode API (if running in VSCode)
    2. Visual Studio API (if running in Visual Studio)
    3. GitHub Copilot Chat context
    4. Current working directory search
    5. Fallback to CORTEX directory
    
    Performance:
    - Detection: <200ms target
    - Caching: 5 minutes per workspace
    - Thread-safe: Uses global cache dictionary
    
    Usage:
        detector = WorkspaceDetector()
        workspace_info = detector.detect_active_workspace()
        print(f"Active workspace: {workspace_info.name}")
        print(f"Write files to: {workspace_info.path}")
    """
    
    # Cache: workspace_path -> (WorkspaceInfo, timestamp)
    _cache: Dict[str, tuple[WorkspaceInfo, float]] = {}
    _cache_ttl_seconds = 300  # 5 minutes
    
    def __init__(self, cortex_root: Optional[Path] = None):
        """
        Initialize workspace detector.
        
        Args:
            cortex_root: Path to CORTEX installation (auto-detected if None)
        """
        self.cortex_root = cortex_root or self._find_cortex_root()
        self.ide_type = IDEDetector.detect(self.cortex_root)
        logger.debug(f"WorkspaceDetector initialized: IDE={self.ide_type.value}")
    
    def detect_active_workspace(self) -> WorkspaceInfo:
        """
        Detect currently active workspace with automatic IDE switching.
        
        Returns:
            WorkspaceInfo with all context needed for operations
        """
        import time
        start_time = time.perf_counter()
        
        # Try detection methods in priority order
        workspace_info = None
        
        if self.ide_type == IDEType.VSCODE:
            workspace_info = self._detect_vscode_workspace()
        elif self.ide_type == IDEType.VISUAL_STUDIO:
            workspace_info = self._detect_visual_studio_workspace()
        
        if not workspace_info:
            workspace_info = self._detect_copilot_workspace()
        
        if not workspace_info:
            workspace_info = self._detect_cwd_workspace()
        
        if not workspace_info:
            workspace_info = self._fallback_cortex_workspace()
        
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        logger.info(
            f"[workspace:{workspace_info.name}] Detected via "
            f"{workspace_info.detection_method.value} ({elapsed_ms:.1f}ms)"
        )
        
        # Cache result
        cache_key = str(workspace_info.path)
        self._cache[cache_key] = (workspace_info, time.time())
        
        return workspace_info
    
    def _detect_vscode_workspace(self) -> Optional[WorkspaceInfo]:
        """
        Detect workspace using VSCode API.
        
        Uses:
        - vscode.workspace.workspaceFolders
        - vscode.window.activeTextEditor
        
        Note: This requires VSCode extension integration.
        For now, falls back to environment-based detection.
        """
        try:
            # Check for VSCode workspace file
            workspace_file = os.getenv("VSCODE_WORKSPACE")
            if workspace_file and Path(workspace_file).exists():
                workspace_root = Path(workspace_file).parent
                return self._build_workspace_info(
                    workspace_root,
                    WorkspaceDetectionMethod.VSCODE_API
                )
            
            # Check for active file in VSCode
            active_file = os.getenv("VSCODE_ACTIVE_FILE")
            if active_file:
                active_file_path = Path(active_file)
                workspace_root = self._find_workspace_root_from_file(active_file_path)
                if workspace_root:
                    return self._build_workspace_info(
                        workspace_root,
                        WorkspaceDetectionMethod.VSCODE_API,
                        active_file=active_file_path
                    )
            
            logger.debug("VSCode API detection: No active workspace found")
            return None
            
        except Exception as e:
            logger.debug(f"VSCode API detection failed: {e}")
            return None
    
    def _detect_visual_studio_workspace(self) -> Optional[WorkspaceInfo]:
        """
        Detect workspace using Visual Studio 2019+ API.
        
        Uses:
        - DTE2.ActiveDocument.FullName
        - DTE2.Solution.FullName
        
        Note: Requires Visual Studio extension integration.
        For now, falls back to solution file detection.
        """
        try:
            # Check for VS solution file
            solution_file = os.getenv("VS_SOLUTION_FILE")
            if solution_file and Path(solution_file).exists():
                workspace_root = Path(solution_file).parent
                return self._build_workspace_info(
                    workspace_root,
                    WorkspaceDetectionMethod.VISUAL_STUDIO_API
                )
            
            # Check for active document in Visual Studio
            active_doc = os.getenv("VS_ACTIVE_DOCUMENT")
            if active_doc:
                active_doc_path = Path(active_doc)
                workspace_root = self._find_workspace_root_from_file(active_doc_path)
                if workspace_root:
                    return self._build_workspace_info(
                        workspace_root,
                        WorkspaceDetectionMethod.VISUAL_STUDIO_API,
                        active_file=active_doc_path
                    )
            
            logger.debug("Visual Studio API detection: No active workspace found")
            return None
            
        except Exception as e:
            logger.debug(f"Visual Studio API detection failed: {e}")
            return None
    
    def _detect_copilot_workspace(self) -> Optional[WorkspaceInfo]:
        """
        Detect workspace from GitHub Copilot Chat context.
        
        Copilot Chat provides:
        - Active file path
        - Workspace folders
        """
        try:
            from src.context.copilot_integration import CopilotIntegration
            
            copilot = CopilotIntegration()
            context = copilot.get_context()
            
            if context and context.get('repo_root'):
                workspace_root = context['repo_root']
                active_file = context.get('active_file')
                
                return self._build_workspace_info(
                    workspace_root,
                    WorkspaceDetectionMethod.COPILOT_CONTEXT,
                    active_file=active_file
                )
            
            logger.debug("Copilot context detection: No workspace found")
            return None
            
        except Exception as e:
            logger.debug(f"Copilot context detection failed: {e}")
            return None
    
    def _detect_cwd_workspace(self) -> Optional[WorkspaceInfo]:
        """
        Detect workspace from current working directory.
        
        Walks up directory tree looking for:
        - .cortex/ directory
        - .git/ directory
        - Solution files (.sln)
        - Project markers (package.json, pyproject.toml, etc.)
        """
        try:
            cwd = Path.cwd()
            workspace_root = self._find_workspace_root_from_file(cwd)
            
            if workspace_root:
                return self._build_workspace_info(
                    workspace_root,
                    WorkspaceDetectionMethod.CWD_SEARCH
                )
            
            logger.debug("CWD detection: No workspace found")
            return None
            
        except Exception as e:
            logger.debug(f"CWD detection failed: {e}")
            return None
    
    def _fallback_cortex_workspace(self) -> WorkspaceInfo:
        """
        Fallback to CORTEX directory as workspace.
        
        Used when no user workspace detected.
        Safe for CORTEX self-operations.
        """
        logger.warning("No workspace detected - falling back to CORTEX directory")
        
        return self._build_workspace_info(
            self.cortex_root,
            WorkspaceDetectionMethod.FALLBACK
        )
    
    def _find_workspace_root_from_file(self, file_path: Path) -> Optional[Path]:
        """
        Find workspace root by walking up from file path.
        
        Looks for workspace markers:
        - .cortex/ (highest priority)
        - .git/
        - .sln file
        - pyproject.toml, package.json, etc.
        """
        current = file_path if file_path.is_dir() else file_path.parent
        
        # Walk up directory tree
        while current != current.parent:
            # Check for .cortex directory (explicit workspace)
            if (current / ".cortex").exists():
                return current
            
            # Check for .git directory (git repository)
            if (current / ".git").exists():
                return current
            
            # Check for solution file (Visual Studio)
            if list(current.glob("*.sln")):
                return current
            
            # Check for project markers
            project_markers = [
                "pyproject.toml", "package.json", "Cargo.toml",
                "go.mod", "pom.xml", "build.gradle"
            ]
            if any((current / marker).exists() for marker in project_markers):
                return current
            
            current = current.parent
        
        return None
    
    def _build_workspace_info(
        self,
        workspace_root: Path,
        detection_method: WorkspaceDetectionMethod,
        active_file: Optional[Path] = None
    ) -> WorkspaceInfo:
        """
        Build WorkspaceInfo from workspace root.
        
        Reads .cortex/config.json and .cortex/workspace-id.txt if available.
        """
        workspace_root = workspace_root.resolve()
        
        # Read workspace ID (or generate default)
        workspace_id_file = workspace_root / ".cortex" / "workspace-id.txt"
        if workspace_id_file.exists():
            workspace_id = workspace_id_file.read_text().strip()
        else:
            # Default workspace ID (not initialized yet)
            workspace_id = f"workspace-{workspace_root.name.lower()}"
        
        # Detect project type
        project_type = self._detect_project_type(workspace_root)
        
        return WorkspaceInfo(
            workspace_id=workspace_id,
            path=workspace_root,
            name=workspace_root.name,
            project_type=project_type,
            ide_type=self.ide_type,
            detection_method=detection_method,
            active_file=active_file
        )
    
    def _detect_project_type(self, workspace_root: Path) -> str:
        """
        Detect project type from workspace contents.
        
        Returns:
            Project type string (python, csharp, typescript, etc.)
        """
        # Python indicators
        if any((workspace_root / f).exists() for f in [
            "pyproject.toml", "setup.py", "requirements.txt", "Pipfile"
        ]):
            return "python"
        
        # C# indicators
        if any(workspace_root.glob("*.csproj")) or any(workspace_root.glob("*.sln")):
            return "csharp"
        
        # TypeScript indicators
        if (workspace_root / "tsconfig.json").exists():
            return "typescript"
        
        # JavaScript indicators
        if (workspace_root / "package.json").exists():
            return "javascript"
        
        # Go indicators
        if (workspace_root / "go.mod").exists():
            return "go"
        
        # Rust indicators
        if (workspace_root / "Cargo.toml").exists():
            return "rust"
        
        # Java indicators
        if (workspace_root / "pom.xml").exists() or (workspace_root / "build.gradle").exists():
            return "java"
        
        return "unknown"
    
    def _find_cortex_root(self) -> Path:
        """
        Find CORTEX installation root.
        
        Looks for cortex-brain/ directory.
        """
        current = Path(__file__).parent
        
        while current != current.parent:
            if (current / "cortex-brain").exists():
                return current
            current = current.parent
        
        raise RuntimeError("CORTEX installation not found")
    
    @classmethod
    def clear_cache(cls):
        """Clear workspace detection cache."""
        cls._cache.clear()


# Global detector instance
_detector: Optional[WorkspaceDetector] = None


def detect_active_workspace() -> WorkspaceInfo:
    """
    Global function to detect active workspace.
    
    Usage:
        from src.core.workspace_detector import detect_active_workspace
        
        workspace = detect_active_workspace()
        print(f"Active: {workspace.name}")
    """
    global _detector
    
    if _detector is None:
        _detector = WorkspaceDetector()
    
    return _detector.detect_active_workspace()
