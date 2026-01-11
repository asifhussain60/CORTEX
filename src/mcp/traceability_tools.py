"""
CORTEX 6.0 MCP Traceability Tools

Implements AC test coverage and traceability MCP tools:
- traceability_scan: Scan tests for @pytest.mark.ac_id markers
- traceability_coverage: Generate AC coverage matrix
- traceability_gaps: Detect gaps in test coverage
- traceability_validate: Validate specific AC coverage

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from pathlib import Path
from typing import Dict, Any, Optional, List

from src.infrastructure.ac_traceability import (
    ACTraceabilitySystem,
    ACCoverageMatrix,
    ACGapReport,
    TraceabilityConfig,
)
from src.mcp.mcp_decorator import mcp_tool


@mcp_tool(
    name="cortex_traceability_scan",
    description="Scan test files for @pytest.mark.ac_id markers to build AC→Test mapping",
    category="traceability",
    parameters={
        "workspace_root": {"type": "string", "required": True, "description": "Workspace root path"},
        "force_refresh": {"type": "boolean", "required": False, "description": "Force cache refresh"}
    },
    metadata={"tags": ["traceability", "testing", "ac-ids"]}
)
def traceability_scan(
    workspace_root: str,
    force_refresh: bool = False
) -> Dict[str, Any]:
    """
    Scan test files for @pytest.mark.ac_id markers.
    
    Args:
        workspace_root: Path to workspace root
        force_refresh: Force cache refresh
    
    Returns:
        Scan results with AC→Test mappings
    """
    try:
        tests_root = Path(workspace_root) / "tests"
        registry_path = Path(workspace_root) / "cortex-brain" / "registry"
        
        config = TraceabilityConfig(
            tests_root=tests_root,
            registry_path=registry_path
        )
        
        system = ACTraceabilitySystem(config)
        results = system.scan_tests(force_refresh=force_refresh)
        
        # Summarize results
        ac_count = len(results)
        test_count = sum(len(tests) for tests in results.values())
        
        return {
            "success": True,
            "ac_count": ac_count,
            "test_count": test_count,
            "coverage_map": results,
            "message": f"Found {test_count} tests covering {ac_count} AC criteria"
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "ac_count": 0,
            "test_count": 0
        }


def traceability_coverage(
    workspace_root: str,
    export_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate AC coverage matrix from test scan.
    
    Args:
        workspace_root: Path to workspace root
        export_path: Optional path to export YAML report
    
    Returns:
        Coverage matrix with statistics
    """
    try:
        tests_root = Path(workspace_root) / "tests"
        registry_path = Path(workspace_root) / "cortex-brain" / "registry"
        ac_definitions_path = Path(workspace_root) / "cortex-brain" / "documents" / "planning" / "active" / "cortex6" / "acceptance-criteria" / "CX6-acceptance-criteria.yaml"
        
        config = TraceabilityConfig(
            tests_root=tests_root,
            registry_path=registry_path,
            ac_definitions_path=ac_definitions_path if ac_definitions_path.exists() else None
        )
        
        system = ACTraceabilitySystem(config)
        matrix = system.generate_coverage_matrix()
        
        # Export if requested
        if export_path:
            output = Path(export_path)
            matrix.export_yaml(output)
        
        return {
            "success": True,
            "covered_ac_count": len(matrix.coverage),
            "total_ac_count": matrix.metadata.get('total_ac_count', 0),
            "coverage_percentage": round(matrix.coverage_percentage, 2),
            "test_file_count": matrix.metadata.get('scan_file_count', 0),
            "total_tests": sum(len(tests) for tests in matrix.coverage.values()),
            "exported_to": export_path if export_path else None,
            "message": f"Coverage: {matrix.coverage_percentage:.1f}%"
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@mcp_tool(
    name="cortex_traceability_gaps",
    description="Detect gaps in test coverage - uncovered AC-IDs and orphaned tests (critical for finding missing tests)",
    category="traceability",
    orchestrator_id="traceability_orchestrator",
    parameters={
        "workspace_root": {"type": "string", "required": True, "description": "Workspace root path"},
        "include_orphans": {"type": "boolean", "required": False, "description": "Include tests without AC markers"}
    },
    returns={
        "type": "object",
        "description": "Gap report with uncovered AC and orphaned tests"
    },
    metadata={
        "tags": ["traceability", "gaps", "coverage", "ac-validation"],
        "version": "1.0",
        "priority": "P0"
    }
)
def traceability_gaps(
    workspace_root: str,
    include_orphans: bool = True
) -> Dict[str, Any]:
    """
    Detect gaps in test coverage.
    
    Args:
        workspace_root: Path to workspace root
        include_orphans: Include tests without AC markers
    
    Returns:
        Gap report with uncovered AC and orphaned tests
    """
    try:
        tests_root = Path(workspace_root) / "tests"
        registry_path = Path(workspace_root) / "cortex-brain" / "registry"
        ac_definitions_path = Path(workspace_root) / "cortex-brain" / "documents" / "planning" / "active" / "cortex6" / "acceptance-criteria" / "CX6-acceptance-criteria.yaml"
        
        config = TraceabilityConfig(
            tests_root=tests_root,
            registry_path=registry_path,
            ac_definitions_path=ac_definitions_path if ac_definitions_path.exists() else None
        )
        
        system = ACTraceabilitySystem(config)
        gaps = system.detect_gaps()
        
        result = {
            "success": True,
            "uncovered_ac_count": len(gaps.uncovered_ac),
            "uncovered_ac": sorted(list(gaps.uncovered_ac)),
            "critical_gaps_count": len(gaps.critical_gaps),
            "critical_gaps": sorted(list(gaps.critical_gaps)),
            "has_critical_gaps": len(gaps.critical_gaps) > 0,
            "message": f"Found {len(gaps.uncovered_ac)} uncovered AC ({len(gaps.critical_gaps)} critical)"
        }
        
        if include_orphans:
            result["orphaned_tests_count"] = len(gaps.orphaned_tests)
            result["orphaned_tests"] = gaps.orphaned_tests[:20]  # Limit to 20
        
        return result
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def traceability_validate(
    workspace_root: str,
    ac_id: str
) -> Dict[str, Any]:
    """
    Validate if a specific AC has test coverage.
    
    Args:
        workspace_root: Path to workspace root
        ac_id: AC-ID to validate (e.g., "AC-GOV-001")
    
    Returns:
        Validation result with test details
    """
    try:
        tests_root = Path(workspace_root) / "tests"
        registry_path = Path(workspace_root) / "cortex-brain" / "registry"
        
        config = TraceabilityConfig(
            tests_root=tests_root,
            registry_path=registry_path
        )
        
        system = ACTraceabilitySystem(config)
        
        # Get test count
        test_count = system.validate_ac(ac_id, return_count=True)
        has_coverage = test_count > 0
        
        # Get test details if covered
        tests = []
        if has_coverage:
            scan_results = system.scan_tests()
            tests = scan_results.get(ac_id, [])
        
        return {
            "success": True,
            "ac_id": ac_id,
            "has_coverage": has_coverage,
            "test_count": test_count,
            "tests": tests,
            "validation_status": "COVERED" if has_coverage else "NOT_COVERED",
            "message": f"{ac_id} {'has' if has_coverage else 'has NO'} test coverage ({test_count} tests)"
        }
    
    except Exception as e:
        return {
            "success": False,
            "ac_id": ac_id,
            "error": str(e)
        }


def traceability_batch_validate(
    workspace_root: str,
    ac_ids: List[str]
) -> Dict[str, Any]:
    """
    Validate multiple AC-IDs for test coverage.
    
    Args:
        workspace_root: Path to workspace root
        ac_ids: List of AC-IDs to validate
    
    Returns:
        Batch validation results
    """
    try:
        tests_root = Path(workspace_root) / "tests"
        registry_path = Path(workspace_root) / "cortex-brain" / "registry"
        
        config = TraceabilityConfig(
            tests_root=tests_root,
            registry_path=registry_path
        )
        
        system = ACTraceabilitySystem(config)
        
        results = {}
        covered_count = 0
        
        for ac_id in ac_ids:
            test_count = system.validate_ac(ac_id, return_count=True)
            has_coverage = test_count > 0
            
            results[ac_id] = {
                "has_coverage": has_coverage,
                "test_count": test_count
            }
            
            if has_coverage:
                covered_count += 1
        
        coverage_pct = (covered_count / len(ac_ids) * 100) if ac_ids else 0
        
        return {
            "success": True,
            "total_validated": len(ac_ids),
            "covered_count": covered_count,
            "uncovered_count": len(ac_ids) - covered_count,
            "coverage_percentage": round(coverage_pct, 2),
            "results": results,
            "message": f"{covered_count}/{len(ac_ids)} AC criteria have test coverage ({coverage_pct:.1f}%)"
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
