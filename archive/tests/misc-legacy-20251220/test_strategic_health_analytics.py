"""
Unit tests for strategic health analytics recording and trend calculation.

Tests BrainAnalyticsCollector methods:
- record_strategic_health()
- get_strategic_health_history()
- get_strategic_health_trends()

Author: Asif Hussain
Copyright: ┬⌐ 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
import sqlite3
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from src.operations.modules.healthcheck.brain_analytics_collector import BrainAnalyticsCollector


@pytest.fixture
def temp_db():
    """Create a temporary Tier 3 database with schema."""
    with tempfile.TemporaryDirectory() as tmpdir:
        brain_path = Path(tmpdir)
        tier3_path = brain_path / "tier3"
        tier3_path.mkdir(parents=True)
        
        db_path = tier3_path / "development_context.db"
        
        # Create schema
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tier3_strategic_health (
                check_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL DEFAULT (datetime('now')),
                conversation_id TEXT,
                overall_status TEXT NOT NULL,
                features_checked INTEGER NOT NULL DEFAULT 5,
                features_healthy INTEGER NOT NULL DEFAULT 0,
                features_warning INTEGER NOT NULL DEFAULT 0,
                features_critical INTEGER NOT NULL DEFAULT 0,
                architecture_intelligence TEXT NOT NULL,
                rollback_system TEXT NOT NULL,
                swagger_dor TEXT NOT NULL,
                ux_enhancement TEXT NOT NULL,
                ado_agent TEXT NOT NULL,
                total_issues INTEGER NOT NULL DEFAULT 0,
                issue_summary TEXT,
                improvement_since_last INTEGER,
                days_since_last_check REAL,
                CHECK (overall_status IN ('healthy', 'warning', 'critical', 'error')),
                CHECK (architecture_intelligence IN ('healthy', 'warning', 'critical', 'error')),
                CHECK (rollback_system IN ('healthy', 'warning', 'critical', 'error')),
                CHECK (swagger_dor IN ('healthy', 'warning', 'critical', 'error')),
                CHECK (ux_enhancement IN ('healthy', 'warning', 'critical', 'error')),
                CHECK (ado_agent IN ('healthy', 'warning', 'critical', 'error'))
            )
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_strategic_health_timestamp 
            ON tier3_strategic_health(timestamp DESC)
        ''')
        conn.commit()
        conn.close()
        
        yield brain_path


@pytest.fixture
def analytics(temp_db):
    """Create BrainAnalyticsCollector with temp database."""
    return BrainAnalyticsCollector(brain_path=temp_db)


class TestRecordStrategicHealth:
    """Test strategic health recording functionality."""
    
    def test_record_all_healthy(self, analytics):
        """Test recording when all features are healthy."""
        arch = {'status': 'healthy', 'details': {}, 'issues': []}
        rollback = {'status': 'healthy', 'details': {}, 'issues': []}
        dor = {'status': 'healthy', 'details': {}, 'issues': []}
        ux = {'status': 'healthy', 'details': {}, 'issues': []}
        ado = {'status': 'healthy', 'details': {}, 'issues': []}
        
        check_id = analytics.record_strategic_health(
            arch, rollback, dor, ux, ado, conversation_id="test-conv-123"
        )
        
        assert check_id is not None
        assert isinstance(check_id, str)
        
        # Verify database record
        conn = sqlite3.connect(analytics.tier3_db)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tier3_strategic_health WHERE check_id = ?', (check_id,))
        row = cursor.fetchone()
        conn.close()
        
        assert row is not None
        # Check overall_status (index 3), features_healthy (index 5)
        assert row[3] == 'healthy'
        assert row[5] == 5  # features_healthy
        assert row[6] == 0  # features_warning
        assert row[7] == 0  # features_critical
    
    def test_record_with_warnings(self, analytics):
        """Test recording when some features have warnings."""
        arch = {'status': 'healthy', 'details': {}, 'issues': []}
        rollback = {'status': 'warning', 'details': {}, 'issues': ['Missing test file']}
        dor = {'status': 'healthy', 'details': {}, 'issues': []}
        ux = {'status': 'warning', 'details': {}, 'issues': ['Missing guide']}
        ado = {'status': 'healthy', 'details': {}, 'issues': []}
        
        check_id = analytics.record_strategic_health(arch, rollback, dor, ux, ado)
        
        # Verify status
        conn = sqlite3.connect(analytics.tier3_db)
        cursor = conn.cursor()
        cursor.execute('SELECT overall_status, features_healthy, features_warning FROM tier3_strategic_health WHERE check_id = ?', (check_id,))
        row = cursor.fetchone()
        conn.close()
        
        assert row[0] == 'warning'  # overall_status
        assert row[1] == 3  # features_healthy
        assert row[2] == 2  # features_warning
    
    def test_record_with_critical(self, analytics):
        """Test recording when some features are critical."""
        arch = {'status': 'critical', 'details': {}, 'issues': ['Missing guide', 'Missing dir']}
        rollback = {'status': 'healthy', 'details': {}, 'issues': []}
        dor = {'status': 'healthy', 'details': {}, 'issues': []}
        ux = {'status': 'healthy', 'details': {}, 'issues': []}
        ado = {'status': 'critical', 'details': {}, 'issues': ['Missing agent']}
        
        check_id = analytics.record_strategic_health(arch, rollback, dor, ux, ado)
        
        # Verify status
        conn = sqlite3.connect(analytics.tier3_db)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT overall_status, features_healthy, features_warning, features_critical, 
                   total_issues, issue_summary 
            FROM tier3_strategic_health WHERE check_id = ?
        ''', (check_id,))
        row = cursor.fetchone()
        conn.close()
        
        assert row[0] == 'critical'  # overall_status
        assert row[1] == 3  # features_healthy
        assert row[2] == 0  # features_warning
        assert row[3] == 2  # features_critical
        assert row[4] == 3  # total_issues
        assert 'Architecture Intelligence' in row[5]  # issue_summary contains feature name


class TestGetStrategicHealthHistory:
    """Test strategic health history retrieval."""
    
    def test_empty_history(self, analytics):
        """Test getting history when no records exist."""
        history = analytics.get_strategic_health_history(days=30)
        
        assert isinstance(history, list)
        assert len(history) == 0
    
    def test_history_with_records(self, analytics):
        """Test getting history with multiple records."""
        # Insert test records
        conn = sqlite3.connect(analytics.tier3_db)
        cursor = conn.cursor()
        
        for i in range(5):
            timestamp = (datetime.now() - timedelta(days=i)).isoformat()
            cursor.execute('''
                INSERT INTO tier3_strategic_health (
                    check_id, timestamp, overall_status,
                    features_healthy, features_warning, features_critical,
                    architecture_intelligence, rollback_system, swagger_dor,
                    ux_enhancement, ado_agent, total_issues
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                f'check-{i}', timestamp, 'healthy',
                5, 0, 0,
                'healthy', 'healthy', 'healthy', 'healthy', 'healthy', 0
            ))
        
        conn.commit()
        conn.close()
        
        # Get history
        history = analytics.get_strategic_health_history(days=30)
        
        assert len(history) == 5
        assert history[0]['check_id'] == 'check-0'  # Most recent first
        assert history[-1]['check_id'] == 'check-4'  # Oldest last
    
    def test_history_with_limit(self, analytics):
        """Test getting history with record limit."""
        # Insert 10 records
        conn = sqlite3.connect(analytics.tier3_db)
        cursor = conn.cursor()
        
        for i in range(10):
            timestamp = (datetime.now() - timedelta(days=i)).isoformat()
            cursor.execute('''
                INSERT INTO tier3_strategic_health (
                    check_id, timestamp, overall_status,
                    features_healthy, features_warning, features_critical,
                    architecture_intelligence, rollback_system, swagger_dor,
                    ux_enhancement, ado_agent, total_issues
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                f'check-{i}', timestamp, 'healthy',
                5, 0, 0,
                'healthy', 'healthy', 'healthy', 'healthy', 'healthy', 0
            ))
        
        conn.commit()
        conn.close()
        
        # Get limited history
        history = analytics.get_strategic_health_history(days=30, limit=3)
        
        assert len(history) == 3


class TestGetStrategicHealthTrends:
    """Test strategic health trend calculation."""
    
    def test_trends_no_data(self, analytics):
        """Test trends when no data available."""
        trends = analytics.get_strategic_health_trends(days=30)
        
        assert trends['status'] == 'no_data'
        assert 'message' in trends
    
    def test_trends_with_stable_features(self, analytics):
        """Test trends when all features remain stable."""
        # Insert records with no changes
        conn = sqlite3.connect(analytics.tier3_db)
        cursor = conn.cursor()
        
        for i in range(5):
            timestamp = (datetime.now() - timedelta(days=i*2)).isoformat()
            cursor.execute('''
                INSERT INTO tier3_strategic_health (
                    check_id, timestamp, overall_status,
                    features_healthy, features_warning, features_critical,
                    architecture_intelligence, rollback_system, swagger_dor,
                    ux_enhancement, ado_agent, total_issues
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                f'check-{i}', timestamp, 'healthy',
                5, 0, 0,
                'healthy', 'healthy', 'healthy', 'healthy', 'healthy', 0
            ))
        
        conn.commit()
        conn.close()
        
        # Get trends
        trends = analytics.get_strategic_health_trends(days=30)
        
        assert trends['status'] == 'success'
        assert trends['current_status'] == 'healthy'
        assert trends['total_checks'] == 5
        # All features should have 0 changes (stable)
        assert all(count == 0 for count in trends['feature_change_counts'].values())
    
    def test_trends_with_volatile_features(self, analytics):
        """Test trends when features change frequently."""
        # Insert records with changing statuses
        conn = sqlite3.connect(analytics.tier3_db)
        cursor = conn.cursor()
        
        statuses = ['healthy', 'warning', 'healthy', 'critical', 'warning']
        
        for i, status in enumerate(statuses):
            timestamp = (datetime.now() - timedelta(days=i*2)).isoformat()
            # Vary architecture_intelligence status, keep others stable
            cursor.execute('''
                INSERT INTO tier3_strategic_health (
                    check_id, timestamp, overall_status,
                    features_healthy, features_warning, features_critical,
                    architecture_intelligence, rollback_system, swagger_dor,
                    ux_enhancement, ado_agent, total_issues
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                f'check-{i}', timestamp, status,
                3, 1, 1,
                status, 'healthy', 'healthy', 'healthy', 'healthy', 0
            ))
        
        conn.commit()
        conn.close()
        
        # Get trends
        trends = analytics.get_strategic_health_trends(days=30)
        
        assert trends['status'] == 'success'
        assert trends['total_checks'] == 5
        # Architecture intelligence should be most volatile
        assert trends['most_volatile_feature'] == 'Architecture Intelligence'
        # Other features should be more stable
        assert trends['feature_change_counts']['architecture_intelligence'] > 0


class TestCalculateHealthTrends:
    """Test internal trend calculation helper."""
    
    def test_improvement_calculation(self, analytics):
        """Test calculating improvement since last check."""
        # Insert baseline check
        conn = sqlite3.connect(analytics.tier3_db)
        cursor = conn.cursor()
        
        baseline_time = (datetime.now() - timedelta(days=7)).isoformat()
        cursor.execute('''
            INSERT INTO tier3_strategic_health (
                check_id, timestamp, overall_status,
                features_healthy, features_warning, features_critical,
                architecture_intelligence, rollback_system, swagger_dor,
                ux_enhancement, ado_agent, total_issues
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            'baseline', baseline_time, 'warning',
            3, 2, 0,
            'warning', 'warning', 'healthy', 'healthy', 'healthy', 2
        ))
        
        conn.commit()
        conn.close()
        
        # Calculate trends with improved statuses
        current_statuses = {
            'architecture_intelligence': 'healthy',  # Improved
            'rollback_system': 'healthy',  # Improved
            'swagger_dor': 'healthy',
            'ux_enhancement': 'healthy',
            'ado_agent': 'healthy'
        }
        
        improvement, days_since = analytics._calculate_health_trends(current_statuses)
        
        assert improvement == 2  # Two features improved
        assert days_since >= 6.9  # ~7 days
        assert days_since <= 7.1
