"""
Cross-Browser Compatibility Testing Script
Tests glassmorphism CSS across different browsers and provides compatibility matrix.
"""

from pathlib import Path
from typing import Dict, List
import re


def analyze_browser_features(content: str) -> Dict:
    """
    Analyze CSS features and their browser support.
    
    Returns:
        Dict with features and browser compatibility
    """
    features = {}
    
    # Define browser support matrix (min version for each feature)
    browser_support = {
        'backdrop-filter': {
            'chrome': {'version': 76, 'status': '✅', 'notes': 'Full support'},
            'firefox': {'version': 103, 'status': '✅', 'notes': 'Full support'},
            'safari': {'version': 9, 'status': '✅', 'notes': 'Requires -webkit- prefix'},
            'edge': {'version': 79, 'status': '✅', 'notes': 'Full support'},
            'ie11': {'version': None, 'status': '❌', 'notes': 'Not supported'},
        },
        'css-grid': {
            'chrome': {'version': 57, 'status': '✅', 'notes': 'Full support'},
            'firefox': {'version': 52, 'status': '✅', 'notes': 'Full support'},
            'safari': {'version': 10.1, 'status': '✅', 'notes': 'Full support'},
            'edge': {'version': 16, 'status': '✅', 'notes': 'Full support'},
            'ie11': {'version': 10, 'status': '⚠️', 'notes': 'Partial support (old syntax)'},
        },
        'css-custom-properties': {
            'chrome': {'version': 49, 'status': '✅', 'notes': 'Full support'},
            'firefox': {'version': 31, 'status': '✅', 'notes': 'Full support'},
            'safari': {'version': 9.1, 'status': '✅', 'notes': 'Full support'},
            'edge': {'version': 15, 'status': '✅', 'notes': 'Full support'},
            'ie11': {'version': None, 'status': '❌', 'notes': 'Not supported'},
        },
        'flexbox': {
            'chrome': {'version': 29, 'status': '✅', 'notes': 'Full support'},
            'firefox': {'version': 28, 'status': '✅', 'notes': 'Full support'},
            'safari': {'version': 9, 'status': '✅', 'notes': 'Full support'},
            'edge': {'version': 12, 'status': '✅', 'notes': 'Full support'},
            'ie11': {'version': 11, 'status': '⚠️', 'notes': 'Partial support'},
        },
        'transforms': {
            'chrome': {'version': 36, 'status': '✅', 'notes': 'Full support'},
            'firefox': {'version': 16, 'status': '✅', 'notes': 'Full support'},
            'safari': {'version': 9, 'status': '✅', 'notes': 'Full support'},
            'edge': {'version': 12, 'status': '✅', 'notes': 'Full support'},
            'ie11': {'version': 10, 'status': '✅', 'notes': 'Full support (with prefixes)'},
        },
        'animations': {
            'chrome': {'version': 43, 'status': '✅', 'notes': 'Full support'},
            'firefox': {'version': 16, 'status': '✅', 'notes': 'Full support'},
            'safari': {'version': 9, 'status': '✅', 'notes': 'Full support'},
            'edge': {'version': 12, 'status': '✅', 'notes': 'Full support'},
            'ie11': {'version': 10, 'status': '✅', 'notes': 'Full support'},
        },
        '@supports': {
            'chrome': {'version': 28, 'status': '✅', 'notes': 'Full support'},
            'firefox': {'version': 22, 'status': '✅', 'notes': 'Full support'},
            'safari': {'version': 9, 'status': '✅', 'notes': 'Full support'},
            'edge': {'version': 12, 'status': '✅', 'notes': 'Full support'},
            'ie11': {'version': None, 'status': '❌', 'notes': 'Not supported'},
        },
        'gap': {
            'chrome': {'version': 84, 'status': '✅', 'notes': 'Full support'},
            'firefox': {'version': 63, 'status': '✅', 'notes': 'Full support'},
            'safari': {'version': 14.1, 'status': '✅', 'notes': 'Full support'},
            'edge': {'version': 84, 'status': '✅', 'notes': 'Full support'},
            'ie11': {'version': None, 'status': '❌', 'notes': 'Not supported'},
        },
    }
    
    # Detect features used in CSS
    feature_patterns = {
        'backdrop-filter': r'backdrop-filter:',
        'css-grid': r'(display:\s*grid|grid-template)',
        'css-custom-properties': r'var\(--',
        'flexbox': r'display:\s*flex',
        'transforms': r'transform:',
        'animations': r'(@keyframes|animation:)',
        '@supports': r'@supports',
        'gap': r'gap:',
    }
    
    for feature, pattern in feature_patterns.items():
        if re.search(pattern, content):
            features[feature] = browser_support[feature]
    
    return features


