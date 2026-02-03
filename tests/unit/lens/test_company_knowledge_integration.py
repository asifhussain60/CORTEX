"""
Tests for Company Knowledge Integration in LENS.

Authority: Phase 20 Component #2 (AC_LENS_COMPANY_002)
Rule: CORE-008 (TDD First)
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List
from pathlib import Path

from cortex.lens.orchestrator import LENSOrchestrator


class TestCompanyKnowledgeIntegration:
    """Test company knowledge integration in LENSOrchestrator."""
    
    @pytest.fixture
    def lens_orchestrator(self, tmp_path: Path) -> LENSOrchestrator:
        """Create LENSOrchestrator instance with temp repo."""
        # Create a temp git repo
        repo_dir = tmp_path / "test_repo"
        repo_dir.mkdir()
        return LENSOrchestrator(repo_path=repo_dir)
    
    @pytest.fixture
    def sample_company_domain(self) -> Dict[str, Any]:
        """Sample company domain knowledge."""
        return {
            "domain": "financial-services",
            "rules": [
                {
                    "rule_id": "FIN-001",
                    "description": "All financial calculations must use Decimal",
                    "severity": "ERROR",
                    "patterns": ["import decimal", "Decimal("]
                }
            ],
            "patterns": {
                "known": [
                    {"pattern": "stripe.api_key", "category": "payment", "confidence": 0.99}
                ]
            },
            "precedence": "OVERRIDE"
        }
    
    def test_load_company_domains_exists(
        self,
        lens_orchestrator: LENSOrchestrator,
        tmp_path: Path
    ):
        """Test loading company domains when files exist."""
        # Create mock company domain YAML
        company_dir = tmp_path / "company" / "domains"
        company_dir.mkdir(parents=True)
        
        domain_file = company_dir / "financial-services.yaml"
        domain_file.write_text("""
domain: financial-services
rules:
  - rule_id: FIN-001
    description: Use Decimal for money
    severity: ERROR
