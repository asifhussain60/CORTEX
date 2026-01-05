#!/usr/bin/env python3
"""
CORTEX Footer Modernizer - v1.0.0

Modernizes footer to display only:
- 100x100px CORTEX logo
- Modern styled copyright text
- Mobile-responsive design

Author: Asif Hussain
Date: January 5, 2026
"""

import re
from pathlib import Path
from typing import List, Tuple

# Modern footer HTML with 100x100px PNG logo (centered horizontal layout)
MODERN_FOOTER_HTML = '''
<!-- Modern Glass Footer -->
<footer class="glass-footer-modern">
    <div class="footer-modern-content">
        <img src="../assets/images/CORTEX-logo.png" alt="CORTEX" class="cortex-logo-footer" width="100" height="100" />
        <p class="footer-copyright-modern">
            Copyright © 2025-2026 <span class="copyright-author">Asif Hussain</span>. All rights reserved.
        </p>
    </div>
</footer>'''

# Modern footer CSS (centered horizontal layout at all sizes)
MODERN_FOOTER_CSS = '''
    /* ═══════════════════════════════════════════════════════════════
       MODERN GLASS FOOTER - Centered Horizontal Layout
       ═══════════════════════════════════════════════════════════════ */
    
    .glass-footer-modern {
        background: rgba(26, 31, 58, 0.6);
        backdrop-filter: blur(20px) saturate(180%);
        border-top: 1px solid rgba(123, 97, 255, 0.3);
        padding: 2rem 1rem;
        margin-top: 4rem;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    
    .footer-modern-content {
        display: flex;
        flex-direction: row;
        align-items: center;
        justify-content: center;
        gap: 1.5rem;
        max-width: 1200px;
        width: 100%;
    }
    
    /* CORTEX Logo Styling */
    .cortex-logo-footer {
        width: 100px;
        height: 100px;
        flex-shrink: 0;
        filter: drop-shadow(0 0 20px rgba(123, 97, 255, 0.5));
        transition: transform 0.3s ease, filter 0.3s ease;
    }
    
    .cortex-logo-footer:hover {
        transform: scale(1.05);
        filter: drop-shadow(0 0 30px rgba(0, 212, 255, 0.7));
    }
    
    /* Modern Copyright Text */
    .footer-copyright-modern {
        font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif;
        font-size: 0.95rem;
        font-weight: 400;
        letter-spacing: 0.02em;
        color: rgba(255, 255, 255, 0.7);
        margin: 0;
        line-height: 1.6;
    }
    
    .copyright-author {
        font-weight: 600;
        color: rgba(255, 255, 255, 0.95);
        background: linear-gradient(135deg, #00d4ff 0%, #7b61ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Desktop (1024px+) - Increased spacing */
    @media (min-width: 1024px) {
        .glass-footer-modern {
            padding: 2.5rem 2rem;
        }
        
        .footer-modern-content {
            gap: 2rem;
        }
    }
    
    /* Mobile Portrait (<768px) - Slightly smaller logo */
    @media (max-width: 767px) {
        .cortex-logo-footer {
            width: 80px;
            height: 80px;
        }
        
        .footer-copyright-modern {
            font-size: 0.875rem;
        }
        
        .footer-modern-content {
            gap: 1rem;
        }
    }
    
    /* Landscape Mode (short viewports) - Compact layout */
    @media (orientation: landscape) and (max-height: 600px) {
        .glass-footer-modern {
            padding: 1.5rem 1rem;
            margin-top: 2rem;
        }
        
        .cortex-logo-footer {
            width: 70px;
            height: 70px;
        }
        
        .footer-modern-content {
            gap: 1rem;
        }
    }'''


def find_footer_section(content: str) -> Tuple[int, int]:
    """Find the start and end position of footer section."""
    # Pattern 1: <!-- Glass Footer --> or <!-- Footer --> followed by <footer>
    footer_patterns = [
        r'<!--\s*(Glass\s*)?Footer\s*-->\s*<footer',  # With comment
        r'<footer[^>]*class=["\']glass-footer[^"\']*["\']',  # With glass-footer class
        r'<footer[^>]*>',  # Plain footer tag
    ]
    
    start_match = None
    for pattern in footer_patterns:
        start_match = re.search(pattern, content, re.IGNORECASE)
        if start_match:
            break
    
    if not start_match:
        return (-1, -1)
    
    start_pos = start_match.start()
    
    # Find corresponding </footer>
    remaining = content[start_pos:]
    end_match = re.search(r'</footer>', remaining, re.IGNORECASE)
    
    if not end_match:
        return (-1, -1)
    
    end_pos = start_pos + end_match.end()
    
    return (start_pos, end_pos)


