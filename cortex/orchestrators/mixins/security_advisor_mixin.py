"""
Security Advisor Mixin for Orchestrators
Provides security-first capabilities with P0/P1/P2 risk assessment

Implements OWASP Top 10 checks, risk assessment, and security recommendations
for all orchestrator operations.
"""
import re
from typing import Dict, Any, List, Optional, Set
from enum import Enum
from pathlib import Path


class SecurityLevel(Enum):
    """Security risk levels (P0-P3)"""
    P0_CRITICAL = "P0_CRITICAL"  # SQL injection, RCE, auth bypass
    P1_HIGH = "P1_HIGH"          # XSS, insecure deserialization
    P2_MEDIUM = "P2_MEDIUM"      # Weak crypto, missing validation
    P3_LOW = "P3_LOW"            # Info disclosure, missing hardening


class VulnerabilityType(Enum):
    """OWASP Top 10 vulnerability types"""
    SQL_INJECTION = "SQL_INJECTION"
    XSS = "XSS"
    BROKEN_AUTH = "BROKEN_AUTH"
    SENSITIVE_DATA_EXPOSURE = "SENSITIVE_DATA_EXPOSURE"
    XXE = "XXE"
    BROKEN_ACCESS_CONTROL = "BROKEN_ACCESS_CONTROL"
    SECURITY_MISCONFIGURATION = "SECURITY_MISCONFIGURATION"
    INSECURE_DESERIALIZATION = "INSECURE_DESERIALIZATION"
    VULNERABLE_COMPONENTS = "VULNERABLE_COMPONENTS"
    INSUFFICIENT_LOGGING = "INSUFFICIENT_LOGGING"


