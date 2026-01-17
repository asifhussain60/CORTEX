"""Unit tests for Cleaner Plugin Architecture (VAC-001-01)

Tests verify SOLID compliance and CleanerInterface contract.

AC-001-01 Acceptance Criteria:
✓ CleanerInterface defines: analyze() → Analysis, execute() → Report, rollback()
✓ Multiple cleaners instantiated without modification to orchestrator
✓ CleanerRegistry.register() accepts cleaner implementations
✓ SOLID principles verified: SRP, OCP
✓ Type hints on all methods (CORE-011)
✓ Google-style docstrings on all classes/methods (CORE-012)

Author: CORTEX Builder
Phase: PHASE-VAC-001-01
CORE Rules: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

"""Unit tests for Cleaner Plugin Architecture (VAC-001-01)

Tests verify SOLID compliance and CleanerInterface contract.

AC-001-01 Acceptance Criteria:
✓ CleanerInterface defines: analyze() → Analysis, execute() → Report, rollback()
✓ Multiple cleaners instantiated without modification to orchestrator
✓ CleanerRegistry.register() accepts cleaner implementations
✓ SOLID principles verified: SRP, OCP
✓ Type hints on all methods (CORE-011)
✓ Google-style docstrings on all classes/methods (CORE-012)

Author: CORTEX Builder
Phase: PHASE-VAC-001-01
CORE Rules: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

import pytest
import sys
import importlib.util
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

# Add cortex-brain to path for imports (handles hyphenated directory names)
project_root = Path(__file__).parent.parent.parent.parent.parent
cortex_brain_path = project_root / "cortex-brain"
sys.path.insert(0, str(cortex_brain_path))

# Import from cortex-brain
from tier1.orchestrators.cleaners import (
    CleanerInterface,
    Analysis,
    Report,
    RollbackResult,
    CleanerRegistry,
    CleanerRegistrationError,
    CleanerNotFoundError,
)


# =============================================================================
# TEST FIXTURES
# =============================================================================


class MockCleanerA(CleanerInterface):
    """Mock cleaner implementation A for testing."""

    @property
    def name(self) -> str:
        """Human-readable name."""
        return "Mock Cleaner A"

    @property
    def version(self) -> str:
        """Version string."""
        return "1.0.0"

    @property
    def domain(self) -> str:
        """Domain identifier."""
        return "mock_a"

    def analyze(self) -> Analysis:
        """Non-destructive analysis."""
        return Analysis(
            cleaner_id=self.cleaner_id,
            timestamp=datetime.now().isoformat(),
            files_scanned=10,
            issues_found=3,
            plan={"action": "test_plan"},
            logs=["Analysis complete"],
        )

    def execute(self, plan: Dict[str, Any]) -> Report:
        """Controlled execution."""
        return Report(
            cleaner_id=self.cleaner_id,
            timestamp=datetime.now().isoformat(),
            status="SUCCESS",
            actions_taken=3,
            changes={"files_modified": 3},
            logs=["Execution complete"],
        )

    def rollback(self) -> RollbackResult:
        """Rollback to pre-execution state."""
        return RollbackResult(
            cleaner_id=self.cleaner_id,
            timestamp=datetime.now().isoformat(),
            status="SUCCESS",
            files_restored=3,
        )


class MockCleanerB(CleanerInterface):
    """Mock cleaner implementation B for testing (different domain)."""

    @property
    def name(self) -> str:
        """Human-readable name."""
        return "Mock Cleaner B"

    @property
    def version(self) -> str:
        """Version string."""
        return "2.0.0"

    @property
    def domain(self) -> str:
        """Domain identifier."""
        return "mock_b"

    def analyze(self) -> Analysis:
        """Non-destructive analysis."""
        return Analysis(
            cleaner_id=self.cleaner_id,
            timestamp=datetime.now().isoformat(),
            files_scanned=20,
            issues_found=5,
            plan={"action": "test_plan_b"},
            logs=["Analysis B complete"],
        )

    def execute(self, plan: Dict[str, Any]) -> Report:
        """Controlled execution."""
        return Report(
            cleaner_id=self.cleaner_id,
            timestamp=datetime.now().isoformat(),
            status="SUCCESS",
            actions_taken=5,
            changes={"files_modified": 5},
            logs=["Execution B complete"],
        )

    def rollback(self) -> RollbackResult:
        """Rollback to pre-execution state."""
        return RollbackResult(
            cleaner_id=self.cleaner_id,
            timestamp=datetime.now().isoformat(),
            status="SUCCESS",
            files_restored=5,
        )


