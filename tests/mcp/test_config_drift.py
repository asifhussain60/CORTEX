"""
TDD Test Suite for ENH-063 P1-009: Configuration Drift Detection
AC-ENH063-P1-009-TEST-001

Tests for cortex/mcp/config_drift.py

RED → GREEN → REFACTOR cycle
"""

import tempfile
from pathlib import Path

import pytest
import yaml

from cortex.mcp.config_drift import (
    ConfigSyncEngine,
    ConfigurationLoader,
    DriftDetector,
    DriftReport,
    DriftSeverity,
    DriftType,
    get_config_loader,
    get_drift_detector,
    get_sync_engine,
    reset_global_instances,
)


# ============================================================================
# TEST FIXTURES
# ============================================================================


@pytest.fixture(autouse=True)
def reset_globals():
    """Reset global instances before each test"""
    reset_global_instances()
    yield
    reset_global_instances()


@pytest.fixture
def temp_workspace(tmp_path):
    """Create temporary workspace with wiring files"""
    workspace = tmp_path / "cortex_workspace"
    workspace.mkdir()

    # Create wiring directory structure
    wiring_dir = workspace / "cortex" / "wiring" / "specifications"
    wiring_dir.mkdir(parents=True)

    contract_dir = workspace / "cortex"
    contract_dir.mkdir(exist_ok=True)

    # Sample wiring configuration
    wiring_config = {
        "version": "1.0",
        "orchestrators": {
            "MasterOrchestrator": {
                "module": "cortex.orchestrators.core.master_orchestrator",
                "class": "MasterOrchestrator",
                "capabilities": ["intent_routing", "workflow_coordination"],
                "depends_on": []
            },
            "TDDOrchestrator": {
                "module": "cortex.orchestrators.core.tdd_orchestrator",
                "class": "TDDOrchestrator",
                "capabilities": ["test_generation", "implementation"],
                "depends_on": ["MasterOrchestrator"]
            }
        }
    }

    # Write source wiring.yaml
    wiring_path = wiring_dir / "wiring.yaml"
    with open(wiring_path, "w") as f:
        yaml.dump(wiring_config, f)

    # Write contract (initially same as source)
    contract_path = contract_dir / "__wiring_contract__.yaml"
    with open(contract_path, "w") as f:
        yaml.dump(wiring_config, f)

    return workspace


# ============================================================================
# TEST 1-3: Configuration Loader
# ============================================================================


def test_loader_load_source_config(temp_workspace):
    """Test loading source wiring configuration"""
    loader = ConfigurationLoader(temp_workspace)
    config = loader.load_source_config()

    assert "orchestrators" in config
    assert "MasterOrchestrator" in config["orchestrators"]
    assert "TDDOrchestrator" in config["orchestrators"]


def test_loader_load_contract_config(temp_workspace):
    """Test loading contract configuration"""
    loader = ConfigurationLoader(temp_workspace)
    config = loader.load_contract_config()

    assert "orchestrators" in config
    assert "MasterOrchestrator" in config["orchestrators"]


def test_loader_compute_hash(temp_workspace):
    """Test computing configuration hash"""
    loader = ConfigurationLoader(temp_workspace)
    config = loader.load_source_config()

    hash1 = loader.compute_hash(config)
    hash2 = loader.compute_hash(config)

    # Same config should produce same hash
    assert hash1 == hash2
    assert len(hash1) == 64  # SHA256 hex digest


# ============================================================================
# TEST 4-6: Drift Detection - No Drift
# ============================================================================


def test_drift_detector_no_drift(temp_workspace):
    """Test drift detection when configurations match"""
    loader = ConfigurationLoader(temp_workspace)
    detector = DriftDetector(loader)

    report = detector.detect_drift()

    assert not report.has_drift()
    assert len(report.issues) == 0
    assert report.source_hash == report.contract_hash


def test_drift_report_summary_no_drift(temp_workspace):
    """Test drift report summary with no drift"""
    loader = ConfigurationLoader(temp_workspace)
    detector = DriftDetector(loader)

    report = detector.detect_drift()

    assert report.summary() == "No drift detected"


