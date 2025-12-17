"""
Adoption Analytics Orchestrator

High-level orchestration for collecting, aggregating, and scheduling adoption metrics.
Coordinates CopilotMetricsCollector, CortexUsageTracker, and team aggregations.

Author: Asif Hussain
Version: 3.0.0
"""

import sqlite3
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Optional
from enum import Enum
from pathlib import Path

from src.tier3.metrics.copilot_metrics import CopilotMetricsCollector, CopilotMetric
from src.tier3.metrics.cortex_usage_tracker import CortexUsageTracker


class ScheduleType(Enum):
    """Collection schedule types"""
    MANUAL = "manual"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


@dataclass
class CollectionConfig:
    """Configuration for adoption analytics collection"""
    db_path: str
    working_memory_db_path: Optional[str] = None  # Path to Tier 1 working_memory.db
    github_token: Optional[str] = None
    org_name: Optional[str] = None
    max_retries: int = 3
    schedule_type: ScheduleType = ScheduleType.MANUAL
    collection_hour: int = 2  # Hour of day (24-hour format)
    collection_day: int = 1  # Day of week for weekly (1=Monday, 7=Sunday)
    backoff_multiplier: float = 2.0  # Exponential backoff multiplier


@dataclass
class CollectionResult:
    """Result of a single collection operation"""
    success: bool
    engineer_id: str
    metrics_collected: int = 0
    target_date: Optional[date] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    timestamp: Optional[datetime] = None


@dataclass
class AggregationResult:
    """Result of team aggregation operation"""
    success: bool
    team_id: str
    aggregation_date: date
    team_size: int = 0
    total_suggestions: int = 0
    total_acceptances: int = 0
    acceptance_rate: float = 0.0
    cortex_total_requests: int = 0
    cortex_success_rate: float = 0.0
    error_message: Optional[str] = None


