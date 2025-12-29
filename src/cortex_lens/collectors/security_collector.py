"""
Security Collector - Identifies security vulnerabilities and OWASP patterns.

Features:
- OWASP Top 10 pattern detection
- Hardcoded secret scanning
- SQL injection vulnerability detection
- XSS vulnerability detection
- Command injection patterns
- Insecure crypto usage
- Optional ruff security rules integration
- CWE (Common Weakness Enumeration) mapping

Author: Asif Hussain
Date: December 2025
"""

import re
import logging
from pathlib import Path
from typing import Dict, Any, List, Set, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)


class SecurityCollector:
    """
    Analyzes codebase for security vulnerabilities and OWASP patterns.
    
    Uses regex patterns to detect common vulnerabilities:
    - Hardcoded secrets (API keys, passwords, tokens)
    - SQL injection vectors
    - XSS vulnerabilities
    - Command injection
    - Insecure cryptography
    - Path traversal
    """
    
    def __init__(self):
        """Initialize security patterns."""
        # Hardcoded secrets patterns
        self.secret_patterns = {
            'api_key': re.compile(r'(?i)(api[_-]?key|apikey)\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,})["\']'),
            'password': re.compile(r'(?i)(password|passwd|pwd)\s*[:=]\s*["\']([^"\']{8,})["\']'),
            'token': re.compile(r'(?i)(token|access[_-]?token)\s*[:=]\s*["\']([a-zA-Z0-9_\-\.]{20,})["\']'),
            'aws_key': re.compile(r'(?i)(aws[_-]?access[_-]?key[_-]?id)\s*[:=]\s*["\']([A-Z0-9]{20})["\']'),
            'private_key': re.compile(r'-----BEGIN (RSA |EC )?PRIVATE KEY-----'),
        }
        
        # SQL injection patterns
        self.sql_injection_patterns = [
            re.compile(r'execute\s*\(\s*["\'].*?\+.*?["\']'),  # Python execute with concatenation
            re.compile(r'cursor\.execute\s*\(\s*f["\']'),  # f-string in execute
            re.compile(r'SELECT.*FROM.*WHERE.*\+'),  # Direct string concatenation
            re.compile(r'query\s*=.*?\+.*?request\.(GET|POST|args|form)'),  # User input concatenation
        ]
        
        # XSS patterns
        self.xss_patterns = [
            re.compile(r'innerHTML\s*=\s*.*?(?:request|params|query)'),  # JavaScript innerHTML with user input
            re.compile(r'\.html\(.*?\$\{.*?\}\)'),  # jQuery html() with template literal
            re.compile(r'dangerouslySetInnerHTML\s*=\s*\{\{'),  # React dangerous HTML
            re.compile(r'render_template.*?\|safe'),  # Flask/Jinja2 safe filter
        ]
        
        # Command injection patterns
        self.command_injection_patterns = [
            re.compile(r'(?:os\.system|subprocess\.call|exec|eval)\s*\(\s*["\'].*?\+'),  # Command with concatenation
            re.compile(r'shell\s*=\s*True'),  # subprocess with shell=True
            re.compile(r'Process\.Start\s*\(.*?\+'),  # C# Process.Start with concatenation
        ]
        
        # Insecure crypto patterns
        self.crypto_patterns = [
            re.compile(r'MD5|SHA1(?!256)'),  # Weak hash algorithms
            re.compile(r'DES|RC4'),  # Weak encryption algorithms
            re.compile(r'Random\(\)'),  # Non-cryptographic random
            re.compile(r'Math\.random'),  # JavaScript non-crypto random
        ]
        
        # Path traversal patterns
        self.path_traversal_patterns = [
            re.compile(r'open\s*\(.*?(?:request|params)\['),  # Direct file open with user input
            re.compile(r'File\.(?:Read|Open).*?\+'),  # File operations with concatenation
            re.compile(r'\.\.\/|\.\.\\'),  # Direct path traversal sequences
        ]
        
        # CWE mapping
        self.cwe_mapping = {
            'sql_injection': 'CWE-89',
            'xss': 'CWE-79',
            'command_injection': 'CWE-78',
            'hardcoded_secret': 'CWE-798',
            'weak_crypto': 'CWE-327',
            'path_traversal': 'CWE-22',
        }
        
    def collect(self, project_path: Path) -> Dict[str, Any]:
        """
        Collect security vulnerability data from project.
        
        Args:
            project_path: Root path of project to analyze
            
        Returns:
            Dictionary with:
            - total_files_scanned: Number of files analyzed
            - vulnerabilities_found: Total vulnerability count
            - vulnerabilities_by_type: Dict[str, int] count per type
            - vulnerabilities_by_severity: Dict[str, int] count per severity
            - findings: List of vulnerability details
            - owasp_coverage: List of OWASP Top 10 categories found
            - cwe_references: List of CWE IDs found
        """
        logger.info(f"🔐 Starting security analysis on: {project_path}")
        
        results = {
            'total_files_scanned': 0,
            'vulnerabilities_found': 0,
            'vulnerabilities_by_type': defaultdict(int),
            'vulnerabilities_by_severity': defaultdict(int),
            'findings': [],
            'owasp_coverage': set(),
            'cwe_references': set(),
        }
        
        # Scan code files
        code_extensions = {'.py', '.js', '.jsx', '.ts', '.tsx', '.cs', '.java', '.php', '.rb', '.go'}
        
        for file_path in project_path.rglob('*'):
            if file_path.suffix not in code_extensions:
                continue
            if any(exclude in str(file_path) for exclude in ['node_modules', '.venv', 'venv', 'bin', 'obj']):
                continue
                
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                results['total_files_scanned'] += 1
                
                # Scan for each vulnerability type
                self._scan_hardcoded_secrets(file_path, content, results)
                self._scan_sql_injection(file_path, content, results)
                self._scan_xss(file_path, content, results)
                self._scan_command_injection(file_path, content, results)
                self._scan_crypto_issues(file_path, content, results)
                self._scan_path_traversal(file_path, content, results)
                
            except Exception as e:
                logger.warning(f"Could not scan {file_path}: {e}")
        
        # Convert sets to lists for JSON serialization
        results['owasp_coverage'] = sorted(list(results['owasp_coverage']))
        results['cwe_references'] = sorted(list(results['cwe_references']))
        results['vulnerabilities_by_type'] = dict(results['vulnerabilities_by_type'])
        results['vulnerabilities_by_severity'] = dict(results['vulnerabilities_by_severity'])
        
        logger.info(f"✅ Security scan complete: {results['vulnerabilities_found']} vulnerabilities found")
        return results
    
    def _scan_hardcoded_secrets(self, file_path: Path, content: str, results: Dict[str, Any]):
        """Scan for hardcoded secrets."""
        for secret_type, pattern in self.secret_patterns.items():
            for match in pattern.finditer(content):
                line_num = content[:match.start()].count('\n') + 1
                
                finding = {
                    'type': 'hardcoded_secret',
                    'subtype': secret_type,
                    'severity': 'HIGH',
                    'file': str(file_path),
                    'line': line_num,
                    'description': f'Hardcoded {secret_type} detected',
                    'owasp': 'A07:2021 – Identification and Authentication Failures',
                    'cwe': self.cwe_mapping['hardcoded_secret'],
                    'recommendation': 'Use environment variables or secure secret management',
                }
                
                results['findings'].append(finding)
                results['vulnerabilities_found'] += 1
                results['vulnerabilities_by_type']['hardcoded_secret'] += 1
                results['vulnerabilities_by_severity']['HIGH'] += 1
                results['owasp_coverage'].add('A07:2021')
                results['cwe_references'].add(self.cwe_mapping['hardcoded_secret'])
    
    def _scan_sql_injection(self, file_path: Path, content: str, results: Dict[str, Any]):
        """Scan for SQL injection vulnerabilities."""
        for pattern in self.sql_injection_patterns:
            for match in pattern.finditer(content):
                line_num = content[:match.start()].count('\n') + 1
                
                finding = {
                    'type': 'sql_injection',
                    'severity': 'CRITICAL',
                    'file': str(file_path),
                    'line': line_num,
                    'description': 'Potential SQL injection vulnerability',
                    'owasp': 'A03:2021 – Injection',
                    'cwe': self.cwe_mapping['sql_injection'],
                    'recommendation': 'Use parameterized queries or prepared statements',
                }
                
                results['findings'].append(finding)
                results['vulnerabilities_found'] += 1
                results['vulnerabilities_by_type']['sql_injection'] += 1
                results['vulnerabilities_by_severity']['CRITICAL'] += 1
                results['owasp_coverage'].add('A03:2021')
                results['cwe_references'].add(self.cwe_mapping['sql_injection'])
    
    def _scan_xss(self, file_path: Path, content: str, results: Dict[str, Any]):
        """Scan for XSS vulnerabilities."""
        for pattern in self.xss_patterns:
            for match in pattern.finditer(content):
                line_num = content[:match.start()].count('\n') + 1
                
                finding = {
                    'type': 'xss',
                    'severity': 'HIGH',
                    'file': str(file_path),
                    'line': line_num,
                    'description': 'Potential Cross-Site Scripting (XSS) vulnerability',
                    'owasp': 'A03:2021 – Injection',
                    'cwe': self.cwe_mapping['xss'],
                    'recommendation': 'Sanitize user input and use safe rendering methods',
                }
                
                results['findings'].append(finding)
                results['vulnerabilities_found'] += 1
                results['vulnerabilities_by_type']['xss'] += 1
                results['vulnerabilities_by_severity']['HIGH'] += 1
                results['owasp_coverage'].add('A03:2021')
                results['cwe_references'].add(self.cwe_mapping['xss'])
    
    def _scan_command_injection(self, file_path: Path, content: str, results: Dict[str, Any]):
        """Scan for command injection vulnerabilities."""
        for pattern in self.command_injection_patterns:
            for match in pattern.finditer(content):
                line_num = content[:match.start()].count('\n') + 1
                
                finding = {
                    'type': 'command_injection',
                    'severity': 'CRITICAL',
                    'file': str(file_path),
                    'line': line_num,
                    'description': 'Potential command injection vulnerability',
                    'owasp': 'A03:2021 – Injection',
                    'cwe': self.cwe_mapping['command_injection'],
                    'recommendation': 'Avoid shell execution or use subprocess with shell=False and validate inputs',
                }
                
                results['findings'].append(finding)
                results['vulnerabilities_found'] += 1
                results['vulnerabilities_by_type']['command_injection'] += 1
                results['vulnerabilities_by_severity']['CRITICAL'] += 1
                results['owasp_coverage'].add('A03:2021')
                results['cwe_references'].add(self.cwe_mapping['command_injection'])
    
    def _scan_crypto_issues(self, file_path: Path, content: str, results: Dict[str, Any]):
        """Scan for insecure cryptography usage."""
        for pattern in self.crypto_patterns:
            for match in pattern.finditer(content):
                line_num = content[:match.start()].count('\n') + 1
                
                finding = {
                    'type': 'weak_crypto',
                    'severity': 'MEDIUM',
                    'file': str(file_path),
                    'line': line_num,
                    'description': 'Insecure cryptographic algorithm or random number generator',
                    'owasp': 'A02:2021 – Cryptographic Failures',
                    'cwe': self.cwe_mapping['weak_crypto'],
                    'recommendation': 'Use SHA-256+ for hashing, AES-256 for encryption, secrets.SystemRandom for random',
                }
                
                results['findings'].append(finding)
                results['vulnerabilities_found'] += 1
                results['vulnerabilities_by_type']['weak_crypto'] += 1
                results['vulnerabilities_by_severity']['MEDIUM'] += 1
                results['owasp_coverage'].add('A02:2021')
                results['cwe_references'].add(self.cwe_mapping['weak_crypto'])
    
    def _scan_path_traversal(self, file_path: Path, content: str, results: Dict[str, Any]):
        """Scan for path traversal vulnerabilities."""
        for pattern in self.path_traversal_patterns:
            for match in pattern.finditer(content):
                line_num = content[:match.start()].count('\n') + 1
                
                finding = {
                    'type': 'path_traversal',
                    'severity': 'HIGH',
                    'file': str(file_path),
                    'line': line_num,
                    'description': 'Potential path traversal vulnerability',
                    'owasp': 'A01:2021 – Broken Access Control',
                    'cwe': self.cwe_mapping['path_traversal'],
                    'recommendation': 'Validate file paths and use Path.resolve() to prevent directory traversal',
                }
                
                results['findings'].append(finding)
                results['vulnerabilities_found'] += 1
                results['vulnerabilities_by_type']['path_traversal'] += 1
                results['vulnerabilities_by_severity']['HIGH'] += 1
                results['owasp_coverage'].add('A01:2021')
                results['cwe_references'].add(self.cwe_mapping['path_traversal'])
