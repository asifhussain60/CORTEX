"""
Glassmorphism Pre-Commit Hook
Prevents commits with glassmorphism design standard violations.

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
Version: 1.0.0

Installation:
    Copy this file to .git/hooks/pre-commit and make it executable:
    
    PowerShell:
    Copy-Item src/validation/glassmorphism_pre_commit_hook.py .git/hooks/pre-commit
    
    Linux/Mac:
    cp src/validation/glassmorphism_pre_commit_hook.py .git/hooks/pre-commit
    chmod +x .git/hooks/pre-commit
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.validation.glassmorphism_validator import GlassmorphismValidator, ValidationSeverity


def main():
    """Pre-commit hook entry point."""
    docs_root = project_root / "docs"
    
    if not docs_root.exists():
        print("⚠️ Warning: docs/ directory not found. Skipping glassmorphism validation.")
        return 0
    
    print("🎨 Running glassmorphism design standard validation...")
    print()
    
    # Run validator
    validator = GlassmorphismValidator(docs_root)
    report = validator.validate_all()
    
    # Check for blocking issues
    blocking_issues = [
        issue for issue in report.issues
        if issue.severity in [ValidationSeverity.CRITICAL, ValidationSeverity.ERROR]
    ]
    
    if blocking_issues:
        print("❌ COMMIT BLOCKED: Glassmorphism design standard violations detected")
        print()
        print(f"   CRITICAL: {report.critical_count}")
        print(f"   ERROR: {report.error_count}")
        print(f"   WARNING: {report.warning_count}")
        print()
        print("📋 Top 10 Issues:")
        print()
        
        for issue in blocking_issues[:10]:
            line_ref = f" (line {issue.line_number})" if issue.line_number else ""
            print(f"   {issue.severity.value}: {issue.file_path.name}{line_ref}")
            print(f"      {issue.message}")
            if issue.fix_suggestion:
                print(f"      Fix: {issue.fix_suggestion}")
            print()
        
        if len(blocking_issues) > 10:
            print(f"   ... and {len(blocking_issues) - 10} more issues")
            print()
        
        print("🛠️ To fix issues, run:")
        print()
        print("   python src/validation/glassmorphism_validator.py --report-file validation-report.md")
        print("   python src/validation/glassmorphism_remediation.py --all")
        print()
        print("💡 Or bypass this check (NOT RECOMMENDED):")
        print()
        print("   git commit --no-verify")
        print()
        
        return 1
    
    elif report.warning_count > 0:
        print("⚠️ COMMIT ALLOWED: Warnings detected but not blocking")
        print()
        print(f"   WARNING: {report.warning_count}")
        print()
        print("Consider fixing warnings before pushing to production.")
        print()
        return 0
    
    else:
        print("✅ All glassmorphism design standard checks passed")
        print()
        return 0


if __name__ == "__main__":
    sys.exit(main())
