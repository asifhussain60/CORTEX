"""
Agent Guardrails System

Phase 5 Task 5.7: Agent Guardrails System
Provides 5-layer security and quality enforcement for agent operations.

Layers:
1. Relevance Classifier - Keep agent on-task
2. Prompt Injection Detector - Security
3. PII Filter - Privacy compliance
4. Compliance Checker - OWASP/CWE integration
5. Tool Risk Assessor - Dynamic risk scoring

Author: CORTEX Development Team
Version: 1.0.0
Created: 2025-12-21
"""

import re
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class GuardrailSeverity(Enum):
    """Severity levels for guardrail violations"""
    CRITICAL = "CRITICAL"  # Block operation immediately
    HIGH = "HIGH"          # Require manual approval
    MEDIUM = "MEDIUM"      # Log warning, allow with flag
    LOW = "LOW"            # Informational only


@dataclass
class GuardrailViolation:
    """Represents a guardrail violation"""
    layer: str
    severity: GuardrailSeverity
    category: str
    message: str
    recommendation: str
    blocked: bool = False


class RelevanceClassifier:
    """Layer 1: Keep agent on-task"""
    
    def __init__(self, allowed_topics: List[str]):
        self.allowed_topics = allowed_topics
    
    def check(self, input_text: str, context: Dict[str, Any]) -> Optional[GuardrailViolation]:
        """Check if input is relevant to allowed topics"""
        # Simple keyword-based relevance (can be enhanced with LLM)
        input_lower = input_text.lower()
        
        # Check if ANY allowed topic is mentioned
        relevant = any(topic.lower() in input_lower for topic in self.allowed_topics)
        
        if not relevant:
            return GuardrailViolation(
                layer="RelevanceClassifier",
                severity=GuardrailSeverity.MEDIUM,
                category="OFF_TOPIC",
                message=f"Input not relevant to allowed topics: {', '.join(self.allowed_topics)}",
                recommendation="Rephrase input to focus on allowed topics",
                blocked=False
            )
        
        return None


class PromptInjectionDetector:
    """Layer 2: Detect prompt injection attacks"""
    
    INJECTION_PATTERNS = [
        r'ignore\s+(previous|above|all)\s+instructions',
        r'system\s*:\s*you\s+are',
        r'<\|im_start\|>',
        r'forget\s+everything',
        r'disregard\s+(previous|all)',
    ]
    
    def check(self, input_text: str, context: Dict[str, Any]) -> Optional[GuardrailViolation]:
        """Detect prompt injection attempts"""
        input_lower = input_text.lower()
        
        for pattern in self.INJECTION_PATTERNS:
            if re.search(pattern, input_lower):
                return GuardrailViolation(
                    layer="PromptInjectionDetector",
                    severity=GuardrailSeverity.CRITICAL,
                    category="PROMPT_INJECTION",
                    message=f"Potential prompt injection detected: {pattern}",
                    recommendation="Reject input, log security event",
                    blocked=True
                )
        
        return None


class PIIFilter:
    """Layer 3: Detect and filter PII"""
    
    PII_PATTERNS = {
        'SSN': r'\b\d{3}-\d{2}-\d{4}\b',
        'CREDIT_CARD': r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
        'EMAIL': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'PHONE': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
    }
    
    def check(self, input_text: str, context: Dict[str, Any]) -> Optional[GuardrailViolation]:
        """Detect PII in input"""
        violations = []
        
        for pii_type, pattern in self.PII_PATTERNS.items():
            matches = re.findall(pattern, input_text)
            if matches:
                violations.append(f"{pii_type}: {len(matches)} instance(s)")
        
        if violations:
            return GuardrailViolation(
                layer="PIIFilter",
                severity=GuardrailSeverity.HIGH,
                category="PII_DETECTED",
                message=f"PII detected: {', '.join(violations)}",
                recommendation="Redact PII before processing",
                blocked=False  # Allow with redaction
            )
        
        return None
    
    def redact(self, text: str) -> str:
        """Redact PII from text"""
        redacted = text
        for pii_type, pattern in self.PII_PATTERNS.items():
            redacted = re.sub(pattern, f'[REDACTED_{pii_type}]', redacted)
        return redacted


