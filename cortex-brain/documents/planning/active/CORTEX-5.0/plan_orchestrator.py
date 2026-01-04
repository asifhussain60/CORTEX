#!/usr/bin/env python3
"""
CORTEX-5.0 Plan Orchestrator

Interactive orchestrator for managing CORTEX-5.0 gap remediation sub-plans.
Call this script repeatedly to execute phases, track progress, and manage the plan.

Usage:
    python plan_orchestrator.py               # Interactive mode
    python plan_orchestrator.py status        # Show status
    python plan_orchestrator.py next          # Execute next available phase
    python plan_orchestrator.py --sub-plan 00 # Work on specific sub-plan

Author: Asif Hussain
Created: January 3, 2026
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class PlanOrchestrator:
    """Manages CORTEX-5.0 plan execution and progress tracking."""
    
    def __init__(self, plan_root: Path):
        self.plan_root = plan_root
        self.master_plan_dir = plan_root / "00-cortex-v5-gap-remediation"
        self.tracker_file = self.master_plan_dir / "tracking" / "progress-tracker.json"
        self.state_file = plan_root / ".orchestrator-state.json"
        self.load_state()
    
    def load_state(self):
        """Load orchestrator state and progress."""
        if self.tracker_file.exists():
            with open(self.tracker_file, 'r') as f:
                self.tracker = json.load(f)
        else:
            print(f"❌ Progress tracker not found: {self.tracker_file}")
            sys.exit(1)
        
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                self.state = json.load(f)
        else:
            self.state = {
                "current_sub_plan": "00",
                "current_phase": 1,
                "session_count": 0,
                "last_updated": None,
                "milestones_achieved": [],
                "notes": []
            }
    
    def save_state(self):
        """Save orchestrator state."""
        self.state["last_updated"] = datetime.now().isoformat()
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
        
        # Also update progress tracker
        with open(self.tracker_file, 'w') as f:
            json.dump(self.tracker, f, indent=2)
    
    def show_status(self):
        """Display current plan status."""
        print("\n" + "="*80)
        print("🎯 CORTEX-5.0 Plan Orchestrator Status")
        print("="*80)
        
        # Overall progress
        overall = self.tracker["overall_progress"]
        print(f"\n📊 Overall Progress: {overall['percentage']}%")
        print(f"   Completed: {overall['completed_sub_plans']}/{overall['total_sub_plans']} sub-plans")
        print(f"   Current Phase: {overall['current_phase']}")
        print(f"   Current Sub-Plan: {overall['current_sub_plan']}")
        
        # Sub-plans status
        print("\n📋 Sub-Plans:")
        print(f"{'#':<4} {'Name':<35} {'Status':<12} {'Progress':<10} {'Duration'}")
        print("-" * 80)
        for sp in self.tracker["sub_plans"]:
            status_icon = self._get_status_icon(sp["status"])
            print(f"{sp['order']:<4} {sp['name']:<35} {status_icon} {sp['status']:<12} "
                  f"{sp['progress']:>3}% {sp['duration_estimate']:>10}")
        
        # Milestones
        print("\n🎯 Milestones:")
        for milestone in self.tracker["milestones"]:
            status = "✅" if milestone["status"] == "complete" else "⏳"
            print(f"   {status} {milestone['name']} - {milestone['target_date']}")
        
        # Metrics
        metrics = self.tracker["metrics"]
        print(f"\n📈 Metrics:")
        print(f"   Implementation: {metrics['acceptance_criteria']['implemented']}/{metrics['acceptance_criteria']['total']} "
              f"({metrics['acceptance_criteria']['implementation_rate']*100:.0f}%)")
        print(f"   Test Coverage: {metrics['acceptance_criteria']['tested']}/{metrics['acceptance_criteria']['total']} "
              f"({metrics['acceptance_criteria']['test_coverage_rate']*100:.0f}%)")
        
        # Current session
        print(f"\n🔄 Session Info:")
        print(f"   Session Count: {self.state['session_count']}")
        print(f"   Last Updated: {self.state.get('last_updated', 'Never')}")
        
        print("\n" + "="*80)
    
    def _get_status_icon(self, status: str) -> str:
        """Get icon for status."""
        icons = {
            "not_started": "⏳",
            "blocked": "⏸️",
            "in_progress": "🔄",
            "complete": "✅",
            "failed": "❌"
        }
        return icons.get(status, "❓")
    
    def get_next_available_sub_plan(self) -> Optional[Dict]:
        """Find the next sub-plan that's ready to execute."""
        for sp in self.tracker["sub_plans"]:
            if sp["status"] in ["not_started", "in_progress"]:
                # Check if dependencies are met
                if self._dependencies_met(sp):
                    return sp
        return None
    
    def _dependencies_met(self, sub_plan: Dict) -> bool:
        """Check if sub-plan dependencies are satisfied."""
        if not sub_plan["dependencies"]:
            return True  # No dependencies
        
        for dep_order in sub_plan["dependencies"]:
            dep_sp = self._get_sub_plan(dep_order)
            # Accept both "complete" and "completed" as valid completion states
            if dep_sp and dep_sp["status"] not in ["complete", "completed"]:
                return False
        return True
    
    def _get_sub_plan(self, order: str) -> Optional[Dict]:
        """Get sub-plan by order number."""
        for sp in self.tracker["sub_plans"]:
            if sp["order"] == order:
                return sp
        return None
    
    def start_sub_plan(self, order: str):
        """Start execution of a sub-plan."""
        sp = self._get_sub_plan(order)
        if not sp:
            print(f"❌ Sub-plan {order} not found")
            return
        
        if sp["status"] == "complete":
            print(f"✅ Sub-plan {order} is already complete")
            return
        
        if not self._dependencies_met(sp):
            print(f"⏸️ Sub-plan {order} is blocked by dependencies:")
            for dep in sp["dependencies"]:
                dep_sp = self._get_sub_plan(dep)
                print(f"   - Sub-Plan {dep}: {dep_sp['name']} ({dep_sp['status']})")
            return
        
        print(f"\n🚀 Starting Sub-Plan {order}: {sp['name']}")
        print(f"   Duration: {sp['duration_estimate']}")
        print(f"   Priority: {sp['priority']}")
        print(f"   Gate: {sp.get('gate', 'None')}")
        
        sp["status"] = "in_progress"
        sp["start_date"] = datetime.now().isoformat()
        
        self.state["current_sub_plan"] = order
        self.state["current_phase"] = 1
        self.save_state()
        
        print(f"\n📋 Next Steps:")
        print(f"   1. Open: {self.plan_root}/{sp['folder']}/{order}-{sp['folder'].split('-', 1)[1]}.md")
        print(f"   2. Follow phases in the sub-plan")
        print(f"   3. Update progress using: python plan_orchestrator.py update {order} <percentage>")
        print(f"   4. Complete using: python plan_orchestrator.py complete {order}")
    
    def update_progress(self, order: str, percentage: int):
        """Update progress for a sub-plan."""
        sp = self._get_sub_plan(order)
        if not sp:
            print(f"❌ Sub-plan {order} not found")
            return
        
        sp["progress"] = percentage
        
        # Update overall progress
        total_progress = sum(sp["progress"] for sp in self.tracker["sub_plans"])
        self.tracker["overall_progress"]["percentage"] = total_progress // len(self.tracker["sub_plans"])
        
        self.save_state()
        print(f"✅ Updated Sub-Plan {order} progress to {percentage}%")
        
        # Check for gate achievements
        if order == "00" and percentage >= 50:
            if "Gate 1: 50% Coverage" not in self.state["milestones_achieved"]:
                self.achieve_milestone("Gate 1: 50% Coverage")
        
        if order == "00" and percentage >= 80:
            if "Gate 2: 80% Coverage" not in self.state["milestones_achieved"]:
                self.achieve_milestone("Gate 2: 80% Coverage")
    
    def complete_sub_plan(self, order: str):
        """Mark a sub-plan as complete."""
        sp = self._get_sub_plan(order)
        if not sp:
            print(f"❌ Sub-plan {order} not found")
            return
        
        sp["status"] = "complete"
        sp["progress"] = 100
        sp["end_date"] = datetime.now().isoformat()
        
        # Update overall progress
        completed = sum(1 for sp in self.tracker["sub_plans"] if sp["status"] == "complete")
        self.tracker["overall_progress"]["completed_sub_plans"] = completed
        
        self.save_state()
        
        print(f"\n🎉 Completed Sub-Plan {order}: {sp['name']}")
        
        # Check what's now unblocked
        unblocked = []
        for other_sp in self.tracker["sub_plans"]:
            if order in other_sp.get("blocking", []) and other_sp["status"] == "blocked":
                if self._dependencies_met(other_sp):
                    other_sp["status"] = "not_started"
                    unblocked.append(other_sp)
        
        if unblocked:
            print(f"\n🔓 Unblocked Sub-Plans:")
            for sp in unblocked:
                print(f"   - Sub-Plan {sp['order']}: {sp['name']}")
    
    def achieve_milestone(self, milestone_name: str):
        """Mark a milestone as achieved."""
        for milestone in self.tracker["milestones"]:
            if milestone["name"] == milestone_name:
                milestone["status"] = "complete"
                self.state["milestones_achieved"].append(milestone_name)
                print(f"\n🎯 MILESTONE ACHIEVED: {milestone_name}")
                print(f"   Criteria: {milestone['criteria']}")
                break
    
    def add_note(self, note: str):
        """Add a note to the session."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "note": note
        }
        self.state["notes"].append(entry)
        self.save_state()
        print(f"✅ Note added")
    
    def show_notes(self):
        """Show all session notes."""
        print("\n📝 Session Notes:")
        for entry in self.state["notes"][-10:]:  # Last 10 notes
            print(f"   [{entry['timestamp']}] {entry['note']}")
    
    def interactive_mode(self):
        """Interactive orchestrator mode."""
        self.state["session_count"] += 1
        print("\n" + "="*80)
        print("🎯 CORTEX-5.0 Plan Orchestrator - Interactive Mode")
        print("="*80)
        print(f"\nSession #{self.state['session_count']}")
        
        while True:
            print("\n📋 Commands:")
            print("   1. status   - Show current status")
            print("   2. next     - Execute next available sub-plan")
            print("   3. start    - Start a specific sub-plan")
            print("   4. update   - Update sub-plan progress")
            print("   5. complete - Complete a sub-plan")
            print("   6. note     - Add a session note")
            print("   7. notes    - Show session notes")
            print("   8. exit     - Save and exit")
            
            cmd = input("\n🎯 Command: ").strip().lower()
            
            if cmd == "1" or cmd == "status":
                self.show_status()
            
            elif cmd == "2" or cmd == "next":
                next_sp = self.get_next_available_sub_plan()
                if next_sp:
                    self.start_sub_plan(next_sp["order"])
                else:
                    print("✅ No more sub-plans available. All work complete or blocked!")
            
            elif cmd == "3" or cmd == "start":
                order = input("   Sub-Plan # (00-09): ").strip()
                self.start_sub_plan(order)
            
            elif cmd == "4" or cmd == "update":
                order = input("   Sub-Plan # (00-09): ").strip()
                percentage = int(input("   Progress % (0-100): ").strip())
                self.update_progress(order, percentage)
            
            elif cmd == "5" or cmd == "complete":
                order = input("   Sub-Plan # (00-09): ").strip()
                self.complete_sub_plan(order)
            
            elif cmd == "6" or cmd == "note":
                note = input("   Note: ").strip()
                self.add_note(note)
            
            elif cmd == "7" or cmd == "notes":
                self.show_notes()
            
            elif cmd == "8" or cmd == "exit":
                self.save_state()
                print("\n✅ Progress saved. Goodbye!")
                break
            
            else:
                print("❌ Unknown command")


def main():
    """Main entry point."""
    plan_root = Path(__file__).parent
    orchestrator = PlanOrchestrator(plan_root)
    
    if len(sys.argv) == 1:
        # Interactive mode
        orchestrator.interactive_mode()
    
    elif sys.argv[1] == "status":
        orchestrator.show_status()
    
    elif sys.argv[1] == "next":
        next_sp = orchestrator.get_next_available_sub_plan()
        if next_sp:
            orchestrator.start_sub_plan(next_sp["order"])
        else:
            print("✅ No more sub-plans available!")
    
    elif sys.argv[1] == "start" and len(sys.argv) >= 3:
        orchestrator.start_sub_plan(sys.argv[2])
    
    elif sys.argv[1] == "update" and len(sys.argv) >= 4:
        orchestrator.update_progress(sys.argv[2], int(sys.argv[3]))
    
    elif sys.argv[1] == "complete" and len(sys.argv) >= 3:
        orchestrator.complete_sub_plan(sys.argv[2])
    
    else:
        print("Usage:")
        print("  python plan_orchestrator.py              # Interactive mode")
        print("  python plan_orchestrator.py status       # Show status")
        print("  python plan_orchestrator.py next         # Next sub-plan")
        print("  python plan_orchestrator.py start 00     # Start sub-plan 00")
        print("  python plan_orchestrator.py update 00 50 # Update to 50%")
        print("  python plan_orchestrator.py complete 00  # Complete sub-plan")


if __name__ == "__main__":
    main()
