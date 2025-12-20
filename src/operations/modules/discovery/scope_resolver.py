"""
Scope Resolver - Determine Discovery Scope

Resolves user input into a concrete DiscoveryScope with validated paths
and exclusion patterns.

Author: Asif Hussain
Version: 1.0.0
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Union

from .models import DiscoveryScope, DiscoveryDepth

logger = logging.getLogger(__name__)


class ScopeResolver:
    """
    Resolves discovery scope from user input.
    
    Handles:
    - Path resolution (relative to absolute)
    - Scope validation
    - Default pattern application
    - Estimated file count calculation
    """
    
    def __init__(self, project_root: Path):
        """
        Initialize scope resolver.
        
        Args:
            project_root: Root directory of the project
        """
        self.project_root = Path(project_root).resolve()
        logger.debug(f"ScopeResolver initialized with root: {self.project_root}")
    
    def resolve(
        self,
        scope_input: str | Path | Dict[str, Any],
        depth: str = "moderate"
    ) -> DiscoveryScope:
        """
        Resolve scope from user input.
        
        Args:
            scope_input: Scope specification (path, "project", or dict)
            depth: Discovery depth ("quick", "moderate", "full")
        
        Returns:
            Resolved DiscoveryScope object
        
        Raises:
            ValueError: If scope cannot be resolved
        """
        # This is a skeleton - implementation in GREEN phase
        
        if isinstance(scope_input, dict):
            return self._resolve_from_dict(scope_input)
        elif isinstance(scope_input, (str, Path)):
            return self._resolve_from_path(scope_input, depth)
        else:
            raise ValueError(f"Unsupported scope input type: {type(scope_input)}")
    
    def _resolve_from_path(self, path: Union[str, Path], depth: str) -> DiscoveryScope:
        """Resolve scope from path string."""
        # Handle special keyword "project"
        if isinstance(path, str) and path.lower() == "project":
            root_path = self.project_root
        else:
            root_path = Path(path).resolve()
        
        # Convert depth string to enum
        try:
            depth_enum = DiscoveryDepth(depth)
        except ValueError:
            depth_enum = DiscoveryDepth.MODERATE
        
        # Create scope
        scope = DiscoveryScope(
            root_path=root_path,
            depth=depth_enum
        )
        
        return scope
    
    def _resolve_from_dict(self, scope_dict: Dict[str, Any]) -> DiscoveryScope:
        """Resolve scope from dictionary specification."""
        # Extract root path
        root_path = Path(scope_dict.get("root_path", self.project_root)).resolve()
        
        # Extract patterns
        include_patterns = scope_dict.get("include_patterns", ["*"])
        exclude_patterns = scope_dict.get("exclude_patterns", [])
        
        # Extract other params
        max_depth = scope_dict.get("max_depth", -1)
        follow_symlinks = scope_dict.get("follow_symlinks", False)
        
        # Depth enum
        depth_str = scope_dict.get("depth", "moderate")
        try:
            depth_enum = DiscoveryDepth(depth_str)
        except ValueError:
            depth_enum = DiscoveryDepth.MODERATE
        
        return DiscoveryScope(
            root_path=root_path,
            include_patterns=include_patterns,
            exclude_patterns=exclude_patterns,
            max_depth=max_depth,
            follow_symlinks=follow_symlinks,
            depth=depth_enum
        )
    
    def validate_scope(self, scope: DiscoveryScope) -> bool:
        """
        Validate that scope is viable.
        
        Args:
            scope: DiscoveryScope to validate
        
        Returns:
            True if valid
        
        Raises:
            ValueError: If scope is invalid
        """
        # Check path exists
        if not scope.root_path.exists():
            raise ValueError(f"Path does not exist: {scope.root_path}")
        
        # Check it's a directory
        if not scope.root_path.is_dir():
            raise ValueError(f"Path is not a directory: {scope.root_path}")
        
        # Check readable
        try:
            list(scope.root_path.iterdir())
        except PermissionError:
            raise ValueError(f"Cannot read directory: {scope.root_path}")
        
        return True
    
    def estimate_file_count(self, scope: DiscoveryScope) -> int:
        """
        Estimate number of files in scope.
        
        Args:
            scope: DiscoveryScope to estimate
        
        Returns:
            Estimated file count
        """
        count = 0
        try:
            # Quick count without filtering (fast estimation)
            for item in scope.root_path.rglob("*"):
                if item.is_file():
                    count += 1
                # Limit estimation to prevent hanging
                if count > 10000:
                    return count
        except Exception:
            # If estimation fails, return 0
            return 0
        
        return count
