"""
QA Orchestrator Tests - CORTEX 4.0

Smoke tests for QA orchestrator.

Author: Asif Hussain
Date: December 10, 2025
"""

import pytest
from pathlib import Path
from src.orchestration_3_0.orchestrators.qa import (
    create_qa_orchestrator,
    ReviewDepth
)
from src.orchestration_3_0.core.state_machine import OrchestratorStates
from src.orchestration_3_0.core.base_orchestrator import WorkflowContext


def test_qa_orchestrator_initialization():
    """Test QA orchestrator can be created and initialized."""
    orchestrator = create_qa_orchestrator()
    
    assert orchestrator is not None
    assert orchestrator.orchestrator_name == "QAOrchestrator"
    assert orchestrator.state_machine is not None
    assert orchestrator.session_manager is not None
    assert orchestrator.code_review_engine is not None
    assert orchestrator.security_scanner is not None
    assert orchestrator.performance_analyzer is not None
    assert orchestrator.architecture_reviewer is not None


def test_qa_code_review_workflow():
    """Test complete QA code review workflow."""
    orchestrator = create_qa_orchestrator()
    
    # Create test file (without CRITICAL issues)
    test_file = Path("test_review_sample.py")
    test_content = """
def example_function():
    \"\"\"Example function for testing.\"\"\"
    # Some code with minor issues
    for i in range(len([1, 2, 3])):  # Performance issue
        print(i)  # Code smell
    return True
"""
    test_file.write_text(test_content)
    
    try:
        # Execute workflow
        result = orchestrator.execute(
            tenant_id="test-tenant",
            project_id="test-project",
            user_id="test-user",
            inputs={
                'files': [str(test_file)],
                'depth': 'STANDARD',
                'project_path': '.'
            }
        )
        
        # Verify execution
        assert result.success is True
        assert 'code_review' in result.outputs
        assert 'security_scan' in result.outputs
        assert 'performance_analysis' in result.outputs
        assert 'architecture_review' in result.outputs
        assert 'summary' in result.outputs
        
        # Verify issues found
        summary = result.outputs['summary']
        assert summary['files_analyzed'] == 1
        assert summary['total_issues'] > 0  # Should find some issues
        
        print(f"QA workflow complete: {summary['total_issues']} issues found")
    
    finally:
        # Cleanup
        if test_file.exists():
            test_file.unlink()
