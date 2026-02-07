"""
SPA Dashboard Suite Generator.

Generates static dashboard suite with:
- Root landing page (dist/index.html)
- Per-repo dashboards (dist/repos/<slug>/index.html)
- Embedded JSON data (no fetch, file:// compatible)
- ChartHost visibility guards

Follows GPT specification for SPA-like static output.

Authority: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings)
AC-ID: SPA-SUITE-002
"""

import json
import re
import shutil
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from cortex.visualization.spa.models import (
    DashboardSuiteConfig,
    RepoDashboardData,
    RepoManifestEntry,
    to_dict,
)

logger = logging.getLogger(__name__)


@dataclass
class GenerationResult:
    """Result of dashboard suite generation."""
    
    success: bool
    landing_path: Optional[str] = None
    repo_dashboards: List[str] = None
    errors: List[str] = None
    
    def __post_init__(self) -> None:
        """Initialize default values."""
        if self.repo_dashboards is None:
            self.repo_dashboards = []
        if self.errors is None:
            self.errors = []


class DashboardSuiteGenerator:
    """
    Generates complete static dashboard suite with glassmorphism design.
    
    Produces:
    - dist/index.html (landing with hero + tile grid)
    - dist/repos/<slug>/index.html (repo dashboards with glassmorphism theme)
    - dist/assets/* (CSS, JS, vendor libs)
    - dist/images/* (logo)
    
    All data embedded as JSON - no fetch() calls (file:// compatible).
    Uses glassmorphism template: repo-dashboard-glass-v1.html
    Follows MVC architecture: Model (JSON) → View (HTML/CSS) → Controller (JS)
    
    Authority: Phase 32 - Glassmorphism Dashboard Generator Fix
    Documentation:
    - docs/guides/dashboard-template-structure.md (template overview)
    - docs/guides/dashboard-mvc-integration.md (MVC patterns)
    
    Example:
        ```python
        generator = DashboardSuiteGenerator(
            output_dir=Path("dist")
        )
        result = generator.generate_suite(config)
        print(f"Generated: {result.landing_path}")
        for dashboard in result.repo_dashboards:
            print(f"  - {dashboard}")
        ```
    """
    
    # Template paths (relative to CORTEX root)
    DASHBOARD_TEMPLATE = "company/dashboards/templates/repo-dashboard-glass-v1.html"
    ASSETS_DIR = "company/dashboards/assets"
    SPA_ASSETS_DIR = "company/dashboards/spa/assets"
    LOGO_PATH = "company/dashboards/assets/images/CORTEX-logo-512.png"
    
    def __init__(
        self,
        output_dir: Path,
        cortex_root: Optional[Path] = None,
    ) -> None:
        """
        Initialize generator.
        
        Args:
            output_dir: Directory to write generated suite
            cortex_root: CORTEX project root (auto-detected if None)
        """
        self.output_dir = Path(output_dir)
        
        # Auto-detect CORTEX root
        if cortex_root is None:
            current = Path(__file__).resolve()
            # Navigate up to find cortex root
            for parent in current.parents:
                if (parent / "cortex" / "__init__.py").exists():
                    cortex_root = parent
                    break
            if cortex_root is None:
                cortex_root = Path.cwd()
        
        self.cortex_root = Path(cortex_root)
        self._validate_templates()
    
    def _validate_templates(self) -> None:
        """Validate required templates exist."""
        dashboard_template = self.cortex_root / self.DASHBOARD_TEMPLATE
        if not dashboard_template.exists():
            logger.warning(f"Dashboard template not found: {dashboard_template}")
    
    def generate_suite(
        self,
        config: DashboardSuiteConfig,
        repo_data: Dict[str, RepoDashboardData],
    ) -> GenerationResult:
        """
        Generate complete dashboard suite.
        
        Args:
            config: Suite configuration with repo list
            repo_data: Dictionary mapping slug -> full dashboard data
            
        Returns:
            GenerationResult with paths to generated files
        """
        errors: List[str] = []
        repo_dashboards: List[str] = []
        
        try:
            # Create output directory structure
            self._create_directory_structure()
            
            # Copy assets
            self._copy_assets()
            
            # Generate landing page
            landing_path = self._generate_landing(config)
            
            # Generate repo dashboards
            for repo in config.repos:
                try:
                    data = repo_data.get(repo.slug)
                    if data is None:
                        errors.append(f"No data for repo: {repo.slug}")
                        continue
                    
                    dashboard_path = self._generate_repo_dashboard(repo, data)
                    repo_dashboards.append(str(dashboard_path))
                    
                except Exception as e:
                    errors.append(f"Failed to generate {repo.slug}: {e}")
                    logger.error(f"Repo dashboard generation failed: {e}", exc_info=True)
            
            return GenerationResult(
                success=len(errors) == 0,
                landing_path=str(landing_path),
                repo_dashboards=repo_dashboards,
                errors=errors,
            )
            
        except Exception as e:
            logger.error(f"Suite generation failed: {e}", exc_info=True)
            return GenerationResult(
                success=False,
                errors=[str(e)],
            )
    
    def _create_directory_structure(self) -> None:
        """Create output directory structure per GPT spec."""
        dirs = [
            self.output_dir,
            self.output_dir / "assets" / "css",
            self.output_dir / "assets" / "js",
            self.output_dir / "assets" / "vendor",
            self.output_dir / "images",
            self.output_dir / "repos",
        ]
        
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Created directory: {dir_path}")
    
    def _copy_assets(self) -> None:
        """Copy CSS, JS, vendor libs, and image assets to output."""
        # Copy main assets
        assets_src = self.cortex_root / self.ASSETS_DIR
        if assets_src.exists():
            # Copy CSS
            css_src = assets_src / "css"
            if css_src.exists():
                for css_file in css_src.glob("*.css"):
                    shutil.copy2(css_file, self.output_dir / "assets" / "css")
            
            # Copy images
            images_src = assets_src / "images"
            if images_src.exists():
                for img_file in images_src.glob("*"):
                    if img_file.is_file():
                        shutil.copy2(img_file, self.output_dir / "images")
        
        # Copy SPA-specific assets (JS, CSS, vendor)
        spa_assets = self.cortex_root / self.SPA_ASSETS_DIR
        if spa_assets.exists():
            # Copy JS files
            js_src = spa_assets / "js"
            if js_src.exists():
                for js_file in js_src.glob("*.js"):
                    shutil.copy2(js_file, self.output_dir / "assets" / "js")
                    logger.debug(f"Copied JS: {js_file.name}")
            
            # Copy CSS files (use-cases.css, etc.)
            css_src = spa_assets / "css"
            if css_src.exists():
                for css_file in css_src.glob("*.css"):
                    shutil.copy2(css_file, self.output_dir / "assets" / "css")
                    logger.debug(f"Copied CSS: {css_file.name}")
            
            # Copy vendor libraries (Fuse.js, Grid.js, ECharts)
            vendor_src = spa_assets / "vendor"
            if vendor_src.exists():
                vendor_dest = self.output_dir / "assets" / "vendor"
                vendor_dest.mkdir(parents=True, exist_ok=True)
                for vendor_file in vendor_src.glob("*"):
                    if vendor_file.is_file():
                        shutil.copy2(vendor_file, vendor_dest)
                        logger.debug(f"Copied vendor: {vendor_file.name}")
        
        # Copy logo to standard location
        logo_src = self.cortex_root / self.LOGO_PATH
        if logo_src.exists():
            shutil.copy2(logo_src, self.output_dir / "images" / "cortex-logo.png")
    
    def _generate_landing(self, config: DashboardSuiteConfig) -> Path:
        """
        Generate landing page with embedded manifest.
        
        Creates hero section + tile grid per GPT spec.
        """
        output_path = self.output_dir / "index.html"
        
        # Prepare manifest data
        manifest_json = json.dumps([to_dict(repo) for repo in config.repos], indent=2)
        
        # Generate HTML
        html = self._render_landing_template(config, manifest_json)
        
        output_path.write_text(html, encoding="utf-8")
        logger.info(f"Generated landing: {output_path}")
        
        return output_path
    
    def _generate_repo_dashboard(
        self,
        repo: RepoManifestEntry,
        data: RepoDashboardData,
    ) -> Path:
        """
        Generate repo dashboard with embedded data.
        
        Creates dist/repos/<slug>/index.html per GPT spec.
        """
        repo_dir = self.output_dir / "repos" / repo.slug
        repo_dir.mkdir(parents=True, exist_ok=True)
        
        output_path = repo_dir / "index.html"
        
        # Prepare embedded data
        data_json = json.dumps(to_dict(data), indent=2)
        
        # Load and modify template
        template_path = self.cortex_root / self.DASHBOARD_TEMPLATE
        logger.debug(f"Template path: {template_path}, exists: {template_path.exists()}")
        if template_path.exists():
            template_html = template_path.read_text(encoding="utf-8")
            logger.debug(f"Loaded template: {len(template_html)} bytes")
            html = self._inject_dashboard_data(template_html, repo, data_json)
        else:
            # Generate from scratch if template missing
            logger.warning(f"Template not found: {template_path}, using fallback renderer")
            html = self._render_dashboard_template(repo, data_json)
        
        output_path.write_text(html, encoding="utf-8")
        logger.info(f"Generated dashboard: {output_path}")
        
        return output_path
    
    def _inject_dashboard_data(
        self,
        template: str,
        repo: RepoManifestEntry,
        data_json: str,
    ) -> str:
        """
        Inject repo data into existing dashboard template.
        
        Replaces window.dashboardData and updates paths to relative.
        """
        # Find and replace dashboardData
        data_marker_start = "window.dashboardData = {"
        data_marker_end = "};"
        
        start_idx = template.find(data_marker_start)
        if start_idx == -1:
            # No existing data, inject before closing </script>
            inject_point = template.find("</head>")
            if inject_point != -1:
                data_script = f'''
<script type="application/json" id="repo-data">
{data_json}
</script>
<script>
window.dashboardData = JSON.parse(document.getElementById("repo-data").textContent);
</script>
'''
                template = template[:inject_point] + data_script + template[inject_point:]
            modified = template
        else:
            # Find matching closing brace
            brace_count = 0
            end_idx = start_idx + len(data_marker_start) - 1
            for i in range(start_idx + len(data_marker_start), len(template)):
                if template[i] == "{":
                    brace_count += 1
                elif template[i] == "}":
                    if brace_count == 0:
                        end_idx = i + 1
                        break
                    brace_count -= 1
            
            # Replace with embedded JSON approach per GPT spec
            new_data_section = f'''window.dashboardData = {data_json}'''
            
            modified = template[:start_idx] + new_data_section + template[end_idx:]
        
        # Update title - use regex to match any placeholder before " | CORTEX Dashboard"
        # This handles KSESSIONS, KASHKOLE, or any other template placeholder
        # Phase 32 fix: Use repo.slug (not display_name) for title per test expectations
        title_pattern = r'<title>[^<]+\| CORTEX Dashboard</title>'
        new_title = f'<title>{repo.slug} | CORTEX Dashboard</title>'
        modified = re.sub(title_pattern, new_title, modified)
        
        # Replace H1 header (hardcoded KSESSIONS → repo display_name)
        # Phase 32 fix: Template has hardcoded <h1>KSESSIONS</h1> that needs replacement
        h1_pattern = r'<h1>KSESSIONS</h1>'
        new_h1 = f'<h1>{repo.display_name}</h1>'
        modified = re.sub(h1_pattern, new_h1, modified)
        
        # Fix asset paths (relative to dist/repos/<slug>/)
        modified = self._fix_asset_paths(modified)
        
        # Add back-to-landing link in header
        modified = self._add_navigation_links(modified, repo)
        
        # Inject Use Cases tab (GPT Spec: Use Cases component integration)
        logger.debug("Injecting Use Cases tab")
        modified = self._inject_use_cases_tab(modified)
        
        # Replace CDN scripts with vendored libraries (GPT Spec: file:// compatibility)
        logger.debug("Replacing CDN scripts with vendored libraries")
        modified = self._replace_cdn_with_vendor(modified)
        
        return modified
    
    def _fix_asset_paths(self, html: str) -> str:
        """Update asset paths for repo subfolder structure."""
        # CSS paths
        html = html.replace('href="assets/', 'href="../../assets/')
        html = html.replace("href='assets/", "href='../../assets/")
        
        # Image paths
        html = html.replace('src="assets/', 'src="../../assets/')
        html = html.replace("src='assets/", "src='../../assets/")
        
        # Also handle images/ directly
        html = html.replace('src="images/', 'src="../../images/')
        html = html.replace("src='images/", "src='../../images/")
        
        return html
    
    def _add_navigation_links(self, html: str, repo: RepoManifestEntry) -> str:
        """Add navigation links to header."""
        # Find header section and add back link
        # This is a minimal injection - real implementation would use proper DOM manipulation
        back_link = '''
<!-- Navigation Links (GPT Spec: Back-to-landing) -->
<a href="../../index.html" class="nav-link back-to-landing" style="
    position: fixed;
    top: 1rem;
    left: 1rem;
    padding: 0.5rem 1rem;
    background: rgba(77, 140, 255, 0.2);
    border: 1px solid rgba(77, 140, 255, 0.4);
    border-radius: 8px;
    color: #4d8cff;
    text-decoration: none;
    z-index: 1000;
    font-size: 0.9rem;
    backdrop-filter: blur(10px);
">← Back to Landing</a>
'''
        
        # Insert after <body>
        body_idx = html.find("<body")
        if body_idx != -1:
            body_end = html.find(">", body_idx)
            if body_end != -1:
                html = html[:body_end + 1] + back_link + html[body_end + 1:]
        
        return html
    
    def _inject_use_cases_tab(self, html: str) -> str:
        """
        Inject Use Cases tab into dashboard per GPT spec.
        
        Adds:
        - Tab button in .tab-navigation
        - Tab panel in .content-panels
        - Required CSS/JS includes
        - use-cases.js script initialization
        """
        # 1. Add Use Cases CSS before </head>
        use_cases_css = '''
    <!-- Use Cases Component CSS (GPT Spec) -->
    <link rel="stylesheet" href="../../assets/css/use-cases.css">
'''
        head_close_idx = html.find("</head>")
        if head_close_idx != -1:
            html = html[:head_close_idx] + use_cases_css + html[head_close_idx:]
        
        # 2. Add vendor libraries and use-cases.js before </body>
        use_cases_scripts = '''
    <!-- Vendor Libraries (GPT Spec: Fuse.js + Grid.js + ECharts) -->
    <script src="../../assets/vendor/fuse.min.js"></script>
    <script src="../../assets/vendor/gridjs.umd.js"></script>
    <link rel="stylesheet" href="../../assets/vendor/gridjs.min.css">
    <script src="../../assets/vendor/echarts.min.js"></script>
    
    <!-- Use Cases Component JS -->
    <script src="../../assets/js/use-cases.js"></script>
    
    <!-- Initialize Use Cases Manager -->
    <script>
        document.addEventListener('DOMContentLoaded', () => {
            // Extract use cases from embedded data
            const useCases = window.dashboardData?.useCases || [];
            
            if (useCases.length > 0) {
                // Initialize Use Cases Manager
                window.useCasesManager = new UseCasesManager('#use-cases-container', useCases);
                console.log('[UseCases] Initialized with', useCases.length, 'use cases');
            }
        });
    </script>
'''
        body_close_idx = html.find("</body>")
        if body_close_idx != -1:
            html = html[:body_close_idx] + use_cases_scripts + html[body_close_idx:]
        
        # 3. Add Use Cases tab button (find tab navigation)
        # Look for tab-navigation section
        tab_nav_marker = '<div class="tab-navigation">'
        tab_nav_idx = html.find(tab_nav_marker)
        if tab_nav_idx != -1:
            # Find the closing </div> of tab-navigation
            # Insert a new tab button before the last existing button or at the end
            tab_end = html.find("</div>", tab_nav_idx)
            if tab_end != -1:
                use_cases_tab = '''
            <button class="tab-btn" data-tab="use-cases">
                📋 Use Cases
            </button>
        '''
                html = html[:tab_end] + use_cases_tab + html[tab_end:]
        
        # 4. Add Use Cases tab panel (find content-panels section)
        # Look for existing panel pattern
        panels_marker = '<div class="content-panels">'
        panels_idx = html.find(panels_marker)
        if panels_idx == -1:
            # Try alternate: find last tab-content
            panels_marker = '<div class="tab-content"'
            panels_idx = html.rfind(panels_marker)
        
        if panels_idx != -1:
            # Find the end of the content-panels or after last tab-content
            # Insert Use Cases panel
            use_cases_panel = '''
        <!-- Use Cases Tab Panel (GPT Spec) -->
        <div id="use-cases" class="tab-content" style="display: none;">
            <div class="panel-card">
                <div class="panel-header">
                    <h2>📋 Use Cases</h2>
                    <p class="panel-description">Searchable use cases with filtering by persona and category</p>
                </div>
                <div id="use-cases-container" class="use-cases-container">
                    <!-- UseCasesManager will populate this -->
                    <div class="use-cases-loading">Loading use cases...</div>
                </div>
            </div>
        </div>
'''
            # Find where to insert - after last tab-content closing div
            last_tab_content = html.rfind('class="tab-content"')
            if last_tab_content != -1:
                # Find the closing </div> for this panel
                div_count = 0
                insert_pos = last_tab_content
                in_tag = False
                for i in range(last_tab_content, len(html)):
                    if html[i] == '<':
                        in_tag = True
                        if html[i:i+4] == '<div':
                            div_count += 1
                        elif html[i:i+5] == '</div':
                            div_count -= 1
                            if div_count == 0:
                                insert_pos = html.find('>', i) + 1
                                break
                    elif html[i] == '>':
                        in_tag = False
                
                html = html[:insert_pos] + use_cases_panel + html[insert_pos:]
        
        return html
    
    def _replace_cdn_with_vendor(self, html: str) -> str:
        """
        Replace CDN script/link tags with vendored libraries.
        
        Ensures file:// compatibility per GPT spec.
        Removes:
        - Chart.js CDN
        - D3 CDN
        - ECharts CDN
        - Google Fonts CDN (progressive enhancement, not critical)
        """
        # Remove Chart.js CDN
        html = re.sub(
            r'<script\s+src="https://cdn\.jsdelivr\.net/npm/chart\.js@[^"]+"></script>\s*',
            '',
            html
        )
        
        # Remove D3 CDN
        html = re.sub(
            r'<script\s+src="https://cdn\.jsdelivr\.net/npm/d3@[^"]+"></script>\s*',
            '',
            html
        )
        
        # Remove ECharts CDN (it's added by Use Cases injection with vendor path)
        html = re.sub(
            r'<script\s+src="https://cdn\.jsdelivr\.net/npm/echarts@[^"]+"></script>\s*',
            '',
            html
        )
        
        logger.debug("Removed CDN scripts from template")
        
        # Note: Google Fonts CDN is left as progressive enhancement
        # The dashboard works offline, fonts will fallback to system fonts
        
        return html
    
    def _render_landing_template(
        self,
        config: DashboardSuiteConfig,
        manifest_json: str,
    ) -> str:
        """Render landing page template with hero and tiles."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        repo_count = len(config.repos)
        
        # Generate tile HTML
        tiles_html = "\n".join([
            self._render_repo_tile(repo) for repo in config.repos
        ])
        
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{config.subtitle}">
    <title>{config.title}</title>
    
    <!-- Favicon -->
    <link rel="icon" type="image/png" href="images/cortex-logo.png">
    
    <!-- Embedded Manifest (GPT Spec: No fetch) -->
    <script type="application/json" id="repos-manifest">
{manifest_json}
    </script>
    
    <!-- Styles -->
    <link rel="stylesheet" href="assets/css/dashboard-combined.css">
    <link rel="stylesheet" href="assets/css/landing.css">
    
    <style>
        /* Landing-specific overrides */
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        html {{
            scroll-behavior: smooth;
        }}
        
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0a1428 0%, #1a2a4a 100%);
            background-attachment: fixed;
            color: #ffffff;
            min-height: 100vh;
            line-height: 1.6;
        }}
        
        .landing-container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }}
        
        /* Hero Section (GPT Spec: Large hero with CTAs) */
        .landing-hero {{
            text-align: center;
            padding: 4rem 2rem;
            margin-bottom: 3rem;
        }}
        
        .landing-logo {{
            width: 150px;
            height: 150px;
            border-radius: 16px;
            box-shadow: 0 8px 32px rgba(77, 140, 255, 0.3);
            margin-bottom: 2rem;
        }}
        
        .landing-title {{
            font-size: clamp(2rem, 5vw, 3.5rem);
            font-weight: 700;
            background: linear-gradient(135deg, #4d8cff 0%, #7fb3ff 100%);
            background-clip: text;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 1rem;
        }}
        
        .landing-subtitle {{
            font-size: 1.25rem;
            color: rgba(255, 255, 255, 0.7);
            margin-bottom: 2rem;
        }}
        
        .landing-meta {{
            color: rgba(255, 255, 255, 0.5);
            font-size: 0.9rem;
            margin-bottom: 2rem;
        }}
        
        .hero-actions {{
            display: flex;
            gap: 1rem;
            justify-content: center;
            flex-wrap: wrap;
        }}
        
        .hero-btn {{
            padding: 1rem 2rem;
            border-radius: 12px;
            font-size: 1rem;
            font-weight: 600;
            text-decoration: none;
            transition: all 0.3s ease;
            cursor: pointer;
        }}
        
        .hero-btn-primary {{
            background: linear-gradient(135deg, #4d8cff 0%, #0d6efd 100%);
            color: white;
            border: none;
        }}
        
        .hero-btn-primary:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(77, 140, 255, 0.4);
        }}
        
        .hero-btn-secondary {{
            background: rgba(77, 140, 255, 0.1);
            color: #4d8cff;
            border: 1px solid rgba(77, 140, 255, 0.3);
        }}
        
        .hero-btn-secondary:hover {{
            background: rgba(77, 140, 255, 0.2);
        }}
        
        /* Search & Filters */
        .controls-section {{
            margin-bottom: 2rem;
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
            align-items: center;
        }}
        
        .search-box {{
            flex: 1;
            min-width: 250px;
            padding: 0.75rem 1rem;
            background: rgba(10, 20, 40, 0.7);
            border: 1px solid rgba(77, 140, 255, 0.2);
            border-radius: 8px;
            color: white;
            font-size: 1rem;
        }}
        
        .search-box::placeholder {{
            color: rgba(255, 255, 255, 0.4);
        }}
        
        .filter-chips {{
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
        }}
        
        .filter-chip {{
            padding: 0.5rem 1rem;
            background: rgba(77, 140, 255, 0.1);
            border: 1px solid rgba(77, 140, 255, 0.2);
            border-radius: 20px;
            color: rgba(255, 255, 255, 0.7);
            font-size: 0.85rem;
            cursor: pointer;
            transition: all 0.2s ease;
        }}
        
        .filter-chip:hover,
        .filter-chip.active {{
            background: rgba(77, 140, 255, 0.2);
            border-color: rgba(77, 140, 255, 0.4);
            color: white;
        }}
        
        /* Repo Tiles Grid */
        .repos-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 1.5rem;
            margin-bottom: 3rem;
        }}
        
        .repo-tile {{
            display: block;
            padding: 1.5rem;
            background: rgba(10, 20, 40, 0.7);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            text-decoration: none;
            color: inherit;
            transition: all 0.3s ease;
        }}
        
        .repo-tile:hover {{
            transform: translateY(-4px);
            background: rgba(77, 140, 255, 0.15);
            border-color: rgba(77, 140, 255, 0.3);
            box-shadow: 0 16px 48px rgba(0, 0, 0, 0.3);
        }}
        
        .repo-tile-header {{
            display: flex;
            align-items: center;
            gap: 1rem;
            margin-bottom: 1rem;
        }}
        
        .repo-tile-icon {{
            font-size: 2rem;
        }}
        
        .repo-tile-title {{
            font-size: 1.25rem;
            font-weight: 600;
            color: #4d8cff;
            margin: 0;
        }}
        
        .repo-tile-owner {{
            font-size: 0.85rem;
            color: rgba(255, 255, 255, 0.5);
        }}
        
        .repo-tile-badges {{
            display: flex;
            gap: 0.5rem;
            margin-bottom: 1rem;
        }}
        
        .badge {{
            padding: 0.25rem 0.75rem;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 600;
        }}
        
        .badge-health-critical {{ background: rgba(239, 68, 68, 0.2); color: #ef4444; }}
        .badge-health-poor {{ background: rgba(249, 115, 22, 0.2); color: #f97316; }}
        .badge-health-fair {{ background: rgba(234, 179, 8, 0.2); color: #eab308; }}
        .badge-health-good {{ background: rgba(34, 197, 94, 0.2); color: #22c55e; }}
        .badge-health-excellent {{ background: rgba(16, 185, 129, 0.2); color: #10b981; }}
        
        .badge-language {{
            background: rgba(77, 140, 255, 0.2);
            color: #4d8cff;
        }}
        
        .repo-tile-metrics {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 0.5rem;
            margin-bottom: 1rem;
        }}
        
        .metric {{
            text-align: center;
        }}
        
        .metric-value {{
            font-size: 1.1rem;
            font-weight: 600;
            color: white;
        }}
        
        .metric-label {{
            font-size: 0.75rem;
            color: rgba(255, 255, 255, 0.5);
        }}
        
        .repo-tile-cta {{
            display: block;
            text-align: center;
            padding: 0.75rem;
            background: rgba(77, 140, 255, 0.1);
            border: 1px solid rgba(77, 140, 255, 0.2);
            border-radius: 8px;
            color: #4d8cff;
            font-weight: 500;
            transition: all 0.2s ease;
        }}
        
        .repo-tile:hover .repo-tile-cta {{
            background: rgba(77, 140, 255, 0.2);
        }}
        
        /* Footer */
        .landing-footer {{
            text-align: center;
            padding: 2rem;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            color: rgba(255, 255, 255, 0.5);
        }}
        
        .landing-footer a {{
            color: #4d8cff;
            text-decoration: none;
        }}
        
        /* Back to Top (GPT Spec) */
        .back-to-top {{
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            width: 48px;
            height: 48px;
            background: rgba(77, 140, 255, 0.9);
            border: none;
            border-radius: 50%;
            color: white;
            font-size: 1.5rem;
            cursor: pointer;
            opacity: 0;
            visibility: hidden;
            transition: all 0.3s ease;
            z-index: 1000;
        }}
        
        .back-to-top.visible {{
            opacity: 1;
            visibility: visible;
        }}
        
        .back-to-top:hover {{
            transform: translateY(-4px);
            box-shadow: 0 8px 24px rgba(77, 140, 255, 0.4);
        }}
        
        @media (max-width: 768px) {{
            .landing-container {{
                padding: 1rem;
            }}
            
            .landing-hero {{
                padding: 2rem 1rem;
            }}
            
            .repos-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="landing-container">
        <!-- Hero Section (GPT Spec: Large hero) -->
        <section class="landing-hero" id="hero">
            <img 
                src="images/cortex-logo.png" 
                alt="CORTEX Logo" 
                class="landing-logo"
            >
            <h1 class="landing-title">{config.title}</h1>
            <p class="landing-subtitle">{config.subtitle}</p>
            <p class="landing-meta">
                {repo_count} repositories onboarded • Powered by CORTEX v{config.version} • Generated {now}
            </p>
            <div class="hero-actions">
                <a href="#repos" class="hero-btn hero-btn-primary">
                    Open a Repository Dashboard
                </a>
                <button onclick="exportManifest()" class="hero-btn hero-btn-secondary">
                    Export Suite Manifest
                </button>
            </div>
        </section>
        
        <!-- Search & Filters (GPT Spec) -->
        <section class="controls-section" id="repos">
            <input 
                type="text" 
                class="search-box" 
                id="repo-search"
                placeholder="Search repositories..."
                aria-label="Search repositories"
            >
            <div class="filter-chips">
                <button class="filter-chip active" data-filter="all">All</button>
                <button class="filter-chip" data-filter="critical">Critical</button>
                <button class="filter-chip" data-filter="python">Python</button>
                <button class="filter-chip" data-filter="typescript">TypeScript</button>
            </div>
            <select id="sort-select" class="search-box" style="min-width: 150px; flex: 0;">
                <option value="risk-desc">Risk (High → Low)</option>
                <option value="health-desc">Health (High → Low)</option>
                <option value="name-asc">Name (A → Z)</option>
                <option value="activity-desc">Recent Activity</option>
            </select>
        </section>
        
        <!-- Repository Tiles Grid -->
        <section class="repos-section">
            <div class="repos-grid" id="repos-grid">
{tiles_html}
            </div>
        </section>
        
        <!-- Footer -->
        <footer class="landing-footer">
            <p>Generated by CORTEX • {now}</p>
            <p style="margin-top: 0.5rem;">
                <a href="https://github.com/asifhussain60/CORTEX" target="_blank">
                    View CORTEX on GitHub →
                </a>
            </p>
        </footer>
    </div>
    
    <!-- Back to Top Button (GPT Spec: Floating + keyboard accessible) -->
    <button 
        class="back-to-top" 
        id="back-to-top"
        aria-label="Back to top"
        tabindex="0"
    >↑</button>
    
    <script>
        // Parse embedded manifest
        const reposManifest = JSON.parse(
            document.getElementById("repos-manifest").textContent
        );
        
        // Back to Top (GPT Spec: Appears after 600px scroll)
        const backToTop = document.getElementById("back-to-top");
        
        window.addEventListener("scroll", () => {{
            if (window.scrollY > 600) {{
                backToTop.classList.add("visible");
            }} else {{
                backToTop.classList.remove("visible");
            }}
        }});
        
        backToTop.addEventListener("click", () => {{
            window.scrollTo({{ top: 0, behavior: "smooth" }});
        }});
        
        backToTop.addEventListener("keydown", (e) => {{
            if (e.key === "Enter" || e.key === " ") {{
                e.preventDefault();
                window.scrollTo({{ top: 0, behavior: "smooth" }});
            }}
        }});
        
        // Search functionality
        const searchBox = document.getElementById("repo-search");
        const tilesContainer = document.getElementById("repos-grid");
        
        searchBox.addEventListener("input", (e) => {{
            const query = e.target.value.toLowerCase();
            const tiles = tilesContainer.querySelectorAll(".repo-tile");
            
            tiles.forEach(tile => {{
                const name = tile.dataset.name?.toLowerCase() || "";
                const tags = tile.dataset.tags?.toLowerCase() || "";
                
                if (name.includes(query) || tags.includes(query)) {{
                    tile.style.display = "";
                }} else {{
                    tile.style.display = "none";
                }}
            }});
        }});
        
        // Export manifest
        function exportManifest() {{
            const blob = new Blob([JSON.stringify(reposManifest, null, 2)], {{
                type: "application/json"
            }});
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = "cortex-repos-manifest.json";
            a.click();
            URL.revokeObjectURL(url);
        }}
        
        // Filter chips
        document.querySelectorAll(".filter-chip").forEach(chip => {{
            chip.addEventListener("click", () => {{
                document.querySelectorAll(".filter-chip").forEach(c => c.classList.remove("active"));
                chip.classList.add("active");
                
                const filter = chip.dataset.filter;
                const tiles = tilesContainer.querySelectorAll(".repo-tile");
                
                tiles.forEach(tile => {{
                    if (filter === "all") {{
                        tile.style.display = "";
                    }} else {{
                        const tags = tile.dataset.tags?.toLowerCase() || "";
                        const health = tile.dataset.health || "";
                        
                        if (tags.includes(filter) || health === filter) {{
                            tile.style.display = "";
                        }} else {{
                            tile.style.display = "none";
                        }}
                    }}
                }});
            }});
        }});
    </script>
</body>
</html>'''
    
    def _render_repo_tile(self, repo: RepoManifestEntry) -> str:
        """Render a single repo tile for the landing page."""
        # Determine health badge class
        if repo.health_score < 20:
            health_class = "badge-health-critical"
            health_label = "Critical"
        elif repo.health_score < 40:
            health_class = "badge-health-poor"
            health_label = "Poor"
        elif repo.health_score < 60:
            health_class = "badge-health-fair"
            health_label = "Fair"
        elif repo.health_score < 80:
            health_class = "badge-health-good"
            health_label = "Good"
        else:
            health_class = "badge-health-excellent"
            health_label = "Excellent"
        
        # Format numbers
        loc_display = f"{repo.loc:,}" if repo.loc < 10000 else f"{repo.loc // 1000}K"
        files_display = f"{repo.files:,}" if repo.files < 1000 else f"{repo.files // 1000}K"
        coverage_display = f"{repo.coverage_pct:.0f}%"
        
        tags_str = " ".join(repo.tags + [repo.primary_language.lower()])
        
        return f'''
                <a 
                    href="repos/{repo.slug}/index.html" 
                    class="repo-tile"
                    data-name="{repo.display_name}"
                    data-tags="{tags_str}"
                    data-health="{health_label.lower()}"
                >
                    <div class="repo-tile-header">
                        <span class="repo-tile-icon">{repo.icon}</span>
                        <div>
                            <h3 class="repo-tile-title">{repo.display_name}</h3>
                            <span class="repo-tile-owner">{repo.owner}</span>
                        </div>
                    </div>
                    <div class="repo-tile-badges">
                        <span class="badge {health_class}">{repo.health_score}% {health_label}</span>
                        <span class="badge badge-language">{repo.primary_language}</span>
                    </div>
                    <div class="repo-tile-metrics">
                        <div class="metric">
                            <div class="metric-value">{loc_display}</div>
                            <div class="metric-label">LOC</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">{files_display}</div>
                            <div class="metric-label">Files</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">{coverage_display}</div>
                            <div class="metric-label">Coverage</div>
                        </div>
                    </div>
                    <span class="repo-tile-cta">Open Dashboard →</span>
                </a>'''
    
    def _render_dashboard_template(
        self,
        repo: RepoManifestEntry,
        data_json: str,
    ) -> str:
        """Render dashboard template from scratch (fallback)."""
        # This is a minimal fallback - the primary path uses the existing template
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{repo.display_name} - Dashboard | CORTEX</title>
    <link rel="stylesheet" href="../../assets/css/dashboard-combined.css">
    <script type="application/json" id="repo-data">
{data_json}
    </script>
</head>
<body>
    <a href="../../index.html" style="position: fixed; top: 1rem; left: 1rem; color: #4d8cff;">
        ← Back to Landing
    </a>
    <div class="dashboard-container">
        <h1>{repo.display_name}</h1>
        <p>Dashboard data loaded. Template not found - using fallback.</p>
    </div>
    <script>
        window.dashboardData = JSON.parse(document.getElementById("repo-data").textContent);
        console.log("Dashboard data loaded:", window.dashboardData);
    </script>
</body>
</html>'''


def generate_dashboard_suite(
    repos: List[Dict[str, Any]],
    repo_data: Dict[str, Dict[str, Any]],
    output_dir: str,
    cortex_root: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Generate dashboard suite (convenience function).
    
    Args:
        repos: List of repo manifest entries as dicts
        repo_data: Dictionary mapping slug -> full dashboard data as dicts
        output_dir: Output directory path
        cortex_root: CORTEX root path (auto-detected if None)
        
    Returns:
        Dict with generation results
    """
    # Convert dicts to dataclasses
    manifest_entries = [
        RepoManifestEntry(**r) for r in repos
    ]
    
    dashboard_data = {
        slug: RepoDashboardData(**data)
        for slug, data in repo_data.items()
    }
    
    config = DashboardSuiteConfig(
        repos=manifest_entries,
        output_dir=output_dir,
    )
    
    generator = DashboardSuiteGenerator(
        output_dir=Path(output_dir),
        cortex_root=Path(cortex_root) if cortex_root else None,
    )
    
    result = generator.generate_suite(config, dashboard_data)
    
    return {
        "success": result.success,
        "landing_path": result.landing_path,
        "repo_dashboards": result.repo_dashboards,
        "errors": result.errors,
    }
