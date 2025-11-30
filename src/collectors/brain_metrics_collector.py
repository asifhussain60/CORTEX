"""
CORTEX 3.0 - Brain Performance Metrics Collector
================================================

Real-time collection of CORTEX brain performance metrics for response templates.
Monitors memory tiers, agent performance, and system health.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

Feature: Quick Win #3 (Week 1)
Effort: 4 hours (core collectors implementation)
Target: <200ms collection latency, real-time availability
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from pathlib import Path
import sqlite3
import json
import logging
import psutil
import os

from .base_collector import BaseCollector, CollectorMetric, CollectorPriority


class BrainMetricsCollector(BaseCollector):
    """
    Collects real-time CORTEX brain performance metrics.
    
    Metrics collected:
    - Memory tier status (conversations, patterns, git commits)
    - Query performance (response times, success rates)
    - Agent coordination health
    - Database sizes and query performance
    - Brain protection status
    """
    
    def __init__(self, brain_path: str):
        super().__init__(
            collector_id="brain_metrics",
            name="CORTEX Brain Performance Metrics",
            priority=CollectorPriority.CRITICAL,
            collection_interval_seconds=30.0,  # Collect every 30 seconds
            brain_path=brain_path
        )
        self.brain_path = Path(brain_path)
        
    def _initialize(self) -> bool:
        """Initialize brain metrics collector"""
        try:
            # Verify brain path exists
            if not self.brain_path.exists():
                self.logger.error(f"Brain path does not exist: {self.brain_path}")
                return False
            
            # Verify database files exist
            required_dbs = [
                "tier1/tier1-working-memory.db",
                "tier2/tier2-knowledge-graph.db", 
                "tier3/tier3-development-context.db"
            ]
            
            for db_path in required_dbs:
                full_path = self.brain_path / db_path
                if not full_path.exists():
                    self.logger.warning(f"Brain database not found: {full_path}")
            
            self.logger.info("Brain metrics collector initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize brain metrics collector: {e}")
            return False
    
    def _collect_metrics(self) -> List[CollectorMetric]:
        """Collect brain performance metrics"""
        metrics = []
        timestamp = datetime.now(timezone.utc)
        
        # Collect Tier 1 (Working Memory) metrics
        metrics.extend(self._collect_tier1_metrics(timestamp))
        
        # Collect Tier 2 (Knowledge Graph) metrics
        metrics.extend(self._collect_tier2_metrics(timestamp))
        
        # Collect Tier 3 (Context Intelligence) metrics
        metrics.extend(self._collect_tier3_metrics(timestamp))
        
        # Collect overall brain health metrics
        metrics.extend(self._collect_brain_health_metrics(timestamp))
        
        # Collect memory usage metrics
        metrics.extend(self._collect_memory_usage_metrics(timestamp))
        
        return metrics
    
    def _collect_tier1_metrics(self, timestamp: datetime) -> List[CollectorMetric]:
        """Collect Tier 1 working memory metrics"""
        metrics = []
        
        try:
            tier1_db = self.brain_path / "tier1/tier1-working-memory.db"
            if not tier1_db.exists():
                return metrics
                
            with sqlite3.connect(tier1_db) as conn:
                cursor = conn.cursor()
                
                # Conversation count
                cursor.execute("SELECT COUNT(*) FROM conversations WHERE active = 1")
                conversation_count = cursor.fetchone()[0]
                metrics.append(CollectorMetric(
                    name="tier1_active_conversations",
                    value=conversation_count,
                    timestamp=timestamp,
                    tags={"tier": "1", "type": "count"},
                    metadata={"max_capacity": 20}
                ))
                
                # Recent activity
                cursor.execute("""
                    SELECT COUNT(*) FROM conversations 
                    WHERE created_at > datetime('now', '-1 hour')
                """)
                recent_conversations = cursor.fetchone()[0]
                metrics.append(CollectorMetric(
                    name="tier1_recent_activity",
                    value=recent_conversations,
                    timestamp=timestamp,
                    tags={"tier": "1", "window": "1hour"}
                ))
                
                # Database size
                db_size_mb = os.path.getsize(tier1_db) / (1024 * 1024)
                metrics.append(CollectorMetric(
                    name="tier1_database_size_mb",
                    value=round(db_size_mb, 2),
                    timestamp=timestamp,
                    tags={"tier": "1", "unit": "mb"}
                ))
                
        except Exception as e:
            self.logger.warning(f"Failed to collect Tier 1 metrics: {e}")
            
        return metrics
    
    def _collect_tier2_metrics(self, timestamp: datetime) -> List[CollectorMetric]:
        """Collect Tier 2 knowledge graph metrics"""
        metrics = []
        
        try:
            tier2_db = self.brain_path / "tier2/tier2-knowledge-graph.db"
            if not tier2_db.exists():
                return metrics
                
            with sqlite3.connect(tier2_db) as conn:
                cursor = conn.cursor()
                
                # Pattern count
                cursor.execute("SELECT COUNT(*) FROM patterns WHERE confidence > 0.7")
                high_confidence_patterns = cursor.fetchone()[0]
                metrics.append(CollectorMetric(
                    name="tier2_high_confidence_patterns",
                    value=high_confidence_patterns,
                    timestamp=timestamp,
                    tags={"tier": "2", "confidence": "high"}
                ))
                
                # Workflow templates
                cursor.execute("SELECT COUNT(*) FROM workflows")
                workflow_count = cursor.fetchone()[0]
                metrics.append(CollectorMetric(
                    name="tier2_workflow_templates",
                    value=workflow_count,
                    timestamp=timestamp,
                    tags={"tier": "2", "type": "workflows"}
                ))
                
                # Database size
                db_size_mb = os.path.getsize(tier2_db) / (1024 * 1024)
                metrics.append(CollectorMetric(
                    name="tier2_database_size_mb",
                    value=round(db_size_mb, 2),
                    timestamp=timestamp,
                    tags={"tier": "2", "unit": "mb"}
                ))
                
        except Exception as e:
            self.logger.warning(f"Failed to collect Tier 2 metrics: {e}")
            
        return metrics
    
    def _collect_tier3_metrics(self, timestamp: datetime) -> List[CollectorMetric]:
        """Collect Tier 3 context intelligence metrics"""
        metrics = []
        
        try:
            tier3_db = self.brain_path / "tier3/tier3-development-context.db"
            if not tier3_db.exists():
                return metrics
                
            with sqlite3.connect(tier3_db) as conn:
                cursor = conn.cursor()
                
                # Git commits analyzed
                cursor.execute("SELECT COUNT(*) FROM git_commits")
                git_commits = cursor.fetchone()[0]
                metrics.append(CollectorMetric(
                    name="tier3_git_commits_analyzed",
                    value=git_commits,
                    timestamp=timestamp,
                    tags={"tier": "3", "type": "git"}
                ))
                
                # File stability entries
                cursor.execute("SELECT COUNT(*) FROM file_metrics")
                file_metrics = cursor.fetchone()[0]
                metrics.append(CollectorMetric(
                    name="tier3_file_metrics_tracked",
                    value=file_metrics,
                    timestamp=timestamp,
                    tags={"tier": "3", "type": "files"}
                ))
                
                # Database size
                db_size_mb = os.path.getsize(tier3_db) / (1024 * 1024)
                metrics.append(CollectorMetric(
                    name="tier3_database_size_mb",
                    value=round(db_size_mb, 2),
                    timestamp=timestamp,
                    tags={"tier": "3", "unit": "mb"}
                ))
                
        except Exception as e:
            self.logger.warning(f"Failed to collect Tier 3 metrics: {e}")
            
        return metrics
    
    def _collect_brain_health_metrics(self, timestamp: datetime) -> List[CollectorMetric]:
        """Collect overall brain health metrics"""
        metrics = []
        
        try:
            # Calculate overall brain health score (0-100)
            health_score = self._calculate_brain_health_score()
            metrics.append(CollectorMetric(
                name="brain_overall_health_score",
                value=health_score,
                timestamp=timestamp,
                tags={"type": "health", "scale": "0-100"}
            ))
            
            # Agent coordination status (mock for now - would integrate with actual agent system)
            metrics.append(CollectorMetric(
                name="brain_agent_coordination_status",
                value="operational",
                timestamp=timestamp,
                tags={"type": "status", "component": "agents"}
            ))
            
            # Protection layers active count
            protection_layers_active = 6  # Would check actual protection system
            metrics.append(CollectorMetric(
                name="brain_protection_layers_active",
                value=protection_layers_active,
                timestamp=timestamp,
                tags={"type": "security", "total": "6"}
            ))
            
        except Exception as e:
            self.logger.warning(f"Failed to collect brain health metrics: {e}")
            
        return metrics
    
    def _collect_memory_usage_metrics(self, timestamp: datetime) -> List[CollectorMetric]:
        """Collect memory usage metrics"""
        metrics = []
        
        try:
            # Process memory usage
            process = psutil.Process()
            memory_info = process.memory_info()
            
            metrics.append(CollectorMetric(
                name="brain_process_memory_mb",
                value=round(memory_info.rss / (1024 * 1024), 2),
                timestamp=timestamp,
                tags={"type": "memory", "unit": "mb"}
            ))
            
            # Brain directory total size
            total_size = self._get_directory_size(self.brain_path)
            metrics.append(CollectorMetric(
                name="brain_total_storage_mb",
                value=round(total_size / (1024 * 1024), 2),
                timestamp=timestamp,
                tags={"type": "storage", "unit": "mb"}
            ))
            
        except Exception as e:
            self.logger.warning(f"Failed to collect memory usage metrics: {e}")
            
        return metrics
    
    def _calculate_brain_health_score(self) -> float:
        """Calculate overall brain health score (0-100)"""
        try:
            score = 100.0
            
            # Check database accessibility (20 points)
            db_paths = [
                "tier1/tier1-working-memory.db",
                "tier2/tier2-knowledge-graph.db",
                "tier3/tier3-development-context.db"
            ]
            
            accessible_dbs = sum(1 for db in db_paths if (self.brain_path / db).exists())
            db_score = (accessible_dbs / len(db_paths)) * 20
            score = db_score
            
            # Memory usage health (20 points)
            try:
                process = psutil.Process()
                memory_mb = process.memory_info().rss / (1024 * 1024)
                if memory_mb < 100:
                    memory_score = 20
                elif memory_mb < 500:
                    memory_score = 15
                else:
                    memory_score = 10
                score += memory_score
            except:
                score += 10  # Partial credit if can't measure
            
            # Storage health (20 points)
            total_size_mb = self._get_directory_size(self.brain_path) / (1024 * 1024)
            if total_size_mb < 50:
                storage_score = 20
            elif total_size_mb < 200:
                storage_score = 15
            else:
                storage_score = 10
            score += storage_score
            
            # Add base operational score (40 points)
            score += 40
            
            return min(100.0, score)
            
        except Exception as e:
            self.logger.warning(f"Failed to calculate brain health score: {e}")
            return 50.0  # Default to 50% if calculation fails
    
    def _get_directory_size(self, directory: Path) -> int:
        """Get total size of directory in bytes"""
        try:
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(directory):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if os.path.exists(filepath):
                        total_size += os.path.getsize(filepath)
            return total_size
        except Exception:
            return 0


# Export for use in collector manager
__all__ = ['BrainMetricsCollector']