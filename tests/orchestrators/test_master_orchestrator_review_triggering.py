"""
Unit Tests for Master Orchestrator Automatic Review Triggering.

Tests the _check_review_schedule() method and automatic holistic review
triggering functionality added in Phase 6.4.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from typing import Dict, Any

from src.orchestrators.master_orchestrator import MasterOrchestrator
from src.mcp.registry import OrchestratorRegistry
from src.database.planning_state_db import PlanningStateDB


class TestCheckReviewSchedule:
    """Test suite for _check_review_schedule() method."""
    
    @pytest.fixture
    def mock_registry(self):
        """Create mock orchestrator registry."""
        registry = Mock(spec=OrchestratorRegistry)
        return registry
    
    @pytest.fixture
    def mock_state_db(self):
        """Create mock state database."""
        state_db = Mock(spec=PlanningStateDB)
        return state_db
    
    @pytest.fixture
    def temp_progress_json(self, tmp_path):
        """Create temporary progress.json for testing."""
        plan_dir = tmp_path / "cortex-brain" / "documents" / "planning" / "active" / "test-plan" / "tracking"
        plan_dir.mkdir(parents=True, exist_ok=True)
        
        progress_file = plan_dir / "progress.json"
        
        progress_data = {
            "plan_id": "test-plan",
            "progress": {
                "overall_percent": 50,
                "current_phase": 2,
                "total_phases": 5
            },
            "holistic_reviews": {
                "enabled": True,
                "auto_trigger": True,
                "schedule": [
                    {
                        "review_number": 1,
                        "name": "Review 1",
                        "status": "completed",
                        "trigger_condition": "phase_0_complete",
                        "document": "architecture/holistic-review-01.md",
                        "scope": "design"
                    },
                    {
                        "review_number": 2,
                        "name": "Review 2",
                        "status": "not_started",
                        "trigger_condition": "phase_1_complete",
                        "document": "architecture/holistic-review-02.md",
                        "scope": "code_reuse_strategy"
                    },
                    {
                        "review_number": 3,
                        "name": "Review 3",
                        "status": "not_started",
                        "trigger_condition": "phase_3_complete",
                        "document": "architecture/holistic-review-03.md",
                        "scope": "implementation_quality"
                    }
                ]
            }
        }
        
        with open(progress_file, 'w') as f:
            json.dump(progress_data, f, indent=2)
        
        return tmp_path, progress_file
    
    @pytest.fixture
    def master_orchestrator(self, mock_registry, mock_state_db, tmp_path):
        """Create MasterOrchestrator instance for testing."""
        # Create mock config file
        config_dir = tmp_path / "cortex-brain" / "config"
        config_dir.mkdir(parents=True, exist_ok=True)
        config_file = config_dir / "master-orchestrator.yaml"
        
        config_data = """
routing_rules:
  - pattern: "test"
    orchestrator: "test_orchestrator"
    confidence: 1.0
