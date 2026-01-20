"""Response Templates

Author: CORTEX Framework
"""

from enum import Enum
from dataclasses import dataclass, field

class VariableType(str, Enum):
    """Template variable types."""
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"


@dataclass
class VariableSpec:
    """Template variable specification."""
    name: str
    var_type: VariableType
    description: str = ""
    required: bool = True
    default: any = None


from typing import Dict

class ResponseType(Enum):
    """Response template types."""
    SUCCESS = "success"
    ERROR = "error"
    INFO = "info"
    WARNING = "warning"


class ResponseTemplate:
    """Response template."""
    
    def render(self, variables: Dict[str, VariableType]) -> str:
        """Render template."""
        return ""


class TemplateRegistry:
    """Registry for response templates."""
    
    def __init__(self):
        self.templates = {}
    
    def register(self, template_id: str, template: ResponseTemplate) -> None:
        """Register template."""
        self.templates[template_id] = template
    
    def get(self, template_id: str) -> ResponseTemplate:
        """Get template."""
        return self.templates.get(template_id)


class SimpleTemplateSubstitutor:
    """Simple template variable substitution."""
    
    def substitute(self, template: str, variables: Dict[str, any]) -> str:
        """Substitute variables in template."""
        result = template
        for key, value in variables.items():
            result = result.replace(f"{{{key}}}", str(value))
        return result


class TemplateCache:
    """Cache for compiled templates."""
    
    def __init__(self):
        self.cache = {}
    
    def get(self, template_id: str) -> ResponseTemplate:
        """Get cached template."""
        return self.cache.get(template_id)
    
    def put(self, template_id: str, template: ResponseTemplate) -> None:
        """Cache template."""
        self.cache[template_id] = template


class TemplateEngine:
    """Template rendering engine."""
    
    def __init__(self):
        self.registry = TemplateRegistry()
        self.cache = TemplateCache()
    
    def render(self, template_id: str, variables: Dict[str, any]) -> str:
        """Render template with variables."""
        template = self.registry.get(template_id)
        if template:
            return template.render(variables)
        return ""

__all__ = ["VariableType", "VariableSpec", "ResponseType", "ResponseTemplate", "TemplateRegistry", "SimpleTemplateSubstitutor", "TemplateCache", "TemplateEngine"]
