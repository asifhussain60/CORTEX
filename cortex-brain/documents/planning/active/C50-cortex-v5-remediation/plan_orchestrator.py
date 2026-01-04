#!/usr/bin/env python3
"""
CORTEX Epic Plan Orchestrator - C50 Autonomous Execution Engine
================================================================

Coordinates multi-phase epic planning with dependency management,
real-time progress tracking, and HTML viewer generation.

Author: Asif Hussain
Version: 5.1.0
Date: 2026-01-04
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import yaml


class C50Orchestrator:
    """Epic-level plan orchestrator for C50 CORTEX v5 Gap Remediation."""
    
    def __init__(self, epic_root: Path):
        """Initialize orchestrator with epic root directory."""
        self.epic_root = epic_root
        self.manifest_path = epic_root / "c50-epic-manifest.yaml"
        self.progress_tracker = epic_root / "tracking" / "epic-progress-tracker.json"
        self.child_registry = epic_root / "tracking" / "child-plan-registry.json"
        self.dependency_graph = epic_root / "tracking" / "dependency-graph.json"
        
        # Load configuration
        self.manifest = self._load_manifest()
        self.progress_data = self._load_progress()
        
    def _load_manifest(self) -> Dict:
        """Load epic manifest YAML."""
        if not self.manifest_path.exists():
            raise FileNotFoundError(f"Epic manifest not found: {self.manifest_path}")
        
        with open(self.manifest_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _load_progress(self) -> Dict:
        """Load progress tracker JSON."""
        if not self.progress_tracker.exists():
            return self._initialize_progress()
        
        with open(self.progress_tracker, 'r') as f:
            return json.load(f)
    
    def _initialize_progress(self) -> Dict:
        """Initialize progress tracker from manifest."""
        print("🔧 Initializing progress tracker...")
        
        progress = {
            "epic_metadata": self.manifest["epic_metadata"],
            "overall_progress": 0,
            "child_plans": [],
            "gates": {},
            "waves": {},
            "statistics": {
                "total_plans": 0,
                "completed": 0,
                "in_progress": 0,
                "blocked": 0,
                "deferred": 0
            },
            "last_updated": datetime.now().isoformat()
        }
        
        # Convert manifest child plans to progress format
        for child in self.manifest.get("child_plans", []):
            progress["child_plans"].append({
                "id": child["id"],
                "order": child["order"],
                "name": child["name"],
                "status": "⏳ PENDING",
                "progress": 0,
                "priority": child["priority"],
                "blocking": child.get("blocking", False),
                "complexity": child["complexity"],
                "estimated_hours": child["estimated_hours"],
                "actual_hours": 0,
                "duration_estimate": child["duration_estimate"],
                "folder": child["folder"],
                "dependencies": child.get("dependencies", []),
                "dependents": [],
                "exit_criteria_met": False
            })
        
        # Calculate dependents
        for plan in progress["child_plans"]:
            for other in progress["child_plans"]:
                if plan["order"] in other["dependencies"]:
                    plan.setdefault("dependents", []).append(other["order"])
        
        self._save_progress(progress)
        return progress
    
    def _save_progress(self, progress: Dict):
        """Save progress tracker to JSON."""
        progress["last_updated"] = datetime.now().isoformat()
        
        with open(self.progress_tracker, 'w') as f:
            json.dump(progress, f, indent=2)
    
    def status(self):
        """Display epic status summary."""
        print("\n" + "=" * 70)
        print(f"📊 {self.manifest['epic_metadata']['epic_name']}")
        print("=" * 70)
        
        stats = self.progress_data.get("statistics", {})
        overall = self.progress_data.get("overall_progress", 0)
        
        # Handle both dict and number formats for overall_progress
        if isinstance(overall, dict):
            overall = overall.get("percentage", 0)
        
        print(f"\n🎯 Overall Progress: {overall}%")
        print(f"✅ Completed: {stats.get('completed', 0)}")
        print(f"🔄 In Progress: {stats.get('in_progress', 0)}")
        print(f"🔒 Blocked: {stats.get('blocked', 0)}")
        print(f"⏳ Pending: {stats.get('total_plans', 0) - stats.get('completed', 0) - stats.get('in_progress', 0) - stats.get('blocked', 0) - stats.get('deferred', 0)}")
        print(f"⏸️ Deferred: {stats.get('deferred', 0)}")
        
        print(f"\n📁 Epic Root: {self.epic_root}")
        print(f"🌐 Viewer: {self.epic_root / 'plan-viewer.html'}")
        
        # Show active plans
        active_plans = [p for p in self.progress_data.get("child_plans", []) 
                       if "PROGRESS" in p.get("status", "").upper()]
        
        if active_plans:
            print(f"\n🔄 Active Plans:")
            for plan in active_plans:
                print(f"  - C50-{plan['order']}: {plan['name']} ({plan.get('progress', 0)}%)")
        
        # Show next available plans
        available = self._get_available_plans()
        if available:
            print(f"\n🚀 Ready to Start:")
            for plan in available[:3]:  # Show top 3
                print(f"  - C50-{plan['order']}: {plan['name']}")
        
        print("\n" + "=" * 70 + "\n")
    
    def _get_available_plans(self) -> List[Dict]:
        """Get child plans ready to start (dependencies met, not started)."""
        available = []
        
        for plan in self.progress_data.get("child_plans", []):
            # Skip if already started/completed/deferred
            if plan.get("progress", 0) > 0 or "DEFERRED" in plan.get("status", ""):
                continue
            
            # Check if dependencies are met
            deps = plan.get("dependencies", [])
            if not deps:
                available.append(plan)
                continue
            
            # Check each dependency
            deps_met = True
            for dep_id in deps:
                dep_plan = next((p for p in self.progress_data["child_plans"] 
                               if p["order"] == dep_id), None)
                if not dep_plan or dep_plan.get("progress", 0) < 100:
                    deps_met = False
                    break
            
            if deps_met:
                available.append(plan)
        
        return available
    
    def start(self, child_id: str):
        """Start a child plan (if dependencies met)."""
        plan = self._find_plan(child_id)
        if not plan:
            print(f"❌ Plan not found: C50-{child_id}")
            return False
        
        # Check dependencies
        blocked = self._check_dependencies(plan)
        if blocked:
            print(f"\n❌ Cannot start C50-{child_id}: {plan['name']}")
            print(f"🔒 Blocked by: {', '.join(blocked)}")
            return False
        
        # Update status
        plan["status"] = "🔄 IN PROGRESS"
        plan["started_at"] = datetime.now().isoformat()
        
        self._recalculate_statistics()
        self._save_progress(self.progress_data)
        
        plan_file = f"00-{plan['id']}.md"
        print(f"\n✅ Started C50-{child_id}: {plan['name']}")
        print(f"📁 Folder: {self.epic_root / plan['folder']}")
        print(f"📄 Plan: {self.epic_root / plan['folder'] / plan_file}")
        
        return True
    
    def _find_plan(self, child_id: str) -> Optional[Dict]:
        """Find child plan by order ID or full ID."""
        # Try order ID first
        plan = next((p for p in self.progress_data["child_plans"] 
                    if p["order"] == child_id), None)
        
        # If not found, try full ID
        if not plan:
            plan = next((p for p in self.progress_data["child_plans"] 
                        if p["id"] == child_id), None)
        
        return plan
    
    def _check_dependencies(self, plan: Dict) -> List[str]:
        """Check if plan dependencies are met. Returns list of blocking plans."""
        blocked_by = []
        
        for dep_id in plan.get("dependencies", []):
            dep_plan = self._find_plan(dep_id)
            if not dep_plan:
                blocked_by.append(dep_id)
                continue
            
            if dep_plan.get("progress", 0) < 100:
                blocked_by.append(f"C50-{dep_id} ({dep_plan.get('progress', 0)}%)")
        
        return blocked_by
    
    def check(self, child_id: str):
        """Check if a child plan can be started."""
        plan = self._find_plan(child_id)
        if not plan:
            print(f"❌ Plan not found: C50-{child_id}")
            return
        
        print(f"\n📋 C50-{plan.get('order', child_id)}: {plan['name']}")
        print(f"📊 Status: {plan.get('status', 'unknown')}")
        print(f"📈 Progress: {plan.get('progress', 0)}%")
        
        if 'estimated_hours' in plan:
            print(f"⏱️ Estimated: {plan['estimated_hours']}h")
        
        if 'complexity' in plan:
            print(f"🔧 Complexity: {plan['complexity']}")
        
        if 'priority' in plan:
            print(f"🎯 Priority: {plan['priority']}")
        
        # Dependencies
        deps = plan.get("dependencies", [])
        if deps:
            print(f"\n📌 Dependencies:")
            for dep_id in deps:
                dep_plan = self._find_plan(dep_id)
                if dep_plan:
                    status_icon = "✅" if dep_plan.get("progress", 0) == 100 else "❌"
                    print(f"  {status_icon} C50-{dep_id}: {dep_plan['name']} ({dep_plan.get('progress', 0)}%)")
        else:
            print("\n📌 No dependencies")
        
        # Dependents
        dependents = plan.get("dependents", [])
        if dependents:
            print(f"\n🔗 Blocks:")
            for dep_id in dependents:
                dep_plan = self._find_plan(dep_id)
                if dep_plan:
                    print(f"  - C50-{dep_id}: {dep_plan['name']}")
        
        # Can start?
        blocked = self._check_dependencies(plan)
        if blocked:
            print(f"\n🔒 BLOCKED by: {', '.join(blocked)}")
        elif plan.get("progress", 0) == 0:
            print(f"\n🚀 READY TO START")
        elif plan.get("progress", 0) == 100:
            print(f"\n✅ COMPLETE")
        else:
            print(f"\n🔄 IN PROGRESS")
    
    def _recalculate_statistics(self):
        """Recalculate epic statistics."""
        stats = {
            "total_plans": len(self.progress_data["child_plans"]),
            "completed": 0,
            "in_progress": 0,
            "blocked": 0,
            "deferred": 0,
            "pending": 0
        }
        
        total_progress = 0
        
        for plan in self.progress_data["child_plans"]:
            status = plan.get("status", "").upper()
            progress = plan.get("progress", 0)
            
            total_progress += progress
            
            if progress == 100 or "COMPLETE" in status:
                stats["completed"] += 1
            elif "PROGRESS" in status:
                stats["in_progress"] += 1
            elif "BLOCKED" in status:
                stats["blocked"] += 1
            elif "DEFERRED" in status:
                stats["deferred"] += 1
            else:
                stats["pending"] += 1
        
        # Calculate overall progress (excluding deferred)
        active_plans = stats["total_plans"] - stats["deferred"]
        if active_plans > 0:
            self.progress_data["overall_progress"] = round(total_progress / active_plans, 1)
        
        self.progress_data["statistics"] = stats
    
    def validate_dependencies(self):
        """Validate all dependency chains."""
        print("\n🔍 Validating dependency graph...")
        
        errors = []
        warnings = []
        
        for plan in self.progress_data["child_plans"]:
            # Check for missing dependencies
            for dep_id in plan.get("dependencies", []):
                if not self._find_plan(dep_id):
                    errors.append(f"C50-{plan['order']}: Missing dependency {dep_id}")
            
            # Check for circular dependencies
            if self._has_circular_dependency(plan):
                errors.append(f"C50-{plan['order']}: Circular dependency detected")
            
            # Check for orphaned plans (no dependents, not final)
            if not plan.get("dependents") and plan.get("dependencies"):
                warnings.append(f"C50-{plan['order']}: No dependents (potential orphan)")
        
        if errors:
            print(f"\n❌ Errors found:")
            for error in errors:
                print(f"  - {error}")
        
        if warnings:
            print(f"\n⚠️ Warnings:")
            for warning in warnings:
                print(f"  - {warning}")
        
        if not errors and not warnings:
            print("✅ All dependencies valid!")
        
        return len(errors) == 0
    
    def _has_circular_dependency(self, plan: Dict, visited: Optional[set] = None) -> bool:
        """Check for circular dependencies (DFS)."""
        if visited is None:
            visited = set()
        
        if plan["order"] in visited:
            return True
        
        visited.add(plan["order"])
        
        for dep_id in plan.get("dependencies", []):
            dep_plan = self._find_plan(dep_id)
            if dep_plan and self._has_circular_dependency(dep_plan, visited.copy()):
                return True
        
        return False
    
    def generate_viewer(self):
        """Regenerate plan-viewer.html with latest data."""
        print("🎨 Generating plan viewer HTML...")
        
        viewer_path = self.epic_root / "plan-viewer.html"
        
        if not viewer_path.exists():
            print(f"⚠️ Viewer template not found: {viewer_path}")
            print("Please ensure plan-viewer.html exists in epic root.")
            return False
        
        print(f"✅ Viewer exists: {viewer_path}")
        print(f"📊 Data source: {self.progress_tracker}")
        print("\n🌐 Open in browser:")
        print(f"   file://{viewer_path.absolute()}")
        
        return True


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="C50 Epic Plan Orchestrator - Autonomous Execution Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 plan_orchestrator.py status
  python3 plan_orchestrator.py start 00B
  python3 plan_orchestrator.py check 00C
  python3 plan_orchestrator.py validate-dependencies
        """
    )
    
    parser.add_argument(
        "command",
        choices=["status", "start", "check", "validate-dependencies", "generate-viewer"],
        help="Command to execute"
    )
    
    parser.add_argument(
        "child_id",
        nargs="?",
        help="Child plan ID (e.g., 00B, 01, 02)"
    )
    
    parser.add_argument(
        "--epic-root",
        default=".",
        help="Epic root directory (default: current directory)"
    )
    
    args = parser.parse_args()
    
    # Initialize orchestrator
    epic_root = Path(args.epic_root).resolve()
    
    try:
        orchestrator = C50Orchestrator(epic_root)
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    
    # Execute command
    try:
        if args.command == "status":
            orchestrator.status()
        
        elif args.command == "start":
            if not args.child_id:
                print("❌ Error: child_id required for 'start' command")
                sys.exit(1)
            orchestrator.start(args.child_id)
        
        elif args.command == "check":
            if not args.child_id:
                print("❌ Error: child_id required for 'check' command")
                sys.exit(1)
            orchestrator.check(args.child_id)
        
        elif args.command == "validate-dependencies":
            if not orchestrator.validate_dependencies():
                sys.exit(1)
        
        elif args.command == "generate-viewer":
            if not orchestrator.generate_viewer():
                sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ Execution error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
