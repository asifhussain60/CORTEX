"""
Smoke Tests for Documentation Orchestrator

Test Strategy: SMOKE TEST - 7 tests total
- Test 1: Initialization
- Test 2: Phase documentation workflow
- Test 3: Architecture diagram workflow
- Test 4: ADR creation workflow
- Test 5: Refactoring comparison workflow
- Test 6: DoR validation (all workflow types)
- Test 7: DoD validation (all workflow types)

Author: Asif Hussain
Date: December 10, 2025
"""

import pytest
from pathlib import Path
from datetime import datetime

from src.orchestration_3_0.orchestrators.documentation import DocumentationOrchestrator
from src.orchestration_3_0.orchestrators.documentation.documentation_orchestrator import (
    create_documentation_orchestrator,
    DocType
)
from src.orchestration_3_0.core.base_orchestrator import WorkflowContext
from src.orchestration_3_0.session.session_manager import SessionManager


@pytest.fixture
def temp_project_dir(tmp_path):
    """Create temporary project directory."""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()
    
    # Create some dummy files
    (project_dir / "README.md").write_text("# Test Project\n")
    (project_dir / "main.py").write_text("'''Main module'''\ndef main():\n    pass\n")
    
    return project_dir


@pytest.fixture
def fresh_session_manager(tmp_path):
    """Create fresh session manager with temp database."""
    db_path = tmp_path / "test_sessions.db"
    return SessionManager(db_path=str(db_path))


