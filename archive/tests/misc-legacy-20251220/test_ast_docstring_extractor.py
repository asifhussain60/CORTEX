"""
Tests for AST Docstring Extractor

TDD RED Phase: Tests written BEFORE implementation
Following CORTEX TDD Mastery workflow

Author: Asif Hussain
"""

import pytest
from pathlib import Path
import tempfile
import shutil
from src.dashboard.intelligence.ast_docstring_extractor import (
    ASTDocstringExtractor,
    DocstringInfo,
    ExtractionResult
)


class TestDocstringInfo:
    """Test DocstringInfo dataclass"""
    
    def test_summary_extraction_first_paragraph(self):
        """Should extract first paragraph as summary"""
        docstring = "First paragraph.\n\nSecond paragraph."
        info = DocstringInfo(
            file_path="test.py",
            entity_type="class",
            entity_name="TestClass",
            docstring=docstring,
            line_number=1,
            char_count=len(docstring),
            summary=""
        )
        
        assert info.summary == "First paragraph."
    
    def test_summary_extraction_single_line(self):
        """Should handle single-line docstrings"""
        docstring = "Single line docstring."
        info = DocstringInfo(
            file_path="test.py",
            entity_type="function",
            entity_name="test_func",
            docstring=docstring,
            line_number=5,
            char_count=len(docstring),
            summary=""
        )
        
        assert info.summary == "Single line docstring."
    
    def test_summary_max_length_200_chars(self):
        """Should truncate summary to 200 chars"""
        long_docstring = "A" * 300
        info = DocstringInfo(
            file_path="test.py",
            entity_type="module",
            entity_name="test_module",
            docstring=long_docstring,
            line_number=1,
            char_count=len(long_docstring),
            summary=""
        )
        
        assert len(info.summary) <= 200


