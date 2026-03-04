"""
Security Test Generator for OWASP-based vulnerability testing.

Generates security tests for:
- Injection attacks (SQL, XSS, Command Injection)
- Authentication/Authorization bypass
- Input validation vulnerabilities

Part of WAVE-2 Stage 4: Intelligent Test Generation.
"""
# CORE-035 — domain-scoped; class name appropriate for this module

from dataclasses import dataclass
from enum import Enum
from typing import Any, List


class SecurityTestType(Enum):
    """Types of security tests."""

    INJECTION = "injection"
    AUTH_BYPASS = "auth_bypass"
    INPUT_VALIDATION = "input_validation"


class VulnerabilityClass(Enum):
    """OWASP vulnerability severity classes."""

    CRITICAL = "critical"  # SQL injection, RCE
    HIGH = "high"          # XSS, auth bypass
    MEDIUM = "medium"      # CSRF, session issues
    LOW = "low"            # Info disclosure


@dataclass
class EndpointInfo:  # CORE-035-scoped — domain-specific variant
    """Information about an API endpoint."""

    path: str
    method: str
    parameters: List[str] = None
    has_database_access: bool = False
    returns_user_content: bool = False
    executes_system_commands: bool = False
    requires_authentication: bool = False
    requires_authorization: List[str] = None
    creates_session: bool = False
    accepts_json_body: bool = False
    accesses_filesystem: bool = False

    def __post_init__(self):
        """Initialize optional fields."""
        if self.parameters is None:
            self.parameters = []
        if self.requires_authorization is None:
            self.requires_authorization = []


@dataclass
class SecurityTest:
    """Represents a security test case."""

    type: SecurityTestType
    endpoint_path: str
    method: str
    payload: Any
    description: str
    vulnerability_class: VulnerabilityClass
    expected_behavior: str = "should reject malicious input"


