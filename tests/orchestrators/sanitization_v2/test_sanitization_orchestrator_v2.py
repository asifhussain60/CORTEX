"""
Unit Tests for Sanitization Orchestrator v2

Tests all 5 phases with comprehensive coverage:
- Discovery: Pattern detection across file types
- Analysis: Risk scoring and sensitivity classification
- Transformation: Sanitization with backup
- Validation: Clean verification
- Finalization: Report generation

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

from src.orchestrators.sanitization_v2.sanitization_orchestrator_v2 import (
    SanitizationOrchestratorV2,
    SanitizationPhase,
    DiscoveryResult,
    AnalysisResult,
    TransformResult,
    ValidationResult,
    FinalResult,
)
from src.orchestrators.sanitization_v2.sanitization_engine import (
    SanitizationEngine,
    PatternRegistry,
    PatternCategory,
    ReplacementStrategy,
)


@pytest.fixture
def temp_workspace(tmp_path):
    """Create temporary workspace with test files."""
    workspace = tmp_path / "test_workspace"
    workspace.mkdir()
    
    # Create test files with sensitive data
    (workspace / "test1.py").write_text("""
# Test file with PII
email = "user@example.com"
phone = "555-123-4567"
password = "MySecret123"
""")
    
    (workspace / "test2.md").write_text("""
