"""
Golden tests for LENS Knowledge Graph — graph database operations.

Authority: Phase 3 Wave 4 | Zero-Mock Philosophy
Test Count: 10 golden tests
"""
import pytest
from pathlib import Path


class TestKnowledgeGraphConstruction:
    """Golden test: Build knowledge graph from code AST."""
    
    def test_create_graph_from_python_file(self, tmp_path: Path) -> None:
        """Golden: Create knowledge graph nodes from Python AST."""
        from cortex_lens.knowledge_graph.ast_graph_builder import ASTKnowledgeGraphBuilder
        
        builder = ASTKnowledgeGraphBuilder()
        
        # Python code with class and function
        code_path = tmp_path / "example.py"
        code_path.write_text("""
class Calculator:
    def add(self, a: int, b: int) -> int:
        return a + b

def multiply(x, y):
    return x * y
""")
        
        graph = builder.build_from_file(code_path)
        
        assert graph.node_count >= 3  # File, class, functions
        assert graph.has_node("Calculator")
        assert graph.has_node("add")
        assert graph.has_node("multiply")
    
    def test_graph_relationships(self, tmp_path: Path) -> None:
        """Golden: Capture relationships between code entities."""
        from cortex_lens.knowledge_graph.ast_graph_builder import ASTKnowledgeGraphBuilder
        
        builder = ASTKnowledgeGraphBuilder()
        
        code_path = tmp_path / "models.py"
        code_path.write_text("""
class User:
    def __init__(self, name: str):
        self.name = name
    
    def greet(self) -> str:
        return f"Hello, {self.name}"
""")
        
        graph = builder.build_from_file(code_path)
        
        # Check relationships
        assert graph.has_relationship("User", "CONTAINS", "greet")
        assert graph.has_relationship("User", "CONTAINS", "__init__")
    
    def test_cross_file_dependencies(self, tmp_path: Path) -> None:
        """Golden: Detect imports and cross-file dependencies."""
        from cortex_lens.knowledge_graph.ast_graph_builder import ASTKnowledgeGraphBuilder
        
        builder = ASTKnowledgeGraphBuilder()
        
        # File 1
        file1 = tmp_path / "utils.py"
        file1.write_text("def helper(): pass")
        
        # File 2 imports file 1
        file2 = tmp_path / "main.py"
        file2.write_text("from utils import helper\n\ndef main(): helper()")
        
        graph = builder.build_from_directory(tmp_path)
        
        assert graph.has_relationship("main.py", "IMPORTS", "utils.py")
        assert graph.has_relationship("main", "CALLS", "helper")


class TestSemanticSearch:
    """Golden test: Semantic search over knowledge graph."""
    
    def test_search_by_name(self, tmp_path: Path) -> None:
        """Golden: Search for code entities by name."""
        from cortex_lens.knowledge_graph.ast_graph_builder import ASTKnowledgeGraphBuilder
        from cortex_lens.knowledge_graph.semantic_search import SemanticSearchEngine
        
        builder = ASTKnowledgeGraphBuilder()
        code_path = tmp_path / "app.py"
        code_path.write_text("""
def calculate_total(items):
    return sum(items)

def process_order(order):
    total = calculate_total(order.items)
    return total
""")
        
        graph = builder.build_from_file(code_path)
        search = SemanticSearchEngine(graph)
        
        results = search.find_by_name("calculate_total")
        
        assert len(results) == 1
        assert results[0].name == "calculate_total"
        assert results[0].type == "function"
    
    def test_search_by_pattern(self, tmp_path: Path) -> None:
        """Golden: Search for architectural patterns."""
        from cortex_lens.knowledge_graph.ast_graph_builder import ASTKnowledgeGraphBuilder
        from cortex_lens.knowledge_graph.semantic_search import SemanticSearchEngine
        
        builder = ASTKnowledgeGraphBuilder()
        code_path = tmp_path / "service.py"
        code_path.write_text("""
class UserService:
    def __init__(self, repository):
        self.repository = repository
    
    def get_user(self, user_id):
        return self.repository.find(user_id)
""")
        
        graph = builder.build_from_file(code_path)
        search = SemanticSearchEngine(graph)
        
        # Search for repository pattern
        results = search.find_pattern("repository_pattern")
        
        assert len(results) > 0
        assert any("UserService" in r.name for r in results)


class TestArchitecturalPatterns:
    """Golden test: Detect architectural patterns via graph queries."""
    
    def test_detect_mvc_pattern(self, tmp_path: Path) -> None:
        """Golden: Detect MVC pattern in codebase."""
        from cortex_lens.knowledge_graph.ast_graph_builder import ASTKnowledgeGraphBuilder
        from cortex_lens.knowledge_graph.pattern_detector import PatternDetector
        
        builder = ASTKnowledgeGraphBuilder()
        
        # Create MVC structure
        (tmp_path / "models.py").write_text("class User: pass")
        (tmp_path / "views.py").write_text("class UserView: pass")
        (tmp_path / "controllers.py").write_text("class UserController: pass")
        
        graph = builder.build_from_directory(tmp_path)
        detector = PatternDetector(graph)
        
        patterns = detector.detect_all()
        
        assert "mvc" in [p.pattern_type for p in patterns]
    
    def test_detect_singleton_pattern(self, tmp_path: Path) -> None:
        """Golden: Detect singleton pattern in code."""
        from cortex_lens.knowledge_graph.ast_graph_builder import ASTKnowledgeGraphBuilder
        from cortex_lens.knowledge_graph.pattern_detector import PatternDetector
        
        builder = ASTKnowledgeGraphBuilder()
        
        code_path = tmp_path / "singleton.py"
        code_path.write_text("""
class DatabaseConnection:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
""")
        
        graph = builder.build_from_file(code_path)
        detector = PatternDetector(graph)
        
        patterns = detector.detect_all()
        
        assert "singleton" in [p.pattern_type for p in patterns]


class TestGraphPerformance:
    """Golden test: Performance benchmarks for graph operations."""
    
    def test_search_performance(self, tmp_path: Path) -> None:
        """Golden: Search completes within 500ms."""
        import time
        from cortex_lens.knowledge_graph.ast_graph_builder import ASTKnowledgeGraphBuilder
        from cortex_lens.knowledge_graph.semantic_search import SemanticSearchEngine
        
        builder = ASTKnowledgeGraphBuilder()
        
        # Create moderate-sized codebase
        for i in range(50):
            (tmp_path / f"module_{i}.py").write_text(f"def func_{i}(): pass")
        
        graph = builder.build_from_directory(tmp_path)
        search = SemanticSearchEngine(graph)
        
        start = time.time()
        results = search.find_by_name("func_25")
        duration = time.time() - start
        
        assert len(results) == 1
        assert duration < 0.5  # <500ms
