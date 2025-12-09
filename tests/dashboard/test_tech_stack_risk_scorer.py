"""
Phase 8.2: Technology Risk Scorer Tests

RED phase: TDD for risk scoring system that integrates EOL data from endoflife.date API
and calculates comprehensive risk scores based on age, EOL proximity, and CVE count.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, Mock
from src.dashboard.data.tech_stack_risk_scorer import TechStackRiskScorer


class TestEOLAPIIntegration:
    """Test endoflife.date API integration."""

    @patch('requests.get')
    def test_fetch_eol_data_for_dotnet(self, mock_get):
        """Should fetch EOL data for .NET from API."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "cycle": "8",
                "releaseDate": "2023-11-14",
                "eol": "2026-11-10",
                "latest": "8.0.22",
                "lts": True
            },
            {
                "cycle": "6",
                "releaseDate": "2021-11-08",
                "eol": "2024-11-12",
                "latest": "6.0.36",
                "lts": True
            }
        ]
        mock_get.return_value = mock_response
        
        scorer = TechStackRiskScorer()
        eol_data = scorer.fetch_eol_data("dotnet", "8")
        
        assert eol_data is not None
        assert eol_data["cycle"] == "8"
        assert eol_data["eol"] == "2026-11-10"
        mock_get.assert_called_once_with("https://endoflife.date/api/dotnet.json", timeout=10)

    @patch('requests.get')
    def test_fetch_eol_data_handles_api_failure(self, mock_get):
        """Should return None when API fails."""
        mock_get.side_effect = Exception("Network error")
        
        scorer = TechStackRiskScorer()
        eol_data = scorer.fetch_eol_data("dotnet", "8")
        
        assert eol_data is None

    @patch('requests.get')
    def test_fetch_eol_data_handles_404(self, mock_get):
        """Should return None for unsupported technologies."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        scorer = TechStackRiskScorer()
        eol_data = scorer.fetch_eol_data("unsupported-tech", "1.0")
        
        assert eol_data is None

    @patch('requests.get')
    def test_fetch_eol_data_matches_version_exactly(self, mock_get):
        """Should match exact version from cycle field."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"cycle": "9", "eol": "2026-11-10"},
            {"cycle": "8", "eol": "2026-11-10"},
            {"cycle": "7", "eol": "2024-05-14"}
        ]
        mock_get.return_value = mock_response
        
        scorer = TechStackRiskScorer()
        eol_data = scorer.fetch_eol_data("dotnet", "7")
        
        assert eol_data["cycle"] == "7"
        assert eol_data["eol"] == "2024-05-14"

    @patch('requests.get')
    def test_fetch_eol_data_handles_dotnetfx_no_eol(self, mock_get):
        """Should handle .NET Framework with eol: false."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"cycle": "4.8", "releaseDate": "2019-04-18", "eol": False}
        ]
        mock_get.return_value = mock_response
        
        scorer = TechStackRiskScorer()
        eol_data = scorer.fetch_eol_data("dotnetfx", "4.8")
        
        assert eol_data is not None
        assert eol_data["eol"] is False


class TestRiskScoreCalculation:
    """Test risk score formula: age(30%) + EOL(40%) + CVE(30%)."""

    def test_calculate_age_score(self):
        """Age score: months since last update / 24 months * 30."""
        scorer = TechStackRiskScorer()
        
        # 12 months old = 50% of 24 months = 15 points
        score = scorer.calculate_age_score(months_since_update=12)
        assert score == 15.0
        
        # 24 months old = 100% = 30 points (max)
        score = scorer.calculate_age_score(months_since_update=24)
        assert score == 30.0
        
        # 36 months old = capped at 30 points
        score = scorer.calculate_age_score(months_since_update=36)
        assert score == 30.0
        
        # 0 months = 0 points
        score = scorer.calculate_age_score(months_since_update=0)
        assert score == 0.0

    def test_calculate_eol_score(self):
        """EOL score: max(0, (12 - months_to_eol) / 12) * 40."""
        scorer = TechStackRiskScorer()
        
        # 6 months to EOL = (12-6)/12 * 40 = 20 points
        score = scorer.calculate_eol_score(months_to_eol=6)
        assert score == 20.0
        
        # 12 months to EOL = 0 points (safe threshold)
        score = scorer.calculate_eol_score(months_to_eol=12)
        assert score == 0.0
        
        # 24 months to EOL = 0 points (still safe)
        score = scorer.calculate_eol_score(months_to_eol=24)
        assert score == 0.0
        
        # 0 months to EOL = 40 points (max)
        score = scorer.calculate_eol_score(months_to_eol=0)
        assert score == 40.0
        
        # Already EOL (-6 months) = 40 points (max)
        score = scorer.calculate_eol_score(months_to_eol=-6)
        assert score == 40.0

    def test_calculate_cve_score(self):
        """CVE score: min(cve_count / 10, 1.0) * 30."""
        scorer = TechStackRiskScorer()
        
        # 5 CVEs = 50% of 10 = 15 points
        score = scorer.calculate_cve_score(cve_count=5)
        assert score == 15.0
        
        # 10 CVEs = 100% = 30 points (max)
        score = scorer.calculate_cve_score(cve_count=10)
        assert score == 30.0
        
        # 20 CVEs = capped at 30 points
        score = scorer.calculate_cve_score(cve_count=20)
        assert score == 30.0
        
        # 0 CVEs = 0 points
        score = scorer.calculate_cve_score(cve_count=0)
        assert score == 0.0

    def test_calculate_total_risk_score(self):
        """Total risk = age + eol + cve (max 100)."""
        scorer = TechStackRiskScorer()
        
        # Healthy tech: 0 months old, 24 months to EOL, 0 CVEs = 0
        score = scorer.calculate_risk_score(
            months_since_update=0,
            months_to_eol=24,
            cve_count=0
        )
        assert score == 0.0
        
        # Moderate risk: 12 months old, 6 months to EOL, 5 CVEs
        # = 15 (age) + 20 (eol) + 15 (cve) = 50
        score = scorer.calculate_risk_score(
            months_since_update=12,
            months_to_eol=6,
            cve_count=5
        )
        assert score == 50.0
        
        # High risk: 24 months old, EOL passed, 10 CVEs
        # = 30 (age) + 40 (eol) + 30 (cve) = 100
        score = scorer.calculate_risk_score(
            months_since_update=24,
            months_to_eol=-1,
            cve_count=10
        )
        assert score == 100.0

    def test_calculate_risk_score_handles_no_eol_data(self):
        """Should handle technologies with no EOL date."""
        scorer = TechStackRiskScorer()
        
        # .NET Framework 4.8 has no EOL (eol: false)
        # Score should use age + cve only (no EOL penalty)
        score = scorer.calculate_risk_score(
            months_since_update=60,  # 5 years old
            months_to_eol=None,  # No EOL
            cve_count=3
        )
        
        # Age: 30 (maxed), EOL: 0 (no penalty), CVE: 9 = 39
        assert score == 39.0


class TestMonthsCalculation:
    """Test date difference calculations."""

    def test_calculate_months_since_update(self):
        """Should calculate months between dates."""
        scorer = TechStackRiskScorer()
        
        # 1 year ago
        release_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        months = scorer.calculate_months_since_update(release_date)
        assert 11 <= months <= 13  # ~12 months with tolerance
        
        # 2 years ago
        release_date = (datetime.now() - timedelta(days=730)).strftime("%Y-%m-%d")
        months = scorer.calculate_months_since_update(release_date)
        assert 23 <= months <= 25  # ~24 months

    def test_calculate_months_to_eol(self):
        """Should calculate months until EOL."""
        scorer = TechStackRiskScorer()
        
        # 6 months in future
        eol_date = (datetime.now() + timedelta(days=180)).strftime("%Y-%m-%d")
        months = scorer.calculate_months_to_eol(eol_date)
        assert 5 <= months <= 7  # ~6 months
        
        # 6 months in past (already EOL)
        eol_date = (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d")
        months = scorer.calculate_months_to_eol(eol_date)
        assert -7 <= months <= -5  # ~-6 months

    def test_calculate_months_handles_invalid_dates(self):
        """Should return large number for invalid dates."""
        scorer = TechStackRiskScorer()
        
        months = scorer.calculate_months_since_update("invalid-date")
        assert months == 999  # Sentinel value
        
        months = scorer.calculate_months_to_eol("invalid-date")
        assert months == 999  # Sentinel value


class TestCaching:
    """Test caching mechanism for API calls."""

    @patch('requests.get')
    def test_cache_stores_eol_data(self, mock_get):
        """Should cache EOL data after first fetch."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"cycle": "8", "eol": "2026-11-10"}
        ]
        mock_get.return_value = mock_response
        
        scorer = TechStackRiskScorer()
        
        # First call - hits API
        eol_data_1 = scorer.fetch_eol_data("dotnet", "8")
        
        # Second call - uses cache
        eol_data_2 = scorer.fetch_eol_data("dotnet", "8")
        
        assert eol_data_1 == eol_data_2
        # Should only call API once
        assert mock_get.call_count == 1

    def test_cache_key_includes_tech_and_version(self):
        """Cache keys should differentiate tech+version combinations."""
        scorer = TechStackRiskScorer()
        
        key1 = scorer.get_cache_key("dotnet", "8")
        key2 = scorer.get_cache_key("dotnet", "6")
        key3 = scorer.get_cache_key("nodejs", "8")
        
        assert key1 != key2  # Different versions
        assert key1 != key3  # Different technologies
        assert key2 != key3