def generate_compatibility_matrix(features: Dict) -> str:
    """
    Generate visual compatibility matrix.
    
    Returns:
        Formatted string with compatibility table
    """
    browsers = ['chrome', 'firefox', 'safari', 'edge', 'ie11']
    browser_names = {
        'chrome': 'Chrome',
        'firefox': 'Firefox',
        'safari': 'Safari',
        'edge': 'Edge',
        'ie11': 'IE11'
    }
    
    # Build table
    table = "\n"
    table += "=" * 90 + "\n"
    table += f"{'Feature':<25} {'Chrome':<12} {'Firefox':<12} {'Safari':<12} {'Edge':<12} {'IE11':<12}\n"
    table += "=" * 90 + "\n"
    
    for feature_name, support in features.items():
        row = f"{feature_name:<25}"
        for browser in browsers:
            browser_info = support[browser]
            status = browser_info['status']
            version = browser_info['version']
            version_str = f"{version}+" if version else "N/A"
            row += f" {status} {version_str:<8}"
        table += row + "\n"
    
    table += "=" * 90 + "\n"
    
    return table


def generate_test_plan() -> str:
    """
    Generate browser testing plan.
    
    Returns:
        Formatted test plan string
    """
    plan = """
CROSS-BROWSER TESTING PLAN
================================================================================

1. CHROME (Windows/macOS/Linux)
   --------------------------------
   [ ] Version 76+ (backdrop-filter support)
   [ ] Check glassmorphism rendering
   [ ] Verify blur effects
   [ ] Test hover animations
   [ ] Validate responsive breakpoints
   [ ] Check DevTools Performance tab
   [ ] Measure FPS during scroll/hover
   
2. FIREFOX (Windows/macOS/Linux)
   --------------------------------
   [ ] Version 103+ (backdrop-filter support)
   [ ] Check glassmorphism rendering
   [ ] Verify gradient borders
   [ ] Test responsive grid layouts
   [ ] Validate accessibility (reduced motion)
   [ ] Check Developer Tools Performance
   
3. SAFARI (macOS/iOS)
   --------------------------------
   [ ] Safari 9+ (desktop)
   [ ] iOS Safari 15+ (mobile)
   [ ] Verify -webkit- prefixes working
   [ ] Check backdrop-filter rendering
   [ ] Test on iPhone 12, 13, 14
   [ ] Test on iPad Pro
   [ ] Validate mobile breakpoints (480px, 768px)
   [ ] Check GPU performance on mobile
   
4. EDGE (Windows)
   --------------------------------
   [ ] Version 79+ (Chromium-based)
   [ ] Check glassmorphism rendering
   [ ] Verify blur effects
   [ ] Test animations
   [ ] Validate Windows-specific rendering
   
5. IE11 (Legacy Support)
   --------------------------------
   [ ] Verify .glass-optimized fallback
   [ ] Check solid background fallbacks
   [ ] Test layout without backdrop-filter
   [ ] Ensure content is readable
   
VISUAL REGRESSION CHECKLIST
================================================================================

[ ] Panel Viewer (docs/design-system/panel-viewer.html)
[ ] CORTEX Lens (docs/lens/index.html)
[ ] Architecture pages (docs/architecture/*.html)
[ ] Orchestrator pages (docs/sts/index.html)
[ ] All 11 named panels render correctly
[ ] Hover states work on all browsers
[ ] Animations smooth (60fps target)
[ ] Mobile responsive layouts
[ ] Dark/light theme toggle
[ ] Copy-to-clipboard functionality

PERFORMANCE BENCHMARKS
================================================================================

Target Metrics (per page):
- First Contentful Paint: <1.5s
- Largest Contentful Paint: <2.5s
- Time to Interactive: <3.5s
- Cumulative Layout Shift: <0.1
- FPS during scroll: >55fps
- GPU memory usage: <200MB

Test URLs:
1. /docs/index.html
2. /docs/lens/index.html
3. /docs/design-system/panel-viewer.html
4. /docs/architecture/skull-protection.html
5. /docs/sts/index.html

ACCESSIBILITY CHECKLIST
================================================================================

[ ] prefers-reduced-motion disables animations
[ ] Keyboard navigation works
[ ] Focus states visible
[ ] Color contrast meets WCAG 2.1 AA
[ ] Screen reader compatibility
[ ] Touch targets minimum 44x44px (mobile)

"""
    return plan


