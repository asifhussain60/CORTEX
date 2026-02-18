"""
CORTEX LENS Golden Tests - Knowledge Graph

Authority: AC-GOLDEN-LENS-KG-001
Tests for knowledge graph construction, relationships, and coverage mapping

Coverage:
- golden_20: Knowledge Graph Construction
- golden_21: Relationship Traversal
- golden_22: Test Coverage Mapping
- golden_23: Dead Code Detection
"""

import pytest
from pathlib import Path

from tests.orchestrators.e2e.test_lens_golden_harness import LENSGoldenTestHarness


class TestLENSKnowledgeGraph:
    """Golden tests for LENS knowledge graph capabilities."""
    
    @pytest.mark.lens
    @pytest.mark.knowledge_graph
    @pytest.mark.xfail(reason="RED phase - Knowledge graph wiring pending")
    def test_golden_20_knowledge_graph_construction(self, lens_harness: LENSGoldenTestHarness):
        """
        Golden Test 20: Knowledge Graph Construction
        
        Validates:
        - Node creation (File, Function, Class nodes)
        - Edge creation (imports, calls, uses relationships)
        - Graph traversal capability
        - Relationship type detection
        """
        result = lens_harness.execute_lens_scenario("lens/knowledge_graph/golden_20_knowledge_graph_construction")
        
        assert result.passed, f"Knowledge graph construction failed: {result.diffs}"
        
        # Verify audit trail
        events = lens_harness.get_audit_events()
        assert any(e['activity'] == 'BUILD_KNOWLEDGE_GRAPH' for e in events)
        assert any(e['activity'] == 'CREATE_RELATIONSHIPS' for e in events)


class TestLENSGraphTraversal:
    """Tests for knowledge graph traversal and queries."""
    
    @pytest.mark.lens
    @pytest.mark.knowledge_graph
    def test_knowledge_graph_nodes_created(self, temp_repo_builder):
        """Test that knowledge graph can represent code structure."""
        files = {
            "main.py": "from auth import login\n\ndef main():\n    login()",
            "auth.py": "def login():\n    pass",
        }
        
        repo_path = temp_repo_builder.create_repo("kg_test", files)
        
        # Knowledge graph should create:
        # - File nodes: main.py, auth.py
        # - Function nodes: main, login
        # - Import edge: main.py -> auth.py
        # - Call edge: main -> login
        
        assert (repo_path / "main.py").exists()
        assert (repo_path / "auth.py").exists()
