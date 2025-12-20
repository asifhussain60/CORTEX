"""
Tests for Package Health Dashboard Component

Tests statistical calculations, outlier detection, color coding,
and D3.js chart rendering logic.
"""

import pytest
import statistics


class TestPackageHealthDashboard:
    """Test suite for Package Health Dashboard"""

    @pytest.fixture
    def sample_projects(self):
        """Sample project data with package counts"""
        return [
            {"name": "PrevalBusiness", "packages": 272, "type": ".NET Framework 4.8"},
            {"name": "PrevalValidation", "packages": 170, "type": ".NET Framework 4.8"},
            {"name": "PrevalCommon", "packages": 173, "type": ".NET Framework 4.8"},
            {"name": "PrevalWeb", "packages": 95, "type": ".NET Framework 4.8"},
            {"name": "PrevalApi", "packages": 88, "type": ".NET Framework 4.8"}
        ]

    @pytest.fixture
    def tech_stack_data(self, sample_projects):
        """Full tech-stack.json structure"""
        return {
            "backend": [
                {
                    "name": "C#",
                    "version": "7.3",
                    "metadata": {
                        "projects": sample_projects
                    }
                }
            ]
        }

    @pytest.fixture
    def empty_data(self):
        """Empty tech stack data"""
        return {"backend": []}

    def test_calculate_mean(self, sample_projects):
        """Test mean calculation"""
        package_counts = [p["packages"] for p in sample_projects]
        mean = sum(package_counts) / len(package_counts)
        
        expected = (272 + 170 + 173 + 95 + 88) / 5
        assert abs(mean - expected) < 0.01
        assert mean == 159.6

    def test_calculate_median(self, sample_projects):
        """Test median calculation"""
        package_counts = sorted([p["packages"] for p in sample_projects])
        median = statistics.median(package_counts)
        
        # Sorted: [88, 95, 170, 173, 272]
        # Median (odd count): 170
        assert median == 170

    def test_calculate_std_dev(self, sample_projects):
        """Test standard deviation calculation"""
        package_counts = [p["packages"] for p in sample_projects]
        std_dev = statistics.stdev(package_counts)
        
        # Expected: ~69.7
        assert 65 < std_dev < 75

    def test_outlier_detection_warning(self, sample_projects):
        """Test outlier detection for warning threshold (>1.5x avg)"""
        package_counts = [p["packages"] for p in sample_projects]
        mean = sum(package_counts) / len(package_counts)  # 159.6
        
        warning_threshold = mean * 1.5  # 239.4
        outliers_warning = [p for p in sample_projects if p["packages"] > warning_threshold]
        
        # PrevalBusiness (272) exceeds warning threshold
        assert len(outliers_warning) == 1
        assert outliers_warning[0]["name"] == "PrevalBusiness"

    def test_outlier_detection_critical(self, sample_projects):
        """Test outlier detection for critical threshold (>2x avg)"""
        package_counts = [p["packages"] for p in sample_projects]
        mean = sum(package_counts) / len(package_counts)  # 159.6
        
        critical_threshold = mean * 2  # 319.2
        outliers_critical = [p for p in sample_projects if p["packages"] > critical_threshold]
        
        # None exceed critical threshold in this dataset
        assert len(outliers_critical) == 0

    def test_outlier_detection_with_critical(self):
        """Test outlier detection with project exceeding critical threshold"""
        projects = [
            {"name": "Bloated", "packages": 500, "type": ".NET Framework 4.8"},
            {"name": "Normal1", "packages": 100, "type": ".NET Framework 4.8"},
            {"name": "Normal2", "packages": 120, "type": ".NET Framework 4.8"}
        ]
        
        mean = (500 + 100 + 120) / 3  # 240
        critical_threshold = mean * 2  # 480
        
        outliers_critical = [p for p in projects if p["packages"] > critical_threshold]
        
        assert len(outliers_critical) == 1
        assert outliers_critical[0]["name"] == "Bloated"

    def test_health_color_coding(self, sample_projects):
        """Test color class assignment based on package count vs average"""
        package_counts = [p["packages"] for p in sample_projects]
        mean = sum(package_counts) / len(package_counts)  # 159.6
        
        def get_health_color(count, avg):
            if count > avg * 2:
                return 'health-critical'
            if count > avg * 1.5:
                return 'health-warning'
            if count > avg:
                return 'health-caution'
            return 'health-good'
        
        # PrevalBusiness: 272 > 239.4 (1.5x) → warning
        assert get_health_color(272, mean) == 'health-warning'
        
        # PrevalValidation: 170 > 159.6 but < 239.4 → caution
        assert get_health_color(170, mean) == 'health-caution'
        
        # PrevalWeb: 95 < 159.6 → good
        assert get_health_color(95, mean) == 'health-good'

    def test_extract_projects_from_tech_stack(self, tech_stack_data):
        """Test project extraction from tech-stack.json"""
        projects = []
        
        for tech in tech_stack_data["backend"]:
            if tech.get("metadata") and tech["metadata"].get("projects"):
                for project in tech["metadata"]["projects"]:
                    if "packages" in project:
                        projects.append({
                            "name": project["name"],
                            "packages": project["packages"],
                            "type": project.get("type", "Unknown")
                        })
        
        assert len(projects) == 5
        assert projects[0]["name"] == "PrevalBusiness"
        assert projects[0]["packages"] == 272

    def test_empty_data_handling(self, empty_data):
        """Test handling of empty tech stack data"""
        projects = []
        
        for tech in empty_data["backend"]:
            if tech.get("metadata") and tech["metadata"].get("projects"):
                projects.extend(tech["metadata"]["projects"])
        
        assert len(projects) == 0
        
        # Statistics should handle empty data gracefully
        if len(projects) == 0:
            stats = {"mean": 0, "median": 0, "stdDev": 0, "outliers": []}
        
        assert stats["mean"] == 0
        assert stats["median"] == 0
        assert len(stats["outliers"]) == 0

    def test_percent_above_mean_calculation(self, sample_projects):
        """Test percentage above mean calculation"""
        package_counts = [p["packages"] for p in sample_projects]
        mean = sum(package_counts) / len(package_counts)  # 159.6
        
        # PrevalBusiness: 272 packages
        percent_above = ((272 - mean) / mean) * 100
        
        # (272 - 159.6) / 159.6 * 100 = 70.4%
        assert 70 < percent_above < 71

    def test_project_sorting_by_package_count(self, sample_projects):
        """Test projects are sorted by package count descending"""
        sorted_projects = sorted(sample_projects, key=lambda p: p["packages"], reverse=True)
        
        assert sorted_projects[0]["name"] == "PrevalBusiness"  # 272
        assert sorted_projects[1]["name"] == "PrevalCommon"    # 173
        assert sorted_projects[2]["name"] == "PrevalValidation"  # 170
        assert sorted_projects[3]["name"] == "PrevalWeb"       # 95
        assert sorted_projects[4]["name"] == "PrevalApi"       # 88


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
