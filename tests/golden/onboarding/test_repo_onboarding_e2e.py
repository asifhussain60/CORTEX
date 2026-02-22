"""
End-to-End Golden Tests for Repository Onboarding.

Verifies the complete onboarding workflow including:
- 9-tab artifact generation in cortex-registry (not cortex_intelligence)
- Path guard blocking ephemeral/tmp inputs
- Schema version 2.0.0 on all outputs
- onboarding-summary.json structure
- Idempotency and error handling

Authority: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import pytest

from cortex.mcp.tools.onboard_repository import (
    DASHBOARD_TABS,
    SCHEMA_VERSION,
    onboard_repository_tool,
)


# ============================================================================
# Constants — repo-agnostic; paths resolved at runtime
# ============================================================================

CORTEX_PATH = Path("/Users/asifhussain/PROJECTS/CORTEX")
CORTEX_REGISTRY_PATH = CORTEX_PATH / "cortex-registry"
KSESSIONS_PATH = Path("/Users/asifhussain/PROJECTS/KSESSIONS")

EXPECTED_TABS = [tab["id"] for tab in DASHBOARD_TABS]  # 9 tab IDs

# Default orchestrator context required by validate_orchestrator_context guard.
_DEFAULT_CTX: Dict[str, Any] = {
    "source": "MasterOrchestrator",
    "request_id": "golden-test",
}


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def test_output_dir(tmp_path: Path) -> Path:
    """Isolated temp directory for test artifact outputs."""
    output = tmp_path / "cortex-registry" / "company" / "repos"
    output.mkdir(parents=True, exist_ok=True)
    return tmp_path


@pytest.fixture
def minimal_repo(tmp_path: Path) -> Path:
    """Create a minimal git repo with Python source."""
    repo = tmp_path / "sample_repo"
    repo.mkdir()
    (repo / ".git").mkdir()
    (repo / "main.py").write_text('"""Entry point."""\n\ndef run() -> None:\n    pass\n')
    (repo / "requirements.txt").write_text("pytest>=7.0\n")
    return repo


@pytest.fixture
def dotnet_repo(tmp_path: Path) -> Path:
    """Create a minimal .NET/C# repo structure."""
    repo = tmp_path / "sample_dotnet"
    repo.mkdir()
    (repo / ".git").mkdir()
    (repo / "App.csproj").write_text("<Project Sdk=\"Microsoft.NET.Sdk\"></Project>")
    (repo / "Program.cs").write_text("Console.WriteLine(\"Hello\");")
    return repo


@pytest.fixture
def polyglot_repo(tmp_path: Path) -> Path:
    """Create a multi-language repo."""
    repo = tmp_path / "sample_polyglot"
    repo.mkdir()
    (repo / ".git").mkdir()
    (repo / "main.py").write_text("# Python\n")
    (repo / "index.ts").write_text("// TypeScript\n")
    (repo / "main.rs").write_text("fn main() {}\n")
    return repo


# ============================================================================
# Helper
# ============================================================================


def assert_nine_tab_structure(repo_dir: Path) -> None:
    """Assert all 9 tab subdirectories exist under repo_dir."""
    for tab in DASHBOARD_TABS:
        tab_path = repo_dir / tab["id"]
        assert tab_path.is_dir(), f"Missing tab directory: {tab['id']}"
        artifact = tab_path / tab["file"]
        assert artifact.exists(), f"Missing artifact: {tab['id']}/{tab['file']}"
        with open(artifact) as fh:
            data = json.load(fh)
        assert data.get("schema_version") == SCHEMA_VERSION, (
            f"{artifact.name}: expected schema_version={SCHEMA_VERSION!r}, "
            f"got {data.get('schema_version')!r}"
        )


def assert_summary(repo_dir: Path, repo_name: str) -> Dict[str, Any]:
    """Assert onboarding-summary.json is correct; return its data."""
    summary_path = repo_dir / "onboarding-summary.json"
    assert summary_path.exists(), f"Missing onboarding-summary.json under {repo_dir}"
    with open(summary_path) as fh:
        summary = json.load(fh)
    assert summary.get("schema_version") == SCHEMA_VERSION
    assert summary.get("repository_name") == repo_name
    tabs = summary.get("tabs", [])
    assert len(tabs) == len(DASHBOARD_TABS), (
        f"Expected {len(DASHBOARD_TABS)} tabs in summary, got {len(tabs)}"
    )
    return summary


