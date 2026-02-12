#!/usr/bin/env python
"""
CLI script to generate complete dashboard suite.

Usage:
    python -m cortex.scripts.generate_dashboard_suite --output dist/
    python -m cortex.scripts.generate_dashboard_suite --output dist/ --repos cortex brain

Generates:
    - dist/index.html (landing page)
    - dist/repos/<slug>/index.html (per-repo dashboards)
    - dist/assets/* (CSS, JS, vendor libs)

Authority: CORE-008 (TDD), CORE-011 (Type hints)
AC-ID: SPA-CLI-001
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Add parent directory for imports when run as script
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from cortex.visualization.spa.models import (
    ArchitectureLayer,
    DashboardSuiteConfig,
    QualityMetric,
    RepoDashboardData,
    RepoManifestEntry,
    Severity,
    TestingMetrics,
    UseCase,
    UseCaseCategory,
    UseCasePersona,
)
from cortex.visualization.spa.suite_generator import (
    DashboardSuiteGenerator,
    GenerationResult,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


def create_sample_repo_data(repo: RepoManifestEntry) -> RepoDashboardData:
    """Create sample data for a repository."""
    return RepoDashboardData(
        repo_slug=repo.slug,
        display_name=repo.display_name,
        owner="CORTEX Team",
        primary_language="Python",
        health_score=85,
        risk_score=15,
        loc=25000,
        files=150,
        services_count=8,
        coverage_pct=78.2,
        last_analyzed_at="2025-01-15T10:00:00Z",
        version="8.0",
        tags=["python", "mcp", "ai"],
        overview_metrics={
            "total_functions": 450,
            "avg_complexity": 4.2,
            "tech_debt_hours": 12,
        },
        architecture=[
            ArchitectureLayer(
                name="cortex.core",
                module_count=12,
                loc=5000,
                complexity=3.5,
                dependencies=["cortex.common", "cortex.models"],
            ),
            ArchitectureLayer(
                name="cortex.mcp",
                module_count=8,
                loc=3500,
                complexity=4.1,
                dependencies=["cortex.core"],
            ),
        ],
        quality=[
            QualityMetric(name="Maintainability", value=85.0, threshold=80.0, status="ok"),
            QualityMetric(name="Complexity", value=4.2, threshold=5.0, status="ok"),
            QualityMetric(name="Duplication", value=2.1, threshold=3.0, status="ok"),
        ],
        testing=TestingMetrics(
            coverage_pct=78.2,
            unit_tests=245,
            integration_tests=32,
            e2e_tests=12,
            risky_files=["src/legacy.py"],
            uncovered_files=["src/experimental.py"],
        ),
        use_cases=[
            UseCase(
                id="UC001",
                title="Code Review Automation",
                summary="Automated code review with AI-powered suggestions for quality improvements",
                persona=UseCasePersona.ENGINEER,
                category=UseCaseCategory.MAINTAINABILITY,
                severity=Severity.HIGH,
                tags=["automation", "quality", "ai"],
                signals=["code_complexity", "duplication_ratio"],
                actions=["Review flagged code", "Apply suggested fixes"],
                related_tabs=["Quality", "Architecture"],
            ),
            UseCase(
                id="UC002",
                title="Security Vulnerability Scanning",
                summary="Identify security vulnerabilities in codebase and dependencies",
                persona=UseCasePersona.SECURITY,
                category=UseCaseCategory.RISK,
                severity=Severity.CRITICAL,
                tags=["security", "vulnerabilities", "compliance"],
                signals=["vulnerability_count", "severity_distribution"],
                actions=["Patch vulnerabilities", "Update dependencies"],
                related_tabs=["Security", "Dependencies"],
            ),
            UseCase(
                id="UC003",
                title="Architecture Compliance",
                summary="Ensure architecture follows defined patterns and layer rules",
                persona=UseCasePersona.PRODUCTION_OWNER,
                category=UseCaseCategory.RELIABILITY,
                severity=Severity.MEDIUM,
                tags=["architecture", "patterns", "compliance"],
                signals=["layer_violations", "circular_dependencies"],
                actions=["Refactor violations", "Update architecture docs"],
                related_tabs=["Architecture", "Quality"],
            ),
        ],
    )


def create_default_config(repos: Optional[List[str]] = None, output_dir: str = "dist") -> DashboardSuiteConfig:
    """Create default suite configuration."""
    if repos is None:
        repos = ["cortex", "cortex-brain", "cortex-lens"]

    repo_entries = [
        RepoManifestEntry(
            slug=slug,
            display_name=slug.replace("-", " ").title(),
            owner="CORTEX Team",
            primary_language="Python",
            health_score=85,
            risk_score=15,
            loc=25000,
            files=150,
            services_count=8,
            coverage_pct=78.2,
            last_analyzed_at="2025-01-15T10:00:00Z",
            version="8.0",
            tags=["python", "mcp"],
        )
        for slug in repos
    ]

    return DashboardSuiteConfig(
        repos=repo_entries,
        output_dir=output_dir,
        title="CORTEX Dashboard Suite",
        subtitle="Cognitive Real-Time Execution System - Repository Analytics",
        version="8.0",
    )


def main() -> int:
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="Generate CORTEX Dashboard Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=Path("dist"),
        help="Output directory for generated suite (default: dist/)",
    )
    parser.add_argument(
        "--repos", "-r",
        nargs="+",
        help="Repository slugs to include (default: cortex, cortex-brain, cortex-lens)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    logger.info(f"Generating dashboard suite to: {args.output}")

    # Create configuration
    config = create_default_config(args.repos, str(args.output))
    logger.info(f"Configuration: {len(config.repos)} repositories")

    # Create sample data for each repo
    repo_data: Dict[str, RepoDashboardData] = {}
    for repo in config.repos:
        repo_data[repo.slug] = create_sample_repo_data(repo)
        logger.debug(f"Created sample data for: {repo.slug}")

    # Initialize generator
    generator = DashboardSuiteGenerator(output_dir=args.output)

    # Generate suite
    result: GenerationResult = generator.generate_suite(config, repo_data)

    # Report results
    if result.success:
        logger.info("✅ Dashboard suite generated successfully!")
        logger.info(f"   Landing: {result.landing_path}")
        logger.info(f"   Repo dashboards: {len(result.repo_dashboards)}")
        for path in result.repo_dashboards:
            logger.info(f"     - {path}")
        return 0
    else:
        logger.error("❌ Dashboard suite generation failed!")
        for error in result.errors:
            logger.error(f"   - {error}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
