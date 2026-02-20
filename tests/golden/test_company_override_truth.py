"""Golden Test: Company Override Truth - Production Verification Harness

Tests real company standards override using production CompanyKnowledgeLoader.
Zero mocks - uses real precedence-based knowledge merging.

RED PHASE:
- Tests must fail if company knowledge doesn't override CORTEX base
- Tests must fail if precedence order incorrect
- Tests must fail if knowledge merging loses data

GREEN PHASE:
- Company layer (precedence 1) overrides cortex-base (precedence 3)
- Compliance standards (precedence 2) between them
- Deep merge preserves all non-conflicting fields

REFACTOR PHASE:
- Clean test data setup
- Modular precedence validation
- Comprehensive merge testing

AC-ID: AC-PHASE24-S1-006
"""

import pytest
from pathlib import Path
from typing import Dict, Any

from cortex.core.core.knowledge.company_knowledge_loader import (
    CompanyKnowledgeLoader,
    KnowledgeLayer,
    MergedKnowledgeResult
)


class TestCompanyOverrideTruth:
    """Company Override Truth Test with Real CompanyKnowledgeLoader."""
    
    @pytest.fixture
    def loader(self, tmp_path: Path) -> CompanyKnowledgeLoader:
        """Initialize loader with temp project root."""
        # Create directory structure
        (tmp_path / "cortex-registry" / "company" / "domains").mkdir(parents=True)
        (tmp_path / "cortex_intelligence" / "tier3" / "knowledge").mkdir(parents=True)
        
        return CompanyKnowledgeLoader(project_root=str(tmp_path))
    
    @pytest.fixture
    def loader_with_company(self, tmp_path: Path) -> CompanyKnowledgeLoader:
        """Initialize loader with company set."""
        # Create directory structure
        company_dir = tmp_path / "cortex-registry" / "company" / "domains" / "acme-corp"
        company_dir.mkdir(parents=True)
        cortex_dir = tmp_path / "cortex_intelligence" / "tier3" / "knowledge"
        cortex_dir.mkdir(parents=True)
        
        loader = CompanyKnowledgeLoader(
            project_root=str(tmp_path),
            company_name="acme-corp"
        )
        return loader
    
    def test_company_layer_highest_precedence(self, loader_with_company: CompanyKnowledgeLoader):
        """
        RED PHASE: Test must fail if:
        1. Company layer not created when company set
        2. Company layer precedence not 1 (highest)
        3. Layer ordering incorrect
        
        GREEN PHASE: Test passes when:
        1. Company layer exists in _layers
        2. Company layer precedence == 1 (highest priority)
        3. Precedence order: company (1) < compliance (2) < cortex (3)
        """
        # Assert: Company layer exists
        assert "company-override" in loader_with_company._layers
        
        # Assert: Company layer has highest precedence (lowest number)
        company_layer = loader_with_company._layers["company-override"]
        assert company_layer.precedence == 1
        
        # Assert: Other layers have correct precedence
        compliance_layer = loader_with_company._layers["compliance-standards"]
        cortex_layer = loader_with_company._layers["cortex-base"]
        
        assert compliance_layer.precedence == 2
        assert cortex_layer.precedence == 3
        
        # Assert: Precedence ordering correct (lower = higher priority)
        assert company_layer.precedence < compliance_layer.precedence
        assert compliance_layer.precedence < cortex_layer.precedence
    
    def test_no_company_layer_when_not_set(self, loader: CompanyKnowledgeLoader):
        """Verify company layer not created when company not set."""
        # Assert: No company layer
        assert "company-override" not in loader._layers
        
        # Assert: Only compliance and cortex layers
        assert "compliance-standards" in loader._layers
        assert "cortex-base" in loader._layers
        assert len(loader._layers) == 2
    
    def test_set_company_adds_layer(self, loader: CompanyKnowledgeLoader):
        """Test setting company dynamically adds layer."""
        # Initial state: no company layer
        assert "company-override" not in loader._layers
        
        # Set company
        loader.set_company("test-company")
        
        # Assert: Company layer added
        assert "company-override" in loader._layers
        assert loader._company_name == "test-company"
        
        # Assert: Correct precedence
        company_layer = loader._layers["company-override"]
        assert company_layer.precedence == 1


