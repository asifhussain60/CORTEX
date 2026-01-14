#!/usr/bin/env python3
"""
Generate HTML views from YAML specifications.
Parses YAML specs and generates complete, styled HTML files.
Integrates with plan-viewer.html design system.
"""

import yaml
import os
import json
from pathlib import Path
from datetime import datetime
from src.utils.project_root import get_project_root

# CSS VARIABLES FROM plan-viewer.html (Design System)
DESIGN_SYSTEM = {
    "colors": {
        "primary_dark": "#0a0e27",
        "primary_darker": "#050814",
        "primary_accent": "#00d4ff",
        "primary_accent_alt": "#7b2cbf",
        "primary_green": "#06ffa5",
        "completed": "#10b981",
        "in_progress": "#f59e0b",
        "blocked": "#ef4444",
        "not_started": "#6b7280",
        "text_primary": "#ffffff",
        "text_secondary": "rgba(255, 255, 255, 0.7)",
        "text_tertiary": "rgba(255, 255, 255, 0.5)",
        "border": "rgba(0, 212, 255, 0.15)",
        "bg_elevated": "rgba(10, 14, 39, 0.6)"
    },
    "spacing": {
        "xs": "0.25rem",
        "sm": "0.5rem",
        "md": "1rem",
        "lg": "1.5rem",
        "xl": "2rem",
        "2xl": "3rem"
    },
    "radius": {
        "sm": "8px",
        "md": "12px",
        "lg": "16px"
    },
    "shadows": {
        "sm": "0 4px 12px rgba(0, 0, 0, 0.15)",
        "md": "0 8px 32px rgba(0, 212, 255, 0.1)",
        "lg": "0 16px 48px rgba(0, 0, 0, 0.3)"
    },
    "transitions": {
        "base": "200ms ease-out",
        "slow": "400ms ease-out"
    }
}

class HTMLViewGenerator:
    def __init__(self, yaml_path):
        self.yaml_path = yaml_path
        self.yaml_name = Path(yaml_path).stem
        try:
            with open(yaml_path, 'r', encoding='utf-8') as f:
                self.spec = yaml.safe_load(f)
        except Exception as e:
            # If YAML parsing fails, use minimal spec
            print(f"    [WARNING] YAML parse failed, using fallback: {str(e)[:50]}")
            self.spec = {
                'metadata': {
                    'title': self.yaml_name.replace('-', ' ').title(),
                    'description': 'CORTEX 6.0 Interactive View',
                    'audience': 'All Users'
                },
                'sections': {
                    'hero': {
                        'title': self.yaml_name.replace('-', ' ').title(),
                        'subtitle': 'CORTEX 6.0 Production System View'
                    },
                    'content': {
                        'title': 'Overview',
                        'description': 'View content loaded from specification'
                    }
                }
            }
        self.output_dir = Path("get_project_root()/cortex-brain/cx6-plan/viewer/docs/html-views/views")
    
    def generate(self):
        """Generate complete HTML file from spec"""
        html = self._build_html()
        return html
    
    def _build_html(self):
        """Build complete HTML document"""
        spec = self.spec
        
        # Extract key sections
        metadata = spec.get('metadata', {})
        hero = spec.get('sections', {}).get('hero', {})
        content = spec.get('sections', {})
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{metadata.get('description', 'CORTEX 6.0 Interactive View')}">
    <title>{metadata.get('title', 'CORTEX 6.0 View')}</title>
    
    <!-- Design System & Libraries -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    
    <style>
        {self._generate_css()}
    </style>
</head>
<body>
    <div class="view-wrapper">
        <!-- Navigation -->
        <nav class="view-nav">
            <div class="nav-content">
                <a href="../plan-viewer.html" class="nav-back">
                    <i class="bi bi-arrow-left"></i> Back to Dashboard
                </a>
                <h1 class="nav-title">{metadata.get('title', 'View')}</h1>
                <div class="nav-actions">
                    <button class="nav-btn" onclick="toggleDarkMode()">
                        <i class="bi bi-moon"></i>
                    </button>
                </div>
            </div>
        </nav>
        
        <!-- Main Content -->
        <main class="view-content">
            {self._generate_hero_section(hero)}
            {self._generate_content_sections(content)}
        </main>
        
        <!-- Footer -->
        <footer class="view-footer">
            <div class="footer-content">
                <p class="footer-text">
                    CORTEX 6.0 • {metadata.get('audience', 'All Users')} • 
                    Generated {datetime.now().strftime('%Y-%m-%d')}
                </p>
                <a href="#" class="footer-link">Documentation</a>
                <a href="#" class="footer-link">Feedback</a>
            </div>
        </footer>
    </div>
    
    <script>
        {self._generate_javascript()}
    </script>
