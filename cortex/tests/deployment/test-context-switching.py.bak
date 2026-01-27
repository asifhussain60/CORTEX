"""Tests for context switching (AC-UNIFIED-DEPLOY-002-03)."""

import pytest
from cortex.lib.context_switcher import ContextSwitcher


class TestContextSwitcherIntegration:
    """Integration tests for context switching."""

    @pytest.fixture
    def switcher(self, tmp_path):
        """Create test context switcher."""
        return ContextSwitcher(cache_dir=str(tmp_path / "cache"))

    def test_multiple_repo_switching(self, switcher, tmp_path):
        """Test switching between multiple repos."""
        repos = []
        for i in range(3):
            repo = tmp_path / f"repo{i}"
            repo.mkdir()
            (repo / ".git").mkdir()
            (repo / ".git" / "config").write_text(f"[remote]\n\turl = git@github.com:org/repo{i}.git\n")
            repos.append(repo)

        # Switch between repos and verify isolation
        for i, repo_path in enumerate(repos):
            result = switcher.switch_context(str(repo_path))
            assert result == True
            assert switcher.current_context.repo_name == f"repo{i}"

    def test_telemetry_batch_per_repo(self, switcher, tmp_path):
        """Test that telemetry batches are separate per repo."""
        repo1 = tmp_path / "repo1"
        repo2 = tmp_path / "repo2"
        repo1.mkdir()
        repo2.mkdir()
        (repo1 / ".git").mkdir()
        (repo1 / ".git" / "config").write_text("")
        (repo2 / ".git").mkdir()
        (repo2 / ".git" / "config").write_text("")

        # Add event to repo1
        switcher.switch_context(str(repo1))
        event1 = {"event_type": "execution", "tool_name": "tool1"}
        switcher.append_telemetry_event(event1)

        # Switch to repo2 and add different event
        switcher.switch_context(str(repo2))
        event2 = {"event_type": "error", "tool_name": "tool2"}
        switcher.append_telemetry_event(event2)

        # Batches should be in different locations
        batch1 = switcher.get_telemetry_batch_path(switcher.detect_repo(str(repo1)))
        batch2 = switcher.get_telemetry_batch_path(switcher.detect_repo(str(repo2)))
        assert batch1 != batch2

    def test_context_persistence(self, switcher, tmp_path):
        """Test that context state persists across calls."""
        repo = tmp_path / "test_repo"
        repo.mkdir()
        (repo / ".git").mkdir()
        (repo / ".git" / "config").write_text("")

        # First switch
        switcher.switch_context(str(repo))
        context1_id = switcher.current_context.repo_id

        # Second switch (should restore from DB)
        switcher2 = ContextSwitcher(cache_dir=str(tmp_path / "cache"))
        switcher2.switch_context(str(repo))
        context2_id = switcher2.current_context.repo_id

        assert context1_id == context2_id

    def test_no_state_mixing(self, switcher, tmp_path):
        """Test that switching repos clears previous state."""
        repo1 = tmp_path / "repo1"
        repo2 = tmp_path / "repo2"
        repo1.mkdir()
        repo2.mkdir()
        (repo1 / ".git").mkdir()
        (repo1 / ".git" / "config").write_text("")
        (repo2 / ".git").mkdir()
        (repo2 / ".git" / "config").write_text("")

        switcher.switch_context(str(repo1))
        repo1_context = switcher.current_context

        switcher.switch_context(str(repo2))
        repo2_context = switcher.current_context

        # Contexts should be completely different
        assert repo1_context.repo_id != repo2_context.repo_id
        assert repo1_context.repo_path != repo2_context.repo_path

    def test_get_context_info(self, switcher, tmp_path):
        """Test getting human-readable context info."""
        repo = tmp_path / "test_repo"
        repo.mkdir()
        (repo / ".git").mkdir()
        config_text = "[remote \"origin\"]\n\turl = git@github.com:org/test.git\n"
        (repo / ".git" / "config").write_text(config_text)

        switcher.switch_context(str(repo))
        info = switcher.get_context_info()

        assert "repo_name" in info
        assert "repo_id" in info
        assert "telemetry_source" in info
        assert info["repo_name"] == "test_repo"
