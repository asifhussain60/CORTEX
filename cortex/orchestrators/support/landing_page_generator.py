"""
Landing Page Generator for Universal Repository Onboarding.

Generates and maintains the central hub page with glassmorphism repository tiles.
Auto-updates when new repositories are onboarded.

Authority: cortex-architect.prompt.md v8.0
Author: Asif Hussain
AC-ID: AC-UNIVERSAL-ONBOARD-002
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


class LandingPageGenerator:
    """
    Generate and maintain the landing page hub for onboarded repositories.
    
    Features:
    - Glassmorphism hero section with CORTEX branding
    - Auto-updating repository tiles grid
    - Registry-driven (registry.json)
    - Health score and status indicators
    - Responsive mobile-first design
    
    Example:
        >>> generator = LandingPageGenerator()
        >>> generator.add_repo_to_registry({
        ...     "name": "kashkole",
        ...     "title": "KASHKOLE",
        ...     "description": "Islamic Knowledge Platform",
        ...     "health_score": 35,
        ...     "dashboard_path": "kashkole/dashboard.html"
        ... })
        >>> generator.regenerate_landing_page()
    """
    
    def __init__(
        self,
        dashboards_root: Optional[Path] = None,
    ):
        """
        Initialize Landing Page Generator.
        
        Args:
            dashboards_root: Root path for dashboards (company/dashboards/)
        """
        cortex_root = Path(__file__).parent.parent.parent.parent
        self.dashboards_root = dashboards_root or cortex_root / "company" / "dashboards"
        self.registry_path = self.dashboards_root / "registry.json"
        self.landing_path = self.dashboards_root / "index.html"
        self.assets_path = self.dashboards_root / "assets"
    
    def add_repo_to_registry(
        self,
        repo_name: Optional[str] = None,
        title: Optional[str] = None,
        description: str = "",
        icon: str = "📦",
        health_score: int = 0,
        confidence_score: int = 50,
        tech_stack: Optional[List[str]] = None,
        repo_info: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Add or update repository in the registry.
        
        Args:
            repo_name: Repository identifier (required if repo_info not provided)
            title: Display name
            description: Short description
            icon: Emoji icon
            health_score: Health score (0-100)
            confidence_score: Analysis confidence (0-100)
            tech_stack: List of technologies
            repo_info: Alternative dict with all info (legacy support)
                
        Returns:
            True if successful
        """
        try:
            registry = self._load_registry()
            
            # Support both dict and keyword args
            if repo_info:
                name = repo_info.get("name")
                entry_title = repo_info.get("title", name.upper() if name else "")
                entry_desc = repo_info.get("description", "")
                entry_icon = repo_info.get("icon", "📦")
                entry_health = repo_info.get("health_score", 0)
                entry_confidence = repo_info.get("confidence_score", repo_info.get("confidence", 50))
                entry_tech = repo_info.get("tech_stack", [])
            else:
                name = repo_name
                entry_title = title or (name.upper() if name else "")
                entry_desc = description
                entry_icon = icon
                entry_health = health_score
                entry_confidence = confidence_score
                entry_tech = tech_stack or []
            
            if not name:
                logger.error("Repository name is required")
                return False
            
            # Find existing or create new
            existing_idx = None
            for i, repo in enumerate(registry.get("repos", [])):
                if repo.get("name") == name:
                    existing_idx = i
                    break
            
            # Prepare repo entry
            entry = {
                "name": name,
                "title": entry_title,
                "description": entry_desc,
                "health_score": entry_health,
                "health_category": self._get_health_category(entry_health),
                "confidence": entry_confidence,
                "dashboard_path": f"{name}/dashboard.html",
                "icon": entry_icon,
                "tech_stack": entry_tech,
                "onboarded_at": datetime.now().isoformat() if existing_idx is None else registry["repos"][existing_idx].get("onboarded_at", datetime.now().isoformat()),
                "updated_at": datetime.now().isoformat(),
            }
            
            if existing_idx is not None:
                registry["repos"][existing_idx] = entry
                logger.info(f"Updated repo in registry: {entry['name']}")
            else:
                registry["repos"].append(entry)
                logger.info(f"Added repo to registry: {entry['name']}")
            
            self._save_registry(registry)
            return True
            
        except Exception as e:
            logger.error(f"Failed to add repo to registry: {e}", exc_info=True)
            return False
    
    def remove_repo_from_registry(self, name: str) -> bool:
        """
        Remove repository from registry.
        
        Args:
            name: Repository name to remove
            
        Returns:
            True if removed, False if not found
        """
        try:
            registry = self._load_registry()
            original_len = len(registry.get("repos", []))
            registry["repos"] = [
                r for r in registry.get("repos", [])
                if r.get("name") != name
            ]
            
            if len(registry["repos"]) < original_len:
                self._save_registry(registry)
                logger.info(f"Removed repo from registry: {name}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to remove repo from registry: {e}", exc_info=True)
            return False
    
    def get_registry(self) -> Dict[str, Any]:
        """Get current registry contents."""
        return self._load_registry()
    
    def list_repos(self) -> List[Dict[str, Any]]:
        """
        List all onboarded repositories.
        
        Returns:
            List of repository info dicts
        """
        registry = self._load_registry()
        return registry.get("repos", [])
    
    def regenerate_landing_page(self) -> Path:
        """
        Regenerate the landing page from registry.
        
        Returns:
            Path to generated index.html
        """
        registry = self._load_registry()
        repos = registry.get("repos", [])
        
        # Sort by most recent first
        repos.sort(key=lambda r: r.get("updated_at", ""), reverse=True)
        
        html = self._generate_landing_html(repos)
        
        self.landing_path.write_text(html, encoding='utf-8')
        logger.info(f"Regenerated landing page: {self.landing_path}")
        
        return self.landing_path
    
    def _load_registry(self) -> Dict[str, Any]:
        """Load registry from JSON file."""
        if self.registry_path.exists():
            return json.loads(self.registry_path.read_text(encoding='utf-8'))
        return {
            "version": "1.0.0",
            "created": datetime.now().isoformat(),
            "repos": [],
        }
    
    def _save_registry(self, registry: Dict[str, Any]) -> None:
        """Save registry to JSON file."""
        registry["updated"] = datetime.now().isoformat()
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self.registry_path.write_text(
            json.dumps(registry, indent=2),
            encoding='utf-8'
        )
    
    def _get_health_category(self, score: int) -> str:
        """Get health category from score."""
        if score >= 80:
            return "excellent"
        elif score >= 60:
            return "good"
        elif score >= 40:
            return "warning"
        else:
            return "critical"
    
    def _generate_landing_html(self, repos: List[Dict[str, Any]]) -> str:
        """Generate complete landing page HTML."""
        
        # Generate repo tiles
        if repos:
            tiles_html = self._generate_repo_tiles(repos)
        else:
            tiles_html = self._generate_empty_state()
        
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="CORTEX Onboarding Dashboard Hub - Security-analyzed repository dashboards">
    <title>CORTEX Onboarding Hub | Repository Dashboards</title>
    
    <!-- Favicon -->
    <link rel="icon" type="image/png" href="assets/images/CORTEX-logo-64.png">
    
    <!-- Styles -->
    <link rel="stylesheet" href="assets/css/dashboard-combined.css">
    <link rel="stylesheet" href="assets/css/landing.css">
    
    <style>
        /* Additional inline styles for landing page */
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
            background: linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 100%);
            background-attachment: fixed;
            color: #ffffff;
            min-height: 100vh;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }}
        
        @media (max-width: 768px) {{
            .container {{
                padding: 1rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Hero Section -->
        <section class="landing-hero">
            <img src="assets/images/CORTEX-logo-512.png" 
                 alt="CORTEX Logo" 
                 class="landing-logo"
                 width="150" 
                 height="150">
            <h1 class="landing-title">CORTEX Onboarding Hub</h1>
            <p class="landing-subtitle">
                Security-Analyzed Repository Dashboards
            </p>
            <p style="color: rgba(255,255,255,0.5); margin-top: 1rem; font-size: 0.9rem;">
                {len(repos)} repositories onboarded • Powered by CORTEX v8.0
            </p>
        </section>
        
        <!-- Repository Tiles Grid -->
        <section class="repos-section">
            <div class="repos-grid">
                {tiles_html}
            </div>
        </section>
        
        <!-- Footer -->
        <footer class="landing-footer">
            <p>Generated by CORTEX • {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
            <p style="margin-top: 0.5rem;">
                <a href="https://github.com/asifhussain60/CORTEX" 
                   style="color: #00d4ff; text-decoration: none;"
                   target="_blank">
                    View CORTEX on GitHub →
                </a>
            </p>
        </footer>
    </div>
    
    <!-- Tile hover sound effect (optional) -->
    <script>
        // Add subtle interaction effects
        document.querySelectorAll('.repo-tile').forEach(tile => {{
            tile.addEventListener('mouseenter', () => {{
                tile.style.zIndex = '10';
            }});
            tile.addEventListener('mouseleave', () => {{
                tile.style.zIndex = '1';
            }});
        }});
    </script>
</body>
</html>'''
    
    def _generate_repo_tiles(self, repos: List[Dict[str, Any]]) -> str:
        """Generate HTML for repository tiles."""
        tiles = []
        
        for repo in repos:
            health_score = repo.get("health_score", 0)
            health_category = repo.get("health_category", self._get_health_category(health_score))
            tech_stack = repo.get("tech_stack", [])
            
            # Tech stack badges
            tech_badges = ""
            if tech_stack:
                badges = [f'<span style="background: rgba(255,255,255,0.1); padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.75rem; margin-right: 0.25rem;">{tech}</span>' for tech in tech_stack[:3]]
                tech_badges = f'<div style="margin-top: 0.75rem;">{" ".join(badges)}</div>'
            
            tile = f'''
                <a href="{repo.get('dashboard_path', '#')}" class="repo-tile">
                    <span class="repo-tile-icon">{repo.get('icon', '📦')}</span>
                    <h3 class="repo-tile-title">{repo.get('title', repo.get('name', 'Unknown'))}</h3>
                    <p class="repo-tile-description">{repo.get('description', 'No description available')}</p>
                    {tech_badges}
                    <div class="repo-tile-meta">
                        <span class="repo-tile-health {health_category}">
                            <span style="font-size: 1.25rem;">{'🟢' if health_score >= 60 else '🟡' if health_score >= 40 else '🔴'}</span>
                            {health_score}% Health
                        </span>
                        <span class="repo-tile-date">{self._format_date(repo.get('onboarded_at', ''))}</span>
                    </div>
                </a>
            '''
            tiles.append(tile)
        
        return '\n'.join(tiles)
    
    def _generate_empty_state(self) -> str:
        """Generate empty state HTML when no repos onboarded."""
        return '''
            <div class="empty-state" style="grid-column: 1 / -1;">
                <div class="empty-state-icon">📂</div>
                <h3 class="empty-state-title">No Repositories Onboarded</h3>
                <p class="empty-state-description">
                    Use the CORTEX MCP tool <code style="background: rgba(255,255,255,0.1); padding: 0.2rem 0.5rem; border-radius: 4px;">cortex_onboard_repository</code> 
                    to analyze and onboard your first repository.
                </p>
                <div style="margin-top: 1.5rem; font-family: monospace; font-size: 0.85rem; color: rgba(255,255,255,0.5);">
                    Example: cortex_onboard_repository(repo_path="/path/to/repo")
                </div>
            </div>
        '''
    
    def _format_date(self, iso_date: str) -> str:
        """Format ISO date to human readable."""
        if not iso_date:
            return "Unknown"
        try:
            dt = datetime.fromisoformat(iso_date.replace('Z', '+00:00'))
            return dt.strftime('%b %d, %Y')
        except (ValueError, AttributeError, TypeError):
            return iso_date[:10] if len(iso_date) >= 10 else iso_date


# Singleton instance
_landing_page_generator = None


def get_landing_page_generator() -> LandingPageGenerator:
    """Get or create singleton LandingPageGenerator."""
    global _landing_page_generator
    if _landing_page_generator is None:
        _landing_page_generator = LandingPageGenerator()
    return _landing_page_generator
