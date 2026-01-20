"""Tool description validation."""

from typing import Dict, List, Any


class ToolDescriptionValidator:
    """Validate tool descriptions for correctness."""
    
    REQUIRED_FIELDS = ["name", "description", "parameters", "return_type"]
    
    def __init__(self):
        self.validations: List[Dict[str, Any]] = []
    
    def validate(self, tool_description: Dict[str, Any]) -> bool:
        """Validate tool description."""
        errors = []
        
        for field in self.REQUIRED_FIELDS:
            if field not in tool_description:
                errors.append(f"Missing required field: {field}")
        
        validation_result = {
            "tool_name": tool_description.get("name", "unknown"),
            "is_valid": len(errors) == 0,
            "errors": errors
        }
        self.validations.append(validation_result)
        
        return validation_result["is_valid"]
    
    def get_report(self) -> Dict[str, Any]:
        """Get validation report."""
        if not self.validations:
            return {"total": 0, "valid": 0, "invalid": 0}
        
        total = len(self.validations)
        valid = sum(1 for v in self.validations if v["is_valid"])
        
        return {
            "total": total,
            "valid": valid,
            "invalid": total - valid,
            "validation_rate": (valid / total * 100) if total > 0 else 0
        }
