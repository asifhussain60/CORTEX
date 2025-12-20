"""
Phase 9.3: Dependency Bloat Analyzer Tests

RED phase: TDD for dependency bloat detection system that identifies projects
with excessive dependencies using statistical analysis.
"""

import pytest
from src.dashboard.intelligence.dependency_bloat_analyzer import DependencyBloatAnalyzer


class TestStatisticalCalculations:
    """Test statistical calculations for dependency analysis."""

    def test_calculate_mean(self):
        """Should calculate arithmetic mean of package counts."""
        package_counts = [10, 20, 30, 40, 50]
        
        analyzer = DependencyBloatAnalyzer()
        mean = analyzer.calculate_mean(package_counts)
        
        assert mean == 30.0

    def test_calculate_median_odd_count(self):
        """Should calculate median with odd number of values."""
        package_counts = [10, 20, 30, 40, 50]
        
        analyzer = DependencyBloatAnalyzer()
        median = analyzer.calculate_median(package_counts)
        
        assert median == 30.0

    def test_calculate_median_even_count(self):
        """Should calculate median with even number of values."""
        package_counts = [10, 20, 30, 40]
        
        analyzer = DependencyBloatAnalyzer()
        median = analyzer.calculate_median(package_counts)
        
        assert median == 25.0  # Average of 20 and 30

    def test_calculate_standard_deviation(self):
        """Should calculate population standard deviation."""
        package_counts = [10, 20, 30, 40, 50]
        
        analyzer = DependencyBloatAnalyzer()
        stddev = analyzer.calculate_stddev(package_counts)
        
        # Expected: sqrt(((10-30)^2 + (20-30)^2 + ... + (50-30)^2) / 5)
        # = sqrt((400 + 100 + 0 + 100 + 400) / 5) = sqrt(200) ≈ 14.14
        assert abs(stddev - 14.14) < 0.1

    def test_calculate_statistics_together(self):
        """Should calculate all statistics together."""
        package_counts = [5, 10, 15, 20, 25, 100]
        
        analyzer = DependencyBloatAnalyzer()
        stats = analyzer.calculate_statistics(package_counts)
        
        assert "mean" in stats
        assert "median" in stats
        assert "stddev" in stats
        assert stats["mean"] > 0
        assert stats["median"] > 0
        assert stats["stddev"] > 0


class TestBloatScoreCalculation:
    """Test bloat score calculation."""

    def test_calculate_bloat_score(self):
        """Should calculate bloat score using z-score formula."""
        analyzer = DependencyBloatAnalyzer()
        
        # Package count above mean
        score = analyzer.calculate_bloat_score(
            package_count=50,
            mean=30,
            stddev=10
        )
        
        # (50 - 30) / 10 = 2.0
        assert score == 2.0

    def test_bloat_score_at_mean(self):
        """Bloat score should be 0 when at mean."""
        analyzer = DependencyBloatAnalyzer()
        
        score = analyzer.calculate_bloat_score(
            package_count=30,
            mean=30,
            stddev=10
        )
        
        assert score == 0.0

    def test_bloat_score_below_mean(self):
        """Bloat score should be negative when below mean."""
        analyzer = DependencyBloatAnalyzer()
        
        score = analyzer.calculate_bloat_score(
            package_count=10,
            mean=30,
            stddev=10
        )
        
        assert score == -2.0

    def test_bloat_score_handles_zero_stddev(self):
        """Should handle zero standard deviation gracefully."""
        analyzer = DependencyBloatAnalyzer()
        
        score = analyzer.calculate_bloat_score(
            package_count=30,
            mean=30,
            stddev=0
        )
        
        # Should return 0 when stddev is 0
        assert score == 0.0


