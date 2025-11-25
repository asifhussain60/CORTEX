"""
Unit tests for PlanningOrchestrator
Tests YAML validation, Markdown generation, and plan migration
"""

import pytest
import tempfile
import yaml
from pathlib import Path
from datetime import datetime
import sys
import os

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from orchestrators.planning_orchestrator import PlanningOrchestrator


@pytest.fixture
def temp_cortex_root(tmp_path):
    """Create temporary CORTEX directory structure."""
    cortex_root = tmp_path / "cortex"
    cortex_root.mkdir()
    
    # Create necessary directories
    (cortex_root / "cortex-brain" / "config").mkdir(parents=True)
    (cortex_root / "cortex-brain" / "documents" / "planning" / "features" / "active").mkdir(parents=True)
    (cortex_root / "cortex-brain" / "documents" / "planning" / "features" / "completed").mkdir(parents=True)
    
    # Create minimal schema
    schema = {
        "schema": {
            "version": "1.0.0",
            "required_fields": ["metadata", "phases", "definition_of_ready", "definition_of_done"]
        }
    }
    schema_path = cortex_root / "cortex-brain" / "config" / "plan-schema.yaml"
    with open(schema_path, 'w') as f:
        yaml.dump(schema, f)
    
    return cortex_root


@pytest.fixture
def orchestrator(temp_cortex_root):
    """Create PlanningOrchestrator instance."""
    return PlanningOrchestrator(str(temp_cortex_root))


@pytest.fixture
def valid_plan_data():
    """Return valid plan data for testing."""
    return {
        "metadata": {
            "plan_id": "TEST-PLAN-001",
            "title": "Test Feature Plan",
            "created_date": "2024-01-15T10:30:00Z",
            "created_by": "Test Suite",
            "status": "proposed",
            "priority": "high",
            "estimated_hours": 5
        },
        "phases": [
            {
                "phase_number": 1,
                "phase_name": "Implementation",
                "estimated_hours": "5",
                "tasks": [
                    {
                        "task_id": "1.1",
                        "task_name": "Create orchestrator",
                        "estimated_hours": 3,
                        "acceptance_criteria": [
                            "Orchestrator created",
                            "Tests passing"
                        ]
                    },
                    {
                        "task_id": "1.2",
                        "task_name": "Add documentation",
                        "estimated_hours": 2
                    }
                ]
            }
        ],
        "definition_of_ready": [
            "Requirements defined",
            "Technical approach agreed"
        ],
        "definition_of_done": [
            "All tests passing",
            "Documentation updated"
        ]
    }