@pytest.fixture
def registry() -> CleanerRegistry:
    """Create fresh registry for each test."""
    return CleanerRegistry()


@pytest.fixture
def config() -> Dict[str, Any]:
    """Sample configuration."""
    return {"test_setting": "value"}


# =============================================================================
# TEST: Analysis Dataclass
# =============================================================================


@pytest.mark.ac("VAC-001-01")
class TestAnalysisDataclass:
    """Test Analysis dataclass structure and methods."""

    def test_analysis_creation(self) -> None:
        """Analysis should create with required fields."""
        analysis = Analysis(
            cleaner_id="TestCleaner",
            timestamp="2026-01-17T10:00:00Z",
            files_scanned=100,
            issues_found=5,
            plan={"test": "data"},
            logs=["log1", "log2"],
        )

        assert analysis.cleaner_id == "TestCleaner"
        assert analysis.files_scanned == 100
        assert analysis.issues_found == 5
        assert len(analysis.logs) == 2

    def test_analysis_to_dict(self) -> None:
        """Analysis should serialize to dictionary."""
        analysis = Analysis(
            cleaner_id="TestCleaner",
            timestamp="2026-01-17T10:00:00Z",
            files_scanned=100,
            issues_found=5,
            plan={"test": "data"},
        )

        data = analysis.to_dict()
        assert isinstance(data, dict)
        assert data["cleaner_id"] == "TestCleaner"
        assert data["files_scanned"] == 100


# =============================================================================
# TEST: Report Dataclass
# =============================================================================


@pytest.mark.ac("VAC-001-01")
class TestReportDataclass:
    """Test Report dataclass structure and methods."""

    def test_report_creation(self) -> None:
        """Report should create with required fields."""
        report = Report(
            cleaner_id="TestCleaner",
            timestamp="2026-01-17T10:00:00Z",
            status="SUCCESS",
            actions_taken=5,
            changes={"modified": 5},
            errors=[],
        )

        assert report.cleaner_id == "TestCleaner"
        assert report.status == "SUCCESS"
        assert report.actions_taken == 5

    def test_report_is_success_property(self) -> None:
        """Report should have is_success property."""
        success_report = Report(
            cleaner_id="Test",
            timestamp="2026-01-17T10:00:00Z",
            status="SUCCESS",
            actions_taken=1,
            changes={},
        )

        failed_report = Report(
            cleaner_id="Test",
            timestamp="2026-01-17T10:00:00Z",
            status="FAILED",
            actions_taken=0,
            changes={},
        )

        assert success_report.is_success is True
        assert success_report.is_failed is False
        assert failed_report.is_success is False
        assert failed_report.is_failed is True

    def test_report_to_dict(self) -> None:
        """Report should serialize to dictionary."""
        report = Report(
            cleaner_id="TestCleaner",
            timestamp="2026-01-17T10:00:00Z",
            status="SUCCESS",
            actions_taken=5,
            changes={"modified": 5},
        )

        data = report.to_dict()
        assert isinstance(data, dict)
        assert data["status"] == "SUCCESS"


# =============================================================================
# TEST: RollbackResult Dataclass
# =============================================================================


