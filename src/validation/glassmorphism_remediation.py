"""
Glassmorphism Remediation Engine
Automatically fixes common glassmorphism design standard violations.

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
Version: 1.0.0
"""

import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import shutil
from datetime import datetime


@dataclass
class RemediationAction:
    """Single remediation action performed."""
    rule_id: str
    file_path: Path
    action: str
    before: Optional[str] = None
    after: Optional[str] = None
    success: bool = True
    error_message: Optional[str] = None


class GlassmorphismRemediator:
    """
    Automatically fixes common glassmorphism violations.
    
    Capabilities:
    1. Extract inline styles to CSS classes
    2. Add missing header/footer templates
    3. Remove T3 animations from Level 1/2 pages
    4. Rename files with forbidden patterns
    5. Create backups before modifications
    """
    
    GLASS_HEADER_TEMPLATE = """<header class="glass-header">
    <div class="header-content">
        <div class="header-brand">
            <i class="fas fa-brain"></i>
            <h1>CORTEX</h1>
        </div>
        <nav class="header-nav">
            <a href="../index.html" class="nav-link">Home</a>
            <a href="#" class="nav-link">Documentation</a>
        </nav>
    </div>
</header>"""
    
    GLASS_FOOTER_TEMPLATE = """<footer class="glass-footer">
    <div class="footer-content">
        <div class="footer-copyright">
            <p>© 2025 Asif Hussain. All rights reserved.</p>
        </div>
        <div class="footer-links">
            <p>CORTEX v4.0 | <a href="https://github.com/asifhussain60/CORTEX">GitHub</a></p>
        </div>
    </div>
</footer>"""
    
    def __init__(self, docs_root: Path, backup_dir: Optional[Path] = None):
        """
        Initialize remediator.
        
        Args:
            docs_root: Path to docs/ directory
            backup_dir: Path to backup directory (default: backups/)
        """
        self.docs_root = Path(docs_root)
        self.backup_dir = backup_dir or Path("backups") / f"glassmorphism_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        self.actions: List[RemediationAction] = []
    
    def create_backup(self, file_path: Path) -> Path:
        """Create backup of file before modification."""
        relative_path = file_path.relative_to(self.docs_root)
        backup_path = self.backup_dir / relative_path
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file_path, backup_path)
        return backup_path
    
    def extract_inline_styles(self, file_path: Path) -> RemediationAction:
        """
        Remove inline style="" attributes and suggest CSS classes.
        
        Note: This is a complex operation that requires semantic understanding.
        For now, we'll just remove inline styles and add TODO comments.
        """
        try:
            self.create_backup(file_path)
            content = file_path.read_text(encoding="utf-8")
            original = content
            
            # Pattern to match inline styles
            pattern = re.compile(r'\s+style\s*=\s*["\'][^"\']*["\']', re.IGNORECASE)
            
            # Count occurrences
            matches = pattern.findall(content)
            
            if matches:
                # Replace with TODO comment
                content = pattern.sub(' <!-- TODO: Extract to CSS class -->', content)
                
                file_path.write_text(content, encoding="utf-8")
                
                return RemediationAction(
                    rule_id="NO_INLINE_STYLES",
                    file_path=file_path,
                    action=f"Removed {len(matches)} inline style attributes",
                    before=f"{len(matches)} inline styles",
                    after="TODO comments added",
                    success=True
                )
            else:
                return RemediationAction(
                    rule_id="NO_INLINE_STYLES",
                    file_path=file_path,
                    action="No inline styles found",
                    success=True
                )
        
        except Exception as e:
            return RemediationAction(
                rule_id="NO_INLINE_STYLES",
                file_path=file_path,
                action="Failed to remove inline styles",
                success=False,
                error_message=str(e)
            )
    
    def add_missing_header(self, file_path: Path) -> RemediationAction:
        """Add standardized glass header to file."""
        try:
            self.create_backup(file_path)
            content = file_path.read_text(encoding="utf-8")
            
            # Check if header already exists
            if '<header class="glass-header">' in content:
                return RemediationAction(
                    rule_id="HEADER_FOOTER_STANDARD",
                    file_path=file_path,
                    action="Header already exists",
                    success=True
                )
            
            # Insert header after <body> tag
            body_pattern = re.compile(r'(<body[^>]*>)', re.IGNORECASE)
            match = body_pattern.search(content)
            
            if match:
                insert_pos = match.end()
                content = (
                    content[:insert_pos] + 
                    "\n\n" + self.GLASS_HEADER_TEMPLATE + "\n\n" +
                    content[insert_pos:]
                )
                
                file_path.write_text(content, encoding="utf-8")
                
                return RemediationAction(
                    rule_id="HEADER_FOOTER_STANDARD",
                    file_path=file_path,
                    action="Added standardized glass header",
                    success=True
                )
            else:
                return RemediationAction(
                    rule_id="HEADER_FOOTER_STANDARD",
                    file_path=file_path,
                    action="Failed to find <body> tag",
                    success=False,
                    error_message="No <body> tag found"
                )
        
        except Exception as e:
            return RemediationAction(
                rule_id="HEADER_FOOTER_STANDARD",
                file_path=file_path,
                action="Failed to add header",
                success=False,
                error_message=str(e)
            )
    
    def add_missing_footer(self, file_path: Path) -> RemediationAction:
        """Add standardized glass footer to file."""
        try:
            self.create_backup(file_path)
            content = file_path.read_text(encoding="utf-8")
            
            # Check if footer already exists
            if '<footer class="glass-footer">' in content:
                return RemediationAction(
                    rule_id="HEADER_FOOTER_STANDARD",
                    file_path=file_path,
                    action="Footer already exists",
                    success=True
                )
            
            # Insert footer before </body> tag
            body_close_pattern = re.compile(r'(</body>)', re.IGNORECASE)
            match = body_close_pattern.search(content)
            
            if match:
                insert_pos = match.start()
                content = (
                    content[:insert_pos] + 
                    "\n\n" + self.GLASS_FOOTER_TEMPLATE + "\n\n" +
                    content[insert_pos:]
                )
                
                file_path.write_text(content, encoding="utf-8")
                
                return RemediationAction(
                    rule_id="HEADER_FOOTER_STANDARD",
                    file_path=file_path,
                    action="Added standardized glass footer",
                    success=True
                )
            else:
                return RemediationAction(
                    rule_id="HEADER_FOOTER_STANDARD",
                    file_path=file_path,
                    action="Failed to find </body> tag",
                    success=False,
                    error_message="No </body> tag found"
                )
        
        except Exception as e:
            return RemediationAction(
                rule_id="HEADER_FOOTER_STANDARD",
                file_path=file_path,
                action="Failed to add footer",
                success=False,
                error_message=str(e)
            )
    
    def remove_t3_animations(self, file_path: Path) -> RemediationAction:
        """Remove T3 dramatic animations from Level 1/2 pages."""
        try:
            self.create_backup(file_path)
            content = file_path.read_text(encoding="utf-8")
            original = content
            
            # T3 keyframe patterns to remove
            t3_patterns = [
                r'@keyframes\s+borderGlowSweep\s*{[^}]*}',
                r'@keyframes\s+blobMorph\s*{[^}]*}',
                r'@keyframes\s+lightLeakPrimary\s*{[^}]*}',
                r'@keyframes\s+glowPulse\s*{[^}]*}',
            ]
            
            removed_count = 0
            for pattern in t3_patterns:
                matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
                removed_count += len(matches)
                content = re.sub(pattern, '', content, flags=re.DOTALL | re.IGNORECASE)
            
            # Remove animation property references
            content = re.sub(
                r'animation:\s*[^;]*(?:borderGlowSweep|blobMorph|lightLeakPrimary|glowPulse)[^;]*;',
                '/* T3 animation removed */',
                content,
                flags=re.IGNORECASE
            )
            
            if content != original:
                file_path.write_text(content, encoding="utf-8")
                
                return RemediationAction(
                    rule_id="T1_ANIMATIONS_ONLY",
                    file_path=file_path,
                    action=f"Removed {removed_count} T3 animation definitions",
                    before="T3 dramatic animations present",
                    after="T3 animations removed",
                    success=True
                )
            else:
                return RemediationAction(
                    rule_id="T1_ANIMATIONS_ONLY",
                    file_path=file_path,
                    action="No T3 animations found",
                    success=True
                )
        
        except Exception as e:
            return RemediationAction(
                rule_id="T1_ANIMATIONS_ONLY",
                file_path=file_path,
                action="Failed to remove T3 animations",
                success=False,
                error_message=str(e)
            )
    
    def rename_forbidden_file(self, file_path: Path) -> RemediationAction:
        """Rename file with forbidden pattern to production name."""
        try:
            file_name = file_path.name
            
            # Extract base name (remove suffixes like -new, -v2, etc.)
            production_name = re.sub(
                r'(-new|-v\d+|-backup|-old|-temp|-test|-draft|-enhanced|-updated)\.html$',
                '.html',
                file_name
            )
            
            if production_name == file_name:
                return RemediationAction(
                    rule_id="PRODUCTION_FILE_NAMING",
                    file_path=file_path,
                    action="File name already production-ready",
                    success=True
                )
            
            new_path = file_path.parent / production_name
            
            # Check if target already exists
            if new_path.exists():
                # Backup existing production file
                self.create_backup(new_path)
            
            # Backup current file before rename
            self.create_backup(file_path)
            
            # Rename file
            file_path.rename(new_path)
            
            return RemediationAction(
                rule_id="PRODUCTION_FILE_NAMING",
                file_path=file_path,
                action=f"Renamed to production name: {production_name}",
                before=file_name,
                after=production_name,
                success=True
            )
        
        except Exception as e:
            return RemediationAction(
                rule_id="PRODUCTION_FILE_NAMING",
                file_path=file_path,
                action="Failed to rename file",
                success=False,
                error_message=str(e)
            )
    
    def generate_report(self) -> str:
        """Generate remediation report."""
        lines = [
            "# 🛠️ Glassmorphism Remediation Report",
            "",
            f"**Backup Location:** {self.backup_dir}",
            f"**Total Actions:** {len(self.actions)}",
            f"**Successful:** {sum(1 for a in self.actions if a.success)}",
            f"**Failed:** {sum(1 for a in self.actions if not a.success)}",
            "",
            "---",
            "",
            "## 📋 Actions Performed",
            "",
        ]
        
        # Group by rule_id
        by_rule: Dict[str, List[RemediationAction]] = {}
        for action in self.actions:
            by_rule.setdefault(action.rule_id, []).append(action)
        
        for rule_id, rule_actions in by_rule.items():
            successful = sum(1 for a in rule_actions if a.success)
            lines.extend([
                f"### {rule_id} ({successful}/{len(rule_actions)} successful)",
                "",
            ])
            
            for action in rule_actions:
                status = "✅" if action.success else "❌"
                lines.append(f"{status} **{action.file_path.name}**: {action.action}")
                
                if action.before and action.after:
                    lines.append(f"   - Before: {action.before}")
                    lines.append(f"   - After: {action.after}")
                
                if not action.success and action.error_message:
                    lines.append(f"   - Error: {action.error_message}")
                
                lines.append("")
        
        lines.extend([
            "---",
            "",
            "## 🔄 Next Steps",
            "",
            "1. Review changes in backup directory",
            "2. Test modified files in browser",
            "3. Run `glassmorphism_validator.py` to verify fixes",
            "4. Commit changes if all tests pass",
            "",
        ])
        
        return "\n".join(lines)


