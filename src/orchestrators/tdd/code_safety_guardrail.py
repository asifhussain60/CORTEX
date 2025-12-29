"""
Code Safety Guardrail for TDD Orchestrator

Package 6: Security and safety checks for generated code
Integrates with Phase 5 agent guardrails to prevent vulnerabilities.

Author: CORTEX Development Team
Version: 1.0.0
Created: 2025-12-21
"""

import logging
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

from src.orchestration_4_0.frameworks.agent_guardrails import (
    GuardrailViolation,
    GuardrailSeverity,
    GuardrailOrchestrator
)

# Alias for compatibility
ViolationSeverity = GuardrailSeverity

logger = logging.getLogger(__name__)


class SafetyCategory(Enum):
    """Safety check categories"""
    DANGEROUS_FUNCTIONS = "dangerous_functions"
    SQL_INJECTION = "sql_injection"
    HARDCODED_SECRETS = "hardcoded_secrets"
    INSECURE_DESERIALIZATION = "insecure_deserialization"
    PATH_TRAVERSAL = "path_traversal"
    COMMAND_INJECTION = "command_injection"
    XSS_VULNERABILITIES = "xss_vulnerabilities"


@dataclass
class SafetyCheckResult:
    """Result of safety check"""
    is_safe: bool
    violations: List[GuardrailViolation]
    risk_score: float  # 1-10
    recommendations: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'is_safe': self.is_safe,
            'violations': [
                {
                    'category': v.category,
                    'severity': v.severity.value,
                    'message': v.message,
                    'recommendation': v.recommendation
                }
                for v in self.violations
            ],
            'risk_score': self.risk_score,
            'recommendations': self.recommendations
        }


