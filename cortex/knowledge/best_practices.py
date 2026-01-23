"""
CORTEX Knowledge System - Best Practices Registry
===================================================

Public API for accessing unified best practices knowledge across all technology stacks.

This module provides:
- Unified access to 35+ best practices guides
- Discovery by technology stack, concern, and learning path
- Integration with CORTEX knowledge repository
- Cross-referencing and related guides

Usage::
    
    from cortex.knowledge import best_practices
    
    # Discover guides by tech stack
    python_guides = best_practices.discover_python_backend()
    
    # Discover guides by concern
    security_guides = best_practices.discover_security()
    
    # Get recommended learning path
    onboarding_path = best_practices.learning_path("onboarding")

Authority: cortex_brain/tier3/knowledge/best-practices
Updated: 2026-01-23
"""

from pathlib import Path
from typing import List, Dict, Optional, Union

# Import discovery modules
from cortex.knowledge.best_practices_discovery import (
    BestPracticesDiscovery,
    get_discovery,
    discover_by_stack,
    discover_by_concern,
    discover_category,
    learning_path,
)

from cortex.knowledge.knowledge_repository_integration import (
    KnowledgeRepository,
    KnowledgeCategory,
    get_repository,
    get_guide,
    list_by_stack,
    list_by_concern,
)

__all__ = [
    # Core classes
    "BestPracticesDiscovery",
    "KnowledgeRepository",
    "KnowledgeCategory",
    
    # Discovery functions
    "get_discovery",
    "discover_python_backend",
    "discover_javascript_react",
    "discover_aws_cloud",
    "discover_security",
    "discover_performance",
    "discover_testing",
    "learning_path",
    
    # Repository functions
    "get_repository",
    "get_guide",
    "list_by_stack",
    "list_by_concern",
    "list_all_guides",
    "list_categories",
    "list_tech_stacks",
    "list_concerns",
    
    # Utilities
    "get_statistics",
    "search_guides",
]


# Convenience discovery functions for common stacks
def discover_python_backend() -> List[Path]:
    """Discover best practices for Python backend development."""
    return discover_by_stack("python-backend")


def discover_javascript_react() -> List[Path]:
    """Discover best practices for JavaScript/React frontend development."""
    return discover_by_stack("javascript-react")


def discover_aws_cloud() -> List[Path]:
    """Discover best practices for AWS cloud development."""
    return discover_by_stack("aws-cloud")


def discover_data_systems() -> List[Path]:
    """Discover best practices for data systems and databases."""
    return discover_by_stack("data-systems")


def discover_ai_ml() -> List[Path]:
    """Discover best practices for AI/ML systems."""
    return discover_by_stack("ai-ml-systems")


def discover_microservices() -> List[Path]:
    """Discover best practices for microservices architecture."""
    return discover_by_stack("microservices-distributed")


def discover_api_development() -> List[Path]:
    """Discover best practices for API development."""
    return discover_by_stack("api-development")


# Convenience functions for common concerns
def discover_security() -> List[Path]:
    """Discover all security-related best practices."""
    return discover_by_concern("security")


def discover_performance() -> List[Path]:
    """Discover all performance optimization best practices."""
    return discover_by_concern("performance")


def discover_testing() -> List[Path]:
    """Discover all testing and validation best practices."""
    return discover_by_concern("testing-validation")


def discover_quality() -> List[Path]:
    """Discover all code quality best practices."""
    return discover_by_concern("quality")


def discover_scalability() -> List[Path]:
    """Discover all scalability best practices."""
    return discover_by_concern("scalability")


# Repository-level functions
def list_all_guides() -> List[str]:
    """List all available best practices guides."""
    return get_repository().list_guides_by_category("")


def list_categories() -> List[str]:
    """List all knowledge categories."""
    return get_repository().list_categories()


def list_tech_stacks() -> List[str]:
    """List all available technology stacks."""
    return get_repository().list_tech_stacks()


def list_concerns() -> List[str]:
    """List all concerns addressed in best practices."""
    return get_repository().list_concerns()


def get_statistics() -> Dict:
    """Get statistics about the knowledge repository."""
    return get_repository().get_statistics()


def search_guides(keyword: str) -> List[Dict]:
    """
    Search best practices guides by keyword.
    
    Args:
        keyword: Search term
        
    Returns:
        List of matching guides with metadata
    """
    return get_discovery().search_guides(keyword)


# Module initialization
def _initialize() -> None:
    """Initialize best practices knowledge system."""
    repo = get_repository()
    discovery = get_discovery()
    
    # Verify structure
    if repo.registry["metadata"]["total_guides"] > 0:
        # Successfully initialized
        pass


# Auto-initialize on import
_initialize()