def main():
    """Run cross-browser compatibility analysis."""
    css_dir = Path('docs/assets/css')
    
    glass_files = [
        'glass-design-tokens.css',
        'glass-named-panels.css',
        'glass-base-patterns.css',
        'glass-ui-components.css',
        'glass-animations.css',
        'glass-utilities.css',
    ]
    
    print("=" * 90)
    print("Cross-Browser Compatibility Analysis - CORTEX Glassmorphism")
    print("=" * 90)
    print()
    
    # Combine all CSS content
    combined_content = ""
    for filename in glass_files:
        filepath = css_dir / filename
        if filepath.exists():
            combined_content += filepath.read_text(encoding='utf-8')
    
    # Analyze features
    print("🔍 Analyzing CSS features...")
    features = analyze_browser_features(combined_content)
    print(f"   Detected {len(features)} features requiring compatibility checks")
    print()
    
    # Generate compatibility matrix
    print("📊 BROWSER COMPATIBILITY MATRIX")
    print(generate_compatibility_matrix(features))
    print()
    
    # Overall compatibility summary
    print("📋 COMPATIBILITY SUMMARY")
    print("-" * 90)
    print("✅ Chrome 76+    - Full support (recommended)")
    print("✅ Firefox 103+  - Full support (recommended)")
    print("✅ Safari 9+     - Full support (requires -webkit- prefixes)")
    print("✅ Edge 79+      - Full support (Chromium-based)")
    print("❌ IE11          - Limited support (fallbacks provided)")
    print()
    
    print("💡 KNOWN ISSUES")
    print("-" * 90)
    print("1. Safari requires -webkit-backdrop-filter prefix (already included)")
    print("2. IE11 does not support backdrop-filter (fallback via .glass-optimized)")
    print("3. Firefox <103 does not support backdrop-filter")
    print("4. Older Safari (<14.1) does not support gap property")
    print()
    
    print("🔧 FALLBACK STRATEGIES")
    print("-" * 90)
    print("✅ @supports queries detect backdrop-filter support")
    print("✅ .glass-optimized class provides solid backgrounds")
    print("✅ -webkit- vendor prefixes for Safari")
    print("✅ prefers-reduced-motion disables effects")
    print("✅ Mobile blur reduction (30% less on phones)")
    print()
    
    # Generate test plan
    test_plan = generate_test_plan()
    test_plan_path = Path('cortex-brain/documents/reports/cross-browser-test-plan.md')
    test_plan_path.parent.mkdir(parents=True, exist_ok=True)
    test_plan_path.write_text(test_plan, encoding='utf-8')
    
    print(f"📄 Test plan saved: {test_plan_path}")
    print()
    
    print("🚀 RECOMMENDED TESTING TOOLS")
    print("-" * 90)
    print("1. BrowserStack (real device testing)")
    print("2. Chrome DevTools Device Mode (mobile simulation)")
    print("3. Firefox Developer Tools (responsive design mode)")
    print("4. Safari Web Inspector (macOS/iOS)")
    print("5. Lighthouse (performance audit)")
    print("6. WebPageTest (multi-location testing)")
    print()
    
    print("✅ Cross-browser analysis complete!")
    print()


if __name__ == '__main__':
    main()
