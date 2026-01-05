#!/usr/bin/env python3
"""
Apply 7-Color Glassmorphism Classes to All Level 1 Hub Pages

Scans all Level 1 hub pages and applies randomized glass-panel-{color} classes 
to glass-card-display sections. Replaces inline styles with CSS classes for 
clean, maintainable code.

Available Classes:
- glass-panel-cyan
- glass-panel-purple
- glass-panel-teal
- glass-panel-indigo
- glass-panel-pink
- glass-panel-emerald
- glass-panel-amber
"""

import re
import random
from pathlib import Path
from typing import List, Dict, Tuple

# Level 1 Hub Pages
LEVEL1_HUBS = [
    "docs/architecture/index.html",
    "docs/features/index.html",
    "docs/getting-started/index.html",
    "docs/knowledge/index.html",
    "docs/learning-paths/index.html",
    "docs/lens/index.html",
    "docs/orchestrators/index.html",
    "docs/security/index.html",
    "docs/story/index.html",
    "docs/sts/index.html",
    "docs/token-optimization/index.html",
    "docs/toolkit-manager/index.html",
]

# 7-Color Palette
GLASS_COLORS = ['cyan', 'purple', 'teal', 'indigo', 'pink', 'emerald', 'amber']


def find_glass_sections(html_content: str) -> List[Tuple[int, int, str]]:
    """
    Find all glass-card-display sections.
    
    Returns: List of (start_pos, end_pos, section_html)
    """
    sections = []
    pattern = r'<section\s+class="glass-card-display[^"]*"[^>]*>.*?</section>'
    
    for match in re.finditer(pattern, html_content, re.DOTALL):
        sections.append((match.start(), match.end(), match.group(0)))
    
    return sections


def has_color_class(section_html: str) -> bool:
    """Check if section already has a glass-panel-{color} class."""
    for color in GLASS_COLORS:
        if f'glass-panel-{color}' in section_html:
            return True
    return False


def add_color_class(section_html: str, color: str) -> str:
    """Add glass-panel-{color} class to section."""
    
    # Check if already has a color class
    if has_color_class(section_html):
        # Replace existing color class
        for existing_color in GLASS_COLORS:
            if f'glass-panel-{existing_color}' in section_html:
                return section_html.replace(
                    f'glass-panel-{existing_color}',
                    f'glass-panel-{color}'
                )
    
    # Add new color class
    pattern = r'class="glass-card-display([^"]*)"'
    replacement = f'class="glass-card-display\\1 glass-panel-{color}"'
    return re.sub(pattern, replacement, section_html, count=1)


def remove_inline_background_styles(section_html: str) -> str:
    """Remove inline background/backdrop-filter/box-shadow styles."""
    
    # Remove entire style attribute if it only contains background/backdrop/box-shadow
    style_pattern = r'\s+style="[^"]*"'
    
    if 'style="' in section_html:
        # Extract style content
        style_match = re.search(r'style="([^"]*)"', section_html)
        if style_match:
            style_content = style_match.group(1)
            
            # Check if style only contains glassmorphism properties
            glass_props = ['background:', 'backdrop-filter:', '-webkit-backdrop-filter:', 
                          'border:', 'box-shadow:']
            
            # Remove glassmorphism properties
            cleaned_style = style_content
            for prop in glass_props:
                # Remove property and its value (up to semicolon or end)
                cleaned_style = re.sub(rf'{prop}[^;]*;?\s*', '', cleaned_style)
            
            cleaned_style = cleaned_style.strip()
            
            if not cleaned_style:
                # Remove entire style attribute
                section_html = re.sub(style_pattern, '', section_html, count=1)
            else:
                # Keep style attribute with remaining properties
                section_html = re.sub(
                    r'style="[^"]*"',
                    f'style="{cleaned_style}"',
                    section_html,
                    count=1
                )
    
    return section_html


def process_file(file_path: Path, dry_run: bool = False) -> Dict:
    """Process a single Level 1 hub file."""
    
    print(f"\n📄 {file_path.relative_to(file_path.parents[2])}")
    
    # Read file
    html_content = file_path.read_text(encoding='utf-8')
    
    # Find all glass-card-display sections
    sections = find_glass_sections(html_content)
    
    if not sections:
        print(f"   ⚠️  No glass-card-display sections found")
        return {'processed': False, 'sections': 0}
    
    print(f"   Found {len(sections)} glass-card-display sections")
    
    # Process sections in reverse order (to preserve positions)
    updated_content = html_content
    sections_updated = 0
    color_distribution = {}
    
    for start_pos, end_pos, section_html in reversed(sections):
        # Choose random color
        color = random.choice(GLASS_COLORS)
        
        # Add color class
        updated_section = add_color_class(section_html, color)
        
        # Remove inline styles
        updated_section = remove_inline_background_styles(updated_section)
        
        # Replace in content
        updated_content = (
            updated_content[:start_pos] +
            updated_section +
            updated_content[end_pos:]
        )
        
        sections_updated += 1
        color_distribution[color] = color_distribution.get(color, 0) + 1
    
    # Show color distribution
    for color, count in sorted(color_distribution.items()):
        print(f"   → {color}: {count} section(s)")
    
    # Write updated content
    if not dry_run:
        file_path.write_text(updated_content, encoding='utf-8')
        print(f"   ✅ Updated {sections_updated} sections")
    else:
        print(f"   🔍 DRY RUN: Would update {sections_updated} sections")
    
    return {
        'processed': True,
        'sections': sections_updated,
        'colors': color_distribution
    }


def main():
    """Main execution."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Apply 7-color glassmorphism classes to Level 1 hub pages"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without modifying files'
    )
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("🎨 Level 1 Glassmorphism Applicator - CSS Class Mode")
    print("=" * 80)
    print(f"\nMode: {'🔍 DRY RUN' if args.dry_run else '✅ LIVE'}")
    print(f"Target: {len(LEVEL1_HUBS)} Level 1 hub pages")
    print(f"Classes: {', '.join([f'glass-panel-{c}' for c in GLASS_COLORS])}")
    
    workspace = Path.cwd()
    total_sections = 0
    total_colors = {}
    
    for hub_path in LEVEL1_HUBS:
        file_path = workspace / hub_path
        
        if not file_path.exists():
            print(f"\n❌ Not found: {hub_path}")
            continue
        
        try:
            result = process_file(file_path, dry_run=args.dry_run)
            if result['processed']:
                total_sections += result['sections']
                for color, count in result.get('colors', {}).items():
                    total_colors[color] = total_colors.get(color, 0) + count
        except Exception as e:
            print(f"\n❌ Error: {e}")
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 SUMMARY")
    print("=" * 80)
    print(f"\n✅ Total Sections Updated: {total_sections}")
    
    if total_colors:
        print("\n🎨 Color Distribution:")
        for color in GLASS_COLORS:
            count = total_colors.get(color, 0)
            if count > 0:
                pct = (count / total_sections * 100) if total_sections > 0 else 0
                print(f"   {color:8s}: {count:2d} ({pct:5.1f}%)")
    
    if args.dry_run:
        print("\n💡 Re-run without --dry-run to apply changes")
    else:
        print("\n✅ All changes applied!")
        print("\n📋 Next Steps:")
        print("   1. Test: Open http://localhost:8000/orchestrators/index.html")
        print("   2. Verify: Check glassmorphism backgrounds")
        print("   3. Commit: git add -A && git commit -m 'feat(ui): Apply 7-color glassmorphism to Level 1 hubs'")


if __name__ == "__main__":
    main()
