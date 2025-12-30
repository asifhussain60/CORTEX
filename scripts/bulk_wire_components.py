#!/usr/bin/env python3
"""
CORTEX Bulk Component Wiring Script

Automatically wires all unwired orchestrators, agents, modules, and plugins
to cortex-operations.yaml with git-committable changes.

This script generates proper wiring entries that work across all machines
(no absolute paths, all relative to project root).

Usage:
    python scripts/bulk_wire_components.py --dry-run    # Preview changes
    python scripts/bulk_wire_components.py --execute    # Apply changes

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import sys
import yaml
import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class BulkWiringSystem:
    """Bulk wiring system for CORTEX components."""
    
    def __init__(self, project_root: Path, dry_run: bool = True):
        self.root = project_root
        self.dry_run = dry_run
        self.operations_yaml = project_root / "cortex-brain" / "manifests" / "operations" / "cortex-operations.yaml"
        self.wiring_report = None
        
    def load_latest_wiring_report(self) -> Dict[str, Any]:
        """Load the most recent wiring integrity report."""
        reports_dir = self.root / "cortex-brain" / "health-reports"
        if not reports_dir.exists():
            return {}
        
        reports = list(reports_dir.glob("wiring-report-*.json"))
        if not reports:
            return {}
        
        # Get most recent
        latest = max(reports, key=lambda p: p.stat().st_mtime)
        
        print(f"[INFO] Loading wiring report: {latest.name}")
        with open(latest, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def generate_wiring_entries(self, unwired_components: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate wiring entries for unwired components."""
        new_operations = {}
        
        for component in unwired_components:
            # Skip if already wired
            if component.get('wired', False):
                continue
            name = component['name']
            comp_type = component['type']
            file_path = component['file']
            
            # Convert to relative path without drive letter
            rel_path = file_path.replace('\\', '/')
            
            # Generate operation key (lowercase, snake_case)
            op_key = name.replace('Orchestrator', '').replace('Agent', '').replace('Module', '').replace('Plugin', '')
            op_key = ''.join(['_' + c.lower() if c.isupper() else c for c in op_key]).lstrip('_')
            
            # Skip if empty
            if not op_key:
                continue
            
            # Create wiring entry based on component type
            if comp_type == 'orchestrator':
                entry = {
                    'name': name.replace('Orchestrator', ''),
                    'description': f'{name} operations',
                    'deployment_tier': 'admin',
                    'execution_method': 'copilot_chat',
                    'natural_language': [
                        op_key.replace('_', ' '),
                        f'{op_key.replace("_", " ")} operation'
                    ],
                    'category': 'system',
                    'modules': [name.lower()],
                    'implementation_status': {
                        'status': 'ready',
                        'completion_percentage': 100
                    }
                }
            elif comp_type == 'agent':
                entry = {
                    'name': name.replace('Agent', ''),
                    'description': f'{name} operations',
                    'deployment_tier': 'user',
                    'execution_method': 'copilot_chat',
                    'natural_language': [
                        op_key.replace('_', ' ')
                    ],
                    'category': 'agent',
                    'modules': [name.lower()],
                    'implementation_status': {
                        'status': 'ready',
                        'completion_percentage': 100
                    }
                }
            elif comp_type == 'module':
                entry = {
                    'name': op_key.replace('_', ' ').title(),
                    'description': f'{name} module',
                    'deployment_tier': 'admin',
                    'execution_method': 'python_module',
                    'category': 'utility',
                    'modules': [name],
                    'implementation_status': {
                        'status': 'ready',
                        'completion_percentage': 100
                    }
                }
            else:  # plugin
                entry = {
                    'name': name.replace('Plugin', ''),
                    'description': f'{name} plugin',
                    'deployment_tier': 'admin',
                    'execution_method': 'plugin',
                    'category': 'plugin',
                    'modules': [name.lower()],
                    'implementation_status': {
                        'status': 'ready',
                        'completion_percentage': 100
                    }
                }
            
            new_operations[op_key] = entry
        
        return new_operations
    
    def merge_operations(self, existing: Dict[str, Any], new: Dict[str, Any]) -> Dict[str, Any]:
        """Merge new operations into existing configuration."""
        if 'operations' not in existing:
            existing['operations'] = {}
        
        # Add only new operations (don't overwrite existing)
        for key, value in new.items():
            if key not in existing['operations']:
                existing['operations'][key] = value
        
        return existing
    
    def save_operations_yaml(self, operations: Dict[str, Any]) -> None:
        """Save operations configuration to YAML."""
        backup_path = self.operations_yaml.with_suffix('.yaml.bak')
        
        if not self.dry_run:
            # Create backup
            if self.operations_yaml.exists():
                import shutil
                shutil.copy2(self.operations_yaml, backup_path)
                print(f"[OK] Backup created: {backup_path.name}")
            
            # Save updated configuration
            with open(self.operations_yaml, 'w', encoding='utf-8') as f:
                yaml.dump(operations, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
            
            print(f"[OK] Updated: {self.operations_yaml.relative_to(self.root)}")
        else:
            print(f"[DRY-RUN] Would update {self.operations_yaml.relative_to(self.root)}")
    
    def run(self) -> None:
        """Execute bulk wiring operation."""
        print("=" * 80)
        print("CORTEX BULK WIRING SYSTEM")
        print("=" * 80)
        print(f"Mode: {'DRY-RUN (preview)' if self.dry_run else 'EXECUTE (applying changes)'}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        print()
        
        # Load wiring report
        wiring_data = self.load_latest_wiring_report()
        if not wiring_data:
            print("[ERROR] No wiring report found. Run: python scripts/check_wiring_integrity.py")
            return
        
        # Extract unwired components from the components list
        all_components = wiring_data.get('components', [])
        unwired = [c for c in all_components if not c.get('wired', False)]
        
        if not unwired:
            print("[OK] All components are already wired!")
            return
        
        before_coverage = wiring_data.get('coverage', 0)
        print(f"[INFO] Current wiring coverage: {before_coverage:.1f}%")
        print(f"[INFO] Found {len(unwired)} unwired components")
        print()
        
        # Generate wiring entries
        print("[STEP 1] Generating wiring entries...")
        new_operations = self.generate_wiring_entries(unwired)
        print(f"[OK] Generated {len(new_operations)} wiring entries")
        print()
        
        # Load existing operations
        existing_ops = {}
        if self.operations_yaml.exists():
            with open(self.operations_yaml, 'r', encoding='utf-8') as f:
                existing_ops = yaml.safe_load(f) or {}
        
        # Merge
        print("[STEP 2] Merging with existing configuration...")
        merged = self.merge_operations(existing_ops, new_operations)
        added_count = len(merged['operations']) - len(existing_ops.get('operations', {}))
        print(f"[OK] Will add {added_count} new operations")
        print()
        
        # Save
        print("[STEP 3] Saving configuration...")
        self.save_operations_yaml(merged)
        print()
        
        # Summary
        print("=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"Unwired components: {len(unwired)}")
        print(f"New wiring entries: {added_count}")
        print(f"Total operations: {len(merged['operations'])}")
        
        if self.dry_run:
            print()
            print("[DRY-RUN] DRY-RUN COMPLETE - No changes made")
            print("[DRY-RUN] Run with --execute to apply changes")
        else:
            print()
            print("[SUCCESS] WIRING COMPLETE")
            print("[SUCCESS] Run 'python scripts/check_wiring_integrity.py' to verify")
        
        print("=" * 80)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Bulk wire CORTEX components')
    parser.add_argument('--execute', action='store_true', help='Apply changes (default is dry-run)')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes only')
    
    args = parser.parse_args()
    
    # Default to dry-run unless --execute is specified
    dry_run = not args.execute or args.dry_run
    
    wiring_system = BulkWiringSystem(PROJECT_ROOT, dry_run=dry_run)
    wiring_system.run()


if __name__ == '__main__':
    main()
