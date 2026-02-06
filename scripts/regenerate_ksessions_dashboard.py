"""
Regenerate KSESSIONS dashboard with glassmorphism template.
"""
from pathlib import Path
import json
import sys

# Add CORTEX to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from cortex.visualization.spa.suite_generator import DashboardSuiteGenerator
from cortex.visualization.spa.models import (
    RepoDashboardData,
    RepoManifestEntry,
    DashboardSuiteConfig,
)

def regenerate_ksessions():
    """Regenerate KSESSIONS dashboard with glassmorphism template."""
    # Load existing data
    data_path = Path("company/dashboards/data/ksessions-data.json")
    with open(data_path, 'r', encoding='utf-8') as f:
        data_dict = json.load(f)
    
    # Map to expected model structure
    dashboard_data = RepoDashboardData(
        repo_slug=data_dict["repo"]["slug"],
        display_name=data_dict["repo"]["display_name"],
        owner=data_dict["repo"]["owner"],
        primary_language=data_dict["repo"]["primary_language"],
        health_score=data_dict["metrics"]["health_score"],
        risk_score=data_dict["metrics"]["risk_score"],
        loc=data_dict["metrics"]["loc"],
        files=data_dict["metrics"]["files"],
        services_count=data_dict.get("services_count", 12),  # Default
        coverage_pct=data_dict["metrics"]["coverage_pct"],
        last_analyzed_at=data_dict["repo"]["last_analyzed_at"],
        version=data_dict["repo"]["version"],
        tags=data_dict.get("tags", []),
        overview_metrics=data_dict.get("overview", {}),
        use_cases=data_dict.get("use_cases", []),
    )
    
    # Create manifest entry
    manifest = RepoManifestEntry(
        slug="ksessions",
        display_name="KSESSIONS",
        owner="KSESSIONS Team",
        primary_language="Go",
        health_score=87,
        risk_score=13,
        loc=45821,
        files=342,
        services_count=12,
        coverage_pct=82.0,
        last_analyzed_at="2026-02-04T14:57:11.240337Z",
        version="3.1",
        icon="🐳"
    )
    
    # Create config
    config = DashboardSuiteConfig(
        repos=[manifest],
        output_dir="company/dashboards"
    )
    
    # Generate
    generator = DashboardSuiteGenerator(
        output_dir=Path("company/dashboards"),
        cortex_root=Path(".")
    )
    
    result = generator.generate_suite(config, {"ksessions": dashboard_data})
    
    print(f"✅ Success: {result.success}")
    if result.repo_dashboards:
        print(f"📊 Generated dashboard: {result.repo_dashboards[0]}")
    if result.errors:
        print(f"⚠️  Errors: {result.errors}")
    
    return result.success

if __name__ == "__main__":
    success = regenerate_ksessions()
    sys.exit(0 if success else 1)
