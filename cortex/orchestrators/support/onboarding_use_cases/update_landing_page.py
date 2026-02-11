"""
Update Landing Page Use Case (Phase 54-A S1)

AC_START: AC-PHASE54A-S1-UC06
Description: Update landing page hub with repository tiles
Authority: phase-54-A-incremental-onboarding-refactor.yaml, S1 task 6
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

from cortex.brain.core.result import Err, Ok, Result


@dataclass
class RepositoryTile:
    """Repository tile for landing page."""
    name: str
    slug: str
    description: str
    color: str
    icon: str
    link: str


class UpdateLandingPageUseCase:
    """Update landing page hub (SOLID: Single Responsibility)."""

    def execute(
        self,
        repo_name: str,
        repo_slug: str,
        dashboard_path: Path,
        landing_page_path: Path,
    ) -> Result[Path]:
        """
        Update landing page with new repository tile.

        Args:
            repo_name: Repository name
            repo_slug: Repository slug (for URL)
            dashboard_path: Path to dashboard HTML/JSON
            landing_page_path: Path to landing page HTML

        Returns:
            Result containing updated landing page path or error
        """
        try:
            if not landing_page_path.exists():
                return Err(f"Landing page not found: {landing_page_path}")

            # Read current landing page
            content = landing_page_path.read_text()

            # Create repository tile
            tile = RepositoryTile(
                name=repo_name,
                slug=repo_slug,
                description=f"Onboarded repository: {repo_name}",
                color=self._generate_color(repo_name),
                icon=self._generate_icon(repo_name),
                link=self._generate_link(repo_slug, dashboard_path),
            )

            # Add tile to landing page
            updated_content = self._insert_tile(content, tile)

            # Write updated landing page
            landing_page_path.write_text(updated_content)

            return Ok(landing_page_path)

        except Exception as e:
            return Err(f"Failed to update landing page: {str(e)}")

    def _generate_color(self, repo_name: str) -> str:
        """Generate color for repository tile."""
        colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#FFA07A", "#98D8C8"]
        hash_val = sum(ord(c) for c in repo_name)
        return colors[hash_val % len(colors)]

    def _generate_icon(self, repo_name: str) -> str:
        """Generate icon for repository tile."""
        if "test" in repo_name.lower():
            return "[TEST]"  # Use ASCII instead of emoji for encoding compatibility
        if "doc" in repo_name.lower():
            return "[DOCS]"
        if "api" in repo_name.lower():
            return "[API]"
        return "[PKG]"

    def _generate_link(self, repo_slug: str, dashboard_path: Path) -> str:
        """Generate link for repository tile."""
        # Assuming dashboards are in dashboards/ directory
        return f"dashboards/{repo_slug}/index.html"

    def _insert_tile(self, content: str, tile: RepositoryTile) -> str:
        """Insert tile HTML into landing page."""
        tile_html = f"""
    <div class="repository-tile" data-slug="{tile.slug}">
        <div class="tile-header" style="background-color: {tile.color}">
            <span class="tile-icon">{tile.icon}</span>
            <h3 class="tile-name">{tile.name}</h3>
        </div>
        <div class="tile-body">
            <p class="tile-description">{tile.description}</p>
        </div>
        <div class="tile-footer">
            <a href="{tile.link}" class="tile-link">View Dashboard →</a>
        </div>
    </div>
"""

        # Insert before closing </div> or </main>
        if "</main>" in content:
            return content.replace("</main>", tile_html + "</main>")
        elif content.count("</div>") > 0:
            return content.rstrip() + tile_html
        else:
            return content + tile_html

    def create_registry_entry(
        self,
        repo_name: str,
        repo_slug: str,
        dashboard_url: str,
    ) -> Result[Dict[str, Any]]:
        """
        Create registry entry for onboarded repository.

        Args:
            repo_name: Repository name
            repo_slug: Repository slug
            dashboard_url: URL to dashboard

        Returns:
            Result containing registry entry or error
        """
        try:
            entry = {
                "id": repo_slug,
                "name": repo_name,
                "slug": repo_slug,
                "dashboard_url": dashboard_url,
                "onboarded_at": self._get_timestamp(),
                "status": "active",
            }
            return Ok(entry)

        except Exception as e:
            return Err(f"Failed to create registry entry: {str(e)}")

    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()


# AC_COMPLETE: AC-PHASE54A-S1-UC06 ✅
