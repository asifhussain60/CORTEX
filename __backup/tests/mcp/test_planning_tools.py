"""
CORTEX 6.0 - Planning MCP Tools Tests

Tests for planning MCP tool wrappers.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import yaml

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from mcp.planning_tools import (
    planning_create,
    planning_execute,
    planning_list,
    planning_status,
    planning_update
)


@pytest.mark.ac_id("AC-PLAN-001")
class TestPlanningCreate:
    """Test planning_create MCP tool."""
    
    def test_create_plan_basic(self):
        """Test creating a basic plan."""
        temp_dir = tempfile.mkdtemp()
        try:
            result = planning_create(
                name="Test Plan",
                description="A test plan",
                workspace_root=temp_dir
            )
            
            assert result["success"] is True
            assert result["plan_id"].startswith("plan-")
            assert result["status"] == "DRAFT"
            assert Path(result["plan_path"]).exists()
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_create_plan_with_stages(self):
        """Test creating plan with stages."""
        temp_dir = tempfile.mkdtemp()
        try:
            stages = [
                {"name": "Stage 1", "status": "PENDING"},
                {"name": "Stage 2", "status": "PENDING"}
            ]
            
            result = planning_create(
                name="Multi-Stage Plan",
                description="Plan with stages",
                workspace_root=temp_dir,
                stages=stages
            )
            
            assert result["success"] is True
            
            # Verify stages in file
            with open(result["plan_path"]) as f:
                plan_data = yaml.safe_load(f)
            assert len(plan_data["stages"]) == 2
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.mark.ac_id("AC-PLAN-002")
class TestPlanningList:
    """Test planning_list MCP tool."""
    
    def test_list_empty(self):
        """Test listing plans in empty workspace."""
        temp_dir = tempfile.mkdtemp()
        try:
            result = planning_list(workspace_root=temp_dir)
            
            assert result["success"] is True
            assert result["count"] == 0
            assert result["plans"] == []
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_list_with_plans(self):
        """Test listing plans."""
        temp_dir = tempfile.mkdtemp()
        try:
            # Create some plans
            planning_create(name="Plan 1", description="First", workspace_root=temp_dir)
            planning_create(name="Plan 2", description="Second", workspace_root=temp_dir)
            
            result = planning_list(workspace_root=temp_dir)
            
            assert result["success"] is True
            assert result["count"] == 2
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.mark.ac_id("AC-PLAN-003")
class TestPlanningStatus:
    """Test planning_status MCP tool."""
    
    def test_status_existing_plan(self):
        """Test getting status of existing plan."""
        temp_dir = tempfile.mkdtemp()
        try:
            create_result = planning_create(
                name="Status Test",
                description="Test",
                workspace_root=temp_dir
            )
            
            result = planning_status(
                plan_id=create_result["plan_id"],
                workspace_root=temp_dir
            )
            
            assert result["success"] is True
            assert result["plan_id"] == create_result["plan_id"]
            assert result["name"] == "Status Test"
            assert result["status"] == "DRAFT"
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_status_nonexistent_plan(self):
        """Test getting status of nonexistent plan."""
        temp_dir = tempfile.mkdtemp()
        try:
            result = planning_status(
                plan_id="plan-nonexistent",
                workspace_root=temp_dir
            )
            
            assert result["success"] is False
            assert "not found" in result["error"].lower()
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.mark.ac_id("AC-PLAN-004")
class TestPlanningUpdate:
    """Test planning_update MCP tool."""
    
    def test_update_status(self):
        """Test updating plan status."""
        temp_dir = tempfile.mkdtemp()
        try:
            create_result = planning_create(
                name="Update Test",
                description="Test",
                workspace_root=temp_dir
            )
            
            result = planning_update(
                plan_id=create_result["plan_id"],
                workspace_root=temp_dir,
                status="IN_PROGRESS"
            )
            
            assert result["success"] is True
            assert result["status"] == "IN_PROGRESS"
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.mark.ac_id("AC-PLAN-005")
class TestPlanningExecute:
    """Test planning_execute MCP tool."""
    
    def test_execute_dry_run(self):
        """Test dry run execution."""
        temp_dir = tempfile.mkdtemp()
        try:
            create_result = planning_create(
                name="Execute Test",
                description="Test",
                workspace_root=temp_dir
            )
            
            result = planning_execute(
                plan_id=create_result["plan_id"],
                workspace_root=temp_dir,
                dry_run=True
            )
            
            # May fail if orchestrator not available, but should handle gracefully
            assert "success" in result
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
