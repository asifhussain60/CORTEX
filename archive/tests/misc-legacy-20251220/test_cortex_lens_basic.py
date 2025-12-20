"""
CORTEX Lens Basic Tests

Tests for Phase 0 foundation components.
"""

import pytest
from pathlib import Path
import sys

# Add cortex_lens to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from cortex_lens import CortexLens, RepoTypeClassifier
from cortex_lens.analyzers import BaseAnalyzer
from cortex_lens.collectors import BaseCollector
from cortex_lens.analyzers.python_analyzer import PythonAnalyzer
from cortex_lens.collectors.health_collector import HealthCollector


class TestFoundation:
    """Test basic foundation components"""
    
    def test_imports(self):
        """Test that all modules can be imported"""
        assert CortexLens is not None
        assert RepoTypeClassifier is not None
        assert BaseAnalyzer is not None
        assert BaseCollector is not None
    
    def test_cortex_lens_initialization(self):
        """Test CortexLens can be initialized"""
        lens = CortexLens()
        assert lens is not None
        assert lens.version == "1.0.0"
    
    def test_classifier_initialization(self):
        """Test RepoTypeClassifier can be initialized"""
        classifier = RepoTypeClassifier()
        assert classifier is not None
        assert hasattr(classifier, 'classify')
    
    def test_python_analyzer_initialization(self):
        """Test PythonAnalyzer can be initialized"""
        analyzer = PythonAnalyzer()
        assert analyzer is not None
        assert '.py' in analyzer.SUPPORTED_EXTENSIONS
    
    def test_health_collector_initialization(self):
        """Test HealthCollector can be initialized"""
        collector = HealthCollector()
        assert collector is not None
        assert hasattr(collector, 'collect')


class TestPythonAnalyzer:
    """Test Python analyzer functionality"""
    
    def test_python_analyzer_parsers(self):
        """Test parser initialization"""
        analyzer = PythonAnalyzer()
        assert 'ast' in analyzer.parsers
        # parso and libcst may or may not be available
    
    def test_simple_code_analysis(self):
        """Test analysis of simple Python code"""
        analyzer = PythonAnalyzer()
        
        code = '''
def hello():
    return "world"

class MyClass:
    def method(self):
        pass
'''
        
        # Create temp file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_path = Path(f.name)
        
        try:
            result = analyzer.analyze(temp_path)
            
            assert result is not None
            assert 'functions' in result
            assert 'classes' in result
            assert len(result['functions']) >= 1
            assert len(result['classes']) >= 1
            assert result['parser_used'] in ['ast', 'parso', 'libcst']
        finally:
            temp_path.unlink()


class TestHealthCollector:
    """Test health collector functionality"""
    
    def test_health_collector_language_map(self):
        """Test language detection map"""
        collector = HealthCollector()
        assert '.py' in collector.LANGUAGE_MAP
        assert collector.LANGUAGE_MAP['.py'] == 'Python'
    
    def test_health_score_calculation(self):
        """Test health score calculation"""
        collector = HealthCollector()
        
        # Test ideal scenario
        score = collector._calculate_health_score(
            total_files=100,
            total_loc=10000,
            language_stats={'Python': {}},
            max_depth=4
        )
        
        assert 0 <= score <= 100
        assert score >= 80  # Should be good score


class TestClassifier:
    """Test repository classifier"""
    
    def test_classifier_thresholds(self):
        """Test classifier has defined thresholds"""
        classifier = RepoTypeClassifier()
        assert len(classifier.THRESHOLDS) == 6
        assert 'fullstack_web' in classifier.THRESHOLDS
        assert 'api_service' in classifier.THRESHOLDS


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
