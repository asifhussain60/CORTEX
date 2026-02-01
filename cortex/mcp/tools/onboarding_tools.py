"""
MCP Tool Wrappers for Onboarding and Configuration Analysis.

Provides MCP-compatible tool interfaces for:
- RepositoryOnboardingOrchestrator (LENS v2.0)
- ConfigAnalyzer (security analysis)

AC-ID: AC-LENS-V2-ONBOARD-001, AC-LENS-V2-CONFIG-001
Authority: CORE-007 (MCP-first)
"""

from pathlib import Path
from typing import Dict, Any
import logging

from cortex.mcp.decorators import mcp_tool

logger = logging.getLogger(__name__)


@mcp_tool(
    name="cortex_onboard_repository",
    description="Onboard repository with holistic LENS analysis + security assessment (P0/P1/P2)",
    parameters={
        "repo_path": "string",
        "include_dashboard": "boolean",
        "update_company_domain": "boolean",
    }
)
def cortex_onboard_repository(
    repo_path: str,
    include_dashboard: bool = True,
    update_company_domain: bool = True,
) -> Dict[str, Any]:
    """
    Onboard repository with holistic LENS v2.0 analysis.
    
    Performs:
    1. Multi-layer analysis (code, config, database, API)
    2. Security threat modeling (P0/P1/P2 classification)
    3. Company domain integration
    4. Dashboard generation (PHASE-14)
    5. Prioritized recommendations
    
    Args:
        repo_path: Path to repository to onboard
        include_dashboard: Whether to generate multi-tab dashboard
        update_company_domain: Whether to update company domain knowledge
        
    Returns:
        Dict with:
        - success: bool
        - repo_path: str
        - timestamp: str
        - security_risks: Dict (p0/p1/p2 breakdown)
        - recommendations: List[Dict]
        - dashboard_path: Optional[str]
        - error: str (if failed)
        
    Example:
        >>> result = cortex_onboard_repository(
        ...     repo_path="/path/to/repo",
        ...     include_dashboard=True
        ... )
        >>> print(f"P0 risks: {len(result['security_risks']['p0_risks'])}")
    """
    try:
        from cortex.orchestrators.support.repository_onboarding_orchestrator import (
            get_repository_onboarding_orchestrator
        )
        
        orchestrator = get_repository_onboarding_orchestrator()
        result = orchestrator.onboard_repository(
            repo_path=Path(repo_path),
            include_dashboard=include_dashboard,
            update_company_domain=update_company_domain,
        )
        
        return {
            "success": result.success,
            "repo_path": result.repo_path,
            "timestamp": result.timestamp,
            "security_risks": result.security_risks,
            "recommendations": result.recommendations,
            "dashboard_path": result.dashboard_path,
            "error": result.error,
            "holistic_context_summary": {
                "code_analysis": result.holistic_context.get("code_analysis", {}),
                "config_analysis_summary": {
                    "total_findings": result.holistic_context.get("config_analysis", {}).get("total_findings", 0),
                    "analyzed_files": result.holistic_context.get("config_analysis", {}).get("analyzed_files", 0),
                },
            },
        }
        
    except Exception as e:
        logger.error(f"cortex_onboard_repository failed: {e}", exc_info=True)
        return {
            "success": False,
            "repo_path": repo_path,
            "error": str(e),
        }


@mcp_tool(
    name="cortex_analyze_config",
    description="Analyze configuration file for security issues (secrets, insecure defaults)",
    parameters={
        "config_path": "string",
    }
)
def cortex_analyze_config(config_path: str) -> Dict[str, Any]:
    """
    Analyze configuration file for security and best practices.
    
    Detects:
    - Hardcoded secrets (API keys, passwords, AWS credentials)
    - Insecure defaults (debug=true, ssl_verify=false)
    - Missing security fields
    - Weak encryption algorithms
    
    Args:
        config_path: Path to config file (YAML, JSON, TOML, .env)
        
    Returns:
        Dict with:
        - success: bool
        - file_path: str
        - config_type: str
        - total_findings: int
        - p0_findings: List[Dict] (CRITICAL)
        - p1_findings: List[Dict] (HIGH)
        - p2_findings: List[Dict] (MEDIUM)
        - error: str (if failed)
        
    Example:
        >>> result = cortex_analyze_config("config/production.yaml")
        >>> for finding in result["p0_findings"]:
        ...     print(f"P0: {finding['description']}")
    """
    try:
        from cortex.brain.analysis.config_analyzer import get_config_analyzer
        
        analyzer = get_config_analyzer()
        result = analyzer.analyze_file(Path(config_path))
        
        if not result.success:
            return {
                "success": False,
                "file_path": config_path,
                "error": result.error,
            }
        
        # Categorize findings by severity
        p0_findings = [f for f in result.findings if f.severity.value == "P0"]
        p1_findings = [f for f in result.findings if f.severity.value == "P1"]
        p2_findings = [f for f in result.findings if f.severity.value == "P2"]
        
        return {
            "success": True,
            "file_path": result.file_path,
            "config_type": result.config_type,
            "analysis_time_ms": result.analysis_time_ms,
            "total_findings": len(result.findings),
            "p0_findings": [_finding_to_dict(f) for f in p0_findings],
            "p1_findings": [_finding_to_dict(f) for f in p1_findings],
            "p2_findings": [_finding_to_dict(f) for f in p2_findings],
        }
        
    except Exception as e:
        logger.error(f"cortex_analyze_config failed: {e}", exc_info=True)
        return {
            "success": False,
            "file_path": config_path,
            "error": str(e),
        }


@mcp_tool(
    name="cortex_analyze_repository_configs",
    description="Analyze all configuration files in a repository for security issues",
    parameters={
        "repo_path": "string",
    }
)
def cortex_analyze_repository_configs(repo_path: str) -> Dict[str, Any]:
    """
    Analyze all config files in repository.
    
    Scans for YAML, JSON, TOML, .env, docker-compose files
    and aggregates security findings.
    
    Args:
        repo_path: Path to repository root
        
    Returns:
        Dict with:
        - analyzed_files: int
        - total_findings: int
        - p0_findings: List[Dict]
        - p1_findings: List[Dict]
        - p2_findings: List[Dict]
        - summary: str
        
    Example:
        >>> result = cortex_analyze_repository_configs("/workspace/project")
        >>> print(result["summary"])
    """
    try:
        from cortex.brain.analysis.config_analyzer import get_config_analyzer
        
        analyzer = get_config_analyzer()
        result = analyzer.analyze_repository(Path(repo_path))
        
        return result
        
    except Exception as e:
        logger.error(f"cortex_analyze_repository_configs failed: {e}", exc_info=True)
        return {
            "analyzed_files": 0,
            "total_findings": 0,
            "error": str(e),
        }


def _finding_to_dict(finding) -> Dict[str, Any]:
    """Convert ConfigFinding to dict for MCP response."""
    return {
        "file_path": finding.file_path,
        "line_number": finding.line_number,
        "severity": finding.severity.value,
        "category": finding.category.value,
        "description": finding.description,
        "recommendation": finding.recommendation,
        "pattern_matched": finding.pattern_matched,
    }