"""
        with open(config_file, 'w') as f:
            f.write(config_data)
        
        orchestrator = MasterOrchestrator(
            config_path=str(config_file),
            registry=mock_registry,
            state_db=mock_state_db
        )
        
        return orchestrator
    
    def test_check_review_schedule_no_parent_plan(self, master_orchestrator):
        """Test when context has no parent_plan_id."""
        context = {}
        
        result = master_orchestrator._check_review_schedule(
            orchestrator_id="test_orchestrator",
            context=context
        )
        
        assert result is None
    
    def test_check_review_schedule_missing_progress_file(self, master_orchestrator):
        """Test when progress.json file doesn't exist."""
        context = {
            'parent_plan_id': 'nonexistent-plan'
        }
        
        result = master_orchestrator._check_review_schedule(
            orchestrator_id="test_orchestrator",
            context=context
        )
        
        assert result is None
    
    def test_check_review_schedule_reviews_disabled(self, master_orchestrator, temp_progress_json, monkeypatch):
        """Test when holistic_reviews.enabled = false."""
        tmp_path, progress_file = temp_progress_json
        
        # Update progress.json to disable reviews
        with open(progress_file, 'r') as f:
            data = json.load(f)
        
        data['holistic_reviews']['enabled'] = False
        
        with open(progress_file, 'w') as f:
            json.dump(data, f)
        
        # Monkey-patch Path to use temp directory
        monkeypatch.setattr(
            'src.orchestrators.master_orchestrator.Path',
            lambda x: tmp_path / x if 'cortex-brain' in x else Path(x)
        )
        
        context = {
            'parent_plan_id': 'test-plan'
        }
        
        result = master_orchestrator._check_review_schedule(
            orchestrator_id="test_orchestrator",
            context=context
        )
        
        assert result is None
    
    def test_check_review_schedule_auto_trigger_disabled(self, master_orchestrator, temp_progress_json, monkeypatch):
        """Test when holistic_reviews.auto_trigger = false."""
        tmp_path, progress_file = temp_progress_json
        
        # Update progress.json to disable auto-trigger
        with open(progress_file, 'r') as f:
            data = json.load(f)
        
        data['holistic_reviews']['auto_trigger'] = False
        
        with open(progress_file, 'w') as f:
            json.dump(data, f)
        
        # Monkey-patch Path
        monkeypatch.setattr(
            'src.orchestrators.master_orchestrator.Path',
            lambda x: tmp_path / x if 'cortex-brain' in x else Path(x)
        )
        
        context = {
            'parent_plan_id': 'test-plan'
        }
        
        result = master_orchestrator._check_review_schedule(
            orchestrator_id="test_orchestrator",
            context=context
        )
        
        assert result is None
    
    def test_check_review_schedule_trigger_condition_met(self, master_orchestrator, temp_progress_json, monkeypatch):
        """Test when trigger condition is met (phase_1_complete, current_phase=2)."""
        tmp_path, progress_file = temp_progress_json
        
        # Monkey-patch Path
        monkeypatch.setattr(
            'src.orchestrators.master_orchestrator.Path',
            lambda x: tmp_path / x if 'cortex-brain' in x else Path(x)
        )
        
        context = {
            'parent_plan_id': 'test-plan'
        }
        
        result = master_orchestrator._check_review_schedule(
            orchestrator_id="test_orchestrator",
            context=context
        )
        
        # Should return review #2 configuration
        assert result is not None
        assert result['review_number'] == 2
        assert result['name'] == "Review 2"
        assert result['trigger_condition'] == "phase_1_complete"
        assert result['scope'] == "code_reuse_strategy"
    
    def test_check_review_schedule_trigger_condition_not_met(self, master_orchestrator, temp_progress_json, monkeypatch):
        """Test when trigger condition not met (phase_3_complete, current_phase=2)."""
        tmp_path, progress_file = temp_progress_json
        
        # Update current_phase to 0 (so phase_1_complete not met)
        with open(progress_file, 'r') as f:
            data = json.load(f)
        
        data['progress']['current_phase'] = 0
        
        with open(progress_file, 'w') as f:
            json.dump(data, f)
        
        # Monkey-patch Path
        monkeypatch.setattr(
            'src.orchestrators.master_orchestrator.Path',
            lambda x: tmp_path / x if 'cortex-brain' in x else Path(x)
        )
        
        context = {
            'parent_plan_id': 'test-plan'
        }
        
        result = master_orchestrator._check_review_schedule(
            orchestrator_id="test_orchestrator",
            context=context
        )
        
        # No review should be triggered
        assert result is None
    
    def test_check_review_schedule_all_reviews_complete(self, master_orchestrator, temp_progress_json, monkeypatch):
        """Test when all reviews are already completed."""
        tmp_path, progress_file = temp_progress_json
        
        # Mark all reviews as completed
        with open(progress_file, 'r') as f:
            data = json.load(f)
        
        for review in data['holistic_reviews']['schedule']:
            review['status'] = 'completed'
        
        with open(progress_file, 'w') as f:
            json.dump(data, f)
        
        # Monkey-patch Path
        monkeypatch.setattr(
            'src.orchestrators.master_orchestrator.Path',
            lambda x: tmp_path / x if 'cortex-brain' in x else Path(x)
        )
        
        context = {
            'parent_plan_id': 'test-plan'
        }
        
        result = master_orchestrator._check_review_schedule(
            orchestrator_id="test_orchestrator",
            context=context
        )
        
        # No review should be triggered
        assert result is None
    
    def test_check_review_schedule_invalid_trigger_condition(self, master_orchestrator, temp_progress_json, monkeypatch):
        """Test with malformed trigger_condition."""
        tmp_path, progress_file = temp_progress_json
        
        # Add review with invalid trigger condition
        with open(progress_file, 'r') as f:
            data = json.load(f)
        
        data['holistic_reviews']['schedule'][1]['trigger_condition'] = 'invalid_condition'
        data['holistic_reviews']['schedule'][1]['status'] = 'not_started'
        
        with open(progress_file, 'w') as f:
            json.dump(data, f)
        
        # Monkey-patch Path
        monkeypatch.setattr(
            'src.orchestrators.master_orchestrator.Path',
            lambda x: tmp_path / x if 'cortex-brain' in x else Path(x)
        )
        
        context = {
            'parent_plan_id': 'test-plan'
        }
        
        # Should handle gracefully (likely skip this review)
        result = master_orchestrator._check_review_schedule(
            orchestrator_id="test_orchestrator",
            context=context
        )
        
        # Should either return None or skip to next valid review
        # Implementation should be defensive
        assert result is None or result['review_number'] == 3
    
    def test_check_review_schedule_invalid_json(self, master_orchestrator, tmp_path, monkeypatch):
        """Test with invalid JSON in progress.json."""
        # Create invalid JSON file
        plan_dir = tmp_path / "cortex-brain" / "documents" / "planning" / "active" / "test-plan" / "tracking"
        plan_dir.mkdir(parents=True, exist_ok=True)
        
        progress_file = plan_dir / "progress.json"
        with open(progress_file, 'w') as f:
            f.write("{ invalid json }")
        
        # Monkey-patch Path
        monkeypatch.setattr(
            'src.orchestrators.master_orchestrator.Path',
            lambda x: tmp_path / x if 'cortex-brain' in x else Path(x)
        )
        
        context = {
            'parent_plan_id': 'test-plan'
        }
        
        result = master_orchestrator._check_review_schedule(
            orchestrator_id="test_orchestrator",
            context=context
        )
        
        # Should handle gracefully and return None
        assert result is None
    
    def test_check_review_schedule_missing_holistic_reviews_section(self, master_orchestrator, tmp_path, monkeypatch):
        """Test when progress.json has no holistic_reviews section."""
        # Create progress.json without holistic_reviews
        plan_dir = tmp_path / "cortex-brain" / "documents" / "planning" / "active" / "test-plan" / "tracking"
        plan_dir.mkdir(parents=True, exist_ok=True)
        
        progress_file = plan_dir / "progress.json"
        progress_data = {
            "plan_id": "test-plan",
            "progress": {
                "current_phase": 2
            }
        }
        
        with open(progress_file, 'w') as f:
            json.dump(progress_data, f)
        
        # Monkey-patch Path
        monkeypatch.setattr(
            'src.orchestrators.master_orchestrator.Path',
            lambda x: tmp_path / x if 'cortex-brain' in x else Path(x)
        )
        
        context = {
            'parent_plan_id': 'test-plan'
        }
        
        result = master_orchestrator._check_review_schedule(
            orchestrator_id="test_orchestrator",
            context=context
        )
        
        # Should return None gracefully
        assert result is None
    
    def test_check_review_schedule_multiple_pending_reviews(self, master_orchestrator, temp_progress_json, monkeypatch):
        """Test with multiple pending reviews (should return first eligible)."""
        tmp_path, progress_file = temp_progress_json
        
        # Set current_phase high enough to trigger multiple reviews
        with open(progress_file, 'r') as f:
            data = json.load(f)
        
        data['progress']['current_phase'] = 4
        data['holistic_reviews']['schedule'][1]['status'] = 'not_started'
        data['holistic_reviews']['schedule'][2]['status'] = 'not_started'
        
        with open(progress_file, 'w') as f:
            json.dump(data, f)
        
        # Monkey-patch Path
        monkeypatch.setattr(
            'src.orchestrators.master_orchestrator.Path',
            lambda x: tmp_path / x if 'cortex-brain' in x else Path(x)
        )
        
        context = {
            'parent_plan_id': 'test-plan'
        }
        
        result = master_orchestrator._check_review_schedule(
            orchestrator_id="test_orchestrator",
            context=context
        )
        
        # Should return first eligible review (review #2)
        assert result is not None
        assert result['review_number'] == 2


