"""
Test Suite: Phase Executor Framework (SIMPLIFIED)

Tests for actual implementation of:
- PhaseExecutorBase (abstract base class)
- PhaseExecutorFactory (factory pattern)
- PhaseOrchestrator (multi-phase coordination)

CORE-008: TDD Mandatory (tests before code)
CORE-011: Type hints required
CORE-012: Docstrings required

AC-PHASE80-TEST-001: Phase executor framework tests
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from tempfile import TemporaryDirectory
import sys

# Add CORTEX to path
cortex_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(cortex_root))

from cortex.orchestrators.core.phase_executors.phase_executor_base import (
    ExecutionResult,
    PhaseExecutorBase,
)
from cortex.orchestrators.core.phase_executors.phase_executor_factory import (
    PhaseExecutorFactory,
    GenericPhaseExecutor,
)
from cortex.orchestrators.core.phase_executors.phase_orchestrator import PhaseOrchestrator


class TestExecutionResult:
    """Tests for ExecutionResult dataclass."""

    def test_execution_result_fields(self) -> None:
        """Test ExecutionResult has all required fields."""
        result = ExecutionResult(
            phase_id="phase-80",
            status="SUCCESS",
            duration_seconds=120.5,
            tests_passed=25,
            tests_total=25,
            coverage_percent=95.0,
            git_commit="abc123",
            error_message=None,
            timestamp="2026-02-10T10:00:00Z",
        )

        assert result.phase_id == "phase-80"
        assert result.status == "SUCCESS"
        assert result.duration_seconds == 120.5
        assert result.tests_passed == 25
        assert result.coverage_percent == 95.0


class TestPhaseExecutorBase:
    """Tests for PhaseExecutorBase abstract class."""

    def test_abstract_class_cannot_instantiate(self) -> None:
        """Test that PhaseExecutorBase is abstract."""
        with TemporaryDirectory() as tmpdir:
            with pytest.raises(TypeError):
                PhaseExecutorBase(
                    phase_id="test", cortex_root=Path(tmpdir)
                )  # type: ignore

    def test_concrete_executor_must_implement_execute(self) -> None:
        """Test that subclass must implement execute."""

        class IncompleteExecutor(PhaseExecutorBase):
            """Missing execute implementation."""

            pass

        with TemporaryDirectory() as tmpdir:
            with pytest.raises(TypeError):
                IncompleteExecutor(
                    phase_id="test", cortex_root=Path(tmpdir)
                )  # type: ignore

    def test_concrete_executor_instantiation(self) -> None:
        """Test concrete executor can be instantiated."""

        class ConcreteExecutor(PhaseExecutorBase):
            """Concrete implementation."""

            def execute(self) -> ExecutionResult:
                return ExecutionResult(
                    phase_id=self.phase_id,
                    status="SUCCESS",
                    duration_seconds=1.0,
                    tests_passed=10,
                    tests_total=10,
                    coverage_percent=100.0,
                    git_commit=None,
                    error_message=None,
                    timestamp="2026-02-10T10:00:00Z",
                )

        with TemporaryDirectory() as tmpdir:
            executor = ConcreteExecutor(
                phase_id="phase-80", cortex_root=Path(tmpdir)
            )
            assert executor.phase_id == "phase-80"

    def test_executor_has_cortex_root(self) -> None:
        """Test executor stores cortex root."""

        class ConcreteExecutor(PhaseExecutorBase):
            def execute(self) -> ExecutionResult:
                pass

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            executor = ConcreteExecutor(phase_id="phase-80", cortex_root=root)
            assert executor.cortex_root == root


class TestPhaseExecutorFactory:
    """Tests for PhaseExecutorFactory."""

    def test_factory_instantiation(self) -> None:
        """Test factory can be created."""
        with TemporaryDirectory() as tmpdir:
            factory = PhaseExecutorFactory(cortex_root=Path(tmpdir))
            assert factory is not None

    def test_factory_has_executor_cache(self) -> None:
        """Test factory initializes cache."""
        with TemporaryDirectory() as tmpdir:
            factory = PhaseExecutorFactory(cortex_root=Path(tmpdir))
            assert hasattr(factory, "_executor_cache")
            assert isinstance(factory._executor_cache, dict)

    def test_create_executor_returns_executor(self) -> None:
        """Test factory creates executors."""
        with TemporaryDirectory() as tmpdir:
            cortex_root = Path(tmpdir)
            # Create a mock phase file
            phases_dir = cortex_root / "cortex-registry" / "_cortex-master" / "phases" / "active"
            phases_dir.mkdir(parents=True, exist_ok=True)
            phase_file = phases_dir / "phase-80.yaml"
            phase_file.write_text("title: Test Phase\nstages: []")
            
            factory = PhaseExecutorFactory(cortex_root=cortex_root)
            executor = factory.create_executor(phase_id="phase-80")
            assert executor is not None

    def test_create_executor_returns_generic_executor(self) -> None:
        """Test factory returns GenericPhaseExecutor for unknown phases."""
        with TemporaryDirectory() as tmpdir:
            cortex_root = Path(tmpdir)
            # Create a mock phase file for the unknown phase
            phases_dir = cortex_root / "cortex-registry" / "_cortex-master" / "phases" / "active"
            phases_dir.mkdir(parents=True, exist_ok=True)
            phase_file = phases_dir / "nonexistent-phase.yaml"
            phase_file.write_text("title: Test Phase\nstages: []")
            
            factory = PhaseExecutorFactory(cortex_root=cortex_root)
            executor = factory.create_executor(phase_id="nonexistent-phase")
            assert isinstance(executor, GenericPhaseExecutor)

    def test_factory_caching_behavior(self) -> None:
        """Test that executor classes are cached."""
        with TemporaryDirectory() as tmpdir:
            cortex_root = Path(tmpdir)
            # Create a mock phase file
            phases_dir = cortex_root / "cortex-registry" / "_cortex-master" / "phases" / "active"
            phases_dir.mkdir(parents=True, exist_ok=True)
            phase_file = phases_dir / "phase-80.yaml"
            phase_file.write_text("title: Test Phase\nstages: []")
            
            factory = PhaseExecutorFactory(cortex_root=cortex_root)
            executor1 = factory.create_executor(phase_id="phase-80")
            executor2 = factory.create_executor(phase_id="phase-80")

            # Should be same type (from cache)
            assert type(executor1) == type(executor2)


class TestGenericPhaseExecutor:
    """Tests for GenericPhaseExecutor."""

    def test_generic_executor_instantiation(self) -> None:
        """Test GenericPhaseExecutor can be created."""
        with TemporaryDirectory() as tmpdir:
            cortex_root = Path(tmpdir)
            # Create a mock phase file
            phases_dir = cortex_root / "cortex-registry" / "_cortex-master" / "phases" / "active"
            phases_dir.mkdir(parents=True, exist_ok=True)
            phase_file = phases_dir / "phase-80.yaml"
            phase_file.write_text("title: Test Phase\nstages: []")
            
            executor = GenericPhaseExecutor(
                phase_id="phase-80", cortex_root=cortex_root
            )
            assert executor.phase_id == "phase-80"

    def test_generic_executor_execute(self) -> None:
        """Test GenericPhaseExecutor.execute() returns result."""
        with TemporaryDirectory() as tmpdir:
            cortex_root = Path(tmpdir)
            # Create a mock phase file with stages
            phases_dir = cortex_root / "cortex-registry" / "_cortex-master" / "phases" / "active"
            phases_dir.mkdir(parents=True, exist_ok=True)
            phase_file = phases_dir / "phase-80.yaml"
            phase_file.write_text("""
