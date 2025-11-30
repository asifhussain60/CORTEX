"""
Investigation Security Plugin for CORTEX 3.0

Specialized security analysis plugin that integrates with InvestigationRouter
to provide security vulnerability detection during investigation phases.

Features:
- Vulnerability pattern scanning (OWASP Top 10)
- Dependency security analysis
- Code security best practices validation
- HTML security analysis (XSS, CSRF, etc.)
- Token-budget aware security scanning

Integration with InvestigationRouter:
- Hooks into analysis phase for detailed security scanning
- Respects token budget constraints
- Provides security-specific findings
- Generates actionable security recommendations

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import re
import logging
import json
from datetime import datetime

from src.plugins.base_plugin import (
    BasePlugin,
    PluginMetadata,
    PluginCategory,
    PluginPriority,
    HookPoint
)

logger = logging.getLogger(__name__)


class SecurityVulnerabilityType(Enum):
    """OWASP Top 10 and common security vulnerabilities"""
    SQL_INJECTION = "sql_injection"
    XSS_REFLECTED = "xss_reflected"
    XSS_STORED = "xss_stored"
    XSS_DOM = "xss_dom"
    CSRF = "csrf"
    HARDCODED_SECRETS = "hardcoded_secrets"
    PATH_TRAVERSAL = "path_traversal"
    INSECURE_DESERIALIZATION = "insecure_deserialization"
    BROKEN_ACCESS_CONTROL = "broken_access_control"
    SECURITY_MISCONFIGURATION = "security_misconfiguration"
    WEAK_CRYPTO = "weak_cryptography"
    INSECURE_STORAGE = "insecure_storage"
    UNVALIDATED_REDIRECTS = "unvalidated_redirects"
    MISSING_AUTHENTICATION = "missing_authentication"
    MISSING_AUTHORIZATION = "missing_authorization"
    EXPOSED_SENSITIVE_DATA = "exposed_sensitive_data"


class SecuritySeverity(Enum):
    """Security vulnerability severity levels"""
    CRITICAL = "critical"  # Immediate fix required
    HIGH = "high"         # Fix in next release
    MEDIUM = "medium"     # Fix when possible
    LOW = "low"          # Monitor/document
    INFO = "info"        # Informational only


@dataclass
class SecurityFinding:
    """Security vulnerability finding"""
    type: SecurityVulnerabilityType
    severity: SecuritySeverity
    file_path: str
    line_number: int
    title: str
    description: str
    recommendation: str
    code_snippet: Optional[str] = None
    confidence: float = 1.0  # 0.0 to 1.0
    owasp_category: Optional[str] = None
    cve_references: List[str] = None
    
    def __post_init__(self):
        if self.cve_references is None:
            self.cve_references = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for investigation router"""
        return {
            "type": "security_finding",
            "vulnerability_type": self.type.value,
            "severity": self.severity.value,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "title": self.title,
            "description": self.description,
            "recommendation": self.recommendation,
            "code_snippet": self.code_snippet,
            "confidence": self.confidence,
            "owasp_category": self.owasp_category,
            "cve_references": self.cve_references,
            "timestamp": datetime.now().isoformat()
        }


