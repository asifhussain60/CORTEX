"""
Component Registry for Template Composition

This module manages reusable template components (headers, footers, sections)
and provides fast resolution for component references.

Architecture:
- Component lookup with URI-style references (file#component_id)
- Component caching to prevent re-parsing
- Nested component support (components can reference other components)
- Circular reference detection

Performance Targets:
- Component resolution: <5ms
- Cache hit rate: >90%
- Support for 30-40 reusable components

Author: Asif Hussain
Phase: 2 - Core Infrastructure  
Version: 1.0
Created: December 5, 2025
"""

import yaml
import time
from pathlib import Path
from typing import Dict, Any, Optional, List, Set
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
import re

logger = logging.getLogger(__name__)


@dataclass
class Component:
    """Represents a reusable template component."""
    component_id: str
    content: Any  # Can be string, dict, or list
    file_path: Path
    loaded_at: datetime
    dependencies: List[str]  # Other components this component references
    
    def is_expired(self, ttl_seconds: int = 300) -> bool:
        """Check if component cache entry has expired."""
        return datetime.now() - self.loaded_at > timedelta(seconds=ttl_seconds)


class ComponentRegistry:
    """
    Registry for reusable template components with caching and reference resolution.
    
    Features:
    - URI-style component references (core/components/headers.yaml#standard_header)
    - Component caching with TTL
    - Nested component resolution
    - Circular reference detection
    - Placeholder substitution
    
    Component Reference Format:
        [category]/[file].yaml#[component_id]
        
        Examples:
        - core/components/headers.yaml#standard_header
        - core/components/footers.yaml#next_steps_planning
        - agents/tactical/executor.yaml#success_section
    
    Usage:
        registry = ComponentRegistry(
            components_dir=Path("cortex-brain/response-templates")
        )
        
        header = registry.resolve_component("core/components/headers.yaml#standard_header")
        footer = registry.resolve_component("core/components/footers.yaml#attribution")
    """
    
    def __init__(
        self,
        components_dir: Path,
        cache_ttl_seconds: int = 300,
        enable_metrics: bool = True
    ):
        """
        Initialize component registry.
        
        Args:
            components_dir: Base directory for component files
            cache_ttl_seconds: Cache TTL in seconds (default: 300 = 5 minutes)
            enable_metrics: Enable performance metrics tracking
        """
        self.components_dir = components_dir
        self.cache_ttl_seconds = cache_ttl_seconds
        self.enable_metrics = enable_metrics
        
        # Cache: component_id → Component
        self.cache: Dict[str, Component] = {}
        
        # File cache: file_path → parsed YAML content
        self.file_cache: Dict[Path, Dict[str, Any]] = {}
        
        # Metrics
        self.total_resolutions = 0
        self.cache_hits = 0
        self.cache_misses = 0
        
        logger.info(
            f"ComponentRegistry initialized: {components_dir}, "
            f"cache TTL: {cache_ttl_seconds}s"
        )
    
    def resolve_component(
        self,
        reference: str,
        context: Optional[Dict[str, Any]] = None,
        visited: Optional[Set[str]] = None
    ) -> Optional[Any]:
        """
        Resolve component reference to actual content.
        
        Args:
            reference: Component reference (e.g., "core/components/headers.yaml#standard_header")
            context: Optional context for placeholder substitution
            visited: Set of visited references (for circular detection, internal use)
        
        Returns:
            Component content (string, dict, or list) or None if not found
        
        Raises:
            ValueError: If circular reference detected
        """
        start_time = time.perf_counter()
        
        # Initialize visited set for circular detection
        if visited is None:
            visited = set()
        
        # Circular reference detection
        if reference in visited:
            raise ValueError(f"Circular component reference detected: {reference}")
        
        visited.add(reference)
        
        self.total_resolutions += 1
        
        # Check cache first
        if reference in self.cache:
            cached = self.cache[reference]
            
            if not cached.is_expired(self.cache_ttl_seconds):
                self.cache_hits += 1
                content = cached.content
                
                # Resolve nested components
                content = self._resolve_nested_components(content, context, visited)
                
                # Substitute placeholders
                if context:
                    content = self._substitute_placeholders(content, context)
                
                load_time = (time.perf_counter() - start_time) * 1000
                logger.debug(f"Component cache HIT: {reference} ({load_time:.2f}ms)")
                
                return content
            else:
                # Cache expired
                del self.cache[reference]
        
        # Cache miss - load component
        self.cache_misses += 1
        logger.debug(f"Component cache MISS: {reference}")
        
        # Parse reference (format: path/to/file.yaml#component_id)
        file_path, component_id = self._parse_reference(reference)
        
        if not file_path:
            logger.error(f"Invalid component reference: {reference}")
            return None
        
        # Load component from file
        content = self._load_component_from_file(file_path, component_id)
        
        if content is None:
            logger.warning(f"Component not found: {reference}")
            return None
        
        # Cache the component
        dependencies = self._extract_component_dependencies(content)
        self.cache[reference] = Component(
            component_id=component_id,
            content=content,
            file_path=file_path,
            loaded_at=datetime.now(),
            dependencies=dependencies
        )
        
        # Resolve nested components
        content = self._resolve_nested_components(content, context, visited)
        
        # Substitute placeholders
        if context:
            content = self._substitute_placeholders(content, context)
        
        load_time = (time.perf_counter() - start_time) * 1000
        logger.info(f"Component resolved: {reference} ({load_time:.2f}ms)")
        
        return content
    
    def _parse_reference(self, reference: str) -> tuple[Optional[Path], Optional[str]]:
        """
        Parse component reference into file path and component ID.
        
        Format: path/to/file.yaml#component_id
        
        Returns:
            Tuple of (absolute_file_path, component_id) or (None, None) if invalid
        """
        if '#' not in reference:
            logger.error(f"Invalid reference format (missing #): {reference}")
            return None, None
        
        file_ref, component_id = reference.split('#', 1)
        
        # Construct absolute path
        file_path = self.components_dir / file_ref
        
        return file_path, component_id
    
    def _load_component_from_file(
        self,
        file_path: Path,
        component_id: str
    ) -> Optional[Any]:
        """Load specific component from YAML file."""
        # Check file cache
        if file_path in self.file_cache:
            file_content = self.file_cache[file_path]
        else:
            # Load file
            if not file_path.exists():
                logger.error(f"Component file not found: {file_path}")
                return None
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_content = yaml.safe_load(f)
                
                # Cache file content
                self.file_cache[file_path] = file_content
            
            except Exception as e:
                logger.error(f"Failed to load component file {file_path}: {e}")
                return None
        
        # Extract component by ID
        if not isinstance(file_content, dict):
            logger.error(f"Invalid file format (expected dict): {file_path}")
            return None
        
        component = file_content.get(component_id)
        
        if component is None:
            logger.warning(f"Component '{component_id}' not found in {file_path}")
        
        return component
    
    def _extract_component_dependencies(self, content: Any) -> List[str]:
        """
        Extract component references from content.
        
        Finds patterns like: {component:path/to/file.yaml#component_id}
        """
        dependencies = []
        
        if isinstance(content, str):
            # Find component references in string
            pattern = r'\{component:([^}]+)\}'
            matches = re.findall(pattern, content)
            dependencies.extend(matches)
        
        elif isinstance(content, dict):
            # Recursively search dict values
            for value in content.values():
                dependencies.extend(self._extract_component_dependencies(value))
        
        elif isinstance(content, list):
            # Recursively search list items
            for item in content:
                dependencies.extend(self._extract_component_dependencies(item))
        
        return dependencies
    
    def _resolve_nested_components(
        self,
        content: Any,
        context: Optional[Dict[str, Any]],
        visited: Set[str]
    ) -> Any:
        """
        Resolve nested component references in content.
        
        Replaces {component:path#id} with actual component content.
        """
        if isinstance(content, str):
            # Find and replace component references
            pattern = r'\{component:([^}]+)\}'
            
            def replace_component(match):
                ref = match.group(1)
                resolved = self.resolve_component(ref, context, visited.copy())
                return str(resolved) if resolved is not None else match.group(0)
            
            return re.sub(pattern, replace_component, content)
        
        elif isinstance(content, dict):
            # Recursively resolve dict values
            return {
                key: self._resolve_nested_components(value, context, visited)
                for key, value in content.items()
            }
        
        elif isinstance(content, list):
            # Recursively resolve list items
            return [
                self._resolve_nested_components(item, context, visited)
                for item in content
            ]
        
        return content
    
    def _substitute_placeholders(self, content: Any, context: Dict[str, Any]) -> Any:
        """
        Substitute {placeholder} with values from context.
        
        Args:
            content: Content with placeholders
            context: Dictionary of placeholder values
        
        Returns:
            Content with placeholders replaced
        """
        if isinstance(content, str):
            # Replace {key} with context[key]
            for key, value in context.items():
                placeholder = f"{{{key}}}"
                if placeholder in content:
                    content = content.replace(placeholder, str(value))
            return content
        
        elif isinstance(content, dict):
            return {
                key: self._substitute_placeholders(value, context)
                for key, value in content.items()
            }
        
        elif isinstance(content, list):
            return [
                self._substitute_placeholders(item, context)
                for item in content
            ]
        
        return content
    
    def clear_cache(self, reference: Optional[str] = None):
        """
        Clear component cache.
        
        Args:
            reference: If provided, clear only this component. Otherwise clear all.
        """
        if reference:
            if reference in self.cache:
                del self.cache[reference]
                logger.info(f"Component cache cleared: {reference}")
        else:
            count = len(self.cache)
            self.cache.clear()
            self.file_cache.clear()
            logger.info(f"Component cache cleared: {count} components")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        cache_hit_rate = 0.0
        if self.total_resolutions > 0:
            cache_hit_rate = (self.cache_hits / self.total_resolutions) * 100
        
        return {
            'total_resolutions': self.total_resolutions,
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'cache_hit_rate_pct': round(cache_hit_rate, 1),
            'cached_components': len(self.cache),
            'cached_files': len(self.file_cache),
        }
    
    def get_cached_references(self) -> List[str]:
        """Get list of currently cached component references."""
        return list(self.cache.keys())
    
    def validate_component(self, reference: str) -> bool:
        """
        Validate that component reference exists and is loadable.
        
        Args:
            reference: Component reference to validate
        
        Returns:
            True if component exists and is valid, False otherwise
        """
        try:
            content = self.resolve_component(reference)
            return content is not None
        except Exception as e:
            logger.error(f"Component validation failed for {reference}: {e}")
            return False
