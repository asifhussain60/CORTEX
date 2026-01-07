#!/usr/bin/env python3
"""
🎨 CORTEX Purpose-Driven Page Designer
========================================

Applies purpose-specific designs to Level 1 and Level 2 pages following
the glassmorphism design standard with thematic color variations.

**Author:** Asif Hussain
**Version:** 1.0.0
**Date:** January 4, 2026
**Copyright:** © 2026 Asif Hussain. All rights reserved.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class ColorTheme:
    """Color theme for a page level."""
    primary: str
    accent: str
    success: str
    warning: str
    glow: str


@dataclass
class DesignTemplate:
    """Design template configuration."""
    level: int
    category: str
    purpose: str
    layout_type: str  # multi-panel-grid, columns-2, columns-3, single-column
    color_theme: ColorTheme
    hero_style: str  # minimal, detailed, metric-focused, diagram-focused
    features: List[str] = field(default_factory=list)


# Level 1 Color Themes (Purple-Blue spectrum)
LEVEL_1_THEMES = {
    "architecture": ColorTheme(
        primary="#7c7cff",    # Purple (brain)
        accent="#00d4ff",     # Blue (connections)
        success="#00ff88",    # Green (healthy)
        warning="#ffd700",    # Gold (governance)
        glow="rgba(124, 124, 255, 0.3)"
    ),
    "security": ColorTheme(
        primary="#ff6b6b",    # Red (alert)
        accent="#ffd700",     # Gold (shield)
        success="#00ff88",    # Green (safe)
        warning="#ff9f40",    # Orange (warning)
        glow="rgba(255, 107, 107, 0.3)"
    ),
    "orchestrators": ColorTheme(
        primary="#00d4ff",    # Blue (orchestration)
        accent="#7c7cff",     # Purple (planning)
        success="#00ff88",    # Green (execution)
        warning="#ffd700",    # Gold (analysis)
        glow="rgba(0, 212, 255, 0.3)"
    ),
    "knowledge": ColorTheme(
        primary="#ffd700",    # Gold (wisdom)
        accent="#7c7cff",     # Purple (learning)
        success="#00d4ff",    # Blue (modules)
        warning="#00ff88",    # Green (completed)
        glow="rgba(255, 215, 0, 0.3)"
    ),
    "operations": ColorTheme(
        primary="#00ff88",    # Green (operational)
        accent="#00d4ff",     # Blue (automation)
        success="#7c7cff",    # Purple (intelligence)
        warning="#ffd700",    # Gold (monitoring)
        glow="rgba(0, 255, 136, 0.3)"
    ),
    "features": ColorTheme(
        primary="#00d4ff",    # Blue (features)
        accent="#00ff88",     # Green (capabilities)
        success="#7c7cff",    # Purple (innovation)
        warning="#ffd700",    # Gold (premium)
        glow="rgba(0, 212, 255, 0.3)"
    ),
    "design-system": ColorTheme(
        primary="#7c7cff",    # Purple (design)
        accent="#00d4ff",     # Blue (standards)
        success="#00ff88",    # Green (compliant)
        warning="#ffd700",    # Gold (guidelines)
        glow="rgba(124, 124, 255, 0.3)"
    ),
}

# Level 2 Color Themes (Blue-Cyan spectrum - cooler, focused)
LEVEL_2_THEMES = {
    "technical": ColorTheme(
        primary="#00d4ff",    # Blue (technical)
        accent="#00bfff",     # Cyan (code)
        success="#00ff88",    # Green (valid)
        warning="#ffd700",    # Gold (important)
        glow="rgba(0, 212, 255, 0.25)"
    ),
    "conceptual": ColorTheme(
        primary="#7c7cff",    # Purple (concepts)
        accent="#00d4ff",     # Blue (learning)
        success="#00ff88",    # Green (understood)
        warning="#ffd700",    # Gold (key point)
        glow="rgba(124, 124, 255, 0.25)"
    ),
    "reference": ColorTheme(
        primary="#00bfff",    # Cyan (reference)
        accent="#7c7cff",     # Purple (documentation)
        success="#00ff88",    # Green (available)
        warning="#ffd700",    # Gold (important)
        glow="rgba(0, 191, 255, 0.25)"
    ),
    "dashboard": ColorTheme(
        primary="#00ff88",    # Green (metrics)
        accent="#00d4ff",     # Blue (analytics)
        success="#7c7cff",    # Purple (insights)
        warning="#ffd700",    # Gold (alerts)
        glow="rgba(0, 255, 136, 0.25)"
    ),
}


class PurposeDrivenDesigner:
    """Applies purpose-driven designs to CORTEX pages."""
    
    def __init__(self, docs_dir: Path = Path("docs")):
        self.docs_dir = Path(docs_dir)
        self.analysis_file = Path("reports/page-refresh-analysis.json")
        self.templates = self._load_templates()
        
    def _load_templates(self) -> Dict[str, DesignTemplate]:
        """Load design templates for each page category."""
        templates = {}
        
        # Level 1 templates
        for category, theme in LEVEL_1_THEMES.items():
            templates[f"level1_{category}"] = DesignTemplate(
                level=1,
                category=category,
                purpose="navigation_hub",
                layout_type="multi-panel-grid" if category in ["architecture", "orchestrators"] else "columns-2",
                color_theme=theme,
                hero_style="metric-focused",
                features=["tetris-metrics", "breadcrumbs", "category-cards", "mermaid-mindmap"]
            )
        
        # Level 2 templates
        for purpose, theme in LEVEL_2_THEMES.items():
            templates[f"level2_{purpose}"] = DesignTemplate(
                level=2,
                category=purpose,
                purpose=purpose,
                layout_type="single-column",
                color_theme=theme,
                hero_style="diagram-focused",
                features=["breadcrumbs", "toc", "d3-diagrams", "mermaid-flows", "code-blocks"]
            )
        
        return templates
    
    def generate_css_variables(self, template: DesignTemplate) -> str:
        """Generate CSS custom properties for a template."""
        theme = template.color_theme
        level_prefix = f"level{template.level}"
        
        return f"""
        /* {template.category.upper()} Theme - Level {template.level} */
        .{level_prefix}-{template.category} {{
            --theme-primary: {theme.primary};
            --theme-accent: {theme.accent};
            --theme-success: {theme.success};
            --theme-warning: {theme.warning};
            --theme-glow: {theme.glow};
            
            /* Apply to glass effects */
            --glass-border-color: {theme.primary}33;
            --pulse-glow-color: {theme.glow};
        }}
        
        /* Themed glass cards */
        .{level_prefix}-{template.category} .glass-card-clickable:hover {{
            border-color: {theme.primary}66;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.37),
                        0 0 30px {theme.glow};
        }}
        
        /* Themed icons */
        .{level_prefix}-{template.category} .pulse-glow-glass--fast {{
            filter: drop-shadow(0 0 10px {theme.glow});
        }}
        
        /* Themed metric tiles */
        .{level_prefix}-{template.category} .token-metric-tile {{
            border-color: {theme.primary}33;
        }}
        
        .{level_prefix}-{template.category} .token-metric-tile:hover {{
            border-color: {theme.primary}66;
            background: {theme.primary}11;
        }}
