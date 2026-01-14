"""
Tests for AC-EVIDENCE-001: Evidence Bundle Structure

Validates 3-file bundle format, manifest creation, and bundle reading.
"""

import pytest
import json
import tempfile
from pathlib import Path
from datetime import datetime
import yaml

from src.infrastructure.evidence_bundle_structure import (
    EvidenceBundleStructure,
    BundleTestResult,
    BundleMetrics,
)


@pytest.fixture
def temp_bundle_base():
    """Create temporary bundle directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def bundle_system(temp_bundle_base, monkeypatch):
    """Create bundle system with test directory."""
    # Mock project_root to return temp dir
    def mock_project_root():
        return str(temp_bundle_base)
    
    import src.infrastructure.evidence_bundle_structure as mod
    monkeypatch.setattr(mod, "project_root", mock_project_root)
    
    system = EvidenceBundleStructure()
    system.bundle_base_dir = temp_bundle_base / "evidence_bundles"
    system.bundle_base_dir.mkdir(parents=True, exist_ok=True)
    
    return system


@pytest.fixture
def sample_metrics():
    """Create sample test metrics."""
    return BundleMetrics(
        total_tests=10,
        passed=9,
        failed=1,
        skipped=0,
        duration=5.23,
        coverage_percentage=85.5
    )


@pytest.fixture
def sample_test_results():
    """Create sample test results."""
    return [
        BundleTestResult("test_valid_input", "passed", 0.1),
        BundleTestResult("test_empty_input", "passed", 0.08),
        BundleTestResult("test_invalid_format", "failed", 0.15, "AssertionError: expected X"),
        BundleTestResult("test_edge_case", "passed", 0.12),
    ]


class TestBundleDirectoryCreation:
    """Tests for bundle directory creation."""
    
    def test_create_bundle_directory(self, bundle_system):
        """Test creating bundle directory for AC-ID."""
        bundle_dir = bundle_system.create_bundle_directory("AC-AUDIT-001")
        
        assert bundle_dir.exists()
        assert bundle_dir.is_dir()
        assert "AC-AUDIT-001" in str(bundle_dir)
    
    def test_create_bundle_directory_with_special_chars(self, bundle_system):
        """Test creating bundle directory with special characters."""
        bundle_dir = bundle_system.create_bundle_directory("AC-TEST-001 extra/path")
        
        assert bundle_dir.exists()
        # Special chars should be sanitized
        assert " " not in bundle_dir.name
        assert "/" not in bundle_dir.name


class TestManifestCreation:
    """Tests for manifest.yaml creation."""
    
    def test_create_manifest(self, bundle_system, sample_metrics):
        """Test creating manifest file."""
        ac_id = "AC-AUDIT-001"
        bundle_dir = bundle_system.create_bundle_directory(ac_id)
        
        manifest = bundle_system.create_manifest(
            ac_id=ac_id,
            status="implemented",
            test_metrics=sample_metrics,
            bundle_dir=bundle_dir
        )
        
        assert manifest["ac_id"] == ac_id
        assert manifest["status"] == "implemented"
        assert manifest["metrics"]["total_tests"] == 10
        assert manifest["metrics"]["passed"] == 9
        assert manifest["metrics"]["coverage_percentage"] == 85.5
        
        # Verify file exists
        manifest_path = bundle_dir / "manifest.yaml"
        assert manifest_path.exists()
    
    def test_manifest_has_evidence_references(self, bundle_system, sample_metrics):
        """Test that manifest references test and audit files."""
        ac_id = "AC-AUDIT-001"
        bundle_dir = bundle_system.create_bundle_directory(ac_id)
        
        manifest = bundle_system.create_manifest(
            ac_id=ac_id,
            status="implemented",
            test_metrics=sample_metrics,
            bundle_dir=bundle_dir
        )
        
        assert "evidence" in manifest
        assert manifest["evidence"]["test_results"] == "test_results.json"
        assert manifest["evidence"]["audit_trace"] == "audit_trace.jsonl"
    
    def test_manifest_success_rate_calculation(self, bundle_system):
        """Test success rate calculation in manifest."""
        metrics = BundleMetrics(
            total_tests=10,
            passed=7,
            failed=3,
            skipped=0,
            duration=2.0,
            coverage_percentage=70.0
        )
        
        bundle_dir = bundle_system.create_bundle_directory("AC-TEST-001")
        
        manifest = bundle_system.create_manifest(
            ac_id="AC-TEST-001",
            status="implemented",
            test_metrics=metrics,
            bundle_dir=bundle_dir
        )
        
        assert manifest["metrics"]["success_rate"] == 70.0  # 7/10 * 100


class BundleResultsFileCreation:
    """Tests for test_results.json creation."""
    
    def test_create_test_results_file(self, bundle_system, sample_test_results, sample_metrics):
        """Test creating test results JSON file."""
        ac_id = "AC-AUDIT-001"
        bundle_dir = bundle_system.create_bundle_directory(ac_id)
        
        results = bundle_system.create_test_results_file(
            ac_id=ac_id,
            test_results=sample_test_results,
            metrics=sample_metrics,
            bundle_dir=bundle_dir
        )
        
        assert results["ac_id"] == ac_id
        assert results["summary"]["total_tests"] == 10
        assert len(results["tests"]) == 4
        
        # Verify file exists and is valid JSON
        results_path = bundle_dir / "test_results.json"
        assert results_path.exists()
        
        with open(results_path, "r") as f:
            loaded = json.load(f)
            assert loaded["ac_id"] == ac_id
    
    def test_test_results_includes_failures(self, bundle_system, sample_test_results, sample_metrics):
        """Test that failed tests are included in results."""
        ac_id = "AC-AUDIT-001"
        bundle_dir = bundle_system.create_bundle_directory(ac_id)
        
        results = bundle_system.create_test_results_file(
            ac_id=ac_id,
            test_results=sample_test_results,
            metrics=sample_metrics,
            bundle_dir=bundle_dir
        )
        
        # Find failed test
        failed_tests = [t for t in results["tests"] if t["status"] == "failed"]
        assert len(failed_tests) == 1
        assert failed_tests[0]["error"] is not None


class TestAuditTraceAppending:
    """Tests for audit_trace.jsonl appending."""
    
    def test_append_audit_trace(self, bundle_system):
        """Test appending audit events to trace file."""
        ac_id = "AC-AUDIT-001"
        bundle_dir = bundle_system.create_bundle_directory(ac_id)
        
        audit_events = [
            {"level": "INFO", "message": "Event 1"},
            {"level": "WARNING", "message": "Event 2"},
        ]
        
        bundle_system.append_audit_trace(
            ac_id=ac_id,
            audit_events=audit_events,
            bundle_dir=bundle_dir
        )
        
        # Verify file exists
        trace_path = bundle_dir / "audit_trace.jsonl"
        assert trace_path.exists()
        
        # Verify content (newline-delimited JSON)
        with open(trace_path, "r") as f:
            lines = f.readlines()
            assert len(lines) == 2
            
            for line in lines:
                event = json.loads(line)
                assert event["ac_id"] == ac_id
                assert "timestamp" in event
    
    def test_append_audit_trace_multiple_times(self, bundle_system):
        """Test appending events multiple times."""
        ac_id = "AC-AUDIT-001"
        bundle_dir = bundle_system.create_bundle_directory(ac_id)
        
        # First append
        bundle_system.append_audit_trace(
            ac_id=ac_id,
            audit_events=[{"level": "INFO", "message": "Event 1"}],
            bundle_dir=bundle_dir
        )
        
        # Second append
        bundle_system.append_audit_trace(
            ac_id=ac_id,
            audit_events=[{"level": "INFO", "message": "Event 2"}],
            bundle_dir=bundle_dir
        )
        
        # Verify both events exist
        trace_path = bundle_dir / "audit_trace.jsonl"
        with open(trace_path, "r") as f:
            lines = f.readlines()
            assert len(lines) == 2


class TestBundleReading:
    """Tests for reading complete bundles."""
    
    def test_read_complete_bundle(self, bundle_system, sample_metrics, sample_test_results):
        """Test reading complete evidence bundle."""
        ac_id = "AC-AUDIT-001"
        bundle_dir = bundle_system.create_bundle_directory(ac_id)
        
        # Create all three files
        bundle_system.create_manifest(
            ac_id=ac_id,
            status="implemented",
            test_metrics=sample_metrics,
            bundle_dir=bundle_dir
        )
        
        bundle_system.create_test_results_file(
            ac_id=ac_id,
            test_results=sample_test_results,
            metrics=sample_metrics,
            bundle_dir=bundle_dir
        )
        
        bundle_system.append_audit_trace(
            ac_id=ac_id,
            audit_events=[
                {"level": "INFO", "message": "AC implemented"},
                {"level": "INFO", "message": "Tests passed"},
            ],
            bundle_dir=bundle_dir
        )
        
        # Read bundle
        bundle = bundle_system.read_bundle(ac_id)
        
        assert bundle is not None
        assert bundle["ac_id"] == ac_id
        assert bundle["manifest"]["status"] == "implemented"
        assert len(bundle["test_results"]["tests"]) == 4
        assert len(bundle["audit_trace"]) == 2
    
    def test_read_nonexistent_bundle(self, bundle_system):
        """Test reading non-existent bundle."""
        bundle = bundle_system.read_bundle("AC-NONEXISTENT-999")
        
        assert bundle is None


class TestBundleListing:
    """Tests for listing bundles."""
    
    def test_list_bundles_empty(self, bundle_system):
        """Test listing bundles when none exist."""
        bundles = bundle_system.list_bundles()
        
        assert bundles == []
    
    def test_list_bundles_multiple(self, bundle_system, sample_metrics):
        """Test listing multiple bundles."""
        # Create multiple bundles
        for ac_id in ["AC-AUDIT-001", "AC-AUDIT-002", "AC-GOV-001"]:
            bundle_dir = bundle_system.create_bundle_directory(ac_id)
            bundle_system.create_manifest(
                ac_id=ac_id,
                status="implemented",
                test_metrics=sample_metrics,
                bundle_dir=bundle_dir
            )
        
        bundles = bundle_system.list_bundles()
        
        assert len(bundles) == 3
        assert "AC-AUDIT-001" in bundles
        assert "AC-AUDIT-002" in bundles
        assert "AC-GOV-001" in bundles
        assert bundles == sorted(bundles)  # Verify sorted


class TestBundleStatistics:
    """Tests for bundle statistics."""
    
    def test_get_bundle_stats(self, bundle_system, sample_metrics, sample_test_results):
        """Test getting statistics for a bundle."""
        ac_id = "AC-AUDIT-001"
        bundle_dir = bundle_system.create_bundle_directory(ac_id)
        
        bundle_system.create_manifest(
            ac_id=ac_id,
            status="implemented",
            test_metrics=sample_metrics,
            bundle_dir=bundle_dir
        )
        
        bundle_system.create_test_results_file(
            ac_id=ac_id,
            test_results=sample_test_results,
            metrics=sample_metrics,
            bundle_dir=bundle_dir
        )
        
        bundle_system.append_audit_trace(
            ac_id=ac_id,
            audit_events=[
                {"level": "INFO", "message": "Event 1"},
                {"level": "INFO", "message": "Event 2"},
            ],
            bundle_dir=bundle_dir
        )
        
        stats = bundle_system.get_bundle_stats(ac_id)
        
        assert stats is not None
        assert stats["ac_id"] == ac_id
        assert stats["status"] == "implemented"
        assert stats["test_count"] == 10
        assert stats["test_passed"] == 9
        assert stats["test_failed"] == 1
        assert stats["coverage"] == 85.5
        assert stats["audit_events"] == 2
    
    def test_get_bundle_stats_nonexistent(self, bundle_system):
        """Test getting stats for non-existent bundle."""
        stats = bundle_system.get_bundle_stats("AC-NONEXISTENT-999")
        
        assert stats is None
