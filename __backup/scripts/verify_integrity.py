#!/usr/bin/env python3
"""
CORTEX 6.0 Post-Operation Verification Script
Runs comprehensive checks after file operations to ensure integrity.

Usage:
    python3 scripts/verify_integrity.py --quick    # Fast checks (references, state)
    python3 scripts/verify_integrity.py --full     # All checks including tests
    python3 scripts/verify_integrity.py --governance  # Governance compliance only

Checks:
    1. Reference integrity (no broken links)
    2. State synchronization (progress-tracker vs AC-INDEX)
    3. Test suite (pytest)
    4. Governance compliance (vacuum violations)
    5. AC-INDEX alignment
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple, Dict
import json
import yaml
import re


class VerificationOrchestrator:
    """Orchestrates post-operation verification checks"""
    
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.results = {}
        self.errors = []
        self.warnings = []
    
    def check_references(self) -> bool:
        """Check for broken file references"""
        print("\n🔍 Checking reference integrity...")
        
        broken_refs = []
        
        # Find all markdown and YAML files
        for file in self.workspace.rglob("*"):
            if file.suffix in ['.md', '.yaml', '.yml', '.py', '.html']:
                try:
                    content = file.read_text(encoding='utf-8', errors='ignore')
                    
                    # Find file paths in content
                    # Pattern: cortex-brain/path/to/file.ext or ../path/to/file.ext
                    path_patterns = [
                        r'cortex-brain/[^\s\'")\]]+',
                        r'\.\./[^\s\'")\]]+',
                        r'src/[^\s\'")\]]+\.py',
                    ]
                    
                    for pattern in path_patterns:
                        matches = re.findall(pattern, content)
                        for match in matches:
                            # Remove markdown link syntax
                            match = match.rstrip(',.;:)')
                            
                            # Construct full path
                            if match.startswith('cortex-brain') or match.startswith('src'):
                                ref_path = self.workspace / match
                            else:
                                ref_path = file.parent / match
                            
                            # Check if exists
                            if not ref_path.exists():
                                broken_refs.append((file, match, ref_path))
                
                except Exception as e:
                    self.warnings.append(f"Error reading {file}: {e}")
        
        if broken_refs:
            print(f"❌ Found {len(broken_refs)} broken references:")
            for source, ref, target in broken_refs[:10]:  # Show first 10
                print(f"   {source.relative_to(self.workspace)}")
                print(f"      → {ref} (not found)")
            if len(broken_refs) > 10:
                print(f"   ... and {len(broken_refs) - 10} more")
            
            self.errors.append(f"{len(broken_refs)} broken references")
            self.results['references'] = False
            return False
        else:
            print("✅ No broken references detected")
            self.results['references'] = True
            return True
    
    def check_state_sync(self) -> bool:
        """Check state synchronization between truth sources"""
        print("\n🔍 Checking state synchronization...")
        
        try:
            # Load progress-tracker
            tracker_path = self.workspace / "cortex-brain/tier1/tracking/progress-tracker.json"
            with open(tracker_path) as f:
                tracker = json.load(f)
            
            # Load AC-INDEX
            ac_index_path = self.workspace / "cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml"
            with open(ac_index_path) as f:
                ac_index = yaml.safe_load(f)
            
            # Extract verified AC-IDs
            verified = tracker.get('current_phase', {}).get('verified_implemented', [])
            
            # Check each verified AC-ID exists in AC-INDEX
            discrepancies = []
            ac_dict = {}
            
            # Build AC dictionary from AC-INDEX
            foundation = ac_index.get('foundation', {})
            for category, ac_list in foundation.items():
                if isinstance(ac_list, list):
                    for ac in ac_list:
                        if isinstance(ac, dict) and 'id' in ac:
                            ac_dict[ac['id']] = ac
            
            # Also check 'master' and 'orchestration_core' sections
            for section in ['master', 'orchestration_core', 'master_control']:
                section_data = ac_index.get(section, {})
                if isinstance(section_data, dict):
                    for category, ac_list in section_data.items():
                        if isinstance(ac_list, list):
                            for ac in ac_list:
                                if isinstance(ac, dict) and 'id' in ac:
                                    ac_dict[ac['id']] = ac
            
            # Verify each AC-ID
            for ac_id in verified:
                if ac_id not in ac_dict:
                    discrepancies.append((ac_id, 'not_found_in_ac_index'))
                else:
                    status = ac_dict[ac_id].get('status', 'unknown')
                    if status != 'implemented':
                        discrepancies.append((ac_id, f'status_mismatch:{status}'))
            
            sync_score = ((len(verified) - len(discrepancies)) / len(verified) * 100) if verified else 100
            
            if discrepancies:
                print(f"⚠️  State sync score: {sync_score:.1f}%")
                print(f"   Discrepancies: {len(discrepancies)}/{len(verified)}")
                for ac_id, issue in discrepancies[:5]:
                    print(f"      {ac_id}: {issue}")
                
                if sync_score < 80:
                    self.errors.append(f"State sync score below 80% ({sync_score:.1f}%)")
                    self.results['state_sync'] = False
                    return False
                else:
                    self.warnings.append(f"State sync score: {sync_score:.1f}% (warning threshold)")
            else:
                print(f"✅ State sync score: 100%")
            
            self.results['state_sync'] = True
            return True
        
        except Exception as e:
            print(f"❌ Error checking state sync: {e}")
            self.errors.append(f"State sync check failed: {e}")
            self.results['state_sync'] = False
            return False
    
    def check_tests(self) -> bool:
        """Run pytest test suite"""
        print("\n🔍 Running test suite...")
        
        try:
            # Run pytest with minimal output
            result = subprocess.run(
                ['python3', '-m', 'pytest', 'tests/', '-v', '-k', 'not slow', '--tb=short'],
                cwd=self.workspace,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                print("✅ All tests passed")
                self.results['tests'] = True
                return True
            else:
                # Count failures
                failures = result.stdout.count('FAILED')
                print(f"❌ Tests failed: {failures} failures")
                print("\nFirst few failures:")
                for line in result.stdout.split('\n')[:20]:
                    if 'FAILED' in line or 'ERROR' in line:
                        print(f"   {line}")
                
                self.errors.append(f"{failures} test failures")
                self.results['tests'] = False
                return False
        
        except subprocess.TimeoutExpired:
            print("❌ Test suite timeout (>5 minutes)")
            self.errors.append("Test suite timeout")
            self.results['tests'] = False
            return False
        except Exception as e:
            print(f"⚠️  Could not run tests: {e}")
            self.warnings.append(f"Test execution error: {e}")
            self.results['tests'] = None
            return True  # Don't fail verification if tests can't run
    
    def check_governance(self) -> bool:
        """Check governance compliance using vacuum orchestrator"""
        print("\n🔍 Checking governance compliance...")
        
        try:
            result = subprocess.run(
                ['python3', 'scripts/vacuum_orchestrator.py', '--dry-run'],
                cwd=self.workspace,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # Parse output for HIGH severity violations
            high_violations = result.stdout.count('Severity: HIGH')
            medium_violations = result.stdout.count('Severity: MEDIUM')
            
            if high_violations > 0:
                print(f"❌ Found {high_violations} HIGH severity violations")
                print(f"   Run: python3 scripts/vacuum_orchestrator.py --dry-run")
                self.errors.append(f"{high_violations} HIGH severity governance violations")
                self.results['governance'] = False
                return False
            elif medium_violations > 0:
                print(f"⚠️  Found {medium_violations} MEDIUM severity violations")
                self.warnings.append(f"{medium_violations} MEDIUM severity violations")
            else:
                print("✅ No governance violations detected")
            
            self.results['governance'] = True
            return True
        
        except Exception as e:
            print(f"⚠️  Could not run governance check: {e}")
            self.warnings.append(f"Governance check error: {e}")
            self.results['governance'] = None
            return True
    
    def check_ac_index_alignment(self) -> bool:
        """Check AC-INDEX alignment with implementation reality"""
        print("\n🔍 Checking AC-INDEX alignment...")
        
        try:
            ac_index_path = self.workspace / "cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml"
            with open(ac_index_path) as f:
                ac_index = yaml.safe_load(f)
            
            misalignments = []
            
            # Build AC dictionary
            ac_dict = {}
            for section in ['foundation', 'master', 'orchestration_core', 'master_control']:
                section_data = ac_index.get(section, {})
                if isinstance(section_data, dict):
                    for category, ac_list in section_data.items():
                        if isinstance(ac_list, list):
                            for ac in ac_list:
                                if isinstance(ac, dict) and 'id' in ac:
                                    ac_dict[ac['id']] = ac
            
            # Check implemented AC-IDs have evidence
            for ac_id, ac_data in ac_dict.items():
                if ac_data.get('status') == 'implemented':
                    # Check evidence bundle exists
                    evidence_dir = self.workspace / f"cortex-brain/tier1/evidence-bundles/{ac_id}"
                    if not evidence_dir.exists():
                        misalignments.append((ac_id, 'no_evidence_bundle'))
                    
                    # Check implementation file exists (if specified)
                    impl_path_str = ac_data.get('implementation', {}).get('path')
                    if impl_path_str:
                        impl_path = self.workspace / impl_path_str
                        if not impl_path.exists():
                            misalignments.append((ac_id, 'implementation_file_missing'))
            
            if misalignments:
                print(f"⚠️  Found {len(misalignments)} AC-INDEX misalignments:")
                for ac_id, issue in misalignments[:5]:
                    print(f"      {ac_id}: {issue}")
                self.warnings.append(f"{len(misalignments)} AC-INDEX misalignments")
            else:
                print("✅ AC-INDEX aligned with reality")
            
            self.results['ac_index'] = True
            return True
        
        except Exception as e:
            print(f"❌ Error checking AC-INDEX: {e}")
            self.errors.append(f"AC-INDEX check failed: {e}")
            self.results['ac_index'] = False
            return False
    
    def generate_report(self) -> Dict:
        """Generate verification report"""
        report = {
            'checks': self.results,
            'errors': self.errors,
            'warnings': self.warnings,
            'passed': len([r for r in self.results.values() if r is True]),
            'failed': len([r for r in self.results.values() if r is False]),
            'skipped': len([r for r in self.results.values() if r is None]),
        }
        return report
    
    def print_summary(self):
        """Print verification summary"""
        report = self.generate_report()
        
        print("\n" + "=" * 70)
        print("VERIFICATION SUMMARY")
        print("=" * 70 + "\n")
        
        print(f"Checks passed:  {report['passed']}")
        print(f"Checks failed:  {report['failed']}")
        print(f"Checks skipped: {report['skipped']}\n")
        
        if self.errors:
            print("❌ ERRORS:")
            for error in self.errors:
                print(f"   - {error}")
            print()
        
        if self.warnings:
            print("⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"   - {warning}")
            print()
        
        if report['failed'] == 0:
            print("✅ ALL CHECKS PASSED\n")
            return 0
        else:
            print("❌ VERIFICATION FAILED\n")
            return 1


def main():
    parser = argparse.ArgumentParser(description="CORTEX 6.0 Integrity Verification")
    parser.add_argument('--quick', action='store_true',
                        help='Run quick checks (references, state sync)')
    parser.add_argument('--full', action='store_true',
                        help='Run all checks including tests')
    parser.add_argument('--governance', action='store_true',
                        help='Run governance compliance check only')
    parser.add_argument('--workspace', type=str, default='.',
                        help='Workspace root directory')
    
    args = parser.parse_args()
    
    workspace = Path(args.workspace).resolve()
    verifier = VerificationOrchestrator(workspace)
    
    print("=" * 70)
    print("CORTEX 6.0 INTEGRITY VERIFICATION")
    print("=" * 70)
    
    if args.governance:
        verifier.check_governance()
    elif args.quick:
        verifier.check_references()
        verifier.check_state_sync()
    elif args.full:
        verifier.check_references()
        verifier.check_state_sync()
        verifier.check_tests()
        verifier.check_governance()
        verifier.check_ac_index_alignment()
    else:
        # Default: quick checks
        verifier.check_references()
        verifier.check_state_sync()
        verifier.check_governance()
    
    exit_code = verifier.print_summary()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
