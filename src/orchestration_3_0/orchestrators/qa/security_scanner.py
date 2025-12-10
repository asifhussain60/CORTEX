"""
Security Scanner - CORTEX 4.0

OWASP Top 10 vulnerability scanning

Author: Asif Hussain
Date: December 10, 2025
"""

from typing import List, Dict, Any
from pathlib import Path
import re
import logging

logger = logging.getLogger(__name__)


class SecurityScanner:
    """
    Security vulnerability scanner focusing on OWASP Top 10.
    """
    
    def __init__(self):
        """Initialize security scanner."""
        self.vulnerability_patterns = self._load_vulnerability_patterns()
        logger.info("SecurityScanner initialized with OWASP Top 10 patterns")
    
    def _load_vulnerability_patterns(self) -> List[Dict[str, Any]]:
        """Load OWASP Top 10 vulnerability patterns."""
        return [
            # A01:2021 - Broken Access Control
            {
                'name': 'missing_auth_check',
                'pattern': r'@app\.route|@router\.(get|post|put|delete)',
                'severity': 'HIGH',
                'category': 'A01:Broken Access Control',
                'message': 'Endpoint may be missing authentication check'
            },
            
            # A02:2021 - Cryptographic Failures
            {
                'name': 'weak_hash',
                'pattern': r'hashlib\.(md5|sha1)\(',
                'severity': 'HIGH',
                'category': 'A02:Cryptographic Failures',
                'message': 'Weak cryptographic hash (MD5/SHA1)'
            },
            {
                'name': 'hardcoded_secret',
                'pattern': r'(secret_key|api_key|password)\s*=\s*["\'][^"\']+["\']',
                'severity': 'CRITICAL',
                'category': 'A02:Cryptographic Failures',
                'message': 'Hardcoded secret/credential'
            },
            
            # A03:2021 - Injection
            {
                'name': 'sql_injection',
                'pattern': r'(execute|cursor\.execute|raw\()\s*\(\s*["\'].*%s.*["\']',
                'severity': 'CRITICAL',
                'category': 'A03:Injection',
                'message': 'Potential SQL injection vulnerability'
            },
            {
                'name': 'command_injection',
                'pattern': r'(os\.system|subprocess\.call|subprocess\.run|eval|exec)\s*\(',
                'severity': 'HIGH',
                'category': 'A03:Injection',
                'message': 'Potential command injection vulnerability'
            },
            
            # A04:2021 - Insecure Design
            {
                'name': 'debug_enabled',
                'pattern': r'debug\s*=\s*True',
                'severity': 'HIGH',
                'category': 'A04:Insecure Design',
                'message': 'Debug mode enabled (should be False in production)'
            },
            
            # A05:2021 - Security Misconfiguration
            {
                'name': 'insecure_ssl',
                'pattern': r'verify\s*=\s*False',
                'severity': 'HIGH',
                'category': 'A05:Security Misconfiguration',
                'message': 'SSL verification disabled'
            },
            
            # A07:2021 - Identification and Authentication Failures
            {
                'name': 'weak_password_policy',
                'pattern': r'password.*length.*<\s*[1-7]',
                'severity': 'HIGH',
                'category': 'A07:Authentication Failures',
                'message': 'Weak password policy (min length < 8)'
            },
            
            # A08:2021 - Software and Data Integrity Failures
            {
                'name': 'unsafe_deserialization',
                'pattern': r'pickle\.loads?|yaml\.load\(',
                'severity': 'CRITICAL',
                'category': 'A08:Data Integrity Failures',
                'message': 'Unsafe deserialization (use pickle.loads with caution)'
            },
            
            # A09:2021 - Security Logging Failures
            {
                'name': 'missing_error_logging',
                'pattern': r'except.*:\s*pass',
                'severity': 'WARNING',
                'category': 'A09:Logging Failures',
                'message': 'Exception caught but not logged'
            },
            
            # A10:2021 - Server-Side Request Forgery
            {
                'name': 'ssrf_vulnerability',
                'pattern': r'requests\.(get|post|put|delete)\s*\(\s*[^)]*\+',
                'severity': 'HIGH',
                'category': 'A10:SSRF',
                'message': 'Potential SSRF vulnerability (user-controlled URL)'
            }
        ]
    
    def scan_for_vulnerabilities(
        self,
        files: List[str],
        project_path: str = '.'
    ) -> Dict[str, Any]:
        """
        Scan files for security vulnerabilities.
        
        Args:
            files: File paths to scan
            project_path: Project root path
            
        Returns:
            Scan results with vulnerabilities
        """
        issues = []
        
        for file_path in files:
            full_path = Path(project_path) / file_path
            
            if not full_path.exists():
                logger.warning(f"File not found: {full_path}")
                continue
            
            if not full_path.suffix == '.py':
                logger.debug(f"Skipping non-Python file: {full_path}")
                continue
            
            file_issues = self._scan_file(full_path)
            issues.extend(file_issues)
        
        # Group by severity
        critical = [i for i in issues if i['severity'] == 'CRITICAL']
        high = [i for i in issues if i['severity'] == 'HIGH']
        warning = [i for i in issues if i['severity'] == 'WARNING']
        
        return {
            'issues': issues,
            'summary': {
                'critical': len(critical),
                'high': len(high),
                'warning': len(warning),
                'total': len(issues)
            },
            'files_scanned': len(files)
        }
    
    def _scan_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Scan single file for vulnerabilities."""
        issues = []
        
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.splitlines()
            
            for i, line in enumerate(lines, 1):
                for pattern_def in self.vulnerability_patterns:
                    if re.search(pattern_def['pattern'], line, re.IGNORECASE):
                        issues.append({
                            'file': str(file_path),
                            'line': i,
                            'severity': pattern_def['severity'],
                            'category': pattern_def['category'],
                            'vulnerability': pattern_def['name'],
                            'message': pattern_def['message'],
                            'code_snippet': line.strip()
                        })
        
        except Exception as e:
            logger.error(f"Error scanning {file_path}: {e}")
            issues.append({
                'file': str(file_path),
                'line': 0,
                'severity': 'ERROR',
                'message': f"Scan failed: {e}"
            })
        
        return issues
