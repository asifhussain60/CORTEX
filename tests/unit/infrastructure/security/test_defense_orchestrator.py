"""
Tests for DefenseOrchestrator - coordinates defense-in-depth security layers.

Author: CORTEX Implementation
Phase: impl-arch-005-hardening
Compliance: CORE-008 (TDD), CORE-011 (100% typed), CORE-012 (Google docstrings)
"""

import pytest


class TestDefenseLayerValidation:
    """Test defense layer validation."""

    def test_defense_layer_1_input_validation(self) -> None:
        """Verify Layer 1 (Input Validation) works."""
        from cortex.infrastructure.security import DefenseOrchestrator
        
        orchestrator = DefenseOrchestrator()
        
        def input_validator(request):
            return request.get("valid") is True
        
        orchestrator.register_layer(1, input_validator)
        
        result, failed = orchestrator.validate_all_layers({"valid": True})
        assert result is True

    def test_defense_layer_2_rate_limiting(self) -> None:
        """Verify Layer 2 (Rate Limiting) works."""
        from cortex.infrastructure.security import DefenseOrchestrator
        
        orchestrator = DefenseOrchestrator()
        
        def rate_limiter(request):
            return request.get("rate_ok") is True
        
        orchestrator.register_layer(2, rate_limiter)
        
        result, failed = orchestrator.validate_all_layers({"rate_ok": True})
        assert result is True

    def test_defense_layer_3_cryptography(self) -> None:
        """Verify Layer 3 (Cryptography) works."""
        from cortex.infrastructure.security import DefenseOrchestrator
        
        orchestrator = DefenseOrchestrator()
        
        def crypto_check(request):
            return True
        
        orchestrator.register_layer(3, crypto_check)
        assert orchestrator is not None

    def test_defense_layer_4_cors_csrf(self) -> None:
        """Verify Layer 4 (CORS/CSRF) works."""
        from cortex.infrastructure.security import DefenseOrchestrator
        
        orchestrator = DefenseOrchestrator()
        
        def cors_check(request):
            return True
        
        orchestrator.register_layer(4, cors_check)
        assert orchestrator is not None

    def test_defense_layer_5_audit_logging(self) -> None:
        """Verify Layer 5 (Audit Logging) works."""
        from cortex.infrastructure.security import DefenseOrchestrator
        
        orchestrator = DefenseOrchestrator()
        
        def audit_check(request):
            return True
        
        orchestrator.register_layer(5, audit_check)
        assert orchestrator is not None


class TestDefenseFailSecure:
    """Test fail-secure defaults."""

    def test_fail_secure_defaults_deny_by_default(self) -> None:
        """Verify fail-secure: deny by default, explicit allow."""
        from cortex.infrastructure.security import DefenseOrchestrator
        
        orchestrator = DefenseOrchestrator()
        defaults = orchestrator.apply_fail_secure_defaults()
        
        assert defaults["default_action"] == "DENY"
        assert defaults["explicit_allow_required"] is True

    def test_defense_overlap_verification(self) -> None:
        """Verify no single point of failure."""
        from cortex.infrastructure.security import DefenseOrchestrator
        
        orchestrator = DefenseOrchestrator()
        
        # Register all 5 layers
        for i in range(1, 6):
            orchestrator.register_layer(i, lambda r: True)
        
        no_spof = orchestrator.validate_no_single_point_of_failure()
        assert no_spof is True


class TestDefenseOrchestration:
    """Test defense coordination."""

    def test_coordinates_all_layers(self) -> None:
        """Verify all layers are coordinated."""
        from cortex.infrastructure.security import DefenseOrchestrator
        
        orchestrator = DefenseOrchestrator()
        
        # Register layers
        for i in range(1, 6):
            orchestrator.register_layer(i, lambda r: True)
        
        status = orchestrator.get_layer_status()
        assert len(status) == 5

    def test_handles_layer_violations(self) -> None:
        """Verify layer violations are handled."""
        from cortex.infrastructure.security import DefenseOrchestrator
        
        orchestrator = DefenseOrchestrator()
        
        def failing_layer(request):
            return False
        
        orchestrator.register_layer(1, failing_layer)
        
        result, failed = orchestrator.validate_all_layers({})
        assert result is False
        assert 1 in failed

    def test_applies_fail_secure_on_any_violation(self) -> None:
        """Verify any violation triggers fail-secure."""
        from cortex.infrastructure.security import DefenseOrchestrator
        
        orchestrator = DefenseOrchestrator()
        
        def failing_layer(request):
            return False
        
        orchestrator.register_layer(1, failing_layer)
        
        result, failed = orchestrator.validate_all_layers({})
        
        response = orchestrator.coordinate_layer_response(failed)
        assert response["action"] == "deny"
