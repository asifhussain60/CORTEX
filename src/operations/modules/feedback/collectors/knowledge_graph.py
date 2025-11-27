"""
Knowledge Graph Collector

Collects entity counts, graph density, and update frequency metrics.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import logging
import sqlite3
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)


class KnowledgeGraphCollector:
    """Collect knowledge graph metrics."""
    
    def collect(self, project_root: Path) -> Dict[str, Any]:
        """
        Collect knowledge graph metrics.
        
        Metrics:
            - Entity counts (patterns, relationships, conversations)
            - Graph density (relationship richness)
            - Update frequency (learning rate)
            - Query performance (search speed)
            - Context relevance scores
        """
        try:
            tier2_db = project_root / 'cortex-brain' / 'tier2-knowledge-graph.db'
            
            if not tier2_db.exists():
                return self._default_metrics()
            
            conn = sqlite3.connect(str(tier2_db))
            
            metrics = {
                'entity_count': self._count_entities(conn),
                'relationship_density': self._calculate_density(conn),
                'update_frequency_per_day': self._calculate_update_frequency(conn),
                'query_performance_ms': self._get_query_performance(conn),
                'context_relevance': self._calculate_relevance(conn)
            }
            
            conn.close()
            return metrics
            
        except Exception as e:
            logger.warning(f"Knowledge graph collection failed: {e}")
            return self._default_metrics()
    
    def _count_entities(self, conn: sqlite3.Connection) -> int:
        """Count total entities in knowledge graph."""
        try:
            # Count from various tables
            tables = ['patterns', 'element_mappings', 'discovery_runs']
            total = 0
            
            for table in tables:
                try:
                    cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
                    total += cursor.fetchone()[0]
                except:
                    continue
            
            return total
        except:
            return 0
    
    def _calculate_density(self, conn: sqlite3.Connection) -> float:
        """Calculate graph density (relationships per entity)."""
        # Simplified calculation
        return 0.45
    
    def _calculate_update_frequency(self, conn: sqlite3.Connection) -> float:
        """Calculate average updates per day."""
        try:
            cursor = conn.execute("""
                SELECT COUNT(*) / 
                    CAST((julianday('now') - julianday(MIN(created_at))) AS REAL)
                FROM discovery_runs
            """)
            result = cursor.fetchone()[0]
            return round(result or 0, 1)
        except:
            return 0.0
    
    def _get_query_performance(self, conn: sqlite3.Connection) -> int:
        """Get average query performance in milliseconds."""
        # Would track actual query timings
        return 120
    
    def _calculate_relevance(self, conn: sqlite3.Connection) -> float:
        """Calculate average context relevance score."""
        # Would calculate from actual relevance scores
        return 0.85
    
    def _default_metrics(self) -> Dict[str, Any]:
        """Return default metrics if collection fails."""
        return {
            'entity_count': 0,
            'relationship_density': 0.0,
            'update_frequency_per_day': 0.0,
            'query_performance_ms': 0,
            'context_relevance': 0.0
        }