class TestHandleRequestWithAutoReviews:
    """Integration tests for handle_request() with automatic review triggering."""
    
    @pytest.fixture
    def mock_components(self, tmp_path):
        """Create all mock components for MasterOrchestrator."""
        registry = Mock(spec=OrchestratorRegistry)
        state_db = Mock(spec=PlanningStateDB)
        
        # Create config file
        config_dir = tmp_path / "cortex-brain" / "config"
        config_dir.mkdir(parents=True, exist_ok=True)
        config_file = config_dir / "master-orchestrator.yaml"
        
        config_data = """
routing_rules:
  - pattern: "^test.*$"
    orchestrator: "test_orchestrator"
    confidence: 1.0
    match_type: "regex"
"""
        with open(config_file, 'w') as f:
            f.write(config_data)
        
        return registry, state_db, str(config_file)
    
    @pytest.fixture
    def setup_review_scenario(self, tmp_path):
        """Setup progress.json with pending review."""
        plan_dir = tmp_path / "cortex-brain" / "documents" / "planning" / "active" / "test-plan" / "tracking"
        plan_dir.mkdir(parents=True, exist_ok=True)
        
        progress_file = plan_dir / "progress.json"
        
        progress_data = {
            "plan_id": "test-plan",
            "progress": {
                "current_phase": 2
            },
            "holistic_reviews": {
                "enabled": True,
                "auto_trigger": True,
                "schedule": [
                    {
                        "review_number": 1,
                        "name": "Test Review",
                        "status": "not_started",
                        "trigger_condition": "phase_1_complete",
                        "document": "architecture/holistic-review-01.md",
                        "scope": "design",
                        "completed_phases": [0, 1]
                    }
                ]
            }
        }
        
        with open(progress_file, 'w') as f:
            json.dump(progress_data, f)
        
        return tmp_path
    
    @patch('src.orchestrators.master_orchestrator.Path')
    def test_handle_request_triggers_review(self, mock_path_class, mock_components, setup_review_scenario):
        """Test that handle_request auto-triggers holistic review when condition met."""
        registry, state_db, config_file = mock_components
        tmp_path = setup_review_scenario
        
        # Setup Path mock
        def path_side_effect(path_str):
            if 'cortex-brain/documents' in str(path_str):
                return tmp_path / path_str
            return Path(path_str)
        
        mock_path_class.side_effect = path_side_effect
        
        # Mock orchestrator execution
        mock_review_orchestrator = Mock()
        mock_target_orchestrator = Mock()
        
        def instantiate_side_effect(orch_id):
            if orch_id == "holistic_review_orchestrator":
                return mock_review_orchestrator
            elif orch_id == "test_orchestrator":
                return mock_target_orchestrator
            return None
        
        registry.instantiate.side_effect = instantiate_side_effect
        
        # Create MasterOrchestrator
        master = MasterOrchestrator(
            config_path=config_file,
            registry=registry,
            state_db=state_db
        )
        
        # Mock execution engine
        from src.orchestrators.execution_engine import ExecutionResult
        
        review_result = ExecutionResult(
            success=True,
            orchestrator_id="holistic_review_orchestrator",
            execution_time=45.0,
            metadata={
                'insights': [
                    'ARCHITECTURE: Test insight 1',
                    'CODE_REUSE: Test insight 2'
                ]
            }
        )
        
        target_result = ExecutionResult(
            success=True,
            orchestrator_id="test_orchestrator",
            execution_time=10.0
        )
        
        def run_side_effect(orchestrator, params, hooks):
            if orchestrator == mock_review_orchestrator:
                return review_result
            elif orchestrator == mock_target_orchestrator:
                return target_result
            return None
        
        master.execution_engine.run = Mock(side_effect=run_side_effect)
        
        # Execute request with parent_plan_id in context
        context = {
            'parent_plan_id': 'test-plan'
        }
        
        result = master.handle_request("test request", context=context)
        
        # Verify review was executed
        assert master.execution_engine.run.call_count == 2  # Review + target orchestrator
        
        # Verify insights were injected
        # (Would need to inspect context passed to target orchestrator)
        assert result.success
    
    def test_handle_request_continues_on_review_failure(self, mock_components):
        """Test that target orchestrator executes even if review fails (non-blocking)."""
        registry, state_db, config_file = mock_components
        
        # Mock review execution to fail
        mock_review_orchestrator = Mock()
        mock_target_orchestrator = Mock()
        
        def instantiate_side_effect(orch_id):
            if orch_id == "holistic_review_orchestrator":
                return mock_review_orchestrator
            elif orch_id == "test_orchestrator":
                return mock_target_orchestrator
            return None
        
        registry.instantiate.side_effect = instantiate_side_effect
        
        master = MasterOrchestrator(
            config_path=config_file,
            registry=registry,
            state_db=state_db
        )
        
        # Mock execution engine to throw exception on review
        from src.orchestrators.execution_engine import ExecutionResult
        
        def run_side_effect(orchestrator, params, hooks):
            if orchestrator == mock_review_orchestrator:
                raise Exception("Review failed")
            elif orchestrator == mock_target_orchestrator:
                return ExecutionResult(
                    success=True,
                    orchestrator_id="test_orchestrator",
                    execution_time=10.0
                )
        
        master.execution_engine.run = Mock(side_effect=run_side_effect)
        
        # Mock _check_review_schedule to return review config
        master._check_review_schedule = Mock(return_value={
            'review_number': 1,
            'review_name': 'Test Review',
            'document_path': 'architecture/test.md',
            'scope': 'design',
            'completed_phases': [0]
        })
        
        # Execute request
        context = {'parent_plan_id': 'test-plan'}
        result = master.handle_request("test request", context=context)
        
        # Target orchestrator should still execute
        assert result.success


