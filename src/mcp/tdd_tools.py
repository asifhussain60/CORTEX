"""
CORTEX 6.0 - TDD MCP Tools

MCP tool wrappers for TDD Orchestrator v4 operations.
Provides 5 MCP tools for RED→GREEN→REFACTOR workflow.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from pathlib import Path
from typing import Dict, Any, Optional
from src.mcp.mcp_decorator import mcp_tool


@mcp_tool(
    name="cortex_tdd_execute",
    description="Execute full TDD cycle for a feature",
    category="tdd",
    parameters={
        "feature_description": {"type": "string", "required": True, "description": "Feature description"},
        "workspace_root": {"type": "string", "required": False, "description": "Path to workspace"},
        "dry_run": {"type": "boolean", "required": False, "description": "Simulate without changes"}
    },
    returns={"type": "object", "description": "TDD execution results"}
)
def tdd_execute(
    feature_description: str,
    workspace_root: str = ".",
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    Execute full TDD cycle for a feature.
    
    Args:
        feature_description: Description of feature to implement
        workspace_root: Path to workspace (default: current directory)
        dry_run: If True, simulate without making changes
    
    Returns:
        TDD execution results with tests and implementation status
    """
    try:
        from orchestrators.tdd.tdd_orchestrator import TDDOrchestrator
        
        workspace = Path(workspace_root).resolve()
        
        orchestrator = TDDOrchestrator(
            workspace_root=workspace,
            dry_run=dry_run
        )
        
        if dry_run:
            return {
                "success": True,
                "dry_run": True,
                "feature": feature_description,
                "phases": ["DISCOVERY", "RED", "GREEN", "REFACTOR", "VALIDATION"]
            }
        
        result = orchestrator.execute(feature_description)
        
        return {
            "success": True,
            "feature": feature_description,
            "status": result.status.value if hasattr(result.status, 'value') else str(result.status),
            "tests_generated": result.tests_generated,
            "all_tests_passing": result.all_tests_passing,
            "clean_code_score": result.clean_code_score,
            "report_path": str(result.report_path) if result.report_path else None
        }
    except ImportError:
        return {
            "success": False,
            "error": "TDD orchestrator not available"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }




