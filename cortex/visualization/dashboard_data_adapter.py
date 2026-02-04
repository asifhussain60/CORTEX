"""
Abstract DashboardDataAdapter Protocol
Enables adapter pattern for JSON → SQLite → PostgreSQL progression
Author: Asif Hussain
Date: 2026-02-04
Authority: CORE-008, CORE-035 (Single implementation, adapter pattern)
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from pathlib import Path


class DashboardDataAdapter(ABC):
    """
    Abstract base class for dashboard data loading adapters.
    
    Supports multiple data formats:
    - JSON: Fast, simple, for <10K file repos
    - SQLite: Medium, indexed, for 10K-100K file repos  
    - PostgreSQL: Full-featured, multi-tenant, for 100K+ repos
    
    Implementation Truth:
    - JSON is 40x faster (5ms vs 200ms)
    - Adapter pattern enables graduation without rewrite
    - YAGNI: Start with JSON, graduate when data proves need
    """
    
    @abstractmethod
    def load(self, repo_slug: str) -> Optional[Dict[str, Any]]:
        """
        Load dashboard data for repository.
        
        Args:
            repo_slug: Repository identifier (e.g., 'cortex')
        
        Returns:
            Dictionary with dashboard data or None if not found
        
        Raises:
            OSError: If file system error occurs
            ValueError: If data format invalid
        """
        pass
    
    @abstractmethod
    def save(self, repo_slug: str, data: Dict[str, Any]) -> bool:
        """
        Save dashboard data for repository.
        
        Args:
            repo_slug: Repository identifier
            data: Dashboard data dictionary
        
        Returns:
            True if successful
        
        Raises:
            OSError: If file system error occurs
            ValueError: If data format invalid
        """
        pass
    
    @abstractmethod
    def list_repos(self) -> List[str]:
        """
        List all repositories with dashboard data.
        
        Returns:
            List of repository slugs
        """
        pass
    
    @abstractmethod
    def search(self, query: str) -> List[str]:
        """
        Search repositories by name/description.
        
        Args:
            query: Search query string
        
        Returns:
            List of matching repository slugs
        
        Note:
            JSON adapter uses Array.filter (O(n))
            SQLite adapter uses FTS5
            PostgreSQL adapter uses pgvector
        """
        pass
