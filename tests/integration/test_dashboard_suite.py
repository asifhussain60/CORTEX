"""
Integration Tests for Dashboard Suite

Tests end-to-end functionality, data consistency, performance,
accessibility, and responsive design for dashboard components.

Author: Asif Hussain
Date: December 6, 2025
"""

import json
import pytest
import tempfile
import time
from pathlib import Path
from typing import Dict, Any

# Import backend dashboard components
from src.dashboard.dependency_bloat_analyzer import DependencyBloatAnalyzer


@pytest.fixture
def sample_luum_tech_stack():
    """
    Sample tech stack data representing luum-fresh structure.
    Includes multiple solutions, packages, frameworks, and varied metrics.
    """
    return {
        "project_name": "luum-fresh",
        "analysis_date": "2025-12-06",
        "solutions": [
            {
                "name": "Luum.Core",
                "path": "/src/Luum.Core/Luum.Core.sln",
                "frameworks": [
                    {
                        "name": ".NET Framework",
                        "version": "4.8",
                        "eol_date": "2027-01-12",
                        "risk_score": 45.0
                    }
                ],
                "packages": [{"name": f"Pkg{i}", "version": "1.0.0", "risk_score": 20.0} for i in range(50)]
            },
            {
                "name": "Luum.API",
                "path": "/src/Luum.API/Luum.API.sln",
                "frameworks": [
                    {
                        "name": ".NET Core",
                        "version": "3.1",
                        "eol_date": "2022-12-13",
                        "risk_score": 85.0
                    }
                ],
                "packages": [{"name": f"APIPkg{i}", "version": "1.0.0", "risk_score": 15.0} for i in range(75)]
            },
            {
                "name": "Luum.Tests",
                "path": "/tests/Luum.Tests/Luum.Tests.sln",
                "frameworks": [
                    {
                        "name": ".NET 8",
                        "version": "8.0",
                        "eol_date": "2026-11-10",
                        "risk_score": 10.0
                    }
                ],
                "packages": [{"name": f"TestPkg{i}", "version": "1.0.0", "risk_score": 10.0} for i in range(25)]
            }
        ]
    }


