"""
Run All Validation Scripts

Executes all documentation validation scripts and provides summary.

Usage:
    python scripts/run_validation_suite.py

Author: Asif Hussain
"""

import subprocess
import sys
from pathlib import Path

CORTEX_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = [
    "scripts/validate_docs_links.py",
    "scripts/detect_duplicates.py",
    "scripts/validate_module_guides.py"
]


def run_script(script_path: str) -> tuple:
    """Run a validation script and return result."""
    full_path = CORTEX_ROOT / script_path
    
    try:
        result = subprocess.run(
            [sys.executable, str(full_path)],
            capture_output=True,
            text=True,
            cwd=CORTEX_ROOT
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)


def main():
    """Run all validation scripts."""
    print("=" * 80)
    print("CORTEX VALIDATION SUITE")
    print("=" * 80)
    print()
    
    results = []
    
    for script in SCRIPTS:
        script_name = Path(script).stem.replace('_', ' ').title()
        print(f"Running: {script_name}")
        print("-" * 80)
        
        returncode, stdout, stderr = run_script(script)
        results.append((script_name, returncode))
        
        print(stdout)
        if stderr:
            print(f"Errors:\n{stderr}")
        
        print()
    
    print("=" * 80)
    print("VALIDATION SUITE SUMMARY")
    print("=" * 80)
    
    all_passed = True
    for script_name, returncode in results:
        status = "[PASS]" if returncode == 0 else "[FAIL]"
        print(f"{status} - {script_name}")
        if returncode != 0:
            all_passed = False
    
    print()
    
    if all_passed:
        print("[SUCCESS] ALL VALIDATIONS PASSED")
        return 0
    else:
        print("[!] SOME VALIDATIONS FAILED")
        print("   Fix issues before proceeding")
        return 1


if __name__ == "__main__":
    exit(main())
