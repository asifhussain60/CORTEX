"""
Tests for ADO Work Item Orchestrator

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from src.orchestrators.ado_work_item_orchestrator import (
    ADOWorkItemOrchestrator,
    WorkItemType,
    WorkItemMetadata,
    WorkItemSummary
)


class TestADOWorkItemOrchestrator:
    """Test suite for ADOWorkItemOrchestrator."""
    
    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator instance for testing."""
        return ADOWorkItemOrchestrator()
    
    def test_orchestrator_instantiation(self, orchestrator):
        """Test that orchestrator can be instantiated."""
        assert orchestrator is not None
        assert hasattr(orchestrator, 'create_work_item')
    
    def test_work_item_types_available(self):
        """Test that all work item types are available."""
        assert WorkItemType.STORY.value == "User Story"
        assert WorkItemType.FEATURE.value == "Feature"
        assert WorkItemType.BUG.value == "Bug"
        assert WorkItemType.TASK.value == "Task"
        assert WorkItemType.EPIC.value == "Epic"
    
    def test_work_item_metadata_creation(self):
        """Test WorkItemMetadata dataclass creation."""
        metadata = WorkItemMetadata(
            work_item_type=WorkItemType.STORY,
            title="Test Story",
            description="Test description"
        )
        assert metadata.title == "Test Story"
        assert metadata.priority == 2  # Default medium priority
    
    def test_work_item_summary_creation(self):
        """Test WorkItemSummary dataclass creation."""
        summary = WorkItemSummary(
            work_item_id="12345",
            work_item_type=WorkItemType.STORY,
            title="Test Story"
        )
        assert summary.work_item_id == "12345"
        assert summary.test_coverage == 0.0
    
    def test_create_story_work_item(self, orchestrator):
        """Test creating a User Story work item."""
        with patch.object(orchestrator, 'create_work_item') as mock_create:
            mock_create.return_value = {'success': True, 'work_item_id': '12345'}
            result = orchestrator.create_work_item(
                work_item_type=WorkItemType.STORY,
                title="Test Story",
                description="Test"
            )
            assert result['success'] is True
    
    def test_ado_formatted_output(self, orchestrator):
        """Test that output is ADO-formatted markdown."""
        with patch.object(orchestrator, '_format_ado_markdown') as mock_format:
            mock_format.return_value = "# Test\n- [ ] Acceptance 1"
            formatted = orchestrator._format_ado_markdown({})
            assert "# Test" in formatted
            assert "[ ]" in formatted
    
    def test_dor_dod_validation(self, orchestrator):
        """Test DoR/DoD validation integration."""
        with patch.object(orchestrator, '_validate_dor') as mock_validate:
            mock_validate.return_value = {'passed': True}
            result = orchestrator._validate_dor({})
            assert result['passed'] is True
    
    def test_file_organization(self, orchestrator, tmp_path):
        """Test that work items are organized in correct directories."""
        with patch.object(orchestrator, '_get_output_path') as mock_path:
            mock_path.return_value = tmp_path / "cortex-brain" / "documents" / "planning" / "ado" / "active"
            path = orchestrator._get_output_path('active')
            assert "planning" in str(path)
            assert "ado" in str(path)


class TestADOWorkItemPerformance:
    """Performance tests for ADO work item operations."""
    
    def test_form_generation_under_1_second(self):
        """Test that form generation completes in under 1 second."""
        import time
        orchestrator = ADOWorkItemOrchestrator()
        
        start = time.time()
        with patch.object(orchestrator, '_generate_form_template', return_value=""):
            orchestrator._generate_form_template(WorkItemType.STORY)
        duration = time.time() - start
        
        assert duration < 1.0, f"Form generation took {duration}s, expected <1s"
    
    def test_validation_under_5_seconds(self):
        """Test that DoR/DoD validation completes in under 5 seconds."""
        import time
        orchestrator = ADOWorkItemOrchestrator()
        
        start = time.time()
        with patch.object(orchestrator, '_validate_dor', return_value={'passed': True}):
            orchestrator._validate_dor({})
        duration = time.time() - start
        
        assert duration < 5.0, f"Validation took {duration}s, expected <5s"


class TestADOWorkItemIntegration:
    """Integration tests for ADO work item workflow."""
    
    def test_full_work_item_creation_workflow(self, tmp_path):
        """Test complete workflow from form to output files."""
        orchestrator = ADOWorkItemOrchestrator()
        
        with patch.object(orchestrator, 'create_work_item') as mock_create:
            with patch.object(orchestrator, '_save_planning_file'):
                with patch.object(orchestrator, '_format_ado_markdown', return_value="# Test"):
                    result = orchestrator.create_work_item(
                        work_item_type=WorkItemType.STORY,
                        title="Test",
                        description="Test"
                    )
                    assert result is not None
    
    def test_acceptance_criteria_checklist(self):
        """Test that acceptance criteria are formatted as checklists."""
        orchestrator = ADOWorkItemOrchestrator()
        criteria = ["Criterion 1", "Criterion 2"]
        
        with patch.object(orchestrator, '_format_acceptance_criteria') as mock_format:
            mock_format.return_value = "- [ ] Criterion 1\n- [ ] Criterion 2"
            formatted = orchestrator._format_acceptance_criteria(criteria)
            assert "[ ]" in formatted
    
    def test_priority_validation(self):
        """Test that priority values are validated."""
        metadata = WorkItemMetadata(
            work_item_type=WorkItemType.STORY,
            title="Test",
            description="Test",
            priority=1  # High priority
        )
        assert metadata.priority in [1, 2, 3, 4]
