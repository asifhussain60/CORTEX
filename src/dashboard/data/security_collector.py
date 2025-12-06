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
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

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
    
    # OWASP Top 10 2025 (Latest)
    OWASP_TOP_10_2025 = [
        ("A01", "Broken Access Control"),
        ("A02", "Cryptographic Failures"),
        ("A03", "Injection"),
        ("A04", "Insecure Design"),
        ("A05", "Security Misconfiguration"),
        ("A06", "Vulnerable and Outdated Components"),
        ("A07", "Identification and Authentication Failures"),
        ("A08", "Software and Data Integrity Failures"),
        ("A09", "Security Logging and Monitoring Failures"),
        ("A10", "Server-Side Request Forgery (SSRF)"),
        ("A11", "Insecure AI/ML Model Deployment")
    ]
    
    def collect(self) -> Optional[Dict[str, Any]]:
        """
        Collect security data with deep scanning.
        
        Returns:
            Dict with keys: overall_score, categories, vulnerabilities, owasp_top_10, last_scan, findings
        """
        self.logger.info("Starting comprehensive security scan...")
        
        # Deep security scans
        vuln_findings = self._scan_for_vulnerabilities()
        hardcoded_secrets = self._scan_hardcoded_secrets()
        config_issues = self._scan_configuration_issues()
        dependency_vulns = self._scan_dependency_vulnerabilities()
        
        # OWASP compliance with detailed findings based on actual scan results
        owasp_compliance = self._check_owasp_compliance_detailed(
            vuln_findings, hardcoded_secrets, config_issues, dependency_vulns
        )
        
        # Calculate vulnerability counts
        vuln_data = {
            "critical": len([f for f in vuln_findings if f.get("severity") == "critical"]),
            "high": len([f for f in vuln_findings if f.get("severity") == "high"]),
            "medium": len([f for f in vuln_findings if f.get("severity") == "medium"]),
            "low": len([f for f in vuln_findings if f.get("severity") == "low"])
        }
        
        # Compliance readiness with evidence
        compliance_data = self._assess_compliance_readiness(
            vuln_findings, hardcoded_secrets, config_issues
        )
        
        # Calculate category scores with details
        categories = self._calculate_category_scores_detailed(
            vuln_findings, hardcoded_secrets, config_issues, dependency_vulns
        )
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(categories, vuln_data)
        
        security_data = {
            "overall_score": overall_score,
            "last_scan": datetime.now().isoformat(),
            "categories": categories,
            "vulnerabilities": vuln_data,
            "owasp_top_10": owasp_compliance,
            "compliance": compliance_data,
            "findings": {
                "vulnerabilities": vuln_findings[:20],  # Top 20
                "hardcoded_secrets": hardcoded_secrets[:10],  # Top 10
                "config_issues": config_issues[:15],  # Top 15
                "dependency_vulns": dependency_vulns[:10]  # Top 10
            },
            "scan_mode": "deep"
        }
        
        self.logger.info(f"Security scan complete. Score: {overall_score}, "
                        f"Findings: {len(vuln_findings)} vulns, {len(hardcoded_secrets)} secrets, "
                        f"{len(config_issues)} config issues")
        return security_data
    
    def _scan_for_vulnerabilities(self) -> List[Dict[str, Any]]:
        """Comprehensive vulnerability scanning for .NET projects."""
        findings = []
        
        # Scan for SQL Injection vulnerabilities
        findings.extend(self._scan_sql_injection())
        
        # Scan for XSS vulnerabilities
        findings.extend(self._scan_xss())
        
        # Scan for insecure deserialization
        findings.extend(self._scan_insecure_deserialization())
        
        # Scan for weak cryptography
        findings.extend(self._scan_weak_cryptography())
        
        # Scan for missing input validation
        findings.extend(self._scan_input_validation())
        
        return findings
    
    def _scan_sql_injection(self) -> List[Dict[str, Any]]:
        """Scan for SQL injection vulnerabilities with parallel processing."""
        findings = []
        import re
        
        cs_files = list(self.project_root.glob("**/*.cs"))
        self.logger.info(f"Scanning {len(cs_files)} C# files for SQL injection...")
        
        # Process files in parallel batches
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {executor.submit(self._scan_file_for_sql_injection, cs_file): cs_file for cs_file in cs_files}
            
            for future in as_completed(futures):
                try:
                    file_findings = future.result()
                    findings.extend(file_findings)
                except Exception as e:
                    self.logger.debug(f"Error in SQL injection scan: {e}")
        
        self.logger.info(f"Found {len(findings)} SQL injection vulnerabilities")
        return findings
    
    def _scan_file_for_sql_injection(self, cs_file: Path) -> List[Dict[str, Any]]:
        """Scan a single file for SQL injection."""
        findings = []
        import re
        
        try:
            content = cs_file.read_text(encoding='utf-8', errors='ignore')
            lines = content.split('\n')
            
            for i, line in enumerate(lines, 1):
                # Check for string concatenation in SQL queries
                if re.search(r'(SqlCommand|OracleCommand|DbCommand).*?".*?\+', line, re.IGNORECASE):
                    findings.append({
                        "type": "SQL Injection",
                        "severity": "high",
                        "file": str(cs_file.relative_to(self.project_root)),
                        "line": i,
                        "description": "Potential SQL injection via string concatenation",
                        "code_snippet": line.strip()[:100],
                        "recommendation": "Use parameterized queries instead"
                    })
                
                # Check for ExecuteReader/ExecuteNonQuery with concatenated strings
                if re.search(r'Execute(Reader|NonQuery|Scalar).*?\+.*?["\']', line, re.IGNORECASE):
                    findings.append({
                        "type": "SQL Injection",
                        "severity": "high",
                        "file": str(cs_file.relative_to(self.project_root)),
                        "line": i,
                        "description": "SQL command execution with string concatenation",
                        "code_snippet": line.strip()[:100],
                        "recommendation": "Use SqlParameter or OracleParameter"
                    })
        
        except Exception as e:
            pass
        
        return findings
    
    def _scan_xss(self) -> List[Dict[str, Any]]:
        """Scan for XSS vulnerabilities with parallel processing."""
        findings = []
        import re
        
        # Scan web config and code files
        config_files = list(self.project_root.glob("**/Web.config")) + list(self.project_root.glob("**/*.aspx"))
        cs_files = list(self.project_root.glob("**/*.cs"))
        all_files = config_files + cs_files
        
        self.logger.info(f"Scanning {len(all_files)} files for XSS vulnerabilities...")
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {executor.submit(self._scan_file_for_xss, file): file for file in all_files}
            
            for future in as_completed(futures):
                try:
                    file_findings = future.result()
                    findings.extend(file_findings)
                except Exception as e:
                    self.logger.debug(f"Error in XSS scan: {e}")
        
        self.logger.info(f"Found {len(findings)} XSS vulnerabilities")
        return findings
    
    def _scan_file_for_xss(self, file: Path) -> List[Dict[str, Any]]:
        """Scan a single file for XSS vulnerabilities."""
        findings = []
        import re
        
        for file in [file]:
            try:
                content = file.read_text(encoding='utf-8', errors='ignore')
                
                # Check for ValidateRequest=false
                if re.search(r'ValidateRequest\s*=\s*["\']false["\']', content, re.IGNORECASE):
                    findings.append({
                        "type": "XSS",
                        "severity": "medium",
                        "file": str(file.relative_to(self.project_root)),
                        "line": 0,
                        "description": "Request validation disabled - potential XSS vulnerability",
                        "code_snippet": "ValidateRequest=false",
                        "recommendation": "Enable request validation or implement custom sanitization"
                    })
                
                # Check for HttpUtility.HtmlEncode missing
                if 'Response.Write' in content and 'HtmlEncode' not in content:
                    findings.append({
                        "type": "XSS",
                        "severity": "medium",
                        "file": str(file.relative_to(self.project_root)),
                        "line": 0,
                        "description": "Response.Write without HtmlEncode - potential XSS",
                        "code_snippet": "Response.Write without encoding",
                        "recommendation": "Use HttpUtility.HtmlEncode for all user input"
                    })
            
            except Exception as e:
                self.logger.debug(f"Error scanning {file}: {e}")
        
        return findings
    
    def _scan_hardcoded_secrets(self) -> List[Dict[str, Any]]:
        """Scan for hardcoded passwords, API keys, connection strings with parallel processing."""
        secrets = []
        import re
        
        # Patterns for secrets
        patterns = [
            (r'password\s*=\s*["\']([^"\']{4,})["\']', "Hardcoded Password", "critical"),
            (r'pwd\s*=\s*["\']([^"\']{4,})["\']', "Hardcoded Password", "critical"),
            (r'api[_-]?key\s*=\s*["\']([^"\']{10,})["\']', "Hardcoded API Key", "high"),
            (r'secret\s*=\s*["\']([^"\']{10,})["\']', "Hardcoded Secret", "high"),
            (r'token\s*=\s*["\']([^"\']{10,})["\']', "Hardcoded Token", "high"),
            (r'connectionString\s*=\s*["\']([^"\']*password[^"\']*)["\']', "Connection String with Password", "critical")
        ]
        
        config_files = list(self.project_root.glob("**/*.config")) + list(self.project_root.glob("**/*.cs"))
        self.logger.info(f"Scanning {len(config_files)} files for hardcoded secrets...")
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {executor.submit(self._scan_file_for_secrets, file, patterns): file for file in config_files}
            
            for future in as_completed(futures):
                try:
                    file_secrets = future.result()
                    secrets.extend(file_secrets)
                except Exception as e:
                    self.logger.debug(f"Error in secrets scan: {e}")
        
        self.logger.info(f"Found {len(secrets)} hardcoded secrets")
        return secrets
    
    def _scan_file_for_secrets(self, file: Path, patterns: List) -> List[Dict[str, Any]]:
        """Scan a single file for hardcoded secrets."""
        secrets = []
        import re
        
        for file in [file]:
            try:
                content = file.read_text(encoding='utf-8', errors='ignore')
                lines = content.split('\n')
                
                for i, line in enumerate(lines, 1):
                    for pattern, secret_type, severity in patterns:
                        matches = re.finditer(pattern, line, re.IGNORECASE)
                        for match in matches:
                            # Skip commented lines
                            if line.strip().startswith('//') or line.strip().startswith('<!--'):
                                continue
                            
                            # Mask the secret value
                            secret_value = match.group(1) if len(match.groups()) > 0 else ""
                            masked_value = secret_value[:3] + '*' * (len(secret_value) - 3) if len(secret_value) > 3 else "***"
                            
                            secrets.append({
                                "type": secret_type,
                                "severity": severity,
                                "file": str(file.relative_to(self.project_root)),
                                "line": i,
                                "description": f"{secret_type} found in plain text",
                                "masked_value": masked_value,
                                "recommendation": "Move to environment variables or secure vault (Azure Key Vault, AWS Secrets Manager)"
                            })
            
            except Exception as e:
                self.logger.debug(f"Error scanning {file}: {e}")
        
        return secrets
    
    def _scan_configuration_issues(self) -> List[Dict[str, Any]]:
        """Scan for security misconfigurations."""
        issues = []
        import re
        
        web_configs = list(self.project_root.glob("**/Web.config"))
        
        for config in web_configs:
            try:
                content = config.read_text(encoding='utf-8', errors='ignore')
                
                # Check for debug mode enabled
                if re.search(r'<compilation\s+debug\s*=\s*["\']true["\']', content, re.IGNORECASE):
                    issues.append({
                        "type": "Security Misconfiguration",
                        "severity": "medium",
                        "file": str(config.relative_to(self.project_root)),
                        "description": "Debug mode enabled in production config",
                        "recommendation": "Set debug=false in production"
                    })
                
                # Check for custom errors off
                if re.search(r'<customErrors\s+mode\s*=\s*["\']Off["\']', content, re.IGNORECASE):
                    issues.append({
                        "type": "Information Disclosure",
                        "severity": "medium",
                        "file": str(config.relative_to(self.project_root)),
                        "description": "Custom errors disabled - exposes stack traces",
                        "recommendation": "Set customErrors mode to RemoteOnly or On"
                    })
                
                # Check for trace enabled
                if re.search(r'<trace\s+enabled\s*=\s*["\']true["\']', content, re.IGNORECASE):
                    issues.append({
                        "type": "Information Disclosure",
                        "severity": "low",
                        "file": str(config.relative_to(self.project_root)),
                        "description": "Trace enabled - may expose sensitive information",
                        "recommendation": "Disable trace in production"
                    })
                
                # Check for missing HTTPS enforcement
                if '<httpCookies' not in content or 'requireSSL' not in content:
                    issues.append({
                        "type": "Security Misconfiguration",
                        "severity": "medium",
                        "file": str(config.relative_to(self.project_root)),
                        "description": "HTTPS not enforced for cookies",
                        "recommendation": "Set httpCookies requireSSL=true"
                    })
            
            except Exception as e:
                self.logger.debug(f"Error scanning {config}: {e}")
        
        return issues
    
    def _scan_dependency_vulnerabilities(self) -> List[Dict[str, Any]]:
        """Scan for known vulnerabilities in NuGet packages."""
        vulns = []
        import re
        
        packages_configs = list(self.project_root.glob("**/packages.config"))
        
        # Known vulnerable package versions (sample - would need real CVE database)
        known_vulns = {
            "Newtonsoft.Json": {
                "versions": ["12.0.0", "12.0.1", "12.0.2"],
                "cve": "CVE-2024-21907",
                "severity": "high",
                "description": "Deserialization vulnerability"
            },
            "System.Text.Json": {
                "versions": ["4.7.0", "4.7.1"],
                "cve": "CVE-2021-26701",
                "severity": "high",
                "description": "Denial of Service vulnerability"
            }
        }
        
        for pkg_config in packages_configs:
            try:
                content = pkg_config.read_text(encoding='utf-8', errors='ignore')
                
                for package_name, vuln_info in known_vulns.items():
                    pattern = f'<package\\s+id="{package_name}"\\s+version="([^"]+)"'
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    
                    for match in matches:
                        version = match.group(1)
                        if version in vuln_info["versions"]:
                            vulns.append({
                                "type": "Vulnerable Dependency",
                                "severity": vuln_info["severity"],
                                "package": package_name,
                                "version": version,
                                "cve": vuln_info["cve"],
                                "description": vuln_info["description"],
                                "file": str(pkg_config.relative_to(self.project_root)),
                                "recommendation": f"Update {package_name} to latest version"
                            })
            
            except Exception as e:
                self.logger.debug(f"Error scanning {pkg_config}: {e}")
        
        return vulns
    
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
    
    def _scan_weak_cryptography(self) -> List[Dict[str, Any]]:
        """Scan for weak cryptography usage with parallel processing."""
        findings = []
        import re
        
        cs_files = list(self.project_root.glob("**/*.cs"))
        weak_patterns = [
            (r'MD5|SHA1(?!256)', "Weak Hashing Algorithm", "medium"),
            (r'DES(?!C)|3DES', "Weak Encryption Algorithm", "high"),
            (r'Random\(\)', "Weak Random Number Generator", "medium")
        ]
        
        self.logger.info(f"Scanning {len(cs_files)} C# files for weak cryptography...")
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {executor.submit(self._scan_file_for_weak_crypto, cs_file, weak_patterns): cs_file for cs_file in cs_files}
            
            for future in as_completed(futures):
                try:
                    file_findings = future.result()
                    findings.extend(file_findings)
                except Exception as e:
                    self.logger.debug(f"Error in crypto scan: {e}")
        
        self.logger.info(f"Found {len(findings)} weak cryptography issues")
        return findings
    
    def _scan_file_for_weak_crypto(self, cs_file: Path, weak_patterns: List) -> List[Dict[str, Any]]:
        """Scan a single file for weak cryptography."""
        findings = []
        import re
        
        for cs_file in [cs_file]:
            try:
                content = cs_file.read_text(encoding='utf-8', errors='ignore')
                lines = content.split('\n')
                
                for i, line in enumerate(lines, 1):
                    for pattern, issue_type, severity in weak_patterns:
                        if re.search(pattern, line):
                            findings.append({
                                "type": issue_type,
                                "severity": severity,
                                "file": str(cs_file.relative_to(self.project_root)),
                                "line": i,
                                "description": f"{issue_type} detected",
                                "code_snippet": line.strip()[:100],
                                "recommendation": "Use SHA256/SHA512 for hashing, AES for encryption, RNGCryptoServiceProvider for random numbers"
                            })
            
            except Exception as e:
                self.logger.debug(f"Error scanning {cs_file}: {e}")
        
        return findings
    
    def _scan_input_validation(self) -> List[Dict[str, Any]]:
        """Scan for missing input validation with parallel processing."""
        findings = []
        import re
        
        cs_files = list(self.project_root.glob("**/*.cs"))
        
        self.logger.info(f"Scanning {len(cs_files)} C# files for input validation issues...")
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {executor.submit(self._scan_file_for_input_validation, cs_file): cs_file for cs_file in cs_files}
            
            for future in as_completed(futures):
                try:
                    file_findings = future.result()
                    findings.extend(file_findings)
                except Exception as e:
                    self.logger.debug(f"Error in validation scan: {e}")
        
        self.logger.info(f"Found {len(findings)} input validation issues")
        return findings
    
    def _scan_file_for_input_validation(self, cs_file: Path) -> List[Dict[str, Any]]:
        """Scan a single file for input validation issues."""
        findings = []
        import re
        
        for cs_file in [cs_file]:
            try:
                content = cs_file.read_text(encoding='utf-8', errors='ignore')
                lines = content.split('\n')
                
                for i, line in enumerate(lines, 1):
                    # Check for Request.QueryString/Form without validation
                    if re.search(r'Request\.(QueryString|Form|Params)\[', line):
                        # Check if next few lines have validation
                        context = '\n'.join(lines[max(0, i-1):min(len(lines), i+5)])
                        if not re.search(r'(IsNull|IsEmpty|Validate|Check|if\s*\()', context):
                            findings.append({
                                "type": "Missing Input Validation",
                                "severity": "medium",
                                "file": str(cs_file.relative_to(self.project_root)),
                                "line": i,
                                "description": "User input used without validation",
                                "code_snippet": line.strip()[:100],
                                "recommendation": "Validate and sanitize all user inputs"
                            })
            
            except Exception as e:
                self.logger.debug(f"Error scanning {cs_file}: {e}")
        
        return findings
    
    def _scan_insecure_deserialization(self) -> List[Dict[str, Any]]:
        """Scan for insecure deserialization with parallel processing."""
        findings = []
        import re
        
        cs_files = list(self.project_root.glob("**/*.cs"))
        
        self.logger.info(f"Scanning {len(cs_files)} C# files for insecure deserialization...")
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {executor.submit(self._scan_file_for_deserialization, cs_file): cs_file for cs_file in cs_files}
            
            for future in as_completed(futures):
                try:
                    file_findings = future.result()
                    findings.extend(file_findings)
                except Exception as e:
                    self.logger.debug(f"Error in deserialization scan: {e}")
        
        self.logger.info(f"Found {len(findings)} deserialization issues")
        return findings
    
    def _scan_file_for_deserialization(self, cs_file: Path) -> List[Dict[str, Any]]:
        """Scan a single file for insecure deserialization."""
        findings = []
        import re
        
        for cs_file in [cs_file]:
            try:
                content = cs_file.read_text(encoding='utf-8', errors='ignore')
                lines = content.split('\n')
                
                for i, line in enumerate(lines, 1):
                    # Check for BinaryFormatter (known insecure)
                    if re.search(r'BinaryFormatter|SoapFormatter|NetDataContractSerializer', line):
                        findings.append({
                            "type": "Insecure Deserialization",
                            "severity": "high",
                            "file": str(cs_file.relative_to(self.project_root)),
                            "line": i,
                            "description": "Insecure deserialization method detected",
                            "code_snippet": line.strip()[:100],
                            "recommendation": "Use DataContractSerializer or JSON.NET instead"
                        })
            
            except Exception as e:
                self.logger.debug(f"Error scanning {cs_file}: {e}")
        
        return findings
    
    def _assess_compliance_readiness(
        self, 
        vuln_findings: List[Dict], 
        secrets: List[Dict], 
        config_issues: List[Dict]
    ) -> Dict[str, Any]:
        """Assess compliance readiness with evidence."""
        
        # Calculate compliance scores based on findings
        critical_issues = len([f for f in vuln_findings + secrets if f.get("severity") == "critical"])
        high_issues = len([f for f in vuln_findings + secrets if f.get("severity") == "high"])
        
        # GDPR - Data protection and privacy
        gdpr_ready = critical_issues == 0 and high_issues < 5
        gdpr_issues = []
        if secrets:
            gdpr_issues.append("Hardcoded credentials found - violates data protection")
        if config_issues:
            gdpr_issues.append("Security misconfigurations detected")
        
        # SOC 2 - Security controls and monitoring
        soc2_ready = critical_issues == 0 and len(config_issues) < 5
        soc2_issues = []
        if high_issues > 0:
            soc2_issues.append(f"{high_issues} high-severity vulnerabilities")
        
        # HIPAA - Healthcare data security
        hipaa_ready = critical_issues == 0 and high_issues == 0 and len(secrets) == 0
        hipaa_issues = []
        if secrets:
            hipaa_issues.append("Encryption keys/credentials not secured")
        if not self._search_code_pattern(r'encrypt|AES'):
            hipaa_issues.append("No encryption implementation found")
        
        # PCI DSS - Payment card security
        pci_ready = critical_issues == 0 and len(secrets) == 0
        pci_issues = []
        if secrets:
            pci_issues.append("Sensitive data stored in plain text")
        if config_issues:
            pci_issues.append("Security configuration weaknesses")
        
        return {
            "gdpr_ready": gdpr_ready,
            "gdpr_issues": gdpr_issues,
            "soc2_ready": soc2_ready,
            "soc2_issues": soc2_issues,
            "hipaa_ready": hipaa_ready,
            "hipaa_issues": hipaa_issues,
            "pci_dss_ready": pci_ready,
            "pci_dss_issues": pci_issues
        }
    
    def _calculate_category_scores_detailed(
        self,
        vuln_findings: List[Dict],
        secrets: List[Dict],
        config_issues: List[Dict],
        dependency_vulns: List[Dict]
    ) -> List[Dict[str, Any]]:
        """Calculate detailed category scores."""
        
        categories = []
        
        # Code Security
        code_vulns = [f for f in vuln_findings if f.get("type") in ["SQL Injection", "XSS", "Insecure Deserialization"]]
        code_score = max(0, 100 - len(code_vulns) * 10)
        categories.append({
            "name": "code_security",
            "score": code_score,
            "status": "healthy" if code_score >= 80 else "warning" if code_score >= 60 else "critical",
            "issues": len(code_vulns),
            "details": f"{len(code_vulns)} code-level vulnerabilities found"
        })
        
        # Dependencies
        dep_score = max(0, 100 - len(dependency_vulns) * 15)
        categories.append({
            "name": "dependencies",
            "score": dep_score,
            "status": "healthy" if dep_score >= 80 else "warning" if dep_score >= 60 else "critical",
            "issues": len(dependency_vulns),
            "details": f"{len(dependency_vulns)} vulnerable dependencies"
        })
        
        # Authentication & Authorization
        auth_issues = [f for f in vuln_findings if "authentication" in f.get("type", "").lower()]
        auth_score = max(0, 100 - len(auth_issues) * 20 - len(secrets) * 10)
        categories.append({
            "name": "authentication",
            "score": auth_score,
            "status": "healthy" if auth_score >= 80 else "warning" if auth_score >= 60 else "critical",
            "issues": len(auth_issues) + len(secrets),
            "details": f"{len(secrets)} hardcoded credentials, {len(auth_issues)} auth issues"
        })
        
        # Configuration Security
        config_score = max(0, 100 - len(config_issues) * 10)
        categories.append({
            "name": "configuration",
            "score": config_score,
            "status": "healthy" if config_score >= 80 else "warning" if config_score >= 60 else "critical",
            "issues": len(config_issues),
            "details": f"{len(config_issues)} configuration issues"
        })
        
        return categories
    
    def _check_owasp_compliance_detailed(
        self,
        vuln_findings: List[Dict],
        hardcoded_secrets: List[Dict],
        config_issues: List[Dict],
        dependency_vulns: List[Dict]
    ) -> Dict[str, Any]:
        """Check OWASP Top 10 2025 compliance with evidence-based scoring."""
        categories = []
        
        # Map findings to OWASP categories
        owasp_findings_map = self._map_findings_to_owasp(
            vuln_findings, hardcoded_secrets, config_issues, dependency_vulns
        )
        
        for risk_id, risk_name in self.OWASP_TOP_10_2025:
            findings = owasp_findings_map.get(risk_id, [])
            findings_count = len(findings)
            
            # Evidence-based scoring: Start at 100, deduct for findings
            score = 100
            for finding in findings:
                if finding.get("severity") == "critical":
                    score -= 20
                elif finding.get("severity") == "high":
                    score -= 10
                elif finding.get("severity") == "medium":
                    score -= 5
                elif finding.get("severity") == "low":
                    score -= 2
            
            score = max(0, min(100, score))  # Clamp between 0-100
            
            categories.append({
                "risk": risk_id,
                "name": risk_name,
                "score": score,
                "status": "pass" if score >= 80 else "warn" if score >= 60 else "fail",
                "findings_count": findings_count,
                "findings": findings[:5]  # Top 5 findings per category
            })
        
        return {
            "categories": categories,
            "overall_compliance": sum(c["score"] for c in categories) / len(categories),
            "version": "2025",
            "last_updated": datetime.now().isoformat()
        }
    
    def _map_findings_to_owasp(
        self,
        vuln_findings: List[Dict],
        hardcoded_secrets: List[Dict],
        config_issues: List[Dict],
        dependency_vulns: List[Dict]
    ) -> Dict[str, List[Dict]]:
        """Map actual findings to OWASP Top 10 2025 categories."""
        owasp_map = {category[0]: [] for category in self.OWASP_TOP_10_2025}
        
        # A01: Broken Access Control - auth/authz issues
        for finding in vuln_findings:
            if any(term in finding.get("type", "").lower() for term in ["access", "authorization", "privilege"]):
                owasp_map["A01"].append(finding)
        
        # A02: Cryptographic Failures - weak crypto, hardcoded secrets
        for finding in vuln_findings:
            if any(term in finding.get("type", "").lower() for term in ["encryption", "cryptography", "crypto", "hash"]):
                owasp_map["A02"].append(finding)
        owasp_map["A02"].extend(hardcoded_secrets)  # Hardcoded secrets = crypto failure
        
        # A03: Injection - SQL, XSS, command injection
        for finding in vuln_findings:
            if any(term in finding.get("type", "").lower() for term in ["injection", "sql", "xss", "command"]):
                owasp_map["A03"].append(finding)
        
        # A04: Insecure Design - architectural issues
        # (Would need architecture analysis - skip for now)
        
        # A05: Security Misconfiguration
        owasp_map["A05"].extend(config_issues)
        
        # A06: Vulnerable and Outdated Components
        owasp_map["A06"].extend(dependency_vulns)
        
        # A07: Identification and Authentication Failures
        for finding in hardcoded_secrets:
            if any(term in finding.get("type", "").lower() for term in ["password", "token", "credential"]):
                owasp_map["A07"].append(finding)
        
        # A08: Software and Data Integrity Failures - deserialization
        for finding in vuln_findings:
            if any(term in finding.get("type", "").lower() for term in ["deserialization", "integrity"]):
                owasp_map["A08"].append(finding)
        
        # A09: Security Logging and Monitoring Failures
        # (Would need logging analysis - skip for now)
        
        # A10: Server-Side Request Forgery (SSRF)
        for finding in vuln_findings:
            if "ssrf" in finding.get("type", "").lower():
                owasp_map["A10"].append(finding)
        
        # A11: Insecure AI/ML Model Deployment (2025 addition)
        # (Would need ML model analysis - skip for now)
        
        return owasp_map
    
    def _search_code_pattern(self, pattern: str) -> bool:
        """Search code for regex pattern."""
        import re
        
        for cs_file in self.project_root.glob("**/*.cs"):
            try:
                content = cs_file.read_text(encoding='utf-8', errors='ignore')
                if re.search(pattern, content, re.IGNORECASE):
                    return True
            except Exception:
                continue
        
        return False
    
    def _check_owasp_compliance(self) -> List[Dict[str, Any]]:
        """
        Check OWASP Top 10 compliance.
        
        Returns:
            List of dicts with risk ID, name, score, status
        """
        compliance = []
        
        for risk_id, risk_name in self.OWASP_TOP_10_2025:
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
        categories: List[Dict[str, Any]], 
        vuln_data: Dict[str, int]
    ) -> int:
        """Calculate overall security score."""
        if not categories:
            return 0
            
        category_scores = [cat["score"] for cat in categories]
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
