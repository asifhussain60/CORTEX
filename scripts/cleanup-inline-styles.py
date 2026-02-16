"""
CORTEX Inline Styles Cleanup Script
Removes all inline style attributes and replaces with CSS classes
"""

import re
from pathlib import Path

# Define mappings from inline styles to CSS classes
STYLE_MAPPINGS = [
    # Z-index layering
    (r' style="position: relative; z-index: 2;"', ' class="z-layer-2"'),
    (r' style="position: relative; z-index: 3;"', ' class="z-layer-3"'),
    
    # Flexbox patterns
    (r' style="display: flex; flex-direction: column; min-height: 420px;"', ' class="flex-column level0-content-card"'),
    (r' style="display: flex; flex-direction: column; height: 100%;"', ' class="flex-column-stretch"'),
    (r' style="display: flex; flex-direction: column; height: 100%; min-height: 180px;"', ' class="flex-column bwc-stat"'),
    (r' style="display: flex; flex-direction: column; align-items: center; height: 100%; padding-bottom: 0.5rem;"', ' class="flex-column sts-category-item"'),
    (r' style="flex: 1; position: relative; z-index: 2;"', ' class="flex-1 z-layer-2"'),
    (r' style="flex: 1; margin-bottom: 0.5rem; position: relative; z-index: 2;"', ' class="flex-1 z-layer-2"'),
    (r' style="flex: 1; text-align: justify;"', ' class="flex-1 text-justify bwc-panel-description"'),
    
    # Grid layouts
    (r' style="display: grid; grid-template-columns: repeat\(2, 1fr\); gap: 2rem; align-items: stretch;"', ' class="feature-grid-2"'),
    (r' style="display: grid; grid-template-columns: repeat\(2, 1fr\); gap: 1.5rem; align-items: stretch;"', ' class="bwc-dual-panels"'),
    (r' style="display: grid; grid-template-columns: repeat\(4, 1fr\); gap: 1.5rem; align-items: stretch;"', ' class="bwc-stats"'),
    (r' style="display: grid; grid-template-columns: repeat\(3, 1fr\); gap: 1.5rem; align-items: stretch;"', ' class="orchestrator-cards-grid"'),
    (r' style="display: grid; grid-template-columns: repeat\(3, 1fr\); gap: 1rem; align-items: stretch;"', ' class="sts-categories-row"'),
    
    # Text alignment
    (r' style="justify-content: center; text-align: center;"', ' class="bwc-panel-header"'),
    (r' style="text-align: center;"', ' class="text-center bwc-panel-subtitle"'),
    
    # Margins and padding
    (r' style="margin-top: auto; padding-bottom: 0; position: relative; z-index: 2;"', ' class="category-tags z-layer-2"'),
    (r' style="margin-top: auto;"', ' class="margin-top-auto"'),
    (r' style="padding-bottom: 0;"', ' class="main-panel-wrapper-no-padding"'),
    
    # BWC stats
    (r' style="margin-top: auto;"', ' class="bwc-panel-stats"'),
    (r' style="border: 1px solid rgba\(0, 200, 255, 0.3\); border-radius: 8px; padding: 0.75rem;"', ' class="bwc-mini-stat"'),
    (r' style="border: 1px solid rgba\(138, 43, 226, 0.3\); border-radius: 8px; padding: 0.75rem;"', ' class="bwc-mini-stat"'),
    
    # Soon badges
    (r'<sup style="color:#7b61ff;font-size:0.7em;margin-left:4px">soon</sup>', '<sup class="badge-soon">soon</sup>'),
    (r'<sup style="color:#7b61ff;font-size:0.6em">SOON</sup>', '<sup class="badge-soon-small">SOON</sup>'),
    
    # Orchestrator cards (must come BEFORE individual class patterns)
    (r'<div class="glass-card-clickable orchestrator-card ([^"]+)" style="display: flex; flex-direction: column; height: 100%; padding-bottom: 1rem;">', 
     r'<div class="glass-card-clickable orchestrator-card \1">'),
    
    # E2E Demo section
    (r'<div style="display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 400px; background: var\(--glass-bg-base\); border-radius: 12px; border: 1px solid var\(--glass-border-subtle\); padding: 2rem;">', 
     r'<div class="e2e-demo-placeholder">'),
    (r'<svg style="width: 64px; height: 64px; color: var\(--accent-cyan\); margin-bottom: 1rem;"', 
     r'<svg class="e2e-demo-icon"'),
    (r'<h3 style="color: var\(--text-primary\); margin: 0 0 0\.5rem 0; font-size: 1\.25rem;">', 
     r'<h3 class="e2e-demo-title">'),
    (r'<p style="color: var\(--text-secondary\); margin: 0 0 1rem 0; text-align: center; max-width: 400px;">', 
     r'<p class="e2e-demo-description">'),
    (r'<p style="color: var\(--text-muted\); font-size: 0\.875rem; font-style: italic;">', 
     r'<p class="e2e-demo-note">'),
]

def clean_inline_styles(html_path: Path):
    """Remove inline styles and replace with CSS classes"""
    
    content = html_path.read_text(encoding='utf-8')
    original_content = content
    
    # Apply all mappings
    replacements = 0
    for pattern, replacement in STYLE_MAPPINGS:
        matches = re.findall(pattern, content)
        if matches:
            content = re.sub(pattern, replacement, content)
            replacements += len(matches)
            print(f"✅ Replaced {len(matches)} instances: {pattern[:50]}...")
    
    # Write back if changes made
    if content != original_content:
        html_path.write_text(content, encoding='utf-8')
        print(f"\n✅ {html_path.name}: {replacements} inline styles removed")
        return replacements
    else:
        print(f"⚠️ {html_path.name}: No changes made")
        return 0

if __name__ == "__main__":
    html_files = [
        Path("d:/PROJECTS/CORTEX/cortex-docs/index.html"),
        Path("d:/PROJECTS/CORTEX/cortex-docs/coming-soon.html"),
        Path("d:/PROJECTS/CORTEX/cortex-docs/api/index.html"),
    ]
    
    total_removed = 0
    for html_file in html_files:
        if html_file.exists():
            removed = clean_inline_styles(html_file)
            total_removed += removed
    
    print(f"\n🎯 TOTAL: {total_removed} inline styles removed across all files")
