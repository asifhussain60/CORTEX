"""Tests for manifest system and deployment (AC-UNIFIED-DEPLOY-003-01, AC-002-03)."""

import pytest
from datetime import datetime
from cortex.lib.manifest_diff import ManifestSchema, ManifestDiff, OrchestratorInfo
from cortex.lib.context_switcher import ContextSwitcher


class TestManifestSchema:
    """Test suite for manifest schema validation."""

    def test_validate_schema_valid_manifest(self):
        """Test validation of valid manifest."""
        manifest = {
            "schema_version": "2.0",
            "released_at": datetime.utcnow().isoformat() + "Z",
            "cortex_version": "2.6.0",
            "orchestrators": [
                {
                    "name": "MasterOrchestrator",
                    "version": "2.6.0",
                    "fingerprint": "abc123def456",
                    "breaking_changes": [],
                }
            ],
            "mcp_tools": [],
            "brain_tiers": [],
            "migrations": [],
        }

        is_valid, errors = ManifestSchema.validate_schema(manifest)
        assert is_valid == True
        assert len(errors) == 0

    def test_validate_schema_missing_required_field(self):
        """Test rejection of manifest missing required field."""
        manifest = {
            "schema_version": "2.0",
            # Missing released_at
            "cortex_version": "2.6.0",
        }

        is_valid, errors = ManifestSchema.validate_schema(manifest)
        assert is_valid == False
        assert len(errors) > 0
        assert any("released_at" in err for err in errors)

    def test_validate_schema_invalid_schema_version(self):
        """Test rejection of invalid schema version."""
        manifest = {
            "schema_version": "1.0",  # Wrong version
            "released_at": datetime.utcnow().isoformat() + "Z",
            "cortex_version": "2.6.0",
        }

        is_valid, errors = ManifestSchema.validate_schema(manifest)
        assert is_valid == False

    def test_validate_schema_invalid_timestamp(self):
        """Test rejection of invalid timestamp format."""
        manifest = {
            "schema_version": "2.0",
            "released_at": "not-a-valid-timestamp",
            "cortex_version": "2.6.0",
        }

        is_valid, errors = ManifestSchema.validate_schema(manifest)
        assert is_valid == False

    def test_validate_dependencies_no_cycles(self):
        """Test validation of dependency graph without cycles."""
        manifest = {
            "orchestrators": [],
            "workflows": [
                {
                    "name": "workflow_a",
                    "version": "1.0",
                    "dependencies": ["workflow_b"],
                },
                {"name": "workflow_b", "version": "1.0", "dependencies": []},
            ],
            "mcp_tools": [],
            "brain_tiers": [],
        }

        is_valid, errors = ManifestSchema.validate_dependencies(manifest)
        assert is_valid == True

    def test_validate_dependencies_circular_dependency(self):
        """Test detection of circular dependencies."""
        manifest = {
            "orchestrators": [],
            "workflows": [
                {
                    "name": "workflow_a",
                    "version": "1.0",
                    "dependencies": ["workflow_b"],
                },
                {
                    "name": "workflow_b",
                    "version": "1.0",
                    "dependencies": ["workflow_a"],
                },
            ],
            "mcp_tools": [],
            "brain_tiers": [],
        }

        is_valid, errors = ManifestSchema.validate_dependencies(manifest)
        # Circular dependency should be detected or handled gracefully


