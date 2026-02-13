"""
Tests for SecurityTestGenerator.

Validates generation of OWASP-based security tests for injection, auth, and validation.
"""

import pytest
from typing import List
from cortex.orchestrators.intelligence.security_test_generator import (
    SecurityTestGenerator,
    SecurityTest,
    SecurityTestType,
    VulnerabilityClass,
    EndpointInfo,
)


class TestSecurityTestGeneratorInitialization:
    """Test SecurityTestGenerator initialization."""

    def test_generator_initialization_default(self):
        """Test generator initializes with default OWASP checks."""
        generator = SecurityTestGenerator()
        
        assert generator is not None
        assert generator.include_injection_tests is True
        assert generator.include_auth_tests is True
        assert generator.include_validation_tests is True

    def test_generator_initialization_custom_config(self):
        """Test generator initializes with custom configuration."""
        generator = SecurityTestGenerator(
            include_injection_tests=True,
            include_auth_tests=False,
            include_validation_tests=True
        )
        
        assert generator.include_injection_tests is True
        assert generator.include_auth_tests is False
        assert generator.include_validation_tests is True


class TestGenerateInjectionTests:
    """Test injection vulnerability detection."""

    def test_generate_sql_injection_tests(self):
        """Test SQL injection test generation."""
        generator = SecurityTestGenerator()
        endpoint = EndpointInfo(
            path="/api/users",
            method="GET",
            parameters=["user_id", "name"],
            has_database_access=True,
        )
        
        tests = generator.generate_injection_tests(endpoint)
        
        assert len(tests) > 0
        # Should include SQL injection payloads
        payloads = {test.payload for test in tests}
        assert any("'" in p or "OR" in p or "SELECT" in p for p in payloads)
        assert all(test.type == SecurityTestType.INJECTION for test in tests)

    def test_generate_xss_tests(self):
        """Test XSS injection test generation."""
        generator = SecurityTestGenerator()
        endpoint = EndpointInfo(
            path="/api/comments",
            method="POST",
            parameters=["comment_text"],
            returns_user_content=True,
        )
        
        tests = generator.generate_injection_tests(endpoint)
        
        assert len(tests) > 0
        # Should include XSS payloads
        payloads = {test.payload for test in tests}
        assert any("<script>" in p or "onerror=" in p for p in payloads)

    def test_generate_command_injection_tests(self):
        """Test command injection test generation."""
        generator = SecurityTestGenerator()
        endpoint = EndpointInfo(
            path="/api/process",
            method="POST",
            parameters=["filename"],
            executes_system_commands=True,
        )
        
        tests = generator.generate_injection_tests(endpoint)
        
        assert len(tests) > 0
        # Should include command injection payloads
        payloads = {test.payload for test in tests}
        assert any(";" in p or "|" in p or "&" in p for p in payloads)

    def test_generate_injection_disabled(self):
        """Test injection generation can be disabled."""
        generator = SecurityTestGenerator(include_injection_tests=False)
        endpoint = EndpointInfo(
            path="/api/users",
            method="GET",
            parameters=["user_id"],
            has_database_access=True,
        )
        
        tests = generator.generate_injection_tests(endpoint)
        
        assert len(tests) == 0


class TestGenerateAuthBypassTests:
    """Test authentication/authorization bypass detection."""

    def test_generate_auth_bypass_tests(self):
        """Test auth bypass test generation."""
        generator = SecurityTestGenerator()
        endpoint = EndpointInfo(
            path="/api/admin/users",
            method="GET",
            requires_authentication=True,
            requires_authorization=["admin"],
        )
        
        tests = generator.generate_auth_bypass_tests(endpoint)
        
        assert len(tests) > 0
        assert all(test.type == SecurityTestType.AUTH_BYPASS for test in tests)
        # Should test: missing token, expired token, wrong role
        descriptions = {test.description.lower() for test in tests}
        assert any("missing" in d or "no auth" in d for d in descriptions)

    def test_generate_session_fixation_tests(self):
        """Test session fixation vulnerability tests."""
        generator = SecurityTestGenerator()
        endpoint = EndpointInfo(
            path="/api/login",
            method="POST",
            creates_session=True,
        )
        
        tests = generator.generate_auth_bypass_tests(endpoint)
        
        assert len(tests) > 0
        # Should include session fixation tests
        descriptions = {test.description.lower() for test in tests}
        assert any("session" in d for d in descriptions)

    def test_generate_auth_disabled(self):
        """Test auth generation can be disabled."""
        generator = SecurityTestGenerator(include_auth_tests=False)
        endpoint = EndpointInfo(
            path="/api/admin/users",
            method="GET",
            requires_authentication=True,
        )
        
        tests = generator.generate_auth_bypass_tests(endpoint)
        
        assert len(tests) == 0


