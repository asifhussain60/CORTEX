"""
RED Phase Tests for Tool Recommendation Engine
Test-first development for language-specific tool recommendations

Coverage: IDE extensions, linters, debuggers, formatters, testing tools
Languages: Python, JavaScript/TypeScript, C#, Ruby, Go, Rust, PHP, Java, Swift, ColdFusion
"""

import pytest
from pathlib import Path


class TestToolRecommenderInitialization:
    """Test recommender initialization."""
    
    def test_creates_recommender_for_workspace(self):
        """Should create recommender with workspace path."""
        from src.intelligence.tool_recommender import ToolRecommender
        
        recommender = ToolRecommender(r"c:\test\workspace")
        assert recommender is not None
        assert recommender.workspace_path == Path(r"c:\test\workspace")
    
    def test_recommends_tools_for_detected_languages(self):
        """Should recommend tools based on detected languages."""
        from src.intelligence.tool_recommender import ToolRecommender
        
        recommender = ToolRecommender(r"c:\test\workspace")
        recommendations = recommender.recommend(["python", "javascript"])
        
        assert isinstance(recommendations, dict)
        assert "python" in recommendations
        assert "javascript" in recommendations


class TestPythonToolRecommendations:
    """Test Python-specific tool recommendations."""
    
    def test_recommends_python_linters(self):
        """Should recommend pylint, flake8, mypy for Python."""
        from src.intelligence.tool_recommender import ToolRecommender
        
        recommender = ToolRecommender(r"c:\test\workspace")
        recommendations = recommender.recommend(["python"])
        
        python_tools = recommendations["python"]
        linters = [t["name"] for t in python_tools if t["category"] == "linter"]
        assert "pylint" in linters or "flake8" in linters
        assert "mypy" in linters  # Type checker
    
    def test_recommends_python_formatters(self):
        """Should recommend black, autopep8 for Python."""
        from src.intelligence.tool_recommender import ToolRecommender
        
        recommender = ToolRecommender(r"c:\test\workspace")
        recommendations = recommender.recommend(["python"])
        
        python_tools = recommendations["python"]
        formatters = [t["name"] for t in python_tools if t["category"] == "formatter"]
        assert "black" in formatters or "autopep8" in formatters
    
    def test_recommends_python_test_frameworks(self):
        """Should recommend pytest, unittest for Python."""
        from src.intelligence.tool_recommender import ToolRecommender
        
        recommender = ToolRecommender(r"c:\test\workspace")
        recommendations = recommender.recommend(["python"])
        
        python_tools = recommendations["python"]
        test_tools = [t["name"] for t in python_tools if t["category"] == "testing"]
        assert "pytest" in test_tools or "unittest" in test_tools
    
    def test_recommends_python_ide_extensions(self):
        """Should recommend Python VS Code extensions."""
        from src.intelligence.tool_recommender import ToolRecommender
        
        recommender = ToolRecommender(r"c:\test\workspace")
        recommendations = recommender.recommend(["python"])
        
        python_tools = recommendations["python"]
        ide_tools = [t["name"] for t in python_tools if t["category"] == "ide"]
        assert any("Python" in name or "Pylance" in name for name in ide_tools)


class TestJavaScriptToolRecommendations:
    """Test JavaScript/TypeScript tool recommendations."""
    
    def test_recommends_javascript_linters(self):
        """Should recommend ESLint for JavaScript."""
        from src.intelligence.tool_recommender import ToolRecommender
        
        recommender = ToolRecommender(r"c:\test\workspace")
        recommendations = recommender.recommend(["javascript"])
        
        js_tools = recommendations["javascript"]
        linters = [t["name"] for t in js_tools if t["category"] == "linter"]
        assert "eslint" in linters
    
    def test_recommends_javascript_formatters(self):
        """Should recommend Prettier for JavaScript."""
        from src.intelligence.tool_recommender import ToolRecommender
        
        recommender = ToolRecommender(r"c:\test\workspace")
        recommendations = recommender.recommend(["javascript"])
        
        js_tools = recommendations["javascript"]
        formatters = [t["name"] for t in js_tools if t["category"] == "formatter"]
        assert "prettier" in formatters
    
    def test_recommends_typescript_type_checker(self):
        """Should recommend TypeScript compiler for TypeScript."""
        from src.intelligence.tool_recommender import ToolRecommender
        
        recommender = ToolRecommender(r"c:\test\workspace")
        recommendations = recommender.recommend(["typescript"])
        
        ts_tools = recommendations["typescript"]
        type_checkers = [t["name"] for t in ts_tools if t["category"] == "linter"]
        assert any("typescript" in name.lower() for name in type_checkers)


class TestCSharpToolRecommendations:
    """Test C# tool recommendations."""
    
    def test_recommends_csharp_ide_extensions(self):
        """Should recommend OmniSharp for C#."""
        from src.intelligence.tool_recommender import ToolRecommender
        
        recommender = ToolRecommender(r"c:\test\workspace")
        recommendations = recommender.recommend(["csharp"])
        
        csharp_tools = recommendations["csharp"]
        ide_tools = [t["name"] for t in csharp_tools if t["category"] == "ide"]
        assert any("omnisharp" in name.lower() or "roslyn" in name.lower() for name in ide_tools)
    
    def test_recommends_csharp_formatters(self):
        """Should recommend C# formatter."""
        from src.intelligence.tool_recommender import ToolRecommender
        
        recommender = ToolRecommender(r"c:\test\workspace")
        recommendations = recommender.recommend(["csharp"])
        
        csharp_tools = recommendations["csharp"]
        formatters = [t["name"] for t in csharp_tools if t["category"] == "formatter"]
        assert len(formatters) > 0


