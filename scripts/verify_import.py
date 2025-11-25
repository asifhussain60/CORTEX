#!/usr/bin/env python3
"""
Verify conversation capture import to CORTEX Tier 2 Knowledge Graph.
"""

import yaml
from pathlib import Path
from typing import Dict, Any


def verify_import(pattern_id: str = "capability_driven_validation_2025_11_18") -> Dict[str, Any]:
    """
    Verify that a pattern was successfully imported to the knowledge graph.
    
    Args:
        pattern_id: The pattern ID to verify
        
    Returns:
        Dictionary with verification results
    """
    kg_path = Path("cortex-brain/tier2/knowledge-graph.yaml")
    
    if not kg_path.exists():
        return {
            "success": False,
            "error": "Knowledge graph file not found"
        }
    
    # Load knowledge graph
    with kg_path.open(encoding='utf-8') as f:
        kg = yaml.safe_load(f)
    
    patterns = kg.get('patterns', [])
    
    # Find the pattern
    pattern = None
    for p in patterns:
        if p.get('pattern_id') == pattern_id:
            pattern = p
            break
    
    if not pattern:
        return {
            "success": False,
            "error": f"Pattern '{pattern_id}' not found in knowledge graph",
            "total_patterns": len(patterns)
        }
    
    # Verification successful
    result = {
        "success": True,
        "total_patterns": len(patterns),
        "pattern": {
            "id": pattern['pattern_id'],
            "title": pattern['title'],
            "status": pattern['status'],
            "namespace": pattern['namespace'],
            "quality_score": pattern.get('quality_score'),
            "key_patterns_count": len(pattern.get('key_patterns', [])),
            "lessons_count": len(pattern.get('lessons_learned', [])),
            "files_count": len(pattern.get('files_involved', [])),
            "tags": pattern.get('tags', [])
        }
    }
    
    return result


def main():
    """Main entry point."""
    result = verify_import()
    
    if result['success']:
        print("✅ Import verification SUCCESSFUL!\n")
        print(f"📊 Total patterns in knowledge graph: {result['total_patterns']}\n")
        print("📄 Pattern Details:")
        print(f"   ID: {result['pattern']['id']}")
        print(f"   Title: {result['pattern']['title']}")
        print(f"   Status: {result['pattern']['status']}")
        print(f"   Namespace: {result['pattern']['namespace']}")
        print(f"   Quality Score: {result['pattern']['quality_score']}")
        print(f"\n📦 Content Summary:")
        print(f"   Key Patterns: {result['pattern']['key_patterns_count']}")
        print(f"   Lessons Learned: {result['pattern']['lessons_count']}")
        print(f"   Files Involved: {result['pattern']['files_count']}")
        print(f"   Tags: {', '.join(result['pattern']['tags'])}")
        print(f"\n🎯 Pattern recognition enabled for these tags!")
    else:
        print("❌ Import verification FAILED!")
        print(f"   Error: {result['error']}")
        if 'total_patterns' in result:
            print(f"   Total patterns found: {result['total_patterns']}")


if __name__ == '__main__':
    main()
