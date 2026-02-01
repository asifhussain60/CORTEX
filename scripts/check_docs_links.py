#!/usr/bin/env python3
"""
Pre-commit hook for DOC-013: Documentation Link Integrity.

Validates all documentation links using the CortexDocsOrchestrator's
3-tier link auditing system. Fails if any P0 (navigation) broken links found.

Author: Asif Hussain
Version: 1.0
Governance: DOC-013, DOC-014, DOC-015, DOC-016, DOC-017
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

if TYPE_CHECKING:
    pass


def main() -> int:
    """
    Run documentation link audit.
    
    Returns:
        0 if no P0 issues, 1 if P0 issues found
    """
    try:
        from cortex.orchestrators.internal.cortex_docs_orchestrator import (
            CortexDocsOrchestrator,
        )
        
        # Initialize orchestrator
        orchestrator = CortexDocsOrchestrator()
        
        # Run link audit
        result = orchestrator.execute(
            "audit_documentation_links",
            entry_point="docs/index.html",
            mode="full",
            skip_external=True,  # Skip slow external checks in pre-commit
            dry_run=True,
        )
        
        if result.is_err():
            print(f"❌ Link audit failed: {result.error}")
            return 1
        
        audit = result.value
        summary = audit.get("summary", {})
        
        # Check for P0 broken links (navigation links)
        p0_count = summary.get("broken_links_by_severity", {}).get("p0_navigation", 0)
        security_violations = summary.get("security_violations", 0)
        
        # Report results
        total_checked = summary.get("total_links_checked", 0)
        orphaned = summary.get("orphaned_files", 0)
        
        print(f"\n📊 Documentation Link Audit Results")
        print(f"   Total links checked: {total_checked}")
        print(f"   P0 broken (navigation): {p0_count}")
        print(f"   Security violations: {security_violations}")
        print(f"   Orphaned files: {orphaned}")
        
        # Fail conditions
        if security_violations > 0:
            print(f"\n❌ SECURITY: {security_violations} security violation(s) detected!")
            print("   Run 'python3 -c \"from cortex.orchestrators.internal.cortex_docs_orchestrator import CortexDocsOrchestrator; o=CortexDocsOrchestrator(); print(o.execute('audit_documentation_links'))\"' for details")
            return 1
        
        if p0_count > 0:
            print(f"\n❌ DOC-013 VIOLATION: {p0_count} P0 broken navigation link(s)")
            print("   P0 links are critical navigation paths that block user access.")
            print("   Run full audit for details and remediation suggestions.")
            return 1
        
        print("\n✅ DOC-013: All documentation links valid")
        return 0
        
    except ImportError as e:
        print(f"⚠️ Import error (skipping check): {e}")
        # Don't fail the commit if orchestrator not available
        return 0
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