def test_drift_report_critical_issues_empty(temp_workspace):
    """Test critical issues when no drift"""
    loader = ConfigurationLoader(temp_workspace)
    detector = DriftDetector(loader)

    report = detector.detect_drift()

    assert len(report.critical_issues()) == 0
    assert len(report.high_issues()) == 0


# ============================================================================
# TEST 7-10: Drift Detection - Missing Orchestrator
# ============================================================================


def test_drift_detector_missing_orchestrator(temp_workspace):
    """Test detecting missing orchestrator in contract"""
    # Load source config
    wiring_path = temp_workspace / "cortex" / "wiring" / "specifications" / "wiring.yaml"
    with open(wiring_path, "r") as f:
        wiring_config = yaml.safe_load(f)

    # Add orchestrator to source
    wiring_config["orchestrators"]["NewOrchestrator"] = {
        "module": "cortex.orchestrators.new",
        "class": "NewOrchestrator",
        "capabilities": ["new_capability"],
        "depends_on": []
    }

    # Update source
    with open(wiring_path, "w") as f:
        yaml.dump(wiring_config, f)

    # Detect drift
    loader = ConfigurationLoader(temp_workspace)
    detector = DriftDetector(loader)
    report = detector.detect_drift()

    assert report.has_drift()
    assert len(report.issues) > 0

    # Find missing orchestrator issue
    missing_issues = [i for i in report.issues if i.drift_type == DriftType.MISSING_ORCHESTRATOR]
    assert len(missing_issues) == 1
    assert "NewOrchestrator" in missing_issues[0].description


def test_drift_detector_extra_orchestrator(temp_workspace):
    """Test detecting extra orchestrator in contract"""
    # Load contract
    contract_path = temp_workspace / "cortex" / "__wiring_contract__.yaml"
    with open(contract_path, "r") as f:
        contract_config = yaml.safe_load(f)

    # Add orchestrator to contract only
    contract_config["orchestrators"]["ExtraOrchestrator"] = {
        "module": "cortex.orchestrators.extra",
        "class": "ExtraOrchestrator",
        "capabilities": [],
        "depends_on": []
    }

    with open(contract_path, "w") as f:
        yaml.dump(contract_config, f)

    # Detect drift
    loader = ConfigurationLoader(temp_workspace)
    detector = DriftDetector(loader)
    report = detector.detect_drift()

    assert report.has_drift()

    extra_issues = [i for i in report.issues if i.drift_type == DriftType.EXTRA_ORCHESTRATOR]
    assert len(extra_issues) == 1
    assert "ExtraOrchestrator" in extra_issues[0].description


def test_drift_severity_levels(temp_workspace):
    """Test drift severity classification"""
    # Create drift by adding orchestrator to source
    wiring_path = temp_workspace / "cortex" / "wiring" / "specifications" / "wiring.yaml"
    with open(wiring_path, "r") as f:
        wiring_config = yaml.safe_load(f)

    wiring_config["orchestrators"]["CriticalOrch"] = {
        "module": "cortex.orchestrators.critical",
        "class": "CriticalOrch",
        "capabilities": [],
        "depends_on": []
    }

    with open(wiring_path, "w") as f:
        yaml.dump(wiring_config, f)

    loader = ConfigurationLoader(temp_workspace)
    detector = DriftDetector(loader)
    report = detector.detect_drift()

    # Missing orchestrator should be CRITICAL
    critical_issues = report.critical_issues()
    assert len(critical_issues) > 0
    assert critical_issues[0].severity == DriftSeverity.CRITICAL


def test_drift_report_summary_with_drift(temp_workspace):
    """Test drift report summary with drift detected"""
    # Introduce drift
    wiring_path = temp_workspace / "cortex" / "wiring" / "specifications" / "wiring.yaml"
    with open(wiring_path, "r") as f:
        wiring_config = yaml.safe_load(f)

    wiring_config["orchestrators"]["NewOrch"] = {
        "module": "cortex.orchestrators.new",
        "class": "NewOrch",
        "capabilities": [],
        "depends_on": []
    }

    with open(wiring_path, "w") as f:
        yaml.dump(wiring_config, f)

    loader = ConfigurationLoader(temp_workspace)
    detector = DriftDetector(loader)
    report = detector.detect_drift()

    summary = report.summary()
    assert "drift detected" in summary.lower()


