"""
Analytics Database Manager

Manages SQLite databases for CORTEX feedback analytics:
- Per-application databases (cortex-brain/analytics/per-app/{AppName}/metrics.db)
- Cross-application aggregate database (cortex-brain/analytics/aggregate/cross-app-metrics.db)

Features:
    - Database initialization with schema
    - Report storage with deduplication
    - Query APIs for trend analysis
    - Backup and maintenance utilities
    - Migration support

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import sqlite3
import logging
import json
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class AnalyticsDBManager:
    """
    Manages analytics databases for feedback reports.
    
    Database Structure:
        - Per-app: cortex-brain/analytics/per-app/{AppName}/metrics.db
        - Aggregate: cortex-brain/analytics/aggregate/cross-app-metrics.db
    
    Features:
        - Auto-initialization with schema
        - Duplicate detection via report hashing
        - Transaction support
        - Query helpers for common analytics
        - Backup utilities
    """
    
    def __init__(self, analytics_root: Path):
        """
        Initialize analytics database manager.
        
        Args:
            analytics_root: Root directory for analytics (cortex-brain/analytics/)
        """
        self.analytics_root = Path(analytics_root)
        self.analytics_root.mkdir(parents=True, exist_ok=True)
        
        self.per_app_dir = self.analytics_root / "per-app"
        self.aggregate_dir = self.analytics_root / "aggregate"
        self.backup_dir = self.analytics_root / "backups"
        
        self.per_app_dir.mkdir(exist_ok=True)
        self.aggregate_dir.mkdir(exist_ok=True)
        self.backup_dir.mkdir(exist_ok=True)
        
        # Cache schema
        self.schema = self._load_schema()
    
    def _load_schema(self) -> str:
        """Load SQL schema from schema.sql file."""
        # Look for schema.sql in the same directory as this file
        schema_file = Path(__file__).parent / "schema.sql"
        if schema_file.exists():
            return schema_file.read_text(encoding='utf-8')
        else:
            logger.warning(f"Schema file not found: {schema_file}")
            return ""
    
    @contextmanager
    def get_connection(self, app_name: Optional[str] = None, aggregate: bool = False):
        """
        Get database connection with context manager.
        
        Args:
            app_name: Application name (for per-app DB), None for aggregate
            aggregate: If True, use aggregate DB
        
        Yields:
            sqlite3.Connection
        """
        if aggregate:
            db_path = self.aggregate_dir / "cross-app-metrics.db"
        elif app_name:
            app_db_dir = self.per_app_dir / app_name
            app_db_dir.mkdir(parents=True, exist_ok=True)
            db_path = app_db_dir / "metrics.db"
        else:
            raise ValueError("Must specify app_name or aggregate=True")
        
        # Initialize DB if doesn't exist
        is_new = not db_path.exists()
        
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row  # Access columns by name
        
        if is_new:
            self._initialize_database(conn)
        
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()
    
    def _initialize_database(self, conn: sqlite3.Connection) -> None:
        """Initialize database with schema."""
        try:
            conn.executescript(self.schema)
            logger.info("Database initialized with schema")
        except sqlite3.Error as e:
            logger.error(f"Schema initialization failed: {e}")
            raise
    
    def store_feedback_report(
        self, 
        app_name: str, 
        report_data: Dict[str, Any],
        gist_url: Optional[str] = None
    ) -> Tuple[bool, Optional[int], str]:
        """
        Store feedback report in per-app database.
        
        Args:
            app_name: Application name
            report_data: Complete feedback report dictionary
            gist_url: Optional GitHub Gist URL
        
        Returns:
            (success, report_id, message)
        """
        try:
            # Calculate report hash for deduplication
            report_hash = self._calculate_report_hash(report_data)
            
            with self.get_connection(app_name=app_name) as conn:
                cursor = conn.cursor()
                
                # Check if report already exists
                cursor.execute(
                    "SELECT id FROM feedback_reports WHERE report_hash = ?",
                    (report_hash,)
                )
                existing = cursor.fetchone()
                
                if existing:
                    return False, existing['id'], "Report already exists (duplicate)"
                
                # Insert master report
                timestamp = report_data.get('timestamp', datetime.now().isoformat())
                privacy_level = report_data.get('privacy_level', 'full')
                
                cursor.execute("""
                    INSERT INTO feedback_reports 
                    (app_name, report_timestamp, report_hash, gist_url, privacy_level, 
                     synced_from_gist, validation_status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    app_name,
                    timestamp,
                    report_hash,
                    gist_url,
                    privacy_level,
                    1 if gist_url else 0,
                    'valid'
                ))
                
                report_id = cursor.lastrowid
                
                # Insert metrics into respective tables
                metrics = report_data.get('metrics', {})
                
                self._insert_application_metrics(cursor, report_id, metrics.get('application_metrics', {}))
                self._insert_crawler_performance(cursor, report_id, metrics.get('crawler_performance', {}))
                self._insert_cortex_performance(cursor, report_id, metrics.get('cortex_performance', {}))
                self._insert_knowledge_graphs(cursor, report_id, metrics.get('knowledge_graph', {}))
                self._insert_development_hygiene(cursor, report_id, metrics.get('development_hygiene', {}))
                self._insert_tdd_mastery(cursor, report_id, metrics.get('tdd_mastery', {}))
                self._insert_commit_metrics(cursor, report_id, metrics.get('commit_metrics', {}))
                self._insert_velocity_metrics(cursor, report_id, metrics.get('velocity_metrics', {}))
                
                logger.info(f"Stored feedback report for {app_name} (ID: {report_id})")
                return True, report_id, "Report stored successfully"
        
        except sqlite3.IntegrityError as e:
            logger.error(f"Integrity error storing report: {e}")
            return False, None, f"Database integrity error: {str(e)}"
        except Exception as e:
            logger.error(f"Error storing report: {e}", exc_info=True)
            return False, None, f"Storage error: {str(e)}"
    
    def _calculate_report_hash(self, report_data: Dict[str, Any]) -> str:
        """Calculate SHA256 hash of report for deduplication."""
        # Use sorted JSON to ensure consistent hashing
        report_str = json.dumps(report_data, sort_keys=True, default=str)
        return hashlib.sha256(report_str.encode('utf-8')).hexdigest()
    
    def _insert_application_metrics(self, cursor: sqlite3.Cursor, report_id: int, metrics: Dict[str, Any]) -> None:
        """Insert application metrics."""
        cursor.execute("""
            INSERT INTO application_metrics 
            (report_id, project_size_mb, lines_of_code, file_count, tech_stack, 
             test_coverage, complexity_score, dependency_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            report_id,
            metrics.get('project_size_mb'),
            metrics.get('lines_of_code'),
            metrics.get('file_count'),
            json.dumps(metrics.get('tech_stack', [])),
            metrics.get('test_coverage'),
            metrics.get('complexity_score'),
            metrics.get('dependency_count')
        ))
    
    def _insert_crawler_performance(self, cursor: sqlite3.Cursor, report_id: int, metrics: Dict[str, Any]) -> None:
        """Insert crawler performance metrics."""
        cursor.execute("""
            INSERT INTO crawler_performance 
            (report_id, discovery_runs, success_rate, cache_hit_rate, 
             avg_discovery_time, elements_discovered, error_count)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            report_id,
            metrics.get('discovery_runs'),
            metrics.get('success_rate'),
            metrics.get('cache_hit_rate'),
            metrics.get('avg_discovery_time'),
            metrics.get('elements_discovered'),
            metrics.get('error_count')
        ))
    
    def _insert_cortex_performance(self, cursor: sqlite3.Cursor, report_id: int, metrics: Dict[str, Any]) -> None:
        """Insert CORTEX performance metrics."""
        brain_sizes = metrics.get('brain_db_sizes', {})
        cursor.execute("""
            INSERT INTO cortex_performance 
            (report_id, avg_operation_time, brain_db_size_mb, tier1_size_mb, 
             tier2_size_mb, tier3_size_mb, token_efficiency, memory_usage_mb)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            report_id,
            metrics.get('avg_operation_time'),
            brain_sizes.get('total'),
            brain_sizes.get('tier1'),
            brain_sizes.get('tier2'),
            brain_sizes.get('tier3'),
            metrics.get('token_efficiency'),
            metrics.get('memory_usage_mb')
        ))
    
    def _insert_knowledge_graphs(self, cursor: sqlite3.Cursor, report_id: int, metrics: Dict[str, Any]) -> None:
        """Insert knowledge graph metrics."""
        cursor.execute("""
            INSERT INTO knowledge_graphs 
            (report_id, entity_count, relationship_count, graph_density, 
             update_frequency, unique_patterns)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            report_id,
            metrics.get('entity_count'),
            metrics.get('relationship_count'),
            metrics.get('graph_density'),
            metrics.get('update_frequency'),
            metrics.get('unique_patterns')
        ))
    
    def _insert_development_hygiene(self, cursor: sqlite3.Cursor, report_id: int, metrics: Dict[str, Any]) -> None:
        """Insert development hygiene metrics."""
        cursor.execute("""
            INSERT INTO development_hygiene 
            (report_id, clean_commit_rate, branch_strategy_score, security_vulnerabilities, 
             code_review_coverage, documentation_coverage, linting_pass_rate)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            report_id,
            metrics.get('clean_commit_rate'),
            metrics.get('branch_strategy_score'),
            metrics.get('security_vulnerabilities'),
            metrics.get('code_review_coverage'),
            metrics.get('documentation_coverage'),
            metrics.get('linting_pass_rate')
        ))
    
    def _insert_tdd_mastery(self, cursor: sqlite3.Cursor, report_id: int, metrics: Dict[str, Any]) -> None:
        """Insert TDD mastery metrics."""
        cursor.execute("""
            INSERT INTO tdd_mastery 
            (report_id, test_coverage, test_first_adherence, first_run_success_rate, 
             coverage_trend, test_count, assertion_count)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            report_id,
            metrics.get('test_coverage'),
            metrics.get('test_first_adherence'),
            metrics.get('first_run_success_rate'),
            metrics.get('coverage_trend'),
            metrics.get('test_count'),
            metrics.get('assertion_count')
        ))
    
    def _insert_commit_metrics(self, cursor: sqlite3.Cursor, report_id: int, metrics: Dict[str, Any]) -> None:
        """Insert commit metrics."""
        cursor.execute("""
            INSERT INTO commit_metrics 
            (report_id, build_success_rate, deployment_frequency, rollback_rate, 
             mttr_hours, commit_count, avg_commit_size)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            report_id,
            metrics.get('build_success_rate'),
            metrics.get('deployment_frequency'),
            metrics.get('rollback_rate'),
            metrics.get('mttr_hours'),
            metrics.get('commit_count'),
            metrics.get('avg_commit_size')
        ))
    
    def _insert_velocity_metrics(self, cursor: sqlite3.Cursor, report_id: int, metrics: Dict[str, Any]) -> None:
        """Insert velocity metrics."""
        cursor.execute("""
            INSERT INTO velocity_metrics 
            (report_id, sprint_velocity, cycle_time_days, estimate_accuracy, 
             lead_time_days, throughput, wip_count)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            report_id,
            metrics.get('sprint_velocity'),
            metrics.get('cycle_time_days'),
            metrics.get('estimate_accuracy'),
            metrics.get('lead_time_days'),
            metrics.get('throughput'),
            metrics.get('wip_count')
        ))
    
    def get_latest_metrics(self, app_name: str) -> Optional[Dict[str, Any]]:
        """Get latest metrics for an application."""
        try:
            with self.get_connection(app_name=app_name) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM latest_metrics WHERE app_name = ?", (app_name,))
                row = cursor.fetchone()
                
                if row:
                    return dict(row)
                return None
        except Exception as e:
            logger.error(f"Error fetching latest metrics: {e}")
            return None
    
    def get_health_score(self, app_name: str) -> Optional[float]:
        """Get application health score (0-100)."""
        try:
            with self.get_connection(app_name=app_name) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT health_score FROM application_health_scores WHERE app_name = ?",
                    (app_name,)
                )
                row = cursor.fetchone()
                
                if row:
                    return row['health_score']
                return None
        except Exception as e:
            logger.error(f"Error fetching health score: {e}")
            return None
    
    def get_critical_issues(self, app_name: str) -> List[Dict[str, Any]]:
        """Get critical unresolved issues."""
        try:
            with self.get_connection(app_name=app_name) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT issue_type, severity, message, detected_at, metric_value
                    FROM issues_reported
                    WHERE app_name = ? AND severity = 'critical' AND resolved_at IS NULL
                    ORDER BY detected_at DESC
                """, (app_name,))
                
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error fetching critical issues: {e}")
            return []
    
    def backup_database(self, app_name: str) -> Optional[Path]:
        """Create backup of application database."""
        try:
            app_db_dir = self.per_app_dir / app_name
            source_db = app_db_dir / "metrics.db"
            
            if not source_db.exists():
                logger.warning(f"Database not found for {app_name}")
                return None
            
            # Create timestamped backup
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            backup_subdir = self.backup_dir / app_name
            backup_subdir.mkdir(parents=True, exist_ok=True)
            
            backup_path = backup_subdir / f"metrics-backup-{timestamp}.db"
            
            # SQLite backup using VACUUM INTO
            with sqlite3.connect(str(source_db)) as conn:
                conn.execute(f"VACUUM INTO '{backup_path}'")
            
            logger.info(f"Database backup created: {backup_path}")
            return backup_path
        
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return None
    
    def vacuum_databases(self, app_name: Optional[str] = None) -> int:
        """
        Vacuum databases to reclaim space and optimize.
        
        Args:
            app_name: Specific app to vacuum, or None for all
        
        Returns:
            Number of databases vacuumed
        """
        count = 0
        
        try:
            if app_name:
                apps = [app_name]
            else:
                # Get all app directories
                apps = [d.name for d in self.per_app_dir.iterdir() if d.is_dir()]
            
            for app in apps:
                try:
                    with self.get_connection(app_name=app) as conn:
                        conn.execute("VACUUM")
                        count += 1
                        logger.info(f"Vacuumed database for {app}")
                except Exception as e:
                    logger.error(f"Failed to vacuum {app}: {e}")
            
            # Also vacuum aggregate DB
            try:
                with self.get_connection(aggregate=True) as conn:
                    conn.execute("VACUUM")
                    count += 1
                    logger.info("Vacuumed aggregate database")
            except Exception as e:
                logger.error(f"Failed to vacuum aggregate DB: {e}")
        
        except Exception as e:
            logger.error(f"Vacuum operation failed: {e}")
        
        return count
