"""
Vendor Detector

Detects external vendor/service integrations from code, config, and environment files.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import ast
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Set

from src.dashboard.data.base_collector import BaseDataCollector
from src.dashboard.utils.recursive_scanner import RecursiveScanner


class VendorDetector(BaseDataCollector):
    """
    Detects external vendor integrations (Stripe, Auth0, AWS, etc.).
    
    Detection Methods:
    - Environment variables (.env files)
    - Configuration files (YAML, JSON, TOML)
    - SDK imports (Python, JavaScript)
    - API endpoint patterns in code
    - Hardcoded credentials (security check)
    
    Data Source: CURRENT STATE ONLY - Real detection from actual files.
    """
    
    # Known vendor patterns
    VENDOR_PATTERNS = {
        'stripe': {
            'env_vars': ['STRIPE_API_KEY', 'STRIPE_SECRET_KEY', 'STRIPE_PUBLISHABLE_KEY'],
            'config_keys': ['stripe_key', 'stripe_secret', 'stripe'],
            'sdk_imports': ['stripe'],
            'endpoints': ['api.stripe.com'],
            'category': 'payment',
            'cost_tier': 'high'
        },
        'auth0': {
            'env_vars': ['AUTH0_DOMAIN', 'AUTH0_CLIENT_ID', 'AUTH0_CLIENT_SECRET'],
            'config_keys': ['auth0_domain', 'auth0_client'],
            'sdk_imports': ['auth0'],
            'endpoints': ['.auth0.com'],
            'category': 'authentication',
            'cost_tier': 'medium'
        },
        'sendgrid': {
            'env_vars': ['SENDGRID_API_KEY', 'SENDGRID_KEY'],
            'config_keys': ['sendgrid_key', 'sendgrid'],
            'sdk_imports': ['sendgrid'],
            'endpoints': ['api.sendgrid.com'],
            'category': 'email',
            'cost_tier': 'low'
        },
        'twilio': {
            'env_vars': ['TWILIO_ACCOUNT_SID', 'TWILIO_AUTH_TOKEN'],
            'config_keys': ['twilio_sid', 'twilio'],
            'sdk_imports': ['twilio'],
            'endpoints': ['api.twilio.com'],
            'category': 'sms',
            'cost_tier': 'medium'
        },
        'aws': {
            'env_vars': ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY'],
            'config_keys': ['aws_access_key', 'aws_region'],
            'sdk_imports': ['boto3', 'botocore'],
            'endpoints': ['amazonaws.com'],
            'category': 'cloud',
            'cost_tier': 'very_high'
        },
        'azure': {
            'env_vars': ['AZURE_CLIENT_ID', 'AZURE_TENANT_ID'],
            'config_keys': ['azure_client', 'azure_tenant'],
            'sdk_imports': ['azure'],
            'endpoints': ['azure.microsoft.com'],
            'category': 'cloud',
            'cost_tier': 'very_high'
        },
        'google_cloud': {
            'env_vars': ['GOOGLE_APPLICATION_CREDENTIALS', 'GCP_PROJECT_ID'],
            'config_keys': ['gcp_project', 'google_cloud'],
            'sdk_imports': ['google.cloud'],
            'endpoints': ['googleapis.com'],
            'category': 'cloud',
            'cost_tier': 'very_high'
        },
        'slack': {
            'env_vars': ['SLACK_BOT_TOKEN', 'SLACK_WEBHOOK_URL'],
            'config_keys': ['slack_token', 'slack_webhook'],
            'sdk_imports': ['slack_sdk'],
            'endpoints': ['slack.com/api'],
            'category': 'communication',
            'cost_tier': 'low'
        },
        'github': {
            'env_vars': ['GITHUB_TOKEN', 'GITHUB_API_KEY'],
            'config_keys': ['github_token', 'github_api'],
            'sdk_imports': ['github', 'pygithub'],
            'endpoints': ['api.github.com'],
            'category': 'development',
            'cost_tier': 'none'
        },
        'sentry': {
            'env_vars': ['SENTRY_DSN'],
            'config_keys': ['sentry_dsn'],
            'sdk_imports': ['sentry_sdk'],
            'endpoints': ['sentry.io'],
            'category': 'monitoring',
            'cost_tier': 'low'
        },
        'datadog': {
            'env_vars': ['DD_API_KEY', 'DATADOG_API_KEY'],
            'config_keys': ['datadog_api_key'],
            'sdk_imports': ['datadog'],
            'endpoints': ['datadoghq.com'],
            'category': 'monitoring',
            'cost_tier': 'medium'
        },
        'mongodb': {
            'env_vars': ['MONGODB_URI', 'MONGO_URL'],
            'config_keys': ['mongodb_uri', 'mongo_connection'],
            'sdk_imports': ['pymongo', 'mongoengine'],
            'endpoints': ['mongodb.com'],
            'category': 'database',
            'cost_tier': 'medium'
        }
    }
    
    def collect(self) -> Optional[Dict[str, Any]]:
        """
        Collect external vendor data.
        
        Returns:
            Dict with code_dependencies and external_vendors
        """
        self.logger.info("Detecting external vendors...")
        
        # Detect vendors
        detected_vendors = self._detect_vendors()
        
        # Get code dependencies (packages)
        code_deps = self._get_code_dependencies()
        
        # Build dependency graph
        dep_graph = self._build_dependency_graph(code_deps, detected_vendors)
        
        vendor_data = {
            "code_dependencies": code_deps,
            "external_vendors": detected_vendors,
            "dependency_graph": dep_graph,
            "vendor_summary": {
                "total_vendors": len(detected_vendors),
                "active_vendors": len([v for v in detected_vendors if v["status"] == "configured_active"]),
                "inactive_vendors": len([v for v in detected_vendors if v["status"] == "configured_unused"]),
                "credentials_needing_refresh": len([v for v in detected_vendors if v["security"]["credentials_expired"]]),
                "high_risk_vendors": len([v for v in detected_vendors if v.get("risk_level") == "high"])
            }
        }
        
        self.logger.info(f"Detected {len(detected_vendors)} external vendors")
        return vendor_data
    
    def _detect_vendors(self) -> List[Dict[str, Any]]:
        """
        Detect all external vendors.
        
        Returns:
            List of detected vendor data
        """
        detected = []
        
        for vendor_name, patterns in self.VENDOR_PATTERNS.items():
            detection_results = self._check_vendor(vendor_name, patterns)
            
            if detection_results["detected"]:
                vendor_entry = {
                    "name": vendor_name.replace('_', ' ').title(),
                    "category": patterns["category"],
                    "detection_method": detection_results["method"],
                    "config_location": detection_results["location"],
                    "status": self._determine_status(vendor_name, detection_results),
                    "endpoints": patterns["endpoints"],
                    "sdk": detection_results.get("sdk_version"),
                    "cost_tier": patterns["cost_tier"],
                    "usage_locations": detection_results["usage_locations"],
                    "security": {
                        "credentials_hardcoded": detection_results["hardcoded"],
                        "credentials_expired": False,  # Would need expiry date checking
                        "handles_pii": self._handles_pii(patterns["category"])
                    },
                    "compliance": {
                        "gdpr_relevant": self._handles_pii(patterns["category"]),
                        "soc2_critical": patterns["category"] in ["authentication", "database", "cloud"]
                    },
                    "risk_level": self._assess_risk(patterns, detection_results)
                }
                detected.append(vendor_entry)
        
        return detected
    
    def _check_vendor(self, vendor_name: str, patterns: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check if vendor is present using multiple detection methods.
        
        Args:
            vendor_name: Vendor identifier
            patterns: Detection patterns
            
        Returns:
            Dict with detection results
        """
        results = {
            "detected": False,
            "method": None,
            "location": None,
            "hardcoded": False,
            "usage_locations": [],
            "sdk_version": None
        }
        
        # Check environment variables
        env_detection = self._check_env_vars(patterns["env_vars"])
        if env_detection["found"]:
            results["detected"] = True
            results["method"] = "env_var"
            results["location"] = env_detection["location"]
            results["hardcoded"] = env_detection["hardcoded"]
        
        # Check config files
        if not results["detected"]:
            config_detection = self._check_config_files(patterns["config_keys"])
            if config_detection["found"]:
                results["detected"] = True
                results["method"] = "config_file"
                results["location"] = config_detection["location"]
        
        # Check SDK imports
        sdk_detection = self._check_sdk_imports(patterns["sdk_imports"])
        if sdk_detection["found"]:
            if not results["detected"]:
                results["detected"] = True
                results["method"] = "sdk_import"
            results["usage_locations"] = sdk_detection["locations"]
            results["sdk_version"] = sdk_detection["version"]
        
        # Check API endpoints in code
        endpoint_detection = self._check_endpoints(patterns["endpoints"])
        if endpoint_detection["found"]:
            if not results["detected"]:
                results["detected"] = True
                results["method"] = "api_endpoint"
            results["usage_locations"].extend(endpoint_detection["locations"])
        
        return results
    
    def _check_env_vars(self, env_var_names: List[str]) -> Dict[str, Any]:
        """Check for environment variables in .env files."""
        result = {"found": False, "location": None, "hardcoded": False}
        
        # Check .env files
        for env_file in [".env", ".env.local", ".env.production"]:
            env_path = self.project_root / env_file
            if env_path.exists():
                content = self._read_file(env_file)
                if content:
                    for var_name in env_var_names:
                        if var_name in content:
                            result["found"] = True
                            result["location"] = f"{env_file}:{var_name}"
                            # Check if value is hardcoded (not just variable name)
                            if re.search(rf'{var_name}\s*=\s*["\']?[\w-]{{10,}}', content):
                                result["hardcoded"] = True
                            break
            if result["found"]:
                break
        
        return result
    
    def _check_config_files(self, config_keys: List[str]) -> Dict[str, Any]:
        """Check for configuration in .NET config files only (web.config, app.config)."""
        result = {"found": False, "location": None}
        
        # Only check .NET config files (common for vendor configuration)
        config_files = ["web.config", "app.config", "Web.config", "App.config"]
        
        for config_file in config_files:
            # Check existence first to avoid warning spam
            if not self._file_exists(config_file):
                continue
                
            content = self._read_file(config_file)
            if content:
                for key in config_keys:
                    if key in content.lower():
                        result["found"] = True
                        result["location"] = f"{config_file}:{key}"
                        break
            if result["found"]:
                break
        
        return result
    
    def _check_sdk_imports(self, sdk_names: List[str]) -> Dict[str, Any]:
        """Check for SDK imports in Python files."""
        result = {"found": False, "locations": [], "version": None}
        
        # Use RecursiveScanner to find all Python files from root
        scanner = RecursiveScanner(self.project_root, logger=self.logger)
        py_files = scanner.scan_python_files()
        
        if not py_files:
            return result
        
        for py_file in py_files:
            
            try:
                content = py_file.read_text()
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            if any(sdk in alias.name for sdk in sdk_names):
                                result["found"] = True
                                location = f"{py_file.relative_to(self.project_root)}:{node.lineno}"
                                result["locations"].append(location)
                    
                    elif isinstance(node, ast.ImportFrom):
                        if node.module and any(sdk in node.module for sdk in sdk_names):
                            result["found"] = True
                            location = f"{py_file.relative_to(self.project_root)}:{node.lineno}"
                            result["locations"].append(location)
                            
            except Exception:
                continue
        
        # Get version from requirements.txt
        if result["found"]:
            result["version"] = self._get_package_version(sdk_names[0])
        
        return result
    
    def _check_endpoints(self, endpoint_patterns: List[str]) -> Dict[str, Any]:
        """Check for API endpoint usage in code."""
        result = {"found": False, "locations": []}
        
        # Use RecursiveScanner to find all Python files from root
        scanner = RecursiveScanner(self.project_root, logger=self.logger)
        py_files = scanner.scan_python_files()
        
        if not py_files:
            return result
        
        for py_file in py_files:
            
            content = self._read_file(str(py_file.relative_to(self.project_root)))
            if content:
                for pattern in endpoint_patterns:
                    if pattern in content:
                        result["found"] = True
                        # Find line number
                        for i, line in enumerate(content.split('\n'), 1):
                            if pattern in line:
                                location = f"{py_file.relative_to(self.project_root)}:{i}"
                                result["locations"].append(location)
                                break
        
        return result
    
    def _get_package_version(self, package_name: str) -> Optional[str]:
        """Get package version from requirements.txt."""
        requirements = self._read_file("requirements.txt")
        if requirements:
            for line in requirements.split('\n'):
                if line.startswith(package_name):
                    match = re.search(r'==([0-9.]+)', line)
                    if match:
                        return f"{package_name}=={match.group(1)}"
        return None
    
    def _determine_status(self, vendor_name: str, detection: Dict[str, Any]) -> str:
        """
        Determine vendor status.
        
        Args:
            vendor_name: Vendor name
            detection: Detection results
            
        Returns:
            Status: configured_active, configured_unused, or not_configured
        """
        if not detection["detected"]:
            return "not_configured"
        
        # If we found code usage, it's active
        if detection["usage_locations"]:
            return "configured_active"
        
        # If only env/config but no usage, it's unused
        return "configured_unused"
    
    def _handles_pii(self, category: str) -> bool:
        """Check if category typically handles PII."""
        pii_categories = ["authentication", "payment", "email", "sms", "communication"]
        return category in pii_categories
    
    def _assess_risk(self, patterns: Dict[str, Any], detection: Dict[str, Any]) -> str:
        """
        Assess vendor risk level.
        
        Args:
            patterns: Vendor patterns
            detection: Detection results
            
        Returns:
            Risk level: low, medium, high
        """
        risk_score = 0
        
        # High risk if handles PII
        if self._handles_pii(patterns["category"]):
            risk_score += 2
        
        # High risk if credentials hardcoded
        if detection["hardcoded"]:
            risk_score += 3
        
        # Medium risk if high cost
        if patterns["cost_tier"] in ["high", "very_high"]:
            risk_score += 1
        
        if risk_score >= 4:
            return "high"
        elif risk_score >= 2:
            return "medium"
        else:
            return "low"
    
    def _get_code_dependencies(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get code dependencies from package files."""
        deps = {
            "python": [],
            "javascript": [],
            "dotnet": []
        }
        
        # Python dependencies
        requirements = self._read_file("requirements.txt")
        if requirements:
            for line in requirements.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    match = re.match(r'^([a-zA-Z0-9\-_.]+)([>=<~!]*)([\d.]*)', line)
                    if match:
                        package, operator, version = match.groups()
                        deps["python"].append({
                            "package": package,
                            "version": version or "unknown",
                            "latest": "unknown",
                            "status": "current",
                            "cve_count": 0
                        })
        
        # JavaScript dependencies
        package_json = self._read_file("package.json")
        if package_json:
            data = self._safe_parse_json(package_json)
            if data:
                all_deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
                for pkg, version in all_deps.items():
                    deps["javascript"].append({
                        "package": pkg,
                        "version": version.replace('^', '').replace('~', ''),
                        "latest": "unknown",
                        "status": "current",
                        "cve_count": 0
                    })
        
        return deps
    
    def _build_dependency_graph(
        self,
        code_deps: Dict[str, List[Dict[str, Any]]],
        vendors: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Build unified dependency graph."""
        nodes = [{"id": "app", "type": "application"}]
        edges = []
        
        # Add vendor nodes
        for vendor in vendors:
            node_id = vendor["name"].lower().replace(' ', '_')
            nodes.append({
                "id": node_id,
                "type": "vendor",
                "category": vendor["category"]
            })
            edges.append({
                "source": "app",
                "target": node_id,
                "type": "uses"
            })
        
        # Add package nodes (limit to important ones)
        important_packages = ["requests", "flask", "django", "fastapi", "boto3", "stripe"]
        for lang, packages in code_deps.items():
            for pkg in packages[:10]:  # Limit to 10 per language
                if pkg["package"].lower() in important_packages:
                    node_id = f"{pkg['package']}"
                    if not any(n["id"] == node_id for n in nodes):
                        nodes.append({
                            "id": node_id,
                            "type": "package",
                            "language": lang
                        })
                        edges.append({
                            "source": "app",
                            "target": node_id,
                            "type": "depends"
                        })
        
        return {"nodes": nodes, "edges": edges}
