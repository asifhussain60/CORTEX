"""
Domain Knowledge Accumulator (STATIC-VIZ-003).

Aggregates knowledge across multiple repositories within a domain.

Author: Asif Hussain
Phase: 17 Track B
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Any, Set
from datetime import datetime
import yaml


@dataclass
class DomainKnowledge:
    """Aggregated knowledge for a domain."""
    domain_name: str
    repository_count: int = 0
    total_loc: int = 0
    total_files: int = 0
    repositories: List[str] = field(default_factory=list)
    common_technologies: List[str] = field(default_factory=list)
    all_features: List[str] = field(default_factory=list)
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())


class DomainKnowledgeAccumulator:
    """
    Aggregate domain knowledge across multiple repositories.
    
    Features:
    - Cross-repository aggregation by domain
    - Technology stack analysis (common vs unique)
    - Feature cataloging across domain
    - YAML storage in company/domains/{domain}/ structure
    
    Output Structure:
        company/
            domains/
                ai/
                    knowledge.yaml      # Aggregated AI domain knowledge
                backend/
                    knowledge.yaml      # Aggregated backend domain knowledge
                ...
    """
    
    def __init__(self, output_dir: Path):
        """
        Initialize accumulator.
        
        Args:
            output_dir: Root directory for domain knowledge
        """
        self.output_dir = Path(output_dir)
        self.company_dir = self.output_dir / "company" / "domains"
        self.company_dir.mkdir(parents=True, exist_ok=True)
    
    def aggregate_domain(
        self,
        domain_name: str,
        repositories: List[Dict[str, Any]]
    ) -> DomainKnowledge:
        """
        Aggregate knowledge from all repositories in a domain.
        
        Args:
            domain_name: Domain name (e.g., "ai", "backend")
            repositories: List of repository data dicts
        
        Returns:
            DomainKnowledge with aggregated metrics
        """
        knowledge = DomainKnowledge(domain_name=domain_name)
        
        # Aggregate basic metrics
        knowledge.repository_count = len(repositories)
        knowledge.total_loc = sum(r.get("loc", 0) for r in repositories)
        knowledge.total_files = sum(r.get("files", 0) for r in repositories)
        knowledge.repositories = [r["name"] for r in repositories]
        
        # Aggregate technologies
        knowledge.common_technologies = self._find_common_technologies(repositories)
        
        # Aggregate features
        knowledge.all_features = self._collect_all_features(repositories)
        
        return knowledge
    
    def save_domain_knowledge(self, knowledge: DomainKnowledge) -> Path:
        """
        Save domain knowledge as YAML.
        
        Args:
            knowledge: DomainKnowledge to save
        
        Returns:
            Path to saved knowledge.yaml
        """
        # Create domain directory
        domain_dir = self.company_dir / knowledge.domain_name
        domain_dir.mkdir(parents=True, exist_ok=True)
        
        # Prepare data for YAML
        data = {
            "domain_name": knowledge.domain_name,
            "repository_count": knowledge.repository_count,
            "total_loc": knowledge.total_loc,
            "total_files": knowledge.total_files,
            "repositories": knowledge.repositories,
            "common_technologies": knowledge.common_technologies,
            "all_features": knowledge.all_features,
            "updated_at": knowledge.updated_at,
        }
        
        # Write YAML
        yaml_path = domain_dir / "knowledge.yaml"
        with open(yaml_path, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return yaml_path
    
    def _find_common_technologies(self, repositories: List[Dict[str, Any]]) -> List[str]:
        """
        Find technologies common across multiple repos.
        
        Args:
            repositories: List of repository dicts
        
        Returns:
            List of common technology names
        """
        if not repositories:
            return []
        
        # Collect all technologies from each repo
        tech_sets: List[Set[str]] = []
        for repo in repositories:
            technologies = repo.get("technologies", [])
            if technologies:
                tech_sets.append(set(technologies))
        
        if not tech_sets:
            return []
        
        # Find intersection (common to all repos that have technologies)
        if len(tech_sets) == 1:
            return sorted(list(tech_sets[0]))
        
        common = tech_sets[0]
        for tech_set in tech_sets[1:]:
            common = common.intersection(tech_set)
        
        return sorted(list(common))
    
    def _collect_all_features(self, repositories: List[Dict[str, Any]]) -> List[str]:
        """
        Collect all unique features across domain.
        
        Args:
            repositories: List of repository dicts
        
        Returns:
            List of all feature names (deduplicated)
        """
        all_features: Set[str] = set()
        
        for repo in repositories:
            features = repo.get("features", [])
            if features:
                all_features.update(features)
        
        return sorted(list(all_features))
