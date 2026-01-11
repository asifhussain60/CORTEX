#!/usr/bin/env python3
"""
Evidence-Based Progress Tracker Validator

CRITICAL: Prevents false positives by requiring test evidence for AC-ID completion.

Philosophy:
- AC-ID marked "implemented" ONLY if tests exist AND pass
- Test files must exist in expected locations
- Audit logs must show test execution
- No manual completion percentage overrides allowed

Evidence Requirements:
1. Test file exists (tests/{category}/test_{feature}.py)
2. Test passes (pytest result code 0)
3. Audit log shows test execution (optional but recommended)

Usage:
  python3 scripts/validate_tracker_evidence.py
  python3 scripts/validate_tracker_evidence.py --fix
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Tuple, Optional


class EvidenceValidator:
    """Validates AC-ID completion claims against test evidence"""
    
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.tracker_path = workspace_root / 'cortex-brain/tier1/tracking/progress-tracker.json'
        self.ac_index_path = workspace_root / 'cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml'
        self.audit_log_dir = workspace_root / 'cortex-brain/audit-logs'
        
        # AC-ID to test file mapping (convention-based)
        self.test_mappings = {
            'AC-AUDIT': 'tests/audit/',
            'AC-GOV': 'tests/governance/',
            'AC-STATE': 'tests/infrastructure/',
            'AC-LIFECYCLE': 'tests/infrastructure/',
            'AC-EVIDENCE': 'tests/infrastructure/',
            'AC-SECURITY': 'tests/infrastructure/',
            'AC-ORCH': 'tests/orchestrators/',
            'AC-TODO': 'tests/orchestrators/',
            'AC-TDD': 'tests/orchestrators/',
            'AC-PLAN': 'tests/orchestrators/',
            'AC-STS': 'tests/sts/',
        }
    
    def validate_all(self) -> Dict[str, any]:
        """Run full validation suite"""
        print("=" * 70)
        print("EVIDENCE-BASED TRACKER VALIDATION")
        print("=" * 70)
        print()
        
        # Load tracker
        if not self.tracker_path.exists():
            return {'error': f'Tracker not found: {self.tracker_path}'}
        
        tracker = json.loads(self.tracker_path.read_text())
        
        # Validate each phase
        results = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'phases': {},
            'summary': {
                'total_claimed': 0,
                'total_verified': 0,
                'false_positives': [],
                'missing_tests': [],
                'test_failures': []
            }
        }
        
        # Phase 1
        if 'current_phase' in tracker:
            phase_result = self._validate_phase(
                tracker['current_phase'],
                phase_name='Phase 1: Foundation Enhancement'
            )
            results['phases']['phase_1'] = phase_result
            results['summary']['total_claimed'] += phase_result['claimed_count']
            results['summary']['total_verified'] += phase_result['verified_count']
            results['summary']['false_positives'].extend(phase_result['false_positives'])
            results['summary']['missing_tests'].extend(phase_result['missing_tests'])
        
        # Phase 1.5
        if 'phase_1_5_sts' in tracker:
            phase_result = self._validate_phase(
                tracker['phase_1_5_sts'],
                phase_name='Phase 1.5: STS'
            )
            results['phases']['phase_1_5'] = phase_result
            results['summary']['total_claimed'] += phase_result['claimed_count']
            results['summary']['total_verified'] += phase_result['verified_count']
        
        # Phase 2
        completed_phases = tracker.get('completed_phases', [])
        for phase_data in completed_phases:
            if phase_data.get('number') == 2:
                phase_result = self._validate_phase(
                    phase_data,
                    phase_name='Phase 2: Orchestration Core'
                )
                results['phases']['phase_2'] = phase_result
                results['summary']['total_claimed'] += phase_result['claimed_count']
                results['summary']['total_verified'] += phase_result['verified_count']
                results['summary']['false_positives'].extend(phase_result['false_positives'])
                results['summary']['missing_tests'].extend(phase_result['missing_tests'])
        
        # Print summary
        self._print_results(results)
        
        return results
    
    def _validate_phase(self, phase_data: Dict, phase_name: str) -> Dict:
        """Validate a single phase"""
        ac_ids = phase_data.get('ac_ids', [])
        claimed_count = phase_data.get('completed_count', 0)
        
        verified_ac_ids = []
        false_positives = []
        missing_tests = []
        
        for ac_id in ac_ids:
            evidence = self._check_evidence(ac_id)
            
            if evidence['status'] == 'verified':
                verified_ac_ids.append(ac_id)
            elif evidence['status'] == 'no_test':
                missing_tests.append({
                    'ac_id': ac_id,
                    'reason': 'Test file not found',
                    'expected': evidence.get('expected_path')
                })
            elif evidence['status'] == 'test_failed':
                false_positives.append({
                    'ac_id': ac_id,
                    'reason': 'Tests exist but fail',
                    'test_file': evidence.get('test_file')
                })
        
        verified_count = len(verified_ac_ids)
        actual_percentage = int((verified_count / len(ac_ids) * 100)) if ac_ids else 0
        claimed_percentage = phase_data.get('completion_percentage', 0)
        
        return {
            'phase_name': phase_name,
            'claimed_count': claimed_count,
            'verified_count': verified_count,
            'claimed_percentage': claimed_percentage,
            'actual_percentage': actual_percentage,
            'total_ac_ids': len(ac_ids),
            'verified_ac_ids': verified_ac_ids,
            'false_positives': false_positives,
            'missing_tests': missing_tests,
            'discrepancy': claimed_count - verified_count
        }
    
    def _check_evidence(self, ac_id: str) -> Dict:
        """Check if AC-ID has test evidence"""
        # Determine test directory
        prefix = ac_id.split('-')[1] if '-' in ac_id else ''
        test_dir = self.test_mappings.get(f'AC-{prefix}', 'tests/')
        
        # Search for test files containing this AC-ID
        test_files = self._find_test_files(ac_id, test_dir)
        
        if not test_files:
            return {
                'status': 'no_test',
                'expected_path': test_dir,
                'ac_id': ac_id
            }
        
        # Run tests to verify they pass
        for test_file in test_files:
            if self._run_test(test_file):
                return {
                    'status': 'verified',
                    'test_file': str(test_file),
                    'ac_id': ac_id
                }
        
        return {
            'status': 'test_failed',
            'test_file': str(test_files[0]) if test_files else None,
            'ac_id': ac_id
        }
    
    def _find_test_files(self, ac_id: str, test_dir: str) -> List[Path]:
        """Find test files that might test this AC-ID"""
        test_path = self.workspace_root / test_dir
        if not test_path.exists():
            return []
        
        # Search for test files containing AC-ID reference
        # (either in filename, docstring, or test function name)
        test_files = []
        for test_file in test_path.rglob('test_*.py'):
            content = test_file.read_text()
            # Simple heuristic: file mentions AC-ID
            if ac_id in content:
                test_files.append(test_file)
        
        return test_files
    
    def _run_test(self, test_file: Path) -> bool:
        """Run a test file and check if it passes"""
        try:
            result = subprocess.run(
                ['python3', '-m', 'pytest', str(test_file), '-v', '--tb=no', '-q'],
                cwd=self.workspace_root,
                capture_output=True,
                timeout=30
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, Exception):
            return False
    
    def _print_results(self, results: Dict):
        """Print validation results"""
        summary = results['summary']
        
        print("\nVALIDATION RESULTS:")
        print("-" * 70)
        
        for phase_key, phase_result in results['phases'].items():
            print(f"\n{phase_result['phase_name']}:")
            print(f"  Claimed: {phase_result['claimed_count']}/{phase_result['total_ac_ids']} ({phase_result['claimed_percentage']}%)")
            print(f"  Verified: {phase_result['verified_count']}/{phase_result['total_ac_ids']} ({phase_result['actual_percentage']}%)")
            
            if phase_result['discrepancy'] > 0:
                print(f"  ⚠️  DISCREPANCY: {phase_result['discrepancy']} AC-IDs claimed without evidence")
            else:
                print(f"  ✅ Accurate")
            
            if phase_result['false_positives']:
                print(f"  ❌ False Positives: {len(phase_result['false_positives'])}")
                for fp in phase_result['false_positives'][:3]:
                    print(f"     - {fp['ac_id']}: {fp['reason']}")
            
            if phase_result['missing_tests']:
                print(f"  ⚠️  Missing Tests: {len(phase_result['missing_tests'])}")
                for mt in phase_result['missing_tests'][:3]:
                    print(f"     - {mt['ac_id']}: {mt['reason']}")
        
        print(f"\n{'=' * 70}")
        print(f"OVERALL:")
        print(f"  Total Claimed: {summary['total_claimed']} AC-IDs")
        print(f"  Total Verified: {summary['total_verified']} AC-IDs")
        print(f"  Accuracy: {int(summary['total_verified']/summary['total_claimed']*100) if summary['total_claimed'] > 0 else 0}%")
        print(f"{'=' * 70}")
    
    def fix_tracker(self, results: Dict) -> bool:
        """Update tracker with corrected evidence-based counts"""
        print("\n🔧 FIXING TRACKER...")
        
        tracker = json.loads(self.tracker_path.read_text())
        
        # Update Phase 1
        if 'phase_1' in results['phases']:
            p1_result = results['phases']['phase_1']
            tracker['current_phase']['completed_count'] = p1_result['verified_count']
            tracker['current_phase']['completion_percentage'] = p1_result['actual_percentage']
            tracker['current_phase']['verified_implemented'] = p1_result['verified_ac_ids']
        
        # Update Phase 2
        if 'phase_2' in results['phases']:
            p2_result = results['phases']['phase_2']
            for phase in tracker.get('completed_phases', []):
                if phase.get('number') == 2:
                    phase['completed_count'] = p2_result['verified_count']
                    phase['completion_percentage'] = p2_result['actual_percentage']
                    phase['verified_implemented'] = p2_result['verified_ac_ids']
                    # Move to in_progress if not fully verified
                    if p2_result['actual_percentage'] < 100:
                        phase['status'] = 'in_progress'
        
        # Update metadata
        tracker['last_updated'] = datetime.now(timezone.utc).isoformat()
        tracker['updated_by'] = 'Evidence-based validator (test verification)'
        
        # Write back
        self.tracker_path.write_text(json.dumps(tracker, indent=2))
        
        print(f"✅ Tracker updated: {self.tracker_path}")
        return True


def main():
    workspace_root = Path(__file__).parent.parent
    validator = EvidenceValidator(workspace_root)
    
    results = validator.validate_all()
    
    # Fix if requested
    if '--fix' in sys.argv:
        validator.fix_tracker(results)
        print("\n✅ Run: python3 scripts/sync_plan_viewer_data.py")
    else:
        print("\n💡 To apply corrections: python3 scripts/validate_tracker_evidence.py --fix")
    
    # Exit with error if discrepancies found
    if results['summary']['total_claimed'] != results['summary']['total_verified']:
        sys.exit(1)


if __name__ == '__main__':
    main()