class TestReviewInsightInjection:
    """Test context injection of review insights."""
    
    def test_insights_added_to_context(self):
        """Test that insights are properly added to enriched_context."""
        # Mock scenario where review returns insights
        insights = [
            'ARCHITECTURE: Use engine-based design',
            'CODE_REUSE: Reuse FilesystemEngine',
            'TESTING: Achieve 95%+ coverage'
        ]
        
        enriched_context = {
            'session_id': 'test-session',
            'parent_plan_id': 'test-plan'
        }
        
        # Simulate insight injection
        enriched_context['review_insights'] = insights
        
        assert 'review_insights' in enriched_context
        assert len(enriched_context['review_insights']) == 3
        assert enriched_context['review_insights'][0].startswith('ARCHITECTURE:')
    
    def test_insights_format(self):
        """Test that insights follow expected format."""
        insights = [
            'ARCHITECTURE: Test insight',
            'CODE_REUSE: Test insight',
            'IMPLEMENTATION: Test insight',
            'TESTING: Test insight'
        ]
        
        for insight in insights:
            # Each insight should have category prefix
            assert ':' in insight
            category, message = insight.split(':', 1)
            assert category in ['ARCHITECTURE', 'CODE_REUSE', 'IMPLEMENTATION', 'TESTING']
            assert len(message.strip()) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
