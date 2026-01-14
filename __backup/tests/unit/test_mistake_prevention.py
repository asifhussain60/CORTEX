"""
Tests for User Mistake Prevention Rules.

Tests the MistakePreventionEngine that enforces:
- Block direct orchestrator creation
- Prevent duplicate orchestrators
- Validate orchestrator hierarchy
- Enforce YAML-first design

Author: CORTEX feat04-core-orchestration Phase 1 Task 1.2
Created: 2026-01-08
"""

import pytest
from pathlib import Path
from typing import Dict, Any, List
from dataclasses import dataclass

# Import the classes we're going to implement
from src.orchestrators.middleware.mistake_prevention import (
    MistakePreventionEngine,
    PreventionRule,
    PreventionResult,
    OrchestrationIntent,
    MistakeType
)


@dataclass
class MockOrchestrator:
    """Mock orchestrator for testing."""
    id: str
    name: str
    patterns: List[str]
    capabilities: List[str]
    parent_id: str = None
    manifest_path: str = None


class TestMistakePreventionEngine:
    """Test suite for MistakePreventionEngine."""
    
    @pytest.fixture
    def rules_path(self, tmp_path: Path) -> Path:
        """Create temporary prevention rules config."""
        config = tmp_path / "prevention-rules.yaml"
        config.write_text("""
rules:
  - id: MPR-001
    name: "Block Direct Orchestrator Creation"
    mistake_type: direct_creation
    severity: blocked
    enabled: true
    message: "Direct orchestrator creation is blocked. Use MasterOrchestrator."
    
  - id: MPR-002
    name: "Prevent Duplicate Orchestrators"
    mistake_type: duplicate_orchestrator
    severity: blocked
    enabled: true
    message: "Orchestrator with similar functionality already exists."
    
  - id: MPR-003
    name: "Validate Orchestrator Hierarchy"
    mistake_type: invalid_hierarchy
    severity: blocked
    enabled: true
    message: "Invalid orchestrator hierarchy detected."
    
  - id: MPR-004
    name: "Enforce YAML-First Design"
    mistake_type: missing_manifest
    severity: blocked
    enabled: true
    message: "YAML manifest required before Python implementation."
""")
        return config
    
    @pytest.fixture
    def prevention_engine(self, rules_path: Path) -> MistakePreventionEngine:
        """Create MistakePreventionEngine instance."""
        return MistakePreventionEngine(rules_path=str(rules_path))
    
    def test_engine_initialization(self, prevention_engine: MistakePreventionEngine):
        """Test engine initializes correctly."""
        assert prevention_engine is not None
        assert prevention_engine.rules_path is not None
        assert isinstance(prevention_engine.rules, list)
        assert len(prevention_engine.rules) == 4
    
    def test_load_rules_from_yaml(self, prevention_engine: MistakePreventionEngine):
        """Test loading prevention rules from YAML."""
        rules = prevention_engine.rules
        assert len(rules) == 4
        assert rules[0].id == "MPR-001"
        assert rules[0].mistake_type == MistakeType.DIRECT_CREATION
        assert rules[0].severity == "blocked"


class TestBlockDirectCreation:
    """Test MPR-001: Block Direct Orchestrator Creation."""
    
    @pytest.fixture
    def prevention_engine(self, tmp_path: Path) -> MistakePreventionEngine:
        """Create engine with rules."""
        config = tmp_path / "rules.yaml"
        config.write_text("""
rules:
  - id: MPR-001
    name: "Block Direct Orchestrator Creation"
    mistake_type: direct_creation
    severity: blocked
    enabled: true
    message: "Direct orchestrator creation is blocked."
""")
        return MistakePreventionEngine(rules_path=str(config))
    
    def test_blocks_direct_file_creation(self, prevention_engine: MistakePreventionEngine):
        """Test blocks creating orchestrator Python file directly."""
        intent = OrchestrationIntent(
            action="create_file",
            target="src/orchestrators/custom/my_orchestrator.py",
            context={"creator": "user"}
        )
        
        result = prevention_engine.validate_intent(intent)
        
        assert result.is_valid is False
        assert len(result.errors) > 0
        assert "Direct orchestrator creation is blocked" in result.errors[0]
        assert result.mistake_type == MistakeType.DIRECT_CREATION
    
    def test_allows_master_orchestrator_creation(self, prevention_engine: MistakePreventionEngine):
        """Test allows MasterOrchestrator to create orchestrators."""
        intent = OrchestrationIntent(
            action="create_file",
            target="src/orchestrators/custom/my_orchestrator.py",
            context={"creator": "master_orchestrator"}
        )
        
        result = prevention_engine.validate_intent(intent)
        
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_blocks_manifest_creation_without_approval(
        self,
        prevention_engine: MistakePreventionEngine
    ):
        """Test blocks creating manifest without master approval."""
        intent = OrchestrationIntent(
            action="create_file",
            target="cortex-brain/manifests/orchestrators/my-orchestrator.yaml",
            context={"creator": "user", "approved_by_master": False}
        )
        
        result = prevention_engine.validate_intent(intent)
        
        assert result.is_valid is False
        assert "Direct orchestrator creation is blocked" in result.errors[0]


