"""
CORTEX Tier 3: Copilot Metrics Collection
Handles GitHub Copilot usage tracking and acceptance rate analysis.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import hashlib
import json
import sqlite3
import time
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import List, Optional, Dict, Any
import logging

try:
    import requests
except ImportError:
    requests = None

logger = logging.getLogger(__name__)


@dataclass
class CopilotLanguageBreakdown:
    """Language-specific Copilot usage breakdown."""
    language: str
    suggestions_count: int
    acceptances_count: int
    acceptance_rate: Optional[float] = None
    
    def __post_init__(self):
        """Calculate acceptance rate if not provided."""
        if self.acceptance_rate is None and self.suggestions_count > 0:
            self.acceptance_rate = self.acceptances_count / self.suggestions_count


@dataclass
class CopilotMetric:
    """Daily Copilot usage metrics."""
    metric_date: date
    engineer_hash: str
    language: str
    suggestions_shown: int
    suggestions_accepted: int
    acceptance_rate: Optional[float] = None
    inline_completions: int = 0
    chat_interactions: int = 0
    avg_suggestion_latency_ms: Optional[float] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Calculate acceptance rate if not provided."""
        if self.acceptance_rate is None and self.suggestions_shown > 0:
            self.acceptance_rate = self.suggestions_accepted / self.suggestions_shown


