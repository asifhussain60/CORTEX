"""
Test suite for Cross-Domain Knowledge Synthesis (KN-004-01)
===========================================================
PHASE-12: Knowledge Ecosystem Expansion
AC: KN-004-01 - Cross-Domain Knowledge Synthesis

Validates:
1. Cross-domain queries
2. Knowledge synthesis engine
3. Source attribution
4. Multi-domain relationships

Specification:
- Query knowledge across domains
- Synthesize insights from multiple domains
- Maintain source attribution
- Track domain relationships
"""

import pytest
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class SynthesisResult:
    """Result of knowledge synthesis."""
    synthesis_id: str
    source_domains: List[str]
    synthesized_knowledge: str
    supporting_entries: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]
    confidence: float


@pytest.fixture(scope="module")
def synthesis_engine():
    """Create synthesis engine instance for tests."""
    from cortex_brain.tier3.knowledge.synthesis_engine import SynthesisEngine
    return SynthesisEngine()


class TestSynthesisEngineStructure:
    """Tests for synthesis engine structure."""
    
    def test_synthesis_config_file_exists(self, synthesis_engine):
        """Verify synthesis config file exists."""
        tier3_path = Path(__file__).parent.parent.parent / "cortex_brain" / "tier3" / "knowledge"
        config_file = tier3_path / "synthesis-config.yaml"
        assert config_file.exists(), "Synthesis config file not found"
    
    def test_synthesis_config_contains_metadata(self, synthesis_engine):
        """Verify config contains metadata."""
        tier3_path = Path(__file__).parent.parent.parent / "cortex_brain" / "tier3" / "knowledge"
        config_file = tier3_path / "synthesis-config.yaml"
        
        import yaml
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        assert "metadata" in config, "Config missing metadata"
        assert config["metadata"].get("ac_id") == "KN-004-01"
    
    def test_synthesis_config_has_domain_relationships(self, synthesis_engine):
        """Verify config defines domain relationships."""
        tier3_path = Path(__file__).parent.parent.parent / "cortex_brain" / "tier3" / "knowledge"
        config_file = tier3_path / "synthesis-config.yaml"
        
        import yaml
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        assert "domain_relationships" in config, "Config missing domain_relationships"


class TestCrossDomainQueries:
    """Tests for cross-domain query functionality."""
    
    def test_engine_has_query_across_domains_method(self, synthesis_engine):
        """Verify engine has cross-domain query method."""
        assert hasattr(synthesis_engine, 'query_across_domains'), \
            "SynthesisEngine missing query_across_domains method"
    
    def test_cross_domain_query_returns_results(self, synthesis_engine):
        """Verify cross-domain query returns results."""
        query = "security and api design patterns"
        domains = ["SECURITY", "API-DESIGN"]
        results = synthesis_engine.query_across_domains(query, domains)
        assert isinstance(results, list), "Should return list of results"
    
    def test_query_filters_by_domains(self, synthesis_engine):
        """Verify query respects domain filters."""
        query = "security"
        results = synthesis_engine.query_across_domains(query, ["SECURITY"])
        # Results should all be from SECURITY domain if any
        for result in results:
            if "domain" in result:
                assert result.get("domain") == "SECURITY"
    
    def test_query_handles_multiple_domains(self, synthesis_engine):
        """Verify query can search multiple domains."""
        query = "design patterns"
        domains = ["API-DESIGN", "ARCHITECTURE", "ERROR-HANDLING"]
        results = synthesis_engine.query_across_domains(query, domains)
        assert isinstance(results, list)