# ============================================================================
# TEST 11-14: Drift Detection - Capability Mismatch
# ============================================================================


def test_drift_detector_capability_mismatch(temp_workspace):
    """Test detecting capability mismatches"""
    # Modify capabilities in contract
    contract_path = temp_workspace / "cortex" / "__wiring_contract__.yaml"
    with open(contract_path, "r") as f:
        contract_config = yaml.safe_load(f)

    contract_config["orchestrators"]["MasterOrchestrator"]["capabilities"] = ["different_capability"]

    with open(contract_path, "w") as f:
        yaml.dump(contract_config, f)

    loader = ConfigurationLoader(temp_workspace)
    detector = DriftDetector(loader)
    report = detector.detect_drift()

    assert report.has_drift()

    cap_issues = [i for i in report.issues if i.drift_type == DriftType.MISMATCHED_CAPABILITY]
    assert len(cap_issues) > 0
    assert "MasterOrchestrator" in cap_issues[0].path


def test_drift_detector_dependency_missing(temp_workspace):
    """Test detecting missing dependencies"""
    # Modify dependencies in contract
    contract_path = temp_workspace / "cortex" / "__wiring_contract__.yaml"
    with open(contract_path, "r") as f:
        contract_config = yaml.safe_load(f)

    # Remove dependency from contract
    contract_config["orchestrators"]["TDDOrchestrator"]["depends_on"] = []

    with open(contract_path, "w") as f:
        yaml.dump(contract_config, f)

    loader = ConfigurationLoader(temp_workspace)
    detector = DriftDetector(loader)
    report = detector.detect_drift()

    assert report.has_drift()

    dep_issues = [i for i in report.issues if i.drift_type == DriftType.MISSING_DEPENDENCY]
    assert len(dep_issues) > 0
    assert "depends_on" in dep_issues[0].path


def test_drift_issue_string_representation():
    """Test drift issue string formatting"""
    from cortex.mcp.config_drift import DriftIssue

    issue = DriftIssue(
        drift_type=DriftType.MISSING_ORCHESTRATOR,
        severity=DriftSeverity.CRITICAL,
        path="orchestrators.TestOrch",
        description="Test orchestrator missing"
    )

    issue_str = str(issue)
    assert "CRITICAL" in issue_str
    assert "missing_orchestrator" in issue_str
    assert "Test orchestrator missing" in issue_str


def test_drift_report_hash_mismatch(temp_workspace):
    """Test hash mismatch detection"""
    # Modify contract slightly
    contract_path = temp_workspace / "cortex" / "__wiring_contract__.yaml"
    with open(contract_path, "r") as f:
        contract_config = yaml.safe_load(f)

    contract_config["version"] = "1.1"

    with open(contract_path, "w") as f:
        yaml.dump(contract_config, f)

    loader = ConfigurationLoader(temp_workspace)
    detector = DriftDetector(loader)
    report = detector.detect_drift()

    # Hashes should be different
    assert report.source_hash != report.contract_hash


# ============================================================================
# TEST 15-18: Sync Engine
# ============================================================================


def test_sync_engine_dry_run(temp_workspace):
    """Test sync engine in dry run mode"""
    # Introduce drift
    wiring_path = temp_workspace / "cortex" / "wiring" / "specifications" / "wiring.yaml"
    with open(wiring_path, "r") as f:
        wiring_config = yaml.safe_load(f)

    wiring_config["orchestrators"]["NewOrch"] = {"module": "test", "class": "Test"}

    with open(wiring_path, "w") as f:
        yaml.dump(wiring_config, f)

    # Sync dry run
    loader = ConfigurationLoader(temp_workspace)
    sync_engine = ConfigSyncEngine(loader)

    result = sync_engine.sync_contract(dry_run=True)
    assert result is True

    # Contract should NOT be modified
    detector = DriftDetector(loader)
    report = detector.detect_drift()
    assert report.has_drift()


