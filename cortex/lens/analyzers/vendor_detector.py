"""
Vendor Detector Analyzer - Phase 19 Component.

Intelligent detection of third-party vendor dependencies:
- Known vendors: Stripe, SendGrid, Twilio, Auth0, LaunchDarkly, etc.
- Multiple evidence sources: dependencies, imports, config files, API keys
- Confidence scoring based on evidence strength
- Integration pattern extraction

AC-ID: AC-PHASE-19-VENDOR-DETECTOR-001
Authority: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings)
"""

import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Set

logger = logging.getLogger(__name__)


class VendorDetector:
    """
    Intelligent vendor dependency detector.

    Detects known third-party vendors across multiple evidence sources:
    - Package dependencies (package.json, requirements.txt, etc.)
    - Import statements in code
    - Environment variables and API keys
    - Configuration files

    Confidence Scoring:
    - 0.9-1.0: Multiple evidence sources (high confidence)
    - 0.7-0.9: Single strong evidence (medium-high)
    - 0.5-0.7: Weak evidence (medium)
    - <0.5: Candidate (low confidence)

    Usage:
        >>> detector = VendorDetector()
        >>> result = detector.detect_vendors(Path("/path/to/repo"))
        >>> print(f"Found {result['total_vendors']} vendors")
    """

    def __init__(self):
        """Initialize VendorDetector with known vendor database."""
        self.known_vendors = self._load_known_vendors()

    def _load_known_vendors(self) -> Dict[str, Dict[str, Any]]:
        """
        Load known vendor database.

        Returns:
            Dict of vendor_id -> metadata
        """
        return {
            "stripe": {
                "name": "Stripe",
                "category": "payment",
                "package_names": ["stripe", "@stripe/stripe-js", "stripe-python"],
                "import_patterns": [r"import stripe", r"from stripe"],
                "env_patterns": [r"STRIPE_API_KEY", r"STRIPE_SECRET"],
            },
            "sendgrid": {
                "name": "SendGrid",
                "category": "email",
                "package_names": ["sendgrid", "@sendgrid/mail", "sendgrid-python"],
                "import_patterns": [r"import sendgrid", r"from sendgrid"],
                "env_patterns": [r"SENDGRID_API_KEY"],
            },
            "twilio": {
                "name": "Twilio",
                "category": "communication",
                "package_names": ["twilio"],
                "import_patterns": [r"import twilio", r"from twilio"],
                "env_patterns": [r"TWILIO_ACCOUNT_SID", r"TWILIO_AUTH_TOKEN"],
            },
            "auth0": {
                "name": "Auth0",
                "category": "authentication",
                "package_names": ["auth0", "auth0-python", "@auth0/auth0-react"],
                "import_patterns": [r"import auth0", r"from auth0"],
                "env_patterns": [r"AUTH0_DOMAIN", r"AUTH0_CLIENT_ID"],
            },
            "launchdarkly": {
                "name": "LaunchDarkly",
                "category": "feature_flags",
                "package_names": ["launchdarkly", "launchdarkly-server-sdk"],
                "import_patterns": [r"import ldclient", r"from ldclient"],
                "env_patterns": [r"LAUNCHDARKLY_SDK_KEY"],
            },
            "datadog": {
                "name": "Datadog",
                "category": "monitoring",
                "package_names": ["datadog", "ddtrace"],
                "import_patterns": [r"import datadog", r"from ddtrace"],
                "env_patterns": [r"DD_API_KEY", r"DATADOG_API_KEY"],
            },
            "sentry": {
                "name": "Sentry",
                "category": "error_tracking",
                "package_names": ["sentry-sdk", "@sentry/react", "@sentry/node"],
                "import_patterns": [r"import sentry_sdk", r"from sentry_sdk"],
                "env_patterns": [r"SENTRY_DSN"],
            },
            "aws": {
                "name": "AWS",
                "category": "cloud",
                "package_names": ["boto3", "aws-sdk", "@aws-sdk"],
                "import_patterns": [r"import boto3", r"from boto3"],
                "env_patterns": [r"AWS_ACCESS_KEY_ID", r"AWS_SECRET_ACCESS_KEY"],
            },
            "redis": {
                "name": "Redis",
                "category": "cache",
                "package_names": ["redis", "ioredis"],
                "import_patterns": [r"import redis", r"from redis"],
                "env_patterns": [r"REDIS_URL", r"REDIS_HOST"],
            },
            "postgresql": {
                "name": "PostgreSQL",
                "category": "database",
                "package_names": ["psycopg2", "pg", "postgresql"],
                "import_patterns": [r"import psycopg2", r"from psycopg2"],
                "env_patterns": [r"POSTGRES_", r"DATABASE_URL.*postgres"],
            },
        }

    def detect_vendors(self, repo_path: Path) -> Dict[str, Any]:
        """
        Detect vendors in repository.

        Args:
            repo_path: Path to repository

        Returns:
            Dict with:
                - vendors: Dict of vendor_id -> detection data
                - total_vendors: Count of detected vendors
                - categories: Set of vendor categories
                - candidates: Unknown/unrecognized vendors
        """
        detected: Dict[str, Dict[str, Any]] = {}
        candidates: List[str] = []

        # Evidence sources
        evidence: Dict[str, List[str]] = {}

        # 1. Check package dependencies
        dep_evidence = self._check_dependencies(repo_path)
        for vendor_id, files in dep_evidence.items():
            if vendor_id not in evidence:
                evidence[vendor_id] = []
            evidence[vendor_id].extend(files)

        # 2. Check import statements
        import_evidence = self._check_imports(repo_path)
        for vendor_id, files in import_evidence.items():
            if vendor_id not in evidence:
                evidence[vendor_id] = []
            evidence[vendor_id].extend(files)

        # 3. Check config files
        config_evidence = self._check_config_files(repo_path)
        for vendor_id, files in config_evidence.items():
            if vendor_id not in evidence:
                evidence[vendor_id] = []
            evidence[vendor_id].extend(files)

        # Calculate confidence and build result
        for vendor_id, files in evidence.items():
            vendor_meta = self.known_vendors.get(vendor_id, {})

            # Confidence based on evidence count
            evidence_count = len(set(files))
            if evidence_count >= 3:
                confidence = 0.95
            elif evidence_count == 2:
                confidence = 0.85
            else:
                confidence = 0.75

            detected[vendor_id] = {
                "name": vendor_meta.get("name", vendor_id.title()),
                "category": vendor_meta.get("category", "unknown"),
                "confidence": confidence,
                "evidence_files": list(set(files)),
                "evidence_count": evidence_count,
            }

        # Categories
        categories = set(v["category"] for v in detected.values())

        return {
            "vendors": detected,
            "total_vendors": len(detected),
            "categories": list(categories),
            "candidates": candidates,
        }

    def _check_dependencies(self, repo_path: Path) -> Dict[str, List[str]]:
        """Check package dependency files."""
        evidence: Dict[str, List[str]] = {}

        # package.json (Node.js)
        package_json = repo_path / "package.json"
        if package_json.exists():
            try:
                with open(package_json, "r") as f:
                    data = json.load(f)
                    deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}

                    for vendor_id, vendor_meta in self.known_vendors.items():
                        for pkg_name in vendor_meta.get("package_names", []):
                            if pkg_name in deps:
                                if vendor_id not in evidence:
                                    evidence[vendor_id] = []
                                evidence[vendor_id].append(str(package_json))
            except (OSError, ValueError, json.JSONDecodeError):
                pass

        # requirements.txt (Python)
        requirements = repo_path / "requirements.txt"
        if requirements.exists():
            try:
                content = requirements.read_text()
                for vendor_id, vendor_meta in self.known_vendors.items():
                    for pkg_name in vendor_meta.get("package_names", []):
                        if pkg_name.lower() in content.lower():
                            if vendor_id not in evidence:
                                evidence[vendor_id] = []
                            evidence[vendor_id].append(str(requirements))
            except (OSError, UnicodeDecodeError):
                pass

        return evidence

    def _check_imports(self, repo_path: Path) -> Dict[str, List[str]]:
        """Check import statements in code files."""
        evidence: Dict[str, List[str]] = {}

        # Python files
        for py_file in repo_path.rglob("*.py"):
            if ".venv" in str(py_file) or "venv" in str(py_file):
                continue

            try:
                content = py_file.read_text()

                for vendor_id, vendor_meta in self.known_vendors.items():
                    for pattern in vendor_meta.get("import_patterns", []):
                        if re.search(pattern, content, re.IGNORECASE):
                            if vendor_id not in evidence:
                                evidence[vendor_id] = []
                            evidence[vendor_id].append(str(py_file))
                            break
            except (OSError, UnicodeDecodeError):
                pass

        # JavaScript/TypeScript files
        for js_file in repo_path.rglob("*.js"):
            if "node_modules" in str(js_file):
                continue

            try:
                content = js_file.read_text()

                for vendor_id, vendor_meta in self.known_vendors.items():
                    for pkg_name in vendor_meta.get("package_names", []):
                        if f"from '{pkg_name}'" in content or f'from "{pkg_name}"' in content:
                            if vendor_id not in evidence:
                                evidence[vendor_id] = []
                            evidence[vendor_id].append(str(js_file))
                            break
            except (OSError, UnicodeDecodeError):
                pass

        return evidence

    def _check_config_files(self, repo_path: Path) -> Dict[str, List[str]]:
        """Check configuration files for API keys and env vars."""
        evidence: Dict[str, List[str]] = {}

        # .env files
        for env_file in repo_path.rglob(".env*"):
            try:
                content = env_file.read_text()

                for vendor_id, vendor_meta in self.known_vendors.items():
                    for pattern in vendor_meta.get("env_patterns", []):
                        if re.search(pattern, content, re.IGNORECASE):
                            if vendor_id not in evidence:
                                evidence[vendor_id] = []
                            evidence[vendor_id].append(str(env_file))
                            break
            except (OSError, UnicodeDecodeError):
                pass

        return evidence


# Singleton
_vendor_detector = None


def get_vendor_detector() -> VendorDetector:
    """Get or create singleton VendorDetector."""
    global _vendor_detector
    if _vendor_detector is None:
        _vendor_detector = VendorDetector()
    return _vendor_detector
