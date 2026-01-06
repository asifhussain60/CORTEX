"""
TDD Tests for Planning Orchestrator Logging Enhancements
RED Phase: Define expected logging behavior
"""

import pytest
import logging
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from src.orchestrators.planning_orchestrator import PlanningOrchestrator


@pytest.fixture
def mock_cortex_root(tmp_path):
    """Create mock CORTEX root structure."""
    cortex_root = tmp_path / "CORTEX"
    cortex_root.mkdir()
    
    # Create necessary directories
    brain_path = cortex_root / "cortex-brain"
    brain_path.mkdir()
    
    config_path = brain_path / "config"
    config_path.mkdir()
    
    plans_path = brain_path / "documents" / "planning" / "features"
    plans_path.mkdir(parents=True)
    
    return cortex_root


@pytest.fixture
def orchestrator(mock_cortex_root):
    """Create PlanningOrchestrator instance with mocked dependencies."""
    with patch('src.orchestrators.planning_orchestrator.DocumentOrganizer'), \
         patch('src.orchestrators.planning_orchestrator.IncrementalPlanGenerator'), \
         patch('src.orchestrators.planning_orchestrator.GitCheckpointOrchestrator'), \
         patch('src.orchestrators.planning_orchestrator.ThreatModelerAgent'):
        return PlanningOrchestrator(str(mock_cortex_root))


class TestPlanningOrchestratorLogging:
    """Test comprehensive logging in PlanningOrchestrator."""
    
    def test_init_logs_configuration(self, caplog, mock_cortex_root):
        """Test that __init__ logs configuration details."""
        with caplog.at_level(logging.DEBUG):
            with patch('src.orchestrators.planning_orchestrator.DocumentOrganizer'), \
                 patch('src.orchestrators.planning_orchestrator.IncrementalPlanGenerator'), \
                 patch('src.orchestrators.planning_orchestrator.GitCheckpointOrchestrator'), \
                 patch('src.orchestrators.planning_orchestrator.ThreatModelerAgent'):
                orch = PlanningOrchestrator(str(mock_cortex_root))
        
        # Should log initialization details
        assert any("Initializing PlanningOrchestrator" in rec.message for rec in caplog.records)
        assert any("cortex_root" in rec.message for rec in caplog.records)
        assert any("schema_path" in rec.message for rec in caplog.records)
    
    def test_load_schema_logs_success(self, caplog, mock_cortex_root):
        """Test that _load_schema logs successful load."""
        schema_path = mock_cortex_root / "cortex-brain" / "config" / "plan-schema.yaml"
        schema_path.write_text("schema:\n  version: '1.0.0'\n")
        
        with caplog.at_level(logging.INFO):
            with patch('src.orchestrators.planning_orchestrator.DocumentOrganizer'), \
                 patch('src.orchestrators.planning_orchestrator.IncrementalPlanGenerator'), \
                 patch('src.orchestrators.planning_orchestrator.GitCheckpointOrchestrator'), \
                 patch('src.orchestrators.planning_orchestrator.ThreatModelerAgent'):
                orch = PlanningOrchestrator(str(mock_cortex_root))
        
        assert any("Schema loaded successfully" in rec.message for rec in caplog.records)
        assert any("plan-schema.yaml" in rec.message for rec in caplog.records)
    
    def test_load_schema_logs_file_not_found(self, caplog, mock_cortex_root):
        """Test that _load_schema logs when schema file is missing."""
        with caplog.at_level(logging.WARNING):
            with patch('src.orchestrators.planning_orchestrator.DocumentOrganizer'), \
                 patch('src.orchestrators.planning_orchestrator.IncrementalPlanGenerator'), \
                 patch('src.orchestrators.planning_orchestrator.GitCheckpointOrchestrator'), \
                 patch('src.orchestrators.planning_orchestrator.ThreatModelerAgent'):
                orch = PlanningOrchestrator(str(mock_cortex_root))
        
        assert any("Schema not found" in rec.message for rec in caplog.records)
        assert any("using minimal defaults" in rec.message for rec in caplog.records)
    
    def test_validate_plan_logs_validation_start(self, caplog, orchestrator):
        """Test that validate_plan logs validation start."""
        plan_data = {
            "metadata": {"plan_id": "TEST-001", "title": "Test", "created_date": "2024-01-01T00:00:00Z", 
                        "created_by": "test", "status": "proposed", "priority": "medium", "estimated_hours": 10},
            "phases": [],
            "definition_of_ready": ["item1"],
            "definition_of_done": ["item1"]
        }
        
        with caplog.at_level(logging.DEBUG):
            orchestrator.validate_plan(plan_data)
        
        assert any("Starting plan validation" in rec.message for rec in caplog.records)
        assert any("plan_id: TEST-001" in rec.message for rec in caplog.records)
    
    def test_validate_plan_logs_validation_errors(self, caplog, orchestrator):
        """Test that validate_plan logs validation errors."""
        plan_data = {"metadata": {}}  # Missing required fields
        
        with caplog.at_level(logging.WARNING):
            is_valid, errors = orchestrator.validate_plan(plan_data)
        
        assert not is_valid
        assert any("Plan validation failed" in rec.message for rec in caplog.records)
        assert any("error" in rec.message.lower() for rec in caplog.records)
    
    def test_validate_plan_logs_validation_success(self, caplog, orchestrator):
        """Test that validate_plan logs successful validation."""
        plan_data = {
            "metadata": {
                "plan_id": "TEST-001",
                "title": "Test Plan",
                "created_date": "2024-01-01T00:00:00Z",
                "created_by": "test",
                "status": "proposed",
                "priority": "medium",
                "estimated_hours": 10
            },
            "phases": [
                {
                    "phase_number": 1,
                    "phase_name": "Phase 1",
                    "estimated_hours": 5,
                    "tasks": [
                        {
                            "task_id": "1.1",
                            "task_name": "Task 1",
                            "estimated_hours": 5
                        }
                    ]
                }
            ],
            "definition_of_ready": ["item1"],
            "definition_of_done": ["item1"]
        }
        
        with caplog.at_level(logging.INFO):
            is_valid, errors = orchestrator.validate_plan(plan_data)
        
        assert is_valid
        assert any("Plan validation successful" in rec.message for rec in caplog.records)
    
    def test_validate_metadata_logs_field_errors(self, caplog, orchestrator):
        """Test that _validate_metadata logs specific field errors."""
        metadata = {"plan_id": "invalid id with spaces"}
        
        with caplog.at_level(logging.DEBUG):
            errors = orchestrator._validate_metadata(metadata)
        
        assert len(errors) > 0
        assert any("Validating metadata" in rec.message for rec in caplog.records)
    
    def test_validate_phases_logs_duplicate_task_ids(self, caplog, orchestrator):
        """Test that _validate_phases logs duplicate task ID errors."""
        phases = [
            {
                "phase_number": 1,
                "phase_name": "Phase 1",
                "estimated_hours": 10,
                "tasks": [
                    {"task_id": "1.1", "task_name": "Task 1", "estimated_hours": 5},
                    {"task_id": "1.1", "task_name": "Task 2", "estimated_hours": 5}  # Duplicate
                ]
            }
        ]
        
        with caplog.at_level(logging.DEBUG):
            errors = orchestrator._validate_phases(phases)
        
        assert any("Duplicate task ID" in str(e) for e in errors)
        assert any("Validating" in rec.message and "phases" in rec.message for rec in caplog.records)
    
    def test_generate_markdown_logs_generation_start(self, caplog, orchestrator):
        """Test that generate_markdown logs generation start."""
        plan_data = {
            "metadata": {"title": "Test Plan", "plan_id": "TEST-001"},
            "phases": []
        }
        
        with caplog.at_level(logging.INFO):
            markdown = orchestrator.generate_markdown(plan_data)
        
        assert any("Generating Markdown" in rec.message for rec in caplog.records)
        assert any("TEST-001" in rec.message for rec in caplog.records)
    
    def test_generate_markdown_logs_missing_sections(self, caplog, orchestrator):
        """Test that generate_markdown logs warnings for missing sections."""
        plan_data = {"metadata": {"title": "Test Plan"}}
        
        with caplog.at_level(logging.WARNING):
            markdown = orchestrator.generate_markdown(plan_data)
        
        # Should warn about missing recommended sections
        assert any("Missing" in rec.message or "not found" in rec.message for rec in caplog.records)
    
    def test_error_handling_logs_exceptions(self, caplog, orchestrator):
        """Test that exceptions are logged with full context."""
        with caplog.at_level(logging.ERROR):
            with patch.object(orchestrator, '_validate_metadata', side_effect=Exception("Test error")):
                try:
                    orchestrator.validate_plan({"metadata": {}})
                except:
                    pass
        
        assert any("Exception" in rec.message or "Error" in rec.message for rec in caplog.records)


