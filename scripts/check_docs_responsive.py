#!/usr/bin/env python3
"""
Pre-commit hook for DOC-021: Documentation Responsive Design.

Validates all documentation pages have proper responsive design patterns.
Fails if critical issues found (missing viewport meta tag).

Author: Asif Hussain
Version: 1.0
Governance: DOC-021, DOC-022, DOC-023, DOC-024, DOC-025, DOC-026, DOC-027, DOC-028
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
    Run documentation responsive design audit.
    
    Returns:
        0 if no critical issues, 1 if critical issues found
    """
    try:
        from cortex.orchestrators.internal.cortex_docs_orchestrator import (
            CortexDocsOrchestrator,
        )
        
        # Initialize orchestrator
        orchestrator = CortexDocsOrchestrator()
        
        # Run responsive audit
        result = orchestrator.execute(
            "audit_responsive_design",
            entry_point="docs/index.html",
            mode="full",
        )
        
        if result.is_err():
            print(f"❌ Responsive audit failed: {result.error}")
            return 1
        
        audit = result.value
        summary = audit.get("summary", {})
        
        # Check for critical issues
        critical_count = summary.get("critical_issues", 0)
        pages_audited = summary.get("pages_audited", 0)
        pages_passed = summary.get("pages_passed", 0)
        pass_percentage = summary.get("pass_percentage", 0)
        
        # Report results
        print(f"\n📊 Documentation Responsive Design Audit Results")
        print(f"   Pages audited: {pages_audited}")
        print(f"   Pages passed: {pages_passed} ({pass_percentage}%)")
        print(f"   Critical issues: {critical_count}")
        
        # List pages missing viewport (critical)
        pages = audit.get("pages", [])
        missing_viewport = [p for p in pages if not p.get("has_viewport", True)]
        
        if missing_viewport:
            print(f"\n❌ CRITICAL: Pages missing viewport meta tag:")
            for page in missing_viewport:
                print(f"   - {page.get('path', 'unknown')}")
        
        # Fail only on critical issues (missing viewport)
        if critical_count > 0:
            print(f"\n❌ DOC-021 VIOLATION: {critical_count} critical responsive issue(s)")
            print("   All HTML pages MUST have a viewport meta tag for mobile rendering.")
            print("   Add: <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">")
            return 1
        
        # Warn on low pass rate but don't fail
        if pass_percentage < 50:
            print(f"\n⚠️ Warning: Only {pass_percentage}% of pages pass responsive checks")
            print("   Consider improving responsive design patterns.")
        
        print("\n✅ DOC-021: No critical responsive design issues")
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