def main():
    """CLI entry point."""
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Automatically fix glassmorphism design standard violations"
    )
    parser.add_argument(
        "docs_root",
        type=Path,
        nargs="?",
        default=Path("docs"),
        help="Path to docs/ directory (default: docs)"
    )
    parser.add_argument(
        "--backup-dir",
        type=Path,
        help="Backup directory path"
    )
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
        help="Apply all fixes"
    )
    parser.add_argument(
        "--report-file",
        type=Path,
        help="Output report to file"
    )
    
    args = parser.parse_args()
    
    # Initialize remediator
    remediator = GlassmorphismRemediator(args.docs_root, args.backup_dir)
    
    # Collect HTML files
    html_files = list(args.docs_root.rglob("*.html"))
    
    print(f"🔍 Found {len(html_files)} HTML files")
    print(f"📦 Backups will be saved to: {remediator.backup_dir}")
    print()
    
    # Apply fixes
    if args.all or args.fix_inline_styles:
        print("🧹 Removing inline styles...")
        for file_path in html_files:
            action = remediator.extract_inline_styles(file_path)
            remediator.actions.append(action)
    
    if args.all or args.add_headers:
        print("📝 Adding missing headers...")
        for file_path in html_files:
            action = remediator.add_missing_header(file_path)
            remediator.actions.append(action)
    
    if args.all or args.add_footers:
        print("📝 Adding missing footers...")
        for file_path in html_files:
            action = remediator.add_missing_footer(file_path)
            remediator.actions.append(action)
    
    if args.all or args.remove_t3_animations:
        print("🎬 Removing T3 animations...")
        for file_path in html_files:
            action = remediator.remove_t3_animations(file_path)
            remediator.actions.append(action)
    
    if args.all or args.rename_files:
        print("📝 Renaming files with forbidden patterns...")
        for file_path in html_files:
            action = remediator.rename_forbidden_file(file_path)
            remediator.actions.append(action)
    
    # Generate report
    report = remediator.generate_report()
    
    if args.report_file:
        args.report_file.write_text(report, encoding="utf-8")
        print(f"\n✅ Report written to: {args.report_file}")
    else:
        print(report)
    
    print(f"\n✅ Remediation complete. {len(remediator.actions)} actions performed.")


if __name__ == "__main__":
    main()
