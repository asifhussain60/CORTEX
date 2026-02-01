#!/usr/bin/env python3
"""
CORTEX TDD Gate - Pre-commit hook to enforce Test-Driven Development
Blocks commits where implementation code exists without corresponding tests
Implements CORE-008: Tests BEFORE code
"""

import sys
import os
import re
from pathlib import Path

# Implementation patterns to check (files being committed)
IMPL_PATTERNS = [
    r'^cortex/orchestrators/.+\.py$',
    r'^cortex/mcp/tools/.+\.py$',
    r'^cortex/.*\.py$',
]

# Test patterns that correspond to implementations
TEST_PATTERNS = {
    r'^cortex/orchestrators/(.+)\.py$': r'^tests/unit/orchestrators/\1/test_*.py$',
    r'^cortex/mcp/tools/(.+)\.py$': r'^tests/unit/mcp/tools/test_\1\.py$',
    r'^cortex/(.+)\.py$': r'^tests/unit/\1/test_*.py$',
}

def get_staged_files():
    """Get list of staged files from git index"""
    import subprocess
    result = subprocess.run(
        ['git', 'diff', '--cached', '--name-only'],
        capture_output=True,
        text=True
    )
    return result.stdout.strip().split('\n') if result.stdout.strip() else []

def find_corresponding_test(impl_file):
    """Find if corresponding test file exists"""
    for impl_pattern, test_pattern in TEST_PATTERNS.items():
        match = re.match(impl_pattern, impl_file)
        if match:
            test_file = re.sub(impl_pattern, test_pattern, impl_file)
            test_dir = os.path.dirname(test_file).replace('test_', '')
            if Path(test_dir).exists() or Path(os.path.dirname(test_file)).exists():
                return True
    return False

def check_tdd_compliance(staged_files):
    """Check that implementations have corresponding tests"""
    violations = []
    
    for file in staged_files:
        if not file or file.startswith('.'):
            continue
            
        # Check if it's an implementation file
        for pattern in IMPL_PATTERNS:
            if re.match(pattern, file):
                # Skip __init__.py, stubs (<50 bytes)
                if '__init__.py' in file or '__pycache__' in file:
                    break
                    
                # Check if test exists
                if not find_corresponding_test(file):
                    violations.append({
                        'file': file,
                        'reason': 'No corresponding test file found',
                        'expected': f'tests/unit/{file.replace("cortex/", "").replace(".py", "/test_*.py")}',
                    })
    
    return violations

def main():
    """Main pre-commit hook"""
    staged_files = get_staged_files()
    
    if not staged_files:
        return 0
    
    violations = check_tdd_compliance(staged_files)
    
    if violations:
        print("❌ TDD GATE VIOLATION - Tests must precede implementation (CORE-008)")
        print("=" * 70)
        for v in violations:
            print(f"\n📄 {v['file']}")
            print(f"   ⚠️  {v['reason']}")
            print(f"   💡 Expected: {v['expected']}")
        print("\n" + "=" * 70)
        print("✅ FIX: Create test specifications BEFORE committing implementation")
        print("   1. Write tests in: tests/unit/{module}/test_{component}.py")
        print("   2. Include: happy path, error cases, boundary conditions")
        print("   3. Then: Write minimal implementation to pass tests")
        print("   4. Finally: Commit both test + implementation together")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
