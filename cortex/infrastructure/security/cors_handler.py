"""
CORSHandler - CORS and CSRF protection.

Implements CORS validation with whitelist approach, CSRF token validation,
and comprehensive security headers for cross-origin attack prevention.

Author: CORTEX Implementation
Phase: impl-arch-005-hardening (HARD-PROD-001-05)
Compliance: CORE-011 (100% typed), CORE-012 (Google docstrings), CORE-013 (no bare except)
"""

import secrets
import time
from typing import Any, Dict, List, Optional


class CORSHandler:
    """Handles CORS and CSRF protection.

    Implements:
    - CORS origin validation (whitelist, not allow-all)
    - CSRF token generation and validation
    - Referer header validation
    - SameSite cookie attribute enforcement
    - Security header injection (HSTS, CSP, etc.)

    Attributes:
        allowed_origins: Whitelist of allowed origins
        csrf_tokens: Dictionary of {token: {created_at, used}}
        token_ttl: CSRF token time-to-live in seconds
    """

    def __init__(self, allowed_origins: Optional[List[str]] = None) -> None:
        """Initialize CORSHandler.

        Args:
            allowed_origins: List of allowed origins (whitelist)
        """
        self.allowed_origins = allowed_origins or []
        self.csrf_tokens: Dict[str, Dict[str, Any]] = {}
        self.token_ttl = 3600  # 1 hour
        self.hsts_max_age = 31536000  # 1 year

    def add_allowed_origin(self, origin: str) -> None:
        """Add origin to whitelist.

        Args:
            origin: Origin URL to allow (e.g., "https://example.com")
        """
        if origin not in self.allowed_origins:
            self.allowed_origins.append(origin)

    def validate_origin(self, origin: str, whitelist: Optional[List[str]] = None) -> bool:
        """Validate request origin against whitelist.

        Args:
            origin: Origin header value from request
            whitelist: Optional whitelist override

        Returns:
            True if origin is allowed, False otherwise
        """
        allowed = whitelist or self.allowed_origins

        if not allowed:
            # No whitelist configured, deny all
            return False

        return origin in allowed

    def generate_csrf_token(self) -> str:
        """Generate a new CSRF token.

        Returns:
            Hex-encoded CSRF token
        """
        token = secrets.token_urlsafe(32)
        self.csrf_tokens[token] = {
            "created_at": time.time(),
            "used": False
        }
        return token

    def validate_csrf_token(self, token: str) -> bool:
        """Validate CSRF token.

        Args:
            token: Token to validate

        Returns:
            True if valid and not expired, False otherwise
        """
        if token not in self.csrf_tokens:
            return False

        token_data = self.csrf_tokens[token]

        # Check expiration
        if time.time() - token_data["created_at"] > self.token_ttl:
            del self.csrf_tokens[token]
            return False

        # Check not already used
        if token_data["used"]:
            return False

        # Mark as used
        token_data["used"] = True
        return True

    def validate_referer(self, referer: str, expected_host: str) -> bool:
        """Validate Referer header.

        Args:
            referer: Referer header value
            expected_host: Expected host

        Returns:
            True if Referer matches expected host
        """
        if not referer:
            return False

        # Extract host from referer URL
        if referer.startswith("http://"):
            referer_host = referer[7:].split("/")[0]
        elif referer.startswith("https://"):
            referer_host = referer[8:].split("/")[0]
        else:
            return False

        return referer_host == expected_host

    def add_security_headers(self, response_headers: Dict[str, str]) -> Dict[str, str]:
        """Add comprehensive security headers to response.

        Adds:
        - Strict-Transport-Security (HSTS)
        - X-Content-Type-Options: nosniff
        - X-Frame-Options: DENY
        - Content-Security-Policy
        - X-XSS-Protection

        Args:
            response_headers: Headers dict to update

        Returns:
            Updated headers dict with security headers
        """
        response_headers["Strict-Transport-Security"] = (
            f"max-age={self.hsts_max_age}; includeSubDomains; preload"
        )
        response_headers["X-Content-Type-Options"] = "nosniff"
        response_headers["X-Frame-Options"] = "DENY"
        response_headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline';"
        )
        response_headers["X-XSS-Protection"] = "1; mode=block"
        response_headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        return response_headers

    def handle_preflight(
        self,
        origin: str,
        request_method: str,
        request_headers: List[str]
    ) -> Dict[str, str]:
        """Handle CORS preflight request.

        Args:
            origin: Request origin
            request_method: Requested HTTP method
            request_headers: Requested headers

        Returns:
            CORS preflight response headers
        """
        headers: Dict[str, str] = {}

        if not self.validate_origin(origin):
            return headers

        headers["Access-Control-Allow-Origin"] = origin
        headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        headers["Access-Control-Allow-Headers"] = ", ".join(request_headers)
        headers["Access-Control-Max-Age"] = "86400"
        headers["Access-Control-Allow-Credentials"] = "true"

        return headers

    def add_samesite_cookie(
        self,
        cookie_value: str,
        samesite: str = "Strict"
    ) -> str:
        """Add SameSite attribute to cookie.

        Args:
            cookie_value: Cookie value
            samesite: SameSite value (Strict, Lax, None)

        Returns:
            Cookie with SameSite attribute
        """
        valid_values = ["Strict", "Lax", "None"]
        if samesite not in valid_values:
            raise ValueError(f"SameSite must be one of {valid_values}")

        return f"{cookie_value}; SameSite={samesite}; Secure"

    def validate_request(self, request_dict: Dict[str, Any]) -> bool:
        """Validate complete request for CORS/CSRF.

        Args:
            request_dict: Request data dict with headers, origin, etc.

        Returns:
            True if request is valid, False otherwise
        """
        # Check origin
        origin = request_dict.get("origin")
        if origin and not self.validate_origin(origin):
            return False

        # Check CSRF token for state-changing operations
        method = request_dict.get("method", "GET")
        if method in ["POST", "PUT", "DELETE", "PATCH"]:
            csrf_token = request_dict.get("csrf_token")
            if csrf_token is None:
                return False

            if not self.validate_csrf_token(csrf_token):
                return False

        return True

    def cleanup_expired_tokens(self) -> int:
        """Clean up expired CSRF tokens.

        Returns:
            Number of tokens removed
        """
        current_time = time.time()
        expired_tokens = [
            token for token, data in self.csrf_tokens.items()
            if current_time - data["created_at"] > self.token_ttl
        ]

        for token in expired_tokens:
            del self.csrf_tokens[token]

        return len(expired_tokens)
