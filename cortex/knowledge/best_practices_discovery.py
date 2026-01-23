"""
Best Practices Knowledge Discovery Module
==========================================

Provides unified access to all CORTEX best practices guides organized by
technology stack, concern, and use case.

Source: cortex/knowledge/best-practices/
Authority: cortex_brain/tier3/knowledge/
Updated: 2026-01-23
"""

from pathlib import Path
from typing import List, Dict, Optional, Set
import yaml


class BestPracticesDiscovery:
    """Discover and retrieve best practices guides from unified repository."""
    
    def __init__(self, base_path: Optional[Path] = None) -> None:
        """
        Initialize best practices discovery.
        
        Args:
            base_path: Root path to best-practices directory.
                      Defaults to cortex/knowledge/best-practices
        """
        if base_path is None:
            base_path = Path(__file__).parent / "best-practices"
        
        self.base_path = base_path
        self._index_cache: Optional[Dict] = None
        self._load_index()
    
    def _load_index(self) -> None:
        """Load master index from INDEX.yaml."""
        index_path = self.base_path / "INDEX.yaml"
        if index_path.exists():
            with open(index_path) as f:
                self._index_cache = yaml.safe_load(f)
    
    def get_by_tech_stack(self, stack: str) -> List[Path]:
        """
        Get all best practices for a specific tech stack.
        
        Args:
            stack: Technology stack name (e.g., 'python-backend', 'javascript-react')
            
        Returns:
            List of Path objects to relevant guides
        """
        if not self._index_cache:
            return []
        
        discovery = self._index_cache.get("discovery", {})
        by_stack = discovery.get("by_technology_stack", [])
        
        for stack_entry in by_stack:
            if stack_entry.get("stack") == stack:
                guides = stack_entry.get("guides", [])
                return [self.base_path / guide for guide in guides]
        
        return []
    
    def get_by_concern(self, concern: str) -> List[Path]:
        """
        Get all best practices addressing a specific concern.
        
        Args:
            concern: Concern type (e.g., 'quality', 'security', 'performance')
            
        Returns:
            List of Path objects to relevant guides
        """
        if not self._index_cache:
            return []
        
        discovery = self._index_cache.get("discovery", {})
        by_concern = discovery.get("by_concern", [])
        
        for concern_entry in by_concern:
            if concern_entry.get("concern") == concern:
                guides = concern_entry.get("guides", [])
                return [self.base_path / guide for guide in guides]
        
        return []
    
    def get_by_category(self, category: str) -> List[Path]:
        """
        Get all guides in a category.
        
        Args:
            category: Category name (e.g., 'architecture', 'testing-validation')
            
        Returns:
            List of Path objects to guides in category
        """
        category_path = self.base_path / category
        if category_path.exists():
            return sorted(category_path.glob("*.yaml"))
        
        return []
    
    def get_all_categories(self) -> List[str]:
        """Get list of all available categories."""
        return [
            "architecture",
            "backend-python",
            "frontend-js-ts",
            "devops-infrastructure",
            "security",
            "testing-validation",
            "performance-optimization",
            "database-management",
            "ai-ml-domains",
            "ui-ux-design",
        ]
    
    def get_learning_path(self, path_name: str) -> List[Path]:
        """
        Get guides for a predefined learning path.
        
        Args:
            path_name: Learning path (e.g., 'onboarding', 'api-development', 'microservices-design')
            
        Returns:
            List of Path objects in recommended reading order
        """
        if not self._index_cache:
            return []
        
        usage = self._index_cache.get("usage", {})
        path = usage.get(path_name, {})
        guides = path.get("sequence", [])
        
        return [self.base_path / guide for guide in guides]
    
    def search_guides(self, keyword: str) -> List[Dict]:
        """
        Search guides by keyword.
        
        Args:
            keyword: Search term to match in guide metadata
            
        Returns:
            List of guide metadata dictionaries matching keyword
        """
        if not self._index_cache:
            return []
        
        results: List[Dict] = []
        keyword_lower = keyword.lower()
        
        # Search through all categories
        for category_name, category_data in self._index_cache.items():
            if isinstance(category_data, dict) and "guides" in category_data:
                for guide in category_data.get("guides", []):
                    # Check title, keywords, and description
                    title = guide.get("title", "").lower()
                    description = guide.get("description", "").lower()
                    keywords = [k.lower() for k in guide.get("keywords", [])]
                    
                    if (keyword_lower in title or 
                        keyword_lower in description or 
                        any(keyword_lower in k for k in keywords)):
                        results.append({
                            "category": category_name,
                            "path": guide.get("path"),
                            "title": guide.get("title"),
                            "description": guide.get("description"),
                            "keywords": guide.get("keywords", [])
                        })
        
        return results
    
    def list_all_guides(self) -> List[str]:
        """Get list of all guide paths."""
        guides = []
        for category in self.get_all_categories():
            guides.extend([str(g.relative_to(self.base_path)) 
                          for g in self.get_by_category(category)])
        return sorted(guides)
    
    def get_guide_metadata(self, guide_path: str) -> Optional[Dict]:
        """
        Get metadata for a specific guide.
        
        Args:
            guide_path: Relative path to guide (e.g., 'architecture/rest-api-design.yaml')
            
        Returns:
            Guide metadata or None if not found
        """
        full_path = self.base_path / guide_path
        
        if not full_path.exists():
            return None
        
        with open(full_path) as f:
            guide_data = yaml.safe_load(f)
        
        return {
            "path": guide_path,
            "file_size": full_path.stat().st_size,
            "metadata": guide_data.get("metadata", {}),
            "title": guide_data.get("metadata", {}).get("title", "Unknown")
        }
    
    def get_related_guides(self, guide_path: str) -> List[Path]:
        """
        Get guides related to a specific guide.
        
        Args:
            guide_path: Relative path to guide
            
        Returns:
            List of related guide paths
        """
        # Get metadata for the guide
        metadata = self.get_guide_metadata(guide_path)
        if not metadata:
            return []
        
        keywords = set(metadata.get("metadata", {}).get("keywords", []))
        if not keywords:
            return []
        
        # Find other guides with matching keywords
        related = []
        all_guides = self.list_all_guides()
        
        for other_guide in all_guides:
            if other_guide == guide_path:
                continue
            
            other_metadata = self.get_guide_metadata(other_guide)
            if other_metadata:
                other_keywords = set(other_metadata.get("metadata", {}).get("keywords", []))
                if keywords & other_keywords:  # Has common keywords
                    related.append(self.base_path / other_guide)
        
        return related


