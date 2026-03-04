"""
Golden tests for cortex/tools/cortex_sync.py — Phase 127 Deterministic Sync Engine.

Validates:
  - Allow/deny policy (SSOT SYNC_POLICY in cortex_sync.py)
  - Idempotency (second run = 0 files written)
  - cortex-docs/ restriction (only .content/ allowed)
  - _workspaces/ exclusion
  - cortex-registry/company/repos/ exclusion
  - Admin prompt exclusion
  - Danger pattern detection
  - Manifest written after --apply

CORE-008: All tests written before/alongside implementation (TDD).
CORE-011: Type hints on all helpers.
CORE-064: All 8 GAP-127-05 scenarios covered — no partial sweep.
"""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Generator

import pytest

# ---------------------------------------------------------------------------
# Import the engine under test
# ---------------------------------------------------------------------------
from cortex.tools.cortex_sync import (
    SYNC_POLICY,
    FileDecision,
    SyncManifest,
    policy_decision,
    run_sync,
    scan_repo,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_run_sync(
    repo_root: Path,
    target: Path,
    dry_run: bool = False,
    write_manifest: bool = False,
) -> SyncManifest:
    """Call run_sync with sensible defaults matching the real signature."""
    baseline_dir = target / ".cortex-sync" / "baselines"
    return run_sync(
        repo_root=repo_root,
        target=target,
        policy=SYNC_POLICY,
        baseline_dir=baseline_dir,
        dry_run=dry_run,
        safe_merge=True,
        extra_deny=[],
        extra_allow=[],
        write_manifest=write_manifest,
    )


def _scan(repo_root: Path) -> list[str]:
    """Return eligible relative paths from scan_repo with default policy."""
    return scan_repo(repo_root, SYNC_POLICY, [])


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def tmp_repo(tmp_path: Path) -> Generator[Path, None, None]:
    """Build a minimal fake CORTEX repo tree for policy testing."""
    repo = tmp_path / "cortex_repo"
    repo.mkdir()

    # Allowed files
    (repo / "cortex").mkdir()
    (repo / "cortex" / "core").mkdir(parents=True)
    (repo / "cortex" / "core" / "master_orchestrator.py").write_text(
        "class MasterOrchestrator: pass\n"
    )
    (repo / "cortex" / "__init__.py").write_text("")
    (repo / "requirements.txt").write_text("pytest>=7\n")
    (repo / "Makefile").write_text("test:\n\tpytest\n")

    # cortex-docs/.content/ — allowed
    (repo / "cortex-docs" / ".content").mkdir(parents=True)
    (repo / "cortex-docs" / ".content" / "guide.md").write_text("# Guide\n")

    # cortex-docs/ root — excluded
    (repo / "cortex-docs" / "index.html").write_text("<html></html>")

    # _workspaces/ — excluded
    (repo / "_workspaces" / "cortex-sts").mkdir(parents=True)
    (repo / "_workspaces" / "cortex-sts" / "config.yaml").write_text("key: val\n")

    # cortex-registry/company/repos/ — excluded
    (repo / "cortex-registry" / "company" / "repos").mkdir(parents=True)
    (repo / "cortex-registry" / "company" / "repos" / "acme.yaml").write_text(
        "repo: acme\n"
    )

    # cortex-registry/company/dashboards/repos/ — excluded
    (repo / "cortex-registry" / "company" / "dashboards" / "repos").mkdir(parents=True)
    (repo / "cortex-registry" / "company" / "dashboards" / "repos" / "dash.yaml").write_text(
        "dash: true\n"
    )

    # Admin prompt — excluded (via deny list)
    (repo / ".github" / "prompts").mkdir(parents=True)
    (repo / ".github" / "prompts" / "cortex-sync.prompt.md").write_text(
        "---\nmode: SYNC\n---\n"
    )

    # .github/workflows — allowed (github_allowlist)
    (repo / ".github" / "workflows").mkdir(parents=True)
    (repo / ".github" / "workflows" / "ci.yml").write_text("on: push\n")

    yield repo


@pytest.fixture()
def tmp_target(tmp_path: Path) -> Path:
    """Empty target directory (simulates company workspace)."""
    target = tmp_path / "company_workspace"
    target.mkdir()
    return target


# ---------------------------------------------------------------------------
# 1. Policy: _workspaces/ must always be excluded
# ---------------------------------------------------------------------------

class TestWorkspacesExclusion:
    def test_workspaces_root_denied(self) -> None:
        """_workspaces/ is in SYNC_POLICY deny list."""
        allowed, reason = policy_decision("_workspaces/cortex-sts/config.yaml", SYNC_POLICY)
        assert not allowed, f"Expected _workspaces to be denied, got: allowed=True reason={reason}"

    def test_workspaces_subdir_denied(self) -> None:
        """Deep paths under _workspaces/ must also be denied."""
        allowed, _ = policy_decision("_workspaces/deep/nested/file.py", SYNC_POLICY)
        assert not allowed

    def test_workspaces_files_not_in_scan(self, tmp_repo: Path) -> None:
        """scan_repo must not yield any _workspaces paths."""
        rel_paths = _scan(tmp_repo)
        workspaces_paths = [p for p in rel_paths if p.startswith("_workspaces")]
        assert workspaces_paths == [], f"_workspaces paths leaked into scan: {workspaces_paths}"


# ---------------------------------------------------------------------------
# 2. Policy: cortex-registry/company/repos/ excluded
# ---------------------------------------------------------------------------

class TestCompanyReposExclusion:
    def test_company_repos_denied(self) -> None:
        """cortex-registry/company/repos/** is in deny list."""
        allowed, reason = policy_decision(
            "cortex-registry/company/repos/acme.yaml", SYNC_POLICY
        )
        assert not allowed, f"Expected company repos to be denied: {reason}"

    def test_company_dashboards_repos_denied(self) -> None:
        """cortex-registry/company/dashboards/repos/** also denied."""
        allowed, _ = policy_decision(
            "cortex-registry/company/dashboards/repos/dash.yaml", SYNC_POLICY
        )
        assert not allowed

    def test_company_repos_not_in_scan(self, tmp_repo: Path) -> None:
        """scan_repo must yield no cortex-registry/company/repos paths."""
        rel_paths = _scan(tmp_repo)
        leaked = [
            p for p in rel_paths
            if "company/repos" in p or "company/dashboards/repos" in p
        ]
        assert leaked == [], f"Company repos leaked into scan: {leaked}"


# ---------------------------------------------------------------------------
# 3. Policy: cortex-docs/ root excluded, .content/ allowed
# ---------------------------------------------------------------------------

class TestCortexDocsRestriction:
    def test_cortex_docs_root_index_denied(self) -> None:
        """cortex-docs/index.html must be excluded (not under .content/)."""
        allowed, reason = policy_decision("cortex-docs/index.html", SYNC_POLICY)
        assert not allowed, f"Expected cortex-docs/index.html to be denied: {reason}"

    def test_cortex_docs_root_any_html_denied(self) -> None:
        """Any file directly in cortex-docs/ root is excluded."""
        allowed, _ = policy_decision("cortex-docs/404.html", SYNC_POLICY)
        assert not allowed

    def test_cortex_docs_content_allowed(self) -> None:
        """cortex-docs/.content/** is allow_overridden."""
        allowed, reason = policy_decision("cortex-docs/.content/guide.md", SYNC_POLICY)
        assert allowed, f"Expected cortex-docs/.content/ to be allowed: {reason}"

    def test_cortex_docs_content_subdirs_allowed(self) -> None:
        """Deep paths under cortex-docs/.content/ must be allowed."""
        allowed, _ = policy_decision(
            "cortex-docs/.content/subdir/deep/page.md", SYNC_POLICY
        )
        assert allowed

    def test_cortex_docs_content_not_excluded_in_scan(self, tmp_repo: Path) -> None:
        """scan_repo must yield the .content/ file but not the root html."""
        rel_paths = _scan(tmp_repo)

        # .content/ guide must be present
        assert "cortex-docs/.content/guide.md" in rel_paths, (
            f".content/guide.md missing from scan. got: {[p for p in rel_paths if 'cortex-docs' in p]}"
        )

        # root html must not be present
        assert "cortex-docs/index.html" not in rel_paths, (
            "cortex-docs/index.html leaked into scan"
        )


# ---------------------------------------------------------------------------
# 4. Admin prompt exclusion
# ---------------------------------------------------------------------------

class TestAdminPromptExclusion:
    def test_sync_prompt_denied(self) -> None:
        """.github/prompts/cortex-sync.prompt.md must never be synced."""
        allowed, reason = policy_decision(
            ".github/prompts/cortex-sync.prompt.md", SYNC_POLICY
        )
        assert not allowed, (
            f"Admin prompt must be excluded. Got allowed=True reason={reason}"
        )

    def test_all_prompts_denied(self) -> None:
        """.github/prompts/ as a whole is in the deny list."""
        for filename in ["cortex-sync.prompt.md", "cortex-architect.prompt.md", "custom.prompt.md"]:
            allowed, _ = policy_decision(f".github/prompts/{filename}", SYNC_POLICY)
            assert not allowed, f".github/prompts/{filename} should be denied"


# ---------------------------------------------------------------------------
# 5. Idempotency — second run produces zero writes
# ---------------------------------------------------------------------------

class TestIdempotency:
    def test_second_run_zero_writes(self, tmp_repo: Path, tmp_target: Path) -> None:
        """Running sync twice must produce 0 new file writes on the second run."""
        # First run: --apply
        manifest1: SyncManifest = _make_run_sync(tmp_repo, tmp_target, write_manifest=True)
        first_written = sum(
            1 for r in manifest1.records
            if r.decision in (FileDecision.COPY, FileDecision.UPDATE, FileDecision.MERGED)
        )
        assert first_written > 0, "First run should have written some files"

        # Second run: --apply again, no repo changes
        manifest2: SyncManifest = _make_run_sync(tmp_repo, tmp_target, write_manifest=True)
        second_written = sum(
            1 for r in manifest2.records
            if r.decision in (FileDecision.COPY, FileDecision.UPDATE, FileDecision.MERGED)
        )
        assert second_written == 0, (
            f"Second run must write 0 files (idempotency). Got {second_written} writes. "
            f"Files: {[r.relative_path for r in manifest2.records if r.decision in (FileDecision.COPY, FileDecision.UPDATE)]}"
        )


# ---------------------------------------------------------------------------
# 6. Danger pattern detection
# ---------------------------------------------------------------------------

class TestDangerPatternDetection:
    def test_aws_key_triggers_danger(self, tmp_repo: Path, tmp_target: Path) -> None:
        """Files containing AWS access key IDs must be flagged as DANGER, not written."""
        danger_file = tmp_repo / "cortex" / "aws_config.py"
        # AKIA{16 uppercase alphanumeric} is the AWS access key ID format
        danger_file.write_text(
            "aws_access_key_id = 'AKIAIOSFODNN7EXAMPLE'\n"
        )

        manifest: SyncManifest = _make_run_sync(tmp_repo, tmp_target)

        danger_records = [
            r for r in manifest.records
            if r.relative_path == "cortex/aws_config.py"
        ]
        assert danger_records, "Danger file record not found in manifest"
        assert danger_records[0].decision == FileDecision.DANGER, (
            f"Expected DANGER, got {danger_records[0].decision}"
        )

        # File must NOT be written to target
        target_file = tmp_target / "cortex" / "aws_config.py"
        assert not target_file.exists(), "DANGER file must not be written to target"

    def test_private_key_triggers_danger(self, tmp_repo: Path, tmp_target: Path) -> None:
        """Files containing -----BEGIN RSA PRIVATE KEY----- must be flagged DANGER."""
        danger_file = tmp_repo / "cortex" / "key.pem"
        danger_file.write_text("-----BEGIN RSA PRIVATE KEY-----\nABCDEF\n-----END RSA PRIVATE KEY-----\n")

        manifest: SyncManifest = _make_run_sync(tmp_repo, tmp_target)

        danger_records = [r for r in manifest.records if r.relative_path == "cortex/key.pem"]
        assert danger_records and danger_records[0].decision == FileDecision.DANGER


# ---------------------------------------------------------------------------
# 7. Manifest written after --apply
# ---------------------------------------------------------------------------

class TestManifestWritten:
    def test_manifest_file_created_after_apply(self, tmp_repo: Path, tmp_target: Path) -> None:
        """manifest.json must exist at .cortex-sync/manifest.json after --apply."""
        _make_run_sync(tmp_repo, tmp_target, write_manifest=True)

        manifest_path = tmp_target / ".cortex-sync" / "manifest.json"
        assert manifest_path.exists(), f"manifest.json not found at {manifest_path}"

        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        assert "records" in data, "manifest.json must contain 'records' key"
        assert "timestamp" in data, "manifest.json must contain 'timestamp' key"
        assert "repo_root" in data, "manifest.json must contain 'repo_root' key"
        assert "target_path" in data, "manifest.json must contain 'target_path' key"

    def test_manifest_not_written_in_dry_run(self, tmp_repo: Path, tmp_target: Path) -> None:
        """manifest.json must NOT be written during --dry-run."""
        _make_run_sync(tmp_repo, tmp_target, dry_run=True, write_manifest=True)

        manifest_path = tmp_target / ".cortex-sync" / "manifest.json"
        assert not manifest_path.exists(), (
            "manifest.json must not be created in dry-run mode"
        )


# ---------------------------------------------------------------------------
# 8. Policy SSOT completeness — all critical deny patterns present
# ---------------------------------------------------------------------------

class TestPolicySSotCompleteness:
    """Ensure SYNC_POLICY dict contains the mandatory deny patterns (Phase 127 SSOT)."""

    def test_workspaces_in_deny_list(self) -> None:
        deny = SYNC_POLICY.get("deny", [])
        assert any("_workspaces" in p for p in deny), (
            f"_workspaces must be in SYNC_POLICY deny list. Got: {deny}"
        )

    def test_company_repos_in_deny_list(self) -> None:
        deny = SYNC_POLICY.get("deny", [])
        assert any("company/repos" in p for p in deny), (
            f"company/repos must be in SYNC_POLICY deny list. Got: {deny}"
        )

    def test_cortex_docs_in_deny_list(self) -> None:
        deny = SYNC_POLICY.get("deny", [])
        assert any("cortex-docs" in p for p in deny), (
            f"cortex-docs must be in SYNC_POLICY deny list. Got: {deny}"
        )

    def test_cortex_docs_content_in_allow_override(self) -> None:
        allow_override = SYNC_POLICY.get("allow_override", [])
        assert any(".content" in p for p in allow_override), (
            f"cortex-docs/.content must be in SYNC_POLICY allow_override. Got: {allow_override}"
        )

    def test_admin_prompts_in_deny_list(self) -> None:
        """.github/prompts/ paths not in github_allowlist must be excluded.

        The engine uses github_allowlist rather than a deny-list entry for
        .github/** paths. Any .github/ path not in the allowlist is blocked.
        Verify the policy decision returns denied for a non-allowlisted prompt.
        """
        # cortex-sync.prompt.md is NOT in github_allowlist → must be denied
        allowed, reason = policy_decision(
            ".github/prompts/cortex-sync.prompt.md", SYNC_POLICY
        )
        assert not allowed, (
            f".github/prompts/cortex-sync.prompt.md must be excluded. "
            f"Got allowed=True reason={reason}"
        )
        # Verify the github_allowlist exists in policy
        allowlist = SYNC_POLICY.get("github_allowlist", [])
        assert allowlist, "SYNC_POLICY must have a github_allowlist"
        # Confirm none of the allowlist entries are cortex-sync.prompt.md
        assert not any("cortex-sync.prompt" in p for p in allowlist), (
            "cortex-sync.prompt.md must NOT be in the github_allowlist"
        )


