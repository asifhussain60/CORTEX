"""
MCP Tools for Dashboard Repository Management.

Provides CRUD operations for the company/dashboards/ structure:
- Create new repo dashboards
- Update existing repo data
- List all registered repos
- Delete repo dashboards
- Validate registry integrity

AC-ID: DASHBOARD-MGMT-MCP-001
Authority: CORE-007 (MCP-first)
"""

import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from cortex.mcp.decorators import mcp_tool

logger = logging.getLogger(__name__)

# Default dashboard root (can be overridden)
DEFAULT_DASHBOARD_ROOT = Path("company/dashboards")


def _get_dashboard_root() -> Path:
    """Get the dashboard root directory."""
    return DEFAULT_DASHBOARD_ROOT


def _get_registry_path() -> Path:
    """Get the registry.json path."""
    return _get_dashboard_root() / "registry.json"


def _load_registry() -> Dict[str, Any]:
    """Load registry.json."""
    registry_path = _get_registry_path()
    if not registry_path.exists():
        return {"repos": [], "generated_at": None, "version": "1.0"}

    with open(registry_path, "r") as f:
        return json.load(f)


def _save_registry(registry: Dict[str, Any]) -> None:
    """Save registry.json."""
    registry["generated_at"] = datetime.now().isoformat()
    registry_path = _get_registry_path()

    with open(registry_path, "w") as f:
        json.dump(registry, f, indent=4)


@mcp_tool(
    name="cortex_dashboard_list_repos",
    description="List all registered repository dashboards",
    parameters={}
)
def cortex_dashboard_list_repos() -> Dict[str, Any]:
    """
    List all registered repository dashboards.

    Returns:
        Dict with:
        - success: bool
        - repos: List of repo summaries (slug, display_name, health_score)
        - count: Total number of repos
        - error: Optional error message
    """
    try:
        registry = _load_registry()
        repos = registry.get("repos", [])

        summaries = []
        for repo in repos:
            summaries.append({
                "slug": repo.get("slug"),
                "display_name": repo.get("display_name"),
                "health_score": repo.get("health_score", 0),
                "icon": repo.get("icon", "📁"),
                "dashboard_url": repo.get("dashboard_url", f"repos/{repo.get('slug')}/index.html"),
            })

        return {
            "success": True,
            "repos": summaries,
            "count": len(summaries),
            "error": None,
        }

    except Exception as e:
        logger.error(f"cortex_dashboard_list_repos failed: {e}", exc_info=True)
        return {
            "success": False,
            "repos": [],
            "count": 0,
            "error": str(e),
        }


