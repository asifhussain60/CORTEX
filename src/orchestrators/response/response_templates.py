"""Response Template System for CORTEX Orchestrators.

This module provides a template engine for common response patterns with support for:
- Template pattern recognition and management
- Variable substitution with type safety
- Template versioning and registry
- Multi-mode template application
- Caching and performance optimization

AC-RESP-003-01: Response Template System Implementation
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Any
from datetime import datetime
import re
from abc import ABC, abstractmethod


class VariableType(Enum):
    """Supported variable types in templates."""
    STRING = "string"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    LIST = "list"
    OPTIONAL = "optional"


class ResponseType(Enum):
    """Types of responses that templates support."""
    ERROR = "error"
    SUCCESS = "success"
    PROGRESS = "progress"
    DECISION = "decision"
    CONFIRMATION = "confirmation"
    WARNING = "warning"
    INFORMATIONAL = "informational"
    DEBUG = "debug"


@dataclass
class VariableSpec:
    """Specification for a template variable.
    
    Attributes:
        name: Variable name (used as {{ name }} in template)
        var_type: Type of variable (string, integer, boolean, list, optional)
        required: Whether this variable must be provided
        default: Default value if not provided and not required
        description: Human-readable description of variable
        pattern: Regex pattern for validation (for strings)
    """
    name: str
    var_type: VariableType
    required: bool = True
    default: Any = None
    description: str = ""
    pattern: Optional[str] = None

    def validate(self, value: Any) -> bool:
        """Validate a value against this variable spec.
        
        Args:
            value: Value to validate
            
        Returns:
            True if valid, False otherwise
        """
        if value is None:
            return not self.required and self.default is not None

        if self.var_type == VariableType.STRING:
            if not isinstance(value, str):
                return False
            if self.pattern:
                return bool(re.match(self.pattern, value))
            return True

        elif self.var_type == VariableType.INTEGER:
            return isinstance(value, int) and not isinstance(value, bool)

        elif self.var_type == VariableType.BOOLEAN:
            return isinstance(value, bool)

        elif self.var_type == VariableType.LIST:
            return isinstance(value, list)

        elif self.var_type == VariableType.OPTIONAL:
            return True  # Any type is OK for optional

        return True


@dataclass
class ResponseTemplate:
    """A response template for common patterns.
    
    Attributes:
        template_id: Unique identifier for template (e.g., "error_processing")
        version: Template version (e.g., "1.0.0")
        name: Human-readable template name
        description: Description of when to use this template
        pattern: Template pattern with {{ variable }} placeholders
        response_type: Type of response this template is for
        supported_modes: Response modes this template supports
        variables: Dict of variable name -> VariableSpec
        created_at: When template was created
        updated_at: When template was last updated
    """
    template_id: str
    version: str
    name: str
    description: str
    pattern: str
    response_type: ResponseType
    supported_modes: Set[str] = field(default_factory=lambda: {"CHAT", "MARKDOWN", "JSON_API"})
    variables: Dict[str, VariableSpec] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def validate_variables(self, variables: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate provided variables against template spec.
        
        Args:
            variables: Dict of variable values to validate
            
        Returns:
            Tuple of (is_valid, list_of_error_messages)
        """
        errors = []

        # Check required variables are provided
        for var_name, var_spec in self.variables.items():
            if var_spec.required and var_name not in variables:
                if var_spec.default is None:
                    errors.append(f"Required variable '{var_name}' not provided")
                continue

            if var_name in variables:
                if not var_spec.validate(variables[var_name]):
                    errors.append(f"Variable '{var_name}' failed validation (type: {var_spec.var_type.value})")

        # Check for unexpected variables
        for var_name in variables:
            if var_name not in self.variables:
                errors.append(f"Unexpected variable '{var_name}'")

        return len(errors) == 0, errors


