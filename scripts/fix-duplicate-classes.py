"""
CORTEX HTML Class Attribute Fix
Merges duplicate class attributes into single consolidated class attribute
"""

import re
from pathlib import Path

def fix_duplicate_classes(html_path: Path):
    """Merge duplicate class attributes in HTML"""
    
    content = html_path.read_text(encoding='utf-8')
    original_content = content
    
    # Pattern to match duplicate class attributes: class="..." class="..."
    # Captures both class values
    pattern = r'class="([^"]*)" class="([^"]*)"'
    
    def merge_classes(match):
        """Merge two class attributes, removing duplicates"""
        classes1 = match.group(1).split()
        classes2 = match.group(2).split()
        
        # Combine and deduplicate while preserving order
        seen = set()
        merged = []
        for cls in classes1 + classes2:
            if cls and cls not in seen:
                seen.add(cls)
                merged.append(cls)
        
        return f'class="{" ".join(merged)}"'
    
    # Apply the fix
    fixed_content = re.sub(pattern, merge_classes, content)
    
    # Count how many fixes were made
    matches = re.findall(pattern, content)
    fixes = len(matches)
    
    # Write back if changes made
    if fixed_content != original_content:
        html_path.write_text(fixed_content, encoding='utf-8')
        print(f"✅ {html_path.name}: {fixes} duplicate class attributes fixed")
        return fixes
    else:
        print(f"⚠️ {html_path.name}: No duplicate class attributes found")
        return 0

if __name__ == "__main__":
    html_files = [
        Path("d:/PROJECTS/CORTEX/cortex-docs/index.html"),
        Path("d:/PROJECTS/CORTEX/cortex-docs/coming-soon.html"),
        Path("d:/PROJECTS/CORTEX/cortex-docs/api/index.html"),
    ]
    
    total_fixed = 0
    for html_file in html_files:
        if html_file.exists():
            fixed = fix_duplicate_classes(html_file)
            total_fixed += fixed
        else:
            print(f"⚠️ File not found: {html_file}")
    
    print(f"\n🎯 TOTAL: {total_fixed} duplicate class attributes fixed across all files")