</body>
</html>
"""
        return html
    
    def _generate_css(self):
        """Generate CSS from design system"""
        css = f"""
        :root {{
            /* Colors */
            --color-primary-dark: {DESIGN_SYSTEM['colors']['primary_dark']};
            --color-primary-accent: {DESIGN_SYSTEM['colors']['primary_accent']};
            --color-primary-accent-alt: {DESIGN_SYSTEM['colors']['primary_accent_alt']};
            --color-primary-green: {DESIGN_SYSTEM['colors']['primary_green']};
            --color-text-primary: {DESIGN_SYSTEM['colors']['text_primary']};
            --color-text-secondary: {DESIGN_SYSTEM['colors']['text_secondary']};
            --color-border: {DESIGN_SYSTEM['colors']['border']};
            --color-bg-elevated: {DESIGN_SYSTEM['colors']['bg_elevated']};
            
            /* Spacing */
            --spacing-xs: {DESIGN_SYSTEM['spacing']['xs']};
            --spacing-md: {DESIGN_SYSTEM['spacing']['md']};
            --spacing-lg: {DESIGN_SYSTEM['spacing']['lg']};
            --spacing-2xl: {DESIGN_SYSTEM['spacing']['2xl']};
            
            /* Radii & Shadows */
            --radius-md: {DESIGN_SYSTEM['radius']['md']};
            --shadow-md: {DESIGN_SYSTEM['shadows']['md']};
            --transition-base: {DESIGN_SYSTEM['transitions']['base']};
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            background: linear-gradient(135deg, #050814 0%, #0a0e27 50%, #050814 100%);
            color: var(--color-text-primary);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            line-height: 1.6;
        }}
        
        .view-wrapper {{
            display: flex;
            flex-direction: column;
            min-height: 100vh;
        }}
        
        /* Navigation */
        .view-nav {{
            background: rgba(10, 14, 39, 0.8);
            backdrop-filter: blur(20px);
            border-bottom: 1px solid var(--color-border);
            position: sticky;
            top: 0;
            z-index: 100;
        }}
        
        .nav-content {{
            max-width: 1400px;
            margin: 0 auto;
            padding: var(--spacing-lg) var(--spacing-2xl);
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: var(--spacing-2xl);
        }}
        
        .nav-back {{
            display: flex;
            align-items: center;
            gap: var(--spacing-xs);
            color: var(--color-primary-accent);
            text-decoration: none;
            font-size: 0.875rem;
            font-weight: 600;
            transition: all var(--transition-base);
        }}
        
        .nav-back:hover {{
            gap: var(--spacing-md);
        }}
        
        .nav-title {{
            flex: 1;
            font-size: 1.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, var(--color-primary-accent), var(--color-primary-green));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .nav-actions {{
            display: flex;
            gap: var(--spacing-md);
        }}
        
        .nav-btn {{
            background: rgba(0, 212, 255, 0.1);
            border: 1px solid var(--color-border);
            color: var(--color-primary-accent);
            width: 40px;
            height: 40px;
            border-radius: var(--radius-md);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all var(--transition-base);
        }}
        
        .nav-btn:hover {{
            background: rgba(0, 212, 255, 0.2);
            box-shadow: var(--shadow-md);
        }}
        
        /* Content */
        .view-content {{
            flex: 1;
            max-width: 1400px;
            width: 100%;
            margin: 0 auto;
            padding: var(--spacing-2xl);
            display: flex;
            flex-direction: column;
            gap: var(--spacing-2xl);
        }}
        
        /* Hero Section */
        .hero-section {{
            background: linear-gradient(135deg, rgba(0, 212, 255, 0.08) 0%, rgba(123, 44, 191, 0.04) 100%);
            backdrop-filter: blur(20px);
            border: 1px solid var(--color-border);
            border-radius: var(--radius-md);
            padding: var(--spacing-2xl);
            position: relative;
            overflow: hidden;
        }}
        
        .hero-section::before {{
            content: '';
            position: absolute;
            top: -50%;
            right: -10%;
            width: 400px;
            height: 400px;
            background: radial-gradient(circle, rgba(0, 212, 255, 0.1) 0%, transparent 70%);
            border-radius: 50%;
            pointer-events: none;
        }}
        
        .hero-content {{
            position: relative;
            z-index: 1;
        }}
        
        .hero-content h1 {{
            font-size: 2.5rem;
            font-weight: 800;
            margin-bottom: var(--spacing-md);
            background: linear-gradient(135deg, var(--color-primary-accent), var(--color-primary-accent-alt));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .hero-content p {{
            color: var(--color-text-secondary);
            font-size: 1.125rem;
            max-width: 600px;
        }}
        
        /* Cards & Sections */
        .section {{
            display: flex;
            flex-direction: column;
            gap: var(--spacing-lg);
        }}
        
        .section-title {{
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--color-text-primary);
            display: flex;
            align-items: center;
            gap: var(--spacing-md);
        }}
        
        .section-title::before {{
            content: '';
            width: 4px;
            height: 28px;
            background: linear-gradient(180deg, var(--color-primary-accent), var(--color-primary-accent-alt));
            border-radius: 2px;
        }}
        
        .card {{
            background: var(--color-bg-elevated);
            backdrop-filter: blur(20px);
            border: 1px solid var(--color-border);
            border-radius: var(--radius-md);
            padding: var(--spacing-lg);
            transition: all var(--transition-base);
        }}
        
        .card:hover {{
            border-color: var(--color-primary-accent);
            box-shadow: var(--shadow-md);
        }}
        
        /* SVG/Diagram Containers */
        .diagram-container {{
            background: rgba(0, 0, 0, 0.2);
            border: 1px solid var(--color-border);
            border-radius: var(--radius-md);
            padding: var(--spacing-lg);
            min-height: 400px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        /* Mermaid Diagram Styling */
        .mermaid {{
            display: flex;
            justify-content: center;
        }}
        
        /* Footer */
        .view-footer {{
            background: rgba(10, 14, 39, 0.6);
            border-top: 1px solid var(--color-border);
            margin-top: auto;
        }}
        
        .footer-content {{
            max-width: 1400px;
            margin: 0 auto;
            padding: var(--spacing-xl) var(--spacing-2xl);
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: var(--spacing-xl);
        }}
        
        .footer-text {{
            font-size: 0.875rem;
            color: var(--color-text-tertiary);
        }}
        
        .footer-link {{
            font-size: 0.875rem;
            color: var(--color-primary-accent);
            text-decoration: none;
            transition: all var(--transition-base);
        }}
        
        .footer-link:hover {{
            color: var(--color-primary-green);
        }}
        
        /* Responsive */
        @media (max-width: 768px) {{
            .view-content {{
                padding: var(--spacing-lg);
            }}
            
            .nav-content {{
                flex-wrap: wrap;
            }}
            
            .hero-content h1 {{
                font-size: 1.875rem;
            }}
            
            .footer-content {{
                flex-direction: column;
                text-align: center;
            }}
        }}
        
        /* Dark mode (future) */
        @media (prefers-color-scheme: dark) {{
            /* Already dark by default */
        }}
        """
        return css
    
    def _generate_hero_section(self, hero):
        """Generate hero section from spec"""
        if not hero:
            return ""
        
        html = f"""
        <section class="hero-section">
            <div class="hero-content">
                <h1>{hero.get('title', 'Section')}</h1>
                <p>{hero.get('subtitle', '')}</p>
            </div>
        </section>
        """
        return html
    
    def _generate_content_sections(self, sections):
        """Generate content sections"""
        html = ""
        for section_key, section_data in sections.items():
            if section_key == 'hero':
                continue
            
            if isinstance(section_data, dict):
                html += f"""
        <section class="section">
            <h2 class="section-title">{section_data.get('title', section_key.replace('_', ' ').title())}</h2>
            <div class="card">
                <p>{section_data.get('description', '')}</p>
                {self._generate_diagram_placeholder(section_data)}
            </div>
        </section>
                """
        
        return html
    
    def _generate_diagram_placeholder(self, section):
        """Generate placeholder for diagrams"""
        diagrams = section.get('diagrams', [])
        html = ""
        for diagram in diagrams:
            diagram_type = diagram.get('type', 'unknown')
            diagram_id = diagram.get('id', 'diagram')
            
            if diagram_type == 'mermaid':
                html += f"""
            <div class="diagram-container">
                <div class="mermaid" id="{diagram_id}">
                    {diagram.get('spec', '-- Diagram spec here')}
                </div>
            </div>
                """
            elif diagram_type == 'd3':
                html += f"""
            <div class="diagram-container" id="{diagram_id}">
                <!-- D3.js diagram will be rendered here -->
            </div>
                """
        
        return html
    
    def _generate_javascript(self):
        """Generate JavaScript for interactivity"""
        js = """
        // Initialize Mermaid
        mermaid.initialize({ startOnLoad: true, theme: 'dark' });
        
        // Dark mode toggle
        function toggleDarkMode() {
            document.body.classList.toggle('dark-mode');
        }
        
        // Initialize D3 diagrams when needed
        document.addEventListener('DOMContentLoaded', () => {
            mermaid.contentLoaded();
        });
        """
        return js


def main():
    """Generate all HTML views from YAML specs"""
    yaml_dir = Path("get_project_root()/cortex-brain/cx6-plan/viewer/docs/html-views")
    output_dir = Path("get_project_root()/cortex-brain/cx6-plan/viewer/docs/html-views/views")
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Process each YAML file
    yaml_files = sorted(yaml_dir.glob("*.yaml"))
    generated_views = []
    
    for yaml_file in yaml_files:
        if yaml_file.name == "00-global-theme-consistency.yaml":
            continue  # Skip global theme file
        
        print(f"Processing {yaml_file.name}...")
        generator = HTMLViewGenerator(str(yaml_file))
        html_content = generator.generate()
        
        # Output filename
        output_name = yaml_file.stem + ".html"
        output_path = output_dir / output_name
        
        # Write HTML file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        generated_views.append({
            'yaml': yaml_file.name,
            'html': output_name,
            'path': str(output_path)
        })
        
        print(f"  [OK] Generated {output_name}")
    
    # Generate index file
    index_html = generate_index(generated_views)
    index_path = output_dir / "index.html"
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(index_html)
    
    print(f"\n[OK] Generated {len(generated_views)} HTML views")
    print(f"[OK] Views directory: {output_dir}")
    
    return generated_views


def generate_index(views):
    """Generate index page linking all views"""
    view_links = "\n".join([
        f'                <li><a href="{v["html"]}">{v["yaml"].replace(".yaml", "")}</a></li>'
        for v in views
    ])
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CORTEX 6.0 Views Index</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
    <style>
        :root {{
            --color-primary-accent: #00d4ff;
            --color-primary-accent-alt: #7b2cbf;
            --color-primary-green: #06ffa5;
            --color-bg-elevated: rgba(10, 14, 39, 0.6);
            --color-border: rgba(0, 212, 255, 0.15);
            --color-text-primary: #ffffff;
            --color-text-secondary: rgba(255, 255, 255, 0.7);
        }}
        
        body {{
            background: linear-gradient(135deg, #050814 0%, #0a0e27 50%, #050814 100%);
            color: var(--color-text-primary);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            padding: 2rem;
        }}
        
        .container {{
            max-width: 800px;
            margin: 0 auto;
        }}
        
        h1 {{
            background: linear-gradient(135deg, var(--color-primary-accent), var(--color-primary-accent-alt));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 2rem;
        }}
        
        ul {{
            list-style: none;
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }}
        
        li {{
            background: var(--color-bg-elevated);
            backdrop-filter: blur(20px);
            border: 1px solid var(--color-border);
            border-radius: 12px;
            padding: 1rem;
            transition: all 200ms ease-out;
        }}
        
        li:hover {{
            border-color: var(--color-primary-accent);
            box-shadow: 0 8px 32px rgba(0, 212, 255, 0.1);
        }}
        
        a {{
            color: var(--color-primary-accent);
            text-decoration: none;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        
        a:hover {{
            color: var(--color-primary-green);
        }}
        
        a::before {{
            content: "▶";
            font-size: 0.75rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>CORTEX 6.0 Interactive Views</h1>
        <ul>
{view_links}
        </ul>
    </div>
</body>
</html>
"""
    return html


if __name__ == "__main__":
    main()
