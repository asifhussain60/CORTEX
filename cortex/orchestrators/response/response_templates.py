"""Response Template System (AC-RESP-003-01).

Author: CORTEX Framework
Date: 2025
Version: 1.0.0
"""

import hashlib
import re
from collections import OrderedDict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from cortex.models.canonical_enums import ResponseType, VariableType


@dataclass
class VariableSpec:
    """Template variable specification.

    Attributes:
        name: Variable name
        var_type: Variable type
        required: Whether variable is required
        description: Variable description
        default: Default value if not provided
        pattern: Regex pattern for string validation
    """
    name: str
    var_type: VariableType
    required: bool = True
    description: str = ""
    default: Any = None
    pattern: Optional[str] = None

    def validate(self, value: Any) -> bool:
        """Validate a variable value.

        Args:
            value: Value to validate

        Returns:
            True if valid, False otherwise
        """
        # None is valid if not required or has default
        if value is None:
            return not self.required or self.default is not None

        # Type checking
        if self.var_type == VariableType.STRING:
            if not isinstance(value, str):
                return False
            # Pattern validation for strings
            if self.pattern:
                return bool(re.match(self.pattern, value))
            return True
        elif self.var_type == VariableType.INTEGER:
            # Must be int, not bool (bool is subclass of int in Python)
            return isinstance(value, int) and not isinstance(value, bool)
        elif self.var_type == VariableType.BOOLEAN:
            return isinstance(value, bool)
        elif self.var_type == VariableType.LIST:
            return isinstance(value, list)
        elif self.var_type == VariableType.OPTIONAL:
            return True  # Any type accepted

        return False




