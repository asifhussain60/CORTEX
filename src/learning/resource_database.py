"""
Learning System Resource Database

Stores and manages external learning resources (documentation, guides, articles).
Provides category-based organization and retrieval.
"""

import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class ResourceDatabase:
    """
    Manages external learning resources.
    
    Features:
    - Category-based organization
    - Resource metadata (title, URL, description)
    - Search and filtering
    - Validation
    """
    
    def __init__(self):
        """Initialize empty resource database."""
        self._resources: Dict[str, List[Dict[str, Any]]] = {}
        self._initialize_categories()
    
    def _initialize_categories(self):
        """Initialize storage for all 15 categories."""
        categories = [
            'concepts', 'patterns', 'milestones', 'resources',
            'ado_workflows', 'planning_strategies', 'workflow_context',
            'architectural_patterns', 'code_quality', 'design_decisions',
            'debugging_patterns', 'productivity_patterns', 'operational_learnings',
            'user_onboarding', 'intent_routing'
        ]
        for category in categories:
            self._resources[category] = []
    
    def add_resource(
        self,
        category: str,
        title: str,
        url: str,
        description: str = ''
    ) -> None:
        """
        Add resource to database.
        
        Args:
            category: Resource category
            title: Resource title
            url: Resource URL
            description: Optional description
        """
        if category not in self._resources:
            logger.warning(f"Unknown category: {category}")
            self._resources[category] = []
        
        resource = {
            'title': title,
            'url': url,
            'description': description,
            'category': category
        }
        
        self._resources[category].append(resource)
        logger.debug(f"Added resource '{title}' to category '{category}'")
    
    def get_resources(self, category: str) -> List[Dict[str, Any]]:
        """
        Get all resources for category.
        
        Args:
            category: Resource category
            
        Returns:
            List of resource dicts
        """
        return self._resources.get(category, [])
    
    def search_resources(self, query: str) -> List[Dict[str, Any]]:
        """
        Search resources by title or description.
        
        Args:
            query: Search query
            
        Returns:
            List of matching resources
        """
        results = []
        query_lower = query.lower()
        
        for category_resources in self._resources.values():
            for resource in category_resources:
                if (query_lower in resource['title'].lower() or
                    query_lower in resource['description'].lower()):
                    results.append(resource)
        
        return results
    
    def get_all_resources(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get all resources grouped by category.
        
        Returns:
            Dict mapping category to resource list
        """
        return self._resources.copy()
    
    def remove_resource(self, category: str, title: str) -> bool:
        """
        Remove resource from database.
        
        Args:
            category: Resource category
            title: Resource title to remove
            
        Returns:
            True if removed, False if not found
        """
        if category not in self._resources:
            return False
        
        resources = self._resources[category]
        for i, resource in enumerate(resources):
            if resource['title'] == title:
                resources.pop(i)
                logger.debug(f"Removed resource '{title}' from category '{category}'")
                return True
        
        return False
    
    def clear_category(self, category: str) -> None:
        """
        Remove all resources from category.
        
        Args:
            category: Category to clear
        """
        if category in self._resources:
            self._resources[category] = []
            logger.debug(f"Cleared category '{category}'")
    
    def get_categories(self) -> List[str]:
        """
        Get list of all categories.
        
        Returns:
            List of category names
        """
        return list(self._resources.keys())
    
    def get_resource_count(self) -> Dict[str, int]:
        """
        Get count of resources per category.
        
        Returns:
            Dict mapping category to count
        """
        return {
            category: len(resources)
            for category, resources in self._resources.items()
        }
