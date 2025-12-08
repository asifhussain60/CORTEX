"""
Tests for AST Docstring Extractor

RED PHASE: Write failing tests first

Author: Asif Hussain
Copyright: © 2025 Asif Hussain. All rights reserved.
"""

import pytest
import tempfile
from pathlib import Path
from src.intelligence.ast_docstring_extractor import (
    AstDocstringExtractor,
    DocstringInfo
)


class TestAstDocstringExtractorInitialization:
    """Test extractor initialization."""
    
    def test_extractor_creation(self):
        """Should create extractor instance."""
        extractor = AstDocstringExtractor()
        assert extractor is not None


class TestClassDocstringExtraction:
    """Test class docstring extraction."""
    
    def test_extract_class_docstring(self):
        """Should extract docstring from class."""
        code = '''
class UserService:
    """
    Manages user authentication and authorization.
    Provides secure access control for enterprise applications.
    """
    pass
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            f.flush()
            
            extractor = AstDocstringExtractor()
            results = extractor.extract_from_file(Path(f.name))
            
            assert len(results) == 1
            assert results[0].name == 'UserService'
            assert results[0].type == 'class'
            assert 'authentication' in results[0].docstring.lower()
            assert results[0].line_number > 0
    
    def test_extract_multiple_classes(self):
        """Should extract docstrings from multiple classes."""
        code = '''
class AuthController:
    """Handles authentication requests."""
    pass

class PaymentController:
    """Processes payment transactions."""
    pass
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            f.flush()
            
            extractor = AstDocstringExtractor()
            results = extractor.extract_from_file(Path(f.name))
            
            assert len(results) == 2
            names = [r.name for r in results]
            assert 'AuthController' in names
            assert 'PaymentController' in names


class TestFunctionDocstringExtraction:
    """Test function docstring extraction."""
    
    def test_extract_function_docstring(self):
        """Should extract docstring from function."""
        code = '''
def calculate_total(items):
    """
    Calculate total price for items.
    
    Args:
        items: List of items to calculate
    
    Returns:
        Total price as decimal
    """
    return sum(item.price for item in items)
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            f.flush()
            
            extractor = AstDocstringExtractor()
            results = extractor.extract_from_file(Path(f.name))
            
            assert len(results) == 1
            assert results[0].name == 'calculate_total'
            assert results[0].type == 'function'
            assert 'calculate total price' in results[0].docstring.lower()
    
    def test_extract_mixed_classes_and_functions(self):
        """Should extract docstrings from both classes and functions."""
        code = '''
def process_order(order_id):
    """Process customer order by ID."""
    pass

class OrderService:
    """Manages order lifecycle."""
    
    def create_order(self):
        """Create new order."""
        pass
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            f.flush()
            
            extractor = AstDocstringExtractor()
            results = extractor.extract_from_file(Path(f.name))
            
            # Should extract top-level function and class (not nested methods by default)
            assert len(results) >= 2
            names = [r.name for r in results]
            assert 'process_order' in names
            assert 'OrderService' in names


class TestSyntaxErrorHandling:
    """Test handling of files with syntax errors."""
    
    def test_syntax_error_returns_empty_list(self):
        """Should return empty list for file with syntax errors."""
        code = '''
class BrokenClass
    """Missing colon in class definition."""
    pass
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            f.flush()
            
            extractor = AstDocstringExtractor()
            results = extractor.extract_from_file(Path(f.name))
            
            assert results == []
    
    def test_syntax_error_logged_as_warning(self, caplog):
        """Should log warning for syntax errors."""
        code = 'def broken('
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            f.flush()
            
            extractor = AstDocstringExtractor()
            extractor.extract_from_file(Path(f.name))
            
            # Should contain warning about syntax error
            assert any('syntax error' in record.message.lower() 
                      for record in caplog.records)


class TestDocstringRanking:
    """Test ranking docstrings by informativeness."""
    
    def test_rank_by_length(self):
        """Should rank longer docstrings higher."""
        code = '''
class ShortDoc:
    """Brief."""
    pass

class LongDoc:
    """
    Comprehensive documentation explaining the purpose, usage,
    and implementation details of this important class.
    """
    pass
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            f.flush()
            
            extractor = AstDocstringExtractor()
            results = extractor.extract_from_file(Path(f.name))
            
            # Results should be ranked (LongDoc first)
            assert len(results) == 2
            assert results[0].name == 'LongDoc'
            assert results[0].informativeness_score > results[1].informativeness_score
    
    def test_limit_top_n_results(self):
        """Should limit results to top N most informative."""
        code = '\n'.join([
            f'class Class{i}:\n    """Docstring for class {i}."""\n    pass'
            for i in range(20)
        ])
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            f.flush()
            
            extractor = AstDocstringExtractor()
            results = extractor.extract_from_file(Path(f.name), top_n=10)
            
            assert len(results) == 10


class TestDirectoryScanning:
    """Test scanning directory for Python files."""
    
    def test_scan_directory(self):
        """Should scan all Python files in directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # Create multiple Python files
            (tmppath / 'service1.py').write_text('''
class Service1:
    """First service."""
    pass
''')
            (tmppath / 'service2.py').write_text('''
class Service2:
    """Second service."""
    pass
''')
            (tmppath / 'readme.txt').write_text('Not a Python file')
            
            extractor = AstDocstringExtractor()
            results = extractor.extract_from_directory(tmppath)
            
            assert len(results) >= 2
            names = [r.name for r in results]
            assert 'Service1' in names
            assert 'Service2' in names
    
    def test_scan_respects_max_files(self):
        """Should limit number of files scanned."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # Create 10 Python files
            for i in range(10):
                (tmppath / f'class{i}.py').write_text(f'''
class Class{i}:
    """Class {i}."""
    pass
''')
            
            extractor = AstDocstringExtractor()
            results = extractor.extract_from_directory(tmppath, max_files=5, top_n=100)
            
            # Should have extracted from only 5 files
            assert len(results) <= 5


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_file(self):
        """Should handle empty file gracefully."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('')
            f.flush()
            
            extractor = AstDocstringExtractor()
            results = extractor.extract_from_file(Path(f.name))
            
            assert results == []
    
    def test_no_docstrings(self):
        """Should handle code without docstrings."""
        code = '''
class NoDoc:
    pass

def no_doc():
    return 42
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            f.flush()
            
            extractor = AstDocstringExtractor()
            results = extractor.extract_from_file(Path(f.name))
            
            assert results == []
    
    def test_file_not_found(self):
        """Should raise FileNotFoundError for missing file."""
        extractor = AstDocstringExtractor()
        
        with pytest.raises(FileNotFoundError):
            extractor.extract_from_file(Path('/nonexistent/file.py'))


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
