"""
Phase 4: Security Audit

Identifies security vulnerabilities and insecure patterns.

Author: Asif Hussain
Created: January 3, 2026
"""

import ast
import logging
import re
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class SecurityAuditPhase:
    """Phase 4: Audit code for security vulnerabilities."""
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.target_path = orchestrator.target_path
    
    def execute(self) -> Dict[str, Any]:
        """
        Execute security audit.
        
        Returns:
            Dictionary containing security issues and remediation suggestions
        """
        logger.info("Phase 4: Starting security audit")
        
        results = {
            "vulnerabilities": [],
            "security_score": 0,
            "high_severity": 0,
            "medium_severity": 0,
            "low_severity": 0,
            "remediation_plan": []
        }
        
        try:
            files = self._get_python_files()
            
            for file_path in files:
                vulnerabilities = self._audit_file(file_path)
                results["vulnerabilities"].extend(vulnerabilities)
            
            # Count by severity
            for vuln in results["vulnerabilities"]:
                severity = vuln.get("severity", "low")
                if severity == "high":
                    results["high_severity"] += 1
                elif severity == "medium":
                    results["medium_severity"] += 1
                else:
                    results["low_severity"] += 1
            
            # Generate remediation plan
            results["remediation_plan"] = self._generate_remediation_plan(results)
            
            # Calculate security score
            results["security_score"] = self._calculate_security_score(results)
            
            logger.info(f"Security audit complete: {len(results['vulnerabilities'])} "
                       f"issues found ({results['high_severity']} high severity)")
            
        except Exception as e:
            logger.error(f"Security audit failed: {e}", exc_info=True)
            results["error"] = str(e)
        
        return results
    
    def _get_python_files(self) -> List[Path]:
        """Get list of Python files to analyze."""
        if self.target_path.is_file():
            return [self.target_path]
        
        python_files = list(self.target_path.rglob("*.py"))
        excluded = ["__pycache__", ".venv", "venv", "migrations", ".git"]
        return [f for f in python_files if not any(ex in str(f) for ex in excluded)]
    
    def _audit_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Audit a single file for security issues."""
        vulnerabilities = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Pattern-based checks
            vulnerabilities.extend(self._check_hardcoded_secrets(content, file_path))
            vulnerabilities.extend(self._check_sql_injection(content, file_path))
            vulnerabilities.extend(self._check_command_injection(content, file_path))
            
            # AST-based checks
            try:
                tree = ast.parse(content)
                vulnerabilities.extend(self._check_unsafe_functions(tree, file_path))
                vulnerabilities.extend(self._check_pickle_usage(tree, file_path))
            except SyntaxError:
                pass
        
        except Exception as e:
            logger.debug(f"Security audit failed for {file_path}: {e}")
        
        return vulnerabilities
    
    def _check_hardcoded_secrets(self, content: str, file_path: Path) -> List[Dict[str, Any]]:
        """Check for hardcoded secrets."""
        vulnerabilities = []
        
        # Patterns for common secrets
        secret_patterns = [
            (r'password\s*=\s*["\'][^"\']+["\']', "Hardcoded password"),
            (r'api[_-]?key\s*=\s*["\'][^"\']+["\']', "Hardcoded API key"),
            (r'secret[_-]?key\s*=\s*["\'][^"\']+["\']', "Hardcoded secret key"),
            (r'token\s*=\s*["\'][a-zA-Z0-9]{20,}["\']', "Hardcoded token"),
        ]
        
        for pattern, message in secret_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                vulnerabilities.append({
                    "file": str(file_path),
                    "line": line_num,
                    "type": "hardcoded_secret",
                    "severity": "high",
                    "message": message,
                    "remediation": "Use environment variables or secrets management"
                })
        
        return vulnerabilities
    
    def _check_sql_injection(self, content: str, file_path: Path) -> List[Dict[str, Any]]:
        """Check for potential SQL injection vulnerabilities."""
        vulnerabilities = []
        
        # Look for string formatting in SQL queries
        sql_patterns = [
            r'execute\([^)]*%',
            r'execute\([^)]*\.format',
            r'execute\([^)]*\+',
        ]
        
        for pattern in sql_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                vulnerabilities.append({
                    "file": str(file_path),
                    "line": line_num,
                    "type": "sql_injection",
                    "severity": "high",
                    "message": "Potential SQL injection - string formatting in query",
                    "remediation": "Use parameterized queries"
                })
        
        return vulnerabilities
    
    def _check_command_injection(self, content: str, file_path: Path) -> List[Dict[str, Any]]:
        """Check for command injection vulnerabilities."""
        vulnerabilities = []
        
        # Look for shell=True in subprocess calls
        if 'shell=True' in content:
            matches = re.finditer(r'shell=True', content)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                vulnerabilities.append({
                    "file": str(file_path),
                    "line": line_num,
                    "type": "command_injection",
                    "severity": "medium",
                    "message": "shell=True can lead to command injection",
                    "remediation": "Avoid shell=True or validate input carefully"
                })
        
        return vulnerabilities
    
    def _check_unsafe_functions(self, tree: ast.AST, file_path: Path) -> List[Dict[str, Any]]:
        """Check for usage of unsafe functions."""
        vulnerabilities = []
        
        unsafe_functions = {
            'eval': ("high", "eval() can execute arbitrary code"),
            'exec': ("high", "exec() can execute arbitrary code"),
            '__import__': ("medium", "Dynamic imports can be dangerous")
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                    if func_name in unsafe_functions:
                        severity, message = unsafe_functions[func_name]
                        vulnerabilities.append({
                            "file": str(file_path),
                            "line": node.lineno,
                            "type": "unsafe_function",
                            "severity": severity,
                            "message": f"Use of {func_name}() - {message}",
                            "remediation": "Avoid dynamic code execution"
                        })
        
        return vulnerabilities
    
    def _check_pickle_usage(self, tree: ast.AST, file_path: Path) -> List[Dict[str, Any]]:
        """Check for unsafe pickle usage."""
        vulnerabilities = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == 'pickle':
                        vulnerabilities.append({
                            "file": str(file_path),
                            "line": node.lineno,
                            "type": "unsafe_deserialization",
                            "severity": "medium",
                            "message": "pickle can execute arbitrary code during deserialization",
                            "remediation": "Use JSON or other safe formats"
                        })
        
        return vulnerabilities
    
    def _generate_remediation_plan(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate prioritized remediation plan."""
        plan = []
        
        # Group by type
        by_type = {}
        for vuln in results["vulnerabilities"]:
            vtype = vuln["type"]
            if vtype not in by_type:
                by_type[vtype] = []
            by_type[vtype].append(vuln)
        
        # Create remediation items
        priority_order = ["high", "medium", "low"]
        
        for severity in priority_order:
            for vtype, vulns in by_type.items():
                type_vulns = [v for v in vulns if v.get("severity") == severity]
                if type_vulns:
                    plan.append({
                        "priority": severity,
                        "type": vtype,
                        "count": len(type_vulns),
                        "remediation": type_vulns[0].get("remediation", "Review and fix"),
                        "files": list(set(v["file"] for v in type_vulns))
                    })
        
        return plan
    
    def _calculate_security_score(self, results: Dict[str, Any]) -> int:
        """Calculate overall security score (0-100)."""
        score = 100
        
        # Deduct points by severity
        score -= results["high_severity"] * 20
        score -= results["medium_severity"] * 10
        score -= results["low_severity"] * 5
        
        return max(0, min(100, score))
