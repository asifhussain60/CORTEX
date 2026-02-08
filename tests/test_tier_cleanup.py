"""Tests for Phase 47 S4: Tier Cleanup."""

import pytest
from pathlib import Path
import tempfile
import yaml
import shutil
from cortex.orchestrators.company_separation.tier_cleanup import (
    TierOverride,
    TierAnalyzer,
    TierCleanup,
    TierBackup,
)


class TestTierOverride:
    """Test TierOverride dataclass."""

    def test_create_override(self):
        """Test creating tier override."""
        override = TierOverride(
            tier_name="tier0",
            override_type="domain",
            original_path="/path/to/tier0.yaml",
            target_path="cortex-registry/company/domain/example.yaml",
            content={"name": "example"},
        )

        assert override.tier_name == "tier0"
        assert override.override_type == "domain"
        assert override.content["name"] == "example"


class TestTierAnalyzer:
    """Test TierAnalyzer class."""

    @pytest.fixture
    def temp_tier_file(self):
        """Create temporary tier file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            tier_content = {
                "base_config": "default",
                "company_domain": {"name": "acme"},
                "company_governance": {"policy": "strict"},
                "standard_setting": "value",
            }
            yaml.dump(tier_content, f)
            temp_path = f.name

        yield temp_path

        Path(temp_path).unlink()

    def test_initialize_analyzer(self):
        """Test analyzer initialization."""
        analyzer = TierAnalyzer()

        assert analyzer.tier_root != ""
        assert len(analyzer.overrides) == 0

    def test_analyze_file_finds_overrides(self, temp_tier_file):
        """Test analyzing file finds company overrides."""
        analyzer = TierAnalyzer()
        overrides = analyzer.analyze_tier(temp_tier_file)

        assert len(overrides) >= 2
        assert any(o.override_type == "domain" for o in overrides)
        assert any(o.override_type == "governance" for o in overrides)

    def test_analyze_file_nonexistent(self):
        """Test analyzing nonexistent file."""
        analyzer = TierAnalyzer()
        overrides = analyzer.analyze_tier("/nonexistent/file.yaml")

        assert len(overrides) == 0

    def test_analyze_directory(self):
        """Test analyzing directory."""
        analyzer = TierAnalyzer()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test tier files
            tier_file = Path(tmpdir) / "tier0.yaml"
            tier_file.write_text(
                yaml.dump(
                    {
                        "base_config": "default",
                        "company_domain": {"name": "acme"},
                    }
                )
            )

            overrides = analyzer.analyze_directory(tmpdir)
            assert len(overrides) > 0

    def test_get_overrides_by_type(self, temp_tier_file):
        """Test filtering overrides by type."""
        analyzer = TierAnalyzer()
        analyzer.analyze_tier(temp_tier_file)

        domain_overrides = analyzer.get_overrides_by_type("domain")
        assert len(domain_overrides) > 0
        assert all(o.override_type == "domain" for o in domain_overrides)

    def test_is_company_override(self):
        """Test company override detection."""
        analyzer = TierAnalyzer()

        assert analyzer._is_company_override("company_domain", {}) is True
        assert analyzer._is_company_override("customer_config", {}) is True
        assert analyzer._is_company_override("standard_field", {}) is False

    def test_classify_override(self):
        """Test override classification."""
        analyzer = TierAnalyzer()

        assert analyzer._classify_override("company_domain") == "domain"
        assert analyzer._classify_override("company_governance") == "governance"
        assert analyzer._classify_override("company_config") == "config"

    def test_compute_target_path(self):
        """Test target path computation."""
        analyzer = TierAnalyzer()

        path = analyzer._compute_target_path("company_domain")
        assert "cortex-registry/company" in path
        assert "domain" in path

    def test_get_summary(self, temp_tier_file):
        """Test getting analysis summary."""
        analyzer = TierAnalyzer()
        analyzer.analyze_tier(temp_tier_file)

        summary = analyzer.get_summary()

        assert "total_overrides" in summary
        assert summary["total_overrides"] > 0
        assert "by_type" in summary


class TestTierCleanup:
    """Test TierCleanup class."""

    def test_initialize_cleanup(self):
        """Test cleanup initialization."""
        analyzer = TierAnalyzer()
        cleanup = TierCleanup(analyzer)

        assert cleanup.analyzer == analyzer
        assert len(cleanup.removals) == 0

    def test_cleanup_file(self):
        """Test cleaning a tier file."""
        analyzer = TierAnalyzer()
        cleanup = TierCleanup(analyzer)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            tier_content = {
                "base_config": "default",
                "company_domain": {"name": "acme"},
            }
            yaml.dump(tier_content, f)
            temp_path = f.name

        success = cleanup.cleanup_file(temp_path)

        assert success is True
        assert len(cleanup.removals) > 0

        # Verify file was cleaned
        with open(temp_path, 'r') as f:
            cleaned = yaml.safe_load(f)
        assert "company_domain" not in cleaned
        assert "base_config" in cleaned

        Path(temp_path).unlink()

    def test_cleanup_directory(self):
        """Test cleaning directory."""
        analyzer = TierAnalyzer()
        cleanup = TierCleanup(analyzer)

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            for i in range(2):
                tier_file = Path(tmpdir) / f"tier{i}.yaml"
                tier_file.write_text(
                    yaml.dump(
                        {
                            "base": "value",
                            "company_domain": {"name": "test"},
                        }
                    )
                )

            count = cleanup.cleanup_directory(tmpdir)
            assert count > 0

    def test_add_migration(self):
        """Test adding migration record."""
        analyzer = TierAnalyzer()
        cleanup = TierCleanup(analyzer)

        cleanup.add_migration("company_domain", "cortex-registry/company/domain/example.yaml")

        assert len(cleanup.migrations) == 1
        assert cleanup.migrations[0]["status"] == "migrated"

    def test_get_migration_summary(self):
        """Test getting migration summary."""
        analyzer = TierAnalyzer()
        cleanup = TierCleanup(analyzer)

        cleanup.add_migration("key1", "path1")
        cleanup.add_migration("key2", "path2")

        summary = cleanup.get_migration_summary()

        assert "total_migrations" in summary
        assert summary["total_migrations"] == 2


class TestTierBackup:
    """Test TierBackup class."""

    def test_initialize_backup(self):
        """Test backup initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backup = TierBackup(tmpdir)

            assert backup.tier_root == tmpdir
            assert len(backup.backed_up_files) == 0

    def test_create_backup(self):
        """Test creating backup."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create tier structure
            tier_dir = Path(tmpdir) / "tier0"
            tier_dir.mkdir()
            (tier_dir / "config.yaml").write_text("key: value\n")

            backup = TierBackup(tmpdir)
            success = backup.create_backup()

            assert success is True
            assert backup.get_backup_size() > 0

    def test_get_backup_size(self):
        """Test getting backup size."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create tier structure
            tier_dir = Path(tmpdir) / "tier0"
            tier_dir.mkdir()
            (tier_dir / "config.yaml").write_text("key: value\n")

            backup = TierBackup(tmpdir)
            backup.create_backup()

            assert backup.get_backup_size() > 0

    def test_get_backup_location(self):
        """Test getting backup location."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backup = TierBackup(tmpdir)

            location = backup.get_backup_location()
            assert "tier_backup" in location
