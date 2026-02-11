"""
MCP Tool Wrappers for Dashboard Generation.

Provides MCP-compatible tool interfaces for:
- Dashboard Suite Generation (GPT Spec compliant)
- Single Repo Dashboard Generation
- Landing Page Generation
- Centralized DashboardCapabilityBroker integration (Phase 53 S4)

AC-ID: SPA-SUITE-MCP-001
Authority: CORE-007 (MCP-first) + Phase 53 S4 (Orchestrator Integration)
"""

import logging
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from cortex.mcp.decorators import mcp_tool
from cortex.orchestrators.domain.dashboard_capability_broker import (
    DashboardCapabilityBroker,
    DashboardGenerationRequest,
    DashboardMetric,
    RepositoryType,
)

logger = logging.getLogger(__name__)

# Global broker instance (initialized once)
_broker_instance: Optional[DashboardCapabilityBroker] = None

def get_broker() -> DashboardCapabilityBroker:
    """Get or create global DashboardCapabilityBroker instance"""
    global _broker_instance
    if _broker_instance is None:
        _broker_instance = DashboardCapabilityBroker()
        # Register all 7 orchestrators on first use
        _register_orchestrators(_broker_instance)
    return _broker_instance

def _register_orchestrators(broker: DashboardCapabilityBroker):
    """Register all 7 operational orchestrators with broker"""
    orchestrators = [
        ("MasterOrchestrator", ["generate_dashboard", "governance_gate"]),
        ("PlanningOrchestrator", ["generate_dashboard", "artifact_registration"]),
        ("InteractionOrchestrator", ["generate_dashboard", "action_listing"]),
        ("RepositoryOnboardingOrchestrator", ["generate_dashboard", "auto_generate"]),
        ("RefactoringOrchestrator", ["generate_dashboard", "post_refactor"]),
        ("RecommendationGate", ["generate_dashboard", "metrics_evidence"]),
        ("TDDOrchestrator", ["generate_dashboard", "test_suite"])
    ]

    for orch_name, capabilities in orchestrators:
        broker.register_orchestrator(orch_name, capabilities)


