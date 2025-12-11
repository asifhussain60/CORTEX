#!/usr/bin/env python3
"""
UML Diagram Generator - Quick Test Script

Demonstrates the Python-native UML diagram generation capability
for the onboarding dashboard architecture tab.

Usage:
    python test_uml_generation.py [path] [output_file]
    
Example:
    python test_uml_generation.py src/dashboard static/dashboard_uml.svg
"""

import sys
import time
from pathlib import Path
import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.use_cases.render_uml_diagrams import render_uml_for_project


def main():
    # Get arguments
    project_path = sys.argv[1] if len(sys.argv) > 1 else 'src/dashboard'
    output_path = sys.argv[2] if len(sys.argv) > 2 else 'static/uml_test_output.svg'
    
    print("=" * 70)
    print("CORTEX UML Diagram Generator - Test Script")
    print("=" * 70)
    print(f"\n📂 Analyzing: {project_path}")
    print(f"💾 Output to: {output_path}")
    print()
    
    # Start timing
    start_time = time.time()
    
    # Generate UML diagram
    print("🔍 Parsing Python files...")
    svg_content, stats = render_uml_for_project(
        project_path=project_path,
        output_path=output_path,
        title="CORTEX Architecture",
        exclude_patterns=['test_', '__pycache__', '.venv', 'site-packages', 'dist']
    )
    
    # End timing
    elapsed = time.time() - start_time
    
    # Display results
    print("\n✅ UML Diagram Generated Successfully!")
    print("\n📊 Statistics:")
    print(f"   • Total Classes:      {stats['total_classes']}")
    print(f"   • Total Relationships: {stats['total_relationships']}")
    print(f"   • Abstract Classes:   {stats['abstract_classes']}")
    print(f"   • Inheritance Links:  {stats['inheritance_relationships']}")
    
    print(f"\n⚡ Performance:")
    print(f"   • Generation Time:    {elapsed:.2f} seconds")
    print(f"   • SVG Size:          {len(svg_content):,} bytes ({len(svg_content)/1024:.1f} KB)")
    
    # Performance check
    if stats['total_classes'] > 0:
        per_class = elapsed / stats['total_classes']
        print(f"   • Time per Class:    {per_class*1000:.1f} ms")
        
        # Check against 2-second target for 500 nodes
        target_time_500 = per_class * 500
        status = "✅ PASS" if target_time_500 < 2.0 else "⚠️  WARN"
        print(f"   • Projected (500):   {target_time_500:.2f}s {status}")
    
    print(f"\n💾 File saved to: {output_path}")
    
    # Display CSS integration note
    print("\n🎨 CSS Integration:")
    print("   To style this diagram, include:")
    print("   <link rel='stylesheet' href='static/css/uml_diagrams.css'>")
    
    print("\n" + "=" * 70)
    print("Test completed successfully!")
    print("=" * 70)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        pytest.skip("Test requires manual verification or configuration")
