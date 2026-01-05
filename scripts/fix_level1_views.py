#!/usr/bin/env python3
"""
Fix Level 1 Views - Remove duplicate logos, remove footers, ensure mobile responsiveness.

Level 1 Views (Hub Pages):
- docs/architecture/index.html
- docs/features/index.html
- docs/getting-started/index.html
- docs/knowledge/index.html
- docs/learning-paths/index.html
- docs/lens/index.html
- docs/orchestrators/index.html
- docs/security/index.html
- docs/sts/index.html
- docs/token-optimization/index.html
- docs/toolkit-manager/index.html
"""

import re
from pathlib import Path

# Define Level 1 hub pages
LEVEL1_VIEWS = [
    "docs/architecture/index.html",
    "docs/features/index.html",
    "docs/getting-started/index.html",
    "docs/knowledge/index.html",
    "docs/learning-paths/index.html",
    "docs/lens/index.html",
    "docs/orchestrators/index.html",
    "docs/security/index.html",
    "docs/sts/index.html",
    "docs/token-optimization/index.html",
    "docs/toolkit-manager/index.html",
]

def remove_duplicate_logos(html_content: str, file_path: str) -> tuple[str, list[str]]:
    """
    Remove duplicate CORTEX logos from hero sections.
    Keep only navigation bar logo, remove hero section duplicates.
    """
    changes = []
    
    # Pattern 1: Remove hero-robot-head logo (duplicate in hero section)
    hero_robot_pattern = r'<img\s+src="[^"]*CORTEX-logo[^"]*"\s+alt="CORTEX Robot"\s+class="hero-robot-head"\s*/>'
    if re.search(hero_robot_pattern, html_content):
        html_content = re.sub(hero_robot_pattern, '', html_content)
        changes.append(f"Removed hero-robot-head logo from {file_path}")
    
    # Pattern 2: Remove standalone hero logo in Level 1 views (not in navigation)
    # Match logo inside hero sections but NOT in navigation
    hero_logo_pattern = r'<div[^>]*class="[^"]*hero[^"]*"[^>]*>[\s\S]*?<img[^>]*class="level1-hero-logo[^"]*"[^>]*>[\s\S]*?</div>'
    if re.search(hero_logo_pattern, html_content):
        # Replace the logo with empty string but keep the container
        html_content = re.sub(
            r'<img[^>]*class="level1-hero-logo[^"]*"[^>]*>',
            '',
            html_content
        )
        changes.append(f"Removed level1-hero-logo from {file_path}")
    
    return html_content, changes

def remove_footer(html_content: str, file_path: str) -> tuple[str, list[str]]:
    """
    Remove footer from Level 1 hub pages.
    """
    changes = []
    
    # Pattern 1: Footer with comment tags
    footer_pattern1 = r'<!--\s*Modern Glass Footer\s*-->[\s\S]*?<footer[^>]*>[\s\S]*?</footer>'
    if re.search(footer_pattern1, html_content):
        html_content = re.sub(footer_pattern1, '', html_content)
        changes.append(f"Removed footer (with comment) from {file_path}")
        return html_content, changes
    
    # Pattern 2: Footer with class="glass-footer-modern"
    footer_pattern2 = r'<footer\s+class="glass-footer-modern"[\s\S]*?</footer>'
    if re.search(footer_pattern2, html_content):
        html_content = re.sub(footer_pattern2, '', html_content)
        changes.append(f"Removed glass-footer-modern from {file_path}")
        return html_content, changes
    
    # Pattern 3: Plain footer tag
    footer_pattern3 = r'<footer[^>]*>[\s\S]*?</footer>'
    if re.search(footer_pattern3, html_content):
        html_content = re.sub(footer_pattern3, '', html_content)
        changes.append(f"Removed plain footer from {file_path}")
    
    return html_content, changes

def ensure_mobile_meta_tags(html_content: str, file_path: str) -> tuple[str, list[str]]:
    """
    Ensure mobile-friendly meta tags are present.
    """
    changes = []
    
    # Check for viewport meta tag
    if 'name="viewport"' not in html_content:
        # Find <head> tag and insert viewport meta
        head_pattern = r'(<head[^>]*>)'
        viewport_meta = r'\1\n<meta name="viewport" content="width=device-width, initial-scale=1.0">'
        html_content = re.sub(head_pattern, viewport_meta, html_content)
        changes.append(f"Added viewport meta tag to {file_path}")
    
    # Check for mobile optimization styles
    if '-webkit-text-size-adjust' not in html_content:
        # Find <head> and add mobile font optimization
        head_end = html_content.find('</head>')
        if head_end != -1:
            mobile_styles = """
<style>
/* Mobile font optimization */
html {
    -webkit-text-size-adjust: 100%;
    -moz-text-size-adjust: 100%;
    text-size-adjust: 100%;
}
</style>
"""
            html_content = html_content[:head_end] + mobile_styles + html_content[head_end:]
            changes.append(f"Added mobile font optimization to {file_path}")
    
    return html_content, changes

def process_file(file_path: Path) -> list[str]:
    """
    Process a single Level 1 view file.
    """
    if not file_path.exists():
        return [f"⚠️  File not found: {file_path}"]
    
    try:
        html_content = file_path.read_text(encoding='utf-8')
        original_content = html_content
        all_changes = []
        
        # Step 1: Remove duplicate logos
        html_content, logo_changes = remove_duplicate_logos(html_content, str(file_path))
        all_changes.extend(logo_changes)
        
        # Step 2: Remove footer
        html_content, footer_changes = remove_footer(html_content, str(file_path))
        all_changes.extend(footer_changes)
        
        # Step 3: Ensure mobile responsiveness
        html_content, mobile_changes = ensure_mobile_meta_tags(html_content, str(file_path))
        all_changes.extend(mobile_changes)
        
        # Write back if changes were made
        if html_content != original_content:
            file_path.write_text(html_content, encoding='utf-8')
            return all_changes if all_changes else [f"✅ Processed {file_path} (no changes needed)"]
        else:
            return [f"✅ {file_path} - Already compliant"]
    
    except Exception as e:
        return [f"❌ Error processing {file_path}: {e}"]

def main():
    """
    Main execution function.
    """
    print("🛡️ CORTEX Level 1 View Fixer")
    print("=" * 60)
    print("\n📋 Processing Level 1 Hub Pages...")
    print(f"   Total files: {len(LEVEL1_VIEWS)}\n")
    
    base_dir = Path(__file__).parent.parent
    total_changes = 0
    
    for view_path in LEVEL1_VIEWS:
        full_path = base_dir / view_path
        print(f"\n🔍 {view_path}")
        
        changes = process_file(full_path)
        for change in changes:
            print(f"   {change}")
            if not change.startswith("✅") and not change.startswith("⚠️") and not change.startswith("❌"):
                total_changes += 1
    
    print("\n" + "=" * 60)
    print(f"✅ Complete! Total changes: {total_changes}")
    print("\n📊 Summary:")
    print("   - Duplicate logos removed")
    print("   - Footers removed from Level 1 views")
    print("   - Mobile responsiveness ensured")
    print("\n🔍 Recommendation: Test each view for mobile responsiveness")

if __name__ == "__main__":
    main()
