"""
Response Template System with Inheritance Support

Provides template loading, caching, and rendering capabilities for
domain-specific response templates. Templates support inheritance from
base templates and variable substitution.

Classes:
    TemplateVariable: Type-safe template variable definition
    TemplateDefinition: Dataclass representing a single template
    DomainTemplateMetadata: Metadata for a domain's templates
    ResponseTemplateRegistry: Singleton registry for all templates
    ResponseTemplateLoader: Loads templates from YAML files
    ResponseTemplateEngine: Renders templates with variable substitution
"""

import os
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from pathlib import Path
import yaml
from functools import lru_cache


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class TemplateVariable:
    """Represents a template variable with type and validation information."""
    
    name: str
    var_type: str  # "string", "integer", "number", "boolean"
    required: bool
    example: Optional[str] = None
    description: Optional[str] = None
    
    def __post_init__(self):
        """Validate variable definition."""
        valid_types = {"string", "integer", "number", "boolean"}
        if self.var_type not in valid_types:
            raise ValueError(f"Invalid variable type: {self.var_type}. Must be one of {valid_types}")


@dataclass
class TemplateDefinition:
    """Represents a template with metadata and content."""
    
    id: str  # e.g., "tdd.test.execution_complete"
    name: str
    description: str
    template: str  # The template string with {variable} placeholders
    variables: List[TemplateVariable]
    severity: str  # "INFO", "WARNING", "ERROR"
    category: str  # e.g., "test_results", "phase_tracking"
    inherits_from: Optional[str] = None  # Template ID to inherit from
    
    @property
    def domain(self) -> str:
        """Extract domain from template ID (first part before dot)."""
        return self.id.split('.')[0]
    
    @property
    def required_variables(self) -> List[str]:
        """Get list of required variable names."""
        return [v.name for v in self.variables if v.required]
    
    @property
    def optional_variables(self) -> List[str]:
        """Get list of optional variable names."""
        return [v.name for v in self.variables if not v.required]
    
    def validate_context(self, context: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate that context provides all required variables with correct types.
        
        Args:
            context: Dictionary of variable values
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check required variables
        for var in self.variables:
            if var.required and var.name not in context:
                errors.append(f"Missing required variable: {var.name}")
        
        # Check types
        for var in self.variables:
            if var.name in context:
                value = context[var.name]
                if not self._check_type(value, var.var_type):
                    errors.append(f"Variable {var.name} has wrong type. Expected {var.var_type}, got {type(value).__name__}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def _check_type(value: Any, expected_type: str) -> bool:
        """Check if value matches expected type."""
        type_map = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
        }
        expected = type_map.get(expected_type)
        if expected is None:
            return True
        return isinstance(value, expected)


@dataclass
class DomainTemplateMetadata:
    """Metadata for a domain's template collection."""
    
    domain_id: str
    description: str
    templates: Dict[str, TemplateDefinition] = field(default_factory=dict)
    
    def get_template_by_name(self, template_name: str) -> Optional[TemplateDefinition]:
        """Get template by its short name (e.g., 'test_execution_complete')."""
        for template in self.templates.values():
            if template.name.lower() == template_name.lower():
                return template
        return None


# =============================================================================
# REGISTRY (SINGLETON)
# =============================================================================

class ResponseTemplateRegistry:
    """
    Singleton registry for all response templates.
    
    Provides O(1) lookup of templates by:
    - Template ID (fully qualified)
    - Domain + template name
    - Category
    
    Implements template inheritance resolution.
    """
    
    _instance: Optional['ResponseTemplateRegistry'] = None
    
    def __init__(self):
        """Initialize registry with empty collections."""
        self.base_templates: Dict[str, TemplateDefinition] = {}
        self.domain_templates: Dict[str, DomainTemplateMetadata] = {}
        self._template_id_index: Dict[str, TemplateDefinition] = {}
        self._category_index: Dict[str, List[TemplateDefinition]] = {}
        self._is_initialized = False
    
    @classmethod
    def get_instance(cls) -> 'ResponseTemplateRegistry':
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def add_base_template(self, template: TemplateDefinition) -> None:
        """Add a base template to the registry."""
        self.base_templates[template.id] = template
        self._index_template(template)
    
    def add_domain_template(self, domain_id: str, template: TemplateDefinition) -> None:
        """Add a domain-specific template to the registry."""
        if domain_id not in self.domain_templates:
            self.domain_templates[domain_id] = DomainTemplateMetadata(domain_id, f"{domain_id} templates")
        
        self.domain_templates[domain_id].templates[template.id] = template
        self._index_template(template)
    
    def _index_template(self, template: TemplateDefinition) -> None:
        """Index template by ID and category for O(1) lookups."""
        self._template_id_index[template.id] = template
        
        if template.category not in self._category_index:
            self._category_index[template.category] = []
        self._category_index[template.category].append(template)
    
    def get_template(self, domain_id: str, template_name: str) -> Optional[TemplateDefinition]:
        """
        Get template with inheritance resolution.
        
        Resolution order:
        1. Check domain-specific templates
        2. Check base templates
        3. Resolve inheritance chain
        
        Args:
            domain_id: Domain identifier (e.g., "tdd", "planning")
            template_name: Template name (e.g., "test_execution_complete")
        
        Returns:
            TemplateDefinition or None if not found
        """
        # Try domain-specific first
        if domain_id in self.domain_templates:
            domain_meta = self.domain_templates[domain_id]
            template = domain_meta.get_template_by_name(template_name)
            if template:
                return self._resolve_inheritance(template)
        
        # Try base templates
        for template in self.base_templates.values():
            if template.name.lower() == template_name.lower():
                return self._resolve_inheritance(template)
        
        return None
    
    def get_template_by_id(self, template_id: str) -> Optional[TemplateDefinition]:
        """Get template by fully qualified ID (O(1) lookup)."""
        return self._template_id_index.get(template_id)
    
    def get_templates_by_category(self, category: str) -> List[TemplateDefinition]:
        """Get all templates in a category."""
        return self._category_index.get(category, [])
    
    def get_templates_for_domain(self, domain_id: str) -> List[TemplateDefinition]:
        """Get all templates for a domain."""
        if domain_id not in self.domain_templates:
            return []
        return list(self.domain_templates[domain_id].templates.values())
    
    def _resolve_inheritance(self, template: TemplateDefinition) -> TemplateDefinition:
        """
        Resolve template inheritance chain.
        
        If template has 'inherits_from', load parent and merge.
        Merge strategy:
        - Child template overrides parent
        - Child variables extend parent variables
        """
        if not template.inherits_from:
            return template
        
        parent = self.get_template_by_id(template.inherits_from)
        if not parent:
            return template  # Parent not found, return child as-is
        
        # Merge: parent variables + child variables (child wins on conflicts)
        merged_vars = {v.name: v for v in parent.variables}
        merged_vars.update({v.name: v for v in template.variables})
        
        # Create merged template
        return TemplateDefinition(
            id=template.id,
            name=template.name,
            description=template.description,
            template=template.template,  # Child template overrides
            variables=list(merged_vars.values()),
            severity=template.severity,
            category=template.category,
            inherits_from=template.inherits_from
        )
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get registry statistics."""
        return {
            "base_templates_count": len(self.base_templates),
            "domain_templates_count": sum(len(m.templates) for m in self.domain_templates.values()),
            "total_templates": len(self._template_id_index),
            "domains": list(self.domain_templates.keys()),
            "categories": list(self._category_index.keys()),
            "templates_with_inheritance": len([
                t for t in self._template_id_index.values() if t.inherits_from
            ])
        }
    
    def clear(self) -> None:
        """Clear all templates (mainly for testing)."""
        self.base_templates.clear()
        self.domain_templates.clear()
        self._template_id_index.clear()
        self._category_index.clear()


# =============================================================================
# LOADER
# =============================================================================

class ResponseTemplateLoader:
    """Loads response templates from YAML files."""
    
    @staticmethod
    def load_from_file(yaml_path: str) -> tuple[Dict[str, TemplateDefinition], Dict[str, Dict[str, TemplateDefinition]]]:
        """
        Load templates from YAML file.
        
        Args:
            yaml_path: Path to response-templates.yaml
        
        Returns:
            Tuple of (base_templates, domain_templates)
        
        Raises:
            FileNotFoundError: If YAML file not found
            yaml.YAMLError: If YAML parsing fails
            ValueError: If template structure is invalid
        """
        if not os.path.exists(yaml_path):
            raise FileNotFoundError(f"Template file not found: {yaml_path}")
        
        with open(yaml_path, 'r') as f:
            try:
                data = yaml.safe_load(f)
            except yaml.YAMLError as e:
                raise yaml.YAMLError(f"Error parsing template YAML: {e}")
        
        if not data:
            raise ValueError("Empty template file")
        
        base_templates = ResponseTemplateLoader._load_base_templates(data)
        domain_templates = ResponseTemplateLoader._load_domain_templates(data)
        
        return base_templates, domain_templates
    
    @staticmethod
    def _load_base_templates(data: Dict[str, Any]) -> Dict[str, TemplateDefinition]:
        """Load base templates from YAML data."""
        templates = {}
        
        if 'base_templates' not in data:
            return templates
        
        base_data = data['base_templates']
        
        for template_id, template_data in base_data.items():
            try:
                variables = ResponseTemplateLoader._parse_variables(template_data.get('variables', []))
                
                template = TemplateDefinition(
                    id=template_data.get('id', template_id),
                    name=template_data.get('name', template_id),
                    description=template_data.get('description', ''),
                    template=template_data.get('template', ''),
                    variables=variables,
                    severity=template_data.get('severity', 'INFO'),
                    category=template_data.get('category', 'general'),
                    inherits_from=template_data.get('inherits_from')
                )
                
                templates[template.id] = template
            
            except Exception as e:
                raise ValueError(f"Error parsing base template {template_id}: {e}")
        
        return templates
    
    @staticmethod
    def _load_domain_templates(data: Dict[str, Any]) -> Dict[str, Dict[str, TemplateDefinition]]:
        """Load domain templates from YAML data."""
        domain_templates = {}
        
        if 'domain_templates' not in data:
            return domain_templates
        
        domain_data = data['domain_templates']
        
        for domain_id, domain_info in domain_data.items():
            domain_templates[domain_id] = {}
            
            if 'templates' not in domain_info:
                continue
            
            for template_key, template_data in domain_info['templates'].items():
                try:
                    variables = ResponseTemplateLoader._parse_variables(template_data.get('variables', []))
                    
                    template = TemplateDefinition(
                        id=template_data.get('id', template_key),
                        name=template_data.get('name', template_key),
                        description=template_data.get('description', ''),
                        template=template_data.get('template', ''),
                        variables=variables,
                        severity=template_data.get('severity', 'INFO'),
                        category=template_data.get('category', 'general'),
                        inherits_from=template_data.get('inherits_from')
                    )
                    
                    domain_templates[domain_id][template.id] = template
                
                except Exception as e:
                    raise ValueError(f"Error parsing domain template {template_key} in {domain_id}: {e}")
        
        return domain_templates
    
    @staticmethod
    def _parse_variables(variables_data: List[Dict[str, Any]]) -> List[TemplateVariable]:
        """Parse variables from template data."""
        variables = []
        
        for var_data in variables_data:
            var = TemplateVariable(
                name=var_data.get('name', ''),
                var_type=var_data.get('type', 'string'),
                required=var_data.get('required', False),
                example=var_data.get('example'),
                description=var_data.get('description')
            )
            variables.append(var)
        
        return variables


# =============================================================================
# ENGINE
# =============================================================================

class ResponseTemplateEngine:
    """Renders templates with variable substitution and caching."""
    
    def __init__(self, registry: Optional[ResponseTemplateRegistry] = None):
        """
        Initialize engine.
        
        Args:
            registry: Template registry (defaults to singleton)
        """
        self.registry = registry or ResponseTemplateRegistry.get_instance()
        self._render_cache: Dict[str, str] = {}
    
    def render(self, domain_id: str, template_name: str, context: Dict[str, Any]) -> str:
        """
        Render a template with provided context.
        
        Args:
            domain_id: Domain identifier
            template_name: Template name
            context: Variable values for substitution
        
        Returns:
            Rendered template string
        
        Raises:
            ValueError: If template not found or validation fails
        """
        # Get template (with inheritance resolution)
        template = self.registry.get_template(domain_id, template_name)
        if not template:
            # Try with just template_name as ID
            template = self.registry.get_template_by_id(template_name)
            if not template:
                raise ValueError(f"Template not found: {domain_id}.{template_name}")
        
        # Validate context
        is_valid, errors = template.validate_context(context)
        if not is_valid:
            raise ValueError(f"Template validation failed: {'; '.join(errors)}")
        
        # Render
        return self._render_template(template, context)
    
    def render_by_id(self, template_id: str, context: Dict[str, Any]) -> str:
        """
        Render template by fully qualified ID.
        
        Args:
            template_id: Fully qualified template ID
            context: Variable values for substitution
        
        Returns:
            Rendered template string
        """
        template = self.registry.get_template_by_id(template_id)
        if not template:
            raise ValueError(f"Template not found: {template_id}")
        
        is_valid, errors = template.validate_context(context)
        if not is_valid:
            raise ValueError(f"Template validation failed: {'; '.join(errors)}")
        
        return self._render_template(template, context)
    
    def _render_template(self, template: TemplateDefinition, context: Dict[str, Any]) -> str:
        """
        Render template with variable substitution.
        
        Replaces {variable_name} with context values.
        Optional variables render as empty string if missing.
        """
        rendered = template.template
        
        # Replace variables
        for var in template.variables:
            placeholder = f"{{{var.name}}}"
            
            if var.name in context:
                value = context[var.name]
                # Convert value to string for substitution
                replacement = str(value)
            elif not var.required:
                # Optional variable not provided, remove it
                replacement = ""
            else:
                # Required variable not provided (should have been caught in validation)
                replacement = ""
            
            rendered = rendered.replace(placeholder, replacement)
        
        return rendered
    
    @lru_cache(maxsize=128)
    def get_template_info(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Get template information (cached)."""
        template = self.registry.get_template_by_id(template_id)
        if not template:
            return None
        
        return {
            "id": template.id,
            "name": template.name,
            "description": template.description,
            "domain": template.domain,
            "category": template.category,
            "severity": template.severity,
            "required_variables": template.required_variables,
            "optional_variables": template.optional_variables,
            "inherits_from": template.inherits_from
        }
    
    def clear_cache(self) -> None:
        """Clear template info cache."""
        self._render_cache.clear()
        self.get_template_info.cache_clear()


# =============================================================================
# POPULATOR (High-level interface)
# =============================================================================

class ResponseTemplatePopulator:
    """High-level interface for loading templates and initializing engine."""
    
    @staticmethod
    def populate_from_file(yaml_path: str) -> ResponseTemplateEngine:
        """
        Load templates from YAML and initialize engine.
        
        Args:
            yaml_path: Path to response-templates.yaml
        
        Returns:
            Initialized ResponseTemplateEngine
        
        Example:
            engine = ResponseTemplatePopulator.populate_from_file(
                "/path/to/response-templates.yaml"
            )
            rendered = engine.render("tdd", "test_execution_complete", context)
        """
        # Load templates
        base_templates, domain_templates = ResponseTemplateLoader.load_from_file(yaml_path)
        
        # Get registry
        registry = ResponseTemplateRegistry.get_instance()
        registry.clear()  # Clear any existing templates
        
        # Register base templates
        for template in base_templates.values():
            registry.add_base_template(template)
        
        # Register domain templates
        for domain_id, templates in domain_templates.items():
            for template in templates.values():
                registry.add_domain_template(domain_id, template)
        
        # Initialize and return engine
        return ResponseTemplateEngine(registry)
    
    @staticmethod
    def get_registry() -> ResponseTemplateRegistry:
        """Get the singleton registry instance."""
        return ResponseTemplateRegistry.get_instance()
