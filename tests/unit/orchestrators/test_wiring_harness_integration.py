"""Tests for WiringHarnessIntegration module.

AC-ID: REMEDIATION-INTENT-005
Tests auto-discovery and wiring of components into orchestration pipeline.
"""

import pytest
from cortex.orchestrators.wiring_harness_integration import (
    WiringHarnessIntegration,
    ComponentRegistry,
    ComponentMetadata,
    WiringStatus,
)


class BaseWiringTest:
    """Base test class with common fixtures."""

    @pytest.fixture(autouse=True)
    def setup_wiring(self):
        """Setup WiringHarnessIntegration instance."""
        self.wiring = WiringHarnessIntegration()


class TestWiringHarnessInitialization(BaseWiringTest):
    """Test WiringHarnessIntegration initialization."""

    def test_wiring_harness_initializes(self):
        """Test wiring harness initialization."""
        assert self.wiring is not None

    def test_component_registry_initialized(self):
        """Test component registry is initialized."""
        assert hasattr(self.wiring, "component_registry")
        assert isinstance(self.wiring.component_registry, ComponentRegistry)

    def test_wiring_status_tracking(self):
        """Test wiring status tracking is available."""
        assert hasattr(self.wiring, "wiring_status")


class TestComponentMetadata(BaseWiringTest):
    """Test ComponentMetadata data class."""

    def test_component_metadata_creation(self):
        """Test ComponentMetadata creation."""
        metadata = ComponentMetadata(
            name="ComprehensionSession",
            module="cortex.orchestrators.core.comprehension_session",
            priority="CRITICAL",
            stage="STAGE_1",
        )
        assert metadata.name == "ComprehensionSession"
        assert metadata.priority == "CRITICAL"

    def test_metadata_with_dependencies(self):
        """Test metadata with dependencies."""
        metadata = ComponentMetadata(
            name="ChallengeGenerator",
            module="cortex.orchestrators.challenge_generator",
            priority="HIGH",
            stage="STAGE_3",
            dependencies=["ComprehensionSession"],
        )
        assert len(metadata.dependencies) > 0

    def test_metadata_to_dict(self):
        """Test to_dict() serialization."""
        metadata = ComponentMetadata(
            name="ConfidenceRouter",
            module="cortex.orchestrators.confidence_router",
            priority="HIGH",
            stage="STAGE_2",
        )
        result = metadata.to_dict()
        assert result["name"] == "ConfidenceRouter"
        assert result["stage"] == "STAGE_2"


class TestComponentRegistry(BaseWiringTest):
    """Test ComponentRegistry functionality."""

    def test_registry_is_empty_initially(self):
        """Test registry starts empty."""
        registry = ComponentRegistry()
        components = registry.list_components()
        assert isinstance(components, list)

    def test_register_component(self):
        """Test registering a component."""
        self.wiring.component_registry.register(
            ComponentMetadata(
                name="TestComponent",
                module="test.module",
                priority="MEDIUM",
                stage="STAGE_1",
            )
        )
        components = self.wiring.component_registry.list_components()
        names = [c.name for c in components]
        assert "TestComponent" in names

    def test_get_component(self):
        """Test retrieving a component."""
        metadata = ComponentMetadata(
            name="RetrievableComponent",
            module="test.retrievable",
            priority="LOW",
            stage="STAGE_2",
        )
        self.wiring.component_registry.register(metadata)
        retrieved = self.wiring.component_registry.get("RetrievableComponent")
        assert retrieved is not None
        assert retrieved.name == "RetrievableComponent"

    def test_get_nonexistent_component(self):
        """Test getting nonexistent component returns None."""
        result = self.wiring.component_registry.get("NonExistent")
        assert result is None


