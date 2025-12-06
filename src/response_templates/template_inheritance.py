"""
Template Inheritance Engine

This module implements multi-level template inheritance, allowing templates
to inherit from base templates and override specific sections.

Architecture:
- Supports 3-level inheritance (template → base → components)
- Override mechanism for sections and components
- Inheritance chain resolution
- Circular inheritance detection

Inheritance Pattern:
    child_template:
      inherits: base_templates/5-part-standard.yaml
      sections:
        understanding: "Custom understanding"
        response: "Custom response"
      components:
        header: core/components/headers.yaml#custom_header

Author: Asif Hussain
Phase: 2 - Core Infrastructure
Version: 1.0
Created: December 5, 2025
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List, Set
import logging
from copy import deepcopy

from .component_registry import ComponentRegistry

logger = logging.getLogger(__name__)


class TemplateInheritanceError(Exception):
    """Raised when template inheritance fails."""
    pass


class CircularInheritanceError(TemplateInheritanceError):
    """Raised when circular inheritance is detected."""
    pass


class TemplateInheritance:
    """
    Multi-level template inheritance engine.
    
    Features:
    - Inherit from base templates
    - Override sections and components
    - Resolve inheritance chains
    - Detect circular inheritance
    - Merge nested dictionaries
    
    Inheritance Directive Format:
        template_id:
          inherits: path/to/base_template.yaml  # or template_id
          sections:
            section_name: "Override content"
          components:
            component_name: "path/to/component.yaml#id"
    
    Usage:
        engine = TemplateInheritance(
            template_dir=Path("cortex-brain/response-templates"),
            component_registry=ComponentRegistry(...)
        )
        
        resolved = engine.resolve_inheritance(template_def)
    """
    
    def __init__(
        self,
        template_dir: Path,
        component_registry: ComponentRegistry
    ):
        """
        Initialize template inheritance engine.
        
        Args:
            template_dir: Base directory for templates
            component_registry: Component registry for resolving component references
        """
        self.template_dir = template_dir
        self.component_registry = component_registry
        
        # Cache for loaded base templates
        self.base_template_cache: Dict[str, Dict[str, Any]] = {}
        
        logger.info(f"TemplateInheritance initialized: {template_dir}")
    
    def resolve_inheritance(
        self,
        template_def: Dict[str, Any],
        visited: Optional[Set[str]] = None
    ) -> Dict[str, Any]:
        """
        Resolve template inheritance chain.
        
        Args:
            template_def: Template definition (may contain 'inherits' directive)
            visited: Set of visited template IDs (for circular detection)
        
        Returns:
            Fully resolved template with inheritance applied
        
        Raises:
            CircularInheritanceError: If circular inheritance detected
            TemplateInheritanceError: If inheritance resolution fails
        """
        # Initialize visited set
        if visited is None:
            visited = set()
        
        # Check if template has inheritance
        if 'inherits' not in template_def:
            # No inheritance - return as-is
            return deepcopy(template_def)
        
        inherits_from = template_def['inherits']
        
        # Circular inheritance detection
        if inherits_from in visited:
            raise CircularInheritanceError(
                f"Circular inheritance detected: {inherits_from} already in chain"
            )
        
        visited.add(inherits_from)
        
        # Load base template
        base_template = self._load_base_template(inherits_from)
        
        if base_template is None:
            raise TemplateInheritanceError(
                f"Base template not found: {inherits_from}"
            )
        
        # Recursively resolve base template's inheritance
        base_resolved = self.resolve_inheritance(base_template, visited.copy())
        
        # Merge child template over base template
        result = self._merge_templates(base_resolved, template_def)
        
        # Remove inheritance directive from result
        result.pop('inherits', None)
        
        return result
    
    def _load_base_template(self, reference: str) -> Optional[Dict[str, Any]]:
        """
        Load base template from file or cache.
        
        Args:
            reference: Template reference (file path or template ID)
        
        Returns:
            Base template definition or None if not found
        """
        # Check cache first
        if reference in self.base_template_cache:
            logger.debug(f"Base template cache HIT: {reference}")
            return deepcopy(self.base_template_cache[reference])
        
        logger.debug(f"Base template cache MISS: {reference}")
        
        # Determine if reference is file path or template ID
        if reference.endswith('.yaml'):
            # File path reference
            file_path = self.template_dir / reference
        else:
            # Template ID reference - need to look up file
            # For now, assume it's in base-templates/
            file_path = self.template_dir / 'core' / 'base-templates' / f"{reference}.yaml"
        
        if not file_path.exists():
            logger.error(f"Base template file not found: {file_path}")
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = yaml.safe_load(f)
            
            # Cache base template
            self.base_template_cache[reference] = content
            
            logger.info(f"Base template loaded: {reference}")
            return deepcopy(content)
        
        except Exception as e:
            logger.error(f"Failed to load base template {reference}: {e}")
            return None
    
    def _merge_templates(
        self,
        base: Dict[str, Any],
        child: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Merge child template over base template.
        
        Merging rules:
        - Child sections override base sections
        - Child components override base components
        - Other keys: child overrides base (shallow merge)
        - Nested dicts: deep merge
        
        Args:
            base: Base template (fully resolved)
            child: Child template (with overrides)
        
        Returns:
            Merged template
        """
        result = deepcopy(base)
        
        for key, value in child.items():
            if key == 'inherits':
                # Skip inheritance directive
                continue
            
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                # Deep merge dictionaries
                result[key] = self._deep_merge(result[key], value)
            else:
                # Override with child value
                result[key] = deepcopy(value)
        
        return result
    
    def _deep_merge(
        self,
        base: Dict[str, Any],
        override: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Deep merge two dictionaries.
        
        Args:
            base: Base dictionary
            override: Override dictionary
        
        Returns:
            Merged dictionary (override takes precedence)
        """
        result = deepcopy(base)
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                # Recursively merge nested dicts
                result[key] = self._deep_merge(result[key], value)
            else:
                # Override with new value
                result[key] = deepcopy(value)
        
        return result
    
    def resolve_with_components(
        self,
        template_def: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Resolve template inheritance AND component references.
        
        This is a convenience method that combines inheritance resolution
        with component resolution.
        
        Args:
            template_def: Template definition
            context: Context for placeholder substitution
        
        Returns:
            Fully resolved template with components
        """
        # First resolve inheritance
        resolved = self.resolve_inheritance(template_def)
        
        # Then resolve component references
        resolved = self._resolve_components_in_template(resolved, context)
        
        return resolved
    
    def _resolve_components_in_template(
        self,
        template: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Resolve component references in template.
        
        Looks for 'components' key and resolves each component reference.
        """
        if 'components' not in template:
            return template
        
        components_def = template.get('components', {})
        
        # Resolve each component
        for component_name, component_ref in components_def.items():
            if isinstance(component_ref, str):
                # It's a component reference
                resolved_component = self.component_registry.resolve_component(
                    component_ref,
                    context
                )
                
                if resolved_component is not None:
                    # Replace reference with resolved content
                    template['components'][component_name] = resolved_component
        
        return template
    
    def validate_inheritance_chain(
        self,
        template_def: Dict[str, Any]
    ) -> tuple[bool, Optional[str]]:
        """
        Validate template inheritance chain.
        
        Checks:
        - No circular inheritance
        - All base templates exist
        - Inheritance chain is valid
        
        Args:
            template_def: Template definition to validate
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Try to resolve inheritance
            self.resolve_inheritance(template_def)
            return True, None
        
        except CircularInheritanceError as e:
            return False, f"Circular inheritance: {str(e)}"
        
        except TemplateInheritanceError as e:
            return False, f"Inheritance error: {str(e)}"
        
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"
    
    def get_inheritance_chain(
        self,
        template_def: Dict[str, Any]
    ) -> List[str]:
        """
        Get inheritance chain for template.
        
        Args:
            template_def: Template definition
        
        Returns:
            List of template IDs in inheritance chain (child to parent)
        """
        chain = []
        current = template_def
        
        while 'inherits' in current:
            inherits_from = current['inherits']
            chain.append(inherits_from)
            
            # Load base template
            base = self._load_base_template(inherits_from)
            if base is None:
                break
            
            current = base
        
        return chain
    
    def clear_cache(self):
        """Clear base template cache."""
        count = len(self.base_template_cache)
        self.base_template_cache.clear()
        logger.info(f"Base template cache cleared: {count} templates")
    
    def get_cache_size(self) -> int:
        """Get number of cached base templates."""
        return len(self.base_template_cache)
