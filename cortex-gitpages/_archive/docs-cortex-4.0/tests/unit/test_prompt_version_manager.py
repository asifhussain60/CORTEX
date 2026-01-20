"""
Unit tests for Prompt Version Management System.

Tests PromptVersionManager for version negotiation, compatibility checking,
and backward compatibility verification across prompt releases.

Covers:
- Version creation and versioned release directories
- Version negotiation (repo requests version X, hub has version X)
- Incompatible version detection and rejection
- Version history tracking in prompt-versions.yaml
- Backward compatibility matrix
- Deprecated version detection
- Future version rejection
- Major version incompatibility
"""

import pytest
import yaml
import tempfile
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock


@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset PromptVersionManager singleton before each test."""
    from src.versioning.prompt_version_manager import PromptVersionManager
    PromptVersionManager.reset_singleton()
    yield
    PromptVersionManager.reset_singleton()


class TestVersionEntry:
    """Test VersionEntry dataclass for version representation."""

    def test_version_entry_creation(self):
        """VersionEntry created with version string."""
        from src.versioning.prompt_version_manager import VersionEntry

        entry = VersionEntry(
            version="1.0.0",
            release_date=datetime.now(),
            sha_hash="abc123def456",
            is_deprecated=False,
        )

        assert entry.version == "1.0.0"
        assert entry.sha_hash == "abc123def456"
        assert not entry.is_deprecated

    def test_version_entry_semantic_versioning(self):
        """VersionEntry validates semantic versioning format."""
        from src.versioning.prompt_version_manager import VersionEntry

        entry = VersionEntry(
            version="1.2.3",
            release_date=datetime.now(),
            sha_hash="hash123",
            is_deprecated=False,
        )

        major, minor, patch = entry.version.split(".")
        assert int(major) >= 0
        assert int(minor) >= 0
        assert int(patch) >= 0

    def test_version_entry_deprecation_flag(self):
        """VersionEntry tracks deprecation status."""
        from src.versioning.prompt_version_manager import VersionEntry

        entry = VersionEntry(
            version="0.9.0",
            release_date=datetime.now(),
            sha_hash="hash999",
            is_deprecated=True,
        )

        assert entry.is_deprecated


class TestPromptVersionManager:
    """Test PromptVersionManager singleton."""

    def test_manager_initialization(self):
        """PromptVersionManager initializes with empty version store."""
        from src.versioning.prompt_version_manager import PromptVersionManager

        manager = PromptVersionManager()

        assert manager.version_count == 0
        assert manager.current_version is None

    def test_register_version(self):
        """PromptVersionManager registers new prompt version."""
        from src.versioning.prompt_version_manager import PromptVersionManager

        manager = PromptVersionManager()

        version = manager.register_version(
            version="1.0.0",
            sha_hash="hash1000",
            is_deprecated=False,
        )

        assert version is not None
        assert version.version == "1.0.0"
        assert manager.version_count == 1
        assert manager.current_version == "1.0.0"

    def test_register_version_multiple(self):
        """PromptVersionManager registers multiple versions."""
        from src.versioning.prompt_version_manager import PromptVersionManager

        manager = PromptVersionManager()

        v1 = manager.register_version("1.0.0", "hash100", False)
        v2 = manager.register_version("1.1.0", "hash110", False)
        v3 = manager.register_version("1.2.0", "hash120", False)

        assert manager.version_count == 3
        assert manager.current_version == "1.2.0"

    def test_get_version_by_string(self):
        """PromptVersionManager retrieves version by version string."""
        from src.versioning.prompt_version_manager import PromptVersionManager

        manager = PromptVersionManager()
        registered = manager.register_version("1.0.0", "hash100", False)

        retrieved = manager.get_version("1.0.0")

        assert retrieved is not None
        assert retrieved.version == "1.0.0"

    def test_get_version_nonexistent(self):
        """PromptVersionManager returns None for nonexistent version."""
        from src.versioning.prompt_version_manager import PromptVersionManager

        manager = PromptVersionManager()

        version = manager.get_version("9.9.9")

        assert version is None

    def test_version_negotiation_exact_match(self):
        """Version negotiation succeeds when repo version matches hub version."""
        from src.versioning.prompt_version_manager import PromptVersionManager

        manager = PromptVersionManager()
        manager.register_version("1.0.0", "hash100", False)

        result = manager.negotiate_version(
            repo_requested_version="1.0.0",
            available_versions=["1.0.0"],
        )

        assert result is not None
        assert result.version == "1.0.0"
        assert result.compatible is True

    def test_version_negotiation_minor_version_compatible(self):
        """Minor version bumps are backward compatible."""
        from src.versioning.prompt_version_manager import PromptVersionManager

        manager = PromptVersionManager()
        manager.register_version("1.0.0", "hash100", False)
        manager.register_version("1.1.0", "hash110", False)
        manager.register_version("1.2.0", "hash120", False)

        # Repo requesting 1.0.0, hub has 1.2.0
        result = manager.negotiate_version(
            repo_requested_version="1.0.0",
            available_versions=["1.0.0", "1.1.0", "1.2.0"],
        )

        assert result is not None
        assert result.compatible is True

    def test_version_negotiation_major_version_incompatible(self):
        """Major version changes are incompatible."""
        from src.versioning.prompt_version_manager import PromptVersionManager

        manager = PromptVersionManager()
        manager.register_version("1.0.0", "hash100", False)
        manager.register_version("2.0.0", "hash200", False)

        # Repo requesting 1.x, hub only has 2.x
        result = manager.negotiate_version(
            repo_requested_version="1.0.0",
            available_versions=["2.0.0"],
        )

        assert result is not None
        assert result.compatible is False

    def test_future_version_rejected(self):
        """Repository requesting future version is rejected."""
        from src.versioning.prompt_version_manager import PromptVersionManager

        manager = PromptVersionManager()
        manager.register_version("1.0.0", "hash100", False)

        # Repo requesting 2.0.0, hub only has 1.0.0
        result = manager.negotiate_version(
            repo_requested_version="2.0.0",
            available_versions=["1.0.0"],
        )

        assert result is not None
        assert result.compatible is False
        # Check for either "future", "not yet", or "available" in error
        assert ("future" in result.error_message.lower() or 
                "not yet" in result.error_message.lower() or
                "not available" in result.error_message.lower())

    def test_deprecated_version_detection(self):
        """Deprecated versions are detected."""
        from src.versioning.prompt_version_manager import PromptVersionManager

        manager = PromptVersionManager()
        manager.register_version("0.9.0", "hash090", True)  # deprecated
        manager.register_version("1.0.0", "hash100", False)

        deprecated_version = manager.get_version("0.9.0")

        assert deprecated_version is not None
        assert deprecated_version.is_deprecated is True

    def test_deprecated_version_rejected_in_negotiation(self):
        """Negotiation rejects deprecated versions."""
        from src.versioning.prompt_version_manager import PromptVersionManager

        manager = PromptVersionManager()
        manager.register_version("0.9.0", "hash090", True)  # deprecated
        manager.register_version("1.0.0", "hash100", False)

        # Repo requesting deprecated version
        result = manager.negotiate_version(
            repo_requested_version="0.9.0",
            available_versions=["0.9.0", "1.0.0"],
        )

        assert result is not None
        assert result.compatible is False
        assert "deprecated" in result.error_message.lower()

    def test_compatibility_matrix_lookup(self):
        """Compatibility matrix determines version compatibility."""
        from src.versioning.prompt_version_manager import PromptVersionManager

        manager = PromptVersionManager()
        manager.register_version("1.0.0", "hash100", False)
        manager.register_version("1.1.0", "hash110", False)
        manager.register_version("2.0.0", "hash200", False)

        # 1.x compatible with 1.x
        assert manager.is_compatible("1.0.0", "1.1.0") is True

        # 1.x not compatible with 2.x
        assert manager.is_compatible("1.0.0", "2.0.0") is False

    def test_version_history_tracking(self):
        """Version history is maintained and queryable."""
        from src.versioning.prompt_version_manager import PromptVersionManager

        manager = PromptVersionManager()
        manager.register_version("1.0.0", "hash100", False)
        manager.register_version("1.1.0", "hash110", False)
        manager.register_version("1.2.0", "hash120", False)

        history = manager.version_history

        assert len(history) == 3
        assert history[0].version == "1.0.0"
        assert history[-1].version == "1.2.0"

    def test_version_release_directory_created(self):
        """Version registration creates release directory structure."""
        from src.versioning.prompt_version_manager import PromptVersionManager

        with tempfile.TemporaryDirectory() as tmpdir:
            releases_path = Path(tmpdir) / "releases"
            manager = PromptVersionManager(releases_path=releases_path)

            manager.register_version("1.0.0", "hash100", False)

            # Release directory should exist
            version_dir = releases_path / "v1.0.0"
            assert version_dir.exists()

    def test_version_manifest_persistence(self):
        """Version manifest saved to prompt-versions.yaml."""
        from src.versioning.prompt_version_manager import PromptVersionManager

        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_path = Path(tmpdir) / "prompt-versions.yaml"
            manager = PromptVersionManager(manifest_path=manifest_path)

            manager.register_version("1.0.0", "hash100", False)
            manager.register_version("1.1.0", "hash110", False)

            manager.save_manifest()

            # Manifest should exist and be valid YAML
            assert manifest_path.exists()
            with open(manifest_path) as f:
                manifest_data = yaml.safe_load(f)
            assert manifest_data is not None
            assert len(manifest_data["versions"]) == 2

    def test_version_manifest_roundtrip(self):
        """Version manifest can be saved and loaded."""
        from src.versioning.prompt_version_manager import PromptVersionManager

        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_path = Path(tmpdir) / "prompt-versions.yaml"

            # Save
            manager1 = PromptVersionManager(manifest_path=manifest_path)
            manager1.register_version("1.0.0", "hash100", False)
            manager1.register_version("1.1.0", "hash110", False)
            manager1.save_manifest()

            # Load
            manager2 = PromptVersionManager(manifest_path=manifest_path)
            manager2.load_manifest()

            assert manager2.version_count == 2
            assert manager2.get_version("1.0.0") is not None
            assert manager2.get_version("1.1.0") is not None


class TestVersionEdgeCases:
    """Test edge cases in version management."""

    def test_patch_version_changes_compatible(self):
        """Patch version changes are backward compatible."""
        from src.versioning.prompt_version_manager import PromptVersionManager

        manager = PromptVersionManager()
        manager.register_version("1.0.0", "hash100", False)
        manager.register_version("1.0.1", "hash101", False)

        result = manager.is_compatible("1.0.0", "1.0.1")

        assert result is True

    def test_empty_version_string_rejected(self):
        """Empty version string rejected."""
        from src.versioning.prompt_version_manager import PromptVersionManager

        manager = PromptVersionManager()

        with pytest.raises(ValueError):
            manager.register_version("", "hash", False)

    def test_invalid_semantic_version_rejected(self):
        """Invalid semantic version format rejected."""
        from src.versioning.prompt_version_manager import PromptVersionManager

        manager = PromptVersionManager()

        with pytest.raises(ValueError):
            manager.register_version("invalid", "hash", False)

    def test_version_hash_validation(self):
        """Version SHA hash is validated and stored."""
        from src.versioning.prompt_version_manager import PromptVersionManager

        manager = PromptVersionManager()
        version = manager.register_version("1.0.0", "abc123", False)

        assert version.sha_hash == "abc123"

    def test_version_release_date_tracking(self):
        """Version release date is tracked."""
        from src.versioning.prompt_version_manager import PromptVersionManager

        manager = PromptVersionManager()
        before = datetime.now()
        version = manager.register_version("1.0.0", "hash100", False)
        after = datetime.now()

        assert before <= version.release_date <= after


class TestVersionManagerThreadSafety:
    """Test thread safety of PromptVersionManager."""

    def test_concurrent_version_registration(self):
        """Multiple threads can register versions concurrently."""
        from src.versioning.prompt_version_manager import PromptVersionManager
        import threading

        manager = PromptVersionManager()
        errors = []

        def register_version(version_str: str):
            try:
                manager.register_version(version_str, f"hash{version_str}", False)
            except Exception as e:
                errors.append(e)

        threads = []
        versions = ["1.0.0", "1.1.0", "1.2.0", "2.0.0"]
        for v in versions:
            t = threading.Thread(target=register_version, args=(v,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        assert len(errors) == 0
        assert manager.version_count == len(versions)

    def test_concurrent_version_negotiation(self):
        """Multiple threads can negotiate versions concurrently."""
        from src.versioning.prompt_version_manager import PromptVersionManager
        import threading

        manager = PromptVersionManager()
        manager.register_version("1.0.0", "hash100", False)
        manager.register_version("1.1.0", "hash110", False)

        results = []

        def negotiate():
            result = manager.negotiate_version("1.0.0", ["1.0.0", "1.1.0"])
            results.append(result)

        threads = []
        for _ in range(10):
            t = threading.Thread(target=negotiate)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        assert len(results) == 10
        assert all(r.compatible for r in results)
