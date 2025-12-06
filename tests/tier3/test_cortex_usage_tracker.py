"""
Tests for CortexUsageTracker

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
from src.tier3.metrics.cortex_usage_tracker import (
    CortexUsageTracker,
    CortexUsageMetric,
    IntentType
)


class TestCortexUsageMetric:
    """Test CortexUsageMetric data class"""
    
    def test_cortex_usage_metric_creation(self):
        """Test creating a CortexUsageMetric instance"""
        metric = CortexUsageMetric(
            metric_date=date(2025, 12, 5),
            engineer_hash="abc123",
            intent_type="PLAN",
            requests_count=15,
            successful_count=14,
            failed_count=1,
            avg_response_time_seconds=2.5,
            tokens_consumed=8234
        )
        
        assert metric.metric_date == date(2025, 12, 5)
        assert metric.engineer_hash == "abc123"
        assert metric.intent_type == "PLAN"
        assert metric.requests_count == 15
        assert metric.successful_count == 14
        assert metric.failed_count == 1
        assert metric.avg_response_time_seconds == 2.5
        assert metric.tokens_consumed == 8234
    
    def test_cortex_usage_metric_calculates_success_rate(self):
        """Test automatic success rate calculation"""
        metric = CortexUsageMetric(
            metric_date=date(2025, 12, 5),
            engineer_hash="abc123",
            intent_type="EXECUTE",
            requests_count=100,
            successful_count=94,
            failed_count=6
        )
        
        # Should calculate 94/100 = 0.94
        assert metric.success_rate == pytest.approx(0.94, rel=0.01)


class TestCortexUsageTracker:
    """Test CortexUsageTracker class"""
    
    @pytest.fixture
    def temp_db(self, tmp_path):
        """Create temporary test database"""
        db_path = tmp_path / "test_context.db"
        
        # Create schema
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cortex_usage_metrics (
                metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_date DATE NOT NULL,
                engineer_hash TEXT,
                intent_type TEXT,
                requests_count INTEGER DEFAULT 0,
                successful_count INTEGER DEFAULT 0,
                failed_count INTEGER DEFAULT 0,
                avg_response_time_seconds REAL,
                tokens_consumed INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(metric_date, engineer_hash, intent_type)
            )
        """)
        conn.commit()
        conn.close()
        
        return db_path
    
    @pytest.fixture
    def working_memory_db(self, tmp_path):
        """Create temporary Tier 1 working memory database"""
        wm_db_path = tmp_path / "working_memory.db"
        
        conn = sqlite3.connect(wm_db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                conversation_id TEXT PRIMARY KEY,
                timestamp TIMESTAMP,
                user_message TEXT,
                assistant_response TEXT,
                intent_type TEXT,
                success BOOLEAN,
                response_time_seconds REAL,
                tokens_used INTEGER,
                metadata TEXT
            )
        """)
        
        # Insert sample conversation data
        sample_conversations = [
            ("conv1", "2025-12-05 10:00:00", "plan authentication", "Planning...", "PLAN", 1, 2.5, 1200, "{}"),
            ("conv2", "2025-12-05 10:30:00", "execute task 1.1", "Executing...", "EXECUTE", 1, 3.2, 2400, "{}"),
            ("conv3", "2025-12-05 11:00:00", "run tests", "Running tests...", "TEST", 1, 1.8, 800, "{}"),
            ("conv4", "2025-12-05 11:30:00", "plan payment integration", "Planning...", "PLAN", 1, 2.8, 1400, "{}"),
            ("conv5", "2025-12-05 12:00:00", "validate schema", "Validating...", "VALIDATE", 0, 2.1, 900, "{}"),
        ]
        
        for conv in sample_conversations:
            cursor.execute("""
                INSERT INTO conversations VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, conv)
        
        conn.commit()
        conn.close()
        
        return wm_db_path
    
    @pytest.fixture
    def tracker(self, temp_db, working_memory_db):
        """Create tracker instance with test databases"""
        return CortexUsageTracker(
            tier3_db_path=temp_db,
            working_memory_db_path=working_memory_db
        )
    
    def test_tracker_initialization(self, temp_db, working_memory_db):
        """Test tracker initializes with valid parameters"""
        tracker = CortexUsageTracker(
            tier3_db_path=temp_db,
            working_memory_db_path=working_memory_db
        )
        
        assert tracker.tier3_db_path == temp_db
        assert tracker.working_memory_db_path == working_memory_db
    
    def test_extract_metrics_from_working_memory(self, tracker):
        """Test extracting CORTEX usage from Tier 1 working memory"""
        metrics = tracker.extract_from_working_memory(
            target_date=date(2025, 12, 5),
            engineer_hash="test_hash"
        )
        
        # Should extract 5 conversations from sample data
        assert len(metrics) > 0
        
        # Verify metrics by intent type
        plan_metrics = [m for m in metrics if m.intent_type == "PLAN"]
        assert len(plan_metrics) > 0
        
        execute_metrics = [m for m in metrics if m.intent_type == "EXECUTE"]
        assert len(execute_metrics) > 0
    
    def test_aggregate_by_intent_type(self, tracker):
        """Test aggregating metrics by intent type"""
        # Insert raw conversation data
        raw_conversations = [
            {"intent": "PLAN", "success": True, "response_time": 2.5, "tokens": 1200},
            {"intent": "PLAN", "success": True, "response_time": 2.8, "tokens": 1400},
            {"intent": "PLAN", "success": False, "response_time": 3.0, "tokens": 1500},
            {"intent": "EXECUTE", "success": True, "response_time": 3.2, "tokens": 2400},
        ]
        
        aggregated = tracker.aggregate_by_intent(
            raw_conversations,
            target_date=date(2025, 12, 5),
            engineer_hash="test_hash"
        )
        
        # Should have 2 aggregated metrics (PLAN and EXECUTE)
        assert len(aggregated) == 2
        
        # Verify PLAN aggregation
        plan_metric = next(m for m in aggregated if m.intent_type == "PLAN")
        assert plan_metric.requests_count == 3
        assert plan_metric.successful_count == 2
        assert plan_metric.failed_count == 1
        assert plan_metric.tokens_consumed == 4100  # 1200 + 1400 + 1500
        assert plan_metric.avg_response_time_seconds == pytest.approx(2.77, rel=0.01)  # (2.5 + 2.8 + 3.0) / 3
    
    def test_calculate_success_rate(self, tracker):
        """Test success rate calculation"""
        metric = CortexUsageMetric(
            metric_date=date(2025, 12, 5),
            engineer_hash="test_hash",
            intent_type="PLAN",
            requests_count=50,
            successful_count=47,
            failed_count=3
        )
        
        success_rate = tracker.calculate_success_rate(metric)
        assert success_rate == pytest.approx(0.94, rel=0.01)
    
    def test_save_cortex_usage_metrics(self, tracker):
        """Test saving usage metrics to Tier 3 database"""
        metric = CortexUsageMetric(
            metric_date=date(2025, 12, 5),
            engineer_hash="hash_abc123",
            intent_type="PLAN",
            requests_count=15,
            successful_count=14,
            failed_count=1,
            avg_response_time_seconds=2.5,
            tokens_consumed=8234
        )
        
        # Save metric
        tracker.save_metrics([metric])
        
        # Verify saved to database
        conn = sqlite3.connect(tracker.tier3_db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM cortex_usage_metrics 
            WHERE metric_date = ? AND engineer_hash = ? AND intent_type = ?
        """, ("2025-12-05", "hash_abc123", "PLAN"))
        
        row = cursor.fetchone()
        conn.close()
        
        assert row is not None
        assert row[1] == "2025-12-05"  # metric_date
        assert row[2] == "hash_abc123"  # engineer_hash
        assert row[3] == "PLAN"  # intent_type
        assert row[4] == 15  # requests_count
        assert row[5] == 14  # successful_count
        assert row[6] == 1  # failed_count
        assert row[7] == pytest.approx(2.5, rel=0.01)  # avg_response_time
        assert row[8] == 8234  # tokens_consumed
    
    def test_prevent_duplicate_metrics(self, tracker):
        """Test UNIQUE constraint prevents duplicate metrics"""
        metric = CortexUsageMetric(
            metric_date=date(2025, 12, 5),
            engineer_hash="hash_abc123",
            intent_type="EXECUTE",
            requests_count=10,
            successful_count=9,
            failed_count=1
        )
        
        # Save once
        tracker.save_metrics([metric])
        
        # Save again with different values (should update)
        metric.requests_count = 15
        metric.successful_count = 14
        tracker.save_metrics([metric])
        
        # Verify only one row exists with updated values
        conn = sqlite3.connect(tracker.tier3_db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*), requests_count FROM cortex_usage_metrics 
            WHERE metric_date = ? AND engineer_hash = ? AND intent_type = ?
        """, ("2025-12-05", "hash_abc123", "EXECUTE"))
        
        count, requests_count = cursor.fetchone()
        conn.close()
        
        assert count == 1
        assert requests_count == 15
    
    def test_get_metrics_by_date_range(self, tracker):
        """Test retrieving metrics for date range"""
        # Save metrics for multiple dates
        metrics = [
            CortexUsageMetric(
                metric_date=date(2025, 12, 3),
                engineer_hash="hash_abc",
                intent_type="PLAN",
                requests_count=10,
                successful_count=9,
                failed_count=1
            ),
            CortexUsageMetric(
                metric_date=date(2025, 12, 4),
                engineer_hash="hash_abc",
                intent_type="PLAN",
                requests_count=12,
                successful_count=11,
                failed_count=1
            ),
            CortexUsageMetric(
                metric_date=date(2025, 12, 5),
                engineer_hash="hash_abc",
                intent_type="PLAN",
                requests_count=15,
                successful_count=14,
                failed_count=1
            )
        ]
        tracker.save_metrics(metrics)
        
        # Retrieve last 2 days
        retrieved = tracker.get_metrics(
            days=2,
            engineer_hash="hash_abc"
        )
        
        assert len(retrieved) == 2
        assert retrieved[0].metric_date == date(2025, 12, 5)
        assert retrieved[1].metric_date == date(2025, 12, 4)
    
    def test_filter_by_intent_type(self, tracker):
        """Test filtering metrics by intent type"""
        metrics = [
            CortexUsageMetric(
                metric_date=date(2025, 12, 5),
                engineer_hash="hash_abc",
                intent_type="PLAN",
                requests_count=15,
                successful_count=14,
                failed_count=1
            ),
            CortexUsageMetric(
                metric_date=date(2025, 12, 5),
                engineer_hash="hash_abc",
                intent_type="EXECUTE",
                requests_count=20,
                successful_count=19,
                failed_count=1
            ),
            CortexUsageMetric(
                metric_date=date(2025, 12, 5),
                engineer_hash="hash_abc",
                intent_type="TEST",
                requests_count=8,
                successful_count=8,
                failed_count=0
            )
        ]
        tracker.save_metrics(metrics)
        
        # Get only PLAN metrics
        plan_metrics = tracker.get_metrics(
            days=1,
            engineer_hash="hash_abc",
            intent_type="PLAN"
        )
        
        assert len(plan_metrics) == 1
        assert plan_metrics[0].intent_type == "PLAN"
        assert plan_metrics[0].requests_count == 15
    
    def test_calculate_total_tokens_consumed(self, tracker):
        """Test calculating total tokens across all intents"""
        metrics = [
            CortexUsageMetric(
                metric_date=date(2025, 12, 5),
                engineer_hash="hash_abc",
                intent_type="PLAN",
                requests_count=10,
                successful_count=10,
                failed_count=0,
                tokens_consumed=5000
            ),
            CortexUsageMetric(
                metric_date=date(2025, 12, 5),
                engineer_hash="hash_abc",
                intent_type="EXECUTE",
                requests_count=15,
                successful_count=15,
                failed_count=0,
                tokens_consumed=8000
            )
        ]
        tracker.save_metrics(metrics)
        
        total_tokens = tracker.calculate_total_tokens(
            engineer_hash="hash_abc",
            target_date=date(2025, 12, 5)
        )
        
        assert total_tokens == 13000  # 5000 + 8000
    
    def test_get_most_used_intent(self, tracker):
        """Test identifying most frequently used intent type"""
        metrics = [
            CortexUsageMetric(
                metric_date=date(2025, 12, 5),
                engineer_hash="hash_abc",
                intent_type="PLAN",
                requests_count=25,
                successful_count=24,
                failed_count=1
            ),
            CortexUsageMetric(
                metric_date=date(2025, 12, 5),
                engineer_hash="hash_abc",
                intent_type="EXECUTE",
                requests_count=15,
                successful_count=14,
                failed_count=1
            ),
            CortexUsageMetric(
                metric_date=date(2025, 12, 5),
                engineer_hash="hash_abc",
                intent_type="TEST",
                requests_count=10,
                successful_count=10,
                failed_count=0
            )
        ]
        tracker.save_metrics(metrics)
        
        most_used = tracker.get_most_used_intent(
            engineer_hash="hash_abc",
            days=1
        )
        
        assert most_used == "PLAN"
    
    def test_calculate_average_response_time(self, tracker):
        """Test calculating average response time across intents"""
        metrics = [
            CortexUsageMetric(
                metric_date=date(2025, 12, 5),
                engineer_hash="hash_abc",
                intent_type="PLAN",
                requests_count=10,
                successful_count=10,
                failed_count=0,
                avg_response_time_seconds=2.5
            ),
            CortexUsageMetric(
                metric_date=date(2025, 12, 5),
                engineer_hash="hash_abc",
                intent_type="EXECUTE",
                requests_count=10,
                successful_count=10,
                failed_count=0,
                avg_response_time_seconds=3.5
            )
        ]
        tracker.save_metrics(metrics)
        
        avg_time = tracker.calculate_average_response_time(
            engineer_hash="hash_abc",
            target_date=date(2025, 12, 5)
        )
        
        # Weighted average: (2.5 * 10 + 3.5 * 10) / 20 = 3.0
        assert avg_time == pytest.approx(3.0, rel=0.01)
    
    def test_export_usage_summary(self, tracker):
        """Test exporting usage summary in privacy-safe format"""
        metrics = [
            CortexUsageMetric(
                metric_date=date(2025, 12, 5),
                engineer_hash="hash_abc123",
                intent_type="PLAN",
                requests_count=25,
                successful_count=24,
                failed_count=1,
                avg_response_time_seconds=2.5,
                tokens_consumed=12000
            ),
            CortexUsageMetric(
                metric_date=date(2025, 12, 5),
                engineer_hash="hash_abc123",
                intent_type="EXECUTE",
                requests_count=15,
                successful_count=14,
                failed_count=1,
                avg_response_time_seconds=3.2,
                tokens_consumed=8000
            )
        ]
        tracker.save_metrics(metrics)
        
        # Export summary
        summary = tracker.export_usage_summary(
            engineer_hash="hash_abc123",
            start_date=date(2025, 12, 5),
            end_date=date(2025, 12, 5)
        )
        
        # Verify summary structure
        assert summary["engineer_id"] == "hash_abc123"
        assert "reporting_period" in summary
        assert summary["total_requests"] == 40  # 25 + 15
        assert summary["total_successful"] == 38  # 24 + 14
        assert summary["overall_success_rate"] == pytest.approx(0.95, rel=0.01)  # 38/40
        assert summary["total_tokens_consumed"] == 20000  # 12000 + 8000
        
        # Verify intent breakdown
        assert "by_intent" in summary
        assert len(summary["by_intent"]) == 2