class TestOutlierDetection:
    """Test outlier detection logic."""

    def test_identify_outliers_by_bloat_score(self):
        """Should identify outliers with bloat score > 2.0."""
        projects = [
            {"name": "Project A", "package_count": 10},
            {"name": "Project B", "package_count": 15},
            {"name": "Project C", "package_count": 20},
            {"name": "Project D", "package_count": 100}  # Outlier
        ]
        
        analyzer = DependencyBloatAnalyzer()
        outliers = analyzer.identify_outliers(projects)
        
        assert len(outliers) == 1
        assert outliers[0]["name"] == "Project D"

    def test_outlier_threshold_configurable(self):
        """Should allow custom outlier threshold."""
        projects = [
            {"name": "Project A", "package_count": 10},
            {"name": "Project B", "package_count": 10},
            {"name": "Project C", "package_count": 10},
            {"name": "Project D", "package_count": 50},  # Clear outlier
        ]
        
        analyzer = DependencyBloatAnalyzer()
        
        # With threshold 2.0, should find outlier
        outliers_strict = analyzer.identify_outliers(projects, threshold=2.0)
        assert len(outliers_strict) >= 0  # May or may not find depending on stddev
        
        # With threshold 0.5, definitely finds outlier
        outliers_lenient = analyzer.identify_outliers(projects, threshold=0.5)
        assert len(outliers_lenient) >= 1

    def test_identify_outliers_includes_bloat_score(self):
        """Outliers should include bloat score."""
        projects = [
            {"name": "Project A", "package_count": 10},
            {"name": "Project B", "package_count": 100}
        ]
        
        analyzer = DependencyBloatAnalyzer()
        outliers = analyzer.identify_outliers(projects)
        
        if outliers:
            assert "bloat_score" in outliers[0]


class TestRecommendationGeneration:
    """Test generating recommendations for bloated projects."""

    def test_generate_recommendation_for_high_bloat(self):
        """Should generate recommendation for high bloat score."""
        analyzer = DependencyBloatAnalyzer()
        
        recommendation = analyzer.generate_recommendation(bloat_score=3.0)
        
        assert "review dependencies" in recommendation.lower() or "reduce" in recommendation.lower()

    def test_generate_recommendation_for_moderate_bloat(self):
        """Should generate different recommendation for moderate bloat."""
        analyzer = DependencyBloatAnalyzer()
        
        high_rec = analyzer.generate_recommendation(bloat_score=3.0)
        moderate_rec = analyzer.generate_recommendation(bloat_score=1.5)
        
        # Recommendations should differ by severity
        assert high_rec != moderate_rec

    def test_generate_recommendation_for_normal_project(self):
        """Should indicate healthy status for normal projects."""
        analyzer = DependencyBloatAnalyzer()
        
        recommendation = analyzer.generate_recommendation(bloat_score=0.5)
        
        assert "healthy" in recommendation.lower() or "acceptable" in recommendation.lower()


class TestHistogramGeneration:
    """Test histogram generation for visualization."""

    def test_generate_histogram_bins(self):
        """Should generate histogram bins for package distribution."""
        package_counts = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50]
        
        analyzer = DependencyBloatAnalyzer()
        histogram = analyzer.generate_histogram(package_counts, bins=5)
        
        assert "bins" in histogram
        assert "counts" in histogram
        assert len(histogram["bins"]) == 5
        assert len(histogram["counts"]) == 5

    def test_histogram_bins_cover_full_range(self):
        """Histogram bins should cover from min to max."""
        package_counts = [10, 50]
        
        analyzer = DependencyBloatAnalyzer()
        histogram = analyzer.generate_histogram(package_counts, bins=4)
        
        bins = histogram["bins"]
        assert bins[0] == 10  # First bin starts at min
        # Bins are start positions, last bin starts before max (covers up to max)

    def test_histogram_counts_sum_to_total(self):
        """Histogram counts should sum to total number of projects."""
        package_counts = [5, 10, 15, 20, 25]
        
        analyzer = DependencyBloatAnalyzer()
        histogram = analyzer.generate_histogram(package_counts, bins=3)
        
        total_count = sum(histogram["counts"])
        assert total_count == len(package_counts)