@dataclass
class ResponseTemplate:
    """Response template structure.

    Attributes:
        template_id: Unique template identifier
        version: Template version
        name: Template name
        description: Template description
        pattern: Template pattern with {{ variable }} placeholders
        response_type: Type of response
        variables: Variable specifications
    """
    template_id: str
    version: str
    name: str
    description: str
    pattern: str
    response_type: ResponseType
    variables: Dict[str, VariableSpec] = field(default_factory=dict)

    def validate_variables(self, provided: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate provided variables against specifications.

        Args:
            provided: Dictionary of provided variables

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        # Check required variables
        for var_name, var_spec in self.variables.items():
            if var_spec.required and var_name not in provided:
                errors.append(f"Missing required variable: {var_name}")
                continue

            # Validate type if provided
            if var_name in provided:
                value = provided[var_name]
                if not var_spec.validate(value):
                    errors.append(
                        f"Invalid type for variable '{var_name}': "
                        f"expected {var_spec.var_type.value}, got {type(value).__name__}"
                    )

        # Check for unexpected variables
        for var_name in provided:
            if var_name not in self.variables:
                errors.append(f"Unexpected variable: {var_name}")

        return (len(errors) == 0, errors)


class ResponseTemplateRegistry:
    """Registry for response templates.

    Manages template storage, versioning, and retrieval.

    Attributes:
        templates: Dictionary of template_id:version -> template
    """

    def __init__(self) -> None:
        """Initialize the template registry."""
        self.templates: Dict[str, ResponseTemplate] = {}

    def register(self, template: ResponseTemplate) -> None:
        """Register a template.

        Args:
            template: Template to register
        """
        key = f"{template.template_id}:{template.version}"
        self.templates[key] = template

    def get(
        self,
        template_id: str,
        version: Optional[str] = None
    ) -> Optional[ResponseTemplate]:
        """Get a template by ID and optional version.

        Args:
            template_id: Template identifier
            version: Optional specific version (gets latest if not specified)

        Returns:
            Template if found, None otherwise
        """
        if version:
            key = f"{template_id}:{version}"
            return self.templates.get(key)

        # Get latest version
        matching = [
            t for k, t in self.templates.items()
            if k.startswith(f"{template_id}:")
        ]

        if not matching:
            return None

        # Sort by version and return latest
        matching.sort(key=lambda t: t.version, reverse=True)
        return matching[0]

    def list_templates(
        self,
        response_type: Optional[ResponseType] = None
    ) -> List[ResponseTemplate]:
        """List all templates, optionally filtered by type.

        Args:
            response_type: Optional type filter

        Returns:
            List of templates
        """
        templates = list(self.templates.values())

        if response_type:
            templates = [t for t in templates if t.response_type == response_type]

        return templates

    def unregister(self, template_id: str) -> None:
        """Unregister all versions of a template.

        Args:
            template_id: Template identifier
        """
        keys_to_remove = [
            k for k in self.templates.keys()
            if k.startswith(f"{template_id}:")
        ]
        for key in keys_to_remove:
            del self.templates[key]


class SimpleTemplateSubstitutor:
    """Simple template variable substitution.

    Handles {{ variable }} style placeholders.
    """

    @staticmethod
    def substitute(pattern: str, variables: Dict[str, Any]) -> str:
        """Substitute variables in template pattern.

        Args:
            pattern: Template pattern with {{ variable }} placeholders
            variables: Dictionary of variable values

        Returns:
            Substituted string
        """
        result = pattern

        # Match {{ variable_name }} with optional whitespace
        placeholder_pattern = r'\{\{\s*(\w+)\s*\}\}'

        def replacer(match: re.Match) -> str:
            var_name = match.group(1)
            if var_name in variables:
                value = variables[var_name]
                # Convert None to empty string
                if value is None:
                    return ""
                return str(value)
            # Leave placeholder unchanged if variable not provided
            return match.group(0)

        result = re.sub(placeholder_pattern, replacer, result)
        return result


class TemplateCache:
    """Cache for rendered templates.

    LRU cache with configurable maximum entries.

    Attributes:
        max_entries: Maximum number of cache entries
        cache: Ordered dictionary for LRU behavior
    """

    def __init__(self, max_entries: int = 100) -> None:
        """Initialize the template cache.

        Args:
            max_entries: Maximum number of cache entries
        """
        self.max_entries = max_entries
        self.cache: OrderedDict[str, Any] = OrderedDict()

    def get(self, key: str) -> Optional[Any]:
        """Get a cached value.

        Args:
            key: Cache key

        Returns:
            Cached value if present, None otherwise
        """
        if key in self.cache:
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            return self.cache[key]
        return None

    def set(self, key: str, value: Any) -> None:
        """Set a cache value.

        Args:
            key: Cache key
            value: Value to cache
        """
        if key in self.cache:
            # Move to end
            self.cache.move_to_end(key)
        else:
            # Add new entry
            self.cache[key] = value
            # Evict oldest if over limit
            if len(self.cache) > self.max_entries:
                self.cache.popitem(last=False)

    def clear(self) -> None:
        """Clear all cache entries."""
        self.cache.clear()


class TemplateEngine:
    """Main template rendering engine.

    Provides template creation, validation, and rendering with caching.

    Attributes:
        registry: Template registry
        cache: Render cache
        substitutor: Variable substitutor
    """

    def __init__(self) -> None:
        """Initialize the template engine."""
        self.registry = ResponseTemplateRegistry()
        self.cache = TemplateCache()
        self.substitutor = SimpleTemplateSubstitutor()
        self._load_default_templates()

    def create_template(
        self,
        template_id: str,
        version: str,
        name: str,
        description: str,
        pattern: str,
        response_type: ResponseType,
        variables: Optional[Dict[str, VariableSpec]] = None
    ) -> ResponseTemplate:
        """Create and register a new template.

        Args:
            template_id: Unique template identifier
            version: Template version
            name: Template name
            description: Template description
            pattern: Template pattern with placeholders
            response_type: Type of response
            variables: Variable specifications

        Returns:
            Created template
        """
        template = ResponseTemplate(
            template_id=template_id,
            version=version,
            name=name,
            description=description,
            pattern=pattern,
            response_type=response_type,
            variables=variables or {}
        )
        self.registry.register(template)
        return template

    def apply_template(
        self,
        template_id: str,
        variables: Dict[str, Any],
        version: Optional[str] = None
    ) -> str:
        """Apply a template with variables.

        Args:
            template_id: Template identifier
            variables: Variable values
            version: Optional specific version

        Returns:
            Rendered template string

        Raises:
            ValueError: If template not found or variables invalid
        """
        # Check cache first
        cache_key = self._make_cache_key(template_id, variables, version)
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        # Get template
        template = self.registry.get(template_id, version)
        if not template:
            raise ValueError(f"Template '{template_id}' not found")

        # Apply defaults for missing optional variables
        final_variables = {}
        for var_name, var_spec in template.variables.items():
            if var_name in variables:
                final_variables[var_name] = variables[var_name]
            elif not var_spec.required and var_spec.default is not None:
                final_variables[var_name] = var_spec.default

        # Also include any extra provided variables
        for var_name, value in variables.items():
            if var_name not in final_variables:
                final_variables[var_name] = value

        # Validate variables
        is_valid, errors = template.validate_variables(final_variables)
        if not is_valid:
            raise ValueError(f"Invalid variables for template '{template_id}': {'; '.join(errors)}")

        # Render
        result = self.substitutor.substitute(template.pattern, final_variables)

        # Cache result
        self.cache.set(cache_key, result)

        return result

    def get_template(
        self,
        template_id: str,
        version: Optional[str] = None
    ) -> Optional[ResponseTemplate]:
        """Get a template.

        Args:
            template_id: Template identifier
            version: Optional specific version

        Returns:
            Template if found, None otherwise
        """
        return self.registry.get(template_id, version)

    def list_templates(
        self,
        response_type: Optional[ResponseType] = None
    ) -> List[ResponseTemplate]:
        """List templates.

        Args:
            response_type: Optional type filter

        Returns:
            List of templates
        """
        return self.registry.list_templates(response_type)

    def unregister_template(self, template_id: str) -> None:
        """Unregister a template.

        Args:
            template_id: Template identifier
        """
        self.registry.unregister(template_id)

    def clear_cache(self) -> None:
        """Clear the render cache."""
        self.cache.clear()

    def _make_cache_key(
        self,
        template_id: str,
        variables: Dict[str, Any],
        version: Optional[str]
    ) -> str:
        """Generate cache key.

        Args:
            template_id: Template identifier
            variables: Variable values
            version: Optional version

        Returns:
            Cache key string
        """
        var_str = str(sorted(variables.items()))
        key_data = f"{template_id}:{version}:{var_str}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def _load_default_templates(self) -> None:
        """Load default built-in templates."""
        # Error processing template
        self.create_template(
            template_id="error_processing",
            version="1.0.0",
            name="Error Processing",
            description="For processing errors",
            pattern="Error processing {{ item }}: {{ reason }}",
            response_type=ResponseType.ERROR,
            variables={
                "item": VariableSpec(name="item", var_type=VariableType.STRING),
                "reason": VariableSpec(name="reason", var_type=VariableType.STRING)
            }
        )

        # Success message template
        self.create_template(
            template_id="operation_success",
            version="1.0.0",
            name="Operation Success",
            description="For successful operations",
            pattern="✓ {{ operation }} completed successfully",
            response_type=ResponseType.SUCCESS,
            variables={
                "operation": VariableSpec(name="operation", var_type=VariableType.STRING)
            }
        )

        # Success completion template
        self.create_template(
            template_id="success_completion",
            version="1.0.0",
            name="Success Completion",
            description="For successful action completion",
            pattern="Successfully {{ action }} {{ item }}",
            response_type=ResponseType.SUCCESS,
            variables={
                "action": VariableSpec(name="action", var_type=VariableType.STRING),
                "item": VariableSpec(name="item", var_type=VariableType.STRING)
            }
        )

        # Informational template
        self.create_template(
            template_id="status_update",
            version="1.0.0",
            name="Status Update",
            description="For status updates",
            pattern="Status: {{ status }} - {{ message }}",
            response_type=ResponseType.INFORMATIONAL,
            variables={
                "status": VariableSpec(name="status", var_type=VariableType.STRING),
                "message": VariableSpec(name="message", var_type=VariableType.STRING)
            }
        )

        # Warning template
        self.create_template(
            template_id="warning_message",
            version="1.0.0",
            name="Warning Message",
            description="For warnings",
            pattern="⚠ Warning: {{ warning }}",
            response_type=ResponseType.WARNING,
            variables={
                "warning": VariableSpec(name="warning", var_type=VariableType.STRING)
            }
        )

        # Progress template
        self.create_template(
            template_id="progress_update",
            version="1.0.0",
            name="Progress Update",
            description="For progress updates",
            pattern="Progress: {{ current }}/{{ total }} ({{ percentage }}%)",
            response_type=ResponseType.INFORMATIONAL,
            variables={
                "current": VariableSpec(name="current", var_type=VariableType.INTEGER),
                "total": VariableSpec(name="total", var_type=VariableType.INTEGER),
                "percentage": VariableSpec(name="percentage", var_type=VariableType.INTEGER)
            }
        )


# Singleton instance
_template_engine: Optional[TemplateEngine] = None


def get_template_engine() -> TemplateEngine:
    """Get the singleton template engine instance.

    Returns:
        Template engine with default templates loaded
    """
    global _template_engine
    if _template_engine is None:
        _template_engine = TemplateEngine()
    return _template_engine


__all__ = [
    "VariableType",
    "VariableSpec",
    "ResponseType",
    "ResponseTemplate",
    "TemplateRegistry",
    "SimpleTemplateSubstitutor",
    "TemplateCache",
    "TemplateEngine",
    "get_template_engine"
]
