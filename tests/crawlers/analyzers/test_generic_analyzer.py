"""
Tests for Generic Analyzer

Author: CORTEX Application Health Dashboard
"""

import pytest
from src.crawlers.analyzers.generic_analyzer import GenericAnalyzer, GenericAnalysisResult


class TestGenericAnalyzerBasics:
    """Test basic generic analyzer functionality"""
    
    def test_analyzer_initialization(self):
        """Test generic analyzer can be created"""
        analyzer = GenericAnalyzer()
        assert analyzer is not None
    
    def test_can_analyze_any_file(self):
        """Test analyzer accepts any file (fallback)"""
        analyzer = GenericAnalyzer()
        assert analyzer.can_analyze("test.py") is True
        assert analyzer.can_analyze("test.xyz") is True
        assert analyzer.can_analyze("unknown.file") is True


class TestGenericAnalyzerLanguageDetection:
    """Test language detection from file extensions"""
    
    def test_detect_python(self):
        """Test Python file detection"""
        analyzer = GenericAnalyzer()
        result = analyzer.analyze("test.py", "print('hello')")
        assert result.language == "python"
    
    def test_detect_javascript(self):
        """Test JavaScript file detection"""
        analyzer = GenericAnalyzer()
        result = analyzer.analyze("app.js", "console.log('hello');")
        assert result.language == "javascript"
    
    def test_detect_unknown(self):
        """Test unknown file extension"""
        analyzer = GenericAnalyzer()
        result = analyzer.analyze("file.xyz", "content")
        assert result.language == "unknown"


class TestGenericAnalyzerLineCountingPython:
    """Test line counting for Python-style comments"""
    
    def test_count_source_lines(self):
        """Test source line counting"""
        analyzer = GenericAnalyzer()
        code = '''
def hello():
    print("hello")
    return True
'''
        result = analyzer.analyze("test.py", code)
        assert result.source_lines == 3  # def, print, return
    
    def test_count_comment_lines(self):
        """Test comment line counting (Python #)"""
        analyzer = GenericAnalyzer()
        code = '''
# This is a comment
def hello():
    # Another comment
    print("hello")
'''
        result = analyzer.analyze("test.py", code)
        assert result.comment_lines == 2
    
    def test_count_blank_lines(self):
        """Test blank line counting"""
        analyzer = GenericAnalyzer()
        code = '''
def hello():

    print("hello")

'''
        result = analyzer.analyze("test.py", code)
        assert result.blank_lines >= 2


class TestGenericAnalyzerLineCountingJavaScript:
    """Test line counting for JavaScript-style comments"""
    
    def test_slash_slash_comments(self):
        """Test // comment detection"""
        analyzer = GenericAnalyzer()
        code = '''
// This is a comment
function hello() {
    // Another comment
    console.log("hello");
}
'''
        result = analyzer.analyze("test.js", code)
        assert result.comment_lines == 2
    
    def test_multiline_comments(self):
        """Test /* ... */ comment detection"""
        analyzer = GenericAnalyzer()
        code = '''
/*
 * Multi-line comment
 * Block
 */
function hello() {
    return true;
}
'''
        result = analyzer.analyze("test.js", code)
        assert result.comment_lines >= 3


class TestGenericAnalyzerMetrics:
    """Test metric calculations"""
    
    def test_comment_ratio(self):
        """Test comment ratio calculation"""
        analyzer = GenericAnalyzer()
        code = '''
# Comment
code
# Comment
'''
        result = analyzer.analyze("test.py", code)
        assert result.raw_metrics['comment_ratio'] > 0
        assert result.raw_metrics['comment_ratio'] <= 1.0
    
    def test_code_density(self):
        """Test code density calculation"""
        analyzer = GenericAnalyzer()
        code = '''
# Comment

code_line
'''
        result = analyzer.analyze("test.py", code)
        assert result.raw_metrics['code_density'] > 0
        assert result.raw_metrics['code_density'] <= 1.0
    
    def test_file_size_calculation(self):
        """Test file size calculation"""
        analyzer = GenericAnalyzer()
        code = "a" * 1024  # 1KB
        result = analyzer.analyze("test.txt", code)
        assert result.file_size_bytes == 1024
        assert result.raw_metrics['file_size_kb'] == 1.0
    
    def test_total_lines_accuracy(self):
        """Test total line count matches input"""
        analyzer = GenericAnalyzer()
        code = "line1\nline2\nline3\nline4"
        result = analyzer.analyze("test.txt", code)
        assert result.lines_of_code == 4
