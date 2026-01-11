"""
Tests for AC-EVIDENCE-002: Evidence Bundle Validation Gates

Validates all 3 gates: coverage, audit, governance.
"""

import pytest
from pathlib import Path
import tempfile

from src.infrastructure.evidence_bundle_structure import EvidenceBundleStructure, TestMetrics, TestResult
from src.infrastructure.evidence_bundle_validation_gates import EvidenceBundleValidationGates


@pytest.fixture
def temp_bundle_base():
    """Create temporary bundle directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def bundle_system(temp_bundle_base, monkeypatch):
    """Create bundle system with temp directory."""
    def mock_project_root():
        return str(temp_bundle_base)
    
    import src.infrastructure.evidence_bundle_structure as mod
    monkeypatch.setattr(mod, "project_root", mock_project_root)
    
    system = EvidenceBundleStructure()
    system.bundle_base_dir = temp_bundle_base / "evidence_bundles"
    system.bundle_base_dir.mkdir(parents=True, exist_ok=True)
    return system


@pytest.fixture
def gates_system(bundle_system):
    """Create validation gates system."""
    gates = EvidenceBundleValidationGates()
    gates.bundle_system = bundle_system
    return gates


class TestCoverageGate:
    """Tests for coverage gate validation."""
    
    def test_coverage_gate_pass(self, gates_system):
        """Test coverage gate passes with ≥80%."""
        # Create complete bundle with 85% coverage
        bundle_dir = gates_system.bundle_system.create_bundle_directory("AC-TEST-001")
        
        metrics = TestMetrics(
            total_tests=10, passed=10, failed=0, skipped=0,
            duration=1.0, coverage_percentage=85.0
        )
        
        gates_system.bundle_system.create_manifest(
            ac_id="AC-TEST-001",
            status="implemented",
            test_metrics=metrics,
            bundle_dir=bundle_dir
        )
        
        gates_system.bundle_system.create_test_results_file(
            ac_id="AC-TEST-001",
            test_results=[TestResult("test_1", "passed", 0.1)],
            metrics=metrics,
            bundle_dir=bundle_dir
        )
        
        is_valid, result = gates_system.validate_coverage_gate("AC-TEST-001")
        
        assert is_valid is True
        assert result["status"] == "PASS"
        assert result["actual"] == 85.0
    
    def test_coverage_gate_fail(self, gates_system):
        """Test coverage gate fails with <80%."""
        bundle_dir = gates_system.bundle_system.create_bundle_directory("AC-TEST-002")
        
        metrics = TestMetrics(
            total_tests=10, passed=7, failed=3, skipped=0,
            duration=1.0, coverage_percentage=70.0
        )
        
        gates_system.bundle_system.create_manifest(
            ac_id="AC-TEST-002",
            status="implemented",
            test_metrics=metrics,
            bundle_dir=bundle_dir
        )
        
        gates_system.bundle_system.create_test_results_file(
            ac_id="AC-TEST-002",
            test_results=[TestResult("test_1", "failed", 0.1, "Error")],
            metrics=metrics,
            bundle_dir=bundle_dir
        )
        
        is_valid, result = gates_system.validate_coverage_gate("AC-TEST-002")
        
        assert is_valid is False
        assert result["status"] == "FAIL"


class TestAuditGate:
    """Tests for audit gate validation."""
    
    def test_audit_gate_pass(self, gates_system):
        """Test audit gate passes with sufficient events."""
        bundle_dir = gates_system.bundle_system.create_bundle_directory("AC-AUDIT-001")
        
        metrics = TestMetrics(
            total_tests=5, passed=5, failed=0, skipped=0,
            duration=1.0, coverage_percentage=90.0
        )
        
        gates_system.bundle_system.create_manifest(
            ac_id="AC-AUDIT-001",
            status="implemented",
            test_metrics=metrics,
            bundle_dir=bundle_dir
        )
        
        gates_system.bundle_system.create_test_results_file(
            ac_id="AC-AUDIT-001",
            test_results=[TestResult("test_1", "passed", 0.1)],
            metrics=metrics,
            bundle_dir=bundle_dir
        )
        
        gates_system.bundle_system.append_audit_trace(
            ac_id="AC-AUDIT-001",
            audit_events=[
                {"level": "INFO", "message": "Implemented"},
                {"level": "INFO", "message": "Tested"},
            ],
            bundle_dir=bundle_dir
        )
        
        is_valid, result = gates_system.validate_audit_gate("AC-AUDIT-001")
        
        assert is_valid is True
        assert result["status"] == "PASS"


class TestGovernanceGate:
    """Tests for governance gate validation."""
    
    def test_governance_gate_pass(self, gates_system):
        """Test governance gate passes with valid format."""
        bundle_dir = gates_system.bundle_system.create_bundle_directory("AC-TEST-001")
        
        metrics = TestMetrics(
            total_tests=5, passed=5, failed=0, skipped=0,
            duration=1.0, coverage_percentage=90.0
        )
        
        gates_system.bundle_system.create_manifest(
            ac_id="AC-TEST-001",
            status="implemented",
            test_metrics=metrics,
            bundle_dir=bundle_dir
        )
        
        gates_system.bundle_system.create_test_results_file(
            ac_id="AC-TEST-001",
            test_results=[TestResult("test_1", "passed", 0.1)],
            metrics=metrics,
            bundle_dir=bundle_dir
        )
        
        is_valid, result = gates_system.validate_governance_gate("AC-TEST-001")
        
        assert is_valid is True
        assert result["status"] == "PASS"


class TestAllGates:
    """Tests for running all gates together."""
    
    def test_all_gates_pass(self, gates_system):
        """Test all gates pass together."""
        bundle_dir = gates_system.bundle_system.create_bundle_directory("AC-TEST-001")
        
        metrics = TestMetrics(
            total_tests=10, passed=10, failed=0, skipped=0,
            duration=1.0, coverage_percentage=85.0
        )
        
        gates_system.bundle_system.create_manifest(
            ac_id="AC-TEST-001",
            status="implemented",
            test_metrics=metrics,
            bundle_dir=bundle_dir
        )
        
        gates_system.bundle_system.create_test_results_file(
            ac_id="AC-TEST-001",
            test_results=[TestResult("test_1", "passed", 0.1)],
            metrics=metrics,
            bundle_dir=bundle_dir
        )
        
        gates_system.bundle_system.append_audit_trace(
            ac_id="AC-TEST-001",
            audit_events=[
                {"level": "INFO", "message": "Implemented"},
                {"level": "INFO", "message": "Tested"},
            ],
            bundle_dir=bundle_dir
        )
        
        all_pass, results = gates_system.run_all_gates("AC-TEST-001")
        
        assert all_pass is True
        assert results["summary"]["all_gates_pass"] is True
        assert results["summary"]["gates_passed"] == 3