class CodeSafetyGuardrail:
    """
    Security and safety guardrails for generated code.
    
    Integrates with Phase 5 agent guardrails to detect:
    - Dangerous function usage (eval, exec, pickle)
    - SQL injection vulnerabilities
    - Hardcoded secrets/credentials
    - Insecure deserialization
    - Path traversal attacks
    - Command injection
    - XSS vulnerabilities
    """
    
    # Language-specific dangerous patterns
    DANGEROUS_PATTERNS = {
        'Python': {
            'eval_exec': r'\b(eval|exec|compile|__import__)\s*\(',
            'pickle': r'\bpickle\.(loads?|dumps?)\s*\(',
            'sql_injection': r'(execute|cursor\.execute|query)\s*\([^?]*["\'].*%s.*["\']',
            'command_injection': r'\b(os\.system|subprocess\.call|subprocess\.run|os\.popen)\s*\(',
            'hardcoded_password': r'(password|passwd|pwd|secret|api_key|token)\s*=\s*["\'][^"\']+["\']',
        },
        'JavaScript': {
            'eval_exec': r'\b(eval|Function|setTimeout|setInterval)\s*\(',
            'sql_injection': r'(execute|query)\s*\([^?]*`.*\$\{',
            'command_injection': r'\b(exec|spawn|execSync)\s*\(',
            'hardcoded_password': r'(password|passwd|pwd|secret|apiKey|token)\s*[:=]\s*["\'][^"\']+["\']',
            'xss': r'(innerHTML|outerHTML|document\.write)\s*=',
        },
        'TypeScript': {
            'eval_exec': r'\b(eval|Function|setTimeout|setInterval)\s*\(',
            'sql_injection': r'(execute|query)\s*\([^?]*`.*\$\{',
            'command_injection': r'\b(exec|spawn|execSync)\s*\(',
            'hardcoded_password': r'(password|passwd|pwd|secret|apiKey|token)\s*[:=]\s*["\'][^"\']+["\']',
            'xss': r'(innerHTML|outerHTML|document\.write)\s*=',
        },
        'C#': {
            'eval_exec': r'\b(Eval|Execute|CompileAssemblyFromSource)\s*\(',
            'sql_injection': r'(ExecuteReader|ExecuteNonQuery|ExecuteScalar)\s*\([^?]*\+',
            'command_injection': r'\b(Process\.Start|ProcessStartInfo)\s*\(',
            'hardcoded_password': r'(Password|Passwd|Pwd|Secret|ApiKey|Token)\s*=\s*"[^"]+"',
            'deserialization': r'\b(BinaryFormatter|ObjectStateFormatter|NetDataContractSerializer)\s*\(',
        }
    }
    
    def __init__(self):
        """Initialize code safety guardrail"""
        # Initialize with code safety topics
        self.guardrail_orchestrator = GuardrailOrchestrator(
            allowed_topics=['code', 'implementation', 'security', 'testing', 'development']
        )
        logger.info("🎭 Code Safety Guardrail initialized")
    
    def check_code_safety(
        self,
        code: str,
        language: str,
        context: Optional[str] = None
    ) -> SafetyCheckResult:
        """
        Perform comprehensive safety check on generated code.
        
        Args:
            code: Code to check
            language: Programming language
            context: Optional context about code purpose
            
        Returns:
            SafetyCheckResult with violations and recommendations
        """
        logger.info(f"🔒 Running safety checks for {language} code")
        
        violations = []
        recommendations = []
        
        # Get language-specific patterns
        patterns = self.DANGEROUS_PATTERNS.get(language, {})
        
        # Check for dangerous functions
        dangerous_violations = self._check_dangerous_functions(code, patterns)
        violations.extend(dangerous_violations)
        
        # Check for SQL injection
        sql_violations = self._check_sql_injection(code, patterns)
        violations.extend(sql_violations)
        
        # Check for hardcoded secrets
        secret_violations = self._check_hardcoded_secrets(code, patterns)
        violations.extend(secret_violations)
        
        # Check for insecure deserialization
        deser_violations = self._check_insecure_deserialization(code, patterns, language)
        violations.extend(deser_violations)
        
        # Check for path traversal
        path_violations = self._check_path_traversal(code)
        violations.extend(path_violations)
        
        # Check for command injection
        cmd_violations = self._check_command_injection(code, patterns)
        violations.extend(cmd_violations)
        
        # Check for XSS (JavaScript/TypeScript)
        if language in ['JavaScript', 'TypeScript']:
            xss_violations = self._check_xss(code, patterns)
            violations.extend(xss_violations)
        
        # Use guardrail orchestrator for additional checks
        orchestrator_violations = self.guardrail_orchestrator.check_code(
            code=code,
            context={'language': language}
        )
        violations.extend(orchestrator_violations)
        
        # Calculate risk score
        risk_score = self._calculate_risk_score(violations)
        
        # Build recommendations
        recommendations = self._build_recommendations(violations, language)
        
        # Determine if code is safe
        is_safe = all(v.severity != ViolationSeverity.CRITICAL for v in violations)
        
        result = SafetyCheckResult(
            is_safe=is_safe,
            violations=violations,
            risk_score=risk_score,
            recommendations=recommendations
        )
        
        if is_safe:
            logger.info(f"✅ Code safety check passed (risk score: {risk_score:.1f}/10)")
        else:
            logger.warning(f"❌ Code safety check failed (risk score: {risk_score:.1f}/10)")
        
        return result
    
    def _check_dangerous_functions(
        self,
        code: str,
        patterns: Dict[str, str]
    ) -> List[GuardrailViolation]:
        """Check for dangerous function usage"""
        violations = []
        
        if 'eval_exec' in patterns:
            matches = re.finditer(patterns['eval_exec'], code, re.IGNORECASE)
            for match in matches:
                violations.append(GuardrailViolation(
                    layer="CodeSafety",
                    severity=GuardrailSeverity.CRITICAL,
                    category="DangerousFunction",
                    message=f"Dangerous function detected: {match.group()}",
                    recommendation="Replace eval/exec with safer alternatives (ast.literal_eval)",
                    blocked=True
                ))
        
        if 'pickle' in patterns:
            matches = re.finditer(patterns['pickle'], code, re.IGNORECASE)
            for match in matches:
                violations.append(GuardrailViolation(
                    layer="CodeSafety",
                    severity=GuardrailSeverity.HIGH,
                    category="InsecurePickle",
                    message="Insecure pickle usage detected",
                    recommendation="Use JSON serialization or implement custom serialization",
                    blocked=False
                ))
        
        return violations
    
    def _check_sql_injection(
        self,
        code: str,
        patterns: Dict[str, str]
    ) -> List[GuardrailViolation]:
        """Check for SQL injection vulnerabilities"""
        violations = []
        
        if 'sql_injection' in patterns:
            matches = re.finditer(patterns['sql_injection'], code, re.IGNORECASE)
            for match in matches:
                violations.append(GuardrailViolation(
                    layer="CodeSafety",
                    severity=GuardrailSeverity.CRITICAL,
                    category="SQLInjection",
                    message="Potential SQL injection vulnerability (string concatenation in query)",
                    recommendation="Use parameterized queries with ? placeholders",
                    blocked=True
                ))
        
        return violations
    
    def _check_hardcoded_secrets(
        self,
        code: str,
        patterns: Dict[str, str]
    ) -> List[GuardrailViolation]:
        """Check for hardcoded secrets"""
        violations = []
        
        if 'hardcoded_password' in patterns:
            matches = re.finditer(patterns['hardcoded_password'], code, re.IGNORECASE)
            for match in matches:
                # Filter out test fixtures and example passwords
                context = self._extract_context(code, match.start())
                if not any(word in context.lower() for word in ['test', 'example', 'dummy', 'fake']):
                    violations.append(GuardrailViolation(
                        layer="CodeSafety",
                        severity=GuardrailSeverity.HIGH,
                        category="HardcodedSecret",
                        message="Hardcoded secret/credential detected",
                        recommendation="Move to environment variables or secure vault",
                        blocked=False
                    ))
        
        return violations
    
    def _check_insecure_deserialization(
        self,
        code: str,
        patterns: Dict[str, str],
        language: str
    ) -> List[GuardrailViolation]:
        """Check for insecure deserialization"""
        violations = []
        
        if 'deserialization' in patterns:
            matches = re.finditer(patterns['deserialization'], code, re.IGNORECASE)
            for match in matches:
                violations.append(GuardrailViolation(
                    layer="CodeSafety",
                    severity=GuardrailSeverity.HIGH,
                    category="InsecureDeserialization",
                    message="Insecure deserialization method detected",
                    recommendation="Use JSON or implement validation on deserialization",
                    blocked=False
                ))
        
        return violations
    
    def _check_path_traversal(self, code: str) -> List[GuardrailViolation]:
        """Check for path traversal vulnerabilities"""
        violations = []
        
        # Look for path operations with user input
        path_patterns = [
            r'(open|read|write|readFile|writeFile)\s*\([^)]*\+',  # Concatenation
            r'(open|read|write|readFile|writeFile)\s*\([^)]*f["\']',  # f-strings
        ]
        
        for pattern in path_patterns:
            matches = re.finditer(pattern, code, re.IGNORECASE)
            for match in matches:
                violations.append(GuardrailViolation(
                    layer="CodeSafety",
                    severity=GuardrailSeverity.MEDIUM,
                    category="PathTraversal",
                    message="Potential path traversal vulnerability (unsanitized path)",
                    recommendation="Validate paths using Path.resolve() or os.path.abspath()",
                    blocked=False
                ))
        
        return violations
    
    def _check_command_injection(
        self,
        code: str,
        patterns: Dict[str, str]
    ) -> List[GuardrailViolation]:
        """Check for command injection"""
        violations = []
        
        if 'command_injection' in patterns:
            matches = re.finditer(patterns['command_injection'], code, re.IGNORECASE)
            for match in matches:
                violations.append(GuardrailViolation(
                    layer="CodeSafety",
                    severity=GuardrailSeverity.CRITICAL,
                    category="CommandInjection",
                    message="Potential command injection (unsanitized input to system command)",
                    recommendation="Use subprocess with list arguments instead of shell=True",
                    blocked=True
                ))
        
        return violations
    
    def _check_xss(
        self,
        code: str,
        patterns: Dict[str, str]
    ) -> List[GuardrailViolation]:
        """Check for XSS vulnerabilities"""
        violations = []
        
        if 'xss' in patterns:
            matches = re.finditer(patterns['xss'], code, re.IGNORECASE)
            for match in matches:
                violations.append(GuardrailViolation(
                    layer="CodeSafety",
                    severity=GuardrailSeverity.HIGH,
                    category="XSS",
                    message="Potential XSS vulnerability (unsafe HTML manipulation)",
                    recommendation="Use textContent or sanitize with DOMPurify",
                    blocked=False
                ))
        
        return violations
    
    def _calculate_risk_score(self, violations: List[GuardrailViolation]) -> float:
        """Calculate overall risk score (1-10)"""
        if not violations:
            return 1.0
        
        # Severity weights
        weights = {
            GuardrailSeverity.CRITICAL: 10.0,
            GuardrailSeverity.HIGH: 7.0,
            GuardrailSeverity.MEDIUM: 4.0,
            GuardrailSeverity.LOW: 2.0
        }
        
        # Calculate weighted average
        total_weight = sum(weights[v.severity] for v in violations)
        avg_severity = total_weight / len(violations)
        
        return min(avg_severity, 10.0)
    
    def _build_recommendations(
        self,
        violations: List[GuardrailViolation],
        language: str
    ) -> List[str]:
        """Build security recommendations"""
        recommendations = []
        
        violation_types = {v.category for v in violations}
        
        if 'DangerousFunction' in violation_types:
            if language == 'Python':
                recommendations.append("Replace eval/exec with ast.literal_eval or safer alternatives")
            elif language in ['JavaScript', 'TypeScript']:
                recommendations.append("Avoid eval() - use JSON.parse() or Function constructor with caution")
        
        if 'SQLInjection' in violation_types:
            recommendations.append("Use parameterized queries or prepared statements (? placeholders)")
        
        if 'HardcodedSecret' in violation_types:
            recommendations.append("Move secrets to environment variables or secure vault (e.g., Azure Key Vault)")
        
        if 'InsecureDeserialization' in violation_types:
            recommendations.append("Use JSON serialization or implement custom serialization with validation")
        
        if 'PathTraversal' in violation_types:
            recommendations.append("Validate and sanitize file paths using Path.resolve() or os.path.abspath()")
        
        if 'CommandInjection' in violation_types:
            recommendations.append("Use subprocess with list arguments instead of shell=True")
        
        if 'XSS' in violation_types:
            recommendations.append("Use textContent instead of innerHTML, or sanitize HTML with DOMPurify")
        
        return recommendations
    
    def _extract_context(self, code: str, position: int, window: int = 50) -> str:
        """Extract context around violation"""
        start = max(0, position - window)
        end = min(len(code), position + window)
        return code[start:end].strip()
