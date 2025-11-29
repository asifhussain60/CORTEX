"""
Tests for Discovery Scanners

Tests convention-based discovery without hardcoded lists:
- OrchestratorScanner
- AgentScanner
- EntryPointScanner
- DocumentationScanner

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
from src.discovery.orchestrator_scanner import OrchestratorScanner
from src.discovery.agent_scanner import AgentScanner
from src.discovery.entry_point_scanner import EntryPointScanner
from src.discovery.documentation_scanner import DocumentationScanner


class TestOrchestratorScanner:
    """Test orchestrator scanner."""
    
    @pytest.fixture
    def project_with_orchestrators(self, tmp_path):
        """Create project with mock orchestrators."""
        # Create base module
        base_path = tmp_path / "src" / "operations" / "base_operation_module.py"
        base_path.parent.mkdir(parents=True)
        base_path.write_text('''"""Base module."""
class BaseOperationModule:
    """Base class for operations."""
    pass
''')
        
        # Create test orchestrator
        orch_path = tmp_path / "src" / "operations" / "modules" / "test_orchestrator.py"
        orch_path.parent.mkdir(parents=True, exist_ok=True)
        orch_path.write_text('''"""Test orchestrator."""
from src.operations.base_operation_module import BaseOperationModule

class TestOrchestrator(BaseOperationModule):
    """Test orchestrator for validation."""
    
    def execute(self, context):
        """Execute operation."""
        pass
    
    def validate(self, context):
        """Validate operation."""
        return True
''')
        
        return tmp_path
    
    def test_discover_orchestrators(self, project_with_orchestrators):
        """Test orchestrator discovery."""
        scanner = OrchestratorScanner(project_with_orchestrators)
        orchestrators = scanner.discover()
        
        assert len(orchestrators) >= 1
        assert "TestOrchestrator" in orchestrators
    
    def test_orchestrator_metadata_extraction(self, project_with_orchestrators):
        """Test metadata extraction from orchestrator."""
        scanner = OrchestratorScanner(project_with_orchestrators)
        orchestrators = scanner.discover()
        
        test_orch = orchestrators["TestOrchestrator"]
        
        assert test_orch["class_name"] == "TestOrchestrator"
        assert test_orch["has_docstring"] is True
        assert "execute" in test_orch["methods"]
        assert "validate" in test_orch["methods"]
        assert test_orch["inherits_base"] is True
    
    def test_exclude_base_files(self, tmp_path):
        """Test exclusion of base/abstract files."""
        # Create base orchestrator (should be excluded)
        base_path = tmp_path / "src" / "operations" / "base_operation_module.py"
        base_path.parent.mkdir(parents=True)
        base_path.write_text('''"""Base module."""
class BaseOperationModule:
    """Base orchestrator."""
    pass
''')
        
        scanner = OrchestratorScanner(tmp_path)
        orchestrators = scanner.discover()
        
        # Base module should not be discovered
        assert "BaseOperationModule" not in orchestrators


class TestAgentScanner:
    """Test agent scanner."""
    
    @pytest.fixture
    def project_with_agents(self, tmp_path):
        """Create project with mock agents."""
        # Create test agent
        agent_path = tmp_path / "src" / "agents" / "test_agent.py"
        agent_path.parent.mkdir(parents=True)
        agent_path.write_text('''"""Test agent module."""

class TestAgent:
    """Test agent for validation."""
    
    def process(self, data):
        """Process data."""
        return data
    
    def execute(self, task):
        """Execute task."""
        pass
''')
        
        return tmp_path
    
    def test_discover_agents(self, project_with_agents):
        """Test agent discovery."""
        scanner = AgentScanner(project_with_agents)
        agents = scanner.discover()
        
        assert len(agents) >= 1
        assert "TestAgent" in agents
    
    def test_agent_metadata_extraction(self, project_with_agents):
        """Test metadata extraction from agent."""
        scanner = AgentScanner(project_with_agents)
        agents = scanner.discover()
        
        test_agent = agents["TestAgent"]
        
        assert test_agent["class_name"] == "TestAgent"
        assert test_agent["has_docstring"] is True
        assert test_agent["has_process_method"] is True
        assert test_agent["has_execute_method"] is True


class TestEntryPointScanner:
    """Test entry point scanner."""
    
    @pytest.fixture
    def project_with_templates(self, tmp_path):
        """Create project with response templates."""
        templates_dir = tmp_path / "cortex-brain"
        templates_dir.mkdir(parents=True)
        
        templates_file = templates_dir / "response-templates.yaml"
        templates_file.write_text('''
schema_version: '2.0'
templates:
  tdd_workflow:
    name: TDD Workflow
    triggers:
      - start tdd
      - tdd workflow
    response_type: detailed
  
  optimize_system:
    name: Optimize System
    triggers:
      - optimize
      - optimize cortex
    response_type: detailed
''')
        
        return tmp_path
    
    def test_discover_entry_points(self, project_with_templates):
        """Test entry point discovery."""
        scanner = EntryPointScanner(project_with_templates)
        entry_points = scanner.discover()
        
        assert len(entry_points) >= 2
        assert "start tdd" in entry_points
        assert "optimize" in entry_points
    
    def test_infer_orchestrator_from_trigger(self, project_with_templates):
        """Test orchestrator inference from trigger."""
        scanner = EntryPointScanner(project_with_templates)
        entry_points = scanner.discover()
        
        tdd_entry = entry_points["start tdd"]
        assert tdd_entry["expected_orchestrator"] == "TDDWorkflowOrchestrator"
        
        optimize_entry = entry_points["optimize"]
        assert optimize_entry["expected_orchestrator"] == "OptimizeSystemOrchestrator"
    
    def test_validate_wiring(self, project_with_templates):
        """Test wiring validation."""
        scanner = EntryPointScanner(project_with_templates)
        
        # Mock orchestrators (none exist)
        mock_orchestrators = {}
        
        orphaned, ghost = scanner.validate_wiring(mock_orchestrators)
        
        # All triggers should be orphaned (no orchestrators)
        assert len(orphaned) >= 2
        assert len(ghost) == 0  # No orchestrators = no ghosts


class TestDocumentationScanner:
    """Test documentation scanner."""
    
    @pytest.fixture
    def project_with_docs(self, tmp_path):
        """Create project with documentation."""
        prompts_dir = tmp_path / ".github" / "prompts"
        prompts_dir.mkdir(parents=True)
        
        # Create main prompt
        main_prompt = prompts_dir / "CORTEX.prompt.md"
        main_prompt.write_text('''
# CORTEX Main Prompt

## TDD Workflow
Complete test-driven development workflow.

## System Optimization
Optimize CORTEX performance.

## References
See #file:modules/tdd-guide.md for details.
See #file:modules/missing-file.md (this is broken).
''')
        
        # Create module documentation
        modules_dir = prompts_dir / "modules"
        modules_dir.mkdir(parents=True)
        
        (modules_dir / "tdd-guide.md").write_text("# TDD Guide\n...")
        
        return tmp_path
    
    def test_discover_documentation(self, project_with_docs):
        """Test documentation discovery."""
        scanner = DocumentationScanner(project_with_docs)
        docs = scanner.discover()
        
        assert "CORTEX.prompt.md" in docs
        # Handle both forward and backslash separators
        assert any("tdd-guide.md" in key for key in docs.keys())
    
    def test_detect_broken_references(self, project_with_docs):
        """Test broken reference detection."""
        scanner = DocumentationScanner(project_with_docs)
        docs = scanner.discover()
        
        main_doc = docs["CORTEX.prompt.md"]
        
        assert len(main_doc["broken_references"]) >= 1
        assert "modules/missing-file.md" in main_doc["broken_references"]
    
    def test_validate_orchestrator_coverage(self, project_with_docs):
        """Test orchestrator documentation coverage validation."""
        scanner = DocumentationScanner(project_with_docs)
        
        # Mock orchestrators
        mock_orchestrators = {
            "TDDWorkflowOrchestrator": {"documented": True},
            "UndocumentedOrchestrator": {"documented": False}
        }
        
        undocumented = scanner.validate_orchestrator_coverage(mock_orchestrators)
        
        # TDD is documented, Undocumented is not
        assert "UndocumentedOrchestrator" in undocumented


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
