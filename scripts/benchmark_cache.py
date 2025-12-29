"""
Quick benchmark script to measure cache performance with real brain-protection-rules.yaml.
"""

import sys
from pathlib import Path
import time

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.tier0.brain_protection_loader import (
    load_brain_protection_rules,
    get_cache_stats,
    clear_cache,
    reset_cache_stats
)

def benchmark():
    print("\n" + "="*60)
    print("CACHE PERFORMANCE BENCHMARK")
    print("="*60)
    
    rules_path = project_root / "cortex-brain" / "brain-protection-rules.yaml"
    
    if not rules_path.exists():
        print(f"\nERROR: Rules file not found: {rules_path}")
        return
    
    # Cold cache
    clear_cache()
    reset_cache_stats()
    
    print(f"\nRules file: {rules_path}")
    print(f"File size: {rules_path.stat().st_size / 1024:.2f} KB")
    
    start = time.perf_counter()
    load_brain_protection_rules(rules_path=rules_path)
    cold_time = time.perf_counter() - start
    
    print(f"\nCold Cache (First Load):")
    print(f"  Time: {cold_time*1000:.2f}ms")
    
    # Warm cache (10 runs)
    warm_times = []
    for i in range(10):
        start = time.perf_counter()
        load_brain_protection_rules(rules_path=rules_path)
        warm_times.append(time.perf_counter() - start)
    
    avg_warm = sum(warm_times) / len(warm_times)
    min_warm = min(warm_times)
    max_warm = max(warm_times)
    
    print(f"\nWarm Cache (10 Loads):")
    print(f"  Average: {avg_warm*1000:.2f}ms")
    print(f"  Min: {min_warm*1000:.2f}ms")
    print(f"  Max: {max_warm*1000:.2f}ms")
    
    # Calculate improvement
    improvement = ((cold_time - avg_warm) / cold_time) * 100
    speedup = cold_time / avg_warm
    
    print(f"\nImprovement:")
    print(f"  Reduction: {improvement:.1f}%")
    print(f"  Speedup: {speedup:.1f}x faster")
    
    # Session savings
    without_cache_100 = 100 * cold_time
    with_cache_100 = cold_time + (99 * avg_warm)
    saved_100 = without_cache_100 - with_cache_100
    
    print(f"\n100-Operation Session:")
    print(f"  Without cache: {without_cache_100*1000:.0f}ms ({without_cache_100:.2f}s)")
    print(f"  With cache: {with_cache_100*1000:.0f}ms ({with_cache_100:.2f}s)")
    print(f"  Time saved: {saved_100*1000:.0f}ms ({saved_100:.2f}s)")
    print(f"  Improvement: {(saved_100/without_cache_100)*100:.1f}%")
    
    # Cache stats
    stats = get_cache_stats()
    print(f"\nCache Statistics:")
    print(f"  Hits: {stats['hits']}")
    print(f"  Misses: {stats['misses']}")
    print(f"  Hit Rate: {stats['hit_rate']:.1f}%")
    
    print("="*60)
    
    # Validation
    print("\nValidation:")
    if improvement > 90.0:
        print(f"  ✅ Improvement {improvement:.1f}% exceeds target 90%")
    else:
        print(f"  ❌ Improvement {improvement:.1f}% below target 90%")
    
    if avg_warm < 0.005:
        print(f"  ✅ Average warm time {avg_warm*1000:.2f}ms under target 5ms")
    else:
        print(f"  ❌ Average warm time {avg_warm*1000:.2f}ms exceeds target 5ms")

if __name__ == "__main__":
    benchmark()
