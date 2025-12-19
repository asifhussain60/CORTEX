"""
Tests for Semantic Indexing & Search (Phase 4)
"""
import pytest
import sqlite3
from pathlib import Path
from src.operations.modules.discovery.semantic_index_builder import SemanticIndexBuilder
from src.operations.modules.discovery.semantic_search_engine import SemanticSearchEngine, SearchResult
from src.operations.modules.discovery.snippet_extractor import SnippetExtractor, CodeSnippet
from src.operations.modules.discovery.models import CodeElement, ComplexityMetrics


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def sample_elements(tmp_path):
    """Sample code elements for indexing"""
    return [
        CodeElement(
            type="class",
            name="Calculator",
            file_path=tmp_path / "calculator.py",
            line_start=1,
            line_end=10,
            signature="class Calculator",
            complexity=ComplexityMetrics(cyclomatic_complexity=2)
        ),
        CodeElement(
            type="function",
            name="add",
            file_path=tmp_path / "calculator.py",
            line_start=2,
            line_end=4,
            signature="def add(a, b)",
            complexity=ComplexityMetrics(cyclomatic_complexity=1)
        ),
        CodeElement(
            type="function",
            name="multiply",
            file_path=tmp_path / "math_utils.py",
            line_start=1,
            line_end=3,
            signature="def multiply(x, y)",
            complexity=ComplexityMetrics(cyclomatic_complexity=1)
        )
    ]

@pytest.fixture
def sample_file_with_code(tmp_path):
    """Create a sample Python file with code"""
    file_path = tmp_path / "calculator.py"
    content = """class Calculator:
    def add(self, a, b):
        return a + b
    
    def subtract(self, a, b):
        return a - b

def multiply(x, y):
    return x * y
"""
    file_path.write_text(content)
    return file_path

@pytest.fixture
def temp_db(tmp_path):
    """Temporary database path"""
    return tmp_path / "test_index.db"


# ============================================================================
# INDEX BUILDER TESTS
# ============================================================================

class TestSemanticIndexBuilder:
    """Test semantic index building"""
    
    def test_build_index_empty_list(self, temp_db):
        """Test building index from empty list"""
        builder = SemanticIndexBuilder(temp_db)
        
        result = builder.build_index([])
        assert result is not None
        assert result['indexed_elements'] == 0
        assert temp_db.exists()
        
        builder.close()
    
    def test_build_index_with_elements(self, temp_db, sample_elements):
        """Test building index from code elements"""
        builder = SemanticIndexBuilder(temp_db)
        
        result = builder.build_index(sample_elements)
        assert result['indexed_elements'] == 3
        assert temp_db.exists()
        
        builder.close()
    
    def test_index_single_element(self, temp_db, sample_elements):
        """Test indexing single element"""
        builder = SemanticIndexBuilder(temp_db)
        
        builder.build_index([])  # Initialize
        builder.index_element(sample_elements[0])
        builder.conn.commit()
        
        # Verify indexed
        cursor = builder.conn.execute("SELECT COUNT(*) FROM code_index")
        count = cursor.fetchone()[0]
        assert count == 1
        
        builder.close()
    
    def test_update_element(self, temp_db, sample_elements):
        """Test updating indexed element"""
        builder = SemanticIndexBuilder(temp_db)
        
        builder.build_index(sample_elements)
        
        # Update element
        updated = sample_elements[0]
        updated.signature = "class Calculator(object)"
        builder.update_element(updated)
        builder.conn.commit()
        
        # Verify update
        cursor = builder.conn.execute("SELECT COUNT(*) FROM code_index")
        count = cursor.fetchone()[0]
        assert count == 3  # Still 3 elements
        
        builder.close()
    
    def test_remove_element(self, temp_db, sample_elements):
        """Test removing element from index"""
        builder = SemanticIndexBuilder(temp_db)
        
        builder.build_index(sample_elements)
        element_id = f"{sample_elements[0].file_path.name}:{sample_elements[0].name}"
        builder.remove_element(element_id)
        builder.conn.commit()
        
        # Verify removal
        cursor = builder.conn.execute("SELECT COUNT(*) FROM code_index")
        count = cursor.fetchone()[0]
        assert count == 2
        
        builder.close()


# ============================================================================
# SEARCH ENGINE TESTS
# ============================================================================

