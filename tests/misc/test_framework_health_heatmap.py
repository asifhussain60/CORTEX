"""
Phase 9.2: Framework Health Heatmap Tests

RED phase: TDD for framework health visualization system that calculates
multiple health factors and generates heatmap data for D3.js.
"""

import pytest
from src.dashboard.intelligence.framework_health_heatmap import FrameworkHealthHeatmap


class TestHealthFactorCalculation:
    """Test individual health factor calculations."""

    def test_calculate_version_currency_score(self):
        """Should calculate version currency based on months since update."""
        heatmap = FrameworkHealthHeatmap()
        
        # Recent update (3 months) = high score
        score_recent = heatmap.calculate_version_currency(months_since_update=3)
        assert score_recent > 80
        
        # Old version (24 months) = low score
        score_old = heatmap.calculate_version_currency(months_since_update=24)
        assert score_old < 40

    def test_calculate_eol_proximity_score(self):
        """Should calculate EOL proximity based on months to EOL."""
        heatmap = FrameworkHealthHeatmap()
        
        # Far from EOL (24 months) = high score
        score_safe = heatmap.calculate_eol_proximity(months_to_eol=24)
        assert score_safe > 80
        
        # Near EOL (3 months) = low score
        score_danger = heatmap.calculate_eol_proximity(months_to_eol=3)
        assert score_danger < 40

    def test_calculate_cve_severity_score(self):
        """Should calculate CVE severity based on vulnerability count."""
        heatmap = FrameworkHealthHeatmap()
        
        # No CVEs = high score
        score_safe = heatmap.calculate_cve_severity(cve_count=0)
        assert score_safe == 100
        
        # Many CVEs = low score
        score_vulnerable = heatmap.calculate_cve_severity(cve_count=15)
        assert score_vulnerable < 30

    def test_eol_proximity_handles_none(self):
        """Should handle missing EOL data gracefully."""
        heatmap = FrameworkHealthHeatmap()
        
        score = heatmap.calculate_eol_proximity(months_to_eol=None)
        
        # Should return neutral score (50) when data unavailable
        assert score == 50

    def test_version_currency_handles_zero(self):
        """Should handle zero months since update (just released)."""
        heatmap = FrameworkHealthHeatmap()
        
        score = heatmap.calculate_version_currency(months_since_update=0)
        
        assert score == 100


class TestHealthCalculation:
    """Test calculating complete health profile for frameworks."""

    def test_calculate_framework_health(self):
        """Should calculate all health factors for a framework."""
        framework = {
            "name": ".NET",
            "version": "8",
            "months_since_update": 6,
            "months_to_eol": 36,
            "cve_count": 2
        }
        
        heatmap = FrameworkHealthHeatmap()
        health = heatmap.calculate_health(framework)
        
        assert "version_currency" in health
        assert "eol_proximity" in health
        assert "cve_severity" in health
        assert health["version_currency"] > 0
        assert health["eol_proximity"] > 0
        assert health["cve_severity"] > 0

    def test_calculate_health_normalizes_scores(self):
        """Health scores should be normalized to 0-100 range."""
        framework = {
            "name": ".NET Framework",
            "version": "4.8",
            "months_since_update": 48,
            "months_to_eol": 0,
            "cve_count": 20
        }
        
        heatmap = FrameworkHealthHeatmap()
        health = heatmap.calculate_health(framework)
        
        for factor, score in health.items():
            assert 0 <= score <= 100, f"{factor} score {score} not in 0-100 range"

    def test_calculate_health_with_missing_fields(self):
        """Should handle frameworks with missing health data."""
        framework = {
            "name": "CustomFramework",
            "version": "1.0"
            # No health data
        }
        
        heatmap = FrameworkHealthHeatmap()
        health = heatmap.calculate_health(framework)
        
        # Should still return health factors (with defaults)
        assert "version_currency" in health
        assert "eol_proximity" in health
        assert "cve_severity" in health


