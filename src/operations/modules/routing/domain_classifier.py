"""
Domain Classifier - Adaptive analysis depth based on domain criticality.

Purpose:
    Classifies code domains into CRITICAL, STANDARD, or SIMPLE tiers to adapt
    analysis depth: security/auth/financial → deep AST, UI → high-level, docs → surface.

Features:
    - 3-tier domain classification: CRITICAL, STANDARD, SIMPLE
    - Pattern-based domain detection (security, compliance, business logic)
    - Analysis depth routing: CRITICAL→deep AST, STANDARD→moderate, SIMPLE→light
    - Integration with ComplexityAnalyzer for risk scoring
    - OWASP Top 10 pattern library for security domain detection

Author: Asif Hussain
Date: December 2024
Version: 1.0.0
Phase: 02 of CORTEX Evolution v3.9
"""

import re
import logging
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Set
from pathlib import Path

logger = logging.getLogger(__name__)


class DomainCriticality(Enum):
    """Domain criticality tiers for analysis depth routing"""
    CRITICAL = "CRITICAL"   # Deep AST: security, auth, payments, compliance, business logic
    STANDARD = "STANDARD"   # High-level: UI components, utilities, helpers
    SIMPLE = "SIMPLE"       # Surface: documentation, configuration, scaffolding


@dataclass
class DomainClassification:
    """Result of domain classification"""
    criticality: DomainCriticality      # Classification tier
    domains: List[str]                   # Detected domains
    confidence: float                    # 0.0-1.0 classification confidence
    analysis_depth: str                  # 'deep', 'moderate', 'light'
    rationale: List[str]                 # Explanation of classification
    security_patterns: List[str]         # Security patterns detected (OWASP Top 10)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            "criticality": self.criticality.value,
            "domains": self.domains,
            "confidence": self.confidence,
            "analysis_depth": self.analysis_depth,
            "rationale": self.rationale,
            "security_patterns": self.security_patterns
        }


