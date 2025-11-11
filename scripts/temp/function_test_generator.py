"""Function test generation."""

from typing import Dict, Any
from ..templates import TemplateManager


class FunctionTestGenerator:
    """Generates test code for functions."""
    
    def __init__(self, template_manager: TemplateManager):
        """Initialize with template manager."""
        self.templates = template_manager
    
    def generate(self, func_info: Dict[str, Any]) -> str:
        """Generate tests for a function."""
        tests = []
        
        # Basic test
        if "basic" in func_info["scenarios"]:
            tests.append(self.templates.basic_function(func_info))
        
        # Edge cases test
        if "edge_cases" in func_info["scenarios"]:
            tests.append(self.templates.edge_cases(func_info))
        
        # Error handling test
        if "error_handling" in func_info["scenarios"]:
            tests.append(self.templates.error_handling(func_info))
        
        return '\n\n'.join(tests)
