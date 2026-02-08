"""
Tests for Data Collectors (Phase 23.2)
Verify comprehensive data collection for all 13 dashboard tabs.

SKIPPED: company.dashboards.core module not present (migrated to spa/)
"""

import pytest
pytestmark = pytest.mark.skip(reason="company.dashboards.core migrated to spa/ structure")

from pathlib import Path
try:
    from company.dashboards.core.data_collectors import (
        OverviewCollector,
        ArchitectureCollector,
        QualityCollector,
        VulnerabilitiesCollector,
        SecurityCollector,
        DependenciesCollector,
        TestingCollector,
        PatternsCollector,
        ComprehensiveDataCollector
    )
except ImportError:
    pass  # Skipped anyway


class TestOverviewCollector:
    """Test overview metrics collection."""
    
    def test_collect_returns_valid_structure(self, tmp_path):
        """Overview collector returns required fields."""
        # Create test repository
        (tmp_path / "main.py").write_text("def main(): pass\n" * 10)
        (tmp_path / "test_main.py").write_text("def test_main(): pass\n" * 5)
        
        collector = OverviewCollector()
        data = collector.collect(tmp_path)
        
        # Verify structure
        assert "health_score" in data
        assert "file_count" in data
        assert "loc_total" in data
        assert "test_coverage" in data
        assert data["file_count"] == 2
        assert data["health_score"] > 0


class TestArchitectureCollector:
    """Test architecture data collection."""
    
    def test_build_structure_tree(self, tmp_path):
        """Architecture collector builds directory tree."""
        # Create structure
        (tmp_path / "api").mkdir()
        (tmp_path / "api" / "views.py").write_text("# API views")
        (tmp_path / "models").mkdir()
        (tmp_path / "models" / "user.py").write_text("# User model")
        
        collector = ArchitectureCollector()
        data = collector.collect(tmp_path)
        
        assert "structure_tree" in data
        assert len(data["structure_tree"]) == 2  # api/ and models/
        assert "module_stats" in data
        assert "layers" in data


class TestQualityCollector:
    """Test quality metrics collection."""
    
    def test_calculate_complexity(self, tmp_path):
        """Quality collector calculates complexity metrics."""
        # Create complex file
        code = """
def complex_function():
    if condition1:
        if condition2:
            for item in items:
                while True:
                    pass
"""
        (tmp_path / "complex.py").write_text(code)
        
        collector = QualityCollector()
        data = collector.collect(tmp_path)
        
        assert "complexity_metrics" in data
        assert "code_smells" in data
        assert "duplication_ratio" in data
        assert data["complexity_metrics"]["average"] > 0


class TestSecurityCollector:
    """Test security data collection."""
    
    def test_detect_secrets(self, tmp_path):
        """Security collector detects potential secrets."""
        # Create file with secret patterns
        (tmp_path / "config.py").write_text("api_key = 'secret123'\npassword = 'test'")
        
        collector = SecurityCollector()
        data = collector.collect(tmp_path)
        
        assert "secrets_detected" in data
        assert "security_score" in data
        assert len(data["secrets_detected"]) > 0


class TestDependenciesCollector:
    """Test dependency analysis."""
    
    def test_parse_requirements(self, tmp_path):
        """Dependencies collector parses requirements.txt."""
        # Create requirements.txt
        (tmp_path / "requirements.txt").write_text(
            "pytest==7.4.3\nrequests==2.31.0\npydantic>=2.0.0"
        )
        
        collector = DependenciesCollector()
        data = collector.collect(tmp_path)
        
        assert "packages" in data
        assert len(data["packages"]) >= 2
        assert any(pkg["name"] == "pytest" for pkg in data["packages"])


class TestTestingCollector:
    """Test testing metrics collection."""
    
    def test_analyze_test_pyramid(self, tmp_path):
        """Testing collector analyzes test pyramid."""
        # Create test files
        (tmp_path / "tests").mkdir()
        (tmp_path / "tests" / "unit").mkdir()
        (tmp_path / "tests" / "unit" / "test_foo.py").write_text("def test_foo(): pass")
        (tmp_path / "tests" / "integration").mkdir()
        (tmp_path / "tests" / "integration" / "test_bar.py").write_text("def test_bar(): pass")
        
        collector = TestingCollector()
        data = collector.collect(tmp_path)
        
        assert "test_pyramid" in data
        assert "coverage" in data
        assert data["test_pyramid"]["unit"] > 0


class TestPatternsCollector:
    """Test design pattern detection."""
    
    def test_detect_design_patterns(self, tmp_path):
        """Patterns collector detects design patterns."""
        # Create singleton pattern
        code = """
class Singleton:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
"""
        (tmp_path / "singleton.py").write_text(code)
        
        collector = PatternsCollector()
        data = collector.collect(tmp_path)
        
        assert "design_patterns" in data
        assert len(data["design_patterns"]) > 0


class TestComprehensiveDataCollector:
    """Test comprehensive data collection orchestration."""
    
    def test_collect_all_sections(self, tmp_path):
        """Comprehensive collector gathers data from all collectors."""
        # Create minimal repository
        (tmp_path / "main.py").write_text("def main(): pass")
        (tmp_path / "requirements.txt").write_text("pytest==7.4.3")
        
        collector = ComprehensiveDataCollector()
        data = collector.collect_all(tmp_path)
        
        # Verify all 13 sections present
        expected_sections = [
            "overview", "architecture", "quality", "vulnerabilities",
            "security", "dependencies", "testing", "patterns",
            "vendors", "usecases", "timeline", "impact", "database"
        ]
        
        for section in expected_sections:
            assert section in data, f"Missing section: {section}"
    
    def test_graceful_degradation_on_error(self, tmp_path):
        """Comprehensive collector handles collection errors gracefully."""
        # Use non-existent path to trigger errors
        collector = ComprehensiveDataCollector()
        data = collector.collect_all(Path("/nonexistent"))
        
        # Should still return data structure (possibly with errors)
        assert isinstance(data, dict)
        assert len(data) > 0
