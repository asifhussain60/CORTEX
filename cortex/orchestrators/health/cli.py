"""CLI Interface for CORTEX Health Check

Command-line tool for running health checks interactively.

Usage:
    python -m cortex.orchestrators.health.cli
    python -m cortex.orchestrators.health.cli --agents DuplicateDetection,TestCoverage
    python -m cortex.orchestrators.health.cli --export-dashboard

Author: CORTEX Framework
Phase: PHASE-95
"""

import argparse
import sys
from pathlib import Path

from cortex.orchestrators.health.health_orchestrator import HealthOrchestrator
from cortex.orchestrators.health.agents import (
    DuplicateDetectionAgent,
    StubDetectionAgent,
    PathIntegrityAgent,
    VersionCleanupAgent,
    TestCoverageAgent,
    RegistryConsistencyAgent,
)
from cortex.orchestrators.health.agents.mcp_auto_healing_agent import MCPAutoHealingAgent
from cortex.dashboards.health_metrics_exporter import HealthMetricsExporter


AVAILABLE_AGENTS = {
    "DuplicateDetection": DuplicateDetectionAgent,
    "StubDetection": StubDetectionAgent,
    "PathIntegrity": PathIntegrityAgent,
    "VersionCleanup": VersionCleanupAgent,
    "TestCoverage": TestCoverageAgent,
    "RegistryConsistency": RegistryConsistencyAgent,
    "MCPAutoHealing": MCPAutoHealingAgent,
}


def main() -> int:
    """Run health check CLI.

    Returns:
        Exit code (0 = success, 1 = errors found)
    """
    parser = argparse.ArgumentParser(
        description="CORTEX Health Check - Repository Health Analysis"
    )

    parser.add_argument(
        "--workspace",
        type=Path,
        default=Path.cwd(),
        help="Workspace root (default: current directory)",
    )

    parser.add_argument(
        "--agents",
        type=str,
        help=f"Comma-separated list of agents to run. Available: {', '.join(AVAILABLE_AGENTS.keys())}",
    )

    parser.add_argument(
        "--export-dashboard",
        action="store_true",
        help="Export metrics to dashboard database",
    )

    parser.add_argument(
        "--db-path",
        type=Path,
        default=Path("cortex/intelligence/governance.db"),
        help="Dashboard database path (default: cortex/intelligence/governance.db)",
    )

    parser.add_argument(
        "--markdown-output",
        type=Path,
        help="Save markdown report to file",
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )

    args = parser.parse_args()

    # Initialize orchestrator
    print("🔍 CORTEX Health Check")
    print(f"   Workspace: {args.workspace}")
    print()

    orchestrator = HealthOrchestrator(args.workspace)

    # Register agents
    if args.agents:
        agent_names = [name.strip() for name in args.agents.split(",")]
        for name in agent_names:
            if name in AVAILABLE_AGENTS:
                orchestrator.register_agent(AVAILABLE_AGENTS[name]())
                print(f"   ✓ Registered: {name}")
            else:
                print(f"   ✗ Unknown agent: {name}")
                return 1
    else:
        # Register all agents
        for agent_class in AVAILABLE_AGENTS.values():
            orchestrator.register_agent(agent_class())
        print(f"   ✓ Registered all {len(AVAILABLE_AGENTS)} agents")

    print()

    # Run health check
    try:
        report = orchestrator.run_health_check()
    except Exception as e:
        print(f"❌ Health check failed: {str(e)}")
        return 1

    # Output results
    if args.json:
        import json
        print(json.dumps(report.to_dict(), indent=2))
    else:
        # Console output
        print(f"Health Score: {report.metrics.health_score:.1f}/100")
        print(f"Total Issues: {report.metrics.total_issues}")
        print(f"  Critical: {report.metrics.critical_issues}")
        print(f"  High: {report.metrics.high_issues}")
        print(f"  Medium: {report.metrics.medium_issues}")
        print(f"  Low: {report.metrics.low_issues}")
        print()

        # Recommendations
        if report.recommendations:
            print("Recommendations:")
            for rec in report.generate_recommendations():
                print(f"  {rec}")
            print()

        # Agent results
        print("Agent Results:")
        for result in report.agent_results:
            status = "✅" if result.issue_count == 0 else f"⚠️  {result.issue_count} issues"
            print(f"  {result.agent_name}: {status}")
        print()

        # Show sample issues
        if report.metrics.total_issues > 0:
            print(f"Sample Issues (showing first 10 of {report.metrics.total_issues}):")
            for issue in report.all_issues[:10]:
                severity_icon = {
                    "critical": "🔴",
                    "high": "🟡",
                    "medium": "🟠",
                    "low": "🔵",
                    "info": "ℹ️",
                }.get(issue.severity.value, "•")

                print(f"  {severity_icon} {issue.file_path}")
                print(f"     {issue.description}")
                print(f"     Fix: {issue.suggested_fix}")
                print()

    # Export to dashboard
    if args.export_dashboard:
        print(f"Exporting to dashboard: {args.db_path}")
        exporter = HealthMetricsExporter(args.db_path)
        exporter.export_report(report)
        print("✅ Dashboard export complete")
        print()

    # Save markdown
    if args.markdown_output:
        args.markdown_output.write_text(report.to_markdown())
        print(f"✅ Markdown saved to: {args.markdown_output}")
        print()

    # Exit code
    if report.metrics.critical_issues > 0:
        print("❌ Health check failed: Critical issues detected")
        return 1

    print("✅ Health check passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