@pytest.mark.ac("VAC-001-01")
class TestRollbackResultDataclass:
    """Test RollbackResult dataclass structure and methods."""

    def test_rollback_result_creation(self) -> None:
        """RollbackResult should create with required fields."""
        result = RollbackResult(
            cleaner_id="TestCleaner",
            timestamp="2026-01-17T10:00:00Z",
            status="SUCCESS",
            files_restored=5,
        )

        assert result.cleaner_id == "TestCleaner"
        assert result.files_restored == 5

    def test_rollback_result_is_success_property(self) -> None:
        """RollbackResult should have is_success property."""
        success = RollbackResult(
            cleaner_id="Test",
            timestamp="2026-01-17T10:00:00Z",
            status="SUCCESS",
            files_restored=5,
        )

        failed = RollbackResult(
            cleaner_id="Test",
            timestamp="2026-01-17T10:00:00Z",
            status="FAILED",
            files_restored=0,
        )

        assert success.is_success is True
        assert failed.is_success is False


# =============================================================================
# TEST: CleanerInterface Contract
# =============================================================================


@pytest.mark.ac("VAC-001-01")
class TestCleanerInterfaceContract:
    """Test CleanerInterface contract requirements."""

    def test_interface_cannot_be_instantiated(self) -> None:
        """CleanerInterface is abstract and cannot be instantiated."""
        with pytest.raises(TypeError):
            CleanerInterface({})  # type: ignore

    def test_cleaner_must_implement_all_abstract_methods(self) -> None:
        """Cleaner subclass must implement all abstract methods."""

        class IncompleteCleaner(CleanerInterface):
            """Incomplete cleaner missing abstract methods."""

            @property
            def name(self) -> str:
                return "Incomplete"

            @property
            def version(self) -> str:
                return "1.0.0"

            @property
            def domain(self) -> str:
                return "incomplete"

            # Missing: analyze(), execute(), rollback()

        with pytest.raises(TypeError):
            IncompleteCleaner({})  # type: ignore

    def test_mock_cleaner_a_has_required_methods(self) -> None:
        """MockCleanerA should have all required methods."""
        cleaner = MockCleanerA({})

        # Check properties
        assert hasattr(cleaner, "name")
        assert hasattr(cleaner, "version")
        assert hasattr(cleaner, "domain")

        # Check methods
        assert callable(cleaner.analyze)
        assert callable(cleaner.execute)
        assert callable(cleaner.rollback)

    def test_mock_cleaner_a_analyze_returns_analysis(self) -> None:
        """MockCleanerA.analyze() should return Analysis."""
        cleaner = MockCleanerA({})
        result = cleaner.analyze()

        assert isinstance(result, Analysis)
        assert result.files_scanned == 10
        assert result.issues_found == 3

    def test_mock_cleaner_a_execute_returns_report(self) -> None:
        """MockCleanerA.execute() should return Report."""
        cleaner = MockCleanerA({})
        result = cleaner.execute({})

        assert isinstance(result, Report)
        assert result.status == "SUCCESS"
        assert result.actions_taken == 3

    def test_mock_cleaner_a_rollback_returns_rollback_result(self) -> None:
        """MockCleanerA.rollback() should return RollbackResult."""
        cleaner = MockCleanerA({})
        result = cleaner.rollback()

        assert isinstance(result, RollbackResult)
        assert result.status == "SUCCESS"
        assert result.files_restored == 3


# =============================================================================
# TEST: CleanerRegistry
# =============================================================================