def test_sync_engine_actual_sync(temp_workspace):
    """Test sync engine actually syncs contract"""
    # Introduce drift
    wiring_path = temp_workspace / "cortex" / "wiring" / "specifications" / "wiring.yaml"
    with open(wiring_path, "r") as f:
        wiring_config = yaml.safe_load(f)

    wiring_config["orchestrators"]["SyncedOrch"] = {"module": "test", "class": "Test"}

    with open(wiring_path, "w") as f:
        yaml.dump(wiring_config, f)

    # Perform sync
    loader = ConfigurationLoader(temp_workspace)
    sync_engine = ConfigSyncEngine(loader)

    result = sync_engine.sync_contract(dry_run=False)
    assert result is True

    # Drift should be resolved
    detector = DriftDetector(loader)
    report = detector.detect_drift()
    assert not report.has_drift()


def test_sync_engine_missing_source(tmp_path):
    """Test sync engine with missing source file"""
    workspace = tmp_path / "empty_workspace"
    workspace.mkdir()

    loader = ConfigurationLoader(workspace)
    sync_engine = ConfigSyncEngine(loader)

    result = sync_engine.sync_contract(dry_run=False)
    assert result is False


def test_sync_resolves_all_drift_types(temp_workspace):
    """Test sync resolves multiple drift types"""
    # Introduce multiple drift types
    wiring_path = temp_workspace / "cortex" / "wiring" / "specifications" / "wiring.yaml"
    with open(wiring_path, "r") as f:
        wiring_config = yaml.safe_load(f)

    # Add orchestrator
    wiring_config["orchestrators"]["AddedOrch"] = {"module": "test", "class": "Test"}

    # Modify capabilities
    wiring_config["orchestrators"]["MasterOrchestrator"]["capabilities"].append("new_cap")

    with open(wiring_path, "w") as f:
        yaml.dump(wiring_config, f)

    # Sync
    loader = ConfigurationLoader(temp_workspace)
    sync_engine = ConfigSyncEngine(loader)
    sync_engine.sync_contract(dry_run=False)

    # Verify all drift resolved
    detector = DriftDetector(loader)
    report = detector.detect_drift()
    assert not report.has_drift()


# ============================================================================
# TEST 19-22: Global Instances
# ============================================================================


def test_get_config_loader_singleton(temp_workspace):
    """Test global config loader singleton"""
    loader1 = get_config_loader(temp_workspace)
    loader2 = get_config_loader(temp_workspace)

    assert loader1 is loader2


def test_get_drift_detector_singleton(temp_workspace):
    """Test global drift detector singleton"""
    detector1 = get_drift_detector(temp_workspace)
    detector2 = get_drift_detector(temp_workspace)

    assert detector1 is detector2


def test_get_sync_engine_singleton(temp_workspace):
    """Test global sync engine singleton"""
    engine1 = get_sync_engine(temp_workspace)
    engine2 = get_sync_engine(temp_workspace)

    assert engine1 is engine2


def test_reset_global_instances_clears_singletons(temp_workspace):
    """Test resetting global instances"""
    loader1 = get_config_loader(temp_workspace)

    reset_global_instances()

    loader2 = get_config_loader(temp_workspace)

    assert loader1 is not loader2


# ============================================================================
# TEST 23-25: Edge Cases
# ============================================================================


def test_loader_missing_source_file(tmp_path):
    """Test loader with missing source file"""
    workspace = tmp_path / "missing_source"
    workspace.mkdir()

    loader = ConfigurationLoader(workspace)

    with pytest.raises(FileNotFoundError):
        loader.load_source_config()


def test_loader_missing_contract_file(tmp_path):
    """Test loader with missing contract file"""
    workspace = tmp_path / "missing_contract"
    workspace.mkdir()

    loader = ConfigurationLoader(workspace)

    with pytest.raises(FileNotFoundError):
        loader.load_contract_config()


def test_drift_detector_missing_files(tmp_path):
    """Test drift detection with missing files"""
    workspace = tmp_path / "no_files"
    workspace.mkdir()

    loader = ConfigurationLoader(workspace)
    detector = DriftDetector(loader)

    report = detector.detect_drift()

    # Should generate critical schema mismatch issue
    assert report.has_drift()
    assert len(report.critical_issues()) > 0
    assert report.critical_issues()[0].drift_type == DriftType.SCHEMA_MISMATCH