@dataclass
class TemplateRegistry:
    """Registry for managing response templates.
    
    Attributes:
        templates: Dict of template_id -> ResponseTemplate
        template_versions: Dict tracking all versions of templates
    """
    templates: Dict[str, ResponseTemplate] = field(default_factory=dict)
    template_versions: Dict[str, List[str]] = field(default_factory=dict)

    def register(self, template: ResponseTemplate) -> None:
        """Register a template in the registry.
        
        Args:
            template: ResponseTemplate to register
        """
        template_key = f"{template.template_id}:{template.version}"
        self.templates[template_key] = template

        if template.template_id not in self.template_versions:
            self.template_versions[template.template_id] = []

        if template.version not in self.template_versions[template.template_id]:
            self.template_versions[template.template_id].append(template.version)

    def get(self, template_id: str, version: Optional[str] = None) -> Optional[ResponseTemplate]:
        """Get a template by ID and optional version.
        
        Args:
            template_id: Template ID to retrieve
            version: Specific version (if None, gets latest)
            
        Returns:
            ResponseTemplate or None if not found
        """
        if version:
            key = f"{template_id}:{version}"
            return self.templates.get(key)

        # Get latest version
        if template_id in self.template_versions:
            versions = sorted(self.template_versions[template_id], reverse=True)
            if versions:
                key = f"{template_id}:{versions[0]}"
                return self.templates.get(key)

        return None

    def list_templates(self, response_type: Optional[ResponseType] = None) -> List[ResponseTemplate]:
        """List all templates, optionally filtered by response type.
        
        Args:
            response_type: Optional filter by response type
            
        Returns:
            List of ResponseTemplate objects
        """
        result = []
        seen_ids = set()

        for template_key, template in self.templates.items():
            if template.template_id not in seen_ids:
                if response_type is None or template.response_type == response_type:
                    result.append(template)
                    seen_ids.add(template.template_id)

        return sorted(result, key=lambda t: t.template_id)

    def unregister(self, template_id: str, version: Optional[str] = None) -> bool:
        """Unregister a template.
        
        Args:
            template_id: Template ID to unregister
            version: Specific version (if None, unregisters all)
            
        Returns:
            True if unregistered, False if not found
        """
        if version:
            key = f"{template_id}:{version}"
            if key in self.templates:
                del self.templates[key]
                if version in self.template_versions.get(template_id, []):
                    self.template_versions[template_id].remove(version)
                return True
            return False
        else:
            # Unregister all versions
            if template_id in self.template_versions:
                for version in self.template_versions[template_id]:
                    key = f"{template_id}:{version}"
                    if key in self.templates:
                        del self.templates[key]
                del self.template_versions[template_id]
                return True
            return False


class TemplateSubstitutor(ABC):
    """Abstract base for template substitution strategies."""

    @abstractmethod
    def substitute(self, pattern: str, variables: Dict[str, Any]) -> str:
        """Substitute variables in pattern.
        
        Args:
            pattern: Template pattern with {{ variable }} placeholders
            variables: Dict of variable values
            
        Returns:
            Pattern with variables substituted
        """
        pass


class SimpleTemplateSubstitutor(TemplateSubstitutor):
    """Simple template substitutor using regex pattern matching."""

    def substitute(self, pattern: str, variables: Dict[str, Any]) -> str:
        """Substitute variables in pattern using {{ variable }} syntax.
        
        Args:
            pattern: Template pattern with {{ variable }} placeholders
            variables: Dict of variable values
            
        Returns:
            Pattern with variables substituted
        """
        result = pattern
        variable_pattern = r'\{\{\s*(\w+)\s*\}\}'

        def replace_func(match):
            var_name = match.group(1)
            if var_name in variables:
                value = variables[var_name]
                if value is None:
                    return ""
                return str(value)
            return match.group(0)  # Return unchanged if not found

        result = re.sub(variable_pattern, replace_func, result)
        return result