class TestPlanValidation:
    """Test plan validation functionality."""
    
    def test_valid_plan_passes_validation(self, orchestrator, valid_plan_data):
        """Valid plan should pass all validation checks."""
        is_valid, errors = orchestrator.validate_plan(valid_plan_data)
        assert is_valid
        assert len(errors) == 0
    
    def test_missing_required_field_fails(self, orchestrator, valid_plan_data):
        """Plan missing required top-level field should fail."""
        del valid_plan_data["phases"]
        is_valid, errors = orchestrator.validate_plan(valid_plan_data)
        assert not is_valid
        assert any("Missing required field: phases" in e for e in errors)
    
    def test_missing_metadata_field_fails(self, orchestrator, valid_plan_data):
        """Plan missing required metadata field should fail."""
        del valid_plan_data["metadata"]["plan_id"]
        is_valid, errors = orchestrator.validate_plan(valid_plan_data)
        assert not is_valid
        assert any("plan_id" in e for e in errors)
    
    def test_invalid_plan_id_format_fails(self, orchestrator, valid_plan_data):
        """Plan ID with invalid format should fail."""
        valid_plan_data["metadata"]["plan_id"] = "invalid plan id!"
        is_valid, errors = orchestrator.validate_plan(valid_plan_data)
        assert not is_valid
        assert any("plan_id" in e and "pattern" in e for e in errors)
    
    def test_invalid_status_fails(self, orchestrator, valid_plan_data):
        """Invalid status value should fail."""
        valid_plan_data["metadata"]["status"] = "invalid-status"
        is_valid, errors = orchestrator.validate_plan(valid_plan_data)
        assert not is_valid
        assert any("status" in e for e in errors)
    
    def test_invalid_priority_fails(self, orchestrator, valid_plan_data):
        """Invalid priority value should fail."""
        valid_plan_data["metadata"]["priority"] = "super-urgent"
        is_valid, errors = orchestrator.validate_plan(valid_plan_data)
        assert not is_valid
        assert any("priority" in e for e in errors)
    
    def test_negative_hours_fails(self, orchestrator, valid_plan_data):
        """Negative estimated hours should fail."""
        valid_plan_data["metadata"]["estimated_hours"] = -5
        is_valid, errors = orchestrator.validate_plan(valid_plan_data)
        assert not is_valid
        assert any("estimated_hours" in e for e in errors)
    
    def test_duplicate_task_ids_fail(self, orchestrator, valid_plan_data):
        """Duplicate task IDs should fail validation."""
        valid_plan_data["phases"][0]["tasks"].append({
            "task_id": "1.1",  # Duplicate of first task
            "task_name": "Duplicate task",
            "estimated_hours": 1
        })
        is_valid, errors = orchestrator.validate_plan(valid_plan_data)
        assert not is_valid
        assert any("Duplicate task ID" in e for e in errors)
    
    def test_non_sequential_phases_fail(self, orchestrator, valid_plan_data):
        """Non-sequential phase numbers should fail."""
        valid_plan_data["phases"].append({
            "phase_number": 3,  # Skips 2
            "phase_name": "Phase 3",
            "estimated_hours": "2",
            "tasks": [
                {
                    "task_id": "3.1",
                    "task_name": "Task",
                    "estimated_hours": 2
                }
            ]
        })
        is_valid, errors = orchestrator.validate_plan(valid_plan_data)
        assert not is_valid
        assert any("sequential" in e.lower() for e in errors)
    
    def test_empty_definition_of_ready_fails(self, orchestrator, valid_plan_data):
        """Empty definition_of_ready should fail."""
        valid_plan_data["definition_of_ready"] = []
        is_valid, errors = orchestrator.validate_plan(valid_plan_data)
        assert not is_valid
        assert any("definition_of_ready" in e for e in errors)
    
    def test_empty_definition_of_done_fails(self, orchestrator, valid_plan_data):
        """Empty definition_of_done should fail."""
        valid_plan_data["definition_of_done"] = []
        is_valid, errors = orchestrator.validate_plan(valid_plan_data)
        assert not is_valid
        assert any("definition_of_done" in e for e in errors)


class TestMarkdownGeneration:
    """Test Markdown generation from YAML."""
    
    def test_generates_title(self, orchestrator, valid_plan_data):
        """Should generate H1 title."""
        markdown = orchestrator.generate_markdown(valid_plan_data)
        assert "# Test Feature Plan" in markdown
    
    def test_generates_metadata_table(self, orchestrator, valid_plan_data):
        """Should generate metadata table."""
        markdown = orchestrator.generate_markdown(valid_plan_data)
        assert "| **Plan ID** | `TEST-PLAN-001` |" in markdown
        assert "| **Status** | Proposed |" in markdown
        assert "| **Priority** | High |" in markdown
    
    def test_generates_definition_of_ready(self, orchestrator, valid_plan_data):
        """Should generate Definition of Ready checklist."""
        markdown = orchestrator.generate_markdown(valid_plan_data)
        assert "## Definition of Ready" in markdown
        assert "- [ ] Requirements defined" in markdown
        assert "- [ ] Technical approach agreed" in markdown
    
    def test_generates_phases(self, orchestrator, valid_plan_data):
        """Should generate phase sections."""
        markdown = orchestrator.generate_markdown(valid_plan_data)
        assert "### Phase 1: Implementation" in markdown
        assert "**Estimated Hours:** 5" in markdown
    
    def test_generates_tasks(self, orchestrator, valid_plan_data):
        """Should generate task lists."""
        markdown = orchestrator.generate_markdown(valid_plan_data)
        assert "**1.1** - Create orchestrator (3h)" in markdown
        assert "**1.2** - Add documentation (2h)" in markdown
    
    def test_generates_acceptance_criteria(self, orchestrator, valid_plan_data):
        """Should generate task acceptance criteria."""
        markdown = orchestrator.generate_markdown(valid_plan_data)
        assert "- **Acceptance Criteria:**" in markdown
        assert "- Orchestrator created" in markdown
        assert "- Tests passing" in markdown
    
    def test_generates_definition_of_done(self, orchestrator, valid_plan_data):
        """Should generate Definition of Done checklist."""
        markdown = orchestrator.generate_markdown(valid_plan_data)
        assert "## Definition of Done" in markdown
        assert "- [ ] All tests passing" in markdown
        assert "- [ ] Documentation updated" in markdown
    
    def test_generates_risks_table(self, orchestrator, valid_plan_data):
        """Should generate risks table if present."""
        valid_plan_data["risks"] = [
            {
                "risk_id": "R1",
                "description": "Test risk",
                "likelihood": "low",
                "impact": "medium",
                "mitigation": "Test mitigation"
            }
        ]
        markdown = orchestrator.generate_markdown(valid_plan_data)
        assert "## Risks & Mitigation" in markdown
        assert "| R1 | Test risk | low | medium | Test mitigation |" in markdown


