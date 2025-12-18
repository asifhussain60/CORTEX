"""
IDE Detection Module for CORTEX 4.0

Detects the active IDE (VSCode, Visual Studio, or Unknown) based on:
1. Environment variables (VSCODE_*, VS_*)
2. Directory markers (.vscode/, .vs/)
3. Process inspection (parent process name)
4. Configuration hints (cortex-brain/ide-context.json)

Design Principles:
- Fast detection (<10ms)
- Cached results (avoid re-detection)
- Graceful degradation (defaults to shared config if unknown)
- No external dependencies beyond psutil
"""

import os
import json
import logging
from enum import Enum
from pathlib import Path
from typing import Optional, Dict, Any
import time

try:
    import psutil
except ImportError:
    psutil = None  # Gracefully handle missing psutil


class IDEType(Enum):
    """Supported IDE types."""
    VSCODE = "vscode"
    VISUAL_STUDIO = "visualstudio"
    UNKNOWN = "unknown"


class IDEDetector:
    """
    Detect active IDE and manage IDE context.
    
    Detection Strategy (in order of precedence):
    1. Explicit environment variable (CORTEX_IDE=vscode|visualstudio)
    2. IDE-specific environment variables (VSCODE_*, VS_*)
    3. Parent process name (Code.exe, devenv.exe) - requires psutil
    4. Directory markers (.vscode/settings.json, .vs/)
    5. Cached context (cortex-brain/ide-context.json)
    6. Default to UNKNOWN (use shared config)
    """
    
    _cached_ide: Optional[IDEType] = None
    _context_file = "cortex-brain/ide-context.json"
    
    @classmethod
    def detect(cls, workspace_root: Path) -> IDEType:
        """
        Detect the active IDE.
        
        Args:
            workspace_root: Root directory of the workspace
            
        Returns:
            IDEType enum value
        """
        if cls._cached_ide:
            return cls._cached_ide
            
        # Strategy 1: Explicit override
        explicit_ide = os.getenv("CORTEX_IDE")
        if explicit_ide:
            try:
                cls._cached_ide = IDEType(explicit_ide.lower())
                cls._save_context(workspace_root, cls._cached_ide)
                return cls._cached_ide
            except ValueError:
                logging.warning(f"Invalid CORTEX_IDE value: {explicit_ide}")
        
        # Strategy 2: IDE-specific environment variables
        if os.getenv("VSCODE_PID") or os.getenv("VSCODE_IPC_HOOK"):
            cls._cached_ide = IDEType.VSCODE
            cls._save_context(workspace_root, cls._cached_ide)
            return cls._cached_ide
            
        if os.getenv("VisualStudioVersion") or os.getenv("VSINSTALLDIR"):
            cls._cached_ide = IDEType.VISUAL_STUDIO
            cls._save_context(workspace_root, cls._cached_ide)
            return cls._cached_ide
        
        # Strategy 3: Parent process detection (only if psutil available)
        if psutil:
            try:
                parent = psutil.Process(os.getppid())
                parent_name = parent.name().lower()
                
                if "code" in parent_name:  # Code.exe, code.exe, VSCode
                    cls._cached_ide = IDEType.VSCODE
                    cls._save_context(workspace_root, cls._cached_ide)
                    return cls._cached_ide
                    
                if "devenv" in parent_name or "visualstudio" in parent_name:
                    cls._cached_ide = IDEType.VISUAL_STUDIO
                    cls._save_context(workspace_root, cls._cached_ide)
                    return cls._cached_ide
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                logging.debug("Could not inspect parent process for IDE detection")
        
        # Strategy 4: Directory markers
        vscode_dir = workspace_root / ".vscode"
        vs_dir = workspace_root / ".vs"
        
        # Prefer most recently modified
        vscode_time = vscode_dir.stat().st_mtime if vscode_dir.exists() else 0
        vs_time = vs_dir.stat().st_mtime if vs_dir.exists() else 0
        
        if vscode_time > vs_time and vscode_time > 0:
            cls._cached_ide = IDEType.VSCODE
            cls._save_context(workspace_root, cls._cached_ide)
            return cls._cached_ide
        elif vs_time > 0:
            cls._cached_ide = IDEType.VISUAL_STUDIO
            cls._save_context(workspace_root, cls._cached_ide)
            return cls._cached_ide
        
        # Strategy 5: Cached context
        cached = cls._load_context(workspace_root)
        if cached:
            cls._cached_ide = cached
            return cls._cached_ide
        
        # Strategy 6: Default to unknown
        cls._cached_ide = IDEType.UNKNOWN
        logging.info("Could not detect IDE, using shared configuration")
        return cls._cached_ide
    
    @classmethod
    def _save_context(cls, workspace_root: Path, ide_type: IDEType) -> None:
        """Save detected IDE context for future sessions."""
        context_path = workspace_root / cls._context_file
        context_path.parent.mkdir(parents=True, exist_ok=True)
        
        context = {
            "detected_ide": ide_type.value,
            "detection_timestamp": time.time(),
            "environment": {
                "os": os.name,
                "platform": os.sys.platform
            }
        }
        
        try:
            with open(context_path, 'w') as f:
                json.dump(context, f, indent=2)
        except Exception as e:
            logging.debug(f"Could not save IDE context: {e}")
    
    @classmethod
    def _load_context(cls, workspace_root: Path) -> Optional[IDEType]:
        """Load previously saved IDE context."""
        context_path = workspace_root / cls._context_file
        
        if not context_path.exists():
            return None
            
        try:
            with open(context_path, 'r') as f:
                context = json.load(f)
                return IDEType(context.get("detected_ide", "unknown"))
        except (json.JSONDecodeError, ValueError, FileNotFoundError):
            return None
    
    @classmethod
    def reset_cache(cls) -> None:
        """Reset cached IDE detection (for testing)."""
        cls._cached_ide = None
    
    @classmethod
    def get_config_filename(cls, ide_type: IDEType) -> str:
        """Get configuration filename for IDE type."""
        return f"{ide_type.value}.config.json"
    
    @classmethod
    def get_ide_directory(cls, ide_type: IDEType) -> str:
        """Get IDE-specific directory name."""
        if ide_type == IDEType.VSCODE:
            return ".vscode"
        elif ide_type == IDEType.VISUAL_STUDIO:
            return ".vs"
        else:
            return ".cortex"  # Fallback for unknown IDEs
