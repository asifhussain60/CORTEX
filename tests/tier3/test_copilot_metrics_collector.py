"""
Tests for CopilotMetricsCollector

TDD Phase: RED - These tests will fail until implementation is complete

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from datetime import date, datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sqlite3
import json

# Module under test (will fail import until created)
from src.tier3.metrics.copilot_metrics import (
    CopilotMetricsCollector,
    CopilotMetric,
    CopilotLanguageBreakdown
)


class TestCopilotMetric:
    """Test CopilotMetric data class"""
    
    def test_copilot_metric_creation(self):
        """Test creating a CopilotMetric instance"""
        metric = CopilotMetric(
            metric_date=date(2025, 12, 5),
            engineer_hash="abc123",
            language="Python",
            suggestions_shown=100,
            suggestions_accepted=67,
            acceptance_rate=0.67,
            inline_completions=45,
            chat_interactions=12,
            avg_suggestion_latency_ms=125.5
        )
        
        assert metric.metric_date == date(2025, 12, 5)
        assert metric.engineer_hash == "abc123"
        assert metric.language == "Python"
        assert metric.suggestions_shown == 100
        assert metric.suggestions_accepted == 67
        assert metric.acceptance_rate == 0.67
        assert metric.inline_completions == 45
        assert metric.chat_interactions == 12
        assert metric.avg_suggestion_latency_ms == 125.5
    
    def test_copilot_metric_calculates_acceptance_rate(self):
        """Test automatic acceptance rate calculation"""
        metric = CopilotMetric(
            metric_date=date(2025, 12, 5),
            engineer_hash="abc123",
            language="Python",
            suggestions_shown=100,
            suggestions_accepted=60,
            acceptance_rate=None  # Should auto-calculate
        )
        
        # Should calculate 60/100 = 0.60
        assert metric.acceptance_rate == 0.60


class TestCopilotMetricsCollector:
    """Test CopilotMetricsCollector class"""
    
    @pytest.fixture
    def temp_db(self, tmp_path):
        """Create temporary test database"""
        db_path = tmp_path / "test_context.db"
        
        # Create schema
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS copilot_metrics (
                metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_date DATE NOT NULL,
                engineer_hash TEXT,
                language TEXT,
                suggestions_shown INTEGER DEFAULT 0,
                suggestions_accepted INTEGER DEFAULT 0,
                acceptance_rate REAL,
                inline_completions INTEGER DEFAULT 0,
                chat_interactions INTEGER DEFAULT 0,
                avg_suggestion_latency_ms REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(metric_date, engineer_hash, language)
            )
        """)
        conn.commit()
        conn.close()
        
        return db_path
    
    @pytest.fixture
    def collector(self, temp_db):
        """Create collector instance with test database"""
        return CopilotMetricsCollector(db_path=temp_db, github_token="test_token_123")
    
    def test_collector_initialization(self, temp_db):
        """Test collector initializes with valid parameters"""
        collector = CopilotMetricsCollector(
            db_path=temp_db,
            github_token="test_token_123"
        )
        
        assert collector.db_path == temp_db
        assert collector.github_token == "test_token_123"
        assert collector.org_name is None  # Optional parameter
    
    def test_collector_requires_github_token(self, temp_db):
        """Test collector raises error without GitHub token"""
        with pytest.raises(ValueError, match="GitHub token required"):
            CopilotMetricsCollector(db_path=temp_db, github_token=None)
    
    @patch('requests.get')
    def test_fetch_copilot_usage_from_github_api(self, mock_get, collector):
        """Test fetching Copilot usage data from GitHub API"""
        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "day": "2025-12-05",
            "total_suggestions_count": 1247,
            "total_acceptances_count": 843,
            "total_lines_suggested": 3891,
            "total_lines_accepted": 2654,
            "breakdown": [
                {
                    "language": "Python",
                    "editor": "vscode",
                    "suggestions_count": 523,
                    "acceptances_count": 367
                },
                {
                    "language": "JavaScript",
                    "editor": "vscode",
                    "suggestions_count": 412,
                    "acceptances_count": 289
                }
            ]
        }
        mock_get.return_value = mock_response
        
        # Fetch data
        usage_data = collector.fetch_copilot_usage(target_date=date(2025, 12, 5))
        
        # Verify API call
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert "api.github.com" in call_args[0][0]
        assert call_args[1]["headers"]["Authorization"] == "token test_token_123"
        
        # Verify parsed data
        assert usage_data["day"] == "2025-12-05"
        assert usage_data["total_suggestions_count"] == 1247
        assert usage_data["total_acceptances_count"] == 843
        assert len(usage_data["breakdown"]) == 2
    
    @patch('requests.get')
    def test_handle_github_api_rate_limiting(self, mock_get, collector):
        """Test handling of GitHub API rate limit (429 response)"""
        # Mock rate limit response
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.headers = {
            "X-RateLimit-Reset": str(int((datetime.now() + timedelta(minutes=5)).timestamp()))
        }
        mock_get.return_value = mock_response
        
        # Should raise rate limit exception
        with pytest.raises(Exception, match="Rate limit exceeded"):
            collector.fetch_copilot_usage(target_date=date(2025, 12, 5))
    
    @patch('requests.get')
    def test_retry_on_network_failure(self, mock_get, collector):
        """Test retry logic on network failures"""
        # First call fails, second succeeds
        mock_get.side_effect = [
            Exception("Network error"),
            Mock(status_code=200, json=lambda: {"day": "2025-12-05", "breakdown": []})
        ]
        
        # Should retry and succeed
        usage_data = collector.fetch_copilot_usage(
            target_date=date(2025, 12, 5),
            max_retries=2
        )
        
        assert usage_data["day"] == "2025-12-05"
        assert mock_get.call_count == 2
    
    def test_parse_language_breakdown(self, collector):
        """Test parsing language breakdown from API response"""
        api_data = {
            "breakdown": [
                {"language": "Python", "suggestions_count": 523, "acceptances_count": 367},
                {"language": "JavaScript", "suggestions_count": 412, "acceptances_count": 289},
                {"language": "TypeScript", "suggestions_count": 312, "acceptances_count": 187}
            ]
        }
        
        breakdowns = collector.parse_language_breakdown(api_data)
        
        assert len(breakdowns) == 3
        assert breakdowns[0].language == "Python"
        assert breakdowns[0].suggestions_count == 523
        assert breakdowns[0].acceptances_count == 367
        assert breakdowns[0].acceptance_rate == pytest.approx(0.702, rel=0.01)
    
    def test_save_copilot_metrics_to_database(self, collector):
        """Test saving metrics to database"""
        metric = CopilotMetric(
            metric_date=date(2025, 12, 5),
            engineer_hash="hash_abc123",
            language="Python",
            suggestions_shown=100,
            suggestions_accepted=67,
            acceptance_rate=0.67,
            inline_completions=45,
            chat_interactions=12,
            avg_suggestion_latency_ms=125.5
        )
        
        # Save metric
        collector.save_metrics([metric])
        
        # Verify saved to database
        conn = sqlite3.connect(collector.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM copilot_metrics 
            WHERE metric_date = ? AND engineer_hash = ? AND language = ?
        """, ("2025-12-05", "hash_abc123", "Python"))
        
        row = cursor.fetchone()
        conn.close()
        
        assert row is not None
        assert row[1] == "2025-12-05"  # metric_date
        assert row[2] == "hash_abc123"  # engineer_hash
        assert row[3] == "Python"  # language
        assert row[4] == 100  # suggestions_shown
        assert row[5] == 67  # suggestions_accepted
        assert row[6] == pytest.approx(0.67, rel=0.01)  # acceptance_rate
    
    def test_prevent_duplicate_metrics(self, collector):
        """Test UNIQUE constraint prevents duplicate metrics"""
        metric = CopilotMetric(
            metric_date=date(2025, 12, 5),
            engineer_hash="hash_abc123",
            language="Python",
            suggestions_shown=100,
            suggestions_accepted=67,
            acceptance_rate=0.67
        )
        
        # Save once
        collector.save_metrics([metric])
        
        # Save again with different values (should update)
        metric.suggestions_shown = 150
        metric.suggestions_accepted = 100
        metric.acceptance_rate = 0.667
        collector.save_metrics([metric])
        
        # Verify only one row exists with updated values
        conn = sqlite3.connect(collector.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*), suggestions_shown FROM copilot_metrics 
            WHERE metric_date = ? AND engineer_hash = ? AND language = ?
        """, ("2025-12-05", "hash_abc123", "Python"))
        
        count, suggestions_shown = cursor.fetchone()
        conn.close()
        
        assert count == 1
        assert suggestions_shown == 150
    
    def test_get_metrics_by_date_range(self, collector):
        """Test retrieving metrics for date range"""
        # Save metrics for multiple dates
        metrics = [
            CopilotMetric(
                metric_date=date(2025, 12, 3),
                engineer_hash="hash_abc",
                language="Python",
                suggestions_shown=100,
                suggestions_accepted=60,
                acceptance_rate=0.60
            ),
            CopilotMetric(
                metric_date=date(2025, 12, 4),
                engineer_hash="hash_abc",
                language="Python",
                suggestions_shown=120,
                suggestions_accepted=80,
                acceptance_rate=0.667
            ),
            CopilotMetric(
                metric_date=date(2025, 12, 5),
                engineer_hash="hash_abc",
                language="Python",
                suggestions_shown=150,
                suggestions_accepted=100,
                acceptance_rate=0.667
            )
        ]
        collector.save_metrics(metrics)
        
        # Retrieve last 2 days
        retrieved = collector.get_metrics(
            days=2,
            engineer_hash="hash_abc"
        )
        
        assert len(retrieved) == 2
        assert retrieved[0].metric_date == date(2025, 12, 5)
        assert retrieved[1].metric_date == date(2025, 12, 4)
    
    def test_calculate_aggregate_acceptance_rate(self, collector):
        """Test calculating aggregate acceptance rate across languages"""
        metrics = [
            CopilotMetric(
                metric_date=date(2025, 12, 5),
                engineer_hash="hash_abc",
                language="Python",
                suggestions_shown=100,
                suggestions_accepted=70,
                acceptance_rate=0.70
            ),
            CopilotMetric(
                metric_date=date(2025, 12, 5),
                engineer_hash="hash_abc",
                language="JavaScript",
                suggestions_shown=80,
                suggestions_accepted=48,
                acceptance_rate=0.60
            )
        ]
        collector.save_metrics(metrics)
        
        # Calculate aggregate
        aggregate_rate = collector.calculate_aggregate_acceptance_rate(
            engineer_hash="hash_abc",
            target_date=date(2025, 12, 5)
        )
        
        # (70 + 48) / (100 + 80) = 118 / 180 = 0.6556
        assert aggregate_rate == pytest.approx(0.6556, rel=0.01)
    
    def test_anonymize_engineer_id(self, collector):
        """Test SHA-256 hashing of engineer IDs for privacy"""
        engineer_email = "engineer@company.com"
        
        hashed_1 = collector.anonymize_engineer_id(engineer_email)
        hashed_2 = collector.anonymize_engineer_id(engineer_email)
        
        # Same input should produce same hash
        assert hashed_1 == hashed_2
        
        # Hash should be 64 characters (SHA-256 hex)
        assert len(hashed_1) == 64
        
        # Hash should not contain original email
        assert "engineer" not in hashed_1
        assert "@company.com" not in hashed_1
    
    def test_export_metrics_privacy_safe(self, collector):
        """Test exported metrics contain no PII"""
        metric = CopilotMetric(
            metric_date=date(2025, 12, 5),
            engineer_hash="hash_abc123",
            language="Python",
            suggestions_shown=100,
            suggestions_accepted=67,
            acceptance_rate=0.67
        )
        collector.save_metrics([metric])
        
        # Export to JSON
        exported = collector.export_metrics(
            engineer_hash="hash_abc123",
            start_date=date(2025, 12, 5),
            end_date=date(2025, 12, 5)
        )
        
        # Verify no PII in export
        exported_str = json.dumps(exported)
        assert "hash_abc123" in exported_str  # Hash is OK
        assert "@" not in exported_str  # No email addresses
        assert "file://" not in exported_str  # No file paths
        assert "def " not in exported_str  # No code snippets


