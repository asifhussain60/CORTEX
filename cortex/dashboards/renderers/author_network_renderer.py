"""
Author Network Renderer for CORTEX Visualization System.

Generates developer collaboration network visualizations showing:
- Author nodes sized by contribution count
- Edges representing collaboration (shared files)
- Expertise areas based on file types/domains

Authority: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings)
Phase: 14 - LENS Dashboard Implementation
Task: 008 - Author Network Renderer
AC-ID: LENS-DASH-003
"""

import json
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


@dataclass
class AuthorNode:
    """
    Represents an author node in the collaboration network.

    Attributes:
        id: Unique author identifier (email or name)
        name: Display name
        commit_count: Number of commits by author
        file_count: Number of unique files touched
        expertise_areas: List of domains/technologies
        avatar_url: Optional avatar URL
    """
    id: str
    name: str
    commit_count: int
    file_count: int
    expertise_areas: List[str]
    avatar_url: str = ""


@dataclass
class CollaborationEdge:
    """
    Represents collaboration between two authors.

    Attributes:
        source: Source author ID
        target: Target author ID
        strength: Number of shared files
        shared_files: List of file paths they both modified
    """
    source: str
    target: str
    strength: int
    shared_files: List[str]


@dataclass
class AuthorNetworkVisualization:
    """
    Complete author network visualization data.

    Attributes:
        nodes: List of author nodes
        edges: List of collaboration edges
        statistics: Network statistics
    """
    nodes: List[Dict]
    edges: List[Dict]
    statistics: Dict[str, any]


