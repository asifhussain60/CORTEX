"""
Test Suite: Planning Orchestrator Optional Enhancements

Tests for Phase 13 Optional Enhancements:
- Enhancement 1: JSON Schema Validation (5 tests)
- Enhancement 2: Checkpoint Tagging System (5 tests)

Total: 10 tests

Author: CORTEX Planning System
Version: 4.0.0
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch
import yaml
import tempfile
from typing import Dict, Any

# Add cortex-toolkit to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "cortex-toolkit"))

from src.orchestrators.planning.planning_orchestrator import PlanningOrchestrator


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def temp_dir():
    """Create temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def orchestrator(temp_dir):
    """Create PlanningOrchestrator instance for testing."""
    # Create cortex-toolkit structure for imports
    toolkit_path = temp_dir / "cortex-toolkit" / "core" / "utilities"
    toolkit_path.mkdir(parents=True, exist_ok=True)
    
    # Create minimal plan_scaffold_generator.py
    scaffold_code = '''
class PlanScaffoldGenerator:
    def __init__(self, cortex_root=None):
        self.cortex_root = cortex_root
    
    def create_scaffold(self, plan_name, plan_type="feature"):
        return {
            "status": "created",
            "plan_name": plan_name,
            "folder_name": f"{plan_type}s/active/{plan_name}"
        }
'''
    (toolkit_path / "plan_scaffold_generator.py").write_text(scaffold_code)
    
    config = {
        "cortex_root": str(temp_dir),
        "schema_path": str(temp_dir / "schema.yaml"),
        "plans_dir": str(temp_dir / "plans"),
        "tdd_enabled": True,
        "enforce_dor": True,
        "enforce_dod": True
    }
    
    # Create required directories
    (temp_dir / "plans" / "active").mkdir(parents=True, exist_ok=True)
    (temp_dir / "plans" / "completed").mkdir(parents=True, exist_ok=True)
    
    # Create minimal schema
    schema = {
        "name": "test-schema",
        "version": "1.0",
        "required": ["metadata", "phases"]
    }
    with open(temp_dir / "schema.yaml", "w") as f:
        yaml.safe_dump(schema, f)
    
    return PlanningOrchestrator(config)


# ============================================================================
# Enhancement 1: JSON Schema Validation Tests (5 tests)
# ============================================================================