class TestIntegration:
    """Integration tests for full workflow"""
    
    @pytest.fixture
    def integration_setup(self, tmp_path):
        """Create full integration test environment"""
        tier3_db = tmp_path / "tier3.db"
        wm_db = tmp_path / "working_memory.db"
        
        # Create Tier 3 schema
        conn = sqlite3.connect(tier3_db)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cortex_usage_metrics (
                metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_date DATE NOT NULL,
                engineer_hash TEXT,
                intent_type TEXT,
                requests_count INTEGER DEFAULT 0,
                successful_count INTEGER DEFAULT 0,
                failed_count INTEGER DEFAULT 0,
                avg_response_time_seconds REAL,
                tokens_consumed INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(metric_date, engineer_hash, intent_type)
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_cortex_usage_date ON cortex_usage_metrics(metric_date)")
        conn.commit()
        conn.close()
        
        # Create working memory with realistic data
        conn = sqlite3.connect(wm_db)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                conversation_id TEXT PRIMARY KEY,
                timestamp TIMESTAMP,
                user_message TEXT,
                assistant_response TEXT,
                intent_type TEXT,
                success BOOLEAN,
                response_time_seconds REAL,
                tokens_used INTEGER,
                metadata TEXT
            )
        """)
        
        # Insert 30 days of conversation data
        import random
        intent_types = ["PLAN", "EXECUTE", "TEST", "VALIDATE", "GOVERN", "ASK"]
        base_date = datetime(2025, 11, 5)
        
        for day in range(30):
            for i in range(random.randint(5, 15)):  # 5-15 requests per day
                intent = random.choice(intent_types)
                success = random.random() > 0.1  # 90% success rate
                response_time = random.uniform(1.0, 5.0)
                tokens = random.randint(500, 3000)
                
                cursor.execute("""
                    INSERT INTO conversations VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    f"conv_{day}_{i}",
                    (base_date + timedelta(days=day, hours=i)).isoformat(),
                    "User request",
                    "Assistant response",
                    intent,
                    success,
                    response_time,
                    tokens,
                    "{}"
                ))
        
        conn.commit()
        conn.close()
        
        return {
            "tier3_db": tier3_db,
            "wm_db": wm_db,
            "tracker": CortexUsageTracker(tier3_db, wm_db)
        }
    
    def test_full_collection_workflow(self, integration_setup):
        """Test complete workflow: extract → aggregate → save → retrieve"""
        tracker = integration_setup["tracker"]
        
        # 1. Extract from working memory for last 30 days (data spans Nov 5 - Dec 4)
        metrics = tracker.extract_from_working_memory(
            target_date=date(2025, 12, 4),  # Use Dec 4 since data ends there
            engineer_hash="integration_test_hash",
            days_window=30  # Need to specify window
        )
        
        # 2. Should have metrics
        assert len(metrics) > 0
        
        # 3. Save to Tier 3
        tracker.save_metrics(metrics)
        
        # 4. Retrieve and verify
        retrieved = tracker.get_metrics(days=30, engineer_hash="integration_test_hash")
        
        assert len(retrieved) > 0
        
        # 5. Calculate summary statistics
        summary = tracker.export_usage_summary(
            engineer_hash="integration_test_hash",
            start_date=date(2025, 11, 5),
            end_date=date(2025, 12, 5)
        )
        
        assert summary["total_requests"] > 0
        assert 0.0 <= summary["overall_success_rate"] <= 1.0
        assert summary["total_tokens_consumed"] > 0