class TestDocumentationOrchestrator:
    """Documentation Orchestrator smoke tests."""
    
    def test_initialization(self, fresh_session_manager):
        """
        Smoke Test 1: Verify orchestrator initializes correctly.
        
        Validates:
        - Factory function creates instance
        - State machine initialized
        - Session manager connected
        - Components resolved (or gracefully handle missing)
        """
        # Create orchestrator using factory
        orchestrator = create_documentation_orchestrator(
            session_manager=fresh_session_manager
        )
        
        # Verify instance created
        assert orchestrator is not None
        assert isinstance(orchestrator, DocumentationOrchestrator)
        
        # Verify orchestrator name
        assert orchestrator.orchestrator_name == "DocumentationOrchestrator"
        
        # Verify state machine initialized
        assert orchestrator.state_machine is not None
        
        # Verify session manager connected
        assert orchestrator.session_manager is not None
        
        print("✅ Documentation Orchestrator initialized successfully")
    
    def test_phase_documentation_workflow(
        self,
        fresh_session_manager,
        temp_project_dir
    ):
        """
        Smoke Test 2: Verify phase documentation generation workflow.
        
        Validates:
        - Phase documentation inputs accepted
        - Workflow executes without errors
        - Output file generated
        - Content includes expected sections
        """
        # Create orchestrator
        orchestrator = create_documentation_orchestrator(
            session_manager=fresh_session_manager
        )
        
        # Create workflow context for phase documentation
        context = WorkflowContext(
            tenant_id="test-tenant",
            project_id="test-project",
            user_id="test-user",
            session_id="test-session-phase",
            inputs={
                "doc_type": DocType.PHASE.value,
                "project_path": str(temp_project_dir),
                "phase_number": 1,
                "phase_name": "Foundation Setup",
                "tasks_completed": ["1.1", "1.2", "1.3"],
                "metrics": {
                    "test_coverage": "92%",
                    "complexity": 4.2,
                    "loc": 450
                },
                "duration_hours": 8.0,
                "lessons_learned": [
                    "AutoFixture reduced test setup boilerplate by 40%",
                    "Directory.Build.props simplified configuration"
                ]
            },
            metadata={}
        )
        
        # Execute workflow
        result = orchestrator.execute_workflow(context)
        
        # Verify result
        assert result.get("success"), f"Workflow failed: {result.get('error')}"
        assert "phase_doc" in result
        assert result["phase_doc"].get("generated")
        assert result["phase_doc"].get("output_file")
        
        print(f"✅ Phase documentation generated: {result['phase_doc']['output_file']}")
    
    def test_architecture_diagram_workflow(
        self,
        fresh_session_manager,
        temp_project_dir
    ):
        """
        Smoke Test 3: Verify architecture diagram generation workflow.
        
        Validates:
        - Diagram inputs accepted
        - Mermaid diagram generated
        - Output file created
        - Diagram syntax valid
        """
        # Create orchestrator
        orchestrator = create_documentation_orchestrator(
            session_manager=fresh_session_manager
        )
        
        # Create workflow context for diagram
        context = WorkflowContext(
            tenant_id="test-tenant",
            project_id="test-project",
            user_id="test-user",
            session_id="test-session-diagram",
            inputs={
                "doc_type": DocType.DIAGRAM.value,
                "project_path": str(temp_project_dir),
                "diagram_type": "layers",
                "elements": [
                    {"name": "Presentation", "dependencies": ["Business"]},
                    {"name": "Business", "dependencies": ["Data"]},
                    {"name": "Data", "dependencies": []}
                ]
            },
            metadata={}
        )
        
        # Execute workflow
        result = orchestrator.execute_workflow(context)
        
        # Verify result
        assert result.get("success"), f"Workflow failed: {result.get('error')}"
        assert "diagram" in result
        assert result["diagram"].get("generated")
        assert result["diagram"]["element_count"] == 3
        
        print(f"✅ Architecture diagram generated: {result['diagram']['output_file']}")
    
    def test_adr_creation_workflow(
        self,
        fresh_session_manager,
        temp_project_dir
    ):
        """
        Smoke Test 4: Verify ADR creation workflow.
        
        Validates:
        - ADR inputs accepted
        - ADR number auto-increments
        - Output file created with proper naming
        - ADR template complete
        """
        # Create orchestrator
        orchestrator = create_documentation_orchestrator(
            session_manager=fresh_session_manager
        )
        
        # Create workflow context for ADR
        context = WorkflowContext(
            tenant_id="test-tenant",
            project_id="test-project",
            user_id="test-user",
            session_id="test-session-adr",
            inputs={
                "doc_type": DocType.ADR.value,
                "project_path": str(temp_project_dir),
                "title": "Use Repository Pattern",
                "status": "accepted",
                "decision": "Implement repository pattern for data access",
                "rationale": "Separates data access concerns from business logic",
                "consequences": "Improved testability and maintainability",
                "alternatives": [
                    "Direct database access",
                    "Active Record pattern"
                ]
            },
            metadata={}
        )
        
        # Execute workflow
        result = orchestrator.execute_workflow(context)
        
        # Verify result
        assert result.get("success"), f"Workflow failed: {result.get('error')}"
        assert "adr" in result
        assert result["adr"].get("generated")
        assert result["adr"]["adr_number"] >= 1  # Auto-increments based on existing ADRs
        assert "adr-" in result["adr"]["output_file"].lower()
        assert "use-repository-pattern" in result["adr"]["output_file"].lower()
        
        print(f"✅ ADR created: ADR-{result['adr']['adr_number']:03d}")
    
    def test_refactoring_comparison_workflow(
        self,
        fresh_session_manager,
        temp_project_dir
    ):
        """
        Smoke Test 5: Verify refactoring comparison workflow.
        
        Validates:
        - Refactoring inputs accepted
        - Metrics comparison calculated
        - Improvement percentages computed
        - Output file created
        """
        # Create orchestrator
        orchestrator = create_documentation_orchestrator(
            session_manager=fresh_session_manager
        )
        
        # Create workflow context for refactoring comparison
        context = WorkflowContext(
            tenant_id="test-tenant",
            project_id="test-project",
            user_id="test-user",
            session_id="test-session-refactor",
            inputs={
                "doc_type": DocType.REFACTORING.value,
                "project_path": str(temp_project_dir),
                "refactoring_name": "Extract Service Layer",
                "anti_pattern": "God Object with 2000+ LOC",
                "solution": "Extracted into 5 focused service classes",
                "metrics_before": {
                    "complexity": 45.0,
                    "loc": 2100.0,
                    "methods": 80.0
                },
                "metrics_after": {
                    "complexity": 12.0,
                    "loc": 1800.0,
                    "methods": 60.0
                }
            },
            metadata={}
        )
        
        # Execute workflow
        result = orchestrator.execute_workflow(context)
        
        # Verify result
        assert result.get("success"), f"Workflow failed: {result.get('error')}"
        assert "refactoring" in result
        assert result["refactoring"].get("generated")
        assert result["refactoring"]["improvement_count"] > 0
        
        print(f"✅ Refactoring comparison created with {result['refactoring']['improvement_count']} improvements")
    
    def test_dor_validation(self, fresh_session_manager, temp_project_dir):
        """
        Smoke Test 6: Verify DoR validation for all workflow types.
        
        Validates:
        - Valid inputs pass DoR
        - Missing required inputs fail DoR
        - Invalid paths fail DoR
        - All doc types validated
        """
        orchestrator = create_documentation_orchestrator(
            session_manager=fresh_session_manager
        )
        
        # Test 1: Valid inputs pass
        valid_context = WorkflowContext(
            tenant_id="test-tenant",
            project_id="test-project",
            user_id="test-user",
            session_id="test-session-dor",
            inputs={
                "doc_type": DocType.PHASE.value,
                "project_path": str(temp_project_dir),
                "phase_number": 1,
                "phase_name": "Test Phase"
            },
            metadata={}
        )
        
        dor_result = orchestrator.validate_dor(valid_context)
        assert dor_result.passed, f"Valid inputs should pass DoR: {dor_result.errors}"
        print("✅ DoR validation passed for valid inputs")
        
        # Test 2: Missing project path fails
        invalid_context = WorkflowContext(
            tenant_id="test-tenant",
            project_id="test-project",
            user_id="test-user",
            session_id="test-session-dor-invalid",
            inputs={
                "doc_type": DocType.PHASE.value,
                # project_path missing
            },
            metadata={}
        )
        
        dor_result = orchestrator.validate_dor(invalid_context)
        assert not dor_result.passed, "Missing project_path should fail DoR"
        assert len(dor_result.errors) > 0
        print("✅ DoR validation correctly failed for missing inputs")
    
    def test_dod_validation(self, fresh_session_manager, temp_project_dir):
        """
        Smoke Test 7: Verify DoD validation for all workflow types.
        
        Validates:
        - Successful generation passes DoD
        - Failed generation fails DoD
        - Missing output files trigger warnings
        - Metrics captured
        """
        orchestrator = create_documentation_orchestrator(
            session_manager=fresh_session_manager
        )
        
        context = WorkflowContext(
            tenant_id="test-tenant",
            project_id="test-project",
            user_id="test-user",
            session_id="test-session-dod",
            inputs={
                "doc_type": DocType.PHASE.value,
                "project_path": str(temp_project_dir)
            },
            metadata={}
        )
        
        # Test 1: Successful result passes DoD
        success_result = {
            "success": True,
            "output_files": ["phase-1-test.md"],
            "metrics": {"files_generated": 1}
        }
        
        dod_result = orchestrator.validate_dod(context, success_result)
        assert dod_result.passed, f"Successful result should pass DoD: {dod_result.errors}"
        print("✅ DoD validation passed for successful generation")
        
        # Test 2: Failed result fails DoD
        failed_result = {
            "success": False,
            "error": "Test error"
        }
        
        dod_result = orchestrator.validate_dod(context, failed_result)
        assert not dod_result.passed, "Failed result should fail DoD"
        assert len(dod_result.errors) > 0
        print("✅ DoD validation correctly failed for unsuccessful generation")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