# Convenience functions
_discovery: Optional[BestPracticesDiscovery] = None


def get_discovery() -> BestPracticesDiscovery:
    """Get or create the best practices discovery instance."""
    global _discovery
    if _discovery is None:
        _discovery = BestPracticesDiscovery()
    return _discovery


def discover_by_stack(stack: str) -> List[Path]:
    """Discover guides for a technology stack."""
    return get_discovery().get_by_tech_stack(stack)


def discover_by_concern(concern: str) -> List[Path]:
    """Discover guides addressing a specific concern."""
    return get_discovery().get_by_concern(concern)


def discover_category(category: str) -> List[Path]:
    """Get all guides in a category."""
    return get_discovery().get_by_category(category)


def learning_path(path_name: str) -> List[Path]:
    """Get a predefined learning path."""
    return get_discovery().get_learning_path(path_name)


if __name__ == "__main__":
    # Example usage
    discovery = get_discovery()
    
    print("Available categories:", discovery.get_all_categories())
    print("All guides:", len(discovery.list_all_guides()))
    
    # Example: Get guides for Python backend
    python_guides = discovery.get_by_tech_stack("python-backend")
    print(f"\nPython backend guides ({len(python_guides)}):")
    for guide in python_guides:
        print(f"  - {guide.name}")
    
    # Example: Get onboarding path
    onboarding = discovery.get_learning_path("onboarding")
    print(f"\nOnboarding path ({len(onboarding)}):")
    for guide in onboarding:
        print(f"  - {guide.name}")
