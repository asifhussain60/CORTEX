"""
YAML-to-Database Bridge Integration Example

Demonstrates how CORTEX 4.0 loads knowledge files into Tier 2 on-demand.

Copyright (c) 2024-2025 Asif Hussain. All rights reserved.
"""

from pathlib import Path
from src.tier2.knowledge_graph.knowledge_graph import KnowledgeGraph


def main():
    """Demonstrate YAML knowledge loading."""
    
    print("=" * 60)
    print("CORTEX 4.0 YAML-to-Database Bridge Demo")
    print("=" * 60)
    print()
    
    # Initialize Knowledge Graph with auto-loading enabled
    print("1. Initializing Knowledge Graph...")
    kg = KnowledgeGraph(auto_load_knowledge=True)
    print("   ✅ Knowledge Graph ready")
    print()
    
    # First query triggers lazy load
    print("2. First query (triggers lazy load)...")
    print("   Query: 'Singleton pattern'")
    results = kg.search_patterns("Singleton pattern", limit=3)
    print(f"   ✅ Found {len(results)} patterns")
    
    if results:
        print(f"\n   Top result: {results[0]['title']}")
        print(f"   Pattern type: {results[0]['pattern_type']}")
        print(f"   Source: {results[0]['source']}")
    print()
    
    # Get load statistics
    print("3. Knowledge load statistics...")
    stats = kg.get_knowledge_load_stats()
    print(f"   Files loaded: {stats['files_loaded']}")
    print(f"   Patterns from knowledge: {stats['patterns_from_knowledge']}")
    print(f"   Last load: {stats['last_load']}")
    print()
    
    # Query different domains
    print("4. Querying different knowledge domains...")
    
    queries = [
        ("TDD best practices", "testing"),
        ("SOLID principles", "engineering"),
        ("OWASP", "security"),
        ("Factory Method", "design-patterns")
    ]
    
    for query, domain in queries:
        results = kg.search_patterns(query, limit=1)
        if results:
            print(f"   ✅ {domain}: {results[0]['title']}")
        else:
            print(f"   ⚠️  {domain}: No patterns found")
    print()
    
    # Load specific category
    print("5. Explicitly loading additional category...")
    count = kg.load_knowledge_category('devops')
    print(f"   ✅ Loaded {count} patterns from devops category")
    print()
    
    # Reload all knowledge
    print("6. Force reload all knowledge files...")
    reload_stats = kg.reload_all_knowledge()
    total = sum(reload_stats.values())
    print(f"   ✅ Reloaded {total} patterns across {len(reload_stats)} categories")
    for category, count in reload_stats.items():
        print(f"      - {category}: {count}")
    print()
    
    print("=" * 60)
    print("Demo complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
