"""Tests for Phase 47 S2: Dual-Path Resolver."""

import pytest
from pathlib import Path
import tempfile
import yaml
import os
from cortex.orchestrators.company_separation.dual_path_resolver import (
    DualPathResolver,
    MigrationValidator,
    ResolutionResult,
)


@pytest.fixture
def temp_registry():
    """Create temporary registry structure."""
    with tempfile.TemporaryDirectory() as tmpdir:
        registry_root = tmpdir
        company_dir = f"{registry_root}/company"
        master_dir = f"{registry_root}/_cortex-master"
        legacy_dir = f"{tmpdir}/legacy_company"

        # Create directories
        Path(f"{company_dir}/domains").mkdir(parents=True, exist_ok=True)
        Path(f"{company_dir}/governance").mkdir(parents=True, exist_ok=True)
        Path(f"{master_dir}/domains").mkdir(parents=True, exist_ok=True)
        Path(f"{legacy_dir}/domains").mkdir(parents=True, exist_ok=True)

        # Create test files
        company_domain = {"name": "company_example", "tier": "company_override"}
        master_domain = {"name": "master_example", "tier": "master"}
        legacy_domain = {"name": "legacy_example", "tier": "legacy"}

        with open(f"{company_dir}/domains/example.yaml", 'w') as f:
            yaml.dump(company_domain, f)

        with open(f"{master_dir}/domains/example.yaml", 'w') as f:
            yaml.dump(master_domain, f)

        with open(f"{master_dir}/domains/master_only.yaml", 'w') as f:
            yaml.dump({"name": "master_only"}, f)

        with open(f"{legacy_dir}/domains/example.yaml", 'w') as f:
            yaml.dump(legacy_domain, f)

        yield registry_root, company_dir, master_dir, legacy_dir


class TestResolutionResult:
    """Test ResolutionResult dataclass."""

    def test_create_result(self):
        """Test creating resolution result."""
        result = ResolutionResult(
            found=True,
            source="company_registry",
            path="/path/to/file.yaml",
            content={"key": "value"},
            resolution_chain=["company_registry ✓"],
        )

        assert result.found is True
        assert result.source == "company_registry"
        assert result.path == "/path/to/file.yaml"
        assert result.content == {"key": "value"}
        assert result.resolution_chain == ["company_registry ✓"]

    def test_not_found_result(self):
        """Test creating not found result."""
        result = ResolutionResult(
            found=False,
            source="not_found",
            path=None,
            content=None,
            resolution_chain=["company ✗", "cortex ✗", "legacy ✗"],
        )

        assert result.found is False
        assert result.source == "not_found"


