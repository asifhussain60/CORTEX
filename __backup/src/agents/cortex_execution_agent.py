#!/usr/bin/env python3
"""
CORTEX Execution Agent v1.0.0
Purpose: Autonomous executor for master-plan.yaml with SSOT enforcement
Author: Asif Hussain
Date: 2026-01-13
Copyright © 2025-2026 Asif Hussain. All rights reserved.

Design Philosophy:
- Execute phases sequentially with 100% gates
- Maintain SSOT sync (master-plan + progress-tracker + dashboard)
- Validate evidence via audit trail (≥80% verification rate)
- Enforce governance rules (19 SKULL rules)
"""

import json
import yaml
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple


class SSotManager:
    """Manages SSOT file operations (read-only for most files)"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.master_plan_path = project_root / "cortex-brain/cx6-plan/master-plan.yaml"
        self.tracker_path = project_root / "cortex-brain/tier1/tracking/progress-tracker.json"
        self.ac_index_path = project_root / "cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml"
        self.core_rules_path = project_root / "cortex-brain/tier0/governance/core-rules.yaml"
        self.viewer_data_path = project_root / "cortex-brain/cx6-plan/viewer/plan-viewer-data.json"
    
    def load_master_plan(self) -> Dict:
        """Load architecture SSOT"""
        if not self.master_plan_path.exists():
            raise FileNotFoundError(f"SSOT missing: {self.master_plan_path}")
        return yaml.safe_load(self.master_plan_path.read_text())
    
    def load_progress_tracker(self) -> Dict:
        """Load execution SSOT"""
        if not self.tracker_path.exists():
            raise FileNotFoundError(f"SSOT missing: {self.tracker_path}")
        return json.loads(self.tracker_path.read_text())
    
    def load_ac_index(self) -> Dict:
        """Load acceptance criteria SSOT"""
        if not self.ac_index_path.exists():
            raise FileNotFoundError(f"SSOT missing: {self.ac_index_path}")
        return yaml.safe_load(self.ac_index_path.read_text())
    
    def load_core_rules(self) -> Dict:
        """Load governance SSOT"""
        if not self.core_rules_path.exists():
            raise FileNotFoundError(f"SSOT missing: {self.core_rules_path}")
        return yaml.safe_load(self.core_rules_path.read_text())
    
    def load_viewer_data(self) -> Dict:
        """Load derived dashboard data"""
        if not self.viewer_data_path.exists():
            raise FileNotFoundError(f"Dashboard data missing: {self.viewer_data_path}")
        return json.loads(self.viewer_data_path.read_text())


class EvidenceValidator:
    """Validates test evidence via audit trail"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.validator_script = project_root / "scripts/audit_based_evidence_validator.py"
        self.results_path = project_root / "cortex-brain/documents/validation/evidence-validation-results.json"
    
    def validate(self) -> Tuple[float, Dict]:
        """
        Run evidence validator and return (verification_rate, results)
        
        Returns:
            (verification_rate, results_dict)
        
        Raises:
            RuntimeError if validation fails
        """
        if not self.validator_script.exists():
            raise FileNotFoundError(f"Validator script missing: {self.validator_script}")
        
        # Run validator
        result = subprocess.run(
            [sys.executable, str(self.validator_script)],
            cwd=self.project_root,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Evidence validation failed: {result.stderr}")
        
        # Load results
        if not self.results_path.exists():
            raise FileNotFoundError(f"Validation results missing: {self.results_path}")
        
        results = json.loads(self.results_path.read_text())
        verification_rate = results['summary']['verification_rate']
        
        return verification_rate, results


class DashboardSyncer:
    """Syncs dashboard from SSOT (master-plan + progress-tracker)"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.sync_script = project_root / "scripts/regenerate_plan_viewer_data.py"
    
    def sync(self) -> bool:
        """
        Sync dashboard data from SSOT
        
        Returns:
            True if sync succeeded, False otherwise
        """
        if not self.sync_script.exists():
            raise FileNotFoundError(f"Sync script missing: {self.sync_script}")
        
        result = subprocess.run(
            [sys.executable, str(self.sync_script)],
            cwd=self.project_root,
            capture_output=True,
            text=True
        )
        
        return result.returncode == 0


class CortexExecutionAgent:
    """Autonomous execution agent for CORTEX 6.0"""
    
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path.cwd()
        self.ssot = SSotManager(self.project_root)
        self.evidence_validator = EvidenceValidator(self.project_root)
        self.dashboard_syncer = DashboardSyncer(self.project_root)
    
    def get_current_state(self) -> Dict:
        """Load current execution state from SSOT"""
        tracker = self.ssot.load_progress_tracker()
        master_plan = self.ssot.load_master_plan()
        ac_index = self.ssot.load_ac_index()
        
        return {
            "tracker": tracker,
            "master_plan": master_plan,
            "ac_index": ac_index,
            "current_phase": tracker["current_phase"],
            "active_epic": tracker.get("active_epic", {})
        }
    
    def get_ac_title(self, ac_id: str) -> str:
        """Get human-readable title for AC-ID"""
        try:
            ac_index = self.ssot.load_ac_index()
            return ac_index.get("ac_ids", {}).get(ac_id, {}).get("title", ac_id)
        except Exception:
            return ac_id
    
    def validate_evidence_gate(self) -> Tuple[bool, float]:
        """
        Validate evidence for completed AC-IDs
        
        Returns:
            (gate_passed, verification_rate)
        """
        print("🔍 Validating evidence via audit trail...")
        
        try:
            verification_rate, results = self.evidence_validator.validate()
            
            if verification_rate >= 80.0:
                print(f"✅ GATE PASSED: Verification rate {verification_rate:.1f}%")
                return True, verification_rate
            else:
                print(f"❌ BLOCKED: Verification rate {verification_rate:.1f}% < 80%")
                print("Fix false positives before proceeding")
                return False, verification_rate
        
        except Exception as e:
            print(f"⚠️ Evidence validation error: {e}")
            return False, 0.0
    
    def get_incomplete_ac_ids(self, state: Dict) -> List[str]:
        """Get list of incomplete AC-IDs for current phase"""
        current_phase = state["current_phase"]
        phase_number = current_phase["number"]
        
        # Get all AC-IDs for current phase from master-plan
        master_plan = state["master_plan"]
        
        # Try different phase key formats
        phase_key_formats = [
            f"phase_{phase_number}_orchestration_core",
            f"phase_{phase_number}",
            f"phase{phase_number}",
        ]
        
        phase_data = None
        for key_format in phase_key_formats:
            phase_data = master_plan.get(key_format, {})
            if phase_data:
                break
        
        if not phase_data:
            # Try searching in nested structure
            print(f"⚠️ Phase {phase_number} definition not found in master-plan.yaml")
            print(f"   Tried keys: {phase_key_formats}")
            
            # Fallback: get AC-IDs from components if available
            components = phase_data.get("components", {}) if phase_data else {}
            if components:
                ac_ids_from_components = []
                for component_name, component_data in components.items():
                    ac_ids_from_components.extend(component_data.get("ac_ids", []))
                
                if ac_ids_from_components:
                    # Check which are incomplete
                    tracker = state["tracker"]
                    completed = self._get_completed_ac_ids(tracker)
                    return [ac_id for ac_id in ac_ids_from_components if ac_id not in completed]
            
            return []
        
        # Get AC-IDs from components
        components = phase_data.get("components", {})
        all_ac_ids = []
        
        for component_name, component_data in components.items():
            component_ac_ids = component_data.get("ac_ids", [])
            all_ac_ids.extend(component_ac_ids)
        
        # Get completed AC-IDs from tracker
        tracker = state["tracker"]
        completed = self._get_completed_ac_ids(tracker)
        
        # Return incomplete AC-IDs
        incomplete = [ac_id for ac_id in all_ac_ids if ac_id not in completed]
        
        return incomplete
    
    def _get_completed_ac_ids(self, tracker: Dict) -> set:
        """Extract all completed AC-IDs from tracker"""
        completed = set()
        
        # Scan all phases in tracker for completed AC-IDs
        for phase_key, phase_state in tracker.items():
            if not isinstance(phase_state, dict):
                continue
            
            # Check if phase_state has ac_ids
            ac_ids_data = phase_state.get("ac_ids", {})
            
            # Handle both dict and list formats
            if isinstance(ac_ids_data, dict):
                for ac_id, ac_data in ac_ids_data.items():
                    if isinstance(ac_data, dict) and ac_data.get("status") == "implemented":
                        completed.add(ac_id)
            elif isinstance(ac_ids_data, list):
                # If ac_ids is a list, those are AC-ID strings
                # Check status separately
                for ac_id in ac_ids_data:
                    if isinstance(ac_id, str):
                        # Look for status elsewhere in phase_state
                        if phase_state.get("status") == "completed":
                            completed.add(ac_id)
        
        return completed
    
    def sync_dashboard(self) -> bool:
        """Sync dashboard from SSOT"""
        print("🔄 Syncing dashboard from SSOT...")
        
        try:
            success = self.dashboard_syncer.sync()
            
            if success:
                print("✅ Dashboard synced successfully")
                return True
            else:
                print("⚠️ Dashboard sync failed")
                return False
        
        except Exception as e:
            print(f"❌ Dashboard sync error: {e}")
            return False
    
    def display_status(self):
        """Display current execution status"""
        state = self.get_current_state()
        current_phase = state["current_phase"]
        
        print("\n" + "="*60)
        print("📊 CORTEX EXECUTION STATUS")
        print("="*60)
        print(f"\n📍 Current Phase: {current_phase['number']} - {current_phase['name']}")
        print(f"📈 Completion: {current_phase['completion_percentage']:.1f}%")
        print(f"🔖 Status: {current_phase['status']}")
        
        # Get incomplete AC-IDs
        incomplete = self.get_incomplete_ac_ids(state)
        
        if incomplete:
            print(f"\n📋 Remaining AC-IDs: {len(incomplete)}")
            print("\nNext to implement:")
            for ac_id in incomplete[:5]:  # Show first 5
                ac_title = self.get_ac_title(ac_id)
                print(f"  • {ac_id}: {ac_title}")
            
            if len(incomplete) > 5:
                print(f"  ... and {len(incomplete) - 5} more")
        else:
            print("\n✅ All AC-IDs complete for current phase")
        
        print("="*60 + "\n")
    
    def execute_autonomous_loop(self, max_iterations: int = 100):
        """
        Execute autonomous loop until phase complete or blocker
        
        Args:
            max_iterations: Maximum iterations (safety limit)
        """
        print("\n🚀 Starting autonomous execution loop...")
        print("="*60)
        
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            
            # Load state
            state = self.get_current_state()
            current_phase = state["current_phase"]
            
            # Check phase completion
            if current_phase["completion_percentage"] >= 100.0:
                print(f"\n✅ Phase {current_phase['number']} COMPLETE (100%)")
                print(f"Ready to proceed to next phase")
                break
            
            # Validate evidence gate
            gate_passed, verification_rate = self.validate_evidence_gate()
            if not gate_passed:
                print("\n⚠️ Blocked by evidence gate. Fix false positives and retry.")
                break
            
            # Get incomplete AC-IDs
            incomplete = self.get_incomplete_ac_ids(state)
            
            if not incomplete:
                print(f"\n✅ All AC-IDs implemented for Phase {current_phase['number']}")
                
                # Sync dashboard
                self.sync_dashboard()
                
                # Reload state to check completion
                state = self.get_current_state()
                current_phase = state["current_phase"]
                
                if current_phase["completion_percentage"] >= 100.0:
                    print(f"\n✅ Phase {current_phase['number']} COMPLETE (100%)")
                    break
                else:
                    print(f"\n⚙️ Phase {current_phase['number']} at {current_phase['completion_percentage']:.1f}%")
                    print("Waiting for test evidence validation...")
                    break
            
            # Execute next AC-ID
            next_ac_id = incomplete[0]
            ac_title = self.get_ac_title(next_ac_id)
            
            print(f"\n🔨 [{iteration}/{max_iterations}] Implementing {next_ac_id}: {ac_title}...")
            
            # Delegate to MasterOrchestrator
            result = subprocess.run(
                [sys.executable, "-m", "src.main", f"implement {next_ac_id}", "--format", "markdown"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print(f"❌ Implementation failed: {result.stderr}")
                break
            
            print(result.stdout)
            
            # Sync dashboard (triggered by MasterOrchestrator, but verify)
            self.sync_dashboard()
            
            # Brief pause for state updates
            import time
            time.sleep(1)
        
        if iteration >= max_iterations:
            print(f"\n⚠️ Max iterations reached ({max_iterations}). Stopping.")
        
        # Final status
        self.display_status()


def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="CORTEX Execution Agent v1.0.0 - Autonomous master-plan executor"
    )
    parser.add_argument(
        "command",
        choices=["status", "validate", "sync", "execute", "continue"],
        help="Command to execute"
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=100,
        help="Maximum iterations for autonomous loop (default: 100)"
    )
    
    args = parser.parse_args()
    
    # Initialize agent
    agent = CortexExecutionAgent()
    
    # Execute command
    if args.command == "status":
        agent.display_status()
    
    elif args.command == "validate":
        gate_passed, verification_rate = agent.validate_evidence_gate()
        sys.exit(0 if gate_passed else 1)
    
    elif args.command == "sync":
        success = agent.sync_dashboard()
        sys.exit(0 if success else 1)
    
    elif args.command in ["execute", "continue"]:
        agent.execute_autonomous_loop(max_iterations=args.max_iterations)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
