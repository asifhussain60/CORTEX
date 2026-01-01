#!/usr/bin/env python3
"""
Phase 3 Level 2 Page Scanner
Identifies which detail pages need inline style cleanup
"""

from pathlib import Path
import re

def scan_level2_pages():
    """Scan all Level 2 detail pages for inline styles"""
    docs_dir = Path("docs")
    
    # Find all HTML files except index.html
    all_html = []
    for html_file in docs_dir.rglob("*.html"):
        if html_file.name != "index.html":
            all_html.append(html_file)
    
    files_with_styles = []
    
    for html_file in all_html:
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Count style= attributes
            style_count = len(re.findall(r'style="[^"]*"', content))
            
            if style_count > 0:
                files_with_styles.append((str(html_file), style_count))
        except Exception as e:
            print(f"Error reading {html_file}: {e}")
    
    # Sort by count descending
    files_with_styles.sort(key=lambda x: x[1], reverse=True)
    
    print(f"\n{'='*80}")
    print("PHASE 3: LEVEL 2 DETAIL PAGES - INLINE STYLE SCAN")
    print(f"{'='*80}\n")
    print(f"Total Level 2 pages scanned: {len(all_html)}")
    print(f"Pages with inline styles: {len(files_with_styles)}")
    print(f"Pages already clean: {len(all_html) - len(files_with_styles)}\n")
    
    if files_with_styles:
        print("FILES NEEDING CLEANUP:\n")
        for file_path, count in files_with_styles:
            print(f"  {file_path:60s} - {count:3d} styles")
    else:
        print("✅ ALL LEVEL 2 PAGES ARE ALREADY CLEAN!\n")
    
    print(f"\n{'='*80}\n")
    
    return files_with_styles

if __name__ == "__main__":
    scan_level2_pages()
