#!/usr/bin/env python3
"""
Simple UML Display Test - Generate Just UML SVG

Bypasses full dashboard to test UML generation directly.

Author: Asif Hussain
Copyright: © 2024-2025
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.use_cases.render_uml_diagrams import render_uml_for_project
from datetime import datetime


def generate_uml_standalone():
    """Generate standalone UML SVG file."""
    
    print("=" * 80)
    print("CORTEX Standalone UML Generation")
    print("Testing UML Generation Directly")
    print("=" * 80)
    print()
    
    # Setup paths
    project_path = project_root / "src"
    output_path = project_root / "cortex_uml_diagram.svg"
    
    print(f"📂 Analyzing: {project_path}")
    print(f"📄 Output: {output_path}")
    print()
    
    # Generate UML
    print("🚀 Generating UML diagram...")
    start_time = datetime.now()
    
    try:
        svg_content, stats = render_uml_for_project(
            project_path=str(project_path),
            output_path=str(output_path),
            title="CORTEX Architecture",
            exclude_patterns=['test_', '__pycache__', '.venv', 'site-packages', 'dist'],
            wrap_in_html=False  # Pure SVG for standalone viewing
        )
        
        elapsed = (datetime.now() - start_time).total_seconds()
        print(f"✓ UML generated in {elapsed:.2f} seconds")
        print()
        
        # Display statistics
        print("📊 UML Statistics:")
        print(f"  - Total classes: {stats.get('total_classes', 0):,}")
        print(f"  - Total relationships: {stats.get('total_relationships', 0):,}")
        print(f"  - Abstract classes: {stats.get('abstract_classes', 0):,}")
        print(f"  - Inheritance relationships: {stats.get('inheritance_relationships', 0):,}")
        print()
        
        # Check output
        svg_size = len(svg_content)
        print(f"✓ SVG size: {svg_size:,} bytes ({svg_size/1024:.1f} KB)")
        print(f"✓ Saved to: {output_path}")
        print()
        
        print("=" * 80)
        print("✅ UML GENERATION SUCCESSFUL")
        print("=" * 80)
        print()
        print(f"📂 Open file: file://{output_path.absolute()}")
        print()
        print("Validation:")
        print("✓ UML generation engine works")
        print("✓ Returns SVG string for embedding")
        print("✓ Returns statistics for dashboard")
        print("✓ Ready for DashboardRenderer integration")
        print()
        print("Next steps:")
        print("1. Open cortex_uml_diagram.svg in browser")
        print("2. Verify diagram displays correctly")
        print("3. This same SVG would be embedded in dashboard HTML")
        print()
        
        return True
        
    except Exception as e:
        print(f"✗ UML generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = generate_uml_standalone()
    sys.exit(0 if success else 1)
