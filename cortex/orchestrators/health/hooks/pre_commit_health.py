"""Pre-commit Hook - Health Check Enforcement

Blocks commits that violate health policies:
- Versioned filenames (*_v*, *-v*)
- Backup files (*.backup, *.old)
- Config files outside registry
- Database files in root

Author: CORTEX Framework
Phase: PHASE-95 S4
CORE Rules: CORE-008 (TDD), CORE-028 (file naming)
"""

import sys
from pathlib import Path
from typing import List, Tuple

from cortex.orchestrators.health.agents.version_cleanup_agent import VersionCleanupAgent
from cortex.orchestrators.health.agents.registry_consistency_agent import RegistryConsistencyAgent


def check_staged_files() -> Tuple[bool, List[str]]:
    """Check staged files for violations.
    
    Returns:
        Tuple of (passed, violations)
    """
    import subprocess
    
    # Get staged files
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True,
        text=True,
    )
    
    if result.returncode != 0:
        return False, ["Failed to get staged files"]
    
    staged_files = [Path(f) for f in result.stdout.strip().split("\n") if f]
    
    violations = []
    
    # Check versioned filenames (CORE-028)
    for file_path in staged_files:
        if "_v" in file_path.stem or "-v" in file_path.stem:
            violations.append(f"❌ CORE-028: Versioned filename: {file_path}")
        
        if file_path.suffix in [".backup", ".old"]:
            violations.append(f"❌ CORE-028: Backup file: {file_path}")
    
    # Check config outside registry
    for file_path in staged_files:
        if file_path.suffix in [".yaml", ".yml"]:
            if not str(file_path).startswith("cortex-registry/"):
                if not str(file_path).startswith(".github/"):
                    violations.append(f"⚠️  Config outside registry: {file_path}")
    
    # Check database files in root
    for file_path in staged_files:
        if file_path.suffix == ".db":
            if file_path.parent == Path("."):
                violations.append(f"❌ Database in root: {file_path} (move to cortex_intelligence/)")
    
    return len(violations) == 0, violations


def main() -> int:
    """Run pre-commit health checks.
    
    Returns:
        Exit code (0 = pass, 1 = fail)
    """
    print("🔍 CORTEX Pre-Commit Health Check...")
    
    passed, violations = check_staged_files()
    
    if not passed:
        print("\n❌ COMMIT BLOCKED - Health violations detected:\n")
        for violation in violations:
            print(f"  {violation}")
        print("\nFix violations before committing.")
        return 1
    
    print("✅ Pre-commit health check passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
