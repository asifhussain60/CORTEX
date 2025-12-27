#!/usr/bin/env python3
"""
Fix orchestrator HTML pages where body content is embedded in style tags as escaped strings.
"""

import re
from pathlib import Path

def fix_embedded_html(file_path):
    """Extract escaped HTML from style tags and properly structure the document."""
    print(f"Fixing: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract the style section
    style_match = re.search(r'<style[^>]*>(.*?)</style>', content, re.DOTALL)
    if not style_match:
        print(f"  ⚠️  No style section found")
        return
    
    style_content = style_match.group(1)
    
    # Find where actual HTML content starts (after CSS, usually marked by escaped tags)
    # Look for escaped HTML tags like <\/nav>, <\/div>, etc.
    html_content_match = re.search(r'(<nav.*?<\/nav>.*)', style_content, re.DOTALL)
    
    if html_content_match:
        # Extract the embedded HTML
        embedded_html = html_content_match.group(1)
        
        # Unescape the HTML
        unescaped_html = embedded_html.replace('\\/', '/')
        unescaped_html = unescaped_html.replace('\\"', '"')
        
        # Extract just the CSS (everything before the HTML content)
        css_only = style_content[:style_content.find(html_content_match.group(0))]
        
        # Extract head content (everything before </head>)
        head_match = re.search(r'(.*?)<style', content, re.DOTALL)
        if not head_match:
            print(f"  ⚠️  Could not find head section")
            return
            
        head_content = head_match.group(1)
        
        # Reconstruct the document
        new_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
{head_content.replace('<!DOCTYPE html>', '').replace('<html lang="en">', '').replace('<head>', '').strip()}
<style>
{css_only.strip()}
</style>
</head>
<body>
{unescaped_html.strip()}
</body>
</html>'''
        
        # Write the fixed content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"  ✅ Fixed successfully")
    else:
        print(f"  ⚠️  No embedded HTML found")

def main():
    files_to_fix = [
        "docs/technical/orchestrators/cortex-lens.html",
        "docs/technical/orchestrators/intelligent-dashboard.html",
        "docs/technical/orchestrators/planning-system.html"
    ]
    
    base_path = Path(__file__).parent.parent
    
    for file_path in files_to_fix:
        full_path = base_path / file_path
        if full_path.exists():
            fix_embedded_html(full_path)
        else:
            print(f"❌ File not found: {full_path}")
    
    print("\n✅ All files processed!")

if __name__ == "__main__":
    main()
