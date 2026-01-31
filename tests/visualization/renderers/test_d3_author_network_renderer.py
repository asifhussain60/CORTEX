"""
Tests for D3AuthorNetworkRenderer.

AC-ID: LENS-DASH-009
Author: Asif Hussain
Phase: 14
"""

import json
from pathlib import Path

import pytest

from cortex.visualization.renderers.d3_author_network_renderer import (
    D3AuthorNetworkRenderer,
    Author,
    Collaboration,
)


@pytest.fixture
def sample_commits() -> list[dict]:
    """Sample commit data for testing."""
    return [
        {
            "hash": "abc123",
            "author": "Alice",
            "date": "2026-01-01T10:00:00",
            "files": ["src/module_a.py", "src/module_b.py"],
        },
        {
            "hash": "def456",
            "author": "Bob",
            "date": "2026-01-02T10:00:00",
            "files": ["src/module_b.py", "tests/test_b.py"],
        },
        {
            "hash": "ghi789",
            "author": "Alice",
            "date": "2026-01-03T10:00:00",
            "files": ["src/module_b.py", "src/module_c.py"],
        },
        {
            "hash": "jkl012",
            "author": "Charlie",
            "date": "2026-01-04T10:00:00",
            "files": ["src/module_c.py", "docs/README.md"],
        },
        {
            "hash": "mno345",
            "author": "Alice",
            "date": "2026-01-05T10:00:00",
            "files": ["src/module_a.py"],
        },
    ]


@pytest.fixture
def renderer() -> D3AuthorNetworkRenderer:
    """Create renderer instance."""
    return D3AuthorNetworkRenderer()


class TestAuthor:
    """Test Author dataclass."""

    def test_initialization(self) -> None:
        """Test Author initialization."""
        author = Author(name="Alice")
        
        assert author.name == "Alice"
        assert author.commits == 0
        assert author.files_touched == set()

    def test_add_commit(self) -> None:
        """Test adding commit to author."""
        author = Author(name="Alice")
        
        author.add_commit(["file1.py", "file2.py"])
        
        assert author.commits == 1
        assert len(author.files_touched) == 2
        assert "file1.py" in author.files_touched

    def test_multiple_commits(self) -> None:
        """Test multiple commits accumulation."""
        author = Author(name="Alice")
        
        author.add_commit(["file1.py", "file2.py"])
        author.add_commit(["file2.py", "file3.py"])
        
        assert author.commits == 2
        assert len(author.files_touched) == 3  # Unique files

    def test_to_dict(self) -> None:
        """Test conversion to dictionary."""
        author = Author(name="Alice")
        author.add_commit(["file1.py", "file2.py"])
        author.add_commit(["file3.py"])
        
        data = author.to_dict()
        
        assert data["id"] == "Alice"
        assert data["name"] == "Alice"
        assert data["commits"] == 2
        assert data["files_touched"] == 3


class TestCollaboration:
    """Test Collaboration dataclass."""

    def test_initialization(self) -> None:
        """Test Collaboration initialization."""
        collab = Collaboration(author1="Alice", author2="Bob")
        
        assert collab.author1 == "Alice"
        assert collab.author2 == "Bob"
        assert collab.shared_files == set()
        assert collab.strength == 0

    def test_add_shared_file(self) -> None:
        """Test adding shared file."""
        collab = Collaboration(author1="Alice", author2="Bob")
        
        collab.add_shared_file("module.py")
        
        assert len(collab.shared_files) == 1
        assert collab.strength == 1

    def test_multiple_shared_files(self) -> None:
        """Test multiple shared files."""
        collab = Collaboration(author1="Alice", author2="Bob")
        
        collab.add_shared_file("file1.py")
        collab.add_shared_file("file2.py")
        collab.add_shared_file("file1.py")  # Duplicate
        
        assert len(collab.shared_files) == 2  # Unique files
        assert collab.strength == 2

    def test_to_dict(self) -> None:
        """Test conversion to dictionary."""
        collab = Collaboration(author1="Alice", author2="Bob")
        collab.add_shared_file("file1.py")
        collab.add_shared_file("file2.py")
        
        data = collab.to_dict()
        
        assert data["source"] == "Alice"
        assert data["target"] == "Bob"
        assert data["strength"] == 2
        assert len(data["shared_files"]) == 2


