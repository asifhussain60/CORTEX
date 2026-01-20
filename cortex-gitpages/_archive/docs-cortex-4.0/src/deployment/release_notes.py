"""Release Notes & User Documentation System"""
from typing import List, Dict, Any


class ReleaseNotesGenerator:
    """Generates release notes from features and fixes."""
    
    def __init__(self):
        self.notes: List[Dict[str, Any]] = []
    
    def add_feature(self, title: str, description: str) -> None:
        """Add feature to release notes.
        
        Args:
            title: Feature title
            description: Feature description
        """
        self.notes.append({"type": "feature", "title": title, "desc": description})
    
    def add_bugfix(self, title: str, description: str) -> None:
        """Add bugfix to release notes.
        
        Args:
            title: Bugfix title
            description: Bugfix description
        """
        self.notes.append({"type": "bugfix", "title": title, "desc": description})
    
    def generate(self) -> str:
        """Generate release notes.
        
        Returns:
            Formatted release notes
        """
        return "\n".join(f"- {n['title']}: {n['desc']}" for n in self.notes)
    
    def get_feature_count(self) -> int:
        """Get count of features.
        
        Returns:
            Feature count
        """
        return sum(1 for n in self.notes if n['type'] == 'feature')


class DocumentationBuilder:
    """Builds user documentation."""
    
    def __init__(self):
        self.sections: Dict[str, str] = {}
    
    def add_section(self, name: str, content: str) -> None:
        """Add documentation section.
        
        Args:
            name: Section name
            content: Section content
        """
        self.sections[name] = content
    
    def build_documentation(self) -> str:
        """Build complete documentation.
        
        Returns:
            Formatted documentation
        """
        result = ""
        for name, content in self.sections.items():
            result += f"## {name}\n{content}\n"
        return result
    
    def get_section_count(self) -> int:
        """Get section count.
        
        Returns:
            Number of sections
        """
        return len(self.sections)
