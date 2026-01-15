"""
Tests for Orchestrator Dependency Registry - AC-AR-015-02

Comprehensive test coverage for tier-orchestrator dependencies including:
- Orchestrator registration
- Tier dependency management
- Transitive dependency tracking
- Circular dependency detection
- Impact analysis
- Validation and consistency checking
- Persistence and loading
"""

import pytest
from pathlib import Path
import tempfile
import json

from src.core.orchestrator_dependency_registry import (
    OrchestratorDependencyRegistry,
    TierLevel,
    DependencyType,
    RegistryValidationResult,
    TierDependency,
    OrchestratorProfile,
    DependencyPath,
    RegistryValidationReport,
)


@pytest.fixture
def registry():
    """Create a fresh registry for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir) / "registry.json"
        reg = OrchestratorDependencyRegistry(storage_path=storage_path)
        yield reg


@pytest.fixture
def registry_with_orchestrators(registry):
    """Create a registry with sample orchestrators."""
    registry.register_orchestrator("orch-base", "Base Orchestrator", "Core orchestrator")
    registry.register_orchestrator("orch-ai", "AI Orchestrator", "Handles AI logic", parent_orchestrator="orch-base")
    registry.register_orchestrator("orch-data", "Data Orchestrator", "Handles data", parent_orchestrator="orch-base")
    return registry


class TestTierDependency:
    """Test TierDependency data structure."""

    def test_create_tier_dependency(self):
        """Test creating a tier dependency."""
        dep = TierDependency(
            tier=TierLevel.TIER0,
            dependency_type=DependencyType.DIRECT,
            required_features=["governance", "validation"],
        )
        
        assert dep.tier == TierLevel.TIER0
        assert dep.dependency_type == DependencyType.DIRECT
        assert len(dep.required_features) == 2

    def test_tier_dependency_serialization(self):
        """Test converting tier dependency to and from dictionary."""
        dep = TierDependency(
            tier=TierLevel.TIER1,
            dependency_type=DependencyType.TRANSITIVE,
            via_orchestrator="parent-orch",
            required_features=["acceptance"],
        )
        
        dep_dict = dep.to_dict()
        restored = TierDependency.from_dict(dep_dict)
        
        assert restored.tier == dep.tier
        assert restored.dependency_type == dep.dependency_type
        assert restored.via_orchestrator == dep.via_orchestrator


class TestOrchestratorProfile:
    """Test OrchestratorProfile data structure."""

    def test_create_orchestrator_profile(self):
        """Test creating an orchestrator profile."""
        profile = OrchestratorProfile(
            orchestrator_id="orch-123",
            name="Test Orchestrator",
            description="For testing",
        )
        
        assert profile.orchestrator_id == "orch-123"
        assert profile.name == "Test Orchestrator"
        assert len(profile.tier_dependencies) == 0

    def test_profile_serialization(self):
        """Test converting profile to and from dictionary."""
        profile = OrchestratorProfile(
            orchestrator_id="orch-123",
            name="Test",
            parent_orchestrator="parent",
            description="Test description",
        )
        
        profile_dict = profile.to_dict()
        restored = OrchestratorProfile.from_dict(profile_dict)
        
        assert restored.orchestrator_id == profile.orchestrator_id
        assert restored.parent_orchestrator == profile.parent_orchestrator


class TestOrchestratorRegistration:
    """Test orchestrator registration."""

    def test_register_orchestrator(self, registry):
        """Test registering a new orchestrator."""
        success, msg = registry.register_orchestrator(
            "orch-ai",
            "AI Handler",
            "Handles AI logic"
        )
        
        assert success is True
        assert "orch-ai" in registry.orchestrators

    def test_register_duplicate_orchestrator(self, registry):
        """Test registering duplicate orchestrator fails."""
        registry.register_orchestrator("orch-ai", "AI Handler")
        success, msg = registry.register_orchestrator("orch-ai", "Another AI")
        
        assert success is False
        assert "already registered" in msg.lower()

    def test_register_with_invalid_parent(self, registry):
        """Test registering with non-existent parent fails."""
        success, msg = registry.register_orchestrator(
            "orch-child",
            "Child",
            parent_orchestrator="non-existent"
        )
        
        assert success is False
        assert "not found" in msg.lower()

    def test_register_with_valid_parent(self, registry):
        """Test registering with valid parent succeeds."""
        registry.register_orchestrator("orch-base", "Base")
        success, msg = registry.register_orchestrator(
            "orch-child",
            "Child",
            parent_orchestrator="orch-base"
        )
        
        assert success is True


class TestTierDependencyManagement:
    """Test adding and removing tier dependencies."""

    def test_add_tier_dependency(self, registry_with_orchestrators):
        """Test adding a tier dependency."""
        success, msg = registry_with_orchestrators.add_tier_dependency(
            "orch-ai",
            TierLevel.TIER0,
            DependencyType.DIRECT,
            required_features=["governance"]
        )
        
        assert success is True
        profile = registry_with_orchestrators.orchestrators["orch-ai"]
        assert "tier0" in profile.tier_dependencies

    def test_cannot_add_duplicate_dependency(self, registry_with_orchestrators):
        """Test that duplicate dependencies cannot be added."""
        registry_with_orchestrators.add_tier_dependency(
            "orch-ai",
            TierLevel.TIER0,
            DependencyType.DIRECT,
        )
        
        success, msg = registry_with_orchestrators.add_tier_dependency(
            "orch-ai",
            TierLevel.TIER0,
            DependencyType.DIRECT,
        )
        
        assert success is False
        assert "already exists" in msg.lower()

    def test_cannot_depend_on_self(self, registry_with_orchestrators):
        """Test that orchestrator cannot depend on itself."""
        success, msg = registry_with_orchestrators.add_tier_dependency(
            "orch-ai",
            TierLevel.TIER2,
            DependencyType.TRANSITIVE,
            via_orchestrator="orch-ai"
        )
        
        assert success is False
        assert "itself" in msg.lower()

    def test_remove_tier_dependency(self, registry_with_orchestrators):
        """Test removing a tier dependency."""
        registry_with_orchestrators.add_tier_dependency("orch-ai", TierLevel.TIER0)
        
        success, msg = registry_with_orchestrators.remove_tier_dependency("orch-ai", TierLevel.TIER0)
        
        assert success is True
        profile = registry_with_orchestrators.orchestrators["orch-ai"]
        assert "tier0" not in profile.tier_dependencies


class TestGetTierDependencies:
    """Test querying tier dependencies."""

    def test_get_direct_dependencies(self, registry_with_orchestrators):
        """Test getting direct tier dependencies."""
        registry_with_orchestrators.add_tier_dependency("orch-ai", TierLevel.TIER0)
        registry_with_orchestrators.add_tier_dependency("orch-ai", TierLevel.TIER1)
        
        deps = registry_with_orchestrators.get_tier_dependencies("orch-ai", include_inherited=False)
        
        assert len(deps) == 2
        assert "tier0" in deps
        assert "tier1" in deps

    def test_get_inherited_dependencies(self, registry_with_orchestrators):
        """Test getting inherited dependencies from parent."""
        registry_with_orchestrators.add_tier_dependency("orch-base", TierLevel.TIER0)
        
        deps = registry_with_orchestrators.get_tier_dependencies("orch-ai", include_inherited=True)
        
        assert len(deps) == 1
        assert "tier0" in deps
        assert deps["tier0"].dependency_type == DependencyType.INHERITED

    def test_orchestrators_for_tier(self, registry_with_orchestrators):
        """Test getting orchestrators for a specific tier."""
        registry_with_orchestrators.add_tier_dependency("orch-ai", TierLevel.TIER0)
        registry_with_orchestrators.add_tier_dependency("orch-data", TierLevel.TIER0)
        
        orchs = registry_with_orchestrators.get_orchestrators_for_tier(TierLevel.TIER0)
        
        assert len(orchs) == 2
        assert "orch-ai" in orchs
        assert "orch-data" in orchs


class TestTransitiveDependencies:
    """Test transitive orchestrator dependencies."""

    def test_find_transitive_dependencies_single_level(self, registry_with_orchestrators):
        """Test finding transitive dependencies one level deep."""
        transitive = registry_with_orchestrators.find_transitive_dependencies("orch-ai")
        
        assert "orch-base" in transitive

    def test_find_transitive_dependencies_multi_level(self):
        """Test finding transitive dependencies multiple levels deep."""
        with tempfile.TemporaryDirectory() as tmpdir:
            registry = OrchestratorDependencyRegistry(Path(tmpdir) / "registry.json")
            
            registry.register_orchestrator("orch-1", "Level 1")
            registry.register_orchestrator("orch-2", "Level 2", parent_orchestrator="orch-1")
            registry.register_orchestrator("orch-3", "Level 3", parent_orchestrator="orch-2")
            
            transitive = registry.find_transitive_dependencies("orch-3")
            
            assert "orch-2" in transitive
            assert "orch-1" in transitive
            assert len(transitive) == 2


class TestCircularDependencyDetection:
    """Test detecting circular dependencies."""

    def test_no_circular_dependencies(self, registry_with_orchestrators):
        """Test registry with no circular dependencies."""
        circular = registry_with_orchestrators.detect_circular_dependencies()
        
        assert len(circular) == 0

    def test_detect_simple_circular_dependency(self):
        """Test detecting a simple circular dependency."""
        with tempfile.TemporaryDirectory() as tmpdir:
            registry = OrchestratorDependencyRegistry(Path(tmpdir) / "registry.json")
            
            registry.register_orchestrator("orch-a", "A")
            registry.register_orchestrator("orch-b", "B", parent_orchestrator="orch-a")
            
            # Manually create circular reference for testing
            registry.orchestrators["orch-a"].parent_orchestrator = "orch-b"
            
            circular = registry.detect_circular_dependencies()
            
            assert len(circular) > 0


class TestValidation:
    """Test registry validation."""

    def test_validate_valid_registry(self, registry_with_orchestrators):
        """Test validating a valid registry."""
        report = registry_with_orchestrators.validate_registry()
        
        assert report.is_valid is True
        assert report.result == RegistryValidationResult.VALID

    def test_validate_with_broken_parent_reference(self):
        """Test validating with broken parent reference."""
        with tempfile.TemporaryDirectory() as tmpdir:
            registry = OrchestratorDependencyRegistry(Path(tmpdir) / "registry.json")
            
            registry.register_orchestrator("orch-a", "A")
            registry.orchestrators["orch-a"].parent_orchestrator = "non-existent"
            
            report = registry.validate_registry()
            
            assert report.is_valid is False
            assert report.result == RegistryValidationResult.UNRESOLVED_ORCHESTRATOR

    def test_validation_report_structure(self, registry_with_orchestrators):
        """Test validation report structure."""
        report = registry_with_orchestrators.validate_registry()
        
        assert hasattr(report, "is_valid")
        assert hasattr(report, "result")
        assert hasattr(report, "errors")
        assert hasattr(report, "warnings")
        assert report.total_orchestrators == 3


class TestImpactAnalysis:
    """Test analyzing impact of tier changes."""

    def test_tier_change_impact_no_dependencies(self, registry):
        """Test impact analysis when no orchestrators depend on tier."""
        impact = registry.analyze_tier_change_impact(TierLevel.TIER0, "major")
        
        assert impact["directly_affected_orchestrators"] == 0
        assert impact["total_affected"] == 0

    def test_tier_change_impact_direct_dependencies(self, registry_with_orchestrators):
        """Test impact analysis with direct dependencies."""
        registry_with_orchestrators.add_tier_dependency("orch-ai", TierLevel.TIER0)
        registry_with_orchestrators.add_tier_dependency("orch-data", TierLevel.TIER0)
        
        impact = registry_with_orchestrators.analyze_tier_change_impact(TierLevel.TIER0, "breaking")
        
        assert impact["directly_affected_orchestrators"] == 2
        assert impact["change_severity"] == "breaking"

    def test_tier_change_impact_transitive(self, registry_with_orchestrators):
        """Test impact analysis with transitive dependencies."""
        registry_with_orchestrators.add_tier_dependency("orch-base", TierLevel.TIER0)
        
        impact = registry_with_orchestrators.analyze_tier_change_impact(TierLevel.TIER0, "major")
        
        assert impact["directly_affected_orchestrators"] >= 1


class TestRegistryStatistics:
    """Test registry statistics."""

    def test_stats_empty_registry(self, registry):
        """Test statistics for empty registry."""
        stats = registry.get_registry_stats()
        
        assert stats["total_orchestrators"] == 0
        assert stats["has_circular_dependencies"] is False

    def test_stats_with_orchestrators(self, registry_with_orchestrators):
        """Test statistics with populated registry."""
        registry_with_orchestrators.add_tier_dependency("orch-ai", TierLevel.TIER0)
        registry_with_orchestrators.add_tier_dependency("orch-data", TierLevel.TIER1)
        
        stats = registry_with_orchestrators.get_registry_stats()
        
        assert stats["total_orchestrators"] == 3
        assert stats["by_tier"]["tier0"] >= 1
        assert stats["orchestrators_with_parents"] == 2


class TestRegistryExport:
    """Test exporting registry data."""

    def test_export_empty_registry(self, registry):
        """Test exporting an empty registry."""
        export = registry.export_registry()
        
        assert "orchestrators" in export
        assert "tier_assignments" in export
        assert len(export["orchestrators"]) == 0

    def test_export_with_data(self, registry_with_orchestrators):
        """Test exporting registry with data."""
        registry_with_orchestrators.add_tier_dependency("orch-ai", TierLevel.TIER0)
        
        export = registry_with_orchestrators.export_registry()
        
        assert len(export["orchestrators"]) == 3
        assert len(export["tier_assignments"]["tier0"]) >= 1

    def test_export_json_serializable(self, registry_with_orchestrators):
        """Test that exported data is JSON serializable."""
        registry_with_orchestrators.add_tier_dependency("orch-ai", TierLevel.TIER1)
        export = registry_with_orchestrators.export_registry()
        
        # Should not raise exception
        json_str = json.dumps(export)
        assert len(json_str) > 0


class TestRegistryPersistence:
    """Test saving and loading registry."""

    def test_save_and_load_registry(self):
        """Test persisting registry to disk and reloading."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "registry.json"
            
            # Create and populate registry
            registry1 = OrchestratorDependencyRegistry(storage_path=storage_path)
            registry1.register_orchestrator("orch-a", "Orchestrator A", "First")
            registry1.register_orchestrator("orch-b", "Orchestrator B", "Second", parent_orchestrator="orch-a")
            registry1.add_tier_dependency("orch-a", TierLevel.TIER0)
            registry1._save_to_storage()
            
            # Load into new registry
            registry2 = OrchestratorDependencyRegistry(storage_path=storage_path)
            
            assert len(registry2.orchestrators) == 2
            assert "orch-a" in registry2.orchestrators
            assert "orch-b" in registry2.orchestrators
            assert registry2.orchestrators["orch-b"].parent_orchestrator == "orch-a"

    def test_auto_save_on_changes(self):
        """Test that changes are automatically saved."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "registry.json"
            
            registry1 = OrchestratorDependencyRegistry(storage_path=storage_path)
            registry1.register_orchestrator("orch-test", "Test Orchestrator")
            
            # Verify file was created
            assert storage_path.exists()
            
            # Load and verify
            registry2 = OrchestratorDependencyRegistry(storage_path=storage_path)
            assert "orch-test" in registry2.orchestrators


class TestComplexScenarios:
    """Test complex registry scenarios."""

    def test_multi_tier_orchestrator(self, registry):
        """Test orchestrator depending on multiple tiers."""
        registry.register_orchestrator("orch-complex", "Complex Orchestrator")
        registry.add_tier_dependency("orch-complex", TierLevel.TIER0)
        registry.add_tier_dependency("orch-complex", TierLevel.TIER1)
        registry.add_tier_dependency("orch-complex", TierLevel.TIER2)
        registry.add_tier_dependency("orch-complex", TierLevel.TIER3)
        
        deps = registry.get_tier_dependencies("orch-complex")
        
        assert len(deps) == 4

    def test_orchestrator_hierarchy(self, registry):
        """Test deep orchestrator hierarchy."""
        registry.register_orchestrator("base", "Base")
        registry.register_orchestrator("level1", "Level 1", parent_orchestrator="base")
        registry.register_orchestrator("level2", "Level 2", parent_orchestrator="level1")
        registry.register_orchestrator("level3", "Level 3", parent_orchestrator="level2")
        
        transitive = registry.find_transitive_dependencies("level3")
        
        assert len(transitive) == 3
        assert "level2" in transitive
        assert "level1" in transitive
        assert "base" in transitive

    def test_multiple_orchestrator_impact(self, registry):
        """Test impact analysis with multiple tiers affected."""
        registry.register_orchestrator("orch-a", "A")
        registry.register_orchestrator("orch-b", "B")
        registry.register_orchestrator("orch-c", "C")
        
        registry.add_tier_dependency("orch-a", TierLevel.TIER0)
        registry.add_tier_dependency("orch-b", TierLevel.TIER0)
        registry.add_tier_dependency("orch-c", TierLevel.TIER1)
        
        impact_t0 = registry.analyze_tier_change_impact(TierLevel.TIER0, "major")
        impact_t1 = registry.analyze_tier_change_impact(TierLevel.TIER1, "minor")
        
        assert impact_t0["directly_affected_orchestrators"] == 2
        assert impact_t1["directly_affected_orchestrators"] == 1
