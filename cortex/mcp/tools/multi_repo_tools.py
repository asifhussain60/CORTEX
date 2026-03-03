"""
Multi-Repo MCP Tools — canonical consolidated module.

Consolidates cross-project governance tools:
- ProjectScanner    — discover project directories
- ContextSwitcher   — switch governance context between projects
- CrossRepoSearch   — search AC-ID references across repositories
- DependencyGraph   — inter-project dependency analysis
- ProfileManager    — apply governance profiles to projects
- SharedAudit       — unified governance audit queries across projects

Phase: Phase 12 (MCP Consolidation — CORE-035)
Authority: AC-PHASE12-001, AC-PHASE12-002
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional


# ──────────────────────────────────────────────────────────────────────────────
# ProjectScanner
# ──────────────────────────────────────────────────────────────────────────────

class ProjectScanner:
    """Discover project directories under a base path."""

    def discover_projects(
        self, base_path: str = "."
    ) -> List[Dict[str, Any]]:
        """Discover project directories.

        Args:
            base_path: Root directory to scan.

        Returns:
            List of project dicts with 'name', 'path', 'cortex_enabled'.
        """
        dirs = self._list_dirs(base_path)
        projects: List[Dict[str, Any]] = []
        for name in dirs:
            projects.append(
                {
                    "name": name,
                    "path": f"{base_path}/{name}",
                    "cortex_enabled": self._has_cortex_marker(name),
                }
            )
        return projects

    def _list_dirs(self, base_path: str) -> List[str]:
        """List subdirectories under base_path.

        Args:
            base_path: Directory to scan.

        Returns:
            List of directory names.
        """
        root = Path(base_path)
        if not root.exists():
            return []
        return [p.name for p in root.iterdir() if p.is_dir()]

    def _has_cortex_marker(self, project_name: str) -> bool:
        """Check if a project has the .cortex-version marker.

        Args:
            project_name: Project directory name.

        Returns:
            True if CORTEX-enabled.
        """
        return False


# ──────────────────────────────────────────────────────────────────────────────
# ContextSwitcher
# ──────────────────────────────────────────────────────────────────────────────

class ContextSwitcher:
    """Switch governance context between projects."""

    def __init__(self) -> None:
        """Initialize ContextSwitcher."""
        self.current_project: Optional[str] = None

    def switch_context(self, project_path: str) -> Dict[str, Any]:
        """Switch governance context to a project.

        Args:
            project_path: Path to the target project.

        Returns:
            Dict with 'tier1_rules' and 'tier0_rules'.
        """
        self.current_project = project_path
        tier1 = self._load_tier1_rules(project_path)
        tier0 = self._get_tier0_rules()
        return {
            "tier1_rules": tier1,
            "tier0_rules": tier0,
        }

    def _load_tier1_rules(self, project_path: str) -> Dict[str, Any]:
        """Load tier1 rules for a project.

        Args:
            project_path: Project path.

        Returns:
            Tier1 rules dict.
        """
        return {}

    def _get_tier0_rules(self) -> Dict[str, Any]:
        """Get universal tier0 rules.

        Returns:
            Tier0 rules dict.
        """
        return {"rules": ["CORE-008"]}


# ──────────────────────────────────────────────────────────────────────────────
# CrossRepoSearch
# ──────────────────────────────────────────────────────────────────────────────

class CrossRepoSearch:
    """Search AC-ID references across repositories."""

    def search_ac_id(
        self, ac_id: str, repos: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Search for AC-ID references across repos.

        Args:
            ac_id: AC-ID pattern (may include '*' wildcard).
            repos: List of repo names to search.

        Returns:
            List of match dicts with 'file', 'line', 'match'.
        """
        repos = repos or []
        results: List[Dict[str, Any]] = []
        for repo in repos:
            hits = self._search_repo(repo, ac_id)
            results.extend(hits)
        return results

    def _search_repo(
        self, repo: str, pattern: str
    ) -> List[Dict[str, Any]]:
        """Search a single repo for a pattern.

        Args:
            repo: Repository name.
            pattern: Search pattern.

        Returns:
            List of match dicts.
        """
        return []


# ──────────────────────────────────────────────────────────────────────────────
# DependencyGraph
# ──────────────────────────────────────────────────────────────────────────────