class TestMultiLanguageRecommendations:
    """Test recommendations for multiple languages."""
    
    def test_recommends_for_multiple_languages(self):
        """Should recommend tools for all detected languages."""
        from src.intelligence.tool_recommender import ToolRecommender
        
        recommender = ToolRecommender(r"c:\test\workspace")
        recommendations = recommender.recommend(["python", "javascript", "csharp"])
        
        assert "python" in recommendations
        assert "javascript" in recommendations
        assert "csharp" in recommendations
    
    def test_each_language_has_multiple_tools(self):
        """Should recommend multiple tools per language."""
        from src.intelligence.tool_recommender import ToolRecommender
        
        recommender = ToolRecommender(r"c:\test\workspace")
        recommendations = recommender.recommend(["python", "javascript"])
        
        assert len(recommendations["python"]) >= 3
        assert len(recommendations["javascript"]) >= 3


class TestToolRecommendationFormat:
    """Test recommendation data structure."""
    
    def test_tool_has_required_fields(self):
        """Should include name, category, description, install_command."""
        from src.intelligence.tool_recommender import ToolRecommender
        
        recommender = ToolRecommender(r"c:\test\workspace")
        recommendations = recommender.recommend(["python"])
        
        for tool in recommendations["python"]:
            assert "name" in tool
            assert "category" in tool
            assert "description" in tool
            assert "install_command" in tool
    
    def test_categorizes_tools_correctly(self):
        """Should categorize tools as linter, formatter, testing, ide, debugger."""
        from src.intelligence.tool_recommender import ToolRecommender
        
        recommender = ToolRecommender(r"c:\test\workspace")
        recommendations = recommender.recommend(["python"])
        
        categories = [t["category"] for t in recommendations["python"]]
        assert any(cat in categories for cat in ["linter", "formatter", "testing", "ide", "debugger"])
    
    def test_provides_install_commands(self):
        """Should provide correct install commands for each tool."""
        from src.intelligence.tool_recommender import ToolRecommender
        
        recommender = ToolRecommender(r"c:\test\workspace")
        recommendations = recommender.recommend(["python"])
        
        for tool in recommendations["python"]:
            assert tool["install_command"] is not None
            assert len(tool["install_command"]) > 0


class TestAdditionalLanguages:
    """Test recommendations for other supported languages."""
    
    def test_recommends_ruby_tools(self):
        """Should recommend tools for Ruby."""
        from src.intelligence.tool_recommender import ToolRecommender
        
        recommender = ToolRecommender(r"c:\test\workspace")
        recommendations = recommender.recommend(["ruby"])
        
        assert "ruby" in recommendations
        assert len(recommendations["ruby"]) > 0
    
    def test_recommends_go_tools(self):
        """Should recommend tools for Go."""
        from src.intelligence.tool_recommender import ToolRecommender
        
        recommender = ToolRecommender(r"c:\test\workspace")
        recommendations = recommender.recommend(["go"])
        
        assert "go" in recommendations
        assert len(recommendations["go"]) > 0
    
    def test_recommends_rust_tools(self):
        """Should recommend tools for Rust."""
        from src.intelligence.tool_recommender import ToolRecommender
        
        recommender = ToolRecommender(r"c:\test\workspace")
        recommendations = recommender.recommend(["rust"])
        
        assert "rust" in recommendations
        assert len(recommendations["rust"]) > 0
    
    def test_recommends_coldfusion_tools(self):
        """Should recommend tools for ColdFusion."""
        from src.intelligence.tool_recommender import ToolRecommender
        
        recommender = ToolRecommender(r"c:\test\workspace")
        recommendations = recommender.recommend(["coldfusion"])
        
        assert "coldfusion" in recommendations
        assert len(recommendations["coldfusion"]) > 0


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_handles_unknown_language(self):
        """Should return empty dict for unknown language."""
        from src.intelligence.tool_recommender import ToolRecommender
        
        recommender = ToolRecommender(r"c:\test\workspace")
        recommendations = recommender.recommend(["unknown_language"])
        
        assert isinstance(recommendations, dict)
        # Should either skip unknown or return empty list
        assert "unknown_language" not in recommendations or len(recommendations["unknown_language"]) == 0
    
    def test_handles_empty_language_list(self):
        """Should return empty dict for no languages."""
        from src.intelligence.tool_recommender import ToolRecommender
        
        recommender = ToolRecommender(r"c:\test\workspace")
        recommendations = recommender.recommend([])
        
        assert isinstance(recommendations, dict)
        assert len(recommendations) == 0
    
    def test_normalizes_language_names(self):
        """Should handle case variations in language names."""
        from src.intelligence.tool_recommender import ToolRecommender
        
        recommender = ToolRecommender(r"c:\test\workspace")
        recommendations = recommender.recommend(["Python", "JAVASCRIPT", "CSharp"])
        
        # Should normalize to lowercase
        assert len(recommendations) > 0
