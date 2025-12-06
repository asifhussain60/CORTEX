#!/usr/bin/env python
"""
CLI wrapper for CORTEX test generation.

Usage:
    python generate_tests.py all                 # Generate all tests
    python generate_tests.py orchestrators       # Generate tests for category
    python generate_tests.py orchestrators 5     # Generate 5 tests for category
    python generate_tests.py --stats             # Show generation statistics
"""

import sys
import os
from pathlib import Path

# Add CORTEX root to path
cortex_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(cortex_root))

from src.test_discovery.test_generator import TestGenerationEngine


def print_banner():
    """Print CORTEX test generation banner."""
    print("=" * 60)
    print("🧪 CORTEX Test Generation Engine")
    print("=" * 60)
    print()


def print_stats(engine: TestGenerationEngine):
    """Print generation statistics."""
    stats = engine.get_generation_stats()
    
    print("\n📊 Generation Statistics")
    print("-" * 60)
    print(f"Total Components: {stats['total_components']}")
    print(f"Total Tested: {stats['total_tested']}")
    print(f"Total Generated: {stats['total_generated']}")
    print(f"Coverage: {stats['coverage_percentage']:.1f}%")
    print()
    
    print("By Category:")
    for category, data in stats['categories'].items():
        coverage = (data['tested'] / data['discovered'] * 100) if data['discovered'] > 0 else 0
        print(f"  {category:20s} {data['tested']:3d}/{data['discovered']:3d} ({coverage:5.1f}%) - {data['untested']:3d} untested")


def main():
    """Main CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python generate_tests.py <category|all|--stats> [max_tests] [--force]")
        print()
        print("Categories: orchestrators, agents, brain_tiers, learning, endpoints,")
        print("           error_handling, configuration, deployment, performance,")
        print("           security, e2e")
        print()
        print("Examples:")
        print("  python generate_tests.py all              # Generate all tests")
        print("  python generate_tests.py orchestrators    # Generate tests for orchestrators")
        print("  python generate_tests.py agents 5         # Generate 5 agent tests")
        print("  python generate_tests.py --stats          # Show statistics")
        print("  python generate_tests.py all --force      # Regenerate all tests")
        sys.exit(1)
    
    print_banner()
    
    cortex_root = os.getcwd()
    engine = TestGenerationEngine(cortex_root)
    
    command = sys.argv[1]
    force = "--force" in sys.argv
    
    # Show statistics
    if command == "--stats":
        print_stats(engine)
        return
    
    # Parse max_tests
    max_tests = None
    if len(sys.argv) > 2 and sys.argv[2].isdigit():
        max_tests = int(sys.argv[2])
    
    # Generate tests
    if command == "all":
        print("🚀 Generating tests for all categories...")
        print()
        
        results = engine.generate_all_tests(
            max_per_category=max_tests or 10,
            force=force
        )
        
        print("\n✅ Generation Complete!")
        print("-" * 60)
        
        total_generated = sum(len(tests) for tests in results.values())
        print(f"Total tests generated: {total_generated}")
        print()
        
        for category, tests in results.items():
            if tests:
                print(f"  {category}: {len(tests)} tests")
                for test in tests[:3]:  # Show first 3
                    print(f"    - {test.test_name}")
                if len(tests) > 3:
                    print(f"    ... and {len(tests) - 3} more")
        
        print_stats(engine)
    
    else:
        # Generate for specific category
        category = command
        print(f"🚀 Generating tests for category: {category}")
        print()
        
        results = engine.generate_tests_for_category(
            category,
            max_tests=max_tests,
            force=force
        )
        
        if not results:
            print(f"⚠️  No tests generated for {category}")
            print("   Possible reasons:")
            print("   - All components already have tests")
            print("   - No untested components found")
            print("   - Use --force to regenerate existing tests")
        else:
            print(f"\n✅ Generated {len(results)} tests for {category}!")
            print("-" * 60)
            
            for test in results:
                print(f"  ✓ {test.test_name}")
                print(f"    Component: {test.component}")
                print(f"    File: {test.test_file}")
                print(f"    Lines: {test.lines_generated}")
                print()
        
        print_stats(engine)


if __name__ == "__main__":
    main()
