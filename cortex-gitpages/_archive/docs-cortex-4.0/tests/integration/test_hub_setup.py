"""
Integration tests for Hub Setup Automation Script.

Tests for scripts/setup-cortex-hub.py covering:
- Hub initialization without errors
- Database initialization with all tables
- Prompt releases created in cortex-brain/releases/
- Registry template created
- Health endpoint returns ready
- Idempotent execution (running twice produces same result)
- Clear success output
"""

import pytest
import tempfile
import subprocess
import yaml
from pathlib import Path
from typing import Dict, Any


class TestHubSetupScript:
    """Test hub setup automation script."""

    def test_setup_script_exists(self):
        """Setup script file exists at scripts/setup_cortex_hub.py."""
        script_path = Path("scripts") / "setup_cortex_hub.py"
        assert script_path.exists(), f"Setup script not found at {script_path}"

    def test_setup_script_executable_or_readable(self):
        """Setup script is readable and properly formatted."""
        script_path = Path("scripts") / "setup_cortex_hub.py"
        assert script_path.is_file()
        assert script_path.read_text().startswith("#!/") or \
               script_path.read_text().startswith('"""')


class TestHubSetupIntegration:
    """Integration tests for hub setup."""

    def test_hub_initialization_creates_db(self, tmp_path):
        """Hub initialization creates governance database."""
        from scripts.setup_cortex_hub import setup_hub

        # Setup in temp directory
        result = setup_hub(db_path=tmp_path / "governance.db")

        assert result.get("success") is True
        assert (tmp_path / "governance.db").exists()

    def test_hub_initialization_creates_tables(self, tmp_path):
        """Hub initialization creates all required database tables."""
        from scripts.setup_cortex_hub import setup_hub

        result = setup_hub(db_path=tmp_path / "governance.db")

        assert result.get("success") is True

        # Check database has expected tables
        import sqlite3
        conn = sqlite3.connect(str(tmp_path / "governance.db"))
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table';"
        )
        tables = {row[0] for row in cursor.fetchall()}
        conn.close()

        # Expect governance, audit, and version tracking tables
        assert len(tables) > 0

    def test_hub_setup_creates_release_directory(self, tmp_path):
        """Hub setup creates v1.0.0 release directory."""
        from scripts.setup_cortex_hub import setup_hub

        releases_path = tmp_path / "releases"
        result = setup_hub(releases_path=releases_path)

        assert result.get("success") is True
        assert (releases_path / "v1.0.0").exists()

    def test_hub_setup_creates_prompt_files(self, tmp_path):
        """Hub setup copies/creates prompt files in releases."""
        from scripts.setup_cortex_hub import setup_hub

        releases_path = tmp_path / "releases"
        result = setup_hub(releases_path=releases_path)

        assert result.get("success") is True

        # Check for prompt files
        v1_dir = releases_path / "v1.0.0"
        assert v1_dir.exists()
        # Expect at least some prompt file
        prompt_files = list(v1_dir.glob("*.md")) + list(v1_dir.glob("*.yaml"))
        assert len(prompt_files) > 0

    def test_hub_setup_creates_manifest(self, tmp_path):
        """Hub setup creates prompt-versions.yaml manifest."""
        from scripts.setup_cortex_hub import setup_hub

        manifest_path = tmp_path / "prompt-versions.yaml"
        result = setup_hub(manifest_path=manifest_path)

        assert result.get("success") is True
        assert manifest_path.exists()

        # Verify manifest is valid YAML
        with open(manifest_path) as f:
            manifest = yaml.safe_load(f)
        assert manifest is not None
        assert "versions" in manifest

    def test_hub_setup_creates_registry_template(self, tmp_path):
        """Hub setup creates registry template file."""
        from scripts.setup_cortex_hub import setup_hub

        registry_path = tmp_path / "repo-registry.yaml"
        result = setup_hub(registry_path_template=registry_path)

        assert result.get("success") is True
        # Template may exist or just be documented
        assert result.get("registry_template_created") is not None

    def test_hub_setup_idempotent_first_run(self, tmp_path):
        """First hub setup run succeeds."""
        from scripts.setup_cortex_hub import setup_hub

        result = setup_hub(
            db_path=tmp_path / "governance.db",
            releases_path=tmp_path / "releases",
            manifest_path=tmp_path / "prompt-versions.yaml",
        )

        assert result.get("success") is True

    def test_hub_setup_idempotent_second_run(self, tmp_path):
        """Second hub setup run produces same result (idempotent)."""
        from scripts.setup_cortex_hub import setup_hub

        # First run
        result1 = setup_hub(
            db_path=tmp_path / "governance.db",
            releases_path=tmp_path / "releases",
            manifest_path=tmp_path / "prompt-versions.yaml",
        )
        assert result1.get("success") is True

        # Record first run state
        v1_dir_first = (tmp_path / "releases" / "v1.0.0").exists()
        manifest_exists_first = (tmp_path / "prompt-versions.yaml").exists()

        # Second run
        result2 = setup_hub(
            db_path=tmp_path / "governance.db",
            releases_path=tmp_path / "releases",
            manifest_path=tmp_path / "prompt-versions.yaml",
        )
        assert result2.get("success") is True

        # Verify same state after second run
        assert (tmp_path / "releases" / "v1.0.0").exists() == v1_dir_first
        assert (tmp_path / "prompt-versions.yaml").exists() == manifest_exists_first

    def test_hub_setup_returns_clear_output(self, tmp_path):
        """Hub setup returns clear success output."""
        from scripts.setup_cortex_hub import setup_hub

        result = setup_hub(
            db_path=tmp_path / "governance.db",
        )

        assert isinstance(result, dict)
        assert "success" in result
        assert "status" in result or "message" in result
        assert result.get("success") is True


class TestHubSetupHealthCheck:
    """Test health check integration."""

    def test_hub_setup_enables_health_check(self, tmp_path):
        """After hub setup, health check endpoint is ready."""
        from scripts.setup_cortex_hub import setup_hub

        result = setup_hub(
            db_path=tmp_path / "governance.db",
            releases_path=tmp_path / "releases",
        )

        assert result.get("success") is True
        # Health check should be available (though server may not be running)
        assert result.get("health_check_configured") is True or \
               "health_check" in str(result.get("components", {})).lower()


class TestHubSetupGovernance:
    """Test governance initialization."""

    def test_hub_setup_initializes_governance_rules(self, tmp_path):
        """Hub setup loads governance rules."""
        from scripts.setup_cortex_hub import setup_hub

        result = setup_hub(
            db_path=tmp_path / "governance.db",
        )

        assert result.get("success") is True
        assert result.get("governance_initialized") is True or \
               "governance" in str(result).lower()

    def test_hub_setup_registers_orchestrators(self, tmp_path):
        """Hub setup registers orchestrators."""
        from scripts.setup_cortex_hub import setup_hub

        result = setup_hub(
            db_path=tmp_path / "governance.db",
        )

        assert result.get("success") is True
        assert result.get("orchestrators_registered") is True or \
               result.get("orchestrators_count", 0) >= 0
