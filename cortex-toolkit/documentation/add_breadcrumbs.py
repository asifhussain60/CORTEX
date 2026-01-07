#!/usr/bin/env python3
"""
CORTEX Breadcrumb Adder

Adds breadcrumb navigation to pages missing them per glassmorphism design standards.
Level 1/2 pages require breadcrumbs for navigation.

Author: Asif Hussain
Version: 1.0.0
"""

import re
from pathlib import Path
from typing import Optional, Tuple

def get_breadcrumb_html(page_path: Path, docs_root: Path) -> Optional[str]:
    """Generate appropriate breadcrumb HTML based on page location."""
    rel_path = page_path.relative_to(docs_root)
    parts = list(rel_path.parts)
    
    if len(parts) == 1:
        # Root level page (e.g., faq.html, sitemap.html)
        page_name = parts[0].replace('.html', '').replace('-', ' ').title()
        return f'''    <!-- Breadcrumb Navigation -->
    <nav class="breadcrumb" aria-label="Breadcrumb">
        <a href="index.html">Home</a>
        <span class="breadcrumb-separator">→</span>
        <span class="breadcrumb-current">{page_name}</span>
    </nav>
'''
    
    elif len(parts) == 2:
        # Level 1 page (e.g., security/index.html, story/viewer.html)
        section = parts[0]
        section_title = section.replace('-', ' ').title()
        page_name = parts[1].replace('.html', '').replace('-', ' ').title()
        
        if parts[1] == 'index.html':
            return f'''    <!-- Breadcrumb Navigation -->
    <nav class="breadcrumb" aria-label="Breadcrumb">
        <a href="../index.html">Home</a>
        <span class="breadcrumb-separator">→</span>
        <span class="breadcrumb-current">{section_title}</span>
    </nav>
'''
        else:
            return f'''    <!-- Breadcrumb Navigation -->
    <nav class="breadcrumb" aria-label="Breadcrumb">
        <a href="../index.html">Home</a>
        <span class="breadcrumb-separator">→</span>
        <a href="index.html">{section_title}</a>
        <span class="breadcrumb-separator">→</span>
        <span class="breadcrumb-current">{page_name}</span>
    </nav>
'''
    
    elif len(parts) >= 3:
        # Level 2+ page
        section = parts[0]
        section_title = section.replace('-', ' ').title()
        subsection = parts[1]
        subsection_title = subsection.replace('-', ' ').title()
        page_name = parts[-1].replace('.html', '').replace('-', ' ').title()
        
        depth = '../' * (len(parts) - 1)
        
        if parts[-1] == 'index.html':
            return f'''    <!-- Breadcrumb Navigation -->
    <nav class="breadcrumb" aria-label="Breadcrumb">
        <a href="{depth}index.html">Home</a>
        <span class="breadcrumb-separator">→</span>
        <a href="{depth}{section}/index.html">{section_title}</a>
        <span class="breadcrumb-separator">→</span>
        <span class="breadcrumb-current">{subsection_title}</span>
    </nav>
'''
        else:
            return f'''    <!-- Breadcrumb Navigation -->
    <nav class="breadcrumb" aria-label="Breadcrumb">
        <a href="{depth}index.html">Home</a>
        <span class="breadcrumb-separator">→</span>
        <a href="{depth}{section}/index.html">{section_title}</a>
        <span class="breadcrumb-separator">→</span>
        <span class="breadcrumb-current">{page_name}</span>
    </nav>
'''
    
    return None

def has_breadcrumb(content: str) -> bool:
    """Check if content already has breadcrumb navigation."""
    return bool(re.search(r'<nav[^>]*class="[^"]*breadcrumb', content))

def add_breadcrumb_to_file(filepath: Path, docs_root: Path) -> bool:
    """Add breadcrumb to HTML file if missing."""
    try:
        content = filepath.read_text(encoding='utf-8')
        
        if has_breadcrumb(content):
            return False  # Already has breadcrumb
        
        breadcrumb = get_breadcrumb_html(filepath, docs_root)
        if not breadcrumb:
            return False
        
        # Insert breadcrumb after <body> tag
        body_match = re.search(r'<body[^>]*>', content)
        if body_match:
            insert_pos = body_match.end()
            new_content = content[:insert_pos] + '\n' + breadcrumb + content[insert_pos:]
            filepath.write_text(new_content, encoding='utf-8')
            return True
        
        return False
    except Exception as e:
        print(f"  ⚠️  Error processing {filepath}: {e}")
        return False

def main():
    """Main execution."""
    docs_path = Path('/Users/asifhussain/PROJECTS/CORTEX/docs')
    
    # Pages/directories that need breadcrumbs checked
    check_paths = [
        'dashboard-diagnostic.html',
        'sitemap.html', 
        'test-tabs.html',
        'cortex-lens-output',
        'story',
        'features/orchestrators.html',
        'toolkit-manager/index.html',
    ]
    
    added_count = 0
    processed_files = []
    
    print("🔗 CORTEX Breadcrumb Adder")
    print("=" * 50)
    print(f"Docs path: {docs_path}")
    print()
    
    # Process specific files and directories
    for check_path in check_paths:
        full_path = docs_path / check_path
        if full_path.is_file():
            if add_breadcrumb_to_file(full_path, docs_path):
                added_count += 1
                processed_files.append(check_path)
                print(f"  ✅ Added breadcrumb: {check_path}")
        elif full_path.is_dir():
            for html_file in full_path.rglob('*.html'):
                rel_path = html_file.relative_to(docs_path)
                if add_breadcrumb_to_file(html_file, docs_path):
                    added_count += 1
                    processed_files.append(str(rel_path))
                    print(f"  ✅ Added breadcrumb: {rel_path}")
    
    print()
    print("=" * 50)
    print(f"✅ Added breadcrumbs to {added_count} files")

if __name__ == '__main__':
    main()