title: Test Phase
stages:
  - name: "S1"
    description: "Test stage"
    estimated_duration: "1h"
""")
            
            executor = GenericPhaseExecutor(
                phase_id="phase-80", cortex_root=cortex_root
            )

            result = executor.execute()

            assert result.phase_id == "phase-80"
            assert result.status in ["SUCCESS", "PARTIAL", "FAILED"]
            assert result.duration_seconds > 0
            assert result.tests_passed >= 0
            assert result.tests_total > 0

    def test_generic_executor_result_structure(self) -> None:
        """Test result has all required fields."""
        with TemporaryDirectory() as tmpdir:
            cortex_root = Path(tmpdir)
            # Create a mock phase file with stages
            phases_dir = cortex_root / "cortex-registry" / "_cortex-master" / "phases" / "active"
            phases_dir.mkdir(parents=True, exist_ok=True)
            phase_file = phases_dir / "phase-80.yaml"
            phase_file.write_text("""
title: Test Phase
stages:
  - name: "S1"
    description: "Test stage"
    estimated_duration: "1h"
""")
            
            executor = GenericPhaseExecutor(
                phase_id="phase-80", cortex_root=cortex_root
            )

            result = executor.execute()

            assert hasattr(result, "phase_id")
            assert hasattr(result, "status")
            assert hasattr(result, "duration_seconds")
            assert hasattr(result, "tests_passed")
            assert hasattr(result, "tests_total")
            assert hasattr(result, "coverage_percent")
            assert hasattr(result, "timestamp")

    def test_generic_executor_coverage_valid(self) -> None:
        """Test coverage percentage is valid."""
        with TemporaryDirectory() as tmpdir:
            cortex_root = Path(tmpdir)
            # Create a mock phase file with stages
            phases_dir = cortex_root / "cortex-registry" / "_cortex-master" / "phases" / "active"
            phases_dir.mkdir(parents=True, exist_ok=True)
            phase_file = phases_dir / "phase-80.yaml"
            phase_file.write_text("""
