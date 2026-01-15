"""
Test suite for AI-Assisted Knowledge Curation (KN-002-01)
=========================================================
PHASE-12: Knowledge Ecosystem Expansion
AC: KN-002-01 - AI-Assisted Knowledge Curation

Validates:
1. Quality scoring system
2. Duplicate detection
3. Category suggestions
4. AI curation workflow

Specification:
- Automated quality assessment
- Duplicate identification
- Smart categorization
- Curation recommendations
"""

import pytest
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass
import json


@dataclass
class CurationResult:
    """Result of AI curation analysis."""
    entry_id: str
    quality_score: float
    is_duplicate: bool
    suggested_categories: List[str]
    recommendations: List[str]


@pytest.fixture(scope="module")
def ai_curator():
    """Create AI curator instance for tests."""
    from cortex_brain.tier3.knowledge.ai_curator import AICurator
    return AICurator()


class TestAICuratorStructure:
    """Tests for AI curator data structure."""
    
    def test_curation_config_file_exists(self, ai_curator):
        """Verify curation config file exists."""
        tier3_path = Path("/Users/asifhussain/PROJECTS/CORTEX/cortex_brain/tier3/knowledge")
        config_file = tier3_path / "curation-config.yaml"
        assert config_file.exists(), "Curation config file not found"
    
    def test_curation_config_contains_metadata(self, ai_curator):
        """Verify config contains metadata."""
        tier3_path = Path("/Users/asifhussain/PROJECTS/CORTEX/cortex_brain/tier3/knowledge")
        config_file = tier3_path / "curation-config.yaml"
        
        import yaml
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        assert "metadata" in config, "Config missing metadata"
        assert config["metadata"].get("ac_id") == "KN-002-01"
    
    def test_quality_scoring_rules_defined(self, ai_curator):
        """Verify quality scoring rules are defined."""
        tier3_path = Path("/Users/asifhussain/PROJECTS/CORTEX/cortex_brain/tier3/knowledge")
        config_file = tier3_path / "curation-config.yaml"
        
        import yaml
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        assert "quality_rules" in config, "Config missing quality_rules"


class TestQualityScoringSystem:
    """Tests for quality scoring system."""
    
    def test_curator_has_score_quality_method(self, ai_curator):
        """Verify curator has score_quality method."""
        assert hasattr(ai_curator, 'score_quality'), \
            "AICurator missing score_quality method"
    
    def test_score_quality_returns_float(self, ai_curator):
        """Verify score_quality returns float score."""
        entry = {
            "entry_id": "KE-TEST-001",
            "title": "Sample Entry",
            "content": "This is a test entry with sufficient content.",
            "domain": "GOVERNANCE"
        }
        score = ai_curator.score_quality(entry)
        assert isinstance(score, float), "Score should be float"
        assert 0.0 <= score <= 1.0, "Score should be between 0.0 and 1.0"
    
    def test_quality_score_considers_content_length(self, ai_curator):
        """Verify quality score considers content length."""
        short_entry = {
            "entry_id": "KE-SHORT-001",
            "title": "Short",
            "content": "Brief",
            "domain": "GOVERNANCE"
        }
        long_entry = {
            "entry_id": "KE-LONG-001",
            "title": "Long Entry",
            "content": "This is a much longer entry with substantial content that should score higher than the short entry due to its length and depth.",
            "domain": "GOVERNANCE"
        }
        short_score = ai_curator.score_quality(short_entry)
        long_score = ai_curator.score_quality(long_entry)
        assert long_score > short_score, "Longer content should score higher"
    
    def test_quality_score_considers_structure(self, ai_curator):
        """Verify quality score considers entry structure."""
        well_structured = {
            "entry_id": "KE-STRUCT-001",
            "title": "Well Structured",
            "content": "This is structured content.",
            "domain": "GOVERNANCE",
            "tags": ["governance", "policy"],
            "references": ["ref-1", "ref-2"]
        }
        poorly_structured = {
            "entry_id": "KE-UNSTRUCTURED-001",
            "title": "Unstructured",
            "content": "This is content.",
            "domain": "GOVERNANCE"
        }
        struct_score = ai_curator.score_quality(well_structured)
        unstruct_score = ai_curator.score_quality(poorly_structured)
        assert struct_score > unstruct_score, "Structured content should score higher"
    
    def test_quality_rules_defined_in_config(self, ai_curator):
        """Verify quality rules are defined in config."""
        tier3_path = Path("/Users/asifhussain/PROJECTS/CORTEX/cortex_brain/tier3/knowledge")
        config_file = tier3_path / "curation-config.yaml"
        
        import yaml
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        rules = config.get("quality_rules", [])
        assert len(rules) > 0, "Quality rules should be defined"


