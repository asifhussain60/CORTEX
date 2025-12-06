"""
CORTEX Tier 3: CORTEX Usage Tracking
Handles CORTEX usage metrics extraction from Tier 1 working memory.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import sqlite3
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


# Intent types enum (matching CORTEX intent classification)
class IntentType:
    PLAN = "PLAN"
    EXECUTE = "EXECUTE"
    TEST = "TEST"
    VALIDATE = "VALIDATE"
    GOVERN = "GOVERN"
    CORRECT = "CORRECT"
    RESUME = "RESUME"
    ASK = "ASK"


@dataclass
class CortexUsageMetric:
    """Daily CORTEX usage metrics by intent type."""
    metric_date: date
    engineer_hash: str
    intent_type: str
    requests_count: int
    successful_count: int
    failed_count: int
    avg_response_time_seconds: Optional[float] = None
    tokens_consumed: int = 0
    success_rate: Optional[float] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Calculate success rate if not provided."""
        if self.success_rate is None and self.requests_count > 0:
            self.success_rate = self.successful_count / self.requests_count


class CortexUsageTracker:
    """
    Tracks CORTEX usage metrics from Tier 1 working memory.
    
    Features:
    - Extract metrics from conversation history
    - Aggregate by intent type
    - Calculate success rates and response times
    - Token consumption tracking
    - Database persistence with uniqueness constraints
    """
    
    def __init__(self, tier3_db_path: Path, working_memory_db_path: Path):
        """
        Initialize CORTEX usage tracker.
        
        Args:
            tier3_db_path: Path to Tier 3 database
            working_memory_db_path: Path to Tier 1 working memory database
        """
        self.tier3_db_path = Path(tier3_db_path)
        self.working_memory_db_path = Path(working_memory_db_path)
        self._ensure_schema()
    
    def _ensure_schema(self):
        """Ensure cortex_usage_metrics table exists."""
        conn = sqlite3.connect(self.tier3_db_path)
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
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_cortex_usage_engineer ON cortex_usage_metrics(engineer_hash)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_cortex_usage_intent ON cortex_usage_metrics(intent_type)")
        
        conn.commit()
        conn.close()
    
    def extract_from_working_memory(
        self,
        target_date: date,
        engineer_hash: str,
        days_window: int = 1
    ) -> List[CortexUsageMetric]:
        """
        Extract CORTEX usage metrics from Tier 1 working memory.
        
        Args:
            target_date: Date to extract metrics for
            engineer_hash: Engineer identifier hash
            days_window: Number of days to include (default: 1)
            
        Returns:
            List of CortexUsageMetric objects aggregated by intent type
        """
        conn = sqlite3.connect(self.working_memory_db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Query conversations within date window (inclusive range)
        start_date = (target_date - timedelta(days=days_window - 1)).isoformat()
        # Include one extra day to catch end of target_date
        end_date = (target_date + timedelta(days=2)).isoformat()
        
        cursor.execute("""
            SELECT 
                DATE(timestamp) as conv_date,
                intent_type,
                success,
                response_time_seconds,
                tokens_used,
                COUNT(*) as count
            FROM conversations
            WHERE timestamp >= ? AND timestamp < ?
            GROUP BY DATE(timestamp), intent_type, success
            ORDER BY DATE(timestamp), intent_type
        """, (start_date, end_date))
        
        # Aggregate by date and intent
        aggregated = {}
        for row in cursor.fetchall():
            conv_date = datetime.fromisoformat(row['conv_date']).date()
            intent = row['intent_type']
            success = bool(row['success'])
            count = row['count']
            
            key = (conv_date, intent)
            if key not in aggregated:
                aggregated[key] = {
                    'date': conv_date,
                    'intent': intent,
                    'total': 0,
                    'successful': 0,
                    'failed': 0,
                    'response_times': [],
                    'tokens': 0
                }
            
            aggregated[key]['total'] += count
            if success:
                aggregated[key]['successful'] += count
            else:
                aggregated[key]['failed'] += count
            
            # Accumulate response time and tokens for this group
            if row['response_time_seconds']:
                aggregated[key]['response_times'].extend([row['response_time_seconds']] * count)
            if row['tokens_used']:
                aggregated[key]['tokens'] += row['tokens_used'] * count
        
        conn.close()
        
        # Convert to CortexUsageMetric objects
        metrics = []
        for key, data in aggregated.items():
            avg_response_time = None
            if data['response_times']:
                avg_response_time = sum(data['response_times']) / len(data['response_times'])
            
            metric = CortexUsageMetric(
                metric_date=data['date'],
                engineer_hash=engineer_hash,
                intent_type=data['intent'],
                requests_count=data['total'],
                successful_count=data['successful'],
                failed_count=data['failed'],
                avg_response_time_seconds=avg_response_time,
                tokens_consumed=data['tokens']
            )
            metrics.append(metric)
        
        return metrics
    
    def aggregate_by_intent(
        self,
        raw_conversations: List[Dict[str, Any]],
        target_date: date,
        engineer_hash: str
    ) -> List[CortexUsageMetric]:
        """
        Aggregate raw conversation data by intent type.
        
        Args:
            raw_conversations: List of conversation dictionaries
            target_date: Date to aggregate for
            engineer_hash: Engineer identifier hash
            
        Returns:
            List of CortexUsageMetric objects
        """
        aggregated = {}
        
        for conv in raw_conversations:
            intent = conv.get('intent', 'UNKNOWN')
            success = conv.get('success', False)
            response_time = conv.get('response_time', 0.0)
            tokens = conv.get('tokens', 0)
            
            if intent not in aggregated:
                aggregated[intent] = {
                    'total': 0,
                    'successful': 0,
                    'failed': 0,
                    'response_times': [],
                    'tokens': 0
                }
            
            aggregated[intent]['total'] += 1
            if success:
                aggregated[intent]['successful'] += 1
            else:
                aggregated[intent]['failed'] += 1
            
            if response_time:
                aggregated[intent]['response_times'].append(response_time)
            
            aggregated[intent]['tokens'] += tokens
        
        # Convert to metrics
        metrics = []
        for intent, data in aggregated.items():
            avg_response_time = None
            if data['response_times']:
                avg_response_time = sum(data['response_times']) / len(data['response_times'])
            
            metric = CortexUsageMetric(
                metric_date=target_date,
                engineer_hash=engineer_hash,
                intent_type=intent,
                requests_count=data['total'],
                successful_count=data['successful'],
                failed_count=data['failed'],
                avg_response_time_seconds=avg_response_time,
                tokens_consumed=data['tokens']
            )
            metrics.append(metric)
        
        return metrics
    
    def calculate_success_rate(self, metric: CortexUsageMetric) -> float:
        """
        Calculate success rate for a metric.
        
        Args:
            metric: CortexUsageMetric object
            
        Returns:
            Success rate (0.0 to 1.0)
        """
        if metric.requests_count == 0:
            return 0.0
        return metric.successful_count / metric.requests_count
    
    def save_metrics(self, metrics: List[CortexUsageMetric]):
        """
        Save CORTEX usage metrics to database.
        
        Uses INSERT OR REPLACE to handle duplicates (updates existing records).
        
        Args:
            metrics: List of CortexUsageMetric objects to save
        """
        conn = sqlite3.connect(self.tier3_db_path)
        cursor = conn.cursor()
        
        for metric in metrics:
            cursor.execute("""
                INSERT OR REPLACE INTO cortex_usage_metrics
                (metric_date, engineer_hash, intent_type, requests_count,
                 successful_count, failed_count, avg_response_time_seconds,
                 tokens_consumed, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metric.metric_date.isoformat(),
                metric.engineer_hash,
                metric.intent_type,
                metric.requests_count,
                metric.successful_count,
                metric.failed_count,
                metric.avg_response_time_seconds,
                metric.tokens_consumed,
                metric.created_at.isoformat()
            ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Saved {len(metrics)} CORTEX usage metrics to database")
    
    def get_metrics(
        self,
        days: int = 30,
        engineer_hash: Optional[str] = None,
        intent_type: Optional[str] = None
    ) -> List[CortexUsageMetric]:
        """
        Retrieve CORTEX usage metrics from database.
        
        Args:
            days: Number of days to retrieve (default: 30)
            engineer_hash: Filter by engineer hash (None = all)
            intent_type: Filter by intent type (None = all)
            
        Returns:
            List of CortexUsageMetric objects sorted by date descending
        """
        conn = sqlite3.connect(self.tier3_db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Calculate since_date
        since_date = (date.today() - timedelta(days=days - 1)).isoformat()
        
        # Build query with optional filters
        query = """
            SELECT * FROM cortex_usage_metrics
            WHERE metric_date >= ?
        """
        params = [since_date]
        
        if engineer_hash:
            query += " AND engineer_hash = ?"
            params.append(engineer_hash)
        
        if intent_type:
            query += " AND intent_type = ?"
            params.append(intent_type)
        
        query += " ORDER BY metric_date DESC, intent_type"
        
        cursor.execute(query, params)
        
        metrics = []
        for row in cursor.fetchall():
            metric = CortexUsageMetric(
                metric_date=datetime.fromisoformat(row['metric_date']).date(),
                engineer_hash=row['engineer_hash'],
                intent_type=row['intent_type'],
                requests_count=row['requests_count'],
                successful_count=row['successful_count'],
                failed_count=row['failed_count'],
                avg_response_time_seconds=row['avg_response_time_seconds'],
                tokens_consumed=row['tokens_consumed'] or 0,
                created_at=datetime.fromisoformat(row['created_at'])
            )
            metrics.append(metric)
        
        conn.close()
        return metrics
    
    def calculate_total_tokens(
        self,
        engineer_hash: str,
        target_date: date
    ) -> int:
        """
        Calculate total tokens consumed across all intents for a date.
        
        Args:
            engineer_hash: Engineer identifier hash
            target_date: Date to calculate for
            
        Returns:
            Total tokens consumed
        """
        conn = sqlite3.connect(self.tier3_db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT SUM(tokens_consumed) as total
            FROM cortex_usage_metrics
            WHERE engineer_hash = ? AND metric_date = ?
        """, (engineer_hash, target_date.isoformat()))
        
        row = cursor.fetchone()
        conn.close()
        
        return row[0] if row and row[0] else 0
    
    def get_most_used_intent(
        self,
        engineer_hash: str,
        days: int = 30
    ) -> Optional[str]:
        """
        Identify most frequently used intent type.
        
        Args:
            engineer_hash: Engineer identifier hash
            days: Number of days to analyze
            
        Returns:
            Most used intent type string, or None
        """
        conn = sqlite3.connect(self.tier3_db_path)
        cursor = conn.cursor()
        
        since_date = (date.today() - timedelta(days=days - 1)).isoformat()
        
        cursor.execute("""
            SELECT intent_type, SUM(requests_count) as total
            FROM cortex_usage_metrics
            WHERE engineer_hash = ? AND metric_date >= ?
            GROUP BY intent_type
            ORDER BY total DESC
            LIMIT 1
        """, (engineer_hash, since_date))
        
        row = cursor.fetchone()
        conn.close()
        
        return row[0] if row else None
    
    def calculate_average_response_time(
        self,
        engineer_hash: str,
        target_date: date
    ) -> float:
        """
        Calculate weighted average response time across all intents for a date.
        
        Args:
            engineer_hash: Engineer identifier hash
            target_date: Date to calculate for
            
        Returns:
            Weighted average response time in seconds
        """
        conn = sqlite3.connect(self.tier3_db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                avg_response_time_seconds,
                requests_count
            FROM cortex_usage_metrics
            WHERE engineer_hash = ? 
              AND metric_date = ?
              AND avg_response_time_seconds IS NOT NULL
        """, (engineer_hash, target_date.isoformat()))
        
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return 0.0
        
        # Calculate weighted average
        total_time = sum(row[0] * row[1] for row in rows)
        total_requests = sum(row[1] for row in rows)
        
        return total_time / total_requests if total_requests > 0 else 0.0
    
    def export_usage_summary(
        self,
        engineer_hash: str,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """
        Export usage summary in privacy-safe format.
        
        Args:
            engineer_hash: Engineer identifier hash
            start_date: Start date for export
            end_date: End date for export
            
        Returns:
            Dictionary with usage summary (no PII)
        """
        # Get metrics for date range
        days_diff = (end_date - start_date).days + 1
        metrics = self.get_metrics(days=days_diff, engineer_hash=engineer_hash)
        
        # Filter to exact date range
        metrics = [
            m for m in metrics
            if start_date <= m.metric_date <= end_date
        ]
        
        # Calculate summary statistics
        total_requests = sum(m.requests_count for m in metrics)
        total_successful = sum(m.successful_count for m in metrics)
        total_tokens = sum(m.tokens_consumed for m in metrics)
        
        overall_success_rate = 0.0
        if total_requests > 0:
            overall_success_rate = total_successful / total_requests
        
        # Group by intent type
        by_intent = {}
        for metric in metrics:
            intent = metric.intent_type
            if intent not in by_intent:
                by_intent[intent] = {
                    'requests': 0,
                    'successful': 0,
                    'tokens': 0,
                    'avg_response_time': []
                }
            
            by_intent[intent]['requests'] += metric.requests_count
            by_intent[intent]['successful'] += metric.successful_count
            by_intent[intent]['tokens'] += metric.tokens_consumed
            
            if metric.avg_response_time_seconds:
                by_intent[intent]['avg_response_time'].append(
                    (metric.avg_response_time_seconds, metric.requests_count)
                )
        
        # Calculate intent-level averages
        for intent, data in by_intent.items():
            if data['avg_response_time']:
                total_time = sum(t * w for t, w in data['avg_response_time'])
                total_weight = sum(w for _, w in data['avg_response_time'])
                data['avg_response_time'] = round(total_time / total_weight, 2)
            else:
                data['avg_response_time'] = 0.0
            
            data['success_rate'] = round(data['successful'] / data['requests'], 4) if data['requests'] > 0 else 0.0
        
        # Build export
        return {
            'engineer_id': engineer_hash,
            'reporting_period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'total_requests': total_requests,
            'total_successful': total_successful,
            'overall_success_rate': round(overall_success_rate, 4),
            'total_tokens_consumed': total_tokens,
            'by_intent': by_intent
        }