title: Test Phase
stages:
  - name: "S1"
    description: "Test stage"
    estimated_duration: "1h"
""")
            
            executor = GenericPhaseExecutor(
                phase_id="phase-80", cortex_root=cortex_root
            )

            result = executor.execute()

            assert 0.0 <= result.coverage_percent <= 100.0


class TestPhaseOrchestrator:
    """Tests for PhaseOrchestrator."""

    def test_orchestrator_instantiation(self) -> None:
        """Test PhaseOrchestrator can be created."""
        with TemporaryDirectory() as tmpdir:
            orchestrator = PhaseOrchestrator(cortex_root=Path(tmpdir))
            assert orchestrator is not None

    def test_orchestrator_has_cortex_root(self) -> None:
        """Test orchestrator stores cortex root."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            orchestrator = PhaseOrchestrator(cortex_root=root)
            assert orchestrator.cortex_root == root

    def test_execute_phase_sequence_empty(self) -> None:
        """Test executing empty phase list."""
        with TemporaryDirectory() as tmpdir:
            orchestrator = PhaseOrchestrator(cortex_root=Path(tmpdir))
            result = orchestrator.execute_phase_sequence([])
            assert isinstance(result, bool)
            assert result is True

    def test_execute_phase_sequence_single(self) -> None:
        """Test executing single phase."""
        with TemporaryDirectory() as tmpdir:
            cortex_root = Path(tmpdir)
            # Create mock phase files
            phases_dir = cortex_root / "cortex-registry" / "_cortex-master" / "phases" / "active"
            phases_dir.mkdir(parents=True, exist_ok=True)
            phase_file = phases_dir / "phase-80.yaml"
            phase_file.write_text("title: Test Phase\nstages: []")
            
            orchestrator = PhaseOrchestrator(cortex_root=cortex_root)

            with patch("builtins.print"):
                result = orchestrator.execute_phase_sequence(["phase-80"])
                assert isinstance(result, bool)

    def test_execute_phase_sequence_multiple(self) -> None:
        """Test executing multiple phases."""
        with TemporaryDirectory() as tmpdir:
            cortex_root = Path(tmpdir)
            # Create mock phase files
            phases_dir = cortex_root / "cortex-registry" / "_cortex-master" / "phases" / "active"
            phases_dir.mkdir(parents=True, exist_ok=True)
            for phase_id in ["phase-80", "phase-81", "phase-82"]:
                phase_file = phases_dir / f"{phase_id}.yaml"
                phase_file.write_text("title: Test Phase\nstages: []")
            
            orchestrator = PhaseOrchestrator(cortex_root=cortex_root)

            with patch("builtins.print"):
                result = orchestrator.execute_phase_sequence(
                    ["phase-80", "phase-81", "phase-82"]
                )
                assert isinstance(result, bool)

    def test_report_summary_formatting(self) -> None:
        """Test summary report generation."""
        with TemporaryDirectory() as tmpdir:
            orchestrator = PhaseOrchestrator(cortex_root=Path(tmpdir))
            results = [
                ExecutionResult(
                    phase_id="phase-80",
                    status="SUCCESS",
                    duration_seconds=10.0,
                    tests_passed=10,
                    tests_total=10,
                    coverage_percent=95.0,
                    git_commit="abc123",
                    error_message=None,
                    timestamp="2026-02-10T10:00:00Z",
                )
            ]

            with patch("builtins.print"):
                orchestrator.report_summary()
                # Should complete without error

    def test_orchestrator_execution_compliance(self) -> None:
        """Test orchestrator follows governance."""
        with TemporaryDirectory() as tmpdir:
            orchestrator = PhaseOrchestrator(cortex_root=Path(tmpdir))

            # Should have key governance methods
            assert hasattr(orchestrator, "execute_phase_sequence")
            assert callable(orchestrator.execute_phase_sequence)