class TestGenerateInputValidationTests:
    """Test input validation vulnerability detection."""

    def test_generate_mass_assignment_tests(self):
        """Test mass assignment vulnerability tests."""
        generator = SecurityTestGenerator()
        endpoint = EndpointInfo(
            path="/api/users/{id}",
            method="PUT",
            parameters=["name", "email"],
            accepts_json_body=True,
        )
        
        tests = generator.generate_input_validation_tests(endpoint)
        
        assert len(tests) > 0
        assert all(test.type == SecurityTestType.INPUT_VALIDATION for test in tests)
        # Should test: extra fields, role escalation
        payloads = {str(test.payload) for test in tests}
        assert any("role" in p.lower() or "admin" in p.lower() for p in payloads)

    def test_generate_path_traversal_tests(self):
        """Test path traversal vulnerability tests."""
        generator = SecurityTestGenerator()
        endpoint = EndpointInfo(
            path="/api/files/{filename}",
            method="GET",
            parameters=["filename"],
            accesses_filesystem=True,
        )
        
        tests = generator.generate_input_validation_tests(endpoint)
        
        assert len(tests) > 0
        # Should include path traversal payloads
        payloads = {test.payload for test in tests}
        assert any("../" in p or "..\\" in p for p in payloads)

    def test_generate_validation_disabled(self):
        """Test validation generation can be disabled."""
        generator = SecurityTestGenerator(include_validation_tests=False)
        endpoint = EndpointInfo(
            path="/api/users",
            method="POST",
            accepts_json_body=True,
        )
        
        tests = generator.generate_input_validation_tests(endpoint)
        
        assert len(tests) == 0


class TestGenerateForEndpoint:
    """Test comprehensive endpoint security analysis."""

    def test_generate_for_api_endpoint(self):
        """Test comprehensive security tests for API endpoint."""
        generator = SecurityTestGenerator()
        endpoint = EndpointInfo(
            path="/api/users",
            method="POST",
            parameters=["username", "email"],
            has_database_access=True,
            requires_authentication=True,
            accepts_json_body=True,
        )
        
        tests = generator.generate_for_endpoint(endpoint)
        
        # Should include multiple test types
        types_found = {test.type for test in tests}
        assert SecurityTestType.INJECTION in types_found
        assert SecurityTestType.AUTH_BYPASS in types_found
        assert SecurityTestType.INPUT_VALIDATION in types_found

    def test_generate_respects_configuration(self):
        """Test generation respects configuration flags."""
        generator = SecurityTestGenerator(
            include_injection_tests=True,
            include_auth_tests=False,
            include_validation_tests=False,
        )
        endpoint = EndpointInfo(
            path="/api/users",
            method="GET",
            has_database_access=True,
            requires_authentication=True,
        )
        
        tests = generator.generate_for_endpoint(endpoint)
        
        # Should only include injection tests
        types_found = {test.type for test in tests}
        assert SecurityTestType.INJECTION in types_found
        assert SecurityTestType.AUTH_BYPASS not in types_found
        assert SecurityTestType.INPUT_VALIDATION not in types_found

    def test_severity_assignment(self):
        """Test proper severity assignment based on vulnerability class."""
        generator = SecurityTestGenerator()
        endpoint = EndpointInfo(
            path="/api/users",
            method="POST",
            has_database_access=True,
        )
        
        tests = generator.generate_for_endpoint(endpoint)
        
        # SQL injection should be CRITICAL
        sql_tests = [t for t in tests if "sql" in t.description.lower()]
        assert all(t.vulnerability_class == VulnerabilityClass.CRITICAL for t in sql_tests)