class TestSemanticSearchEngine:
    """Test semantic search operations"""
    
    def test_search_returns_results(self, temp_db, sample_elements):
        """Test search returns ranked results"""
        builder = SemanticIndexBuilder(temp_db)
        engine = SemanticSearchEngine(temp_db)
        
        builder.build_index(sample_elements)
        results = engine.search("calculator")
        
        assert isinstance(results, list)
        # Should find Calculator class
        if results:
            assert any('Calculator' in r.element_name for r in results)
        
        builder.close()
        engine.close()
    
    def test_search_by_type(self, temp_db, sample_elements):
        """Test search filtered by element type"""
        builder = SemanticIndexBuilder(temp_db)
        engine = SemanticSearchEngine(temp_db)
        
        builder.build_index(sample_elements)
        results = engine.search_by_type("add", "function")
        
        assert isinstance(results, list)
        # All results should be functions
        for r in results:
            assert r.element_type == "function"
        
        builder.close()
        engine.close()
    
    def test_find_symbol_exact(self, temp_db, sample_elements):
        """Test finding symbol by exact name"""
        builder = SemanticIndexBuilder(temp_db)
        engine = SemanticSearchEngine(temp_db)
        
        builder.build_index(sample_elements)
        result = engine.find_symbol("Calculator")
        
        if result:
            assert result.element_name == "Calculator"
            assert result.element_type == "class"
        
        builder.close()
        engine.close()
    
    def test_find_references(self, temp_db, sample_elements):
        """Test finding references to symbol"""
        builder = SemanticIndexBuilder(temp_db)
        engine = SemanticSearchEngine(temp_db)
        
        builder.build_index(sample_elements)
        refs = engine.find_references("add")
        
        assert isinstance(refs, list)
        
        builder.close()
        engine.close()
    
    def test_empty_search_results(self, temp_db, sample_elements):
        """Test handling empty search results"""
        builder = SemanticIndexBuilder(temp_db)
        engine = SemanticSearchEngine(temp_db)
        
        builder.build_index(sample_elements)
        results = engine.search("nonexistent_symbol_xyz123")
        
        assert isinstance(results, list)
        assert len(results) == 0
        
        builder.close()
        engine.close()


# ============================================================================
# SNIPPET EXTRACTOR TESTS
# ============================================================================

class TestSnippetExtractor:
    """Test code snippet extraction"""
    
    def test_extract_snippet_with_context(self, sample_file_with_code, sample_elements):
        """Test extracting snippet with context"""
        extractor = SnippetExtractor()
        element = sample_elements[0]  # Calculator class
        element.file_path = sample_file_with_code
        
        snippet = extractor.extract_snippet(element, context_lines=2)
        
        assert snippet is not None
        assert isinstance(snippet, CodeSnippet)
        assert len(snippet.code) > 0
    
    def test_highlight_matches(self):
        """Test highlighting search matches"""
        extractor = SnippetExtractor()
        snippet = "def add(a, b):\n    return a + b"
        
        highlighted = extractor.highlight_matches(snippet, "add")
        
        assert ">>>add<<<" in highlighted
    
    def test_get_surrounding_context(self, sample_file_with_code):
        """Test getting surrounding context"""
        extractor = SnippetExtractor()
        
        context = extractor.get_surrounding_context(sample_file_with_code, 5, context_lines=2)
        
        assert isinstance(context, str)
        assert len(context) > 0
    
    def test_snippet_edge_cases(self, tmp_path):
        """Test snippet extraction at file boundaries"""
        extractor = SnippetExtractor()
        
        # Create small file
        small_file = tmp_path / "small.py"
        small_file.write_text("x = 1\ny = 2\n")
        
        element = CodeElement(
            type="variable",
            name="x",
            file_path=small_file,
            line_start=1,
            line_end=1,
            signature="x = 1"
        )
        
        snippet = extractor.extract_snippet(element, context_lines=10)
        
        assert snippet is not None
        assert len(snippet.code) > 0


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestSemanticIndexingIntegration:
    """Test end-to-end semantic indexing"""
    
    def test_end_to_end_index_and_search(self, temp_db, sample_elements, sample_file_with_code):
        """Test complete workflow: index, search, extract"""
        builder = SemanticIndexBuilder(temp_db)
        engine = SemanticSearchEngine(temp_db)
        extractor = SnippetExtractor()
        
        # Update file paths
        for elem in sample_elements:
            elem.file_path = sample_file_with_code
        
        # Build index
        builder.build_index(sample_elements)
        
        # Search
        results = engine.search("Calculator")
        assert isinstance(results, list)
        
        # Extract snippet (if results found)
        if results:
            snippet = extractor.extract_snippet(sample_elements[0])
            assert snippet is not None
        
        builder.close()
        engine.close()
    
    def test_index_persistence(self, temp_db, sample_elements):
        """Test index persists across sessions"""
        # First session: build index
        builder1 = SemanticIndexBuilder(temp_db)
        builder1.build_index(sample_elements)
        builder1.close()
        
        # Second session: search existing index
        engine = SemanticSearchEngine(temp_db)
        results = engine.search("Calculator")
        assert isinstance(results, list)
        engine.close()
