"""
Dashboard Data Collector

Purpose: Fetch data from Tier 1/2/3 databases for dashboard visualization.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import sqlite3
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional


class DashboardDataCollector:
    """
    Collects data from CORTEX brain databases for dashboard visualization.
    
    Data Sources:
    - Tier 1: Test results, conversation history
    - Tier 2: Knowledge graph, pattern learning
    - Tier 3: Architecture health, development context
    """
    
    def __init__(self, brain_path: Path):
        """
        Initialize data collector.
        
        Args:
            brain_path: Path to cortex-brain directory
        """
        self.logger = logging.getLogger(__name__)
        self.brain_path = Path(brain_path)
        
        # Database paths
        self.tier1_db = self.brain_path / "tier1" / "working_memory.db"
        self.tier2_db = self.brain_path / "tier2" / "knowledge_graph.db"
        self.tier3_db = self.brain_path / "tier3" / "context.db"
        
        self.logger.info(f"DataCollector initialized with brain_path={brain_path}")
    
    def fetch_health_snapshots(self, since: datetime) -> Optional[List[Dict[str, Any]]]:
        """
        Fetch architecture health snapshots from Tier 3.
        
        Args:
            since: Start date for historical data
        
        Returns:
            List of snapshot dicts or None if data unavailable
        """
        try:
            if not self.tier3_db.exists():
                self.logger.warning(f"Tier 3 database not found: {self.tier3_db}")
                return None
            
            conn = sqlite3.connect(str(self.tier3_db))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Check if table exists
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='architecture_health_snapshots'
            """)
            
            if not cursor.fetchone():
                self.logger.warning("architecture_health_snapshots table not found")
                conn.close()
                return None
            
            # Fetch snapshots since date
            cursor.execute("""
                SELECT snapshot_time, overall_score, layer_scores, feature_counts,
                       velocity, direction, volatility
                FROM architecture_health_snapshots
                WHERE snapshot_time >= ?
                ORDER BY snapshot_time ASC
            """, (since.isoformat(),))
            
            snapshots = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            if not snapshots:
                self.logger.info("No health snapshots found in date range")
                return None
            
            # Parse JSON fields
            import json
            for snapshot in snapshots:
                if snapshot.get('layer_scores'):
                    snapshot['layer_scores'] = json.loads(snapshot['layer_scores'])
                if snapshot.get('feature_counts'):
                    snapshot['feature_counts'] = json.loads(snapshot['feature_counts'])
            
            self.logger.info(f"Fetched {len(snapshots)} health snapshots")
            return snapshots
            
        except Exception as e:
            self.logger.error(f"Failed to fetch health snapshots: {e}", exc_info=True)
            return None
    
    def fetch_test_results(self, since: datetime) -> Optional[List[Dict[str, Any]]]:
        """
        Fetch test results from Tier 1.
        
        Args:
            since: Start date for historical data
        
        Returns:
            List of test result dicts or None if data unavailable
        """
        try:
            if not self.tier1_db.exists():
                self.logger.warning(f"Tier 1 database not found: {self.tier1_db}")
                return None
            
            conn = sqlite3.connect(str(self.tier1_db))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Check if table exists
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='test_results'
            """)
            
            if not cursor.fetchone():
                self.logger.warning("test_results table not found")
                conn.close()
                return None
            
            cursor.execute("""
                SELECT run_time, total_tests, passed, failed, skipped,
                       coverage_percent, module_coverage
                FROM test_results
                WHERE run_time >= ?
                ORDER BY run_time ASC
            """, (since.isoformat(),))
            
            results = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            if not results:
                self.logger.info("No test results found in date range")
                return None
            
            # Parse JSON fields
            import json
            for result in results:
                if result.get('module_coverage'):
                    result['module_coverage'] = json.loads(result['module_coverage'])
            
            self.logger.info(f"Fetched {len(results)} test results")
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to fetch test results: {e}", exc_info=True)
            return None
    
    def fetch_code_metrics(self, since: datetime) -> Optional[List[Dict[str, Any]]]:
        """
        Fetch code quality metrics from Tier 3.
        
        Args:
            since: Start date for historical data
        
        Returns:
            List of metric dicts or None if data unavailable
        """
        try:
            if not self.tier3_db.exists():
                self.logger.warning(f"Tier 3 database not found: {self.tier3_db}")
                return None
            
            conn = sqlite3.connect(str(self.tier3_db))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Check if table exists
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='code_metrics'
            """)
            
            if not cursor.fetchone():
                self.logger.warning("code_metrics table not found")
                conn.close()
                return None
            
            cursor.execute("""
                SELECT measured_at, maintainability_index, cyclomatic_complexity,
                       documentation_ratio, test_coverage_ratio, security_score
                FROM code_metrics
                WHERE measured_at >= ?
                ORDER BY measured_at ASC
            """, (since.isoformat(),))
            
            metrics = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            if not metrics:
                self.logger.info("No code metrics found in date range")
                return None
            
            self.logger.info(f"Fetched {len(metrics)} code metrics")
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to fetch code metrics: {e}", exc_info=True)
            return None
    
    def fetch_git_activity(self, since: datetime) -> Optional[List[Dict[str, Any]]]:
        """
        Fetch git activity data (commit frequency).
        
        Args:
            since: Start date for historical data
        
        Returns:
            List of activity dicts or None (not yet implemented)
        """
        # TODO: Implement actual git log parsing
        self.logger.warning("Git activity fetch not yet implemented")
        return None
    
    def fetch_performance_data(self, since: datetime) -> Optional[List[Dict[str, Any]]]:
        """
        Fetch performance benchmark data.
        
        Args:
            since: Start date for historical data
        
        Returns:
            List of performance dicts or None (not yet implemented)
        """
        # TODO: Implement actual performance data collection
        self.logger.warning("Performance data fetch not yet implemented")
        return None
    

