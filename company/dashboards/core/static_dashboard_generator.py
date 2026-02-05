"""
Static Dashboard Generator - Phase 23.1 Foundation.

Generates self-contained HTML dashboards with CORTEX glassmorphism theme.
All assets (CSS, JS, data) embedded inline for file:// protocol compatibility.

Architecture: Single HTML file with embedded JSON, inline CSS/JS
Theme: Dark Blue Glassmorphism (13+ tabs)
Size Tiers: small/medium/large/enterprise (auto-detection)

Reference:
- Phase 23 spec: cortex-registry/_cortex-master/phases/active/phase-23-static-dashboard-generator.yaml
- Design system: _workspaces/dashboard-design-reference/design-system.md
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, Any, List, Optional
import json


class SizeTier(str, Enum):
    """Repository size classification for rendering optimization."""
    SMALL = "small"          # <100 files
    MEDIUM = "medium"        # 100-1000 files
    LARGE = "large"          # 1000-10000 files
    ENTERPRISE = "enterprise"  # >10000 files


@dataclass
class DashboardData:
    """
    Container for all dashboard data.
    
    Attributes:
        repo_name: Repository name
        generated_at: Generation timestamp
        generator_version: Generator version string
        size_tier: Detected repository size tier
        metadata: Additional metadata (file counts, metrics)
        sections: Tab content data keyed by tab ID
    """
    repo_name: str
    generated_at: datetime
    generator_version: str
    size_tier: SizeTier
    metadata: Dict[str, Any] = field(default_factory=dict)
    sections: Dict[str, Any] = field(default_factory=dict)


class StaticDashboardGenerator:
    """
    Generate self-contained HTML dashboards with embedded assets.
    
    Features:
    - Single HTML file (no external dependencies)
    - Embedded JSON data
    - Inline CSS (glassmorphism theme)
    - Inline JavaScript (tab navigation, chart rendering)
    - file:// protocol compatible
    - Size tier optimization
    
    Usage:
        generator = StaticDashboardGenerator()
        output_path = generator.generate(
            repo_path=Path("path/to/repo"),
            output_path=Path("output/dashboard.html"),
            size_tier="auto"
        )
    """
    
    VERSION = "1.0.0"
    
    # Size tier thresholds
    SIZE_THRESHOLDS = {
        SizeTier.SMALL: (0, 100),
        SizeTier.MEDIUM: (100, 1000),
        SizeTier.LARGE: (1000, 10000),
        SizeTier.ENTERPRISE: (10000, float('inf'))
    }
    
    def __init__(self):
        """Initialize generator."""
        pass
    
    def detect_size_tier(self, file_count: int) -> SizeTier:
        """
        Detect appropriate size tier based on file count.
        
        Args:
            file_count: Number of files in repository
            
        Returns:
            SizeTier enum value
            
        Examples:
            >>> generator = StaticDashboardGenerator()
            >>> generator.detect_size_tier(50)
            <SizeTier.SMALL: 'small'>
            >>> generator.detect_size_tier(500)
            <SizeTier.MEDIUM: 'medium'>
        """
        for tier, (min_count, max_count) in self.SIZE_THRESHOLDS.items():
            if min_count <= file_count < max_count:
                return tier
        return SizeTier.ENTERPRISE
    
    def collect_data(self, repo_path: Path) -> DashboardData:
        """
        Collect data from repository for dashboard generation.
        
        Args:
            repo_path: Path to repository root
            
        Returns:
            DashboardData object with collected metrics
            
        Note:
            Phase 23.1 - Basic implementation (minimal data collection)
            Phase 23.2 - Full data collection (all sections) ✅
        """
        from company.dashboards.core.data_collectors import ComprehensiveDataCollector
        
        # Count files in repository
        python_files = list(repo_path.rglob("*.py"))
        all_files = list(repo_path.rglob("*"))
        file_count = len([f for f in all_files if f.is_file()])
        
        # Detect size tier
        size_tier = self.detect_size_tier(file_count)
        
        # Phase 23.2: Comprehensive data collection
        collector = ComprehensiveDataCollector()
        sections = collector.collect_all(repo_path)
        
        # Create dashboard data
        data = DashboardData(
            repo_name=repo_path.name,
            generated_at=datetime.now(),
            generator_version=self.VERSION,
            size_tier=size_tier,
            metadata={
                "file_count": file_count,
                "python_files": len(python_files),
                "repo_path": str(repo_path.resolve()),
                "collection_timestamp": datetime.now().isoformat()
            },
            sections=sections
        )
        
        return data
    
    def render_html(self, data: DashboardData, template: Optional[str] = None) -> str:
        """
        Render HTML from dashboard data.
        
        Args:
            data: Dashboard data to render
            template: Optional custom template (default: built-in template)
            
        Returns:
            Complete HTML string with embedded data
            
        Note:
            Phase 23.1 - Basic template
            Phase 23.4 - Full 13-tab template
        """
        if template is None:
            template = self._get_default_template()
        
        # Embed JSON data
        json_data = json.dumps({
            "repo_name": data.repo_name,
            "generated_at": data.generated_at.isoformat(),
            "generator_version": data.generator_version,
            "size_tier": data.size_tier.value,
            "metadata": data.metadata,
            "sections": data.sections
        }, indent=2)
        
        # Replace template placeholders
        html = template.replace("{{repo_name}}", data.repo_name)
        html = html.replace("{{generated_at}}", data.generated_at.strftime("%Y-%m-%d %H:%M:%S"))
        html = html.replace("{{health_score}}", str(data.sections.get("overview", {}).get("health_score", 0)))
        html = html.replace("{{dashboard_data}}", json_data)
        
        return html
    
    def embed_assets(self, html: str, css: str, js: str) -> str:
        """
        Embed CSS and JavaScript into HTML.
        
        Args:
            html: Base HTML content
            css: CSS to embed in <style> tag
            js: JavaScript to embed in <script> tag
            
        Returns:
            HTML with embedded assets
        """
        # Insert CSS before </head>
        if "</head>" in html:
            html = html.replace("</head>", f"<style>\n{css}\n</style>\n</head>")
        
        # Insert JS before </body>
        if "</body>" in html:
            html = html.replace("</body>", f"<script>\n{js}\n</script>\n</body>")
        
        return html
    
    def generate(
        self, 
        repo_path: Path, 
        output_path: Path, 
        size_tier: str = "auto"
    ) -> Path:
        """
        Generate complete dashboard HTML file.
        
        Args:
            repo_path: Path to repository to analyze
            output_path: Path where dashboard HTML will be written
            size_tier: Size tier ("auto" for auto-detection or specific tier)
            
        Returns:
            Path to generated dashboard file
            
        Examples:
            >>> generator = StaticDashboardGenerator()
            >>> output = generator.generate(
            ...     repo_path=Path("./my-repo"),
            ...     output_path=Path("./dashboard.html")
            ... )
            >>> print(f"Dashboard: {output}")
            Dashboard: ./dashboard.html
        """
        # Collect data
        data = self.collect_data(repo_path)
        
        # Override size tier if specified
        if size_tier != "auto":
            data.size_tier = SizeTier(size_tier)
        
        # Render HTML
        html = self.render_html(data)
        
        # Embed assets (CSS + JS)
        css = self._get_glassmorphism_css()
        js = self._get_dashboard_js()
        html = self.embed_assets(html, css, js)
        
        # Write output file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html, encoding="utf-8")
        
        return output_path
    
    def _get_default_template(self) -> str:
        """Get default HTML template."""
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{repo_name}} Dashboard</title>
</head>
<body>
    <header>
        <h1>{{repo_name}}</h1>
        <span class="health-score">{{health_score}}%</span>
    </header>
    
    <main>
        <section class="overview">
            <h2>Overview</h2>
            <p>Dashboard generated at {{generated_at}}</p>
        </section>
    </main>
    
    <script type="application/json" id="dashboard-data">
    {{dashboard_data}}
    </script>
</body>
</html>'''
    
    def _get_glassmorphism_css(self) -> str:
        """Get glassmorphism CSS (Phase 23.1 - minimal styles)."""
        return '''
/* CORTEX Glassmorphism Theme - Phase 23.1 */
:root {
    --color-dark-bg: #0a1428;
    --color-dark-secondary: #1a2a4a;
    --glass-bg: rgba(10, 20, 40, 0.7);
    --glass-border: rgba(255, 255, 255, 0.1);
    --accent-primary: #4d8cff;
    --text-primary: rgba(255, 255, 255, 0.87);
    --text-secondary: rgba(255, 255, 255, 0.7);
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background: linear-gradient(135deg, 
        var(--color-dark-bg) 0%, 
        var(--color-dark-secondary) 100%);
    color: var(--text-primary);
    line-height: 1.6;
    min-height: 100vh;
    padding: 2rem;
}

header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.5rem;
    background: var(--glass-bg);
    backdrop-filter: blur(10px);
    border: 1px solid var(--glass-border);
    border-radius: 12px;
    margin-bottom: 2rem;
}

h1 {
    font-size: 2rem;
    font-weight: 700;
}

.health-score {
    background: var(--accent-primary);
    padding: 0.5rem 1rem;
    border-radius: 8px;
    font-weight: 600;
}

main {
    background: var(--glass-bg);
    backdrop-filter: blur(10px);
    border: 1px solid var(--glass-border);
    border-radius: 12px;
    padding: 2rem;
}
'''
    
    def _get_dashboard_js(self) -> str:
        """
        Phase 23.3 enhanced - Full visualization with Chart.js and D3.js.
        
        Returns:
            JavaScript with inline libraries and chart initialization
        """
        from company.dashboards.core.visualization_manager import VisualizationManager
        
        viz_manager = VisualizationManager()
        
        return f'''
/* CORTEX Dashboard - Phase 23.3 Enhanced */
// Load embedded data first
document.addEventListener('DOMContentLoaded', () => {{
    const dataElement = document.getElementById('dashboard-data');
    if (dataElement) {{
        try {{
            window.dashboardData = JSON.parse(dataElement.textContent);
            console.log('Dashboard data loaded:', window.dashboardData);
        }} catch (e) {{
            console.error('Failed to parse dashboard data:', e);
        }}
    }}
}});

{viz_manager.get_complete_visualization_js()}
'''