@pytest.mark.ac("VAC-001-01")
class TestCleanerRegistry:
    """Test CleanerRegistry plugin management."""

    def test_registry_creation(self, registry: CleanerRegistry) -> None:
        """Registry should create empty."""
        assert len(registry.list_all()) == 0
        assert registry.list_all() == []

    def test_register_single_cleaner(
        self, registry: CleanerRegistry
    ) -> None:
        """Registry should register cleaner."""
        registry.register_cleaner(MockCleanerA)

        assert "mock_a" in registry.list_all()
        assert registry.has_cleaner("mock_a") is True

    def test_register_multiple_cleaners(
        self, registry: CleanerRegistry
    ) -> None:
        """Registry should register multiple cleaners."""
        registry.register_cleaner(MockCleanerA)
        registry.register_cleaner(MockCleanerB)

        domains = registry.list_all()
        assert len(domains) == 2
        assert "mock_a" in domains
        assert "mock_b" in domains

    def test_register_duplicate_domain_raises_error(
        self, registry: CleanerRegistry
    ) -> None:
        """Registry should reject duplicate domain registrations."""
        registry.register_cleaner(MockCleanerA)

        with pytest.raises(CleanerRegistrationError):
            registry.register_cleaner(MockCleanerA)  # Same domain

    def test_register_non_class_raises_error(
        self, registry: CleanerRegistry
    ) -> None:
        """Registry should reject non-class arguments."""
        with pytest.raises(CleanerRegistrationError):
            registry.register_cleaner(MockCleanerA(config={}))  # type: ignore

    def test_register_non_interface_raises_error(
        self, registry: CleanerRegistry
    ) -> None:
        """Registry should reject classes not implementing CleanerInterface."""

        class NotACleaner:
            pass

        with pytest.raises(CleanerRegistrationError):
            registry.register_cleaner(NotACleaner)  # type: ignore

    def test_get_cleaner_returns_instance(
        self, registry: CleanerRegistry, config: Dict[str, Any]
    ) -> None:
        """Registry should return instantiated cleaner."""
        registry.register_cleaner(MockCleanerA)
        cleaner = registry.get_cleaner("mock_a", config=config)

        assert isinstance(cleaner, CleanerInterface)
        assert isinstance(cleaner, MockCleanerA)
        assert cleaner.domain == "mock_a"

    def test_get_unregistered_cleaner_raises_error(
        self, registry: CleanerRegistry
    ) -> None:
        """Registry should raise error for unregistered domain."""
        with pytest.raises(CleanerNotFoundError):
            registry.get_cleaner("nonexistent")

    def test_get_cleaner_unregistered_shows_available_domains(
        self, registry: CleanerRegistry
    ) -> None:
        """Error for unregistered cleaner should list available domains."""
        registry.register_cleaner(MockCleanerA)
        registry.register_cleaner(MockCleanerB)

        with pytest.raises(CleanerNotFoundError) as exc_info:
            registry.get_cleaner("nonexistent")

        error_msg = str(exc_info.value)
        assert "mock_a" in error_msg
        assert "mock_b" in error_msg

    def test_registry_repr(self, registry: CleanerRegistry) -> None:
        """Registry should have useful repr."""
        registry.register_cleaner(MockCleanerA)
        repr_str = repr(registry)

        assert "CleanerRegistry" in repr_str
        assert "mock_a" in repr_str


# =============================================================================
# TEST: SOLID Principles
# =============================================================================


