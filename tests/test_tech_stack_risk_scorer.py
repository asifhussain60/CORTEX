"""
Tests for Technology Risk Scorer.
Tests API integration, caching, score calculations, recommendations.
"""

import pytest
import json
import os
import sys
import tempfile
import sqlite3
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

# Add src to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from collectors.tech_stack_risk_scorer import TechStackRiskScorer


@pytest.fixture
def temp_cache_db():
    """Create temporary cache database for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    yield db_path
    
    # Cleanup
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture
def scorer(temp_cache_db):
    """Create TechStackRiskScorer instance with temp cache."""
    return TechStackRiskScorer(cache_db_path=temp_cache_db)


class TestCacheDatabase:
    """Test SQLite caching functionality."""
    
    def test_cache_db_initialization(self, scorer):
        """Test cache database is created with correct schema."""
        conn = sqlite3.connect(scorer.cache_db_path)
        cursor = conn.cursor()
        
        # Check table exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='eol_cache'"
        )
        assert cursor.fetchone() is not None
        
        # Check schema
        cursor.execute("PRAGMA table_info(eol_cache)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        assert 'cache_key' in columns
        assert 'product' in columns
        assert 'version' in columns
        assert 'response_data' in columns
        assert 'cached_at' in columns
        
        conn.close()
    
    def test_cache_storage_and_retrieval(self, scorer):
        """Test caching stores and retrieves data correctly."""
        product = '.NET'
        version = '8.0'
        test_data = {
            'product': product,
            'version': version,
            'eol': '2026-11-10',
            'releaseDate': '2023-11-14'
        }
        
        # Cache data
        scorer._cache_response(product, version, test_data)
        
        # Retrieve from cache
        cached = scorer._get_cached_response(product, version)
        
        assert cached is not None
        assert cached['product'] == product
        assert cached['version'] == version
        assert cached['eol'] == '2026-11-10'
    
    def test_cache_expiration(self, scorer, temp_cache_db):
        """Test cache expires after 7 days."""
        product = '.NET'
        version = '6.0'
        test_data = {'product': product, 'version': version}
        
        # Cache data with old timestamp
        cache_key = scorer._get_cache_key(product, version)
        old_timestamp = (datetime.now() - timedelta(days=8)).isoformat()
        
        conn = sqlite3.connect(temp_cache_db)
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO eol_cache 
               (cache_key, product, version, response_data, cached_at)
               VALUES (?, ?, ?, ?, ?)''',
            (cache_key, product, version, json.dumps(test_data), old_timestamp)
        )
        conn.commit()
        conn.close()
        
        # Should return None (expired)
        cached = scorer._get_cached_response(product, version)
        assert cached is None


class TestAgeScoreCalculation:
    """Test age score calculation logic."""
    
    def test_age_score_new_release(self, scorer):
        """Test age score for recent release (< 1 year)."""
        # Release 6 months ago
        release_date = (datetime.now() - timedelta(days=180)).date().isoformat()
        score = scorer.calculate_age_score(release_date)
        
        # 0.5 years / 5 years * 100 = 10
        assert 5 <= score <= 15
    
    def test_age_score_old_release(self, scorer):
        """Test age score for old release (> 5 years)."""
        # Release 6 years ago
        release_date = (datetime.now() - timedelta(days=365*6)).date().isoformat()
        score = scorer.calculate_age_score(release_date)
        
        # Capped at 100
        assert score == 100
    
    def test_age_score_unknown_date(self, scorer):
        """Test age score for unknown release date."""
        score = scorer.calculate_age_score(None)
        assert score == 50.0  # Default moderate risk


class TestEOLScoreCalculation:
    """Test end-of-life score calculation logic."""
    
    def test_eol_score_already_eol(self, scorer):
        """Test EOL score for already end-of-life version."""
        # EOL 6 months ago
        eol_date = (datetime.now() - timedelta(days=180)).date().isoformat()
        score, months = scorer.calculate_eol_score(eol_date)
        
        assert score == 100  # Maximum risk
        assert months == 0
    
    def test_eol_score_critical_proximity(self, scorer):
        """Test EOL score for EOL within 6 months."""
        # EOL in 3 months
        eol_date = (datetime.now() + timedelta(days=90)).date().isoformat()
        score, months = scorer.calculate_eol_score(eol_date)
        
        assert 70 <= score <= 100  # High risk
        assert 2 <= months <= 3  # Allow rounding variance
    
    def test_eol_score_moderate_proximity(self, scorer):
        """Test EOL score for EOL within 1 year."""
        # EOL in 9 months
        eol_date = (datetime.now() + timedelta(days=270)).date().isoformat()
        score, months = scorer.calculate_eol_score(eol_date)
        
        assert 30 <= score <= 70  # Moderate risk
        assert 8 <= months <= 9  # Allow rounding variance
    
    def test_eol_score_distant_future(self, scorer):
        """Test EOL score for EOL far in future."""
        # EOL in 3 years
        eol_date = (datetime.now() + timedelta(days=365*3)).date().isoformat()
        score, months = scorer.calculate_eol_score(eol_date)
        
        assert score <= 30  # Low risk
        assert months >= 35  # Allow rounding variance
    
    def test_eol_score_boolean_true(self, scorer):
        """Test EOL score for boolean True (already EOL)."""
        score, months = scorer.calculate_eol_score(True)
        assert score == 100
        assert months == 0
    
    def test_eol_score_boolean_false(self, scorer):
        """Test EOL score for boolean False (not EOL)."""
        score, months = scorer.calculate_eol_score(False)
        assert score == 0
        assert months == 999


class TestCVEScoreCalculation:
    """Test CVE score calculation logic."""
    
    def test_cve_score_no_vulnerabilities(self, scorer):
        """Test CVE score with no known vulnerabilities."""
        score = scorer.calculate_cve_score(0)
        assert score == 0.0
    
    def test_cve_score_few_vulnerabilities(self, scorer):
        """Test CVE score with few vulnerabilities."""
        score = scorer.calculate_cve_score(3)
        assert 25 <= score <= 35  # 3/10 * 100 = 30
    
    def test_cve_score_many_vulnerabilities(self, scorer):
        """Test CVE score with many vulnerabilities."""
        score = scorer.calculate_cve_score(15)
        assert score == 100  # Capped at 100


class TestOverallRiskScore:
    """Test overall risk score formula."""
    
    def test_risk_score_formula(self, scorer):
        """Test weighted risk score calculation."""
        age_score = 50.0
        eol_score = 80.0
        cve_score = 30.0
        
        # Formula: age (30%) + eol (40%) + cve (30%)
        expected = (50 * 0.30) + (80 * 0.40) + (30 * 0.30)
        # = 15 + 32 + 9 = 56
        
        actual = scorer.calculate_risk_score(age_score, eol_score, cve_score)
        assert abs(actual - expected) < 0.01
    
    def test_risk_score_low_risk(self, scorer):
        """Test risk score for low-risk technology."""
        risk = scorer.calculate_risk_score(10.0, 5.0, 0.0)
        assert risk < 30
    
    def test_risk_score_high_risk(self, scorer):
        """Test risk score for high-risk technology."""
        risk = scorer.calculate_risk_score(100.0, 100.0, 100.0)
        assert risk == 100


class TestRecommendations:
    """Test recommendation generation."""
    
    def test_recommendation_critical(self, scorer):
        """Test CRITICAL recommendation for high risk + near EOL."""
        recommendation = scorer.get_recommendation(75.0, 3)
        assert 'CRITICAL' in recommendation
        assert 'immediately' in recommendation
    
    def test_recommendation_high(self, scorer):
        """Test HIGH recommendation for high risk."""
        recommendation = scorer.get_recommendation(80.0, 12)
        assert 'HIGH' in recommendation
    
    def test_recommendation_medium_near_eol(self, scorer):
        """Test MEDIUM recommendation for moderate risk + near EOL."""
        recommendation = scorer.get_recommendation(50.0, 10)
        assert 'MEDIUM' in recommendation
        assert '1 year' in recommendation
    
    def test_recommendation_low(self, scorer):
        """Test LOW recommendation for low risk."""
        recommendation = scorer.get_recommendation(20.0, 36)
        assert 'LOW' in recommendation
        assert 'monitoring' in recommendation.lower()


class TestProductNameNormalization:
    """Test product name normalization for API."""
    
    def test_normalize_dotnet_variants(self, scorer):
        """Test normalization of .NET variants."""
        assert scorer._normalize_product_name('.NET') == 'dotnet'
        assert scorer._normalize_product_name('.NET Core') == 'dotnet'
        assert scorer._normalize_product_name('dotnet') == 'dotnet'
    
    def test_normalize_dotnet_framework(self, scorer):
        """Test normalization of .NET Framework."""
        assert scorer._normalize_product_name('.NET Framework') == 'dotnetfx'
    
    def test_normalize_csharp(self, scorer):
        """Test normalization of C#."""
        assert scorer._normalize_product_name('C#') == 'csharp'
        assert scorer._normalize_product_name('csharp') == 'csharp'
    
    def test_normalize_visual_studio(self, scorer):
        """Test normalization of Visual Studio."""
        assert scorer._normalize_product_name('Visual Studio') == 'visual-studio'
        assert scorer._normalize_product_name('VS') == 'visual-studio'


