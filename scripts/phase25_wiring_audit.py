#!/usr/bin/env python
"""
Phase 25 S3: Wiring Contract Audit Script

Validates all 28+ wiring entries point to real importable classes.
AC-PHASE25-S3: Wiring validation
"""
# AC_START: AC-PHASE25-S3
# Description: Wiring contract audit for Phase 25

import sys
from pathlib import Path
from typing import List, Tuple

import yaml


def load_wiring() -> dict:
    """Load wiring.yaml from registry."""
    wiring_path = Path(__file__).parent.parent / "cortex-registry" / "_cortex-master" / "core" / "wiring" / "wiring.yaml"
    with open(wiring_path) as f:
        return yaml.safe_load(f)


def extract_orchestrator_entries(wiring: dict) -> List[Tuple[str, str, str]]:
    """Extract (name, module, class) tuples from wiring."""
    entries = []
    
    # Core orchestrators
    if "orchestrators" in wiring and "core" in wiring["orchestrators"]:
        for orch in wiring["orchestrators"]["core"]:
            entries.append((orch["name"], orch["module"], orch["class"]))
    
    # Domain orchestrators
    if "orchestrators" in wiring and "domain" in wiring["orchestrators"]:
        for orch in wiring["orchestrators"]["domain"]:
            entries.append((orch["name"], orch["module"], orch["class"]))
    
    # Support orchestrators
    if "orchestrators" in wiring and "support" in wiring["orchestrators"]:
        for orch in wiring["orchestrators"]["support"]:
            entries.append((orch["name"], orch["module"], orch["class"]))
    
    # Analyzers
    if "analyzers" in wiring:
        for analyzer in wiring["analyzers"]:
            entries.append((analyzer["name"], analyzer["module"], analyzer["class"]))
    
    return entries


def validate_import(name: str, module: str, class_name: str) -> Tuple[bool, str]:
    """
    Validate that a class can be imported.
    
    Returns:
        (success, error_message)
    """
    try:
        mod = __import__(module, fromlist=[class_name])
        if not hasattr(mod, class_name):
            return False, f"Module {module} has no attribute '{class_name}'"
        return True, ""
    except ImportError as e:
        return False, f"ImportError: {e}"
    except Exception as e:
        return False, f"Unexpected error: {e}"


def main() -> int:
    """Run wiring audit."""
    print("🔍 Phase 25 S3: Wiring Contract Audit\n")
    
    # Load wiring
    wiring = load_wiring()
    entries = extract_orchestrator_entries(wiring)
    
    print(f"Found {len(entries)} wiring entries to validate\n")
    
    # Validate each entry
    passed = 0
    failed = 0
    failures = []
    
    for name, module, class_name in entries:
        success, error = validate_import(name, module, class_name)
        if success:
            passed += 1
            print(f"✅ {name}: {module}.{class_name}")
        else:
            failed += 1
            failures.append((name, module, class_name, error))
            print(f"❌ {name}: {module}.{class_name}")
            print(f"   Error: {error}")
    
    # Summary
    print(f"\n{'='*60}")
    print(f"Total: {len(entries)} | Passed: {passed} | Failed: {failed}")
    print(f"{'='*60}\n")
    
    if failed > 0:
        print("❌ WIRING AUDIT FAILED")
        print("\nFailures:")
        for name, module, class_name, error in failures:
            print(f"  • {name} ({module}.{class_name}): {error}")
        return 1
    else:
        print("✅ WIRING AUDIT PASSED - All entries importable")
        return 0


if __name__ == "__main__":
    sys.exit(main())

# AC_COMPLETE: AC-PHASE25-S3 ✅ Wiring audit script implemented
