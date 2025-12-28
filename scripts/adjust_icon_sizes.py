#!/usr/bin/env python3
"""
Adjust icon sizes to be proportionate to their titles across all HTML files.
"""
import re
from pathlib import Path

def adjust_icon_sizes(file_path: Path) -> bool:
    """Adjust icon sizes in an HTML file."""
    try:
        content = file_path.read_text(encoding='utf-8')
        original_content = content
        
        # Pattern 1: card-icon without size - add 3rem size
        pattern1 = r'(<span class="card-icon">)'
        replacement1 = r'<span class="card-icon" style="font-size: 3rem;">'
        content = re.sub(pattern1, replacement1, content)
        
        # Pattern 2: persona-icon without size - add 3.5rem size
        pattern2 = r'(<div class="persona-icon">)'
        replacement2 = r'<div class="persona-icon" style="font-size: 3.5rem;">'
        content = re.sub(pattern2, replacement2, content)
        
        # Pattern 3: metric-card icons (emoji in div without class) - add 3rem size
        # Look for pattern: <div>🤖</div> followed by <h3>
        pattern3 = r'(<div class="metric-card">\s*<div>)([\U0001F000-\U0001FFFF]+)(</div>\s*<h3>)'
        replacement3 = r'\1<span style="font-size: 3rem; display: block; margin-bottom: 1rem;">\2</span>\3'
        content = re.sub(pattern3, replacement3, content, flags=re.UNICODE)
        
        # Pattern 4: icon div with emoji - ensure consistent sizing
        pattern4 = r'<div>([🎯🔍🔒📚⚙️🤖🎓🔄⏱️📊🧹🔧✨🛡️📖❓💻📋👔])</div>'
        replacement4 = r'<div style="font-size: 3rem; margin-bottom: 1rem;">\1</div>'
        content = re.sub(pattern4, replacement4, content)
        
        if content != original_content:
            file_path.write_text(content, encoding='utf-8')
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    docs_dir = Path('docs')
    html_files = list(docs_dir.rglob('*.html'))
    
    modified_count = 0
    for html_file in html_files:
        if adjust_icon_sizes(html_file):
            print(f"✅ Adjusted icons in: {html_file}")
            modified_count += 1
    
    print(f"\n🎉 Modified {modified_count} files")

if __name__ == '__main__':
    main()
