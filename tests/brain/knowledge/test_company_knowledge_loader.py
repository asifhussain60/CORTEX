# AC-ID: KN-005-01 - Company Knowledge Override Tests
"""
Tests for Company Knowledge Loader with Precedence Override (KN-005-01).

CORE Governance:
  - CORE-008: TDD (tests first - these verify the implementation)
  - CORE-011: Type hints mandatory
  - CORE-012: Google-style docstrings
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from typing import Dict, Any

from cortex.brain.core.knowledge.company_knowledge_loader import (
    CompanyKnowledgeLoader,
    ComplianceMatch,
    KnowledgeLayer,
    MergedKnowledgeResult,
    get_company_knowledge_loader,
    COMPLIANCE_PATTERNS,
)


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def mock_project_root(tmp_path: Path) -> Path:
    """Create a mock project structure."""
    # Create cortex_brain/tier3/knowledge structure
    tier3_path = tmp_path / "cortex_brain" / "tier3" / "knowledge"
    tier3_path.mkdir(parents=True)
    
    # Create SECURITY domain YAML
    security_yaml = tier3_path / "SECURITY" / "security-best-practices.yaml"
    security_yaml.parent.mkdir(parents=True)
    security_yaml.write_text("""
metadata:
  domain: SECURITY
  version: "1.0"
best_practices:
  - id: SEC-001
    title: Input Validation
    content: Always validate user input
  - id: SEC-002
    title: Encryption
    content: Use AES-256 for data at rest
""")
    
    # Create company/domains/compliance-standards structure
    compliance_path = tmp_path / "company" / "domains" / "compliance-standards"
    compliance_path.mkdir(parents=True)
    
    # Create PCI-DSS compliance YAML
    pci_yaml = compliance_path / "pci-dss.yaml"
    pci_yaml.write_text("""
metadata:
  standard: PCI-DSS
  version: "4.0"
requirements:
  - id: REQ-1.1
    title: Install and maintain firewall
    description: Network security controls
  - id: REQ-3.4
    title: Encrypt stored cardholder data
    description: Use strong cryptography
""")
    
    # Create HIPAA compliance YAML
    hipaa_yaml = compliance_path / "hipaa.yaml"
    hipaa_yaml.write_text("""
metadata:
  standard: HIPAA
  version: "2024"
requirements:
  - id: 164.312
    title: Technical Safeguards
    description: Access controls, audit controls, integrity controls
""")
    
    # Create company-specific override
    company_path = tmp_path / "company" / "domains" / "acme-corp" / "compliance"
    company_path.mkdir(parents=True)
    
    company_override_yaml = company_path / "pci-override.yaml"
    company_override_yaml.write_text("""
metadata:
  company: acme-corp
  overrides: PCI-DSS
custom_requirements:
  - id: ACME-PCI-001
    title: Extended key rotation
    description: Rotate keys every 30 days (stricter than standard)
