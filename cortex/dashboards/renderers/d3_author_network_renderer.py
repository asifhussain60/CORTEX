"""
D3.js Author Network Renderer.

Generates D3.js force-directed network visualization data for author collaborations.
Detects collaborations via shared files and calculates contribution metrics.

AC-ID: LENS-DASH-009
Author: Asif Hussain
Phase: 14
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class Author:
    """Represents an author in the collaboration network."""

    name: str
    commits: int = 0
    files_touched: set[str] = field(default_factory=set)

    def add_commit(self, files: list[str]) -> None:
        """
        Add a commit to this author's history.

        Args:
            files: List of files touched in the commit

        Example:
            >>> author = Author(name="Alice")
            >>> author.add_commit(["file1.py", "file2.py"])
            >>> author.commits
            1
            >>> len(author.files_touched)
            2
        """
        self.commits += 1
        self.files_touched.update(files)

    def to_dict(self) -> dict[str, Any]:
        """
        Convert to dictionary for JSON serialization.

        Returns:
            Dictionary representation

        Example:
            >>> author.to_dict()
            {
                "id": "Alice",
                "name": "Alice",
                "commits": 5,
                "files_touched": 15
            }
        """
        return {
            "id": self.name,
            "name": self.name,
            "commits": self.commits,
            "files_touched": len(self.files_touched),
        }


@dataclass
class Collaboration:
    """Represents a collaboration between two authors."""

    author1: str
    author2: str
    shared_files: set[str] = field(default_factory=set)

    @property
    def strength(self) -> int:
        """
        Calculate collaboration strength (number of shared files).

        Returns:
            Number of files both authors have touched

        Example:
            >>> collab = Collaboration("Alice", "Bob")
            >>> collab.add_shared_file("module.py")
            >>> collab.strength
            1
        """
        return len(self.shared_files)

    def add_shared_file(self, file_path: str) -> None:
        """
        Add a file that both authors have touched.

        Args:
            file_path: Path to shared file

        Example:
            >>> collab.add_shared_file("src/module.py")
        """
        self.shared_files.add(file_path)

    def to_dict(self) -> dict[str, Any]:
        """
        Convert to dictionary for JSON serialization.

        Returns:
            Dictionary representation for D3.js links

        Example:
            >>> collab.to_dict()
            {
                "source": "Alice",
                "target": "Bob",
                "strength": 3,
                "shared_files": ["file1.py", "file2.py", "file3.py"]
            }
        """
        return {
            "source": self.author1,
            "target": self.author2,
            "strength": self.strength,
            "shared_files": sorted(list(self.shared_files)),
        }


class D3AuthorNetworkRenderer:
    """
    Renders author collaboration network as D3.js force-directed graph.

    Detects collaborations by finding files that multiple authors have touched.
    Calculates contribution metrics and collaboration strength.

    Example:
        >>> renderer = D3AuthorNetworkRenderer()
        >>> network_data = renderer.render_network(commits)
        >>> renderer.render_to_file(commits, Path("author_network.json"))
    """

    def __init__(
        self,
        width: int = 1000,
        height: int = 800,
    ) -> None:
        """
        Initialize D3 Author Network Renderer.

        Args:
            width: SVG width in pixels
            height: SVG height in pixels
        """
        self.width = width
        self.height = height

    def render_network(self, commits: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Render author collaboration network as D3.js graph data.

        Args:
            commits: List of commit dictionaries with keys:
                    - hash: Commit hash
                    - author: Author name
                    - date: ISO format date
                    - files: List of file paths touched

        Returns:
            Dictionary with D3.js force-directed graph data:
            - config: Visualization configuration
            - nodes: Author nodes with metadata
            - links: Collaboration links with strength
            - stats: Network statistics

        Example:
            >>> commits = [
            ...     {
            ...         "hash": "abc123",
            ...         "author": "Alice",
            ...         "date": "2026-01-01T10:00:00",
            ...         "files": ["src/module.py"],
            ...     },
            ...     {
            ...         "hash": "def456",
            ...         "author": "Bob",
            ...         "date": "2026-01-02T10:00:00",
            ...         "files": ["src/module.py"],
            ...     }
            ... ]
            >>> data = renderer.render_network(commits)
            >>> len(data["nodes"])
            2
            >>> len(data["links"])
            1
        """
        # Build author graph
        authors, collaborations = self._build_author_graph(commits)

        # Calculate node sizes based on commits
        node_sizes = self._calculate_node_sizes(authors)

        # Build nodes
        nodes = []
        for author in authors.values():
            node_dict = author.to_dict()
            node_dict["size"] = node_sizes[author.name]
            nodes.append(node_dict)

        # Build links
        links = [collab.to_dict() for collab in collaborations.values()]

        # Calculate statistics
        stats = self._calculate_statistics(authors, collaborations)

        return {
            "config": {
                "width": self.width,
                "height": self.height,
                "type": "author_network",
            },
            "nodes": nodes,
            "links": links,
            "stats": stats,
        }

    def _build_author_graph(
        self, commits: list[dict[str, Any]]
    ) -> tuple[dict[str, Author], dict[tuple[str, str], Collaboration]]:
        """
        Build author collaboration graph from commits.

        Args:
            commits: List of commit dictionaries

        Returns:
            Tuple of (authors dict, collaborations dict)
        """
        authors: dict[str, Author] = {}
        file_authors: dict[str, set[str]] = {}  # file -> set of authors

        # First pass: Build author profiles and track file ownership
        for commit in commits:
            author_name = commit["author"]
            files = commit.get("files", [])

            # Create or update author
            if author_name not in authors:
                authors[author_name] = Author(name=author_name)

            authors[author_name].add_commit(files)

            # Track which authors touched which files
            for file_path in files:
                if file_path not in file_authors:
                    file_authors[file_path] = set()
                file_authors[file_path].add(author_name)

        # Second pass: Detect collaborations via shared files
        collaborations: dict[tuple[str, str], Collaboration] = {}

        for file_path, file_author_set in file_authors.items():
            if len(file_author_set) < 2:
                continue  # No collaboration on this file

            # Create collaborations for all pairs of authors who touched this file
            author_list = sorted(file_author_set)
            for i in range(len(author_list)):
                for j in range(i + 1, len(author_list)):
                    author1, author2 = author_list[i], author_list[j]
                    collab_key = (author1, author2)

                    if collab_key not in collaborations:
                        collaborations[collab_key] = Collaboration(
                            author1=author1, author2=author2
                        )

                    collaborations[collab_key].add_shared_file(file_path)

        return authors, collaborations

    def _calculate_node_sizes(self, authors: dict[str, Author]) -> dict[str, int]:
        """
        Calculate node sizes based on commit count.

        Args:
            authors: Dictionary of Author objects

        Returns:
            Dictionary mapping author name to node size (20-80)
        """
        if not authors:
            return {}

        max_commits = max(author.commits for author in authors.values())
        min_commits = min(author.commits for author in authors.values())

        # Avoid division by zero
        commit_range = max_commits - min_commits or 1

        # Scale to 20-80 range
        sizes = {}
        for author in authors.values():
            normalized = (author.commits - min_commits) / commit_range
            sizes[author.name] = int(20 + (normalized * 60))

        return sizes

    def _calculate_statistics(
        self,
        authors: dict[str, Author],
        collaborations: dict[tuple[str, str], Collaboration],
    ) -> dict[str, Any]:
        """
        Calculate network statistics.

        Args:
            authors: Dictionary of Author objects
            collaborations: Dictionary of Collaboration objects

        Returns:
            Dictionary with statistics:
            - total_authors: Number of authors
            - total_collaborations: Number of collaboration links
            - most_active_author: Author with most commits
            - most_commits: Highest commit count
            - average_commits_per_author: Mean commits
        """
        if not authors:
            return {
                "total_authors": 0,
                "total_collaborations": 0,
                "most_active_author": None,
                "most_commits": 0,
                "average_commits_per_author": 0.0,
            }

        total_commits = sum(author.commits for author in authors.values())
        most_active = max(authors.values(), key=lambda a: a.commits)

        return {
            "total_authors": len(authors),
            "total_collaborations": len(collaborations),
            "most_active_author": most_active.name,
            "most_commits": most_active.commits,
            "average_commits_per_author": round(
                total_commits / len(authors), 2
            ),
        }

    def render_to_file(
        self, commits: list[dict[str, Any]], output_path: Path
    ) -> None:
        """
        Render author network to JSON file.

        Args:
            commits: List of commit dictionaries
            output_path: Output file path (will be created if doesn't exist)

        Example:
            >>> renderer.render_to_file(commits, Path("author_network.json"))
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        network_data = self.render_network(commits)

        with open(output_path, "w") as f:
            json.dump(network_data, f, indent=2)
