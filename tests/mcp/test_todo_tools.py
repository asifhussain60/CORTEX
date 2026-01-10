"""
CORTEX 6.0 - TODO MCP Tools Tests

Tests for TODO MCP tool wrappers.

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

from mcp.todo_tools import (
    todo_create,
    todo_list,
    todo_update,
    todo_complete,
    todo_dependencies
)


@pytest.mark.ac_id("AC-TODO-001")
class TestTodoCreate:
    """Test todo_create MCP tool."""
    
    def test_create_basic(self):
        """Test creating a basic TODO."""
        temp_dir = tempfile.mkdtemp()
        try:
            result = todo_create(
                title="Test TODO",
                description="A test task",
                workspace_root=temp_dir
            )
            
            assert result["success"] is True
            assert result["todo_id"].startswith("todo-")
            assert result["title"] == "Test TODO"
            assert result["status"] == "PENDING"
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_create_with_priority(self):
        """Test creating TODO with priority."""
        temp_dir = tempfile.mkdtemp()
        try:
            result = todo_create(
                title="High Priority Task",
                workspace_root=temp_dir,
                priority="HIGH"
            )
            
            assert result["success"] is True
            assert result["priority"] == "HIGH"
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.mark.ac_id("AC-TODO-002")
class TestTodoList:
    """Test todo_list MCP tool."""
    
    def test_list_empty(self):
        """Test listing TODOs in empty workspace."""
        temp_dir = tempfile.mkdtemp()
        try:
            result = todo_list(workspace_root=temp_dir)
            
            assert result["success"] is True
            assert result["count"] == 0
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_list_with_filter(self):
        """Test listing TODOs with status filter."""
        temp_dir = tempfile.mkdtemp()
        try:
            # Create TODOs
            todo_create(title="Task 1", workspace_root=temp_dir)
            create_result = todo_create(title="Task 2", workspace_root=temp_dir)
            todo_update(create_result["todo_id"], workspace_root=temp_dir, status="IN_PROGRESS")
            
            # Filter by status
            result = todo_list(workspace_root=temp_dir, status="IN_PROGRESS")
            
            assert result["success"] is True
            assert result["count"] == 1
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.mark.ac_id("AC-TODO-003")
class TestTodoUpdate:
    """Test todo_update MCP tool."""
    
    def test_update_status(self):
        """Test updating TODO status."""
        temp_dir = tempfile.mkdtemp()
        try:
            create_result = todo_create(
                title="Update Test",
                workspace_root=temp_dir
            )
            
            result = todo_update(
                todo_id=create_result["todo_id"],
                workspace_root=temp_dir,
                status="IN_PROGRESS"
            )
            
            assert result["success"] is True
            assert result["status"] == "IN_PROGRESS"
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.mark.ac_id("AC-TODO-004")
class TestTodoComplete:
    """Test todo_complete MCP tool."""
    
    def test_complete_todo(self):
        """Test completing a TODO."""
        temp_dir = tempfile.mkdtemp()
        try:
            create_result = todo_create(
                title="Complete Me",
                workspace_root=temp_dir
            )
            
            result = todo_complete(
                todo_id=create_result["todo_id"],
                workspace_root=temp_dir
            )
            
            assert result["success"] is True
            assert result["status"] == "COMPLETE"
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.mark.ac_id("AC-TODO-005")
class TestTodoDependencies:
    """Test todo_dependencies MCP tool."""
    
    def test_dependencies_analysis(self):
        """Test analyzing TODO dependencies."""
        temp_dir = tempfile.mkdtemp()
        try:
            # Create parent task
            parent = todo_create(title="Parent Task", workspace_root=temp_dir)
            
            # Create child task with dependency
            child = todo_create(
                title="Child Task",
                workspace_root=temp_dir,
                dependencies=[parent["todo_id"]]
            )
            
            # Analyze child dependencies
            result = todo_dependencies(
                todo_id=child["todo_id"],
                workspace_root=temp_dir
            )
            
            assert result["success"] is True
            assert parent["todo_id"] in result["dependencies"]
            assert result["can_start"] is False  # Parent not complete
            
            # Complete parent
            todo_complete(parent["todo_id"], workspace_root=temp_dir)
            
            # Re-analyze
            result = todo_dependencies(
                todo_id=child["todo_id"],
                workspace_root=temp_dir
            )
            
            assert result["can_start"] is True
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