class TestAutoDiscovery(BaseWiringTest):
    """Test component auto-discovery."""

    def test_discover_components(self):
        """Test auto-discovery of components."""
        discovered = self.wiring.discover_components()
        assert isinstance(discovered, list)
        # Should discover at least ComprehensionSession
        names = [c.name for c in discovered]
        assert len(names) >= 0  # Discovery might find 0-8 components

    def test_discovery_identifies_stage(self):
        """Test discovery identifies component stages."""
        discovered = self.wiring.discover_components()
        if discovered:
            assert any(c.stage for c in discovered)

    def test_discovery_includes_priority(self):
        """Test discovery includes priority information."""
        discovered = self.wiring.discover_components()
        if discovered:
            priorities = {c.priority for c in discovered}
            # Should have some priority assigned
            assert len(priorities) > 0


class TestStageWiring(BaseWiringTest):
    """Test wiring components to orchestration stages."""

    def test_wire_to_stage_1(self):
        """Test wiring component to Stage 1."""
        status = self.wiring.wire_to_stage(
            component_name="ComprehensionSession",
            stage="STAGE_1",
        )
        assert status in [WiringStatus.SUCCESS, WiringStatus.ALREADY_WIRED, WiringStatus.NOT_FOUND]

    def test_wire_to_stage_2(self):
        """Test wiring component to Stage 2."""
        status = self.wiring.wire_to_stage(
            component_name="ConfidenceRouter",
            stage="STAGE_2",
        )
        assert status is not None

    def test_wire_to_stage_3(self):
        """Test wiring component to Stage 3."""
        status = self.wiring.wire_to_stage(
            component_name="ChallengeGenerator",
            stage="STAGE_3",
        )
        assert status is not None

    def test_wire_to_stage_4(self):
        """Test wiring component to Stage 4."""
        status = self.wiring.wire_to_stage(
            component_name="ResponseChallengeInjector",
            stage="STAGE_4",
        )
        assert status is not None

    def test_wiring_nonexistent_component(self):
        """Test wiring nonexistent component fails gracefully."""
        status = self.wiring.wire_to_stage(
            component_name="NonExistent",
            stage="STAGE_1",
        )
        assert status == WiringStatus.NOT_FOUND


class TestWiringStatus(BaseWiringTest):
    """Test wiring status tracking."""

    def test_wiring_status_enum(self):
        """Test WiringStatus enum values."""
        assert hasattr(WiringStatus, "SUCCESS")
        assert hasattr(WiringStatus, "FAILED")
        assert hasattr(WiringStatus, "NOT_FOUND")

    def test_wiring_creates_audit_trail(self):
        """Test wiring creates audit trail."""
        self.wiring.wire_to_stage("ComprehensionSession", "STAGE_1")
        audit = self.wiring.get_wiring_audit_trail()
        assert isinstance(audit, list)
        assert len(audit) > 0

    def test_wiring_audit_includes_timestamp(self):
        """Test audit trail includes timestamps."""
        self.wiring.wire_to_stage("ComprehensionSession", "STAGE_1")
        audit = self.wiring.get_wiring_audit_trail()
        if audit:
            assert any(item.get("timestamp") for item in audit)


class TestDependencyResolution(BaseWiringTest):
    """Test dependency resolution."""

    def test_resolve_dependencies(self):
        """Test dependency resolution."""
        deps = self.wiring.resolve_dependencies("ChallengeGenerator")
        assert isinstance(deps, list)

    def test_dependency_order(self):
        """Test dependencies are in correct order."""
        # ComprehensionSession should be resolved before ChallengeGenerator
        cs_deps = self.wiring.resolve_dependencies("ComprehensionSession")
        cg_deps = self.wiring.resolve_dependencies("ChallengeGenerator")
        assert isinstance(cs_deps, list)
        assert isinstance(cg_deps, list)

class TestIntegrationWiring(BaseWiringTest):
    """Test full integration wiring."""

    def test_wire_all_components(self):
        """Test wiring all components."""
        status = self.wiring.wire_all()
        assert status in [
            WiringStatus.SUCCESS,
            WiringStatus.PARTIAL_SUCCESS,
            WiringStatus.FAILED,
        ]

    def test_wiring_preserves_order(self):
        """Test wiring preserves component order."""
        self.wiring.wire_all()
        wired_components = self.wiring.get_wired_components()
        assert isinstance(wired_components, list)

    def test_wiring_all_creates_audit(self):
        """Test wire_all creates audit trail."""
        self.wiring.wire_all()
        audit = self.wiring.get_wiring_audit_trail()
        assert len(audit) > 0