class TestPreventDuplicates:
    """Test MPR-002: Prevent Duplicate Orchestrators."""
    
    @pytest.fixture
    def prevention_engine(self, tmp_path: Path) -> MistakePreventionEngine:
        """Create engine with existing orchestrators."""
        config = tmp_path / "rules.yaml"
        config.write_text("""
rules:
  - id: MPR-002
    name: "Prevent Duplicate Orchestrators"
    mistake_type: duplicate_orchestrator
    severity: blocked
    enabled: true
    message: "Orchestrator with similar functionality exists."
""")
        engine = MistakePreventionEngine(rules_path=str(config))
        
        # Register existing orchestrators
        engine.register_orchestrator(MockOrchestrator(
            id="planning_orchestrator",
            name="Planning Orchestrator",
            patterns=["plan", "create plan"],
            capabilities=["planning", "task_breakdown"]
        ))
        
        return engine
    
    def test_detects_pattern_overlap(self, prevention_engine: MistakePreventionEngine):
        """Test detects overlapping patterns."""
        new_orchestrator = MockOrchestrator(
            id="plan_creator",
            name="Plan Creator",
            patterns=["plan", "make plan"],  # Overlaps with existing
            capabilities=["planning"]
        )
        
        result = prevention_engine.check_for_duplicates(new_orchestrator)
        
        assert result.is_valid is False
        assert "similar functionality" in result.errors[0].lower()
        assert result.mistake_type == MistakeType.DUPLICATE_ORCHESTRATOR
    
    def test_detects_capability_overlap(self, prevention_engine: MistakePreventionEngine):
        """Test detects overlapping capabilities."""
        new_orchestrator = MockOrchestrator(
            id="task_planner",
            name="Task Planner",
            patterns=["organize tasks"],
            capabilities=["planning", "task_breakdown"]  # Same capabilities
        )
        
        result = prevention_engine.check_for_duplicates(new_orchestrator)
        
        assert result.is_valid is False
        assert result.suggestions[0].startswith("Consider consolidating")
    
    def test_allows_distinct_orchestrator(self, prevention_engine: MistakePreventionEngine):
        """Test allows orchestrator with distinct functionality."""
        new_orchestrator = MockOrchestrator(
            id="vacuum_orchestrator",
            name="Vacuum Orchestrator",
            patterns=["vacuum", "clean", "cleanup"],
            capabilities=["file_cleanup", "pattern_matching"]
        )
        
        result = prevention_engine.check_for_duplicates(new_orchestrator)
        
        assert result.is_valid is True
        assert len(result.errors) == 0


