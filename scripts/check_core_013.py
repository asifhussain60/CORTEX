#!/usr/bin/env python3
"""
CORE-013 Compliance Checker
Verifies no bare except blocks exist in production code.

AC-ID: AC-CORE-013-CHECKER-001
Authority: CORE-013 (No bare except)
"""

import subprocess
import sys
from pathlib import Path


def check_bare_except() -> tuple[int, list[str]]:
    """
    Check for bare except blocks in production code.
    
    Returns:
        Tuple of (violation_count, list_of_violations)
    """
    try:
        result = subprocess.run(
            ['grep', '-rn', r'except:\s*$', 'cortex/', 'scripts/', '--include=*.py'],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        
        # Filter out test files
        violations = []
        for line in result.stdout.splitlines():
            if 'tests/' not in line and '# bare except:' not in line:
                violations.append(line)
        
        return len(violations), violations
        
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"❌ Error running grep: {e}")
        return -1, []


def main() -> int:
    """Main entry point."""
    print("🔍 CORE-013 Compliance Check: Scanning for bare except blocks...")
    print("=" * 70)
    
    count, violations = check_bare_except()
    
    if count == -1:
        print("❌ Check failed - could not run grep")
        return 1
    
    if count == 0:
        print("✅ PASSED - No bare except blocks found in production code")
        print("\nCORE-013 Status: COMPLIANT")
        return 0
    
    print(f"❌ FAILED - Found {count} bare except block(s):\n")
    for violation in violations:
        print(f"  {violation}")
    
    print("\n" + "=" * 70)
    print("CORE-013 Requirement: All except blocks must specify exception types")
    print("\nExample Fix:")
    print("  BAD:  except:")
    print("  GOOD: except (ValueError, KeyError, TypeError) as e:")
    
    return 1


if __name__ == "__main__":
    sys.exit(main())
