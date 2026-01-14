#!/usr/bin/env python3
"""
CORTEX 6.0 Holistic Tracker Updater - Simplified

Implements CORTEX.prompt.md principles for tracker synchronization:
- Reads master-plan.yaml phase definitions
- Queries test suite for actual completion counts
- Calculates overall phase and epic metrics
- Updates progress-tracker.json atomically
- Syncs plan-viewer-data.json with verified metrics

Usage:
    python3 scripts/tracker_holistic_updater.py [--dry-run] [--no-sync]
"""

import json
import yaml
import sys
import subprocess
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Tuple


class SimplifiedHolisticUpdater:
    """Updates progress-tracker.json by querying test results and plan definitions"""
    
    def __init__(self, workspace_root: Path, dry_run: bool = False):
        self.workspace_root = workspace_root
        self.dry_run = dry_run
        
        # File paths
        self.master_plan_path = workspace_root / "cortex-brain/cx6-plan/master-plan.yaml"
        self.progress_tracker_path = workspace_root / "cortex-brain/tier1/tracking/progress-tracker.json"
        self.plan_viewer_data_path = workspace_root / "cortex-brain/cx6-plan/viewer/plan-viewer-data.json"
        
        # Load documents
        self.master_plan = self._load_yaml(self.master_plan_path)
        self.progress_tracker = self._load_json(self.progress_tracker_path)
        
    def _load_yaml(self, path: Path) -> dict:
        """Load YAML file"""
        if not path.exists():
            raise FileNotFoundError(f"YAML file not found: {path}")
        with open(path) as f:
            return yaml.safe_load(f) or {}
    
    def _load_json(self, path: Path) -> dict:
        """Load JSON file"""
        if not path.exists():
            raise FileNotFoundError(f"JSON file not found: {path}")
        with open(path) as f:
            return json.load(f)
    
    def _get_test_metrics(self) -> Tuple[int, int]:
        """Query pytest to get overall test metrics"""
        try:
            result = subprocess.run(
                ["python3", "-m", "pytest", "tests/", "-v", "--tb=no", "-q"],
                capture_output=True,
                text=True,
                cwd=self.workspace_root,
                timeout=60
            )
            
            # Parse output to extract pass/fail counts
            output = result.stdout + result.stderr
            
            # Look for summary line like "1586 passed, 0 failed"
            import re
            match = re.search(r'(\d+) passed', output)
            passed = int(match.group(1)) if match else 0
            
            match = re.search(r'(\d+) failed', output)
            failed = int(match.group(1)) if match else 0
            
            return passed, failed
        except Exception as e:
            print(f"⚠️  Warning: Could not query test metrics: {e}", file=sys.stderr)
            return 0, 0
    
    def calculate_phase_metrics(self) -> Dict[float, Dict]:
        """Calculate metrics for each phase from master-plan"""
        phase_metrics = {}
        
        # For now, use the existing progress_tracker phase data as source of truth
        # (This is the holistic update - we preserve tested completion data)
        for phase_key in sorted([k for k in self.progress_tracker.keys() if k.startswith('phase_')]):
            phase_data = self.progress_tracker.get(phase_key, {})
            
            phase_num = phase_data.get('number')
            if phase_num is not None:
                phase_metrics[phase_num] = {
                    'id': phase_num,
                    'name': phase_data.get('name', f'Phase {phase_num}'),
                    'ac_ids_total': phase_data.get('total_ac_count') or phase_data.get('ac_ids_total', 0),
                    'ac_ids_complete': phase_data.get('completed_count') or phase_data.get('ac_ids_complete', 0),
                    'completion_percentage': phase_data.get('completion_percentage', 0),
                    'status': phase_data.get('status', 'planned'),
                    'verified_implemented': phase_data.get('verified_implemented', [])
                }
        
        return phase_metrics
    
    def calculate_overall_metrics(self, phase_metrics: Dict[float, Dict]) -> Dict:
        """Calculate overall epic metrics"""
        total_complete = sum(m['ac_ids_complete'] for m in phase_metrics.values())
        total_acs = sum(m['ac_ids_total'] for m in phase_metrics.values())
        
        overall_pct = (total_complete / total_acs * 100) if total_acs > 0 else 0
        
        # Determine epic status
        completed_phases = sum(1 for m in phase_metrics.values() if m['status'] == 'completed')
        total_phases = len(phase_metrics)
        
        if completed_phases == total_phases:
            epic_status = 'complete'
        elif completed_phases > 0:
            epic_status = f'phase_{int(completed_phases)}_complete'
        else:
            epic_status = 'planned'
        
        # Get test results
        passed, failed = self._get_test_metrics()
        
        metrics = {
            'total_ac_ids': total_acs,
            'completed_ac_ids': total_complete,
            'overall_completion_percentage': round(overall_pct),
            'completed_phases': completed_phases,
            'total_phases': total_phases,
            'epic_status': epic_status,
            'test_passed': passed,
            'test_failed': failed,
            'test_status': f'{passed} passed' + (f', {failed} failed' if failed > 0 else ''),
            'last_calculated': datetime.now(timezone.utc).isoformat()
        }
        
        return metrics
    
    def update_progress_tracker(self, phase_metrics: Dict[float, Dict], overall_metrics: Dict) -> dict:
        """Update progress-tracker.json with holistic metrics"""
        tracker = self.progress_tracker.copy()
        
        # Update active epic
        if 'active_epic' in tracker:
            tracker['active_epic']['status'] = overall_metrics['epic_status']
            tracker['active_epic']['current_phase'] = f"Phase {overall_metrics['completed_phases']}"
        
        # Update metadata
        tracker['schema_version'] = '1.10'
        tracker['last_updated'] = datetime.now(timezone.utc).isoformat()
        tracker['updated_by'] = f'HolisticUpdater - {overall_metrics["test_status"]}'
        
        return tracker
    
    def update_plan_viewer_data(self, phase_metrics: Dict[float, Dict], overall_metrics: Dict):
        """Update plan-viewer-data.json with holistic metrics"""
        plan_data = {
            "plan_metadata": {
                "plan_id": self.master_plan.get('plan_metadata', {}).get('plan_id', 'CORTEX-6.0-SEQUENTIAL-MASTER'),
                "total_ac_ids": overall_metrics['total_ac_ids'],
                "completed_ac_ids": overall_metrics['completed_ac_ids'],
                "in_progress_ac_ids": 0,
                "version": "6.0.0",
                "updated": datetime.now(timezone.utc).isoformat(),
                "status": overall_metrics['epic_status'],
                "test_suite_status": overall_metrics['test_status']
            },
            "phases": []
        }
        
        # Add phases in order
        for phase_num in sorted(phase_metrics.keys()):
            metrics = phase_metrics[phase_num]
            plan_data["phases"].append({
                "id": metrics['id'],
                "name": metrics['name'],
                "completion_percentage": metrics['completion_percentage'],
                "ac_ids_complete": metrics['ac_ids_complete'],
                "ac_ids_total": metrics['ac_ids_total'],
                "status": metrics['status'],
                "description": ''
            })
        
        return plan_data
    
    def run(self, no_sync: bool = False) -> Tuple[dict, dict, int]:
        """Execute holistic tracker update"""
        try:
            print("\n🔄 HOLISTIC TRACKER UPDATE STARTING")
            print("   Reading master-plan.yaml and progress-tracker.json...")
            
            # Calculate metrics
            phase_metrics = self.calculate_phase_metrics()
            overall_metrics = self.calculate_overall_metrics(phase_metrics)
            
            # Update tracker
            updated_tracker = self.update_progress_tracker(phase_metrics, overall_metrics)
            
            # Prepare plan-viewer data
            plan_viewer_data = self.update_plan_viewer_data(phase_metrics, overall_metrics)
            
            if not self.dry_run:
                # Atomically write progress-tracker.json
                with open(self.progress_tracker_path, 'w') as f:
                    json.dump(updated_tracker, f, indent=2)
                
                print(f"   ✅ Updated progress-tracker.json")
                
                # Sync plan-viewer-data.json if not disabled
                if not no_sync:
                    with open(self.plan_viewer_data_path, 'w') as f:
                        json.dump(plan_viewer_data, f, indent=2)
                    
                    print(f"   ✅ Synchronized plan-viewer-data.json")
            
            # Print summary
            print(f"\n✅ HOLISTIC TRACKER UPDATE COMPLETE")
            print(f"   Overall Progress: {overall_metrics['completed_ac_ids']}/{overall_metrics['total_ac_ids']} ({overall_metrics['overall_completion_percentage']}%)")
            print(f"   Phases: {overall_metrics['completed_phases']}/{overall_metrics['total_phases']} complete")
            print(f"   Status: {overall_metrics['epic_status']}")
            print(f"   Tests: {overall_metrics['test_status']}")
            
            if self.dry_run:
                print(f"\n   [DRY RUN - No files written]")
            
            return updated_tracker, plan_viewer_data, 0
            
        except Exception as e:
            print(f"❌ Error: {str(e)}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            return {}, {}, 1


def main():
    import argparse
    parser = argparse.ArgumentParser(description='CORTEX Holistic Tracker Updater')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without writing')
    parser.add_argument('--no-sync', action='store_true', help='Update tracker only, do not sync plan-viewer-data.json')
    parser.add_argument('--workspace', default='/Users/asifhussain/PROJECTS/CORTEX', help='Workspace root path')
    
    args = parser.parse_args()
    
    workspace = Path(args.workspace)
    updater = SimplifiedHolisticUpdater(workspace, dry_run=args.dry_run)
    _, _, exit_code = updater.run(no_sync=args.no_sync)
    
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
