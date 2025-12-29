"""
Plan Realignment CLI - Migrate Plans to Canonical Structure

Realigns plans to conform to Planning System 3.0 canonical structure:
- WP## naming for worker plans
- execution/ subfolder for YAML files
- context/ subfolder for AST/Lens graphs
- Standard task injection verification

Author: Asif Hussain
Date: December 17, 2025
Version: 1.0.0
"""

import sys
import logging
from pathlib import Path
from typing import List, Dict, Any
import json
import shutil
import re

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

logger = logging.getLogger(__name__)


class PlanRealignmentEngine:
    """
    Migrates old-format plans to Planning System 3.0 canonical structure.
    
    Migrations:
    - Rename sub-plans to WP##-Phase-Name.md format
    - Move execution YAML files to execution/ subfolder
    - Move context graphs to context/ subfolder
    - Validate standard task presence
    """
    
    def __init__(self, project_root: Path):
        """
        Initialize realignment engine.
        
        Args:
            project_root: Root directory of CORTEX project
        """
        self.project_root = Path(project_root)
        self.planning_root = self.project_root / "cortex-brain" / "documents" / "planning"
        
        # Folder paths
        self.active_folder = self.planning_root / "active"
        self.completed_folder = self.planning_root / "completed"
    
    def realign_plan(self, plan_id: str, dry_run: bool = False) -> Dict[str, Any]:
        """
        Realign specific plan to canonical structure.
        
        Args:
            plan_id: Plan identifier
            dry_run: If True, don't actually modify (report only)
            
        Returns:
            Realignment report
        """
        logger.info(f"🔧 Realigning plan: {plan_id}")
        
        # Find plan folder
        plan_folder = None
        for folder in [self.active_folder, self.completed_folder]:
            candidate = folder / plan_id
            if candidate.exists():
                plan_folder = candidate
                break
        
        if not plan_folder:
            return {
                "plan_id": plan_id,
                "status": "not_found",
                "changes": []
            }
        
        changes = []
        
        # 1. Rename sub-plans to WP## format
        sub_plan_changes = self._realign_worker_plans(plan_folder, dry_run)
        changes.extend(sub_plan_changes)
        
        # 2. Create execution/ subfolder
        execution_changes = self._create_execution_folder(plan_folder, dry_run)
        changes.extend(execution_changes)
        
        # 3. Create context/ subfolder
        context_changes = self._create_context_folder(plan_folder, dry_run)
        changes.extend(context_changes)
        
        # 4. Validate standard tasks (report only)
        task_validation = self._validate_standard_tasks(plan_folder)
        if task_validation:
            changes.append(task_validation)
        
        return {
            "plan_id": plan_id,
            "status": "realigned" if not dry_run else "would_realign",
            "changes": changes,
            "total_changes": len(changes)
        }
    
    def _realign_worker_plans(self, plan_folder: Path, dry_run: bool) -> List[Dict[str, Any]]:
        """Rename worker plans to WP## format."""
        changes = []
        
        # Find all MD files that aren't master-plan.md
        worker_plans = [f for f in plan_folder.glob("*.md") if f.name != "master-plan.md"]
        
        for idx, plan_file in enumerate(sorted(worker_plans), start=1):
            # Check if already in WP## format
            if re.match(r'^WP\d{2}-', plan_file.name):
                continue  # Already correct format
            
            # Generate new name
            phase_name = plan_file.stem.replace("-", " ").title().replace(" ", "-")
            new_name = f"WP{idx:02d}-{phase_name}.md"
            new_path = plan_folder / new_name
            
            if not dry_run:
                plan_file.rename(new_path)
            
            changes.append({
                "type": "rename_worker_plan",
                "old": plan_file.name,
                "new": new_name,
                "applied": not dry_run
            })
            
            logger.info(f"  {'Would rename' if dry_run else 'Renamed'}: {plan_file.name} → {new_name}")
        
        return changes
    
    def _create_execution_folder(self, plan_folder: Path, dry_run: bool) -> List[Dict[str, Any]]:
        """Create execution/ subfolder and move YAML files."""
        changes = []
        
        execution_folder = plan_folder / "execution"
        
        # Find all YAML files in root
        yaml_files = list(plan_folder.glob("*.yaml")) + list(plan_folder.glob("*.yml"))
        
        if not yaml_files:
            return changes
        
        # Create execution folder if needed
        if not execution_folder.exists():
            if not dry_run:
                execution_folder.mkdir(parents=True, exist_ok=True)
            
            changes.append({
                "type": "create_folder",
                "folder": "execution/",
                "applied": not dry_run
            })
            
            logger.info(f"  {'Would create' if dry_run else 'Created'}: execution/")
        
        # Move YAML files
        for yaml_file in yaml_files:
            target = execution_folder / yaml_file.name
            
            if not dry_run:
                yaml_file.rename(target)
            
            changes.append({
                "type": "move_execution_file",
                "file": yaml_file.name,
                "destination": "execution/",
                "applied": not dry_run
            })
            
            logger.info(f"  {'Would move' if dry_run else 'Moved'}: {yaml_file.name} → execution/")
        
        return changes
    
    def _create_context_folder(self, plan_folder: Path, dry_run: bool) -> List[Dict[str, Any]]:
        """Create context/ subfolder and move analysis files."""
        changes = []
        
        context_folder = plan_folder / "context"
        
        # Find analysis files
        analysis_patterns = ["*ast*.json", "*lens*.json", "*analysis*.json", "*dependencies*.json"]
        analysis_files = []
        for pattern in analysis_patterns:
            analysis_files.extend(plan_folder.glob(pattern))
        
        if not analysis_files:
            return changes
        
        # Create context folder if needed
        if not context_folder.exists():
            if not dry_run:
                context_folder.mkdir(parents=True, exist_ok=True)
            
            changes.append({
                "type": "create_folder",
                "folder": "context/",
                "applied": not dry_run
            })
            
            logger.info(f"  {'Would create' if dry_run else 'Created'}: context/")
        
        # Move analysis files
        for analysis_file in analysis_files:
            target = context_folder / analysis_file.name
            
            if not dry_run:
                analysis_file.rename(target)
            
            changes.append({
                "type": "move_context_file",
                "file": analysis_file.name,
                "destination": "context/",
                "applied": not dry_run
            })
            
            logger.info(f"  {'Would move' if dry_run else 'Moved'}: {analysis_file.name} → context/")
        
        return changes
    
    def _validate_standard_tasks(self, plan_folder: Path) -> Dict[str, Any]:
        """Validate standard tasks present in worker plans."""
        missing_tasks = []
        
        worker_plans = list(plan_folder.glob("WP*.md"))
        
        for worker_plan in worker_plans:
            with open(worker_plan, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for standard task indicators
            required_tasks = [
                ("git_checkpoint_start", r"Git Checkpoint.*Start", "Git checkpoint at phase start"),
                ("git_checkpoint_end", r"Git Checkpoint.*(?:End|Complete)", "Git checkpoint at phase end"),
                ("ast_lens", r"AST.*Lens.*Analysis", "AST/Lens analysis"),
                ("documentation", r"Update Documentation", "Documentation updates"),
                ("tdd_validation", r"TDD Validation", "TDD validation"),
                ("dod_validation", r"DoD Validation", "DoD validation")
            ]
            
            plan_missing = []
            for task_id, pattern, description in required_tasks:
                if not re.search(pattern, content, re.IGNORECASE):
                    plan_missing.append({
                        "task_id": task_id,
                        "description": description
                    })
            
            if plan_missing:
                missing_tasks.append({
                    "worker_plan": worker_plan.name,
                    "missing_tasks": plan_missing
                })
        
        if missing_tasks:
            return {
                "type": "validation_warning",
                "issue": "missing_standard_tasks",
                "details": missing_tasks,
                "recommendation": "Regenerate worker plans with TaskInjector"
            }
        
        return None
    
    def realign_all_plans(self, dry_run: bool = False) -> Dict[str, Any]:
        """
        Realign all plans in active/ and completed/ folders.
        
        Args:
            dry_run: If True, don't actually modify (report only)
            
        Returns:
            Comprehensive realignment report
        """
        logger.info("🔧 Realigning all plans...")
        
        results = []
        
        for folder in [self.active_folder, self.completed_folder]:
            if not folder.exists():
                continue
            
            for plan_folder in folder.iterdir():
                if not plan_folder.is_dir():
                    continue
                
                result = self.realign_plan(plan_folder.name, dry_run=dry_run)
                results.append(result)
        
        return {
            "total_plans": len(results),
            "realigned": sum(1 for r in results if r["status"] == "realigned"),
            "would_realign": sum(1 for r in results if r["status"] == "would_realign"),
            "not_found": sum(1 for r in results if r["status"] == "not_found"),
            "total_changes": sum(r["total_changes"] for r in results),
            "details": results
        }


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="CORTEX Plan Realignment Utility")
    parser.add_argument("--plan-id", type=str, help="Realign specific plan (optional)")
    parser.add_argument("--dry-run", action="store_true", help="Report only, don't actually realign")
    parser.add_argument("--output", type=str, help="Save report to file (JSON)")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    
    # Initialize engine
    engine = PlanRealignmentEngine(project_root)
    
    # Realign
    if args.plan_id:
        report = engine.realign_plan(args.plan_id, dry_run=args.dry_run)
        reports = [report]
    else:
        full_report = engine.realign_all_plans(dry_run=args.dry_run)
        report = full_report
        reports = full_report.get("details", [])
    
    # Print summary
    print("\n" + "="*60)
    print("🔧 CORTEX Plan Realignment Report")
    print("="*60)
    
    if args.plan_id:
        print(f"\nPlan: {report['plan_id']}")
        print(f"Status: {report['status']}")
        print(f"Changes: {report['total_changes']}")
        
        if report['changes']:
            print("\nDetails:")
            for change in report['changes']:
                if change['type'] == 'rename_worker_plan':
                    print(f"  📄 {change['old']} → {change['new']}")
                elif change['type'] == 'create_folder':
                    print(f"  📁 Created: {change['folder']}")
                elif change['type'] == 'move_execution_file':
                    print(f"  📋 Moved {change['file']} → {change['destination']}")
                elif change['type'] == 'move_context_file':
                    print(f"  🔍 Moved {change['file']} → {change['destination']}")
                elif change['type'] == 'validation_warning':
                    print(f"  ⚠️  {change['issue']}: {len(change['details'])} worker plans")
    else:
        print(f"\nTotal Plans: {report['total_plans']}")
        print(f"Realigned: {report['realigned']}")
        if args.dry_run:
            print(f"Would Realign: {report['would_realign']}")
        print(f"Total Changes: {report['total_changes']}")
        
        if reports:
            print("\nPer-Plan Summary:")
            for r in reports:
                if r['total_changes'] > 0:
                    print(f"  {r['plan_id']}: {r['total_changes']} changes")
    
    print("\n" + "="*60)
    
    # Save report if requested
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        print(f"\n💾 Report saved to: {args.output}")


if __name__ == "__main__":
    main()