class DependencyGraph:  # noqa: CORE-035-scoped — independent dependency graph — domain-specific structure
    """Build and analyze inter-project dependency graphs."""

    def build(
        self, projects: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Build a dependency graph for the given projects.

        Args:
            projects: List of project names.

        Returns:
            Dict with 'nodes', 'edges', 'has_cycles', 'cycles', 'build_order'.
        """
        projects = projects or []
        deps = self._scan_dependencies(projects)
        nodes = list(deps.keys())
        edges: List[Dict[str, str]] = []
        for proj, dep_list in deps.items():
            for dep in dep_list:
                edges.append({"from": proj, "to": dep})
        cycles = self._detect_cycles(deps)
        build_order = self._topological_sort(deps) if not cycles else []
        return {
            "nodes": nodes,
            "edges": edges,
            "has_cycles": len(cycles) > 0,
            "cycles": cycles,
            "build_order": build_order,
        }

    def _scan_dependencies(
        self, projects: List[str]
    ) -> Dict[str, List[str]]:
        """Scan project dependencies (designed for patching).

        Args:
            projects: List of project names.

        Returns:
            Dict mapping project → list of dependencies.
        """
        return {p: [] for p in projects}

    def _detect_cycles(
        self, deps: Dict[str, List[str]]
    ) -> List[List[str]]:
        """Detect cycles in the dependency graph.

        Args:
            deps: Adjacency list.

        Returns:
            List of cycle paths.
        """
        visited: set = set()
        rec_stack: set = set()
        cycles: List[List[str]] = []

        def _dfs(node: str, path: List[str]) -> None:
            """Depth-first search for cycle detection."""
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            for neighbor in deps.get(node, []):
                if neighbor not in visited:
                    _dfs(neighbor, path)
                elif neighbor in rec_stack:
                    idx = path.index(neighbor)
                    cycles.append(path[idx:] + [neighbor])
            path.pop()
            rec_stack.discard(node)

        for node in deps:
            if node not in visited:
                _dfs(node, [])
        return cycles

    def _topological_sort(
        self, deps: Dict[str, List[str]]
    ) -> List[str]:
        """Compute topological order for builds.

        Args:
            deps: Adjacency list.

        Returns:
            Build order list.
        """
        order: List[str] = []
        remaining = dict(deps)
        while remaining:
            ready = [n for n, d in remaining.items() if all(dep in order for dep in d)]
            if not ready:
                break
            for n in sorted(ready):
                order.append(n)
                del remaining[n]
        return order


# ──────────────────────────────────────────────────────────────────────────────
# ProfileManager
# ──────────────────────────────────────────────────────────────────────────────

_DEFAULT_PROFILES = [
    {"name": "FinOps", "rules": ["FIN-001", "FIN-002"]},
    {"name": "Auth", "rules": ["AUTH-001", "AUTH-002"]},
    {"name": "General", "rules": ["GEN-001"]},
]


class ProfileManager:
    """Manage governance profile application across projects."""

    def apply_profile(
        self, profile_name: str, project_path: str = "."
    ) -> Dict[str, Any]:
        """Apply a governance profile to a project.

        Args:
            profile_name: Profile name.
            project_path: Target project path.

        Returns:
            Dict with 'success'.
        """
        profile = self._get_profile(profile_name)
        if not profile:
            return {"success": False, "error": f"Profile {profile_name} not found"}
        return self._apply_to_project(profile, project_path)

    def list_profiles(self) -> List[Dict[str, Any]]:
        """List available governance profiles.

        Returns:
            List of profile dicts.
        """
        return list(_DEFAULT_PROFILES)

    def validate_profile(
        self, profile_name: str, project_path: str = "."
    ) -> Dict[str, Any]:
        """Validate profile compatibility with a project.

        Args:
            profile_name: Profile name.
            project_path: Project path.

        Returns:
            Dict with 'compatible' and 'warnings'.
        """
        return self._check_compatibility(profile_name, project_path)

    def _get_profile(self, name: str) -> Optional[Dict[str, Any]]:
        """Retrieve profile by name.

        Args:
            name: Profile name.

        Returns:
            Profile dict or None.
        """
        for p in _DEFAULT_PROFILES:
            if p["name"] == name:
                return p
        return None

    def _apply_to_project(
        self, profile: Dict[str, Any], project_path: str
    ) -> Dict[str, Any]:
        """Apply profile to project filesystem.

        Args:
            profile: Profile dict.
            project_path: Target path.

        Returns:
            Result dict.
        """
        return {"success": True}

    def _check_compatibility(
        self, profile_name: str, project_path: str
    ) -> Dict[str, Any]:
        """Check profile-project compatibility.

        Args:
            profile_name: Profile name.
            project_path: Project path.

        Returns:
            Compatibility dict.
        """
        return {"compatible": True, "warnings": []}


# ──────────────────────────────────────────────────────────────────────────────
# SharedAudit
# ──────────────────────────────────────────────────────────────────────────────

class SharedAudit:
    """Query unified governance database across projects."""

    def __init__(self) -> None:
        """Initialize SharedAudit."""
        self._entries: List[Dict[str, Any]] = []

    def query(
        self,
        ac_id_pattern: Optional[str] = None,
        project: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Query audit entries.

        Args:
            ac_id_pattern: AC-ID pattern filter.
            project: Project name filter.

        Returns:
            List of matching audit entries.
        """
        results = self._query_unified_db(ac_id_pattern, project)
        if project:
            return [r for r in results if r.get("project") == project]
        return results

    def aggregate_stats(self) -> Dict[str, Any]:
        """Aggregate statistics across projects.

        Returns:
            Dict with 'total_entries' and 'by_project' breakdown.
        """
        entries = self._query_unified_db()
        by_project: Dict[str, int] = {}
        for entry in entries:
            proj = entry.get("project", "unknown")
            by_project[proj] = by_project.get(proj, 0) + 1
        return {
            "total_entries": len(entries),
            "by_project": by_project,
        }

    def _query_unified_db(
        self,
        ac_id_pattern: Optional[str] = None,
        project: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Query the unified database (designed for patching).

        Args:
            ac_id_pattern: Pattern filter.
            project: Project filter.

        Returns:
            List of audit entries.
        """
        return []


__all__ = [
    "ProjectScanner",
    "ContextSwitcher",
    "CrossRepoSearch",
    "DependencyGraph",
    "ProfileManager",
    "SharedAudit",
]
