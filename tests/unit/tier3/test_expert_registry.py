"""
Test suite for Domain Expert Registry (KN-003-02)
==================================================
PHASE-12: Knowledge Ecosystem Expansion
AC: KN-003-02 - Domain Expert Registry

Validates:
1. Expert registry populated
2. Expertise areas mapped
3. Validation workflow defined

Specification:
- Registry of domain experts
- Expertise area mapping
- Validation workflow
"""

import pytest
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class Expert:
    """Represents a domain expert."""
    expert_id: str
    name: str
    email: str
    domains: List[str]
    expertise_level: str  # 'expert', 'advanced', 'intermediate'
    active: bool


@pytest.fixture(scope="module")
def expert_registry():
    """Create expert registry instance for tests."""
    from cortex_brain.tier3.knowledge.expert_registry import ExpertRegistry
    return ExpertRegistry()


class TestExpertRegistryStructure:
    """Tests for expert registry data structure."""
    
    def test_expert_registry_file_exists(self, expert_registry):
        """Verify expert registry file exists."""
        tier3_path = Path(__file__).parent.parent.parent / "cortex-brain" / "tier3" / "knowledge"
        registry_file = tier3_path / "expert-registry.yaml"
        assert registry_file.exists(), "Expert registry file not found"
    
    def test_expert_registry_contains_metadata(self, expert_registry):
        """Verify registry contains metadata."""
        tier3_path = Path(__file__).parent.parent.parent / "cortex-brain" / "tier3" / "knowledge"
        registry_file = tier3_path / "expert-registry.yaml"
        
        import yaml
        with open(registry_file, 'r') as f:
            registry = yaml.safe_load(f)
        
        assert "metadata" in registry, "Registry missing metadata"
        assert "ac_id" in registry["metadata"], "Metadata missing ac_id"
        assert registry["metadata"]["ac_id"] == "KN-003-02"
    
    def test_expert_registry_contains_experts(self, expert_registry):
        """Verify registry contains experts list."""
        tier3_path = Path(__file__).parent.parent.parent / "cortex-brain" / "tier3" / "knowledge"
        registry_file = tier3_path / "expert-registry.yaml"
        
        import yaml
        with open(registry_file, 'r') as f:
            registry = yaml.safe_load(f)
        
        assert "experts" in registry, "Registry missing experts"
        assert isinstance(registry["experts"], list), "Experts should be a list"


class TestExpertData:
    """Tests for expert data structure and validation."""
    
    def test_expert_has_required_fields(self, expert_registry):
        """Verify each expert has required fields."""
        tier3_path = Path(__file__).parent.parent.parent / "cortex-brain" / "tier3" / "knowledge"
        registry_file = tier3_path / "expert-registry.yaml"
        
        import yaml
        with open(registry_file, 'r') as f:
            registry = yaml.safe_load(f)
        
        required_fields = ["expert_id", "name", "email", "domains", "expertise_level"]
        
        for expert in registry.get("experts", []):
            for field in required_fields:
                assert field in expert, f"Expert missing required field: {field}"
    
    def test_expert_domains_are_valid(self, expert_registry):
        """Verify expert domains are valid."""
        valid_domains = [
            "GOVERNANCE", "INTENT-ROUTING", "HALLUCINATION-PREVENTION",
            "EXECUTION-ORCHESTRATION", "DATA-MANAGEMENT", "OBSERVABILITY",
            "SECURITY", "API-DESIGN", "ML-MODELS", "KNOWLEDGE-CURATION",
            "TESTING-VALIDATION", "DEPLOYMENT", "DOCUMENTATION",
            "PERFORMANCE", "ARCHITECTURE", "ERROR-HANDLING"
        ]
        
        tier3_path = Path(__file__).parent.parent.parent / "cortex-brain" / "tier3" / "knowledge"
        registry_file = tier3_path / "expert-registry.yaml"
        
        import yaml
        with open(registry_file, 'r') as f:
            registry = yaml.safe_load(f)
        
        for expert in registry.get("experts", []):
            for domain in expert.get("domains", []):
                assert domain in valid_domains, f"Invalid domain for expert {expert['expert_id']}: {domain}"
    
    def test_expert_expertise_level_valid(self, expert_registry):
        """Verify expertise levels are valid."""
        valid_levels = ["expert", "advanced", "intermediate"]
        
        tier3_path = Path(__file__).parent.parent.parent / "cortex-brain" / "tier3" / "knowledge"
        registry_file = tier3_path / "expert-registry.yaml"
        
        import yaml
        with open(registry_file, 'r') as f:
            registry = yaml.safe_load(f)
        
        for expert in registry.get("experts", []):
            assert expert.get("expertise_level") in valid_levels, \
                f"Invalid expertise level for {expert['expert_id']}: {expert.get('expertise_level')}"


class TestExpertRegistryAPI:
    """Tests for expert registry API methods."""
    
    def test_registry_has_get_expert_method(self, expert_registry):
        """Verify registry has get_expert method."""
        assert hasattr(expert_registry, 'get_expert'), \
            "ExpertRegistry missing get_expert method"
    
    def test_registry_has_get_experts_by_domain(self, expert_registry):
        """Verify registry has get_experts_by_domain method."""
        assert hasattr(expert_registry, 'get_experts_by_domain'), \
            "ExpertRegistry missing get_experts_by_domain method"
    
    def test_registry_has_add_expert(self, expert_registry):
        """Verify registry has add_expert method."""
        assert hasattr(expert_registry, 'add_expert'), \
            "ExpertRegistry missing add_expert method"
    
    def test_registry_has_is_expert_for_domain(self, expert_registry):
        """Verify registry has is_expert_for_domain method."""
        assert hasattr(expert_registry, 'is_expert_for_domain'), \
            "ExpertRegistry missing is_expert_for_domain method"
    
    def test_get_experts_by_domain_returns_list(self, expert_registry):
        """Verify get_experts_by_domain returns list."""
        result = expert_registry.get_experts_by_domain("GOVERNANCE")
        assert isinstance(result, list), "Should return list of experts"


