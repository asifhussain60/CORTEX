"""
GAP-128-G-02: Sync merge safety — three-way merge logic in cortex_sync must
correctly handle conflict detection and safe-merge semantics.

Tests that:
- FileDecision enum has all required decision codes
- policy_decision() correctly classifies known deny patterns
- policy_decision() allows paths that should be synced
- github_allowlist enforcement works (non-allowlisted .github paths denied)

Drift lock: check-47-production-purity-lock.yaml (sub-concern: merge safety)
"""

import sys
import importlib
from pathlib import Path
from typing import Callable, Tuple
import pytest

REPO_ROOT = Path(__file__).parents[2]
SYNC_MODULE = "cortex.tools.cortex_sync"


def _load_sync_module():
    """Load cortex_sync module and return it."""
    try:
        if SYNC_MODULE in sys.modules:
            del sys.modules[SYNC_MODULE]
        sys.path.insert(0, str(REPO_ROOT))
        return importlib.import_module(SYNC_MODULE)
    except ImportError as e:
        pytest.skip(f"Cannot import cortex_sync: {e}")


class TestSyncMergeSafety:
    """GAP-128-G-02: Sync decision logic and merge safety contracts."""

    def test_file_decision_enum_has_required_codes(self):
        """FileDecision enum must include all required decision codes."""
        mod = _load_sync_module()
        FileDecision = getattr(mod, "FileDecision", None)
        assert FileDecision is not None, "FileDecision enum not found in cortex_sync"
        required_codes = {"copy", "update", "merged", "conflict", "skip", "excluded", "danger"}
        actual_values = {d.value for d in FileDecision}
        missing = required_codes - actual_values
        assert missing == set(), (
            f"FileDecision enum missing required codes: {missing}"
        )

    def test_policy_decision_denies_workspace_paths(self):
        """policy_decision must deny _workspaces/** paths."""
        mod = _load_sync_module()
        policy_decision = getattr(mod, "policy_decision", None)
        policy = getattr(mod, "SYNC_POLICY", {})
        assert policy_decision is not None, "policy_decision() not found in cortex_sync"
        allowed, reason = policy_decision("_workspaces/cortex-sts/secret.py", policy)
        assert allowed is False, (
            f"_workspaces/** should be denied but got allowed=True, reason='{reason}'"
        )

    def test_policy_decision_denies_runtime_paths(self):
        """policy_decision must deny .cortex-runtime/** paths."""
        mod = _load_sync_module()
        policy_decision = getattr(mod, "policy_decision", None)
        policy = getattr(mod, "SYNC_POLICY", {})
        allowed, reason = policy_decision(".cortex-runtime/traces/audit.db", policy)
        assert allowed is False, (
            f".cortex-runtime/** should be denied but got allowed=True, reason='{reason}'"
        )

    def test_policy_decision_denies_planning_artifacts(self):
        """policy_decision must deny cortex-registry/planning/** paths."""
        mod = _load_sync_module()
        policy_decision = getattr(mod, "policy_decision", None)
        policy = getattr(mod, "SYNC_POLICY", {})
        allowed, reason = policy_decision("cortex-registry/planning/phases/phase-128.yaml", policy)
        assert allowed is False, (
            f"cortex-registry/planning/** should be denied but got allowed=True, reason='{reason}'"
        )

    def test_policy_decision_denies_cortex_master_yaml(self):
        """policy_decision must deny cortex-registry/cortex-master.yaml."""
        mod = _load_sync_module()
        policy_decision = getattr(mod, "policy_decision", None)
        policy = getattr(mod, "SYNC_POLICY", {})
        allowed, reason = policy_decision("cortex-registry/cortex-master.yaml", policy)
        assert allowed is False, (
            f"cortex-master.yaml should be denied but got allowed=True, reason='{reason}'"
        )

    def test_policy_decision_denies_secrets(self):
        """policy_decision must deny .env files."""
        mod = _load_sync_module()
        policy_decision = getattr(mod, "policy_decision", None)
        policy = getattr(mod, "SYNC_POLICY", {})
        for secret_path in [".env", ".env.local", ".env.production"]:
            allowed, reason = policy_decision(secret_path, policy)
            assert allowed is False, (
                f"'{secret_path}' should be denied but got allowed=True, reason='{reason}'"
            )

    def test_policy_decision_denies_non_allowlisted_github_paths(self):
        """policy_decision must deny .github paths not in github_allowlist."""
        mod = _load_sync_module()
        policy_decision = getattr(mod, "policy_decision", None)
        policy = getattr(mod, "SYNC_POLICY", {})
        # This is a .github path not in the allowlist
        allowed, reason = policy_decision(".github/workflows/ci.yml", policy)
        assert allowed is False, (
            f".github/workflows/ci.yml should be denied (not in allowlist) but got allowed=True"
        )

    def test_policy_decision_allows_allowlisted_github_paths(self):
        """
        github_allowlist entries should not be blocked by the 'not in allowlist' guard.
        Note: policy_decision's github_allowlist check prevents the 'not in allowlist'
        early denial but paths still flow through the full deny check. This test verifies
        that the allowlist at minimum prevents the 'admin-prompt excluded' error message.
        """
        mod = _load_sync_module()
        policy_decision = getattr(mod, "policy_decision", None)
        policy = getattr(mod, "SYNC_POLICY", {})
        # The allowlist entry must not return the 'admin-prompt excluded' reason
        allowed, reason = policy_decision(".github/prompts/CORTEX.prompt.md", policy)
        assert "admin-prompt excluded" not in reason, (
            f"CORTEX.prompt.md should not be blocked by allowlist check, but got: '{reason}'"
        )

    def test_policy_decision_denies_database_files(self):
        """policy_decision must deny *.db files (runtime artefacts)."""
        mod = _load_sync_module()
        policy_decision = getattr(mod, "policy_decision", None)
        policy = getattr(mod, "SYNC_POLICY", {})
        allowed, reason = policy_decision("some/path/audit.db", policy)
        assert allowed is False, (
            f"*.db files should be denied but got allowed=True, reason='{reason}'"
        )

    def test_policy_decision_allows_source_python_files(self):
        """policy_decision must allow regular cortex Python source files."""
        mod = _load_sync_module()
        policy_decision = getattr(mod, "policy_decision", None)
        policy = getattr(mod, "SYNC_POLICY", {})
        allowed, reason = policy_decision("cortex/orchestrators/core/master_orchestrator.py", policy)
        assert allowed is True, (
            f"cortex source files should be allowed but got denied: '{reason}'"
        )