class TestVersionMatching:
    """Test version matching logic."""
    
    def test_version_match_exact(self, scorer):
        """Test exact version match."""
        assert scorer._version_matches('8.0', '8.0') is True
        assert scorer._version_matches('6.0.1', '6.0.0') is True  # Major.minor match
    
    def test_version_no_match(self, scorer):
        """Test version mismatch."""
        assert scorer._version_matches('8.0', '7.0') is False
        assert scorer._version_matches('6.1', '6.0') is False


class TestAPIIntegration:
    """Test EOL API integration with mocking."""
    
    @patch('requests.get')
    def test_api_query_successful(self, mock_get, scorer):
        """Test successful API query."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                'cycle': '8.0',
                'eol': '2026-11-10',
                'support': '2026-11-10',
                'releaseDate': '2023-11-14',
                'latest': '8.0.1',
                'lts': True
            }
        ]
        mock_get.return_value = mock_response
        
        result = scorer._query_eol_api('.NET', '8.0')
        
        assert result is not None
        assert result['version'] == '8.0'
        assert result['eol'] == '2026-11-10'
        assert result['lts'] is True
    
    @patch('requests.get')
    def test_api_query_failure(self, mock_get, scorer):
        """Test API query failure handling."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        result = scorer._query_eol_api('UnknownProduct', '1.0')
        assert result is None
    
    @patch('requests.get')
    def test_api_uses_cache(self, mock_get, scorer):
        """Test API uses cached data when available."""
        # Pre-cache data
        cached_data = {'product': '.NET', 'version': '8.0', 'eol': '2026-11-10'}
        scorer._cache_response('.NET', '8.0', cached_data)
        
        # Query should use cache, not call API
        result = scorer._query_eol_api('.NET', '8.0')
        
        assert result == cached_data
        mock_get.assert_not_called()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
