"""
Test suite for JavaScriptAnalyzer class.
"""

import pytest


class TestJavaScriptAnalyzerInitialization:
    """Test JavaScriptAnalyzer initialization."""
    
    def test_analyzer_exists(self):
        """Test that JavaScriptAnalyzer class can be imported."""
        from src.crawlers.analyzers.javascript_analyzer import JavaScriptAnalyzer
        
        analyzer = JavaScriptAnalyzer()
        assert analyzer is not None


class TestJavaScriptAnalyzerFunctionDetection:
    """Test function detection."""
    
    def test_detect_functions(self, tmp_path):
        """Test that analyzer detects function definitions."""
        from src.crawlers.analyzers.javascript_analyzer import JavaScriptAnalyzer
        
        code = """
function hello() {
    console.log('hello');
}

const goodbye = () => {
    console.log('bye');
};
"""
        test_file = tmp_path / "app.js"
        test_file.write_text(code)
        
        analyzer = JavaScriptAnalyzer()
        result = analyzer.analyze(str(test_file))
        
        assert result['language'] == 'javascript'
        assert 'hello' in result['functions']
        assert 'goodbye' in result['functions']


class TestTypeScriptAnalyzer:
    """Test TypeScript file analysis."""
    
    def test_typescript_detection(self, tmp_path):
        """Test that .ts files are detected as TypeScript."""
        from src.crawlers.analyzers.javascript_analyzer import JavaScriptAnalyzer
        
        code = """
class Person {
    name: string;
    constructor(name: string) {
        this.name = name;
    }
}
"""
        test_file = tmp_path / "person.ts"
        test_file.write_text(code)
        
        analyzer = JavaScriptAnalyzer()
        result = analyzer.analyze(str(test_file))
        
        assert result['language'] == 'typescript'
        assert 'Person' in result['classes']