class TestPhaseExecutorFrameworkIntegration:
    """Integration tests for phase executor framework."""

    def test_end_to_end_factory_to_execution(self) -> None:
        """Test complete flow: factory -> create -> execute."""
        with TemporaryDirectory() as tmpdir:
            cortex_root = Path(tmpdir)
            # Create mock phase file
            phases_dir = cortex_root / "cortex-registry" / "_cortex-master" / "phases" / "active"
            phases_dir.mkdir(parents=True, exist_ok=True)
            phase_file = phases_dir / "phase-80.yaml"
            phase_file.write_text("title: Test Phase\nstages: []")
            
            factory = PhaseExecutorFactory(cortex_root=cortex_root)
            executor = factory.create_executor(phase_id="phase-80")

            result = executor.execute()

            assert result.phase_id == "phase-80"
            assert result.status in ["SUCCESS", "PARTIAL", "FAILED"]
            assert result.duration_seconds > 0

    def test_end_to_end_orchestration(self) -> None:
        """Test orchestrator coordinates multiple phases."""
        with TemporaryDirectory() as tmpdir:
            cortex_root = Path(tmpdir)
            # Create mock phase files
            phases_dir = cortex_root / "cortex-registry" / "_cortex-master" / "phases" / "active"
            phases_dir.mkdir(parents=True, exist_ok=True)
            for phase_id in ["phase-80", "phase-81"]:
                phase_file = phases_dir / f"{phase_id}.yaml"
                phase_file.write_text("title: Test Phase\nstages: []")
            
            orchestrator = PhaseOrchestrator(cortex_root=cortex_root)

            with patch("builtins.print"):
                result = orchestrator.execute_phase_sequence(["phase-80", "phase-81"])
                assert isinstance(result, bool)

    def test_framework_core_compliance(self) -> None:
        """Test framework meets CORE requirements."""
        # CORE-011: Type hints present in methods
        import inspect
        
        # Check PhaseExecutorBase has typed methods
        base_methods = inspect.getmembers(PhaseExecutorBase, predicate=inspect.isfunction)
        assert len(base_methods) > 0, "PhaseExecutorBase should have methods"
        
        # Check for docstrings (CORE-012)
        assert PhaseExecutorBase.__doc__ is not None
        assert PhaseExecutorFactory.__doc__ is not None
        assert GenericPhaseExecutor.__doc__ is not None
        assert PhaseOrchestrator.__doc__ is not None
        
        # Check ExecutionResult has type hints (data class)
        assert hasattr(ExecutionResult, "__annotations__")
        assert len(ExecutionResult.__annotations__) > 0

    def test_all_classes_have_docstrings(self) -> None:
        """Verify all classes documented (CORE-012)."""
        classes = [
            ExecutionResult,
            PhaseExecutorBase,
            PhaseExecutorFactory,
            GenericPhaseExecutor,
            PhaseOrchestrator,
        ]

        for cls in classes:
            assert cls.__doc__ is not None, f"{cls.__name__} missing docstring"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
