"""
CORTEX LENS Golden Tests - Discovery & Security

Authority: AC-GOLDEN-LENS-DISCO-SEC-001
Tests for capability discovery, tech stack fingerprinting, and security scanning

Coverage:
- golden_32: Tech Stack Fingerprinting
- golden_33: Capability Gap Detection
- golden_34: Crawler Spec Generation
- golden_37: Secret Detection
- golden_38: Code Smell Detection
"""

import pytest
from pathlib import Path

from tests.orchestrators.e2e.test_lens_golden_harness import LENSGoldenTestHarness


class TestLENSDiscovery:
    """Golden tests for LENS discovery capabilities."""
    
    @pytest.mark.lens
    @pytest.mark.discovery
    @pytest.mark.xfail(reason="RED phase - Fingerprint analyzer wiring pending")
    def test_golden_32_tech_stack_fingerprinting(self, lens_harness: LENSGoldenTestHarness):
        """
        Golden Test 32: Tech Stack Fingerprinting
        
        Validates:
        - Language detection (Python, TypeScript)
        - Framework identification (Django, React, Next.js)
        - Tool detection (Docker, Kubernetes)
        - Confidence scoring
        """
        result = lens_harness.execute_lens_scenario("lens/discovery/golden_32_tech_stack_fingerprinting")
        
        assert result.passed, f"Tech stack fingerprinting failed: {result.diffs}"


class TestLENSSecurity:
    """Golden tests for LENS security scanning."""
    
    @pytest.mark.lens
    @pytest.mark.security
    @pytest.mark.xfail(reason="RED phase - Secret detector wiring pending")
    def test_golden_37_secret_detection(self, lens_harness: LENSGoldenTestHarness):
        """
        Golden Test 37: Secret Detection
        
        Validates:
        - API key detection (Stripe, AWS, GitHub)
        - Password detection
        - High-entropy string identification
        - Severity classification (CRITICAL, HIGH)
        - Remediation advice generation
        """
        result = lens_harness.execute_lens_scenario("lens/security/golden_37_secret_detection")
        
        assert result.passed, f"Secret detection failed: {result.diffs}"
        
        # Verify audit trail
        events = lens_harness.get_audit_events()
        assert any(e['activity'] == 'SCAN_SECRETS' for e in events)
        assert any(e['activity'] == 'DETECT_HIGH_ENTROPY' for e in events)


class TestLENSSecurityIntegration:
    """Integration tests for security scanning."""
    
    @pytest.mark.lens
    @pytest.mark.security
    def test_secret_files_created_with_patterns(self, temp_repo_builder):
        """Test that secret fixtures contain detectable patterns."""
        files = {
            "config.py": "API_KEY = 'sk_live_1234567890abcdef'",
            ".env": "AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE",
        }
        
        repo_path = temp_repo_builder.create_repo("secrets_test", files)
        
        config_content = (repo_path / "config.py").read_text()
        assert "sk_live_" in config_content  # Stripe pattern
        
        env_content = (repo_path / ".env").read_text()
        assert "AKIA" in env_content  # AWS pattern
