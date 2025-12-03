"""
Context Detector Utility

Detects whether the current execution context is within the CORTEX development
repository or a user repository. This determines which operations are available
and how certain commands should be routed.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

from pathlib import Path
from typing import Optional
import os


def is_cortex_repo(project_root: Optional[Path] = None) -> bool:
    """
    Detect if the current context is the CORTEX development repository.
    
    CORTEX development repository indicators:
    - cortex-brain/admin/ directory exists
    - src/operations/modules/admin/ directory exists
    
    Args:
        project_root: Path to check (defaults to current working directory)
    
    Returns:
        True if in CORTEX development repo, False if in user repo
    
    Examples:
        >>> is_cortex_repo()  # In CORTEX repo
        True
        
        >>> is_cortex_repo(Path("/home/user/myapp"))  # In user app
        False
    """
    if project_root is None:
        project_root = Path(os.getcwd())
    
    # Check for cortex-brain/admin/ directory
    admin_brain = project_root / "cortex-brain" / "admin"
    if admin_brain.exists() and admin_brain.is_dir():
        return True
    
    # Check for src/operations/modules/admin/ directory
    admin_ops = project_root / "src" / "operations" / "modules" / "admin"
    if admin_ops.exists() and admin_ops.is_dir():
        return True
    
    return False


def get_context_type(project_root: Optional[Path] = None) -> str:
    """
    Get a string description of the current context type.
    
    Args:
        project_root: Path to check (defaults to current working directory)
    
    Returns:
        Either "cortex" or "user"
    
    Examples:
        >>> get_context_type()
        'cortex'
        
        >>> get_context_type(Path("/home/user/myapp"))
        'user'
    """
    return "cortex" if is_cortex_repo(project_root) else "user"


def detect_cortex_root() -> Optional[Path]:
    """
    Auto-detect CORTEX project root by walking up from current directory.
    
    Looks for indicators that this is the CORTEX repository:
    - cortex-brain/admin/ directory
    - src/operations/modules/admin/ directory
    
    Returns:
        Path to CORTEX root if found, None otherwise
    
    Examples:
        >>> detect_cortex_root()
        Path('D:/PROJECTS/CORTEX')
    """
    current = Path(os.getcwd())
    
    # Walk up the directory tree
    for parent in [current] + list(current.parents):
        if is_cortex_repo(parent):
            return parent
    
    return None