class TestCopilotLanguageBreakdown:
    """Test CopilotLanguageBreakdown data class"""
    
    def test_language_breakdown_creation(self):
        """Test creating language breakdown instance"""
        breakdown = CopilotLanguageBreakdown(
            language="Python",
            suggestions_count=523,
            acceptances_count=367,
            acceptance_rate=0.702
        )
        
        assert breakdown.language == "Python"
        assert breakdown.suggestions_count == 523
        assert breakdown.acceptances_count == 367
        assert breakdown.acceptance_rate == pytest.approx(0.702, rel=0.01)
    
    def test_language_breakdown_auto_calculates_rate(self):
        """Test automatic acceptance rate calculation"""
        breakdown = CopilotLanguageBreakdown(
            language="JavaScript",
            suggestions_count=412,
            acceptances_count=289,
            acceptance_rate=None  # Should auto-calculate
        )
        
        # 289 / 412 = 0.7015
        assert breakdown.acceptance_rate == pytest.approx(0.7015, rel=0.01)


class TestIntegration:
    """Integration tests for full workflow"""
    
    @pytest.fixture
    def integration_collector(self, tmp_path):
        """Create collector with full database schema"""
        db_path = tmp_path / "integration_test.db"
        
        # Create full schema
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Copilot metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS copilot_metrics (
                metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_date DATE NOT NULL,
                engineer_hash TEXT,
                language TEXT,
                suggestions_shown INTEGER DEFAULT 0,
                suggestions_accepted INTEGER DEFAULT 0,
                acceptance_rate REAL,
                inline_completions INTEGER DEFAULT 0,
                chat_interactions INTEGER DEFAULT 0,
                avg_suggestion_latency_ms REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(metric_date, engineer_hash, language)
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_copilot_date ON copilot_metrics(metric_date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_copilot_engineer ON copilot_metrics(engineer_hash)")
        
        conn.commit()
        conn.close()
        
        return CopilotMetricsCollector(db_path=db_path, github_token="integration_test_token")
    
    @patch('requests.get')
    def test_full_collection_workflow(self, mock_get, integration_collector):
        """Test complete workflow: fetch → parse → save → retrieve"""
        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "day": "2025-12-05",
            "total_suggestions_count": 1000,
            "total_acceptances_count": 700,
            "breakdown": [
                {"language": "Python", "suggestions_count": 600, "acceptances_count": 450},
                {"language": "JavaScript", "suggestions_count": 400, "acceptances_count": 250}
            ]
        }
        mock_get.return_value = mock_response
        
        # 1. Fetch from API
        usage_data = integration_collector.fetch_copilot_usage(target_date=date(2025, 12, 5))
        
        # 2. Parse language breakdown
        breakdowns = integration_collector.parse_language_breakdown(usage_data)
        
        # 3. Convert to metrics with anonymized engineer ID
        engineer_hash = integration_collector.anonymize_engineer_id("test@example.com")
        metrics = [
            CopilotMetric(
                metric_date=date(2025, 12, 5),
                engineer_hash=engineer_hash,
                language=bd.language,
                suggestions_shown=bd.suggestions_count,
                suggestions_accepted=bd.acceptances_count,
                acceptance_rate=bd.acceptance_rate
            )
            for bd in breakdowns
        ]
        
        # 4. Save to database
        integration_collector.save_metrics(metrics)
        
        # 5. Retrieve and verify
        retrieved = integration_collector.get_metrics(days=1, engineer_hash=engineer_hash)
        
        assert len(retrieved) == 2
        assert sum(m.suggestions_shown for m in retrieved) == 1000
        assert sum(m.suggestions_accepted for m in retrieved) == 700
