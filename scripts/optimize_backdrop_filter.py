"""
Backdrop-Filter Performance Optimization Script
Analyzes and optimizes backdrop-filter usage for production deployment.
Adds performance hints and mobile optimizations.
"""

from pathlib import Path
from typing import Dict, List
import re


def analyze_backdrop_filters(css_dir: Path) -> Dict:
    """
    Analyze backdrop-filter usage across all CSS files.
    
    Returns:
        Dict with counts, locations, and optimization recommendations
    """
    glass_files = [
        'glass-design-tokens.css',
        'glass-named-panels.css',
        'glass-base-patterns.css',
        'glass-ui-components.css',
        'glass-animations.css',
        'glass-utilities.css',
    ]
    
    results = {
        'total_backdrop_filters': 0,
        'by_file': {},
        'blur_values': {},
        'has_will_change': 0,
        'has_webkit_prefix': 0,
        'has_reduced_motion': 0,
        'recommendations': []
    }
    
    for filename in glass_files:
        filepath = css_dir / filename
        if not filepath.exists():
            continue
        
        content = filepath.read_text(encoding='utf-8')
        
        # Count backdrop-filters
        backdrop_filters = re.findall(r'backdrop-filter:\s*([^;]+)', content)
        webkit_filters = re.findall(r'-webkit-backdrop-filter:', content)
        will_change = re.findall(r'will-change:', content)
        reduced_motion = re.findall(r'@media.*prefers-reduced-motion', content)
        
        # Extract blur values
        blur_values = re.findall(r'blur\(([^)]+)\)', content)
        
        results['by_file'][filename] = {
            'backdrop_filters': len(backdrop_filters),
            'webkit_prefixes': len(webkit_filters),
            'will_change': len(will_change),
        }
        
        results['total_backdrop_filters'] += len(backdrop_filters)
        results['has_webkit_prefix'] += len(webkit_filters)
        results['has_will_change'] += len(will_change)
        results['has_reduced_motion'] += len(reduced_motion)
        
        for blur in blur_values:
            results['blur_values'][blur] = results['blur_values'].get(blur, 0) + 1
    
    # Generate recommendations
    if results['total_backdrop_filters'] > 30:
        results['recommendations'].append(
            f"⚠️  HIGH: {results['total_backdrop_filters']} backdrop-filters detected. "
            "Consider using composite layers for frequent animations."
        )
    
    if results['has_webkit_prefix'] != results['total_backdrop_filters']:
        results['recommendations'].append(
            "⚠️  MISSING: Some backdrop-filters lack -webkit- prefix (Safari support)."
        )
    
    if results['has_will_change'] < 5:
        results['recommendations'].append(
            "✅ GOOD: Minimal will-change usage (avoids excessive layer creation)."
        )
    
    if results['has_reduced_motion'] > 0:
        results['recommendations'].append(
            f"✅ GOOD: {results['has_reduced_motion']} reduced-motion queries detected."
        )
    
    # Check for high blur values
    high_blur = [b for b in results['blur_values'].keys() if 'px' in b and int(b.replace('px', '')) > 25]
    if high_blur:
        results['recommendations'].append(
            f"⚠️  PERFORMANCE: High blur values detected ({', '.join(high_blur)}). "
            "Consider reducing blur radius on mobile devices."
        )
    
    return results