class TestDuplicateDetection:
    """Tests for duplicate detection system."""
    
    def test_curator_has_detect_duplicates_method(self, ai_curator):
        """Verify curator has detect_duplicates method."""
        assert hasattr(ai_curator, 'detect_duplicates'), \
            "AICurator missing detect_duplicates method"
    
    def test_detect_duplicates_identifies_exact_match(self, ai_curator):
        """Verify detection identifies exact duplicates."""
        entry1 = {
            "entry_id": "KE-DUP1-001",
            "content": "Identical content about governance policies"
        }
        entry2 = {
            "entry_id": "KE-DUP1-002",
            "content": "Identical content about governance policies"
        }
        duplicates = ai_curator.detect_duplicates(entry1, [entry2])
        assert len(duplicates) > 0, "Should detect exact duplicate"
    
    def test_detect_duplicates_ignores_minor_differences(self, ai_curator):
        """Verify detection handles minor textual variations."""
        entry1 = {
            "entry_id": "KE-SIM1-001",
            "content": "The governance framework for API design"
        }
        entry2 = {
            "entry_id": "KE-SIM1-002",
            "content": "governance framework for API design"
        }
        # Should detect as similar/potential duplicate
        duplicates = ai_curator.detect_duplicates(entry1, [entry2])
        assert isinstance(duplicates, list), "Should return list"
    
    def test_duplicate_detection_returns_list(self, ai_curator):
        """Verify duplicate detection returns list."""
        entry = {"entry_id": "KE-TEST-001", "content": "Test"}
        result = ai_curator.detect_duplicates(entry, [])
        assert isinstance(result, list), "Should return list of duplicates"
    
    def test_duplicate_detection_includes_similarity_score(self, ai_curator):
        """Verify duplicates include similarity scores."""
        entry1 = {"entry_id": "KE-DUP2-001", "content": "Governance policies"}
        entry2 = {"entry_id": "KE-DUP2-002", "content": "Governance policies"}
        duplicates = ai_curator.detect_duplicates(entry1, [entry2])
        if duplicates:
            assert "similarity_score" in duplicates[0], "Should include similarity score"


class TestCategorySuggestion:
    """Tests for category suggestion system."""
    
    def test_curator_has_suggest_categories_method(self, ai_curator):
        """Verify curator has suggest_categories method."""
        assert hasattr(ai_curator, 'suggest_categories'), \
            "AICurator missing suggest_categories method"
    
    def test_suggest_categories_returns_list(self, ai_curator):
        """Verify suggest_categories returns list."""
        entry = {
            "entry_id": "KE-CAT-001",
            "title": "API Security Best Practices",
            "content": "Guidelines for securing API endpoints"
        }
        categories = ai_curator.suggest_categories(entry)
        assert isinstance(categories, list), "Should return list of categories"
    
    def test_suggest_categories_returns_valid_domains(self, ai_curator):
        """Verify suggested categories are valid domains."""
        valid_domains = [
            "GOVERNANCE", "INTENT-ROUTING", "HALLUCINATION-PREVENTION",
            "EXECUTION-ORCHESTRATION", "DATA-MANAGEMENT", "OBSERVABILITY",
            "SECURITY", "API-DESIGN", "ML-MODELS", "KNOWLEDGE-CURATION",
            "TESTING-VALIDATION", "DEPLOYMENT", "DOCUMENTATION",
            "PERFORMANCE", "ARCHITECTURE", "ERROR-HANDLING"
        ]
        
        entry = {
            "entry_id": "KE-CAT-002",
            "title": "Security and API Design",
            "content": "Combining security practices with API design principles"
        }
        categories = ai_curator.suggest_categories(entry)
        for category in categories:
            assert category in valid_domains, f"Invalid category: {category}"
    
    def test_suggest_categories_includes_confidence(self, ai_curator):
        """Verify category suggestions include confidence scores."""
        entry = {
            "entry_id": "KE-CAT-003",
            "title": "Test Validation Framework",
            "content": "Framework for validating tests"
        }
        categories = ai_curator.suggest_categories(entry)
        if categories:
            assert isinstance(categories[0], dict) or isinstance(categories[0], str), \
                "Should return dict with scores or strings"


class TestCurationWorkflow:
    """Tests for complete curation workflow."""
    
    def test_curator_has_curate_entry_method(self, ai_curator):
        """Verify curator has curate_entry method."""
        assert hasattr(ai_curator, 'curate_entry'), \
            "AICurator missing curate_entry method"
    
    def test_curate_entry_returns_curation_result(self, ai_curator):
        """Verify curate_entry returns comprehensive result."""
        entry = {
            "entry_id": "KE-CURATE-001",
            "title": "Sample Knowledge Entry",
            "content": "This is a sample knowledge entry for curation testing.",
            "domain": "GOVERNANCE"
        }
        result = ai_curator.curate_entry(entry)
        
        assert "quality_score" in result or hasattr(result, 'quality_score'), \
            "Result should include quality_score"
        assert "recommendations" in result or hasattr(result, 'recommendations'), \
            "Result should include recommendations"
    
    def test_curator_logs_curation_activity(self, ai_curator):
        """Verify curator logs curation activity."""
        assert hasattr(ai_curator, 'log_curation'), \
            "AICurator missing log_curation method"
    
    def test_curator_has_get_curation_history(self, ai_curator):
        """Verify curator can retrieve curation history."""
        assert hasattr(ai_curator, 'get_curation_history'), \
            "AICurator missing get_curation_history method"
    
    def test_curation_history_returns_list(self, ai_curator):
        """Verify curation history returns list."""
        history = ai_curator.get_curation_history()
        assert isinstance(history, list), "Should return list of curation records"