class SecurityTestGenerator:
    """
    Generates OWASP-based security tests for API endpoints.

    Automatically creates test cases for common vulnerabilities:
    - OWASP A03:2021 Injection
    - OWASP A01:2021 Broken Access Control
    - OWASP A04:2021 Insecure Design

    Args:
        include_injection_tests: Generate injection tests (default True)
        include_auth_tests: Generate auth bypass tests (default True)
        include_validation_tests: Generate validation tests (default True)
    """

    def __init__(
        self,
        include_injection_tests: bool = True,
        include_auth_tests: bool = True,
        include_validation_tests: bool = True,
    ) -> None:
        """Initialize SecurityTestGenerator with configuration."""
        self.include_injection_tests = include_injection_tests
        self.include_auth_tests = include_auth_tests
        self.include_validation_tests = include_validation_tests

        # OWASP injection payloads
        self.sql_injection_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users--",
            "' UNION SELECT * FROM passwords--",
            "admin'--",
            "1' OR 1=1--",
        ]

        self.xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<svg onload=alert('XSS')>",
        ]

        self.command_injection_payloads = [
            "; ls -la",
            "| cat /etc/passwd",
            "&& whoami",
            "`rm -rf /`",
            "$(cat /etc/shadow)",
        ]

        self.path_traversal_payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "/etc/passwd",
            "....//....//....//etc/passwd",
        ]

    def generate_injection_tests(self, endpoint: EndpointInfo) -> List[SecurityTest]:
        """
        Generate injection vulnerability tests.

        Tests for SQL injection, XSS, and command injection
        based on endpoint characteristics.

        Args:
            endpoint: Endpoint information

        Returns:
            List of injection security tests
        """
        if not self.include_injection_tests:
            return []

        tests = []

        # SQL Injection tests
        if endpoint.has_database_access:
            # If no parameters specified, generate generic tests
            params_to_test = endpoint.parameters if endpoint.parameters else ["input"]

            for payload in self.sql_injection_payloads:
                for param in params_to_test:
                    tests.append(SecurityTest(
                        type=SecurityTestType.INJECTION,
                        endpoint_path=endpoint.path,
                        method=endpoint.method,
                        payload=payload,
                        description=f"SQL injection test for {param}: {payload}",
                        vulnerability_class=VulnerabilityClass.CRITICAL,
                        expected_behavior="should sanitize SQL input and reject injection"
                    ))

        # XSS tests
        if endpoint.returns_user_content:
            params_to_test = endpoint.parameters if endpoint.parameters else ["input"]

            for payload in self.xss_payloads:
                for param in params_to_test:
                    tests.append(SecurityTest(
                        type=SecurityTestType.INJECTION,
                        endpoint_path=endpoint.path,
                        method=endpoint.method,
                        payload=payload,
                        description=f"XSS injection test for {param}: {payload}",
                        vulnerability_class=VulnerabilityClass.HIGH,
                        expected_behavior="should encode HTML and reject scripts"
                    ))

        # Command Injection tests
        if endpoint.executes_system_commands:
            params_to_test = endpoint.parameters if endpoint.parameters else ["input"]

            for payload in self.command_injection_payloads:
                for param in params_to_test:
                    tests.append(SecurityTest(
                        type=SecurityTestType.INJECTION,
                        endpoint_path=endpoint.path,
                        method=endpoint.method,
                        payload=payload,
                        description=f"Command injection test for {param}: {payload}",
                        vulnerability_class=VulnerabilityClass.CRITICAL,
                        expected_behavior="should sanitize command input and reject injection"
                    ))

        return tests

    def generate_auth_bypass_tests(self, endpoint: EndpointInfo) -> List[SecurityTest]:
        """
        Generate authentication/authorization bypass tests.

        Tests for missing auth, expired tokens, privilege escalation,
        and session fixation vulnerabilities.

        Args:
            endpoint: Endpoint information

        Returns:
            List of auth bypass security tests
        """
        if not self.include_auth_tests:
            return []

        tests = []

        # Authentication bypass tests
        if endpoint.requires_authentication:
            # Missing authentication token
            tests.append(SecurityTest(
                type=SecurityTestType.AUTH_BYPASS,
                endpoint_path=endpoint.path,
                method=endpoint.method,
                payload={"Authorization": None},
                description="Test access with missing authentication token (no auth)",
                vulnerability_class=VulnerabilityClass.HIGH,
                expected_behavior="should return 401 Unauthorized"
            ))

            # Expired token
            tests.append(SecurityTest(
                type=SecurityTestType.AUTH_BYPASS,
                endpoint_path=endpoint.path,
                method=endpoint.method,
                payload={"Authorization": "Bearer expired_token_xyz"},
                description="Test access with expired authentication token",
                vulnerability_class=VulnerabilityClass.HIGH,
                expected_behavior="should return 401 Unauthorized"
            ))

            # Malformed token
            tests.append(SecurityTest(
                type=SecurityTestType.AUTH_BYPASS,
                endpoint_path=endpoint.path,
                method=endpoint.method,
                payload={"Authorization": "Bearer malformed!!!"},
                description="Test access with malformed authentication token",
                vulnerability_class=VulnerabilityClass.HIGH,
                expected_behavior="should return 401 Unauthorized"
            ))

        # Authorization bypass tests
        if endpoint.requires_authorization:
            for role in endpoint.requires_authorization:
                # Wrong role
                tests.append(SecurityTest(
                    type=SecurityTestType.AUTH_BYPASS,
                    endpoint_path=endpoint.path,
                    method=endpoint.method,
                    payload={"role": "user"},  # When admin required
                    description=f"Test access without required {role} role",
                    vulnerability_class=VulnerabilityClass.HIGH,
                    expected_behavior="should return 403 Forbidden"
                ))

        # Session fixation tests
        if endpoint.creates_session:
            tests.append(SecurityTest(
                type=SecurityTestType.AUTH_BYPASS,
                endpoint_path=endpoint.path,
                method=endpoint.method,
                payload={"session_id": "attacker_fixed_session"},
                description="Test session fixation vulnerability",
                vulnerability_class=VulnerabilityClass.MEDIUM,
                expected_behavior="should regenerate session ID on login"
            ))

        return tests

    def generate_input_validation_tests(self, endpoint: EndpointInfo) -> List[SecurityTest]:
        """
        Generate input validation vulnerability tests.

        Tests for mass assignment, path traversal, and other
        input validation issues.

        Args:
            endpoint: Endpoint information

        Returns:
            List of input validation security tests
        """
        if not self.include_validation_tests:
            return []

        tests = []

        # Mass assignment tests
        if endpoint.accepts_json_body and endpoint.method in ["POST", "PUT", "PATCH"]:
            tests.append(SecurityTest(
                type=SecurityTestType.INPUT_VALIDATION,
                endpoint_path=endpoint.path,
                method=endpoint.method,
                payload={"role": "admin", "is_superuser": True},
                description="Test mass assignment vulnerability (role escalation)",
                vulnerability_class=VulnerabilityClass.HIGH,
                expected_behavior="should ignore unauthorized fields"
            ))

            tests.append(SecurityTest(
                type=SecurityTestType.INPUT_VALIDATION,
                endpoint_path=endpoint.path,
                method=endpoint.method,
                payload={"id": "999", "created_at": "2020-01-01"},
                description="Test mass assignment vulnerability (protected fields)",
                vulnerability_class=VulnerabilityClass.MEDIUM,
                expected_behavior="should ignore protected system fields"
            ))

        # Path traversal tests
        if endpoint.accesses_filesystem:
            for payload in self.path_traversal_payloads:
                tests.append(SecurityTest(
                    type=SecurityTestType.INPUT_VALIDATION,
                    endpoint_path=endpoint.path,
                    method=endpoint.method,
                    payload=payload,
                    description=f"Test path traversal vulnerability: {payload}",
                    vulnerability_class=VulnerabilityClass.HIGH,
                    expected_behavior="should validate and sanitize file paths"
                ))

        return tests

    def generate_for_endpoint(self, endpoint: EndpointInfo) -> List[SecurityTest]:
        """
        Generate all applicable security tests for an endpoint.

        Combines injection, auth bypass, and validation tests
        based on endpoint characteristics and configuration.

        Args:
            endpoint: Endpoint information

        Returns:
            List of all security tests for the endpoint
        """
        tests = []

        # Add injection tests
        tests.extend(self.generate_injection_tests(endpoint))

        # Add auth bypass tests
        tests.extend(self.generate_auth_bypass_tests(endpoint))

        # Add input validation tests
        tests.extend(self.generate_input_validation_tests(endpoint))

        return tests
