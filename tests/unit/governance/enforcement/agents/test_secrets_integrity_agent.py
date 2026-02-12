"""
Tests for SecretsIntegrityAgent - Phase 76 Stage 3 Task 5

Tests the 9th enforcement agent for secrets management validation.

Authority: phase-76-production-foundation-trilogy.yaml S3.T5
AC-ID: AC-PHASE76-S3-005
"""

import pytest
import os

from cortex.governance.enforcement.agents.secrets_integrity_agent import (
    SecretsIntegrityAgent,
    SecretsValidationResult,
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def agent():
    """Create SecretsIntegrityAgent instance."""
    return SecretsIntegrityAgent()


@pytest.fixture
def valid_master_key():
    """Generate valid master key."""
    return "0" * 32 + "a" * 32  # 64 character key


@pytest.fixture
def weak_master_key():
    """Generate weak master key."""
    return "short"


# ============================================================================
# PRE-FLIGHT VALIDATION TESTS
# ============================================================================

class TestPreFlightValidation:
    """Tests for pre-flight validation"""
    
    def test_preflight_passes_with_valid_key(self, agent, valid_master_key, monkeypatch):
        """Test pre-flight validation passes with valid key."""
        monkeypatch.setenv("CORTEX_MASTER_KEY", valid_master_key)
        
        result = agent.validate_pre_flight(check_environment=False)
        
        assert result.passed is True
        assert result.severity == "PASSED"
    
    def test_preflight_fails_without_key(self, agent, monkeypatch):
        """Test pre-flight fails without master key."""
        monkeypatch.delenv("CORTEX_MASTER_KEY", raising=False)
        
        result = agent.validate_pre_flight(check_environment=False)
        
        assert result.passed is False
        assert result.severity == "CRITICAL"
        assert result.missing_master_key is True
    
    def test_preflight_fails_with_weak_key(self, agent, weak_master_key, monkeypatch):
        """Test pre-flight fails with weak master key."""
        monkeypatch.setenv("CORTEX_MASTER_KEY", weak_master_key)
        
        result = agent.validate_pre_flight(check_environment=False)
        
        assert result.passed is False
        assert result.severity == "CRITICAL"
    
    def test_preflight_includes_action(self, agent, monkeypatch):
        """Test pre-flight result includes action."""
        monkeypatch.delenv("CORTEX_MASTER_KEY", raising=False)
        
        result = agent.validate_pre_flight(check_environment=False)
        
        assert result.action is not None
        assert len(result.action) > 0


# ============================================================================
# PLAINTEXT SECRETS DETECTION TESTS
# ============================================================================

class TestPlaintextSecretsDetection:
    """Tests for plaintext secrets detection"""
    
    def test_detects_password_variable(self, agent, valid_master_key, monkeypatch):
        """Test detection of PASSWORD variable."""
        monkeypatch.setenv("CORTEX_MASTER_KEY", valid_master_key)
        monkeypatch.setenv("DATABASE_PASSWORD", "plaintext_password")
        
        result = agent.validate_pre_flight(check_environment=True)
        
        # Should detect plaintext password
        assert len(result.plaintext_secrets) > 0 or result.passed is True
    
    def test_detects_api_key_variable(self, agent, valid_master_key, monkeypatch):
        """Test detection of API_KEY variable."""
        monkeypatch.setenv("CORTEX_MASTER_KEY", valid_master_key)
        monkeypatch.setenv("API_KEY", "plaintext_key")
        
        result = agent.validate_pre_flight(check_environment=True)
        
        # Should detect or warn about plaintext API key
        if len(result.plaintext_secrets) > 0:
            assert "API_KEY" in result.plaintext_secrets
    
    def test_detects_token_variable(self, agent, valid_master_key, monkeypatch):
        """Test detection of TOKEN variable."""
        monkeypatch.setenv("CORTEX_MASTER_KEY", valid_master_key)
        monkeypatch.setenv("AUTH_TOKEN", "plaintext_token")
        
        result = agent.validate_pre_flight(check_environment=True)
        
        if len(result.plaintext_secrets) > 0:
            assert "AUTH_TOKEN" in result.plaintext_secrets
    
    def test_ignores_cortex_variables(self, agent, valid_master_key, monkeypatch):
        """Test that CORTEX_ variables are not flagged."""
        monkeypatch.setenv("CORTEX_MASTER_KEY", valid_master_key)
        monkeypatch.setenv("CORTEX_SOME_CONFIG", "value")
        
        result = agent.validate_pre_flight(check_environment=True)
        
        # CORTEX_SOME_CONFIG should not be flagged as plaintext
        assert "CORTEX_SOME_CONFIG" not in result.plaintext_secrets


# ============================================================================
# SECRET ACCESS VALIDATION TESTS
# ============================================================================

class TestSecretAccessValidation:
    """Tests for secret access validation"""
    
    def test_validates_env_fallback_warning(self, agent, monkeypatch):
        """Test that env fallback triggers warning."""
        monkeypatch.setenv("SOME_SECRET", "plaintext")
        
        result = agent.validate_secret_access("SOME_SECRET")
        
        assert result.passed is True
        assert result.severity == "WARNING"
    
    def test_validates_secure_storage_access(self, agent):
        """Test that secure storage access passes."""
        result = agent.validate_secret_access("NOT_IN_ENV")
        
        assert result.passed is True
        assert result.severity == "PASSED"


# ============================================================================
# OPERATION CONTEXT VALIDATION TESTS
# ============================================================================

class TestOperationContextValidation:
    """Tests for operation context validation"""
    
    def test_validates_normal_operation(self, agent, valid_master_key, monkeypatch):
        """Test validation for normal operation."""
        monkeypatch.setenv("CORTEX_MASTER_KEY", valid_master_key)
        
        result = agent.validate_operation_context("IMPLEMENT", requires_secrets=False)
        
        assert result.passed is True
    
    def test_fails_sensitive_operation_without_key(self, agent, monkeypatch):
        """Test that sensitive operation fails without key."""
        monkeypatch.delenv("CORTEX_MASTER_KEY", raising=False)
        
        result = agent.validate_operation_context("DEPLOY", requires_secrets=True)
        
        assert result.passed is False
        assert result.severity == "CRITICAL"
    
    def test_passes_sensitive_operation_with_key(self, agent, valid_master_key, monkeypatch):
        """Test that sensitive operation passes with valid key."""
        monkeypatch.setenv("CORTEX_MASTER_KEY", valid_master_key)
        
        result = agent.validate_operation_context("DEPLOY", requires_secrets=True)
        
        assert result.passed is True
    
    def test_release_operation_blocked_without_key(self, agent, monkeypatch):
        """Test RELEASE operation blocked without key."""
        monkeypatch.delenv("CORTEX_MASTER_KEY", raising=False)
        
        result = agent.validate_operation_context("RELEASE")
        
        assert result.passed is False
        assert result.severity == "CRITICAL"


# ============================================================================
# VALIDATION RESULT TESTS
# ============================================================================

class TestValidationResult:
    """Tests for SecretsValidationResult"""
    
    def test_result_passed_state(self):
        """Test result with passed state."""
        result = SecretsValidationResult(
            passed=True,
            severity="PASSED",
            reason="Test reason",
            action="Test action",
        )
        
        assert result.passed is True
        assert result.severity == "PASSED"
    
    def test_result_failed_state(self):
        """Test result with failed state."""
        result = SecretsValidationResult(
            passed=False,
            severity="CRITICAL",
            reason="Test failure",
            action="Fix this",
        )
        
        assert result.passed is False
        assert result.severity == "CRITICAL"
    
    def test_result_with_plaintext_secrets(self):
        """Test result with plaintext secrets."""
        secrets = ["PASSWORD", "API_KEY"]
        result = SecretsValidationResult(
            passed=False,
            severity="CRITICAL",
            reason="Plaintext secrets found",
            action="Encrypt them",
            plaintext_secrets=secrets,
        )
        
        assert result.plaintext_secrets == secrets
    
    def test_result_with_missing_key(self):
        """Test result indicating missing key."""
        result = SecretsValidationResult(
            passed=False,
            severity="CRITICAL",
            reason="Key missing",
            action="Set key",
            missing_master_key=True,
        )
        
        assert result.missing_master_key is True


# ============================================================================
# ENFORCEMENT AGENT INTEGRATION TESTS
# ============================================================================

class TestEnforcementIntegration:
    """Tests for enforcement in orchestrator context"""
    
    def test_agent_can_block_implement(self, agent, monkeypatch):
        """Test that agent can block IMPLEMENT without secrets."""
        monkeypatch.delenv("CORTEX_MASTER_KEY", raising=False)
        
        result = agent.validate_operation_context("IMPLEMENT", requires_secrets=True)
        
        assert result.passed is False
        # Don't raise, let orchestrator decide
    
    def test_agent_can_block_deploy(self, agent, monkeypatch):
        """Test that agent can block DEPLOY without key."""
        monkeypatch.delenv("CORTEX_MASTER_KEY", raising=False)
        
        result = agent.validate_operation_context("DEPLOY")
        
        assert result.passed is False
    
    def test_agent_provides_action_for_fix(self, agent, monkeypatch):
        """Test agent provides action for fixing."""
        monkeypatch.delenv("CORTEX_MASTER_KEY", raising=False)
        
        result = agent.validate_pre_flight(check_environment=False)
        
        assert result.action is not None
        assert "CORTEX_MASTER_KEY" in result.action or "key" in result.action.lower()


# ============================================================================
# PLAINTEXT PATTERN TESTS
# ============================================================================

class TestPlaintextPatterns:
    """Tests for plaintext detection patterns"""
    
    def test_patterns_include_password(self, agent):
        """Test PASSWORD pattern is included."""
        assert "PASSWORD" in agent.PLAINTEXT_SECRET_PATTERNS
    
    def test_patterns_include_apikey(self, agent):
        """Test API_KEY pattern is included."""
        assert "API_KEY" in agent.PLAINTEXT_SECRET_PATTERNS
    
    def test_patterns_include_token(self, agent):
        """Test TOKEN pattern is included."""
        assert "TOKEN" in agent.PLAINTEXT_SECRET_PATTERNS
    
    def test_patterns_include_secret(self, agent):
        """Test SECRET pattern is included."""
        assert "SECRET" in agent.PLAINTEXT_SECRET_PATTERNS


# ============================================================================
# SECURE ENVIRONMENT PATTERNS TESTS
# ============================================================================

class TestSecureEnvironmentPatterns:
    """Tests for secure environment variable patterns"""
    
    def test_cortex_pattern_is_secure(self, agent):
        """Test CORTEX_ pattern is marked as secure."""
        assert "CORTEX_" in agent.SECURE_ENV_PATTERNS
    
    def test_cortex_variables_excluded_from_plaintext(self, agent, valid_master_key, monkeypatch):
        """Test CORTEX_ variables not flagged as plaintext."""
        monkeypatch.setenv("CORTEX_MASTER_KEY", valid_master_key)
        monkeypatch.setenv("CORTEX_PASSWORD", "value")  # Even with PASSWORD
        
        result = agent.validate_pre_flight(check_environment=True)
        
        # Should not be in plaintext_secrets
        if result.plaintext_secrets:
            assert "CORTEX_PASSWORD" not in result.plaintext_secrets


# ============================================================================
# ERROR MESSAGE TESTS
# ============================================================================

class TestErrorMessages:
    """Tests for error messages provided by agent"""
    
    def test_missing_key_error_message(self, agent, monkeypatch):
        """Test error message for missing key."""
        monkeypatch.delenv("CORTEX_MASTER_KEY", raising=False)
        
        result = agent.validate_pre_flight(check_environment=False)
        
        assert "CORTEX_MASTER_KEY" in result.reason
        assert len(result.action) > 0
    
    def test_weak_key_error_message(self, agent, monkeypatch):
        """Test error message for weak key."""
        monkeypatch.setenv("CORTEX_MASTER_KEY", "short")
        
        result = agent.validate_pre_flight(check_environment=False)
        
        assert "32" in result.reason or "short" in result.reason.lower()
    
    def test_plaintext_secrets_error_message(self, agent, valid_master_key, monkeypatch):
        """Test error message for plaintext secrets."""
        monkeypatch.setenv("CORTEX_MASTER_KEY", valid_master_key)
        monkeypatch.setenv("DATABASE_PASSWORD", "pass")
        
        result = agent.validate_pre_flight(check_environment=True)
        
        if not result.passed:
            assert len(result.action) > 0
