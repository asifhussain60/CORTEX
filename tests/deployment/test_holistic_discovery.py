"""
Tests for Holistic Functionality Discovery

Author: Asif Hussain
Version: 1.0.0
"""

import pytest
from pathlib import Path
import tempfile
import yaml
import shutil

from src.deployment.holistic_discovery import HolisticDiscovery, run_discovery


class TestHolisticDiscoveryInitialization:
    """Test holistic discovery initialization."""
    
    def test_discovery_initializes_with_cortex_root(self, tmp_path):
        """Test discovery initializes with CORTEX root."""
        discovery = HolisticDiscovery(tmp_path)
        
        assert discovery.cortex_root == tmp_path
        assert discovery.src_path == tmp_path / "src"
        assert discovery.tests_path == tmp_path / "tests"
        assert discovery.docs_path == tmp_path / "cortex-brain" / "documents"
    
    def test_discovery_initializes_component_lists(self, tmp_path):
        """Test discovery initializes empty component lists."""
        discovery = HolisticDiscovery(tmp_path)
        
        assert discovery.discovered_components == []
        assert discovery.wiring_gaps == []


class TestComponentDiscovery:
    """Test component discovery functionality."""
    
    @pytest.fixture
    def mock_cortex_structure(self, tmp_path):
        """Create mock CORTEX structure."""
        # Create directories
        (tmp_path / "src" / "orchestrators").mkdir(parents=True)
        (tmp_path / "src" / "operations" / "modules").mkdir(parents=True)
        (tmp_path / "src" / "cortex_agents").mkdir(parents=True)
        (tmp_path / "src" / "dashboard").mkdir(parents=True)
        (tmp_path / "tests" / "orchestrators").mkdir(parents=True)
        (tmp_path / "cortex-brain" / "documents").mkdir(parents=True)
        (tmp_path / "cortex-brain" / "orchestrator-manifests").mkdir(parents=True)
        
        # Create mock files
        (tmp_path / "src" / "orchestrators" / "test_orchestrator.py").write_text("# Orchestrator")
        (tmp_path / "src" / "operations" / "modules" / "test_module.py").write_text("# Module")
        (tmp_path / "src" / "cortex_agents" / "test_agent.py").write_text("# Agent")
        (tmp_path / "src" / "dashboard" / "test_orchestrator.py").write_text("# Dashboard")
        
        # Create operations.yaml
        operations_yaml = {
            "operations": {
                "test_operation": {
                    "name": "Test Operation",
                    "modules": ["test_orchestrator"]
                }
            }
        }
        with open(tmp_path / "cortex-operations.yaml", "w") as f:
            yaml.dump(operations_yaml, f)
        
        return tmp_path
    
    def test_discovers_orchestrators(self, mock_cortex_structure):
        """Test orchestrator discovery."""
        discovery = HolisticDiscovery(mock_cortex_structure)
        orchestrators = discovery._discover_orchestrators()
        
        assert len(orchestrators) == 1
        assert orchestrators[0].name == "test_orchestrator.py"
    
    def test_discovers_operations(self, mock_cortex_structure):
        """Test operation discovery."""
        discovery = HolisticDiscovery(mock_cortex_structure)
        operations = discovery._discover_operations()
        
        assert len(operations) == 1
        assert "test_module.py" in operations[0].name
    
    def test_discovers_agents(self, mock_cortex_structure):
        """Test agent discovery."""
        discovery = HolisticDiscovery(mock_cortex_structure)
        agents = discovery._discover_agents()
        
        assert len(agents) == 1
        assert agents[0].name == "test_agent.py"
    
    def test_discovers_dashboards(self, mock_cortex_structure):
        """Test dashboard discovery."""
        discovery = HolisticDiscovery(mock_cortex_structure)
        dashboards = discovery._discover_dashboards()
        
        assert len(dashboards) == 1
        assert "test_orchestrator.py" in dashboards[0].name