@mcp_tool(
    name="cortex_generate_dashboard_suite",
    description="Generate complete static dashboard suite with landing + per-repo dashboards (GPT Spec compliant)",
    parameters={
        "repos": "array",
        "repo_data": "object",
        "output_dir": "string",
        "title": "string",
        "subtitle": "string",
    }
)
def cortex_generate_dashboard_suite(
    repos: List[Dict[str, Any]],
    repo_data: Dict[str, Dict[str, Any]],
    output_dir: str,
    title: str = "CORTEX Repository Intelligence",
    subtitle: str = "Offline enterprise dashboards • file:// compatible • MCP-generated",
) -> Dict[str, Any]:
    """
    Generate complete static dashboard suite.

    Produces:
    - dist/index.html (landing with hero + tile grid)
    - dist/repos/<slug>/index.html (repo dashboards)
    - dist/assets/* (CSS, JS, vendor libs)
    - dist/images/* (logo)

    All data embedded as JSON - no fetch() calls, file:// compatible.

    Args:
        repos: List of repo manifest entries:
            - slug: URL-safe identifier
            - display_name: Human-readable name
            - owner: Repository owner/team
            - primary_language: Main language
            - health_score: 0-100
            - risk_score: 0-100
            - loc: Lines of code
            - files: Total files
            - services_count: Number of services
            - coverage_pct: Test coverage %
            - last_analyzed_at: ISO timestamp
            - version: CORTEX version
            - tags: List of tags
            - icon: Emoji icon

        repo_data: Dictionary mapping slug -> full dashboard data:
            - repo_slug, display_name, owner, primary_language
            - health_score, risk_score, loc, files
            - overview_metrics, architecture, dependencies
            - quality, vulnerabilities, testing
            - use_cases, recommendations

        output_dir: Output directory path (absolute)
        title: Suite title for landing page
        subtitle: Suite subtitle

    Returns:
        Dict with:
        - success: bool
        - landing_path: str (path to landing HTML)
        - repo_dashboards: List[str] (paths to repo HTMLs)
        - errors: List[str]

    Example:
        >>> result = cortex_generate_dashboard_suite(
        ...     repos=[{
        ...         "slug": "kashkole",
        ...         "display_name": "KASHKOLE",
        ...         "owner": "Data Team",
        ...         "primary_language": "Python",
        ...         "health_score": 45,
        ...         "risk_score": 65,
        ...         "loc": 15000,
        ...         "files": 120,
        ...         "services_count": 5,
        ...         "coverage_pct": 35.5,
        ...         "last_analyzed_at": "2026-02-01T09:00:00",
        ...         "version": "8.0",
        ...         "tags": ["critical", "python"],
        ...         "icon": "📿"
        ...     }],
        ...     repo_data={"kashkole": {...}},
        ...     output_dir="/path/to/dist"
        ... )
        >>> print(f"Generated: {result['landing_path']}")
    """
    try:
        from cortex.visualization.spa.models import RepoManifestEntry
        from cortex.visualization.spa.suite_generator import (
            DashboardSuiteConfig,
            DashboardSuiteGenerator,
            RepoDashboardData,
        )

        # Convert dicts to dataclasses
        manifest_entries = []
        for r in repos:
            entry = RepoManifestEntry(
                slug=r.get("slug", ""),
                display_name=r.get("display_name", r.get("slug", "")),
                owner=r.get("owner", "Unknown"),
                primary_language=r.get("primary_language", "Unknown"),
                health_score=r.get("health_score", 0),
                risk_score=r.get("risk_score", 0),
                loc=r.get("loc", 0),
                files=r.get("files", 0),
                services_count=r.get("services_count", 0),
                coverage_pct=r.get("coverage_pct", 0.0),
                last_analyzed_at=r.get("last_analyzed_at", ""),
                version=r.get("version", "8.0"),
                tags=r.get("tags", []),
                icon=r.get("icon", "📁"),
            )
            manifest_entries.append(entry)

        # Convert repo data (simplified - uses dict directly)
        dashboard_data = {}
        for slug, data in repo_data.items():
            # Create RepoDashboardData from dict
            dashboard_data[slug] = RepoDashboardData(
                repo_slug=data.get("repo_slug", slug),
                display_name=data.get("display_name", slug),
                owner=data.get("owner", "Unknown"),
                primary_language=data.get("primary_language", "Unknown"),
                health_score=data.get("health_score", 0),
                risk_score=data.get("risk_score", 0),
                loc=data.get("loc", 0),
                files=data.get("files", 0),
                services_count=data.get("services_count", 0),
                coverage_pct=data.get("coverage_pct", 0.0),
                last_analyzed_at=data.get("last_analyzed_at", ""),
                version=data.get("version", "8.0"),
                tags=data.get("tags", []),
                overview_metrics=data.get("overview_metrics", {}),
                # Note: Other fields use defaults for now
            )

        # Create config
        config = DashboardSuiteConfig(
            repos=manifest_entries,
            output_dir=output_dir,
            title=title,
            subtitle=subtitle,
        )

        # Generate suite
        generator = DashboardSuiteGenerator(
            output_dir=Path(output_dir),
        )

        result = generator.generate_suite(config, dashboard_data)

        return {
            "success": result.success,
            "landing_path": result.landing_path,
            "repo_dashboards": result.repo_dashboards,
            "errors": result.errors,
        }

    except Exception as e:
        logger.error(f"cortex_generate_dashboard_suite failed: {e}", exc_info=True)
        return {
            "success": False,
            "landing_path": None,
            "repo_dashboards": [],
            "errors": [str(e)],
        }


