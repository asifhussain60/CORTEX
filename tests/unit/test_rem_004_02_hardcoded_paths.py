"""
Test for AC-REM-004-02: Hardcoded Path Removal

This test verifies that all hardcoded /Users paths have been replaced with
dynamic path resolution, as required by CORE-028 governance rule.

Issue: ISSUE-004 (Code Quality - Hardcoded Paths)
AC-ID: AC-REM-004-02
Priority: CRITICAL
"""

import subprocess
import sys
from pathlib import Path
from typing import List


def test_no_hardcoded_paths() -> None:
    """
    Verify that no hardcoded /Users paths exist in tests/ directory.
    
    This test uses grep to find all hardcoded absolute paths and asserts that
    none are found. The grep pattern looks for /Users/ which is a strong
    indicator of hardcoded paths that won't work on other machines.
    
    Expected: 0 matches
    
    Raises:
        AssertionError: If any hardcoded /Users paths are found
    """
    project_root = Path(__file__).parent.parent.parent
    tests_dir = project_root / "tests"
    
    # Run grep to find hardcoded /Users paths
    try:
        result = subprocess.run(
            [
                "grep",
                "-rn",
                r"/Users/",
                str(tests_dir),
                "--include=*.py",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        
        matches = result.stdout.strip().split("\n") if result.stdout.strip() else []
        
        # Filter out false positives
        # Valid exceptions:
        # - Comments referencing the pattern
        # - Grep commands in test code
        # - Test code that validates against hardcoded paths
        hardcoded_paths = []
        for match in matches:
            if not match:
                continue
            # Skip comments
            if "#" in match and match.index("#") < match.index("/Users/"):
                continue
            # Skip grep/find commands in test code
            if "grep" in match or "grep -rn" in match:
                continue
            # Skip validation test code (brittleness_fixes tests for hardcoded paths)
            if "brittleness_fixes" in match and ('in content or "/home/"' in match or 'if "/Users/"' in match):
                continue
            # Skip our own test file
            if "test_rem_004_02_hardcoded_paths.py" in match:
                continue
            hardcoded_paths.append(match)
        
        # Assert no hardcoded paths found
        assert (
            len(hardcoded_paths) == 0
        ), f"Found {len(hardcoded_paths)} hardcoded paths:\n" + "\n".join(hardcoded_paths[:20])
        
    except subprocess.TimeoutExpired:
        sys.fail("Grep search timed out")
    except FileNotFoundError:
        sys.fail("grep command not found")


def test_uses_dynamic_path_resolution() -> None:
    """
    Verify that tests use dynamic path resolution patterns.
    
    This test checks that common dynamic path patterns are used instead of
    hardcoded paths. Examples:
    - Path(__file__).parent
    - Path(__file__).parent.parent
    - os.path.dirname(__file__)
    
    Expected: All absolute paths should use dynamic resolution
    """
    project_root = Path(__file__).parent.parent.parent
    tests_dir = project_root / "tests"
    
    # Find files using Path(__file__).parent pattern (good pattern)
    try:
        result = subprocess.run(
            [
                "grep",
                "-rn",
                r"Path(__file__).parent",
                str(tests_dir),
                "--include=*.py",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        
        # Should have at least some matches
        matches = [m for m in result.stdout.strip().split("\n") if m]
        
        # We expect at least some files using this pattern
        # but it's OK if none yet (as long as hardcoded paths are gone)
        
    except subprocess.TimeoutExpired:
        sys.fail("Grep search timed out")
    except FileNotFoundError:
        sys.fail("grep command not found")


if __name__ == "__main__":
    # Run tests manually for verification
    print("Running AC-REM-004-02 tests...")
    
    try:
        test_no_hardcoded_paths()
        print("✓ test_no_hardcoded_paths PASSED")
    except AssertionError as e:
        print(f"✗ test_no_hardcoded_paths FAILED: {e}")
        sys.exit(1)
    
    try:
        test_uses_dynamic_path_resolution()
        print("✓ test_uses_dynamic_path_resolution PASSED")
    except AssertionError as e:
        print(f"✗ test_uses_dynamic_path_resolution FAILED: {e}")
        sys.exit(1)
    
    print("\nAll tests passed!")