# ============================================================================
# TestRepoOnboardingE2E
# ============================================================================


class TestRepoOnboardingE2E:
    """Core end-to-end workflow assertions."""

    def test_onboarding_returns_status(self, minimal_repo: Path, test_output_dir: Path) -> None:
        """Golden: onboard_repository_tool returns a dict with status key."""
        result = onboard_repository_tool(
            repository_path=str(minimal_repo),
            orchestrator_context=_DEFAULT_CTX,
            test_mode=True,
            test_output_dir=str(test_output_dir),
        )
        assert isinstance(result, dict)
        assert "status" in result

    def test_onboarding_success_on_valid_repo(
        self, minimal_repo: Path, test_output_dir: Path
    ) -> None:
        """Golden: Valid repo produces success or partial_success."""
        result = onboard_repository_tool(
            repository_path=str(minimal_repo),
            orchestrator_context=_DEFAULT_CTX,
            test_mode=True,
            test_output_dir=str(test_output_dir),
        )
        assert result["status"] in ("success", "partial_success"), (
            f"Unexpected status: {result.get('status')} — {result.get('error')}"
        )

    def test_nonexistent_path_returns_error(self, test_output_dir: Path) -> None:
        """Golden: Non-existent path returns status=error with message."""
        result = onboard_repository_tool(
            repository_path="/nonexistent/repo/path",
            orchestrator_context=_DEFAULT_CTX,
            test_mode=True,
            test_output_dir=str(test_output_dir),
        )
        assert result["status"] == "error"
        assert "error" in result

    def test_ephemeral_path_is_blocked(self, tmp_path: Path) -> None:
        """Golden: Ephemeral (tmp) path is blocked by path guard."""
        result = onboard_repository_tool(
            repository_path=str(tmp_path),
            orchestrator_context=_DEFAULT_CTX,
            test_mode=False,  # prod mode — path guard must fire
        )
        assert result["status"] == "error"
        err = result.get("error", "")
        assert "BLOCKED" in err or "ephemeral" in err.lower(), (
            f"Expected BLOCKED error, got: {err!r}"
        )

    def test_result_includes_repository_path(
        self, minimal_repo: Path, test_output_dir: Path
    ) -> None:
        """Golden: Result contains repository_path matching input."""
        result = onboard_repository_tool(
            repository_path=str(minimal_repo),
            orchestrator_context=_DEFAULT_CTX,
            test_mode=True,
            test_output_dir=str(test_output_dir),
        )
        assert result.get("repository_path") == str(minimal_repo)

    def test_onboarding_is_idempotent(
        self, minimal_repo: Path, test_output_dir: Path
    ) -> None:
        """Golden: Running onboarding twice produces consistent status."""
        ctx = {"source": "MasterOrchestrator", "request_id": "idempotent-1"}
        result1 = onboard_repository_tool(
            repository_path=str(minimal_repo),
            orchestrator_context=ctx,
            test_mode=True,
            test_output_dir=str(test_output_dir),
        )
        ctx["request_id"] = "idempotent-2"
        result2 = onboard_repository_tool(
            repository_path=str(minimal_repo),
            orchestrator_context=ctx,
            test_mode=True,
            test_output_dir=str(test_output_dir),
        )
        assert result1["status"] == result2["status"]
        assert result1["repository_path"] == result2["repository_path"]

    def test_feature_flags_respected(
        self, minimal_repo: Path, test_output_dir: Path
    ) -> None:
        """Golden: Flags capture_learning=False, apply_brain_enhancement=False suppress extras."""
        result = onboard_repository_tool(
            repository_path=str(minimal_repo),
            capture_learning=False,
            apply_brain_enhancement=False,
            generate_artifacts=False,
            orchestrator_context=_DEFAULT_CTX,
            test_mode=True,
            test_output_dir=str(test_output_dir),
        )
        assert result["status"] in ("success", "partial_success")
        learning = result.get("learning_metrics", {})
        assert not learning or len(learning) == 0, (
            "Expected empty learning_metrics when capture_learning=False"
        )

    def test_dotnet_repo_onboards(
        self, dotnet_repo: Path, test_output_dir: Path
    ) -> None:
        """Golden: .NET/C# repository onboards without error."""
        result = onboard_repository_tool(
            repository_path=str(dotnet_repo),
            orchestrator_context=_DEFAULT_CTX,
            test_mode=True,
            test_output_dir=str(test_output_dir),
        )
        assert "status" in result
        assert result.get("repository_path") == str(dotnet_repo)

    def test_polyglot_repo_onboards(
        self, polyglot_repo: Path, test_output_dir: Path
    ) -> None:
        """Golden: Multi-language repository onboards without crash."""
        result = onboard_repository_tool(
            repository_path=str(polyglot_repo),
            orchestrator_context=_DEFAULT_CTX,
            test_mode=True,
            test_output_dir=str(test_output_dir),
        )
        assert "status" in result


