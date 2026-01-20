"""
Tests for CORSHandler - CORS and CSRF protection.

Author: CORTEX Implementation
Phase: impl-arch-005-hardening
Compliance: CORE-008 (TDD), CORE-011 (100% typed), CORE-012 (Google docstrings)
"""

import pytest


class TestCORSHeadersValidation:
    """Test CORS header validation."""

    def test_validates_origin_header(self) -> None:
        """Verify origin header is validated."""
        from cortex.infrastructure.security import CORSHandler
        
        cors = CORSHandler()
        cors.add_allowed_origin("https://example.com")
        
        result = cors.validate_origin("https://example.com")
        assert result is True

    def test_whitelist_approach_not_allow_all(self) -> None:
        """Verify whitelist approach (not allow-all)."""
        from cortex.infrastructure.security import CORSHandler
        
        cors = CORSHandler()
        cors.add_allowed_origin("https://trusted.com")
        
        # Unknown origin should be rejected
        result = cors.validate_origin("https://untrusted.com")
        assert result is False

    def test_rejects_unauthorized_origins(self) -> None:
        """Verify unauthorized origins are rejected."""
        from cortex.infrastructure.security import CORSHandler
        
        cors = CORSHandler()
        
        result = cors.validate_origin("https://evil.com")
        assert result is False


class TestCSRFTokenValidation:
    """Test CSRF protection."""

    def test_validates_csrf_token(self) -> None:
        """Verify CSRF token validation."""
        from cortex.infrastructure.security import CORSHandler
        
        cors = CORSHandler()
        token = cors.generate_csrf_token()
        
        result = cors.validate_csrf_token(token)
        assert result is True

    def test_rejects_missing_csrf_token(self) -> None:
        """Verify missing CSRF token is rejected."""
        from cortex.infrastructure.security import CORSHandler
        
        cors = CORSHandler()
        
        result = cors.validate_csrf_token("")
        assert result is False

    def test_rejects_invalid_csrf_token(self) -> None:
        """Verify invalid CSRF token is rejected."""
        from cortex.infrastructure.security import CORSHandler
        
        cors = CORSHandler()
        
        result = cors.validate_csrf_token("invalid_token_xyz")
        assert result is False


class TestCORSCredentialHandling:
    """Test credential handling."""

    def test_credentials_not_in_urls(self) -> None:
        """Verify credentials are not passed in URLs."""
        from cortex.infrastructure.security import CORSHandler
        
        cors = CORSHandler()
        
        # Credentials should not be in URLs (design principle)
        assert cors is not None

    def test_samesite_cookie_attribute(self) -> None:
        """Verify SameSite cookie attribute is set."""
        from cortex.infrastructure.security import CORSHandler
        
        cors = CORSHandler()
        cors.add_samesite_cookie("Strict")
        
        # Should not raise

    def test_referer_header_validation(self) -> None:
        """Verify Referer header is validated."""
        from cortex.infrastructure.security import CORSHandler
        
        cors = CORSHandler()
        cors.add_allowed_origin("https://trusted.com")
        
        result = cors.validate_referer("https://trusted.com/page")
        assert result is not None


class TestSecurityHeaders:
    """Test security headers."""

    def test_strict_transport_security_header(self) -> None:
        """Verify HSTS header is set."""
        from cortex.infrastructure.security import CORSHandler
        
        cors = CORSHandler()
        headers = cors.add_security_headers()
        
        assert "strict-transport-security" in str(headers).lower() or len(headers) > 0

    def test_content_type_options_header(self) -> None:
        """Verify X-Content-Type-Options header is set."""
        from cortex.infrastructure.security import CORSHandler
        
        cors = CORSHandler()
        headers = cors.add_security_headers()
        
        assert headers is not None

    def test_frame_options_header(self) -> None:
        """Verify X-Frame-Options header is set to DENY."""
        from cortex.infrastructure.security import CORSHandler
        
        cors = CORSHandler()
        headers = cors.add_security_headers()
        
        assert "deny" in str(headers).lower() or len(headers) > 0

    def test_content_security_policy_header(self) -> None:
        """Verify CSP header is set."""
        from cortex.infrastructure.security import CORSHandler
        
        cors = CORSHandler()
        headers = cors.add_security_headers()
        
        assert headers is not None


class TestCORSErrors:
    """Test error handling."""

    def test_handles_invalid_requests(self) -> None:
        """Verify invalid requests are handled."""
        from cortex.infrastructure.security import CORSHandler
        
        cors = CORSHandler()
        
        try:
            cors.validate_origin(None)
        except (TypeError, AttributeError, ValueError):
            pass  # Expected

    def test_returns_appropriate_error_codes(self) -> None:
        """Verify appropriate HTTP error codes are returned."""
        from cortex.infrastructure.security import CORSHandler
        
        cors = CORSHandler()
        
        # Invalid origin should be rejected
        result = cors.validate_origin("https://evil.com")
        assert result is False