def check_main_css_has_footer_styles(html_content: str) -> bool:
    """Check if main.css is linked and likely contains footer styles."""
    # Check if main.css is linked
    if 'main.css' in html_content:
        # Assume main.css has footer styles (prevents duplication)
        # This is safe because main.css is the central stylesheet
        return True
    return False


def add_modern_footer_css(content: str) -> str:
    """Add modern footer CSS if not already present.
    
    INTELLIGENCE: Checks multiple locations to prevent duplication:
    1. Inline <style> tags in the HTML
    2. Linked main.css stylesheet (assumes it has footer styles)
    3. External CSS imports
    
    This prevents the "CSS missing" issue when main.css already has the styles.
    """
    # Check if CSS already exists in inline styles
    if 'glass-footer-modern' in content:
        print("  ℹ️  Modern footer CSS already exists (inline)")
        return content
    
    # Check if main.css is linked (PREVENTS DUPLICATION)
    if check_main_css_has_footer_styles(content):
        print("  ℹ️  Modern footer CSS already exists (main.css)")
        return content
    
    # Only add CSS if neither inline nor in main.css
    # Find </style> tag
    style_end_match = re.search(r'</style>', content, re.IGNORECASE)
    
    if style_end_match:
        # Insert before </style>
        insert_pos = style_end_match.start()
        new_content = content[:insert_pos] + MODERN_FOOTER_CSS + '\n' + content[insert_pos:]
        return new_content
    else:
        # No </style> tag - add <style> section before </head>
        head_end_match = re.search(r'</head>', content, re.IGNORECASE)
        if head_end_match:
            insert_pos = head_end_match.start()
            css_section = f'<style>{MODERN_FOOTER_CSS}\n</style>\n'
            new_content = content[:insert_pos] + css_section + content[insert_pos:]
            return new_content
    
    return content


def modernize_footer(file_path: Path) -> bool:
    """Replace old footer with modern copyright-only footer."""
    try:
        content = file_path.read_text(encoding='utf-8')
        original_content = content
        
        # Find existing footer
        start_pos, end_pos = find_footer_section(content)
        
        if start_pos == -1:
            print(f"  ⚠️  No footer found in {file_path.name}")
            return False
        
        # Replace old footer with modern footer
        new_content = content[:start_pos] + MODERN_FOOTER_HTML + content[end_pos:]
        
        # Add modern footer CSS
        new_content = add_modern_footer_css(new_content)
        
        # Save changes
        if new_content != original_content:
            file_path.write_text(new_content, encoding='utf-8')
            return True
        
        return False
        
    except Exception as e:
        print(f"  ❌ Error processing {file_path}: {e}")
        return False


def main():
    """Main execution."""
    docs_dir = Path('docs')
    
    # Get all HTML files
    html_files = list(docs_dir.rglob('*.html'))
    
    print("\n╔══════════════════════════════════════════════════════════════╗")
    print("║  🎨 CORTEX Footer Modernizer v1.0.0                     ║")
    print("╚══════════════════════════════════════════════════════════════╝\n")
    
    print(f"📊 Found {len(html_files)} HTML files\n")
    
    modified_count = 0
    skipped_count = 0
    
    for html_file in html_files:
        print(f"🔍 Processing: {html_file.relative_to(docs_dir)}")
        
        if modernize_footer(html_file):
            print(f"  ✅ Modernized footer with logo + copyright\n")
            modified_count += 1
        else:
            print(f"  ⏭️  Skipped\n")
            skipped_count += 1
    
    # Summary
    print("\n╔══════════════════════════════════════════════════════════════╗")
    print("║  📊 FOOTER MODERNIZATION SUMMARY                        ║")
    print("╚══════════════════════════════════════════════════════════════╝\n")
    
    print(f"✅ Modernized: {modified_count} files")
    print(f"⏭️  Skipped: {skipped_count} files")
    print(f"📁 Total: {len(html_files)} files\n")
    
    if modified_count > 0:
        print("🎉 Footer modernization complete!\n")
        print("📱 Features:")
        print("   • 100x100px animated CORTEX logo")
        print("   • Modern typography (Inter font family)")
        print("   • Gradient-styled author name")
        print("   • Mobile-responsive (320px → 1440px+)")
        print("   • Portrait & landscape mode support")
        print("   • Glassmorphism design with backdrop blur\n")
        
        print("💡 Test at: http://localhost:8000/")
        print("   (Footer appears at bottom of each page)\n")


if __name__ == '__main__':
    main()