""")
        
        # Mock the company domains path
        with patch("cortex.lens.orchestrator.Path") as mock_path:
            mock_path.return_value = company_dir.parent
            
            domains = lens_orchestrator._load_company_domains("financial-services")
        
        assert domains is not None
        assert "rules" in domains or len(domains) > 0
    
    def test_load_company_domains_not_found(
        self,
        lens_orchestrator: LENSOrchestrator
    ):
        """Test loading company domains when files don't exist."""
        domains = lens_orchestrator._load_company_domains("nonexistent-company")
        
        # Should return empty dict, not raise
        assert domains == {}
    
    def test_detect_compliance_pci_dss(
        self,
        lens_orchestrator: LENSOrchestrator
    ):
        """Test PCI-DSS compliance detection."""
        code_content = """
import stripe
stripe.api_key = "sk_test_key"

def process_payment(card_number):
    # Store credit card number
    db.save(card_number)
"""
        
        compliance = lens_orchestrator._detect_compliance(code_content)
        
        assert "detected_standards" in compliance
        # Should detect PCI-DSS from credit card patterns
        standards = [s["standard_id"] for s in compliance["detected_standards"]]
        assert any("PCI" in s for s in standards)
    
    def test_detect_compliance_hipaa(
        self,
        lens_orchestrator: LENSOrchestrator
    ):
        """Test HIPAA compliance detection."""
        code_content = """
class Patient:
    def __init__(self, ssn, medical_record):
        self.ssn = ssn
        self.medical_record = medical_record
        
    def save_to_s3(self):
        # Unencrypted health data
        upload(self.medical_record)
"""
        
        compliance = lens_orchestrator._detect_compliance(code_content)
        
        assert "detected_standards" in compliance
        standards = [s["standard_id"] for s in compliance["detected_standards"]]
        assert any("HIPAA" in s for s in standards)
    
    def test_merge_knowledge_company_override(
        self,
        lens_orchestrator: LENSOrchestrator,
        sample_company_domain: Dict[str, Any]
    ):
        """Test knowledge merging with company override."""
        base_knowledge = {
            "rules": [
                {"rule_id": "CORTEX-001", "description": "Base rule"}
            ]
        }
        
        company_knowledge = {
            "rules": [
                {"rule_id": "FIN-001", "description": "Company rule"}
            ],
            "precedence": "OVERRIDE"
        }
        
        merged = lens_orchestrator._merge_knowledge(
            base_knowledge,
            company_knowledge,
            {}
        )
        
        # Company rules should take precedence
        assert len(merged["rules"]) > 0
        assert any(r["rule_id"] == "FIN-001" for r in merged["rules"])
    
    def test_merge_knowledge_merge_mode(
        self,
        lens_orchestrator: LENSOrchestrator
    ):
        """Test knowledge merging with MERGE mode."""
        base_knowledge = {
            "rules": [
                {"rule_id": "CORTEX-001", "description": "Base rule"}
            ]
        }
        
        company_knowledge = {
            "rules": [
                {"rule_id": "FIN-001", "description": "Company rule"}
            ],
            "precedence": "MERGE"
        }
        
        merged = lens_orchestrator._merge_knowledge(
            base_knowledge,
            company_knowledge,
            {}
        )
        
        # Both sets of rules should be present
        assert len(merged["rules"]) >= 2
        assert any(r["rule_id"] == "CORTEX-001" for r in merged["rules"])
        assert any(r["rule_id"] == "FIN-001" for r in merged["rules"])
    
    def test_merge_knowledge_compliance_flags(
        self,
        lens_orchestrator: LENSOrchestrator
    ):
        """Test compliance flags in merged knowledge."""
        compliance_flags = {
            "detected_standards": [
                {"standard_id": "PCI-DSS-3.2.1", "confidence": 0.95}
            ]
        }
        
        merged = lens_orchestrator._merge_knowledge(
            {},
            {},
            compliance_flags
        )
        
        assert "compliance_flags" in merged
        assert len(merged["compliance_flags"]["detected_standards"]) == 1
    
    @patch("cortex.lens.orchestrator.LENSOrchestrator._load_company_domains")
    @patch("cortex.lens.orchestrator.LENSOrchestrator._detect_compliance")
    @patch("cortex.lens.orchestrator.LENSOrchestrator.analyze_file")
    def test_analyze_with_company_knowledge(
        self,
        mock_analyze: Mock,
        mock_detect: Mock,
        mock_load: Mock,
        lens_orchestrator: LENSOrchestrator,
        sample_company_domain: Dict[str, Any]
    ):
        """Test analyze_with_company_knowledge method."""
        # Setup mocks
        mock_analyze.return_value = {
            "git_analysis": {"commits": 10},
            "ast_analysis": {"complexity": 5}
        }
        mock_load.return_value = sample_company_domain
        mock_detect.return_value = {
            "detected_standards": [
                {"standard_id": "PCI-DSS", "confidence": 0.90}
            ]
        }
        
        # Call method
        result = lens_orchestrator.analyze_with_company_knowledge(
            "/test/file.py",
            "acme-corp"
        )
        
        # Verify structure
        assert "git_analysis" in result
        assert "ast_analysis" in result
        assert "company_knowledge" in result
        assert "compliance_flags" in result["company_knowledge"]
    
    def test_knowledge_precedence_tracking(
        self,
        lens_orchestrator: LENSOrchestrator
    ):
        """Test knowledge precedence tracking in merged result."""
        base_knowledge = {"rules": [{"rule_id": "C-1"}]}
        company_knowledge = {"rules": [{"rule_id": "F-1"}], "precedence": "OVERRIDE"}
        compliance = {"detected_standards": [{"standard_id": "PCI"}]}
        
        merged = lens_orchestrator._merge_knowledge(
            base_knowledge,
            company_knowledge,
            compliance
        )
        
        assert "knowledge_precedence" in merged
        precedence = merged["knowledge_precedence"]
        assert "company_overrides" in precedence
        assert "cortex_base" in precedence


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
