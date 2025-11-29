#!/usr/bin/env python3
"""
Search CORTEX Tier 2 Knowledge Graph patterns by tags or keywords.
"""

import yaml
from pathlib import Path
from typing import List, Dict, Any
import sys


def search_patterns(search_term: str = None, tag: str = None) -> List[Dict[str, Any]]:
    """
    Search patterns in the knowledge graph.
    
    Args:
        search_term: Free-text search in title/description
        tag: Exact tag match
        
    Returns:
        List of matching patterns
    """
    kg_path = Path("cortex-brain/tier2/knowledge-graph.yaml")
    
    if not kg_path.exists():
        return []
    
    with kg_path.open(encoding='utf-8') as f:
        kg = yaml.safe_load(f)
    
    patterns = kg.get('patterns', [])
    results = []
    
    for pattern in patterns:
        match = False
        
        # Search by tag
        if tag:
            if tag in pattern.get('tags', []):
                match = True
        
        # Search by term in title
        elif search_term:
            title = pattern.get('title', '').lower()
            if search_term.lower() in title:
                match = True
        
        # No filter - return all
        else:
            match = True
        
        if match:
            results.append({
                'pattern_id': pattern['pattern_id'],
                'title': pattern['title'],
                'status': pattern['status'],
                'namespace': pattern.get('namespace'),
                'quality_score': pattern.get('quality_score'),
                'tags': pattern.get('tags', []),
                'key_patterns_count': len(pattern.get('key_patterns', [])),
                'lessons_count': len(pattern.get('lessons_learned', []))
            })
    
    return results


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python search_patterns.py --tag <tag>")
        print("  python search_patterns.py --search <term>")
        print("  python search_patterns.py --list")
        print("\nAvailable tags:")
        print("  - validation")
        print("  - test_driven_development")
        print("  - configuration_driven")
        print("  - iterative_debugging")
        print("  - documentation_coverage")
        print("  - yaml_driven")
        print("  - production_ready")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == '--list':
        results = search_patterns()
        print(f"📚 Total patterns: {len(results)}\n")
        for r in results:
            print(f"📄 {r['title']}")
            print(f"   ID: {r['pattern_id']}")
            print(f"   Status: {r['status']}")
            print(f"   Quality: {r['quality_score']}/10")
            print(f"   Tags: {', '.join(r['tags'][:3])}{'...' if len(r['tags']) > 3 else ''}")
            print()
    
    elif command == '--tag':
        if len(sys.argv) < 3:
            print("Error: Please provide a tag")
            sys.exit(1)
        
        tag = sys.argv[2]
        results = search_patterns(tag=tag)
        
        print(f"🔍 Patterns tagged with '{tag}': {len(results)}\n")
        for r in results:
            print(f"📄 {r['title']}")
            print(f"   ID: {r['pattern_id']}")
            print(f"   Key Patterns: {r['key_patterns_count']}")
            print(f"   Lessons: {r['lessons_count']}")
            print()
    
    elif command == '--search':
        if len(sys.argv) < 3:
            print("Error: Please provide a search term")
            sys.exit(1)
        
        term = sys.argv[2]
        results = search_patterns(search_term=term)
        
        print(f"🔍 Patterns matching '{term}': {len(results)}\n")
        for r in results:
            print(f"📄 {r['title']}")
            print(f"   Namespace: {r['namespace']}")
            print(f"   Quality: {r['quality_score']}/10")
            print()


if __name__ == '__main__':
    main()
