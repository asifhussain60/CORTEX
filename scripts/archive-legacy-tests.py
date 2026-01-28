#!/usr/bin/env python3
"""
Test Suite Archiving Script

Archives non-production-critical tests to reduce CI/CD time and improve signal clarity.

Strategy: PRESERVE-THEN-ARCHIVE (not delete)
- Identifies production-critical tests (wiring, mcp, orchestrators/core, lens, governance)
- Moves legacy/deprecated tests to tests/_archive/
- Updates pytest.ini to ignore archived tests
- Preserves historical tests for reference

Usage:
    python scripts/archive-legacy-tests.py --dry-run  # Preview changes
    python scripts/archive-legacy-tests.py            # Execute archiving

Author: Asif Hussain
Phase: 8 (Test Suite Cleanup)
AC-ID: TEST-AUDIT-001
"""

import argparse
import shutil
from pathlib import Path
from typing import List, Set
import sys


# Production-critical test patterns (KEEP ACTIVE)
PRODUCTION_PATTERNS = [
    "tests/wiring/",
    "tests/mcp/",
    "tests/orchestrators/core/",
    "tests/lens/",
    "tests/brain/analysis/",  # LENS analyzers
    "tests/governance/",
    "tests/test_governance_",  # Root-level governance tests
    "tests/collaboration/",  # Phase 5.5 team collaboration
]

# Legacy patterns to archive (MOVE TO _archive/)
ARCHIVE_PATTERNS = [
    "tests/test_ac_ar_",  # Phase 1-3 acceptance tests
    "tests/test_ac_nfr_",  # Non-functional requirement tests
    "tests/test_ac_phase",  # Old phase completion tests
    "tests/test_impl_",  # Implementation validation tests (superseded)
    "tests/test_rem_",  # Remediation tests (one-time fixes)
    "tests/test_enterprise_features.py",  # Future feature tests
    "tests/test_phase_2_5_component_wiring.py",  # Legacy wiring tests
    "tests/test_planning_naming_factory.py",  # Deprecated
    "tests/test_cortex_company_overlap.py",  # Analysis report (not test)
    "tests/test_tdd_enhancement_",  # TDD enhancement validation (Phase 4)
]


