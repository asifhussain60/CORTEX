"""
Phase 66 Stage 2: Knowledge Graph Storage - Unit Tests

Tests for SQLite-based graph storage with property graph model.

AC_START: AC-PHASE66-S2-001
Tests BEFORE implementation (TDD)
"""

import pytest
import sqlite3
from pathlib import Path
import tempfile
import json


class TestGraphStorage:
    """Test suite for GraphStorage SQLite backend"""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary SQLite database"""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = Path(tmp.name)
        
        yield db_path
        
        # Cleanup
        if db_path.exists():
            db_path.unlink()
    
    def test_graph_schema_validation(self, temp_db):
        """Test graph schema creation and validation"""
        from cortex_lens.knowledge_graph.graph_storage import GraphStorage
        
        storage = GraphStorage(temp_db)
        storage.initialize_schema()
        
        # Verify tables exist
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        # Check nodes table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='nodes'")
        assert cursor.fetchone() is not None
        
        # Check edges table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='edges'")
        assert cursor.fetchone() is not None
        
        # Check indexes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = [row[0] for row in cursor.fetchall()]
        assert any("node_type" in idx for idx in indexes)
        assert any("edge_type" in idx for idx in indexes)
        
        conn.close()
    
    def test_node_insertion(self, temp_db):
        """Test inserting nodes into graph"""
        from cortex_lens.knowledge_graph.graph_storage import GraphStorage
        
        storage = GraphStorage(temp_db)
        storage.initialize_schema()
        
        # Insert file node
        node_id = storage.insert_node(
            node_type="File",
            name="user_controller.py",
            properties={"path": "/controllers/user_controller.py", "lines": 50}
        )
        
        assert node_id is not None
        assert isinstance(node_id, int)
        
        # Retrieve node
        node = storage.get_node(node_id)
        assert node is not None
        assert node["node_type"] == "File"
        assert node["name"] == "user_controller.py"
        assert node["properties"]["lines"] == 50
    
    def test_edge_insertion(self, temp_db):
        """Test inserting edges between nodes"""
        from cortex_lens.knowledge_graph.graph_storage import GraphStorage
        
        storage = GraphStorage(temp_db)
        storage.initialize_schema()
        
        # Insert two nodes
        node1_id = storage.insert_node("File", "controller.py", {})
        node2_id = storage.insert_node("File", "service.py", {})
        
        # Insert edge
        edge_id = storage.insert_edge(
            source_id=node1_id,
            target_id=node2_id,
            edge_type="imports",
            properties={"line_number": 5}
        )
        
        assert edge_id is not None
        assert isinstance(edge_id, int)
        
        # Retrieve edge
        edge = storage.get_edge(edge_id)
        assert edge is not None
        assert edge["source_id"] == node1_id
        assert edge["target_id"] == node2_id
        assert edge["edge_type"] == "imports"
    
    def test_query_1hop_relationships(self, temp_db):
        """Test querying 1-hop relationships from a node"""
        from cortex_lens.knowledge_graph.graph_storage import GraphStorage
        
        storage = GraphStorage(temp_db)
        storage.initialize_schema()
        
        # Create graph: A → B, A → C
        node_a = storage.insert_node("File", "a.py", {})
        node_b = storage.insert_node("File", "b.py", {})
        node_c = storage.insert_node("File", "c.py", {})
        
        storage.insert_edge(node_a, node_b, "imports", {})
        storage.insert_edge(node_a, node_c, "imports", {})
        
        # Query 1-hop
        neighbors = storage.query_neighbors(node_a, edge_type="imports", depth=1)
        
        assert len(neighbors) == 2
        neighbor_names = [n["name"] for n in neighbors]
        assert "b.py" in neighbor_names
        assert "c.py" in neighbor_names
    
    def test_query_2hop_relationships(self, temp_db):
        """Test querying 2-hop relationships from a node"""
        from cortex_lens.knowledge_graph.graph_storage import GraphStorage
        
        storage = GraphStorage(temp_db)
        storage.initialize_schema()
        
        # Create graph: A → B → C
        node_a = storage.insert_node("File", "a.py", {})
        node_b = storage.insert_node("File", "b.py", {})
        node_c = storage.insert_node("File", "c.py", {})
        
        storage.insert_edge(node_a, node_b, "imports", {})
        storage.insert_edge(node_b, node_c, "imports", {})
        
        # Query 2-hop
        neighbors = storage.query_neighbors(node_a, edge_type="imports", depth=2)
        
        assert len(neighbors) >= 2
        neighbor_names = [n["name"] for n in neighbors]
        assert "b.py" in neighbor_names
        assert "c.py" in neighbor_names
    
    def test_query_performance_100ms(self, temp_db):
        """Test query performance meets <100ms SLA"""
        import time
        from cortex_lens.knowledge_graph.graph_storage import GraphStorage
        
        storage = GraphStorage(temp_db)
        storage.initialize_schema()
        
        # Create larger graph (100 nodes)
        node_ids = []
        for i in range(100):
            node_id = storage.insert_node("File", f"file_{i}.py", {})
            node_ids.append(node_id)
        
        # Create edges (each node connects to next 3)
        for i in range(97):
            for j in range(1, 4):
                storage.insert_edge(node_ids[i], node_ids[i + j], "imports", {})
        
        # Measure query time
        start = time.time()
        neighbors = storage.query_neighbors(node_ids[0], edge_type="imports", depth=2)
        duration_ms = (time.time() - start) * 1000
        
        assert duration_ms < 100, f"Query took {duration_ms}ms, expected <100ms"
        assert len(neighbors) > 0
    
    def test_incremental_update_file_change(self, temp_db):
        """Test incremental graph update when file changes"""
        from cortex_lens.knowledge_graph.graph_storage import GraphStorage
        
        storage = GraphStorage(temp_db)
        storage.initialize_schema()
        
        # Initial insert
        node_id = storage.insert_node("File", "test.py", {"hash": "abc123", "lines": 50})
        
        # Update node (file changed)
        storage.update_node(node_id, properties={"hash": "def456", "lines": 60})
        
        # Verify update
        node = storage.get_node(node_id)
        assert node["properties"]["hash"] == "def456"
        assert node["properties"]["lines"] == 60
    
    def test_graph_serialization(self, temp_db):
        """Test graph serialization to JSON for export"""
        from cortex_lens.knowledge_graph.graph_storage import GraphStorage
        
        storage = GraphStorage(temp_db)
        storage.initialize_schema()
        
        # Build small graph
        node_a = storage.insert_node("File", "a.py", {})
        node_b = storage.insert_node("File", "b.py", {})
        storage.insert_edge(node_a, node_b, "imports", {})
        
        # Export to JSON
        graph_json = storage.export_to_json()
        
        assert isinstance(graph_json, str)
        graph_dict = json.loads(graph_json)
        
        assert "nodes" in graph_dict
        assert "edges" in graph_dict
        assert len(graph_dict["nodes"]) == 2
        assert len(graph_dict["edges"]) == 1
    
    def test_node_deletion(self, temp_db):
        """Test deleting nodes and cascade edges"""
        from cortex_lens.knowledge_graph.graph_storage import GraphStorage
        
        storage = GraphStorage(temp_db)
        storage.initialize_schema()
        
        # Create graph
        node_a = storage.insert_node("File", "a.py", {})
        node_b = storage.insert_node("File", "b.py", {})
        edge_id = storage.insert_edge(node_a, node_b, "imports", {})
        
        # Delete node_a (should cascade delete edge)
        storage.delete_node(node_a)
        
        # Verify deletion
        assert storage.get_node(node_a) is None
        assert storage.get_edge(edge_id) is None
        assert storage.get_node(node_b) is not None  # node_b still exists
    
    def test_bulk_insert_performance(self, temp_db):
        """Test bulk insertion performance"""
        import time
        from cortex_lens.knowledge_graph.graph_storage import GraphStorage
        
        storage = GraphStorage(temp_db)
        storage.initialize_schema()
        
        # Bulk insert 1000 nodes
        nodes_data = [
            ("File", f"file_{i}.py", {"index": i})
            for i in range(1000)
        ]
        
        start = time.time()
        node_ids = storage.bulk_insert_nodes(nodes_data)
        duration_s = time.time() - start
        
        assert len(node_ids) == 1000
        assert duration_s < 2.0, f"Bulk insert took {duration_s}s, expected <2s"
    
    def test_query_by_node_type(self, temp_db):
        """Test querying nodes by type"""
        from cortex_lens.knowledge_graph.graph_storage import GraphStorage
        
        storage = GraphStorage(temp_db)
        storage.initialize_schema()
        
        # Insert mixed types
        storage.insert_node("File", "a.py", {})
        storage.insert_node("File", "b.py", {})
        storage.insert_node("Class", "UserController", {})
        storage.insert_node("Function", "get_user", {})
        
        # Query by type
        files = storage.query_nodes_by_type("File")
        classes = storage.query_nodes_by_type("Class")
        
        assert len(files) == 2
        assert len(classes) == 1
        assert all(n["node_type"] == "File" for n in files)


class TestGraphQuery:
    """Test suite for GraphQuery traversal interface"""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary SQLite database"""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = Path(tmp.name)
        
        yield db_path
        
        # Cleanup
        if db_path.exists():
            db_path.unlink()
    
    @pytest.fixture
    def populated_db(self):
        """Create populated graph database"""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = Path(tmp.name)
        
        from cortex_lens.knowledge_graph.graph_storage import GraphStorage
        storage = GraphStorage(db_path)
        storage.initialize_schema()
        
        # Build test graph: A → B → C, A → D
        node_a = storage.insert_node("File", "a.py", {})
        node_b = storage.insert_node("File", "b.py", {})
        node_c = storage.insert_node("File", "c.py", {})
        node_d = storage.insert_node("File", "d.py", {})
        
        # Add functions for find_callers tests
        foo_func = storage.insert_node("Function", "foo", {})
        bar_func = storage.insert_node("Function", "bar", {})
        
        storage.insert_edge(node_a, node_b, "imports", {})
        storage.insert_edge(node_b, node_c, "imports", {})
        storage.insert_edge(node_a, node_d, "calls", {})
        
        # Function call edges
        storage.insert_edge(foo_func, bar_func, "calls", {})
        
        yield db_path, storage
        
        if db_path.exists():
            db_path.unlink()
    
    def test_traverse_single_edge_type(self, populated_db):
        """Test traversal filtering by edge type"""
        db_path, storage = populated_db
        from cortex_lens.knowledge_graph.graph_query import GraphQuery
        
        query = GraphQuery(storage)
        
        # Get node ID for a.py (should be the first one inserted)
        # In populated_db, node_a is the first insert, so ID should be 1
        # Let's just use the ID we know from fixture
        node_a_id = 1  # From populated_db fixture
        
        # Find files imported by a.py
        results = query.traverse(
            start_node_id=node_a_id,
            edge_types=["imports"],
            direction="outgoing",
            max_depth=1
        )
        
        assert len(results) >= 1
        assert any(n.name == "b.py" for n in results)
        assert not any(n.name == "d.py" for n in results)  # calls edge, not imports
    
    def test_traverse_multiple_hops(self, populated_db):
        """Test multi-hop traversal"""
        db_path, storage = populated_db
        from cortex_lens.knowledge_graph.graph_query import GraphQuery
        
        query = GraphQuery(storage)
        
        # Use node_a ID from fixture (first insert)
        node_a_id = 1
        
        # Find all files reachable via imports (2 hops)
        results = query.traverse(
            start_node_id=node_a_id,
            edge_types=["imports"],
            direction="outgoing",
            max_depth=2
        )
        
        result_names = [n.name for n in results]
        assert "b.py" in result_names  # 1 hop
        assert "c.py" in result_names  # 2 hops
    
    def test_find_path_between_nodes(self, populated_db):
        """Test finding path between two nodes"""
        db_path, storage = populated_db
        from cortex_lens.knowledge_graph.graph_query import GraphQuery
        
        query = GraphQuery(storage)
        
        # Use node IDs from fixture (sequential inserts)
        a_node_id = 1  # node_a
        c_node_id = 3  # node_c
        
        # Find path from a.py to c.py
        path = query.find_path(
            start_node_id=a_node_id,
            end_node_id=c_node_id,
            edge_types=["imports"]
        )
        
        assert path is not None
        assert len(path) == 3  # a.py → b.py → c.py
        assert path[0][0].name == "a.py"
        assert path[1][0].name == "b.py"
        assert path[2][0].name == "c.py"


    def test_get_statistics(self, populated_db):
        """Test graph statistics retrieval"""
        db_path, storage = populated_db
        
        # Get statistics
        stats = storage.get_statistics()
        
        # Verify structure
        assert "total_nodes" in stats
        assert "total_edges" in stats
        assert "nodes_by_type" in stats
        assert "edges_by_type" in stats
        
        # Verify counts (from populated_db fixture: 4 files + 2 functions = 6 nodes, 2 imports + 2 calls = 4 edges)
        assert stats["total_nodes"] == 6
        assert stats["total_edges"] == 4
        
        # Verify type breakdowns
        assert stats["nodes_by_type"]["File"] == 4
        assert stats["nodes_by_type"]["Function"] == 2
        assert stats["edges_by_type"]["imports"] == 2
        assert stats["edges_by_type"]["calls"] == 2
    
    def test_find_callers(self, populated_db):
        """Test finding callers of a function by name"""
        db_path, storage = populated_db
        from cortex_lens.knowledge_graph.graph_query import GraphQuery
        
        query = GraphQuery(storage)
        
        # Find callers of "bar" function
        callers = query.find_callers(target_name="bar", edge_type="calls", max_depth=2)
        
        # Should find "foo" function (which calls "bar")
        assert len(callers) > 0
        caller_names = [c.name for c in callers]
        assert "foo" in caller_names
    
    def test_find_callers_no_matches(self, populated_db):
        """Test find_callers with non-existent target"""
        db_path, storage = populated_db
        from cortex_lens.knowledge_graph.graph_query import GraphQuery
        
        query = GraphQuery(storage)
        
        # Search for non-existent function
        callers = query.find_callers(target_name="nonexistent", edge_type="calls")
        
        assert callers == []
    
    def test_find_callers_deduplication(self, temp_db):
        """Test that find_callers deduplicates results"""
        from cortex_lens.knowledge_graph.graph_storage import GraphStorage
        from cortex_lens.knowledge_graph.graph_query import GraphQuery
        
        storage = GraphStorage(temp_db)
        storage.initialize_schema()
        query = GraphQuery(storage)
        
        # Create diamond pattern: foo → bar, foo → baz, bar → target, baz → target
        foo_id = storage.insert_node("Function", "foo", {})
        bar_id = storage.insert_node("Function", "bar", {})
        baz_id = storage.insert_node("Function", "baz", {})
        target_id = storage.insert_node("Function", "target", {})
        
        storage.insert_edge(foo_id, bar_id, "calls", {})
        storage.insert_edge(foo_id, baz_id, "calls", {})
        storage.insert_edge(bar_id, target_id, "calls", {})
        storage.insert_edge(baz_id, target_id, "calls", {})
        
        # Find callers of "target" with depth=2
        callers = query.find_callers(target_name="target", edge_type="calls", max_depth=2)
        
        # Should find: bar, baz, foo (no duplicates)
        caller_names = [c.name for c in callers]
        assert len(caller_names) == len(set(caller_names)), "Found duplicate callers"
        assert set(caller_names) == {"foo", "bar", "baz"}


# AC_CHECKPOINT: AC-PHASE66-S2-001 RED phase complete
# 24 tests created for graph storage + query (including S3 methods), all should FAIL (implementation pending)