class TestValidateHierarchy:
    """Test MPR-003: Validate Orchestrator Hierarchy."""
    
    @pytest.fixture
    def prevention_engine(self, tmp_path: Path) -> MistakePreventionEngine:
        """Create engine with hierarchy rules."""
        config = tmp_path / "rules.yaml"
        config.write_text("""
rules:
  - id: MPR-003
    name: "Validate Orchestrator Hierarchy"
    mistake_type: invalid_hierarchy
    severity: blocked
    enabled: true
    message: "Invalid orchestrator hierarchy."
""")
        engine = MistakePreventionEngine(rules_path=str(config))
        
        # Register orchestrators with hierarchy
        engine.register_orchestrator(MockOrchestrator(
            id="master",
            name="Master Orchestrator",
            patterns=["master"],
            capabilities=["orchestration"]
        ))
        
        engine.register_orchestrator(MockOrchestrator(
            id="planning",
            name="Planning Orchestrator",
            patterns=["plan"],
            capabilities=["planning"],
            parent_id="master"
        ))
        
        return engine
    
    def test_blocks_missing_parent(self, prevention_engine: MistakePreventionEngine):
        """Test blocks orchestrator with non-existent parent."""
        new_orchestrator = MockOrchestrator(
            id="child",
            name="Child Orchestrator",
            patterns=["child"],
            capabilities=["child_task"],
            parent_id="non_existent_parent"
        )
        
        result = prevention_engine.validate_hierarchy(new_orchestrator)
        
        assert result.is_valid is False
        assert "parent" in result.errors[0].lower()
        assert result.mistake_type == MistakeType.INVALID_HIERARCHY
    
    def test_detects_circular_dependency(self, prevention_engine: MistakePreventionEngine):
        """Test detects circular parent-child relationships."""
        # Try to make planning's parent be a child of planning
        circular_orchestrator = MockOrchestrator(
            id="circular",
            name="Circular Orchestrator",
            patterns=["circular"],
            capabilities=["circular"],
            parent_id="planning"
        )
        
        # Register it first
        prevention_engine.register_orchestrator(circular_orchestrator)
        
        # Now try to update planning to have circular as parent
        updated_planning = MockOrchestrator(
            id="planning",
            name="Planning Orchestrator",
            patterns=["plan"],
            capabilities=["planning"],
            parent_id="circular"  # Creates cycle
        )
        
        result = prevention_engine.validate_hierarchy(updated_planning)
        
        assert result.is_valid is False
        assert "circular" in result.errors[0].lower()
    
    def test_blocks_excessive_depth(self, prevention_engine: MistakePreventionEngine):
        """Test blocks hierarchy depth >3 levels."""
        # Create depth-3 chain: master → planning → child
        child = MockOrchestrator(
            id="child",
            name="Child Orchestrator",
            patterns=["child"],
            capabilities=["child_task"],
            parent_id="planning"
        )
        prevention_engine.register_orchestrator(child)
        
        # Try to add grandchild (depth 4)
        grandchild = MockOrchestrator(
            id="grandchild",
            name="Grandchild Orchestrator",
            patterns=["grandchild"],
            capabilities=["grandchild_task"],
            parent_id="child"
        )
        
        result = prevention_engine.validate_hierarchy(grandchild)
        
        assert result.is_valid is False
        assert "depth" in result.errors[0].lower() or "level" in result.errors[0].lower()
    
    def test_allows_valid_hierarchy(self, prevention_engine: MistakePreventionEngine):
        """Test allows valid parent-child relationship."""
        valid_child = MockOrchestrator(
            id="valid_child",
            name="Valid Child",
            patterns=["valid"],
            capabilities=["valid_task"],
            parent_id="planning"  # Valid existing parent
        )
        
        result = prevention_engine.validate_hierarchy(valid_child)
        
        assert result.is_valid is True
        assert len(result.errors) == 0


class TestEnforceYAMLFirst:
    """Test MPR-004: Enforce YAML-First Design."""
    
    @pytest.fixture
    def prevention_engine(self, tmp_path: Path) -> MistakePreventionEngine:
        """Create engine with YAML-first rules."""
        config = tmp_path / "rules.yaml"
        config.write_text("""
rules:
  - id: MPR-004
    name: "Enforce YAML-First Design"
    mistake_type: missing_manifest
    severity: blocked
    enabled: true
    message: "YAML manifest required."
""")
        return MistakePreventionEngine(rules_path=str(config))
    
    def test_blocks_implementation_without_manifest(
        self,
        prevention_engine: MistakePreventionEngine
    ):
        """Test blocks Python implementation without YAML manifest."""
        orchestrator = MockOrchestrator(
            id="no_manifest",
            name="No Manifest Orchestrator",
            patterns=["test"],
            capabilities=["testing"],
            manifest_path=None  # No manifest
        )
        
        result = prevention_engine.validate_yaml_first(orchestrator)
        
        assert result.is_valid is False
        assert "manifest" in result.errors[0].lower()
        assert result.mistake_type == MistakeType.MISSING_MANIFEST
    
    def test_validates_manifest_exists(self, prevention_engine: MistakePreventionEngine):
        """Test validates manifest file exists."""
        orchestrator = MockOrchestrator(
            id="with_manifest",
            name="With Manifest Orchestrator",
            patterns=["test"],
            capabilities=["testing"],
            manifest_path="non_existent_manifest.yaml"
        )
        
        result = prevention_engine.validate_yaml_first(orchestrator)
        
        assert result.is_valid is False
        assert "not found" in result.errors[0].lower() or "does not exist" in result.errors[0].lower()
    
    def test_allows_orchestrator_with_valid_manifest(
        self,
        prevention_engine: MistakePreventionEngine,
        tmp_path: Path
    ):
        """Test allows orchestrator with existing manifest."""
        # Create a manifest file
        manifest = tmp_path / "test-orchestrator.yaml"
        manifest.write_text("""
name: "Test Orchestrator"
version: "1.0.0"
phases:
  - phase_1: "Test Phase"
""")
        
        orchestrator = MockOrchestrator(
            id="valid",
            name="Valid Orchestrator",
            patterns=["test"],
            capabilities=["testing"],
            manifest_path=str(manifest)
        )
        
        result = prevention_engine.validate_yaml_first(orchestrator)
        
        assert result.is_valid is True
        assert len(result.errors) == 0


