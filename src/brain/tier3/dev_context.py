"""
Tier 3: Development Context for CORTEX 4.0

Repository-specific development context and metrics.
- Storage: {workspace}/cortex-brain/tier3/metrics.db (per-repo)
- Features: Git metrics, hotspot detection, IDE context

Author: Asif Hussain
Copyright: © 2025 Asif Hussain. All rights reserved.
"""

import sqlite3
import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Any
from contextlib import contextmanager


class DevelopmentContext:
    """
    Tier 3: Development Context - Repository-specific metrics
    
    Features:
    - Git metrics (commits, changes, hotspots)
    - IDE context tracking
    - Repository health indicators
    
    Usage:
        context = DevelopmentContext(db_path)
        
        # Store git metrics
        context.store_git_metrics({"commits": 150, "hotspots": ["src/main.py"]})
        
        # Store IDE context
        context.store_ide_context("vscode")
        
        # Retrieve metrics
        metrics = context.get_metrics()
    """
    
    def __init__(self, db_path: Path):
        """
        Initialize development context.
        
        Args:
            db_path: Path to metrics.db
        """
        self.db_path = Path(db_path)
        self.logger = logging.getLogger(__name__)
        
        # Ensure directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize schema
        self._initialize_schema()
        
        self.logger.debug(f"Development Context initialized: {db_path}")
    
    @contextmanager
    def _get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def _initialize_schema(self):
        """Create database schema."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS metrics (
                    metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_type TEXT NOT NULL,
                    data_json TEXT NOT NULL,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # IDE context table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ide_context (
                    context_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ide_type TEXT NOT NULL,
                    context_data TEXT,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_metrics_type 
                ON metrics(metric_type, timestamp DESC)
            """)
            
            conn.commit()
    
    def store_git_metrics(self, metrics: Dict[str, Any]):
        """
        Store git metrics.
        
        Args:
            metrics: Git metrics data
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO metrics (metric_type, data_json)
                VALUES ('git', ?)
            """, (json.dumps(metrics),))
            conn.commit()
        
        self.logger.debug("Stored git metrics")
    
    def store_ide_context(self, ide_type: str, context_data: Optional[Dict[str, Any]] = None):
        """
        Store IDE context.
        
        Args:
            ide_type: IDE type (vscode, visualstudio, etc.)
            context_data: Additional context data
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO ide_context (ide_type, context_data)
                VALUES (?, ?)
            """, (ide_type, json.dumps(context_data or {})))
            conn.commit()
        
        self.logger.debug(f"Stored IDE context: {ide_type}")
    
    def get_metrics(self, metric_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Get latest metrics.
        
        Args:
            metric_type: Optional metric type filter
            
        Returns:
            Dictionary of metrics
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            if metric_type:
                cursor.execute("""
                    SELECT data_json FROM metrics
                    WHERE metric_type = ?
                    ORDER BY timestamp DESC
                    LIMIT 1
                """, (metric_type,))
            else:
                cursor.execute("""
                    SELECT metric_type, data_json FROM metrics
                    ORDER BY timestamp DESC
                """)
            
            row = cursor.fetchone()
            if row:
                return json.loads(row["data_json"])
            return {}
    
    def get_ide_context(self) -> Optional[str]:
        """
        Get latest IDE context.
        
        Returns:
            IDE type or None
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT ide_type FROM ide_context
                ORDER BY timestamp DESC
                LIMIT 1
            """)
            
            row = cursor.fetchone()
            return row["ide_type"] if row else None
    
    def close(self):
        """Close development context (cleanup)."""
        self.logger.debug("Development Context closed")
