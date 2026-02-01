"""
Business Language Translator
Converts technical terms to business-friendly language
"""

from typing import Dict, Any, List


class BusinessTranslator:
    """Translate technical terms to business-friendly language"""
    
    # Technical → Business use case mapping
    USE_CASE_MAPPING = {
        "crud": {"title": "📝 Manage organizational data", "icon": "📝"},
        "data management": {"title": "📝 Manage organizational data", "icon": "📝"},
        "reporting": {"title": "📊 Track key performance indicators", "icon": "📊"},
        "analytics": {"title": "📊 Analyze business insights", "icon": "📊"},
        "notifications": {"title": "🔔 Stay informed with real-time alerts", "icon": "🔔"},
        "file": {"title": "📁 Organize and share documents", "icon": "📁"},
        "scheduling": {"title": "📅 Plan and coordinate activities", "icon": "📅"},
        "search": {"title": "🔍 Find information quickly", "icon": "🔍"},
        "authentication": {"title": "🔐 Secure user access", "icon": "🔐"},
        "api": {"title": "🔌 Connect with other systems", "icon": "🔌"}
    }
    
    # Technology → Business description mapping
    TECH_MAPPING = {
        "Python": {"description": "Modern data processing", "icon": "🐍"},
        "Node.js": {"description": "Scalable backend", "icon": "🟢"},
        "React": {"description": "Interactive user interface", "icon": "⚛️"},
        "SQL Server": {"description": "Enterprise data storage", "icon": "🗄️"},
        "ASP.NET": {"description": "Robust web framework", "icon": "🔷"},
        "VB.NET": {"description": "Legacy business logic", "icon": "🟦"},
        "C#": {"description": "Enterprise development", "icon": "🟪"}
    }
    
    def translate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Translate technical data to business-friendly format"""
        
        # Translate use cases
        if "overview" in data and "use_cases" in data["overview"]:
            data["overview"]["use_cases"] = self._translate_use_cases(
                data["overview"]["use_cases"]
            )
        
        # Translate tech stack
        if "tech_stack" in data and "technologies" in data["tech_stack"]:
            data["tech_stack"]["technologies"] = self._translate_technologies(
                data["tech_stack"]["technologies"]
            )
        
        # Translate project description
        if "overview" in data and "project" in data["overview"]:
            data["overview"]["project"]["description"] = self._make_business_friendly(
                data["overview"]["project"].get("description", "")
            )
        
        return data
    
    def _translate_use_cases(self, use_cases: List[Dict]) -> List[Dict]:
        """Translate technical use case titles to business-friendly"""
        
        for uc in use_cases:
            title_lower = uc.get("title", "").lower()
            
            # Find matching business term
            for tech_term, business_term in self.USE_CASE_MAPPING.items():
                if tech_term in title_lower:
                    uc["title"] = business_term["title"]
                    if "icon" not in uc:
                        uc["icon"] = business_term["icon"]
                    break
        
        return use_cases
    
    def _translate_technologies(self, technologies: List[Dict]) -> List[Dict]:
        """Add business-friendly descriptions to technologies"""
        
        for tech in technologies:
            name = tech.get("name", "")
            if name in self.TECH_MAPPING:
                mapping = self.TECH_MAPPING[name]
                tech["description"] = mapping["description"]
                if "icon" not in tech:
                    tech["icon"] = mapping["icon"]
        
        return technologies
    
    def _make_business_friendly(self, description: str) -> str:
        """Convert technical jargon to business language"""
        
        # Remove technical terms
        replacements = {
            "CRUD": "data management",
            "REST API": "web services",
            "microservices": "modular architecture",
            "monolithic": "unified application",
            "CI/CD": "automated deployment",
            "containerized": "portable deployment"
        }
        
        result = description
        for tech, business in replacements.items():
            result = result.replace(tech, business)
        
        return result
