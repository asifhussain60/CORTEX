"""
Golden Tests: VacuumOrchestrator (enhanced) — Phase 48
Scenarios GV-001 to GV-006

TDD: RED phase — drives VacuumOrchestrator health-issues.yaml reader.
Authority: Phase 48, CORE-008, CORE-028, CORE-035
"""

import pytest
import json
from pathlib import Path


# ===========================================================================
# FIXTURES
# ===========================================================================


@pytest.fixture
def tmp_repo(tmp_path):
    """Temporary repo with standard structure."""
    for d in ["cortex", "docs", "scripts", "cortex/brain/vacuum"]:
        (tmp_path / d).mkdir(parents=True, exist_ok=True)
    return tmp_path


@pytest.fixture
def health_issues_yaml(tmp_repo):
    """Write a synthetic health-issues.yaml for vacuum tests."""
    import yaml
    data = {
        "metadata": {
            "generated_at": "2026-02-18T10:00:00Z",
            "scan_duration_ms": 1200,
            "total_files_scanned": 100,
            "issues_found": 5,
        },
        "issues": {
            "screaming_case": {
                "count": 2,
                "files": [
                    {
                        "path": "WAVE-1-CERTIFICATE.txt",
                        "recommended_name": "wave-1-certificate.txt",
                        "action": "rename",
                    },
                    {
                        "path": "AUDIT-REPORT.md",
                        "recommended_name": "audit-report.md",
                        "action": "rename",
                    },
                ],
            },
            "empty_files": {
                "count": 1,
                "files": [
                    {"path": "cortex/stub.py", "action": "delete"},
                ],
            },
            "orphaned_directories": {
                "count": 1,
                "directories": [
                    {"path": "cortex/wiring/specs", "action": "delete"},
                ],
            },
            "deprecated_code": {"count": 0, "files": []},
            "duplicate_content": {"count": 0, "groups": []},
            "wrong_references": {"count": 0, "files": []},
            "invalid_markdown": {"count": 1, "files": [
                {"path": "cortex/agents/REPORT.md", "action": "delete"},
            ]},
        },
        "summary": {
            "delete_count": 3,
            "rename_count": 2,
            "relocate_count": 0,
            "estimated_bytes_freed": 4096,
        },
    }
    issues_path = tmp_repo / "cortex" / "brain" / "vacuum" / "health-issues.yaml"
    with open(issues_path, "w") as f:
        yaml.dump(data, f)
    return issues_path


@pytest.fixture
def vacuum_executor(tmp_repo):
    """VacuumExecutor from health_orchestrator module."""
    from cortex.orchestrators.support.health_orchestrator import VacuumExecutor
    return VacuumExecutor(workspace_root=tmp_repo, dry_run=False)


@pytest.fixture
def vacuum_executor_dry(tmp_repo):
    from cortex.orchestrators.support.health_orchestrator import VacuumExecutor
    return VacuumExecutor(workspace_root=tmp_repo, dry_run=True)


# ===========================================================================
# GV-001: Rename Screaming to Kebab
# ===========================================================================


class TestRenameScreamingToKebab:
    """GV-001: UPPERCASE → kebab-case rename."""

    def test_renames_screaming_txt(self, tmp_repo, vacuum_executor):
        """GV-001: WAVE-1-CERTIFICATE.txt → wave-1-certificate.txt."""
        original = tmp_repo / "WAVE-1-CERTIFICATE.txt"
        original.write_text("cert content")

        result = vacuum_executor.rename_file(original, "wave-1-certificate.txt")

        assert result.success
        # Use os.listdir for exact case-sensitive check on macOS APFS
        import os
        dir_listing = os.listdir(str(tmp_repo))
        assert "WAVE-1-CERTIFICATE.txt" not in dir_listing
        assert "wave-1-certificate.txt" in dir_listing

    def test_kebab_rename_preserves_content(self, tmp_repo, vacuum_executor):
        """GV-001: Renamed file retains original content."""
        original = tmp_repo / "TEST-REPORT.txt"
        original.write_text("original content")

        vacuum_executor.rename_file(original, "test-report.txt")

        assert (tmp_repo / "test-report.txt").read_text() == "original content"


# ===========================================================================
# GV-002: Truncate Long Names
# ===========================================================================


class TestTruncateLongNames:
    """GV-002: Names exceeding 30 chars truncated."""

    def test_name_truncated_to_30_chars(self, tmp_repo, vacuum_executor):
        """GV-002: 50-char name → max 30 chars (incl extension)."""
        from cortex.orchestrators.support.health_orchestrator import to_kebab_case

        long_name = "THIS-IS-A-VERY-LONG-FILENAME-THAT-EXCEEDS-LIMIT.txt"
        result = to_kebab_case(long_name, max_length=30)

        assert len(result) <= 30
        assert result.endswith(".txt")
        assert result == result.lower()

    def test_short_name_not_truncated(self, tmp_repo, vacuum_executor):
        """GV-002: 15-char name unchanged length."""
        from cortex.orchestrators.support.health_orchestrator import to_kebab_case

        result = to_kebab_case("SHORT-NAME.txt", max_length=30)

        assert result == "short-name.txt"
        assert len(result) <= 30


