#!/usr/bin/env python3
"""
CORTEX Visual Sitemap Generator

Generates visual-only ASCII tree showing documentation node hierarchy.
This is a VISUAL TOOL ONLY - shows structure, NOT for status tracking.

Author: Asif Hussain
Version: 1.0.0
Date: January 3, 2026
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class PageNode:
    """Represents a documentation page in the site hierarchy."""
    path: Path
    title: str
    level: int  # 0=Home, 1=Hub, 2=Detail, 3=Deep
    section: str
    is_stub: bool
    is_archived: bool
    children: List['PageNode']
    
    @property
    def status_icon(self) -> str:
        """Get status icon for display."""
        if self.is_archived:
            return "⏭️"
        elif self.is_stub:
            return "🚧"
        else:
            return "✅"
    
    @property
    def display_name(self) -> str:
        """Get display name with status."""
        status = " [STUB]" if self.is_stub else " [ARCHIVED]" if self.is_archived else ""
        return f"{self.title}{status}"


class VisualSitemapGenerator:
    """Generate visual-only ASCII tree showing site hierarchy."""
    
    # Section icons
    SECTION_ICONS = {
        "knowledge": "📚",
        "orchestrators": "🎯",
        "security": "🛡️",
        "sts": "🔧",
        "architecture": "🧠",
        "token-optimization": "💰",
        "toolkit": "🛠️",
        "cortex-lens": "🔍",
        "getting-started": "🚀",
        "story": "📖",
        "features": "⚡",
        "future": "🔮",
    }
    
    def __init__(self, docs_dir: Path):
        self.docs_dir = docs_dir
        self.pages: List[PageNode] = []
        self.tree_lines: List[str] = []
        
    def scan_pages(self) -> List[PageNode]:
        """Scan all documentation pages and build tree structure."""
        if not self.docs_dir.exists():
            return []
        
        # Find all HTML files (exclude archives and cortex-lens-output)
        html_files = []
        for html_file in self.docs_dir.rglob("*.html"):
            rel_path = html_file.relative_to(self.docs_dir)
            if "archives" in rel_path.parts or "cortex-lens-output" in rel_path.parts:
                continue
            html_files.append(html_file)
        
        # Parse each page
        for html_file in html_files:
            node = self._parse_page(html_file)
            self.pages.append(node)
        
        return self.pages
    
    def _parse_page(self, html_file: Path) -> PageNode:
        """Parse a single page and extract metadata."""
        rel_path = html_file.relative_to(self.docs_dir)
        parts = rel_path.parts
        
        # Determine level and section
        if len(parts) == 1 and parts[0] == "index.html":
            level = 0
            section = "root"
        elif len(parts) == 2 and parts[1] == "index.html":
            level = 1
            section = parts[0]
        elif len(parts) == 2:
            level = 1
            section = parts[0]
        elif len(parts) == 3:
            level = 2
            section = parts[0]
        else:
            level = 3
            section = parts[0]
        
        # Read content for title and status
        try:
            content = html_file.read_text(encoding='utf-8', errors='ignore')
            
            # Extract title
            title_match = re.search(r'<title>([^<]+)</title>', content, re.IGNORECASE)
            title = title_match.group(1) if title_match else html_file.stem.replace("-", " ").title()
            
            # Clean title (remove " | CORTEX" suffix)
            title = re.sub(r'\s*\|\s*CORTEX\s*$', '', title)
            
            # Check if stub
            is_stub = bool(re.search(r'stub-container|under construction|Page Status.*Placeholder', content, re.IGNORECASE))
            
            # Check if archived (shouldn't happen, but check)
            is_archived = "archives" in str(rel_path).lower()
            
        except Exception:
            title = html_file.stem.replace("-", " ").title()
            is_stub = False
            is_archived = False
        
        return PageNode(
            path=rel_path,
            title=title,
            level=level,
            section=section,
            is_stub=is_stub,
            is_archived=is_archived,
            children=[]
        )
    
    def build_tree(self) -> str:
        """Build ASCII tree representation."""
        if not self.pages:
            return "No pages found."
        
        # Sort pages by level and path
        sorted_pages = sorted(self.pages, key=lambda p: (p.level, str(p.path)))
        
        # Find home page
        home = next((p for p in sorted_pages if p.level == 0), None)
        if not home:
            return "Home page not found."
        
        # Group pages by section
        sections = defaultdict(list)
        for page in sorted_pages:
            if page.level > 0:
                sections[page.section].append(page)
        
        # Build tree
        lines = [
            "📁 VISUAL SITE MAP - NODE HIERARCHY",
            "",
            f"🏠 {home.title} ({home.path}) - Level 0",
            "|"
        ]
        
        # Sort sections by priority
        section_order = [
            "knowledge", "orchestrators", "security", "sts", 
            "architecture", "token-optimization", "toolkit", 
            "cortex-lens", "getting-started", "story", "features", "future"
        ]
        
        sorted_sections = []
        for sec in section_order:
            if sec in sections:
                sorted_sections.append((sec, sections[sec]))
        
        # Add remaining sections not in priority list
        for sec in sorted(sections.keys()):
            if sec not in section_order:
                sorted_sections.append((sec, sections[sec]))
        
        # Generate tree for each section
        for idx, (section_name, section_pages) in enumerate(sorted_sections):
            is_last_section = (idx == len(sorted_sections) - 1)
            
            # Get section icon
            icon = self.SECTION_ICONS.get(section_name, "📄")
            section_title = section_name.replace("-", " ").upper()
            
            # Count pages by level
            level1_pages = [p for p in section_pages if p.level == 1]
            level2_pages = [p for p in section_pages if p.level == 2]
            level3_pages = [p for p in section_pages if p.level == 3]
            
            # Count stubs
            stubs = len([p for p in section_pages if p.is_stub])
            active = len(section_pages) - stubs
            
            # Section header
            prefix = "└─" if is_last_section else "├─"
            lines.append(f"{prefix}{icon} {section_title} ({active} active, {stubs} stubs)")
            
            # Add Level 1 hub if exists
            hub_pages = [p for p in level1_pages if "index.html" in str(p.path)]
            if hub_pages:
                hub = hub_pages[0]
                indent = "   " if is_last_section else "│  "
                lines.append(f"{indent}├─ {hub.display_name} ({hub.path}) - Hub")
                lines.append(f"{indent}│")
            
            # Add Level 1 pages (non-hub)
            detail_pages = [p for p in level1_pages if "index.html" not in str(p.path)]
            for page_idx, page in enumerate(detail_pages[:5]):  # Limit to 5 for brevity
                indent = "   " if is_last_section else "│  "
                is_last_page = (page_idx == len(detail_pages) - 1) and not level2_pages
                page_prefix = "└─" if is_last_page else "├─"
                lines.append(f"{indent}{page_prefix} {page.display_name} ({page.path})")
            
            if len(detail_pages) > 5:
                indent = "   " if is_last_section else "│  "
                lines.append(f"{indent}├─ ... ({len(detail_pages) - 5} more Level 1 pages)")
            
            # Add Level 2 summary
            if level2_pages:
                indent = "   " if is_last_section else "│  "
                lines.append(f"{indent}│")
                lines.append(f"{indent}└─ Level 2: {len(level2_pages)} pages")
                
                # Show first few Level 2 pages
                for page in level2_pages[:3]:
                    lines.append(f"{indent}   ├─ {page.display_name}")
                
                if len(level2_pages) > 3:
                    lines.append(f"{indent}   └─ ... ({len(level2_pages) - 3} more)")
            
            # Add spacing between sections
            if not is_last_section:
                lines.append("│")
        
        return "\n".join(lines)
    
    def generate_statistics(self) -> Dict:
        """Generate statistics summary."""
        total = len(self.pages)
        stubs = len([p for p in self.pages if p.is_stub])
        active = total - stubs
        
        by_level = defaultdict(int)
        for page in self.pages:
            by_level[page.level] += 1
        
        by_section = defaultdict(lambda: {"total": 0, "stubs": 0, "active": 0})
        for page in self.pages:
            section = page.section
            by_section[section]["total"] += 1
            if page.is_stub:
                by_section[section]["stubs"] += 1
            else:
                by_section[section]["active"] += 1
        
        return {
            "total_pages": total,
            "active_pages": active,
            "stub_pages": stubs,
            "by_level": dict(by_level),
            "by_section": dict(by_section),
        }
    
    def save_to_file(self, output_path: Path):
        """Embed visual sitemap into docs-sitemap.md."""
        tree = self.build_tree()
        stats = self.generate_statistics()
        
        # Read existing docs-sitemap.md
        if not output_path.exists():
            print(f"❌ Error: {output_path} not found. Create it first.")
            return
        
        existing_content = output_path.read_text(encoding='utf-8')
        
        # Build new visual hierarchy section
        new_section = "## 📁 Complete Visual Site Hierarchy\n\n"
        new_section += tree + "\n\n"
        new_section += "---\n\n"
        new_section += f"**Statistics:** {stats['total_pages']} total pages | "
        new_section += f"{stats['active_pages']} active | {stats['stub_pages']} stubs | "
        new_section += f"By Level: Home ({stats['by_level'].get(0, 0)}), "
        new_section += f"L1 ({stats['by_level'].get(1, 0)}), "
        new_section += f"L2 ({stats['by_level'].get(2, 0)}), "
        new_section += f"L3 ({stats['by_level'].get(3, 0)})\n\n"
        
        # Find and replace the "Complete Visual Site Hierarchy" section
        import re
        pattern = r'## 📁 Complete Visual Site Hierarchy.*?(?=^## |\Z)'
        
        if re.search(pattern, existing_content, re.MULTILINE | re.DOTALL):
            # Use a lambda to avoid escape sequence issues
            updated_content = re.sub(
                pattern, 
                lambda m: new_section, 
                existing_content, 
                flags=re.MULTILINE | re.DOTALL
            )
        else:
            # Append before v5.0 Architecture section or at end
            if "## 📋 v5.0 Architecture Documentation Structure" in existing_content:
                parts = existing_content.split("## 📋 v5.0 Architecture Documentation Structure", 1)
                updated_content = parts[0] + new_section + "## 📋 v5.0 Architecture Documentation Structure" + parts[1]
            else:
                updated_content = existing_content + "\n\n" + new_section
        
        # Write back
        output_path.write_text(updated_content, encoding='utf-8')
        
        print(f"✅ Visual sitemap embedded into: {output_path}")
        print(f"   Total pages: {stats['total_pages']} ({stats['active_pages']} active, {stats['stub_pages']} stubs)")


def main():
    """Main entry point."""
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(description="CORTEX Visual Sitemap Generator")
    parser.add_argument("--output", "-o",
                       default="cortex-brain/documents/planning/active/cortex-documentation/artifacts/docs-sitemap.md",
                       help="Output file path (docs-sitemap.md)")
    parser.add_argument("--project-root", "-p", default=None,
                       help="Project root directory (default: auto-detect)")
    
    args = parser.parse_args()
    
    # Auto-detect project root
    if args.project_root:
        project_root = Path(args.project_root).resolve()
    else:
        script_path = Path(__file__).resolve()
        project_root = script_path.parent.parent.parent
        
        if not (project_root / "docs").exists():
            print("Error: Could not find project root. Use --project-root option.")
            sys.exit(1)
    
    docs_dir = project_root / "docs"
    output_path = project_root / args.output
    
    print(f"📄 CORTEX Visual Sitemap Generator v1.0.0")
    print(f"   Docs directory: {docs_dir}")
    
    generator = VisualSitemapGenerator(docs_dir)
    generator.scan_pages()
    generator.save_to_file(output_path)


if __name__ == "__main__":
    main()