class TestASTDocstringExtractor:
    """Test ASTDocstringExtractor main functionality"""
    
    @pytest.fixture
    def temp_repo(self):
        """Create temporary repository with sample Python files"""
        temp_dir = Path(tempfile.mkdtemp())
        
        # Create sample files with docstrings
        (temp_dir / "controller.py").write_text('''
"""
UserController module.

Handles user authentication and profile management.
"""

class UserController:
    """
    Controller for user operations.
    
    Manages user authentication, registration, and profile updates.
    Integrates with database and external auth services.
    """
    
    def authenticate(self, username, password):
        """Authenticate user credentials."""
        pass
    
    def _internal_method(self):
        """Should be skipped (private)."""
        pass
''')
        
        (temp_dir / "service.py").write_text('''
"""Payment service module."""

class PaymentService:
    """
    Handles payment processing and transaction management.
    
    Supports credit card, PayPal, and bank transfer payments.
    """
    pass
''')
        
        (temp_dir / "no_docstring.py").write_text('''
class NoDocstringClass:
    pass

def no_docstring_func():
    return True
''')
        
        (temp_dir / "syntax_error.py").write_text('''
def broken_syntax(
    # Missing closing parenthesis
''')
        
        # Create excluded directory
        (temp_dir / "tests").mkdir()
        (temp_dir / "tests" / "test_skip.py").write_text('''
"""Should be skipped - test file"""
class TestClass:
    """Test docstring"""
    pass
''')
        
        yield temp_dir
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    def test_extract_from_repository_success(self, temp_repo):
        """Should extract docstrings from all valid Python files"""
        extractor = ASTDocstringExtractor()
        result = extractor.extract_from_repository(temp_repo)
        
        assert isinstance(result, ExtractionResult)
        assert result.total_files_scanned > 0
        assert result.successful_extractions > 0
        assert len(result.docstrings) > 0
    
    def test_extracts_module_docstrings(self, temp_repo):
        """Should extract module-level docstrings"""
        extractor = ASTDocstringExtractor()
        result = extractor.extract_from_repository(temp_repo)
        
        module_docstrings = [d for d in result.docstrings if d.entity_type == 'module']
        assert len(module_docstrings) >= 2  # controller.py and service.py
    
    def test_extracts_class_docstrings(self, temp_repo):
        """Should extract class docstrings"""
        extractor = ASTDocstringExtractor()
        result = extractor.extract_from_repository(temp_repo)
        
        class_docstrings = [d for d in result.docstrings if d.entity_type == 'class']
        assert len(class_docstrings) >= 2  # UserController and PaymentService
        
        # Check specific class
        user_controller = next(
            (d for d in class_docstrings if d.entity_name == 'UserController'),
            None
        )
        assert user_controller is not None
        assert 'authentication' in user_controller.docstring.lower()
    
    def test_extracts_function_docstrings(self, temp_repo):
        """Should extract public function docstrings"""
        extractor = ASTDocstringExtractor()
        result = extractor.extract_from_repository(temp_repo)
        
        func_docstrings = [d for d in result.docstrings if d.entity_type == 'function']
        assert len(func_docstrings) >= 1  # authenticate method
        
        # Check authenticate function
        auth_func = next(
            (d for d in func_docstrings if d.entity_name == 'authenticate'),
            None
        )
        assert auth_func is not None
    
    def test_skips_private_methods(self, temp_repo):
        """Should skip private methods (starting with _)"""
        extractor = ASTDocstringExtractor()
        result = extractor.extract_from_repository(temp_repo)
        
        func_docstrings = [d for d in result.docstrings if d.entity_type == 'function']
        private_methods = [d for d in func_docstrings if d.entity_name.startswith('_')]
        
        assert len(private_methods) == 0
    
    def test_skips_files_without_docstrings(self, temp_repo):
        """Should handle files without docstrings"""
        extractor = ASTDocstringExtractor()
        result = extractor.extract_from_repository(temp_repo)
        
        # Should not crash, should not extract from no_docstring.py
        no_doc_extractions = [
            d for d in result.docstrings 
            if 'no_docstring.py' in d.file_path
        ]
        assert len(no_doc_extractions) == 0
    
    def test_handles_syntax_errors_gracefully(self, temp_repo):
        """Should skip files with syntax errors and continue"""
        extractor = ASTDocstringExtractor()
        result = extractor.extract_from_repository(temp_repo)
        
        # Should have at least one failed file (syntax_error.py)
        assert len(result.failed_files) > 0
        assert any('syntax_error.py' in f for f in result.failed_files)
        
        # But should still extract from valid files
        assert result.successful_extractions > 0
    
    def test_excludes_test_directories(self, temp_repo):
        """Should exclude test directories and test files"""
        extractor = ASTDocstringExtractor()
        result = extractor.extract_from_repository(temp_repo)
        
        # Should not extract from tests/test_skip.py
        test_extractions = [
            d for d in result.docstrings 
            if 'test' in d.file_path.lower()
        ]
        assert len(test_extractions) == 0
    
    def test_min_docstring_length_filter(self, temp_repo):
        """Should filter out short docstrings below minimum length"""
        extractor = ASTDocstringExtractor(min_docstring_length=100)
        result = extractor.extract_from_repository(temp_repo)
        
        # All extracted docstrings should meet minimum length
        for doc in result.docstrings:
            assert len(doc.docstring) >= 100
    
    def test_max_files_limit(self, temp_repo):
        """Should respect max_files limit"""
        extractor = ASTDocstringExtractor(max_files=1)
        result = extractor.extract_from_repository(temp_repo)
        
        # Should scan at most 1 file
        assert result.total_files_scanned <= 1
    
    def test_prioritizes_controller_service_files(self, temp_repo):
        """Should prioritize files with controller/service in name"""
        extractor = ASTDocstringExtractor(max_files=1)
        result = extractor.extract_from_repository(temp_repo)
        
        # First file scanned should be controller.py or service.py
        if result.docstrings:
            first_file = Path(result.docstrings[0].file_path).name
            assert 'controller' in first_file or 'service' in first_file
    
    def test_ranks_docstrings_by_informativeness(self, temp_repo):
        """Should rank docstrings with most informative first"""
        extractor = ASTDocstringExtractor()
        result = extractor.extract_from_repository(temp_repo)
        
        assert len(result.top_docstrings) > 0
        
        # Top docstring should be more informative than last
        if len(result.top_docstrings) > 1:
            first = result.top_docstrings[0]
            last = result.top_docstrings[-1]
            
            # First should have more content or business terms
            assert first.char_count >= last.char_count or \
                   'user' in first.docstring.lower() or \
                   'payment' in first.docstring.lower()
    
    def test_generate_narrative_from_docstrings(self, temp_repo):
        """Should generate coherent narrative from top docstrings"""
        extractor = ASTDocstringExtractor()
        result = extractor.extract_from_repository(temp_repo)
        
        narrative = extractor.generate_narrative(result)
        
        assert isinstance(narrative, str)
        assert len(narrative) > 0
        assert narrative.endswith('.')  # Proper sentence ending
        
        # Should contain business context from docstrings
        narrative_lower = narrative.lower()
        assert 'user' in narrative_lower or 'payment' in narrative_lower
    
    def test_generate_narrative_handles_no_docstrings(self, temp_repo):
        """Should handle case with no docstrings"""
        # Create empty result
        empty_result = ExtractionResult(
            total_files_scanned=0,
            successful_extractions=0,
            failed_files=[],
            docstrings=[],
            top_docstrings=[]
        )
        
        extractor = ASTDocstringExtractor()
        narrative = extractor.generate_narrative(empty_result)
        
        assert 'no documentation' in narrative.lower() or 'undocumented' in narrative.lower()
    
    def test_parallel_processing(self, temp_repo):
        """Should process files in parallel without errors"""
        # Create multiple files to trigger parallel processing
        for i in range(10):
            (temp_repo / f"file_{i}.py").write_text(f'''
"""Module {i} docstring."""

class Class{i}:
    """Class {i} docstring."""
    pass
''')
        
        extractor = ASTDocstringExtractor()
        result = extractor.extract_from_repository(temp_repo)
        
        # Should successfully extract from all files
        assert result.successful_extractions >= 10


class TestRealWorldScenarios:
    """Test with realistic code patterns"""
    
    def test_django_style_docstrings(self):
        """Should handle Django-style class docstrings"""
        code = '''
class UserViewSet:
    """
    API endpoint for user operations.
    
    list: Return list of all users
    retrieve: Return user by ID
    create: Create new user
    update: Update existing user
    destroy: Delete user
    """
    pass
'''
        # Test will be implemented after basic functionality works
        pass
    
    def test_google_style_docstrings(self):
        """Should handle Google-style docstrings with Args/Returns"""
        code = '''
def calculate_total(items, tax_rate):
    """
    Calculate total cost including tax.
    
    Args:
        items (list): List of items with prices
        tax_rate (float): Tax rate as decimal (e.g., 0.08)
    
    Returns:
        float: Total cost including tax
    
    Raises:
        ValueError: If items is empty
    """
    pass
'''
        # Test will be implemented after basic functionality works
        pass
