#!/usr/bin/env python3
"""
Replace inline styles with CSS classes in all story markdown files.

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
"""

import re
from pathlib import Path


def replace_inline_styles(content):
    """Replace inline image styles with CSS classes"""
    
    # Pattern 1: float: right images
    content = re.sub(
        r'<img src="([^"]+)" alt="([^"]*)" style="float:\s*right;\s*margin:\s*0\s+0\s+1em\s+1em;\s*max-width:\s*45%;\s*height:\s*auto;">',
        r'<img src="\1" alt="\2" class="story-image-right">',
        content,
        flags=re.IGNORECASE
    )
    
    # Pattern 2: float: left images
    content = re.sub(
        r'<img src="([^"]+)" alt="([^"]*)" style="float:\s*left;\s*margin:\s*0\s+1em\s+1em\s+0;\s*max-width:\s*45%;\s*height:\s*auto;">',
        r'<img src="\1" alt="\2" class="story-image-left">',
        content,
        flags=re.IGNORECASE
    )
    
    # Pattern 3: Any remaining img with float: right
    content = re.sub(
        r'<img\s+([^>]*)style="[^"]*float:\s*right[^"]*"([^>]*)>',
        lambda m: f'<img {m.group(1)}class="story-image-right"{m.group(2)}>'.replace('class="story-image-right"class=', 'class="story-image-right '),
        content,
        flags=re.IGNORECASE
    )
    
    # Pattern 4: Any remaining img with float: left
    content = re.sub(
        r'<img\s+([^>]*)style="[^"]*float:\s*left[^"]*"([^>]*)>',
        lambda m: f'<img {m.group(1)}class="story-image-left"{m.group(2)}>'.replace('class="story-image-left"class=', 'class="story-image-left '),
        content,
        flags=re.IGNORECASE
    )
    
    # Pattern 5: Special epilogue div
    content = re.sub(
        r'<div style="text-align:\s*center;\s*margin-top:\s*40px;\s*padding:\s*20px;\s*background:\s*linear-gradient\([^)]+\);\s*border-radius:\s*10px;">',
        r'<div class="epilogue-container">',
        content,
        flags=re.IGNORECASE
    )
    
    return content


def process_chapter_file(file_path):
    """Process a single chapter markdown file"""
    print(f"Processing {file_path.name}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    content = replace_inline_styles(content)
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✅ Updated {file_path.name}")
        return True
    else:
        print(f"  ⏭️ No changes needed for {file_path.name}")
        return False


def main():
    """Main execution"""
    story_dir = Path('D:/PROJECTS/CORTEX/docs/story')
    
    if not story_dir.exists():
        print(f"❌ Story directory not found: {story_dir}")
        return
    
    print("🔄 Replacing Inline Styles with CSS Classes")
    print("=" * 60)
    
    updated_count = 0
    total_count = 0
    
    # Process all chapter directories
    chapters = ['Prologue'] + [f'Chapter-{i:02d}' for i in range(1, 14)]
    
    for chapter_dir in chapters:
        chapter_path = story_dir / chapter_dir / 'index.md'
        if chapter_path.exists():
            total_count += 1
            if process_chapter_file(chapter_path):
                updated_count += 1
    
    print("\n" + "=" * 60)
    print(f"✅ Complete: {updated_count}/{total_count} files updated")


if __name__ == '__main__':
    main()