class ComplianceChecker:
    """Layer 4: OWASP/CWE compliance checks"""
    
    OWASP_TOP_10 = [
        'A01:2021 – Broken Access Control',
        'A02:2021 – Cryptographic Failures',
        'A03:2021 – Injection',
        'A04:2021 – Insecure Design',
        'A05:2021 – Security Misconfiguration',
        'A06:2021 – Vulnerable and Outdated Components',
        'A07:2021 – Identification and Authentication Failures',
        'A08:2021 – Software and Data Integrity Failures',
        'A09:2021 – Security Logging and Monitoring Failures',
        'A10:2021 – Server-Side Request Forgery (SSRF)',
    ]
    
    def check(self, code: str, context: Dict[str, Any]) -> List[GuardrailViolation]:
        """Check code for OWASP Top 10 vulnerabilities"""
        violations = []
        
        # A03: Injection
        if 'eval(' in code or 'exec(' in code:
            violations.append(GuardrailViolation(
                layer="ComplianceChecker",
                severity=GuardrailSeverity.CRITICAL,
                category="A03_INJECTION",
                message="Dangerous eval/exec usage (OWASP A03)",
                recommendation="Use safe alternatives like ast.literal_eval()",
                blocked=True
            ))
        
        # A02: Cryptographic Failures
        if 'md5' in code.lower() or 'sha1' in code.lower():
            violations.append(GuardrailViolation(
                layer="ComplianceChecker",
                severity=GuardrailSeverity.HIGH,
                category="A02_CRYPTO_FAILURE",
                message="Weak cryptographic algorithm (OWASP A02)",
                recommendation="Use SHA-256 or bcrypt for hashing",
                blocked=False
            ))
        
        return violations


class ToolRiskAssessor:
    """Layer 5: Dynamic tool risk scoring"""
    
    TOOL_RISK_LEVELS = {
        'file_delete': 9,
        'database_drop': 10,
        'system_shutdown': 10,
        'network_call': 5,
        'file_read': 3,
        'file_write': 6,
        'code_execution': 8,
    }
    
    def assess_risk(self, tool_name: str, params: Dict[str, Any]) -> int:
        """Assess risk level (1-10) for tool usage"""
        base_risk = self.TOOL_RISK_LEVELS.get(tool_name, 5)
        
        # Adjust risk based on parameters
        if tool_name == 'file_write' and '/etc/' in params.get('path', ''):
            base_risk = 9  # System file write is critical
        
        if tool_name == 'network_call' and 'production' in params.get('env', ''):
            base_risk = 7  # Production network calls higher risk
        
        return min(base_risk, 10)
    
    def check(self, tool_name: str, params: Dict[str, Any]) -> Optional[GuardrailViolation]:
        """Check if tool usage exceeds risk threshold"""
        risk = self.assess_risk(tool_name, params)
        
        if risk >= 9:
            return GuardrailViolation(
                layer="ToolRiskAssessor",
                severity=GuardrailSeverity.CRITICAL,
                category="HIGH_RISK_TOOL",
                message=f"Tool {tool_name} has risk level {risk}/10",
                recommendation="Require manual approval for high-risk tools",
                blocked=True
            )
        elif risk >= 7:
            return GuardrailViolation(
                layer="ToolRiskAssessor",
                severity=GuardrailSeverity.HIGH,
                category="ELEVATED_RISK_TOOL",
                message=f"Tool {tool_name} has risk level {risk}/10",
                recommendation="Log tool usage for audit",
                blocked=False
            )
        
        return None


class GuardrailOrchestrator:
    """Orchestrates all 5 guardrail layers"""
    
    def __init__(self, allowed_topics: List[str]):
        self.relevance_classifier = RelevanceClassifier(allowed_topics)
        self.prompt_injection_detector = PromptInjectionDetector()
        self.pii_filter = PIIFilter()
        self.compliance_checker = ComplianceChecker()
        self.tool_risk_assessor = ToolRiskAssessor()
    
    def check_input(self, input_text: str, context: Dict[str, Any]) -> List[GuardrailViolation]:
        """Run all input guardrails"""
        violations = []
        
        # Layer 1: Relevance
        violation = self.relevance_classifier.check(input_text, context)
        if violation:
            violations.append(violation)
        
        # Layer 2: Prompt Injection
        violation = self.prompt_injection_detector.check(input_text, context)
        if violation:
            violations.append(violation)
            if violation.blocked:
                return violations  # Stop immediately on critical
        
        # Layer 3: PII
        violation = self.pii_filter.check(input_text, context)
        if violation:
            violations.append(violation)
        
        return violations
    
    def check_code(self, code: str, context: Dict[str, Any]) -> List[GuardrailViolation]:
        """Run all code guardrails"""
        # Layer 4: Compliance
        violations = self.compliance_checker.check(code, context)
        return violations
    
    def check_tool(self, tool_name: str, params: Dict[str, Any]) -> Optional[GuardrailViolation]:
        """Run tool risk assessment"""
        # Layer 5: Tool Risk
        return self.tool_risk_assessor.assess_risk(tool_name, params)