class TestDataFlattening:
    """Test flattening framework data for D3.js heatmap."""

    def test_flatten_to_heatmap_data(self):
        """Should flatten frameworks × factors into 2D array."""
        frameworks = [
            {"name": ".NET", "version": "8"},
            {"name": "Node.js", "version": "20"}
        ]
        health_data = {
            ".NET 8": {"version_currency": 90, "eol_proximity": 85, "cve_severity": 80},
            "Node.js 20": {"version_currency": 95, "eol_proximity": 90, "cve_severity": 92}
        }
        
        heatmap = FrameworkHealthHeatmap()
        flattened = heatmap.flatten_to_heatmap(frameworks, health_data)
        
        # Should have rows for each framework × factor combination
        assert len(flattened) == 2 * 3  # 2 frameworks × 3 factors

    def test_heatmap_row_structure(self):
        """Each heatmap row should have framework, factor, and score."""
        frameworks = [{"name": ".NET", "version": "8"}]
        health_data = {
            ".NET 8": {"version_currency": 90, "eol_proximity": 85, "cve_severity": 80}
        }
        
        heatmap = FrameworkHealthHeatmap()
        flattened = heatmap.flatten_to_heatmap(frameworks, health_data)
        
        row = flattened[0]
        assert "framework" in row
        assert "factor" in row
        assert "score" in row

    def test_heatmap_factor_labels(self):
        """Factors should have human-readable labels."""
        frameworks = [{"name": ".NET", "version": "8"}]
        health_data = {
            ".NET 8": {"version_currency": 90, "eol_proximity": 85, "cve_severity": 80}
        }
        
        heatmap = FrameworkHealthHeatmap()
        flattened = heatmap.flatten_to_heatmap(frameworks, health_data)
        
        factors = [row["factor"] for row in flattened]
        assert "Version Currency" in factors
        assert "EOL Proximity" in factors
        assert "CVE Severity" in factors


class TestScoreNormalization:
    """Test score normalization for consistent color mapping."""

    def test_normalize_scores_to_0_100(self):
        """Should ensure all scores are in 0-100 range."""
        scores = [25, 50, 75, 100, 0]
        
        heatmap = FrameworkHealthHeatmap()
        normalized = heatmap.normalize_scores(scores)
        
        for score in normalized:
            assert 0 <= score <= 100

    def test_normalize_handles_negative_scores(self):
        """Should clamp negative scores to 0."""
        scores = [-10, -5, 0, 50, 100]
        
        heatmap = FrameworkHealthHeatmap()
        normalized = heatmap.normalize_scores(scores)
        
        assert all(score >= 0 for score in normalized)

    def test_normalize_handles_excessive_scores(self):
        """Should clamp scores above 100."""
        scores = [100, 110, 120]
        
        heatmap = FrameworkHealthHeatmap()
        normalized = heatmap.normalize_scores(scores)
        
        assert all(score <= 100 for score in normalized)


class TestColorScaleGeneration:
    """Test color scale generation for heatmap visualization."""

    def test_generate_color_scale(self):
        """Should generate color scale thresholds."""
        heatmap = FrameworkHealthHeatmap()
        scale = heatmap.generate_color_scale()
        
        assert "thresholds" in scale
        assert "colors" in scale
        assert len(scale["thresholds"]) > 0
        assert len(scale["colors"]) > 0

    def test_color_scale_has_standard_ranges(self):
        """Color scale should use standard health ranges."""
        heatmap = FrameworkHealthHeatmap()
        scale = heatmap.generate_color_scale()
        
        thresholds = scale["thresholds"]
        # Should have thresholds for: Critical (<30), Warning (30-60), Healthy (60-80), Excellent (80+)
        assert 30 in thresholds or 25 in thresholds
        assert 60 in thresholds or 50 in thresholds
        assert 80 in thresholds or 75 in thresholds

    def test_color_scale_colors_are_hex(self):
        """Colors should be hex codes."""
        heatmap = FrameworkHealthHeatmap()
        scale = heatmap.generate_color_scale()
        
        for color in scale["colors"]:
            assert color.startswith("#")
            assert len(color) == 7  # #RRGGBB


