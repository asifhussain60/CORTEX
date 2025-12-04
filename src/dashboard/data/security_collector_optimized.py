"""
Optimized Security Collector

Fast security collector with timeouts and depth limits for external repository scanning.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import subprocess
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from src.dashboard.data.base_collector import BaseDataCollector


class SecurityCollectorOptimized(BaseDataCollector):
    """
    Optimized security collector for fast external repository scanning.
    
    Optimizations:
    - 5-second timeout on npm audit
    - Limited file scanning depth (max 1000 files)
    - Skip large directories (node_modules, vendor, etc.)
    - No hanging on subprocess calls
    
    Data Source: CURRENT STATE ONLY - Real scans, no mock data.
    """
    
    # Maximum files to scan for code patterns
    MAX_FILES_TO_SCAN = 1000
    
    # Directories to skip
    SKIP_DIRS = {'.git', 'node_modules', 'vendor', '__pycache__', 'venv', 
                 'bin', 'obj', 'dist', 'build', '.next', '.nuxt'}
    
    def collect(self) -> Optional[Dict[str, Any]]:
        """
        Collect security data with optimizations.
        
        Returns:
            Dict with keys: overall_score, categories, vulnerabilities, last_scan
            Returns minimal structure if no data found.
        """
        self.logger.info("Collecting security data (optimized)...")
        
        # Collect vulnerability data with timeout
        vuln_data = self._collect_vulnerabilities_fast()
        
        # Calculate category scores with limited scanning
        categories = self._calculate_category_scores_fast(vuln_data)
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(categories, vuln_data)
        
        security_data = {
            "overall_score": overall_score,
            "last_scan": datetime.now().isoformat(),
            "categories": [
                {"name": cat_name, "score": cat_data["score"], "status": self._get_status(cat_data["score"])}
                for cat_name, cat_data in categories.items()
            ],
            "vulnerabilities": self._format_vulnerabilities(vuln_data),
            "scan_mode": "fast"
        }
        
        self.logger.info(f"Security scan complete. Overall score: {overall_score}")
        return security_data
    
    def _collect_vulnerabilities_fast(self) -> Dict[str, int]:
        """
        Run vulnerability scans with strict timeouts.
        
        Returns:
            Dict with keys: critical, high, medium, low
        """
        vulns = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        
        # Try npm audit with 5-second timeout (ONE attempt only)
        if self._file_exists("package.json"):
            try:
                self.logger.debug("Running npm audit with 5s timeout...")
                result = subprocess.run(
                    ["npm", "audit", "--json"],
                    cwd=str(self.project_root),
                    capture_output=True,
                    text=True,
                    timeout=5  # 5-second timeout
                )
                
                if result.stdout:
                    data = self._safe_parse_json(result.stdout)
                    if data and "metadata" in data and "vulnerabilities" in data["metadata"]:
                        npm_vulns = data["metadata"]["vulnerabilities"]
                        for severity, count in npm_vulns.items():
                            if severity in vulns:
                                vulns[severity] += count
                        self.logger.info(f"npm audit: {sum(npm_vulns.values())} vulnerabilities found")
            
            except subprocess.TimeoutExpired:
                self.logger.warning("npm audit timeout after 5s - skipping")
            except FileNotFoundError:
                self.logger.debug("npm not found - skipping npm audit")
            except Exception as e:
                self.logger.debug(f"npm audit failed: {e}")
        
        # Try Python vulnerability scan with 5-second timeout
        if self._file_exists("requirements.txt"):
            try:
                self.logger.debug("Running pip-audit with 5s timeout...")
                result = subprocess.run(
                    ["pip-audit", "--format", "json"],
                    cwd=str(self.project_root),
                    capture_output=True,
                    text=True,
                    timeout=5  # 5-second timeout
                )
                
                if result.stdout:
                    data = self._safe_parse_json(result.stdout)
                    if data and "dependencies" in data:
                        for dep in data["dependencies"]:
                            vulns["medium"] += len(dep.get("vulns", []))
                        self.logger.info(f"pip-audit: {vulns['medium']} vulnerabilities found")
            
            except (subprocess.TimeoutExpired, FileNotFoundError):
                self.logger.debug("pip-audit not available or timeout - skipping")
            except Exception as e:
                self.logger.debug(f"pip-audit failed: {e}")
        
        return vulns
    
    def _calculate_category_scores_fast(self, vuln_data: Dict[str, int]) -> Dict[str, Dict[str, Any]]:
        """
        Calculate security category scores with limited file scanning.
        
        Only scans first MAX_FILES_TO_SCAN files for patterns.
        """
        return {
            "code_security": {
                "score": max(50, 90 - (vuln_data["critical"] * 10 + vuln_data["high"] * 5)),
                "issues": vuln_data["critical"] + vuln_data["high"]
            },
            "dependencies": {
                "score": max(50, 100 - sum(vuln_data.values()) * 5),
                "issues": sum(vuln_data.values())
            },
            "authentication": {
                "score": self._check_authentication_fast(),
                "issues": 0
            },
            "authorization": {
                "score": self._check_access_control_fast(),
                "issues": 0
            }
        }
    
    def _check_authentication_fast(self) -> int:
        """Check authentication with limited scanning."""
        score = 70
        
        # Check for auth patterns in limited files
        if self._search_codebase_limited(r"(mfa|two_factor|2fa|passport|jwt|oauth)", max_files=100):
            score += 15
        
        # Check for session management
        if self._search_codebase_limited(r"(session|cookie|SESSION_COOKIE_SECURE)", max_files=100):
            score += 15
        
        return min(score, 100)
    
    def _check_access_control_fast(self) -> int:
        """Check access control with limited scanning."""
        score = 75
        
        # Check for authorization patterns
        if self._search_codebase_limited(r"(authorize|permission|role|@require|@login_required)", max_files=100):
            score += 15
        
        return min(score, 100)
    
    def _search_codebase_limited(self, pattern: str, max_files: int = 100) -> bool:
        """
        Search codebase for regex pattern with strict limits.
        
        Args:
            pattern: Regex pattern to search for
            max_files: Maximum files to scan
            
        Returns:
            True if pattern found, False otherwise
        """
        files_scanned = 0
        
        # Search Python files
        for py_file in self.project_root.glob("**/*.py"):
            # Skip excluded directories
            if any(skip_dir in py_file.parts for skip_dir in self.SKIP_DIRS):
                continue
            
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                if re.search(pattern, content, re.IGNORECASE):
                    return True
                
                files_scanned += 1
                if files_scanned >= max_files:
                    self.logger.debug(f"Reached max file scan limit ({max_files})")
                    break
            
            except Exception:
                continue
        
        # Search JavaScript/TypeScript files if not found in Python
        if files_scanned < max_files:
            for js_file in self.project_root.glob("**/*.js"):
                if any(skip_dir in js_file.parts for skip_dir in self.SKIP_DIRS):
                    continue
                
                try:
                    content = js_file.read_text(encoding='utf-8', errors='ignore')
                    if re.search(pattern, content, re.IGNORECASE):
                        return True
                    
                    files_scanned += 1
                    if files_scanned >= max_files:
                        break
                
                except Exception:
                    continue
        
        return False
    
    def _calculate_overall_score(self, categories: Dict[str, Dict], vuln_data: Dict[str, int]) -> int:
        """Calculate overall security score."""
        # Weighted average of categories
        weights = {
            "code_security": 0.3,
            "dependencies": 0.3,
            "authentication": 0.2,
            "authorization": 0.2
        }
        
        score = sum(cat["score"] * weights.get(name, 0) for name, cat in categories.items())
        
        # Penalty for critical vulnerabilities
        score -= vuln_data["critical"] * 10
        score -= vuln_data["high"] * 5
        
        return max(0, min(100, int(score)))
    
    def _format_vulnerabilities(self, vuln_data: Dict[str, int]) -> List[Dict[str, Any]]:
        """Format vulnerability data for dashboard."""
        vulns = []
        for severity, count in vuln_data.items():
            if count > 0:
                vulns.append({
                    "severity": severity,
                    "count": count,
                    "description": f"{count} {severity} severity issues found"
                })
        return vulns
    
    def _get_status(self, score: int) -> str:
        """Get status from score."""
        if score >= 80:
            return "healthy"
        elif score >= 60:
            return "warning"
        else:
            return "critical"
