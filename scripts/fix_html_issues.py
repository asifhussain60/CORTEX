#!/usr/bin/env python3
"""
Fix HTML structural issues across all documentation pages.
Focuses on removing orphaned closing tags and fixing malformed structures.
"""

import re
from pathlib import Path
from typing import Tuple

def fix_orphaned_closing_tags(content: str) -> Tuple[str, int]:
    """Remove orphaned standalone closing tags."""
    fixes = 0
    
    # Remove lines that are just orphaned closing tags
    lines = content.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Skip lines that are ONLY a closing tag with nothing else
        if re.match(r'^\s*</[a-zA-Z]+>\s*$', stripped):
            # Check if it's truly orphaned (not part of a multi-line structure)
            # by looking at previous lines
            if i > 0:
                prev_line = lines[i-1].strip()
                # If previous line doesn't open a tag or has content, it's orphaned
                if not prev_line.endswith('>') or prev_line.startswith('</'):
                    fixes += 1
                    continue
        
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines), fixes

def fix_malformed_emojis(content: str) -> Tuple[str, int]:
    """Fix broken emoji characters."""
    emoji_map = {
        '�️': '🗺️',  # Map icon
        '�': '📈',   # Chart icon (default guess)
    }
    
    fixes = 0
    for broken, fixed in emoji_map.items():
        count = content.count(broken)
        if count > 0:
            content = content.replace(broken, fixed)
            fixes += count
    
    return content, fixes

def fix_closing_before_opening(content: str) -> Tuple[str, int]:
    """Fix pattern where closing tag appears before opening tag of next card."""
    fixes = 0
    
    # Pattern: </tag> followed by newlines and then <div class="glass-card
    pattern = r'(</[a-zA-Z]+>)\s*\n\s*(<(?:div|a)[^>]*class="glass-card)'
    
    def replacer(match):
        nonlocal fixes
        fixes += 1
        # Just put them on consecutive lines with proper spacing
        return f'\n\n                {match.group(2)}'
    
    content = re.sub(pattern, replacer, content)
    
    return content, fixes

def process_file(filepath: Path, dry_run: bool = False) -> dict:
    """Process a single HTML file."""
    try:
        original_content = filepath.read_text(encoding='utf-8')
        content = original_content
        total_fixes = 0
        
        # Apply fixes
        content, orphaned_fixes = fix_orphaned_closing_tags(content)
        total_fixes += orphaned_fixes
        
        content, emoji_fixes = fix_malformed_emojis(content)
        total_fixes += emoji_fixes
        
        content, ordering_fixes = fix_closing_before_opening(content)
        total_fixes += ordering_fixes
        
        if total_fixes > 0 and not dry_run:
            filepath.write_text(content, encoding='utf-8')
        
        return {
            'path': filepath,
            'orphaned_fixed': orphaned_fixes,
            'emoji_fixed': emoji_fixes,
            'ordering_fixed': ordering_fixes,
            'total_fixes': total_fixes
        }
        
    except Exception as e:
        return {
            'path': filepath,
            'error': str(e),
            'total_fixes': 0
        }

def main():
    """Fix all HTML files in docs directory."""
    import sys
    
    project_root = Path(__file__).parent.parent
    docs_dir = project_root / "docs"
    
    dry_run = "--dry-run" in sys.argv
    
    if dry_run:
        print("🧪 DRY RUN MODE - No files will be modified\n")
    
    html_files = sorted(docs_dir.rglob("*.html"))
    
    print(f"🔧 Processing {len(html_files)} HTML files...\n")
    
    files_fixed = 0
    total_fixes = 0
    
    for html_file in html_files:
        result = process_file(html_file, dry_run=dry_run)
        
        if 'error' in result:
            print(f"❌ {html_file.relative_to(docs_dir)}: {result['error']}")
        elif result['total_fixes'] > 0:
            files_fixed += 1
            total_fixes += result['total_fixes']
            
            rel_path = html_file.relative_to(docs_dir)
            print(f"✅ {rel_path}")
            if result['orphaned_fixed'] > 0:
                print(f"   └─ Removed {result['orphaned_fixed']} orphaned closing tags")
            if result['emoji_fixed'] > 0:
                print(f"   └─ Fixed {result['emoji_fixed']} malformed emojis")
            if result['ordering_fixed'] > 0:
                print(f"   └─ Fixed {result['ordering_fixed']} tag ordering issues")
    
    print(f"\n{'[DRY RUN] ' if dry_run else ''}📊 Summary:")
    print(f"   Files fixed: {files_fixed}/{len(html_files)}")
    print(f"   Total fixes applied: {total_fixes}")
    print(f"\n✅ Done!")

if __name__ == "__main__":
    main()
