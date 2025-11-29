"""
Test suite for CSharpAnalyzer class.

TDD approach for C# code analysis using regex patterns.
"""

import pytest
from pathlib import Path


class TestCSharpAnalyzerInitialization:
    """Test CSharpAnalyzer initialization."""
    
    def test_analyzer_exists(self):
        """Test that CSharpAnalyzer class can be imported and instantiated."""
        from src.crawlers.analyzers.csharp_analyzer import CSharpAnalyzer
        
        analyzer = CSharpAnalyzer()
        assert analyzer is not None


class TestCSharpAnalyzerBasicAnalysis:
    """Test basic C# file analysis."""
    
    def test_analyze_returns_dict(self, tmp_path):
        """Test that analyze() returns a dictionary with metrics."""
        from src.crawlers.analyzers.csharp_analyzer import CSharpAnalyzer
        
        code = """
namespace MyApp
{
    class Program
    {
        static void Main(string[] args)
        {
        }
    }
}
"""
        test_file = tmp_path / "Program.cs"
        test_file.write_text(code)
        
        analyzer = CSharpAnalyzer()
        result = analyzer.analyze(str(test_file))
        
        assert isinstance(result, dict)
        assert result['language'] == 'csharp'


class TestCSharpAnalyzerClassDetection:
    """Test class detection in C# files."""
    
    def test_detect_classes(self, tmp_path):
        """Test that analyzer detects class definitions."""
        from src.crawlers.analyzers.csharp_analyzer import CSharpAnalyzer
        
        code = """
public class Customer
{
    public string Name { get; set; }
}

internal class Order
{
}
"""
        test_file = tmp_path / "Models.cs"
        test_file.write_text(code)
        
        analyzer = CSharpAnalyzer()
        result = analyzer.analyze(str(test_file))
        
        assert 'classes' in result
        assert len(result['classes']) == 2
        assert 'Customer' in result['classes']
        assert 'Order' in result['classes']
