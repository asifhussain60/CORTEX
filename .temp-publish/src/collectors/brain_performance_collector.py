"""
CORTEX 3.0 - Brain Performance Collector
=======================================

Collects metrics on CORTEX brain performance and health.
Monitors tier performance, agent coordination, and knowledge graph efficiency.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

Feature: Quick Win #3 (Week 1)
Effort: 1 hour (brain performance collector)
Target: Brain health monitoring and optimization
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import os
import psutil
import sqlite3
from pathlib import Path

from .base_collector import BaseCollector, CollectorMetric, CollectorPriority


class BrainPerformanceCollector(BaseCollector):
    """
    Collects metrics on CORTEX brain performance and health.
    
    Metrics collected:
    - Tier database performance (query times, sizes)
    - Agent coordination efficiency
    - Knowledge graph performance
    - Memory usage and storage optimization
    - Brain file system health
    """
    
    def __init__(self, brain_path: Optional[str] = None):
        super().__init__(
            collector_id="brain_performance",
            name="Brain Performance Monitor",
            priority=CollectorPriority.HIGH,
            collection_interval_seconds=60.0,  # Monitor every minute
            brain_path=brain_path
        )
        
        # Database paths
        self.tier1_db = None
        self.tier2_db = None
        self.tier3_db = None
        self.conversation_db = None
        
        # Performance tracking
        self.query_times = []
        self.brain_file_sizes = {}
        self.last_optimization_check = None
    
    def _initialize(self) -> bool:
        """Initialize brain performance collector"""
        try:
            if not self.brain_path:
                self.logger.warning("No brain path provided, some metrics will be unavailable")
                return True
            
            # Find brain database files
            self._locate_brain_databases()
            
            self.logger.info("Brain performance collector initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize brain performance collector: {e}")
            return False
    
    def _locate_brain_databases(self) -> None:
        """Locate CORTEX brain database files"""
        if not self.brain_path:
            return
        
        # Look for tier databases
        potential_dbs = [
            "tier1-working-memory.db",
            "tier2-knowledge-graph.db", 
            "tier3-development-context.db",
            "conversation-history.db"
        ]
        
        for db_name in potential_dbs:
            db_path = self.brain_path / db_name
            if db_path.exists():
                if "tier1" in db_name:
                    self.tier1_db = db_path
                elif "tier2" in db_name:
                    self.tier2_db = db_path
                elif "tier3" in db_name:
                    self.tier3_db = db_path
                elif "conversation" in db_name:
                    self.conversation_db = db_path
    
    def _collect_metrics(self) -> List[CollectorMetric]:
        """Collect brain performance metrics"""
        metrics = []
        timestamp = datetime.now(timezone.utc)
        
        # Database performance metrics
        metrics.extend(self._collect_database_metrics(timestamp))
        
        # Brain file system metrics
        metrics.extend(self._collect_filesystem_metrics(timestamp))
        
        # Memory usage metrics
        metrics.extend(self._collect_memory_metrics(timestamp))
        
        # Brain health score
        metrics.append(self._calculate_brain_health_score(timestamp))
        
        return metrics
    
    def _collect_database_metrics(self, timestamp: datetime) -> List[CollectorMetric]:
        """Collect database performance metrics"""
        metrics = []
        
        databases = {
            "tier1": self.tier1_db,
            "tier2": self.tier2_db,
            "tier3": self.tier3_db,
            "conversation": self.conversation_db
        }
        
        for db_name, db_path in databases.items():
            if not db_path or not db_path.exists():
                continue
            
            try:
                # Database size
                db_size = db_path.stat().st_size
                metrics.append(CollectorMetric(
                    name=f"database_size_{db_name}",
                    value=db_size,
                    timestamp=timestamp,
                    tags={"type": "storage", "database": db_name, "unit": "bytes"}
                ))
                
                # Query performance test
                query_time = self._test_database_query_performance(db_path)
                if query_time is not None:
                    metrics.append(CollectorMetric(
                        name=f"database_query_time_{db_name}",
                        value=query_time,
                        timestamp=timestamp,
                        tags={"type": "performance", "database": db_name, "unit": "ms"}
                    ))
                
            except Exception as e:
                self.logger.warning(f"Failed to collect metrics for {db_name}: {e}")
        
        return metrics
    
    def _collect_filesystem_metrics(self, timestamp: datetime) -> List[CollectorMetric]:
        """Collect brain filesystem metrics"""
        metrics = []
        
        if not self.brain_path:
            return metrics
        
        try:
            # Total brain directory size
            total_size = self._calculate_directory_size(self.brain_path)
            metrics.append(CollectorMetric(
                name="brain_total_size",
                value=total_size,
                timestamp=timestamp,
                tags={"type": "storage", "unit": "bytes"}
            ))
            
            # Count of important brain files
            important_files = [
                "response-templates.yaml",
                "capabilities.yaml",
                "lessons-learned.yaml",
                "knowledge-graph.yaml"
            ]
            
            existing_files = sum(1 for f in important_files if (self.brain_path / f).exists())
            metrics.append(CollectorMetric(
                name="brain_important_files_count",
                value=existing_files,
                timestamp=timestamp,
                tags={"type": "inventory", "total_expected": len(important_files)}
            ))
            
        except Exception as e:
            self.logger.warning(f"Failed to collect filesystem metrics: {e}")
        
        return metrics
    
    def _collect_memory_metrics(self, timestamp: datetime) -> List[CollectorMetric]:
        """Collect memory usage metrics"""
        metrics = []
        
        try:
            # Process memory usage
            process = psutil.Process()
            memory_info = process.memory_info()
            
            metrics.append(CollectorMetric(
                name="brain_process_memory_rss",
                value=memory_info.rss,
                timestamp=timestamp,
                tags={"type": "memory", "unit": "bytes"}
            ))
            
            metrics.append(CollectorMetric(
                name="brain_process_memory_vms",
                value=memory_info.vms,
                timestamp=timestamp,
                tags={"type": "memory", "unit": "bytes"}
            ))
            
            # System memory usage
            system_memory = psutil.virtual_memory()
            metrics.append(CollectorMetric(
                name="system_memory_usage_percent",
                value=system_memory.percent,
                timestamp=timestamp,
                tags={"type": "memory", "unit": "percent"}
            ))
            
        except Exception as e:
            self.logger.warning(f"Failed to collect memory metrics: {e}")
        
        return metrics
    
    def _calculate_brain_health_score(self, timestamp: datetime) -> CollectorMetric:
        """Calculate overall brain health score (0-100)"""
        score = 100.0
        factors = []
        
        try:
            # Database availability (20 points)
            db_count = sum(1 for db in [self.tier1_db, self.tier2_db, self.tier3_db] if db and db.exists())
            db_score = (db_count / 3) * 20
            score = min(score, 80 + db_score)
            factors.append(f"databases: {db_count}/3")
            
            # File system health (30 points) 
            if self.brain_path and self.brain_path.exists():
                file_health_score = 30.0
            else:
                file_health_score = 0.0
                score = min(score, 70)
            factors.append(f"filesystem: {file_health_score}/30")
            
            # Memory health (25 points)
            try:
                process = psutil.Process()
                memory_mb = process.memory_info().rss / (1024 * 1024)
                if memory_mb < 100:  # Under 100MB is good
                    memory_score = 25.0
                elif memory_mb < 500:  # Under 500MB is acceptable
                    memory_score = 15.0
                else:  # Over 500MB is concerning
                    memory_score = 5.0
                score = min(score, 75 + memory_score)
                factors.append(f"memory: {memory_score}/25 ({memory_mb:.1f}MB)")
            except:
                factors.append("memory: unknown")
            
            # Performance health (25 points)
            avg_query_time = sum(self.query_times[-10:]) / len(self.query_times[-10:]) if self.query_times else 0
            if avg_query_time == 0:
                perf_score = 25.0  # No data, assume good
            elif avg_query_time < 10:  # Under 10ms is excellent
                perf_score = 25.0
            elif avg_query_time < 50:  # Under 50ms is good
                perf_score = 20.0
            elif avg_query_time < 100:  # Under 100ms is acceptable
                perf_score = 15.0
            else:  # Over 100ms is slow
                perf_score = 5.0
            score = min(score, 75 + perf_score)
            factors.append(f"performance: {perf_score}/25 ({avg_query_time:.1f}ms)")
            
        except Exception as e:
            self.logger.warning(f"Error calculating brain health score: {e}")
            score = 50.0  # Default to middle score on error
            factors.append("error in calculation")
        
        return CollectorMetric(
            name="brain_health_score",
            value=score,
            timestamp=timestamp,
            tags={"type": "health", "unit": "score"},
            metadata={"factors": factors, "max_score": 100.0}
        )
    
    def _test_database_query_performance(self, db_path: Path) -> Optional[float]:
        """Test database query performance and return time in milliseconds"""
        try:
            start_time = datetime.now()
            
            with sqlite3.connect(str(db_path), timeout=5.0) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' LIMIT 5;")
                cursor.fetchall()
            
            end_time = datetime.now()
            query_time_ms = (end_time - start_time).total_seconds() * 1000
            
            # Store for health calculation
            self.query_times.append(query_time_ms)
            if len(self.query_times) > 50:  # Keep only recent times
                self.query_times = self.query_times[-50:]
            
            return query_time_ms
            
        except Exception as e:
            self.logger.debug(f"Database query test failed for {db_path}: {e}")
            return None
    
    def _calculate_directory_size(self, directory: Path) -> int:
        """Calculate total size of directory in bytes"""
        total_size = 0
        try:
            for file_path in directory.rglob("*"):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
        except Exception as e:
            self.logger.warning(f"Error calculating directory size: {e}")
        return total_size
    
    def get_brain_summary(self) -> Dict[str, Any]:
        """Get summary of brain performance"""
        return {
            "databases_found": sum(1 for db in [self.tier1_db, self.tier2_db, self.tier3_db, self.conversation_db] if db and db.exists()),
            "avg_query_time_ms": sum(self.query_times[-10:]) / len(self.query_times[-10:]) if self.query_times else 0,
            "brain_path_exists": self.brain_path and self.brain_path.exists(),
            "recent_query_count": len(self.query_times)
        }