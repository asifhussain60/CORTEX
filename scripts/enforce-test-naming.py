"""
File Naming Enforcement Script

Scans test files and enforces CORE-028 (kebab-case) naming.

Authority: AC-GOLDEN-FRAMEWORK-001
Governance: CORE-028

Usage:
    python scripts/enforce-test-naming.py --check     # Check only (CI mode)
    python scripts/enforce-test-naming.py --fix       # Auto-fix violations
"""
import argparse
import re
import sys
from pathlib import Path
from typing import List, Tuple


class NamingViolation:
    """Represents a file naming violation."""
    
    def __init__(self, file_path: Path, violation_type: str, suggested_name: str):
        self.file_path = file_path
        self.violation_type = violation_type
        self.suggested_name = suggested_name
    
    def __str__(self) -> str:
        return (
            f"  {self.file_path}\n"
            f"    Violation: {self.violation_type}\n"
            f"    Suggested: {self.suggested_name}"
        )


def scan_test_files(base_dir: Path = Path("tests")) -> List[NamingViolation]:
    """
    Scan test files for naming violations.
    
    Args:
        base_dir: Base directory to scan
        
    Returns:
        List of naming violations
    """
    violations = []
    
    for test_file in base_dir.rglob("*.py"):
        # Skip __init__.py and base classes
        if test_file.name.startswith("__") or test_file.name.startswith("base-"):
            continue
        
        filename = test_file.name
        stem = test_file.stem
        
        # Check for SCREAMING_CASE
        if filename.isupper():
            suggested = filename.lower()
            violations.append(
                NamingViolation(
                    test_file,
                    "SCREAMING_CASE (CORE-028)",
                    suggested
                )
            )
            continue
        
        # Check for snake_case in test files
        if filename.startswith("test_"):
            # Convert test_foo_bar.py → test-foo-bar.py
            name_part = stem[5:]  # Remove "test_"
            if "_" in name_part:
                suggested = f"test-{name_part.replace('_', '-')}.py"
                violations.append(
                    NamingViolation(
                        test_file,
                        "snake_case (should be kebab-case per CORE-028)",
                        suggested
                    )
                )
                continue
        
        # Check for CamelCase
        if any(c.isupper() for c in stem):
            # Convert TestFooBar.py → test-foo-bar.py
            suggested_stem = re.sub(r'([A-Z])', r'-\1', stem).lower().lstrip('-')
            if not suggested_stem.startswith("test-"):
                suggested_stem = f"test-{suggested_stem}"
            suggested = f"{suggested_stem}.py"
            violations.append(
                NamingViolation(
                    test_file,
                    "CamelCase (should be kebab-case per CORE-028)",
                    suggested
                )
            )
            continue
        
        # Check for version suffixes (CORE-066)
        version_pattern = r"[-_]v\d+$"
        if re.search(version_pattern, stem):
            suggested = re.sub(version_pattern, "", stem) + ".py"
            violations.append(
                NamingViolation(
                    test_file,
                    "Version suffix (CORE-066 forbids _v2, -v3, etc.)",
                    suggested
                )
            )
    
    return violations


def fix_violations(violations: List[NamingViolation]) -> int:
    """
    Fix naming violations by renaming files.
    
    Args:
        violations: List of violations to fix
        
    Returns:
        Number of files renamed
    """
    renamed_count = 0
    
    for violation in violations:
        old_path = violation.file_path
        new_path = old_path.parent / violation.suggested_name
        
        if new_path.exists():
            print(f"⚠️  Cannot rename {old_path}: {new_path} already exists")
            continue
        
        try:
            old_path.rename(new_path)
            print(f"✅ Renamed: {old_path.name} → {new_path.name}")
            renamed_count += 1
        except Exception as e:
            print(f"❌ Failed to rename {old_path}: {e}")
    
    return renamed_count


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Enforce CORE-028 test file naming (kebab-case)"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check only (exit 1 if violations found)"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Auto-fix naming violations"
    )
    parser.add_argument(
        "--base-dir",
        type=Path,
        default=Path("tests"),
        help="Base directory to scan (default: tests/)"
    )
    
    args = parser.parse_args()
    
    if not args.check and not args.fix:
        parser.error("Must specify either --check or --fix")
    
    print(f"🔍 Scanning {args.base_dir} for naming violations...")
    violations = scan_test_files(args.base_dir)
    
    if not violations:
        print("✅ No naming violations found. All test files comply with CORE-028.")
        return 0
    
    print(f"\n❌ Found {len(violations)} naming violation(s):\n")
    for violation in violations:
        print(violation)
    
    if args.check:
        print("\n❌ CI CHECK FAILED: Naming violations detected")
        print("   Run: python scripts/enforce-test-naming.py --fix")
        return 1
    
    if args.fix:
        print(f"\n🔧 Fixing {len(violations)} violations...")
        renamed = fix_violations(violations)
        print(f"\n✅ Renamed {renamed}/{len(violations)} files")
        return 0 if renamed == len(violations) else 1


if __name__ == "__main__":
    sys.exit(main())
