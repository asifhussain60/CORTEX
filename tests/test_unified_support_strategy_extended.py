"""
Tests for Extended Support Domain Strategy.

Tests all support capabilities (discovery, onboarding, lifecycle, migration)
and integration with unified domain orchestration framework.

AC_START: AC-WAVE7T2-2E-TEST-001
Tests: 16 total (discovery: 4, onboarding: 4, lifecycle: 4, migration: 4)
"""

import pytest
from cortex.orchestrators.unified_support_strategy_extended import (
    ExtendedSupportDomainStrategy,
    DiscoveryComponent,
    OnboardingComponent,
    LifecycleComponent,
    MigrationComponent,
    SupportContext,
    SupportOperation,
)


class TestDiscoveryComponent:
    """Tests for discovery component."""

    def test_component_initialization(self):
        """Test initialization."""
        discovery = DiscoveryComponent()
        assert discovery is not None
        assert len(discovery.supported_operations) > 0

    def test_discover_resources(self):
        """Test resource discovery."""
        discovery = DiscoveryComponent()
        context = SupportContext(
            operation=SupportOperation.DISCOVERY,
            target_path="/path/to/repo"
        )
        result = discovery.discover_resources(context)
        assert result.status == "success"
        assert result.data is not None
        assert "files" in result.data

    def test_discover_infrastructure(self):
        """Test infrastructure discovery."""
        discovery = DiscoveryComponent()
        context = SupportContext(
            operation=SupportOperation.DISCOVERY,
            target_path="/path/to/repo"
        )
        result = discovery.discover_infrastructure(context)
        assert result.status == "success"
        assert result.data is not None
        assert "database" in result.data

    def test_discover_capabilities(self):
        """Test capability discovery."""
        discovery = DiscoveryComponent()
        context = SupportContext(
            operation=SupportOperation.DISCOVERY,
            target_path="/path/to/repo"
        )
        result = discovery.discover_capabilities(context)
        assert result.status == "success"
        assert result.data is not None
        assert "api_endpoints" in result.data


class TestOnboardingComponent:
    """Tests for onboarding component."""

    def test_component_initialization(self):
        """Test initialization."""
        onboarding = OnboardingComponent()
        assert onboarding is not None
        assert len(onboarding.supported_operations) > 0

    def test_scan_repository(self):
        """Test repository scanning."""
        onboarding = OnboardingComponent()
        context = SupportContext(
            operation=SupportOperation.ONBOARDING,
            target_path="/path/to/repo"
        )
        result = onboarding.scan_repository(context)
        assert result.status == "success"
        assert result.data is not None
        assert "health_score" in result.data

    def test_analyze_security(self):
        """Test security analysis."""
        onboarding = OnboardingComponent()
        context = SupportContext(
            operation=SupportOperation.ONBOARDING,
            target_path="/path/to/repo"
        )
        result = onboarding.analyze_security(context)
        assert result.status == "success"
        assert result.data is not None
        assert "security_score" in result.data

    def test_generate_dashboard(self):
        """Test dashboard generation."""
        onboarding = OnboardingComponent()
        context = SupportContext(
            operation=SupportOperation.ONBOARDING,
            target_path="/path/to/repo"
        )
        result = onboarding.generate_dashboard(context)
        assert result.status == "success"
        assert result.data is not None
        assert "path" in result.data


class TestLifecycleComponent:
    """Tests for lifecycle component."""

    def test_component_initialization(self):
        """Test initialization."""
        lifecycle = LifecycleComponent()
        assert lifecycle is not None
        assert len(lifecycle.supported_operations) > 0

    def test_initialize(self):
        """Test lifecycle initialization."""
        lifecycle = LifecycleComponent()
        context = SupportContext(
            operation=SupportOperation.LIFECYCLE,
            target_path="/path/to/repo"
        )
        result = lifecycle.initialize(context)
        assert result.status == "success"
        assert result.message == "Lifecycle initialized"

    def test_transition_phase(self):
        """Test phase transition."""
        lifecycle = LifecycleComponent()
        context = SupportContext(
            operation=SupportOperation.LIFECYCLE,
            target_path="/path/to/repo"
        )
        result = lifecycle.transition_phase(context)
        assert result.status == "success"
        assert result.data is not None
        assert "to_phase" in result.data

    def test_get_status(self):
        """Test getting lifecycle status."""
        lifecycle = LifecycleComponent()
        context = SupportContext(
            operation=SupportOperation.LIFECYCLE,
            target_path="/path/to/repo"
        )
        result = lifecycle.get_status(context)
        assert result.status == "success"
        assert result.data is not None
        assert "current_phase" in result.data