@mcp_tool(
    name="cortex_tdd_red_phase",
    description="Execute only RED phase - generate failing tests",
    category="tdd",
    parameters={
        "feature_description": {"type": "string", "required": True, "description": "Feature description"},
        "workspace_root": {"type": "string", "required": False, "description": "Path to workspace"}
    },
    returns={"type": "object", "description": "RED phase results"}
)
def tdd_red_phase(
    feature_description: str,
    workspace_root: str = "."
) -> Dict[str, Any]:
    """
    Execute only RED phase - generate failing tests.
    
    Args:
        feature_description: Description of feature to test
        workspace_root: Path to workspace (default: current directory)
    
    Returns:
        Generated tests (all should be FAILING)
    """
    try:
        from orchestrators.tdd.tdd_orchestrator import TDDOrchestrator
        
        workspace = Path(workspace_root).resolve()
        orchestrator = TDDOrchestrator(workspace_root=workspace)
        
        result = orchestrator.execute_red_phase(feature_description)
        
        return {
            "success": True,
            "phase": "RED",
            "status": result.status.value if hasattr(result.status, 'value') else "complete",
            "tests_generated": result.tests_generated,
            "tests": [
                {
                    "name": t.name,
                    "status": t.status,
                    "category": t.category
                }
                for t in result.tests
            ],
            "domain_knowledge_used": result.domain_knowledge_used
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


    try:
        from orchestrators.tdd.tdd_orchestrator import TDDOrchestrator
        
        workspace = Path(workspace_root).resolve()
        orchestrator = TDDOrchestrator(workspace_root=workspace)
        
        result = orchestrator.execute_red_phase(feature_description)
        
        return {
            "success": True,
            "phase": "RED",
            "status": result.status.value if hasattr(result.status, 'value') else "complete",
            "tests_generated": result.tests_generated,
            "tests": [
                {
                    "name": t.name,
                    "status": t.status,
                    "category": t.category
                }
                for t in result.tests
            ],
            "domain_knowledge_used": result.domain_knowledge_used
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@mcp_tool(
    name="cortex_tdd_green_phase",
    description="Execute only GREEN phase - implement until tests pass",
    category="tdd",
    parameters={
        "tests_file": {"type": "string", "required": True, "description": "Path to test file"},
        "workspace_root": {"type": "string", "required": False, "description": "Path to workspace"}
    },
    returns={"type": "object", "description": "GREEN phase results"}
)
def tdd_green_phase(
    tests_file: str,
    workspace_root: str = "."
) -> Dict[str, Any]:
    """
    Execute only GREEN phase - implement until tests pass.
    
    Args:
        tests_file: Path to test file from RED phase
        workspace_root: Path to workspace (default: current directory)
    
    Returns:
        Implementation status
    """
    try:
        from orchestrators.tdd.tdd_orchestrator import TDDOrchestrator
        from unittest.mock import Mock
        
        workspace = Path(workspace_root).resolve()
        orchestrator = TDDOrchestrator(workspace_root=workspace)
        
        # Create mock red_result (in real usage, would load from file)
        red_result = Mock(tests=[])
        
        result = orchestrator.execute_green_phase(red_result)
        
        return {
            "success": True,
            "phase": "GREEN",
            "status": result.status.value if hasattr(result.status, 'value') else "complete",
            "implementation_created": result.implementation_created,
            "all_tests_passing": result.all_tests_passing,
            "iterations": result.iterations
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


        return {
            "success": False,
            "error": str(e)
        }


@mcp_tool(
    name="cortex_tdd_refactor_phase",
    description="Execute only REFACTOR phase - apply clean code principles",
    category="tdd",
    parameters={
        "implementation_path": {"type": "string", "required": True, "description": "Path to implementation"},
        "workspace_root": {"type": "string", "required": False, "description": "Path to workspace"}
    },
    returns={"type": "object", "description": "REFACTOR phase results"}
)
def tdd_refactor_phase(
    implementation_path: str,
    workspace_root: str = "."
) -> Dict[str, Any]:
    """
    Execute only REFACTOR phase - apply clean code principles.
    
    Args:
        implementation_path: Path to implementation file
        workspace_root: Path to workspace (default: current directory)
    
    Returns:
        Refactoring results with clean code score
    """
    try:
        from orchestrators.tdd.tdd_orchestrator import TDDOrchestrator, PhaseResultData
        
        workspace = Path(workspace_root).resolve()
        orchestrator = TDDOrchestrator(workspace_root=workspace)
        
        # Create green_result with implementation path
        green_result = PhaseResultData(
            implementation_path=Path(implementation_path),
            code_metrics={}
        )
        
        result = orchestrator.execute_refactor_phase(green_result)
        
        return {
            "success": True,
            "phase": "REFACTOR",
            "status": result.status.value if hasattr(result.status, 'value') else "complete",
            "refactorings_applied": result.refactorings_applied,
            "clean_code_score": result.clean_code_score,
            "code_smells_detected": result.code_smells_detected,
            "tests_still_passing": result.tests_still_passing
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


        return {
            "success": False,
            "error": str(e)
        }


@mcp_tool(
    name="cortex_tdd_check_code",
    description="Analyze code for TDD readiness and quality metrics",
    category="tdd",
    parameters={
        "code": {"type": "string", "required": True, "description": "Code to check"},
        "workspace_root": {"type": "string", "required": False, "description": "Path to workspace"}
    },
    returns={"type": "object", "description": "Code analysis results"}
)
def tdd_check_code(
    code: str,
    workspace_root: str = "."
) -> Dict[str, Any]:
    """
    Check code against clean code principles.
    
    Args:
        code: Source code to analyze
        workspace_root: Path to workspace (default: current directory)
    
    Returns:
        List of clean code violations
    """
    try:
        from orchestrators.tdd.tdd_orchestrator import TDDOrchestrator
        
        workspace = Path(workspace_root).resolve()
        orchestrator = TDDOrchestrator(workspace_root=workspace)
        
        violations = orchestrator.check_clean_code(code)
        
        return {
            "success": True,
            "violations_count": len(violations),
            "violations": [
                {
                    "type": v.type,
                    "principle": v.principle,
                    "message": v.message,
                    "line": v.line
                }
                for v in violations
            ],
            "clean": len(violations) == 0
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