class AuthorNetworkRenderer:
    """
    Renders developer collaboration network from Git analysis.

    Creates force-directed graph where:
    - Nodes = Authors (sized by commits)
    - Edges = Shared files (weighted by count)
    - Colors = Expertise areas

    Example:
        >>> renderer = AuthorNetworkRenderer()
        >>> git_data = {"commits": [...]}
        >>> network = renderer.render_author_network(git_data)
        >>> json_output = renderer.format_for_d3(network)
    """

    def __init__(self, repo_path: Optional[Path] = None) -> None:
        """
        Initialize author network renderer.

        Args:
            repo_path: Optional repository path for relative paths
        """
        self.repo_path = repo_path or Path.cwd()

    def render_author_network(
        self,
        git_analysis: Dict
    ) -> AuthorNetworkVisualization:
        """
        Generate author collaboration network from Git analysis.

        Args:
            git_analysis: Git analysis dict with 'commits' and 'blame' keys

        Returns:
            AuthorNetworkVisualization with nodes and edges

        Example:
            >>> git_data = {"commits": [{"author": "Alice", "files": ["a.py"]}]}
            >>> network = renderer.render_author_network(git_data)
            >>> len(network.nodes) >= 1
            True
        """
        commits = git_analysis.get("commits", [])

        # Build author statistics
        author_stats = self._build_author_stats(commits)

        # Create nodes
        nodes = [
            asdict(self._create_author_node(author, stats))
            for author, stats in author_stats.items()
        ]

        # Calculate collaborations
        edges = self._calculate_collaborations(author_stats)

        # Calculate network statistics
        statistics = self._calculate_network_stats(nodes, edges)

        return AuthorNetworkVisualization(
            nodes=nodes,
            edges=edges,
            statistics=statistics
        )

    def calculate_collaboration_strength(
        self,
        author1: str,
        author2: str,
        author_stats: Dict
    ) -> int:
        """
        Calculate collaboration strength between two authors.

        Collaboration strength = number of shared files modified by both.

        Args:
            author1: First author identifier
            author2: Second author identifier
            author_stats: Dict mapping authors to their file sets

        Returns:
            Number of shared files

        Example:
            >>> stats = {"alice": {"files": {"a.py", "b.py"}}, "bob": {"files": {"b.py"}}}
            >>> strength = renderer.calculate_collaboration_strength("alice", "bob", stats)
            >>> strength == 1
            True
        """
        files1 = author_stats.get(author1, {}).get("files", set())
        files2 = author_stats.get(author2, {}).get("files", set())

        shared = files1 & files2  # Set intersection
        return len(shared)

    def identify_expertise_areas(
        self,
        author: str,
        author_stats: Dict
    ) -> List[str]:
        """
        Identify expertise areas for an author based on file patterns.

        Args:
            author: Author identifier
            author_stats: Dict with author file statistics

        Returns:
            List of expertise area tags

        Example:
            >>> stats = {"alice": {"files": {"api/route.py", "tests/test.py"}}}
            >>> areas = renderer.identify_expertise_areas("alice", stats)
            >>> "backend" in areas or "testing" in areas
            True
        """
        files = author_stats.get(author, {}).get("files", set())

        expertise = set()

        for file_path in files:
            path_lower = file_path.lower()

            # Backend/API
            if "api" in path_lower or "backend" in path_lower or "server" in path_lower:
                expertise.add("backend")

            # Frontend
            if any(ext in path_lower for ext in [".jsx", ".tsx", ".vue", ".html", ".css"]):
                expertise.add("frontend")

            # Testing
            if "test" in path_lower or "spec" in path_lower:
                expertise.add("testing")

            # Database
            if "model" in path_lower or "migration" in path_lower or ".sql" in path_lower:
                expertise.add("database")

            # DevOps
            if any(keyword in path_lower for keyword in ["docker", "deploy", "ci", ".yml", ".yaml"]):
                expertise.add("devops")

            # Documentation
            if path_lower.endswith(".md") or "doc" in path_lower:
                expertise.add("documentation")

        return sorted(list(expertise))

    def format_for_d3(self, visualization: AuthorNetworkVisualization) -> str:
        """
        Format visualization data as JSON for D3.js force-directed graph.

        Args:
            visualization: AuthorNetworkVisualization instance

        Returns:
            JSON string for D3.js consumption

        Example:
            >>> viz = AuthorNetworkVisualization([], [], {})
            >>> json_str = renderer.format_for_d3(viz)
            >>> '"nodes"' in json_str
            True
        """
        return json.dumps(asdict(visualization), indent=2)

    # Private methods

    def _build_author_stats(self, commits: List[Dict]) -> Dict:
        """Build author statistics from commits."""
        author_stats: Dict[str, Dict] = defaultdict(
            lambda: {
                "commits": 0,
                "files": set(),
                "name": "",
            }
        )

        for commit in commits:
            author = commit.get("author", "Unknown")
            files = commit.get("files", [])

            author_stats[author]["commits"] += 1
            author_stats[author]["files"].update(files)
            author_stats[author]["name"] = author  # Use author as display name

        return dict(author_stats)

    def _create_author_node(self, author: str, stats: Dict) -> AuthorNode:
        """Create author node from statistics."""
        expertise = self.identify_expertise_areas(author, {author: stats})

        return AuthorNode(
            id=author,
            name=stats["name"],
            commit_count=stats["commits"],
            file_count=len(stats["files"]),
            expertise_areas=expertise,
            avatar_url="",  # Could be populated from Git config
        )

    def _calculate_collaborations(
        self,
        author_stats: Dict
    ) -> List[Dict]:
        """Calculate collaboration edges between authors."""
        edges = []
        authors = list(author_stats.keys())

        # Calculate pairwise collaborations
        for i, author1 in enumerate(authors):
            for author2 in authors[i + 1:]:
                strength = self.calculate_collaboration_strength(
                    author1,
                    author2,
                    author_stats
                )

                if strength > 0:  # Only include if they collaborated
                    files1 = author_stats[author1]["files"]
                    files2 = author_stats[author2]["files"]
                    shared = list(files1 & files2)

                    edge = CollaborationEdge(
                        source=author1,
                        target=author2,
                        strength=strength,
                        shared_files=shared
                    )
                    edges.append(asdict(edge))

        return edges

    def _calculate_network_stats(
        self,
        nodes: List[Dict],
        edges: List[Dict]
    ) -> Dict:
        """Calculate network statistics."""
        if not nodes:
            return {
                "total_authors": 0,
                "total_collaborations": 0,
                "avg_commits_per_author": 0.0,
                "most_collaborative_author": None,
            }

        total_commits = sum(n["commit_count"] for n in nodes)

        # Find most collaborative author (most edges)
        collaboration_counts = defaultdict(int)
        for edge in edges:
            collaboration_counts[edge["source"]] += 1
            collaboration_counts[edge["target"]] += 1

        most_collaborative = (
            max(collaboration_counts.items(), key=lambda x: x[1])[0]
            if collaboration_counts
            else None
        )

        return {
            "total_authors": len(nodes),
            "total_collaborations": len(edges),
            "avg_commits_per_author": total_commits / len(nodes) if nodes else 0.0,
            "most_collaborative_author": most_collaborative,
        }
