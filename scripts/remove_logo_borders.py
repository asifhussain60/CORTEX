#!/usr/bin/env python3
"""
Remove border/background box from CORTEX logo across all HTML files.
"""
import re
from pathlib import Path

def remove_logo_border(file_path: Path) -> bool:
    """Remove border and add transparent background to logo images."""
    try:
        content = file_path.read_text(encoding='utf-8')
        original_content = content
        
        # Pattern 1: Logo with inline style - ensure transparent background and no border
        # Match any CORTEX-logo.png with style attribute
        pattern1 = r'(<img[^>]*src="[^"]*CORTEX-logo\.png"[^>]*style=")([^"]*)(">)'
        
        def fix_logo_style(match):
            opening = match.group(1)
            current_style = match.group(2)
            closing = match.group(3)
            
            # Parse existing styles
            styles = {}
            for style_pair in current_style.split(';'):
                style_pair = style_pair.strip()
                if ':' in style_pair:
                    key, value = style_pair.split(':', 1)
                    styles[key.strip()] = value.strip()
            
            # Ensure these properties
            styles['border'] = 'none'
            styles['background'] = 'transparent'
            styles['border-radius'] = '0'
            styles['padding'] = '0'
            
            # Rebuild style string
            new_style = '; '.join(f"{k}: {v}" for k, v in styles.items())
            return f"{opening}{new_style}{closing}"
        
        content = re.sub(pattern1, fix_logo_style, content)
        
        # Pattern 2: Container divs around logos - ensure transparent background
        pattern2 = r'(<div class="container"[^>]*)(style="[^"]*")'
        
        def fix_container_style(match):
            opening = match.group(1)
            style_attr = match.group(2)
            
            # If container has a logo inside, ensure transparent
            if 'CORTEX-logo.png' in content[match.end():match.end()+500]:
                current_style = style_attr[7:-1]  # Remove style=" and "
                if 'background' not in current_style:
                    if current_style.strip():
                        new_style = f'style="{current_style}; background: transparent;"'
                    else:
                        new_style = 'style="background: transparent;"'
                    return f"{opening} {new_style}"
            return match.group(0)
        
        content = re.sub(pattern2, fix_container_style, content)
        
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
        if 'CORTEX-logo.png' in html_file.read_text(encoding='utf-8', errors='ignore'):
            if remove_logo_border(html_file):
                print(f"✅ Removed logo border from: {html_file}")
                modified_count += 1
    
    print(f"\n🎉 Modified {modified_count} files")

if __name__ == '__main__':
    main()
