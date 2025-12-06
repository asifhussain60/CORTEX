"""
SQL Injection Specialized Scanner

Deep scans for SQL injection vulnerabilities: inline SQL, string concatenation,
missing parameterization, ORM bypasses.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import re
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass, asdict


@dataclass
class SQLInjectionFinding:
    """SQL injection vulnerability finding"""
    severity: str  # critical, high, medium, low
    file: str
    line: int
    pattern: str
    code_snippet: str
    vulnerability_type: str
    recommendation: str


class SQLInjectionScanner:
    """
    Specialized scanner for SQL injection vulnerabilities.
    Detects inline SQL, concatenation, missing parameterization.
    """
    
    # Dangerous SQL patterns
    SQL_PATTERNS = [
        # String concatenation in SQL
        (r'["\']SELECT.*?\+.*?["\']', 'string_concatenation', 'critical'),
        (r'["\']INSERT.*?\+.*?["\']', 'string_concatenation', 'critical'),
        (r'["\']UPDATE.*?\+.*?["\']', 'string_concatenation', 'critical'),
        (r'["\']DELETE.*?\+.*?["\']', 'string_concatenation', 'critical'),
        
        # String interpolation in SQL
        (r'["\']SELECT.*?\{.*?\}.*?["\']', 'string_interpolation', 'critical'),
        (r'["\']INSERT.*?\{.*?\}.*?["\']', 'string_interpolation', 'critical'),
        (r'f["\']SELECT.*?["\']', 'f-string_sql', 'critical'),
        
        # Direct user input in SQL (simplified patterns)
        (r'request\.(GET|POST|query|form).*?SELECT', 'user_input_sql', 'critical'),
        (r'input\(.*?\).*?SELECT', 'user_input_sql', 'high'),
        
        # Missing parameterization
        (r'execute\(["\']SELECT.*?%s.*?["\'],\s*\(', 'missing_params', 'medium'),
        
        # Raw SQL execution
        (r'exec\(["\']SELECT', 'raw_exec', 'high'),
        (r'ExecuteNonQuery\(["\']SELECT', 'raw_exec', 'high'),
    ]
    
    # File extensions to scan
    CODE_EXTENSIONS = ['.py', '.cs', '.java', '.js', '.ts', '.php', '.rb', '.go']
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.findings: List[SQLInjectionFinding] = []
        
    def scan(self) -> Dict[str, Any]:
        """
        Scan repository for SQL injection vulnerabilities.
        
        Returns:
            Dictionary with findings, statistics, and recommendations
        """
        print(f"🔬 Deep scanning for SQL injection in {self.repo_path}")
        
        # Scan all code files
        files_scanned = 0
        for ext in self.CODE_EXTENSIONS:
            for file_path in self.repo_path.rglob(f'*{ext}'):
                if self._should_skip(file_path):
                    continue
                self._scan_file(file_path)
                files_scanned += 1
        
        # Categorize findings
        by_severity = {
            'critical': [f for f in self.findings if f.severity == 'critical'],
            'high': [f for f in self.findings if f.severity == 'high'],
            'medium': [f for f in self.findings if f.severity == 'medium'],
            'low': [f for f in self.findings if f.severity == 'low']
        }
        
        print(f"  Found {len(self.findings)} SQL injection risks across {files_scanned} files")
        
        return {
            'scan_type': 'sql_injection_deep_scan',
            'files_scanned': files_scanned,
            'total_findings': len(self.findings),
            'findings_by_severity': {
                'critical': len(by_severity['critical']),
                'high': len(by_severity['high']),
                'medium': len(by_severity['medium']),
                'low': len(by_severity['low'])
            },
            'findings': [asdict(f) for f in self.findings[:50]],  # Top 50
            'risk_score': self._calculate_risk_score(),
            'recommendations': self._generate_scan_recommendations()
        }
    
    def _should_skip(self, file_path: Path) -> bool:
        """Check if file should be skipped"""
        skip_dirs = {'.git', 'node_modules', 'venv', '__pycache__', 'bin', 'obj', 'test', 'tests'}
        return any(part in skip_dirs for part in file_path.parts)
    
    def _scan_file(self, file_path: Path) -> None:
        """Scan individual file for SQL injection patterns"""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            lines = content.split('\n')
            
            for line_num, line in enumerate(lines, start=1):
                # Check each pattern
                for pattern, vuln_type, severity in self.SQL_PATTERNS:
                    matches = re.finditer(pattern, line, re.IGNORECASE)
                    for match in matches:
                        self.findings.append(SQLInjectionFinding(
                            severity=severity,
                            file=str(file_path.relative_to(self.repo_path)),
                            line=line_num,
                            pattern=pattern,
                            code_snippet=line.strip()[:100],  # First 100 chars
                            vulnerability_type=vuln_type,
                            recommendation=self._get_recommendation(vuln_type)
                        ))
        except Exception as e:
            print(f"  Warning: Could not scan {file_path}: {e}")
    
    def _get_recommendation(self, vuln_type: str) -> str:
        """Get remediation recommendation for vulnerability type"""
        recommendations = {
            'string_concatenation': 'Use parameterized queries instead of string concatenation',
            'string_interpolation': 'Replace string interpolation with parameterized queries',
            'f-string_sql': 'Never use f-strings for SQL queries; use parameterized queries',
            'user_input_sql': 'Never include user input directly in SQL; use parameters',
            'missing_params': 'Use proper parameterization with execute() method',
            'raw_exec': 'Use ORM or parameterized queries instead of raw execution'
        }
        return recommendations.get(vuln_type, 'Use parameterized queries')
    
    def _calculate_risk_score(self) -> int:
        """Calculate overall SQL injection risk score (0-100)"""
        if not self.findings:
            return 0
        
        weights = {'critical': 10, 'high': 5, 'medium': 2, 'low': 1}
        total_risk = sum(weights.get(f.severity, 1) for f in self.findings)
        
        # Normalize to 0-100 scale (100 = maximum risk)
        # Assume 50 critical findings = 100 risk
        max_risk = 50 * weights['critical']
        risk_score = min(100, int((total_risk / max_risk) * 100))
        
        return risk_score
    
    def _generate_scan_recommendations(self) -> List[str]:
        """Generate specific recommendations based on findings"""
        recommendations = []
        
        if any(f.severity == 'critical' for f in self.findings):
            recommendations.append('CRITICAL: Address string concatenation in SQL queries immediately')
        
        if any(f.vulnerability_type == 'user_input_sql' for f in self.findings):
            recommendations.append('HIGH: Sanitize all user inputs before database operations')
        
        if len(self.findings) > 10:
            recommendations.append('Conduct code review for all database access layers')
            recommendations.append('Implement ORM framework to reduce raw SQL usage')
        
        recommendations.append('Enable SQL injection testing in CI/CD pipeline')
        
        return recommendations
