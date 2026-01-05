#!/usr/bin/env python3
"""
CORTEX Plan Viewer Generator
Generates self-contained plan-viewer.html files with inline CSS.

Usage:
    # Generate for specific plan
    python3 generate-plan-viewer.py --plan-dir cortex-brain/documents/planning/active/my-plan
    
    # Regenerate all plans
    python3 generate-plan-viewer.py --regenerate-all
    
    # Create new plan with viewer
    python3 generate-plan-viewer.py --new-plan my-new-plan --epic-name "My New Epic"

Author: Asif Hussain
Version: 1.0.0
Created: January 5, 2026
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional


class PlanViewerGenerator:
    """Generates self-contained plan-viewer.html files."""
    
    TEMPLATE_VERSION = "1.0.0"
    
    def __init__(self, template_dir: Path):
        self.template_dir = template_dir
        self.template_path = template_dir / "plan-viewer-template.html"
        self.css_path = template_dir / "glassmorphism-theme.css"
        
        if not self.template_path.exists():
            raise FileNotFoundError(f"Template not found: {self.template_path}")
        if not self.css_path.exists():
            raise FileNotFoundError(f"CSS not found: {self.css_path}")
    
    def load_template(self) -> str:
        """Load HTML template."""
        return self.template_path.read_text(encoding='utf-8')
    
    def load_css(self) -> str:
        """Load and minify CSS."""
        css_content = self.css_path.read_text(encoding='utf-8')
        # Simple minification: remove comments and excess whitespace
        lines = []
        for line in css_content.split('\n'):
            stripped = line.strip()
            # Skip comment-only lines
            if stripped.startswith('/*') or stripped.startswith('*') or not stripped:
                continue
            lines.append(stripped)
        return ' '.join(lines)
    
    def load_epic_manifest(self, plan_dir: Path) -> Optional[Dict]:
        """Load epic manifest YAML (basic parsing)."""
        manifest_path = plan_dir / "epic-manifest.yaml"
        if not manifest_path.exists():
            return None
        
        # Basic YAML parsing for our needs
        manifest = {}
        content = manifest_path.read_text(encoding='utf-8')
        
        for line in content.split('\n'):
            line = line.strip()
            if ':' in line and not line.startswith('#'):
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip().strip('"\'')
                manifest[key] = value
        
        return manifest
    
    def load_progress_tracker(self, plan_dir: Path) -> Optional[Dict]:
        """Load progress tracker JSON."""
        tracker_path = plan_dir / "tracking" / "progress-tracker.json"
        if not tracker_path.exists():
            return None
        
        with open(tracker_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def generate(self, plan_dir: Path, config: Optional[Dict] = None) -> str:
        """
        Generate plan-viewer.html with inline CSS.
        
        Args:
            plan_dir: Path to plan directory
            config: Optional configuration overrides
        
        Returns:
            Generated HTML content
        """
        plan_dir = Path(plan_dir).resolve()
        
        # Load manifest and tracker for metadata
        manifest = self.load_epic_manifest(plan_dir)
        tracker = self.load_progress_tracker(plan_dir)
        
        # Build configuration
        default_config = {
            'epic_name': manifest.get('epic_name', 'CORTEX Plan') if manifest else 'CORTEX Plan',
            'epic_subtitle': manifest.get('epic_type', 'Planning Execution') if manifest else 'Planning Execution',
            'epic_icon': 'fa-brain',
            'total_phases': tracker['phases']['total'] if tracker else 0,
            'initial_status': tracker.get('status', 'Planning').title() if tracker else 'Planning',
            'refresh_interval_seconds': 5,
            'refresh_interval_ms': 5000,
            'progress_file': 'tracking/progress-tracker.json',
            'task_file': 'tracking/task-registry.json',
            'version': manifest.get('version', '1.0.0') if manifest else '1.0.0',
            'execution_mode': 'Autonomous Python',
            'creation_date': datetime.now().strftime('%B %d, %Y'),
            'generation_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'copyright': '© 2025-2026 Asif Hussain. All rights reserved.',
            'template_version': self.TEMPLATE_VERSION,
        }
        
        # Merge with provided config
        if config:
            default_config.update(config)
        
        # Load template and CSS
        template = self.load_template()
        css_content = self.load_css()
        
        # Replace placeholders
        html = template.replace('{{CSS_CONTENT}}', css_content)
        html = html.replace('{{EPIC_NAME}}', default_config['epic_name'])
        html = html.replace('{{EPIC_SUBTITLE}}', default_config['epic_subtitle'])
        html = html.replace('{{EPIC_ICON}}', default_config['epic_icon'])
        html = html.replace('{{TOTAL_PHASES}}', str(default_config['total_phases']))
        html = html.replace('{{INITIAL_STATUS}}', default_config['initial_status'])
        html = html.replace('{{REFRESH_INTERVAL_SECONDS}}', str(default_config['refresh_interval_seconds']))
        html = html.replace('{{REFRESH_INTERVAL_MS}}', str(default_config['refresh_interval_ms']))
        html = html.replace('{{PROGRESS_FILE}}', default_config['progress_file'])
        html = html.replace('{{TASK_FILE}}', default_config['task_file'])
        html = html.replace('{{VERSION}}', default_config['version'])
        html = html.replace('{{EXECUTION_MODE}}', default_config['execution_mode'])
        html = html.replace('{{CREATION_DATE}}', default_config['creation_date'])
        html = html.replace('{{GENERATION_DATE}}', default_config['generation_date'])
        html = html.replace('{{COPYRIGHT}}', default_config['copyright'])
        html = html.replace('{{TEMPLATE_VERSION}}', default_config['template_version'])
        
        return html
    
    def save(self, plan_dir: Path, html_content: str) -> Path:
        """Save generated HTML to plan directory."""
        plan_dir = Path(plan_dir).resolve()
        output_path = plan_dir / "plan-viewer.html"
        
        output_path.write_text(html_content, encoding='utf-8')
        return output_path
    
    def regenerate_all(self, plans_root: Path) -> list:
        """Regenerate all plan viewers in plans directory."""
        plans_root = Path(plans_root).resolve()
        regenerated = []
        
        print(f"🔍 Scanning for plans in: {plans_root}")
        
        # Find all directories with epic-manifest.yaml or progress-tracker.json
        for plan_dir in plans_root.rglob("*"):
            if not plan_dir.is_dir():
                continue
            
            # Check if this looks like a plan directory
            has_manifest = (plan_dir / "epic-manifest.yaml").exists()
            has_tracker = (plan_dir / "tracking" / "progress-tracker.json").exists()
            
            if has_manifest or has_tracker:
                print(f"\n📋 Processing: {plan_dir.name}")
                try:
                    html = self.generate(plan_dir)
                    output_path = self.save(plan_dir, html)
                    regenerated.append(output_path)
                    print(f"   ✅ Generated: {output_path.relative_to(plans_root)}")
                except Exception as e:
                    print(f"   ❌ Error: {e}")
        
        return regenerated


def main():
    parser = argparse.ArgumentParser(
        description="Generate self-contained plan-viewer.html files with inline CSS"
    )
    
    parser.add_argument(
        '--plan-dir',
        type=str,
        help='Path to plan directory (relative or absolute)'
    )
    
    parser.add_argument(
        '--regenerate-all',
        action='store_true',
        help='Regenerate all plan viewers in active plans directory'
    )
    
    parser.add_argument(
        '--template-dir',
        type=str,
        default='templates/plan-viewer',
        help='Path to template directory (default: templates/plan-viewer)'
    )
    
    parser.add_argument(
        '--plans-root',
        type=str,
        default='cortex-brain/documents/planning/active',
        help='Root directory for plans (default: cortex-brain/documents/planning/active)'
    )
    
    parser.add_argument(
        '--epic-name',
        type=str,
        help='Override epic name'
    )
    
    parser.add_argument(
        '--epic-icon',
        type=str,
        default='fa-brain',
        help='Font Awesome icon class (default: fa-brain)'
    )
    
    args = parser.parse_args()
    
    # Find template directory
    template_dir = Path(args.template_dir)
    if not template_dir.is_absolute():
        # Try relative to script location
        script_dir = Path(__file__).parent
        template_dir = script_dir
        if not (template_dir / "plan-viewer-template.html").exists():
            # Try relative to current directory
            template_dir = Path.cwd() / args.template_dir
    
    if not template_dir.exists():
        print(f"❌ Template directory not found: {template_dir}")
        sys.exit(1)
    
    print("=" * 60)
    print("🧠 CORTEX Plan Viewer Generator")
    print("=" * 60)
    print(f"📁 Template dir: {template_dir}")
    print()
    
    try:
        generator = PlanViewerGenerator(template_dir)
        
        if args.regenerate_all:
            # Regenerate all plans
            plans_root = Path(args.plans_root)
            if not plans_root.is_absolute():
                plans_root = Path.cwd() / plans_root
            
            print(f"🔄 Regenerating all plans in: {plans_root}")
            print()
            
            regenerated = generator.regenerate_all(plans_root)
            
            print()
            print("=" * 60)
            print(f"✅ Regenerated {len(regenerated)} plan viewer(s)")
            print("=" * 60)
            
        elif args.plan_dir:
            # Generate single plan
            plan_dir = Path(args.plan_dir)
            if not plan_dir.is_absolute():
                plan_dir = Path.cwd() / plan_dir
            
            if not plan_dir.exists():
                print(f"❌ Plan directory not found: {plan_dir}")
                sys.exit(1)
            
            config = {}
            if args.epic_name:
                config['epic_name'] = args.epic_name
            if args.epic_icon:
                config['epic_icon'] = args.epic_icon
            
            print(f"📋 Generating plan viewer for: {plan_dir.name}")
            print()
            
            html = generator.generate(plan_dir, config)
            output_path = generator.save(plan_dir, html)
            
            print("=" * 60)
            print(f"✅ Generated: {output_path}")
            print("=" * 60)
            print()
            print(f"📊 View at: file://{output_path}")
            print(f"🚀 Or run: cd {plan_dir} && python3 -m http.server 8000")
            
        else:
            parser.print_help()
            sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