class TestMigrationComponent:
    """Tests for migration component."""

    def test_component_initialization(self):
        """Test initialization."""
        migration = MigrationComponent()
        assert migration is not None
        assert len(migration.supported_operations) > 0

    def test_plan_migration(self):
        """Test migration planning."""
        migration = MigrationComponent()
        context = SupportContext(
            operation=SupportOperation.MIGRATION,
            target_path="/path/to/repo"
        )
        result = migration.plan_migration(context)
        assert result.status == "success"
        assert result.data is not None
        assert "steps" in result.data

    def test_execute_migration(self):
        """Test migration execution."""
        migration = MigrationComponent()
        context = SupportContext(
            operation=SupportOperation.MIGRATION,
            target_path="/path/to/repo"
        )
        result = migration.execute_migration(context)
        assert result.status == "success"
        assert result.data is not None
        assert result.data["status"] == "successful"

    def test_validate_migration(self):
        """Test migration validation."""
        migration = MigrationComponent()
        context = SupportContext(
            operation=SupportOperation.MIGRATION,
            target_path="/path/to/repo"
        )
        result = migration.validate_migration(context)
        assert result.status == "success"
        assert result.data is not None
        assert "data_integrity" in result.data


class TestExtendedSupportStrategy:
    """Tests for extended support strategy."""

    def test_strategy_initialization(self):
        """Test strategy initialization."""
        strategy = ExtendedSupportDomainStrategy()
        assert strategy is not None
        assert strategy.discovery is not None
        assert strategy.onboarding is not None
        assert strategy.lifecycle is not None
        assert strategy.migration is not None

    def test_get_metadata(self):
        """Test metadata retrieval."""
        strategy = ExtendedSupportDomainStrategy()
        metadata = strategy.get_metadata()
        assert metadata["name"] == "ExtendedSupportDomainStrategy"
        assert "discovery" in metadata["components"]
        assert metadata["total_supported_operations"] == 16

    def test_execute_discovery(self):
        """Test executing discovery via strategy."""
        strategy = ExtendedSupportDomainStrategy()
        context = SupportContext(
            operation=SupportOperation.DISCOVERY,
            target_path="/path/to/repo"
        )
        result = strategy.execute(context)
        assert result.status == "success"

    def test_execute_onboarding(self):
        """Test executing onboarding via strategy."""
        strategy = ExtendedSupportDomainStrategy()
        context = SupportContext(
            operation=SupportOperation.ONBOARDING,
            target_path="/path/to/repo"
        )
        result = strategy.execute(context)
        assert result.status == "success"

    def test_execute_lifecycle(self):
        """Test executing lifecycle via strategy."""
        strategy = ExtendedSupportDomainStrategy()
        context = SupportContext(
            operation=SupportOperation.LIFECYCLE,
            target_path="/path/to/repo"
        )
        result = strategy.execute(context)
        assert result.status == "success"

    def test_execute_migration(self):
        """Test executing migration via strategy."""
        strategy = ExtendedSupportDomainStrategy()
        context = SupportContext(
            operation=SupportOperation.MIGRATION,
            target_path="/path/to/repo"
        )
        result = strategy.execute(context)
        assert result.status == "success"


class TestSupportStrategyIntegration:
    """Integration tests for support strategy."""

    def test_all_operations_supported(self):
        """Test all support operations."""
        strategy = ExtendedSupportDomainStrategy()
        
        operations = [
            SupportOperation.DISCOVERY,
            SupportOperation.ONBOARDING,
            SupportOperation.LIFECYCLE,
            SupportOperation.MIGRATION,
        ]
        
        for operation in operations:
            context = SupportContext(
                operation=operation,
                target_path="/path/to/repo"
            )
            result = strategy.execute(context)
            assert result.status == "success"

    def test_context_creation(self):
        """Test context creation and properties."""
        context = SupportContext(
            operation=SupportOperation.DISCOVERY,
            target_path="/path/to/repo",
            options={"key": "value"}
        )
        assert context.operation == SupportOperation.DISCOVERY
        assert context.target_path == "/path/to/repo"
        assert context.options is not None
        assert context.options["key"] == "value"
        assert context.timestamp is not None

    def test_support_result_properties(self):
        """Test support result properties."""
        strategy = ExtendedSupportDomainStrategy()
        context = SupportContext(
            operation=SupportOperation.DISCOVERY,
            target_path="/path/to/repo"
        )
        result = strategy.discover(context)
        assert result.operation == SupportOperation.DISCOVERY
        assert result.status == "success"
        assert result.duration_ms > 0


# AC_COMPLETE: AC-WAVE7T2-2E-TEST-001 ✅ 16 test cases for support strategy
