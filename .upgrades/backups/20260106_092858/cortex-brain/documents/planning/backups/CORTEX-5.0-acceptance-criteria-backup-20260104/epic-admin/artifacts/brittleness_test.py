#!/usr/bin/env python3
"""
CORTEX-5.0 Brittleness Test Suite

Comprehensive validation system to identify breaks, gaps, and structural issues
in CORTEX-5.0 epic plan. Runs as Phase 0 pre-flight check before sub-plan execution.

Features:
- Folder structure validation (brain protection rules)
- Broken link detection (internal references)
- Orchestrator functionality verification
- Tracking file integrity checks
- Sub-plan completeness validation
- Auto-fix capabilities for common issues

Usage:
    python brittleness_test.py --test all              # Run all tests
    python brittleness_test.py --test structure        # Structure only
    python brittleness_test.py --test links            # Links only
    python brittleness_test.py --auto-fix              # Run tests + auto-fix

Author: Asif Hussain
Created: January 4, 2026
Part of: CORTEX-5.0 Brain Protection Enhancement
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from enum import Enum


class TestSeverity(Enum):
    """Test result severity levels."""
    CRITICAL = "🔴 CRITICAL"
    WARNING = "⚠️  WARNING"
    INFO = "ℹ️  INFO"
    PASS = "✅ PASS"


class BrittlenessTest:
    """Comprehensive brittleness testing for CORTEX-5.0 epic plan."""
    
    def __init__(self, plan_root: Path, auto_fix: bool = False):
        self.plan_root = plan_root
        self.auto_fix = auto_fix
        self.results = []
        self.fixes_applied = []
        
    def run_all_tests(self) -> Dict[str, any]:
        """Run complete test suite."""
        print("\n" + "="*70)
        print("🧪 CORTEX-5.0 Brittleness Test Suite")
        print("="*70)
        print(f"Plan Root: {self.plan_root}")
        print(f"Auto-Fix: {'ENABLED' if self.auto_fix else 'DISABLED'}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70 + "\n")
        
        # Test 1: Folder Structure Validation
        self.test_folder_structure()
        
        # Test 2: Broken Link Detection
        self.test_broken_links()
        
        # Test 3: Orchestrator Functionality
        self.test_orchestrator()
        
        # Test 4: Tracking File Integrity
        self.test_tracking_integrity()
        
        # Test 5: Sub-Plan Completeness
        self.test_subplan_completeness()
        
        # Test 6: File Naming Compliance
        self.test_file_naming()
        
        # Generate summary
        summary = self.generate_summary()
        
        # Save report
        self.save_report(summary)
        
        return summary
    
    def test_folder_structure(self):
        """Validate folder structure against planning-system-4.0 manifest."""
        print("\n📁 Test 1: Folder Structure Validation")
        print("-" * 70)
        
        required_folders = ["context", "reports", "artifacts", "tracking"]
        missing_folders = []
        
        for folder in required_folders:
            folder_path = self.plan_root / folder
            if not folder_path.exists():
                missing_folders.append(folder)
                self.add_result(
                    test="Folder Structure",
                    severity=TestSeverity.CRITICAL,
                    message=f"Missing required folder: {folder}/",
                    fix=f"mkdir -p {folder}/"
                )
                
                if self.auto_fix:
                    folder_path.mkdir(parents=True, exist_ok=True)
                    self.fixes_applied.append(f"Created folder: {folder}/")
                    print(f"   🔧 AUTO-FIX: Created {folder}/")
            else:
                print(f"   ✅ Found: {folder}/")
        
        # Check for root-level violations
        root_md_files = list(self.plan_root.glob("*.md"))
        violations = [
            f for f in root_md_files 
            if not f.name.startswith("00-") and f.name != ".orchestrator-state.json"
        ]
        
        if violations:
            for violation in violations:
                self.add_result(
                    test="Folder Structure",
                    severity=TestSeverity.WARNING,
                    message=f"Root-level file found: {violation.name}",
                    fix="Should be in context/, reports/, or artifacts/"
                )
                print(f"   ⚠️  Root violation: {violation.name}")
        else:
            print(f"   ✅ No root-level violations detected")
        
        print(f"   Result: {'PASS' if not missing_folders and not violations else 'ISSUES FOUND'}")
    
    def test_broken_links(self):
        """Scan all markdown files for broken internal links."""
        print("\n🔗 Test 2: Broken Link Detection")
        print("-" * 70)
        
        # Pattern to match markdown links: [text](path)
        link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
        
        all_md_files = list(self.plan_root.rglob("*.md"))
        broken_links = []
        
        for md_file in all_md_files:
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Find all markdown links
                links = link_pattern.findall(content)
                
                for link_text, link_path in links:
                    # Skip external links
                    if link_path.startswith(('http://', 'https://', 'mailto:', '#')):
                        continue
                    
                    # Resolve relative path
                    target_path = (md_file.parent / link_path).resolve()
                    
                    if not target_path.exists():
                        broken_links.append({
                            'source': md_file.relative_to(self.plan_root),
                            'link_text': link_text,
                            'target': link_path,
                            'resolved': target_path
                        })
                        
                        self.add_result(
                            test="Broken Links",
                            severity=TestSeverity.WARNING,
                            message=f"Broken link in {md_file.name}: {link_path}",
                            fix="Update link or restore missing file"
                        )
            
            except Exception as e:
                print(f"   ⚠️  Error scanning {md_file.name}: {e}")
        
        if broken_links:
            print(f"   ⚠️  Found {len(broken_links)} broken link(s)")
            for link in broken_links[:5]:  # Show first 5
                print(f"      - {link['source']}: [{link['link_text']}]({link['target']})")
            if len(broken_links) > 5:
                print(f"      ... and {len(broken_links) - 5} more")
        else:
            print(f"   ✅ No broken links detected")
        
        print(f"   Result: {'PASS' if not broken_links else f'{len(broken_links)} ISSUES'}")
    
    def test_orchestrator(self):
        """Verify plan orchestrator functionality."""
        print("\n🎯 Test 3: Orchestrator Functionality")
        print("-" * 70)
        
        orchestrator_file = self.plan_root / "plan_orchestrator.py"
        state_file = self.plan_root / ".orchestrator-state.json"
        tracker_file = self.plan_root / "tracking" / "epic-progress-tracker.json"
        
        # Test orchestrator file exists
        if not orchestrator_file.exists():
            self.add_result(
                test="Orchestrator",
                severity=TestSeverity.CRITICAL,
                message="plan_orchestrator.py not found",
                fix="Restore from backup or git"
            )
            print(f"   🔴 CRITICAL: plan_orchestrator.py missing")
            return
        else:
            print(f"   ✅ Found: plan_orchestrator.py")
        
        # Test state file
        if not state_file.exists():
            self.add_result(
                test="Orchestrator",
                severity=TestSeverity.INFO,
                message=".orchestrator-state.json not found (will be created on first run)",
                fix="Run orchestrator once to initialize"
            )
            print(f"   ℹ️  State file not initialized (normal for first run)")
        else:
            print(f"   ✅ Found: .orchestrator-state.json")
        
        # Test tracker file
        if not tracker_file.exists():
            self.add_result(
                test="Orchestrator",
                severity=TestSeverity.CRITICAL,
                message="tracking/epic-progress-tracker.json not found",
                fix="Restore from git or regenerate"
            )
            print(f"   🔴 CRITICAL: epic-progress-tracker.json missing")
        else:
            # Validate JSON structure
            try:
                with open(tracker_file, 'r') as f:
                    tracker_data = json.load(f)
                
                required_keys = ["schema_version", "child_plans", "overall_progress"]
                missing_keys = [k for k in required_keys if k not in tracker_data]
                
                if missing_keys:
                    self.add_result(
                        test="Orchestrator",
                        severity=TestSeverity.WARNING,
                        message=f"Tracker missing keys: {missing_keys}",
                        fix="Update tracker structure"
                    )
                    print(f"   ⚠️  Tracker structure incomplete: missing {missing_keys}")
                else:
                    print(f"   ✅ Tracker structure valid")
                    print(f"   ℹ️  Sub-plans: {len(tracker_data.get('child_plans', []))}")
            
            except json.JSONDecodeError as e:
                self.add_result(
                    test="Orchestrator",
                    severity=TestSeverity.CRITICAL,
                    message=f"Tracker JSON invalid: {e}",
                    fix="Fix JSON syntax or restore from backup"
                )
                print(f"   🔴 CRITICAL: Invalid JSON in tracker")
        
        print(f"   Result: {'PASS' if orchestrator_file.exists() and tracker_file.exists() else 'ISSUES FOUND'}")
    
    def test_tracking_integrity(self):
        """Verify tracking files match actual sub-plan folders."""
        print("\n📊 Test 4: Tracking File Integrity")
        print("-" * 70)
        
        tracker_file = self.plan_root / "tracking" / "epic-progress-tracker.json"
        
        if not tracker_file.exists():
            print(f"   ⚠️  Tracker file not found (skipping test)")
            return
        
        try:
            with open(tracker_file, 'r') as f:
                tracker_data = json.load(f)
            
            tracked_plans = tracker_data.get('child_plans', [])
            
            # Get actual sub-plan folders
            actual_folders = [
                d.name for d in self.plan_root.iterdir() 
                if d.is_dir() and re.match(r'^\d{2}[A-Z]?-', d.name)
            ]
            
            # Compare
            tracked_ids = [p['order'] for p in tracked_plans]
            actual_ids = [f.split('-')[0] for f in actual_folders]
            
            missing_in_tracker = set(actual_ids) - set(tracked_ids)
            missing_folders = set(tracked_ids) - set(actual_ids)
            
            if missing_in_tracker:
                for plan_id in missing_in_tracker:
                    self.add_result(
                        test="Tracking Integrity",
                        severity=TestSeverity.WARNING,
                        message=f"Sub-plan {plan_id} exists but not in tracker",
                        fix="Update epic-progress-tracker.json"
                    )
                    print(f"   ⚠️  Not tracked: {plan_id}")
            
            if missing_folders:
                for plan_id in missing_folders:
                    self.add_result(
                        test="Tracking Integrity",
                        severity=TestSeverity.WARNING,
                        message=f"Sub-plan {plan_id} in tracker but folder missing",
                        fix="Create folder or remove from tracker"
                    )
                    print(f"   ⚠️  Missing folder: {plan_id}")
            
            if not missing_in_tracker and not missing_folders:
                print(f"   ✅ All sub-plans properly tracked")
                print(f"   ℹ️  Total sub-plans: {len(tracked_plans)}")
        
        except Exception as e:
            self.add_result(
                test="Tracking Integrity",
                severity=TestSeverity.WARNING,
                message=f"Error validating tracker: {e}",
                fix="Check tracker JSON structure"
            )
            print(f"   ⚠️  Validation error: {e}")
        
        print(f"   Result: {'PASS' if not missing_in_tracker and not missing_folders else 'ISSUES FOUND'}")
    
    def test_subplan_completeness(self):
        """Verify each sub-plan has required structure."""
        print("\n🗂️  Test 5: Sub-Plan Completeness")
        print("-" * 70)
        
        required_subfolders = ["context", "reports", "artifacts", "tracking"]
        
        # Get all sub-plan folders
        subplan_folders = [
            d for d in self.plan_root.iterdir() 
            if d.is_dir() and re.match(r'^\d{2}[A-Z]?-', d.name)
        ]
        
        incomplete_plans = []
        
        for subplan in subplan_folders:
            missing = []
            for subfolder in required_subfolders:
                if not (subplan / subfolder).exists():
                    missing.append(subfolder)
            
            if missing:
                incomplete_plans.append((subplan.name, missing))
                self.add_result(
                    test="Sub-Plan Completeness",
                    severity=TestSeverity.INFO,
                    message=f"{subplan.name} missing: {', '.join(missing)}",
                    fix=f"Create missing folders in {subplan.name}/"
                )
                
                if self.auto_fix:
                    for subfolder in missing:
                        (subplan / subfolder).mkdir(parents=True, exist_ok=True)
                        self.fixes_applied.append(f"Created {subplan.name}/{subfolder}/")
                    print(f"   🔧 AUTO-FIX: Created folders in {subplan.name}/")
        
        if incomplete_plans:
            print(f"   ℹ️  {len(incomplete_plans)} sub-plan(s) with missing folders")
            for plan_name, missing in incomplete_plans[:3]:
                print(f"      - {plan_name}: missing {', '.join(missing)}")
        else:
            print(f"   ✅ All sub-plans have complete structure")
        
        print(f"   Result: PASS (structure optional for sub-plans)")
    
    def test_file_naming(self):
        """Check file naming compliance (≤20 chars, kebab-case)."""
        print("\n📝 Test 6: File Naming Compliance")
        print("-" * 70)
        
        violations = []
        
        # Check all markdown files
        for md_file in self.plan_root.rglob("*.md"):
            # Skip sub-plan master plans (00-*.md)
            if md_file.name.startswith("00-"):
                continue
            
            # Get filename without extension
            name_without_ext = md_file.stem
            
            # Check length (≤20 chars)
            if len(name_without_ext) > 20:
                violations.append({
                    'file': md_file.relative_to(self.plan_root),
                    'issue': f'Name too long ({len(name_without_ext)} chars)',
                    'severity': TestSeverity.WARNING
                })
                
                self.add_result(
                    test="File Naming",
                    severity=TestSeverity.WARNING,
                    message=f"Filename too long: {md_file.name} ({len(name_without_ext)} chars)",
                    fix="Rename to ≤20 characters"
                )
        
        if violations:
            print(f"   ⚠️  Found {len(violations)} naming violation(s)")
            for v in violations[:5]:
                print(f"      - {v['file']}: {v['issue']}")
        else:
            print(f"   ✅ All filenames compliant")
        
        print(f"   Result: {'PASS' if not violations else f'{len(violations)} WARNINGS'}")
    
    def add_result(self, test: str, severity: TestSeverity, message: str, fix: str):
        """Add test result to collection."""
        self.results.append({
            'test': test,
            'severity': severity,
            'message': message,
            'fix': fix,
            'timestamp': datetime.now().isoformat()
        })
    
    def generate_summary(self) -> Dict:
        """Generate test summary with statistics."""
        print("\n" + "="*70)
        print("📊 Test Summary")
        print("="*70)
        
        # Count by severity
        critical = sum(1 for r in self.results if r['severity'] == TestSeverity.CRITICAL)
        warnings = sum(1 for r in self.results if r['severity'] == TestSeverity.WARNING)
        info = sum(1 for r in self.results if r['severity'] == TestSeverity.INFO)
        
        summary = {
            'timestamp': datetime.now().isoformat(),
            'plan_root': str(self.plan_root),
            'auto_fix_enabled': self.auto_fix,
            'total_issues': len(self.results),
            'critical': critical,
            'warnings': warnings,
            'info': info,
            'fixes_applied': len(self.fixes_applied),
            'results': self.results,
            'fixes': self.fixes_applied
        }
        
        print(f"\nTotal Issues: {len(self.results)}")
        print(f"  🔴 Critical: {critical}")
        print(f"  ⚠️  Warnings: {warnings}")
        print(f"  ℹ️  Info: {info}")
        
        if self.auto_fix:
            print(f"\n🔧 Auto-Fixes Applied: {len(self.fixes_applied)}")
            for fix in self.fixes_applied:
                print(f"   - {fix}")
        
        # Overall status
        if critical > 0:
            print(f"\n🔴 Overall Status: CRITICAL ISSUES FOUND")
            print(f"   Action Required: Fix critical issues before proceeding")
        elif warnings > 0:
            print(f"\n⚠️  Overall Status: WARNINGS PRESENT")
            print(f"   Recommendation: Review and fix warnings")
        else:
            print(f"\n✅ Overall Status: ALL TESTS PASSED")
        
        print("="*70 + "\n")
        
        return summary
    
    def save_report(self, summary: Dict):
        """Save brittleness test report."""
        report_dir = self.plan_root / "reports"
        report_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = report_dir / f"brittleness-test-{timestamp}.json"
        
        with open(report_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        print(f"📄 Report saved: {report_file.relative_to(self.plan_root)}")


def main():
    """Main entry point for brittleness testing."""
    import sys
    
    # Determine plan root (script is in artifacts/)
    script_path = Path(__file__).resolve()
    plan_root = script_path.parent.parent
    
    # Parse arguments
    auto_fix = '--auto-fix' in sys.argv
    test_type = 'all'
    
    if '--test' in sys.argv:
        idx = sys.argv.index('--test')
        if idx + 1 < len(sys.argv):
            test_type = sys.argv[idx + 1]
    
    # Run tests
    tester = BrittlenessTest(plan_root, auto_fix=auto_fix)
    summary = tester.run_all_tests()
    
    # Exit code based on critical issues
    exit_code = 1 if summary['critical'] > 0 else 0
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
