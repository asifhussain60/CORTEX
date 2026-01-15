# © 2025-2026 Asif Hussain. All rights reserved.
# AC-ID: IR-001-03 - Code Comment Intelligence Tests
"""
Tests for Code Comment Intelligence.

PHASE-07: Holistic Intent Router Intelligence
AC-ID: IR-001-03 - Code Comment Intelligence

Tests cover:
- Docstring extraction (Google, NumPy, Sphinx styles)
- Inline comment analysis
- TODO/FIXME/HACK tracking
- Comment-to-code linking
- Semantic indexing
"""

import textwrap
from pathlib import Path
from typing import Any, Dict, List

import pytest


# =============================================================================
# TEST FIXTURES
# =============================================================================


@pytest.fixture
def google_style_docstring_code() -> str:
    """Python code with Google-style docstrings."""
    return textwrap.dedent('''
        def calculate_total(items: List[dict], tax_rate: float = 0.1) -> float:
            """Calculate the total price including tax.
            
            This function takes a list of items and calculates the total
            price including the specified tax rate.
            
            Args:
                items: List of item dictionaries with 'price' key.
                tax_rate: Tax rate to apply. Defaults to 0.1 (10%).
                
            Returns:
                The total price including tax.
                
            Raises:
                ValueError: If items list is empty.
                TypeError: If item doesn't have price key.
                
            Example:
                >>> items = [{'name': 'item1', 'price': 10.0}]
                >>> calculate_total(items)
                11.0
                
            Note:
                Prices are rounded to 2 decimal places.
            
            See Also:
                calculate_discount: For applying discounts.
            """
            if not items:
                raise ValueError("Items list cannot be empty")
            total = sum(item['price'] for item in items)
            return round(total * (1 + tax_rate), 2)
    ''')


@pytest.fixture
def numpy_style_docstring_code() -> str:
    """Python code with NumPy-style docstrings."""
    return textwrap.dedent('''
        def process_array(data, axis=None):
            """Process a numerical array along specified axis.
            
            Parameters
            ----------
            data : array_like
                Input array to process.
            axis : int or None, optional
                Axis along which to process. Default is None.
                
            Returns
            -------
            ndarray
                Processed array with same shape as input.
                
            Raises
            ------
            ValueError
                If data is empty or axis is out of bounds.
                
            Notes
            -----
            Processing is done in-place when possible for efficiency.
            
            Examples
            --------
            >>> import numpy as np
            >>> data = np.array([1, 2, 3])
            >>> process_array(data)
            array([2, 4, 6])
            """
            pass
    ''')


@pytest.fixture
def sphinx_style_docstring_code() -> str:
    """Python code with Sphinx-style docstrings."""
    return textwrap.dedent('''
        def create_connection(host, port=5432, timeout=30):
            """Create a database connection.
            
            :param host: Database host address
            :type host: str
            :param port: Database port number
            :type port: int
            :param timeout: Connection timeout in seconds
            :type timeout: int
            :returns: Database connection object
            :rtype: Connection
            :raises ConnectionError: If connection fails
            
            .. note::
                Connection is automatically retried 3 times.
                
            .. seealso::
                :func:`close_connection` for cleanup
            """
            pass
    ''')


@pytest.fixture
def inline_comments_code() -> str:
    """Python code with various inline comments."""
    return textwrap.dedent('''
        def process_data(data):
            """Process incoming data."""
            # Initialize the result container
            result = []
            
            # IMPORTANT: Validate input before processing
            if not data:
                return result
            
            for item in data:  # Iterate through each item
                # Skip invalid items
                if not item.get('valid'):
                    continue
                    
                # Transform the item
                # This is a multi-line
                # comment explaining the logic
                transformed = item['value'] * 2
                
                result.append(transformed)  # Add to results
                
            # Return processed results
            return result
    ''')