"""
    
    def create_level1_hub(self, category: str, page_data: Dict) -> str:
        """Generate Level 1 hub page HTML."""
        template = self.templates.get(f"level1_{category}")
        if not template:
            return ""
        
        theme = template.color_theme
        
        # Generate hero section
        hero_html = f"""
    <!-- Page Title Card with Tetris Metrics -->
    <div class="glass-card-display animation-t1 level1-{category}">
        <div class="page-title-section">
            <h1 class="page-title">
                <i class="fas {self._get_category_icon(category)} pulse-glow-glass--fast"></i>
                {page_data.get('title', category.title())}
            </h1>
            <p class="page-subtitle">{page_data.get('subtitle', '')}</p>
        </div>
        
        <!-- Tetris-style metric tiles -->
        <div class="tetris-panel">
            <div class="token-metrics-tetris">
"""
        
        # Add metric tiles based on category
        for metric in page_data.get('metrics', []):
            hero_html += f"""
                <a href="#{metric['anchor']}" class="token-metric-tile tile-{metric['type']}">
                    <i class="fas {metric['icon']} pulse-glow-glass--fast"></i>
                    <div>
                        <span class="metric-value">{metric['value']}</span>
                        <span class="metric-label">{metric['label']}</span>
                    </div>
                </a>
"""
        
        hero_html += """
            </div>
        </div>
    </div>