class TestWiringVerification:
    """Test wiring verification functionality."""
    
    @pytest.fixture
    def discovery_with_components(self, tmp_path):
        """Create discovery instance with mock components."""
        # Create structure
        (tmp_path / "src" / "orchestrators").mkdir(parents=True)
        (tmp_path / "tests" / "orchestrators").mkdir(parents=True)
        (tmp_path / "cortex-brain" / "orchestrator-manifests").mkdir(parents=True)
        
        # Create component
        component_path = tmp_path / "src" / "orchestrators" / "wired_orchestrator.py"
        component_path.write_text("# Wired orchestrator")
        
        # Create test file
        test_path = tmp_path / "tests" / "orchestrators" / "test_wired_orchestrator.py"
        test_path.write_text("# Tests")
        
        # Create manifest
        manifest_path = tmp_path / "cortex-brain" / "orchestrator-manifests" / "wired-orchestrator-manifest.yaml"
        manifest_path.write_text("manifest_version: 1.0")
        
        # Create operations.yaml
        operations_yaml = {
            "operations": {
                "wired_operation": {
                    "name": "Wired Operation",
                    "modules": ["wired_orchestrator"]
                }
            }
        }
        with open(tmp_path / "cortex-operations.yaml", "w") as f:
            yaml.dump(operations_yaml, f)
        
        discovery = HolisticDiscovery(tmp_path)
        return discovery, component_path
    
    def test_verifies_operations_yaml_entry(self, discovery_with_components):
        """Test operations.yaml entry verification."""
        discovery, _ = discovery_with_components
        operations_config = discovery._load_operations_yaml()
        
        assert discovery._check_operations_yaml_entry("wired_orchestrator", operations_config)
        assert not discovery._check_operations_yaml_entry("nonexistent", operations_config)
    
    def test_verifies_test_file_existence(self, discovery_with_components):
        """Test test file verification."""
        discovery, component_path = discovery_with_components
        
        assert discovery._check_test_file(component_path)
    
    def test_verifies_manifest_existence(self, discovery_with_components):
        """Test manifest verification."""
        discovery, _ = discovery_with_components
        
        assert discovery._check_manifest("wired_orchestrator", "orchestrator")
        assert not discovery._check_manifest("nonexistent", "orchestrator")
    
    def test_detects_fully_wired_component(self, discovery_with_components):
        """Test fully wired component detection."""
        discovery, component_path = discovery_with_components
        components = [component_path]
        
        discovery._verify_wiring(components, "orchestrator")
        
        assert len(discovery.discovered_components) == 1
        assert discovery.discovered_components[0]["fully_wired"]
        assert len(discovery.wiring_gaps) == 0
    
    def test_detects_wiring_gaps(self, tmp_path):
        """Test wiring gap detection."""
        # Create minimal structure
        (tmp_path / "src" / "orchestrators").mkdir(parents=True)
        component_path = tmp_path / "src" / "orchestrators" / "unwired_orchestrator.py"
        component_path.write_text("# Unwired orchestrator")
        
        # No test file, no manifest, no operations.yaml entry
        (tmp_path / "cortex-brain" / "orchestrator-manifests").mkdir(parents=True)
        with open(tmp_path / "cortex-operations.yaml", "w") as f:
            yaml.dump({"operations": {}}, f)
        
        discovery = HolisticDiscovery(tmp_path)
        discovery._verify_wiring([component_path], "orchestrator")
        
        assert len(discovery.discovered_components) == 1
        assert not discovery.discovered_components[0]["fully_wired"]
        assert len(discovery.wiring_gaps) == 1


class TestReportGeneration:
    """Test report generation functionality."""
    
    def test_generates_report_summary(self, tmp_path):
        """Test report summary generation."""
        discovery = HolisticDiscovery(tmp_path)
        discovery.discovered_components = [
            {"component": "comp1", "type": "orchestrator", "fully_wired": True},
            {"component": "comp2", "type": "operation", "fully_wired": False}
        ]
        discovery.wiring_gaps = [
            {
                "component": "comp2",
                "type": "operation",
                "path": "src/comp2.py",
                "wired_in_operations_yaml": False,
                "has_tests": True,
                "has_manifest": None,
                "has_documentation": True
            }
        ]
        
        report = discovery._generate_report()
        
        assert report["summary"]["total_components"] == 2
        assert report["summary"]["fully_wired"] == 1
        assert report["summary"]["wiring_gaps"] == 1
        assert "50.0%" in report["summary"]["wiring_rate"]
    
    def test_groups_components_by_type(self, tmp_path):
        """Test component grouping by type."""
        discovery = HolisticDiscovery(tmp_path)
        discovery.discovered_components = [
            {"component": "orch1", "type": "orchestrator", "fully_wired": True},
            {"component": "orch2", "type": "orchestrator", "fully_wired": True},
            {"component": "agent1", "type": "agent", "fully_wired": True}
        ]
        
        report = discovery._generate_report()
        
        assert report["components_by_type"]["orchestrator"] == 2
        assert report["components_by_type"]["agent"] == 1
    
    def test_generates_remediation_steps(self, tmp_path):
        """Test remediation steps generation."""
        discovery = HolisticDiscovery(tmp_path)
        discovery.wiring_gaps = [
            {
                "component": "broken_orch",
                "type": "orchestrator",
                "path": "src/orchestrators/broken_orch.py",
                "wired_in_operations_yaml": False,
                "has_tests": False,
                "has_manifest": False,
                "has_documentation": False
            }
        ]
        
        report = discovery._generate_report()
        
        assert len(report["remediation_steps"]) == 1
        assert report["remediation_steps"][0]["component"] == "broken_orch"
        assert len(report["remediation_steps"][0]["actions"]) == 4  # All 4 issues
    
    def test_saves_report_to_file(self, tmp_path):
        """Test report file saving."""
        discovery = HolisticDiscovery(tmp_path)
        discovery.discovered_components = [
            {
                "component": "test_orch",
                "type": "orchestrator",
                "path": "src/orchestrators/test_orch.py",
                "wired_in_operations_yaml": True,
                "has_tests": True,
                "has_manifest": True,
                "has_documentation": True,
                "fully_wired": True
            }
        ]
        
        report = discovery._generate_report()
        report_path = discovery.save_report(report)
        
        assert report_path.exists()
        assert "deployment-discovery-" in report_path.name
        assert report_path.suffix == ".md"
        
        # Verify content
        content = report_path.read_text()
        assert "Deployment Functionality Discovery Report" in content
        assert "test_orch" in content
        assert "✅" in content  # Fully wired indicator


class TestEndToEndDiscovery:
    """Test end-to-end discovery workflow."""
    
    def test_run_discovery_function(self):
        """Test run_discovery() convenience function."""
        # Use actual CORTEX root
        cortex_root = Path(__file__).parent.parent.parent
        
        report = run_discovery(cortex_root)
        
        assert "timestamp" in report
        assert "summary" in report
        assert "discovered_components" in report
        assert "wiring_gaps" in report
        assert "remediation_steps" in report
        
        # Should discover actual CORTEX components
        assert report["summary"]["total_components"] > 0