@pytest.fixture
def tech_debt_comments_code() -> str:
    """Python code with TODO, FIXME, and HACK comments."""
    return textwrap.dedent('''
        def legacy_function():
            """A function with technical debt markers."""
            
            # TODO: Refactor this to use the new API
            old_api_call()
            
            # FIXME: This doesn't handle unicode properly
            result = process_string(data)
            
            # HACK: Temporary workaround for #1234
            # This should be removed once the upstream bug is fixed
            if result is None:
                result = fallback_value
            
            # TODO(john): Add proper error handling
            # Priority: HIGH
            return result
            
            # XXX: This code path is never reached
            unreachable_code()
            
            # NOTE: Performance bottleneck identified here
            slow_operation()
            
            # WARNING: Don't modify without understanding the implications
            critical_section()
    ''')


@pytest.fixture
def temp_python_files(tmp_path: Path) -> Dict[str, Path]:
    """Create temporary Python files with various comments."""
    files = {}
    
    # File with mixed docstrings
    mixed_file = tmp_path / "mixed_style.py"
    mixed_file.write_text(textwrap.dedent('''
        """Module with mixed documentation styles."""
        
        def func_google(x):
            """Google style.
            
            Args:
                x: Input value
            """
            pass
        
        def func_numpy(x):
            """NumPy style.
            
            Parameters
            ----------
            x : int
                Input value
            """
            pass
    '''))
    files['mixed'] = mixed_file
    
    return files


# =============================================================================
# TEST CLASSES: DOCSTRING EXTRACTION
# =============================================================================


class TestDocstringExtraction:
    """Tests for docstring extraction functionality."""

    def test_extract_google_style_docstring(
        self, google_style_docstring_code: str
    ) -> None:
        """Test extraction of Google-style docstrings."""
        from src.core.intelligence.comment_analyzer import CommentAnalyzer
        
        analyzer = CommentAnalyzer()
        result = analyzer.analyze_string(google_style_docstring_code)
        
        assert len(result.docstrings) >= 1
        docstring = result.docstrings[0]
        assert docstring.style == "google"
        assert "calculate_total" in docstring.function_name

    def test_parse_google_args_section(
        self, google_style_docstring_code: str
    ) -> None:
        """Test parsing of Args section in Google-style docstring."""
        from src.core.intelligence.comment_analyzer import CommentAnalyzer
        
        analyzer = CommentAnalyzer()
        result = analyzer.analyze_string(google_style_docstring_code)
        
        docstring = result.docstrings[0]
        assert "items" in [arg.name for arg in docstring.args]
        assert "tax_rate" in [arg.name for arg in docstring.args]

    def test_parse_google_returns_section(
        self, google_style_docstring_code: str
    ) -> None:
        """Test parsing of Returns section in Google-style docstring."""
        from src.core.intelligence.comment_analyzer import CommentAnalyzer
        
        analyzer = CommentAnalyzer()
        result = analyzer.analyze_string(google_style_docstring_code)
        
        docstring = result.docstrings[0]
        assert docstring.returns is not None
        assert "total price" in docstring.returns.lower()

    def test_parse_google_raises_section(
        self, google_style_docstring_code: str
    ) -> None:
        """Test parsing of Raises section in Google-style docstring."""
        from src.core.intelligence.comment_analyzer import CommentAnalyzer
        
        analyzer = CommentAnalyzer()
        result = analyzer.analyze_string(google_style_docstring_code)
        
        docstring = result.docstrings[0]
        assert len(docstring.raises) >= 2
        exception_names = [r.exception for r in docstring.raises]
        assert "ValueError" in exception_names
        assert "TypeError" in exception_names

    def test_extract_numpy_style_docstring(
        self, numpy_style_docstring_code: str
    ) -> None:
        """Test extraction of NumPy-style docstrings."""
        from src.core.intelligence.comment_analyzer import CommentAnalyzer
        
        analyzer = CommentAnalyzer()
        result = analyzer.analyze_string(numpy_style_docstring_code)
        
        assert len(result.docstrings) >= 1
        docstring = result.docstrings[0]
        assert docstring.style == "numpy"

    def test_extract_sphinx_style_docstring(
        self, sphinx_style_docstring_code: str
    ) -> None:
        """Test extraction of Sphinx-style docstrings."""
        from src.core.intelligence.comment_analyzer import CommentAnalyzer
        
        analyzer = CommentAnalyzer()
        result = analyzer.analyze_string(sphinx_style_docstring_code)
        
        assert len(result.docstrings) >= 1
        docstring = result.docstrings[0]
        assert docstring.style == "sphinx"


