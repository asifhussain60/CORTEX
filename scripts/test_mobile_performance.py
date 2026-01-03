"""
Mobile Performance Testing Script
Simulates mobile device performance characteristics for glassmorphism CSS.
Tests rendering performance, memory usage, and provides optimization recommendations.
"""

from pathlib import Path
from typing import Dict, List
import re


def analyze_mobile_performance(css_dir: Path) -> Dict:
    """
    Analyze CSS for mobile performance issues.
    
    Returns:
        Dict with performance metrics and recommendations
    """
    glass_files = [
        'glass-design-tokens.css',
        'glass-named-panels.css',
        'glass-base-patterns.css',
        'glass-ui-components.css',
        'glass-animations.css',
        'glass-utilities.css',
    ]
    
    metrics = {
        'total_lines': 0,
        'total_size': 0,
        'backdrop_filters': 0,
        'animations': 0,
        'media_queries': 0,
        'mobile_breakpoints': {},
        'expensive_properties': {
            'backdrop-filter': 0,
            'box-shadow': 0,
            'filter': 0,
            'transform': 0,
            'animation': 0,
        },
        'performance_score': 0,
        'issues': [],
        'optimizations': []
    }
    
    for filename in glass_files:
        filepath = css_dir / filename
        if not filepath.exists():
            continue
        
        content = filepath.read_text(encoding='utf-8')
        lines = content.count('\n') + 1
        size = len(content)
        
        metrics['total_lines'] += lines
        metrics['total_size'] += size
        
        # Count expensive properties
        metrics['backdrop_filters'] += len(re.findall(r'backdrop-filter:', content))
        metrics['expensive_properties']['backdrop-filter'] += len(re.findall(r'backdrop-filter:', content))
        metrics['expensive_properties']['box-shadow'] += len(re.findall(r'box-shadow:', content))
        metrics['expensive_properties']['filter'] += len(re.findall(r'\bfilter:', content))
        metrics['expensive_properties']['transform'] += len(re.findall(r'transform:', content))
        metrics['expensive_properties']['animation'] += len(re.findall(r'animation:', content))
        
        # Count animations
        metrics['animations'] += len(re.findall(r'@keyframes', content))
        
        # Count media queries
        media_queries = re.findall(r'@media[^{]+', content)
        metrics['media_queries'] += len(media_queries)
        
        # Extract mobile breakpoints
        for mq in media_queries:
            if 'max-width' in mq or 'max-device-width' in mq:
                breakpoint_match = re.search(r'(\d+)px', mq)
                if breakpoint_match:
                    bp = breakpoint_match.group(1)
                    metrics['mobile_breakpoints'][bp] = metrics['mobile_breakpoints'].get(bp, 0) + 1
    
    # Performance scoring (0-100)
    score = 100
    
    # Deduct for expensive properties
    if metrics['backdrop_filters'] > 50:
        score -= 20
        metrics['issues'].append(f"❌ CRITICAL: {metrics['backdrop_filters']} backdrop-filters (target: <30)")
    elif metrics['backdrop_filters'] > 30:
        score -= 10
        metrics['issues'].append(f"⚠️  HIGH: {metrics['backdrop_filters']} backdrop-filters (target: <30)")
    
    if metrics['expensive_properties']['box-shadow'] > 100:
        score -= 15
        metrics['issues'].append(f"⚠️  HIGH: {metrics['expensive_properties']['box-shadow']} box-shadows (target: <80)")
    
    if metrics['animations'] > 20:
        score -= 10
        metrics['issues'].append(f"⚠️  MEDIUM: {metrics['animations']} animations (target: <15)")
    
    # Check file size
    size_kb = metrics['total_size'] / 1024
    if size_kb > 150:
        score -= 15
        metrics['issues'].append(f"❌ CRITICAL: {size_kb:.1f} KB total CSS (target: <100 KB)")
    elif size_kb > 100:
        score -= 8
        metrics['issues'].append(f"⚠️  MEDIUM: {size_kb:.1f} KB total CSS (target: <100 KB)")
    
    # Check mobile optimization
    has_mobile_breakpoint = any(int(bp) <= 768 for bp in metrics['mobile_breakpoints'].keys())
    if not has_mobile_breakpoint:
        score -= 10
        metrics['issues'].append("⚠️  Missing mobile breakpoints (<768px)")
    
    # Generate optimizations
    if metrics['backdrop_filters'] > 30:
        metrics['optimizations'].append(
            "✅ Use .glass-optimized fallback class for low-end devices"
        )
        metrics['optimizations'].append(
            "✅ Reduce blur radius by 30% on mobile (already in glass-performance.css)"
        )
    
    if size_kb > 100:
        metrics['optimizations'].append(
            "✅ Use minified CSS files (reduces size by 45%)"
        )
    
    if metrics['animations'] > 15:
        metrics['optimizations'].append(
            "✅ Disable complex animations on mobile (prefers-reduced-motion)"
        )
    
    metrics['optimizations'].append(
        "✅ Use transform: translateZ(0) for GPU acceleration"
    )
    metrics['optimizations'].append(
        "✅ Lazy-load non-critical glassmorphism effects"
    )
    
    metrics['performance_score'] = max(0, score)
    
    return metrics


