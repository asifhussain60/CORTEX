"""
Tests for Git Commit Orchestrator (AC-GIT-001, AC-GIT-002, AC-GIT-003).

Author: GitHub Copilot
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.orchestrators.git import GitCommitOrchestrator, FileClassification


class TestFileClassification:
    """Test file classification logic."""

    def test_classify_commit_patterns(self):
        """Test COMMIT pattern matching."""
        orchestrator = GitCommitOrchestrator()

        commit_files = [
            "src/orchestrators/git/git_commit_orchestrator.py",
            "src/tools/analyzer.py",
            "tests/orchestrators/test_git.py",
            "cortex-brain/tier1/orchestrators/manifest.yaml",
            "cortex-brain/tier2/governance/rules.yaml",
            "cortex-brain/documents/implementation.md",
            ".github/prompts/cortex-git-commit.prompt.md",
        ]

        for file_path in commit_files:
            result = orchestrator.classify_file(file_path)
            assert result.classification == FileClassification.COMMIT, \
                f"Expected COMMIT for {file_path}, got {result.classification}"

    def test_classify_ignore_patterns(self):
        """Test IGNORE pattern matching."""
        orchestrator = GitCommitOrchestrator()

        ignore_files = [
            ".cortex/analysis.md",
            "cortex-brain/cx6-plan/viewer/data-backup-20260113.json",
            "cortex-brain/audit-logs/audit_20260113.jsonl",
            "__pycache__/module.cpython-39.pyc",
            ".pytest_cache/",
            ".coverage",
            "something.db-wal",
        ]

        for file_path in ignore_files:
            result = orchestrator.classify_file(file_path)
            assert result.classification == FileClassification.IGNORE, \
                f"Expected IGNORE for {file_path}, got {result.classification}"

    def test_classify_reset_patterns(self):
        """Test RESET pattern matching."""
        orchestrator = GitCommitOrchestrator()

        reset_files = [
            "file.tmp",
            "backup.bak",
            "build/output.o",
            "dist/package.whl",
        ]

        for file_path in reset_files:
            result = orchestrator.classify_file(file_path)
            assert result.classification == FileClassification.RESET, \
                f"Expected RESET for {file_path}, got {result.classification}"

    def test_classify_unknown(self):
        """Test UNKNOWN classification."""
        orchestrator = GitCommitOrchestrator()

        unknown_files = [
            "random_file.xyz",
            "config.xyz",
        ]

        for file_path in unknown_files:
            result = orchestrator.classify_file(file_path)
            assert result.classification == FileClassification.UNKNOWN, \
                f"Expected UNKNOWN for {file_path}, got {result.classification}"


class TestFileClassificationBatch:
    """Test batch file classification."""

    def test_classify_multiple_files(self):
        """Test classifying multiple files."""
        orchestrator = GitCommitOrchestrator()

        files = [
            "src/orchestrators/git/new_tool.py",  # COMMIT
            ".cortex/analysis.md",  # IGNORE
            "backup.tmp",  # RESET
            "tests/test_new.py",  # COMMIT
            "cortex-brain/audit-logs/log.jsonl",  # IGNORE
        ]

        commits, ignores, resets, classifications = orchestrator.classify_untracked_files(files)

        assert len(commits) == 2, f"Expected 2 commits, got {len(commits)}"
        assert len(ignores) == 2, f"Expected 2 ignores, got {len(ignores)}"
        assert len(resets) == 1, f"Expected 1 reset, got {len(resets)}"

    def test_empty_file_list(self):
        """Test classifying empty file list."""
        orchestrator = GitCommitOrchestrator()

        commits, ignores, resets, classifications = orchestrator.classify_untracked_files([])

        assert len(commits) == 0
        assert len(ignores) == 0
        assert len(resets) == 0


class TestOrchestratorDiscovery:
    """Test orchestrator discovery."""

    def test_discover_orchestrators_from_files(self):
        """Test discovering orchestrators from modified files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create orchestrator file
            orch_file = tmpdir / "src" / "orchestrators" / "test" / "test_orchestrator.py"
            orch_file.parent.mkdir(parents=True, exist_ok=True)

            orch_file.write_text("""
class TestOrchestrator:
    \"\"\"Test orchestrator.\"\"\"
    
    @OrchestratorRegistry.register(
        name="test_orch",
        domain="testing"
    )
    def execute(self):
        pass

# AC-TEST-001: Feature one
# AC-TEST-002: Feature two
""")

            orchestrator = GitCommitOrchestrator(workspace_root=tmpdir)
            discoveries = orchestrator.discover_orchestrators([
                "src/orchestrators/test/test_orchestrator.py"
            ])

            assert len(discoveries) == 1
            discovery = discoveries[0]
            assert discovery.class_name == "TestOrchestrator"
            assert discovery.orchestrator_id == "test_orch"
            assert discovery.domain == "testing"

    def test_no_orchestrators_found(self):
        """Test when no orchestrators found."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            orchestrator = GitCommitOrchestrator(workspace_root=tmpdir)
            discoveries = orchestrator.discover_orchestrators([])

            assert len(discoveries) == 0


class TestCommitMessageGeneration:
    """Test commit message generation."""

    def test_generate_commit_message_with_ac_ids(self):
        """Test generating commit message with AC-IDs."""
        orchestrator = GitCommitOrchestrator()

        message = orchestrator.generate_commit_message(
            phase_number=10,
            ac_ids=["AC-GIT-001", "AC-GIT-002"],
            completion_percentage=50,
            committed_files=["src/orchestrators/git/tool.py"],
            orchestrators_registered=1,
            capabilities_added=3,
            untracked_files_removed=2
        )

        assert "feat:" in message
        assert "AC-GIT-001" in message
        assert "PHASE: 10" in message
        assert "ORCHESTRATORS_REGISTERED: 1" in message
        assert "CAPABILITIES_ADDED: 3" in message

    def test_generate_commit_message_minimal(self):
        """Test generating minimal commit message."""
        orchestrator = GitCommitOrchestrator()

        message = orchestrator.generate_commit_message(
            phase_number=None,
            ac_ids=None,
            completion_percentage=None,
            committed_files=[],
            orchestrators_registered=0,
            capabilities_added=0,
            untracked_files_removed=0
        )

        assert "chore:" in message
        assert message.strip()  # Not empty


class TestGitOperations:
    """Test git operations."""

    @patch("subprocess.run")
    def test_git_add_files(self, mock_run):
        """Test git add operation."""
        mock_run.return_value = MagicMock(returncode=0)

        orchestrator = GitCommitOrchestrator()
        result = orchestrator.git_add_files([
            "file1.py",
            "file2.py"
        ])

        assert result is True
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_git_add_empty_list(self, mock_run):
        """Test git add with empty list."""
        orchestrator = GitCommitOrchestrator()
        result = orchestrator.git_add_files([])

        assert result is True
        mock_run.assert_not_called()

    @patch("subprocess.run")
    def test_git_reset_files(self, mock_run):
        """Test git reset operation."""
        mock_run.return_value = MagicMock(returncode=0)

        orchestrator = GitCommitOrchestrator()
        result = orchestrator.git_reset_files(["file.tmp"])

        assert result is True
        mock_run.assert_called_once()


class TestGitignoreUpdate:
    """Test .gitignore updates."""

    def test_update_gitignore(self):
        """Test updating .gitignore."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            gitignore = tmpdir / ".gitignore"
            gitignore.write_text("*.pyc\n")

            orchestrator = GitCommitOrchestrator(workspace_root=tmpdir)
            result = orchestrator.update_gitignore([
                "*.tmp",
                "build/"
            ])

            assert result is True
            content = gitignore.read_text()
            assert "*.tmp" in content
            assert "build/" in content

    def test_update_gitignore_no_duplicates(self):
        """Test that duplicate patterns aren't added."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            gitignore = tmpdir / ".gitignore"
            gitignore.write_text("*.pyc\n")

            orchestrator = GitCommitOrchestrator(workspace_root=tmpdir)
            orchestrator.update_gitignore(["*.pyc"])

            content = gitignore.read_text()
            assert content.count("*.pyc") == 1  # Only one copy


class TestOrchestrationRegistration:
    """Test orchestrator registration."""

    def test_register_orchestrators(self):
        """Test registering orchestrators."""
        from src.orchestrators.git import OrchestratorDiscovery

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            (tmpdir / "cortex-brain" / "state").mkdir(parents=True, exist_ok=True)

            discoveries = [
                OrchestratorDiscovery(
                    orchestrator_id="test_orch",
                    class_name="TestOrchestrator",
                    domain="testing",
                    capabilities=["analyze", "validate"],
                    ac_ids=["AC-TEST-001"],
                    file_path="src/orchestrators/test/test_orchestrator.py"
                )
            ]

            orchestrator = GitCommitOrchestrator(workspace_root=tmpdir)
            count, capabilities = orchestrator.register_orchestrators(discoveries)

            assert count == 1
            assert len(capabilities) >= 2

            # Verify registry file created
            registry_file = tmpdir / "cortex-brain" / "state" / "orchestrator_registry.json"
            assert registry_file.exists()

            with open(registry_file) as f:
                registry = json.load(f)
                assert "test_orch" in registry


class TestFullWorkflow:
    """Test full git commit workflow."""

    @patch("subprocess.run")
    def test_run_with_no_untracked_files(self, mock_run):
        """Test run when no untracked files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            orchestrator = GitCommitOrchestrator(workspace_root=tmpdir)

            # Mock git ls-files to return empty
            def side_effect(cmd, **kwargs):
                if "ls-files" in cmd:
                    return MagicMock(
                        returncode=0,
                        stdout="",
                        stderr=""
                    )
                return MagicMock(returncode=0, stdout="", stderr="")

            mock_run.side_effect = side_effect

            result = orchestrator.run(
                phase_number=10,
                ac_ids=["AC-GIT-001"]
            )

            assert result.success is True
            assert result.untracked_files_before == 0

    @patch("subprocess.run")
    def test_run_full_workflow(self, mock_run):
        """Test full workflow execution."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            (tmpdir / "cortex-brain" / "state").mkdir(parents=True, exist_ok=True)

            orchestrator = GitCommitOrchestrator(workspace_root=tmpdir)

            # Mock git operations
            def side_effect(cmd, **kwargs):
                if "ls-files" in cmd:
                    return MagicMock(
                        returncode=0,
                        stdout="src/orchestrators/git/new.py\n.cortex/analysis.md\n",
                        stderr=""
                    )
                elif "add" in cmd:
                    return MagicMock(returncode=0, stdout="", stderr="")
                elif "commit" in cmd:
                    return MagicMock(
                        returncode=0,
                        stdout="[CORTEX6 abc1234] feat: Implement\n",
                        stderr=""
                    )
                elif "push" in cmd:
                    return MagicMock(returncode=0, stdout="", stderr="")
                return MagicMock(returncode=0, stdout="", stderr="")

            mock_run.side_effect = side_effect

            result = orchestrator.run(
                phase_number=10,
                ac_ids=["AC-GIT-001"],
                completion_percentage=50
            )

            assert result.success is True
            assert len(result.committed_files) == 1
            assert len(result.ignored_files) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
