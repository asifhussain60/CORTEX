"""
Expert Registry - Tier 3.

Manages domain expert registry for knowledge validation.

AC: KN-003-02 - Domain Expert Registry
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Any, Optional
import yaml


@dataclass
class Expert:
    """Represents a domain expert."""
    expert_id: str
    name: str
    email: str
    domains: List[str]
    expertise_level: str
    active: bool


class ExpertRegistry:
    """Registry of domain experts for knowledge validation."""
    
    def __init__(self) -> None:
        """Initialize expert registry."""
        self._experts: Dict[str, Expert] = {}
        self._load_registry()
    
    def _load_registry(self) -> None:
        """Load expert registry from YAML file."""
        registry_file = Path(__file__).parent / "expert-registry.yaml"
        if registry_file.exists():
            with open(registry_file, 'r') as f:
                data = yaml.safe_load(f)
                for expert_data in data.get("experts", []):
                    expert = Expert(
                        expert_id=expert_data["expert_id"],
                        name=expert_data["name"],
                        email=expert_data["email"],
                        domains=expert_data["domains"],
                        expertise_level=expert_data["expertise_level"],
                        active=expert_data.get("active", True)
                    )
                    self._experts[expert.expert_id] = expert
    
    def get_expert(self, expert_id: str) -> Optional[Expert]:
        """
        Get expert by ID.
        
        Args:
            expert_id: Expert ID
            
        Returns:
            Expert object or None
        """
        return self._experts.get(expert_id)
    
    def get_experts_for_domain(self, domain: str) -> List[Expert]:
        """
        Get all experts for a specific domain.
        
        Args:
            domain: Domain name
            
        Returns:
            List of experts
        """
        return [
            expert for expert in self._experts.values()
            if domain in expert.domains and expert.active
        ]
    
    def list_all_experts(self) -> List[Expert]:
        """
        List all experts.
        
        Returns:
            List of all experts
        """
        return list(self._experts.values())
    
    def get_expertise_areas(self, expert_id: str) -> List[str]:
        """
        Get expertise areas for an expert.
        
        Args:
            expert_id: Expert ID
            
        Returns:
            List of domain names
        """
        expert = self._experts.get(expert_id)
        return expert.domains if expert else []
    
    def validate_entry_with_expert(self, entry: Dict[str, Any], expert_id: str) -> Dict[str, Any]:
        """
        Validate knowledge entry with expert review.
        
        Args:
            entry: Entry to validate
            expert_id: Expert ID
            
        Returns:
            Validation result
        """
        expert = self._experts.get(expert_id)
        if not expert:
            return {"valid": False, "error": "Expert not found"}
        
        if "domain" in entry and entry["domain"] not in expert.domains:
            return {"valid": False, "error": "Expert not qualified for domain"}
        
        return {"valid": True, "expert": expert.name}


__all__ = ["ExpertRegistry", "Expert"]
