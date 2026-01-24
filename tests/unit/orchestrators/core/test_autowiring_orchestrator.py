"""
Tests for AutowiringOrchestrator.

AC-ID: AC-AR-AUTOWIRING-001
Tests CORE-031 compliance: Declarative autowiring infrastructure.
"""

import tempfile
from pathlib import Path

import pytest
import yaml

from cortex.orchestrators.core.autowiring_orchestrator import (
    AutowiringOrchestrator,
    WiringSpec,
)


class TestWiringSpec:
    """Tests for WiringSpec data class."""

    def test_init_with_valid_data(self) -> None:
        """Test WiringSpec initialization with valid data."""
        data = {
            "module_name": "test_orchestrator",
            "version": "1.0.0",
            "dependencies": [{"name": "dep1", "version": ">=1.0.0", "required": True}],
            "provides": [{"interface": "ITest", "version": "1.0.0"}],
            "entry_points": [{"name": "init", "function": "test.init", "phase": "startup"}],
            "initialization_order": 50,
        }
        spec = WiringSpec(data, Path("/test/path.yaml"))

        assert spec.module_name == "test_orchestrator"
        assert spec.version == "1.0.0"
        assert len(spec.dependencies) == 1
        assert spec.initialization_order == 50
        assert spec.source_path == Path("/test/path.yaml")

    def test_init_with_defaults(self) -> None:
        """Test WiringSpec uses defaults for missing fields."""
        data = {"module_name": "minimal"}
        spec = WiringSpec(data, Path("/test.yaml"))

        assert spec.module_name == "minimal"
        assert spec.version == "1.0.0"
        assert spec.dependencies == []
        assert spec.initialization_order == 1000

    def test_get_dependency_names(self) -> None:
        """Test extracting dependency names."""
        data = {
            "module_name": "test",
            "dependencies": [
                {"name": "required_dep", "required": True},
                {"name": "optional_dep", "required": False},
                {"name": "default_required"},
            ],
        }
        spec = WiringSpec(data, Path("/test.yaml"))
        deps = spec.get_dependency_names()

        assert "required_dep" in deps
        assert "default_required" in deps
        assert "optional_dep" not in deps


