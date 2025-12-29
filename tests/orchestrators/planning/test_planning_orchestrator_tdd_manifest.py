"""
Test Suite: Planning Orchestrator TDD & Manifest Integration

Tests for Task 13.3:
- Part 1: TDD Workflow Methods (6 tests)
- Part 2: Manifest Inheritance Methods (5 tests)
- Part 3: Integration Tests (4 tests)

Total: 15 tests

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


@pytest.fixture
def valid_plan():
    """Create valid plan for TDD integration."""
    return {
        "metadata": {
            "name": "Test Feature",
            "objectives": ["Implement feature X", "Add tests for X"],
            "acceptance_criteria": [
                "Feature must handle edge cases",
                "API endpoints must return proper responses",
                "Database operations must be atomic"
            ],
            "technologies": ["Python", "FastAPI", "PostgreSQL"],
            "dependencies": [],
            "tdd_required": True
        },
        "phases": [
            {
                "name": "Requirements Analysis",
                "type": "planning",
                "description": "Analyze requirements",
                "status": "not_started"
            },
            {
                "name": "Architecture Design",
                "type": "design",
                "description": "Design system architecture",
                "status": "not_started"
            },
            {
                "name": "Implementation",
                "type": "development",
                "description": "Implement feature",
                "status": "not_started"
            }
        ]
    }


@pytest.fixture
def parent_manifest(temp_dir):
    """Create parent manifest file."""
    manifest = {
        "orchestrator_name": "BaseOrchestrator",
        "version": "1.0",
        "phases": [
            {"name": "Setup", "required": True},
            {"name": "Execution", "required": True}
        ],
        "quality_gates": {
            "definition_of_ready": {
                "requirements_clear": True
            }
        },
        "config": {
            "timeout": 300,
            "retry_limit": 3
        }
    }
    
    manifest_path = temp_dir / "parent-manifest.yaml"
    with open(manifest_path, "w") as f:
        yaml.safe_dump(manifest, f)
    
    return manifest_path


@pytest.fixture
def child_manifest(temp_dir, parent_manifest):
    """Create child manifest with inheritance."""
    manifest = {
        "inherits_from": "parent-manifest.yaml",
        "orchestrator_name": "ChildOrchestrator",
        "version": "2.0",
        "phases": [
            {"name": "Validation", "required": True}
        ],
        "quality_gates": {
            "definition_of_done": {
                "tests_passing": True
            }
        },
        "config": {
            "timeout": 600  # Override parent timeout
        }
    }
    
    manifest_path = temp_dir / "child-manifest.yaml"
    with open(manifest_path, "w") as f:
        yaml.safe_dump(manifest, f)
    
    return manifest_path


# ============================================================================
# Part 1: TDD Workflow Tests (6 tests)
# ============================================================================

class TestTDDWorkflow:
    """Test TDD workflow integration methods."""
    
    def test_integrate_tdd_workflow_adds_phases(self, orchestrator, valid_plan):
        """Test TDD phases are inserted after design phase."""
        result = orchestrator._integrate_tdd_workflow(valid_plan)
        
        # Check TDD phases added
        phase_names = [p["name"] for p in result["phases"]]
        assert "Test Planning" in phase_names
        assert "RED Phase - Write Failing Tests" in phase_names
        assert "GREEN Phase - Implement Code" in phase_names
        assert "REFACTOR Phase - Clean Code" in phase_names
        
        # Check metadata updated
        assert result["metadata"]["tdd_integrated"] is True
        assert result["metadata"]["tdd_required"] is True
        
        # Verify insertion after design phase
        design_idx = phase_names.index("Architecture Design")
        test_planning_idx = phase_names.index("Test Planning")
        assert test_planning_idx == design_idx + 1
    
    def test_integrate_tdd_workflow_disabled(self, orchestrator, valid_plan):
        """Test TDD integration skipped when disabled."""
        orchestrator.config["tdd_enabled"] = False
        result = orchestrator._integrate_tdd_workflow(valid_plan)
        
        # Check TDD phases NOT added
        phase_names = [p["name"] for p in result["phases"]]
        assert "Test Planning" not in phase_names
        assert "RED Phase - Write Failing Tests" not in phase_names
    
    def test_generate_test_plan_from_acceptance_criteria(self, orchestrator, valid_plan):
        """Test test plan generation from acceptance criteria."""
        test_plan = orchestrator._generate_test_plan(valid_plan)
        
        # Check test plan structure
        assert test_plan["strategy"] == "TDD (RED→GREEN→REFACTOR)"
        assert test_plan["framework"] == "pytest"
        assert "unit" in test_plan["coverage_targets"]
        assert "integration" in test_plan["coverage_targets"]
        
        # Check test cases generated
        assert len(test_plan["test_cases"]) >= 3  # 3 acceptance criteria
        
        # Check technology-specific tests
        test_names = [tc["name"] for tc in test_plan["test_cases"]]
        assert any("api" in name.lower() for name in test_names)
    
    def test_execute_red_phase(self, orchestrator, valid_plan):
        """Test RED phase execution (write failing tests)."""
        # Add test plan to metadata
        valid_plan["metadata"]["test_plan"] = orchestrator._generate_test_plan(valid_plan)
        
        result = orchestrator._execute_red_phase(valid_plan)
        
        # Check RED results
        red = result["tdd_results"]["red"]
        assert red["phase"] == "RED"
        assert red["tests_written"] > 0
        assert red["tests_failing"] == red["tests_written"]  # All should fail
        assert red["tests_passing"] == 0
        assert "validation" in red
    
    def test_execute_green_phase(self, orchestrator, valid_plan):
        """Test GREEN phase execution (pass tests)."""
        # Setup: Run RED phase first
        valid_plan["metadata"]["test_plan"] = orchestrator._generate_test_plan(valid_plan)
        valid_plan = orchestrator._execute_red_phase(valid_plan)
        
        result = orchestrator._execute_green_phase(valid_plan)
        
        # Check GREEN results
        green = result["tdd_results"]["green"]
        assert green["phase"] == "GREEN"
        assert green["pass_rate"] >= 95.0
        assert green["coverage"] >= 80.0
        assert green["tests_passing"] == green["tests_total"]
        assert green["tests_failing"] == 0
    
    def test_execute_refactor_phase(self, orchestrator, valid_plan):
        """Test REFACTOR phase execution (clean code)."""
        # Setup: Run RED and GREEN phases first
        valid_plan["metadata"]["test_plan"] = orchestrator._generate_test_plan(valid_plan)
        valid_plan = orchestrator._execute_red_phase(valid_plan)
        valid_plan = orchestrator._execute_green_phase(valid_plan)
        
        result = orchestrator._execute_refactor_phase(valid_plan)
        
        # Check REFACTOR results
        refactor = result["tdd_results"]["refactor"]
        assert refactor["phase"] == "REFACTOR"
        assert refactor["complexity_after"] <= 30
        assert refactor["complexity_after"] < refactor["complexity_before"]
        assert refactor["tests_still_passing"] is True
        assert len(refactor["refactorings_applied"]) > 0


# ============================================================================
# Part 2: Manifest Inheritance Tests (5 tests)
# ============================================================================

class TestManifestInheritance:
    """Test manifest inheritance and merging."""
    
    def test_load_manifest_with_inheritance(self, orchestrator, child_manifest):
        """Test loading manifest with inheritance chain."""
        resolved = orchestrator._load_manifest_with_inheritance(str(child_manifest))
        
        # Check merged fields
        assert resolved["orchestrator_name"] == "ChildOrchestrator"  # Child override
        assert resolved["version"] == "2.0"  # Child override
        
        # Check inherited phases (parent + child)
        phase_names = [p["name"] for p in resolved["phases"]]
        assert "Setup" in phase_names  # From parent
        assert "Execution" in phase_names  # From parent
        assert "Validation" in phase_names  # From child
        
        # Check merged quality gates
        assert "definition_of_ready" in resolved["quality_gates"]  # From parent
        assert "definition_of_done" in resolved["quality_gates"]  # From child
        
        # Check config override
        assert resolved["config"]["timeout"] == 600  # Child override
        assert resolved["config"]["retry_limit"] == 3  # Parent value
    
    def test_load_manifest_without_inheritance(self, orchestrator, parent_manifest):
        """Test loading manifest without inheritance."""
        resolved = orchestrator._load_manifest_with_inheritance(str(parent_manifest))
        
        # Should return manifest as-is
        assert resolved["orchestrator_name"] == "BaseOrchestrator"
        assert "inherits_from" not in resolved
    
    def test_merge_manifest_configs_scalar_override(self, orchestrator):
        """Test scalar values are overridden by child."""
        parent = {"name": "Parent", "version": "1.0", "timeout": 100}
        child = {"name": "Child", "timeout": 200}
        
        merged = orchestrator._merge_manifest_configs(parent, child)
        
        assert merged["name"] == "Child"  # Override
        assert merged["version"] == "1.0"  # Preserve parent
        assert merged["timeout"] == 200  # Override
    
    def test_merge_manifest_configs_list_append(self, orchestrator):
        """Test lists are appended (child extends parent)."""
        parent = {"phases": [{"name": "Phase1"}, {"name": "Phase2"}]}
        child = {"phases": [{"name": "Phase3"}]}
        
        merged = orchestrator._merge_manifest_configs(parent, child)
        
        assert len(merged["phases"]) == 3
        assert merged["phases"][0]["name"] == "Phase1"
        assert merged["phases"][2]["name"] == "Phase3"
    
    def test_merge_manifest_configs_dict_recursive(self, orchestrator):
        """Test nested dicts are merged recursively."""
        parent = {
            "config": {
                "timeout": 100,
                "retry": 3,
                "nested": {"level2": "parent"}
            }
        }
        child = {
            "config": {
                "timeout": 200,
                "nested": {"level2": "child", "new_key": "value"}
            }
        }
        
        merged = orchestrator._merge_manifest_configs(parent, child)
        
        assert merged["config"]["timeout"] == 200  # Override
        assert merged["config"]["retry"] == 3  # Preserve
        assert merged["config"]["nested"]["level2"] == "child"  # Override nested
        assert merged["config"]["nested"]["new_key"] == "value"  # New key


# ============================================================================
# Part 3: Integration Tests (4 tests)
# ============================================================================

class TestTDDManifestIntegration:
    """Test integration of TDD and manifest systems."""
    
    def test_validate_tdd_completion_success(self, orchestrator, valid_plan):
        """Test TDD validation succeeds for complete workflow."""
        # Execute full TDD cycle
        valid_plan["metadata"]["test_plan"] = orchestrator._generate_test_plan(valid_plan)
        valid_plan = orchestrator._execute_red_phase(valid_plan)
        valid_plan = orchestrator._execute_green_phase(valid_plan)
        valid_plan = orchestrator._execute_refactor_phase(valid_plan)
        
        is_complete, issues = orchestrator._validate_tdd_completion(valid_plan)
        
        assert is_complete is True
        assert len(issues) == 0
    
    def test_validate_tdd_completion_missing_phases(self, orchestrator, valid_plan):
        """Test TDD validation fails when phases missing."""
        # Only run RED phase
        valid_plan["metadata"]["test_plan"] = orchestrator._generate_test_plan(valid_plan)
        valid_plan = orchestrator._execute_red_phase(valid_plan)
        
        is_complete, issues = orchestrator._validate_tdd_completion(valid_plan)
        
        assert is_complete is False
        assert any("GREEN phase" in issue for issue in issues)
        assert any("REFACTOR phase" in issue for issue in issues)
    
    def test_validate_manifest_schema_valid(self, orchestrator):
        """Test manifest schema validation succeeds for valid manifest."""
        manifest = {
            "orchestrator_name": "TestOrchestrator",
            "version": "1.0",
            "phases": [
                {"name": "Phase1", "type": "test"}
            ],
            "quality_gates": {
                "definition_of_ready": {"requirements": True}
            }
        }
        
        is_valid, errors = orchestrator._validate_manifest_schema(manifest)
        
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_manifest_schema_invalid(self, orchestrator):
        """Test manifest schema validation fails for invalid manifest."""
        manifest = {
            "orchestrator_name": "TestOrchestrator",
            # Missing: version, phases
            "quality_gates": {
                "invalid_structure": True  # Missing DoR/DoD
            }
        }
        
        is_valid, errors = orchestrator._validate_manifest_schema(manifest)
        
        assert is_valid is False
        assert any("version" in error for error in errors)
        assert any("phases" in error for error in errors)


# ============================================================================
# Part 4: Cache Tests (Bonus - 1 test)
# ============================================================================

class TestManifestCaching:
    """Test manifest caching functionality."""
    
    def test_cache_resolved_manifest(self, orchestrator, child_manifest):
        """Test manifest caching reduces re-parsing."""
        manifest_path = str(child_manifest)
        
        # First load (not cached)
        resolved1 = orchestrator._load_manifest_with_inheritance(manifest_path)
        
        # Second load (should use cache)
        resolved2 = orchestrator._load_manifest_with_inheritance(manifest_path)
        
        # Should return same object (cached)
        assert resolved1 == resolved2
        assert manifest_path in orchestrator._manifest_cache
        assert "timestamp" in orchestrator._manifest_cache[manifest_path]
