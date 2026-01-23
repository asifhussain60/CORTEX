"""
Knowledge Repository Integration Module
========================================

Integrates best practices discovery with the main CORTEX knowledge repository,
enabling unified knowledge access and cross-referencing.

Authority: cortex_brain/tier3/knowledge/
Updated: 2026-01-23
"""

from pathlib import Path
from typing import List, Dict, Optional
from enum import Enum
import yaml


class KnowledgeCategory(Enum):
    """Enumeration of knowledge categories in CORTEX."""
    
    ARCHITECTURE = "architecture"
    BACKEND_PYTHON = "backend-python"
    FRONTEND_JS_TS = "frontend-js-ts"
    DEVOPS_INFRASTRUCTURE = "devops-infrastructure"
    SECURITY = "security"
    TESTING_VALIDATION = "testing-validation"
    PERFORMANCE_OPTIMIZATION = "performance-optimization"
    DATABASE_MANAGEMENT = "database-management"
    AI_ML_DOMAINS = "ai-ml-domains"
    UI_UX_DESIGN = "ui-ux-design"
    QA_AUTOMATION_TESTING = "qa-automation-testing"


class KnowledgeRepository:
    """Unified knowledge repository for CORTEX best practices."""
    
    def __init__(self, knowledge_root: Optional[Path] = None) -> None:
        """
        Initialize knowledge repository.
        
        Args:
            knowledge_root: Root path to cortex/knowledge/
                           Defaults to cortex/knowledge
        """
        if knowledge_root is None:
            knowledge_root = Path(__file__).parent
        
        self.knowledge_root = knowledge_root
        self.best_practices_root = knowledge_root / "best-practices"
        self._initialize_registry()
    
    def _initialize_registry(self) -> None:
        """Initialize the knowledge registry."""
        self.registry: Dict[str, Dict] = {
            "metadata": {
                "version": "2.0",
                "created": "2026-01-23",
                "authority": "cortex_brain/tier3/knowledge",
                "total_guides": 35,
            },
            "categories": {},
            "discovery_index": {
                "by_technology_stack": {},
                "by_concern": {},
                "by_category": {},
                "learning_paths": {},
            }
        }
        
        # Load best practices index
        index_path = self.best_practices_root / "INDEX.yaml"
        if index_path.exists():
            with open(index_path) as f:
                bp_index = yaml.safe_load(f)
            self._populate_registry(bp_index)
    
    def _populate_registry(self, bp_index: Dict) -> None:
        """Populate registry from best practices index."""
        # Populate categories
        for category in KnowledgeCategory:
            category_name = category.value
            if category_name in bp_index:
                self.registry["categories"][category_name] = {
                    "description": bp_index[category_name].get("description"),
                    "count": bp_index[category_name].get("count", 0),
                    "guides": bp_index[category_name].get("guides", [])
                }
        
        # Populate discovery index
        discovery = bp_index.get("discovery", {})
        
        for stack_entry in discovery.get("by_technology_stack", []):
            stack = stack_entry.get("stack")
            self.registry["discovery_index"]["by_technology_stack"][stack] = {
                "guides": stack_entry.get("guides", [])
            }
        
        for concern_entry in discovery.get("by_concern", []):
            concern = concern_entry.get("concern")
            self.registry["discovery_index"]["by_concern"][concern] = {
                "guides": concern_entry.get("guides", [])
            }
        
        for usage_key, usage_data in bp_index.get("usage", {}).items():
            self.registry["discovery_index"]["learning_paths"][usage_key] = {
                "description": usage_data.get("description"),
                "sequence": usage_data.get("sequence", [])
            }
    
    def get_guide(self, category: str, guide_name: str) -> Optional[Dict]:
        """
        Retrieve a specific guide.
        
        Args:
            category: Category name
            guide_name: Guide filename (e.g., 'rest-api-design.yaml')
            
        Returns:
            Guide content and metadata, or None if not found
        """
        guide_path = self.best_practices_root / category / guide_name
        
        if not guide_path.exists():
            return None
        
        with open(guide_path) as f:
            guide_data = yaml.safe_load(f)
        
        return {
            "path": str(guide_path.relative_to(self.knowledge_root)),
            "metadata": guide_data.get("metadata", {}),
            "content": guide_data
        }
    
    def list_guides_by_category(self, category: str) -> List[str]:
        """List all guides in a category."""
        category_path = self.best_practices_root / category
        if category_path.exists():
            return sorted([f.name for f in category_path.glob("*.yaml")])
        return []
    
    def list_guides_by_stack(self, tech_stack: str) -> List[str]:
        """List guides for a technology stack."""
        discovery = self.registry["discovery_index"]["by_technology_stack"]
        return discovery.get(tech_stack, {}).get("guides", [])
    
    def list_guides_by_concern(self, concern: str) -> List[str]:
        """List guides addressing a concern."""
        discovery = self.registry["discovery_index"]["by_concern"]
        return discovery.get(concern, {}).get("guides", [])
    
    def get_learning_path(self, path_name: str) -> Dict:
        """Get a learning path with description and sequence."""
        paths = self.registry["discovery_index"]["learning_paths"]
        return paths.get(path_name, {"sequence": []})
    
    def list_learning_paths(self) -> List[str]:
        """List all available learning paths."""
        return list(self.registry["discovery_index"]["learning_paths"].keys())
    
    def list_tech_stacks(self) -> List[str]:
        """List all available technology stacks."""
        return list(self.registry["discovery_index"]["by_technology_stack"].keys())
    
    def list_concerns(self) -> List[str]:
        """List all concerns addressed by guides."""
        return list(self.registry["discovery_index"]["by_concern"].keys())
    
    def list_categories(self) -> List[str]:
        """List all guide categories."""
        return list(self.registry["categories"].keys())
    
    def export_registry(self, output_path: Path) -> None:
        """
        Export the knowledge registry.
        
        Args:
            output_path: Path to export registry YAML
        """
        with open(output_path, 'w') as f:
            yaml.dump(self.registry, f, default_flow_style=False, sort_keys=False)
    
    def get_statistics(self) -> Dict:
        """Get statistics about the knowledge repository."""
        return {
            "version": self.registry["metadata"]["version"],
            "total_guides": self.registry["metadata"]["total_guides"],
            "categories": len(self.list_categories()),
            "tech_stacks": len(self.list_tech_stacks()),
            "concerns": len(self.list_concerns()),
            "learning_paths": len(self.list_learning_paths()),
            "category_breakdown": {
                cat: len(guides)
                for cat, guides in self.registry["categories"].items()
            }
        }


