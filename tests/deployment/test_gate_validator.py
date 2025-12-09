"""
Tests for Enhanced Gate Validation Framework

TDD approach for Item 4: Gate validation with discovery integration.

Author: Asif Hussain
Version: 1.0.0
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
import tempfile

from src.deployment.gate_validator import (
    GateValidator,
    GateSeverity,
    GateResult,
    GateCategory
)


class TestGateValidatorInitialization:
    """Test gate validator initialization."""
    
    def test_validator_initializes_with_cortex_root(self, tmp_path):
        """Test validator initializes with CORTEX root."""
        validator = GateValidator(tmp_path)
        
        assert validator.cortex_root == tmp_path
        assert validator.gate_cache == {}
    
    def test_validator_loads_discovery_report(self, tmp_path):
        """Test validator can load discovery report."""
        # Create mock discovery report
        discovery_path = tmp_path / "cortex-brain" / "documents" / "reports"
        discovery_path.mkdir(parents=True)
        
        report_file = discovery_path / "deployment-discovery-test.md"
        report_file.write_text("# Discovery Report")
        
        validator = GateValidator(tmp_path)
        report = validator.load_discovery_report(report_file)
        
        assert report is not None


class TestGateSeverityLevels:
    """Test gate severity categorization."""
    
    def test_critical_gates_block_deployment(self):
        """Test CRITICAL gates block deployment when failed."""
        result = GateResult(
            gate_id="test_gate",
            name="Test Gate",
            severity=GateSeverity.CRITICAL,
            passed=False,
            message="Critical failure"
        )
        
        assert result.severity == GateSeverity.CRITICAL
        assert not result.passed
        assert result.blocks_deployment()
    
    def test_warning_gates_dont_block_deployment(self):
        """Test WARNING gates don't block deployment."""
        result = GateResult(
            gate_id="test_gate",
            name="Test Gate",
            severity=GateSeverity.WARNING,
            passed=False,
            message="Warning only"
        )
        
        assert result.severity == GateSeverity.WARNING
        assert not result.blocks_deployment()
    
    def test_info_gates_are_metrics_only(self):
        """Test INFO gates are for metrics only."""
        result = GateResult(
            gate_id="test_gate",
            name="Test Gate",
            severity=GateSeverity.INFO,
            passed=True,
            message="Informational"
        )
        
        assert result.severity == GateSeverity.INFO
        assert not result.blocks_deployment()


class TestGateCategories:
    """Test gate categorization."""
    
    def test_gates_have_categories(self):
        """Test gates can be categorized."""
        result = GateResult(
            gate_id="test_gate",
            name="Test Gate",
            severity=GateSeverity.CRITICAL,
            passed=True,
            message="Test",
            category=GateCategory.QUALITY
        )
        
        assert result.category == GateCategory.QUALITY
    
    def test_all_categories_defined(self):
        """Test all gate categories are defined."""
        categories = [
            GateCategory.QUALITY,
            GateCategory.SECURITY,
            GateCategory.INTEGRATION,
            GateCategory.DOCUMENTATION,
            GateCategory.TESTING
        ]
        
        for category in categories:
            assert isinstance(category.value, str)


class TestGateDependencies:
    """Test gate dependency management."""
    
    def test_gates_can_have_dependencies(self, tmp_path):
        """Test gates can declare dependencies."""
        validator = GateValidator(tmp_path)
        
        # Define gate with dependencies
        gate_config = {
            "gate_id": "test_gate",
            "name": "Test Gate",
            "depends_on": ["discovery_gate", "alignment_gate"]
        }
        
        dependencies = validator.get_gate_dependencies(gate_config)
        
        assert len(dependencies) == 2
        assert "discovery_gate" in dependencies
        assert "alignment_gate" in dependencies
    
    def test_dependent_gates_run_after_dependencies(self, tmp_path):
        """Test dependent gates wait for dependencies."""
        validator = GateValidator(tmp_path)
        
        # Create execution order
        gates = [
            {"gate_id": "gate_a", "depends_on": []},
            {"gate_id": "gate_b", "depends_on": ["gate_a"]},
            {"gate_id": "gate_c", "depends_on": ["gate_a", "gate_b"]}
        ]
        
        execution_order = validator.resolve_execution_order(gates)
        
        # Verify dependencies execute first
        assert execution_order.index("gate_a") < execution_order.index("gate_b")
        assert execution_order.index("gate_b") < execution_order.index("gate_c")


class TestParallelExecution:
    """Test parallel gate execution."""
    
    def test_independent_gates_can_run_parallel(self, tmp_path):
        """Test independent gates identified for parallel execution."""
        validator = GateValidator(tmp_path)
        
        gates = [
            {"gate_id": "gate_a", "depends_on": []},
            {"gate_id": "gate_b", "depends_on": []},
            {"gate_id": "gate_c", "depends_on": ["gate_a"]}
        ]
        
        parallel_groups = validator.get_parallel_groups(gates)
        
        # gate_a and gate_b can run in parallel
        assert len(parallel_groups[0]) == 2
        assert "gate_a" in parallel_groups[0]
        assert "gate_b" in parallel_groups[0]
        
        # gate_c must run after gate_a
        assert len(parallel_groups[1]) == 1
        assert "gate_c" in parallel_groups[1]