class TestLoggingLevels:
    """Test appropriate logging levels for different scenarios."""
    
    def test_debug_level_for_detailed_operations(self, caplog, orchestrator):
        """Test DEBUG level for detailed operation tracking."""
        with caplog.at_level(logging.DEBUG):
            plan_data = {"metadata": {"plan_id": "TEST"}}
            orchestrator._validate_metadata(plan_data["metadata"])
        
        debug_logs = [rec for rec in caplog.records if rec.levelno == logging.DEBUG]
        assert len(debug_logs) > 0
    
    def test_info_level_for_major_operations(self, caplog, orchestrator):
        """Test INFO level for major operation milestones."""
        plan_data = {
            "metadata": {"plan_id": "TEST", "title": "Test", "created_date": "2024-01-01T00:00:00Z",
                        "created_by": "test", "status": "proposed", "priority": "medium", "estimated_hours": 10},
            "phases": [],
            "definition_of_ready": ["x"],
            "definition_of_done": ["x"]
        }
        
        with caplog.at_level(logging.INFO):
            orchestrator.validate_plan(plan_data)
        
        info_logs = [rec for rec in caplog.records if rec.levelno == logging.INFO]
        assert len(info_logs) > 0
    
    def test_warning_level_for_recoverable_issues(self, caplog, orchestrator):
        """Test WARNING level for recoverable issues."""
        with caplog.at_level(logging.WARNING):
            orchestrator._validate_metadata({})
        
        # Should have warnings for missing required fields
        # The validation will complete but return errors
    
    def test_error_level_for_critical_failures(self, caplog, mock_cortex_root):
        """Test ERROR level for critical failures."""
        with caplog.at_level(logging.ERROR):
            with patch('yaml.safe_load', side_effect=Exception("Parse error")):
                schema_path = mock_cortex_root / "cortex-brain" / "config" / "plan-schema.yaml"
                schema_path.write_text("invalid: yaml: content:")
                
                with patch('src.orchestrators.planning_orchestrator.DocumentOrganizer'), \
                     patch('src.orchestrators.planning_orchestrator.IncrementalPlanGenerator'), \
                     patch('src.orchestrators.planning_orchestrator.GitCheckpointOrchestrator'), \
                     patch('src.orchestrators.planning_orchestrator.ThreatModelerAgent'):
                    orch = PlanningOrchestrator(str(mock_cortex_root))
        
        error_logs = [rec for rec in caplog.records if rec.levelno == logging.ERROR]
        assert len(error_logs) > 0