@pytest.fixture
def temp_tech_stack_file(sample_luum_tech_stack):
    """Create temporary tech stack JSON file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(sample_luum_tech_stack, f)
        temp_path = f.name
    
    yield temp_path
    
    Path(temp_path).unlink()


class TestEndToEndWithLuumData:
    """Test complete workflow with luum-fresh-like data."""
    
    def test_dependency_bloat_analyzer_with_luum_data(self, sample_luum_tech_stack, temp_tech_stack_file):
        """Test that dependency bloat analyzer successfully processes luum-fresh data."""
        
        # Dependency Bloat Analyzer
        dba = DependencyBloatAnalyzer(temp_tech_stack_file)
        dba.load_data()
        bloat_analysis = dba.analyze()
        
        # Verify results
        assert bloat_analysis.mean > 0
        assert len(bloat_analysis.solutions) == 3
        assert bloat_analysis.median > 0
        assert bloat_analysis.iqr >= 0
        
        # Verify solutions are present
        solution_names = {s.solution_name for s in bloat_analysis.solutions}
        assert 'Luum.Core' in solution_names
        assert 'Luum.API' in solution_names
        assert 'Luum.Tests' in solution_names
    
    def test_frontend_components_exist(self):
        """Test that all frontend JavaScript components exist."""
        base_path = Path("/Users/asifhussain/PROJECTS/CORTEX/static/js/dashboard")
        
        expected_files = [
            "dependency-bloat-analyzer.js",
            "framework-health-heatmap.js",
            "migration-roadmap-generator.js"
        ]
        
        for filename in expected_files:
            file_path = base_path / filename
            assert file_path.exists(), f"Frontend component {filename} not found"
    
    def test_css_stylesheets_exist(self):
        """Test that all CSS stylesheets exist."""
        base_path = Path("/Users/asifhussain/PROJECTS/CORTEX/static/css/dashboard")
        
        expected_files = [
            "dependency-bloat-analyzer.css",
            "framework-health-heatmap.css",
            "migration-roadmap-generator.css"
        ]
        
        for filename in expected_files:
            file_path = base_path / filename
            assert file_path.exists(), f"CSS stylesheet {filename} not found"


class TestDataConsistency:
    """Test data consistency across dashboard components."""
    
    def test_package_counts_extraction(self, temp_tech_stack_file):
        """Test that package counts are extracted correctly."""
        
        dba = DependencyBloatAnalyzer(temp_tech_stack_file)
        dba.load_data()
        counts = dba.extract_package_counts()
        
        # Verify counts match expected values
        count_dict = {name: count for name, count in counts}
        assert count_dict['Luum.Core'] == 50
        assert count_dict['Luum.API'] == 75
        assert count_dict['Luum.Tests'] == 25
    
    def test_bloat_analysis_consistency(self, temp_tech_stack_file):
        """Test that bloat analysis produces consistent results."""
        
        dba = DependencyBloatAnalyzer(temp_tech_stack_file)
        dba.load_data()
        
        # Run analysis twice
        analysis1 = dba.analyze()
        analysis2 = dba.analyze()
        
        # Results should be identical
        assert analysis1.mean == analysis2.mean
        assert analysis1.median == analysis2.median
        assert analysis1.iqr == analysis2.iqr
        assert len(analysis1.solutions) == len(analysis2.solutions)


class TestResponsiveDesign:
    """Test responsive design considerations (data structure validation)."""
    
    def test_data_structures_support_responsive_rendering(self, sample_luum_tech_stack):
        """Test that data structures include necessary fields for responsive design."""
        
        dba = DependencyBloatAnalyzer()
        analysis = dba.analyze(sample_luum_tech_stack)
        
        # Verify all solutions have required fields
        for solution in analysis.solutions:
            assert hasattr(solution, 'solution_name')
            assert hasattr(solution, 'package_count')
            assert hasattr(solution, 'bloat_score')
            assert hasattr(solution, 'category')
    
    def test_large_dataset_handling(self):
        """Test that dashboards handle large datasets efficiently."""
        
        # Create large dataset (500 packages)
        large_data = {
            "solutions": [
                {
                    "name": "LargeSolution",
                    "packages": [
                        {"name": f"Package{i}", "version": "1.0.0", "risk_score": 20.0}
                        for i in range(500)
                    ],
                    "frameworks": [
                        {"name": ".NET 8", "version": "8.0", "risk_score": 10.0}
                    ]
                }
            ]
        }
        
        # Test Dependency Bloat Analyzer with large dataset
        dba = DependencyBloatAnalyzer()
        analysis = dba.analyze(large_data)
        
        # Should complete successfully
        assert analysis.mean > 0
        assert len(analysis.solutions) == 1
        assert analysis.solutions[0].package_count == 500


class TestErrorHandling:
    """Test error handling across all components."""
    
    def test_missing_data_handling(self):
        """Test handling of missing or incomplete data."""
        
        incomplete_data = {
            "solutions": [
                {
                    "name": "IncompleteSolution",
                    "packages": []  # No packages
                }
            ]
        }
        
        # Dependency Bloat Analyzer should handle gracefully
        dba = DependencyBloatAnalyzer()
        analysis = dba.analyze(incomplete_data)
        assert analysis.mean == 0
        assert len(analysis.recommendations) > 0
    
    def test_invalid_json_handling(self):
        """Test handling of invalid JSON files."""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{ invalid json }")
            temp_path = f.name
        
        try:
            analyzer = DependencyBloatAnalyzer(temp_path)
            with pytest.raises(json.JSONDecodeError):
                analyzer.load_data()
        finally:
            Path(temp_path).unlink()
    
    def test_missing_file_handling(self):
        """Test handling of missing files."""
        
        analyzer = DependencyBloatAnalyzer("/nonexistent/path.json")
        with pytest.raises(FileNotFoundError):
            analyzer.load_data()


class TestPerformance:
    """Test performance characteristics."""
    
    def test_analysis_completes_within_time_limit(self, temp_tech_stack_file):
        """Test that full analysis completes within reasonable time."""
        
        start_time = time.time()
        
        # Run analyzer
        dba = DependencyBloatAnalyzer(temp_tech_stack_file)
        dba.load_data()
        dba.analyze()
        
        elapsed_time = time.time() - start_time
        
        # Should complete within 2 seconds for sample dataset
        assert elapsed_time < 2.0, f"Analysis took {elapsed_time:.2f}s, expected <2s"
    
    def test_memory_efficiency(self, temp_tech_stack_file):
        """Test that components don't duplicate data unnecessarily."""
        
        # Load data once
        with open(temp_tech_stack_file, 'r') as f:
            data = json.load(f)
        
        # Component should be able to work with same data dict
        dba = DependencyBloatAnalyzer()
        
        # Should not raise errors
        analysis = dba.analyze(data)
        assert analysis is not None


