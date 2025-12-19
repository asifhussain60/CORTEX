"""
TEST RED Phase - Python Docstring Extraction

Tests for get_top_docstrings() method in PythonAnalyzer.
These tests MUST FAIL initially (RED phase).

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import pytest
import ast
from pathlib import Path
from src.intelligence.analyzers.python_analyzer import PythonAnalyzer
from src.intelligence.docstring_extractor import DocstringInfo, DocstringSource


class TestPythonDocstringExtractorRED:
    """Test suite for Python docstring extraction - RED phase"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.analyzer = PythonAnalyzer()
        self.fixtures_dir = Path(__file__).parent.parent / "fixtures" / "python"
        self.fixtures_dir.mkdir(parents=True, exist_ok=True)
    
    def test_get_top_docstrings_method_exists(self):
        """Test that get_top_docstrings method exists"""
        assert hasattr(self.analyzer, 'get_top_docstrings'), \
            "PythonAnalyzer must have get_top_docstrings method"
    
    def test_extract_module_level_docstring(self):
        """Test extraction of module-level docstring"""
        code = '''"""
This is a comprehensive module docstring.
It describes the module's purpose, features, and usage.

Features:
- Feature A
- Feature B

Author: Test Author
"""

def some_function():
    pass
'''
        file_path = self.fixtures_dir / "test_module_docstring.py"
        file_path.write_text(code)
        
        result = self.analyzer.get_top_docstrings(file_path, limit=5)
        
        assert isinstance(result, list), "Result must be a list"
        assert len(result) > 0, "Should extract at least module docstring"
        
        # Find module docstring
        module_doc = next((d for d in result if d.object_type == "module"), None)
        assert module_doc is not None, "Should extract module-level docstring"
        assert "comprehensive module docstring" in module_doc.docstring_text
        assert module_doc.language == "python"
        assert module_doc.source_type == DocstringSource.MODULE_LEVEL
        assert module_doc.informativeness_score > 0.5, "Well-structured docstring should score high"
    
    def test_extract_class_docstrings(self):
        """Test extraction of class-level docstrings"""
        code = '''
class DataProcessor:
    """
    Processes data from multiple sources.
    
    This class handles data ingestion, validation, and transformation
    for analytics pipelines.
    
    Attributes:
        source_type: Type of data source (database, api, file)
        validators: List of validation rules
    
    Example:
        processor = DataProcessor("database")
        processor.process(data)
    """
    
    def process(self, data):
        """Process the data"""
        pass

class SimpleClass:
    """A simple class with minimal documentation"""
    pass
'''
        file_path = self.fixtures_dir / "test_class_docstrings.py"
        file_path.write_text(code)
        
        result = self.analyzer.get_top_docstrings(file_path, limit=10)
        
        # Should extract both class docstrings
        class_docs = [d for d in result if d.object_type == "class"]
        assert len(class_docs) >= 2, "Should extract both class docstrings"
        
        # DataProcessor should rank higher due to structure and length
        data_processor_doc = next((d for d in class_docs if d.object_name == "DataProcessor"), None)
        simple_class_doc = next((d for d in class_docs if d.object_name == "SimpleClass"), None)
        
        assert data_processor_doc is not None
        assert simple_class_doc is not None
        assert data_processor_doc.informativeness_score > simple_class_doc.informativeness_score, \
            "More detailed docstring should score higher"
    
    def test_extract_function_docstrings(self):
        """Test extraction of function-level docstrings"""
        code = '''
def authenticate_user(username: str, password: str) -> bool:
    """
    Authenticate user with provided credentials.
    
    Args:
        username: User's login name
        password: User's password (will be hashed)
    
    Returns:
        bool: True if authentication successful, False otherwise
    
    Raises:
        ValueError: If username or password is empty
        AuthenticationError: If authentication fails
    
    Example:
        >>> authenticate_user("john", "secret123")
        True
    """
    pass

def helper():
    """Quick helper function"""
    pass
'''
        file_path = self.fixtures_dir / "test_function_docstrings.py"
        file_path.write_text(code)
        
        result = self.analyzer.get_top_docstrings(file_path, limit=10)
        
        func_docs = [d for d in result if d.object_type == "function"]
        assert len(func_docs) >= 2, "Should extract both function docstrings"
        
        # authenticate_user should rank much higher
        auth_doc = next((d for d in func_docs if d.object_name == "authenticate_user"), None)
        helper_doc = next((d for d in func_docs if d.object_name == "helper"), None)
        
        assert auth_doc is not None
        assert helper_doc is not None
        assert auth_doc.informativeness_score > helper_doc.informativeness_score
        assert auth_doc.informativeness_score > 0.7, "Well-documented function should score very high"
    
    def test_extract_method_docstrings(self):
        """Test extraction of method-level docstrings"""
        code = '''
class APIClient:
    """REST API client for external service"""
    
    def __init__(self, base_url: str):
        """
        Initialize API client.
        
        Args:
            base_url: Base URL for API endpoint
        """
        self.base_url = base_url
    
    def fetch_data(self, endpoint: str, params: dict) -> dict:
        """
        Fetch data from API endpoint.
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
        
        Returns:
            dict: JSON response data
        
        Raises:
            RequestException: If HTTP request fails
            JSONDecodeError: If response is not valid JSON
        """
        pass
    
    def _internal_helper(self):
        """Internal helper method"""
        pass
'''
        file_path = self.fixtures_dir / "test_method_docstrings.py"
        file_path.write_text(code)
        
        result = self.analyzer.get_top_docstrings(file_path, limit=10)
        
        method_docs = [d for d in result if d.object_type == "method"]
        assert len(method_docs) >= 3, "Should extract all method docstrings"
        
        # fetch_data should rank highest among methods
        fetch_doc = next((d for d in method_docs if d.object_name == "fetch_data"), None)
        assert fetch_doc is not None
        assert fetch_doc.informativeness_score > 0.6
        assert fetch_doc.metadata.get('parent_class') == "APIClient"
    
    def test_ranking_by_informativeness(self):
        """Test that docstrings are ranked by informativeness score"""
        code = '''
"""
Comprehensive Data Analytics Module

This module provides advanced analytics capabilities for processing
large-scale datasets from multiple sources.

Features:
- Real-time data ingestion from databases and APIs
- Data validation and cleaning
- Statistical analysis and aggregation
- Machine learning model integration
- Performance optimization with caching

Example:
    from analytics import DataAnalyzer
    
    analyzer = DataAnalyzer(source="database")
    results = analyzer.analyze(dataset)

Author: Analytics Team
"""

class DataAnalyzer:
    """Main analyzer class"""
    
    def analyze(self, data):
        """Analyze data"""
        pass

def helper():
    """Helper function"""
    pass
'''
        file_path = self.fixtures_dir / "test_ranking.py"
        file_path.write_text(code)
        
        result = self.analyzer.get_top_docstrings(file_path, limit=10)
        
        # Module docstring should rank first (most comprehensive)
        assert result[0].object_type == "module", \
            "Most informative (module) docstring should rank first"
        assert result[0].informativeness_score > 0.7
        
        # Scores should be in descending order
        for i in range(len(result) - 1):
            assert result[i].informativeness_score >= result[i + 1].informativeness_score, \
                "Docstrings must be sorted by score descending"
    
    def test_limit_parameter(self):
        """Test that limit parameter controls number of results"""
        code = '''
"""Module docstring"""

class Class1:
    """Class 1 docstring"""
    def method1(self):
        """Method 1 docstring"""
        pass
    def method2(self):
        """Method 2 docstring"""
        pass

class Class2:
    """Class 2 docstring"""
    def method3(self):
        """Method 3 docstring"""
        pass

def function1():
    """Function 1 docstring"""
    pass

def function2():
    """Function 2 docstring"""
    pass
'''
        file_path = self.fixtures_dir / "test_limit.py"
        file_path.write_text(code)
        
        # Request only top 3
        result = self.analyzer.get_top_docstrings(file_path, limit=3)
        assert len(result) == 3, "Should return exactly 3 docstrings when limit=3"
        
        # Request top 5
        result = self.analyzer.get_top_docstrings(file_path, limit=5)
        assert len(result) == 5, "Should return exactly 5 docstrings when limit=5"
        
        # Request more than available (should return all)
        result = self.analyzer.get_top_docstrings(file_path, limit=100)
        assert len(result) <= 8, "Should return all docstrings (8 total)"
    
    def test_handles_missing_docstrings(self):
        """Test handling of classes/functions without docstrings"""
        code = '''
def no_docstring_function():
    pass

class NoDocstringClass:
    def no_docstring_method(self):
        pass

def with_docstring():
    """This function has a docstring"""
    pass
'''
        file_path = self.fixtures_dir / "test_missing_docstrings.py"
        file_path.write_text(code)
        
        result = self.analyzer.get_top_docstrings(file_path, limit=10)
        
        # Should only return items WITH docstrings
        assert all(d.docstring_text.strip() for d in result), \
            "Should not return empty docstrings"
        assert len(result) == 1, "Should only extract the one function with docstring"
    
    def test_handles_file_not_found(self):
        """Test graceful handling of non-existent files"""
        fake_path = Path("/nonexistent/file.py")
        
        with pytest.raises(FileNotFoundError):
            self.analyzer.get_top_docstrings(fake_path)
    
    def test_handles_syntax_errors(self):
        """Test handling of files with syntax errors"""
        code = '''
def broken_function(
    # Missing closing parenthesis and colon
    """This file has syntax errors"""
    pass
'''
        file_path = self.fixtures_dir / "test_syntax_error.py"
        file_path.write_text(code)
        
        # Should raise SyntaxError or return empty list
        result = self.analyzer.get_top_docstrings(file_path)
        assert result == [] or isinstance(result, list), \
            "Should handle syntax errors gracefully"
    
    def test_performance_with_large_file(self):
        """Test performance with file containing many docstrings"""
        import time
        
        # Generate file with 100 classes, each with 5 methods
        code_parts = ['"""Large module for performance testing"""']
        
        for i in range(100):
            code_parts.append(f'''
class Class{i}:
    """
    Class {i} documentation with moderate detail.
    This class performs operations related to feature {i}.
    
    Attributes:
        attr1: First attribute
        attr2: Second attribute
    """
    
    def method1(self):
        """Method 1 in Class {i}"""
        pass
    
    def method2(self):
        """Method 2 in Class {i}"""
        pass
    
    def method3(self):
        """Method 3 in Class {i}"""
        pass
    
    def method4(self):
        """Method 4 in Class {i}"""
        pass
    
    def method5(self):
        """Method 5 in Class {i}"""
        pass
''')
        
        code = '\n'.join(code_parts)
        file_path = self.fixtures_dir / "test_performance_large.py"
        file_path.write_text(code)
        
        start_time = time.time()
        result = self.analyzer.get_top_docstrings(file_path, limit=10)
        elapsed = time.time() - start_time
        
        assert elapsed < 2.0, f"Should process large file in <2 seconds, took {elapsed:.2f}s"
        assert len(result) == 10, "Should return exactly 10 top docstrings"
        assert all(isinstance(d, DocstringInfo) for d in result), \
            "All results must be DocstringInfo instances"
    
    def test_docstring_info_schema(self):
        """Test that returned DocstringInfo objects have correct schema"""
        code = '''
"""Module docstring"""

class TestClass:
    """Class docstring"""
    def test_method(self):
        """Method docstring"""
        pass
'''
        file_path = self.fixtures_dir / "test_schema.py"
        file_path.write_text(code)
        
        result = self.analyzer.get_top_docstrings(file_path, limit=10)
        
        for doc in result:
            # Verify all required fields
            assert isinstance(doc, DocstringInfo), "Must return DocstringInfo instances"
            assert isinstance(doc.source_file, Path), "source_file must be Path"
            assert isinstance(doc.object_name, str), "object_name must be string"
            assert isinstance(doc.object_type, str), "object_type must be string"
            assert isinstance(doc.docstring_text, str), "docstring_text must be string"
            assert isinstance(doc.line_number, int), "line_number must be int"
            assert doc.language == "python", "language must be 'python'"
            assert isinstance(doc.source_type, (DocstringSource, str)), "source_type must be DocstringSource"
            assert isinstance(doc.informativeness_score, float), "informativeness_score must be float"
            assert 0.0 <= doc.informativeness_score <= 1.0, "Score must be between 0 and 1"
            assert isinstance(doc.metadata, dict), "metadata must be dict"
    
    def test_includes_line_numbers(self):
        """Test that line numbers are accurately captured"""
        code = '''"""Line 1: Module docstring"""

class ClassAtLine3:
    """Class docstring at line 4"""
    pass

def function_at_line7():
    """Function docstring at line 8"""
    pass
'''
        file_path = self.fixtures_dir / "test_line_numbers.py"
        file_path.write_text(code)
        
        result = self.analyzer.get_top_docstrings(file_path, limit=10)
        
        module_doc = next((d for d in result if d.object_type == "module"), None)
        assert module_doc.line_number == 1
        
        class_doc = next((d for d in result if d.object_name == "ClassAtLine3"), None)
        assert class_doc.line_number == 3  # Class definition line
        
        func_doc = next((d for d in result if d.object_name == "function_at_line7"), None)
        assert func_doc.line_number == 7  # Function definition line


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