@mcp_tool(
    name="cortex_generate_repo_dashboard",
    description="Generate single repo dashboard HTML with embedded data",
    parameters={
        "repo_slug": "string",
        "dashboard_data": "object",
        "output_path": "string",
    }
)
def cortex_generate_repo_dashboard(
    repo_slug: str,
    dashboard_data: Dict[str, Any],
    output_path: str,
) -> Dict[str, Any]:
    """
    Generate single repository dashboard.

    Creates a standalone HTML dashboard with embedded JSON data.
    Useful for generating individual repo dashboards without full suite.

    Args:
        repo_slug: Repository identifier
        dashboard_data: Full dashboard data dictionary
        output_path: Output file path (absolute)

    Returns:
        Dict with:
        - success: bool
        - output_path: str
        - error: Optional[str]

    Example:
        >>> result = cortex_generate_repo_dashboard(
        ...     repo_slug="kashkole",
        ...     dashboard_data={...},
        ...     output_path="/path/to/output/dashboard.html"
        ... )
    """
    try:
        from cortex.visualization.spa.models import RepoDashboardData, RepoManifestEntry
        from cortex.visualization.spa.suite_generator import DashboardSuiteGenerator

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Create manifest entry
        repo = RepoManifestEntry(
            slug=repo_slug,
            display_name=dashboard_data.get("display_name", repo_slug),
            owner=dashboard_data.get("owner", "Unknown"),
            primary_language=dashboard_data.get("primary_language", "Unknown"),
            health_score=dashboard_data.get("health_score", 0),
            risk_score=dashboard_data.get("risk_score", 0),
            loc=dashboard_data.get("loc", 0),
            files=dashboard_data.get("files", 0),
            services_count=dashboard_data.get("services_count", 0),
            coverage_pct=dashboard_data.get("coverage_pct", 0.0),
            last_analyzed_at=dashboard_data.get("last_analyzed_at", ""),
            version=dashboard_data.get("version", "8.0"),
            tags=dashboard_data.get("tags", []),
            icon=dashboard_data.get("icon", "📁"),
        )

        # Create dashboard data
        data = RepoDashboardData(
            repo_slug=repo_slug,
            display_name=dashboard_data.get("display_name", repo_slug),
            owner=dashboard_data.get("owner", "Unknown"),
            primary_language=dashboard_data.get("primary_language", "Unknown"),
            health_score=dashboard_data.get("health_score", 0),
            risk_score=dashboard_data.get("risk_score", 0),
            loc=dashboard_data.get("loc", 0),
            files=dashboard_data.get("files", 0),
            services_count=dashboard_data.get("services_count", 0),
            coverage_pct=dashboard_data.get("coverage_pct", 0.0),
            last_analyzed_at=dashboard_data.get("last_analyzed_at", ""),
            version=dashboard_data.get("version", "8.0"),
            tags=dashboard_data.get("tags", []),
            overview_metrics=dashboard_data.get("overview_metrics", {}),
        )

        # Generate using suite generator's method
        generator = DashboardSuiteGenerator(
            output_dir=output_path.parent,
        )

        result_path = generator._generate_repo_dashboard(repo, data)

        return {
            "success": True,
            "output_path": str(result_path),
            "error": None,
        }

    except Exception as e:
        logger.error(f"cortex_generate_repo_dashboard failed: {e}", exc_info=True)
        return {
            "success": False,
            "output_path": None,
            "error": str(e),
        }


@mcp_tool(
    name="cortex_generate_landing_page",
    description="Generate landing page HTML for dashboard suite",
    parameters={
        "repos": "array",
        "output_path": "string",
        "title": "string",
        "subtitle": "string",
    }
)
def cortex_generate_landing_page(
    repos: List[Dict[str, Any]],
    output_path: str,
    title: str = "CORTEX Repository Intelligence",
    subtitle: str = "Offline enterprise dashboards • file:// compatible",
) -> Dict[str, Any]:
    """
    Generate landing page HTML for dashboard suite.

    Creates a hero + tile grid landing page with embedded manifest.

    Args:
        repos: List of repo manifest entries (see cortex_generate_dashboard_suite)
        output_path: Output file path (absolute)
        title: Page title
        subtitle: Page subtitle

    Returns:
        Dict with:
        - success: bool
        - output_path: str
        - error: Optional[str]
    """
    try:
        from cortex.visualization.spa.models import RepoManifestEntry
        from cortex.visualization.spa.suite_generator import (
            DashboardSuiteConfig,
            DashboardSuiteGenerator,
        )

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Convert repos
        manifest_entries = []
        for r in repos:
            entry = RepoManifestEntry(
                slug=r.get("slug", ""),
                display_name=r.get("display_name", r.get("slug", "")),
                owner=r.get("owner", "Unknown"),
                primary_language=r.get("primary_language", "Unknown"),
                health_score=r.get("health_score", 0),
                risk_score=r.get("risk_score", 0),
                loc=r.get("loc", 0),
                files=r.get("files", 0),
                services_count=r.get("services_count", 0),
                coverage_pct=r.get("coverage_pct", 0.0),
                last_analyzed_at=r.get("last_analyzed_at", ""),
                version=r.get("version", "8.0"),
                tags=r.get("tags", []),
                icon=r.get("icon", "📁"),
            )
            manifest_entries.append(entry)

        config = DashboardSuiteConfig(
            repos=manifest_entries,
            output_dir=str(output_path.parent),
            title=title,
            subtitle=subtitle,
        )

        generator = DashboardSuiteGenerator(
            output_dir=output_path.parent,
        )

        result_path = generator._generate_landing(config)

        return {
            "success": True,
            "output_path": str(result_path),
            "error": None,
        }

    except Exception as e:
        logger.error(f"cortex_generate_landing_page failed: {e}", exc_info=True)
        return {
            "success": False,
            "output_path": None,
            "error": str(e),
        }
