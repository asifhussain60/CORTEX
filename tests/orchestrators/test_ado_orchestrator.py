"""
Tests for ADO Orchestrator v2 (Azure DevOps Integration).

Validates Azure DevOps work item generation:
- User story creation
- Feature creation
- Epic linking
- Acceptance criteria generation
- Work item relationships
- Status tracking

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.orchestrators.ado.ado_orchestrator import (
    ADOOrchestratorV2,
    WorkItemType,
    ADOResult
)
from src.orchestrators.base.base_orchestrator import (
    OrchestratorStatus,
    OrchestratorResult
)


class TestADOOrchestratorV2:
    """Test suite for ADO Orchestrator v2."""
    
    @pytest.fixture
    def workspace_root(self, tmp_path):
        """Create temporary workspace."""
        workspace = tmp_path / "test_workspace"
        workspace.mkdir()
        return str(workspace)
    
    @pytest.fixture
    def orchestrator(self, workspace_root):
        """Create ADOOrchestratorV2 instance."""
        return ADOOrchestratorV2(workspace_root=workspace_root)
    
    def test_orchestrator_initialization(self, orchestrator):
        """Test RED: Orchestrator initializes correctly."""
        assert orchestrator is not None
        assert orchestrator.workspace_root is not None
        assert hasattr(orchestrator, 'execute')
    
    def test_create_user_story(self, orchestrator):
        """Test RED: Create user story work item."""
        result = orchestrator._create_user_story(
            title="User Authentication",
            description="Implement user login system",
            acceptance_criteria=["Users can log in", "Passwords are encrypted"]
        )
        
        assert result is not None
        assert 'work_item_id' in result or 'title' in result
    
    def test_create_feature(self, orchestrator):
        """Test RED: Create feature work item."""
        result = orchestrator._create_feature(
            title="Authentication System",
            description="Complete authentication module",
            user_stories=["story-1", "story-2"]
        )
        
        assert result is not None
        assert 'work_item_id' in result or 'title' in result
    
    def test_create_epic(self, orchestrator):
        """Test RED: Create epic work item."""
        result = orchestrator._create_epic(
            title="CORTEX 6.0 Build",
            description="Complete CORTEX 6.0 implementation",
            features=["feature-1", "feature-2"]
        )
        
        assert result is not None
        assert 'work_item_id' in result or 'title' in result
    
    def test_generate_acceptance_criteria(self, orchestrator):
        """Test RED: Generate acceptance criteria from context."""
        result = orchestrator._generate_acceptance_criteria(
            context="User needs to authenticate with username and password"
        )
        
        assert result is not None
        assert isinstance(result, list)
        assert len(result) > 0
    
    def test_link_work_items(self, orchestrator):
        """Test RED: Link parent-child work items."""
        result = orchestrator._link_work_items(
            parent_id="feature-1",
            child_id="story-1",
            link_type="parent-child"
        )
        
        assert result is not None
        assert 'success' in result or 'linked' in result
    
    def test_full_ado_execution(self, orchestrator):
        """Test RED: Full ADO workflow execution."""
        result = orchestrator.execute(
            context={
                "type": "user_story",
                "title": "User Authentication",
                "description": "Implement login"
            }
        )
        
        assert result.status == OrchestratorStatus.SUCCESS
        assert 'work_item_created' in result.data or 'created' in result.data
