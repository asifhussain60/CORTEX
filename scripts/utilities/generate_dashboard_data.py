"""
Generate dashboard data for real repositories.

Processes KSESSIONS, Alist, and KASHKOLE to create comprehensive
dashboard JSON files with enterprise-level metrics.

Usage:
    python generate_dashboard_data.py
"""

import sys
from pathlib import Path

# Add cortex to path
sys.path.insert(0, str(Path(__file__).parent))

from cortex.lens.capability_discovery import FingerprintAnalyzer
from cortex.lens.dashboard_data_aggregator import DashboardDataAggregator
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def main():
    """Generate dashboard data for all repositories."""
    
    # Repository paths
    repos = [
        {
            "name": "KSESSIONS",
            "path": Path("D:/PROJECTS/KSESSIONS"),
        },
        {
            "name": "Alist",
            "path": Path("D:/PROJECTS/Alist"),
        },
        {
            "name": "KASHKOLE",
            "path": Path("D:/PROJECTS/KASHKOLE"),
        },
    ]
    
    # Initialize components
    fingerprint_analyzer = FingerprintAnalyzer()
    aggregator = DashboardDataAggregator()
    
    for repo_info in repos:
        repo_name = repo_info["name"]
        repo_path = repo_info["path"]
        
        if not repo_path.exists():
            logger.warning(f"Repository not found: {repo_path}")
            continue
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing: {repo_name}")
        logger.info(f"Path: {repo_path}")
        logger.info(f"{'='*60}\n")
        
        try:
            # Step 1: Fingerprint analysis
            logger.info("Step 1: Analyzing technology stack...")
            fingerprint = fingerprint_analyzer.analyze(repo_path)
            logger.info(f"  Primary Language: {fingerprint.primary_language}")
            logger.info(f"  Languages: {', '.join(fingerprint.languages)}")
            logger.info(f"  Frameworks: {', '.join(fingerprint.frameworks)}")
            logger.info(f"  Database: {fingerprint.has_database}")
            logger.info(f"  API: {fingerprint.has_api}")
            
            # Step 2: Aggregate dashboard data
            logger.info("\nStep 2: Aggregating dashboard data...")
            result = aggregator.aggregate(
                repo_path=repo_path,
                fingerprint=fingerprint,
                repo_name=repo_name,
            )
            
            logger.info(f"  Overview: {result.overview.total_files} files, {result.overview.total_lines:,} lines")
            logger.info(f"  Metrics: {result.metrics.test_coverage}% coverage, {result.metrics.code_quality}/10 quality")
            logger.info(f"  Security: {result.security.security_score}/10 score")
            logger.info(f"  Dependencies: {result.dependencies.direct_dependencies} direct, {result.dependencies.transitive_dependencies} transitive")
            
            # Step 3: Write JSON file
            output_dir = Path("company/dashboards/repos") / repo_name.lower()
            output_file = output_dir / "dashboard-data.json"
            
            logger.info(f"\nStep 3: Writing dashboard JSON...")
            aggregator.write_json(result, output_file)
            logger.info(f"  ✅ Dashboard data written to: {output_file}")
            
            # Also write to dist for immediate use
            dist_output_dir = Path("company/dashboards/dist/repos") / repo_name.lower()
            dist_output_file = dist_output_dir / "dashboard-data.json"
            aggregator.write_json(result, dist_output_file)
            logger.info(f"  ✅ Dashboard data written to: {dist_output_file}")
            
        except Exception as e:
            logger.error(f"  ❌ Failed to process {repo_name}: {e}")
            import traceback
            traceback.print_exc()
    
    logger.info(f"\n{'='*60}")
    logger.info("Dashboard data generation complete!")
    logger.info(f"{'='*60}\n")


if __name__ == "__main__":
    main()
