#!/usr/bin/env python3
"""
Generate Demo Dashboard with UML Integration

Creates a demo dashboard to validate UML static integration.

Author: Asif Hussain
Copyright: © 2024-2025
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.dashboard.presentation.dashboard_renderer import DashboardRenderer
from datetime import datetime


def generate_demo_dashboard():
    """Generate a demo dashboard with UML integration."""
    
    print("=" * 80)
    print("CORTEX Demo Dashboard Generation")
    print("Testing UML Static Integration")
    print("=" * 80)
    print()
    
    # Setup paths
    project_path = project_root / "src"
    data_dir = project_root / "examples" / "demo_project_data"
    output_path = project_root / "demo_dashboard.html"
    
    print(f"📂 Project path: {project_path}")
    print(f"📂 Data directory: {data_dir}")
    print(f"📄 Output path: {output_path}")
    print()
    
    # Check if data directory exists
    if not data_dir.exists():
        print(f"⚠️  Warning: Data directory not found: {data_dir}")
        print(f"📝 Creating minimal demo data...")
        
        # Create minimal data directory
        data_dir.mkdir(parents=True, exist_ok=True)
        
        # Create minimal components.json
        import json
        
        components = {
            "components": [
                {
                    "name": "DashboardRenderer",
                    "type": "class",
                    "path": "src/dashboard/presentation/dashboard_renderer.py",
                    "health_score": 85,
                    "complexity": 12
                }
            ]
        }
        
        dependencies = {
            "dependencies": []
        }
        
        issues = {
            "issues": []
        }
        
        health = {
            "system_health": {
                "score": 85,
                "timestamp": datetime.now().isoformat(),
                "description": "Demo system health"
            }
        }
        
        (data_dir / "components.json").write_text(json.dumps(components, indent=2))
        (data_dir / "dependencies.json").write_text(json.dumps(dependencies, indent=2))
        (data_dir / "issues.json").write_text(json.dumps(issues, indent=2))
        (data_dir / "health.json").write_text(json.dumps(health, indent=2))
        
        print("✓ Created minimal demo data")
        print()
    
    # Create renderer
    print("🎨 Creating dashboard renderer...")
    try:
        renderer = DashboardRenderer(project_path, data_dir)
        print("✓ Renderer created successfully")
    except Exception as e:
        print(f"✗ Failed to create renderer: {e}")
        import traceback
        traceback.print_exc()
        return False
    print()
    
    # Generate dashboard
    print("🚀 Generating dashboard with UML integration...")
    start_time = datetime.now()
    
    try:
        result_path = renderer.render(output_path, enable_websocket=False)
        
        elapsed = (datetime.now() - start_time).total_seconds()
        print(f"✓ Dashboard generated in {elapsed:.2f} seconds")
        print(f"✓ Output: {result_path}")
        print()
        
        # Validate output
        html_content = result_path.read_text()
        html_size = len(html_content)
        
        print("📊 Dashboard Statistics:")
        print(f"  - HTML size: {html_size:,} bytes ({html_size/1024:.1f} KB)")
        
        # Check for UML integration
        if 'uml_diagram_svg' in html_content or '<svg' in html_content:
            svg_count = html_content.count('<svg')
            print(f"  - SVG diagrams: {svg_count}")
            print("  - UML integration: ✓ EMBEDDED")
        else:
            print("  - UML integration: ⚠️  NOT FOUND")
        
        # Check for dashboard data
        if '"uml":' in html_content:
            print("  - UML data in JSON: ✓ PRESENT")
        else:
            print("  - UML data in JSON: ⚠️  NOT FOUND")
        
        # Check for architecture tab
        if 'architecture-tab' in html_content:
            print("  - Architecture tab: ✓ PRESENT")
        else:
            print("  - Architecture tab: ⚠️  NOT FOUND")
        
        print()
        print("=" * 80)
        print("✅ DASHBOARD GENERATED SUCCESSFULLY")
        print("=" * 80)
        print()
        print(f"📂 Open in browser: file://{result_path.absolute()}")
        print()
        print("Next steps:")
        print("1. Open demo_dashboard.html in your browser")
        print("2. Click 'Architecture' tab")
        print("3. Click 'UML Diagrams' sub-tab")
        print("4. Verify UML diagram displays instantly (no loading)")
        print("5. Click 'Export SVG' to download diagram")
        print()
        
        return True
        
    except Exception as e:
        print(f"✗ Dashboard generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = generate_demo_dashboard()
    sys.exit(0 if success else 1)
