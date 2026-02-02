#!/usr/bin/env python
"""
CLI script to generate a single repository dashboard.

Usage:
    python -m cortex.scripts.generate_repo_dashboard --repo cortex --output dist/repos/cortex/
    python -m cortex.scripts.generate_repo_dashboard --repo cortex --data analysis.json --output dist/repos/cortex/

Generates:
    - <output>/index.html (repo dashboard with embedded data)

Authority: CORE-008 (TDD), CORE-011 (Type hints)
AC-ID: SPA-CLI-002
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional

# Add parent directory for imports when run as script
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from cortex.visualization.spa.suite_generator import DashboardSuiteGenerator
from cortex.visualization.spa.models import (
    RepoDashboardData,
    RepoManifestEntry,
    Severity,
    UseCase,
    UseCasePersona,
    UseCaseCategory,
    TestingMetrics,
    QualityMetric,
    ArchitectureLayer,
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


def create_sample_data(repo_slug: str, repo_name: str) -> RepoDashboardData:
    """Create sample dashboard data for testing."""
    return RepoDashboardData(
        repo_slug=repo_slug,
        display_name=repo_name,
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
                name=f"{repo_slug}.core",
                module_count=12,
                loc=5000,
                complexity=3.5,
                dependencies=[f"{repo_slug}.common"],
            ),
        ],
        quality=[
            QualityMetric(name="Maintainability", value=85.0, threshold=80.0, status="ok"),
            QualityMetric(name="Complexity", value=4.2, threshold=5.0, status="ok"),
        ],
        testing=TestingMetrics(
            coverage_pct=78.2,
            unit_tests=245,
            integration_tests=32,
            e2e_tests=12,
            risky_files=[],
            uncovered_files=[],
        ),
        use_cases=[
            UseCase(
                id="UC001",
                title="Code Review Automation",
                summary="Automated code review with AI-powered suggestions",
                persona=UseCasePersona.ENGINEER,
                category=UseCaseCategory.MAINTAINABILITY,
                severity=Severity.HIGH,
                tags=["automation", "quality"],
                signals=["code_complexity"],
                actions=["Review flagged code"],
                related_tabs=["Quality"],
            ),
            UseCase(
                id="UC002",
                title="Security Scanning",
                summary="Identify security vulnerabilities in codebase",
                persona=UseCasePersona.SECURITY,
                category=UseCaseCategory.RISK,
                severity=Severity.CRITICAL,
                tags=["security", "vulnerabilities"],
                signals=["vulnerability_count"],
                actions=["Patch vulnerabilities"],
                related_tabs=["Security"],
            ),
        ],
    )


def load_data_from_file(data_path: Path) -> RepoDashboardData:
    """Load dashboard data from JSON file."""
    with open(data_path, "r", encoding="utf-8") as f:
        data_dict = json.load(f)
    
    # Convert use_cases if present
    use_cases = []
    for uc in data_dict.get("use_cases", []):
        use_cases.append(UseCase(
            id=uc["id"],
            title=uc["title"],
            summary=uc.get("summary", ""),
            persona=UseCasePersona(uc.get("persona", "engineer")),
            category=UseCaseCategory(uc.get("category", "maintainability")),
            severity=Severity(uc.get("severity", "medium")),
            tags=uc.get("tags", []),
            signals=uc.get("signals", []),
            actions=uc.get("actions", []),
            related_tabs=uc.get("related_tabs", []),
        ))
    
    # Convert architecture layers if present
    architecture = []
    for layer in data_dict.get("architecture", []):
        architecture.append(ArchitectureLayer(
            name=layer["name"],
            module_count=layer.get("module_count", 0),
            loc=layer.get("loc", 0),
            complexity=layer.get("complexity", 0.0),
            dependencies=layer.get("dependencies", []),
        ))
    
    # Convert quality metrics if present
    quality = []
    for metric in data_dict.get("quality", []):
        quality.append(QualityMetric(
            name=metric["name"],
            value=metric["value"],
            threshold=metric.get("threshold"),
            status=metric.get("status", "ok"),
        ))
    
    # Convert testing metrics if present
    testing_dict = data_dict.get("testing")
    testing = None
    if testing_dict:
        testing = TestingMetrics(
            coverage_pct=testing_dict.get("coverage_pct", 0.0),
            unit_tests=testing_dict.get("unit_tests", 0),
            integration_tests=testing_dict.get("integration_tests", 0),
            e2e_tests=testing_dict.get("e2e_tests", 0),
            risky_files=testing_dict.get("risky_files", []),
            uncovered_files=testing_dict.get("uncovered_files", []),
        )
    
    return RepoDashboardData(
        repo_slug=data_dict["repo_slug"],
        display_name=data_dict.get("display_name", data_dict["repo_slug"]),
        owner=data_dict.get("owner", "Unknown"),
        primary_language=data_dict.get("primary_language", "Unknown"),
        health_score=data_dict.get("health_score", 0),
        risk_score=data_dict.get("risk_score", 0),
        loc=data_dict.get("loc", 0),
        files=data_dict.get("files", 0),
        services_count=data_dict.get("services_count", 0),
        coverage_pct=data_dict.get("coverage_pct", 0.0),
        last_analyzed_at=data_dict.get("last_analyzed_at", ""),
        version=data_dict.get("version", "8.0"),
        tags=data_dict.get("tags", []),
        overview_metrics=data_dict.get("overview_metrics", {}),
        architecture=architecture,
        quality=quality,
        testing=testing,
        use_cases=use_cases,
    )


def main() -> int:
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="Generate single repository dashboard",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--repo", "-r",
        type=str,
        required=True,
        help="Repository slug (e.g., 'cortex', 'cortex-brain')",
    )
    parser.add_argument(
        "--name", "-n",
        type=str,
        help="Display name for repository (default: derived from slug)",
    )
    parser.add_argument(
        "--data", "-d",
        type=Path,
        help="Path to JSON file with dashboard data (optional, uses sample data if not provided)",
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=Path("dist"),
        help="Output directory for generated dashboard (default: dist/)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging",
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    repo_slug = args.repo
    repo_name = args.name or repo_slug.replace("-", " ").title()
    
    logger.info(f"Generating dashboard for: {repo_name} ({repo_slug})")
    logger.info(f"Output directory: {args.output}")
    
    # Load or create data
    if args.data and args.data.exists():
        logger.info(f"Loading data from: {args.data}")
        data = load_data_from_file(args.data)
    else:
        logger.info("Using sample data (no --data provided)")
        data = create_sample_data(repo_slug, repo_name)
    
    # Create repo entry
    repo = RepoManifestEntry(
        slug=repo_slug,
        display_name=repo_name,
        owner=data.owner,
        primary_language=data.primary_language,
        health_score=data.health_score,
        risk_score=data.risk_score,
        loc=data.loc,
        files=data.files,
        services_count=data.services_count,
        coverage_pct=data.coverage_pct,
        last_analyzed_at=data.last_analyzed_at,
        version=data.version,
        tags=data.tags,
    )
    
    # Initialize generator
    generator = DashboardSuiteGenerator(output_dir=args.output)
    
    # Generate single dashboard using internal method
    try:
        # Ensure directory structure
        generator._create_directory_structure()
        generator._copy_assets()
        
        # Generate the dashboard
        output_path = generator._generate_repo_dashboard(repo, data)
        
        logger.info(f"✅ Dashboard generated: {output_path}")
        return 0
        
    except Exception as e:
        logger.error(f"❌ Dashboard generation failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
