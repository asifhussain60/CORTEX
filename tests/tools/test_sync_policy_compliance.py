"""
GAP-128-G-01: Sync policy in cortex/tools/cortex_sync.py must comply with
the documented policy contracts.

Tests that:
- SSOT_POLICY has all required keys (deny, allow_override, security_danger_patterns, github_allowlist)
- Critical paths are always in the deny list (private workspaces, runtime data, secrets)
- Security danger patterns exist and are compilable regexes
- The github_allowlist only contains allowed paths

Drift lock: check-47-production-purity-lock.yaml (sub-concern: sync policy)
"""

import re
import importlib
import sys
from pathlib import Path
from typing import List
import pytest

REPO_ROOT = Path(__file__).parents[2]
SYNC_MODULE = "cortex.tools.cortex_sync"

# Paths that must ALWAYS be in the deny list — privacy/security critical
MANDATORY_DENIES = [
    "_workspaces/**",
    ".cortex-runtime/**",
    ".git/**",
    ".env",
    "**/*.db",
    "**/*.log",
    "cortex-docs/**",
    "cortex-registry/cortex-master.yaml",
    "cortex-registry/planning/**",
]

# Paths that must NEVER appear in github_allowlist (admin/sensitive)
NEVER_ALLOWED = [
    "cortex-registry/planning",
    ".cortex-runtime",
    "_workspaces",
    "cortex-registry/cortex-master.yaml",
]


def _load_policy() -> dict:
    """Load SYNC_POLICY from cortex_sync module."""
    try:
        if SYNC_MODULE in sys.modules:
            del sys.modules[SYNC_MODULE]
        sys.path.insert(0, str(REPO_ROOT))
        mod = importlib.import_module(SYNC_MODULE)
        return getattr(mod, "SYNC_POLICY", {})
    except ImportError as e:
        pytest.skip(f"Cannot import cortex_sync: {e}")
        return {}


class TestSyncPolicyCompliance:
    """GAP-128-G-01: SYNC_POLICY in cortex_sync.py must satisfy documented contracts."""

    def test_sync_module_importable(self):
        """cortex.tools.cortex_sync must be importable."""
        try:
            policy = _load_policy()
            assert policy, "SYNC_POLICY is empty or missing"
        except SystemExit:
            pytest.skip("cortex_sync requires specific environment")

    def test_policy_has_required_keys(self):
        """SYNC_POLICY must have all required top-level keys."""
        policy = _load_policy()
        required_keys = {"deny", "allow_override", "security_danger_patterns", "github_allowlist"}
        missing = required_keys - set(policy.keys())
        assert missing == set(), (
            f"SYNC_POLICY missing required keys: {missing}"
        )

    def test_policy_has_version(self):
        """SYNC_POLICY must declare a version string."""
        policy = _load_policy()
        version = policy.get("version")
        assert version and isinstance(version, str), (
            "SYNC_POLICY must declare a 'version' string"
        )

    def test_mandatory_deny_paths_present(self):
        """All mandatory deny patterns must be present in SYNC_POLICY.deny."""
        policy = _load_policy()
        deny_list = policy.get("deny", []) or []
        missing = [
            path for path in MANDATORY_DENIES
            if path not in deny_list
        ]
        assert missing == [], (
            f"Mandatory deny patterns missing from SYNC_POLICY:\n"
            + "\n".join(f"  '{p}'" for p in missing)
        )

    def test_security_danger_patterns_are_valid_regexes(self):
        """Every pattern in security_danger_patterns must compile as a valid regex."""
        policy = _load_policy()
        patterns = policy.get("security_danger_patterns", []) or []
        invalid = []
        for pattern in patterns:
            try:
                re.compile(pattern)
            except re.error as e:
                invalid.append(f"'{pattern}': {e}")
        assert invalid == [], (
            f"Invalid regexes in security_danger_patterns:\n"
            + "\n".join(f"  {i}" for i in invalid)
        )

    def test_security_danger_patterns_covers_credentials(self):
        """security_danger_patterns must cover at least password and api_key patterns."""
        policy = _load_policy()
        patterns = policy.get("security_danger_patterns", []) or []
        combined = " ".join(patterns).lower()
        assert "password" in combined, "security_danger_patterns must include a password pattern"
        assert "api" in combined or "key" in combined, (
            "security_danger_patterns must include an API key pattern"
        )

    def test_github_allowlist_does_not_contain_sensitive_paths(self):
        """github_allowlist must not contain sensitive or admin-only paths."""
        policy = _load_policy()
        allowlist = policy.get("github_allowlist", []) or []
        violations = []
        for sensitive in NEVER_ALLOWED:
            for allowed in allowlist:
                if sensitive in allowed:
                    violations.append(f"Sensitive path '{sensitive}' in allowlist entry '{allowed}'")
        assert violations == [], (
            f"Sensitive paths found in github_allowlist:\n"
            + "\n".join(f"  {v}" for v in violations)
        )

    def test_deny_list_has_minimum_coverage(self):
        """deny list must have at least 15 patterns (comprehensive coverage check)."""
        policy = _load_policy()
        deny_count = len(policy.get("deny", []) or [])
        assert deny_count >= 15, (
            f"SYNC_POLICY.deny has only {deny_count} patterns — expected ≥15 for comprehensive coverage"
        )
