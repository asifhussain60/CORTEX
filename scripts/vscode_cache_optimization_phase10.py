"""
VSCode Cache Optimization for Phase 10 Integration Testing
"""

import sys
import os
from pathlib import Path

# Add src to path
workspace = Path(__file__).parent.parent
sys.path.insert(0, str(workspace / "src"))

from operations.utilities.vscode_cache_manager import VSCodeCacheManager
import json


def main():
    print("🧹 Phase 10: VSCode Cache Optimization")
    print("=" * 80)
    
    # Initialize cache manager
    cache_mgr = VSCodeCacheManager()
    
    # Execute pre-flight optimization
    print("\n🔍 Running pre-flight cache optimization...")
    result = cache_mgr.pre_flight_optimize(
        dry_run=False,
        log_metrics=True,
        fail_silently=True
    )
    
    # Display results
    print("\n📊 Cache Optimization Results:")
    print("=" * 80)
    
    if result.get('success'):
        if result.get('skipped'):
            print(f"⏭️ Optimization skipped: {result.get('reason', 'Unknown')}")
            if 'current_size_mb' in result:
                print(f"   Current size: {result['current_size_mb']:.2f} MB")
                print(f"   Threshold: {result['threshold_mb']:.2f} MB")
        else:
            freed_mb = result.get('freed_mb', 0)
            if 'cache_cleared' in result:
                for cache_name, cache_result in result['cache_cleared'].items():
                    print(f"✅ {cache_name}:")
                    print(f"   Before: {cache_result.get('before_mb', 0):.2f} MB")
                    print(f"   After: {cache_result.get('after_mb', 0):.2f} MB")
                    print(f"   Freed: {cache_result.get('freed_mb', 0):.2f} MB")
            else:
                print(f"✅ Pre-flight cache optimization: {freed_mb:.2f} MB freed")
            
            print(f"\n⏱️ Duration: {result.get('duration_ms', 0)} ms")
    else:
        print(f"⚠️ Cache optimization failed: {result.get('error', 'Unknown')}")
    
    # Health check
    print("\n🏥 Running health check...")
    health = cache_mgr.health_check()
    
    print(f"\nCache Health Status: {health.get('status', 'Unknown')}")
    print(f"Total Cache Size: {health.get('total_mb', 0):.2f} MB")
    
    if 'caches' in health:
        print("\nCache Breakdown:")
        for cache_name, cache_info in health['caches'].items():
            size = cache_info.get('size_mb', 0)
            exists = cache_info.get('exists', False)
            status_icon = "✅" if exists else "⏭️"
            print(f"  {status_icon} {cache_name}: {size:.2f} MB")
    
    # Recommendation handling
    if 'recommendations' in health:
        print("\n💡 Recommendations:")
        for rec in health['recommendations']:
            print(f"  • {rec}")
    
    # Save results
    reports_dir = workspace / "cortex-brain" / "documents" / "planning" / "active" / "html-glassmorphism-alignment" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = reports_dir / "vscode-cache-optimization-log.json"
    with open(output_file, 'w') as f:
        json.dump({
            "optimization_result": result,
            "health_check": health
        }, f, indent=2)
    
    print(f"\n📝 Results saved to: {output_file.relative_to(workspace)}")
    print("\n✅ VSCode cache optimization complete!")


if __name__ == "__main__":
    main()