class TestHeatmapGeneration:
    """Test complete heatmap generation."""

    def test_generate_heatmap_from_tech_stack(self):
        """Should generate complete heatmap from tech stack."""
        tech_stack = {
            "backend": [
                {
                    "name": ".NET",
                    "version": "8",
                    "months_since_update": 6,
                    "months_to_eol": 36,
                    "cve_count": 2
                },
                {
                    "name": ".NET Framework",
                    "version": "4.8",
                    "months_since_update": 48,
                    "months_to_eol": 0,
                    "cve_count": 15
                }
            ]
        }
        
        heatmap = FrameworkHealthHeatmap()
        result = heatmap.generate(tech_stack)
        
        assert "data" in result
        assert "color_scale" in result
        assert "summary" in result
        assert len(result["data"]) > 0

    def test_heatmap_includes_all_frameworks(self):
        """Heatmap should include all frameworks from tech stack."""
        tech_stack = {
            "backend": [
                {"name": ".NET", "version": "8"},
                {"name": "Node.js", "version": "20"}
            ],
            "frontend": [
                {"name": "React", "version": "18"}
            ]
        }
        
        heatmap = FrameworkHealthHeatmap()
        result = heatmap.generate(tech_stack)
        
        frameworks = set(row["framework"] for row in result["data"])
        assert ".NET 8" in frameworks
        assert "Node.js 20" in frameworks
        assert "React 18" in frameworks

    def test_heatmap_summary_statistics(self):
        """Summary should contain aggregate health statistics."""
        tech_stack = {
            "backend": [
                {"name": ".NET", "version": "8", "months_since_update": 6, "months_to_eol": 36, "cve_count": 2}
            ]
        }
        
        heatmap = FrameworkHealthHeatmap()
        result = heatmap.generate(tech_stack)
        
        summary = result["summary"]
        assert "total_frameworks" in summary
        assert "average_health_score" in summary
        assert "critical_frameworks" in summary

    def test_heatmap_identifies_critical_frameworks(self):
        """Should identify frameworks with low health scores."""
        tech_stack = {
            "backend": [
                {"name": ".NET Framework", "version": "4.8", "months_since_update": 48, "months_to_eol": 0, "cve_count": 20}
            ]
        }
        
        heatmap = FrameworkHealthHeatmap()
        result = heatmap.generate(tech_stack)
        
        assert result["summary"]["critical_frameworks"] > 0

    def test_generate_handles_empty_tech_stack(self):
        """Should handle empty tech stack gracefully."""
        heatmap = FrameworkHealthHeatmap()
        result = heatmap.generate({"backend": [], "frontend": []})
        
        assert result["data"] == []
        assert result["summary"]["total_frameworks"] == 0


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_handles_framework_without_version(self):
        """Should handle frameworks without version information."""
        framework = {"name": "CustomFramework"}
        
        heatmap = FrameworkHealthHeatmap()
        health = heatmap.calculate_health(framework)
        
        assert health is not None
        assert "version_currency" in health

    def test_handles_extreme_months_values(self):
        """Should handle extreme months_since_update values."""
        heatmap = FrameworkHealthHeatmap()
        
        # Very old (100 years)
        score_ancient = heatmap.calculate_version_currency(months_since_update=1200)
        assert 0 <= score_ancient <= 100
        
        # Just released
        score_new = heatmap.calculate_version_currency(months_since_update=0)
        assert score_new == 100

    def test_handles_negative_cve_count(self):
        """Should handle invalid negative CVE counts."""
        heatmap = FrameworkHealthHeatmap()
        
        score = heatmap.calculate_cve_severity(cve_count=-5)
        
        # Should treat as 0
        assert score == 100
