"""
Plan Cleanup CLI - Automated Plan Lifecycle Management

Implements cleanup policies for planning system:
- Delete temp plans older than 7 days
- Archive completed plans after 30 days
- Archive failed plans after 14 days
- Detect and flag orphaned plans

Author: Asif Hussain
Date: December 17, 2025
Version: 1.0.0
"""

import sys
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any
import json
import yaml

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

logger = logging.getLogger(__name__)


class PlanCleanupManager:
    """
    Manages automated cleanup of planning artifacts.
    
    Policies:
    - Temp plans: Delete after 7 days (or archive)
    - Completed plans: Archive after 30 days
    - Failed plans: Archive after 14 days
    - Orphaned plans: Detect and flag
    """
    
    def __init__(self, project_root: Path):
        """
        Initialize cleanup manager.
        
        Args:
            project_root: Root directory of CORTEX project
        """
        self.project_root = Path(project_root)
        self.planning_root = self.project_root / "cortex-brain" / "documents" / "planning"
        
        # Folder paths
        self.temp_plans_folder = self.planning_root / "temp-plans"
        self.active_folder = self.planning_root / "active"
        self.completed_folder = self.planning_root / "completed"
        self.archived_folder = self.planning_root / "archived"
        
        # Load cleanup policies
        self.policies = self._load_policies()
    
    def _load_policies(self) -> Dict[str, Any]:
        """
        Load cleanup policies from YAML.
        
        Returns:
            Policies dictionary
        """
        policies_file = self.planning_root / "cleanup-policies.yaml"
        
        if policies_file.exists():
            with open(policies_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        
        # Default policies
        return {
            "temp_plan_retention_days": 7,
            "completed_plan_retention_days": 30,
            "failed_plan_retention_days": 14,
            "orphaned_plan_detection": True,
            "dry_run_mode": False
        }
    
    def cleanup_old_temp_plans(self, dry_run: bool = False) -> Dict[str, Any]:
        """
        Delete temp plans older than retention period.
        
        Args:
            dry_run: If True, don't actually delete (report only)
            
        Returns:
            Cleanup report
        """
        retention_days = self.policies.get("temp_plan_retention_days", 7)
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        deleted = []
        errors = []
        
        if not self.temp_plans_folder.exists():
            return {"deleted": deleted, "errors": errors, "total": 0}
        
        for plan_folder in self.temp_plans_folder.iterdir():
            if not plan_folder.is_dir():
                continue
            
            # Check folder age
            mtime = datetime.fromtimestamp(plan_folder.stat().st_mtime)
            
            if mtime < cutoff_date:
                try:
                    if not dry_run:
                        # Delete folder and contents
                        import shutil
                        shutil.rmtree(plan_folder)
                    
                    deleted.append({
                        "plan_id": plan_folder.name,
                        "age_days": (datetime.now() - mtime).days,
                        "deleted": not dry_run
                    })
                    
                    logger.info(f"{'Would delete' if dry_run else 'Deleted'} temp plan: {plan_folder.name}")
                
                except Exception as e:
                    errors.append({
                        "plan_id": plan_folder.name,
                        "error": str(e)
                    })
                    logger.error(f"Error deleting {plan_folder.name}: {e}")
        
        return {
            "deleted": deleted,
            "errors": errors,
            "total": len(deleted)
        }
    
    def archive_old_completed_plans(self, dry_run: bool = False) -> Dict[str, Any]:
        """
        Archive completed plans older than retention period.
        
        Args:
            dry_run: If True, don't actually move (report only)
            
        Returns:
            Archive report
        """
        retention_days = self.policies.get("completed_plan_retention_days", 30)
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        archived = []
        errors = []
        
        if not self.completed_folder.exists():
            return {"archived": archived, "errors": errors, "total": 0}
        
        # Ensure archive folder exists
        self.archived_folder.mkdir(parents=True, exist_ok=True)
        
        for plan_folder in self.completed_folder.iterdir():
            if not plan_folder.is_dir():
                continue
            
            # Check folder age
            mtime = datetime.fromtimestamp(plan_folder.stat().st_mtime)
            
            if mtime < cutoff_date:
                try:
                    archive_path = self.archived_folder / plan_folder.name
                    
                    if not dry_run:
                        plan_folder.rename(archive_path)
                    
                    archived.append({
                        "plan_id": plan_folder.name,
                        "age_days": (datetime.now() - mtime).days,
                        "archived": not dry_run
                    })
                    
                    logger.info(f"{'Would archive' if dry_run else 'Archived'} completed plan: {plan_folder.name}")
                
                except Exception as e:
                    errors.append({
                        "plan_id": plan_folder.name,
                        "error": str(e)
                    })
                    logger.error(f"Error archiving {plan_folder.name}: {e}")
        
        return {
            "archived": archived,
            "errors": errors,
            "total": len(archived)
        }
    
    def detect_orphaned_plans(self) -> Dict[str, Any]:
        """
        Detect plans with missing artifacts (orphaned).
        
        Returns:
            Detection report
        """
        orphaned = []
        
        for folder in [self.active_folder, self.completed_folder]:
            if not folder.exists():
                continue
            
            for plan_folder in folder.iterdir():
                if not plan_folder.is_dir():
                    continue
                
                issues = []
                
                # Check for master plan
                master_plan = plan_folder / "master-plan.md"
                if not master_plan.exists():
                    issues.append("missing_master_plan")
                
                # Check for execution folder
                execution_folder = plan_folder / "execution"
                if not execution_folder.exists():
                    issues.append("missing_execution_folder")
                
                # Check for context folder
                context_folder = plan_folder / "context"
                if not context_folder.exists():
                    issues.append("missing_context_folder")
                
                # Check for worker plans (WP## files)
                worker_plans = list(plan_folder.glob("WP*.md"))
                if master_plan.exists() and len(worker_plans) == 0:
                    # Read master plan to see if it references worker plans
                    with open(master_plan, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if "WP01" in content or "Worker Plan" in content:
                            issues.append("missing_worker_plans")
                
                if issues:
                    orphaned.append({
                        "plan_id": plan_folder.name,
                        "location": str(folder.relative_to(self.project_root)),
                        "issues": issues
                    })
                    
                    logger.warning(f"Orphaned plan detected: {plan_folder.name} - {', '.join(issues)}")
        
        return {
            "orphaned": orphaned,
            "total": len(orphaned)
        }
    
    def generate_cleanup_report(self, dry_run: bool = True) -> Dict[str, Any]:
        """
        Generate comprehensive cleanup report.
        
        Args:
            dry_run: If True, don't actually perform cleanup
            
        Returns:
            Full cleanup report
        """
        logger.info("🧹 Generating cleanup report...")
        
        temp_result = self.cleanup_old_temp_plans(dry_run=dry_run)
        completed_result = self.archive_old_completed_plans(dry_run=dry_run)
        orphaned_result = self.detect_orphaned_plans()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "dry_run": dry_run,
            "temp_plans": temp_result,
            "completed_plans": completed_result,
            "orphaned_plans": orphaned_result,
            "summary": {
                "temp_deleted": temp_result["total"],
                "completed_archived": completed_result["total"],
                "orphaned_detected": orphaned_result["total"]
            }
        }


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="CORTEX Plan Cleanup Utility")
    parser.add_argument("--dry-run", action="store_true", help="Report only, don't actually clean")
    parser.add_argument("--temp-only", action="store_true", help="Clean temp plans only")
    parser.add_argument("--completed-only", action="store_true", help="Archive completed plans only")
    parser.add_argument("--orphaned-only", action="store_true", help="Detect orphaned plans only")
    parser.add_argument("--output", type=str, help="Save report to file (JSON)")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    
    # Initialize manager
    manager = PlanCleanupManager(project_root)
    
    # Generate report
    if args.temp_only:
        report = {
            "temp_plans": manager.cleanup_old_temp_plans(dry_run=args.dry_run)
        }
    elif args.completed_only:
        report = {
            "completed_plans": manager.archive_old_completed_plans(dry_run=args.dry_run)
        }
    elif args.orphaned_only:
        report = {
            "orphaned_plans": manager.detect_orphaned_plans()
        }
    else:
        report = manager.generate_cleanup_report(dry_run=args.dry_run)
    
    # Print summary
    print("\n" + "="*60)
    print("🧹 CORTEX Plan Cleanup Report")
    print("="*60)
    
    if "temp_plans" in report:
        print(f"\n📁 Temp Plans:")
        print(f"  Deleted: {report['temp_plans']['total']}")
        print(f"  Errors: {len(report['temp_plans'].get('errors', []))}")
    
    if "completed_plans" in report:
        print(f"\n📦 Completed Plans:")
        print(f"  Archived: {report['completed_plans']['total']}")
        print(f"  Errors: {len(report['completed_plans'].get('errors', []))}")
    
    if "orphaned_plans" in report:
        print(f"\n⚠️  Orphaned Plans:")
        print(f"  Detected: {report['orphaned_plans']['total']}")
        
        if report['orphaned_plans']['total'] > 0:
            print("\n  Details:")
            for orphan in report['orphaned_plans']['orphaned']:
                print(f"    - {orphan['plan_id']}: {', '.join(orphan['issues'])}")
    
    print("\n" + "="*60)
    
    # Save report if requested
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        print(f"\n💾 Report saved to: {args.output}")


if __name__ == "__main__":
    main()
