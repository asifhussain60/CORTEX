"""Fix indentation errors."""

from pathlib import Path
from typing import Dict, Any, Optional
from .base_strategy import BaseFixStrategy


class IndentationFixStrategy(BaseFixStrategy):
    """Strategy for fixing indentation errors."""
    
    def can_fix(self, parsed_error: Dict[str, Any], fix_pattern: Dict[str, Any]) -> bool:
        """Check if this is an indentation error."""
        return (
            parsed_error.get("category") == "indentation" or
            fix_pattern.get("action") == "normalize_indentation"
        )
    
    def apply_fix(
        self, 
        parsed_error: Dict[str, Any], 
        fix_pattern: Dict[str, Any],
        file_path: Optional[str]
    ) -> Dict[str, Any]:
        """
        Fix indentation errors by normalizing tabs to spaces.
        
        Returns:
            Fix result with success, message, changes, fixed_content
        """
        spaces = fix_pattern.get("params", {}).get("spaces", 4)
        
        # If file doesn't exist, return recommendation
        if not file_path or not Path(file_path).exists():
            return {
                "success": True,
                "message": f"Indentation error detected. Recommend normalizing to {spaces} spaces.",
                "changes": [f"Convert tabs to {spaces} spaces"],
                "recommendation": f"Use {spaces} spaces for indentation consistently"
            }
        
        try:
            # Read file
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            # Normalize indentation (convert tabs to spaces)
            fixed_lines = []
            for line in lines:
                # Replace tabs with spaces
                fixed_line = line.replace('\t', ' ' * spaces)
                fixed_lines.append(fixed_line)
            
            return {
                "success": True,
                "message": f"Normalized indentation to {spaces} spaces",
                "changes": [f"Convert tabs to {spaces} spaces"],
                "fixed_content": ''.join(fixed_lines)
            }
        
        except Exception as e:
            return {
                "success": False,
                "message": f"Indentation fix failed: {str(e)}"
            }
