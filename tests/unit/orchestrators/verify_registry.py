"""
CORTEX Registry Verification Script

AC-ID: AC-PERMANENT-FIX-002
Purpose: Verify registry template lock and orchestrator wiring status.

This script ensures AC-PERMANENT-FIX-001 (Orchestrator Registry Unwiring Fix)
remains active and has not regressed.

Entry Point: tests.unit.orchestrators.verify_registry
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Tuple, Dict, Any, Optional

import yaml


def verify_registry_template_locked(registry_path: Optional[Path] = None) -> Tuple[bool, str]:
    """
    Verify that registry_template is set to false (locked).
    
    AC-PERMANENT-FIX-001 requires registry_template: false to prevent
    automatic regeneration that wipes orchestrator wiring.
    
    Args:
        registry_path: Path to repo-registry.yaml. Defaults to standard location.
        
    Returns:
        Tuple[bool, str]: (is_valid, message)
    """
    if registry_path is None:
        registry_path = Path(__file__).parents[3] / "cortex_brain" / "tier0" / "repo-registry.yaml"
    
    if not registry_path.exists():
        return False, f"Registry file not found: {registry_path}"
    
    try:
        content = registry_path.read_text(encoding="utf-8")
        registry = yaml.safe_load(content)
        
        registry_template = registry.get("registry_template", True)
        
        if registry_template is False:
            return True, "registry_template is locked (false)"
        else:
            return False, f"registry_template is NOT locked (value: {registry_template})"
            
    except Exception as e:
        return False, f"Failed to parse registry: {e}"


def verify_orchestrator_wiring(registry_path: Path | None = None, min_wired: int = 18) -> Tuple[bool, str]:
    """
    Verify that minimum number of orchestrators are wired.
    
    Args:
        registry_path: Path to repo-registry.yaml. Defaults to standard location.
        min_wired: Minimum number of wired orchestrators required.
        
    Returns:
        Tuple[bool, str]: (is_valid, message)
    """
    if registry_path is None:
        registry_path = Path(__file__).parents[3] / "cortex_brain" / "tier0" / "repo-registry.yaml"
    
    if not registry_path.exists():
        return False, f"Registry file not found: {registry_path}"
    
    try:
        content = registry_path.read_text(encoding="utf-8")
        registry = yaml.safe_load(content)
        
        orchestrators = registry.get("registered_orchestrators", [])
        wired_count = sum(
            1 for o in orchestrators 
            if o.get("wiring_status") == "wired"
        )
        
        if wired_count >= min_wired:
            return True, f"{wired_count} orchestrators wired (minimum: {min_wired})"
        else:
            return False, f"Only {wired_count} orchestrators wired (need {min_wired}+)"
            
    except Exception as e:
        return False, f"Failed to parse registry: {e}"


def verify_wiring_status_section(registry_path: Path | None = None) -> Tuple[bool, str]:
    """
    Verify the wiring_status section reports correct totals.
    
    Args:
        registry_path: Path to repo-registry.yaml. Defaults to standard location.
        
    Returns:
        Tuple[bool, str]: (is_valid, message)
    """
    if registry_path is None:
        registry_path = Path(__file__).parents[3] / "cortex_brain" / "tier0" / "repo-registry.yaml"
    
    if not registry_path.exists():
        return False, f"Registry file not found: {registry_path}"
    
    try:
        content = registry_path.read_text(encoding="utf-8")
        registry = yaml.safe_load(content)
        
        wiring_status = registry.get("wiring_status", {})
        total = wiring_status.get("total_orchestrators", 0)
        wired = wiring_status.get("wired", 0)
        coverage = wiring_status.get("coverage_percentage", 0)
        
        if total >= 20 and wired >= 18 and coverage >= 80:
            return True, f"Wiring status valid: {wired}/{total} ({coverage}%)"
        else:
            return False, f"Wiring status insufficient: {wired}/{total} ({coverage}%)"
            
    except Exception as e:
        return False, f"Failed to parse registry: {e}"


def verify_all() -> Dict[str, Dict[str, Any]]:
    """
    Run all registry verifications.
    
    Returns:
        Dict with verification results for each check.
    """
    results = {}
    
    # Check 1: Registry template locked
    is_valid, message = verify_registry_template_locked()
    results["registry_template_locked"] = {
        "valid": is_valid,
        "message": message,
        "critical": True,
    }
    
    # Check 2: Orchestrator wiring
    is_valid, message = verify_orchestrator_wiring()
    results["orchestrator_wiring"] = {
        "valid": is_valid,
        "message": message,
        "critical": True,
    }
    
    # Check 3: Wiring status section
    is_valid, message = verify_wiring_status_section()
    results["wiring_status_section"] = {
        "valid": is_valid,
        "message": message,
        "critical": False,
    }
    
    return results


def main() -> int:
    """
    Main entry point for CLI usage.
    
    Returns:
        0 if all critical checks pass, 1 otherwise.
    """
    print("=" * 60)
    print("CORTEX Registry Verification (AC-PERMANENT-FIX-002)")
    print("=" * 60)
    
    results = verify_all()
    
    all_critical_passed = True
    
    for check_name, result in results.items():
        status = "PASS" if result["valid"] else "FAIL"
        critical_marker = " [CRITICAL]" if result["critical"] else ""
        
        print(f"\n{status}: {check_name}{critical_marker}")
        print(f"  {result['message']}")
        
        if result["critical"] and not result["valid"]:
            all_critical_passed = False
    
    print("\n" + "=" * 60)
    
    if all_critical_passed:
        print("RESULT: All critical checks PASSED")
        return 0
    else:
        print("RESULT: Critical checks FAILED - AC-PERMANENT-FIX-001 may be regressed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