class SecurityAdvisorMixin:
    """
    Mixin providing security-first capabilities for orchestrators.
    
    Provides comprehensive security assessment:
    - OWASP Top 10 vulnerability detection
    - P0/P1/P2/P3 risk assessment
    - Context-aware security recommendations
    - Input validation and sanitization checks
    """
    
    # SQL injection patterns (basic detection)
    SQL_INJECTION_PATTERNS = [
        r"execute\s*\(\s*['\"].*?%s.*?['\"]",  # String interpolation in SQL
        r"execute\s*\(\s*f['\"].*?\{.*?\}.*?['\"]",  # F-string in SQL
        r"cursor\.execute\s*\(\s*['\"].*?\+",  # String concatenation
        r"\.raw\s*\(\s*['\"].*?\+",  # Django ORM raw queries
        r"\.execute\s*\(\s*['\"]SELECT.*?WHERE.*?\+",  # Direct concatenation
    ]
    
    # XSS patterns
    XSS_PATTERNS = [
        r"\.innerHTML\s*=",  # Direct innerHTML assignment
        r"document\.write\s*\(",  # document.write usage
        r"eval\s*\(",  # eval() usage
        r"dangerouslySetInnerHTML",  # React dangerous HTML
        r"v-html\s*=",  # Vue v-html directive
    ]
    
    # Hardcoded secrets patterns
    SECRET_PATTERNS = [
        r"password\s*=\s*['\"][^'\"]+['\"]",
        r"api_key\s*=\s*['\"][^'\"]+['\"]",
        r"secret\s*=\s*['\"][^'\"]+['\"]",
        r"token\s*=\s*['\"][^'\"]+['\"]",
        r"private_key\s*=\s*['\"][^'\"]+['\"]",
    ]
    
    # Insecure deserialization patterns
    DESERIALIZATION_PATTERNS = [
        r"pickle\.loads",
        r"yaml\.load\s*\(",  # Should use safe_load
        r"eval\s*\(",
        r"exec\s*\(",
        r"__import__",
    ]
    
    def assess_security_risk(
        self,
        operation: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Assess security risk of an operation with OWASP checks.
        
        Args:
            operation: Operation being performed (IMPLEMENT, FIX, etc.)
            context: Operation context (code, file_path, intent, etc.)
        
        Returns:
            Dict with risk_level, vulnerabilities, recommendations, confidence
        """
        context = context or {}
        vulnerabilities: List[Dict[str, Any]] = []
        
        # Extract code for analysis
        code_snippet = context.get("code", "")
        file_path = context.get("file_path", "")
        intent = context.get("intent", "")
        
        # Run OWASP Top 10 checks
        if code_snippet:
            vulnerabilities.extend(self.check_owasp_top_10(code_snippet, context))
        
        # Determine risk level based on vulnerabilities
        risk_level = self._calculate_risk_level(vulnerabilities, operation, intent)
        
        # Generate context-aware recommendations
        recommendations = self.get_security_recommendations(operation, risk_level.value)
        
        # Add vulnerability-specific recommendations
        for vuln in vulnerabilities:
            vuln_type = vuln.get("type")
            if vuln_type:
                recommendations.extend(self._get_mitigation_for_vuln(vuln_type))
        
        return {
            "risk_level": risk_level.value,
            "vulnerabilities": vulnerabilities,
            "recommendations": list(set(recommendations)),  # Deduplicate
            "assessment_confidence": self._calculate_confidence(code_snippet, vulnerabilities),
            "operation": operation,
            "files_analyzed": [file_path] if file_path else [],
        }
    
    def check_owasp_top_10(
        self,
        code_snippet: str,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Check code against OWASP Top 10 vulnerabilities.
        
        Args:
            code_snippet: Code to analyze
            context: Optional analysis context
        
        Returns:
            List of detected vulnerabilities with type, severity, line, description
        """
        vulnerabilities = []
        lines = code_snippet.split('\n')
        
        # Check for SQL injection
        for i, line in enumerate(lines, 1):
            for pattern in self.SQL_INJECTION_PATTERNS:
                if re.search(pattern, line, re.IGNORECASE):
                    vulnerabilities.append({
                        "type": VulnerabilityType.SQL_INJECTION.value,
                        "severity": SecurityLevel.P0_CRITICAL.value,
                        "line": i,
                        "description": "Potential SQL injection via string concatenation/interpolation",
                        "code": line.strip(),
                    })
        
        # Check for XSS
        for i, line in enumerate(lines, 1):
            for pattern in self.XSS_PATTERNS:
                if re.search(pattern, line, re.IGNORECASE):
                    vulnerabilities.append({
                        "type": VulnerabilityType.XSS.value,
                        "severity": SecurityLevel.P1_HIGH.value,
                        "line": i,
                        "description": "Potential XSS vulnerability via unsafe HTML rendering",
                        "code": line.strip(),
                    })
        
        # Check for hardcoded secrets
        for i, line in enumerate(lines, 1):
            for pattern in self.SECRET_PATTERNS:
                if re.search(pattern, line, re.IGNORECASE):
                    # Exclude test files and examples
                    if not any(x in line.lower() for x in ['example', 'test', 'dummy', 'placeholder']):
                        vulnerabilities.append({
                            "type": VulnerabilityType.SENSITIVE_DATA_EXPOSURE.value,
                            "severity": SecurityLevel.P1_HIGH.value,
                            "line": i,
                            "description": "Hardcoded secret detected - use environment variables",
                            "code": line.strip()[:50] + "...",  # Truncate for safety
                        })
        
        # Check for insecure deserialization
        for i, line in enumerate(lines, 1):
            for pattern in self.DESERIALIZATION_PATTERNS:
                if re.search(pattern, line):
                    vulnerabilities.append({
                        "type": VulnerabilityType.INSECURE_DESERIALIZATION.value,
                        "severity": SecurityLevel.P1_HIGH.value,
                        "line": i,
                        "description": "Insecure deserialization pattern detected",
                        "code": line.strip(),
                    })
        
        # Check for missing input validation
        if "request." in code_snippet and not any(x in code_snippet for x in ["validate", "sanitize", "clean"]):
            vulnerabilities.append({
                "type": VulnerabilityType.BROKEN_ACCESS_CONTROL.value,
                "severity": SecurityLevel.P2_MEDIUM.value,
                "line": 0,
                "description": "Request data used without apparent validation",
                "code": "",
            })
        
        # Check for insufficient logging
        if any(x in code_snippet for x in ["password", "secret", "token"]):
            if "log" not in code_snippet.lower():
                vulnerabilities.append({
                    "type": VulnerabilityType.INSUFFICIENT_LOGGING.value,
                    "severity": SecurityLevel.P2_MEDIUM.value,
                    "line": 0,
                    "description": "Security-sensitive operation without audit logging",
                    "code": "",
                })
        
        return vulnerabilities
    
    def get_security_recommendations(
        self,
        operation_type: str,
        risk_level: str
    ) -> List[str]:
        """
        Get security recommendations based on operation and risk level.
        
        Args:
            operation_type: Type of operation (IMPLEMENT, FIX, etc.)
            risk_level: Current risk level (P0/P1/P2/P3)
        
        Returns:
            List of actionable security recommendations
        """
        recommendations = []
        
        # Base recommendations for all operations
        recommendations.extend([
            "Follow principle of least privilege",
            "Validate and sanitize all inputs",
            "Use parameterized queries for database operations",
            "Enable comprehensive audit logging",
        ])
        
        # Risk-level specific recommendations
        if risk_level in [SecurityLevel.P0_CRITICAL.value, SecurityLevel.P1_HIGH.value]:
            recommendations.extend([
                "⚠️  CRITICAL: Address P0/P1 vulnerabilities before deployment",
                "Implement security testing in CI/CD pipeline",
                "Conduct security code review",
                "Add integration tests for security controls",
            ])
        
        # Operation-specific recommendations
        if operation_type in ["IMPLEMENT", "FIX"]:
            recommendations.extend([
                "Use established security libraries (don't roll your own crypto)",
                "Implement defense in depth",
                "Add error handling without information leakage",
            ])
        elif operation_type == "REFACTOR":
            recommendations.extend([
                "Preserve existing security controls",
                "Review access control after structural changes",
                "Update security tests to match new structure",
            ])
        
        return recommendations
    
    def validate_security_context(
        self,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate security context before operation execution.
        
        Args:
            context: Operation context to validate
        
        Returns:
            Dict with valid flag, issues list, warnings list
        """
        issues = []
        warnings = []
        
        # Check for required security metadata
        if "user_id" not in context:
            warnings.append("No user_id in context - audit trail incomplete")
        
        if "intent" not in context:
            issues.append("Missing intent - cannot assess security risk")
        
        # Check for dangerous operations without confirmation
        dangerous_operations = ["DELETE", "DROP", "TRUNCATE", "EXECUTE"]
        code = context.get("code", "")
        if any(op in code.upper() for op in dangerous_operations):
            if not context.get("confirmed", False):
                issues.append("Dangerous operation requires explicit confirmation")
        
        # Check for security-sensitive files
        file_path = context.get("file_path", "")
        if file_path:
            sensitive_paths = ["auth", "security", "secrets", "credentials", "config"]
            if any(x in file_path.lower() for x in sensitive_paths):
                warnings.append(f"Modifying security-sensitive file: {file_path}")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
        }
    
    def _calculate_risk_level(
        self,
        vulnerabilities: List[Dict[str, Any]],
        operation: str,
        intent: str
    ) -> SecurityLevel:
        """Calculate overall risk level from vulnerabilities."""
        if not vulnerabilities:
            return SecurityLevel.P3_LOW
        
        # Get highest severity from vulnerabilities
        severities = [v.get("severity") for v in vulnerabilities]
        
        if SecurityLevel.P0_CRITICAL.value in severities:
            return SecurityLevel.P0_CRITICAL
        elif SecurityLevel.P1_HIGH.value in severities:
            return SecurityLevel.P1_HIGH
        elif SecurityLevel.P2_MEDIUM.value in severities:
            return SecurityLevel.P2_MEDIUM
        else:
            return SecurityLevel.P3_LOW
    
    def _calculate_confidence(
        self,
        code_snippet: str,
        vulnerabilities: List[Dict[str, Any]]
    ) -> float:
        """Calculate confidence score for security assessment."""
        if not code_snippet:
            return 0.0
        
        # Higher confidence with more code analyzed
        code_length_factor = min(len(code_snippet) / 1000, 1.0)
        
        # Higher confidence with clear vulnerability signals
        vuln_clarity_factor = 0.8 if vulnerabilities else 0.6
        
        return round(code_length_factor * vuln_clarity_factor, 2)
    
    def _get_mitigation_for_vuln(self, vuln_type: str) -> List[str]:
        """Get specific mitigation recommendations for vulnerability type."""
        mitigations = {
            VulnerabilityType.SQL_INJECTION.value: [
                "Use parameterized queries or ORMs",
                "Never concatenate user input into SQL",
                "Apply input validation and whitelist allowed characters",
            ],
            VulnerabilityType.XSS.value: [
                "Use framework-provided escaping (e.g., Jinja2 autoescape)",
                "Implement Content Security Policy (CSP)",
                "Sanitize user input on both client and server",
            ],
            VulnerabilityType.SENSITIVE_DATA_EXPOSURE.value: [
                "Move secrets to environment variables",
                "Use secret management systems (Vault, AWS Secrets Manager)",
                "Never commit secrets to version control",
            ],
            VulnerabilityType.INSECURE_DESERIALIZATION.value: [
                "Use safe deserialization methods (yaml.safe_load)",
                "Validate data structure before deserializing",
                "Avoid pickle for untrusted data",
            ],
        }
        
        return mitigations.get(vuln_type, [])
