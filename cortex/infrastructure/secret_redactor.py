"""
Secret Redactor - Sensitive Data Masking

Production-grade secret redaction with:
- Pattern-based secret detection (API keys, passwords, tokens)
- Configurable redaction patterns
- Non-destructive masking (preserves data structure)
- Performance-optimized regex compilation
- Audit trail integration

Satisfies: NFR-003 - Security - Secret Redaction

Author: Asif Hussain
"""

import json
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Pattern, Set

from cortex.brain.core.result import Err, Ok, Result


@dataclass
class RedactionRule:
    """Pattern for detecting and redacting secrets."""
    
    id: str
    pattern: str
    description: str
    replacement: str = "***REDACTED***"
    enabled: bool = True
    
    def get_compiled_pattern(self) -> Pattern[str]:
        """Get compiled regex pattern."""
        return re.compile(self.pattern, re.IGNORECASE | re.MULTILINE)


class SecretRedactor:
    """
    Redact sensitive information from logs and data.
    
    Patterns include:
    - API keys (AWS, Azure, GCP)
    - Bearer tokens
    - JWT tokens
    - Password fields
    - SSH keys
    - Database connection strings
    - Credit card numbers
    """
    
    # Standard redaction rules
    DEFAULT_RULES: List[RedactionRule] = [
        RedactionRule(
            id="api_key_aws",
            pattern=r'(?Union[aws_access_key_id, AKIA][0-9A-Z]{16})',
            description="AWS Access Key ID",
        ),
        RedactionRule(
            id="api_key_azure",
            pattern=r'(?Union[azure_key, access_key])[\s]*[:=][\s]*[a-zA-Z0-9+/]{20,}',
            description="Azure Access Key",
        ),
        RedactionRule(
            id="bearer_token",
            pattern=r'(?Union[Authorization, authorization])[\s]*[:=][\s]*Bearer\s+[a-zA-Z0-9\-._~+/]+=*',
            description="Bearer Token",
        ),
        RedactionRule(
            id="jwt_token",
            pattern=r'eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+',
            description="JWT Token",
        ),
        RedactionRule(
            id="password_field",
            pattern=r'(?Union[password, passwd]|pwd)[\s]*[:=][\s]*[^\s\n,}]+',
            description="Password Field",
        ),
        RedactionRule(
            id="connection_string",
            pattern=r'(?:connection.?string|connection)[\s]*[:=][\s]*.*(?Union[password, pwd])=([^\s;]+)',
            description="Database Connection String",
        ),
        RedactionRule(
            id="private_key",
            pattern=r'-----BEGIN (?Union[RSA, EC] |DSA )?PRIVATE KEY-----[\s\S]+?-----END (?Union[RSA, EC] |DSA )?PRIVATE KEY-----',
            description="Private Key",
        ),
        RedactionRule(
            id="api_key_generic",
            pattern=r'(?:api[_-]?key|apikey)[\s]*[:=][\s]*[a-zA-Z0-9\-._~+/]{20,}',
            description="Generic API Key",
        ),
        RedactionRule(
            id="credit_card",
            pattern=r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
            description="Credit Card Number",
        ),
        RedactionRule(
            id="github_token",
            pattern=r'(?Union[github, gh])_[a-zA-Z0-9_]{36,}',
            description="GitHub Token",
        ),
    ]
    
    def __init__(self, custom_rules: Optional[List[RedactionRule]] = None):
        """
        Initialize redactor with standard or custom rules.
        
        Args:
            custom_rules: Optional list of custom redaction rules
        """
        self.rules = custom_rules if custom_rules is not None else self.DEFAULT_RULES
        self._compiled_rules: Dict[str, Pattern[str]] = {}
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Pre-compile all regex patterns for performance."""
        for rule in self.rules:
            if rule.enabled:
                self._compiled_rules[rule.id] = rule.get_compiled_pattern()
    
    def redact_string(self, text: str) -> str:
        """
        Redact secrets from a string.
        
        Args:
            text: Input text to redact
            
        Returns:
            Text with secrets redacted
        """
        if not text:
            return text
        
        result = text
        for rule in self.rules:
            if not rule.enabled:
                continue
            
            pattern = self._compiled_rules.get(rule.id)
            if pattern:
                result = pattern.sub(rule.replacement, result)
        
        return result
    
    def redact_dict(self, data: Dict[str, Any], keys_to_redact: Optional[Set[str]] = None) -> Dict[str, Any]:
        """
        Redact secrets from dictionary values.
        
        Args:
            data: Dictionary to redact
            keys_to_redact: Optional set of keys to check (if None, checks all)
            
        Returns:
            Dictionary with redacted values
        """
        if not data:
            return data
        
        result = {}
        sensitive_keys = keys_to_redact or {
            'password', 'passwd', 'pwd', 'secret', 'token', 'key',
            'api_key', 'apikey', 'access_token', 'authorization',
            'connection_string', 'private_key'
        }
        
        for key, value in data.items():
            if isinstance(value, dict):
                result[key] = self.redact_dict(value, keys_to_redact)
            elif isinstance(value, list):
                result[key] = [
                    self.redact_dict(item, keys_to_redact) if isinstance(item, dict)
                    else "***REDACTED***" if key.lower() in sensitive_keys
                    else self.redact_string(str(item))
                    for item in value
                ]
            elif isinstance(value, str):
                # Redact by key name for sensitive keys, always redact patterns
                if key.lower() in sensitive_keys:
                    result[key] = "***REDACTED***"
                else:
                    result[key] = self.redact_string(value)
            else:
                result[key] = value
        
        return result
    
    def redact_json(self, json_str: str) -> str:
        """
        Redact secrets from JSON string.
        
        Args:
            json_str: JSON string to redact
            
        Returns:
            Result with redacted JSON or error
        """
        try:
            data = json.loads(json_str)
            redacted = self.redact_dict(data)
            return Ok(json.dumps(redacted))
        except json.JSONDecodeError as e:
            return Err(f"Invalid JSON: {e}")
        except Exception as e:
            return Err(f"Redaction error: {e}")
    
    def _is_likely_secret(self, value: str) -> bool:
        """
        Check if a value matches any redaction pattern.
        
        Args:
            value: Value to check
            
        Returns:
            True if value matches a pattern
        """
        for pattern in self._compiled_rules.values():
            if pattern.search(value):
                return True
        return False
    
    def get_redaction_report(self, text: str) -> Dict[str, Any]:
        """
        Generate report of secrets found in text (without revealing them).
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with findings
        """
        findings = {
            'secrets_found': 0,
            'rules_matched': {},
            'total_matches': 0,
        }
        
        for rule in self.rules:
            if not rule.enabled:
                continue
            
            pattern = self._compiled_rules.get(rule.id)
            if pattern:
                matches = pattern.findall(text)
                if matches:
                    findings['secrets_found'] += len(matches)
                    findings['rules_matched'][rule.id] = {
                        'description': rule.description,
                        'match_count': len(matches),
                    }
                    findings['total_matches'] += len(matches)
        
        return findings
