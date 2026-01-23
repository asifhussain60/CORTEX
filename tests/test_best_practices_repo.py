#!/usr/bin/env python3
"""
Test best practices knowledge repository integration.
"""

import sys
from pathlib import Path

# Add CORTEX to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    print("Testing CORTEX Best Practices Knowledge Repository...")
    print("-" * 60)
    
    from cortex.knowledge.knowledge_repository_integration import get_repository
    from cortex.knowledge.best_practices_discovery import get_discovery
    
    # Test repository
    repo = get_repository()
    stats = repo.get_statistics()
    
    print("\n[OK] Knowledge Repository Loaded")
    print(f"  Version: {stats['version']}")
    print(f"  Total Guides: {stats['total_guides']}")
    print(f"  Categories: {stats['categories']}")
    print(f"  Tech Stacks: {stats['tech_stacks']}")
    print(f"  Learning Paths: {stats['learning_paths']}")
    
    # Test discovery
    discovery = get_discovery()
    all_guides = discovery.list_all_guides()
    
    print(f"\n[OK] Discovery Module Loaded")
    print(f"  Total discoverable guides: {len(all_guides)}")
    
    # Test category listing
    categories = repo.list_categories()
    print(f"\n[OK] Categories ({len(categories)}):")
    for cat in sorted(categories):
        guides = repo.list_guides_by_category(cat)
        print(f"    - {cat}: {len(guides)} guides")
    
    # Test tech stack discovery
    stacks = repo.list_tech_stacks()
    print(f"\n[OK] Technology Stacks ({len(stacks)}):")
    for stack in sorted(stacks):
        guides = repo.list_guides_by_stack(stack)
        print(f"    - {stack}: {len(guides)} guides")
    
    # Test learning paths
    paths = repo.list_learning_paths()
    print(f"\n[OK] Learning Paths ({len(paths)}):")
    for path_name in sorted(paths):
        path_info = repo.get_learning_path(path_name)
        seq_len = len(path_info.get('sequence', []))
        print(f"    - {path_name}: {seq_len} guides")
    
    # Test search
    search_results = discovery.search_guides("security")
    print(f"\n[OK] Search Test (keyword: 'security')")
    print(f"  Found {len(search_results)} matching guides")
    if search_results:
        for result in search_results[:3]:
            print(f"    - {result['path']}: {result['title']}")
    
    print("\n" + "=" * 60)
    print("[PASS] All tests passed!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n[FAIL] Error: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc()
    sys.exit(1)