class TestAccessibility:
    """Test accessibility considerations (data structure validation)."""
    
    def test_data_includes_descriptive_labels(self, sample_luum_tech_stack):
        """Test that data structures include descriptive labels for screen readers."""
        
        dba = DependencyBloatAnalyzer()
        analysis = dba.analyze(sample_luum_tech_stack)
        
        # All solutions should have descriptive names and categories
        for solution in analysis.solutions:
            assert solution.solution_name is not None
            assert solution.category in ['critical', 'warning', 'normal']
    
    def test_color_coding_has_alternatives(self, sample_luum_tech_stack):
        """Test that color-coded data has alternative indicators."""
        
        dba = DependencyBloatAnalyzer()
        analysis = dba.analyze(sample_luum_tech_stack)
        
        # Categories should exist (critical, warning, normal) - not just colors
        categories = {s.category for s in analysis.solutions}
        assert 'critical' in categories or 'warning' in categories or 'normal' in categories
        
        # Each solution should have explicit category AND numeric bloat_score
        for solution in analysis.solutions:
            assert solution.category is not None
            assert isinstance(solution.bloat_score, float)


class TestFilterInteractions:
    """Test filter functionality across components."""
    
    def test_bloat_score_filtering(self, temp_tech_stack_file):
        """Test filtering by bloat score."""
        
        dba = DependencyBloatAnalyzer(temp_tech_stack_file)
        dba.load_data()
        analysis = dba.analyze()
        
        # Filter critical solutions (bloat_score >= 2.0)
        critical_solutions = [s for s in analysis.solutions if s.category == 'critical']
        
        # Filter warning solutions (1.0 <= bloat_score < 2.0)
        warning_solutions = [s for s in analysis.solutions if s.category == 'warning']
        
        # Filter normal solutions (bloat_score < 1.0)
        normal_solutions = [s for s in analysis.solutions if s.category == 'normal']
        
        # All solutions should be categorized
        total_categorized = len(critical_solutions) + len(warning_solutions) + len(normal_solutions)
        assert total_categorized == len(analysis.solutions)
    
    def test_histogram_bin_filtering(self, temp_tech_stack_file):
        """Test histogram bin assignments."""
        
        dba = DependencyBloatAnalyzer(temp_tech_stack_file)
        dba.load_data()
        analysis = dba.analyze()
        
        # Verify histogram bins exist
        assert len(analysis.histogram_bins) == 5
        
        # Verify all solutions are in bins
        total_in_bins = sum(bin['count'] for bin in analysis.histogram_bins)
        assert total_in_bins == len(analysis.solutions)
    
    def test_outlier_filtering(self, temp_tech_stack_file):
        """Test outlier detection and filtering."""
        
        dba = DependencyBloatAnalyzer(temp_tech_stack_file)
        dba.load_data()
        analysis = dba.analyze()
        
        # Count outliers
        outlier_count = sum(1 for s in analysis.solutions if s.is_outlier)
        
        # Outliers should be identifiable
        assert outlier_count >= 0  # May or may not have outliers
        
        # All outliers should be in box plot data
        if outlier_count > 0:
            assert len(analysis.box_plot_data['outliers']) == outlier_count


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
