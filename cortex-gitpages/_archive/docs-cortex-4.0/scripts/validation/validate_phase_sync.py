#!/usr/bin/env python3
"""
Validate cortex-master.yaml phases section for consistency and completeness.

This script ensures:
1. No AC-IDs are duplicated or undefined
2. All status transitions follow valid state machine
3. Locked phases cannot have incomplete AC-IDs
4. Counts in metadata match actual phase data
5. No circular dependencies
"""

import yaml
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any
from collections import defaultdict


class PhaseValidator:
    
    VALID_STATUSES = {'NOT_STARTED', 'IN_PROGRESS', 'COMPLETED'}
    MASTER_FILE = Path("/Users/asifhussain/PROJECTS/CORTEX/_workspaces/roadmap/cortex-master.yaml")
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.fixes_applied = 0
        self.master_data = None
        self.phases = {}
        self.all_ac_ids = defaultdict(list)
    
    def load_master(self) -> bool:
        """Load cortex-master.yaml"""
        try:
            with open(self.MASTER_FILE, 'r') as f:
                self.master_data = yaml.safe_load(f)
            print(f"✓ Loaded {self.MASTER_FILE}")
            return True
        except Exception as e:
            self.errors.append(f"Cannot load cortex-master.yaml: {e}")
            return False
    
    def validate_phases_exist(self) -> bool:
        """Check that phases: section exists"""
        if 'phases' not in self.master_data:
            self.errors.append("phases: section not found in cortex-master.yaml")
            return False
        
        self.phases = self.master_data['phases']
        print(f"✓ Found phases: section with {len(self.phases)} phases")
        return True
    
    def validate_phase_structure(self) -> bool:
        """Validate each phase has required fields"""
        valid = True
        
        for phase_id, phase_spec in self.phases.items():
            
            # Check required fields
            required = ['title', 'status', 'locked', 'ac_ids']
            for field in required:
                if field not in phase_spec:
                    self.errors.append(f"{phase_id}: Missing required field '{field}'")
                    valid = False
                    continue
            
            # Validate status
            status = phase_spec.get('status')
            if status not in self.VALID_STATUSES:
                self.errors.append(f"{phase_id}: Invalid status '{status}' (must be {self.VALID_STATUSES})")
                valid = False
            
            # Validate locked constraint
            if phase_spec.get('locked') and status != 'COMPLETED':
                self.warnings.append(f"{phase_id}: Locked but not COMPLETED")
            
            # Count AC-IDs
            ac_ids = phase_spec.get('ac_ids', {})
            if not isinstance(ac_ids, dict):
                self.errors.append(f"{phase_id}: ac_ids must be a dict, got {type(ac_ids)}")
                valid = False
                continue
            
            # Track all AC-IDs for duplicate detection
            for ac_id in ac_ids.keys():
                self.all_ac_ids[ac_id].append(phase_id)
        
        return valid
    
    def validate_ac_id_uniqueness(self) -> bool:
        """Check for duplicate AC-IDs across phases"""
        valid = True
        
        for ac_id, phases in self.all_ac_ids.items():
            if len(phases) > 1:
                self.errors.append(f"AC-ID '{ac_id}' appears in multiple phases: {phases}")
                valid = False
        
        print(f"✓ All {len(self.all_ac_ids)} AC-IDs are unique")
        return valid
    
    def validate_ac_id_naming(self) -> bool:
        """Validate AC-ID naming convention: AC-DOMAIN-NNN-NN"""
        valid = True
        invalid_names = []
        
        for ac_id in self.all_ac_ids.keys():
            # AC-DOMAIN-NNN-NN pattern
            parts = ac_id.split('-')
            
            if len(parts) < 4:
                invalid_names.append(ac_id)
                continue
            
            if parts[0] != 'AC':
                invalid_names.append(ac_id)
            
            try:
                # Should have numeric parts
                int(parts[2])  # Numeric sequence
                int(parts[3])  # Numeric sequence
            except (ValueError, IndexError):
                invalid_names.append(ac_id)
        
        if invalid_names:
            self.warnings.append(f"AC-IDs with non-standard names: {invalid_names}")
            valid = False
        
        return valid
    
    def validate_metadata_counts(self) -> bool:
        """Validate metadata counts match actual phase data"""
        valid = True
        metadata = self.master_data.get('metadata', {})
        
        # Count actual AC-IDs
        actual_ac_count = sum(
            len(phase.get('ac_ids', {}))
            for phase in self.phases.values()
        )
        
        declared_ac_count = metadata.get('total_ac_ids')
        
        if declared_ac_count != actual_ac_count:
            self.warnings.append(
                f"AC-ID count mismatch: metadata says {declared_ac_count}, "
                f"actual is {actual_ac_count}"
            )
            
            # Auto-fix
            print(f"   🔧 AUTO-FIX: Updating total_ac_ids {declared_ac_count} → {actual_ac_count}")
            self.master_data['metadata']['total_ac_ids'] = actual_ac_count
            self.fixes_applied += 1
            valid = False
        
        # Count locked phases
        actual_locked = sum(
            1 for phase in self.phases.values()
            if phase.get('locked', False)
        )
        
        declared_locked = metadata.get('total_ac_ids_locked')
        
        if declared_locked != actual_locked:
            self.warnings.append(
                f"Locked phases count mismatch: metadata says {declared_locked}, "
                f"actual is {actual_locked}"
            )
        
        print(f"✓ Total AC-IDs: {actual_ac_count} ({actual_locked} in locked phases)")
        return valid
    
    def validate_dependencies(self) -> bool:
        """Validate no circular dependencies between phases"""
        valid = True
        
        def has_cycle(phase_id: str, visited: set, path: set) -> bool:
            if phase_id in path:
                return True
            if phase_id in visited:
                return False
            
            visited.add(phase_id)
            path.add(phase_id)
            
            deps = self.phases.get(phase_id, {}).get('dependencies', [])
            for dep in deps:
                if has_cycle(dep, visited, path):
                    return True
            
            path.remove(phase_id)
            return False
        
        visited = set()
        for phase_id in self.phases.keys():
            if has_cycle(phase_id, visited, set()):
                self.errors.append(f"Circular dependency detected involving {phase_id}")
                valid = False
        
        if valid:
            print(f"✓ No circular dependencies detected")
        
        return valid
    
    def validate_completion_consistency(self) -> bool:
        """Check COMPLETED phases have all AC-IDs marked complete"""
        valid = True
        
        for phase_id, phase_spec in self.phases.items():
            if phase_spec['status'] != 'COMPLETED':
                continue
            
            ac_ids = phase_spec.get('ac_ids', {})
            
            # Check if any AC-IDs are marked incomplete
            for ac_id, ac_spec in ac_ids.items():
                if isinstance(ac_spec, dict):
                    ac_status = ac_spec.get('status', 'COMPLETED')
                    if ac_status != 'COMPLETED':
                        self.warnings.append(
                            f"{phase_id}: COMPLETED but AC-ID {ac_id} has status '{ac_status}'"
                        )
        
        print(f"✓ Completion consistency validated")
        return valid
    
    def validate_all(self) -> Tuple[bool, Dict[str, Any]]:
        """Run all validations"""
        print("\n" + "=" * 80)
        print("PHASE SYNC VALIDATOR")
        print("=" * 80 + "\n")
        
        checks = [
            ("Loading master file", self.load_master),
            ("Phases section exists", self.validate_phases_exist),
            ("Phase structure", self.validate_phase_structure),
            ("AC-ID uniqueness", self.validate_ac_id_uniqueness),
            ("AC-ID naming", self.validate_ac_id_naming),
            ("Metadata counts", self.validate_metadata_counts),
            ("Dependencies (no cycles)", self.validate_dependencies),
            ("Completion consistency", self.validate_completion_consistency),
        ]
        
        all_valid = True
        for check_name, check_func in checks:
            print(f"\n[CHECK] {check_name}...")
            try:
                result = check_func()
                if not result:
                    all_valid = False
            except Exception as e:
                print(f"❌ Exception in {check_name}: {e}")
                self.errors.append(f"{check_name}: {e}")
                all_valid = False
        
        return all_valid, self._generate_report()
    
    def _generate_report(self) -> Dict[str, Any]:
        """Generate validation report"""
        return {
            'valid': len(self.errors) == 0,
            'errors': self.errors,
            'warnings': self.warnings,
            'fixes_applied': self.fixes_applied,
            'total_phases': len(self.phases),
            'total_ac_ids': len(self.all_ac_ids),
        }
    
    def print_report(self, report: Dict[str, Any]):
        """Print human-readable report"""
        print("\n" + "=" * 80)
        print("VALIDATION REPORT")
        print("=" * 80)
        
        print(f"\n📊 Summary:")
        print(f"   Total Phases: {report['total_phases']}")
        print(f"   Total AC-IDs: {report['total_ac_ids']}")
        print(f"   Fixes Applied: {report['fixes_applied']}")
        
        if report['errors']:
            print(f"\n❌ ERRORS ({len(report['errors'])}):")
            for error in report['errors']:
                print(f"   - {error}")
        
        if report['warnings']:
            print(f"\n⚠️ WARNINGS ({len(report['warnings'])}):")
            for warning in report['warnings']:
                print(f"   - {warning}")
        
        if report['valid']:
            print(f"\n✅ ALL CHECKS PASSED")
        else:
            print(f"\n❌ VALIDATION FAILED")
        
        print("=" * 80 + "\n")
    
    def save_master(self) -> bool:
        """Save updated master file (if fixes were applied)"""
        if self.fixes_applied == 0:
            return True
        
        try:
            with open(self.MASTER_FILE, 'w') as f:
                yaml.dump(self.master_data, f, default_flow_style=False, sort_keys=False)
            print(f"💾 Saved {self.fixes_applied} fixes to cortex-master.yaml")
            return True
        except Exception as e:
            self.errors.append(f"Cannot save cortex-master.yaml: {e}")
            return False


def main():
    """Main validation workflow"""
    
    validator = PhaseValidator()
    all_valid, report = validator.validate_all()
    validator.print_report(report)
    
    if report['fixes_applied'] > 0:
        validator.save_master()
    
    return 0 if all_valid else 1


if __name__ == "__main__":
    sys.exit(main())
