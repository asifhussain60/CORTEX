"""
CORTEX Universal Dashboard Generator
Version: 1.0.0
Author: Asif Hussain
Created: 2026-02-01

Generates universal, self-contained HTML dashboards for ANY repository
analyzed by CORTEX. Single-file output with all assets inline.

Usage:
    python -m company.dashboards.tooling.universal_generator \\
        --repo D:\\PROJECTS\\KASHKOLE \\
        --output company/dashboards/kashkole/dashboard.html
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Import data collectors
from .data_collectors.lens_collector import LensDataCollector
from .data_collectors.business_translator import BusinessTranslator
from .data_collectors.security_collector import SecurityCollector
from .data_collectors.git_collector import GitCollector

class UniversalDashboardGenerator:
    """Generate universal HTML dashboards from CORTEX analysis"""
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.repo_name = self.repo_path.name
        self.output_data = {}
        
        # Initialize collectors
        self.lens_collector = LensDataCollector(repo_path)
        self.business_translator = BusinessTranslator()
        self.security_collector = SecurityCollector(repo_path)
        self.git_collector = GitCollector(repo_path)
    
    def collect_data(self) -> Dict[str, Any]:
        """Collect all dashboard data from CORTEX LENS and other sources"""
        print(f"📊 Collecting data for {self.repo_name}...")
        
        # Collect from CORTEX LENS
        print("  🔍 Running CORTEX LENS analysis...")
        lens_data = self.lens_collector.analyze()
        
        # Translate to business language
        print("  💼 Translating to business language...")
        lens_data = self.business_translator.translate(lens_data)
        
        # Collect security data
        print("  🔒 Scanning for security issues...")
        security_data = self.security_collector.scan()
        
        # Collect git history
        print("  📈 Analyzing git history...")
        git_data = self.git_collector.analyze()
        
        # Merge all data
        self.output_data = {
            "repo_metadata": {
                "name": self.repo_name,
                "path": str(self.repo_path),
                "generated_at": datetime.now().isoformat(),
                "cortex_version": "8.0"
            },
            "overview": lens_data.get("overview", {}),
            "dependencies": lens_data.get("dependencies", {}),
            "classes": lens_data.get("classes", {}),
            "timeline": git_data,
            "impact": lens_data.get("impact", {}),
            "security": security_data,
            "tech_stack": lens_data.get("tech_stack", {}),
            "architecture": lens_data.get("architecture", {})
        }
        
        return self.output_data
    
    def generate_html(self, output_path: str) -> None:
        """Generate the final HTML dashboard"""
        print(f"🎨 Generating dashboard...")
        
        # Load template
        template_path = Path(__file__).parent / "templates" / "universal_dashboard.html.j2"
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # Load CORTEX logo (base64)
        logo_path = Path(__file__).parent.parent / "cortex_logo_base64.txt"
        with open(logo_path, 'r', encoding='utf-8') as f:
            cortex_logo_base64 = f.read().strip()
        
        # Load glassmorphism CSS
        css_path = Path(__file__).parent / "assets" / "css_templates" / "glassmorphism.css"
        with open(css_path, 'r', encoding='utf-8') as f:
            glassmorphism_css = f.read()
        
        # Render template (simple string replacement for now, Jinja2 later)
        html_output = template_content.replace("{{CORTEX_LOGO_BASE64}}", cortex_logo_base64)
        html_output = html_output.replace("{{GLASSMORPHISM_CSS}}", glassmorphism_css)
        html_output = html_output.replace("{{DASHBOARD_DATA}}", json.dumps(self.output_data, indent=2))
        html_output = html_output.replace("{{REPO_NAME}}", self.repo_name)
        
        # Write output
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_output)
        
        print(f"✅ Dashboard generated: {output_path}")
        print(f"   File size: {output_file.stat().st_size / 1024:.1f} KB")
    
    def run(self, output_path: str) -> None:
        """Main execution flow"""
        try:
            # Collect data
            self.collect_data()
            
            # Generate HTML
            self.generate_html(output_path)
            
            print("\\n🎉 Dashboard generation complete!")
            
        except Exception as e:
            print(f"\\n❌ Error: {e}", file=sys.stderr)
            raise


def main():
    parser = argparse.ArgumentParser(
        description="Generate universal CORTEX dashboard for any repository"
    )
    parser.add_argument(
        "--repo",
        required=True,
        help="Path to repository to analyze"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output path for generated dashboard.html"
    )
    
    args = parser.parse_args()
    
    # Run generator
    generator = UniversalDashboardGenerator(args.repo)
    generator.run(args.output)


if __name__ == "__main__":
    main()
