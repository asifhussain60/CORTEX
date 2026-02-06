"""Generate CORE-028 naming migration inventory.

Scans workspace and creates prioritized inventory of files needing rename.
Excludes special Python files (__init__.py, __main__.py, etc.)

Phase 7.4, Task NAMING-003
AC-ID: NAMING-003
"""

from pathlib import Path
from typing import List, Dict, Set
import yaml

from cortex.tools.naming_violation_detector import (
    NamingViolationDetector,
    ViolationType,
)


# Special files to exclude (Python conventions)
SPECIAL_FILES = {
    "__init__.py",
    "__main__.py",
    "__version__.py",
    "__about__.py",
}


def prioritize_violations(violations: List) -> Dict[str, List[Dict]]:
    """Prioritize violations by type and impact.
    
    P0 - Critical: Public API files, orchestrators
    P1 - High: Core brain files, tools
    P2 - Medium: Tests, utilities
    
    Args:
        violations: List of Violation objects
        
    Returns:
        Dictionary with P0, P1, P2 keys containing violation dicts
    """
    prioritized = {"P0": [], "P1": [], "P2": []}
    
    for v in violations:
        # Skip special Python files
        if v.file_path.name in SPECIAL_FILES:
            continue
        
        file_str = str(v.file_path)
        
        # Determine priority based on path
        if "orchestrators/" in file_str or "api/" in file_str:
            priority = "P0"  # Critical: Public APIs
        elif "brain/" in file_str or "tools/" in file_str or "core/" in file_str:
            priority = "P1"  # High: Core functionality
        elif "tests/" in file_str or "scripts/" in file_str:
            priority = "P2"  # Medium: Tests and utilities
        else:
            priority = "P2"  # Default to medium
        
        violation_dict = {
            "file": str(v.file_path.relative_to(Path.cwd())),
            "type": v.type.value,
            "current_name": v.current_name,
            "suggested_name": v.suggested_fix,
            "reason": v.reason,
        }
        
        prioritized[priority].append(violation_dict)
    
    return prioritized


def main():
    """Generate naming migration inventory."""
    print("Scanning workspace for CORE-028 violations...")
    
    detector = NamingViolationDetector(workspace_root=Path.cwd())
    all_violations = detector.scan_workspace()
    
    # Filter out special files
    filtered = [v for v in all_violations if v.file_path.name not in SPECIAL_FILES]
    
    print(f"Found {len(all_violations)} total violations")
    print(f"After filtering special files: {len(filtered)} violations")
    
    # Prioritize violations
    prioritized = prioritize_violations(filtered)
    
    print(f"\nPriority Breakdown:")
    print(f"  P0 (Critical): {len(prioritized['P0'])} files")
    print(f"  P1 (High): {len(prioritized['P1'])} files")
    print(f"  P2 (Medium): {len(prioritized['P2'])} files")
    
    # Create inventory YAML
    inventory = {
        "# CORE-028 File Naming Migration Inventory": None,
        "generated": "2026-01-27",
        "total_violations": len(filtered),
        "summary": {
            "P0_critical": len(prioritized["P0"]),
            "P1_high": len(prioritized["P1"]),
            "P2_medium": len(prioritized["P2"]),
        },
        "priorities": prioritized,
    }
    
    # Write to file
    output_path = Path("cortex-registry/_cortex-master/meta/naming-migration-inventory.yaml")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w") as f:
        yaml.dump(inventory, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print(f"\n✅ Inventory created: {output_path}")
    print(f"\nTop 10 P0 (Critical) files to rename:")
    for i, item in enumerate(prioritized["P0"][:10], 1):
        print(f"  {i}. {item['file']}")
        print(f"     → {item['suggested_name']}")


if __name__ == "__main__":
    main()
