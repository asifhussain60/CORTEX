"""
Company Knowledge Provider - Phase 1 Implementation
CORTEX 5.5 Enhancement Epic

Provides access to company-specific knowledge (architecture, tech stack, APIs, standards).
Company knowledge overrides CORTEX defaults where explicitly defined.
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class CompanyKnowledge:
    """Container for company knowledge data."""
    architecture: Optional[str] = None
    tech_stack: Optional[Dict] = None
    api_catalog: Optional[List[Dict]] = None
    coding_standards: Optional[str] = None
    governance: Optional[Dict] = None


class CompanyKnowledgeProvider:
    """
    Provides access to company-specific knowledge.
    
    Knowledge files are stored in: cortex-brain/tier2/company-knowledge/{company_id}/
    - architecture.md: Architecture patterns & principles
    - tech-stack.yaml: Technology stack (languages, frameworks, tools)
    - api-catalog.json: Internal API inventory
    - coding-standards.md: Coding standards & best practices
    - governance.yaml: Company-specific governance rules
    """
    
    def __init__(self, company_id: str, knowledge_base_path: Optional[Path] = None):
        """
        Initialize knowledge provider for a company.
        
        Args:
            company_id: Unique company identifier
            knowledge_base_path: Override default knowledge base path (for testing)
        """
        self.company_id = company_id
        
        if knowledge_base_path:
            self.company_path = knowledge_base_path / company_id
        else:
            # Default: cortex-brain/tier2/company-knowledge/{company_id}/
            project_root = Path(__file__).parent.parent.parent
            self.company_path = project_root / "cortex-brain" / "tier2" / "company-knowledge" / company_id
        
        self._cache: Optional[CompanyKnowledge] = None
    
    def exists(self) -> bool:
        """Check if company knowledge exists."""
        return self.company_path.exists() and self.company_path.is_dir()
    
    def load_all(self) -> CompanyKnowledge:
        """
        Load all company knowledge files.
        
        Returns:
            CompanyKnowledge object with all loaded data
        """
        if self._cache:
            return self._cache
        
        if not self.exists():
            return CompanyKnowledge()
        
        knowledge = CompanyKnowledge(
            architecture=self._load_markdown("architecture.md"),
            tech_stack=self._load_yaml("tech-stack.yaml"),
            api_catalog=self._load_json("api-catalog.json"),
            coding_standards=self._load_markdown("coding-standards.md"),
            governance=self._load_yaml("governance.yaml")
        )
        
        self._cache = knowledge
        return knowledge
    
    def query_architecture(self, topic: Optional[str] = None) -> Dict[str, Any]:
        """
        Query company architecture information.
        
        Args:
            topic: Optional topic filter (e.g., "security", "deployment")
        
        Returns:
            Dict with architecture information
        """
        knowledge = self.load_all()
        
        if not knowledge.architecture:
            return {"exists": False, "company_id": self.company_id}
        
        result = {
            "exists": True,
            "company_id": self.company_id,
            "content": knowledge.architecture
        }
        
        if topic:
            # Simple topic filtering (search for section containing topic)
            lines = knowledge.architecture.split("\n")
            topic_sections = []
            in_section = False
            current_section = []
            
            for line in lines:
                if line.startswith("#") and topic.lower() in line.lower():
                    in_section = True
                    current_section = [line]
                elif line.startswith("#") and in_section:
                    topic_sections.append("\n".join(current_section))
                    in_section = False
                    current_section = []
                elif in_section:
                    current_section.append(line)
            
            if current_section:
                topic_sections.append("\n".join(current_section))
            
            result["filtered_content"] = "\n\n".join(topic_sections) if topic_sections else None
        
        return result
    
    def query_tech_stack(self, component: Optional[str] = None) -> Dict[str, Any]:
        """
        Query company technology stack.
        
        Args:
            component: Optional component filter (e.g., "languages", "backend", "cloud")
        
        Returns:
            Dict with tech stack information
        """
        knowledge = self.load_all()
        
        if not knowledge.tech_stack:
            return {"exists": False, "company_id": self.company_id}
        
        result = {
            "exists": True,
            "company_id": self.company_id,
            "tech_stack": knowledge.tech_stack
        }
        
        if component and component in knowledge.tech_stack:
            result["filtered"] = {component: knowledge.tech_stack[component]}
        
        return result
    
    def query_api_catalog(self, api_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Query company internal API catalog.
        
        Args:
            api_name: Optional API name filter (e.g., "user-service-api")
        
        Returns:
            Dict with API catalog information
        """
        knowledge = self.load_all()
        
        if not knowledge.api_catalog:
            return {"exists": False, "company_id": self.company_id, "apis": []}
        
        apis = knowledge.api_catalog.get("api_catalog", [])
        
        if api_name:
            filtered = [api for api in apis if api_name.lower() in api.get("api_id", "").lower() 
                       or api_name.lower() in api.get("name", "").lower()]
            return {
                "exists": True,
                "company_id": self.company_id,
                "apis": filtered,
                "total_count": len(filtered)
            }
        
        return {
            "exists": True,
            "company_id": self.company_id,
            "apis": apis,
            "total_count": len(apis)
        }
    
    def query_coding_standards(self, language: Optional[str] = None) -> Dict[str, Any]:
        """
        Query company coding standards.
        
        Args:
            language: Optional language filter (e.g., "C#", "TypeScript")
        
        Returns:
            Dict with coding standards information
        """
        knowledge = self.load_all()
        
        if not knowledge.coding_standards:
            return {"exists": False, "company_id": self.company_id}
        
        result = {
            "exists": True,
            "company_id": self.company_id,
            "content": knowledge.coding_standards
        }
        
        if language:
            # Filter sections related to the language
            lines = knowledge.coding_standards.split("\n")
            language_sections = []
            in_section = False
            current_section = []
            
            for line in lines:
                if line.startswith("#") and language.lower() in line.lower():
                    in_section = True
                    current_section = [line]
                elif line.startswith("#") and in_section:
                    language_sections.append("\n".join(current_section))
                    in_section = False
                    current_section = []
                elif in_section:
                    current_section.append(line)
            
            if current_section:
                language_sections.append("\n".join(current_section))
            
            result["filtered_content"] = "\n\n".join(language_sections) if language_sections else None
        
        return result
    
    def query_governance(self, category: Optional[str] = None) -> Dict[str, Any]:
        """
        Query company governance rules.
        
        Args:
            category: Optional category filter (e.g., "security", "testing", "deployment")
        
        Returns:
            Dict with governance rules
        """
        knowledge = self.load_all()
        
        if not knowledge.governance:
            return {"exists": False, "company_id": self.company_id}
        
        result = {
            "exists": True,
            "company_id": self.company_id,
            "governance": knowledge.governance
        }
        
        if category and category in knowledge.governance:
            result["filtered"] = {category: knowledge.governance[category]}
        
        return result
    
    def get_primary_language(self) -> Optional[str]:
        """Get the company's primary programming language."""
        tech_stack = self.query_tech_stack()
        if not tech_stack.get("exists"):
            return None
        
        languages = tech_stack["tech_stack"].get("languages", [])
        for lang in languages:
            if lang.get("primary"):
                return lang.get("name")
        
        return languages[0].get("name") if languages else None
    
    def get_primary_framework(self, framework_type: str = "backend") -> Optional[str]:
        """
        Get the company's primary framework.
        
        Args:
            framework_type: Type of framework ("backend", "frontend")
        
        Returns:
            Framework name or None
        """
        tech_stack = self.query_tech_stack(component=framework_type)
        if not tech_stack.get("exists"):
            return None
        
        filtered = tech_stack.get("filtered", {})
        if framework_type in filtered:
            return filtered[framework_type].get("framework")
        
        return None
    
    def get_cloud_provider(self) -> Optional[str]:
        """Get the company's cloud provider."""
        tech_stack = self.query_tech_stack(component="cloud")
        if not tech_stack.get("exists"):
            return None
        
        filtered = tech_stack.get("filtered", {})
        if "cloud" in filtered:
            return filtered["cloud"].get("provider")
        
        return None
    
    def _load_markdown(self, filename: str) -> Optional[str]:
        """Load markdown file content."""
        file_path = self.company_path / filename
        if not file_path.exists():
            return None
        
        try:
            return file_path.read_text(encoding="utf-8")
        except Exception:
            return None
    
    def _load_yaml(self, filename: str) -> Optional[Dict]:
        """Load YAML file content."""
        file_path = self.company_path / filename
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except Exception:
            return None
    
    def _load_json(self, filename: str) -> Optional[Dict]:
        """Load JSON file content."""
        file_path = self.company_path / filename
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None