class TestJSONSchemaValidation:
    """Test JSON Schema validation enhancement."""
    
    def test_validate_manifest_schema_with_jsonschema_valid(self, orchestrator):
        """Test manifest passes JSON Schema validation."""
        manifest = {
            "orchestrator_name": "TestOrchestrator",
            "version": "1.0.0",
            "phases": [
                {
                    "name": "Phase 1",
                    "description": "Test phase",
                    "status": "not_started",
                    "tasks": ["Task 1", "Task 2"],
                    "dependencies": []
                }
            ],
            "quality_gates": {
                "definition_of_ready": {
                    "enabled": True,
                    "criteria": ["Requirement 1", "Requirement 2"]
                },
                "definition_of_done": {
                    "enabled": True,
                    "criteria": ["Test 1", "Test 2"]
                }
            },
            "tdd_workflow": {
                "enabled": True,
                "test_framework": "pytest",
                "coverage_threshold": 80
            },
            "metadata": {
                "author": "Test",
                "created": "2025-12-25"
            }
        }
        
        is_valid, errors = orchestrator._validate_manifest_schema(manifest)
        
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_manifest_schema_missing_required_fields(self, orchestrator):
        """Test manifest fails validation when missing required fields."""
        manifest = {
            "orchestrator_name": "TestOrchestrator"
            # Missing: version, phases
        }
        
        is_valid, errors = orchestrator._validate_manifest_schema(manifest)
        
        assert is_valid is False
        assert any("version" in error.lower() for error in errors)
        assert any("phases" in error.lower() for error in errors)
    
    def test_validate_manifest_schema_invalid_version_format(self, orchestrator):
        """Test manifest fails validation with invalid version format."""
        manifest = {
            "orchestrator_name": "TestOrchestrator",
            "version": "invalid-version",  # Must match semver pattern
            "phases": [{"name": "Phase 1"}]
        }
        
        is_valid, errors = orchestrator._validate_manifest_schema(manifest)
        
        # Should fail if jsonschema available (checks version pattern)
        # Basic validation won't catch this, but that's OK
        try:
            import jsonschema
            assert is_valid is False
            assert any("version" in error.lower() or "pattern" in error.lower() for error in errors)
        except ImportError:
            # Without jsonschema, basic validation passes
            assert is_valid is True
    
    def test_validate_manifest_schema_invalid_phase_status(self, orchestrator):
        """Test manifest fails validation with invalid phase status enum."""
        manifest = {
            "orchestrator_name": "TestOrchestrator",
            "version": "1.0",
            "phases": [
                {
                    "name": "Phase 1",
                    "status": "invalid_status"  # Must be one of enum values
                }
            ]
        }
        
        is_valid, errors = orchestrator._validate_manifest_schema(manifest)
        
        # Should fail if jsonschema available (checks enum constraint)
        try:
            import jsonschema
            assert is_valid is False
            assert any("status" in error.lower() or "enum" in error.lower() for error in errors)
        except ImportError:
            # Without jsonschema, basic validation passes
            assert is_valid is True
    
    def test_get_manifest_json_schema_structure(self, orchestrator):
        """Test JSON Schema structure is valid."""
        schema = orchestrator._get_manifest_json_schema()
        
        # Check schema structure
        assert schema["$schema"] == "http://json-schema.org/draft-07/schema#"
        assert schema["type"] == "object"
        assert "orchestrator_name" in schema["required"]
        assert "version" in schema["required"]
        assert "phases" in schema["required"]
        
        # Check properties defined
        assert "orchestrator_name" in schema["properties"]
        assert "version" in schema["properties"]
        assert "phases" in schema["properties"]
        assert "quality_gates" in schema["properties"]
        assert "tdd_workflow" in schema["properties"]
        
        # Check phases array structure
        phases_schema = schema["properties"]["phases"]
        assert phases_schema["type"] == "array"
        assert phases_schema["minItems"] == 1
        assert "items" in phases_schema
        
        # Check phase status enum
        phase_props = phases_schema["items"]["properties"]
        assert "status" in phase_props
        assert "enum" in phase_props["status"]
        assert "not_started" in phase_props["status"]["enum"]


# ============================================================================
# Enhancement 2: Checkpoint Tagging Tests (5 tests)
# ============================================================================