# =============================================================================
# TEST CLASSES: INLINE COMMENT ANALYSIS
# =============================================================================


class TestInlineCommentAnalysis:
    """Tests for inline comment analysis."""

    def test_extract_inline_comments(
        self, inline_comments_code: str
    ) -> None:
        """Test extraction of inline comments."""
        from src.core.intelligence.comment_analyzer import CommentAnalyzer
        
        analyzer = CommentAnalyzer()
        result = analyzer.analyze_string(inline_comments_code)
        
        assert len(result.inline_comments) >= 5

    def test_classify_comment_types(
        self, inline_comments_code: str
    ) -> None:
        """Test classification of comment types."""
        from src.core.intelligence.comment_analyzer import CommentAnalyzer
        
        analyzer = CommentAnalyzer()
        result = analyzer.analyze_string(inline_comments_code)
        
        # Should identify IMPORTANT comment
        important_comments = [
            c for c in result.inline_comments 
            if c.category == "IMPORTANT"
        ]
        assert len(important_comments) >= 1

    def test_link_comments_to_code(
        self, inline_comments_code: str
    ) -> None:
        """Test linking comments to related code."""
        from src.core.intelligence.comment_analyzer import CommentAnalyzer
        
        analyzer = CommentAnalyzer()
        result = analyzer.analyze_string(inline_comments_code)
        
        # Each comment should have a line number
        for comment in result.inline_comments:
            assert comment.line_number > 0


# =============================================================================
# TEST CLASSES: TECH DEBT TRACKING
# =============================================================================


class TestTechDebtTracking:
    """Tests for TODO/FIXME/HACK detection."""

    def test_detect_todo_comments(
        self, tech_debt_comments_code: str
    ) -> None:
        """Test detection of TODO comments."""
        from src.core.intelligence.comment_analyzer import CommentAnalyzer
        
        analyzer = CommentAnalyzer()
        result = analyzer.analyze_string(tech_debt_comments_code)
        
        todos = [d for d in result.tech_debt if d.marker == "TODO"]
        assert len(todos) >= 2

    def test_detect_fixme_comments(
        self, tech_debt_comments_code: str
    ) -> None:
        """Test detection of FIXME comments."""
        from src.core.intelligence.comment_analyzer import CommentAnalyzer
        
        analyzer = CommentAnalyzer()
        result = analyzer.analyze_string(tech_debt_comments_code)
        
        fixmes = [d for d in result.tech_debt if d.marker == "FIXME"]
        assert len(fixmes) >= 1

    def test_detect_hack_comments(
        self, tech_debt_comments_code: str
    ) -> None:
        """Test detection of HACK comments."""
        from src.core.intelligence.comment_analyzer import CommentAnalyzer
        
        analyzer = CommentAnalyzer()
        result = analyzer.analyze_string(tech_debt_comments_code)
        
        hacks = [d for d in result.tech_debt if d.marker == "HACK"]
        assert len(hacks) >= 1

    def test_extract_todo_assignee(
        self, tech_debt_comments_code: str
    ) -> None:
        """Test extraction of TODO assignee."""
        from src.core.intelligence.comment_analyzer import CommentAnalyzer
        
        analyzer = CommentAnalyzer()
        result = analyzer.analyze_string(tech_debt_comments_code)
        
        # Should find TODO(john)
        assigned_todos = [
            d for d in result.tech_debt 
            if d.assignee is not None
        ]
        assert len(assigned_todos) >= 1
        assert "john" in [t.assignee.lower() for t in assigned_todos]

    def test_detect_warning_comments(
        self, tech_debt_comments_code: str
    ) -> None:
        """Test detection of WARNING comments."""
        from src.core.intelligence.comment_analyzer import CommentAnalyzer
        
        analyzer = CommentAnalyzer()
        result = analyzer.analyze_string(tech_debt_comments_code)
        
        warnings = [d for d in result.tech_debt if d.marker == "WARNING"]
        assert len(warnings) >= 1