class TestGateCaching:
    """Test gate result caching."""
    
    def test_gate_results_are_cached(self, tmp_path):
        """Test gate results stored in cache."""
        validator = GateValidator(tmp_path)
        
        result = GateResult(
            gate_id="test_gate",
            name="Test Gate",
            severity=GateSeverity.CRITICAL,
            passed=True,
            message="Cached"
        )
        
        validator.cache_result("test_gate", result)
        
        assert "test_gate" in validator.gate_cache
        assert validator.gate_cache["test_gate"].passed
    
    def test_cached_gates_not_rerun(self, tmp_path):
        """Test cached gates skipped on re-execution."""
        validator = GateValidator(tmp_path)
        
        # Cache a result
        cached_result = GateResult(
            gate_id="cached_gate",
            name="Cached Gate",
            severity=GateSeverity.CRITICAL,
            passed=True,
            message="From cache"
        )
        validator.cache_result("cached_gate", cached_result)
        
        # Try to get result
        result = validator.get_cached_result("cached_gate")
        
        assert result is not None
        assert result.message == "From cache"


class TestDiscoveryIntegration:
    """Test discovery report integration."""
    
    def test_validator_uses_discovery_targets(self, tmp_path):
        """Test validator uses discovery report for validation targets."""
        validator = GateValidator(tmp_path)
        
        # Mock discovery report
        discovery_data = {
            "discovered_components": [
                {"component": "new_orch", "fully_wired": False},
                {"component": "old_orch", "fully_wired": True}
            ]
        }
        
        targets = validator.extract_validation_targets(discovery_data)
        
        assert len(targets) == 2
        assert "new_orch" in [t["component"] for t in targets]
    
    def test_validator_checks_new_component_wiring(self, tmp_path):
        """Test validator verifies new components are wired."""
        validator = GateValidator(tmp_path)
        
        component = {
            "component": "test_orch",
            "type": "orchestrator",
            "fully_wired": False,
            "wired_in_operations_yaml": False,
            "has_tests": True
        }
        
        result = validator.validate_component_wiring(component)
        
        assert not result.passed
        assert "operations.yaml" in result.message.lower()


class TestRemediationSteps:
    """Test remediation step generation."""
    
    def test_failed_gates_generate_remediation(self, tmp_path):
        """Test failed gates include remediation steps."""
        result = GateResult(
            gate_id="test_gate",
            name="Test Gate",
            severity=GateSeverity.CRITICAL,
            passed=False,
            message="Gate failed",
            remediation_steps=[
                "Step 1: Fix issue",
                "Step 2: Re-run gate"
            ]
        )
        
        assert len(result.remediation_steps) == 2
        assert "Fix issue" in result.remediation_steps[0]
    
    def test_remediation_includes_commands(self, tmp_path):
        """Test remediation includes executable commands."""
        validator = GateValidator(tmp_path)
        
        failure = {
            "gate_id": "wiring_gate",
            "issue": "Missing operations.yaml entry",
            "component": "test_orch"
        }
        
        remediation = validator.generate_remediation(failure)
        
        assert "command" in remediation
        assert "python3 -m src.operations.align" in remediation["command"]


class TestGateReporting:
    """Test gate execution reporting."""
    
    def test_generates_gate_execution_report(self, tmp_path):
        """Test gate execution report generation."""
        validator = GateValidator(tmp_path)
        
        results = [
            GateResult("gate1", "Gate 1", GateSeverity.CRITICAL, True, "Passed"),
            GateResult("gate2", "Gate 2", GateSeverity.WARNING, False, "Failed"),
        ]
        
        report_path = validator.generate_report(results, tmp_path / "test_report.md")
        
        assert report_path.exists()
        content = report_path.read_text()
        assert "Gate 1" in content
        assert "Gate 2" in content
    
    def test_report_includes_statistics(self, tmp_path):
        """Test report includes gate statistics."""
        validator = GateValidator(tmp_path)
        
        results = [
            GateResult("gate1", "Gate 1", GateSeverity.CRITICAL, True, "Passed"),
            GateResult("gate2", "Gate 2", GateSeverity.CRITICAL, False, "Failed"),
            GateResult("gate3", "Gate 3", GateSeverity.WARNING, False, "Warning"),
        ]
        
        stats = validator.calculate_statistics(results)
        
        assert stats["total"] == 3
        assert stats["passed"] == 1
        assert stats["failed_critical"] == 1
        assert stats["failed_warning"] == 1


class TestEndToEndGateValidation:
    """Test end-to-end gate validation workflow."""
    
    def test_validates_all_gates_with_discovery(self, tmp_path):
        """Test full gate validation with discovery integration."""
        validator = GateValidator(tmp_path)
        
        # Mock discovery data
        discovery_data = {
            "discovered_components": [
                {
                    "component": "test_orch",
                    "type": "orchestrator",
                    "fully_wired": True,
                    "wired_in_operations_yaml": True,
                    "has_tests": True,
                    "has_manifest": True
                }
            ]
        }
        
        results = validator.validate_all_gates(discovery_data=discovery_data)
        
        assert "gate_results" in results
        assert "statistics" in results
        assert "deployment_allowed" in results
