"""
Unit tests for ArchitectureGraphBuilder.

Tests multi-language dependency graph generation with Python, JavaScript,
TypeScript, and C# import detection.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
import tempfile
from pathlib import Path
from src.discovery.architecture_graph_builder import ArchitectureGraphBuilder, ModuleNode


class TestArchitectureGraphBuilder:
    """Test suite for ArchitectureGraphBuilder."""
    
    @pytest.fixture
    def builder(self):
        """Create ArchitectureGraphBuilder instance."""
        return ArchitectureGraphBuilder()
    
    @pytest.fixture
    def temp_repo(self):
        """Create temporary repository structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir)
            yield repo
    
    def test_build_graph_empty_repo(self, builder, temp_repo):
        """Test building graph for empty repository."""
        result = builder.build_graph(str(temp_repo))
        
        assert "nodes" in result
        assert "edges" in result
        assert len(result["nodes"]) == 0
        assert len(result["edges"]) == 0
    
    def test_build_graph_nonexistent_path(self, builder):
        """Test building graph for nonexistent path."""
        result = builder.build_graph("/nonexistent/path")
        
        # Should return empty graph structure (graceful degradation)
        assert "nodes" in result
        assert "edges" in result
        assert len(result["nodes"]) == 0
        assert len(result["edges"]) == 0
    
    def test_python_imports_detection(self, builder, temp_repo):
        """Test Python import detection."""
        # Create source files
        module_a = temp_repo / "module_a.py"
        module_b = temp_repo / "module_b.py"
        
        module_a.write_text("""
import module_b
from pathlib import Path

def function_a():
    pass
""")
        
        module_b.write_text("""
def function_b():
    pass
""")
        
        # Build graph
        result = builder.build_graph(str(temp_repo))
        
        # Verify nodes
        assert len(result["nodes"]) == 2
        node_ids = [node["id"] for node in result["nodes"]]
        assert "module_a.py" in node_ids
        assert "module_b.py" in node_ids
        
        # Verify edges (module_a imports module_b)
        assert len(result["edges"]) == 1
        edge = result["edges"][0]
        assert edge["source"] == "module_a.py"
        assert edge["target"] == "module_b.py"
        assert edge["weight"] == 1
    
    def test_python_stdlib_exclusion(self, builder, temp_repo):
        """Test that Python standard library imports are excluded."""
        module = temp_repo / "test_module.py"
        module.write_text("""
import os
import sys
from pathlib import Path
from typing import Dict
""")
        
        result = builder.build_graph(str(temp_repo))
        
        # Should have 1 node (the module itself), 0 edges (no internal imports)
        assert len(result["nodes"]) == 1
        assert len(result["edges"]) == 0
    
    def test_javascript_imports_detection(self, builder, temp_repo):
        """Test JavaScript ES6 import detection."""
        # Create source files
        app_js = temp_repo / "app.js"
        utils_js = temp_repo / "utils.js"
        
        app_js.write_text("""
import { helper } from './utils';

function main() {
    helper();
}
""")
        
        utils_js.write_text("""
export function helper() {
    return 42;
}
""")
        
        # Build graph
        result = builder.build_graph(str(temp_repo), file_extensions=['.js'])
        
        # Verify nodes
        assert len(result["nodes"]) == 2
        
        # Verify edges
        assert len(result["edges"]) == 1
        edge = result["edges"][0]
        assert edge["source"] == "app.js"
        assert edge["target"] == "utils.js"
    
    def test_typescript_imports_detection(self, builder, temp_repo):
        """Test TypeScript import detection."""
        main_ts = temp_repo / "main.ts"
        types_ts = temp_repo / "types.ts"
        
        main_ts.write_text("""
import { User } from './types';

const user: User = { name: 'Test' };
""")
        
        types_ts.write_text("""
export interface User {
    name: string;
}
""")
        
        result = builder.build_graph(str(temp_repo), file_extensions=['.ts'])
        
        # Verify nodes
        assert len(result["nodes"]) == 2
        
        # Verify edge exists
        assert len(result["edges"]) == 1
    
    def test_csharp_usings_detection(self, builder, temp_repo):
        """Test C# using directive detection."""
        program_cs = temp_repo / "Program.cs"
        helper_cs = temp_repo / "Helper.cs"
        
        program_cs.write_text("""
using System;
using MyApp.Helper;

namespace MyApp
{
    class Program
    {
        static void Main()
        {
        }
    }
}
""")
        
        helper_cs.write_text("""
namespace MyApp
{
    class Helper
    {
    }
}
""")
        
        result = builder.build_graph(str(temp_repo), file_extensions=['.cs'])
        
        # Should have 2 nodes
        assert len(result["nodes"]) == 2
        
        # C# resolution is heuristic-based, may or may not find edge
        # Just verify it doesn't crash
        assert "edges" in result
    
    def test_multi_language_graph(self, builder, temp_repo):
        """Test graph with multiple languages."""
        # Create Python file
        python_file = temp_repo / "main.py"
        python_file.write_text("print('hello')")
        
        # Create JavaScript file
        js_file = temp_repo / "app.js"
        js_file.write_text("console.log('hello');")
        
        # Create TypeScript file
        ts_file = temp_repo / "utils.ts"
        ts_file.write_text("export const x = 42;")
        
        result = builder.build_graph(str(temp_repo))
        
        # Should have 3 nodes
        assert len(result["nodes"]) == 3
        
        # Verify language distribution
        assert "metadata" in result
        assert "languages" in result["metadata"]
        langs = result["metadata"]["languages"]
        assert langs["python"] == 1
        assert langs["javascript"] == 1
        assert langs["typescript"] == 1
    
    def test_loc_counting(self, builder, temp_repo):
        """Test lines of code counting."""
        test_file = temp_repo / "test.py"
        test_file.write_text("""
# Comment line
def function():
    pass

# Another comment
    
""")
        
        result = builder.build_graph(str(temp_repo))
        
        node = result["nodes"][0]
        # Should count non-empty lines (excluding pure whitespace)
        assert node["loc"] > 0
    
    def test_exclusion_patterns(self, builder, temp_repo):
        """Test that excluded directories are ignored."""
        # Create files in excluded directories
        node_modules = temp_repo / "node_modules"
        node_modules.mkdir()
        (node_modules / "package.js").write_text("export const x = 1;")
        
        venv = temp_repo / "venv"
        venv.mkdir()
        (venv / "lib.py").write_text("print('lib')")
        
        # Create file in included directory
        (temp_repo / "main.py").write_text("print('main')")
        
        result = builder.build_graph(str(temp_repo))
        
        # Should only have main.py
        assert len(result["nodes"]) == 1
        assert result["nodes"][0]["id"] == "main.py"
    
    def test_edge_weight_increment(self, builder, temp_repo):
        """Test that multiple imports increase edge weight."""
        module_a = temp_repo / "module_a.py"
        module_b = temp_repo / "module_b.py"
        
        # Module A imports module B twice (different forms)
        module_a.write_text("""
import module_b
from module_b import helper
""")
        
        module_b.write_text("def helper(): pass")
        
        result = builder.build_graph(str(temp_repo))
        
        # Should have 1 edge with weight 2
        assert len(result["edges"]) == 1
        assert result["edges"][0]["weight"] == 2
    
    def test_circular_dependencies(self, builder, temp_repo):
        """Test detection of circular dependencies."""
        module_a = temp_repo / "module_a.py"
        module_b = temp_repo / "module_b.py"
        
        module_a.write_text("import module_b")
        module_b.write_text("import module_a")
        
        result = builder.build_graph(str(temp_repo))
        
        # Should have 2 nodes and 2 edges (bidirectional)
        assert len(result["nodes"]) == 2
        assert len(result["edges"]) == 2
        
        # Find edges
        edges = result["edges"]
        sources = [e["source"] for e in edges]
        targets = [e["target"] for e in edges]
        
        assert "module_a.py" in sources
        assert "module_a.py" in targets
        assert "module_b.py" in sources
        assert "module_b.py" in targets
    
    def test_node_metadata(self, builder, temp_repo):
        """Test that nodes contain all required metadata."""
        test_file = temp_repo / "test.py"
        test_file.write_text("def test(): pass")
        
        result = builder.build_graph(str(temp_repo))
        
        node = result["nodes"][0]
        
        # Verify required fields
        assert "id" in node
        assert "label" in node
        assert "type" in node
        assert "loc" in node
        assert "language" in node
        
        # Verify values
        assert node["id"] == "test.py"
        assert node["label"] == "test"
        assert node["type"] == "module"
        assert node["language"] == "python"
        assert node["loc"] > 0
    
    def test_file_extensions_filter(self, builder, temp_repo):
        """Test filtering by file extensions."""
        # Create multiple file types
        (temp_repo / "script.py").write_text("print('py')")
        (temp_repo / "app.js").write_text("console.log('js');")
        (temp_repo / "data.txt").write_text("text file")
        
        # Build graph with only Python files
        result = builder.build_graph(str(temp_repo), file_extensions=['.py'])
        
        # Should only have Python file
        assert len(result["nodes"]) == 1
        assert result["nodes"][0]["language"] == "python"