def generate_performance_css() -> str:
    """
    Generate performance optimization CSS for production.
    
    Returns:
        CSS string with performance hints
    """
    css = """/**
 * CORTEX Glassmorphism - Performance Optimizations
 * Auto-generated performance hints for production deployment.
 */

/* ============================================
   GPU ACCELERATION
   ============================================
   Force GPU acceleration for glassmorphism elements
   Reduces CPU rendering overhead for backdrop-filter
*/

.glass-card,
.glass-panel,
.panel-tetris,
.panel-intro,
.panel-compact-cards,
.panel-grid-cards,
.panel-hero-glass,
.panel-sidebar-glass,
.panel-modal-glass,
.panel-toast-glass,
.panel-neon-glass {
    /* Force GPU layer */
    transform: translateZ(0);
    /* Optimize rendering */
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

/* ============================================
   MOBILE OPTIMIZATION
   ============================================
   Reduce backdrop-filter intensity on mobile
   30% blur reduction improves performance
*/

@media (max-width: 768px) {
    :root {
        /* Reduce blur for mobile performance */
        --glass-blur-sm: 7px !important;   /* was 10px */
        --glass-blur-md: 14px !important;  /* was 20px */
        --glass-blur-lg: 21px !important;  /* was 30px */
    }
    
    /* Disable blob animations on mobile */
    .panel-blob-glass,
    .liquid-blob {
        animation: none;
    }
    
    /* Simplify shadows */
    .glass-card,
    .glass-panel,
    [class*="panel-"] {
        box-shadow: var(--shadow-glass-sm) !important;
    }
}

/* ============================================
   LOW-END DEVICE FALLBACK
   ============================================
   Detect low-performance devices and disable effects
   Uses media query for devices with reduced performance
*/

@media (prefers-reduced-motion: reduce) {
    /* Disable all backdrop-filters */
    * {
        backdrop-filter: none !important;
        -webkit-backdrop-filter: none !important;
    }
    
    /* Use solid backgrounds instead */
    .glass-card,
    .glass-panel,
    [class*="panel-"] {
        background: var(--glass-bg-fallback, rgba(10, 15, 30, 0.95)) !important;
    }
}

/* ============================================
   CONTAINMENT OPTIMIZATION
   ============================================
   Use CSS containment to isolate repaint areas
   Prevents full-page repaints on glass element changes
*/

.glass-card,
.glass-panel,
[class*="panel-"] {
    /* Isolate layout calculations */
    contain: layout style paint;
}

/* Modal/overlay should allow size changes */
.panel-modal-glass,
.glass-modal-overlay {
    contain: layout style;
}

/* ============================================
   COMPOSITOR HINTS
   ============================================
   Hint to browser compositor for optimized rendering
*/

.glass-hover-lift:hover,
.glass-card:hover,
[class*="panel-"]:hover {
    /* Prepare for animation */
    will-change: transform, box-shadow;
}

/* Remove hint after hover */
.glass-hover-lift,
.glass-card,
[class*="panel-"] {
    will-change: auto;
}

/* ============================================
   CRITICAL CSS LOADING
   ============================================
   Preload backdrop-filter support detection
*/

@supports (backdrop-filter: blur(10px)) {
    /* Browser supports backdrop-filter */
    .glass-supported {
        --glass-supported: 1;
    }
}

@supports not (backdrop-filter: blur(10px)) {
    /* Fallback for unsupported browsers */
    .glass-card,
    .glass-panel,
    [class*="panel-"] {
        background: var(--glass-bg-fallback, rgba(10, 15, 30, 0.95)) !important;
    }
}
"""
    return css


def main():
    """Run backdrop-filter performance analysis and optimization."""
    css_dir = Path('docs/assets/css')
    
    print("=" * 70)
    print("Backdrop-Filter Performance Analysis")
    print("=" * 70)
    print()
    
    # Analyze current usage
    results = analyze_backdrop_filters(css_dir)
    
    print("📊 USAGE STATISTICS")
    print("-" * 70)
    print(f"Total backdrop-filters:    {results['total_backdrop_filters']}")
    print(f"WebKit prefixes:           {results['has_webkit_prefix']}")
    print(f"will-change declarations:  {results['has_will_change']}")
    print(f"Reduced-motion queries:    {results['has_reduced_motion']}")
    print()
    
    print("📁 BY FILE")
    print("-" * 70)
    for filename, stats in results['by_file'].items():
        print(f"{filename:30} {stats['backdrop_filters']:2} filters, "
              f"{stats['webkit_prefixes']:2} webkit, {stats['will_change']:2} will-change")
    print()
    
    print("🎨 BLUR VALUES")
    print("-" * 70)
    for blur, count in sorted(results['blur_values'].items(), key=lambda x: x[1], reverse=True):
        print(f"{blur:20} {count:3} occurrences")
    print()
    
    print("💡 RECOMMENDATIONS")
    print("-" * 70)
    for rec in results['recommendations']:
        print(f"  {rec}")
    print()
    
    # Generate performance CSS
    perf_css = generate_performance_css()
    output_path = css_dir / 'glass-performance.css'
    output_path.write_text(perf_css, encoding='utf-8')
    
    print("✅ OPTIMIZATION FILE CREATED")
    print("-" * 70)
    print(f"📁 {output_path}")
    print(f"📏 {len(perf_css)} bytes ({len(perf_css.splitlines())} lines)")
    print()
    
    print("🚀 NEXT STEPS")
    print("-" * 70)
    print("1. Import glass-performance.css AFTER cortex-glass-system.css")
    print("2. Test on mobile devices (iOS Safari, Chrome Mobile)")
    print("3. Run Lighthouse performance audit")
    print("4. Validate with Chrome DevTools Performance monitor")
    print()


if __name__ == '__main__':
    main()