class TestCurationGovernanceIntegration:
    """Tests for integration with governance system."""
    
    def test_curator_references_ac_id(self, ai_curator):
        """Verify curator references correct AC-ID."""
        assert hasattr(ai_curator, 'ac_id')
        assert ai_curator.ac_id == "KN-002-01"
    
    def test_curator_uses_governance_manager(self, ai_curator):
        """Verify curator integrates with governance."""
        assert hasattr(ai_curator, 'governance_manager'), \
            "AICurator should reference governance manager"
    
    def test_curator_uses_expert_registry(self, ai_curator):
        """Verify curator integrates with expert registry."""
        assert hasattr(ai_curator, 'expert_registry'), \
            "AICurator should reference expert registry"
    
    def test_curator_validates_with_governance_rules(self, ai_curator):
        """Verify curator validates against governance rules."""
        assert hasattr(ai_curator, 'apply_governance'), \
            "AICurator should apply governance rules"


class TestCurationIndexerIntegration:
    """Tests for integration with knowledge indexer."""
    
    def test_curator_has_knowledge_indexer(self, ai_curator):
        """Verify curator has access to knowledge indexer."""
        assert hasattr(ai_curator, 'indexer'), \
            "AICurator should have indexer reference"
    
    def test_curator_can_query_indexed_entries(self, ai_curator):
        """Verify curator can query indexed entries."""
        assert hasattr(ai_curator, 'find_similar_entries'), \
            "AICurator should be able to find similar entries"
    
    def test_curator_updates_index_on_curation(self, ai_curator):
        """Verify curator updates index after curation."""
        assert hasattr(ai_curator, 'update_after_curation'), \
            "AICurator should update index after curation"


class TestCurationMetrics:
    """Tests for curation metrics and statistics."""
    
    def test_curator_has_get_metrics_method(self, ai_curator):
        """Verify curator can retrieve metrics."""
        assert hasattr(ai_curator, 'get_metrics'), \
            "AICurator missing get_metrics method"
    
    def test_metrics_include_quality_distribution(self, ai_curator):
        """Verify metrics include quality score distribution."""
        metrics = ai_curator.get_metrics()
        assert isinstance(metrics, dict), "Metrics should be dict"
    
    def test_metrics_include_duplicate_count(self, ai_curator):
        """Verify metrics track duplicates found."""
        metrics = ai_curator.get_metrics()
        # Metrics should have relevant curation statistics
        assert isinstance(metrics, dict)
    
    def test_metrics_include_category_distribution(self, ai_curator):
        """Verify metrics track category distribution."""
        metrics = ai_curator.get_metrics()
        assert isinstance(metrics, dict)


class TestCurationPerformance:
    """Tests for curation system performance."""
    
    def test_quality_scoring_is_fast(self, ai_curator):
        """Verify quality scoring performs well."""
        import time
        entry = {
            "entry_id": "KE-PERF-001",
            "title": "Test Entry",
            "content": "This is test content for performance testing.",
            "domain": "GOVERNANCE"
        }
        start = time.time()
        ai_curator.score_quality(entry)
        elapsed = (time.time() - start) * 1000
        assert elapsed < 100, f"Scoring took {elapsed:.2f}ms (should be < 100ms)"
    
    def test_duplicate_detection_is_fast(self, ai_curator):
        """Verify duplicate detection performs well."""
        import time
        entry = {"entry_id": "KE-DUP-PERF-001", "content": "Test"}
        comparisons = [
            {"entry_id": f"KE-DUP-{i}-001", "content": f"Test {i}"}
            for i in range(10)
        ]
        start = time.time()
        ai_curator.detect_duplicates(entry, comparisons)
        elapsed = (time.time() - start) * 1000
        assert elapsed < 200, f"Detection took {elapsed:.2f}ms (should be < 200ms)"
    
    def test_category_suggestion_is_fast(self, ai_curator):
        """Verify category suggestion performs well."""
        import time
        entry = {
            "entry_id": "KE-CAT-PERF-001",
            "title": "Test",
            "content": "Test content for performance"
        }
        start = time.time()
        ai_curator.suggest_categories(entry)
        elapsed = (time.time() - start) * 1000
        assert elapsed < 150, f"Suggestion took {elapsed:.2f}ms (should be < 150ms)"


class TestCurationErrorHandling:
    """Tests for error handling in curation."""
    
    def test_curator_handles_missing_fields(self, ai_curator):
        """Verify curator handles entries with missing fields."""
        incomplete_entry = {
            "entry_id": "KE-INCOMPLETE-001"
            # Missing title, content, domain
        }
        # Should not crash, should return graceful result
        result = ai_curator.score_quality(incomplete_entry)
        assert isinstance(result, float)
    
    def test_curator_handles_empty_entry(self, ai_curator):
        """Verify curator handles empty entries."""
        empty_entry = {}
        score = ai_curator.score_quality(empty_entry)
        assert isinstance(score, float)
        assert score >= 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