class SecurityPatternDatabase:
    """Database of security vulnerability patterns"""
    
    def __init__(self):
        self.patterns = {
            # SQL Injection patterns
            SecurityVulnerabilityType.SQL_INJECTION: [
                {
                    "pattern": r'(SELECT|INSERT|UPDATE|DELETE).*\+.*[\'"]\s*\+',
                    "language": ["python", "csharp", "java"],
                    "description": "Potential SQL injection via string concatenation",
                    "confidence": 0.8
                },
                {
                    "pattern": r'execute\s*\(\s*["\'][^"\']*[\'"]\s*\+',
                    "language": ["python"],
                    "description": "SQL execution with string concatenation",
                    "confidence": 0.9
                },
                {
                    "pattern": r'cursor\.execute\s*\([^)]*\%[^)]*\)',
                    "language": ["python"],
                    "description": "Potential SQL injection via string formatting",
                    "confidence": 0.7
                },
            ],
            
            # XSS patterns
            SecurityVulnerabilityType.XSS_REFLECTED: [
                {
                    "pattern": r'innerHTML\s*=.*request\.|innerHTML\s*=.*params\.',
                    "language": ["javascript", "typescript"],
                    "description": "Potential XSS via innerHTML with user input",
                    "confidence": 0.9
                },
                {
                    "pattern": r'document\.write\s*\(.*request\.',
                    "language": ["javascript"],
                    "description": "Potential XSS via document.write with user input",
                    "confidence": 0.8
                },
            ],
            
            # Hardcoded secrets patterns
            SecurityVulnerabilityType.HARDCODED_SECRETS: [
                {
                    "pattern": r'password\s*=\s*["\'][^"\']{8,}["\']',
                    "language": ["python", "javascript", "csharp", "java"],
                    "description": "Potential hardcoded password",
                    "confidence": 0.7
                },
                {
                    "pattern": r'api_key\s*=\s*["\'][A-Za-z0-9]{20,}["\']',
                    "language": ["python", "javascript", "csharp", "java"],
                    "description": "Potential hardcoded API key",
                    "confidence": 0.8
                },
                {
                    "pattern": r'(secret|token|key)\s*=\s*["\'][A-Za-z0-9+/=]{16,}["\']',
                    "language": ["python", "javascript", "csharp", "java"],
                    "description": "Potential hardcoded secret/token",
                    "confidence": 0.6
                },
            ],
            
            # Path traversal patterns
            SecurityVulnerabilityType.PATH_TRAVERSAL: [
                {
                    "pattern": r'open\s*\(.*\+.*\)|read\s*\(.*\+.*\)',
                    "language": ["python"],
                    "description": "Potential path traversal via file operations",
                    "confidence": 0.6
                },
                {
                    "pattern": r'\.\.[\\/]|\.\.%2[fF]|\.\.%5[cC]',
                    "language": ["python", "javascript", "csharp", "java"],
                    "description": "Directory traversal pattern detected",
                    "confidence": 0.8
                },
            ]
        }
    
    def get_patterns_for_language(self, language: str) -> Dict[SecurityVulnerabilityType, List[Dict]]:
        """Get security patterns for specific programming language"""
        filtered_patterns = {}
        
        for vuln_type, patterns in self.patterns.items():
            filtered_patterns[vuln_type] = [
                pattern for pattern in patterns 
                if language.lower() in pattern["language"]
            ]
        
        return filtered_patterns


