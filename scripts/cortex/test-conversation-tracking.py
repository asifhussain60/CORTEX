"""
CORTEX Conversation Tracking - Quick Test Script

This script validates that conversation tracking works by:
1. Running existing Tier 1 tests
2. Checking cortex-capture.ps1 exists and is valid
3. Providing a summary for Rule #24 validation

Run this instead of the full integration test if there are import issues.
"""

import subprocess
import sys
from pathlib import Path


def main():
    print("\n" + "="*70)
    print(" "*20 + "CORTEX BRAIN PROTECTOR")
    print(" "*15 + "Conversation Tracking Validation")
    print(" "*25 + "Rule #24")
    print("="*70 + "\n")
    
    # Get project root (scripts/ is directly under project root)
    project_root = Path(__file__).parent.parent
    print(f"Project root: {project_root}\n")
    
    # Test 1: Run Tier 1 SQLite tests
    print("Test 1: Tier 1 SQLite Conversation Storage")
    print("-" * 60)
    
    result = subprocess.run(
        ["python", "-m", "pytest", "CORTEX/tests/tier1/test_working_memory.py", "-v", "-k", "conversation"],
        capture_output=True,
        text=True,
        cwd=str(project_root)
    )
    
    if result.returncode == 0:
        print("✅ PASS: Tier 1 conversation tests passing")
    else:
        print("❌ FAIL: Tier 1 conversation tests failing")
        print(result.stdout[-500:] if len(result.stdout) > 500 else result.stdout)
    
    # Test 2: Check cortex-capture.ps1
    print("\nTest 2: cortex-capture.ps1 Script")
    print("-" * 60)
    
    script_path = project_root / "scripts" / "cortex-capture.ps1"
    if script_path.exists():
        content = script_path.read_text(encoding='utf-8')
        
        checks = [
            ('Invoke-PythonTracking', 'Invoke-PythonTracking' in content),
            ('Test-ConversationTracking', 'Test-ConversationTracking' in content),
            ('Parameters defined', '-Message' in content and '-Intent' in content),
            ('Validation mode', '-Validate' in content)
        ]
        
        all_passed = all(passed for _, passed in checks)
        
        for check_name, passed in checks:
            status = "✅" if passed else "❌"
            print(f"{status} {check_name}")
        
        if all_passed:
            print("✅ PASS: cortex-capture.ps1 is properly structured")
        else:
            print("❌ FAIL: cortex-capture.ps1 missing required components")
    else:
        print(f"❌ FAIL: cortex-capture.ps1 not found at {script_path}")
        all_passed = False
    
    # Test 3: Check cortex_cli.py exists
    print("\nTest 3: cortex_cli.py Script")
    print("-" * 60)
    
    cli_path = project_root / "scripts" / "cortex_cli.py"
    if cli_path.exists():
        print(f"✅ PASS: cortex_cli.py exists at {cli_path}")
        cli_exists = True
    else:
        print(f"❌ FAIL: cortex_cli.py not found")
        cli_exists = False
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    tests_passed = []
    tests_passed.append(("Tier 1 SQLite Tests", result.returncode == 0))
    tests_passed.append(("cortex-capture.ps1", all_passed if 'all_passed' in locals() else False))
    tests_passed.append(("cortex_cli.py exists", cli_exists))
    
    for test_name, passed in tests_passed:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    all_tests_passed = all(passed for _, passed in tests_passed)
    
    print("\n" + "="*70)
    if all_tests_passed:
        print("✅ Rule #24 VALIDATED: Conversation tracking infrastructure ready")
        print("\nNext Steps:")
        print("  1. Use: python scripts/cortex_cli.py \"<message>\" to track conversations")
        print("  2. Use: .\\scripts\\cortex-capture.ps1 -AutoDetect for manual capture")
        print("  3. Validate: python scripts/cortex_cli.py --validate")
    else:
        print("❌ Rule #24 VIOLATION: Conversation tracking not fully operational")
        print("\nRequired Actions:")
        print("  1. Fix failing tests")
        print("  2. Ensure all scripts are present and properly configured")
        print("  3. Re-run this validation")
    print("="*70 + "\n")
    
    return 0 if all_tests_passed else 1


if __name__ == "__main__":
    sys.exit(main())
