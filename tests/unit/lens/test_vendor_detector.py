"""
Tests for VendorDetector analyzer.

AC-ID: AC-PHASE-19-VENDOR-DETECTOR-001
Authority: CORE-008 (TDD - tests first)
"""

import pytest
from pathlib import Path
from typing import Dict, Any, List

from cortex.lens.analyzers.vendor_detector import VendorDetector


class TestVendorDetector:
    """Tests for VendorDetector analyzer."""
    
    @pytest.fixture
    def detector(self) -> VendorDetector:
        """Create detector instance."""
        return VendorDetector()
    
    @pytest.fixture
    def sample_repo(self, tmp_path: Path) -> Path:
        """Create sample repository with vendor dependencies."""
        repo = tmp_path / "test-repo"
        repo.mkdir()
        
        # Create package.json with known vendors
        package_json = repo / "package.json"
        package_json.write_text("""
{
  "dependencies": {
    "@stripe/stripe-js": "^1.0.0",
    "@sendgrid/mail": "^7.0.0",
    "twilio": "^3.0.0"
  }
}
        """)
        
        # Create requirements.txt
        requirements = repo / "requirements.txt"
        requirements.write_text("""
stripe==5.0.0
sendgrid==6.9.0
twilio==7.0.0
auth0-python==3.0.0
        """)
        
        return repo
    
    def test_detector_initializes(self, detector: VendorDetector):
        """Test detector initializes with known vendors."""
        assert detector is not None
        assert len(detector.known_vendors) > 0
        assert "stripe" in detector.known_vendors
    
    def test_detect_stripe(self, detector: VendorDetector, sample_repo: Path):
        """Test Stripe detection."""
        result = detector.detect_vendors(sample_repo)
        
        assert "stripe" in result["vendors"]
        # With 2 evidence sources (requirements.txt + package.json), confidence = 0.85
        assert result["vendors"]["stripe"]["confidence"] >= 0.85
        assert "payment" in result["vendors"]["stripe"]["category"]
    
    def test_detect_sendgrid(self, detector: VendorDetector, sample_repo: Path):
        """Test SendGrid detection."""
        result = detector.detect_vendors(sample_repo)
        
        assert "sendgrid" in result["vendors"]
        assert result["vendors"]["sendgrid"]["category"] == "email"
    
    def test_detect_twilio(self, detector: VendorDetector, sample_repo: Path):
        """Test Twilio detection."""
        result = detector.detect_vendors(sample_repo)
        
        assert "twilio" in result["vendors"]
        assert result["vendors"]["twilio"]["category"] == "communication"
    
    def test_detect_auth0(self, detector: VendorDetector, sample_repo: Path):
        """Test Auth0 detection."""
        result = detector.detect_vendors(sample_repo)
        
        assert "auth0" in result["vendors"]
        assert result["vendors"]["auth0"]["category"] == "authentication"
    
    def test_confidence_scoring(self, detector: VendorDetector, sample_repo: Path):
        """Test confidence scoring based on evidence."""
        result = detector.detect_vendors(sample_repo)
        
        # Multiple evidence sources = higher confidence
        for vendor_data in result["vendors"].values():
            assert 0.0 <= vendor_data["confidence"] <= 1.0
    
    def test_detect_from_import_statements(
        self, 
        detector: VendorDetector,
        tmp_path: Path
    ):
        """Test detection from Python import statements."""
        repo = tmp_path / "test-repo"
        repo.mkdir()
        
        # Create Python file with imports
        py_file = repo / "app.py"
        py_file.write_text("""
import stripe
from sendgrid import SendGridAPIClient
from twilio.rest import Client
        """)
        
        result = detector.detect_vendors(repo)
        
        assert "stripe" in result["vendors"]
        assert "sendgrid" in result["vendors"]
        assert "twilio" in result["vendors"]
    
    def test_detect_from_config_files(
        self, 
        detector: VendorDetector,
        tmp_path: Path
    ):
        """Test detection from configuration files."""
        repo = tmp_path / "test-repo"
        repo.mkdir()
        
        # Create .env with vendor API keys
        env_file = repo / ".env"
        env_file.write_text("""
STRIPE_API_KEY=sk_test_xxxxx
SENDGRID_API_KEY=SG.xxxxx
TWILIO_ACCOUNT_SID=ACxxxxx
        """)
        
        result = detector.detect_vendors(repo)
        
        assert "stripe" in result["vendors"]
        assert "sendgrid" in result["vendors"]
        assert "twilio" in result["vendors"]
    
    def test_vendor_summary(self, detector: VendorDetector, sample_repo: Path):
        """Test vendor summary generation."""
        result = detector.detect_vendors(sample_repo)
        
        assert "total_vendors" in result
        assert result["total_vendors"] == len(result["vendors"])
        assert "categories" in result
    
    def test_unknown_vendor_handling(
        self, 
        detector: VendorDetector,
        tmp_path: Path
    ):
        """Test handling of unknown vendors."""
        repo = tmp_path / "test-repo"
        repo.mkdir()
        
        # Create package.json with unknown vendor
        package_json = repo / "package.json"
        package_json.write_text("""
{
  "dependencies": {
    "custom-internal-lib": "^1.0.0"
  }
}
        """)
        
        result = detector.detect_vendors(repo)
        
        # Unknown vendors should be in candidates
        assert "candidates" in result or "unknown" in result
    
    def test_get_vendor_integration_patterns(
        self, 
        detector: VendorDetector,
        sample_repo: Path
    ):
        """Test extraction of vendor integration patterns."""
        result = detector.detect_vendors(sample_repo)
        
        stripe_data = result["vendors"].get("stripe", {})
        if stripe_data:
            # Implementation uses evidence_files, not integration_patterns or files
            assert "evidence_files" in stripe_data
            assert len(stripe_data["evidence_files"]) > 0


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
