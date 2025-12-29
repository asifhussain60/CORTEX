"""
Scan External Repositories and Generate Dashboard Data

Scans external repositories (KSESSIONS, KASHKOLE, ALIST) and generates dashboard data
in the exact format expected by the unified dashboard UI.

This script uses the same collectors as CORTEX to ensure 100% schema compatibility.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import argparse
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# Add CORTEX to path
cortex_root = Path(__file__).parent.parent
sys.path.insert(0, str(cortex_root))

from src.dashboard.data.tech_stack_collector import TechStackCollector
from src.dashboard.data.security_collector import SecurityCollector
from src.dashboard.data.architecture_collector import ArchitectureCollector
from src.dashboard.data.code_org_collector import CodeOrganizationCollector
from src.dashboard.data.vendor_detector import VendorDetector
from src.dashboard.data.team_metrics_collector import TeamMetricsCollector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ExternalRepoScanner:
    """
    Scans external repositories and generates dashboard-compatible data.
    
    Ensures 100% schema compatibility with mock data by using the same collectors.
    """
    
    def __init__(self, repo_path: Path, repo_name: str):
        """
        Initialize scanner.
        
        Args:
            repo_path: Path to repository root
            repo_name: Repository name (e.g., 'ksessions', 'kashkole', 'alist')
        """
        self.repo_path = repo_path
        self.repo_name = repo_name.lower().replace(' ', '-')
        self.output_dir = cortex_root / "cortex-brain" / "dashboards" / self.repo_name
        
        logger.info(f"ExternalRepoScanner initialized for {repo_name}")
        logger.info(f"  Repository: {repo_path}")
        logger.info(f"  Output: {self.output_dir}")
    
    def scan_repository(self) -> bool:
        """
        Scan repository and generate all dashboard data files.
        
        Returns:
            True if scan successful, False otherwise
        """
        try:
            logger.info(f"Starting scan of {self.repo_name}...")
            start_time = time.time()
            
            # Ensure output directory exists
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
            # Collect all data using CORTEX collectors
            dashboard_data = {
                "app_id": self.repo_name,
                "tabs": {},
                "metadata": {
                    "app_name": self.repo_name.upper().replace('-', ' '),
                    "app_type": "external",
                    "version": "1.0.0",
                    "last_updated": datetime.now().isoformat(),
                    "last_scan": datetime.now().isoformat(),
                    "scan_duration_seconds": 0
                }
            }
            
            # 1. Tech Stack
            logger.info("Collecting tech stack data...")
            tech_stack_data = self._collect_tech_stack()
            dashboard_data["tabs"]["tech_stack"] = tech_stack_data
            
            # 2. Security
            logger.info("Collecting security data...")
            security_data = self._collect_security()
            dashboard_data["tabs"]["security"] = security_data
            
            # 3. Architecture
            logger.info("Collecting architecture data...")
            architecture_data = self._collect_architecture()
            dashboard_data["tabs"]["architecture"] = architecture_data
            
            # 4. Code Organization
            logger.info("Collecting code organization data...")
            code_org_data = self._collect_code_organization()
            dashboard_data["tabs"]["code_organization"] = code_org_data
            
            # 5. Team Metrics
            logger.info("Collecting team metrics...")
            team_metrics_data = self._collect_team_metrics()
            dashboard_data["tabs"]["team_metrics"] = team_metrics_data
            
            # 6. Vendors
            logger.info("Detecting external vendors...")
            vendors_data = self._collect_vendors()
            dashboard_data["tabs"]["vendors"] = vendors_data
            
            # 7. Overview (health data)
            logger.info("Generating overview data...")
            overview_data = self._generate_overview(
                tech_stack_data,
                security_data,
                architecture_data,
                code_org_data,
                team_metrics_data,
                vendors_data
            )
            dashboard_data["tabs"]["overview"] = overview_data
            
            # Update scan duration
            scan_duration = time.time() - start_time
            dashboard_data["metadata"]["scan_duration_seconds"] = round(scan_duration, 2)
            
            # Write dashboard_data.json
            dashboard_file = self.output_dir / "dashboard_data.json"
            with open(dashboard_file, 'w', encoding='utf-8') as f:
                json.dump(dashboard_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Dashboard data written to {dashboard_file}")
            
            # Write metadata.json (minimal, for compatibility)
            metadata_file = self.output_dir / "metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(dashboard_data["metadata"], f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Metadata written to {metadata_file}")
            
            elapsed = time.time() - start_time
            logger.info(f"✅ Scan complete in {elapsed:.2f} seconds")
            logger.info(f"📊 Dashboard URL: cortex-brain/dashboards/ui/index.html?source={self.repo_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Scan failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _collect_tech_stack(self) -> Dict[str, Any]:
        """Collect technology stack data."""
        try:
            collector = TechStackCollector(self.repo_path)
            return collector.collect()
        except Exception as e:
            logger.error(f"Tech stack collection failed: {e}")
            return {"error": str(e), "languages": [], "frameworks": [], "tools": []}
    
    def _collect_security(self) -> Dict[str, Any]:
        """Collect security data."""
        try:
            collector = SecurityCollector(self.repo_path)
            return collector.collect()
        except Exception as e:
            logger.error(f"Security collection failed: {e}")
            return {"error": str(e), "score": 0, "vulnerabilities": []}
    
    def _collect_architecture(self) -> Dict[str, Any]:
        """Collect architecture data."""
        try:
            collector = ArchitectureCollector(self.repo_path)
            return collector.collect()
        except Exception as e:
            logger.error(f"Architecture collection failed: {e}")
            return {"error": str(e), "components": [], "layers": []}
    
    def _collect_code_organization(self) -> Dict[str, Any]:
        """Collect code organization data."""
        try:
            collector = CodeOrganizationCollector(self.repo_path)
            return collector.collect()
        except Exception as e:
            logger.error(f"Code organization collection failed: {e}")
            return {"error": str(e), "files": 0, "hotspots": []}
    
    def _collect_team_metrics(self) -> Dict[str, Any]:
        """Collect team metrics data."""
        try:
            collector = TeamMetricsCollector(self.repo_path)
            return collector.collect()
        except Exception as e:
            logger.error(f"Team metrics collection failed: {e}")
            return {"error": str(e), "contributors": 0, "commits": 0}
    
    def _collect_vendors(self) -> Dict[str, Any]:
        """Collect vendor/dependency data."""
        try:
            detector = VendorDetector(self.repo_path)
            return detector.detect()
        except Exception as e:
            logger.error(f"Vendor detection failed: {e}")
            return {"error": str(e), "vendors": []}
    
    def _generate_overview(
        self,
        tech_stack: Dict[str, Any],
        security: Dict[str, Any],
        architecture: Dict[str, Any],
        code_org: Dict[str, Any],
        team_metrics: Dict[str, Any],
        vendors: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate overview/health data from collected metrics.
        
        Calculates overall health score based on all metrics.
        """
        # Calculate health score (0-100)
        score_components = []
        
        # Security score (0-100)
        security_score = security.get("score", 0)
        score_components.append(security_score * 0.3)  # 30% weight
        
        # Architecture score (0-100, based on complexity)
        arch_components = len(architecture.get("components", []))
        arch_score = min(100, max(0, 100 - (arch_components / 10)))
        score_components.append(arch_score * 0.2)  # 20% weight
        
        # Code organization score (0-100, based on hotspots)
        hotspots = len(code_org.get("hotspots", []))
        code_org_score = min(100, max(0, 100 - (hotspots * 5)))
        score_components.append(code_org_score * 0.2)  # 20% weight
        
        # Tech stack diversity score (0-100)
        tech_count = len(tech_stack.get("languages", []))
        tech_score = min(100, tech_count * 20)
        score_components.append(tech_score * 0.15)  # 15% weight
        
        # Team activity score (0-100, based on commits)
        commits = team_metrics.get("total_commits", 0)
        team_score = min(100, commits / 10)
        score_components.append(team_score * 0.15)  # 15% weight
        
        overall_health_score = sum(score_components)
        
        # Determine status
        if overall_health_score >= 80:
            status = "healthy"
        elif overall_health_score >= 60:
            status = "warning"
        else:
            status = "critical"
        
        return {
            "overall_health_score": round(overall_health_score, 1),
            "status": status,
            "total_files": code_org.get("total_files", 0),
            "lines_of_code": code_org.get("total_lines", 0),
            "contributors": team_metrics.get("contributor_count", 0),
            "languages": len(tech_stack.get("languages", [])),
            "frameworks": len(tech_stack.get("frameworks", [])),
            "security_score": security_score,
            "security_issues": len(security.get("vulnerabilities", [])),
            "architecture_components": arch_components,
            "complexity_hotspots": hotspots,
            "external_vendors": len(vendors.get("vendors", [])),
            "recent_commits": commits,
            "last_commit_date": team_metrics.get("last_commit_date", "N/A")
        }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Scan external repository for dashboard")
    parser.add_argument(
        "repo_path",
        type=Path,
        help="Path to repository (e.g., D:\\PROJECTS\\KSESSIONS)"
    )
    parser.add_argument(
        "--name",
        type=str,
        help="Repository name (default: inferred from path)"
    )
    
    args = parser.parse_args()
    
    # Validate repository path
    if not args.repo_path.exists():
        logger.error(f"Repository path does not exist: {args.repo_path}")
        return 1
    
    # Infer name from path if not provided
    repo_name = args.name if args.name else args.repo_path.name
    
    # Initialize scanner
    scanner = ExternalRepoScanner(args.repo_path, repo_name)
    
    # Run scan
    success = scanner.scan_repository()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