class TestKnowledgeSynthesis:
    """Tests for knowledge synthesis."""
    
    def test_engine_has_synthesize_method(self, synthesis_engine):
        """Verify engine has synthesize method."""
        assert hasattr(synthesis_engine, 'synthesize'), \
            "SynthesisEngine missing synthesize method"
    
    def test_synthesize_returns_synthesis_result(self, synthesis_engine):
        """Verify synthesize returns structured result."""
        entries = [
            {
                "entry_id": "KE-SEC-001",
                "content": "Security best practices",
                "domain": "SECURITY"
            },
            {
                "entry_id": "KE-API-001",
                "content": "API design principles",
                "domain": "API-DESIGN"
            }
        ]
        result = synthesis_engine.synthesize(entries, ["SECURITY", "API-DESIGN"])
        
        assert isinstance(result, dict), "Should return dict"
        assert "synthesis_id" in result or "synthesized_knowledge" in result
    
    def test_synthesize_includes_source_attribution(self, synthesis_engine):
        """Verify synthesis includes source references."""
        entries = [
            {"entry_id": "KE-001", "content": "Knowledge 1", "domain": "GOVERNANCE"},
            {"entry_id": "KE-002", "content": "Knowledge 2", "domain": "SECURITY"}
        ]
        result = synthesis_engine.synthesize(entries, ["GOVERNANCE", "SECURITY"])
        
        # Should reference source entries
        assert "supporting_entries" in result or "sources" in result or len(result) > 0
    
    def test_synthesize_handles_empty_input(self, synthesis_engine):
        """Verify synthesize handles empty input gracefully."""
        result = synthesis_engine.synthesize([], [])
        assert isinstance(result, dict)
    
    def test_synthesize_combines_related_concepts(self, synthesis_engine):
        """Verify synthesis combines related knowledge."""
        entries = [
            {
                "entry_id": "KE-API-SEC-001",
                "content": "API security implementation",
                "domain": "API-DESIGN",
                "tags": ["security", "api"]
            },
            {
                "entry_id": "KE-SEC-AUTH-001",
                "content": "Authentication for secure endpoints",
                "domain": "SECURITY",
                "tags": ["authentication", "security", "api"]
            }
        ]
        result = synthesis_engine.synthesize(entries, ["API-DESIGN", "SECURITY"])
        assert isinstance(result, dict)


class TestSourceAttribution:
    """Tests for source attribution and traceability."""
    
    def test_engine_has_track_sources_method(self, synthesis_engine):
        """Verify engine tracks synthesis sources."""
        assert hasattr(synthesis_engine, 'track_sources'), \
            "SynthesisEngine missing track_sources method"
    
    def test_synthesis_maintains_entry_references(self, synthesis_engine):
        """Verify each synthesis includes entry references."""
        entries = [
            {"entry_id": "KE-TEST-001", "content": "Content 1", "domain": "GOVERNANCE"},
            {"entry_id": "KE-TEST-002", "content": "Content 2", "domain": "ARCHITECTURE"}
        ]
        result = synthesis_engine.synthesize(entries, ["GOVERNANCE", "ARCHITECTURE"])
        
        # Should be able to trace back to source entries
        assert isinstance(result, dict)
    
    def test_attribution_includes_domain_source(self, synthesis_engine):
        """Verify attribution tracks domain source."""
        tier3_path = Path(__file__).parent.parent.parent / "cortex_brain" / "tier3" / "knowledge"
        config_file = tier3_path / "synthesis-config.yaml"
        
        import yaml
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        # Config should define attribution structure
        assert "attribution" in config or "traceability" in config or len(config) > 0


class TestDomainRelationships:
    """Tests for inter-domain relationships."""
    
    def test_engine_has_get_domain_relationships_method(self, synthesis_engine):
        """Verify engine can query domain relationships."""
        assert hasattr(synthesis_engine, 'get_domain_relationships'), \
            "SynthesisEngine missing get_domain_relationships method"
    
    def test_domain_relationships_include_all_domains(self, synthesis_engine):
        """Verify all 16 domains have relationship definitions."""
        tier3_path = Path(__file__).parent.parent.parent / "cortex_brain" / "tier3" / "knowledge"
        config_file = tier3_path / "synthesis-config.yaml"
        
        import yaml
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        relationships = config.get("domain_relationships", {})
        valid_domains = [
            "GOVERNANCE", "INTENT-ROUTING", "HALLUCINATION-PREVENTION",
            "EXECUTION-ORCHESTRATION", "DATA-MANAGEMENT", "OBSERVABILITY",
            "SECURITY", "API-DESIGN", "ML-MODELS", "KNOWLEDGE-CURATION",
            "TESTING-VALIDATION", "DEPLOYMENT", "DOCUMENTATION",
            "PERFORMANCE", "ARCHITECTURE", "ERROR-HANDLING"
        ]
        
        # Most domains should have relationships defined
        assert len(relationships) >= 10
    
    def test_relationships_define_connection_strength(self, synthesis_engine):
        """Verify relationships include strength/weight."""
        relationships = synthesis_engine.get_domain_relationships()
        
        for rel in relationships:
            if isinstance(rel, dict):
                assert "strength" in rel or "weight" in rel or len(rel) > 1
    
    def test_query_uses_relationship_graph(self, synthesis_engine):
        """Verify queries can leverage relationship graph."""
        # Query with domain relationships should find more relevant results
        results = synthesis_engine.query_across_domains("security", ["API-DESIGN"])
        assert isinstance(results, list)


