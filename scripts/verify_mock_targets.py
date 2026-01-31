#!/usr/bin/env python3
"""
Verify Mock Targets CI Check

Ensures that @patch decorators in test files target existing functions/classes/methods
in the codebase. Prevents obsolete mock patterns after refactoring.

This prevents test mock drift (TEST-MOCK-PATTERN-001).

Usage:
    python scripts/verify_mock_targets.py [--verbose]

Exit Codes:
    0: All mock targets verified
    1: Obsolete mocks detected
    2: Script error

AC-ID: REM-002 (Prevention Measure)
Phase: 16 (Remediation Framework)
Author: Asif Hussain
"""

import ast
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Set
from dataclasses import dataclass


@dataclass
class MockTarget:
    """Mock target specification from test file."""
    target_path: str
    test_file: Path
    line_number: int
    decorator_type: str  # "patch", "patch.object", etc.


@dataclass
class ValidationResult:
    """Result of mock target validation."""
    target_path: str
    exists: bool
    test_file: str
    line_number: int
    error_message: str = ""


class MockTargetVerifier:
    """Verifies test mock targets exist in codebase."""
    
    def __init__(self, cortex_root: Path):
        """
        Initialize verifier.
        
        Args:
            cortex_root: Root directory of CORTEX project
        """
        self.cortex_root = cortex_root
        self.tests_dir = cortex_root / "tests"
        self.cortex_dir = cortex_root / "cortex"
    
    def extract_patch_decorators(self, test_file: Path) -> List[MockTarget]:
        """
        Extract @patch decorators from test file.
        
        Args:
            test_file: Path to test file
            
        Returns:
            List of mock targets
        """
        if not test_file.exists():
            return []
        
        with open(test_file) as f:
            content = f.read()
        
        targets: List[MockTarget] = []
        
        # Pattern: @patch("module.path.to.target")
        # Pattern: @patch.object(Class, "method")
        patch_patterns = [
            (r'@patch\(["\']([^"\']+)["\']', "patch"),
            (r'@mock\.patch\(["\']([^"\']+)["\']', "mock.patch"),
        ]
        
        for pattern, decorator_type in patch_patterns:
            for match in re.finditer(pattern, content):
                target_path = match.group(1)
                # Find line number
                lines_before = content[:match.start()].count('\n')
                
                targets.append(MockTarget(
                    target_path=target_path,
                    test_file=test_file,
                    line_number=lines_before + 1,
                    decorator_type=decorator_type
                ))
        
        return targets
    
    def verify_target_exists(self, target_path: str) -> Tuple[bool, str]:
        """
        Verify that mock target exists in codebase.
        
        Args:
            target_path: Import path to target (e.g., "cortex.orchestrators.core.intent_router.IntentRouter")
            
        Returns:
            (exists, error_message) tuple
        """
        # Skip standard library and external package mocks (not our code)
        stdlib_packages = {
            "subprocess", "sys", "os", "pathlib", "json", "re", "ast", "typing",
            "datetime", "threading", "collections", "logging", "unittest", "pytest",
            "requests", "yaml", "pydantic", "fastapi", "uvicorn", "sqlalchemy",
            "external", "builtins", "shutil", "tempfile", "io", "contextlib",
            "urllib", "http", "socket", "socketserver", "email", "html", "xml", "zipfile",
        }
        
        first_part = target_path.split(".")[0]
        if first_part in stdlib_packages:
            return True, ""  # Assume stdlib/external packages exist
        
        # Parse target path
        parts = target_path.split(".")
        
        if len(parts) < 2:
            return False, "Invalid target path (too short)"
        
        # Try to find the module file
        # cortex.orchestrators.core.intent_router → cortex/orchestrators/core/intent_router.py
        module_parts = []
        target_name = parts[-1]
        
        for i in range(len(parts) - 1, 0, -1):
            module_path_parts = parts[:i]
            module_path = self.cortex_root / "/".join(module_path_parts)
            
            # Check if it's a package
            if (module_path / "__init__.py").exists():
                module_parts = module_path_parts
                break
            
            # Check if it's a module
            module_file = module_path.with_suffix(".py")
            if module_file.exists():
                module_parts = module_path_parts
                break
        
        if not module_parts:
            return False, f"Module not found: {'.'.join(parts[:-1])}"
        
        # Now verify the target exists in the module
        module_file = self.cortex_root / "/".join(module_parts)
        if not module_file.suffix:
            module_file = module_file.with_suffix(".py")
        
        if not module_file.exists():
            module_file = module_file.parent / "__init__.py"
            if not module_file.exists():
                return False, f"Module file not found: {module_file}"
        
        # Search for target in module
        try:
            with open(module_file) as f:
                content = f.read()
            
            # Check for class/function definition
            patterns = [
                rf'^class {re.escape(target_name)}\b',
                rf'^def {re.escape(target_name)}\(',
                rf'^async def {re.escape(target_name)}\(',
                rf'^\s*{re.escape(target_name)}\s*=',  # Variable assignment
            ]
            
            for pattern in patterns:
                if re.search(pattern, content, re.MULTILINE):
                    return True, ""
            
            return False, f"Target '{target_name}' not found in {module_file.name}"
            
        except Exception as e:
            return False, f"Error reading module: {e}"
    
    def scan_all_tests(self) -> List[MockTarget]:
        """
        Scan all test files for mock targets.
        
        Returns:
            List of all mock targets found
        """
        all_targets: List[MockTarget] = []
        
        for test_file in self.tests_dir.rglob("test_*.py"):
            targets = self.extract_patch_decorators(test_file)
            all_targets.extend(targets)
        
        return all_targets
    
    def validate_all_targets(self, targets: List[MockTarget]) -> List[ValidationResult]:
        """
        Validate all mock targets.
        
        Args:
            targets: List of mock targets
            
        Returns:
            List of validation results
        """
        results: List[ValidationResult] = []
        
        for target in targets:
            exists, error_msg = self.verify_target_exists(target.target_path)
            
            results.append(ValidationResult(
                target_path=target.target_path,
                exists=exists,
                test_file=str(target.test_file.relative_to(self.cortex_root)),
                line_number=target.line_number,
                error_message=error_msg
            ))
        
        return results
    
    def print_report(self, results: List[ValidationResult], verbose: bool = False) -> int:
        """
        Print validation report.
        
        Args:
            results: Validation results
            verbose: Show all results (including passed)
            
        Returns:
            Exit code (0 if all pass, 1 if failures)
        """
        print("=" * 80)
        print("🔍 MOCK TARGET VERIFICATION (REM-002)")
        print("=" * 80)
        print()
        
        passed = 0
        failed = 0
        
        # Group by test file for better readability
        by_file: Dict[str, List[ValidationResult]] = {}
        for result in results:
            if result.test_file not in by_file:
                by_file[result.test_file] = []
            by_file[result.test_file].append(result)
        
        for test_file, file_results in sorted(by_file.items()):
            file_failures = [r for r in file_results if not r.exists]
            
            if file_failures or verbose:
                print(f"📄 {test_file}")
                
                for result in file_results:
                    if result.exists:
                        if verbose:
                            print(f"   ✅ Line {result.line_number}: {result.target_path}")
                        passed += 1
                    else:
                        print(f"   ❌ Line {result.line_number}: {result.target_path}")
                        print(f"      {result.error_message}")
                        failed += 1
                
                print()
        
        print("=" * 80)
        print(f"📊 Results: {passed} valid, {failed} obsolete")
        
        if failed > 0:
            print()
            print("⚠️  Obsolete mock targets detected!")
            print("   Action: Update mock targets to reflect current codebase")
        
        print("=" * 80)
        
        return 0 if failed == 0 else 1


def main() -> int:
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Verify mock targets in test files")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show all results")
    args = parser.parse_args()
    
    cortex_root = Path.cwd()
    
    # Verify we're in CORTEX root
    if not (cortex_root / "cortex").exists():
        print("❌ Error: Run this script from CORTEX root directory")
        return 2
    
    verifier = MockTargetVerifier(cortex_root)
    targets = verifier.scan_all_tests()
    
    if not targets:
        print("✅ No @patch decorators found in tests")
        return 0
    
    results = verifier.validate_all_targets(targets)
    
    return verifier.print_report(results, verbose=args.verbose)


if __name__ == "__main__":
    sys.exit(main())