class TestPreventionResult:
    """Test PreventionResult data structure."""
    
    def test_create_valid_result(self):
        """Test creating valid prevention result."""
        result = PreventionResult(
            is_valid=True,
            errors=[],
            warnings=[],
            suggestions=[],
            mistake_type=None
        )
        
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_create_invalid_result(self):
        """Test creating invalid prevention result."""
        result = PreventionResult(
            is_valid=False,
            errors=["Error 1", "Error 2"],
            warnings=["Warning 1"],
            suggestions=["Suggestion 1"],
            mistake_type=MistakeType.DIRECT_CREATION
        )
        
        assert result.is_valid is False
        assert len(result.errors) == 2
        assert len(result.warnings) == 1
        assert result.mistake_type == MistakeType.DIRECT_CREATION
    
    def test_format_error_message(self):
        """Test formatting error message."""
        result = PreventionResult(
            is_valid=False,
            errors=["Direct creation blocked"],
            warnings=[],
            suggestions=["Use MasterOrchestrator instead"],
            mistake_type=MistakeType.DIRECT_CREATION
        )
        
        message = result.format_error_message()
        
        assert "Direct creation blocked" in message
        assert "Use MasterOrchestrator instead" in message
        assert "⛔" in message or "Suggestions" in message


class TestMistakeType:
    """Test MistakeType enum."""
    
    def test_mistake_types_defined(self):
        """Test all mistake types are defined."""
        assert MistakeType.DIRECT_CREATION
        assert MistakeType.DUPLICATE_ORCHESTRATOR
        assert MistakeType.INVALID_HIERARCHY
        assert MistakeType.MISSING_MANIFEST
    
    def test_mistake_types_have_values(self):
        """Test mistake types have string values."""
        assert isinstance(MistakeType.DIRECT_CREATION.value, str)
        assert isinstance(MistakeType.DUPLICATE_ORCHESTRATOR.value, str)


class TestOrchestrationIntent:
    """Test OrchestrationIntent data structure."""
    
    def test_create_intent(self):
        """Test creating orchestration intent."""
        intent = OrchestrationIntent(
            action="create_file",
            target="src/orchestrators/test.py",
            context={"creator": "user"}
        )
        
        assert intent.action == "create_file"
        assert intent.target == "src/orchestrators/test.py"
        assert intent.context["creator"] == "user"
    
    def test_intent_with_metadata(self):
        """Test intent with additional metadata."""
        intent = OrchestrationIntent(
            action="register_orchestrator",
            target="test_orchestrator",
            context={
                "creator": "master",
                "timestamp": "2026-01-08T04:30:00Z",
                "approved": True
            }
        )
        
        assert intent.context["approved"] is True
        assert "timestamp" in intent.context


class TestIntegration:
    """Integration tests for mistake prevention."""
    
    @pytest.fixture
    def full_engine(self, tmp_path: Path) -> MistakePreventionEngine:
        """Create engine with all rules."""
        config = tmp_path / "full-rules.yaml"
        config.write_text("""
rules:
  - id: MPR-001
    name: "Block Direct Orchestrator Creation"
    mistake_type: direct_creation
    severity: blocked
    enabled: true
    message: "Direct creation blocked."
    
  - id: MPR-002
    name: "Prevent Duplicate Orchestrators"
    mistake_type: duplicate_orchestrator
    severity: blocked
    enabled: true
    message: "Duplicate functionality."
    
  - id: MPR-003
    name: "Validate Orchestrator Hierarchy"
    mistake_type: invalid_hierarchy
    severity: blocked
    enabled: true
    message: "Invalid hierarchy."
    
  - id: MPR-004
    name: "Enforce YAML-First Design"
    mistake_type: missing_manifest
    severity: blocked
    enabled: true
    message: "Missing manifest."
""")
        return MistakePreventionEngine(rules_path=str(config))
    
    def test_full_validation_workflow(
        self,
        full_engine: MistakePreventionEngine,
        tmp_path: Path
    ):
        """Test complete validation workflow."""
        # Create manifest
        manifest = tmp_path / "test-orch.yaml"
        manifest.write_text("name: Test\nversion: 1.0.0\n")
        
        # Create valid orchestrator
        orch = MockOrchestrator(
            id="test",
            name="Test Orchestrator",
            patterns=["unique_pattern"],
            capabilities=["unique_capability"],
            parent_id="master",
            manifest_path=str(manifest)
        )
        
        # Register master first
        full_engine.register_orchestrator(MockOrchestrator(
            id="master",
            name="Master",
            patterns=["master"],
            capabilities=["orchestration"]
        ))
        
        # Run all validations
        dup_result = full_engine.check_for_duplicates(orch)
        hier_result = full_engine.validate_hierarchy(orch)
        yaml_result = full_engine.validate_yaml_first(orch)
        
        assert dup_result.is_valid is True
        assert hier_result.is_valid is True
        assert yaml_result.is_valid is True