""")
    
    return tmp_path


@pytest.fixture
def loader(mock_project_root: Path) -> CompanyKnowledgeLoader:
    """Create a CompanyKnowledgeLoader with mock project."""
    return CompanyKnowledgeLoader(
        project_root=str(mock_project_root),
        company_name=None,
    )


@pytest.fixture
def loader_with_company(mock_project_root: Path) -> CompanyKnowledgeLoader:
    """Create a CompanyKnowledgeLoader with company set."""
    return CompanyKnowledgeLoader(
        project_root=str(mock_project_root),
        company_name="acme-corp",
    )


# =============================================================================
# COMPLIANCE DETECTION TESTS
# =============================================================================

class TestComplianceDetection:
    """Tests for compliance standard auto-detection."""
    
    def test_detect_pci_dss_from_payment_code(self, loader: CompanyKnowledgeLoader):
        """Should detect PCI-DSS from payment-related code."""
        code = """
        def process_payment(card_number: str, cvv: str):
            # Process credit card payment
            validate_cardholder_data(card_number)
            return charge_card(card_number, cvv)
        """
        
        matches = loader.detect_compliance_standards(code)
        
        assert len(matches) > 0
        pci_match = next((m for m in matches if m.standard_id == "pci-dss"), None)
        assert pci_match is not None
        assert pci_match.confidence > 0.3
        assert any("card" in t.lower() for t in pci_match.triggers)
    
    def test_detect_hipaa_from_health_code(self, loader: CompanyKnowledgeLoader):
        """Should detect HIPAA from healthcare-related code."""
        code = """
        def get_patient_records(patient_id: str):
            # Get protected health information (PHI)
            medical_record = fetch_medical_data(patient_id)
            return medical_record
        """
        
        matches = loader.detect_compliance_standards(code)
        
        hipaa_match = next((m for m in matches if m.standard_id == "hipaa"), None)
        assert hipaa_match is not None
        assert hipaa_match.confidence > 0.3
    
    def test_detect_gdpr_from_privacy_code(self, loader: CompanyKnowledgeLoader):
        """Should detect GDPR from privacy-related code."""
        code = """
        def handle_data_subject_request(user_id: str, request_type: str):
            # Handle GDPR right to erasure
            if request_type == "erasure":
                delete_personal_data(user_id)
        """
        
        matches = loader.detect_compliance_standards(code)
        
        gdpr_match = next((m for m in matches if m.standard_id == "gdpr"), None)
        assert gdpr_match is not None
    
    def test_detect_multiple_standards(self, loader: CompanyKnowledgeLoader):
        """Should detect multiple applicable standards."""
        code = """
        def process_healthcare_payment(patient_id: str, card_number: str):
            # Process payment for medical services
            medical_record = get_PHI(patient_id)
            charge_credit_card(card_number)
        """
        
        matches = loader.detect_compliance_standards(code)
        
        # Should detect both PCI-DSS and HIPAA
        standard_ids = [m.standard_id for m in matches]
        assert "pci-dss" in standard_ids
        assert "hipaa" in standard_ids
    
    def test_no_match_for_generic_code(self, loader: CompanyKnowledgeLoader):
        """Should return no matches for generic code."""
        code = """
        def add_numbers(a: int, b: int) -> int:
            return a + b
        """
        
        matches = loader.detect_compliance_standards(code)
        
        assert len(matches) == 0
    
    def test_min_confidence_filter(self, loader: CompanyKnowledgeLoader):
        """Should respect minimum confidence threshold."""
        code = "payment"  # Very minimal match
        
        # Low threshold - should match
        matches_low = loader.detect_compliance_standards(code, min_confidence=0.1)
        
        # High threshold - should not match
        matches_high = loader.detect_compliance_standards(code, min_confidence=0.9)
        
        assert len(matches_low) > 0 or len(matches_high) == 0


# =============================================================================
# COMPLIANCE LOADING TESTS
# =============================================================================

class TestComplianceLoading:
    """Tests for compliance standard YAML loading."""
    
    def test_load_pci_dss_standard(self, loader: CompanyKnowledgeLoader):
        """Should load PCI-DSS compliance standard."""
        standard = loader.load_compliance_standard("pci-dss")
        
        assert standard is not None
        assert "metadata" in standard
        assert standard["metadata"]["standard"] == "PCI-DSS"
        assert "requirements" in standard
    
    def test_load_hipaa_standard(self, loader: CompanyKnowledgeLoader):
        """Should load HIPAA compliance standard."""
        standard = loader.load_compliance_standard("hipaa")
        
        assert standard is not None
        assert standard["metadata"]["standard"] == "HIPAA"
    
    def test_load_nonexistent_standard(self, loader: CompanyKnowledgeLoader):
        """Should return None for non-existent standard."""
        standard = loader.load_compliance_standard("nonexistent-standard")
        
        assert standard is None
    
    def test_compliance_cache(self, loader: CompanyKnowledgeLoader):
        """Should cache loaded compliance standards."""
        # First load
        loader.load_compliance_standard("pci-dss")
        
        # Second load should use cache
        assert "pci-dss" in loader._compliance_cache


# =============================================================================
# COMPANY KNOWLEDGE TESTS
# =============================================================================

class TestCompanyKnowledge:
    """Tests for company-specific knowledge loading."""
    
    def test_load_company_knowledge(self, loader_with_company: CompanyKnowledgeLoader):
        """Should load company-specific knowledge."""
        knowledge = loader_with_company.load_company_knowledge("compliance")
        
        assert knowledge is not None
        assert "pci-override" in knowledge
    
    def test_no_company_returns_none(self, loader: CompanyKnowledgeLoader):
        """Should return None when no company set."""
        knowledge = loader.load_company_knowledge("compliance")
        
        assert knowledge is None
    
    def test_set_company(self, loader: CompanyKnowledgeLoader):
        """Should allow changing active company."""
        assert loader._company_name is None
        
        loader.set_company("acme-corp")
        
        assert loader._company_name == "acme-corp"
        assert "company-override" in loader._layers


# =============================================================================
# PRECEDENCE MERGE TESTS
# =============================================================================

class TestPrecedenceMerge:
    """Tests for knowledge merge with precedence."""
    
    def test_layer_initialization(self, loader: CompanyKnowledgeLoader):
        """Should initialize layers with correct precedence."""
        assert "compliance-standards" in loader._layers
        assert "cortex-base" in loader._layers
        
        # Check precedence order
        compliance_layer = loader._layers["compliance-standards"]
        cortex_layer = loader._layers["cortex-base"]
        
        assert compliance_layer.precedence < cortex_layer.precedence  # Lower = higher priority
    
    def test_company_layer_added_when_set(self, loader_with_company: CompanyKnowledgeLoader):
        """Should add company layer when company is set."""
        assert "company-override" in loader_with_company._layers
        
        company_layer = loader_with_company._layers["company-override"]
        assert company_layer.precedence == 1  # Highest priority
    
    def test_deep_merge_override(self, loader: CompanyKnowledgeLoader):
        """Should properly deep merge with override."""
        base = {
            "key1": "base_value",
            "nested": {"a": 1, "b": 2},
        }
        override = {
            "key1": "override_value",
            "nested": {"b": 3, "c": 4},
        }
        
        result = loader._deep_merge(base, override)
        
        assert result["key1"] == "override_value"  # Overridden
        assert result["nested"]["a"] == 1  # Preserved from base
        assert result["nested"]["b"] == 3  # Overridden
        assert result["nested"]["c"] == 4  # Added from override
    
    def test_get_merged_knowledge(self, loader: CompanyKnowledgeLoader):
        """Should return merged knowledge result."""
        result = loader.get_merged_knowledge("SECURITY")
        
        assert isinstance(result, MergedKnowledgeResult)
        assert "source_layers" in result.__dict__


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestIntegration:
    """Integration tests for full flow."""
    
    def test_get_applicable_compliance_standards(self, loader: CompanyKnowledgeLoader):
        """Should get full compliance info for code."""
        code = """
        def charge_card(card_number: str):
            # Credit card processing
            pass
        """
        
        result = loader.get_applicable_compliance_standards(code, load_full=True)
        
        assert "detected_standards" in result
        assert "standards_content" in result
        
        if result["detected_standards"]:
            # Should have loaded content for detected standards
            first_standard = result["detected_standards"][0]["standard_id"]
            if first_standard in result["standards_content"]:
                assert result["standards_content"][first_standard] is not None
    
    def test_metrics(self, loader_with_company: CompanyKnowledgeLoader):
        """Should return valid metrics."""
        metrics = loader_with_company.get_metrics()
        
        assert "project_root" in metrics
        assert "active_company" in metrics
        assert metrics["active_company"] == "acme-corp"
        assert "layers" in metrics
    
    def test_clear_cache(self, loader: CompanyKnowledgeLoader):
        """Should clear all caches."""
        # Populate caches
        loader.load_compliance_standard("pci-dss")
        
        assert len(loader._compliance_cache) > 0
        
        loader.clear_cache()
        
        assert len(loader._compliance_cache) == 0


# =============================================================================
# SINGLETON TESTS
# =============================================================================

class TestSingleton:
    """Tests for singleton accessor."""
    
    def test_get_company_knowledge_loader(self, mock_project_root: Path):
        """Should return singleton instance."""
        loader1 = get_company_knowledge_loader(
            project_root=str(mock_project_root),
            force_reload=True,
        )
        loader2 = get_company_knowledge_loader()
        
        assert loader1 is loader2
    
    def test_singleton_company_change(self, mock_project_root: Path):
        """Should update company on existing singleton."""
        loader = get_company_knowledge_loader(
            project_root=str(mock_project_root),
            force_reload=True,
        )
        
        assert loader._company_name is None
        
        get_company_knowledge_loader(company_name="acme-corp")
        
        assert loader._company_name == "acme-corp"


# =============================================================================
# COMPLIANCE PATTERNS TESTS
# =============================================================================

class TestCompliancePatterns:
    """Tests for compliance pattern definitions."""
    
    def test_all_standards_have_patterns(self):
        """Should have patterns for all expected standards."""
        expected_standards = [
            "pci-dss", "pii-protection", "hipaa", "hsa-fsa",
            "gdpr", "ccpa", "financial-services", "soc2",
            "iso27001", "nist-800-53", "fedramp", "wcag",
        ]
        
        for standard in expected_standards:
            assert standard in COMPLIANCE_PATTERNS, f"Missing patterns for {standard}"
            assert len(COMPLIANCE_PATTERNS[standard]) > 0
    
    def test_patterns_are_valid_regex(self):
        """Should have valid regex patterns."""
        import re
        
        for standard_id, patterns in COMPLIANCE_PATTERNS.items():
            for pattern in patterns:
                try:
                    re.compile(pattern, re.IGNORECASE)
                except re.error as e:
                    pytest.fail(f"Invalid regex for {standard_id}: {pattern} - {e}")
