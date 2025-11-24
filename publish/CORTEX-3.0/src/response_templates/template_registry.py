"""Template registry for CORTEX response templates.

This module provides a centralized registry for managing templates,
including plugin-registered templates.

Author: Asif Hussain
Version: 1.0
"""

from typing import Dict, List, Optional
from .template_loader import Template


class TemplateRegistry:
    """Central registry for all response templates."""
    
    def __init__(self):
        """Initialize template registry."""
        self._templates: Dict[str, Template] = {}
        self._plugin_templates: Dict[str, List[str]] = {}  # plugin_id -> template_ids
        self._category_index: Dict[str, List[str]] = {}  # category -> template_ids
    
    def register_template(self, template: Template) -> None:
        """Register a single template.
        
        Args:
            template: Template object to register
        """
        self._templates[template.template_id] = template
        
        # Index by category if available
        if template.metadata and 'category' in template.metadata:
            category = template.metadata['category']
            if category not in self._category_index:
                self._category_index[category] = []
            self._category_index[category].append(template.template_id)
    
    def register_plugin_templates(
        self, 
        plugin_id: str, 
        templates: List[Template]
    ) -> None:
        """Register templates from a plugin.
        
        Args:
            plugin_id: Plugin identifier
            templates: List of Template objects
        """
        template_ids = []
        
        for template in templates:
            # Add plugin metadata
            if not template.metadata:
                template.metadata = {}
            template.metadata['plugin_id'] = plugin_id
            
            # Register template
            self.register_template(template)
            template_ids.append(template.template_id)
        
        self._plugin_templates[plugin_id] = template_ids
    
    def get_template(self, template_id: str) -> Optional[Template]:
        """Get template by ID.
        
        Args:
            template_id: Template identifier
            
        Returns:
            Template object if found, None otherwise
        """
        return self._templates.get(template_id)
    
    def search_templates(
        self, 
        query: str,
        category: Optional[str] = None,
        plugin_id: Optional[str] = None
    ) -> List[Template]:
        """Search templates by query.
        
        Args:
            query: Search query (matches template_id, triggers, content)
            category: Optional category filter
            plugin_id: Optional plugin filter
            
        Returns:
            List of matching Template objects
        """
        query_lower = query.lower()
        results = []
        
        for template in self._templates.values():
            # Apply filters
            if category and (
                not template.metadata or 
                template.metadata.get('category') != category
            ):
                continue
            
            if plugin_id and (
                not template.metadata or 
                template.metadata.get('plugin_id') != plugin_id
            ):
                continue
            
            # Check if query matches
            if (query_lower in template.template_id.lower() or
                any(query_lower in trigger.lower() for trigger in template.triggers) or
                query_lower in template.content.lower()):
                results.append(template)
        
        return results
    
    def list_templates(
        self,
        category: Optional[str] = None,
        plugin_id: Optional[str] = None
    ) -> List[Template]:
        """List all templates with optional filters.
        
        Args:
            category: Optional category filter
            plugin_id: Optional plugin filter
            
        Returns:
            List of Template objects
        """
        if category and category in self._category_index:
            template_ids = self._category_index[category]
            templates = [self._templates[tid] for tid in template_ids]
        elif plugin_id and plugin_id in self._plugin_templates:
            template_ids = self._plugin_templates[plugin_id]
            templates = [self._templates[tid] for tid in template_ids]
        else:
            templates = list(self._templates.values())
        
        return templates
    
    def get_categories(self) -> List[str]:
        """Get all registered categories.
        
        Returns:
            List of category names
        """
        return list(self._category_index.keys())
    
    def get_plugins(self) -> List[str]:
        """Get all plugins that registered templates.
        
        Returns:
            List of plugin IDs
        """
        return list(self._plugin_templates.keys())
    
    def unregister_plugin_templates(self, plugin_id: str) -> int:
        """Unregister all templates for a plugin.
        
        Args:
            plugin_id: Plugin identifier
            
        Returns:
            Number of templates unregistered
        """
        if plugin_id not in self._plugin_templates:
            return 0
        
        template_ids = self._plugin_templates[plugin_id]
        count = 0
        
        for template_id in template_ids:
            if template_id in self._templates:
                template = self._templates[template_id]
                
                # Remove from category index
                if template.metadata and 'category' in template.metadata:
                    category = template.metadata['category']
                    if category in self._category_index:
                        self._category_index[category].remove(template_id)
                
                # Remove from main registry
                del self._templates[template_id]
                count += 1
        
        # Remove plugin entry
        del self._plugin_templates[plugin_id]
        
        return count
    
    def get_template_count(self) -> int:
        """Get total number of registered templates.
        
        Returns:
            Template count
        """
        return len(self._templates)
    
    def clear(self) -> None:
        """Clear all registered templates."""
        self._templates.clear()
        self._plugin_templates.clear()
        self._category_index.clear()
