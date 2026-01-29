"""
Tests for AuthorNetworkRenderer.

Authority: CORE-008 (TDD - tests before code)
Phase: 14 - LENS Dashboard Implementation
Task: 008 - Author Network Renderer Tests
AC-ID: LENS-DASH-003
"""

import json
import pytest
from pathlib import Path

from cortex.visualization.renderers.author_network_renderer import (
    AuthorNetworkRenderer,
    AuthorNetworkVisualization,
    AuthorNode,
    CollaborationEdge,
)


# Fixtures

@pytest.fixture
def sample_git_analysis():
    """Sample Git analysis data with multiple authors."""
    return {
        "commits": [
            {
                "author": "alice@example.com",
                "files": ["api/routes.py", "tests/test_api.py", "models/user.py"],
            },
            {
                "author": "bob@example.com",
                "files": ["api/routes.py", "frontend/app.jsx", "styles/app.css"],
            },
            {
                "author": "alice@example.com",
                "files": ["models/user.py", "tests/test_models.py"],
            },
            {
                "author": "charlie@example.com",
                "files": ["deploy/docker-compose.yml", "README.md"],
            },
            {
                "author": "bob@example.com",
                "files": ["frontend/app.jsx", "frontend/components.tsx"],
            },
        ]
    }


@pytest.fixture
def renderer():
    """Create AuthorNetworkRenderer instance."""
    return AuthorNetworkRenderer(repo_path=Path("/test/repo"))


# Tests for initialization

def test_renderer_initialization_with_path():
    """Test AuthorNetworkRenderer initializes with custom path."""
    path = Path("/custom/repo")
    renderer = AuthorNetworkRenderer(repo_path=path)
    assert renderer.repo_path == path


def test_renderer_initialization_default_path():
    """Test AuthorNetworkRenderer initializes with default path."""
    renderer = AuthorNetworkRenderer()
    assert renderer.repo_path == Path.cwd()


# Tests for render_author_network

def test_render_author_network_basic(renderer, sample_git_analysis):
    """Test basic author network generation."""
    network = renderer.render_author_network(sample_git_analysis)
    
    assert isinstance(network, AuthorNetworkVisualization)
    assert len(network.nodes) == 3  # alice, bob, charlie
    assert len(network.edges) >= 1  # At least one collaboration


def test_render_author_network_empty_commits(renderer):
    """Test network generation with no commits."""
    network = renderer.render_author_network({"commits": []})
    
    assert len(network.nodes) == 0
    assert len(network.edges) == 0
    assert network.statistics["total_authors"] == 0


def test_author_node_structure(renderer, sample_git_analysis):
    """Test author nodes have correct structure."""
    network = renderer.render_author_network(sample_git_analysis)
    
    for node in network.nodes:
        assert "id" in node
        assert "name" in node
        assert "commit_count" in node
        assert "file_count" in node
        assert "expertise_areas" in node
        assert isinstance(node["expertise_areas"], list)


def test_author_commit_counts(renderer, sample_git_analysis):
    """Test author commit counts are correctly calculated."""
    network = renderer.render_author_network(sample_git_analysis)
    
    alice = next(n for n in network.nodes if "alice" in n["id"])
    bob = next(n for n in network.nodes if "bob" in n["id"])
    charlie = next(n for n in network.nodes if "charlie" in n["id"])
    
    assert alice["commit_count"] == 2
    assert bob["commit_count"] == 2
    assert charlie["commit_count"] == 1


def test_author_file_counts(renderer, sample_git_analysis):
    """Test unique file counts per author."""
    network = renderer.render_author_network(sample_git_analysis)
    
    alice = next(n for n in network.nodes if "alice" in n["id"])
    # alice touched: api/routes.py, tests/test_api.py, models/user.py, tests/test_models.py
    assert alice["file_count"] == 4


# Tests for calculate_collaboration_strength

