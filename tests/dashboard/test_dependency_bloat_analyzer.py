"""
Tests for Dependency Bloat Analyzer

Author: Asif Hussain
Date: December 6, 2025
"""

import json
import pytest
import tempfile
from pathlib import Path
from src.dashboard.dependency_bloat_analyzer import (
    DependencyBloatAnalyzer,
    SolutionPackageStats,
    BloatAnalysis
)


@pytest.fixture
def sample_tech_stack():
    """Sample tech stack data with varied package counts."""
    return {
        "solutions": [
            {"name": "Solution1", "packages": ["pkg" + str(i) for i in range(50)]},   # 50 packages
            {"name": "Solution2", "packages": ["pkg" + str(i) for i in range(75)]},   # 75 packages
            {"name": "Solution3", "packages": ["pkg" + str(i) for i in range(100)]},  # 100 packages
            {"name": "Solution4", "packages": ["pkg" + str(i) for i in range(125)]},  # 125 packages
            {"name": "Solution5", "packages": ["pkg" + str(i) for i in range(150)]},  # 150 packages
            {"name": "Solution6", "packages": ["pkg" + str(i) for i in range(400)]},  # 400 packages (clear outlier)
        ]
    }


@pytest.fixture
def temp_tech_stack_file(sample_tech_stack):
    """Create temporary tech stack JSON file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(sample_tech_stack, f)
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    Path(temp_path).unlink()


class TestHistogramBinning:
    """Test histogram bin assignment."""
    
    def test_bin_assignment(self):
        """Test that solutions are assigned to correct bins."""
        analyzer = DependencyBloatAnalyzer()
        
        counts_with_names = [
            ("Solution1", 30),   # 0-50
            ("Solution2", 75),   # 51-100
            ("Solution3", 120),  # 101-150
            ("Solution4", 180),  # 151-200
            ("Solution5", 250),  # 200+
        ]
        
        bins = analyzer.create_histogram_bins(counts_with_names)
        
        assert len(bins) == 5
        assert bins[0]['label'] == '0-50'
        assert bins[0]['count'] == 1
        assert 'Solution1' in bins[0]['solutions']
        
        assert bins[1]['label'] == '51-100'
        assert bins[1]['count'] == 1
        assert 'Solution2' in bins[1]['solutions']
        
        assert bins[2]['label'] == '101-150'
        assert bins[2]['count'] == 1
        assert 'Solution3' in bins[2]['solutions']
        
        assert bins[3]['label'] == '151-200'
        assert bins[3]['count'] == 1
        assert 'Solution4' in bins[3]['solutions']
        
        assert bins[4]['label'] == '200+'
        assert bins[4]['count'] == 1
        assert 'Solution5' in bins[4]['solutions']
    
    def test_empty_bins(self):
        """Test bins with no solutions."""
        analyzer = DependencyBloatAnalyzer()
        
        counts_with_names = [
            ("Solution1", 30),   # 0-50
            ("Solution2", 250),  # 200+
        ]
        
        bins = analyzer.create_histogram_bins(counts_with_names)
        
        # Bins 1, 2, 3 should be empty
        assert bins[1]['count'] == 0
        assert bins[2]['count'] == 0
        assert bins[3]['count'] == 0
        
        # Bins 0 and 4 should have solutions
        assert bins[0]['count'] == 1
        assert bins[4]['count'] == 1
    
    def test_single_solution(self):
        """Test binning with single solution."""
        analyzer = DependencyBloatAnalyzer()
        
        counts_with_names = [("OnlySolution", 75)]
        
        bins = analyzer.create_histogram_bins(counts_with_names)
        
        # Only bin 1 (51-100) should have a solution
        assert sum(bin['count'] for bin in bins) == 1
        assert bins[1]['count'] == 1
        assert 'OnlySolution' in bins[1]['solutions']


class TestQuartileCalculation:
    """Test quartile and IQR calculations."""
    
    def test_median_and_quartiles(self):
        """Test median, Q1, Q3 calculation."""
        analyzer = DependencyBloatAnalyzer()
        
        # Even number of values
        counts = [10, 20, 30, 40, 50, 60, 70, 80]
        stats = analyzer.calculate_statistics(counts)
        
        # Median of [10, 20, 30, 40, 50, 60, 70, 80] = (40 + 50) / 2 = 45
        assert stats['median'] == 45.0
        
        # Q1 = median of [10, 20, 30, 40] = (20 + 30) / 2 = 25
        assert stats['q1'] == 25.0
        
        # Q3 = median of [50, 60, 70, 80] = (60 + 70) / 2 = 65
        assert stats['q3'] == 65.0
        
        # IQR = Q3 - Q1 = 65 - 25 = 40
        assert stats['iqr'] == 40.0
    
    def test_outlier_threshold(self):
        """Test outlier threshold calculation (Q3 + 1.5*IQR)."""
        analyzer = DependencyBloatAnalyzer()
        
        counts = [10, 20, 30, 40, 50, 60, 70, 80]
        stats = analyzer.calculate_statistics(counts)
        
        # Outlier threshold = Q3 + 1.5*IQR = 65 + 1.5*40 = 125
        expected_threshold = 65.0 + (1.5 * 40.0)
        assert stats['outlier_threshold'] == expected_threshold


class TestBloatScore:
    """Test bloat score (z-score) calculation."""
    
    def test_normal_range_bloat_score(self):
        """Test bloat score for solutions in normal range."""
        analyzer = DependencyBloatAnalyzer()
        
        mean = 100.0
        std_dev = 20.0
        
        # Package count equal to mean
        score = analyzer.calculate_bloat_score(100, mean, std_dev)
        assert score == pytest.approx(0.0, abs=0.01)
        
        # Package count 1 std dev above mean
        score = analyzer.calculate_bloat_score(120, mean, std_dev)
        assert score == pytest.approx(1.0, abs=0.01)
        
        # Package count 1 std dev below mean
        score = analyzer.calculate_bloat_score(80, mean, std_dev)
        assert score == pytest.approx(-1.0, abs=0.01)
    
    def test_high_bloat_score(self):
        """Test bloat score for solutions with high package counts."""
        analyzer = DependencyBloatAnalyzer()
        
        mean = 100.0
        std_dev = 20.0
        
        # Package count 2 std devs above mean (critical threshold)
        score = analyzer.calculate_bloat_score(140, mean, std_dev)
        assert score == pytest.approx(2.0, abs=0.01)
        
        # Package count 3 std devs above mean
        score = analyzer.calculate_bloat_score(160, mean, std_dev)
        assert score == pytest.approx(3.0, abs=0.01)
        
        # Verify categorization
        assert analyzer.categorize_bloat(2.0) == 'critical'
        assert analyzer.categorize_bloat(3.0) == 'critical'


class TestOutlierDetection:
    """Test outlier detection using IQR method."""
    
    def test_detect_single_outlier(self):
        """Test detection of single outlier."""
        analyzer = DependencyBloatAnalyzer()
        
        counts = [10, 20, 30, 40, 50, 200]  # 200 is outlier
        
        stats = analyzer.calculate_statistics(counts)
        outlier_flags = analyzer.detect_outliers(counts, stats['outlier_threshold'])
        
        # First 5 values should not be outliers
        assert outlier_flags[:5] == [False, False, False, False, False]
        
        # Last value should be outlier
        assert outlier_flags[5] is True
    
    def test_detect_multiple_outliers(self):
        """Test detection of multiple outliers."""
        analyzer = DependencyBloatAnalyzer()
        
        # Use distribution where outliers are clearly beyond Q3 + 1.5*IQR
        # Normal range: 20-40, Outliers: 100, 120 (far beyond threshold)
        counts = [20, 22, 25, 28, 30, 32, 35, 38, 40, 100, 120]
        # Q1 ≈ 26, Q3 ≈ 37, IQR ≈ 11, threshold ≈ 53.5
        # So 100 and 120 are clear outliers
        
        stats = analyzer.calculate_statistics(counts)
        outlier_flags = analyzer.detect_outliers(counts, stats['outlier_threshold'])
        
        # Count outliers (expect 2)
        outlier_count = sum(outlier_flags)
        assert outlier_count == 2
        
        # Verify last 2 are outliers (100 and 120 are well above threshold)
        assert outlier_flags[-2:] == [True, True]
    
    def test_no_outliers(self):
        """Test when no outliers exist."""
        analyzer = DependencyBloatAnalyzer()
        
        # Tightly clustered data
        counts = [45, 50, 55, 60, 65]
        
        stats = analyzer.calculate_statistics(counts)
        outlier_flags = analyzer.detect_outliers(counts, stats['outlier_threshold'])
        
        # No outliers should be detected
        assert all(flag is False for flag in outlier_flags)


class TestDataLoading:
    """Test data loading and extraction."""
    
    def test_load_valid_data(self, temp_tech_stack_file):
        """Test loading valid tech stack JSON."""
        analyzer = DependencyBloatAnalyzer(temp_tech_stack_file)
        data = analyzer.load_data()
        
        assert data is not None
        assert 'solutions' in data
        assert len(data['solutions']) == 6
    
    def test_extract_package_counts(self, sample_tech_stack):
        """Test extracting package counts from data."""
        analyzer = DependencyBloatAnalyzer()
        counts = analyzer.extract_package_counts(sample_tech_stack)
        
        assert len(counts) == 6
        assert counts[0] == ("Solution1", 50)
        assert counts[1] == ("Solution2", 75)
        assert counts[2] == ("Solution3", 100)
        assert counts[3] == ("Solution4", 125)
        assert counts[4] == ("Solution5", 150)
        assert counts[5] == ("Solution6", 400)  # Outlier


class TestCompleteAnalysis:
    """Test complete bloat analysis workflow."""
    
    def test_full_analysis(self, sample_tech_stack):
        """Test complete analysis workflow."""
        analyzer = DependencyBloatAnalyzer()
        analysis = analyzer.analyze(sample_tech_stack)
        
        # Verify analysis structure
        assert isinstance(analysis, BloatAnalysis)
        assert len(analysis.solutions) == 6
        
        # Verify statistics
        assert analysis.mean > 0
        assert analysis.median > 0
        assert analysis.iqr > 0
        
        # Verify solutions are sorted by bloat score (highest first)
        assert analysis.solutions[0].bloat_score >= analysis.solutions[-1].bloat_score
        
        # Verify Solution6 (250 packages) is identified as outlier
        solution6 = next(s for s in analysis.solutions if s.solution_name == "Solution6")
        assert solution6.is_outlier is True
        assert solution6.category in ['critical', 'warning']
        
        # Verify histogram bins
        assert len(analysis.histogram_bins) == 5
        
        # Verify recommendations exist
        assert len(analysis.recommendations) > 0
    
    def test_export_to_json(self, sample_tech_stack):
        """Test JSON export functionality."""
        analyzer = DependencyBloatAnalyzer()
        analysis = analyzer.analyze(sample_tech_stack)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            output_path = f.name
        
        try:
            analyzer.export_to_json(analysis, output_path)
            
            # Verify file was created and contains valid JSON
            with open(output_path, 'r') as f:
                exported_data = json.load(f)
            
            assert 'statistics' in exported_data
            assert 'solutions' in exported_data
            assert 'histogram_bins' in exported_data
            assert 'box_plot' in exported_data
            assert 'recommendations' in exported_data
            
            # Verify statistics
            assert exported_data['statistics']['mean'] == analysis.mean
            assert exported_data['statistics']['median'] == analysis.median
            
            # Verify solutions count
            assert len(exported_data['solutions']) == 6
        
        finally:
            Path(output_path).unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