"""
        
        return hero_html
    
    def _get_category_icon(self, category: str) -> str:
        """Get Font Awesome icon for category."""
        icons = {
            "architecture": "fa-sitemap",
            "security": "fa-shield-halved",
            "orchestrators": "fa-code-branch",
            "knowledge": "fa-graduation-cap",
            "operations": "fa-gears",
            "features": "fa-star",
            "design-system": "fa-palette",
        }
        return icons.get(category, "fa-folder")
    
    def transform_page(self, file_path: Path, template: DesignTemplate) -> bool:
        """Transform a single page with purpose-driven design."""
        try:
            html_content = file_path.read_text(encoding='utf-8')
            
            # Add theme class to body or main container
            theme_class = f"level{template.level}-{template.category}"
            
            # Inject CSS variables in head
            css_injection = self.generate_css_variables(template)
            
            # Insert before </head>
            if '</head>' in html_content:
                html_content = html_content.replace(
                    '</head>',
                    f'<style>{css_injection}</style>\n</head>'
                )
            
            # Add theme class to main container
            html_content = re.sub(
                r'<main([^>]*)class="([^"]*)"',
                rf'<main\1class="\2 {theme_class}"',
                html_content
            )
            
            # Write back
            file_path.write_text(html_content, encoding='utf-8')
            return True
            
        except Exception as e:
            print(f"❌ Error transforming {file_path}: {e}")
            return False
    
    def process_all_pages(self) -> Dict[str, int]:
        """Process all pages with purpose-driven designs."""
        stats = {
            "level1_transformed": 0,
            "level2_transformed": 0,
            "errors": 0
        }
        
        # Load analysis data
        if not self.analysis_file.exists():
            print(f"❌ Analysis file not found: {self.analysis_file}")
            return stats
        
        with open(self.analysis_file, 'r', encoding='utf-8') as f:
            analysis = json.load(f)
        
        # Transform Level 1 hubs
        print("\n🎨 Transforming Level 1 Hub Pages...")
        for page_data in analysis['pages_by_level'].get('level_1_hubs', []):
            file_path = self.docs_dir / page_data['file']
            category = page_data['file'].split('\\')[0] if '\\' in page_data['file'] else 'default'
            
            template = self.templates.get(f"level1_{category}")
            if template and self.transform_page(file_path, template):
                stats['level1_transformed'] += 1
                print(f"   ✅ {page_data['file']} → {category} theme applied")
            else:
                stats['errors'] += 1
                print(f"   ❌ {page_data['file']} → Failed")
        
        # Transform Level 2 detail pages
        print("\n🎨 Transforming Level 2 Detail Pages...")
        for page_data in analysis['pages_by_level'].get('level_2_details', [])[:20]:  # First 20 for demo
            file_path = self.docs_dir / page_data['file']
            
            # Determine purpose type
            purpose = self._determine_purpose(page_data)
            template = self.templates.get(f"level2_{purpose}")
            
            if template and self.transform_page(file_path, template):
                stats['level2_transformed'] += 1
                print(f"   ✅ {page_data['file']} → {purpose} theme")
            else:
                stats['errors'] += 1
        
        return stats
    
    def _determine_purpose(self, page_data: Dict) -> str:
        """Determine the purpose type for a Level 2 page."""
        features = page_data.get('current_features', [])
        filename = page_data.get('file', '').lower()
        
        if 'code-examples' in features or 'api' in filename:
            return 'technical'
        elif 'diagrams' in features or 'concept' in filename:
            return 'conceptual'
        elif 'metrics' in features or 'dashboard' in filename:
            return 'dashboard'
        else:
            return 'reference'


def main():
    """Main execution function."""
    print("🎨 CORTEX Purpose-Driven Page Designer")
    print("=" * 50)
    
    designer = PurposeDrivenDesigner()
    
    # Process all pages
    stats = designer.process_all_pages()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Transformation Summary:")
    print(f"   Level 1 Hubs: {stats['level1_transformed']}")
    print(f"   Level 2 Details: {stats['level2_transformed']}")
    print(f"   Errors: {stats['errors']}")
    print(f"   Total Success: {stats['level1_transformed'] + stats['level2_transformed']}")
    
    # Generate CSS theme file
    print("\n📄 Generating global theme stylesheet...")
    theme_css = designer.docs_dir / "assets" / "css" / "purpose-driven-themes.css"
    theme_css.parent.mkdir(parents=True, exist_ok=True)
    
    with open(theme_css, 'w', encoding='utf-8') as f:
        f.write("/* CORTEX Purpose-Driven Themes - Auto-Generated */\n")
        f.write("/* Version: 1.0.0 | Generated: 2026-01-04 */\n\n")
        
        for template_name, template in designer.templates.items():
            f.write(designer.generate_css_variables(template))
            f.write("\n")
    
    print(f"   ✅ {theme_css}")
    print("\n🎉 Design transformation complete!")


if __name__ == "__main__":
    main()