class DomainClassifier:
    """
    Classifies code domains for adaptive analysis depth.
    
    Domain Tiers:
        CRITICAL (deep AST analysis):
            - Security: authentication, authorization, encryption, input validation
            - Compliance: PII handling, GDPR, HIPAA, PCI, audit trails
            - Financial: payment processing, calculations, rounding, transactions
            - Business Logic: core workflows, state machines, business rules
        
        STANDARD (high-level analysis):
            - UI Components: React/Vue/Angular components, templates
            - Utilities: helpers, formatters, converters
            - API Clients: HTTP clients, SDK wrappers
            - Middleware: logging, caching, error handling
        
        SIMPLE (surface-level analysis):
            - Documentation: READMEs, guides, comments
            - Configuration: JSON/YAML configs, env files
            - Scaffolding: boilerplate, templates
            - Test fixtures: mock data, test constants
    
    Security Pattern Library (OWASP Top 10):
        - A01:2021 - Broken Access Control
        - A02:2021 - Cryptographic Failures
        - A03:2021 - Injection (SQL, XSS, Command)
        - A04:2021 - Insecure Design
        - A05:2021 - Security Misconfiguration
        - A06:2021 - Vulnerable Components
        - A07:2021 - Authentication Failures
        - A08:2021 - Software/Data Integrity
        - A09:2021 - Security Logging Failures
        - A10:2021 - Server-Side Request Forgery
    
    Integration:
        - Called by ComplexityAnalyzer to boost risk scores
        - Used by AST Engine to determine analysis depth
        - Influences router tier classification (CRITICAL → Tier 4)
    """
    
    # CRITICAL domain patterns (require deep AST analysis)
    CRITICAL_PATTERNS = {
        'security_auth': [
            r'auth(entication|orization|orize)?',
            r'login|logout|signin|signout',
            r'password|credential|secret|api[_-]?key',
            r'token|jwt|session|cookie',
            r'oauth|saml|sso|openid',
            r'mfa|2fa|two[_-]?factor',
            r'rbac|acl|permission|role',
            r'access[_-]?control'
        ],
        'security_crypto': [
            r'encrypt|decrypt|cipher',
            r'hash|sha\d+|md5|bcrypt',
            r'sign(ature)?|verify',
            r'tls|ssl|https',
            r'certificate|pki|keypair',
            r'aes|rsa|ecdsa'
        ],
        'security_injection': [
            r'sql\s+(query|injection|prepare)',
            r'xss|cross[_-]?site',
            r'csrf|cross[_-]?site[_-]?request',
            r'command[_-]?injection',
            r'ldap[_-]?injection',
            r'xml[_-]?injection',
            r'sanitize|escape|validate[_-]?input'
        ],
        'compliance_privacy': [
            r'pii|personal[_-]?identif',
            r'gdpr|ccpa|hipaa|pci[_-]?dss',
            r'data[_-]?subject|right[_-]?to[_-]?erasure',
            r'consent|opt[_-]?in|privacy',
            r'data[_-]?retention|anonymiz',
            r'audit[_-]?trail|audit[_-]?log'
        ],
        'financial_operations': [
            r'payment|transaction|billing',
            r'invoice|charge|refund',
            r'balance|account|ledger',
            r'financial|monetary|currency',
            r'tax|vat|gst',
            r'rounding|decimal|precision',
            r'stripe|paypal|checkout'
        ],
        'business_logic': [
            r'workflow|state[_-]?machine',
            r'business[_-]?rule|business[_-]?logic',
            r'validation[_-]?rule|constraint',
            r'eligibility|qualification',
            r'approval|review[_-]?process',
            r'calculation|formula|algorithm'
        ]
    }
    
    # STANDARD domain patterns (high-level analysis)
    STANDARD_PATTERNS = {
        'ui_components': [
            r'component|widget|control',
            r'react|vue|angular|svelte',
            r'jsx|tsx|template',
            r'button|input|form|modal',
            r'layout|grid|flex',
            r'chart|graph|visualization'
        ],
        'utilities': [
            r'util(ity|ities)?|helper',
            r'formatter|parser|converter',
            r'validator|checker',
            r'string[_-]?util|array[_-]?util',
            r'date[_-]?util|time[_-]?util'
        ],
        'api_clients': [
            r'api[_-]?client|http[_-]?client',
            r'rest[_-]?client|graphql[_-]?client',
            r'sdk|wrapper',
            r'fetch|axios|request'
        ],
        'middleware': [
            r'middleware|interceptor',
            r'logging|logger',
            r'caching|cache',
            r'error[_-]?handler|exception'
        ]
    }
    
    # SIMPLE domain patterns (surface-level validation)
    SIMPLE_PATTERNS = {
        'documentation': [
            r'readme|documentation|doc',
            r'guide|tutorial|example',
            r'comment|docstring',
            r'changelog|release[_-]?notes'
        ],
        'configuration': [
            r'config(uration)?|settings',
            r'\.json$|\.yaml$|\.yml$|\.toml$',
            r'env(ironment)?|\.env',
            r'constant|variable'
        ],
        'scaffolding': [
            r'boilerplate|template|scaffold',
            r'generator|creator',
            r'init(ialize)?|setup'
        ],
        'test_fixtures': [
            r'mock|stub|fake',
            r'fixture|factory',
            r'test[_-]?data|sample[_-]?data'
        ]
    }
    
    # OWASP Top 10:2021 Security Patterns
    OWASP_PATTERNS = {
        'A01_broken_access_control': [
            r'authorization|access[_-]?control',
            r'rbac|acl|permission',
            r'bypass|escalat(e|ion)',
            r'insecure[_-]?direct[_-]?object'
        ],
        'A02_cryptographic_failures': [
            r'weak[_-]?crypto|weak[_-]?cipher',
            r'hard[_-]?coded[_-]?(key|secret)',
            r'plain[_-]?text',
            r'md5|sha1',  # Weak hashing
            r'ssl\s*v[23]|tls\s*1\.[01]',  # Weak protocols
            r'hardcoded.*?(key|secret|password)',
            r'encryption\s+key'
        ],
        'A03_injection': [
            r'sql[_-]?injection|sqli',
            r'xss|cross[_-]?site[_-]?scripting',
            r'command[_-]?injection|shell[_-]?exec',
            r'ldap[_-]?injection|xml[_-]?injection',
            r'sanitize.*?(sql|query)',
            r'prevent\s+(injection|sql|xss)'
        ],
        'A07_authentication_failures': [
            r'brute[_-]?force|credential[_-]?stuffing',
            r'session[_-]?fixation|session[_-]?hijack',
            r'weak[_-]?password|default[_-]?credential',
            r'authentication[_-]?bypass',
            r'(brute|force).*?(attack|login)'
        ],
        'A08_data_integrity': [
            r'unsigned[_-]?(url|jwt)',
            r'insecure[_-]?deserialization',
            r'tampering|integrity[_-]?check',
            r'code[_-]?injection|remote[_-]?code',
            r'validate.*?unsigned',
            r'jwt.*?token'
        ],
        'A09_logging_failures': [
            r'missing[_-]?audit|no[_-]?logging',
            r'log[_-]?injection',
            r'sensitive[_-]?data[_-]?log',
            r'insufficient[_-]?monitoring',
            r'audit.*?log(ging)?'
        ],
        'A10_ssrf': [
            r'ssrf|server[_-]?side[_-]?request',
            r'url[_-]?fetch|remote[_-]?resource',
            r'redirect|forward'
        ]
    }
    
    def __init__(self):
        """Initialize domain classifier"""
        self.classification_cache: Dict[str, DomainClassification] = {}
        logger.info("🎭 DomainClassifier initialized: 3-tier classification (CRITICAL/STANDARD/SIMPLE)")
    
    def classify(
        self,
        user_request: str,
        file_paths: Optional[List[str]] = None,
        codebase_context: Optional[Dict] = None
    ) -> DomainClassification:
        """
        Classify domain criticality for adaptive analysis depth.
        
        Args:
            user_request: User's feature request or task description
            file_paths: Optional list of file paths being analyzed
            codebase_context: Optional codebase analysis from AST
        
        Returns:
            DomainClassification with criticality tier and analysis depth
        
        Example:
            >>> classifier = DomainClassifier()
            >>> result = classifier.classify("Add JWT authentication to API")
            >>> print(result.criticality)  # CRITICAL
            >>> print(result.analysis_depth)  # 'deep'
            >>> print(result.security_patterns)  # ['A07_authentication_failures']
        """
        logger.info(f"Classifying domain for: {user_request[:100]}...")
        
        # Detect security patterns first (OWASP Top 10) - always check
        security_patterns = self._detect_security_patterns(user_request)
        
        # Detect CRITICAL domains
        critical_domains, critical_confidence = self._detect_critical_domains(
            user_request, file_paths
        )
        
        # If CRITICAL domains or security patterns detected, classify as CRITICAL
        if critical_domains or security_patterns:
            rationale = []
            if critical_domains:
                rationale.append(f"CRITICAL domains detected: {', '.join(critical_domains)}")
            if security_patterns:
                rationale.append(f"Security patterns: {', '.join(security_patterns)}")
            
            return DomainClassification(
                criticality=DomainCriticality.CRITICAL,
                domains=critical_domains,
                confidence=critical_confidence,
                analysis_depth='deep',
                rationale=rationale,
                security_patterns=security_patterns
            )
        
        # Detect STANDARD domains
        standard_domains, standard_confidence = self._detect_standard_domains(
            user_request, file_paths
        )
        
        if standard_domains:
            return DomainClassification(
                criticality=DomainCriticality.STANDARD,
                domains=standard_domains,
                confidence=standard_confidence,
                analysis_depth='moderate',
                rationale=[f"STANDARD domains detected: {', '.join(standard_domains)}"],
                security_patterns=[]
            )
        
        # Detect SIMPLE domains
        simple_domains, simple_confidence = self._detect_simple_domains(
            user_request, file_paths
        )
        
        if simple_domains:
            return DomainClassification(
                criticality=DomainCriticality.SIMPLE,
                domains=simple_domains,
                confidence=simple_confidence,
                analysis_depth='light',
                rationale=[f"SIMPLE domains detected: {', '.join(simple_domains)}"],
                security_patterns=[]
            )
        
        # Default: STANDARD tier (moderate analysis)
        return DomainClassification(
            criticality=DomainCriticality.STANDARD,
            domains=['general'],
            confidence=0.5,
            analysis_depth='moderate',
            rationale=['No specific domain patterns detected - defaulting to STANDARD'],
            security_patterns=[]
        )
    
    def _detect_critical_domains(
        self, 
        text: str, 
        file_paths: Optional[List[str]]
    ) -> tuple[List[str], float]:
        """Detect CRITICAL domain patterns"""
        text_lower = text.lower()
        detected = set()  # Use set to avoid duplicates
        
        for domain_type, patterns in self.CRITICAL_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    detected.add(domain_type)
                    break  # Move to next domain_type once found
        
        # Check file paths for CRITICAL indicators
        if file_paths:
            for path in file_paths:
                path_lower = path.lower()
                if any(keyword in path_lower for keyword in [
                    'auth', 'security', 'payment', 'billing', 'compliance',
                    'encryption', 'financial', 'audit', 'business_logic'
                ]):
                    detected.add('critical_file_path')
                    break
        
        confidence = min(1.0, len(detected) * 0.3)
        return list(detected), confidence
    
    def _detect_standard_domains(
        self, 
        text: str, 
        file_paths: Optional[List[str]]
    ) -> tuple[List[str], float]:
        """Detect STANDARD domain patterns"""
        text_lower = text.lower()
        detected = []
        
        for domain_type, patterns in self.STANDARD_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    detected.append(domain_type)
                    break
        
        confidence = min(1.0, len(detected) * 0.3)
        return list(set(detected)), confidence
    
    def _detect_simple_domains(
        self, 
        text: str, 
        file_paths: Optional[List[str]]
    ) -> tuple[List[str], float]:
        """Detect SIMPLE domain patterns"""
        text_lower = text.lower()
        detected = []
        
        for domain_type, patterns in self.SIMPLE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    detected.append(domain_type)
                    break
        
        # Check file extensions for documentation/config
        if file_paths:
            for path in file_paths:
                path_lower = path.lower()
                if any(path_lower.endswith(ext) for ext in [
                    '.md', '.txt', '.json', '.yaml', '.yml', '.toml', '.env'
                ]):
                    detected.append('simple_file_type')
                    break
        
        confidence = min(1.0, len(detected) * 0.3)
        return list(set(detected)), confidence
    
    def _detect_security_patterns(self, text: str) -> List[str]:
        """Detect OWASP Top 10 security patterns"""
        text_lower = text.lower()
        detected = []
        
        for owasp_category, patterns in self.OWASP_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    detected.append(owasp_category)
                    logger.warning(f"🔒 Security pattern detected: {owasp_category}")
                    break
        
        return list(set(detected))
    
    def get_analysis_depth_config(
        self, 
        classification: DomainClassification
    ) -> Dict[str, any]:
        """
        Get analysis configuration based on domain classification.
        
        Returns dict with:
            - ast_depth: 'deep', 'moderate', 'light'
            - enable_security_scan: bool
            - enable_compliance_check: bool
            - enable_business_logic_analysis: bool
        """
        if classification.criticality == DomainCriticality.CRITICAL:
            return {
                'ast_depth': 'deep',
                'enable_security_scan': True,
                'enable_compliance_check': True,
                'enable_business_logic_analysis': True,
                'scan_for_vulnerabilities': True,
                'require_peer_review': True
            }
        elif classification.criticality == DomainCriticality.STANDARD:
            return {
                'ast_depth': 'moderate',
                'enable_security_scan': False,
                'enable_compliance_check': False,
                'enable_business_logic_analysis': False,
                'scan_for_vulnerabilities': False,
                'require_peer_review': False
            }
        else:  # SIMPLE
            return {
                'ast_depth': 'light',
                'enable_security_scan': False,
                'enable_compliance_check': False,
                'enable_business_logic_analysis': False,
                'scan_for_vulnerabilities': False,
                'require_peer_review': False
            }