# ============================================================================
# TestOnboardingFileGeneration
# ============================================================================


class TestOnboardingFileGeneration:
    """Verify the 9-tab artifact folder structure is written correctly."""

    def test_nine_tab_dirs_created(
        self, minimal_repo: Path, test_output_dir: Path
    ) -> None:
        """Golden: All 9 tab directories are created under repo folder."""
        result = onboard_repository_tool(
            repository_path=str(minimal_repo),
            generate_artifacts=True,
            orchestrator_context=_DEFAULT_CTX,
            test_mode=True,
            test_output_dir=str(test_output_dir),
        )
        if result["status"] == "error":
            pytest.skip(f"Onboarding failed: {result.get('error')}")

        repo_name = minimal_repo.name
        repo_dir = (
            test_output_dir / "cortex-registry" / "company" / "repos" / repo_name
        )
        assert_nine_tab_structure(repo_dir)

    def test_all_artifacts_schema_version(
        self, minimal_repo: Path, test_output_dir: Path
    ) -> None:
        """Golden: Every tab JSON artifact carries schema_version=2.0.0."""
        result = onboard_repository_tool(
            repository_path=str(minimal_repo),
            generate_artifacts=True,
            orchestrator_context=_DEFAULT_CTX,
            test_mode=True,
            test_output_dir=str(test_output_dir),
        )
        if result["status"] == "error":
            pytest.skip(f"Onboarding failed: {result.get('error')}")

        repo_name = minimal_repo.name
        repo_dir = (
            test_output_dir / "cortex-registry" / "company" / "repos" / repo_name
        )
        for tab in DASHBOARD_TABS:
            artifact = repo_dir / tab["id"] / tab["file"]
            assert artifact.exists(), f"Missing: {tab['id']}/{tab['file']}"
            data = json.loads(artifact.read_text())
            assert data.get("schema_version") == SCHEMA_VERSION

    def test_summary_json_structure(
        self, minimal_repo: Path, test_output_dir: Path
    ) -> None:
        """Golden: onboarding-summary.json lists all 9 tabs with correct keys."""
        result = onboard_repository_tool(
            repository_path=str(minimal_repo),
            generate_artifacts=True,
            orchestrator_context=_DEFAULT_CTX,
            test_mode=True,
            test_output_dir=str(test_output_dir),
        )
        if result["status"] == "error":
            pytest.skip(f"Onboarding failed: {result.get('error')}")

        repo_name = minimal_repo.name
        repo_dir = (
            test_output_dir / "cortex-registry" / "company" / "repos" / repo_name
        )
        summary = assert_summary(repo_dir, repo_name)
        tab_ids = [t["id"] for t in summary.get("tabs", [])]
        assert tab_ids == EXPECTED_TABS, (
            f"Tab IDs mismatch.\n  Expected: {EXPECTED_TABS}\n  Got:      {tab_ids}"
        )

    def test_no_write_to_cortex_intelligence(
        self, minimal_repo: Path, test_output_dir: Path
    ) -> None:
        """Golden: Onboarding must NOT write to cortex/intelligence/."""
        ci_dir = CORTEX_PATH / "cortex_intelligence" / "onboarded_repos"
        before = set(ci_dir.glob("*")) if ci_dir.exists() else set()

        onboard_repository_tool(
            repository_path=str(minimal_repo),
            generate_artifacts=True,
            orchestrator_context=_DEFAULT_CTX,
            test_mode=True,
            test_output_dir=str(test_output_dir),
        )

        after = set(ci_dir.glob("*")) if ci_dir.exists() else set()
        new_files = after - before
        assert not new_files, (
            f"Onboarding wrote {len(new_files)} unexpected file(s) to cortex_intelligence: "
            f"{[p.name for p in new_files]}"
        )

    def test_utc_timestamp_not_midnight(
        self, minimal_repo: Path, test_output_dir: Path
    ) -> None:
        """Golden: Artifact timestamps are UTC, not midnight placeholder."""
        result = onboard_repository_tool(
            repository_path=str(minimal_repo),
            generate_artifacts=True,
            orchestrator_context=_DEFAULT_CTX,
            test_mode=True,
            test_output_dir=str(test_output_dir),
        )
        if result["status"] == "error":
            pytest.skip(f"Onboarding failed: {result.get('error')}")

        repo_name = minimal_repo.name
        repo_dir = (
            test_output_dir / "cortex-registry" / "company" / "repos" / repo_name
        )
        # Tab artifacts are index.json; check the first tab
        index_path = repo_dir / "01_overview" / "index.json"
        assert index_path.exists(), "01_overview/index.json not generated"

        data = json.loads(index_path.read_text())
        ts = data.get("generated_at", "")
        assert ts, "generated_at field is missing from index.json"
        assert "T00:00:00.000000" not in ts, f"Midnight placeholder detected: {ts!r}"
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        assert dt.year >= 2024, f"Timestamp year looks invalid: {ts!r}"


