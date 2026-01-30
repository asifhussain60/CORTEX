"""
Test Domain Knowledge Accumulator (STATIC-VIZ-003).

Tests aggregation of knowledge across multiple repositories in a domain.

AC Coverage:
- VIZ-003-AC01: Aggregate domain knowledge from multiple repos
- VIZ-003-AC02: Store in company/domains/{domain}/ structure
"""

import pytest
from pathlib import Path
import yaml
from cortex.visualization.domain_knowledge_accumulator import (
    DomainKnowledgeAccumulator,
    DomainKnowledge,
)


class TestDomainAggregation:
    """Test domain knowledge aggregation (VIZ-003-AC01)."""
    
    def test_aggregate_single_repository(self, tmp_path):
        """Aggregate knowledge from single repository."""
        accumulator = DomainKnowledgeAccumulator(output_dir=tmp_path)
        
        repo_data = {
            "name": "cortex",
            "domain": "ai",
            "features": ["LENS Intelligence", "Multi-model estimation"],
            "technologies": ["Python", "FastAPI"],
        }
        
        domain_knowledge = accumulator.aggregate_domain("ai", [repo_data])
        
        assert domain_knowledge.domain_name == "ai"
        assert domain_knowledge.repository_count == 1
        assert "cortex" in domain_knowledge.repositories
    
    def test_aggregate_multiple_repositories(self, tmp_path):
        """Aggregate knowledge from multiple repos in same domain."""
        accumulator = DomainKnowledgeAccumulator(output_dir=tmp_path)
        
        repos = [
            {"name": "cortex", "domain": "ai", "loc": 50000},
            {"name": "ml-pipeline", "domain": "ai", "loc": 30000},
            {"name": "data-processor", "domain": "ai", "loc": 15000},
        ]
        
        domain_knowledge = accumulator.aggregate_domain("ai", repos)
        
        assert domain_knowledge.repository_count == 3
        assert domain_knowledge.total_loc == 95000
        assert len(domain_knowledge.repositories) == 3
    
    def test_aggregate_common_technologies(self, tmp_path):
        """Aggregate should identify common technologies across repos."""
        accumulator = DomainKnowledgeAccumulator(output_dir=tmp_path)
        
        repos = [
            {"name": "cortex", "domain": "ai", "technologies": ["Python", "FastAPI", "Docker"]},
            {"name": "ml-pipeline", "domain": "ai", "technologies": ["Python", "PyTorch", "Docker"]},
        ]
        
        domain_knowledge = accumulator.aggregate_domain("ai", repos)
        
        # Python and Docker are common
        assert "Python" in domain_knowledge.common_technologies
        assert "Docker" in domain_knowledge.common_technologies
    
    def test_aggregate_domain_features(self, tmp_path):
        """Aggregate should collect all features across domain."""
        accumulator = DomainKnowledgeAccumulator(output_dir=tmp_path)
        
        repos = [
            {"name": "cortex", "domain": "ai", "features": ["LENS", "Estimation"]},
            {"name": "ml-pipeline", "domain": "ai", "features": ["Training", "Inference"]},
        ]
        
        domain_knowledge = accumulator.aggregate_domain("ai", repos)
        
        # Should have all features
        all_features = domain_knowledge.all_features
        assert "LENS" in all_features
        assert "Estimation" in all_features
        assert "Training" in all_features
        assert "Inference" in all_features


class TestKnowledgeStorage:
    """Test domain knowledge storage (VIZ-003-AC02)."""
    
    def test_save_domain_knowledge_yaml(self, tmp_path):
        """Save domain knowledge as YAML."""
        accumulator = DomainKnowledgeAccumulator(output_dir=tmp_path)
        
        repos = [
            {"name": "cortex", "domain": "ai", "loc": 50000},
        ]
        
        domain_knowledge = accumulator.aggregate_domain("ai", repos)
        result = accumulator.save_domain_knowledge(domain_knowledge)
        
        # Should create company/domains/ai/knowledge.yaml
        yaml_path = tmp_path / "company" / "domains" / "ai" / "knowledge.yaml"
        assert yaml_path.exists()
        assert result == yaml_path
    
    def test_yaml_contains_aggregated_data(self, tmp_path):
        """YAML should contain all aggregated domain data."""
        accumulator = DomainKnowledgeAccumulator(output_dir=tmp_path)
        
        repos = [
            {"name": "cortex", "domain": "ai", "loc": 50000},
            {"name": "ml-pipeline", "domain": "ai", "loc": 30000},
        ]
        
        domain_knowledge = accumulator.aggregate_domain("ai", repos)
        yaml_path = accumulator.save_domain_knowledge(domain_knowledge)
        
        # Read and validate YAML
        with open(yaml_path) as f:
            data = yaml.safe_load(f)
        
        assert data["domain_name"] == "ai"
        assert data["repository_count"] == 2
        assert data["total_loc"] == 80000
        assert "cortex" in data["repositories"]
        assert "ml-pipeline" in data["repositories"]
    
    def test_update_existing_domain_knowledge(self, tmp_path):
        """Update should merge with existing domain knowledge."""
        accumulator = DomainKnowledgeAccumulator(output_dir=tmp_path)
        
        # First save
        repos1 = [{"name": "cortex", "domain": "ai", "loc": 50000}]
        knowledge1 = accumulator.aggregate_domain("ai", repos1)
        accumulator.save_domain_knowledge(knowledge1)
        
        # Second save (add new repo)
        repos2 = [
            {"name": "cortex", "domain": "ai", "loc": 50000},
            {"name": "ml-pipeline", "domain": "ai", "loc": 30000},
        ]
        knowledge2 = accumulator.aggregate_domain("ai", repos2)
        yaml_path = accumulator.save_domain_knowledge(knowledge2)
        
        # Should have updated data
        with open(yaml_path) as f:
            data = yaml.safe_load(f)
        
        assert data["repository_count"] == 2
        assert data["total_loc"] == 80000
    
    def test_multiple_domains_separate_files(self, tmp_path):
        """Multiple domains should have separate knowledge.yaml files."""
        accumulator = DomainKnowledgeAccumulator(output_dir=tmp_path)
        
        # AI domain
        ai_repos = [{"name": "cortex", "domain": "ai"}]
        ai_knowledge = accumulator.aggregate_domain("ai", ai_repos)
        ai_path = accumulator.save_domain_knowledge(ai_knowledge)
        
        # Backend domain
        backend_repos = [{"name": "api-gateway", "domain": "backend"}]
        backend_knowledge = accumulator.aggregate_domain("backend", backend_repos)
        backend_path = accumulator.save_domain_knowledge(backend_knowledge)
        
        # Should have separate files
        assert ai_path == tmp_path / "company" / "domains" / "ai" / "knowledge.yaml"
        assert backend_path == tmp_path / "company" / "domains" / "backend" / "knowledge.yaml"
        assert ai_path.exists()
        assert backend_path.exists()
