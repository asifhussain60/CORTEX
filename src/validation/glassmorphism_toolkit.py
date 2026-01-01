"""
Glassmorphism Toolkit Wrapper
Unified interface for all glassmorphism validation and remediation tools.

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
Version: 1.0.0
"""

import sys
import argparse
from pathlib import Path
from typing import Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.validation.glassmorphism_validator import GlassmorphismValidator
from src.validation.glassmorphism_remediation import GlassmorphismRemediator


class GlassmorphismToolkit:
    """
    Unified toolkit for glassmorphism design standard enforcement.
    
    Capabilities:
    - Validate HTML against glassmorphism-design-standard.md v4.0.0
    - Automatically fix common violations
    - Generate validation and remediation reports
    - Enforce SKULL rules for UI consistency
    """
    
    def __init__(self, docs_root: Path = Path("docs")):
        """
        Initialize toolkit.
        
        Args:
            docs_root: Path to docs/ directory
        """
        self.docs_root = docs_root
    
    def validate(
        self,
        report_file: Optional[Path] = None,
        fail_on_warnings: bool = False
    ) -> int:
        """
        Run validation against all HTML files.
        
        Args:
            report_file: Output report path (markdown)
            fail_on_warnings: Exit with error if warnings present
        
        Returns:
            Exit code (0=success, 1=errors, 2=warnings with fail_on_warnings)
        """
        print("🎨 Glassmorphism Design Standard Validator v1.0.0")
        print(f"📁 Scanning: {self.docs_root}")
        print()
        
        validator = GlassmorphismValidator(self.docs_root)
        report = validator.validate_all()
        
        # Generate report
        markdown_report = validator.generate_report_markdown()
        
        # Output
        if report_file:
            report_file.write_text(markdown_report, encoding="utf-8")
            print(f"✅ Report written to: {report_file}")
            print()
        else:
            print(markdown_report)
        
        # Summary
        print("=" * 80)
        print(f"📊 SUMMARY: {report.total_files_scanned} files scanned")
        print(f"   ✅ Passed: {report.passed_files}")
        print(f"   ❌ Failed: {report.failed_files}")
        print()
        print(f"   🔴 CRITICAL: {report.critical_count}")
        print(f"   🟠 ERROR: {report.error_count}")
        print(f"   🟡 WARNING: {report.warning_count}")
        print()
        
        if report.is_valid:
            if report.warning_count > 0:
                print("⚠️ VALIDATION PASSED (with warnings)")
                return 2 if fail_on_warnings else 0
            else:
                print("✅ VALIDATION PASSED")
                return 0
        else:
            print("❌ VALIDATION FAILED")
            print()
            print("🛠️ To fix issues, run:")
            print()
            print("   python src/validation/glassmorphism_toolkit.py remediate --all")
            print()
            return 1
    
    def remediate(
        self,
        fix_inline_styles: bool = False,
        add_headers: bool = False,
        add_footers: bool = False,
        remove_t3_animations: bool = False,
        rename_files: bool = False,
        all_fixes: bool = False,
        backup_dir: Optional[Path] = None,
        report_file: Optional[Path] = None
    ) -> int:
        """
        Automatically fix glassmorphism violations.
        
        Args:
            fix_inline_styles: Remove inline style attributes
            add_headers: Add missing glass headers
            add_footers: Add missing glass footers
            remove_t3_animations: Remove T3 dramatic animations
            rename_files: Rename files with forbidden patterns
            all_fixes: Apply all fixes
            backup_dir: Backup directory path
            report_file: Output report path
        
        Returns:
            Exit code (0=success, 1=failures)
        """
        print("🛠️ Glassmorphism Remediation Engine v1.0.0")
        print(f"📁 Target: {self.docs_root}")
        print()
        
        remediator = GlassmorphismRemediator(self.docs_root, backup_dir)
        
        print(f"📦 Backups will be saved to: {remediator.backup_dir}")
        print()
        
        # Collect HTML files
        html_files = list(self.docs_root.rglob("*.html"))
        print(f"🔍 Found {len(html_files)} HTML files")
        print()
        
        # Apply fixes
        if all_fixes or fix_inline_styles:
            print("🧹 Removing inline styles...")
            for file_path in html_files:
                action = remediator.extract_inline_styles(file_path)
                remediator.actions.append(action)
        
        if all_fixes or add_headers:
            print("📝 Adding missing headers...")
            for file_path in html_files:
                action = remediator.add_missing_header(file_path)
                remediator.actions.append(action)
        
        if all_fixes or add_footers:
            print("📝 Adding missing footers...")
            for file_path in html_files:
                action = remediator.add_missing_footer(file_path)
                remediator.actions.append(action)
        
        if all_fixes or remove_t3_animations:
            print("🎬 Removing T3 animations...")
            for file_path in html_files:
                action = remediator.remove_t3_animations(file_path)
                remediator.actions.append(action)
        
        if all_fixes or rename_files:
            print("📝 Renaming files with forbidden patterns...")
            for file_path in html_files:
                action = remediator.rename_forbidden_file(file_path)
                remediator.actions.append(action)
        
        # Generate report
        report = remediator.generate_report()
        
        if report_file:
            report_file.write_text(report, encoding="utf-8")
            print(f"\n✅ Report written to: {report_file}")
        else:
            print(report)
        
        # Summary
        successful = sum(1 for a in remediator.actions if a.success)
        failed = sum(1 for a in remediator.actions if not a.success)
        
        print()
        print("=" * 80)
        print(f"📊 SUMMARY: {len(remediator.actions)} actions performed")
        print(f"   ✅ Successful: {successful}")
        print(f"   ❌ Failed: {failed}")
        print()
        
        if failed > 0:
            print("⚠️ Some fixes failed. Review report for details.")
            return 1
        else:
            print("✅ All fixes applied successfully")
            print()
            print("🔍 Next steps:")
            print("   1. Review changes in browser")
            print("   2. Run validation: python src/validation/glassmorphism_toolkit.py validate")
            print("   3. Commit if all tests pass")
            print()
            return 0
    
    def install_hook(self) -> int:
        """
        Install pre-commit hook.
        
        Returns:
            Exit code (0=success, 1=failure)
        """
        print("🪝 Installing Glassmorphism Pre-Commit Hook")
        print()
        
        hook_source = project_root / "src" / "validation" / "glassmorphism_pre_commit_hook.py"
        hook_dest = project_root / ".git" / "hooks" / "pre-commit"
        
        if not hook_source.exists():
            print(f"❌ Hook source not found: {hook_source}")
            return 1
        
        if not (project_root / ".git").exists():
            print("❌ Not a git repository")
            return 1
        
        # Create hooks directory if not exists
        hook_dest.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy hook
        import shutil
        shutil.copy2(hook_source, hook_dest)
        
        # Make executable (Unix-like systems)
        if sys.platform != "win32":
            import os
            os.chmod(hook_dest, 0o755)
        
        print(f"✅ Hook installed: {hook_dest}")
        print()
        print("🎯 Hook will now run before every commit to enforce:")
        print("   - NO_INLINE_STYLES")
        print("   - NO_LEVEL_3")
        print("   - HEADER_FOOTER_STANDARD")
        print("   - T1_ANIMATIONS_ONLY")
        print("   - PRODUCTION_FILE_NAMING")
        print()
        print("💡 To bypass hook (not recommended):")
        print("   git commit --no-verify")
        print()
        
        return 0


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Glassmorphism Design Standard Toolkit",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate all HTML files
  python src/validation/glassmorphism_toolkit.py validate
  
  # Validate with report output
  python src/validation/glassmorphism_toolkit.py validate --report-file validation-report.md
  
  # Fix all violations
  python src/validation/glassmorphism_toolkit.py remediate --all
  
  # Fix specific issues
  python src/validation/glassmorphism_toolkit.py remediate --fix-inline-styles --add-headers
  
  # Install pre-commit hook
  python src/validation/glassmorphism_toolkit.py install-hook
        """
    )
    
    parser.add_argument(
        "command",
        choices=["validate", "remediate", "install-hook"],
        help="Command to execute"
    )
    parser.add_argument(
        "--docs-root",
        type=Path,
        default=Path("docs"),
        help="Path to docs/ directory (default: docs)"
    )
    parser.add_argument(
        "--report-file",
        type=Path,
        help="Output report to file (markdown)"
    )
    
    # Validation options
    parser.add_argument(
        "--fail-on-warnings",
        action="store_true",
        help="Exit with error code if warnings present"
    )
    
    # Remediation options
    parser.add_argument(
        "--fix-inline-styles",
        action="store_true",
        help="Remove inline style attributes"
    )
    parser.add_argument(
        "--add-headers",
        action="store_true",
        help="Add missing glass headers"
    )
    parser.add_argument(
        "--add-footers",
        action="store_true",
        help="Add missing glass footers"
    )
    parser.add_argument(
        "--remove-t3-animations",
        action="store_true",
        help="Remove T3 dramatic animations"
    )
    parser.add_argument(
        "--rename-files",
        action="store_true",
        help="Rename files with forbidden patterns"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        dest="all_fixes",
        help="Apply all fixes"
    )
    parser.add_argument(
        "--backup-dir",
        type=Path,
        help="Backup directory path"
    )
    
    args = parser.parse_args()
    
    # Initialize toolkit
    toolkit = GlassmorphismToolkit(args.docs_root)
    
    # Execute command
    if args.command == "validate":
        exit_code = toolkit.validate(
            report_file=args.report_file,
            fail_on_warnings=args.fail_on_warnings
        )
    elif args.command == "remediate":
        exit_code = toolkit.remediate(
            fix_inline_styles=args.fix_inline_styles,
            add_headers=args.add_headers,
            add_footers=args.add_footers,
            remove_t3_animations=args.remove_t3_animations,
            rename_files=args.rename_files,
            all_fixes=args.all_fixes,
            backup_dir=args.backup_dir,
            report_file=args.report_file
        )
    elif args.command == "install-hook":
        exit_code = toolkit.install_hook()
    else:
        parser.print_help()
        exit_code = 1
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
