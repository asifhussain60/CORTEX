#!/usr/bin/env python3
"""
Convert glass-card divs with nested links to fully clickable anchor-wrapped cards.
Applies consistent hover effects across all HTML pages in the docs directory.
"""

import re
from pathlib import Path
from typing import List, Tuple

def convert_card_to_clickable(html_content: str) -> Tuple[str, int]:
    """
    Convert div.glass-card.feature-card with nested <a class="learn-more"> 
    to anchor-wrapped clickable cards.
    
    Returns: (modified_content, num_conversions)
    """
    conversions = 0
    
    # Pattern to match: <div class="glass-card feature-card">...content...<a href="..." class="learn-more">...</a></div>
    pattern = r'(<div class="glass-card feature-card"[^>]*>)(.*?)<a href="([^"]+)" class="learn-more"[^>]*>([^<]+)</a>\s*</div>'
    
    def replace_card(match):
        nonlocal conversions
        div_opening = match.group(1)
        card_content = match.group(2)
        link_href = match.group(3)
        link_text = match.group(4)
        
        # Extract any inline styles from the div
        style_match = re.search(r'style="([^"]*)"', div_opening)
        existing_style = style_match.group(1) if style_match else ""
        
        # Build new anchor tag
        if existing_style:
            new_opening = f'<a href="{link_href}" class="glass-card feature-card feature-card-link" style="{existing_style}; text-decoration: none;">'
        else:
            new_opening = f'<a href="{link_href}" class="glass-card feature-card feature-card-link" style="text-decoration: none;">'
        
        # Remove the learn-more link from content (it's now redundant)
        conversions += 1
        return f"{new_opening}{card_content}</a>"
    
    modified_content = re.sub(pattern, replace_card, html_content, flags=re.DOTALL)
    return modified_content, conversions

def process_html_files(docs_dir: Path, dry_run: bool = False) -> None:
    """Process all HTML files in the docs directory."""
    
    html_files = list(docs_dir.rglob("*.html"))
    total_conversions = 0
    files_modified = 0
    
    print(f"🔍 Found {len(html_files)} HTML files to process...")
    print()
    
    for html_file in html_files:
        try:
            content = html_file.read_text(encoding='utf-8')
            modified_content, conversions = convert_card_to_clickable(content)
            
            if conversions > 0:
                files_modified += 1
                total_conversions += conversions
                
                print(f"✅ {html_file.relative_to(docs_dir)}")
                print(f"   └─ {conversions} card(s) converted")
                
                if not dry_run:
                    html_file.write_text(modified_content, encoding='utf-8')
                    
        except Exception as e:
            print(f"❌ Error processing {html_file.relative_to(docs_dir)}: {e}")
    
    print()
    print(f"{'[DRY RUN] ' if dry_run else ''}📊 Summary:")
    print(f"   Files modified: {files_modified}")
    print(f"   Total conversions: {total_conversions}")

if __name__ == "__main__":
    import sys
    
    # Get project root (2 levels up from scripts/)
    project_root = Path(__file__).parent.parent
    docs_dir = project_root / "docs"
    
    # Check for dry-run flag
    dry_run = "--dry-run" in sys.argv
    
    if dry_run:
        print("🧪 DRY RUN MODE - No files will be modified")
        print()
    
    process_html_files(docs_dir, dry_run=dry_run)
    
    print()
    print("✅ Done!")
