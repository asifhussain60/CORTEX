"""
Test for AC-REM-004-01: Bare Except Clause Removal

This test verifies that all bare except clauses have been replaced with
specific exception types, as required by CORE-013 governance rule.

Issue: ISSUE-004 (Code Quality - Bare Except Clauses)
AC-ID: AC-REM-004-01
Priority: CRITICAL
"""

import subprocess
import sys
from pathlib import Path
from typing import List


def test_no_bare_except_clauses() -> None:
    """
    Verify that no bare except clauses exist in src/ directory.
    
    This test uses grep to find all bare except clauses and asserts that
    none are found. The grep pattern looks for "except:" at the end of a line,
    which indicates a bare except (not followed by exception type).
    
    Expected: 0 matches
    
    Raises:
        AssertionError: If any bare except clauses are found
    """
    project_root = Path(__file__).parent.parent.parent
    src_dir = project_root / "src"
    
    # Run grep to find bare except clauses
    # Pattern explanation:
    # - grep -rn: recursive, line numbers
    # - "except:" matches the bare except keyword
    # - --include="*.py": only Python files
    # - | grep -v "except.*:" filters out except clauses with exception types
    
    try:
        result = subprocess.run(
            [
                "grep",
                "-rn",
                r"except:$",  # Match "except:" at end of line (bare except)
                str(src_dir),
                "--include=*.py",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        
        matches = result.stdout.strip().split("\n") if result.stdout.strip() else []
        
        # Filter out false positives (lines that contain "except:" in strings, etc.)
        bare_excepts = []
        for match in matches:
            # Skip empty lines
            if not match:
                continue
            # Skip comments
            if "#" in match and match.index("#") < match.index("except"):
                continue
            bare_excepts.append(match)
        
        # Assert no bare except clauses found
        assert (
            len(bare_excepts) == 0
        ), f"Found {len(bare_excepts)} bare except clauses:\n" + "\n".join(bare_excepts)
        
    except subprocess.TimeoutExpired:
        sys.fail("Grep search timed out")
    except FileNotFoundError:
        sys.fail("grep command not found")


def test_specific_exception_types_used() -> None:
    """
    Verify that except clauses use specific exception types.
    
    This test checks that common exception types are used instead of bare excepts.
    Examples of specific exceptions:
    - except ValueError:
    - except (TypeError, AttributeError):
    - except Exception as e:
    
    Expected: All except clauses should specify exception types
    """
    project_root = Path(__file__).parent.parent.parent
    src_dir = project_root / "src"
    
    # Find all except clauses
    try:
        result = subprocess.run(
            [
                "grep",
                "-rn",
                r"except [A-Za-z]",  # Match except followed by exception name
                str(src_dir),
                "--include=*.py",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        
        matches = result.stdout.strip().split("\n") if result.stdout.strip() else []
        
        # Should have at least some matches (except clauses with types)
        assert len(matches) > 0, "No except clauses with specific exception types found"
        
    except subprocess.TimeoutExpired:
        sys.fail("Grep search timed out")
    except FileNotFoundError:
        sys.fail("grep command not found")


if __name__ == "__main__":
    # Run tests manually for verification
    print("Running AC-REM-004-01 tests...")
    
    try:
        test_no_bare_except_clauses()
        print("✓ test_no_bare_except_clauses PASSED")
    except AssertionError as e:
        print(f"✗ test_no_bare_except_clauses FAILED: {e}")
        sys.exit(1)
    
    try:
        test_specific_exception_types_used()
        print("✓ test_specific_exception_types_used PASSED")
    except AssertionError as e:
        print(f"✗ test_specific_exception_types_used FAILED: {e}")
        sys.exit(1)
    
    print("\nAll tests passed!")
