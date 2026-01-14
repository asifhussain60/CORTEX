"""
CORTEX 6.0 - Housekeeping MCP Tools Tests

Tests for housekeeping MCP tool wrappers.
Validates all 5 MCP tools for system maintenance.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import yaml

# Add src to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from mcp.housekeeping_tools import (
    housekeeping_status,
    housekeeping_execute,
    housekeeping_phase,
    housekeeping_health,
    housekeeping_reports
)


@pytest.mark.ac_id("AC-HOUSE-001")
class TestHousekeepingStatus:
    """Test housekeeping_status MCP tool."""
    
    def test_status_real_workspace(self):
        """Test status on real CORTEX workspace."""
        result = housekeeping_status()
        
        assert result["success"] is True
        assert result["status"] == "ready"
        assert result["configuration"]["manual_only"] is True
        assert result["configuration"]["phases_available"] == 9
        assert len(result["phases"]) == 9
    
    def test_status_temp_workspace(self):
        """Test status on temporary workspace."""
        temp_dir = tempfile.mkdtemp()
        try:
            result = housekeeping_status(workspace_root=temp_dir)
            
            assert result["success"] is True
            assert result["status"] == "ready"
            # No last execution in empty workspace
            assert result["last_execution"] is None
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.mark.ac_id("AC-HOUSE-002")
class TestHousekeepingExecute:
    """Test housekeeping_execute MCP tool."""
    
    def test_execute_dry_run(self):
        """Test dry run mode."""
        temp_dir = tempfile.mkdtemp()
        try:
            result = housekeeping_execute(workspace_root=temp_dir, dry_run=True)
            
            assert result["success"] is True
            assert result["dry_run"] is True
            assert len(result["phases_to_execute"]) == 9
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_execute_full_workflow(self):
        """Test full workflow execution."""
        temp_dir = tempfile.mkdtemp()
        try:
            # Create minimal cortex-brain structure
            brain_dir = Path(temp_dir) / "cortex-brain"
            (brain_dir / "tier0").mkdir(parents=True)
            (brain_dir / "tier1").mkdir(parents=True)
            (brain_dir / "tier2").mkdir(parents=True)
            (brain_dir / "tier3").mkdir(parents=True)
            (brain_dir / "documents" / "reports").mkdir(parents=True)
            
            result = housekeeping_execute(workspace_root=temp_dir)
            
            assert result["success"] is True
            assert "overall_health_score" in result
            assert result["phases_executed"] == 9
            assert result["total_duration_seconds"] >= 0
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.mark.ac_id("AC-HOUSE-003")
class TestHousekeepingPhase:
    """Test housekeeping_phase MCP tool."""
    
    def test_execute_single_phase(self):
        """Test executing a single phase."""
        temp_dir = tempfile.mkdtemp()
        try:
            # Create minimal structure
            brain_dir = Path(temp_dir) / "cortex-brain"
            (brain_dir / "tier0").mkdir(parents=True)
            (brain_dir / "tier1").mkdir(parents=True)
            (brain_dir / "tier2").mkdir(parents=True)
            (brain_dir / "tier3").mkdir(parents=True)
            
            # Execute phase 4 (brain tier sync)
            result = housekeeping_phase(phase_number=4, workspace_root=temp_dir)
            
            assert result["success"] is True
            assert result["phase"]["number"] == 4
            assert result["phase"]["name"] == "brain_tier_sync"
            assert result["phase"]["status"] in ["SUCCESS", "SKIPPED"]
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_invalid_phase_number(self):
        """Test invalid phase number."""
        result = housekeeping_phase(phase_number=0)
        
        assert result["success"] is False
        assert "Invalid phase number" in result["error"]
        
        result = housekeeping_phase(phase_number=10)
        
        assert result["success"] is False
        assert "Invalid phase number" in result["error"]


@pytest.mark.ac_id("AC-HOUSE-004")
class TestHousekeepingHealth:
    """Test housekeeping_health MCP tool."""
    
    def test_health_real_workspace(self):
        """Test health on real CORTEX workspace."""
        result = housekeeping_health()
        
        assert result["success"] is True
        assert "overall_health_score" in result
        assert "components" in result
        assert isinstance(result["components"], dict)
    
    def test_health_temp_workspace(self):
        """Test health on temporary workspace."""
        temp_dir = tempfile.mkdtemp()
        try:
            result = housekeeping_health(workspace_root=temp_dir)
            
            assert result["success"] is True
            # Empty workspace has lower scores
            assert "overall_health_score" in result
            assert len(result["recommendations"]) > 0
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.mark.ac_id("AC-HOUSE-005")
class TestHousekeepingReports:
    """Test housekeeping_reports MCP tool."""
    
    def test_reports_real_workspace(self):
        """Test listing reports on real workspace."""
        result = housekeeping_reports()
        
        assert result["success"] is True
        assert "reports" in result
        assert "count" in result
    
    def test_reports_empty_workspace(self):
        """Test listing reports on empty workspace."""
        temp_dir = tempfile.mkdtemp()
        try:
            result = housekeeping_reports(workspace_root=temp_dir)
            
            assert result["success"] is True
            assert result["count"] == 0
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_reports_with_data(self):
        """Test listing reports with actual report files."""
        temp_dir = tempfile.mkdtemp()
        try:
            # Create reports directory with sample report
            reports_dir = Path(temp_dir) / "cortex-brain" / "documents" / "reports"
            reports_dir.mkdir(parents=True)
            
            report_data = {
                "timestamp": "2026-01-09T12:00:00",
                "overall_health_score": 85.5,
                "total_duration_seconds": 1.5,
                "phase_results": [{"phase": 1}]
            }
            
            with open(reports_dir / "housekeeping-20260109-120000.yaml", "w") as f:
                yaml.dump(report_data, f)
            
            result = housekeeping_reports(workspace_root=temp_dir)
            
            assert result["success"] is True
            assert result["count"] == 1
            assert result["reports"][0]["overall_health_score"] == 85.5
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