class TestAutowiringOrchestrator:
    """Tests for AutowiringOrchestrator."""

    @pytest.fixture
    def temp_orchestrators_dir(self) -> Path:
        """Create temporary orchestrators directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def orchestrator(self, temp_orchestrators_dir: Path) -> AutowiringOrchestrator:
        """Create AutowiringOrchestrator instance."""
        return AutowiringOrchestrator(temp_orchestrators_dir)

    def test_discover_empty_directory(self, orchestrator: AutowiringOrchestrator) -> None:
        """Test discovery in empty directory returns empty dict."""
        result = orchestrator.discover_wiring_specs()
        assert result.is_ok()
        assert result.value == {}

    def test_discover_valid_spec(
        self, orchestrator: AutowiringOrchestrator, temp_orchestrators_dir: Path
    ) -> None:
        """Test discovering valid wiring spec."""
        spec_content = {
            "module_name": "test_orch",
            "version": "1.0.0",
            "dependencies": [],
        }
        spec_file = temp_orchestrators_dir / "test_wiring.yaml"
        with open(spec_file, "w") as f:
            yaml.dump(spec_content, f)

        result = orchestrator.discover_wiring_specs()
        assert result.is_ok()
        assert "test_orch" in result.value

    def test_discover_invalid_yaml(
        self, orchestrator: AutowiringOrchestrator, temp_orchestrators_dir: Path
    ) -> None:
        """Test discovering invalid YAML returns error."""
        spec_file = temp_orchestrators_dir / "invalid_wiring.yaml"
        with open(spec_file, "w") as f:
            f.write("invalid: yaml: content: [")

        result = orchestrator.discover_wiring_specs()
        assert not result.is_ok()
        assert "Invalid YAML" in result.error

    def test_validate_no_cycles(
        self, orchestrator: AutowiringOrchestrator, temp_orchestrators_dir: Path
    ) -> None:
        """Test validation passes for acyclic dependencies."""
        # Create spec A depends on B
        spec_a = {"module_name": "module_a", "dependencies": [{"name": "module_b", "internal": True}]}
        spec_b = {"module_name": "module_b", "dependencies": []}

        (temp_orchestrators_dir / "a_wiring.yaml").write_text(yaml.dump(spec_a))
        (temp_orchestrators_dir / "b_wiring.yaml").write_text(yaml.dump(spec_b))

        orchestrator.discover_wiring_specs()
        result = orchestrator.validate_dependency_graph()

        assert result.is_ok()
        # B should come before A in topological order
        sorted_modules = result.value
        assert sorted_modules.index("module_b") < sorted_modules.index("module_a")

    def test_validate_detects_cycle(
        self, orchestrator: AutowiringOrchestrator, temp_orchestrators_dir: Path
    ) -> None:
        """Test validation detects circular dependencies."""
        # Create cycle: A -> B -> A
        spec_a = {"module_name": "module_a", "dependencies": [{"name": "module_b", "internal": True}]}
        spec_b = {"module_name": "module_b", "dependencies": [{"name": "module_a", "internal": True}]}

        (temp_orchestrators_dir / "a_wiring.yaml").write_text(yaml.dump(spec_a))
        (temp_orchestrators_dir / "b_wiring.yaml").write_text(yaml.dump(spec_b))

        orchestrator.discover_wiring_specs()
        result = orchestrator.validate_dependency_graph()

        assert not result.is_ok()
        assert "Circular dependency" in result.error

    def test_resolve_dependencies_sorts_by_order(
        self, orchestrator: AutowiringOrchestrator, temp_orchestrators_dir: Path
    ) -> None:
        """Test resolve_dependencies sorts by initialization order."""
        spec_high = {"module_name": "high_priority", "initialization_order": 10}
        spec_low = {"module_name": "low_priority", "initialization_order": 100}

        (temp_orchestrators_dir / "high_wiring.yaml").write_text(yaml.dump(spec_high))
        (temp_orchestrators_dir / "low_wiring.yaml").write_text(yaml.dump(spec_low))

        result = orchestrator.resolve_dependencies()
        assert result.is_ok()

        sorted_specs = result.value
        names = [s.module_name for s in sorted_specs]
        assert names.index("high_priority") < names.index("low_priority")

    def test_validate_full_pipeline(
        self, orchestrator: AutowiringOrchestrator, temp_orchestrators_dir: Path
    ) -> None:
        """Test full validation pipeline."""
        spec = {"module_name": "valid_module", "version": "1.0.0"}
        (temp_orchestrators_dir / "valid_wiring.yaml").write_text(yaml.dump(spec))

        result = orchestrator.validate()
        assert result.is_ok()
        assert result.value is True

    def test_query_wiring_state(
        self, orchestrator: AutowiringOrchestrator, temp_orchestrators_dir: Path
    ) -> None:
        """Test querying wiring state."""
        spec = {"module_name": "test_module"}
        (temp_orchestrators_dir / "test_wiring.yaml").write_text(yaml.dump(spec))

        orchestrator.discover_wiring_specs()
        state = orchestrator.query_wiring_state()

        assert state["discovered_specs"] == 1
        assert "test_module" in state["modules"]
        assert str(temp_orchestrators_dir) in state["orchestrators_root"]

    def test_get_missing_wiring_specs(
        self, orchestrator: AutowiringOrchestrator, temp_orchestrators_dir: Path
    ) -> None:
        """Test finding orchestrators without wiring specs."""
        # Create orchestrator file without wiring spec
        orch_file = temp_orchestrators_dir / "test_orchestrator.py"
        orch_file.write_text("class TestOrchestrator: pass")

        result = orchestrator.get_missing_wiring_specs()
        assert result.is_ok()
        assert orch_file in result.value
