"""Fix package-related errors."""

from typing import Dict, Any, Optional
from .base_strategy import BaseFixStrategy


class PackageFixStrategy(BaseFixStrategy):
    """Strategy for suggesting package installations."""
    
    def can_fix(self, parsed_error: Dict[str, Any], fix_pattern: Dict[str, Any]) -> bool:
        """Check if this is a missing package error."""
        return (
            parsed_error.get("missing_module") or
            fix_pattern.get("action") == "install_package"
        )
    
    def apply_fix(
        self, 
        parsed_error: Dict[str, Any], 
        fix_pattern: Dict[str, Any],
        file_path: Optional[str]
    ) -> Dict[str, Any]:
        """
        Suggest package installation.
        
        Returns:
            Fix result with success, message, changes, command
        """
        params = fix_pattern.get("params", {})
        package = params.get("package") or parsed_error.get("missing_module")
        
        if not package:
            return {
                "success": False,
                "message": "Cannot determine which package to install"
            }
        
        return {
            "success": True,
            "message": f"Install missing package: {package}",
            "changes": [f"pip install {package}"],
            "command": f"pip install {package}"
        }
