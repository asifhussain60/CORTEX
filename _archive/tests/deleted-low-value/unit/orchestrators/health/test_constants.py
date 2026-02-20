"""Unit Tests — constants.py

Phase: PHASE-51
CORE: CORE-008 (TDD — tests first)
"""

from pathlib import Path


class TestConstants:
    """Validate all shared constants are defined and correct."""

    def test_protected_files_is_frozenset(self) -> None:
        """PROTECTED_FILES must be immutable."""
        from cortex.orchestrators.health.constants import PROTECTED_FILES

        assert isinstance(PROTECTED_FILES, frozenset)

    def test_protected_files_contains_essentials(self) -> None:
        """Root files that must never be moved or deleted."""
        from cortex.orchestrators.health.constants import PROTECTED_FILES

        for name in (
            "pyproject.toml",
            "requirements.txt",
            "pytest.ini",
            "conftest.py",
            "Makefile",
            "README.md",
            ".gitignore",
        ):
            assert name in PROTECTED_FILES, f"{name} missing from PROTECTED_FILES"

    def test_excluded_dirs_contains_essentials(self) -> None:
        """Directories that should never be traversed."""
        from cortex.orchestrators.health.constants import EXCLUDED_DIRS

        for name in (".git", "__pycache__", ".venv", "node_modules", ".mypy_cache"):
            assert name in EXCLUDED_DIRS, f"{name} missing from EXCLUDED_DIRS"

    def test_excluded_dirs_is_frozenset(self) -> None:
        from cortex.orchestrators.health.constants import EXCLUDED_DIRS

        assert isinstance(EXCLUDED_DIRS, frozenset)

    def test_allowed_markdown_prefixes(self) -> None:
        """At least README and CHANGELOG should be allowed in root."""
        from cortex.orchestrators.health.constants import ALLOWED_MARKDOWN_PREFIXES

        assert "README" in ALLOWED_MARKDOWN_PREFIXES
        assert "CHANGELOG" in ALLOWED_MARKDOWN_PREFIXES

    def test_kebab_max_len(self) -> None:
        from cortex.orchestrators.health.constants import KEBAB_MAX_LEN

        assert isinstance(KEBAB_MAX_LEN, int)
        assert KEBAB_MAX_LEN > 0

    def test_protected_root_extensions(self) -> None:
        """Extensions for files that are allowed in root."""
        from cortex.orchestrators.health.constants import PROTECTED_ROOT_EXTENSIONS

        assert ".toml" in PROTECTED_ROOT_EXTENSIONS
        assert ".cfg" in PROTECTED_ROOT_EXTENSIONS
        assert ".ini" in PROTECTED_ROOT_EXTENSIONS

    def test_archive_dir(self) -> None:
        """Archive location for stale markdown."""
        from cortex.orchestrators.health.constants import ARCHIVE_DIR

        assert ARCHIVE_DIR == ".cortex-runtime/archived-docs"

    def test_handoff_path(self) -> None:
        """Canonical handoff location."""
        from cortex.orchestrators.health.constants import HANDOFF_FILENAME

        assert HANDOFF_FILENAME == "health-issues.yaml"

    def test_rollback_filename(self) -> None:
        from cortex.orchestrators.health.constants import ROLLBACK_FILENAME

        assert ROLLBACK_FILENAME == "rollback-manifest.json"
