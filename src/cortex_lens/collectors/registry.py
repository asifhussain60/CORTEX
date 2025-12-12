"""
Registry for data collectors with execution matrix.

The CollectorRegistry manages collector lifecycle and determines
which collectors to run based on repository type.
"""

from typing import Dict, List, Optional, Set
from pathlib import Path
import logging

from .base import BaseCollector

logger = logging.getLogger(__name__)


class CollectorRegistry:
    """
    Central registry for data collectors.
    
    Provides plugin system for registering collectors and
    execution matrix for repo-type-specific collection.
    
    Example:
        >>> registry = CollectorRegistry()
        >>> registry.register(HealthCollector())
        >>> collectors = registry.get_collectors_for_type('api_service')
    """
    
    # Execution matrix: repo_type -> required collector names
    EXECUTION_MATRIX = {
        'fullstack_web': [
            'health', 'architecture', 'security', 'tech_stack',
            'api_endpoint', 'database_schema', 'frontend_routes',
            'dependency', 'complexity', 'test_coverage', 'comment',
            'performance'
        ],
        'api_service': [
            'health', 'architecture', 'security', 'tech_stack',
            'api_endpoint', 'dependency', 'complexity', 'test_coverage',
            'comment', 'performance'
        ],
        'database_project': [
            'health', 'architecture', 'security', 'database_schema',
            'dependency', 'complexity', 'comment', 'performance'
        ],
        'console_app': [
            'health', 'architecture', 'security', 'dependency',
            'complexity', 'test_coverage', 'comment'
        ],
        'microservices': [
            'health', 'architecture', 'security', 'tech_stack',
            'api_endpoint', 'database_schema', 'dependency',
            'complexity', 'test_coverage', 'comment', 'performance',
            'ownership'
        ],
        'library_package': [
            'health', 'architecture', 'security', 'dependency',
            'complexity', 'test_coverage', 'comment'
        ],
    }
    
    def __init__(self):
        """Initialize empty registry."""
        self._collectors: Dict[str, BaseCollector] = {}
        logger.info("🎭 CollectorRegistry initialized")
    
    def register(self, collector: BaseCollector) -> None:
        """
        Register a collector.
        
        Args:
            collector: Collector instance implementing BaseCollector protocol
            
        Raises:
            ValueError: If collector name already registered
        """
        name = collector.name
        if name in self._collectors:
            raise ValueError(f"Collector '{name}' already registered")
        
        self._collectors[name] = collector
        logger.info(f"📝 Registered collector: {name}")
    
    def get_collector(self, name: str) -> Optional[BaseCollector]:
        """
        Get collector by name.
        
        Args:
            name: Collector identifier
            
        Returns:
            Collector instance or None
        """
        return self._collectors.get(name)
    
    def get_collectors_for_type(self, repo_type: str) -> List[BaseCollector]:
        """
        Get all collectors required for a repository type.
        
        Args:
            repo_type: Repository type identifier
            
        Returns:
            List of collector instances in execution order
            
        Raises:
            ValueError: If repo_type is unknown
        """
        if repo_type not in self.EXECUTION_MATRIX:
            raise ValueError(f"Unknown repo type: {repo_type}")
        
        required_names = self.EXECUTION_MATRIX[repo_type]
        collectors = []
        
        for name in required_names:
            collector = self._collectors.get(name)
            if collector:
                collectors.append(collector)
            else:
                logger.warning(f"⚠️ Required collector '{name}' not registered")
        
        logger.info(f"🎯 Selected {len(collectors)} collectors for {repo_type}")
        return collectors
    
    def list_collectors(self) -> List[str]:
        """
        List all registered collector names.
        
        Returns:
            List of collector identifiers
        """
        return list(self._collectors.keys())
    
    def list_repo_types(self) -> List[str]:
        """
        List all supported repository types.
        
        Returns:
            List of repo type identifiers
        """
        return list(self.EXECUTION_MATRIX.keys())
    
    def get_required_collectors(self, repo_type: str) -> Set[str]:
        """
        Get set of required collector names for repo type.
        
        Args:
            repo_type: Repository type identifier
            
        Returns:
            Set of collector names
        """
        return set(self.EXECUTION_MATRIX.get(repo_type, []))
    
    def is_collector_required(self, collector_name: str, repo_type: str) -> bool:
        """
        Check if collector is required for repo type.
        
        Args:
            collector_name: Collector identifier
            repo_type: Repository type identifier
            
        Returns:
            True if required, False otherwise
        """
        required = self.EXECUTION_MATRIX.get(repo_type, [])
        return collector_name in required
    
    def unregister(self, name: str) -> bool:
        """
        Unregister a collector.
        
        Args:
            name: Collector identifier
            
        Returns:
            True if unregistered, False if not found
        """
        if name not in self._collectors:
            return False
        
        del self._collectors[name]
        logger.info(f"🗑️ Unregistered collector: {name}")
        return True
    
    def clear(self) -> None:
        """Clear all registered collectors."""
        count = len(self._collectors)
        self._collectors.clear()
        logger.info(f"🧹 Cleared {count} collectors")


# Global singleton instance
_default_registry: Optional[CollectorRegistry] = None


def get_default_registry() -> CollectorRegistry:
    """
    Get the default global registry instance.
    
    Returns:
        Global CollectorRegistry singleton
    """
    global _default_registry
    if _default_registry is None:
        _default_registry = CollectorRegistry()
    return _default_registry