class TestD3AuthorNetworkRenderer:
    """Test D3AuthorNetworkRenderer."""

    def test_initialization(self, renderer: D3AuthorNetworkRenderer) -> None:
        """Test renderer initialization."""
        assert renderer.width == 1000
        assert renderer.height == 800

    def test_build_author_graph(
        self, renderer: D3AuthorNetworkRenderer, sample_commits: list[dict]
    ) -> None:
        """Test building author collaboration graph."""
        authors, collaborations = renderer._build_author_graph(sample_commits)
        
        # Check authors
        assert len(authors) == 3  # Alice, Bob, Charlie
        assert "Alice" in authors
        assert authors["Alice"].commits == 3
        assert authors["Bob"].commits == 1
        
        # Check collaborations
        assert len(collaborations) > 0
        # Alice and Bob both touched module_b.py
        alice_bob = next(
            (c for c in collaborations.values()
             if set([c.author1, c.author2]) == {"Alice", "Bob"}),
            None
        )
        assert alice_bob is not None
        assert "src/module_b.py" in alice_bob.shared_files

    def test_render_network(
        self, renderer: D3AuthorNetworkRenderer, sample_commits: list[dict]
    ) -> None:
        """Test rendering author network."""
        result = renderer.render_network(sample_commits)
        
        assert "config" in result
        assert "nodes" in result
        assert "links" in result
        assert "stats" in result
        
        # Check config
        assert result["config"]["width"] == 1000
        assert result["config"]["type"] == "author_network"
        
        # Check nodes
        assert len(result["nodes"]) == 3
        alice_node = next(n for n in result["nodes"] if n["id"] == "Alice")
        assert alice_node["commits"] == 3
        
        # Check links
        assert len(result["links"]) > 0
        
        # Check stats
        assert result["stats"]["total_authors"] == 3
        assert result["stats"]["total_collaborations"] == len(result["links"])

    def test_calculate_node_sizes(
        self, renderer: D3AuthorNetworkRenderer
    ) -> None:
        """Test node size calculation."""
        authors = {
            "Alice": Author(name="Alice"),
            "Bob": Author(name="Bob"),
            "Charlie": Author(name="Charlie"),
        }
        authors["Alice"].commits = 10
        authors["Bob"].commits = 5
        authors["Charlie"].commits = 1
        
        sizes = renderer._calculate_node_sizes(authors)
        
        assert sizes["Alice"] > sizes["Bob"]
        assert sizes["Bob"] > sizes["Charlie"]
        assert 20 <= sizes["Alice"] <= 80  # Within bounds

    def test_collaboration_detection(
        self, renderer: D3AuthorNetworkRenderer
    ) -> None:
        """Test collaboration detection via shared files."""
        commits = [
            {
                "hash": "abc",
                "author": "Alice",
                "date": "2026-01-01T10:00:00",
                "files": ["module.py"],
            },
            {
                "hash": "def",
                "author": "Bob",
                "date": "2026-01-02T10:00:00",
                "files": ["module.py"],
            },
            {
                "hash": "ghi",
                "author": "Charlie",
                "date": "2026-01-03T10:00:00",
                "files": ["other.py"],
            },
        ]
        
        authors, collaborations = renderer._build_author_graph(commits)
        
        # Alice and Bob should have collaboration via module.py
        assert len(collaborations) == 1
        collab_key = ("Alice", "Bob")
        assert collab_key in collaborations
        assert "module.py" in collaborations[collab_key].shared_files
        
        # Charlie should have no collaborations
        charlie_collabs = [
            c for c in collaborations.values()
            if "Charlie" in [c.author1, c.author2]
        ]
        assert len(charlie_collabs) == 0

    def test_render_empty_commits(
        self, renderer: D3AuthorNetworkRenderer
    ) -> None:
        """Test rendering with no commits."""
        result = renderer.render_network([])
        
        assert len(result["nodes"]) == 0
        assert len(result["links"]) == 0
        assert result["stats"]["total_authors"] == 0

    def test_render_to_json_file(
        self, renderer: D3AuthorNetworkRenderer, sample_commits: list[dict], tmp_path: Path
    ) -> None:
        """Test rendering to JSON file."""
        output_file = tmp_path / "author_network.json"
        
        renderer.render_to_file(sample_commits, output_file)
        
        assert output_file.exists()
        
        # Verify JSON is valid
        with open(output_file) as f:
            data = json.load(f)
        
        assert "nodes" in data
        assert "links" in data
        assert len(data["nodes"]) == 3

    def test_single_author_no_links(
        self, renderer: D3AuthorNetworkRenderer
    ) -> None:
        """Test single author produces no collaboration links."""
        commits = [
            {
                "hash": "abc",
                "author": "Alice",
                "date": "2026-01-01T10:00:00",
                "files": ["file1.py", "file2.py"],
            }
        ]
        
        result = renderer.render_network(commits)
        
        assert len(result["nodes"]) == 1
        assert len(result["links"]) == 0
        assert result["nodes"][0]["id"] == "Alice"

    def test_most_active_author_stat(
        self, renderer: D3AuthorNetworkRenderer, sample_commits: list[dict]
    ) -> None:
        """Test most active author statistic."""
        result = renderer.render_network(sample_commits)
        
        assert result["stats"]["most_active_author"] == "Alice"
        assert result["stats"]["most_commits"] == 3
