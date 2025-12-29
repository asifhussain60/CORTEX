#!/usr/bin/env python3
"""
Quick script to regenerate CORTEX dashboard with properly rendered templates
"""

import sys
import os
import json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

def regenerate_dashboard():
    """Regenerate the dashboard with proper Jinja2 rendering"""
    
    # Paths
    template_dir = Path(__file__).parent.parent / 'src' / 'cortex_lens' / 'templates'
    output_dir = Path(__file__).parent.parent / 'cortex-lens-output' / 'CORTEX'
    docs_output_dir = Path(__file__).parent.parent / 'docs' / 'cortex-lens-output' / 'CORTEX'
    
    # Load the existing index.html to extract the analysisData
    existing_html = output_dir / 'index.html'
    if not existing_html.exists():
        print(f"❌ File not found: {existing_html}")
        return False
    
    # Read existing HTML to extract the JSON data
    with open(existing_html, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Extract the analysisData JSON block
    start_marker = 'const analysisData = '
    end_marker = '\n};\n        \n        // Initialize charts and visualizations'
    
    start_idx = html_content.find(start_marker)
    if start_idx == -1:
        print("❌ Could not find analysisData in HTML")
        return False
    
    start_idx += len(start_marker)
    end_idx = html_content.find(end_marker, start_idx)
    if end_idx == -1:
        # Try alternate end marker
        end_marker = '\n};'
        end_idx = html_content.find(end_marker, start_idx)
        if end_idx == -1:
            print("❌ Could not find end of analysisData")
            return False
    
    json_str = html_content[start_idx:end_idx + 2]  # +2 to include \n}
    
    try:
        analysis_data = json.loads(json_str)
        print(f"✅ Loaded analysis data: {len(json_str)} bytes")
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse JSON: {e}")
        return False
    
    # Setup Jinja2 environment
    base_template_dir = template_dir / 'base'
    if not base_template_dir.exists():
        print(f"❌ Template directory not found: {base_template_dir}")
        return False
    
    env = Environment(loader=FileSystemLoader(str(base_template_dir)))
    
    # Load the index template
    try:
        template = env.get_template('dashboard.html')
        print(f"✅ Loaded template: dashboard.html")
    except Exception as e:
        print(f"❌ Failed to load template: {e}")
        print(f"Available templates: {list(base_template_dir.glob('*.html'))}")
        return False
    
    # Render the template with the data
    try:
        rendered_html = template.render(**analysis_data)
        print(f"✅ Rendered template: {len(rendered_html)} bytes")
    except Exception as e:
        print(f"❌ Failed to render template: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Write to both locations
    for target_dir in [output_dir, docs_output_dir]:
        target_file = target_dir / 'index.html'
        target_dir.mkdir(parents=True, exist_ok=True)
        
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(rendered_html)
        
        print(f"✅ Written to: {target_file}")
    
    return True

if __name__ == '__main__':
    success = regenerate_dashboard()
    sys.exit(0 if success else 1)