def test_collaboration_strength_basic(renderer):
    """Test collaboration strength calculation."""
    author_stats = {
        "alice": {"files": {"a.py", "b.py", "c.py"}},
        "bob": {"files": {"b.py", "c.py", "d.py"}},
    }
    
    strength = renderer.calculate_collaboration_strength("alice", "bob", author_stats)
    assert strength == 2  # b.py and c.py are shared


def test_collaboration_strength_no_overlap(renderer):
    """Test collaboration strength with no shared files."""
    author_stats = {
        "alice": {"files": {"a.py"}},
        "bob": {"files": {"b.py"}},
    }
    
    strength = renderer.calculate_collaboration_strength("alice", "bob", author_stats)
    assert strength == 0


def test_collaboration_strength_complete_overlap(renderer):
    """Test collaboration strength with complete overlap."""
    author_stats = {
        "alice": {"files": {"a.py", "b.py"}},
        "bob": {"files": {"a.py", "b.py"}},
    }
    
    strength = renderer.calculate_collaboration_strength("alice", "bob", author_stats)
    assert strength == 2


def test_collaboration_strength_missing_author(renderer):
    """Test collaboration strength with missing author."""
    author_stats = {
        "alice": {"files": {"a.py"}},
    }
    
    strength = renderer.calculate_collaboration_strength("alice", "bob", author_stats)
    assert strength == 0


# Tests for identify_expertise_areas

def test_expertise_backend_detection(renderer):
    """Test backend expertise detection."""
    author_stats = {
        "alice": {"files": {"api/routes.py", "backend/server.py"}}
    }
    
    areas = renderer.identify_expertise_areas("alice", author_stats)
    assert "backend" in areas


def test_expertise_frontend_detection(renderer):
    """Test frontend expertise detection."""
    author_stats = {
        "bob": {"files": {"app.jsx", "components.tsx", "styles.css"}}
    }
    
    areas = renderer.identify_expertise_areas("bob", author_stats)
    assert "frontend" in areas


def test_expertise_testing_detection(renderer):
    """Test testing expertise detection."""
    author_stats = {
        "alice": {"files": {"tests/test_api.py", "specs/user.spec.js"}}
    }
    
    areas = renderer.identify_expertise_areas("alice", author_stats)
    assert "testing" in areas


def test_expertise_database_detection(renderer):
    """Test database expertise detection."""
    author_stats = {
        "alice": {"files": {"models/user.py", "migrations/001.sql"}}
    }
    
    areas = renderer.identify_expertise_areas("alice", author_stats)
    assert "database" in areas


def test_expertise_devops_detection(renderer):
    """Test devops expertise detection."""
    author_stats = {
        "charlie": {"files": {"docker-compose.yml", "deploy/config.yaml", ".github/workflows/ci.yml"}}
    }
    
    areas = renderer.identify_expertise_areas("charlie", author_stats)
    assert "devops" in areas


def test_expertise_documentation_detection(renderer):
    """Test documentation expertise detection."""
    author_stats = {
        "charlie": {"files": {"README.md", "docs/guide.md"}}
    }
    
    areas = renderer.identify_expertise_areas("charlie", author_stats)
    assert "documentation" in areas


def test_expertise_multiple_areas(renderer):
    """Test author with multiple expertise areas."""
    author_stats = {
        "alice": {"files": {"api/routes.py", "tests/test_api.py", "models/user.py"}}
    }
    
    areas = renderer.identify_expertise_areas("alice", author_stats)
    assert "backend" in areas
    assert "testing" in areas
    assert "database" in areas


def test_expertise_no_files(renderer):
    """Test expertise with no files."""
    author_stats = {
        "alice": {"files": set()}
    }
    
    areas = renderer.identify_expertise_areas("alice", author_stats)
    assert len(areas) == 0


# Tests for collaboration edge generation