# Convenience singleton
_repo: Optional[KnowledgeRepository] = None


def get_repository() -> KnowledgeRepository:
    """Get or create knowledge repository instance."""
    global _repo
    if _repo is None:
        _repo = KnowledgeRepository()
    return _repo


def get_guide(category: str, guide_name: str) -> Optional[Dict]:
    """Retrieve a guide from the repository."""
    return get_repository().get_guide(category, guide_name)


def list_by_stack(tech_stack: str) -> List[str]:
    """List guides for a technology stack."""
    return get_repository().list_guides_by_stack(tech_stack)


def list_by_concern(concern: str) -> List[str]:
    """List guides addressing a concern."""
    return get_repository().list_guides_by_concern(concern)


def learning_path(path_name: str) -> Dict:
    """Get a learning path."""
    return get_repository().get_learning_path(path_name)


if __name__ == "__main__":
    repo = get_repository()
    
    stats = repo.get_statistics()
    print("Knowledge Repository Statistics:")
    print(f"  Version: {stats['version']}")
    print(f"  Total Guides: {stats['total_guides']}")
    print(f"  Categories: {stats['categories']}")
    print(f"  Tech Stacks: {stats['tech_stacks']}")
    print(f"  Concerns: {stats['concerns']}")
    print(f"  Learning Paths: {stats['learning_paths']}")
    print("\nCategory Breakdown:")
    for cat, count in stats["category_breakdown"].items():
        print(f"  {cat}: {count} guides")
    
    print("\nAvailable Tech Stacks:")
    for stack in repo.list_tech_stacks():
        guides = repo.list_guides_by_stack(stack)
        print(f"  {stack}: {len(guides)} guides")
    
    print("\nAvailable Learning Paths:")
    for path_name in repo.list_learning_paths():
        path_info = repo.get_learning_path(path_name)
        print(f"  {path_name}: {path_info.get('description', 'N/A')}")