@mcp_tool(
    name="cortex_dashboard_create_repo",
    description="Create a new repository dashboard from template",
    parameters={
        "slug": "string",
        "display_name": "string",
        "description": "string",
        "owner": "string",
        "primary_language": "string",
        "icon": "string",
        "tags": "array",
    }
)
def cortex_dashboard_create_repo(
    slug: str,
    display_name: str,
    description: str = "",
    owner: str = "Unknown",
    primary_language: str = "Python",
    icon: str = "📁",
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Create a new repository dashboard from template.

    Args:
        slug: URL-safe identifier (e.g., "my-repo")
        display_name: Human-readable name
        description: Repository description
        owner: Team/owner name
        primary_language: Primary programming language
        icon: Emoji icon
        tags: List of tags

    Returns:
        Dict with:
        - success: bool
        - dashboard_path: Path to created dashboard
        - error: Optional error message
    """
    try:
        if tags is None:
            tags = []

        dashboard_root = _get_dashboard_root()
        template_path = dashboard_root / "repos" / "_template"
        repo_path = dashboard_root / "repos" / slug

        # Check if already exists
        if repo_path.exists():
            return {
                "success": False,
                "dashboard_path": None,
                "error": f"Repository '{slug}' already exists",
            }

        # Copy template
        shutil.copytree(template_path, repo_path)

        # Update data.json with provided info
        data_path = repo_path / "data.json"
        with open(data_path, "r") as f:
            data = json.load(f)

        data["repo"] = {
            "slug": slug,
            "display_name": display_name,
            "owner": owner,
            "primary_language": primary_language,
            "version": "1.0.0",
            "last_analyzed_at": datetime.now().isoformat(),
        }
        data["overview"]["summary"] = description

        with open(data_path, "w") as f:
            json.dump(data, f, indent=4)

        # Add to registry
        registry = _load_registry()
        registry["repos"].append({
            "slug": slug,
            "display_name": display_name,
            "description": description,
            "owner": owner,
            "primary_language": primary_language,
            "health_score": 0,
            "risk_score": 0,
            "loc": 0,
            "files": 0,
            "coverage_pct": 0,
            "version": "1.0.0",
            "icon": icon,
            "tags": tags,
            "last_analyzed_at": datetime.now().isoformat(),
            "dashboard_url": f"repos/{slug}/index.html",
        })
        _save_registry(registry)

        return {
            "success": True,
            "dashboard_path": str(repo_path / "index.html"),
            "error": None,
        }

    except Exception as e:
        logger.error(f"cortex_dashboard_create_repo failed: {e}", exc_info=True)
        return {
            "success": False,
            "dashboard_path": None,
            "error": str(e),
        }


@mcp_tool(
    name="cortex_dashboard_update_repo",
    description="Update an existing repository dashboard data",
    parameters={
        "slug": "string",
        "data": "object",
    }
)
def cortex_dashboard_update_repo(
    slug: str,
    data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Update an existing repository dashboard data.

    Args:
        slug: Repository identifier
        data: Data to update (partial update supported)

    Returns:
        Dict with:
        - success: bool
        - error: Optional error message
    """
    try:
        dashboard_root = _get_dashboard_root()
        repo_path = dashboard_root / "repos" / slug
        data_path = repo_path / "data.json"

        if not repo_path.exists():
            return {
                "success": False,
                "error": f"Repository '{slug}' not found",
            }

        # Load existing data
        with open(data_path, "r") as f:
            existing_data = json.load(f)

        # Deep merge data
        def deep_merge(base: dict, update: dict) -> dict:
            for key, value in update.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    deep_merge(base[key], value)
                else:
                    base[key] = value
            return base

        merged_data = deep_merge(existing_data, data)

        with open(data_path, "w") as f:
            json.dump(merged_data, f, indent=4)

        # Update registry if metrics changed
        registry = _load_registry()
        for repo in registry.get("repos", []):
            if repo.get("slug") == slug:
                if "metrics" in data:
                    repo["health_score"] = data["metrics"].get("health_score", repo.get("health_score", 0))
                    repo["risk_score"] = data["metrics"].get("risk_score", repo.get("risk_score", 0))
                    repo["loc"] = data["metrics"].get("loc", repo.get("loc", 0))
                    repo["coverage_pct"] = data["metrics"].get("coverage_pct", repo.get("coverage_pct", 0))
                repo["last_analyzed_at"] = datetime.now().isoformat()
                break
        _save_registry(registry)

        return {
            "success": True,
            "error": None,
        }

    except Exception as e:
        logger.error(f"cortex_dashboard_update_repo failed: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
        }


@mcp_tool(
    name="cortex_dashboard_delete_repo",
    description="Delete a repository dashboard",
    parameters={
        "slug": "string",
        "confirm": "boolean",
    }
)
def cortex_dashboard_delete_repo(
    slug: str,
    confirm: bool = False,
) -> Dict[str, Any]:
    """
    Delete a repository dashboard.

    Args:
        slug: Repository identifier
        confirm: Must be True to proceed (safety check)

    Returns:
        Dict with:
        - success: bool
        - error: Optional error message
    """
    try:
        if not confirm:
            return {
                "success": False,
                "error": "Must set confirm=True to delete",
            }

        if slug == "_template":
            return {
                "success": False,
                "error": "Cannot delete _template folder",
            }

        dashboard_root = _get_dashboard_root()
        repo_path = dashboard_root / "repos" / slug

        if not repo_path.exists():
            return {
                "success": False,
                "error": f"Repository '{slug}' not found",
            }

        # Remove folder
        shutil.rmtree(repo_path)

        # Remove from registry
        registry = _load_registry()
        registry["repos"] = [r for r in registry.get("repos", []) if r.get("slug") != slug]
        _save_registry(registry)

        return {
            "success": True,
            "error": None,
        }

    except Exception as e:
        logger.error(f"cortex_dashboard_delete_repo failed: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
        }


@mcp_tool(
    name="cortex_dashboard_validate",
    description="Validate dashboard registry and folder structure",
    parameters={}
)
def cortex_dashboard_validate() -> Dict[str, Any]:
    """
    Validate dashboard registry and folder structure.

    Checks:
    - All registry entries have corresponding folders
    - All folders have required files (index.html, data.json)
    - Asset paths are correct

    Returns:
        Dict with:
        - success: bool
        - valid: bool
        - issues: List of validation issues
        - error: Optional error message
    """
    try:
        dashboard_root = _get_dashboard_root()
        registry = _load_registry()
        issues = []

        # Check each registry entry
        for repo in registry.get("repos", []):
            slug = repo.get("slug")
            repo_path = dashboard_root / "repos" / slug

            if not repo_path.exists():
                issues.append(f"Registry entry '{slug}' has no folder at repos/{slug}/")
                continue

            # Check required files
            if not (repo_path / "index.html").exists():
                issues.append(f"repos/{slug}/ missing index.html")
            if not (repo_path / "data.json").exists():
                issues.append(f"repos/{slug}/ missing data.json")

        # Check for orphan folders
        repos_path = dashboard_root / "repos"
        if repos_path.exists():
            registry_slugs = {r.get("slug") for r in registry.get("repos", [])}
            for folder in repos_path.iterdir():
                if folder.is_dir() and folder.name not in registry_slugs and folder.name != "_template":
                    issues.append(f"Orphan folder: repos/{folder.name}/ not in registry")

        # Check assets
        assets_path = dashboard_root / "assets"
        if not assets_path.exists():
            issues.append("Missing assets/ folder")
        else:
            required_assets = ["css/variables.css", "css/base.css", "images/cortex-logo-200.png"]
            for asset in required_assets:
                if not (assets_path / asset).exists():
                    issues.append(f"Missing asset: assets/{asset}")

        return {
            "success": True,
            "valid": len(issues) == 0,
            "issues": issues,
            "error": None,
        }

    except Exception as e:
        logger.error(f"cortex_dashboard_validate failed: {e}", exc_info=True)
        return {
            "success": False,
            "valid": False,
            "issues": [],
            "error": str(e),
        }