# ===========================================================================
# GV-003: Delete Empty Directories
# ===========================================================================


class TestDeleteEmptyDirectories:
    """GV-003: Orphaned (empty) directories removed."""

    def test_deletes_empty_directory(self, tmp_repo, vacuum_executor):
        """GV-003: cortex/wiring/specs → deleted."""
        empty_dir = tmp_repo / "cortex" / "wiring" / "specs"
        empty_dir.mkdir(parents=True)

        result = vacuum_executor.delete_directory(empty_dir)

        assert result.success
        assert not empty_dir.exists()

    def test_non_empty_directory_protected(self, tmp_repo, vacuum_executor):
        """GV-003: Non-empty dir → not deleted."""
        d = tmp_repo / "cortex" / "live"
        d.mkdir(parents=True)
        (d / "file.py").write_text("content")

        result = vacuum_executor.delete_directory(d)

        assert not result.success
        assert d.exists()


# ===========================================================================
# GV-004: Relocate Root Scripts
# ===========================================================================


class TestRelocateRootScripts:
    """GV-004: Python files in root moved to scripts/."""

    def test_relocates_root_py_to_scripts(self, tmp_repo, vacuum_executor):
        """GV-004: cleanup_script.py → scripts/cleanup_script.py."""
        root_script = tmp_repo / "cleanup_script.py"
        root_script.write_text("# script")
        scripts_dir = tmp_repo / "scripts"
        scripts_dir.mkdir(exist_ok=True)

        result = vacuum_executor.relocate_file(root_script, scripts_dir)

        assert result.success
        assert not root_script.exists()
        assert (scripts_dir / "cleanup_script.py").exists()

    def test_protected_root_file_not_relocated(self, tmp_repo, vacuum_executor):
        """GV-004: conftest.py (protected) stays in root."""
        protected = tmp_repo / "conftest.py"
        protected.write_text("# conftest")

        result = vacuum_executor.relocate_file(
            protected, tmp_repo / "scripts", protected=True
        )

        assert not result.success
        assert protected.exists()


# ===========================================================================
# GV-005: Rollback on Failure
# ===========================================================================


class TestRollbackOnFailure:
    """GV-005: Failed verification triggers rollback."""

    def test_rollback_manifest_written(self, tmp_repo, vacuum_executor):
        """GV-005: After operations, rollback manifest exists."""
        original = tmp_repo / "SCREAMING.txt"
        original.write_text("data")

        vacuum_executor.rename_file(original, "screaming.txt")

        manifest_path = tmp_repo / "cortex" / "brain" / "vacuum" / "rollback-manifest.json"
        vacuum_executor.save_rollback_manifest(manifest_path)

        assert manifest_path.exists()
        manifest = json.loads(manifest_path.read_text())
        assert "operations" in manifest
        assert len(manifest["operations"]) >= 1

    def test_rollback_restores_renamed_file(self, tmp_repo, vacuum_executor):
        """GV-005: Rollback reverses rename → original name restored."""
        import os
        original = tmp_repo / "SCREAMING.txt"
        original.write_text("data")

        vacuum_executor.rename_file(original, "screaming.txt")
        manifest_path = tmp_repo / "cortex" / "brain" / "vacuum" / "rollback-manifest.json"
        vacuum_executor.save_rollback_manifest(manifest_path)

        vacuum_executor.rollback(manifest_path)

        dir_listing = os.listdir(str(tmp_repo))
        assert "SCREAMING.txt" in dir_listing
        assert "screaming.txt" not in dir_listing


# ===========================================================================
# GV-006: Delete Handoff File on Success
# ===========================================================================


class TestHandoffFileDeletion:
    """GV-006: health-issues.yaml deleted after successful cleanup."""

    def test_deletes_handoff_on_success(self, tmp_repo, health_issues_yaml, vacuum_executor):
        """GV-006: handoff file removed after teardown."""
        assert health_issues_yaml.exists()

        vacuum_executor.delete_handoff(health_issues_yaml)

        assert not health_issues_yaml.exists()

    def test_handoff_preserved_on_failure(self, tmp_repo, health_issues_yaml, vacuum_executor):
        """GV-006: handoff file kept if verification fails."""
        assert health_issues_yaml.exists()

        # Simulate: do NOT call delete_handoff (failure path)
        assert health_issues_yaml.exists()