# Documentation
API Key: sk-1234567890abcdef1234567890abcdef
Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9
""")
    
    (workspace / "test3.json").write_text(json.dumps({
        "user": "john@company.com",
        "ssn": "123-45-6789",
        "credit_card": "4532-1234-5678-9010",
    }))
    
    return workspace


@pytest.fixture
def pattern_registry():
    """Create pattern registry instance."""
    return PatternRegistry()


@pytest.fixture
def sanitization_engine():
    """Create sanitization engine instance."""
    return SanitizationEngine()


class TestPatternRegistry:
    """Test pattern registry functionality."""
    
    def test_registry_initialization(self, pattern_registry):
        """Test registry loads all pattern categories."""
        assert PatternCategory.CRITICAL_SECRETS in pattern_registry.patterns
        assert PatternCategory.PII in pattern_registry.patterns
        assert PatternCategory.PHI in pattern_registry.patterns
        assert PatternCategory.PCI in pattern_registry.patterns
        assert PatternCategory.PATHS in pattern_registry.patterns
        assert PatternCategory.COMPANY in pattern_registry.patterns
        assert PatternCategory.HASHES in pattern_registry.patterns
    
    def test_get_all_patterns(self, pattern_registry):
        """Test pattern retrieval with exclusions."""
        patterns = pattern_registry.get_all_patterns()
        
        # Should have patterns
        assert len(patterns) > 0
        
        # Should be sorted by priority (descending)
        priorities = [p.priority for p in patterns]
        assert priorities == sorted(priorities, reverse=True)
        
        # Should exclude hashes by default
        pattern_names = [p.name for p in patterns]
        assert "hash" not in pattern_names
    
    def test_add_custom_pattern(self, pattern_registry):
        """Test adding custom patterns."""
        from src.orchestrators.sanitization_v2.sanitization_engine import PatternDefinition
        
        custom = PatternDefinition(
            name="custom_id",
            regex=r'ID-\d{6}',
            category=PatternCategory.PII,
            confidence=0.9,
            strategy=ReplacementStrategy.PLACEHOLDER,
            priority=85,
        )
        
        pattern_registry.add_custom_pattern(custom)
        
        # Verify added
        pii_patterns = pattern_registry.patterns[PatternCategory.PII]
        assert any(p.name == "custom_id" for p in pii_patterns)


class TestSanitizationEngine:
    """Test sanitization engine functionality."""
    
    def test_detect_email(self, sanitization_engine):
        """Test email pattern detection."""
        text = "Contact: john.doe@example.com"
        matches = sanitization_engine.detect_all(text)
        
        # Should detect email (and may detect domains as well)
        email_matches = [m for m in matches if m.pattern_name == "email"]
        assert len(email_matches) == 1
        assert email_matches[0].matched_text == "john.doe@example.com"
        assert email_matches[0].confidence >= 0.95
    
    def test_detect_password(self, sanitization_engine):
        """Test password pattern detection."""
        text = 'password: "MySecret123"'
        matches = sanitization_engine.detect_all(text)
        
        assert len(matches) == 1
        assert matches[0].pattern_name == "password"
        assert matches[0].category == PatternCategory.CRITICAL_SECRETS
    
    def test_detect_api_key(self, sanitization_engine):
        """Test API key pattern detection."""
        text = "api_key = sk-1234567890abcdef1234567890abcdef"
        matches = sanitization_engine.detect_all(text)
        
        assert len(matches) == 1
        assert matches[0].pattern_name == "api_key"
        assert matches[0].confidence >= 0.95
    
    def test_detect_ssn(self, sanitization_engine):
        """Test SSN pattern detection."""
        text = "SSN: 123-45-6789"
        matches = sanitization_engine.detect_all(text)
        
        assert len(matches) == 1
        assert matches[0].pattern_name == "ssn"
        assert matches[0].confidence >= 0.99
    
    def test_detect_credit_card(self, sanitization_engine):
        """Test credit card pattern detection."""
        text = "Card: 4532-1234-5678-9010"
        matches = sanitization_engine.detect_all(text)
        
        assert len(matches) == 1
        assert matches[0].pattern_name == "credit_card"
        assert matches[0].category == PatternCategory.PCI
    
    def test_sanitize_text(self, sanitization_engine):
        """Test text sanitization."""
        text = "Email: user@example.com, Password: secret123"
        sanitized, matches = sanitization_engine.sanitize_text(text)
        
        # Should find at least 2 matches (email and password, may find domain too)
        assert len(matches) >= 2
        
        # Check email match
        email_matches = [m for m in matches if m.pattern_name == "email"]
        assert len(email_matches) == 1
        
        # Check password match
        password_matches = [m for m in matches if m.pattern_name == "password"]
        assert len(password_matches) == 1
        
        # Should replace sensitive data
        assert "secret123" not in sanitized or "[REDACTED" in sanitized
    
    def test_validate_sanitization_clean(self, sanitization_engine):
        """Test validation with clean text."""
        text = "This is clean text with no sensitive data."
        is_clean, matches = sanitization_engine.validate_sanitization(text)
        
        assert is_clean
        assert len(matches) == 0
    
    def test_validate_sanitization_dirty(self, sanitization_engine):
        """Test validation with sensitive data."""
        text = "Password: MySecret123"
        is_clean, matches = sanitization_engine.validate_sanitization(text, min_confidence=0.8)
        
        assert not is_clean
        assert len(matches) > 0
        assert matches[0].confidence >= 0.8


class TestSanitizationOrchestratorV2:
    """Test orchestrator integration."""
    
    def test_initialization(self, temp_workspace):
        """Test orchestrator initialization."""
        orchestrator = SanitizationOrchestratorV2(
            workspace_root=temp_workspace
        )
        
        assert orchestrator.workspace_root == temp_workspace
        assert orchestrator.engine is not None
        assert isinstance(orchestrator.engine, SanitizationEngine)
    
    def test_discovery_phase(self, temp_workspace):
        """Test discovery phase."""
        orchestrator = SanitizationOrchestratorV2(
            workspace_root=temp_workspace
        )
        
        discovery = orchestrator.discover_sensitive_content()
        
        # Should scan all files
        assert discovery.files_scanned >= 3
        
        # Should find matches
        assert discovery.total_matches > 0
        assert discovery.files_with_matches > 0
        
        # Should have match breakdown
        assert len(discovery.matches_by_category) > 0
    
    def test_analysis_phase(self, temp_workspace):
        """Test analysis phase."""
        orchestrator = SanitizationOrchestratorV2(
            workspace_root=temp_workspace
        )
        
        discovery = orchestrator.discover_sensitive_content()
        analysis = orchestrator.analyze_sensitivity_levels(discovery)
        
        # Should have risk score
        assert 0 <= analysis.risk_score <= 100
        
        # Should have recommendation
        assert len(analysis.recommended_action) > 0
        
        # Should detect categories
        assert analysis.pii_found > 0 or analysis.critical_secrets_found > 0
    
    def test_full_pipeline_dry_run(self, temp_workspace):
        """Test complete pipeline in dry-run mode."""
        orchestrator = SanitizationOrchestratorV2(
            workspace_root=temp_workspace
        )
        
        result = orchestrator.execute(user_input={"dry_run": True})
        
        # Should complete successfully
        assert isinstance(result, FinalResult)
        
        # Should have all phase results
        assert result.discovery is not None
        assert result.analysis is not None
        assert result.transformation is not None
        assert result.validation is not None
        
        # Should track duration
        assert result.total_duration_ms > 0


# Integration tests
class TestIntegration:
    """Integration tests for end-to-end workflows."""
    
    def test_empty_workspace(self, tmp_path):
        """Test handling of empty workspace."""
        workspace = tmp_path / "empty"
        workspace.mkdir()
        
        orchestrator = SanitizationOrchestratorV2(workspace_root=workspace)
        result = orchestrator.execute()
        
        # Should handle gracefully
        assert result.discovery.files_scanned == 0
        assert result.discovery.total_matches == 0
        assert result.success  # Clean by definition
    
    def test_binary_file_handling(self, tmp_path):
        """Test handling of binary files."""
        workspace = tmp_path / "binary_test"
        workspace.mkdir()
        
        # Create binary file
        (workspace / "test.bin").write_bytes(b'\x00\x01\x02\x03')
        
        orchestrator = SanitizationOrchestratorV2(workspace_root=workspace)
        result = orchestrator.execute()
        
        # Should skip binary files
        assert result.success


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