class TestEnrichTechnology:
    """Test enriching technology with risk data."""

    @patch('requests.get')
    def test_enrich_technology_with_eol_data(self, mock_get):
        """Should enrich technology dict with EOL and risk score."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "cycle": "8",
                "releaseDate": "2023-11-14",
                "eol": "2026-11-10",
                "latest": "8.0.22"
            }
        ]
        mock_get.return_value = mock_response
        
        tech = {
            "name": ".NET",
            "version": "8",
            "cve_count": 2
        }
        
        scorer = TechStackRiskScorer()
        enriched = scorer.enrich_technology(tech)
        
        assert "eol_date" in enriched
        assert "months_to_eol" in enriched
        assert "risk_score" in enriched
        assert enriched["eol_date"] == "2026-11-10"
        assert isinstance(enriched["risk_score"], float)
        assert 0 <= enriched["risk_score"] <= 100

    @patch('requests.get')
    def test_enrich_technology_handles_no_eol_data(self, mock_get):
        """Should handle technologies with no EOL data gracefully."""
        mock_get.side_effect = Exception("API error")
        
        tech = {
            "name": "Custom Framework",
            "version": "1.0",
            "cve_count": 0
        }
        
        scorer = TechStackRiskScorer()
        enriched = scorer.enrich_technology(tech)
        
        assert enriched["eol_date"] is None
        assert enriched["months_to_eol"] is None
        assert "risk_score" in enriched
        # Should still calculate risk based on age + CVE
        assert enriched["risk_score"] >= 0

    def test_enrich_technology_preserves_original_fields(self):
        """Should preserve all original technology fields."""
        tech = {
            "name": ".NET",
            "version": "8",
            "category": "framework",
            "cve_count": 2,
            "status": "current"
        }
        
        scorer = TechStackRiskScorer()
        enriched = scorer.enrich_technology(tech)
        
        # All original fields preserved
        assert enriched["name"] == ".NET"
        assert enriched["version"] == "8"
        assert enriched["category"] == "framework"
        assert enriched["cve_count"] == 2
        assert enriched["status"] == "current"


class TestTechnologyNameMapping:
    """Test mapping technology names to endoflife.date API names."""

    def test_map_technology_name_to_api(self):
        """Should map common names to API endpoint names."""
        scorer = TechStackRiskScorer()
        
        assert scorer.map_tech_name_to_api(".NET") == "dotnet"
        assert scorer.map_tech_name_to_api(".NET Framework") == "dotnetfx"
        assert scorer.map_tech_name_to_api("Node.js") == "nodejs"
        assert scorer.map_tech_name_to_api("PostgreSQL") == "postgresql"
        assert scorer.map_tech_name_to_api("Redis") == "redis"

    def test_map_technology_name_handles_case_insensitive(self):
        """Should handle case-insensitive matching."""
        scorer = TechStackRiskScorer()
        
        assert scorer.map_tech_name_to_api("NODEJS") == "nodejs"
        assert scorer.map_tech_name_to_api("node.js") == "nodejs"
        assert scorer.map_tech_name_to_api("Node.JS") == "nodejs"

    def test_map_technology_name_returns_lowercase(self):
        """Should return lowercase for unknown techs (API convention)."""
        scorer = TechStackRiskScorer()
        
        result = scorer.map_tech_name_to_api("Unknown Framework")
        assert result == "unknown framework"


class TestBatchProcessing:
    """Test batch processing of tech-stack.json."""

    @patch('requests.get')
    def test_enrich_tech_stack_json(self, mock_get):
        """Should enrich all technologies in tech-stack.json."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"cycle": "8", "eol": "2026-11-10", "releaseDate": "2023-11-14"}
        ]
        mock_get.return_value = mock_response
        
        tech_stack = {
            "backend": [
                {"name": ".NET", "version": "8", "cve_count": 2}
            ],
            "frontend": [
                {"name": "Node.js", "version": "20", "cve_count": 0}
            ]
        }
        
        scorer = TechStackRiskScorer()
        enriched_stack = scorer.enrich_tech_stack(tech_stack)
        
        # Both technologies enriched
        assert "eol_date" in enriched_stack["backend"][0]
        assert "risk_score" in enriched_stack["backend"][0]
        assert "eol_date" in enriched_stack["frontend"][0]
        assert "risk_score" in enriched_stack["frontend"][0]

    def test_enrich_tech_stack_preserves_summary(self):
        """Should preserve summary section."""
        tech_stack = {
            "backend": [
                {"name": ".NET", "version": "8", "cve_count": 2}
            ],
            "summary": {
                "total_technologies": 1,
                "critical_cves": 0
            }
        }
        
        scorer = TechStackRiskScorer()
        enriched_stack = scorer.enrich_tech_stack(tech_stack)
        
        assert "summary" in enriched_stack
        assert enriched_stack["summary"]["total_technologies"] == 1


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_handles_null_version(self):
        """Should handle technologies with null version."""
        tech = {
            "name": "Unknown Framework",
            "version": None,
            "cve_count": 0
        }
        
        scorer = TechStackRiskScorer()
        enriched = scorer.enrich_technology(tech)
        
        assert enriched["eol_date"] is None
        assert "risk_score" in enriched

    def test_handles_missing_cve_count(self):
        """Should default cve_count to 0 if missing."""
        tech = {
            "name": ".NET",
            "version": "8"
        }
        
        scorer = TechStackRiskScorer()
        enriched = scorer.enrich_technology(tech)
        
        assert "risk_score" in enriched
        assert enriched["risk_score"] >= 0

    def test_risk_score_never_exceeds_100(self):
        """Risk score should be capped at 100."""
        scorer = TechStackRiskScorer()
        
        # Extreme values
        score = scorer.calculate_risk_score(
            months_since_update=1000,  # Very old
            months_to_eol=-1000,  # Long past EOL
            cve_count=1000  # Many CVEs
        )
        
        assert score == 100.0

    def test_risk_score_never_negative(self):
        """Risk score should never be negative."""
        scorer = TechStackRiskScorer()
        
        score = scorer.calculate_risk_score(
            months_since_update=0,
            months_to_eol=1000,  # Very safe
            cve_count=0
        )
        
        assert score >= 0.0