class AdoptionAnalyticsOrchestrator:
    """
    Orchestrates adoption analytics collection and aggregation.
    
    Features:
    - Single engineer collection (Copilot + CORTEX)
    - Batch collection with parallel processing
    - Team-level aggregation
    - Scheduled collection (daily, weekly, monthly)
    - Retry logic with exponential backoff
    - Error handling and logging
    - Incremental backfilling
    
    Usage:
        config = CollectionConfig(
            db_path="/path/to/db",
            github_token="token",
            org_name="myorg",
            schedule_type=ScheduleType.DAILY
        )
        
        orchestrator = AdoptionAnalyticsOrchestrator(config)
        
        # Collect for single engineer
        result = orchestrator.collect_copilot_metrics(
            engineer_id="john@example.com",
            target_date=date.today()
        )
        
        # Batch collection
        results = orchestrator.collect_batch([
            "john@example.com",
            "jane@example.com"
        ])
        
        # Team aggregation
        agg_result = orchestrator.aggregate_team_metrics(
            team_id="platform-team",
            team_members=["hash1", "hash2", "hash3"],
            aggregation_date=date.today()
        )
    """
    
    def __init__(self, config: CollectionConfig):
        """
        Initialize orchestrator with configuration.
        
        Args:
            config: CollectionConfig with database path and settings
        """
        self.config = config
        self.db_path = config.db_path
        self.schedule_type = config.schedule_type
        self.max_retries = config.max_retries
        
        # Initialize collectors
        self.copilot_collector = CopilotMetricsCollector(
            db_path=config.db_path,
            github_token=config.github_token,
            org_name=config.org_name
        )
        
        # Initialize CORTEX tracker if working memory path provided
        if config.working_memory_db_path:
            self.cortex_tracker = CortexUsageTracker(
                tier3_db_path=Path(config.db_path),
                working_memory_db_path=Path(config.working_memory_db_path)
            )
        else:
            self.cortex_tracker = None
        
        # Calculate next collection time if scheduled
        self.next_collection_time = self._calculate_next_collection_time()
        
        # Collection history for status tracking
        self._collection_history: List[CollectionResult] = []
    
    def collect_copilot_metrics(
        self,
        engineer_id: str,
        target_date: Optional[date] = None
    ) -> CollectionResult:
        """
        Collect Copilot metrics for single engineer with retry logic.
        
        Args:
            engineer_id: Engineer email/identifier
            target_date: Target date for metrics (defaults to today)
            
        Returns:
            CollectionResult with success status and metrics count
        """
        target_date = target_date or date.today()
        retry_count = 0
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                # Fetch metrics from GitHub API
                usage_data = self.copilot_collector.fetch_copilot_usage(
                    target_date=target_date
                )
                
                # Parse and create CopilotMetric objects
                engineer_hash = self.copilot_collector.anonymize_engineer_id(engineer_id)
                language_breakdowns = self.copilot_collector.parse_language_breakdown(usage_data)
                
                metrics = []
                for breakdown in language_breakdowns:
                    metric = CopilotMetric(
                        metric_date=target_date,
                        engineer_hash=engineer_hash,
                        language=breakdown.language,
                        suggestions_shown=breakdown.suggestions_count,
                        suggestions_accepted=breakdown.acceptances_count,
                        acceptance_rate=(
                            breakdown.acceptances_count / breakdown.suggestions_count
                            if breakdown.suggestions_count > 0
                            else 0.0
                        ),
                        inline_completions=0,  # Not in API response
                        chat_interactions=0,    # Not in API response
                        avg_suggestion_latency_ms=0.0,  # Not in API response
                        created_at=datetime.now()
                    )
                    metrics.append(metric)
                
                # Save to database
                self.copilot_collector.save_metrics(metrics)
                
                result = CollectionResult(
                    success=True,
                    engineer_id=engineer_id,
                    metrics_collected=len(metrics),
                    target_date=target_date,
                    retry_count=retry_count,
                    timestamp=datetime.now()
                )
                
                self._collection_history.append(result)
                return result
                
            except Exception as e:
                retry_count += 1
                last_error = str(e)
                
                if retry_count < self.max_retries:
                    # Exponential backoff
                    import time
                    delay = (self.config.backoff_multiplier ** attempt)
                    time.sleep(delay)
                    continue
                
                # Max retries exhausted
                result = CollectionResult(
                    success=False,
                    engineer_id=engineer_id,
                    error_message=last_error,
                    retry_count=retry_count,
                    timestamp=datetime.now()
                )
                
                self._collection_history.append(result)
                return result
        
        # Should not reach here, but fallback
        result = CollectionResult(
            success=False,
            engineer_id=engineer_id,
            error_message=last_error or "Unknown error",
            retry_count=retry_count,
            timestamp=datetime.now()
        )
        self._collection_history.append(result)
        return result
    
    def collect_batch(
        self,
        engineer_ids: List[str],
        target_date: Optional[date] = None
    ) -> List[CollectionResult]:
        """
        Collect metrics for multiple engineers in batch.
        
        Args:
            engineer_ids: List of engineer emails/identifiers
            target_date: Target date for metrics (defaults to today)
            
        Returns:
            List of CollectionResult (one per engineer)
        """
        results = []
        
        for engineer_id in engineer_ids:
            result = self.collect_copilot_metrics(
                engineer_id=engineer_id,
                target_date=target_date
            )
            results.append(result)
        
        return results
    
    def aggregate_team_metrics(
        self,
        team_id: str,
        team_members: List[str],
        aggregation_date: date
    ) -> AggregationResult:
        """
        Aggregate engineer-level metrics to team level.
        
        Args:
            team_id: Team identifier
            team_members: List of engineer hashes (anonymized)
            aggregation_date: Date for aggregation
            
        Returns:
            AggregationResult with team-level metrics
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Aggregate Copilot metrics
            placeholders = ','.join('?' * len(team_members))
            cursor.execute(f"""
                SELECT 
                    SUM(total_suggestions) as total_sugg,
                    SUM(acceptances) as total_acc,
                    SUM(lines_suggested) as total_lines_sugg,
                    SUM(lines_accepted) as total_lines_acc
                FROM copilot_metrics
                WHERE engineer_hash IN ({placeholders})
                  AND metric_date = ?
            """, (*team_members, aggregation_date.isoformat()))
            
            copilot_row = cursor.fetchone()
            total_suggestions = copilot_row[0] or 0
            total_acceptances = copilot_row[1] or 0
            
            acceptance_rate = (
                total_acceptances / total_suggestions
                if total_suggestions > 0
                else 0.0
            )
            
            # Aggregate CORTEX metrics (if tracker available)
            cortex_total_requests = 0
            cortex_total_successful = 0
            cortex_success_rate = 0.0
            
            if self.cortex_tracker:
                cursor.execute(f"""
                    SELECT 
                        SUM(requests_count) as total_req,
                        SUM(successful_count) as total_succ
                    FROM cortex_usage_metrics
                    WHERE engineer_hash IN ({placeholders})
                      AND metric_date = ?
                """, (*team_members, aggregation_date.isoformat()))
                
                cortex_row = cursor.fetchone()
                cortex_total_requests = cortex_row[0] or 0
                cortex_total_successful = cortex_row[1] or 0
                
                cortex_success_rate = (
                    cortex_total_successful / cortex_total_requests
                    if cortex_total_requests > 0
                    else 0.0
                )
            
            # Save team aggregation
            cursor.execute("""
                INSERT OR REPLACE INTO team_aggregations
                (team_id, aggregation_date, copilot_total_suggestions,
                 copilot_acceptance_rate, cortex_total_requests,
                 cortex_success_rate, team_size, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                team_id,
                aggregation_date.isoformat(),
                total_suggestions,
                acceptance_rate,
                cortex_total_requests,
                cortex_success_rate,
                len(team_members),
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
            return AggregationResult(
                success=True,
                team_id=team_id,
                aggregation_date=aggregation_date,
                team_size=len(team_members),
                total_suggestions=total_suggestions,
                total_acceptances=total_acceptances,
                acceptance_rate=acceptance_rate,
                cortex_total_requests=cortex_total_requests,
                cortex_success_rate=cortex_success_rate
            )
            
        except Exception as e:
            return AggregationResult(
                success=False,
                team_id=team_id,
                aggregation_date=aggregation_date,
                error_message=str(e)
            )
    
    def backfill_metrics(
        self,
        engineer_id: str,
        start_date: date,
        end_date: date
    ) -> List[CollectionResult]:
        """
        Backfill metrics for date range incrementally.
        
        Args:
            engineer_id: Engineer email/identifier
            start_date: Start of date range (inclusive)
            end_date: End of date range (inclusive)
            
        Returns:
            List of CollectionResult (one per date)
        """
        results = []
        current_date = start_date
        
        while current_date <= end_date:
            result = self.collect_copilot_metrics(
                engineer_id=engineer_id,
                target_date=current_date
            )
            results.append(result)
            current_date += timedelta(days=1)
        
        return results
    
    def get_collection_status(self) -> Dict[str, Any]:
        """
        Get collection status summary.
        
        Returns:
            Dictionary with collection statistics
        """
        if not self._collection_history:
            return {
                'total_collections': 0,
                'successful_collections': 0,
                'failed_collections': 0,
                'success_rate': 0.0
            }
        
        total = len(self._collection_history)
        successful = sum(1 for r in self._collection_history if r.success)
        failed = total - successful
        success_rate = successful / total if total > 0 else 0.0
        
        return {
            'total_collections': total,
            'successful_collections': successful,
            'failed_collections': failed,
            'success_rate': success_rate
        }
    
    def _calculate_next_collection_time(self) -> Optional[datetime]:
        """
        Calculate next collection time based on schedule type.
        
        Returns:
            Next collection datetime or None for manual
        """
        if self.schedule_type == ScheduleType.MANUAL:
            return None
        
        now = datetime.now()
        
        if self.schedule_type == ScheduleType.DAILY:
            # Next occurrence at collection_hour
            next_time = now.replace(
                hour=self.config.collection_hour,
                minute=0,
                second=0,
                microsecond=0
            )
            
            if next_time <= now:
                # Already passed today, schedule for tomorrow
                next_time += timedelta(days=1)
            
            return next_time
        
        elif self.schedule_type == ScheduleType.WEEKLY:
            # Next occurrence on collection_day at collection_hour
            current_weekday = now.weekday() + 1  # 1=Monday
            days_until_collection = (
                self.config.collection_day - current_weekday
            ) % 7
            
            next_time = now.replace(
                hour=self.config.collection_hour,
                minute=0,
                second=0,
                microsecond=0
            ) + timedelta(days=days_until_collection)
            
            if next_time <= now:
                # Already passed this week, schedule for next week
                next_time += timedelta(days=7)
            
            return next_time
        
        elif self.schedule_type == ScheduleType.MONTHLY:
            # Next occurrence on 1st of month at collection_hour
            next_month = now.replace(day=1, hour=self.config.collection_hour)
            if next_month <= now:
                # Move to next month
                if now.month == 12:
                    next_month = next_month.replace(year=now.year + 1, month=1)
                else:
                    next_month = next_month.replace(month=now.month + 1)
            
            return next_month
        
        return None