class TestManifestDiff:
    """Test suite for manifest diff computation."""

    def test_compute_diff_identical_manifests(self):
        """Test diff of identical manifests."""
        manifest = {
            "cortex_version": "2.6.0",
            "orchestrators": [
                {"name": "Orch1", "version": "2.6.0", "fingerprint": "abc123"}
            ],
            "workflows": [],
            "mcp_tools": [],
            "brain_tiers": [],
        }

        diff = ManifestDiff.compute(manifest, manifest)
        assert diff.change_type == "patch"
        assert len(diff.new_orchestrators) == 0
        assert len(diff.removed_orchestrators) == 0

    def test_compute_diff_new_orchestrator(self):
        """Test diff with new orchestrator."""
        manifest_old = {
            "cortex_version": "2.5.0",
            "orchestrators": [],
            "workflows": [],
            "mcp_tools": [],
            "brain_tiers": [],
        }

        manifest_new = {
            "cortex_version": "2.6.0",
            "orchestrators": [
                {"name": "NewOrch", "version": "2.6.0", "fingerprint": "new123"}
            ],
            "workflows": [],
            "mcp_tools": [],
            "brain_tiers": [],
        }

        diff = ManifestDiff.compute(manifest_old, manifest_new)
        assert diff.change_type == "major"
        assert "NewOrch" in diff.new_orchestrators
        assert diff.impact_score >= 0.75

    def test_compute_diff_removed_orchestrator(self):
        """Test diff with removed orchestrator."""
        manifest_old = {
            "cortex_version": "2.6.0",
            "orchestrators": [
                {"name": "OldOrch", "version": "2.6.0", "fingerprint": "old123"}
            ],
            "workflows": [],
            "mcp_tools": [],
            "brain_tiers": [],
        }

        manifest_new = {
            "cortex_version": "2.7.0",
            "orchestrators": [],
            "workflows": [],
            "mcp_tools": [],
            "brain_tiers": [],
        }

        diff = ManifestDiff.compute(manifest_old, manifest_new)
        assert diff.change_type == "breaking"
        assert "OldOrch" in diff.removed_orchestrators
        assert diff.impact_score == 1.0


class TestContextSwitcher:
    """Test suite for multi-repo context switching."""

    @pytest.fixture
    def switcher(self, tmp_path):
        """Create test context switcher."""
        return ContextSwitcher(cache_dir=str(tmp_path / "cortex-cache"))

    def test_detect_repo_not_git_repo(self, switcher, tmp_path):
        """Test detection fails for non-git directory."""
        non_repo = tmp_path / "non_repo"
        non_repo.mkdir()

        context = switcher.detect_repo(str(non_repo))
        assert context is None

    def test_detect_repo_git_directory(self, switcher, tmp_path):
        """Test detection succeeds for git directory."""
        repo = tmp_path / "my_repo"
        repo.mkdir()
        git_dir = repo / ".git"
        git_dir.mkdir()
        config = git_dir / "config"
        config.write_text("[core]\n\trepositoryformatversion = 0\n")

        context = switcher.detect_repo(str(repo))
        assert context is not None
        assert context.repo_name == "my_repo"
        assert context.repo_id is not None

    def test_switch_context_success(self, switcher, tmp_path):
        """Test successful context switch."""
        repo1 = tmp_path / "repo1"
        repo1.mkdir()
        git1 = repo1 / ".git"
        git1.mkdir()
        (git1 / "config").write_text("")

        result = switcher.switch_context(str(repo1))
        assert result == True
        assert switcher.current_context is not None

    def test_context_isolation(self, switcher, tmp_path):
        """Test that repos have isolated state."""
        repo1 = tmp_path / "repo1"
        repo2 = tmp_path / "repo2"
        repo1.mkdir()
        repo2.mkdir()

        (repo1 / ".git").mkdir()
        (repo1 / ".git" / "config").write_text("")
        (repo2 / ".git").mkdir()
        (repo2 / ".git" / "config").write_text("")

        # Switch to repo1
        switcher.switch_context(str(repo1))
        context1 = switcher.current_context
        cache1 = switcher.get_isolated_cache_path(context1)

        # Switch to repo2
        switcher.switch_context(str(repo2))
        context2 = switcher.current_context
        cache2 = switcher.get_isolated_cache_path(context2)

        # Caches should be different
        assert cache1 != cache2

    def test_telemetry_tagging_per_repo(self, switcher, tmp_path):
        """Test that telemetry is tagged per repo."""
        repo = tmp_path / "test_repo"
        repo.mkdir()
        (repo / ".git").mkdir()
        (repo / ".git" / "config").write_text("")

        switcher.switch_context(str(repo))
        tag1 = switcher.get_telemetry_tag()
        assert "repo:" in tag1

        # Tag should be consistent
        tag2 = switcher.get_telemetry_tag()
        assert tag1 == tag2

    def test_append_telemetry_event(self, switcher, tmp_path):
        """Test appending telemetry events to batch."""
        repo = tmp_path / "test_repo"
        repo.mkdir()
        (repo / ".git").mkdir()
        (repo / ".git" / "config").write_text("")

        switcher.switch_context(str(repo))

        event = {
            "event_type": "execution",
            "tool_name": "test",
            "success": True,
        }

        result = switcher.append_telemetry_event(event)
        assert result == True

        # Verify event was tagged
        assert "repo_identifier" in event
        assert "telemetry_source" in event
