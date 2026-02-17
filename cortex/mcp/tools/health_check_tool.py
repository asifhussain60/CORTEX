"""Health Check MCP Tool

Exposes health orchestrator functionality via MCP for Copilot Chat.
Allows users to run health checks from chat interface.

Author: CORTEX Framework
Phase: PHASE-95
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from cortex.orchestrators.health.health_orchestrator import HealthOrchestrator
from cortex.orchestrators.health.agents import (
    DuplicateDetectionAgent,
    StubDetectionAgent,
    PathIntegrityAgent,
    VersionCleanupAgent,
    TestCoverageAgent,
    RegistryConsistencyAgent,
)


def cortex_health_check(
    workspace_root: str,
    agents: Optional[List[str]] = None,
    include_recommendations: bool = True,
) -> Dict[str, Any]:
    """Run CORTEX health check on repository.
    
    Args:
        workspace_root: Path to repository root
        agents: Optional list of specific agents to run.
               Available: DuplicateDetection, StubDetection, PathIntegrity,
                         VersionCleanup, TestCoverage, RegistryConsistency
               If None, runs all agents.
        include_recommendations: Whether to generate recommendations
    
    Returns:
        Dict with health report data:
        - health_score: Overall score (0-100)
        - total_issues: Total issue count
        - by_severity: Issues grouped by severity
        - agent_results: Results from each agent
        - recommendations: List of recommended actions
        - markdown_report: Full markdown report
    
    Example:
        ```python
        # Run all agents
        result = cortex_health_check("/path/to/repo")
        print(f"Health Score: {result['health_score']}")
        
        # Run specific agents
        result = cortex_health_check(
            "/path/to/repo",
            agents=["DuplicateDetection", "TestCoverage"]
        )
        ```
    """
    workspace_path = Path(workspace_root)
    
    if not workspace_path.exists():
        return {
            "error": f"Workspace not found: {workspace_root}",
            "health_score": 0.0,
        }
    
    # Initialize orchestrator
    orchestrator = HealthOrchestrator(workspace_path)
    
    # Register agents based on input
    agent_mapping = {
        "DuplicateDetection": DuplicateDetectionAgent(),
        "StubDetection": StubDetectionAgent(),
        "PathIntegrity": PathIntegrityAgent(),
        "VersionCleanup": VersionCleanupAgent(),
        "TestCoverage": TestCoverageAgent(),
        "RegistryConsistency": RegistryConsistencyAgent(),
    }
    
    if agents:
        # Register only specified agents
        for agent_name in agents:
            if agent_name in agent_mapping:
                orchestrator.register_agent(agent_mapping[agent_name])
            else:
                return {
                    "error": f"Unknown agent: {agent_name}",
                    "available_agents": list(agent_mapping.keys()),
                }
    else:
        # Register all agents
        for agent in agent_mapping.values():
            orchestrator.register_agent(agent)
    
    # Run health check
    try:
        report = orchestrator.run_health_check()
    except Exception as e:
        return {
            "error": f"Health check failed: {str(e)}",
            "health_score": 0.0,
        }
    
    # Generate recommendations if requested
    if include_recommendations:
        report.generate_recommendations()
    
    # Build response
    result = {
        "health_score": report.metrics.health_score,
        "total_issues": report.metrics.total_issues,
        "by_severity": {
            "critical": report.metrics.critical_issues,
            "high": report.metrics.high_issues,
            "medium": report.metrics.medium_issues,
            "low": report.metrics.low_issues,
            "info": report.metrics.info_issues,
        },
        "files_scanned": report.metrics.files_scanned,
        "agents_run": report.metrics.agents_run,
        "duration_seconds": report.metrics.duration_seconds,
        "agent_results": [
            {
                "name": r.agent_name,
                "issues": r.issue_count,
                "files_scanned": r.files_scanned,
                "duration": r.duration_seconds,
            }
            for r in report.agent_results
        ],
        "recommendations": report.recommendations if include_recommendations else [],
        "markdown_report": report.to_markdown(),
    }
    
    # Add issue details if requested
    if report.metrics.total_issues > 0:
        result["issues"] = [
            {
                "category": issue.category.value,
                "severity": issue.severity.value,
                "file": str(issue.file_path),
                "description": issue.description,
                "fix": issue.suggested_fix,
            }
            for issue in report.all_issues[:50]  # Limit to first 50
        ]
    
    return result


__all__ = ["cortex_health_check"]
