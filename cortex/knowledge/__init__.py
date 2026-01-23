"""
CORTEX Knowledge System
=======================

Unified knowledge repository for best practices, patterns, and domain expertise.

Components:
- best_practices: 35+ guides organized by technology stack and concern
- knowledge_repository_integration: Repository integration and cross-referencing
- best_practices_discovery: Discovery and search functionality

Examples::
    
    from cortex.knowledge import best_practices
    
    # Discover guides
    python_guides = best_practices.discover_python_backend()
    security_guides = best_practices.discover_security()
    
    # Get learning paths
    onboarding = best_practices.learning_path("onboarding")
    
    # Repository operations
    repo = best_practices.get_repository()
    guides = repo.list_guides_by_stack("python-backend")

Authority: cortex_brain/tier3/knowledge/
Version: 2.0
Updated: 2026-01-23
"""

from cortex.knowledge import best_practices

__all__ = [
    "best_practices",
]