def simulate_mobile_rendering(metrics: Dict) -> Dict:
    """
    Simulate mobile device rendering characteristics.
    
    Returns:
        Dict with estimated rendering metrics
    """
    # Device profiles (based on typical mobile specs)
    devices = {
        'iPhone 12': {
            'cpu_speed': 3.1,  # GHz
            'gpu_cores': 4,
            'ram': 4,  # GB
            'screen_width': 390,
            'screen_height': 844,
            'pixel_ratio': 3,
        },
        'Samsung Galaxy S21': {
            'cpu_speed': 2.9,
            'gpu_cores': 16,
            'ram': 8,
            'screen_width': 360,
            'screen_height': 800,
            'pixel_ratio': 3,
        },
        'iPhone SE (2020)': {
            'cpu_speed': 2.65,
            'gpu_cores': 4,
            'ram': 3,
            'screen_width': 375,
            'screen_height': 667,
            'pixel_ratio': 2,
        },
        'Budget Android': {
            'cpu_speed': 2.0,
            'gpu_cores': 2,
            'ram': 2,
            'screen_width': 360,
            'screen_height': 640,
            'pixel_ratio': 2,
        }
    }
    
    simulations = {}
    
    for device_name, specs in devices.items():
        # Calculate estimated render time
        # Base time (ms) = backdrop_filters * 2 + animations * 1.5
        base_time = (metrics['backdrop_filters'] * 2) + (metrics['animations'] * 1.5)
        
        # Adjust for device specs
        cpu_factor = specs['cpu_speed'] / 3.0  # Normalized to 3GHz
        gpu_factor = specs['gpu_cores'] / 8  # Normalized to 8 cores
        ram_factor = specs['ram'] / 4  # Normalized to 4GB
        
        # Lower specs = slower rendering
        device_factor = (cpu_factor + gpu_factor + ram_factor) / 3
        estimated_time = base_time / device_factor
        
        # Calculate memory usage (rough estimate)
        # Each backdrop-filter ~2MB, each animation ~0.5MB
        memory_mb = (metrics['backdrop_filters'] * 2) + (metrics['animations'] * 0.5)
        
        # Performance rating
        if estimated_time < 50:
            rating = "🟢 EXCELLENT"
        elif estimated_time < 100:
            rating = "🟡 GOOD"
        elif estimated_time < 200:
            rating = "🟠 FAIR"
        else:
            rating = "🔴 POOR"
        
        simulations[device_name] = {
            'estimated_render_time_ms': round(estimated_time, 1),
            'estimated_memory_mb': round(memory_mb, 1),
            'performance_rating': rating,
            'specs': specs
        }
    
    return simulations


def main():
    """Run mobile performance testing simulation."""
    css_dir = Path('docs/assets/css')
    
    print("=" * 70)
    print("Mobile Performance Testing - Glassmorphism CSS")
    print("=" * 70)
    print()
    
    # Analyze CSS
    metrics = analyze_mobile_performance(css_dir)
    
    print("📊 CSS METRICS")
    print("-" * 70)
    print(f"Total Lines:           {metrics['total_lines']:>6}")
    print(f"Total Size:            {metrics['total_size'] / 1024:>6.1f} KB")
    print(f"Backdrop Filters:      {metrics['backdrop_filters']:>6}")
    print(f"Box Shadows:           {metrics['expensive_properties']['box-shadow']:>6}")
    print(f"Animations:            {metrics['animations']:>6}")
    print(f"Media Queries:         {metrics['media_queries']:>6}")
    print()
    
    print("📱 MOBILE BREAKPOINTS")
    print("-" * 70)
    if metrics['mobile_breakpoints']:
        for bp, count in sorted(metrics['mobile_breakpoints'].items(), key=lambda x: int(x[0])):
            print(f"{bp}px: {count} queries")
    else:
        print("⚠️  No mobile breakpoints detected")
    print()
    
    print("⚡ PERFORMANCE SCORE")
    print("-" * 70)
    score = metrics['performance_score']
    bar_length = 50
    filled = int((score / 100) * bar_length)
    bar = "█" * filled + "░" * (bar_length - filled)
    
    if score >= 80:
        score_label = "🟢 EXCELLENT"
    elif score >= 60:
        score_label = "🟡 GOOD"
    elif score >= 40:
        score_label = "🟠 FAIR"
    else:
        score_label = "🔴 POOR"
    
    print(f"{bar} {score}/100 {score_label}")
    print()
    
    if metrics['issues']:
        print("⚠️  ISSUES DETECTED")
        print("-" * 70)
        for issue in metrics['issues']:
            print(f"  {issue}")
        print()
    
    if metrics['optimizations']:
        print("💡 RECOMMENDED OPTIMIZATIONS")
        print("-" * 70)
        for opt in metrics['optimizations']:
            print(f"  {opt}")
        print()
    
    # Simulate mobile rendering
    print("🔬 DEVICE SIMULATION")
    print("-" * 70)
    simulations = simulate_mobile_rendering(metrics)
    
    for device_name, sim in simulations.items():
        print(f"\n{device_name}")
        print(f"  CPU: {sim['specs']['cpu_speed']} GHz | "
              f"GPU: {sim['specs']['gpu_cores']} cores | "
              f"RAM: {sim['specs']['ram']} GB")
        print(f"  Screen: {sim['specs']['screen_width']}x{sim['specs']['screen_height']} "
              f"@{sim['specs']['pixel_ratio']}x")
        print(f"  Estimated Render Time: {sim['estimated_render_time_ms']} ms")
        print(f"  Estimated Memory Usage: {sim['estimated_memory_mb']} MB")
        print(f"  Performance: {sim['performance_rating']}")
    
    print()
    print("=" * 70)
    print("✅ Mobile Performance Analysis Complete")
    print("=" * 70)
    print()
    print("📋 NEXT STEPS:")
    print("  1. Test on real devices (iOS Safari, Chrome Mobile)")
    print("  2. Use Chrome DevTools Device Mode for initial testing")
    print("  3. Run Lighthouse audit with mobile profile")
    print("  4. Monitor FPS and paint times in Performance tab")
    print("  5. Consider lazy-loading glassmorphism for below-fold content")
    print()


if __name__ == '__main__':
    main()