class TestDualPathResolver:
    """Test DualPathResolver class."""

    def test_initialize(self, temp_registry):
        """Test resolver initialization."""
        registry_root, _, _, legacy_dir = temp_registry
        resolver = DualPathResolver(registry_root, legacy_dir)

        assert resolver.registry_root == registry_root
        assert resolver.legacy_root == legacy_dir
        assert resolver.company_registry_root == f"{registry_root}/company"
        assert resolver.cortex_master_root == f"{registry_root}/_cortex-master"

    def test_resolve_company_precedence(self, temp_registry):
        """Test that company registry has highest precedence."""
        registry_root, _, _, legacy_dir = temp_registry
        resolver = DualPathResolver(registry_root, legacy_dir)

        result = resolver.resolve("domains/example.yaml")

        assert result.found is True
        assert result.source == "company_registry"
        assert result.content["tier"] == "company_override"

    def test_resolve_cortex_fallback(self, temp_registry):
        """Test fallback to cortex master."""
        registry_root, _, _, legacy_dir = temp_registry
        resolver = DualPathResolver(registry_root, legacy_dir)

        result = resolver.resolve("domains/master_only.yaml")

        assert result.found is True
        assert result.source == "cortex_master"
        assert result.content["name"] == "master_only"

    def test_resolve_legacy_fallback(self, temp_registry):
        """Test fallback to legacy directory."""
        registry_root, company_dir, master_dir, legacy_dir = temp_registry

        # Remove from company and master
        Path(f"{company_dir}/domains/example.yaml").unlink()
        Path(f"{master_dir}/domains/example.yaml").unlink()

        resolver = DualPathResolver(registry_root, legacy_dir)
        result = resolver.resolve("domains/example.yaml")

        assert result.found is True
        assert result.source == "legacy"
        assert result.content["tier"] == "legacy"

    def test_resolve_not_found(self, temp_registry):
        """Test resolution when file doesn't exist."""
        registry_root, _, _, legacy_dir = temp_registry
        resolver = DualPathResolver(registry_root, legacy_dir)

        result = resolver.resolve("domains/nonexistent.yaml")

        assert result.found is False
        assert result.source == "not_found"
        assert result.path is None
        assert result.content is None

    def test_resolution_chain_tracking(self, temp_registry):
        """Test that resolution chain is tracked."""
        registry_root, _, _, legacy_dir = temp_registry
        resolver = DualPathResolver(registry_root, legacy_dir)

        result = resolver.resolve("domains/example.yaml")

        assert "company_registry ✓" in result.resolution_chain
        assert len(result.resolution_chain) == 1

    def test_cache_behavior(self, temp_registry):
        """Test that resolutions are cached."""
        registry_root, _, _, legacy_dir = temp_registry
        resolver = DualPathResolver(registry_root, legacy_dir)

        # First call
        result1 = resolver.resolve("domains/example.yaml")
        # Second call should use cache
        result2 = resolver.resolve("domains/example.yaml")

        assert result1.found == result2.found
        assert result1.source == result2.source
        assert len(resolver.cache) == 1

    def test_clear_cache(self, temp_registry):
        """Test clearing cache."""
        registry_root, _, _, legacy_dir = temp_registry
        resolver = DualPathResolver(registry_root, legacy_dir)

        resolver.resolve("domains/example.yaml")
        assert len(resolver.cache) == 1

        result = resolver.resolve("domains/example.yaml", clear_cache=True)
        assert result.found is True
        assert len(resolver.cache) == 1

    def test_get_resolution_stats(self, temp_registry):
        """Test resolution statistics."""
        registry_root, _, _, legacy_dir = temp_registry
        resolver = DualPathResolver(registry_root, legacy_dir)

        resolver.resolve("domains/example.yaml")
        resolver.resolve("domains/master_only.yaml")
        resolver.resolve("domains/nonexistent.yaml")

        stats = resolver.get_resolution_stats()

        assert stats["total_resolutions"] == 3
        assert stats["company_registry_hits"] == 1
        assert stats["cortex_master_hits"] == 1
        assert stats["not_found"] == 1

    def test_empty_yaml_handling(self, temp_registry):
        """Test handling of empty YAML files."""
        registry_root, company_dir, _, legacy_dir = temp_registry

        # Create empty YAML file
        with open(f"{company_dir}/domains/empty.yaml", 'w') as f:
            f.write("")

        resolver = DualPathResolver(registry_root, legacy_dir)
        result = resolver.resolve("domains/empty.yaml")

        assert result.found is True
        assert result.content == {}

    def test_multiple_resolutions(self, temp_registry):
        """Test multiple resolution calls."""
        registry_root, _, _, legacy_dir = temp_registry
        resolver = DualPathResolver(registry_root, legacy_dir)

        results = [
            resolver.resolve("domains/example.yaml"),
            resolver.resolve("domains/master_only.yaml"),
            resolver.resolve("domains/nonexistent.yaml"),
        ]

        found_count = sum(1 for r in results if r.found)
        assert found_count == 2
        assert len(resolver.cache) == 3


class TestMigrationValidator:
    """Test MigrationValidator class."""

    def test_initialize_validator(self, temp_registry):
        """Test validator initialization."""
        registry_root, _, _, legacy_dir = temp_registry
        resolver = DualPathResolver(registry_root, legacy_dir)
        validator = MigrationValidator(resolver)

        assert validator.resolver == resolver
        assert len(validator.issues) == 0

    def test_validate_migration_success(self, temp_registry):
        """Test successful migration validation."""
        registry_root, _, _, legacy_dir = temp_registry
        resolver = DualPathResolver(registry_root, legacy_dir)
        validator = MigrationValidator(resolver)

        is_valid = validator.validate_migration(legacy_dir, f"{registry_root}/company")
        assert is_valid is True
        assert len(validator.get_issues()) == 0

    def test_validate_migration_nonexistent_source(self, temp_registry):
        """Test migration validation with nonexistent source."""
        registry_root, _, _, legacy_dir = temp_registry
        resolver = DualPathResolver(registry_root, legacy_dir)
        validator = MigrationValidator(resolver)

        is_valid = validator.validate_migration("/nonexistent", f"{registry_root}/company")
        assert is_valid is False
        assert len(validator.get_issues()) > 0

    def test_get_validation_issues(self, temp_registry):
        """Test getting validation issues."""
        registry_root, _, _, legacy_dir = temp_registry
        resolver = DualPathResolver(registry_root, legacy_dir)
        validator = MigrationValidator(resolver)

        validator.validate_migration("/nonexistent", f"{registry_root}/company")
        issues = validator.get_issues()

        assert len(issues) > 0
        assert any("not found" in issue.lower() for issue in issues)
