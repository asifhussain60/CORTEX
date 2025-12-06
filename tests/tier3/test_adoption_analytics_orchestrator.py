"""
RED Phase Tests for AdoptionAnalyticsOrchestrator

Tests scheduled collection, team aggregation, batch processing, and error handling.
These tests MUST fail initially (ModuleNotFoundError for orchestrator).
"""

import pytest
from datetime import date, datetime, timedelta
from pathlib import Path
import tempfile
import sqlite3
from unittest.mock import Mock, patch, MagicMock

# Will fail initially - module doesn't exist yet
from src.tier3.orchestrators.adoption_analytics_orchestrator import (
    AdoptionAnalyticsOrchestrator,
    CollectionConfig,
    CollectionResult,
    AggregationResult,
    ScheduleType
)


class TestAdoptionAnalyticsOrchestrator:
    """Test suite for adoption analytics orchestration"""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        # Initialize schema
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create required tables (from migration_006)
        cursor.execute("""
            CREATE TABLE copilot_metrics (
                engineer_hash TEXT NOT NULL,
                metric_date TEXT NOT NULL,
                total_suggestions INTEGER DEFAULT 0,
                acceptances INTEGER DEFAULT 0,
                lines_suggested INTEGER DEFAULT 0,
                lines_accepted INTEGER DEFAULT 0,
                active_users INTEGER DEFAULT 1,
                language_breakdown TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (engineer_hash, metric_date)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE cortex_usage_metrics (
                engineer_hash TEXT NOT NULL,
                metric_date TEXT NOT NULL,
                intent_type TEXT NOT NULL,
                requests_count INTEGER DEFAULT 0,
                successful_count INTEGER DEFAULT 0,
                failed_count INTEGER DEFAULT 0,
                success_rate REAL DEFAULT 0.0,
                tokens_consumed INTEGER DEFAULT 0,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (engineer_hash, metric_date, intent_type)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE team_aggregations (
                team_id TEXT NOT NULL,
                aggregation_date TEXT NOT NULL,
                copilot_total_suggestions INTEGER DEFAULT 0,
                copilot_acceptance_rate REAL DEFAULT 0.0,
                cortex_total_requests INTEGER DEFAULT 0,
                cortex_success_rate REAL DEFAULT 0.0,
                team_size INTEGER DEFAULT 0,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (team_id, aggregation_date)
            )
        """)
        
        conn.commit()
        conn.close()
        
        yield db_path
        
        # Cleanup
        Path(db_path).unlink(missing_ok=True)
    
    def test_orchestrator_initialization(self, temp_db):
        """Test orchestrator can be instantiated with config"""
        config = CollectionConfig(
            db_path=temp_db,
            github_token="test_token",
            org_name="test_org"
        )
        
        orchestrator = AdoptionAnalyticsOrchestrator(config)
        assert orchestrator is not None
        assert orchestrator.config == config
        assert orchestrator.db_path == temp_db
    
    def test_collect_single_engineer_copilot(self, temp_db):
        """Test collecting Copilot metrics for single engineer"""
        config = CollectionConfig(
            db_path=temp_db,
            github_token="test_token",
            org_name="test_org"
        )
        orchestrator = AdoptionAnalyticsOrchestrator(config)
        
        # Mock GitHub API response
        with patch.object(orchestrator.copilot_collector, 'fetch_copilot_usage') as mock_fetch:
            mock_fetch.return_value = {
                'total_suggestions': 150,
                'total_acceptances': 120,
                'total_lines_suggested': 500,
                'total_lines_accepted': 400,
                'total_active_users': 1
            }
            
            result = orchestrator.collect_copilot_metrics(
                engineer_id="john.doe@example.com",
                target_date=date(2025, 12, 5)
            )
            
            assert result.success is True
            assert result.engineer_id == "john.doe@example.com"
            assert result.metrics_collected == 1
            assert result.errors == []
    
    def test_collect_batch_engineers(self, temp_db):
        """Test collecting metrics for multiple engineers in batch"""
        config = CollectionConfig(
            db_path=temp_db,
            github_token="test_token",
            org_name="test_org"
        )
        orchestrator = AdoptionAnalyticsOrchestrator(config)
        
        engineers = [
            "john.doe@example.com",
            "jane.smith@example.com",
            "bob.jones@example.com"
        ]
        
        with patch.object(orchestrator.copilot_collector, 'fetch_copilot_usage') as mock_fetch:
            mock_fetch.return_value = {'total_suggestions': 100, 'total_acceptances': 80}
            
            results = orchestrator.collect_batch(engineers, target_date=date(2025, 12, 5))
            
            assert len(results) == 3
            assert all(r.success for r in results)
            assert all(r.engineer_id in engineers for r in results)
    
    def test_collect_batch_with_failures(self, temp_db):
        """Test batch collection handles individual failures gracefully"""
        config = CollectionConfig(
            db_path=temp_db,
            github_token="test_token",
            org_name="test_org"
        )
        orchestrator = AdoptionAnalyticsOrchestrator(config)
        
        engineers = [
            "john.doe@example.com",
            "jane.smith@example.com",
            "invalid@example.com"
        ]
        
        def mock_fetch_side_effect(*args, **kwargs):
            if "invalid" in str(args) or "invalid" in str(kwargs):
                raise Exception("API error")
            return {'total_suggestions': 100}
        
        with patch.object(orchestrator.copilot_collector, 'fetch_copilot_usage') as mock_fetch:
            mock_fetch.side_effect = mock_fetch_side_effect
            
            results = orchestrator.collect_batch(engineers, target_date=date(2025, 12, 5))
            
            assert len(results) == 3
            successful = [r for r in results if r.success]
            failed = [r for r in results if not r.success]
            
            assert len(successful) == 2
            assert len(failed) == 1
            assert failed[0].engineer_id == "invalid@example.com"
    
    def test_aggregate_team_metrics(self, temp_db):
        """Test team-level aggregation from engineer metrics"""
        config = CollectionConfig(db_path=temp_db)
        orchestrator = AdoptionAnalyticsOrchestrator(config)
        
        # Insert sample engineer metrics
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        engineers = [
            ("hash1", "2025-12-05", 150, 120, 500, 400),
            ("hash2", "2025-12-05", 200, 160, 600, 480),
            ("hash3", "2025-12-05", 100, 80, 300, 240)
        ]
        
        for eng_hash, metric_date, suggestions, acceptances, lines_sugg, lines_acc in engineers:
            cursor.execute("""
                INSERT INTO copilot_metrics 
                (engineer_hash, metric_date, total_suggestions, acceptances, 
                 lines_suggested, lines_accepted)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (eng_hash, metric_date, suggestions, acceptances, lines_sugg, lines_acc))
        
        conn.commit()
        conn.close()
        
        # Aggregate for team
        result = orchestrator.aggregate_team_metrics(
            team_id="platform-team",
            team_members=["hash1", "hash2", "hash3"],
            aggregation_date=date(2025, 12, 5)
        )
        
        assert result.success is True
        assert result.team_id == "platform-team"
        assert result.total_suggestions == 450  # 150 + 200 + 100
        assert result.total_acceptances == 360  # 120 + 160 + 80
        assert result.acceptance_rate == 0.8  # 360/450
        assert result.team_size == 3
    
    def test_aggregate_team_with_cortex_metrics(self, temp_db):
        """Test team aggregation includes CORTEX usage metrics"""
        config = CollectionConfig(db_path=temp_db)
        orchestrator = AdoptionAnalyticsOrchestrator(config)
        
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        # Insert Copilot metrics
        cursor.execute("""
            INSERT INTO copilot_metrics 
            (engineer_hash, metric_date, total_suggestions, acceptances)
            VALUES ('hash1', '2025-12-05', 150, 120)
        """)
        
        # Insert CORTEX metrics
        cursor.execute("""
            INSERT INTO cortex_usage_metrics
            (engineer_hash, metric_date, intent_type, requests_count, successful_count)
            VALUES ('hash1', '2025-12-05', 'CODE_GEN', 50, 45)
        """)
        
        conn.commit()
        conn.close()
        
        result = orchestrator.aggregate_team_metrics(
            team_id="team1",
            team_members=["hash1"],
            aggregation_date=date(2025, 12, 5)
        )
        
        assert result.success is True
        assert result.cortex_total_requests == 50
        assert result.cortex_success_rate == 0.9  # 45/50
    
    def test_schedule_daily_collection(self, temp_db):
        """Test scheduling daily collection"""
        config = CollectionConfig(
            db_path=temp_db,
            schedule_type=ScheduleType.DAILY,
            collection_hour=2  # 2 AM
        )
        orchestrator = AdoptionAnalyticsOrchestrator(config)
        
        # Check schedule configuration
        assert orchestrator.schedule_type == ScheduleType.DAILY
        assert orchestrator.next_collection_time is not None
    
    def test_schedule_weekly_collection(self, temp_db):
        """Test scheduling weekly collection"""
        config = CollectionConfig(
            db_path=temp_db,
            schedule_type=ScheduleType.WEEKLY,
            collection_day=1,  # Monday
            collection_hour=3
        )
        orchestrator = AdoptionAnalyticsOrchestrator(config)
        
        assert orchestrator.schedule_type == ScheduleType.WEEKLY
        assert orchestrator.next_collection_time is not None
    
    def test_retry_failed_collection(self, temp_db):
        """Test retry logic for failed collections"""
        config = CollectionConfig(
            db_path=temp_db,
            github_token="test_token",
            max_retries=3
        )
        orchestrator = AdoptionAnalyticsOrchestrator(config)
        
        attempt_count = 0
        
        def mock_fetch_with_retry(*args, **kwargs):
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise Exception("Temporary error")
            return {'total_suggestions': 100}
        
        with patch.object(orchestrator.copilot_collector, 'fetch_copilot_usage') as mock_fetch:
            mock_fetch.side_effect = mock_fetch_with_retry
            
            result = orchestrator.collect_copilot_metrics(
                engineer_id="john@example.com",
                target_date=date(2025, 12, 5)
            )
            
            assert result.success is True
            assert attempt_count == 3  # Succeeded on 3rd attempt
    
    def test_retry_exhausted(self, temp_db):
        """Test retry logic when max retries exhausted"""
        config = CollectionConfig(
            db_path=temp_db,
            github_token="test_token",
            max_retries=2
        )
        orchestrator = AdoptionAnalyticsOrchestrator(config)
        
        with patch.object(orchestrator.copilot_collector, 'fetch_copilot_usage') as mock_fetch:
            mock_fetch.side_effect = Exception("Persistent error")
            
            result = orchestrator.collect_copilot_metrics(
                engineer_id="john@example.com",
                target_date=date(2025, 12, 5)
            )
            
            assert result.success is False
            assert "Persistent error" in result.error_message
            assert result.retry_count == 2
    
    def test_get_collection_status(self, temp_db):
        """Test retrieving collection status summary"""
        config = CollectionConfig(db_path=temp_db)
        orchestrator = AdoptionAnalyticsOrchestrator(config)
        
        # Simulate some collections
        with patch.object(orchestrator, 'collect_batch') as mock_collect:
            mock_collect.return_value = [
                CollectionResult(success=True, engineer_id="eng1", metrics_collected=1),
                CollectionResult(success=True, engineer_id="eng2", metrics_collected=1),
                CollectionResult(success=False, engineer_id="eng3", error_message="Error")
            ]
            
            orchestrator.collect_batch(["eng1", "eng2", "eng3"])
        
        status = orchestrator.get_collection_status()
        
        assert status['total_collections'] == 3
        assert status['successful_collections'] == 2
        assert status['failed_collections'] == 1
        assert status['success_rate'] == pytest.approx(0.667, rel=0.01)
    
    def test_error_logging(self, temp_db):
        """Test error logging for failed collections"""
        config = CollectionConfig(db_path=temp_db)
        orchestrator = AdoptionAnalyticsOrchestrator(config)
        
        with patch.object(orchestrator.copilot_collector, 'fetch_copilot_usage') as mock_fetch:
            mock_fetch.side_effect = Exception("API timeout")
            
            result = orchestrator.collect_copilot_metrics(
                engineer_id="john@example.com",
                target_date=date(2025, 12, 5)
            )
            
            assert result.success is False
            assert result.error_message is not None
            assert "API timeout" in result.error_message
            assert result.timestamp is not None
    
    def test_incremental_backfill(self, temp_db):
        """Test backfilling missing dates incrementally"""
        config = CollectionConfig(db_path=temp_db)
        orchestrator = AdoptionAnalyticsOrchestrator(config)
        
        # Define date range to backfill
        start_date = date(2025, 12, 1)
        end_date = date(2025, 12, 5)
        
        with patch.object(orchestrator.copilot_collector, 'fetch_copilot_usage') as mock_fetch:
            mock_fetch.return_value = {'total_suggestions': 100}
            
            results = orchestrator.backfill_metrics(
                engineer_id="john@example.com",
                start_date=start_date,
                end_date=end_date
            )
            
            assert len(results) == 5  # 5 days
            assert all(r.success for r in results)
            # Verify dates are sequential
            dates = [r.target_date for r in results]
            assert dates == [
                date(2025, 12, 1),
                date(2025, 12, 2),
                date(2025, 12, 3),
                date(2025, 12, 4),
                date(2025, 12, 5)
            ]


class TestCollectionConfig:
    """Test CollectionConfig data class"""
    
    def test_config_defaults(self):
        """Test default configuration values"""
        config = CollectionConfig(db_path="/tmp/test.db")
        
        assert config.db_path == "/tmp/test.db"
        assert config.github_token is None
        assert config.org_name is None
        assert config.max_retries == 3
        assert config.schedule_type == ScheduleType.MANUAL
    
    def test_config_custom_values(self):
        """Test custom configuration values"""
        config = CollectionConfig(
            db_path="/tmp/test.db",
            github_token="token123",
            org_name="myorg",
            max_retries=5,
            schedule_type=ScheduleType.DAILY,
            collection_hour=4
        )
        
        assert config.github_token == "token123"
        assert config.org_name == "myorg"
        assert config.max_retries == 5
        assert config.schedule_type == ScheduleType.DAILY
        assert config.collection_hour == 4


class TestCollectionResult:
    """Test CollectionResult data class"""
    
    def test_result_success(self):
        """Test successful collection result"""
        result = CollectionResult(
            success=True,
            engineer_id="john@example.com",
            metrics_collected=5,
            target_date=date(2025, 12, 5),
            timestamp=datetime.now()
        )
        
        assert result.success is True
        assert result.engineer_id == "john@example.com"
        assert result.metrics_collected == 5
        assert result.error_message is None
    
    def test_result_failure(self):
        """Test failed collection result"""
        result = CollectionResult(
            success=False,
            engineer_id="john@example.com",
            error_message="API error",
            retry_count=2,
            timestamp=datetime.now()
        )
        
        assert result.success is False
        assert result.error_message == "API error"
        assert result.retry_count == 2


class TestAggregationResult:
    """Test AggregationResult data class"""
    
    def test_aggregation_result_structure(self):
        """Test aggregation result has correct fields"""
        result = AggregationResult(
            success=True,
            team_id="platform-team",
            aggregation_date=date(2025, 12, 5),
            team_size=5,
            total_suggestions=1000,
            total_acceptances=800,
            acceptance_rate=0.8,
            cortex_total_requests=500,
            cortex_success_rate=0.9
        )
        
        assert result.success is True
        assert result.team_id == "platform-team"
        assert result.team_size == 5
        assert result.acceptance_rate == 0.8
        assert result.cortex_success_rate == 0.9
