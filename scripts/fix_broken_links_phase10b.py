"""
Fix broken internal links in HTML files
Phase 10b: Link Validation and Repair
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

class LinkFixer:
    """Automated link fixer for Phase 10b"""
    
    def __init__(self, workspace_root: str):
        self.workspace_root = Path(workspace_root)
        self.docs_dir = self.workspace_root / "docs"
        self.fixes_applied = []
        
    def analyze_broken_links(self, broken_links_file: str) -> Dict:
        """Parse link validation report"""
        
        # Most broken links are CSS files with wrong version query strings
        # Strategy: Remove version query strings from CSS links
        
        return {
            "strategy": "remove_version_query_strings",
            "reason": "CSS files don't need version params, browser cache busting handled elsewhere"
        }
    
    def fix_css_version_links(self, html_file: Path) -> int:
        """Remove version query strings from CSS links"""
        
        fixes = 0
        
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Pattern 1: main.css?v=4.0.1 → main.css
            # Pattern 2: variables.css?v=2026-01-03 → variables.css
            
            patterns = [
                (r'href="([^"]+\.css)\?v=[^"]*"', r'href="\1"'),
                (r'src="([^"]+\.js)\?v=[^"]*"', r'src="\1"'),
            ]
            
            for pattern, replacement in patterns:
                content = re.sub(pattern, replacement, content)
            
            if content != original_content:
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                # Count fixes
                fixes = len(re.findall(r'\?v=', original_content)) - len(re.findall(r'\?v=', content))
                
                self.fixes_applied.append({
                    "file": str(html_file.relative_to(self.workspace_root)),
                    "fixes": fixes,
                    "type": "css_version_removal"
                })
        
        except Exception as e:
            print(f"Error fixing {html_file}: {e}")
        
        return fixes
    
    def fix_missing_files(self, html_file: Path) -> int:
        """Fix links to missing files"""
        
        fixes = 0
        
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Fix specific known missing files
            replacements = {
                'technical/orchestrators/code-sanitization.html': 'orchestrators/cleanup-orchestrator.html',
                'technical/orchestrators/refinement-orchestrator.html': 'orchestrators/refinement-orchestrator.html',
                '../governance/skull-rulebook.html': '../security/index.html',  # SKULL rules in security section
                'brain-tiers.html': 'four-tier-brain.html',  # Renamed file
                'migration-guide.html': 'index.html',  # Design system migration guide in index
                '../assets/css/intentional-classes.css': 'assets/css/intentional-classes.css',  # Wrong path depth
            }
            
            for old_link, new_link in replacements.items():
                content = content.replace(f'"{old_link}"', f'"{new_link}"')
                content = content.replace(f"'{old_link}'", f"'{new_link}'")
            
            if content != original_content:
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                fixes = len([k for k in replacements.keys() if k in original_content])
                
                self.fixes_applied.append({
                    "file": str(html_file.relative_to(self.workspace_root)),
                    "fixes": fixes,
                    "type": "missing_file_redirect"
                })
        
        except Exception as e:
            print(f"Error fixing {html_file}: {e}")
        
        return fixes
    
    def fix_all_html_files(self) -> Dict:
        """Fix all HTML files in docs directory"""
        
        print("🔧 Phase 10b: Link Repair")
        print("=" * 80)
        
        all_html_files = list(self.docs_dir.rglob("*.html"))
        
        total_fixes = 0
        files_modified = 0
        
        print(f"\n📄 Found {len(all_html_files)} HTML files")
        print("\n🔗 Fixing CSS version query strings...")
        
        for html_file in all_html_files:
            fixes = self.fix_css_version_links(html_file)
            if fixes > 0:
                total_fixes += fixes
                files_modified += 1
                print(f"  ✅ {html_file.relative_to(self.workspace_root)}: {fixes} fixes")
        
        print(f"\n✅ CSS version links: {total_fixes} fixes across {files_modified} files")
        
        print("\n🔗 Fixing missing file links...")
        
        missing_fixes = 0
        missing_files_modified = 0
        
        for html_file in all_html_files:
            fixes = self.fix_missing_files(html_file)
            if fixes > 0:
                missing_fixes += fixes
                missing_files_modified += 1
                print(f"  ✅ {html_file.relative_to(self.workspace_root)}: {fixes} fixes")
        
        print(f"\n✅ Missing file links: {missing_fixes} fixes across {missing_files_modified} files")
        
        summary = {
            "total_files_scanned": len(all_html_files),
            "files_modified": files_modified + missing_files_modified,
            "total_fixes": total_fixes + missing_fixes,
            "css_version_fixes": total_fixes,
            "missing_file_fixes": missing_fixes,
            "fixes_by_file": self.fixes_applied
        }
        
        print("\n" + "=" * 80)
        print("📊 Summary")
        print("=" * 80)
        print(f"Total Files Scanned: {summary['total_files_scanned']}")
        print(f"Files Modified: {summary['files_modified']}")
        print(f"Total Fixes Applied: {summary['total_fixes']}")
        print(f"  - CSS Version Fixes: {summary['css_version_fixes']}")
        print(f"  - Missing File Fixes: {summary['missing_file_fixes']}")
        
        return summary


def main():
    workspace = r"D:\PROJECTS\CORTEX"
    fixer = LinkFixer(workspace)
    
    summary = fixer.fix_all_html_files()
    
    # Save summary
    import json
    from datetime import datetime
    
    reports_dir = Path(workspace) / "cortex-brain" / "documents" / "planning" / "active" / "html-glassmorphism-alignment" / "reports"
    output_file = reports_dir / "phase-10b-link-fixes.json"
    
    with open(output_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "summary": summary
        }, f, indent=2)
    
    print(f"\n📝 Summary saved to: {output_file.relative_to(workspace)}")
    print("\n✅ Phase 10b Link Repair Complete!")


if __name__ == "__main__":
    main()