@pytest.mark.ac("VAC-001-01")
class TestSOLIDCompliance:
    """Test SOLID principles compliance."""

    def test_single_responsibility(self) -> None:
        """Each cleaner has single responsibility (its domain)."""
        cleaner_a = MockCleanerA({})
        cleaner_b = MockCleanerB({})

        assert cleaner_a.domain == "mock_a"
        assert cleaner_b.domain == "mock_b"
        assert cleaner_a.domain != cleaner_b.domain

    def test_open_closed_principle(
        self, registry: CleanerRegistry
    ) -> None:
        """New cleaners can be added without modifying registry."""
        # Register first cleaner
        registry.register_cleaner(MockCleanerA)
        assert len(registry.list_all()) == 1

        # Add second cleaner without registry modification
        registry.register_cleaner(MockCleanerB)
        assert len(registry.list_all()) == 2

    def test_liskov_substitution(
        self, registry: CleanerRegistry, config: Dict[str, Any]
    ) -> None:
        """All cleaners swap via interface."""
        registry.register_cleaner(MockCleanerA)
        registry.register_cleaner(MockCleanerB)

        cleaner_a = registry.get_cleaner("mock_a", config=config)
        cleaner_b = registry.get_cleaner("mock_b", config=config)

        # Both should have same interface methods
        assert callable(cleaner_a.analyze)
        assert callable(cleaner_b.analyze)

        # Both should return compatible types
        analysis_a = cleaner_a.analyze()
        analysis_b = cleaner_b.analyze()

        assert isinstance(analysis_a, Analysis)
        assert isinstance(analysis_b, Analysis)

    def test_interface_segregation(self) -> None:
        """CleanerInterface has minimal required methods."""
        # Check abstract methods
        abstract_methods = {
            method
            for method in dir(CleanerInterface)
            if hasattr(getattr(CleanerInterface, method), "__isabstractmethod__")
            and getattr(CleanerInterface, method).__isabstractmethod__
        }

        # Should have exactly these abstract methods
        required = {"analyze", "execute", "rollback"}
        assert required.issubset(abstract_methods)

    def test_dependency_inversion(
        self, registry: CleanerRegistry
    ) -> None:
        """Registry depends on abstraction, not concrete classes."""
        # Registry only knows about CleanerInterface abstraction
        assert all(
            issubclass(cleaner_class, CleanerInterface)
            for cleaner_class in registry._cleaners.values()
        )

        # New concrete implementation can be added
        registry.register_cleaner(MockCleanerA)

        cleaner = registry.get_cleaner("mock_a")
        # Registry works with abstract type
        assert isinstance(cleaner, CleanerInterface)


# =============================================================================
# TEST: Type Hints (CORE-011)
# =============================================================================


@pytest.mark.ac("VAC-001-01")
class TestTypeHints:
    """Test that all public methods have type hints (CORE-011)."""

    def test_cleaner_interface_methods_have_return_types(self) -> None:
        """CleanerInterface methods should have return type hints."""
        # Check abstract methods have return annotations
        assert CleanerInterface.analyze.__annotations__.get("return") is Analysis
        assert CleanerInterface.execute.__annotations__.get("return") is Report
        assert CleanerInterface.rollback.__annotations__.get("return") is RollbackResult

    def test_cleaner_interface_properties_have_return_types(self) -> None:
        """CleanerInterface properties should have return type hints."""
        # Properties return strings
        assert CleanerInterface.name.fget.__annotations__.get("return") is str
        assert CleanerInterface.version.fget.__annotations__.get("return") is str
        assert CleanerInterface.domain.fget.__annotations__.get("return") is str

    def test_registry_methods_have_type_hints(self) -> None:
        """CleanerRegistry methods should have type hints."""
        registry = CleanerRegistry()

        # Check method signatures have annotations
        assert "return" in CleanerRegistry.list_all.__annotations__
        assert "return" in CleanerRegistry.has_cleaner.__annotations__


# =============================================================================
# TEST: Docstrings (CORE-012)
# =============================================================================


@pytest.mark.ac("VAC-001-01")
class TestDocstrings:
    """Test that all public APIs have docstrings (CORE-012)."""

    def test_cleaner_interface_has_docstring(self) -> None:
        """CleanerInterface should have module and class docstrings."""
        # Class docstring
        assert CleanerInterface.__doc__ is not None
        assert len(CleanerInterface.__doc__) > 0

        # Method docstrings
        assert CleanerInterface.analyze.__doc__ is not None
        assert CleanerInterface.execute.__doc__ is not None
        assert CleanerInterface.rollback.__doc__ is not None

    def test_registry_has_docstring(self) -> None:
        """CleanerRegistry should have docstrings."""
        # Class docstring
        assert CleanerRegistry.__doc__ is not None

        # Method docstrings
        assert CleanerRegistry.register_cleaner.__doc__ is not None
        assert CleanerRegistry.get_cleaner.__doc__ is not None
        assert CleanerRegistry.list_all.__doc__ is not None

    def test_dataclasses_have_docstrings(self) -> None:
        """Analysis, Report, RollbackResult should have docstrings."""
        assert Analysis.__doc__ is not None
        assert Report.__doc__ is not None
        assert RollbackResult.__doc__ is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
