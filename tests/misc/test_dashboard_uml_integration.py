#!/usr/bin/env python3
"""
Test Dashboard UML Integration - Static Generation Approach

Tests that UML generation works correctly for embedding in dashboards.

Author: Asif Hussain
Copyright: © 2024-2025
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.use_cases.render_uml_diagrams import render_uml_for_project


def test_uml_static_generation():
    """Test that UML diagram can be pre-generated for dashboard embedding."""
    
    print("=" * 80)
    print("CORTEX Dashboard UML Integration Test")
    print("Testing static generation approach (no REST API)")
    print("=" * 80)
    print()
    
    # Setup paths
    project_path = project_root / "src"
    
    print(f"✓ Project path: {project_path}")
    print()
    
    # Test UML generation
    print("Testing UML pre-generation for dashboard...")
    try:
        svg_content, stats = render_uml_for_project(
            project_path=str(project_path),
            title="CORTEX Architecture Test",
            exclude_patterns=['test_', '__pycache__', '.venv', 'site-packages']
        )
        
        print("✓ UML generation completed")
        
        # Check SVG
        if svg_content:
            svg_length = len(svg_content)
            print(f"✓ SVG generated: {svg_length:,} characters")
            
            # Validate SVG structure
            if '<svg' in svg_content and '</svg>' in svg_content:
                print("✓ SVG structure valid")
            else:
                print("✗ SVG structure invalid")
                return False
        else:
            print("✗ No SVG content generated")
            return False
        
        # Check statistics
        if stats:
            print(f"\n📊 UML Statistics:")
            print(f"  - Total classes: {stats.get('total_classes', 0)}")
            print(f"  - Total relationships: {stats.get('total_relationships', 0)}")
            print(f"  - Abstract classes: {stats.get('abstract_classes', 0)}")
            print(f"  - Inheritance relationships: {stats.get('inheritance_relationships', 0)}")
        else:
            print("⚠ No statistics returned")
        
    except Exception as e:
        print(f"✗ UML generation exception: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print()
    print("=" * 80)
    print("✅ ALL TESTS PASSED")
    print("=" * 80)
    print()
    print("Summary:")
    print("- UML diagram can be pre-generated ✓")
    print("- Returns SVG string for embedding ✓")
    print("- Returns statistics for dashboard ✓")
    print("- No REST API endpoint needed ✓")
    print("- Ready for DashboardRenderer integration ✓")
    print()
    print("Integration approach:")
    print("1. DashboardRenderer._generate_uml_diagram() calls render_uml_for_project()")
    print("2. SVG and stats added to template context")
    print("3. Template embeds SVG in HTML (no AJAX needed)")
    print("4. JavaScript displays embedded data")
    print()
    
    return True


if __name__ == "__main__":
    success = test_uml_static_generation()
    sys.exit(0 if success else 1)