class TestPlanSaving:
    """Test plan saving functionality."""
    
    def test_saves_valid_plan(self, orchestrator, valid_plan_data):
        """Should save valid plan to active directory."""
        success, message = orchestrator.save_plan(valid_plan_data)
        assert success
        assert "saved" in message.lower()
        
        # Verify file exists
        expected_path = orchestrator.active_plans_dir / "TEST-PLAN-001.yaml"
        assert expected_path.exists()
    
    def test_rejects_invalid_plan(self, orchestrator, valid_plan_data):
        """Should reject invalid plan."""
        del valid_plan_data["metadata"]["plan_id"]
        success, message = orchestrator.save_plan(valid_plan_data)
        assert not success
        assert "validation failed" in message.lower()
    
    def test_saves_completed_plan_to_completed_dir(self, orchestrator, valid_plan_data):
        """Completed plans should go to completed directory."""
        valid_plan_data["metadata"]["status"] = "completed"
        success, message = orchestrator.save_plan(valid_plan_data)
        assert success
        
        expected_path = orchestrator.completed_plans_dir / "TEST-PLAN-001.yaml"
        assert expected_path.exists()


class TestPlanLoading:
    """Test plan loading functionality."""
    
    def test_loads_valid_plan(self, orchestrator, valid_plan_data):
        """Should load and validate plan from file."""
        # Save plan first
        orchestrator.save_plan(valid_plan_data)
        plan_path = orchestrator.active_plans_dir / "TEST-PLAN-001.yaml"
        
        # Load it
        success, loaded_data, errors = orchestrator.load_plan(plan_path)
        assert success
        assert loaded_data["metadata"]["plan_id"] == "TEST-PLAN-001"
        assert len(errors) == 0
    
    def test_detects_invalid_plan(self, orchestrator, temp_cortex_root):
        """Should detect validation errors when loading."""
        # Create invalid plan file
        invalid_plan = {"metadata": {}}  # Missing required fields
        plan_path = temp_cortex_root / "invalid-plan.yaml"
        with open(plan_path, 'w') as f:
            yaml.dump(invalid_plan, f)
        
        success, loaded_data, errors = orchestrator.load_plan(plan_path)
        assert not success
        assert len(errors) > 0


class TestMarkdownMigration:
    """Test Markdown to YAML migration."""
    
    def test_migrates_simple_plan(self, orchestrator, temp_cortex_root):
        """Should migrate simple Markdown plan to YAML."""
        md_content = """# Test Plan

## Definition of Ready

- [ ] Requirements defined
- [ ] Approach agreed

## Phase 1: Implementation

- **1.1** - Create code (2h)
- **1.2** - Add tests (1h)

## Definition of Done

- [ ] All tests passing
- [ ] Code reviewed
"""
        md_path = temp_cortex_root / "test-plan.md"
        with open(md_path, 'w') as f:
            f.write(md_content)
        
        success, plan_data, message = orchestrator.migrate_markdown_plan(md_path)
        assert success
        assert plan_data["metadata"]["title"] == "Test Plan"
        assert len(plan_data["phases"]) == 1
        assert len(plan_data["phases"][0]["tasks"]) == 2
        assert len(plan_data["definition_of_ready"]) == 2
        assert len(plan_data["definition_of_done"]) == 2


class TestMarkdownViewGeneration:
    """Test Markdown view generation from YAML files."""
    
    def test_generates_markdown_view(self, orchestrator, valid_plan_data):
        """Should generate Markdown view from saved YAML."""
        # Save plan
        orchestrator.save_plan(valid_plan_data)
        plan_path = orchestrator.active_plans_dir / "TEST-PLAN-001.yaml"
        
        # Generate view
        success, message = orchestrator.generate_markdown_view(plan_path)
        assert success
        
        # Verify Markdown file exists
        md_path = orchestrator.active_plans_dir / "TEST-PLAN-001.md"
        assert md_path.exists()
        
        # Verify content
        with open(md_path, 'r') as f:
            content = f.read()
        assert "# Test Feature Plan" in content
        assert "## Definition of Ready" in content
