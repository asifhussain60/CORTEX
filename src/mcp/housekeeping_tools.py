"""
CORTEX 6.0 - Housekeeping MCP Tools

MCP tool wrappers for housekeeping orchestrator operations.
Provides 5 MCP tools for system maintenance and health monitoring.

IMPORTANT: All housekeeping is MANUAL ON-DEMAND ONLY per DOR Q4/Q9.
No automatic triggers, cron jobs, or file watchers.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from pathlib import Path
from typing import Dict, Any, Optional, List
import yaml


def housekeeping_status(
    workspace_root: str = "."
) -> Dict[str, Any]:
    """
    Get current housekeeping system status and configuration.
    
    Args:
        workspace_root: Path to workspace (default: current directory)
    
    Returns:
        Status information including configuration and last execution
    """
    try:
        workspace = Path(workspace_root).resolve()
        cortex_brain = workspace / "cortex-brain"
        
        # Check configuration
        config_status = {
            "workspace_root": str(workspace),
            "manual_only": True,  # Always per DOR Q4/Q9
            "allow_background": False,
            "phases_available": 9
        }
        
        # Check for last execution report
        reports_dir = cortex_brain / "documents" / "reports"
        last_report = None
        
        if reports_dir.exists():
            report_files = sorted(reports_dir.glob("housekeeping-*.yaml"), reverse=True)
            if report_files:
                last_report_path = report_files[0]
                with open(last_report_path) as f:
                    last_report = yaml.safe_load(f)
        
        return {
            "success": True,
            "status": "ready",
            "configuration": config_status,
            "last_execution": last_report.get("timestamp") if last_report else None,
            "last_health_score": last_report.get("overall_health_score") if last_report else None,
            "phases": [
                "governance_validation",
                "test_coverage_analysis",
                "audit_log_health_check",
                "brain_tier_sync",
                "cache_cleanup",
                "git_isolation_check",
                "manifest_validation",
                "ac_gap_detection",
                "health_report_generation"
            ]
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def housekeeping_execute(
    workspace_root: str = ".",
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    Execute full housekeeping workflow (9 phases).
    
    MANUAL INVOCATION ONLY - No automatic triggers per DOR Q4/Q9.
    
    Args:
        workspace_root: Path to workspace (default: current directory)
        dry_run: If True, simulate without making changes
    
    Returns:
        Complete housekeeping report with all phase results
    """
    try:
        from orchestrators.housekeeping_orchestrator import (
            HousekeepingOrchestrator,
            HousekeepingConfig
        )
        
        workspace = Path(workspace_root).resolve()
        
        config = HousekeepingConfig(
            workspace_root=workspace,
            manual_only=True  # MUST be True per DOR Q4/Q9
        )
        
        orchestrator = HousekeepingOrchestrator(config)
        
        if dry_run:
            # Return what would be executed
            return {
                "success": True,
                "dry_run": True,
                "phases_to_execute": [p.name for p in orchestrator.get_phases()],
                "configuration": {
                    "workspace_root": str(workspace),
                    "manual_only": True
                }
            }
        
        # Execute full workflow
        report = orchestrator.execute()
        
        # Format phase results
        phase_results = []
        for result in report.phase_results:
            phase_results.append({
                "phase": result.phase_number,
                "name": result.phase_name,
                "status": result.status,
                "duration_seconds": result.duration_seconds,
                "health_contribution": result.health_contribution,
                "details": result.details,
                "error": result.error_message
            })
        
        return {
            "success": True,
            "timestamp": report.timestamp.isoformat(),
            "overall_health_score": report.overall_health_score,
            "total_duration_seconds": report.total_duration_seconds,
            "phases_executed": len(report.phase_results),
            "phases_passed": sum(1 for p in report.phase_results if p.status == "SUCCESS"),
            "phases_failed": sum(1 for p in report.phase_results if p.status == "FAILED"),
            "phases_skipped": sum(1 for p in report.phase_results if p.status == "SKIPPED"),
            "phase_results": phase_results,
            "report_path": str(report.report_path) if report.report_path else None
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def housekeeping_phase(
    phase_number: int,
    workspace_root: str = "."
) -> Dict[str, Any]:
    """
    Execute a single housekeeping phase.
    
    Args:
        phase_number: Phase number (1-9) to execute
        workspace_root: Path to workspace (default: current directory)
    
    Returns:
        Single phase result with status and metrics
    """
    try:
        if phase_number < 1 or phase_number > 9:
            return {
                "success": False,
                "error": f"Invalid phase number: {phase_number}. Must be 1-9."
            }
        
        from orchestrators.housekeeping_orchestrator import (
            HousekeepingOrchestrator,
            HousekeepingConfig
        )
        
        workspace = Path(workspace_root).resolve()
        
        config = HousekeepingConfig(
            workspace_root=workspace,
            manual_only=True
        )
        
        orchestrator = HousekeepingOrchestrator(config)
        
        # Get the specific phase method
        phase_methods = {
            1: orchestrator._execute_phase_1,
            2: orchestrator._execute_phase_2,
            3: orchestrator._execute_phase_3,
            4: orchestrator._execute_phase_4,
            5: orchestrator._execute_phase_5,
            6: orchestrator._execute_phase_6,
            7: orchestrator._execute_phase_7,
            8: orchestrator._execute_phase_8,
            9: orchestrator._execute_phase_9,
        }
        
        phase_names = {
            1: "governance_validation",
            2: "test_coverage_analysis",
            3: "audit_log_health_check",
            4: "brain_tier_sync",
            5: "cache_cleanup",
            6: "git_isolation_check",
            7: "manifest_validation",
            8: "ac_gap_detection",
            9: "health_report_generation"
        }
        
        # Execute single phase
        result = phase_methods[phase_number]()
        result.phase_number = phase_number
        result.phase_name = phase_names[phase_number]
        
        return {
            "success": True,
            "phase": {
                "number": result.phase_number,
                "name": result.phase_name,
                "status": result.status,
                "duration_seconds": result.duration_seconds,
                "health_contribution": result.health_contribution,
                "details": result.details,
                "error": result.error_message
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def housekeeping_health(
    workspace_root: str = "."
) -> Dict[str, Any]:
    """
    Get current system health score without running full cleanup.
    
    This performs a lightweight health assessment based on:
    - Last housekeeping report
    - Quick filesystem checks
    - Brain tier structure validation
    
    Args:
        workspace_root: Path to workspace (default: current directory)
    
    Returns:
        Health score and component breakdown
    """
    try:
        workspace = Path(workspace_root).resolve()
        cortex_brain = workspace / "cortex-brain"
        
        components = {}
        issues = []
        recommendations = []
        
        # Check brain structure
        tiers = ["tier0", "tier1", "tier2", "tier3"]
        tiers_present = sum(1 for t in tiers if (cortex_brain / t).exists())
        components["brain_structure"] = (tiers_present / 4) * 100
        if tiers_present < 4:
            issues.append(f"Missing {4 - tiers_present} brain tiers")
            recommendations.append("Run housekeeping to diagnose missing tiers")
        
        # Check governance rules
        rules_file = cortex_brain / "tier0" / "governance" / "core-rules.yaml"
        if rules_file.exists():
            with open(rules_file) as f:
                rules_data = yaml.safe_load(f)
            rules_count = len(rules_data.get("rules", []))
            components["governance"] = 100.0 if rules_count >= 15 else (rules_count / 15) * 100
        else:
            components["governance"] = 0.0
            issues.append("Missing governance rules")
            recommendations.append("Add core-rules.yaml to tier0/governance")
        
        # Check tests directory
        tests_dir = workspace / "tests"
        if tests_dir.exists():
            test_files = list(tests_dir.rglob("test_*.py"))
            components["tests"] = min(100.0, len(test_files) * 5)  # Cap at 100
        else:
            components["tests"] = 0.0
            issues.append("No tests directory found")
            recommendations.append("Create tests/ with unit tests")
        
        # Check cache (older = lower score)
        cache_dir = cortex_brain / "cache"
        if cache_dir.exists():
            cache_files = list(cache_dir.rglob("*"))
            # Lower score if too many cache files
            components["cache"] = max(0.0, 100.0 - len(cache_files))
            if len(cache_files) > 50:
                recommendations.append("Run cache cleanup phase")
        else:
            components["cache"] = 100.0  # No cache = clean
        
        # Check last housekeeping report
        reports_dir = cortex_brain / "documents" / "reports"
        if reports_dir.exists():
            report_files = list(reports_dir.glob("housekeeping-*.yaml"))
            components["maintenance"] = 100.0 if report_files else 50.0
            if not report_files:
                recommendations.append("Run housekeeping for baseline health report")
        else:
            components["maintenance"] = 0.0
            recommendations.append("Run housekeeping to establish baseline")
        
        # Calculate overall score
        overall_score = sum(components.values()) / len(components) if components else 0.0
        
        return {
            "success": True,
            "overall_health_score": overall_score,
            "components": components,
            "issues": issues,
            "recommendations": recommendations,
            "note": "For comprehensive health check, run housekeeping_execute()"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def housekeeping_reports(
    workspace_root: str = ".",
    limit: int = 10
) -> Dict[str, Any]:
    """
    List recent housekeeping reports.
    
    Args:
        workspace_root: Path to workspace (default: current directory)
        limit: Maximum number of reports to return
    
    Returns:
        List of recent housekeeping reports with summaries
    """
    try:
        workspace = Path(workspace_root).resolve()
        reports_dir = workspace / "cortex-brain" / "documents" / "reports"
        
        if not reports_dir.exists():
            return {
                "success": True,
                "reports": [],
                "count": 0,
                "message": "No reports directory found. Run housekeeping to create first report."
            }
        
        report_files = sorted(reports_dir.glob("housekeeping-*.yaml"), reverse=True)[:limit]
        
        reports = []
        for report_file in report_files:
            try:
                with open(report_file) as f:
                    report_data = yaml.safe_load(f)
                
                reports.append({
                    "filename": report_file.name,
                    "timestamp": report_data.get("timestamp"),
                    "overall_health_score": report_data.get("overall_health_score"),
                    "total_duration_seconds": report_data.get("total_duration_seconds"),
                    "phases_count": len(report_data.get("phase_results", []))
                })
            except Exception:
                reports.append({
                    "filename": report_file.name,
                    "error": "Failed to parse report"
                })
        
        return {
            "success": True,
            "reports": reports,
            "count": len(reports),
            "total_available": len(list(reports_dir.glob("housekeeping-*.yaml")))
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
