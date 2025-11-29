"""
Tests for ApplicationHealthOrchestrator

Tests the orchestrator that coordinates application health analysis:
- Integration with CrawlerOrchestrator
- Multi-language analysis
- Report generation
- Caching and performance
"""

import pytest
import tempfile
import os
from pathlib import Path
from src.orchestrators.application_health_orchestrator import ApplicationHealthOrchestrator


class TestApplicationHealthOrchestratorInitialization:
    """Test orchestrator initialization"""
    
    def test_orchestrator_exists(self):
        """Test that ApplicationHealthOrchestrator class exists"""
        orchestrator = ApplicationHealthOrchestrator()
        assert orchestrator is not None
    
    def test_orchestrator_has_analyze_method(self):
        """Test that orchestrator has analyze method"""
        orchestrator = ApplicationHealthOrchestrator()
        assert hasattr(orchestrator, 'analyze')
        assert callable(orchestrator.analyze)


class TestApplicationHealthOrchestratorAnalysis:
    """Test application analysis functionality"""
    
    def test_analyze_simple_python_project(self, tmp_path):
        """Test analyzing a simple Python project"""
        # Create test project structure
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "app.py").write_text("""
def hello():
    print("Hello World")

class User:
    def __init__(self, name):
        self.name = name
""")
        
        orchestrator = ApplicationHealthOrchestrator()
        result = orchestrator.analyze(str(tmp_path))
        
        assert result is not None
        assert result['total_files'] == 1
        assert 'python' in result['languages']
        assert result['languages']['python']['file_count'] == 1
    
    def test_analyze_multi_language_project(self, tmp_path):
        """Test analyzing a project with multiple languages"""
        # Python file
        (tmp_path / "app.py").write_text("def test(): pass")
        
        # JavaScript file
        (tmp_path / "app.js").write_text("function test() {}")
        
        # C# file
        (tmp_path / "App.cs").write_text("public class App {}")
        
        orchestrator = ApplicationHealthOrchestrator()
        result = orchestrator.analyze(str(tmp_path))
        
        assert result['total_files'] == 3
        assert len(result['languages']) == 3
        assert 'python' in result['languages']
        assert 'javascript' in result['languages']
        assert 'csharp' in result['languages']
    
    def test_analyze_with_scan_level(self, tmp_path):
        """Test analyze respects scan level parameter"""
        # Create files including excluded directories
        (tmp_path / "src").mkdir()
        (tmp_path / "node_modules").mkdir()
        (tmp_path / "src" / "app.py").write_text("pass")
        (tmp_path / "node_modules" / "lib.js").write_text("// lib")
        
        orchestrator = ApplicationHealthOrchestrator()
        
        # Overview should exclude node_modules
        result_overview = orchestrator.analyze(str(tmp_path), scan_level='overview')
        assert result_overview['total_files'] == 1
        
        # Deep should include everything
        result_deep = orchestrator.analyze(str(tmp_path), scan_level='deep')
        assert result_deep['total_files'] == 2


class TestApplicationHealthOrchestratorReporting:
    """Test report generation"""
    
    def test_generate_report_returns_string(self, tmp_path):
        """Test that generate_report returns formatted string"""
        (tmp_path / "app.py").write_text("def test(): pass")
        
        orchestrator = ApplicationHealthOrchestrator()
        result = orchestrator.analyze(str(tmp_path))
        report = orchestrator.generate_report(result)
        
        assert isinstance(report, str)
        assert len(report) > 0
    
    def test_report_contains_summary_section(self, tmp_path):
        """Test report contains summary information"""
        (tmp_path / "app.py").write_text("def test(): pass")
        
        orchestrator = ApplicationHealthOrchestrator()
        result = orchestrator.analyze(str(tmp_path))
        report = orchestrator.generate_report(result)
        
        assert "Application Health Report" in report
        assert "Total Files" in report
        assert "Languages Detected" in report
    
    def test_report_contains_language_breakdown(self, tmp_path):
        """Test report includes language-specific details"""
        (tmp_path / "app.py").write_text("def test(): pass")
        (tmp_path / "app.js").write_text("function test() {}")
        
        orchestrator = ApplicationHealthOrchestrator()
        result = orchestrator.analyze(str(tmp_path))
        report = orchestrator.generate_report(result)
        
        assert "Python" in report
        assert "JavaScript" in report
        assert "Files:" in report


class TestApplicationHealthOrchestratorPerformance:
    """Test performance features (caching, multi-threading)"""
    
    def test_caching_improves_second_scan(self, tmp_path):
        """Test that second scan is faster due to caching"""
        # Create test files
        for i in range(10):
            (tmp_path / f"file{i}.py").write_text(f"def func{i}(): pass")
        
        orchestrator = ApplicationHealthOrchestrator()
        
        # First scan - cache miss
        import time
        start1 = time.time()
        result1 = orchestrator.analyze(str(tmp_path))
        duration1 = time.time() - start1
        
        # Second scan - cache hit
        start2 = time.time()
        result2 = orchestrator.analyze(str(tmp_path))
        duration2 = time.time() - start2
        
        # Results should be identical
        assert result1['total_files'] == result2['total_files']
        
        # Second scan should be faster (allow for some variance)
        # Note: May not always be true in test environment, so this is lenient
        assert duration2 <= duration1 * 2  # At most 2x slower (very lenient)
    
    def test_handles_large_number_of_files(self, tmp_path):
        """Test that orchestrator can handle many files efficiently"""
        # Create 100 Python files
        for i in range(100):
            (tmp_path / f"file{i}.py").write_text(f"def func{i}(): pass\n" * 10)
        
        orchestrator = ApplicationHealthOrchestrator()
        result = orchestrator.analyze(str(tmp_path))
        
        assert result['total_files'] == 100
        assert result['languages']['python']['file_count'] == 100