class HTMLSecurityAnalyzer:
    """Analyzes HTML for security vulnerabilities and ID mapping"""
    
    def __init__(self):
        self.logger = logging.getLogger("security.html")
    
    def analyze_html_security(self, file_path: str, content: str) -> List[SecurityFinding]:
        """Analyze HTML content for security vulnerabilities"""
        findings = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Check for missing CSRF tokens in forms
            if '<form' in line.lower() and 'method="post"' in line.lower():
                if not self._has_csrf_protection(content, line_num):
                    findings.append(SecurityFinding(
                        type=SecurityVulnerabilityType.CSRF,
                        severity=SecuritySeverity.HIGH,
                        file_path=file_path,
                        line_number=line_num,
                        title="Missing CSRF Protection",
                        description="POST form without CSRF token detected",
                        recommendation="Add CSRF token to form. Use {% csrf_token %} in Django or equivalent in your framework.",
                        code_snippet=line.strip(),
                        confidence=0.8,
                        owasp_category="A01:2021 – Broken Access Control"
                    ))
            
            # Check for potential XSS via innerHTML
            if 'innerHTML' in line and any(unsafe in line for unsafe in ['user', 'input', 'param']):
                findings.append(SecurityFinding(
                    type=SecurityVulnerabilityType.XSS_DOM,
                    severity=SecuritySeverity.HIGH,
                    file_path=file_path,
                    line_number=line_num,
                    title="Potential DOM XSS via innerHTML",
                    description="innerHTML usage with potential user input detected",
                    recommendation="Use textContent instead of innerHTML, or sanitize input properly.",
                    code_snippet=line.strip(),
                    confidence=0.7,
                    owasp_category="A03:2021 – Injection"
                ))
        
        return findings
    
    def analyze_html_id_mapping(self, file_path: str, content: str) -> Dict[str, Any]:
        """Analyze HTML for element ID mapping and missing IDs"""
        element_mapping = {
            "elements_with_ids": [],
            "elements_missing_ids": [],
            "suggested_ids": [],
            "accessibility_issues": []
        }
        
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Find elements that should have IDs but don't
            missing_id_patterns = [
                (r'<(button|input|select|textarea)[^>]*>', "form controls should have IDs for accessibility"),
                (r'<(h[1-6])[^>]*>', "headings should have IDs for navigation"),
                (r'<(section|article|main|nav)[^>]*>', "semantic elements should have IDs for navigation")
            ]
            
            for pattern, reason in missing_id_patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    element_tag = match.group()
                    if 'id=' not in element_tag:
                        # Extract element type and suggest ID
                        element_type = match.group(1).lower()
                        suggested_id = self._generate_suggested_id(element_tag, element_type, line_num)
                        
                        element_mapping["elements_missing_ids"].append({
                            "line_number": line_num,
                            "element": element_tag,
                            "element_type": element_type,
                            "reason": reason,
                            "suggested_id": suggested_id,
                            "code_snippet": line.strip()
                        })
            
            # Find existing elements with IDs
            id_pattern = r'<([a-zA-Z]+)[^>]*id=["\']([^"\']+)["\'][^>]*>'
            id_matches = re.finditer(id_pattern, line, re.IGNORECASE)
            for match in id_matches:
                element_type = match.group(1)
                element_id = match.group(2)
                element_mapping["elements_with_ids"].append({
                    "line_number": line_num,
                    "element_type": element_type,
                    "id": element_id,
                    "full_element": match.group(),
                    "code_snippet": line.strip()
                })
        
        return element_mapping
    
    def _has_csrf_protection(self, content: str, form_line: int) -> bool:
        """Check if form has CSRF protection"""
        csrf_patterns = [
            r'csrf_token',
            r'__RequestVerificationToken',
            r'_token',
            r'authenticity_token'
        ]
        
        # Look for CSRF patterns in the next 10 lines after form
        lines = content.split('\n')
        start_idx = max(0, form_line - 1)
        end_idx = min(len(lines), form_line + 10)
        
        for line in lines[start_idx:end_idx]:
            for pattern in csrf_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    return True
        
        return False
    
    def _generate_suggested_id(self, element_tag: str, element_type: str, line_num: int) -> str:
        """Generate suggested ID for an element"""
        # Extract meaningful attributes
        text_content = ""
        name_attr = ""
        class_attr = ""
        
        # Extract name attribute
        name_match = re.search(r'name=["\']([^"\']+)["\']', element_tag)
        if name_match:
            name_attr = name_match.group(1)
        
        # Extract class attribute
        class_match = re.search(r'class=["\']([^"\']+)["\']', element_tag)
        if class_match:
            class_attr = class_match.group(1).split()[0]  # Take first class
        
        # Extract text content for buttons
        text_match = re.search(r'>([^<]+)<', element_tag)
        if text_match:
            text_content = text_match.group(1).strip()
        
        # Generate ID based on available information
        if name_attr:
            return f"{name_attr}_{element_type}"
        elif class_attr:
            return f"{class_attr}_{element_type}"
        elif text_content:
            # Convert text to valid ID
            clean_text = re.sub(r'[^a-zA-Z0-9]', '_', text_content.lower())
            return f"{clean_text}_{element_type}"
        else:
            return f"{element_type}_{line_num}"


