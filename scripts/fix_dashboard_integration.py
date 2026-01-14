#!/usr/bin/env python3
"""
Fix Dashboard Integration - Reconcile plan-viewer.html with actual data structures

Purpose: 
  - Repair progress-tracker.json AC counts from master-plan.yaml
  - Ensure plan-viewer.html correctly parses tracker data
  - Validate data integrity before dashboard rendering

Version: 1.0.0 | Date: 2026-01-13
Author: Asif Hussain
"""

import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

class DashboardIntegrationFixer:
    def __init__(self, project_root: str = "/Users/asifhussain/PROJECTS/CORTEX"):
        self.project_root = Path(project_root)
        self.tracker_path = self.project_root / "cortex-brain/tier1/tracking/progress-tracker.json"
        self.plan_path = self.project_root / "cortex-brain/cx6-plan/master-plan.yaml"
        self.ac_index_path = self.project_root / "cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml"
        
        self.tracker = None
        self.plan = None
        self.ac_index = None
        
        print("\n" + "="*80)
        print("🔧 DASHBOARD INTEGRATION FIXER v1.0")
        print("="*80 + "\n")
    
    def load_files(self) -> bool:
        """Load all required SSOT files"""
        try:
            print("📂 Loading SSOT files...")
            
            # Load tracker
            with open(self.tracker_path) as f:
                self.tracker = json.load(f)
            print(f"  ✅ progress-tracker.json ({len(self.tracker.get('phases', {}))} phases)")
            
            # Load master plan
            with open(self.plan_path) as f:
                self.plan = yaml.safe_load(f)
            print(f"  ✅ master-plan.yaml ({len(self.plan.get('phases', {}))} phases)")
            
            # Load AC index
            with open(self.ac_index_path) as f:
                self.ac_index = yaml.safe_load(f)
            print(f"  ✅ AC-INDEX.yaml ({len(self.ac_index)} ACs)")
            
            return True
        except Exception as e:
            print(f"  ❌ Failed to load files: {e}")
            return False
    
    def analyze_structure_mismatch(self) -> Dict[str, Any]:
        """Identify mismatches between tracker and plan"""
        issues = {
            "phases_in_tracker": list(self.tracker.get("phases", {}).keys()),
            "phases_in_plan": list(self.plan.get("phases", {}).keys()),
            "zero_ac_counts": [],
            "missing_from_plan": [],
            "missing_from_tracker": []
        }
        
        # Find phases with zero AC counts
        for phase_key, phase_data in self.tracker.get("phases", {}).items():
            if (phase_data.get("total_ac_count") == 0 or phase_data.get("total_ac_count") is None) and \
               (phase_data.get("acs_total", 0) > 0 or phase_data.get("completed_ac_count", 0) > 0):
                issues["zero_ac_counts"].append(phase_key)
        
        # Find phases in tracker but not in plan
        tracker_phases = set(self.tracker.get("phases", {}).keys())
        plan_phases = set(self.plan.get("phases", {}).keys())
        issues["missing_from_plan"] = list(tracker_phases - plan_phases)
        issues["missing_from_tracker"] = list(plan_phases - tracker_phases)
        
        return issues
    
    def repair_ac_counts(self) -> Dict[str, Dict[str, int]]:
        """Repair AC counts from master-plan.yaml"""
        print("\n📊 REPAIRING AC COUNTS FROM MASTER-PLAN\n")
        
        repairs = {}
        
        for phase_key, phase_data in self.plan.get("phases", {}).items():
            ac_ids = phase_data.get("ac_ids", [])
            completed_count = phase_data.get("completed_ac_count", 0)
            total_ac_count = len(ac_ids)
            
            # Find matching phase in tracker
            if phase_key in self.tracker.get("phases", {}):
                tracker_phase = self.tracker["phases"][phase_key]
                
                # Update counts
                old_total = tracker_phase.get("total_ac_count", 0)
                old_completed = tracker_phase.get("completed_count", 0)
                
                # Use values from plan
                tracker_phase["total_ac_count"] = total_ac_count
                tracker_phase["completed_count"] = completed_count
                tracker_phase["ac_ids"] = ac_ids  # Store AC list for debugging
                
                # Calculate percentage
                percentage = (completed_count / total_ac_count * 100) if total_ac_count > 0 else 0
                tracker_phase["completion_percentage"] = round(percentage, 1)
                
                repairs[phase_key] = {
                    "old_total": old_total,
                    "new_total": total_ac_count,
                    "old_completed": old_completed,
                    "new_completed": completed_count,
                    "percentage": round(percentage, 1)
                }
                
                print(f"  {phase_key:12} | {old_total:2} → {total_ac_count:2} total | "
                      f"{old_completed:2} → {completed_count:2} completed | {percentage:5.1f}%")
        
        return repairs
    
    def validate_data_integrity(self) -> bool:
        """Validate tracker data before saving"""
        print("\n✅ VALIDATING DATA INTEGRITY\n")
        
        all_valid = True
        total_acs = 0
        total_completed = 0
        
        for phase_key, phase_data in self.tracker.get("phases", {}).items():
            total = phase_data.get("total_ac_count", 0)
            completed = phase_data.get("completed_count", 0)
            
            # Validate counts
            if total < 0 or completed < 0:
                print(f"  ❌ {phase_key}: Negative counts detected")
                all_valid = False
            
            if completed > total:
                print(f"  ❌ {phase_key}: Completed ({completed}) > Total ({total})")
                all_valid = False
            
            # Check for null/missing values
            if total is None:
                print(f"  ❌ {phase_key}: total_ac_count is None")
                all_valid = False
            
            total_acs += total
            total_completed += completed
        
        print(f"  ✅ Total ACs: {total_acs}")
        print(f"  ✅ Total Completed: {total_completed}")
        print(f"  ✅ Overall: {total_completed}/{total_acs} ({total_completed/total_acs*100:.1f}%)")
        
        return all_valid
    
    def update_tracker_metadata(self):
        """Update tracker metadata with fix timestamp"""
        self.tracker["last_updated"] = datetime.utcnow().isoformat() + "+00:00"
        self.tracker["updated_by"] = "DashboardIntegrationFixer v1.0"
        
        if "recent_fixes" not in self.tracker.get("active_epic", {}):
            self.tracker["active_epic"]["recent_fixes"] = []
        
        self.tracker["active_epic"]["recent_fixes"].insert(0,
            f"{datetime.utcnow().isoformat()}Z: Dashboard Integration Fix - AC counts repaired from master-plan.yaml"
        )
    
    def save_tracker(self) -> bool:
        """Save repaired tracker to disk"""
        try:
            print("\n💾 SAVING REPAIRED TRACKER\n")
            
            # Update metadata
            self.update_tracker_metadata()
            
            # Write with pretty formatting
            with open(self.tracker_path, 'w') as f:
                json.dump(self.tracker, f, indent=2)
            
            print(f"  ✅ Saved to {self.tracker_path}")
            return True
        except Exception as e:
            print(f"  ❌ Failed to save: {e}")
            return False
    
    def generate_report(self):
        """Generate summary report"""
        print("\n" + "="*80)
        print("📋 DASHBOARD INTEGRATION FIX REPORT")
        print("="*80 + "\n")
        
        # Summary
        total_acs = sum(p.get("total_ac_count", 0) for p in self.tracker.get("phases", {}).values())
        total_completed = sum(p.get("completed_count", 0) for p in self.tracker.get("phases", {}).values())
        
        print(f"✅ OUTCOMES\n")
        print(f"• AC counts repaired from master-plan.yaml for all phases")
        print(f"• Total ACs across all phases: {total_acs}")
        print(f"• Total completed: {total_completed} ({total_completed/total_acs*100:.1f}%)")
        print(f"• Data integrity validated")
        print(f"• Tracker metadata updated with fix timestamp\n")
        
        print(f"📊 PHASE STATUS AFTER FIX\n")
        for phase_key in sorted(self.tracker.get("phases", {}).keys(), 
                                key=lambda x: (int(x.split('_')[1].split('.')[0]), 
                                             float(x.split('_')[1].split('.')[1]) if '.' in x.split('_')[1] else 0)):
            phase = self.tracker["phases"][phase_key]
            total = phase.get("total_ac_count", 0)
            completed = phase.get("completed_count", 0)
            pct = (completed / total * 100) if total > 0 else 0
            
            print(f"• {phase_key:12} | {completed:3}/{total:3} ACs ({pct:5.1f}%) | "
                  f"Status: {phase.get('status', 'unknown')}")
        
        print(f"\n🎯 NEXT STEPS\n")
        print(f"1. Open plan-viewer.html in browser (serve via HTTP)")
        print(f"2. Verify dashboard loads without errors")
        print(f"3. Check that phase cards display correct AC counts")
        print(f"4. Confirm auto-refresh works every 2 seconds\n")
        
        print("="*80 + "\n")
    
    def run(self):
        """Execute full repair workflow"""
        # Step 1: Load files
        if not self.load_files():
            return False
        
        # Step 2: Analyze structure
        print("\n🔍 ANALYZING STRUCTURE\n")
        issues = self.analyze_structure_mismatch()
        print(f"  Phases in tracker: {len(issues['phases_in_tracker'])}")
        print(f"  Phases in plan: {len(issues['phases_in_plan'])}")
        print(f"  Phases with zero AC counts: {len(issues['zero_ac_counts'])}")
        if issues['missing_from_plan']:
            print(f"  ⚠️  Missing from plan: {issues['missing_from_plan']}")
        if issues['missing_from_tracker']:
            print(f"  ⚠️  Missing from tracker: {issues['missing_from_tracker']}")
        
        # Step 3: Repair AC counts
        repairs = self.repair_ac_counts()
        
        # Step 4: Validate
        if not self.validate_data_integrity():
            print("\n❌ Validation failed. Aborting save.")
            return False
        
        # Step 5: Save
        if not self.save_tracker():
            return False
        
        # Step 6: Report
        self.generate_report()
        
        return True


if __name__ == "__main__":
    fixer = DashboardIntegrationFixer()
    success = fixer.run()
    exit(0 if success else 1)