class TestKnowledgePrecedence:
    """Test knowledge layer precedence ordering."""
    
    @pytest.fixture
    def loader(self, tmp_path: Path) -> CompanyKnowledgeLoader:
        """Initialize loader."""
        (tmp_path / "cortex-registry" / "company" / "domains").mkdir(parents=True)
        (tmp_path / "cortex_intelligence" / "tier3" / "knowledge").mkdir(parents=True)
        return CompanyKnowledgeLoader(project_root=str(tmp_path))
    
    def test_deep_merge_preserves_nested_data(self, loader: CompanyKnowledgeLoader):
        """Verify deep merge preserves non-conflicting nested data."""
        base = {
            "key1": "base_value",
            "nested": {
                "a": 1,
                "b": 2,
                "deep": {"x": "base_x"}
            },
            "array": [1, 2]
        }
        
        override = {
            "key1": "override_value",
            "nested": {
                "b": 3,
                "c": 4,
                "deep": {"y": "override_y"}
            },
            "new_key": "new_value"
        }
        
        # Execute deep merge
        result = loader._deep_merge(base, override)
        
        # Assert: Overridden values
        assert result["key1"] == "override_value"
        assert result["nested"]["b"] == 3
        
        # Assert: Preserved base values
        assert result["nested"]["a"] == 1
        
        # Assert: New values added
        assert result["nested"]["c"] == 4
        assert result["new_key"] == "new_value"
        
        # Assert: Deep nesting handled
        assert result["nested"]["deep"]["x"] == "base_x"
        assert result["nested"]["deep"]["y"] == "override_y"
    
    def test_deep_merge_list_replacement(self, loader: CompanyKnowledgeLoader):
        """Verify lists are replaced, not merged."""
        base = {"rules": [1, 2, 3]}
        override = {"rules": [4, 5]}
        
        result = loader._deep_merge(base, override)
        
        # Assert: Override list replaces base list (not merged)
        assert result["rules"] == [4, 5]
    
    def test_get_merged_knowledge_structure(self, loader: CompanyKnowledgeLoader):
        """Test merged knowledge result structure."""
        # Execute merge
        result = loader.get_merged_knowledge("test-domain")
        
        # Assert: Result is MergedKnowledgeResult
        assert isinstance(result, MergedKnowledgeResult)
        
        # Assert: Has required fields (actual API)
        assert hasattr(result, "merged_content")
        assert hasattr(result, "source_layers")
        assert hasattr(result, "override_count")
        assert hasattr(result, "merge_timestamp")
        
        # Assert: merged_content is dict
        assert isinstance(result.merged_content, dict)
        
        # Assert: source_layers is list of layer names
        assert isinstance(result.source_layers, list)


class TestLayerMetrics:
    """Test knowledge layer metrics and tracking."""
    
    @pytest.fixture
    def loader(self, tmp_path: Path) -> CompanyKnowledgeLoader:
        """Initialize loader."""
        (tmp_path / "cortex-registry" / "company" / "domains").mkdir(parents=True)
        (tmp_path / "cortex_intelligence" / "tier3" / "knowledge").mkdir(parents=True)
        return CompanyKnowledgeLoader(project_root=str(tmp_path))
    
    def test_metrics_tracking(self, loader: CompanyKnowledgeLoader):
        """Verify loader tracks usage metrics."""
        # Access metrics
        metrics = loader.get_metrics()
        
        # Assert: Metrics exist
        assert isinstance(metrics, dict)
        
        # Assert: Has expected metric fields (actual API)
        assert "project_root" in metrics
        assert "layers" in metrics
        assert "cached_merges" in metrics
    
    def test_cache_clearing(self, loader: CompanyKnowledgeLoader):
        """Test cache can be cleared."""
        # Load some knowledge (triggers cache)
        loader.get_merged_knowledge("test-domain")
        
        # Clear cache
        loader.clear_cache()
        
        # Assert: Cache cleared (metrics should reflect)
        metrics = loader.get_metrics()
        assert metrics["cached_merges"] == 0


class TestComplianceDetection:
    """Test compliance standard detection."""
    
    @pytest.fixture
    def loader(self, tmp_path: Path) -> CompanyKnowledgeLoader:
        """Initialize loader."""
        (tmp_path / "cortex-registry" / "company" / "domains").mkdir(parents=True)
        (tmp_path / "cortex_intelligence" / "tier3" / "knowledge").mkdir(parents=True)
        return CompanyKnowledgeLoader(project_root=str(tmp_path))
    
    def test_detect_pci_dss_patterns(self, loader: CompanyKnowledgeLoader):
        """Test PCI-DSS pattern detection."""
        code_content = """
        # Payment card processing
        credit_card_number = encrypt_card_data(card)
        cardholder_name = validate_name(name)
        """
        
        matches = loader.detect_compliance_standards(code_content)
        
        # Assert: PCI-DSS detected
        pci_matches = [m for m in matches if m.standard_id == "pci-dss"]
        assert len(pci_matches) > 0
        
        # Assert: Match has required fields (actual API: triggers, not matched_terms)
        if pci_matches:
            match = pci_matches[0]
            assert match.confidence > 0.0
            assert match.triggers  # List of triggered patterns
    
    def test_detect_hipaa_patterns(self, loader: CompanyKnowledgeLoader):
        """Test HIPAA pattern detection."""
        code_content = """
        # Healthcare data processing
        patient_record = load_phi(patient_id)
        medical_history = encrypt_health_data(data)
        """
        
        matches = loader.detect_compliance_standards(code_content)
        
        # Assert: HIPAA detected
        hipaa_matches = [m for m in matches if m.standard_id == "hipaa"]
        assert len(hipaa_matches) > 0
    
    def test_no_detection_for_generic_code(self, loader: CompanyKnowledgeLoader):
        """Test no false positives for generic code."""
        code_content = """
        def add_numbers(a, b):
            return a + b
        """
        
        matches = loader.detect_compliance_standards(code_content)
        
        # Assert: No matches for generic code
        assert len(matches) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