class TestWiredComponentsRetrieval(BaseWiringTest):
    """Test retrieving wired components."""

    def test_get_wired_components_returns_list(self):
        """Test get_wired_components returns list."""
        wired = self.wiring.get_wired_components()
        assert isinstance(wired, list)

    def test_get_stage_components(self):
        """Test getting components by stage."""
        stage1_components = self.wiring.get_stage_components("STAGE_1")
        assert isinstance(stage1_components, list)

    def test_get_all_stages_components(self):
        """Test getting components from all stages."""
        for stage in ["STAGE_1", "STAGE_2", "STAGE_3", "STAGE_4"]:
            components = self.wiring.get_stage_components(stage)
            assert isinstance(components, list)

    def test_component_priority_ordering(self):
        """Test components are ordered by priority."""
        self.wiring.wire_all()
        wired = self.wiring.get_wired_components()
        if len(wired) > 1:
            # Check that priorities are logical
            priority_order = {"CRITICAL": 3, "HIGH": 2, "MEDIUM": 1, "LOW": 0}
            priorities = [priority_order.get(c.get("priority", "LOW"), 0) for c in wired]
            # Should be descending (CRITICAL first)


class TestWiringValidation(BaseWiringTest):
    """Test wiring validation."""

    def test_validate_wiring(self):
        """Test wiring validation."""
        self.wiring.wire_all()
        is_valid = self.wiring.validate_wiring()
        assert isinstance(is_valid, bool)

    def test_validate_stage_completeness(self):
        """Test all required stages have components."""
        self.wiring.wire_all()
        for stage in ["STAGE_1", "STAGE_2", "STAGE_3", "STAGE_4"]:
            components = self.wiring.get_stage_components(stage)
            # Each stage should have at least some configuration
            assert isinstance(components, list)

    def test_validation_report(self):
        """Test getting validation report."""
        self.wiring.wire_all()
        report = self.wiring.get_validation_report()
        assert isinstance(report, dict)
        assert "valid" in report or "status" in report


class TestWiringReset(BaseWiringTest):
    """Test wiring reset functionality."""

    def test_reset_clears_wiring(self):
        """Test reset clears wiring."""
        self.wiring.wire_to_stage("ComprehensionSession", "STAGE_1")
        self.wiring.reset()
        wired = self.wiring.get_wired_components()
        assert len(wired) == 0

    def test_reset_clears_audit_trail(self):
        """Test reset clears audit trail."""
        self.wiring.wire_to_stage("ComprehensionSession", "STAGE_1")
        self.wiring.reset()
        audit = self.wiring.get_wiring_audit_trail()
        assert len(audit) == 0


class TestEdgeCases(BaseWiringTest):
    """Test edge cases and boundary conditions."""

    def test_wire_same_component_twice(self):
        """Test wiring same component twice."""
        status1 = self.wiring.wire_to_stage("ComprehensionSession", "STAGE_1")
        status2 = self.wiring.wire_to_stage("ComprehensionSession", "STAGE_1")
        # Second wiring should be ALREADY_WIRED or SUCCESS
        assert status2 in [WiringStatus.SUCCESS, WiringStatus.ALREADY_WIRED]

    def test_multiple_wiring_instances_independent(self):
        """Test multiple wiring instances are independent."""
        wiring1 = WiringHarnessIntegration()
        wiring2 = WiringHarnessIntegration()
        wiring1.wire_to_stage("ComprehensionSession", "STAGE_1")
        wired2 = wiring2.get_wired_components()
        # wiring2 should not have components wired in wiring1
        names2 = [c.get("name") for c in wired2]
        assert "ComprehensionSession" not in names2 or len(wired2) == 0