class TestArchiver:
    """Manages test suite archiving process."""
    
    def __init__(self, dry_run: bool = False):
        """
        Initialize test archiver.
        
        Args:
            dry_run: If True, only preview changes without modifying files
        """
        self.dry_run = dry_run
        self.tests_dir = Path("tests")
        self.archive_dir = Path("tests/_archive")
        self.archived_count = 0
        self.skipped_count = 0
        
    def is_production_critical(self, test_path: Path) -> bool:
        """
        Check if test is production-critical.
        
        Args:
            test_path: Path to test file
            
        Returns:
            True if test should remain active
        """
        test_str = str(test_path)
        return any(pattern in test_str for pattern in PRODUCTION_PATTERNS)
    
    def should_archive(self, test_path: Path) -> bool:
        """
        Check if test should be archived.
        
        Args:
            test_path: Path to test file
            
        Returns:
            True if test should be moved to archive
        """
        test_str = str(test_path)
        return any(pattern in test_str for pattern in ARCHIVE_PATTERNS)
    
    def find_archivable_tests(self) -> List[Path]:
        """
        Find all tests that should be archived.
        
        Returns:
            List of test file paths to archive
        """
        archivable = []
        
        # Find all test files
        for test_file in self.tests_dir.rglob("test_*.py"):
            # Skip already archived tests
            if "_archive" in str(test_file):
                continue
                
            # Skip production-critical tests
            if self.is_production_critical(test_file):
                self.skipped_count += 1
                continue
            
            # Check if should be archived
            if self.should_archive(test_file):
                archivable.append(test_file)
        
        return archivable
    
    def archive_test(self, test_path: Path) -> None:
        """
        Archive a single test file.
        
        Args:
            test_path: Path to test file to archive
        """
        # Calculate relative path from tests/
        relative_path = test_path.relative_to(self.tests_dir)
        
        # Create archive destination
        archive_dest = self.archive_dir / relative_path
        
        if self.dry_run:
            print(f"  [DRY-RUN] Would move: {test_path} -> {archive_dest}")
        else:
            # Create parent directories
            archive_dest.parent.mkdir(parents=True, exist_ok=True)
            
            # Move file
            shutil.move(str(test_path), str(archive_dest))
            print(f"  ✅ Archived: {test_path} -> {archive_dest}")
        
        self.archived_count += 1
    
    def update_pytest_ini(self) -> None:
        """Update pytest.ini to ignore archived tests."""
        pytest_ini = Path("pytest.ini")
        
        if not pytest_ini.exists():
            print("  ⚠️  pytest.ini not found, skipping update")
            return
        
        # Read current content
        content = pytest_ini.read_text()
        
        # Check if already configured
        if "--ignore=tests/_archive/" in content:
            print("  ℹ️  pytest.ini already configured to ignore _archive/")
            return
        
        # Add ignore pattern
        ignore_line = "\n    --ignore=tests/_archive/\n"
        
        if "[pytest]" in content:
            # Add to existing [pytest] section
            updated = content.replace("[pytest]", f"[pytest]{ignore_line}")
        else:
            # Create [pytest] section
            updated = f"[pytest]{ignore_line}\n{content}"
        
        if self.dry_run:
            print(f"  [DRY-RUN] Would update pytest.ini with: {ignore_line.strip()}")
        else:
            pytest_ini.write_text(updated)
            print(f"  ✅ Updated pytest.ini to ignore _archive/")
    
    def create_archive_readme(self) -> None:
        """Create README in archive directory."""
        readme_path = self.archive_dir / "README.md"
        
        readme_content = """# Archived Tests

This directory contains tests that are no longer production-critical but are preserved for historical reference.

## Why These Tests Were Archived

- **Phase 1-3 Completion Tests** (`test_ac_ar_*.py`, `test_ac_nfr_*.py`): Validated legacy phases that are now complete.
- **Remediation Tests** (`test_rem_*.py`): One-time fixes that have been validated and deployed.
- **Implementation Validation Tests** (`test_impl_*.py`): Superseded by production wiring/MCP tests.
- **TDD Enhancement Tests** (`test_tdd_enhancement_*.py`): Phase 4 validation, now in production.

## Running Archived Tests

If you need to run these tests:

```bash
# Run specific archived test
pytest tests/_archive/test_ac_ar_010_01_design.py

# Run all archived tests
pytest tests/_archive/
```

## Restoring Tests

To restore a test to active status:

```bash
# Move test back to tests/
mv tests/_archive/path/to/test_file.py tests/path/to/test_file.py
```

---

**Archive Date:** 2026-01-28  
**Archive Reason:** Test suite cleanup (Phase 8)  
**Total Archived:** See git log for count
"""
        
        if self.dry_run:
            print(f"  [DRY-RUN] Would create README at: {readme_path}")
        else:
            readme_path.parent.mkdir(parents=True, exist_ok=True)
            readme_path.write_text(readme_content)
            print(f"  ✅ Created {readme_path}")
    
    def run(self) -> None:
        """Execute the archiving process."""
        print("\n" + "="*70)
        print("CORTEX Test Suite Archiving")
        print("="*70)
        
        if self.dry_run:
            print("\n⚠️  DRY-RUN MODE: No files will be modified\n")
        
        # Find tests to archive
        print("\n🔍 Scanning for archivable tests...")
        archivable_tests = self.find_archivable_tests()
        
        print(f"\n📊 Analysis Results:")
        print(f"  - Production-critical tests (kept active): {self.skipped_count}")
        print(f"  - Tests to archive: {len(archivable_tests)}")
        
        if not archivable_tests:
            print("\n✅ No tests need archiving!")
            return
        
        # Show what will be archived
        print(f"\n📦 Tests to archive:")
        for test_path in archivable_tests[:10]:  # Show first 10
            print(f"  - {test_path}")
        if len(archivable_tests) > 10:
            print(f"  ... and {len(archivable_tests) - 10} more")
        
        # Confirm if not dry-run
        if not self.dry_run:
            print(f"\n⚠️  This will move {len(archivable_tests)} tests to tests/_archive/")
            response = input("Continue? (yes/no): ").strip().lower()
            if response not in ["yes", "y"]:
                print("❌ Aborted by user")
                return
        
        # Archive tests
        print(f"\n📦 Archiving tests...")
        for test_path in archivable_tests:
            self.archive_test(test_path)
        
        # Update pytest.ini
        print(f"\n⚙️  Updating pytest.ini...")
        self.update_pytest_ini()
        
        # Create archive README
        print(f"\n📄 Creating archive documentation...")
        self.create_archive_readme()
        
        # Summary
        print("\n" + "="*70)
        print("Summary")
        print("="*70)
        print(f"  ✅ Tests archived: {self.archived_count}")
        print(f"  ✅ Production tests kept active: {self.skipped_count}")
        
        if not self.dry_run:
            print(f"\n📝 Next steps:")
            print(f"  1. Run: pytest tests/ -v (should be faster now)")
            print(f"  2. Verify: pytest tests/_archive/ (archived tests still work)")
            print(f"  3. Commit: git add tests/ pytest.ini && git commit -m 'chore: archive legacy tests'")
        else:
            print(f"\n💡 Run without --dry-run to execute archiving")
        
        print("="*70 + "\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Archive non-production-critical tests",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview what will be archived
  python scripts/archive-legacy-tests.py --dry-run
  
  # Execute archiving
  python scripts/archive-legacy-tests.py
        """
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without modifying files"
    )
    
    args = parser.parse_args()
    
    # Run archiver
    archiver = TestArchiver(dry_run=args.dry_run)
    archiver.run()


if __name__ == "__main__":
    main()