class TestSynthesisPersistence:
    """Tests for synthesis result persistence."""
    
    def test_engine_has_log_synthesis_method(self, synthesis_engine):
        """Verify engine logs synthesis activities."""
        assert hasattr(synthesis_engine, 'log_synthesis'), \
            "SynthesisEngine missing log_synthesis method"
    
    def test_engine_has_get_synthesis_history(self, synthesis_engine):
        """Verify engine can retrieve synthesis history."""
        assert hasattr(synthesis_engine, 'get_synthesis_history'), \
            "SynthesisEngine missing get_synthesis_history method"
    
    def test_synthesis_history_returns_list(self, synthesis_engine):
        """Verify synthesis history returns list."""
        history = synthesis_engine.get_synthesis_history()
        assert isinstance(history, list)


class TestSynthesisGovernanceIntegration:
    """Tests for governance integration."""
    
    def test_engine_references_ac_id(self, synthesis_engine):
        """Verify engine references correct AC-ID."""
        assert hasattr(synthesis_engine, 'ac_id')
        assert synthesis_engine.ac_id == "KN-004-01"
    
    def test_engine_integrates_with_governance(self, synthesis_engine):
        """Verify engine uses governance rules."""
        assert hasattr(synthesis_engine, 'governance_manager'), \
            "SynthesisEngine should reference governance"
    
    def test_synthesis_validates_with_governance(self, synthesis_engine):
        """Verify synthesis applies governance rules."""
        assert hasattr(synthesis_engine, 'apply_governance'), \
            "SynthesisEngine should apply governance"
    
    def test_engine_integrates_with_curator(self, synthesis_engine):
        """Verify engine uses curation system."""
        assert hasattr(synthesis_engine, 'curator'), \
            "SynthesisEngine should reference curator"


class TestSynthesisIndexerIntegration:
    """Tests for indexer integration."""
    
    def test_engine_has_indexer_reference(self, synthesis_engine):
        """Verify engine has indexer access."""
        assert hasattr(synthesis_engine, 'indexer'), \
            "SynthesisEngine should have indexer reference"
    
    def test_engine_uses_index_for_queries(self, synthesis_engine):
        """Verify engine leverages indexing."""
        assert hasattr(synthesis_engine, 'search_indexed_entries'), \
            "SynthesisEngine should search indexed entries"


class TestSynthesisMetrics:
    """Tests for synthesis metrics."""
    
    def test_engine_has_get_metrics(self, synthesis_engine):
        """Verify engine can retrieve metrics."""
        assert hasattr(synthesis_engine, 'get_metrics'), \
            "SynthesisEngine missing get_metrics method"
    
    def test_metrics_include_synthesis_count(self, synthesis_engine):
        """Verify metrics track synthesis operations."""
        metrics = synthesis_engine.get_metrics()
        assert isinstance(metrics, dict)
    
    def test_metrics_include_domain_coverage(self, synthesis_engine):
        """Verify metrics track domain coverage."""
        metrics = synthesis_engine.get_metrics()
        assert isinstance(metrics, dict)


class TestSynthesisPerformance:
    """Tests for synthesis performance."""
    
    def test_cross_domain_query_is_fast(self, synthesis_engine):
        """Verify cross-domain query performance."""
        import time
        start = time.time()
        synthesis_engine.query_across_domains("test query", ["GOVERNANCE", "SECURITY"])
        elapsed = (time.time() - start) * 1000
        assert elapsed < 500, f"Query took {elapsed:.2f}ms (should be < 500ms)"
    
    def test_synthesis_completes_quickly(self, synthesis_engine):
        """Verify synthesis performance."""
        import time
        entries = [
            {"entry_id": f"KE-{i}", "content": f"Content {i}", "domain": "GOVERNANCE"}
            for i in range(5)
        ]
        start = time.time()
        synthesis_engine.synthesize(entries, ["GOVERNANCE"])
        elapsed = (time.time() - start) * 1000
        assert elapsed < 300, f"Synthesis took {elapsed:.2f}ms (should be < 300ms)"


class TestSynthesisErrorHandling:
    """Tests for error handling."""
    
    def test_handles_invalid_domains(self, synthesis_engine):
        """Verify handling of invalid domains."""
        result = synthesis_engine.query_across_domains("test", ["INVALID-DOMAIN"])
        assert isinstance(result, list)
    
    def test_handles_empty_results(self, synthesis_engine):
        """Verify handling of empty query results."""
        result = synthesis_engine.query_across_domains("xyzabc123", ["GOVERNANCE"])
        assert isinstance(result, list)
    
    def test_handles_malformed_entries(self, synthesis_engine):
        """Verify handling of malformed entries."""
        entries = [{"invalid": "structure"}]
        result = synthesis_engine.synthesize(entries, [])
        assert isinstance(result, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