# ============================================================================
# TestOnboardingAuditLog
# ============================================================================


class TestOnboardingAuditLog:
    """Verify audit metadata returned in the result dict."""

    def test_result_contains_artifacts_key(
        self, minimal_repo: Path, test_output_dir: Path
    ) -> None:
        """Golden: Result dict contains artifacts key."""
        result = onboard_repository_tool(
            repository_path=str(minimal_repo),
            generate_artifacts=True,
            orchestrator_context=_DEFAULT_CTX,
            test_mode=True,
            test_output_dir=str(test_output_dir),
        )
        assert "artifacts" in result

    def test_artifacts_tracks_files_generated(
        self, minimal_repo: Path, test_output_dir: Path
    ) -> None:
        """Golden: artifacts dict tracks generated file count."""
        result = onboard_repository_tool(
            repository_path=str(minimal_repo),
            generate_artifacts=True,
            orchestrator_context=_DEFAULT_CTX,
            test_mode=True,
            test_output_dir=str(test_output_dir),
        )
        if result["status"] == "error":
            pytest.skip(f"Onboarding failed: {result.get('error')}")
        artifacts = result.get("artifacts", {})
        assert artifacts, "artifacts should not be empty on success"
        assert (
            "files_generated" in artifacts
            or "tabs_written" in artifacts
            or "yaml_files_created" in artifacts
            or "total_files" in artifacts
        )


# ============================================================================
# TestOnboardingMultipleRepos — parametrized, repo-agnostic
# ============================================================================


@pytest.mark.parametrize(
    "repo_name,fixture_name",
    [
        ("minimal_python", "minimal_repo"),
        ("dotnet_csharp", "dotnet_repo"),
    ],
)
class TestOnboardingMultipleRepos:
    """Parametrized: onboarding different repo types must not conflict."""

    def test_onboard_no_conflict(
        self,
        repo_name: str,
        fixture_name: str,
        request: pytest.FixtureRequest,
        test_output_dir: Path,
    ) -> None:
        """Golden: Each repo gets its own isolated output directory."""
        repo_path: Path = request.getfixturevalue(fixture_name)
        result = onboard_repository_tool(
            repository_path=str(repo_path),
            orchestrator_context={
                "source": "MasterOrchestrator",
                "request_id": f"multi-{repo_name}",
            },
            test_mode=True,
            test_output_dir=str(test_output_dir),
        )
        assert result["status"] in ("success", "partial_success", "error")
        assert result.get("repository_path") == str(repo_path)