class CopilotMetricsCollector:
    """
    Collects GitHub Copilot usage metrics with privacy protection.
    
    Features:
    - GitHub API integration for Copilot usage data
    - Language-specific breakdown
    - Rate limiting with exponential backoff
    - Retry logic for network failures
    - SHA-256 hashing for engineer privacy
    - Database persistence with uniqueness constraints
    """
    
    def __init__(self, db_path: Path, github_token: Optional[str] = None, org_name: Optional[str] = None):
        """
        Initialize Copilot metrics collector.
        
        Args:
            db_path: Path to Tier 3 database
            github_token: GitHub Personal Access Token with 'copilot' scope
            org_name: Optional GitHub organization name
            
        Raises:
            ValueError: If github_token is None or empty
        """
        if not github_token:
            raise ValueError("GitHub token required for Copilot API access")
        
        self.db_path = Path(db_path)
        self.github_token = github_token
        self.org_name = org_name
        self._ensure_schema()
    
    def _ensure_schema(self):
        """Ensure copilot_metrics table exists."""
        conn = sqlite3.connect(self.db_path)
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
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_copilot_date ON copilot_metrics(metric_date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_copilot_engineer ON copilot_metrics(engineer_hash)")
        
        conn.commit()
        conn.close()
    
    def fetch_copilot_usage(
        self,
        target_date: Optional[date] = None,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Fetch Copilot usage data from GitHub API.
        
        Args:
            target_date: Date to fetch metrics for (default: yesterday)
            max_retries: Maximum number of retry attempts
            
        Returns:
            Dictionary with usage data including breakdown by language
            
        Raises:
            Exception: If rate limit exceeded or max retries exhausted
        """
        if requests is None:
            raise ImportError("requests library required for GitHub API access")
        
        if target_date is None:
            target_date = date.today() - timedelta(days=1)
        
        # GitHub Copilot API endpoint
        if self.org_name:
            url = f"https://api.github.com/orgs/{self.org_name}/copilot/usage"
        else:
            url = "https://api.github.com/user/copilot_usage"
        
        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        
        params = {
            "since": target_date.isoformat(),
            "until": target_date.isoformat()
        }
        
        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers=headers, params=params, timeout=30)
                
                # Handle rate limiting
                if response.status_code == 429:
                    reset_time = int(response.headers.get("X-RateLimit-Reset", 0))
                    wait_seconds = max(reset_time - int(time.time()), 60)
                    raise Exception(f"Rate limit exceeded. Resets in {wait_seconds}s")
                
                response.raise_for_status()
                return response.json()
                
            except (requests.RequestException, Exception) as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(f"Network error (attempt {attempt + 1}/{max_retries}): {e}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Failed to fetch Copilot usage after {max_retries} attempts: {e}")
                    raise
        
        return {}
    
    def parse_language_breakdown(self, api_data: Dict[str, Any]) -> List[CopilotLanguageBreakdown]:
        """
        Parse language breakdown from API response.
        
        Args:
            api_data: Raw API response data
            
        Returns:
            List of CopilotLanguageBreakdown objects
        """
        breakdowns = []
        
        for item in api_data.get("breakdown", []):
            breakdown = CopilotLanguageBreakdown(
                language=item.get("language", "Unknown"),
                suggestions_count=item.get("suggestions_count", 0),
                acceptances_count=item.get("acceptances_count", 0)
            )
            breakdowns.append(breakdown)
        
        return breakdowns
    
    def anonymize_engineer_id(self, engineer_id: str) -> str:
        """
        Hash engineer ID using SHA-256 for privacy protection.
        
        Args:
            engineer_id: Original engineer identifier (email, username, etc.)
            
        Returns:
            64-character hexadecimal SHA-256 hash
        """
        return hashlib.sha256(engineer_id.encode('utf-8')).hexdigest()
    
    def save_metrics(self, metrics: List[CopilotMetric]):
        """
        Save Copilot metrics to database.
        
        Uses INSERT OR REPLACE to handle duplicates (updates existing records).
        
        Args:
            metrics: List of CopilotMetric objects to save
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for metric in metrics:
            cursor.execute("""
                INSERT OR REPLACE INTO copilot_metrics
                (metric_date, engineer_hash, language, suggestions_shown, 
                 suggestions_accepted, acceptance_rate, inline_completions,
                 chat_interactions, avg_suggestion_latency_ms, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metric.metric_date.isoformat(),
                metric.engineer_hash,
                metric.language,
                metric.suggestions_shown,
                metric.suggestions_accepted,
                metric.acceptance_rate,
                metric.inline_completions,
                metric.chat_interactions,
                metric.avg_suggestion_latency_ms,
                metric.created_at.isoformat()
            ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Saved {len(metrics)} Copilot metrics to database")
    
    def get_metrics(
        self,
        days: int = 30,
        engineer_hash: Optional[str] = None,
        language: Optional[str] = None
    ) -> List[CopilotMetric]:
        """
        Retrieve Copilot metrics from database.
        
        Args:
            days: Number of days to retrieve (default: 30)
            engineer_hash: Filter by engineer hash (None = all)
            language: Filter by programming language (None = all)
            
        Returns:
            List of CopilotMetric objects sorted by date descending
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Calculate since_date: today minus days (exclusive, so we get last N days)
        since_date = (date.today() - timedelta(days=days - 1)).isoformat()
        
        # Build query with optional filters
        query = """
            SELECT * FROM copilot_metrics
            WHERE metric_date >= ?
        """
        params = [since_date]
        
        if engineer_hash:
            query += " AND engineer_hash = ?"
            params.append(engineer_hash)
        
        if language:
            query += " AND language = ?"
            params.append(language)
        
        query += " ORDER BY metric_date DESC"
        
        cursor.execute(query, params)
        
        metrics = []
        for row in cursor.fetchall():
            metric = CopilotMetric(
                metric_date=datetime.fromisoformat(row['metric_date']).date(),
                engineer_hash=row['engineer_hash'],
                language=row['language'],
                suggestions_shown=row['suggestions_shown'],
                suggestions_accepted=row['suggestions_accepted'],
                acceptance_rate=row['acceptance_rate'],
                inline_completions=row['inline_completions'] or 0,
                chat_interactions=row['chat_interactions'] or 0,
                avg_suggestion_latency_ms=row['avg_suggestion_latency_ms'],
                created_at=datetime.fromisoformat(row['created_at'])
            )
            metrics.append(metric)
        
        conn.close()
        return metrics
    
    def calculate_aggregate_acceptance_rate(
        self,
        engineer_hash: str,
        target_date: date
    ) -> float:
        """
        Calculate aggregate acceptance rate across all languages for a date.
        
        Args:
            engineer_hash: Engineer identifier hash
            target_date: Date to calculate for
            
        Returns:
            Aggregate acceptance rate (0.0 to 1.0)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                SUM(suggestions_shown) as total_shown,
                SUM(suggestions_accepted) as total_accepted
            FROM copilot_metrics
            WHERE engineer_hash = ? AND metric_date = ?
        """, (engineer_hash, target_date.isoformat()))
        
        row = cursor.fetchone()
        conn.close()
        
        if row and row[0] and row[0] > 0:
            return row[1] / row[0]
        return 0.0
    
    def export_metrics(
        self,
        engineer_hash: str,
        start_date: date,
        end_date: date,
        format: str = "json"
    ) -> Dict[str, Any]:
        """
        Export metrics in privacy-safe format.
        
        Args:
            engineer_hash: Engineer identifier hash
            start_date: Start date for export
            end_date: End date for export
            format: Export format ('json', 'csv', 'yaml')
            
        Returns:
            Dictionary with exported metrics (no PII)
        """
        # Get metrics for date range
        days_diff = (end_date - start_date).days + 1
        metrics = self.get_metrics(days=days_diff, engineer_hash=engineer_hash)
        
        # Filter to exact date range
        metrics = [
            m for m in metrics
            if start_date <= m.metric_date <= end_date
        ]
        
        # Build privacy-safe export
        export_data = {
            "engineer_id": engineer_hash,  # Hash is safe
            "reporting_period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "metrics": []
        }
        
        for metric in metrics:
            export_data["metrics"].append({
                "date": metric.metric_date.isoformat(),
                "language": metric.language,
                "suggestions_shown": metric.suggestions_shown,
                "suggestions_accepted": metric.suggestions_accepted,
                "acceptance_rate": round(metric.acceptance_rate, 4) if metric.acceptance_rate else 0.0,
                "inline_completions": metric.inline_completions,
                "chat_interactions": metric.chat_interactions
            })
        
        # Calculate summary statistics
        if metrics:
            total_shown = sum(m.suggestions_shown for m in metrics)
            total_accepted = sum(m.suggestions_accepted for m in metrics)
            
            export_data["summary"] = {
                "total_suggestions": total_shown,
                "total_accepted": total_accepted,
                "overall_acceptance_rate": round(total_accepted / total_shown, 4) if total_shown > 0 else 0.0,
                "days_tracked": len(set(m.metric_date for m in metrics)),
                "languages_used": list(set(m.language for m in metrics))
            }
        
        return export_data