class TestExpertDomainMapping:
    """Tests for expert domain mapping."""
    
    def test_all_16_domains_have_experts(self, expert_registry):
        """Verify all 16 domains have at least one expert."""
        domains = [
            "GOVERNANCE", "INTENT-ROUTING", "HALLUCINATION-PREVENTION",
            "EXECUTION-ORCHESTRATION", "DATA-MANAGEMENT", "OBSERVABILITY",
            "SECURITY", "API-DESIGN", "ML-MODELS", "KNOWLEDGE-CURATION",
            "TESTING-VALIDATION", "DEPLOYMENT", "DOCUMENTATION",
            "PERFORMANCE", "ARCHITECTURE", "ERROR-HANDLING"
        ]
        
        for domain in domains:
            experts = expert_registry.get_experts_by_domain(domain)
            assert len(experts) > 0, f"No experts found for domain: {domain}"
    
    def test_domain_mapping_includes_expertise_level(self, expert_registry):
        """Verify domain mapping includes expertise levels."""
        tier3_path = Path(__file__).parent.parent.parent / "cortex-brain" / "tier3" / "knowledge"
        registry_file = tier3_path / "expert-registry.yaml"
        
        import yaml
        with open(registry_file, 'r') as f:
            registry = yaml.safe_load(f)
        
        for expert in registry.get("experts", []):
            assert expert.get("expertise_level") is not None


class TestExpertValidationWorkflow:
    """Tests for expert validation workflow."""
    
    def test_registry_has_can_validate_entry_method(self, expert_registry):
        """Verify registry has can_validate_entry method."""
        assert hasattr(expert_registry, 'can_validate_entry'), \
            "ExpertRegistry missing can_validate_entry method"
    
    def test_registry_has_log_validation_method(self, expert_registry):
        """Verify registry has log_validation method."""
        assert hasattr(expert_registry, 'log_validation'), \
            "ExpertRegistry missing log_validation method"
    
    def test_can_validate_entry_returns_bool(self, expert_registry):
        """Verify can_validate_entry returns boolean."""
        result = expert_registry.can_validate_entry(expert_id="EXPERT-001", domain="GOVERNANCE")
        assert isinstance(result, bool), "Should return boolean"
    
    def test_registry_has_get_validation_log(self, expert_registry):
        """Verify registry has get_validation_log method."""
        assert hasattr(expert_registry, 'get_validation_log'), \
            "ExpertRegistry missing get_validation_log method"


class TestExpertGovernanceIntegration:
    """Tests for integration with governance system."""
    
    def test_registry_references_ac_id(self, expert_registry):
        """Verify registry references correct AC-ID."""
        assert hasattr(expert_registry, 'ac_id')
        assert expert_registry.ac_id == "KN-003-02"
    
    def test_expert_registry_links_to_governance_rules(self, expert_registry):
        """Verify registry links to governance rules."""
        tier3_path = Path(__file__).parent.parent.parent / "cortex-brain" / "tier3" / "knowledge"
        registry_file = tier3_path / "expert-registry.yaml"
        
        import yaml
        with open(registry_file, 'r') as f:
            registry = yaml.safe_load(f)
        
        assert "metadata" in registry
        assert registry["metadata"].get("ac_id") == "KN-003-02"
    
    def test_expert_validation_integrates_with_governance(self, expert_registry):
        """Verify expert validation can integrate with governance."""
        # Should have ability to validate entries
        assert hasattr(expert_registry, 'validate_entry_with_expert')


class TestExpertRegistryInitialization:
    """Tests for expert registry initialization."""
    
    def test_registry_initializes_with_default_experts(self, expert_registry):
        """Verify registry initializes with default experts."""
        tier3_path = Path(__file__).parent.parent.parent / "cortex-brain" / "tier3" / "knowledge"
        registry_file = tier3_path / "expert-registry.yaml"
        
        import yaml
        with open(registry_file, 'r') as f:
            registry = yaml.safe_load(f)
        
        assert len(registry.get("experts", [])) > 0, "Registry should have default experts"
    
    def test_registry_has_proper_metadata(self, expert_registry):
        """Verify registry has proper metadata."""
        tier3_path = Path(__file__).parent.parent.parent / "cortex-brain" / "tier3" / "knowledge"
        registry_file = tier3_path / "expert-registry.yaml"
        
        import yaml
        with open(registry_file, 'r') as f:
            registry = yaml.safe_load(f)
        
        metadata = registry.get("metadata", {})
        assert metadata.get("ac_id") == "KN-003-02"
        assert "created_at" in metadata
        assert "version" in metadata


class TestExpertQueryPerformance:
    """Tests for query performance."""
    
    def test_get_expert_is_fast(self, expert_registry):
        """Verify get_expert queries are fast."""
        import time
        start = time.time()
        expert_registry.get_expert("EXPERT-001")
        elapsed = (time.time() - start) * 1000
        assert elapsed < 10, f"Query took {elapsed:.2f}ms (should be < 10ms)"
    
    def test_domain_lookup_is_fast(self, expert_registry):
        """Verify domain lookups are fast."""
        import time
        start = time.time()
        expert_registry.get_experts_by_domain("GOVERNANCE")
        elapsed = (time.time() - start) * 1000
        assert elapsed < 50, f"Query took {elapsed:.2f}ms (should be < 50ms)"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
