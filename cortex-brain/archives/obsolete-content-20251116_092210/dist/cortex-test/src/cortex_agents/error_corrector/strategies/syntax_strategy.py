"""Fix syntax errors."""

import re
from pathlib import Path
from typing import Dict, Any, Optional
from .base_strategy import BaseFixStrategy


class SyntaxFixStrategy(BaseFixStrategy):
    """Strategy for fixing syntax errors."""
    
    def can_fix(self, parsed_error: Dict[str, Any], fix_pattern: Dict[str, Any]) -> bool:
        """Check if this is a syntax error."""
        return (
            parsed_error.get("category") in ["syntax", "invalid_syntax"] or
            fix_pattern.get("action") == "fix_syntax"
        )
    
    def apply_fix(
        self, 
        parsed_error: Dict[str, Any], 
        fix_pattern: Dict[str, Any],
        file_path: Optional[str]
    ) -> Dict[str, Any]:
        """
        Fix syntax errors like missing colons.
        
        Returns:
            Fix result with success, message, changes, fixed_line
        """
        # Try to fix missing colons
        return self._check_missing_colons(file_path, parsed_error)
    
    def _check_missing_colons(self, file_path: Optional[str], parsed_error: Dict) -> Dict[str, Any]:
        """Check for missing colons in control structures."""
        if not file_path or not Path(file_path).exists():
            return {
                "success": False,
                "message": "File path required"
            }
        
        line_num = parsed_error.get("line")
        
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            if line_num and line_num <= len(lines):
                problem_line = lines[line_num - 1]
                
                # Check if it's a control structure without colon
                if re.match(r'^\s*(if|elif|else|for|while|def|class|try|except|finally|with)\b', problem_line):
                    if not problem_line.rstrip().endswith(':'):
                        return {
                            "success": True,
                            "message": f"Add missing colon to line {line_num}",
                            "changes": [f"Add ':' to end of line {line_num}"],
                            "fixed_line": problem_line.rstrip() + ':'
                        }
            
            return {
                "success": False,
                "message": "Could not identify missing colon"
            }
        
        except Exception as e:
            return {
                "success": False,
                "message": f"Colon check failed: {str(e)}"
            }
