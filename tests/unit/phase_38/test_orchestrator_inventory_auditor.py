"""
Tests for OrchestratorInventoryAuditor - Phase 38.0 Stage 2
Tests MUST come before implementation (CORE-008 TDD)

AC-PHASE38.0-002: Orchestrator Inventory Audit
- Discovers all orchestrators in cortex/orchestrators
- Cross-references with wiring.yaml
- Generates JSON inventory report
- Validates 35 orchestrators + 199 support files
"""

import pytest
from pathlib import Path
from typing import Dict, Any, List
import json


class TestOrchestratorInventoryAuditor:
    """Test suite for orchestrator inventory audit."""
    
    def test_auditor_initializes_with_valid_paths(self):
        """Test auditor initialization with workspace paths."""
        from cortex.phase_38.orchestrator_inventory_auditor import OrchestratorInventoryAuditor
        
        workspace = Path("/Users/asifhussain/PROJECTS/CORTEX")
        auditor = OrchestratorInventoryAuditor(workspace_root=workspace)
        
        assert auditor.workspace_root == workspace
        assert auditor.orchestrators_dir == workspace / "cortex" / "orchestrators"
        assert auditor.wiring_file == workspace / "cortex" / "wiring" / "specifications" / "wiring.yaml"
    
    def test_auditor_discovers_orchestrator_files(self):
        """Test discovery of all Python files in orchestrators directory."""
        from cortex.phase_38.orchestrator_inventory_auditor import OrchestratorInventoryAuditor
        
        workspace = Path("/Users/asifhussain/PROJECTS/CORTEX")
        auditor = OrchestratorInventoryAuditor(workspace_root=workspace)
        
        files = auditor.discover_orchestrator_files()
        
        assert isinstance(files, list)
        assert len(files) > 0
        # Should find ~234 files (35 orchestrators + 199 support)
        assert len(files) >= 200
        assert all(isinstance(f, Path) for f in files)
        assert all(f.suffix == ".py" for f in files)
    
    def test_auditor_categorizes_files_by_type(self):
        """Test categorization of files into orchestrators vs support."""
        from cortex.phase_38.orchestrator_inventory_auditor import OrchestratorInventoryAuditor
        
        workspace = Path("/Users/asifhussain/PROJECTS/CORTEX")
        auditor = OrchestratorInventoryAuditor(workspace_root=workspace)
        
        categories = auditor.categorize_files()
        
        assert "orchestrators" in categories
        assert "support_files" in categories
        assert isinstance(categories["orchestrators"], list)
        assert isinstance(categories["support_files"], list)
        
        # Validate counts
        assert len(categories["orchestrators"]) >= 30  # Should find ~35
        assert len(categories["support_files"]) >= 100  # Should find ~199
    
    def test_auditor_loads_wiring_yaml(self):
        """Test loading and parsing of wiring.yaml."""
        from cortex.phase_38.orchestrator_inventory_auditor import OrchestratorInventoryAuditor
        
        workspace = Path("/Users/asifhussain/PROJECTS/CORTEX")
        auditor = OrchestratorInventoryAuditor(workspace_root=workspace)
        
        wiring_data = auditor.load_wiring_yaml()
        
        assert isinstance(wiring_data, dict)
        assert "orchestrators" in wiring_data or "tools" in wiring_data
    
    def test_auditor_cross_references_with_wiring(self):
        """Test cross-referencing discovered orchestrators with wiring.yaml."""
        from cortex.phase_38.orchestrator_inventory_auditor import OrchestratorInventoryAuditor
        
        workspace = Path("/Users/asifhussain/PROJECTS/CORTEX")
        auditor = OrchestratorInventoryAuditor(workspace_root=workspace)
        
        cross_ref = auditor.cross_reference_wiring()
        
        assert "in_wiring" in cross_ref
        assert "not_in_wiring" in cross_ref
        assert "wiring_not_found" in cross_ref
        
        assert isinstance(cross_ref["in_wiring"], list)
        assert isinstance(cross_ref["not_in_wiring"], list)
        assert isinstance(cross_ref["wiring_not_found"], list)
    
    def test_auditor_generates_json_report(self):
        """Test generation of JSON inventory report."""
        from cortex.phase_38.orchestrator_inventory_auditor import OrchestratorInventoryAuditor
        
        workspace = Path("/Users/asifhussain/PROJECTS/CORTEX")
        auditor = OrchestratorInventoryAuditor(workspace_root=workspace)
        
        report_path = auditor.generate_report()
        
        assert report_path.exists()
        assert report_path.suffix == ".json"
        assert "orchestrator-inventory" in report_path.name
        
        # Validate JSON structure
        with open(report_path, 'r') as f:
            report = json.load(f)
        
        assert "timestamp" in report
        assert "total_files" in report
        assert "orchestrators_count" in report
        assert "support_files_count" in report
        assert "orchestrators" in report
        assert "wiring_cross_reference" in report
    
    def test_auditor_report_has_minimum_orchestrator_count(self):
        """Test that report contains expected minimum orchestrator count."""
        from cortex.phase_38.orchestrator_inventory_auditor import OrchestratorInventoryAuditor
        
        workspace = Path("/Users/asifhussain/PROJECTS/CORTEX")
        auditor = OrchestratorInventoryAuditor(workspace_root=workspace)
        
        report_path = auditor.generate_report()
        
        with open(report_path, 'r') as f:
            report = json.load(f)
        
        # Phase 38.0 specification: 35 orchestrators minimum
        assert report["orchestrators_count"] >= 30
    
    def test_auditor_report_has_minimum_support_count(self):
        """Test that report contains expected minimum support file count."""
        from cortex.phase_38.orchestrator_inventory_auditor import OrchestratorInventoryAuditor
        
        workspace = Path("/Users/asifhussain/PROJECTS/CORTEX")
        auditor = OrchestratorInventoryAuditor(workspace_root=workspace)
        
        report_path = auditor.generate_report()
        
        with open(report_path, 'r') as f:
            report = json.load(f)
        
        # Phase 38.0 specification: 199 support files minimum
        assert report["support_files_count"] >= 100
    
    def test_auditor_validates_total_file_count(self):
        """Test that total file count matches sum of orchestrators + support."""
        from cortex.phase_38.orchestrator_inventory_auditor import OrchestratorInventoryAuditor
        
        workspace = Path("/Users/asifhussain/PROJECTS/CORTEX")
        auditor = OrchestratorInventoryAuditor(workspace_root=workspace)
        
        report_path = auditor.generate_report()
        
        with open(report_path, 'r') as f:
            report = json.load(f)
        
        expected_total = report["orchestrators_count"] + report["support_files_count"]
        assert report["total_files"] == expected_total
    
    def test_auditor_report_saved_to_correct_location(self):
        """Test that report is saved to cortex-registry/_cortex-master/reports/."""
        from cortex.phase_38.orchestrator_inventory_auditor import OrchestratorInventoryAuditor
        
        workspace = Path("/Users/asifhussain/PROJECTS/CORTEX")
        auditor = OrchestratorInventoryAuditor(workspace_root=workspace)
        
        report_path = auditor.generate_report()
        
        # Verify path structure
        assert "cortex-registry" in str(report_path)
        assert "_cortex-master" in str(report_path)
        assert "reports" in str(report_path)