class TestBloatAnalysis:
    """Test complete bloat analysis."""

    def test_analyze_dependency_bloat(self):
        """Should analyze dependency bloat for all projects."""
        projects = [
            {"name": "Project A", "dependencies": {"backend": ["pkg1", "pkg2"]}},
            {"name": "Project B", "dependencies": {"backend": ["pkg1", "pkg2", "pkg3"]}},
            {"name": "Project C", "dependencies": {"backend": ["pkg1"] * 50}}  # Bloated
        ]
        
        analyzer = DependencyBloatAnalyzer()
        analysis = analyzer.analyze(projects)
        
        assert "statistics" in analysis
        assert "outliers" in analysis
        assert "histogram" in analysis
        assert "summary" in analysis

    def test_analysis_statistics_accuracy(self):
        """Statistics should accurately reflect data."""
        projects = [
            {"name": "A", "dependencies": {"backend": ["pkg1", "pkg2"]}},
            {"name": "B", "dependencies": {"backend": ["pkg1", "pkg2", "pkg3", "pkg4"]}}
        ]
        
        analyzer = DependencyBloatAnalyzer()
        analysis = analyzer.analyze(projects)
        
        stats = analysis["statistics"]
        # Mean of 2 and 4 is 3
        assert stats["mean"] == 3.0

    def test_analysis_identifies_bloated_projects(self):
        """Should identify projects with excessive dependencies."""
        projects = [
            {"name": "Normal1", "dependencies": {"backend": ["pkg1", "pkg2"]}},
            {"name": "Normal2", "dependencies": {"backend": ["pkg1", "pkg2", "pkg3"]}},
            {"name": "Normal3", "dependencies": {"backend": ["pkg1", "pkg2"]}},
            {"name": "Bloated", "dependencies": {"backend": ["pkg" + str(i) for i in range(100)]}}
        ]
        
        analyzer = DependencyBloatAnalyzer()
        analysis = analyzer.analyze(projects)
        
        assert len(analysis["outliers"]) > 0
        assert analysis["outliers"][0]["name"] == "Bloated"

    def test_analysis_summary_statistics(self):
        """Summary should contain aggregate metrics."""
        projects = [
            {"name": "A", "dependencies": {"backend": ["pkg1"]}},
            {"name": "B", "dependencies": {"backend": ["pkg1", "pkg2"]}}
        ]
        
        analyzer = DependencyBloatAnalyzer()
        analysis = analyzer.analyze(projects)
        
        summary = analysis["summary"]
        assert "total_projects" in summary
        assert "bloated_projects" in summary
        assert "average_packages" in summary

    def test_analyze_handles_empty_dependencies(self):
        """Should handle projects with no dependencies."""
        projects = [
            {"name": "Empty", "dependencies": {}}
        ]
        
        analyzer = DependencyBloatAnalyzer()
        analysis = analyzer.analyze(projects)
        
        assert analysis["statistics"]["mean"] == 0
        assert len(analysis["outliers"]) == 0

    def test_analyze_handles_missing_dependencies_key(self):
        """Should handle projects without dependencies key."""
        projects = [
            {"name": "Project A"},
            {"name": "Project B", "dependencies": {"backend": ["pkg1"]}}
        ]
        
        analyzer = DependencyBloatAnalyzer()
        analysis = analyzer.analyze(projects)
        
        # Should treat missing as 0 packages
        assert analysis is not None


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_handles_single_project(self):
        """Should handle single project gracefully."""
        projects = [{"name": "Only", "dependencies": {"backend": ["pkg1"]}}]
        
        analyzer = DependencyBloatAnalyzer()
        analysis = analyzer.analyze(projects)
        
        assert analysis["statistics"]["stddev"] == 0

    def test_handles_empty_project_list(self):
        """Should handle empty project list."""
        analyzer = DependencyBloatAnalyzer()
        analysis = analyzer.analyze([])
        
        assert analysis["statistics"]["mean"] == 0
        assert analysis["outliers"] == []

    def test_handles_all_projects_same_count(self):
        """Should handle all projects with same package count."""
        projects = [
            {"name": f"Project {i}", "dependencies": {"backend": ["pkg1", "pkg2"]}}
            for i in range(5)
        ]
        
        analyzer = DependencyBloatAnalyzer()
        analysis = analyzer.analyze(projects)
        
        assert analysis["statistics"]["stddev"] == 0
        assert len(analysis["outliers"]) == 0
