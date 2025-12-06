"""
Test Suite Cleanup Script

Identifies and removes obsolete tests based on:
1. Tests marked with @pytest.mark.skip for removed features
2. Tests in obsolete-tests-manifest.json that still exist
3. Tests with xfail due to API changes that are never fixed

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Set, Tuple
import ast
import subprocess

# CORTEX root
CORTEX_ROOT = Path(__file__).parent.parent
MANIFEST_PATH = CORTEX_ROOT / "cortex-brain" / "obsolete-tests-manifest.json"
TESTS_DIR = CORTEX_ROOT / "tests"


class TestCleanupAnalyzer:
    """Analyze and cleanup obsolete tests."""
    
    def __init__(self):
        self.obsolete_from_manifest: List[Dict] = []
        self.skipped_tests: List[Dict] = []
        self.xfail_tests: List[Dict] = []
        self.to_delete: Set[Path] = set()
        
    def load_manifest(self) -> None:
        """Load obsolete tests manifest."""
        if MANIFEST_PATH.exists():
            with open(MANIFEST_PATH, 'r') as f:
                data = json.load(f)
                # Only include tests not already removed
                self.obsolete_from_manifest = [
                    t for t in data.get('tests', [])
                    if not t.get('removed', False)
                ]
    
    def scan_for_skip_markers(self) -> None:
        """Find tests marked with @pytest.mark.skip for removed features."""
        for test_file in TESTS_DIR.rglob("test_*.py"):
            try:
                content = test_file.read_text(encoding='utf-8')
                
                # Check for skip marker with specific reasons
                if '@pytest.mark.skip' in content:
                    # Parse to extract reason
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef) or isinstance(node, ast.ClassDef):
                            for decorator in node.decorator_list:
                                if isinstance(decorator, ast.Call):
                                    if hasattr(decorator.func, 'attr') and decorator.func.attr == 'skip':
                                        # Extract reason
                                        reason = None
                                        for keyword in decorator.keywords:
                                            if keyword.arg == 'reason':
                                                if isinstance(keyword.value, ast.Constant):
                                                    reason = keyword.value.value
                                        
                                        if reason and any(keyword in reason.lower() for keyword in [
                                            'removed from cortex',
                                            'deprecated',
                                            'no longer needed',
                                            'obsolete'
                                        ]):
                                            self.skipped_tests.append({
                                                'file': test_file,
                                                'name': node.name,
                                                'reason': reason
                                            })
            except Exception as e:
                print(f"⚠️  Error parsing {test_file}: {e}")
    
    def scan_for_xfail_markers(self) -> None:
        """Find tests with xfail that are never going to be fixed."""
        for test_file in TESTS_DIR.rglob("test_*.py"):
            try:
                content = test_file.read_text(encoding='utf-8')
                
                if '@pytest.mark.xfail' in content:
                    tree = ast.parse(content)
                    xfail_count = 0
                    
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            for decorator in node.decorator_list:
                                if isinstance(decorator, ast.Call):
                                    if hasattr(decorator.func, 'attr') and decorator.func.attr == 'xfail':
                                        xfail_count += 1
                                        
                                        # Extract reason
                                        reason = None
                                        for keyword in decorator.keywords:
                                            if keyword.arg == 'reason':
                                                if isinstance(keyword.value, ast.Constant):
                                                    reason = keyword.value.value
                                        
                                        if reason and 'needs refactoring' in reason.lower():
                                            self.xfail_tests.append({
                                                'file': test_file,
                                                'name': node.name,
                                                'reason': reason
                                            })
                    
                    # If entire file is xfail tests, mark for review
                    if xfail_count > 5:  # Threshold
                        print(f"📋 {test_file.relative_to(CORTEX_ROOT)}: {xfail_count} xfail tests")
                        
            except Exception as e:
                print(f"⚠️  Error parsing {test_file}: {e}")
    
    def verify_manifest_tests_exist(self) -> List[Dict]:
        """Check which obsolete manifest tests still exist."""
        existing_obsolete = []
        
        for test_info in self.obsolete_from_manifest:
            test_path = CORTEX_ROOT / test_info['file_path']
            if test_path.exists():
                existing_obsolete.append({
                    'file': test_path,
                    'reason': test_info['reason'],
                    'confidence': test_info.get('confidence', 0.9)
                })
        
        return existing_obsolete
    
    def generate_cleanup_plan(self) -> None:
        """Generate cleanup plan."""
        print("\n" + "="*80)
        print("🧹 CORTEX Test Suite Cleanup Analysis")
        print("="*80)
        
        # Category 1: Tests marked skip for removed features
        print(f"\n📌 Category 1: Skipped Tests (Removed Features)")
        print(f"   Count: {len(self.skipped_tests)}")
        skip_files = set(t['file'] for t in self.skipped_tests)
        for file in skip_files:
            tests_in_file = [t for t in self.skipped_tests if t['file'] == file]
            print(f"   • {file.relative_to(CORTEX_ROOT)} ({len(tests_in_file)} tests)")
            if tests_in_file:
                print(f"     Reason: {tests_in_file[0]['reason'][:80]}...")
        
        # Category 2: Obsolete manifest tests
        existing_obsolete = self.verify_manifest_tests_exist()
        print(f"\n📌 Category 2: Obsolete Manifest Tests (Still Exist)")
        print(f"   Count: {len(existing_obsolete)}")
        for i, test_info in enumerate(existing_obsolete[:10], 1):  # Show first 10
            print(f"   {i}. {test_info['file'].relative_to(CORTEX_ROOT)}")
            print(f"      Reason: {test_info['reason'][:80]}...")
        if len(existing_obsolete) > 10:
            print(f"   ... and {len(existing_obsolete) - 10} more")
        
        # Category 3: Xfail tests needing refactoring
        xfail_files = set(t['file'] for t in self.xfail_tests)
        print(f"\n📌 Category 3: Xfail Tests (Needs Refactoring)")
        print(f"   Count: {len(xfail_files)} files")
        for file in list(xfail_files)[:5]:
            tests_count = len([t for t in self.xfail_tests if t['file'] == file])
            print(f"   • {file.relative_to(CORTEX_ROOT)} ({tests_count} tests)")
        
        # Recommendation
        print(f"\n💡 Cleanup Recommendations:")
        print(f"   1. SAFE TO DELETE: Category 1 ({len(skip_files)} files)")
        print(f"      These are explicitly marked as obsolete")
        print(f"   ")
        print(f"   2. REVIEW REQUIRED: Category 2 ({len(existing_obsolete)} files)")
        print(f"      Missing imports suggest code was removed")
        print(f"   ")
        print(f"   3. FIX OR DELETE: Category 3 ({len(xfail_files)} files)")
        print(f"      Long-standing xfail tests should be fixed or removed")
        
        return skip_files, existing_obsolete, xfail_files
    
    def delete_obsolete_tests(self, skip_files: Set[Path], dry_run: bool = True) -> None:
        """Delete Category 1 tests (safe to delete)."""
        print(f"\n{'🔍 DRY RUN' if dry_run else '🗑️  DELETING'}: Removing Category 1 tests")
        
        deleted_count = 0
        for file in skip_files:
            if file.exists():
                if dry_run:
                    print(f"   Would delete: {file.relative_to(CORTEX_ROOT)}")
                else:
                    file.unlink()
                    print(f"   ✅ Deleted: {file.relative_to(CORTEX_ROOT)}")
                deleted_count += 1
        
        print(f"\n   Total: {deleted_count} files {'would be' if dry_run else ''} deleted")


def main():
    """Run cleanup analysis."""
    analyzer = TestCleanupAnalyzer()
    
    print("🔍 Loading obsolete tests manifest...")
    analyzer.load_manifest()
    print(f"   Found {len(analyzer.obsolete_from_manifest)} tests in manifest")
    
    print("\n🔍 Scanning for @pytest.mark.skip markers...")
    analyzer.scan_for_skip_markers()
    print(f"   Found {len(analyzer.skipped_tests)} skipped tests")
    
    print("\n🔍 Scanning for @pytest.mark.xfail markers...")
    analyzer.scan_for_xfail_markers()
    print(f"   Found {len(analyzer.xfail_tests)} xfail tests")
    
    skip_files, existing_obsolete, xfail_files = analyzer.generate_cleanup_plan()
    
    # Ask for confirmation
    print("\n" + "="*80)
    if '--execute' in sys.argv:
        analyzer.delete_obsolete_tests(skip_files, dry_run=False)
        print("\n✅ Cleanup complete!")
    else:
        print("\n💡 To execute cleanup, run:")
        print(f"   python {Path(__file__).name} --execute")
        print("\n   This is a DRY RUN. No files were deleted.")


if __name__ == "__main__":
    main()