# =============================================================================
# TEST CLASSES: SEMANTIC INDEXING
# =============================================================================


class TestSemanticIndexing:
    """Tests for semantic indexing of comments."""

    def test_build_comment_index(
        self, google_style_docstring_code: str
    ) -> None:
        """Test building searchable comment index."""
        from src.core.intelligence.comment_analyzer import CommentAnalyzer
        
        analyzer = CommentAnalyzer()
        result = analyzer.analyze_string(google_style_docstring_code)
        
        index = result.build_index()
        
        assert index is not None
        # Should be able to search for concepts
        matches = index.search("tax")
        assert len(matches) >= 1

    def test_search_by_keyword(
        self, google_style_docstring_code: str
    ) -> None:
        """Test searching comments by keyword."""
        from src.core.intelligence.comment_analyzer import CommentAnalyzer
        
        analyzer = CommentAnalyzer()
        result = analyzer.analyze_string(google_style_docstring_code)
        
        index = result.build_index()
        matches = index.search("price")
        
        assert len(matches) >= 1


# =============================================================================
# TEST CLASSES: COMMENT QUALITY
# =============================================================================


class TestCommentQuality:
    """Tests for comment quality analysis."""

    def test_detect_outdated_comments(
        self, temp_python_files: Dict[str, Path]
    ) -> None:
        """Test detection of potentially outdated comments."""
        from src.core.intelligence.comment_analyzer import CommentAnalyzer
        
        # Create file with comment-code mismatch
        test_code = textwrap.dedent('''
            def add_numbers(x, y):
                """Subtract two numbers."""  # Outdated docstring
                return x + y
        ''')
        
        analyzer = CommentAnalyzer()
        result = analyzer.analyze_string(test_code)
        
        # Should flag potential mismatch
        assert any(
            issue.type == "POTENTIAL_MISMATCH"
            for issue in result.quality_issues
        )


# =============================================================================
# TEST CLASSES: INTEGRATION
# =============================================================================


class TestCommentAnalyzerIntegration:
    """Integration tests for comment analyzer."""

    def test_full_analysis_pipeline(
        self, google_style_docstring_code: str
    ) -> None:
        """Test complete comment analysis pipeline."""
        from src.core.intelligence.comment_analyzer import CommentAnalyzer
        
        analyzer = CommentAnalyzer()
        result = analyzer.analyze_string(google_style_docstring_code)
        
        assert result is not None
        assert len(result.docstrings) >= 1
        
        # Build index
        index = result.build_index()
        assert index is not None

    def test_analyze_file(
        self, temp_python_files: Dict[str, Path]
    ) -> None:
        """Test analyzing a Python file."""
        from src.core.intelligence.comment_analyzer import CommentAnalyzer
        
        analyzer = CommentAnalyzer()
        result = analyzer.analyze_file(temp_python_files['mixed'])
        
        assert result is not None
        assert len(result.docstrings) >= 2

    def test_serialization_to_dict(
        self, google_style_docstring_code: str
    ) -> None:
        """Test serialization of analysis results."""
        from src.core.intelligence.comment_analyzer import CommentAnalyzer
        
        analyzer = CommentAnalyzer()
        result = analyzer.analyze_string(google_style_docstring_code)
        
        serialized = result.to_dict()
        
        assert isinstance(serialized, dict)
        assert "docstrings" in serialized
        assert "inline_comments" in serialized
        assert "tech_debt" in serialized
