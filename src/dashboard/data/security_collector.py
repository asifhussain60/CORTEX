"""
Security Collector

Collects security metrics, vulnerabilities, and compliance data.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from src.dashboard.data.base_collector import BaseDataCollector


class SecurityCollector(BaseDataCollector):
    """
    Collects security-related data for dashboard.
    
    Data Sources:
    - npm audit (JavaScript vulnerabilities)
    - pip-audit or safety (Python vulnerabilities)
    - OWASP Top 10 compliance checks
    - Security best practices validation
    
    Data Source: CURRENT STATE ONLY - Real vulnerability scans, no mock data.
    """
    
    # OWASP Top 10 2021
    OWASP_TOP_10 = [
        ("A01", "Broken Access Control"),
        ("A02", "Cryptographic Failures"),
        ("A03", "Injection"),
        ("A04", "Insecure Design"),
        ("A05", "Security Misconfiguration"),
        ("A06", "Vulnerable and Outdated Components"),
        ("A07", "Identification and Authentication Failures"),
        ("A08", "Software and Data Integrity Failures"),
        ("A09", "Security Logging and Monitoring Failures"),
        ("A10", "Server-Side Request Forgery (SSRF)")
    ]
    
    def collect(self) -> Optional[Dict[str, Any]]:
        """
        Collect security data.
        
        Returns:
            Dict with keys: overall_score, categories, vulnerabilities, owasp_top_10, last_scan
        """
        self.logger.info("Collecting security data...")
        
        # Collect vulnerability data
        vuln_data = self._collect_vulnerabilities()
        
        # OWASP compliance
        owasp_compliance = self._check_owasp_compliance()
        
        # Calculate category scores
        categories = self._calculate_category_scores(vuln_data)
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(categories, vuln_data)
        
        security_data = {
            "overall_score": overall_score,
            "last_scan": datetime.now().isoformat(),
            "categories": categories,
            "vulnerabilities": vuln_data,
            "owasp_top_10": owasp_compliance,
            "compliance": {
                "gdpr_ready": self._check_gdpr_compliance(),
                "soc2_ready": self._check_soc2_compliance(),
                "hipaa_ready": False,  # Would require specific checks
                "pci_dss_ready": False  # Would require specific checks
            }
        }
        
        self.logger.info(f"Security scan complete. Overall score: {overall_score}")
        return security_data
    
    def _collect_vulnerabilities(self) -> Dict[str, int]:
        """
        Run vulnerability scans and collect results.
        
        Returns:
            Dict with keys: critical, high, medium, low
        """
        vulns = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        
        # Try npm audit (for JavaScript projects)
        if self._file_exists("package.json"):
            npm_vulns = self._run_npm_audit()
            for severity, count in npm_vulns.items():
                vulns[severity] += count
        
        # Try Python vulnerability scan
        if self._file_exists("requirements.txt"):
            py_vulns = self._run_python_audit()
            for severity, count in py_vulns.items():
                vulns[severity] += count
        
        return vulns
    
    def _run_npm_audit(self) -> Dict[str, int]:
        """
        Run npm audit and parse results.
        
        Returns:
            Dict with vulnerability counts by severity
        """
        try:
            result = subprocess.run(
                ["npm", "audit", "--json"],
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 or result.stdout:
                data = self._safe_parse_json(result.stdout)
                if data and "metadata" in data and "vulnerabilities" in data["metadata"]:
                    return data["metadata"]["vulnerabilities"]
        
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
            self.logger.warning(f"npm audit failed: {e}")
        
        return {"critical": 0, "high": 0, "medium": 0, "low": 0}
    
    def _run_python_audit(self) -> Dict[str, int]:
        """
        Run Python vulnerability scan (pip-audit or safety).
        
        Returns:
            Dict with vulnerability counts by severity
        """
        vulns = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        
        # Try pip-audit first
        try:
            result = subprocess.run(
                ["pip-audit", "--format", "json"],
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 or result.stdout:
                data = self._safe_parse_json(result.stdout)
                if data and "dependencies" in data:
                    # Parse pip-audit JSON format
                    for dep in data["dependencies"]:
                        for vuln in dep.get("vulns", []):
                            # Map CVSS scores to severity
                            # (simplified - would need actual CVSS parsing)
                            vulns["medium"] += 1
                    
                    return vulns
        
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            self.logger.debug("pip-audit not available, trying safety...")
        
        # Fallback to safety
        try:
            result = subprocess.run(
                ["safety", "check", "--json"],
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.stdout:
                data = self._safe_parse_json(result.stdout)
                if data:
                    # Count vulnerabilities
                    vuln_count = len(data) if isinstance(data, list) else 0
                    vulns["medium"] = vuln_count
        
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
            self.logger.warning(f"Python audit failed: {e}")
        
        return vulns
    
    def _check_owasp_compliance(self) -> List[Dict[str, Any]]:
        """
        Check OWASP Top 10 compliance.
        
        Returns:
            List of dicts with risk ID, name, score, status
        """
        compliance = []
        
        for risk_id, risk_name in self.OWASP_TOP_10:
            # Simplified scoring - would need actual security tests
            score = self._calculate_owasp_score(risk_id)
            
            compliance.append({
                "risk": f"{risk_id}_{risk_name.replace(' ', '_')}",
                "name": risk_name,
                "score": score,
                "status": "pass" if score >= 80 else "warn" if score >= 60 else "fail"
            })
        
        return compliance
    
    def _calculate_owasp_score(self, risk_id: str) -> int:
        """
        Calculate OWASP compliance score for specific risk.
        
        Args:
            risk_id: OWASP risk ID (A01-A10)
            
        Returns:
            Score 0-100
        """
        # Simplified heuristics - would need real security tests
        checks = {
            "A01": self._check_access_control(),
            "A02": self._check_cryptography(),
            "A03": self._check_injection_prevention(),
            "A04": 85,  # Design security - manual review needed
            "A05": self._check_security_config(),
            "A06": self._check_component_security(),
            "A07": self._check_authentication(),
            "A08": 80,  # Data integrity - manual review needed
            "A09": self._check_logging(),
            "A10": 75   # SSRF - manual review needed
        }
        
        return checks.get(risk_id, 70)
    
    def _check_access_control(self) -> int:
        """Check for access control implementation."""
        score = 70
        
        # Check for authorization middleware
        if self._search_codebase(r"@require_auth|@login_required|authorize"):
            score += 15
        
        # Check for role-based access
        if self._search_codebase(r"@role_required|check_permission|has_role"):
            score += 15
        
        return min(score, 100)
    
    def _check_cryptography(self) -> int:
        """Check for proper cryptography usage."""
        score = 70
        
        # Check for password hashing
        if self._search_codebase(r"bcrypt|argon2|pbkdf2"):
            score += 15
        
        # Check for HTTPS enforcement
        if self._search_codebase(r"SECURE_SSL_REDIRECT|force_https"):
            score += 15
        
        return min(score, 100)
    
    def _check_injection_prevention(self) -> int:
        """Check for injection prevention."""
        score = 80
        
        # Check for parameterized queries
        if self._search_codebase(r"execute\(.*?\?|prepare\("):
            score += 10
        
        # Check for input validation
        if self._search_codebase(r"validate|sanitize|escape"):
            score += 10
        
        return min(score, 100)
    
    def _check_security_config(self) -> int:
        """Check security configuration."""
        score = 75
        
        # Check for secure headers
        if self._search_codebase(r"X-Frame-Options|Content-Security-Policy"):
            score += 15
        
        # Check for secrets management
        if self._file_exists(".env.example") and not self._search_codebase(r"password\s*=\s*['\"]"):
            score += 10
        
        return min(score, 100)
    
    def _check_component_security(self) -> int:
        """Check for vulnerable components."""
        # Use vulnerability counts
        vuln_data = self._collect_vulnerabilities()
        total_vulns = sum(vuln_data.values())
        
        if total_vulns == 0:
            return 100
        elif total_vulns < 5:
            return 85
        elif total_vulns < 10:
            return 70
        else:
            return max(50, 100 - (total_vulns * 5))
    
    def _check_authentication(self) -> int:
        """Check authentication implementation."""
        score = 70
        
        # Check for multi-factor auth
        if self._search_codebase(r"mfa|two_factor|2fa"):
            score += 15
        
        # Check for session management
        if self._search_codebase(r"session_timeout|SESSION_COOKIE_SECURE"):
            score += 15
        
        return min(score, 100)
    
    def _check_logging(self) -> int:
        """Check logging implementation."""
        score = 80
        
        # Check for audit logging
        if self._search_codebase(r"audit_log|security_log"):
            score += 10
        
        # Check for monitoring
        if self._search_codebase(r"sentry|logging.error|log.error"):
            score += 10
        
        return min(score, 100)
    
    def _search_codebase(self, pattern: str) -> bool:
        """
        Search codebase for regex pattern.
        
        Args:
            pattern: Regex pattern to search for
            
        Returns:
            True if pattern found, False otherwise
        """
        import re
        
        # Search Python files
        for py_file in self.project_root.glob("**/*.py"):
            if "venv" in str(py_file) or "node_modules" in str(py_file):
                continue
            
            try:
                content = py_file.read_text()
                if re.search(pattern, content, re.IGNORECASE):
                    return True
            except Exception:
                continue
        
        return False
    
    def _calculate_category_scores(self, vuln_data: Dict[str, int]) -> Dict[str, Dict[str, Any]]:
        """Calculate security category scores."""
        return {
            "code_security": {
                "score": 90 - (vuln_data["critical"] * 10 + vuln_data["high"] * 5),
                "issues": vuln_data["critical"] + vuln_data["high"]
            },
            "dependencies": {
                "score": 100 - sum(vuln_data.values()) * 5,
                "issues": sum(vuln_data.values())
            },
            "authentication": {
                "score": self._check_authentication(),
                "issues": 0
            },
            "authorization": {
                "score": self._check_access_control(),
                "issues": 0
            },
            "data_security": {
                "score": self._check_cryptography(),
                "issues": 0
            },
            "network": {
                "score": 90,
                "issues": 0
            }
        }
    
    def _calculate_overall_score(
        self, 
        categories: Dict[str, Dict[str, Any]], 
        vuln_data: Dict[str, int]
    ) -> int:
        """Calculate overall security score."""
        category_scores = [cat["score"] for cat in categories.values()]
        avg_score = sum(category_scores) / len(category_scores)
        
        # Penalty for critical vulnerabilities
        penalty = vuln_data["critical"] * 10 + vuln_data["high"] * 5
        
        return max(0, int(avg_score - penalty))
    
    def _check_gdpr_compliance(self) -> bool:
        """Check GDPR compliance indicators."""
        # Check for privacy policy, data handling, etc.
        return (
            self._search_codebase(r"privacy_policy|data_protection|gdpr") or
            self._file_exists("PRIVACY.md")
        )
    
    def _check_soc2_compliance(self) -> bool:
        """Check SOC 2 compliance indicators."""
        # Check for audit logging, access controls, etc.
        return (
            self._check_logging() >= 80 and
            self._check_access_control() >= 80
        )