def test_collaboration_edges_created(renderer, sample_git_analysis):
    """Test collaboration edges are created for shared files."""
    network = renderer.render_author_network(sample_git_analysis)
    
    # alice and bob both touched api/routes.py
    alice_bob_edge = next(
        (e for e in network.edges 
         if ("alice" in e["source"] and "bob" in e["target"]) or
            ("bob" in e["source"] and "alice" in e["target"])),
        None
    )
    
    assert alice_bob_edge is not None
    assert alice_bob_edge["strength"] >= 1


def test_collaboration_edge_structure(renderer, sample_git_analysis):
    """Test collaboration edges have correct structure."""
    network = renderer.render_author_network(sample_git_analysis)
    
    if network.edges:
        edge = network.edges[0]
        assert "source" in edge
        assert "target" in edge
        assert "strength" in edge
        assert "shared_files" in edge
        assert isinstance(edge["shared_files"], list)


def test_no_self_collaboration_edges(renderer, sample_git_analysis):
    """Test no edges are created from author to themselves."""
    network = renderer.render_author_network(sample_git_analysis)
    
    for edge in network.edges:
        assert edge["source"] != edge["target"]


# Tests for format_for_d3

def test_format_for_d3_returns_valid_json(renderer):
    """Test D3 format returns valid JSON string."""
    viz = AuthorNetworkVisualization(
        nodes=[],
        edges=[],
        statistics={}
    )
    
    json_str = renderer.format_for_d3(viz)
    
    # Should be valid JSON
    data = json.loads(json_str)
    assert "nodes" in data
    assert "edges" in data
    assert "statistics" in data


def test_format_for_d3_with_data(renderer, sample_git_analysis):
    """Test D3 format with actual network data."""
    network = renderer.render_author_network(sample_git_analysis)
    json_str = renderer.format_for_d3(network)
    
    data = json.loads(json_str)
    assert len(data["nodes"]) == 3
    assert "statistics" in data


# Tests for network statistics

def test_network_statistics_basic(renderer, sample_git_analysis):
    """Test network statistics calculation."""
    network = renderer.render_author_network(sample_git_analysis)
    
    stats = network.statistics
    assert stats["total_authors"] == 3
    assert stats["total_collaborations"] >= 1
    assert stats["avg_commits_per_author"] > 0


def test_network_statistics_empty(renderer):
    """Test statistics with empty network."""
    network = renderer.render_author_network({"commits": []})
    
    stats = network.statistics
    assert stats["total_authors"] == 0
    assert stats["total_collaborations"] == 0
    assert stats["avg_commits_per_author"] == 0.0
    assert stats["most_collaborative_author"] is None


def test_most_collaborative_author_detection(renderer, sample_git_analysis):
    """Test most collaborative author is identified."""
    network = renderer.render_author_network(sample_git_analysis)
    
    stats = network.statistics
    # Either alice or bob should be most collaborative (both have shared files)
    assert stats["most_collaborative_author"] is not None


# Integration tests

def test_end_to_end_network_generation(renderer, sample_git_analysis):
    """Test complete network generation pipeline."""
    # Generate network
    network = renderer.render_author_network(sample_git_analysis)
    
    # Verify all components
    assert len(network.nodes) == 3
    assert all("expertise_areas" in n for n in network.nodes)
    assert network.statistics["total_authors"] == 3
    
    # Format for D3
    json_str = renderer.format_for_d3(network)
    data = json.loads(json_str)
    
    # Verify JSON structure
    assert "nodes" in data
    assert "edges" in data
    assert len(data["nodes"]) == 3


def test_network_with_single_author(renderer):
    """Test network generation with single author."""
    git_data = {
        "commits": [
            {"author": "alice", "files": ["a.py", "b.py"]},
            {"author": "alice", "files": ["c.py"]},
        ]
    }
    
    network = renderer.render_author_network(git_data)
    
    assert len(network.nodes) == 1
    assert len(network.edges) == 0  # No collaborations with self
    assert network.nodes[0]["commit_count"] == 2