@dataclass
class TemplateCache:
    """Cache for template substitution results.
    
    Attributes:
        cache: Dict of cache_key -> substituted_result
        max_entries: Maximum number of cached entries
    """
    cache: Dict[str, str] = field(default_factory=dict)
    max_entries: int = 1000

    def get(self, key: str) -> Optional[str]:
        """Get cached value.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None
        """
        return self.cache.get(key)

    def set(self, key: str, value: str) -> None:
        """Set cached value.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        if len(self.cache) >= self.max_entries:
            # Remove oldest entry (simple FIFO)
            first_key = next(iter(self.cache))
            del self.cache[first_key]

        self.cache[key] = value

    def clear(self) -> None:
        """Clear all cached entries."""
        self.cache.clear()


@dataclass
class TemplateEngine:
    """Main template engine for response templates.
    
    Provides:
    - Template registration and lookup
    - Variable substitution with validation
    - Template versioning
    - Caching for performance
    - Multi-mode support
    
    Attributes:
        registry: TemplateRegistry for managing templates
        substitutor: Strategy for variable substitution
        cache: Cache for substitution results
    """
    registry: TemplateRegistry = field(default_factory=TemplateRegistry)
    substitutor: TemplateSubstitutor = field(default_factory=SimpleTemplateSubstitutor)
    cache: TemplateCache = field(default_factory=TemplateCache)

    def register_template(self, template: ResponseTemplate) -> None:
        """Register a template.
        
        Args:
            template: ResponseTemplate to register
        """
        self.registry.register(template)

    def apply_template(
        self, template_id: str, variables: Dict[str, Any], version: Optional[str] = None
    ) -> str:
        """Apply a template with variable substitution.
        
        Args:
            template_id: ID of template to apply
            variables: Dict of variables to substitute
            version: Optional specific template version
            
        Returns:
            Rendered template with variables substituted
            
        Raises:
            ValueError: If template not found or variables invalid
        """
        template = self.registry.get(template_id, version)
        if not template:
            raise ValueError(f"Template '{template_id}' not found")

        # Validate variables
        is_valid, errors = template.validate_variables(variables)
        if not is_valid:
            raise ValueError(f"Invalid variables for template '{template_id}': {'; '.join(errors)}")

        # Check cache
        cache_key = f"{template_id}:{version}:{hash(frozenset(variables.items()))}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        # Fill in defaults for optional variables
        filled_vars = dict(variables)
        for var_name, var_spec in template.variables.items():
            if var_name not in filled_vars and var_spec.default is not None:
                filled_vars[var_name] = var_spec.default

        # Substitute and cache
        result = self.substitutor.substitute(template.pattern, filled_vars)
        self.cache.set(cache_key, result)

        return result

    def get_template(self, template_id: str, version: Optional[str] = None) -> Optional[ResponseTemplate]:
        """Get a template by ID and optional version.
        
        Args:
            template_id: Template ID
            version: Optional specific version
            
        Returns:
            ResponseTemplate or None
        """
        return self.registry.get(template_id, version)

    def list_templates(self, response_type: Optional[ResponseType] = None) -> List[ResponseTemplate]:
        """List all templates, optionally filtered by response type.
        
        Args:
            response_type: Optional filter by response type
            
        Returns:
            List of ResponseTemplate objects
        """
        return self.registry.list_templates(response_type)

    def create_template(
        self,
        template_id: str,
        version: str,
        name: str,
        description: str,
        pattern: str,
        response_type: ResponseType,
        variables: Optional[Dict[str, VariableSpec]] = None,
        supported_modes: Optional[Set[str]] = None,
    ) -> ResponseTemplate:
        """Create and register a template.
        
        Args:
            template_id: Unique template ID
            version: Template version
            name: Human-readable name
            description: Template description
            pattern: Template pattern with {{ variable }} placeholders
            response_type: Type of response
            variables: Optional dict of variable specs
            supported_modes: Optional set of supported response modes
            
        Returns:
            Created ResponseTemplate
        """
        if variables is None:
            variables = {}
        if supported_modes is None:
            supported_modes = {"CHAT", "MARKDOWN", "JSON_API"}

        template = ResponseTemplate(
            template_id=template_id,
            version=version,
            name=name,
            description=description,
            pattern=pattern,
            response_type=response_type,
            supported_modes=supported_modes,
            variables=variables,
        )

        self.register_template(template)
        return template

    def clear_cache(self) -> None:
        """Clear template substitution cache."""
        self.cache.clear()

    def unregister_template(self, template_id: str, version: Optional[str] = None) -> bool:
        """Unregister a template.
        
        Args:
            template_id: Template ID
            version: Optional specific version
            
        Returns:
            True if unregistered, False if not found
        """
        return self.registry.unregister(template_id, version)


# Singleton instance
_template_engine: Optional[TemplateEngine] = None


def get_template_engine() -> TemplateEngine:
    """Get or create singleton template engine instance.
    
    Returns:
        TemplateEngine singleton
    """
    global _template_engine
    if _template_engine is None:
        _template_engine = TemplateEngine()
        _load_default_templates(_template_engine)
    return _template_engine


def _load_default_templates(engine: TemplateEngine) -> None:
    """Load default built-in templates.
    
    Args:
        engine: TemplateEngine to load templates into
    """
    # Error template
    engine.create_template(
        template_id="error_processing",
        version="1.0.0",
        name="Error Processing",
        description="Standard error response template",
        pattern="Error processing {{ item }}: {{ reason }}",
        response_type=ResponseType.ERROR,
        variables={
            "item": VariableSpec(name="item", var_type=VariableType.STRING, description="Item being processed"),
            "reason": VariableSpec(
                name="reason", var_type=VariableType.STRING, description="Reason for error"
            ),
        },
    )

    # Success template
    engine.create_template(
        template_id="success_completion",
        version="1.0.0",
        name="Success Completion",
        description="Standard success response template",
        pattern="Successfully {{ action }} {{ item }}",
        response_type=ResponseType.SUCCESS,
        variables={
            "action": VariableSpec(name="action", var_type=VariableType.STRING, description="Action performed"),
            "item": VariableSpec(name="item", var_type=VariableType.STRING, description="Item affected"),
        },
    )

    # Progress template
    engine.create_template(
        template_id="progress_update",
        version="1.0.0",
        name="Progress Update",
        description="Progress update template",
        pattern="Progress: {{ current }} of {{ total }} ({{ percentage }}%)",
        response_type=ResponseType.PROGRESS,
        variables={
            "current": VariableSpec(name="current", var_type=VariableType.INTEGER, description="Current progress"),
            "total": VariableSpec(name="total", var_type=VariableType.INTEGER, description="Total items"),
            "percentage": VariableSpec(
                name="percentage", var_type=VariableType.INTEGER, description="Percentage complete"
            ),
        },
    )

    # Decision template
    engine.create_template(
        template_id="decision_request",
        version="1.0.0",
        name="Decision Request",
        description="Request user decision template",
        pattern="{{ question }} Options: {{ options }}",
        response_type=ResponseType.DECISION,
        variables={
            "question": VariableSpec(name="question", var_type=VariableType.STRING, description="Decision question"),
            "options": VariableSpec(name="options", var_type=VariableType.LIST, description="Available options"),
        },
    )

    # Warning template
    engine.create_template(
        template_id="warning_alert",
        version="1.0.0",
        name="Warning Alert",
        description="Warning message template",
        pattern="⚠️ Warning: {{ message }}",
        response_type=ResponseType.WARNING,
        variables={
            "message": VariableSpec(name="message", var_type=VariableType.STRING, description="Warning message"),
        },
    )
