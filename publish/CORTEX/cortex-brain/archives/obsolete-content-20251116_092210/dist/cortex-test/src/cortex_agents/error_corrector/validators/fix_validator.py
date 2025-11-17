"""Validate error fixes before applying."""

from typing import Dict, Any


class FixValidator:
    """Validator for error fixes."""
    
    def validate(self, fix_result: Dict[str, Any]) -> bool:
        """
        Validate a fix result before applying.
        
        Args:
            fix_result: Fix result from strategy
            
        Returns:
            True if fix is valid and safe to apply
        """
        # Check required fields
        if not isinstance(fix_result, dict):
            return False
        
        if not fix_result.get("success"):
            return False
        
        # Must have either changes or fixed_content
        has_changes = bool(fix_result.get("changes"))
        has_content = bool(fix_result.get("fixed_content"))
        
        if not (has_changes or has_content):
            return False
        
        # If fixed_content exists, ensure it's a string
        if has_content and not isinstance(fix_result["fixed_content"], str):
            return False
        
        return True
    
    def is_safe(self, fix_result: Dict[str, Any], parsed_error: Dict[str, Any]) -> bool:
        """
        Check if fix is safe to apply automatically.
        
        Args:
            fix_result: Fix result from strategy
            parsed_error: Original parsed error
            
        Returns:
            True if fix is safe for automatic application
        """
        # For now, consider all validated fixes safe
        # In future, could add more sophisticated safety checks:
        # - Check if fix modifies only expected lines
        # - Verify fix doesn't introduce new syntax errors
        # - Ensure fix is minimal and targeted
        
        if not self.validate(fix_result):
            return False
        
        return True