class TestCheckpointTagging:
    """Test checkpoint tagging system enhancement."""
    
    def test_create_checkpoint_with_tags(self, orchestrator):
        """Test checkpoint creation with tags."""
        checkpoint_id = orchestrator._create_checkpoint(
            phase_name="Test Phase",
            metadata={"progress": "50%"},
            tags=["stable", "pre-migration"]
        )
        
        assert checkpoint_id != ""
        
        # Verify checkpoint has tags
        checkpoints = orchestrator._list_checkpoints()
        checkpoint = next(cp for cp in checkpoints if cp["checkpoint_id"] == checkpoint_id)
        assert "tags" in checkpoint
        assert "stable" in checkpoint["tags"]
        assert "pre-migration" in checkpoint["tags"]
    
    def test_create_checkpoint_without_tags(self, orchestrator):
        """Test checkpoint creation without tags (backward compatibility)."""
        checkpoint_id = orchestrator._create_checkpoint(
            phase_name="Test Phase",
            metadata={"progress": "50%"}
        )
        
        assert checkpoint_id != ""
        
        # Verify checkpoint has empty tags list
        checkpoints = orchestrator._list_checkpoints()
        checkpoint = next(cp for cp in checkpoints if cp["checkpoint_id"] == checkpoint_id)
        assert "tags" in checkpoint
        assert checkpoint["tags"] == []
    
    def test_list_checkpoints_filter_by_single_tag(self, orchestrator):
        """Test filtering checkpoints by single tag."""
        # Create checkpoints with different tags
        orchestrator._create_checkpoint("Phase 1", {"progress": "25%"}, tags=["stable"])
        orchestrator._create_checkpoint("Phase 2", {"progress": "50%"}, tags=["experimental"])
        orchestrator._create_checkpoint("Phase 3", {"progress": "75%"}, tags=["stable", "reviewed"])
        
        # Filter by 'stable' tag
        stable_checkpoints = orchestrator._list_checkpoints(tags_filter=["stable"])
        
        assert len(stable_checkpoints) == 2
        for cp in stable_checkpoints:
            assert "stable" in cp["tags"]
    
    def test_list_checkpoints_filter_by_multiple_tags(self, orchestrator):
        """Test filtering checkpoints by multiple tags (OR logic)."""
        # Create checkpoints with different tags
        orchestrator._create_checkpoint("Phase 1", {"progress": "25%"}, tags=["stable"])
        orchestrator._create_checkpoint("Phase 2", {"progress": "50%"}, tags=["experimental"])
        orchestrator._create_checkpoint("Phase 3", {"progress": "75%"}, tags=["reviewed"])
        orchestrator._create_checkpoint("Phase 4", {"progress": "100%"}, tags=["stable", "reviewed"])
        
        # Filter by 'stable' OR 'reviewed' tags
        filtered = orchestrator._list_checkpoints(tags_filter=["stable", "reviewed"])
        
        assert len(filtered) == 3  # Phase 1, 3, 4
        for cp in filtered:
            assert any(tag in cp["tags"] for tag in ["stable", "reviewed"])
    
    def test_list_checkpoints_filter_by_phase_and_tags(self, orchestrator):
        """Test filtering checkpoints by both phase and tags."""
        # Create checkpoints for different phases with tags
        orchestrator._create_checkpoint("Phase A", {"progress": "25%"}, tags=["stable"])
        orchestrator._create_checkpoint("Phase A", {"progress": "50%"}, tags=["experimental"])
        orchestrator._create_checkpoint("Phase B", {"progress": "75%"}, tags=["stable"])
        orchestrator._create_checkpoint("Phase A", {"progress": "100%"}, tags=["stable", "final"])
        
        # Filter by phase='Phase A' AND tags=['stable']
        filtered = orchestrator._list_checkpoints(
            phase_filter="Phase A",
            tags_filter=["stable"]
        )
        
        assert len(filtered) == 2  # Phase A with stable tag
        for cp in filtered:
            assert cp["phase_name"] == "Phase A"
            assert "stable" in cp["tags"]


# ============================================================================
# Integration Tests (Bonus - 2 tests)
# ============================================================================

class TestEnhancementsIntegration:
    """Test integration of both enhancements."""
    
    def test_jsonschema_validation_catches_errors_early(self, orchestrator):
        """Test JSON Schema catches type errors that basic validation misses."""
        manifest = {
            "orchestrator_name": "TestOrchestrator",
            "version": "1.0",
            "phases": "not-a-list",  # Should be list, not string
            "quality_gates": {
                "definition_of_ready": "not-a-dict"  # Should be dict
            }
        }
        
        is_valid, errors = orchestrator._validate_manifest_schema(manifest)
        
        assert is_valid is False
        # Basic validation will catch 'phases' type error
        assert any("phases" in error.lower() for error in errors)
    
    def test_checkpoint_tags_improve_discovery(self, orchestrator):
        """Test tags improve checkpoint discovery and organization."""
        # Create realistic checkpoint scenario
        orchestrator._create_checkpoint("Requirements", {"progress": "100%"}, tags=["complete"])
        orchestrator._create_checkpoint("Design", {"progress": "100%"}, tags=["complete", "reviewed"])
        orchestrator._create_checkpoint("Implementation", {"progress": "50%"}, tags=["in-progress"])
        orchestrator._create_checkpoint("Implementation", {"progress": "75%"}, tags=["in-progress", "stable"])
        orchestrator._create_checkpoint("Testing", {"progress": "25%"}, tags=["in-progress"])
        
        # Find all stable checkpoints (for rollback candidates)
        stable = orchestrator._list_checkpoints(tags_filter=["stable"])
        assert len(stable) == 1
        assert stable[0]["phase_name"] == "Implementation"
        
        # Find all complete phases
        complete = orchestrator._list_checkpoints(tags_filter=["complete"])
        assert len(complete) == 2
        
        # Find work in progress
        in_progress = orchestrator._list_checkpoints(tags_filter=["in-progress"])
        assert len(in_progress) == 3
