"""Phase S3: Vulnerabilities Tab (⚠️) - TDD Test Suite
Tests for CVE tracking, severity counts, and security findings
"""

import pytest
from pydantic import ValidationError
from cortex.orchestrators.onboarding.dashboard_schema_models import VulnerabilitiesTab


@pytest.fixture
def valid_vulnerabilities():
    """Valid vulnerabilities fixture"""
    return {
        "critical": 2,
        "high": 5,
        "medium": 12,
        "low": 8,
        "owasp_findings": [],
        "secrets_scan": None,
        "cves": []
    }


class TestCriticalVulnerabilities:
    """Test critical severity vulnerabilities"""
    
    def test_zero_critical(self):
        """Test zero critical vulnerabilities"""
        data = {
            "critical": 0,
            "high": 5,
            "medium": 12,
            "low": 8
        }
        vuln = VulnerabilitiesTab(**data)
        assert vuln.critical == 0
    
    def test_few_critical(self, valid_vulnerabilities):
        """Test few critical vulnerabilities"""
        vuln = VulnerabilitiesTab(**valid_vulnerabilities)
        assert vuln.critical == 2
    
    def test_many_critical(self):
        """Test many critical vulnerabilities (50+)"""
        data = {
            "critical": 50,
            "high": 100,
            "medium": 200,
            "low": 300
        }
        vuln = VulnerabilitiesTab(**data)
        assert vuln.critical == 50
    
    def test_negative_critical(self):
        """Test negative critical count (invalid)"""
        data = {
            "critical": -1,
            "high": 5,
            "medium": 12,
            "low": 8
        }
        with pytest.raises(ValidationError):
            VulnerabilitiesTab(**data)


class TestHighVulnerabilities:
    """Test high severity vulnerabilities"""
    
    def test_high_vulnerability_count(self, valid_vulnerabilities):
        """Test high severity count"""
        vuln = VulnerabilitiesTab(**valid_vulnerabilities)
        assert vuln.high == 5


class TestMediumVulnerabilities:
    """Test medium severity vulnerabilities"""
    
    def test_medium_vulnerability_count(self, valid_vulnerabilities):
        """Test medium severity count"""
        vuln = VulnerabilitiesTab(**valid_vulnerabilities)
        assert vuln.medium == 12


class TestLowVulnerabilities:
    """Test low severity vulnerabilities"""
    
    def test_low_vulnerability_count(self, valid_vulnerabilities):
        """Test low severity count"""
        vuln = VulnerabilitiesTab(**valid_vulnerabilities)
        assert vuln.low == 8


class TestCVETracking:
    """Test CVE collection and tracking"""
    
    def test_empty_cves(self, valid_vulnerabilities):
        """Test with no CVEs"""
        vuln = VulnerabilitiesTab(**valid_vulnerabilities)
        assert len(vuln.cves) == 0


class TestOWASPFindings:
    """Test OWASP security findings"""
    
    def test_no_owasp_findings(self, valid_vulnerabilities):
        """Test with no OWASP findings"""
        vuln = VulnerabilitiesTab(**valid_vulnerabilities)
        assert len(vuln.owasp_findings) == 0
    
    def test_owasp_findings_list(self, valid_vulnerabilities):
        """Test OWASP findings as list"""
        vuln = VulnerabilitiesTab(**valid_vulnerabilities)
        assert isinstance(vuln.owasp_findings, list)


class TestSecretsScan:
    """Test secrets scanning"""
    
    def test_no_secrets_scan(self, valid_vulnerabilities):
        """Test with no secrets scan data"""
        vuln = VulnerabilitiesTab(**valid_vulnerabilities)
        assert vuln.secrets_scan is None
    
    def test_optional_secrets_scan(self, valid_vulnerabilities):
        """Test secrets_scan is optional field"""
        vuln = VulnerabilitiesTab(**valid_vulnerabilities)
        # Should not raise error when None
        assert vuln.secrets_scan is None


class TestSeverityDistribution:
    """Test vulnerability severity distribution"""
    
    def test_severity_sum(self, valid_vulnerabilities):
        """Test severity count sum is positive"""
        vuln = VulnerabilitiesTab(**valid_vulnerabilities)
        total = vuln.critical + vuln.high + vuln.medium + vuln.low
        assert total > 0
    
    def test_all_critical(self):
        """Test all vulnerabilities critical"""
        data = {
            "critical": 50,
            "high": 0,
            "medium": 0,
            "low": 0
        }
        vuln = VulnerabilitiesTab(**data)
        assert vuln.critical == 50
        assert vuln.high == 0
    
    def test_pyramid_distribution(self):
        """Test typical pyramid distribution"""
        data = {
            "critical": 2,
            "high": 8,
            "medium": 25,
            "low": 65
        }
        vuln = VulnerabilitiesTab(**data)
        # Low should be more than high
        assert vuln.low > vuln.high
        assert vuln.high > vuln.critical


class TestVulnerabilityEdgeCases:
    """Test vulnerability edge cases"""
    
    def test_minimal_vulnerabilities(self):
        """Test minimal vulnerability spec"""
        data = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0
        }
        vuln = VulnerabilitiesTab(**data)
        assert vuln.critical == 0
    
    def test_high_vulnerability_count(self):
        """Test high vulnerability count"""
        data = {
            "critical": 500,
            "high": 1000,
            "medium": 5000,
            "low": 10000
        }
        vuln = VulnerabilitiesTab(**data)
        assert vuln.critical == 500
        assert vuln.low == 10000
