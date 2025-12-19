"""
Tests for plan CLI commands integration.

This module tests the plan subcommands: list, show, search, update.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from src.workflows.plan_cli import PlanCLI


@pytest.fixture
def cli(tmp_path):
    """Create CLI with temporary brain path."""
    brain_path = tmp_path / "cortex-brain"
    brain_path.mkdir(parents=True)
    return PlanCLI(brain_path)


@pytest.fixture
def registry_with_plans(tmp_path):
    """Create registry with sample plans."""
    from src.workflows.plan_registry import PlanRegistry
    
    brain_path = tmp_path / "cortex-brain"
    planning_dir = brain_path / "documents" / "planning"
    planning_dir.mkdir(parents=True)
    
    # Create sample plans
    plans = [
        ("active-001.md", "ACTIVE-001", "in-progress", "high", "Active Feature"),
        ("completed-001.md", "COMP-001", "completed", "medium", "Completed Feature"),
    ]
    
    for filename, plan_id, status, priority, title in plans:
        plan_file = planning_dir / filename
        plan_file.write_text(f"""---
plan_id: {plan_id}
title: {title}
status: {status}
priority: {priority}
created_date: 2025-12-03
estimated_hours: 10
---
# Content
""")
    
    registry = PlanRegistry(brain_path)
    registry.scan_and_index()
    return brain_path, registry


class TestPlanCLIList:
    """Test 'plan list' command."""
    
    def test_list_all_plans(self, registry_with_plans):
        """Should list all plans."""
        brain_path, _ = registry_with_plans
        cli = PlanCLI(brain_path)
        
        output = cli.list_plans()
        
        assert "ACTIVE-001" in output
        assert "COMP-001" in output
        assert "Active Feature" in output
    
    def test_list_with_status_filter(self, registry_with_plans):
        """Should filter by status."""
        brain_path, _ = registry_with_plans
        cli = PlanCLI(brain_path)
        
        output = cli.list_plans(status="in-progress")
        
        assert "ACTIVE-001" in output
        assert "COMP-001" not in output
    
    def test_list_with_priority_filter(self, registry_with_plans):
        """Should filter by priority."""
        brain_path, _ = registry_with_plans
        cli = PlanCLI(brain_path)
        
        output = cli.list_plans(priority="high")
        
        assert "ACTIVE-001" in output
        assert "COMP-001" not in output
    
    def test_list_empty_registry(self, tmp_path):
        """Should handle empty registry gracefully."""
        brain_path = tmp_path / "cortex-brain"
        brain_path.mkdir(parents=True)
        cli = PlanCLI(brain_path)
        
        output = cli.list_plans()
        
        assert "No plans found" in output


class TestPlanCLIShow:
    """Test 'plan show' command."""
    
    def test_show_existing_plan(self, registry_with_plans):
        """Should display plan details."""
        brain_path, _ = registry_with_plans
        cli = PlanCLI(brain_path)
        
        output = cli.show_plan("ACTIVE-001")
        
        assert "ACTIVE-001" in output
        assert "Active Feature" in output
        assert "in-progress" in output
        assert "high" in output
    
    def test_show_nonexistent_plan(self, registry_with_plans):
        """Should handle nonexistent plan."""
        brain_path, _ = registry_with_plans
        cli = PlanCLI(brain_path)
        
        output = cli.show_plan("NONEXISTENT")
        
        assert "not found" in output.lower()


class TestPlanCLISearch:
    """Test 'plan search' command."""
    
    def test_search_finds_matches(self, registry_with_plans):
        """Should find matching plans."""
        brain_path, _ = registry_with_plans
        cli = PlanCLI(brain_path)
        
        output = cli.search_plans("Active")
        
        assert "ACTIVE-001" in output
        assert "Active Feature" in output
    
    def test_search_no_matches(self, registry_with_plans):
        """Should handle no matches gracefully."""
        brain_path, _ = registry_with_plans
        cli = PlanCLI(brain_path)
        
        output = cli.search_plans("nonexistent")
        
        assert "No plans found" in output


class TestPlanCLIUpdate:
    """Test 'plan update' command."""
    
    def test_update_plan_status(self, registry_with_plans):
        """Should update plan status."""
        brain_path, registry = registry_with_plans
        cli = PlanCLI(brain_path)
        
        output = cli.update_plan_status("ACTIVE-001", "completed")
        
        assert "updated" in output.lower()
        
        # Verify update in registry
        plan = registry.get_plan("ACTIVE-001")
        assert plan["status"] == "completed"
    
    def test_update_nonexistent_plan(self, registry_with_plans):
        """Should handle nonexistent plan."""
        brain_path, _ = registry_with_plans
        cli = PlanCLI(brain_path)
        
        output = cli.update_plan_status("NONEXISTENT", "completed")
        
        assert "not found" in output.lower()
    
    def test_update_invalid_status(self, registry_with_plans):
        """Should validate status values."""
        brain_path, _ = registry_with_plans
        cli = PlanCLI(brain_path)
        
        output = cli.update_plan_status("ACTIVE-001", "invalid-status")
        
        assert "invalid" in output.lower()


class TestPlanCLIFormatting:
    """Test output formatting."""
    
    def test_list_formats_as_table(self, registry_with_plans):
        """Should format list output as table."""
        brain_path, _ = registry_with_plans
        cli = PlanCLI(brain_path)
        
        output = cli.list_plans()
        
        # Should have table-like formatting
        assert "ID" in output or "Plan ID" in output
        assert "Title" in output
        assert "Status" in output
        assert "Priority" in output
    
    def test_show_formats_as_details(self, registry_with_plans):
        """Should format show output with details."""
        brain_path, _ = registry_with_plans
        cli = PlanCLI(brain_path)
        
        output = cli.show_plan("ACTIVE-001")
        
        # Should have key-value pairs
        assert ":" in output
        assert "Plan ID" in output or "ID" in output
        assert "Title" in output


class TestPlanCLIIntegration:
    """Test CLI integration with other components."""
    
    def test_cli_uses_registry(self, tmp_path):
        """Should use PlanRegistry for data."""
        brain_path = tmp_path / "cortex-brain"
        brain_path.mkdir(parents=True)
        
        cli = PlanCLI(brain_path)
        
        # Should have registry attribute
        assert hasattr(cli, "registry")
        assert cli.registry is not None
    
    def test_cli_regenerates_index_after_update(self, registry_with_plans):
        """Should regenerate INDEX.md after status update."""
        brain_path, _ = registry_with_plans
        cli = PlanCLI(brain_path)
        
        cli.update_plan_status("ACTIVE-001", "completed")
        
        # Verify INDEX.md exists and is recent
        index_path = brain_path / "documents" / "planning" / "INDEX.md"
        assert index_path.exists()