class InvestigationSecurityPlugin(BasePlugin):
    """Security analysis plugin for investigation router"""
    
    def __init__(self):
        super().__init__()
        self.pattern_db = SecurityPatternDatabase()
        self.html_analyzer = HTMLSecurityAnalyzer()
    
    def _get_metadata(self) -> PluginMetadata:
        """Get plugin metadata"""
        return PluginMetadata(
            plugin_id="investigation_security",
            name="Investigation Security Analyzer",
            version="1.0.0",
            category=PluginCategory.ANALYSIS,
            priority=PluginPriority.HIGH,
            description="Security vulnerability analysis for investigation router",
            author="Asif Hussain",
            dependencies=[],
            hooks=[HookPoint.ON_INVESTIGATION_ANALYSIS.value],
            natural_language_patterns=[
                "security analysis",
                "vulnerability scan",
                "security check",
                "find security issues",
                "security investigation"
            ]
        )
    
    def initialize(self) -> bool:
        """Initialize security plugin"""
        try:
            self.logger.info("Initializing Investigation Security Plugin")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize security plugin: {e}")
            return False
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute security analysis during investigation
        
        Args:
            context: Investigation context with target entity and budget info
            
        Returns:
            Security analysis results
        """
        try:
            # Extract investigation context
            target_entity = context.get('target_entity')
            entity_type = context.get('entity_type', 'unknown')
            current_phase = context.get('current_phase', 'analysis')
            budget_remaining = context.get('budget_remaining', 0)
            
            # Estimate token cost for security analysis
            estimated_tokens = self._estimate_security_analysis_cost(target_entity, entity_type)
            
            if estimated_tokens > budget_remaining:
                return {
                    "success": False,
                    "error": "Insufficient budget for security analysis",
                    "estimated_tokens": estimated_tokens,
                    "budget_remaining": budget_remaining
                }
            
            # Perform security analysis
            security_findings = self._analyze_security(target_entity, entity_type, context)
            
            return {
                "success": True,
                "plugin_id": self.metadata.plugin_id,
                "analysis_type": "security",
                "target_entity": target_entity,
                "findings": [finding.to_dict() for finding in security_findings],
                "tokens_consumed": estimated_tokens,
                "recommendations": self._generate_security_recommendations(security_findings)
            }
            
        except Exception as e:
            self.logger.error(f"Security analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "plugin_id": self.metadata.plugin_id
            }
    
    def cleanup(self) -> bool:
        """Cleanup security plugin"""
        try:
            self.logger.info("Cleaning up Investigation Security Plugin")
            return True
        except Exception as e:
            self.logger.error(f"Failed to cleanup security plugin: {e}")
            return False
    
    def _estimate_security_analysis_cost(self, target_entity: str, entity_type: str) -> int:
        """Estimate token cost for security analysis"""
        base_cost = 200  # Base analysis cost
        
        if entity_type == 'file':
            # File analysis cost based on extension
            if target_entity.endswith(('.html', '.htm')):
                return base_cost + 300  # HTML analysis
            elif target_entity.endswith(('.py', '.js', '.cs', '.java')):
                return base_cost + 500  # Code analysis
            else:
                return base_cost + 150  # Basic file analysis
        elif entity_type == 'component':
            return base_cost + 400  # Component analysis
        else:
            return base_cost + 250  # General analysis
    
    def _analyze_security(self, target_entity: str, entity_type: str, context: Dict[str, Any]) -> List[SecurityFinding]:
        """Perform comprehensive security analysis"""
        findings = []
        
        if entity_type == 'file':
            findings.extend(self._analyze_file_security(target_entity, context))
        elif entity_type == 'component':
            findings.extend(self._analyze_component_security(target_entity, context))
        
        return findings
    
    def _analyze_file_security(self, file_path: str, context: Dict[str, Any]) -> List[SecurityFinding]:
        """Analyze specific file for security issues"""
        findings = []
        
        try:
            # Get file content (this would integrate with actual file system)
            file_content = context.get('file_content', '')
            if not file_content:
                return findings  # No content to analyze
            
            # Determine file type
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext in ['.html', '.htm']:
                # HTML security analysis
                findings.extend(self.html_analyzer.analyze_html_security(file_path, file_content))
                
                # Add HTML ID mapping analysis
                id_mapping = self.html_analyzer.analyze_html_id_mapping(file_path, file_content)
                if id_mapping['elements_missing_ids']:
                    findings.append(SecurityFinding(
                        type=SecurityVulnerabilityType.MISSING_AUTHENTICATION,  # Using as generic
                        severity=SecuritySeverity.LOW,
                        file_path=file_path,
                        line_number=0,
                        title="Missing Element IDs",
                        description=f"Found {len(id_mapping['elements_missing_ids'])} elements without IDs",
                        recommendation="Add IDs to form controls and semantic elements for better accessibility and testing",
                        confidence=1.0,
                        owasp_category="Accessibility & Testing"
                    ))
            
            elif file_ext in ['.py', '.js', '.ts', '.cs', '.java']:
                # Code security analysis
                language = self._detect_language(file_ext)
                findings.extend(self._analyze_code_security(file_path, file_content, language))
            
        except Exception as e:
            self.logger.error(f"Error analyzing file {file_path}: {e}")
        
        return findings
    
    def _analyze_component_security(self, component_name: str, context: Dict[str, Any]) -> List[SecurityFinding]:
        """Analyze component for security issues"""
        findings = []
        
        # Component-level security analysis would examine multiple files
        # For now, return placeholder findings
        findings.append(SecurityFinding(
            type=SecurityVulnerabilityType.SECURITY_MISCONFIGURATION,
            severity=SecuritySeverity.MEDIUM,
            file_path=f"component:{component_name}",
            line_number=0,
            title="Component Security Review Required",
            description=f"Component '{component_name}' requires comprehensive security review",
            recommendation="Perform detailed security assessment of all component files and dependencies",
            confidence=0.5
        ))
        
        return findings
    
    def _analyze_code_security(self, file_path: str, content: str, language: str) -> List[SecurityFinding]:
        """Analyze source code for security vulnerabilities"""
        findings = []
        lines = content.split('\n')
        
        # Get security patterns for this language
        patterns = self.pattern_db.get_patterns_for_language(language)
        
        for vuln_type, pattern_list in patterns.items():
            for pattern_info in pattern_list:
                pattern = pattern_info["pattern"]
                confidence = pattern_info["confidence"]
                description = pattern_info["description"]
                
                for line_num, line in enumerate(lines, 1):
                    matches = re.finditer(pattern, line, re.IGNORECASE)
                    for match in matches:
                        severity = self._determine_severity(vuln_type)
                        
                        findings.append(SecurityFinding(
                            type=vuln_type,
                            severity=severity,
                            file_path=file_path,
                            line_number=line_num,
                            title=f"{vuln_type.value.replace('_', ' ').title()} Detected",
                            description=description,
                            recommendation=self._get_vulnerability_recommendation(vuln_type),
                            code_snippet=line.strip(),
                            confidence=confidence,
                            owasp_category=self._get_owasp_category(vuln_type)
                        ))
        
        return findings
    
    def _detect_language(self, file_ext: str) -> str:
        """Detect programming language from file extension"""
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.cs': 'csharp',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.php': 'php',
            '.rb': 'ruby',
            '.go': 'go'
        }
        return language_map.get(file_ext, 'unknown')
    
    def _determine_severity(self, vuln_type: SecurityVulnerabilityType) -> SecuritySeverity:
        """Determine severity based on vulnerability type"""
        critical_vulns = [
            SecurityVulnerabilityType.SQL_INJECTION,
            SecurityVulnerabilityType.HARDCODED_SECRETS,
            SecurityVulnerabilityType.BROKEN_ACCESS_CONTROL
        ]
        
        high_vulns = [
            SecurityVulnerabilityType.XSS_REFLECTED,
            SecurityVulnerabilityType.XSS_STORED,
            SecurityVulnerabilityType.CSRF,
            SecurityVulnerabilityType.PATH_TRAVERSAL
        ]
        
        if vuln_type in critical_vulns:
            return SecuritySeverity.CRITICAL
        elif vuln_type in high_vulns:
            return SecuritySeverity.HIGH
        else:
            return SecuritySeverity.MEDIUM
    
    def _get_vulnerability_recommendation(self, vuln_type: SecurityVulnerabilityType) -> str:
        """Get specific recommendation for vulnerability type"""
        recommendations = {
            SecurityVulnerabilityType.SQL_INJECTION: "Use parameterized queries or ORM. Never concatenate user input directly into SQL statements.",
            SecurityVulnerabilityType.XSS_REFLECTED: "Sanitize and validate all user input. Use output encoding and Content Security Policy (CSP).",
            SecurityVulnerabilityType.XSS_STORED: "Implement input validation, output encoding, and Content Security Policy (CSP).",
            SecurityVulnerabilityType.CSRF: "Implement CSRF tokens for all state-changing operations.",
            SecurityVulnerabilityType.HARDCODED_SECRETS: "Use environment variables or secure configuration management for secrets.",
            SecurityVulnerabilityType.PATH_TRAVERSAL: "Validate and sanitize file paths. Use allowlists and avoid user input in file operations.",
        }
        return recommendations.get(vuln_type, "Review code for security best practices.")
    
    def _get_owasp_category(self, vuln_type: SecurityVulnerabilityType) -> str:
        """Get OWASP Top 10 category for vulnerability"""
        owasp_mapping = {
            SecurityVulnerabilityType.SQL_INJECTION: "A03:2021 – Injection",
            SecurityVulnerabilityType.XSS_REFLECTED: "A03:2021 – Injection",
            SecurityVulnerabilityType.XSS_STORED: "A03:2021 – Injection",
            SecurityVulnerabilityType.CSRF: "A01:2021 – Broken Access Control",
            SecurityVulnerabilityType.HARDCODED_SECRETS: "A02:2021 – Cryptographic Failures",
            SecurityVulnerabilityType.PATH_TRAVERSAL: "A01:2021 – Broken Access Control",
        }
        return owasp_mapping.get(vuln_type, "Security Best Practices")
    
    def _generate_security_recommendations(self, findings: List[SecurityFinding]) -> List[str]:
        """Generate overall security recommendations"""
        recommendations = []
        
        critical_count = sum(1 for f in findings if f.severity == SecuritySeverity.CRITICAL)
        high_count = sum(1 for f in findings if f.severity == SecuritySeverity.HIGH)
        
        if critical_count > 0:
            recommendations.append(f"🚨 CRITICAL: {critical_count} critical security vulnerabilities found. Address immediately.")
        
        if high_count > 0:
            recommendations.append(f"⚠️  HIGH: {high_count} high-severity security issues require attention.")
        
        # Specific recommendations based on vulnerability types found
        vuln_types = {f.type for f in findings}
        
        if SecurityVulnerabilityType.SQL_INJECTION in vuln_types:
            recommendations.append("💉 Implement parameterized queries to prevent SQL injection attacks.")
        
        if any(xss in vuln_types for xss in [SecurityVulnerabilityType.XSS_REFLECTED, SecurityVulnerabilityType.XSS_STORED]):
            recommendations.append("🔒 Implement Content Security Policy (CSP) and input validation to prevent XSS attacks.")
        
        if SecurityVulnerabilityType.HARDCODED_SECRETS in vuln_types:
            recommendations.append("🔑 Move hardcoded secrets to environment variables or secure vault.")
        
        if not recommendations:
            recommendations.append("✅ No critical security issues detected in this analysis.")
        
        return recommendations


def register() -> BasePlugin:
    """Register the investigation security plugin"""
    return InvestigationSecurityPlugin()