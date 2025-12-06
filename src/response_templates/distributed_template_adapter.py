"""
Integration Adapter for Phase 4: LazyTemplateLoader Bridge

This adapter integrates the new distributed template system (Phase 2-3)
with the existing ResponseTemplateManager (Phase 5.x) infrastructure.

Provides seamless transition from monolithic to distributed templates
while maintaining full backward compatibility.

Author: Asif Hussain
Phase: 4 - Integration & Testing
Version: 1.0
Created: December 5, 2025
"""

from pathlib import Path
from typing import Dict, Any, Optional
import logging

from .lazy_template_loader import LazyTemplateLoader
from .template_inheritance import TemplateInheritance
from .component_registry import ComponentRegistry

logger = logging.getLogger(__name__)


class DistributedTemplateAdapter:
    """
    Adapter between distributed template system and existing infrastructure.
    
    Features:
    - Loads templates from distributed structure via LazyTemplateLoader
    - Resolves template inheritance via TemplateInheritance
    - Resolves component references via ComponentRegistry
    - Maintains backward compatibility with existing API
    - Graceful fallback to monolithic file
    
    Usage:
        adapter = DistributedTemplateAdapter()
        template = adapter.get_template('planning')
        # Returns fully resolved template with inheritance and components
    """
    
    def __init__(
        self,
        template_dir: Optional[Path] = None,
        registry_file: Optional[Path] = None,
        enable_inheritance: bool = True,
        enable_components: bool = True,
        cache_ttl: int = 300
    ):
        """
        Initialize distributed template adapter.
        
        Args:
            template_dir: Path to distributed templates (default: cortex-brain/response-templates)
            registry_file: Path to template registry (auto-detected if None)
            enable_inheritance: Enable template inheritance resolution (default: True)
            enable_components: Enable component reference resolution (default: True)
            cache_ttl: Cache TTL in seconds (default: 300 = 5 minutes)
        """
        self.template_dir = template_dir or Path("cortex-brain/response-templates")
        self.enable_inheritance = enable_inheritance
        self.enable_components = enable_components
        
        # Initialize core systems
        self.loader = LazyTemplateLoader(
            template_dir=self.template_dir,
            registry_file=registry_file,
            cache_ttl_seconds=cache_ttl
        )
        
        if enable_components:
            self.component_registry = ComponentRegistry(
                components_dir=self.template_dir
            )
        else:
            self.component_registry = None
        
        if enable_inheritance:
            self.inheritance_engine = TemplateInheritance(
                template_dir=self.template_dir,
                component_registry=self.component_registry
            )
        else:
            self.inheritance_engine = None
        
        logger.info(
            f"DistributedTemplateAdapter initialized: "
            f"{len(self.loader.registry)} templates, "
            f"inheritance: {enable_inheritance}, "
            f"components: {enable_components}"
        )
    
    def get_template(
        self,
        template_id: str,
        resolve_inheritance: Optional[bool] = None,
        resolve_components: Optional[bool] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get fully resolved template by ID.
        
        Process:
        1. Load template from distributed files (via LazyTemplateLoader)
        2. Resolve template inheritance if enabled (via TemplateInheritance)
        3. Resolve component references if enabled (via ComponentRegistry)
        4. Return fully composed template
        
        Args:
            template_id: Template identifier (e.g., 'planning', 'help')
            resolve_inheritance: Override global inheritance setting
            resolve_components: Override global component setting
        
        Returns:
            Fully resolved template dictionary, or None if not found
        
        Example:
            template = adapter.get_template('planning')
            if template:
                sections = template.get('sections', {})
                response = sections.get('response_content', '')
        """
        # Load template from distributed files
        template = self.loader.load_template(template_id)
        
        if template is None:
            logger.warning(f"Template not found: {template_id}")
            return None
        
        # Resolve inheritance if enabled
        if self.enable_inheritance and (resolve_inheritance is None or resolve_inheritance):
            if 'inherits_from' in template:
                try:
                    template = self._resolve_inheritance(template, template_id)
                except Exception as e:
                    logger.error(f"Inheritance resolution failed for {template_id}: {e}")
                    # Continue with base template
        
        # Resolve components if enabled
        if self.enable_components and (resolve_components is None or resolve_components):
            try:
                template = self._resolve_components(template)
            except Exception as e:
                logger.error(f"Component resolution failed for {template_id}: {e}")
                # Continue with unresolved components
        
        return template
    
    def _resolve_inheritance(
        self,
        template: Dict[str, Any],
        template_id: str
    ) -> Dict[str, Any]:
        """
        Resolve template inheritance chain.
        
        Args:
            template: Template with 'inherits_from' directive
            template_id: Template identifier for logging
        
        Returns:
            Resolved template with base template merged
        """
        if not self.inheritance_engine:
            return template
        
        inherits_from = template.get('inherits_from')
        if not inherits_from:
            return template
        
        logger.debug(f"Resolving inheritance: {template_id} -> {inherits_from}")
        
        # Resolve inheritance chain
        resolved = self.inheritance_engine.resolve_inheritance(template)
        
        return resolved
    
    def _resolve_components(self, template: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve component references in template.
        
        Component references have format: file_path#component_id
        Example: "core/components/headers.yaml#standard_header"
        
        Args:
            template: Template with potential component references
        
        Returns:
            Template with components resolved to actual content
        """
        if not self.component_registry:
            return template
        
        # Recursively resolve component references in template
        return self._resolve_components_recursive(template)
    
    def _resolve_components_recursive(self, data: Any) -> Any:
        """
        Recursively resolve component references in nested structures.
        
        Args:
            data: Template data (dict, list, str, etc.)
        
        Returns:
            Data with component references resolved
        """
        if isinstance(data, dict):
            resolved = {}
            for key, value in data.items():
                # Check if key indicates component reference
                if key == 'component' and isinstance(value, str) and '#' in value:
                    # Resolve component reference
                    try:
                        component_content = self.component_registry.resolve(value)
                        return component_content  # Replace entire dict with component
                    except Exception as e:
                        logger.warning(f"Failed to resolve component {value}: {e}")
                        resolved[key] = value
                else:
                    # Recursively resolve nested structures
                    resolved[key] = self._resolve_components_recursive(value)
            return resolved
        
        elif isinstance(data, list):
            return [self._resolve_components_recursive(item) for item in data]
        
        elif isinstance(data, str):
            # Check if string is component reference (file#id format)
            if '#' in data and '/' in data and data.endswith('.yaml'):
                # Potential component reference
                try:
                    component_content = self.component_registry.resolve(data)
                    return component_content
                except Exception:
                    # Not a valid component reference, return as-is
                    return data
            return data
        
        else:
            return data
    
    def list_templates(self) -> list:
        """
        List all available templates from registry.
        
        Returns:
            List of template IDs
        """
        return list(self.loader.registry.keys())
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics from all subsystems.
        
        Returns:
            Dictionary with metrics from loader, inheritance, components
        """
        metrics = {
            'loader': {
                'total_loads': self.loader.metrics.total_loads,
                'cache_hits': self.loader.metrics.cache_hits,
                'cache_misses': self.loader.metrics.cache_misses,
                'cache_hit_rate': self.loader.metrics.cache_hit_rate,
                'avg_load_time_ms': self.loader.metrics.avg_load_time_ms
            }
        }
        
        if self.inheritance_engine and hasattr(self.inheritance_engine, 'get_metrics'):
            inheritance_metrics = self.inheritance_engine.get_metrics()
            metrics['inheritance'] = inheritance_metrics
        
        if self.component_registry and hasattr(self.component_registry, 'get_metrics'):
            component_metrics = self.component_registry.get_metrics()
            metrics['components'] = component_metrics
        
        return metrics
    
    def clear_caches(self):
        """Clear all caches in subsystems."""
        self.loader.clear_cache()
        
        if self.inheritance_engine:
            self.inheritance_engine.clear_cache()
        
        if self.component_registry:
            self.component_registry.clear_cache()
        
        logger.info("All caches cleared")
    
    def preload_templates(self, template_ids: Optional[list] = None):
        """
        Preload templates into cache for faster first access.
        
        Args:
            template_ids: List of template IDs to preload (None = all templates)
        """
        if template_ids is None:
            template_ids = self.list_templates()
        
        logger.info(f"Preloading {len(template_ids)} templates...")
        
        preloaded = 0
        for template_id in template_ids:
            try:
                self.get_template(template_id)
                preloaded += 1
            except Exception as e:
                logger.warning(f"Failed to preload {template_id}: {e}")
        
        logger.info(f"Preloaded {preloaded}/{len(template_ids)} templates")
