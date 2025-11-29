#!/usr/bin/env python3
"""
Display detailed pattern information from CORTEX Knowledge Graph.
"""

import yaml
from pathlib import Path
import sys


def show_pattern_details(pattern_id: str):
    """Display comprehensive pattern details."""
    kg_path = Path("cortex-brain/tier2/knowledge-graph.yaml")
    
    if not kg_path.exists():
        print("❌ Knowledge graph not found!")
        return
    
    with kg_path.open(encoding='utf-8') as f:
        kg = yaml.safe_load(f)
    
    pattern = None
    for p in kg.get('patterns', []):
        if p.get('pattern_id') == pattern_id:
            pattern = p
            break
    
    if not pattern:
        print(f"❌ Pattern '{pattern_id}' not found!")
        return
    
    # Display pattern details
    print(f"\n{'='*60}")
    print(f"📄 {pattern['title']}")
    print(f"{'='*60}\n")
    
    print(f"📊 Metadata:")
    print(f"   ID: {pattern['pattern_id']}")
    print(f"   Date: {pattern.get('date')}")
    print(f"   Status: {pattern['status']}")
    print(f"   Namespace: {pattern['namespace']}")
    print(f"   Quality Score: {pattern.get('quality_score')}/10")
    print(f"   Source: {pattern.get('source_file')}")
    print(f"   Imported: {pattern.get('imported_at')}")
    
    print(f"\n🔑 Key Patterns ({len(pattern.get('key_patterns', []))}):")
    for kp in pattern.get('key_patterns', []):
        print(f"\n   • {kp['name']} (confidence: {kp['confidence']})")
        print(f"     Description: {kp['description']}")
        if 'evidence' in kp:
            print(f"     Evidence: {kp['evidence']}")
    
    print(f"\n📚 Lessons Learned ({len(pattern.get('lessons_learned', []))}):")
    for lesson in pattern.get('lessons_learned', []):
        print(f"\n   • {lesson['lesson']}")
        if 'context' in lesson:
            print(f"     Context: {lesson['context']}")
        if 'impact' in lesson:
            print(f"     Impact: {lesson['impact']}")
    
    print(f"\n📈 Implementation Metrics:")
    metrics = pattern.get('implementation_metrics', {})
    if 'code' in metrics:
        print(f"   Code Changes:")
        print(f"     - Added: {metrics['code'].get('lines_added')} lines")
        print(f"     - Modified: {metrics['code'].get('lines_modified')} lines")
        print(f"     - Created: {metrics['code'].get('files_created')} files")
    if 'tests' in metrics:
        print(f"   Test Coverage:")
        print(f"     - Unit: {metrics['tests'].get('unit_tests')} passing")
        print(f"     - Integration: {metrics['tests'].get('integration_tests')} passing")
    if 'quality' in metrics:
        print(f"   Quality:")
        print(f"     - Pass Rate: {metrics['quality'].get('test_pass_rate')}")
        print(f"     - Bugs Found: {metrics['quality'].get('bugs_found_by_tests')}")
    
    print(f"\n📁 Files Involved ({len(pattern.get('files_involved', []))}):")
    for file in pattern.get('files_involved', []):
        print(f"   - {file}")
    
    print(f"\n🔧 Reusable Artifacts ({len(pattern.get('reusable_artifacts', []))}):")
    for artifact in pattern.get('reusable_artifacts', []):
        print(f"   - {artifact}")
    
    print(f"\n🏷️  Tags ({len(pattern.get('tags', []))}):")
    print(f"   {', '.join(pattern.get('tags', []))}")
    
    print(f"\n{'='*60}\n")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python show_pattern.py <pattern_id>")
        print("\nExample:")
        print("  python show_pattern.py capability_driven_validation_2025_11_18")
        sys.exit(1)
    
    pattern_id = sys.argv[1]
    show_pattern_details(pattern_id)


if __name__ == '__main__':
    main()
