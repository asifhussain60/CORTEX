"""
CORTEX Brain Connector - Interface to CORTEX Brain Knowledge Systems
Feature 5.1: Brain Database Integration

Provides secure, efficient access to CORTEX Brain's Tier 2 Knowledge Graph and development
context systems for documentation pattern learning and adaptive generation.
"""

import sqlite3
import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging


@dataclass
class PatternRecord:
    """Represents a pattern from Tier 2 knowledge graph"""
    pattern_id: str
    name: str
    category: str
    description: str
    confidence: float
    usage_count: int
    success_count: int
    failure_count: int
    tags: List[str]
    code_snippet: Optional[str] = None
    file_path: Optional[str] = None
    created_at: Optional[str] = None
    last_used: Optional[str] = None


@dataclass
class QualityMetrics:
    """Quality metrics for documentation generation feedback"""
    generation_id: str
    quality_score: float
    readability_score: float
    completeness_score: float
    accuracy_score: float
    user_rating: Optional[int] = None
    feedback_notes: Optional[str] = None
    timestamp: Optional[str] = None


class BrainConnector:
    """
    Secure connector to CORTEX Brain knowledge systems with read-only access
    to pattern learning data and safe write access for documentation metrics.
    """
    
    def __init__(self, brain_root: Optional[Path] = None):
        """
        Initialize connection to CORTEX Brain systems
        
        Args:
            brain_root: Path to cortex-brain directory (auto-detected if None)
        """
        self.logger = logging.getLogger(__name__)
        
        # Auto-detect brain root if not provided
        if brain_root is None:
            current = Path.cwd()
            for parent in [current] + list(current.parents):
                candidate = parent / "cortex-brain"
                if candidate.exists() and candidate.is_dir():
                    brain_root = candidate
                    break
            
            if brain_root is None:
                raise ValueError("Could not locate cortex-brain directory")
        
        self.brain_root = Path(brain_root)
        self._validate_brain_structure()
        
        # Database paths
        self.tier2_db = self.brain_root / "tier2-knowledge-graph.db"
        self.tier3_db = self.brain_root / "tier3-development-context.db"
        
        # YAML knowledge files
        self.knowledge_graph = self.brain_root / "knowledge-graph.yaml"
        self.development_context = self.brain_root / "development-context.yaml"
        
        self._connection_cache: Dict[str, sqlite3.Connection] = {}
        
        self.logger.info(f"BrainConnector initialized: {self.brain_root}")

    def _validate_brain_structure(self):
        """Validate CORTEX Brain directory structure"""
        required_files = [
            "tier2-knowledge-graph.db",
            "tier3-development-context.db", 
            "knowledge-graph.yaml",
            "development-context.yaml"
        ]
        
        missing = []
        for file in required_files:
            if not (self.brain_root / file).exists():
                missing.append(file)
        
        if missing:
            self.logger.warning(f"Missing brain files: {missing}")

    def _get_connection(self, db_name: str) -> sqlite3.Connection:
        """Get cached database connection with read-only safety"""
        if db_name not in self._connection_cache:
            db_path = self.brain_root / f"{db_name}.db"
            
            if not db_path.exists():
                self.logger.warning(f"Database not found: {db_path}")
                # Create minimal connection for safety
                conn = sqlite3.connect(":memory:")
                conn.row_factory = sqlite3.Row
                self._connection_cache[db_name] = conn
                return conn
            
            # Open with read-only mode for safety
            conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
            conn.row_factory = sqlite3.Row
            self._connection_cache[db_name] = conn
            
        return self._connection_cache[db_name]

    def get_documentation_patterns(
        self, 
        category: Optional[str] = None,
        min_confidence: float = 0.6,
        limit: int = 50
    ) -> List[PatternRecord]:
        """
        Retrieve documentation patterns from Tier 2 knowledge graph
        
        Args:
            category: Filter by pattern category
            min_confidence: Minimum confidence threshold
            limit: Maximum patterns to return
            
        Returns:
            List of pattern records relevant to documentation generation
        """
        try:
            conn = self._get_connection("tier2-knowledge-graph")
            
            query = """
                SELECT pattern_id, name, category, description, confidence,
                       usage_count, success_count, failure_count, tags,
                       code_snippet, file_path, created_at, last_used
                FROM tier2_patterns 
                WHERE confidence >= ?
            """
            params = [min_confidence]
            
            if category:
                query += " AND category = ?"
                params.append(category)
                
            query += " ORDER BY confidence DESC, usage_count DESC LIMIT ?"
            params.append(limit)
            
            cursor = conn.execute(query, params)
            patterns = []
            
            for row in cursor.fetchall():
                tags = json.loads(row['tags']) if row['tags'] else []
                pattern = PatternRecord(
                    pattern_id=row['pattern_id'],
                    name=row['name'],
                    category=row['category'], 
                    description=row['description'],
                    confidence=row['confidence'],
                    usage_count=row['usage_count'],
                    success_count=row['success_count'],
                    failure_count=row['failure_count'],
                    tags=tags,
                    code_snippet=row['code_snippet'],
                    file_path=row['file_path'],
                    created_at=row['created_at'],
                    last_used=row['last_used']
                )
                patterns.append(pattern)
                
            self.logger.debug(f"Retrieved {len(patterns)} patterns")
            return patterns
            
        except Exception as e:
            self.logger.error(f"Error retrieving patterns: {e}")
            return []

    def search_patterns_by_intent(
        self, 
        intent: str,
        context_tags: Optional[List[str]] = None
    ) -> List[PatternRecord]:
        """
        Search patterns using FTS5 full-text search based on intent and context
        
        Args:
            intent: Documentation intent/goal
            context_tags: Context tags for relevance filtering
            
        Returns:
            List of relevant patterns sorted by relevance
        """
        try:
            conn = self._get_connection("tier2-knowledge-graph")
            
            # Use FTS5 for semantic search
            query = """
                SELECT p.pattern_id, p.name, p.category, p.description, 
                       p.confidence, p.usage_count, p.success_count, 
                       p.failure_count, p.tags, p.code_snippet, p.file_path,
                       p.created_at, p.last_used
                FROM tier2_patterns p
                JOIN tier2_patterns_fts fts ON p.rowid = fts.rowid
                WHERE tier2_patterns_fts MATCH ?
                ORDER BY rank, p.confidence DESC
                LIMIT 20
            """
            
            cursor = conn.execute(query, [intent])
            patterns = []
            
            for row in cursor.fetchall():
                tags = json.loads(row['tags']) if row['tags'] else []
                
                # Filter by context tags if provided
                if context_tags:
                    tag_overlap = set(tags) & set(context_tags)
                    if not tag_overlap:
                        continue
                
                pattern = PatternRecord(
                    pattern_id=row['pattern_id'],
                    name=row['name'],
                    category=row['category'],
                    description=row['description'],
                    confidence=row['confidence'],
                    usage_count=row['usage_count'],
                    success_count=row['success_count'],
                    failure_count=row['failure_count'],
                    tags=tags,
                    code_snippet=row['code_snippet'],
                    file_path=row['file_path'],
                    created_at=row['created_at'],
                    last_used=row['last_used']
                )
                patterns.append(pattern)
                
            self.logger.debug(f"Found {len(patterns)} patterns for intent: {intent}")
            return patterns
            
        except Exception as e:
            self.logger.error(f"Error searching patterns: {e}")
            return []

    def get_file_relationships(self, file_path: str) -> Dict[str, float]:
        """
        Get files that are frequently modified together with the given file
        
        Args:
            file_path: Path to analyze relationships for
            
        Returns:
            Dictionary mapping related file paths to confidence scores
        """
        try:
            conn = self._get_connection("tier2-knowledge-graph")
            
            query = """
                SELECT 
                    CASE WHEN file_a = ? THEN file_b ELSE file_a END as related_file,
                    confidence
                FROM tier2_file_relationships 
                WHERE file_a = ? OR file_b = ?
                ORDER BY confidence DESC
                LIMIT 20
            """
            
            cursor = conn.execute(query, [file_path, file_path, file_path])
            relationships = {}
            
            for row in cursor.fetchall():
                relationships[row['related_file']] = row['confidence']
                
            return relationships
            
        except Exception as e:
            self.logger.error(f"Error retrieving file relationships: {e}")
            return {}

    def load_knowledge_graph(self) -> Dict[str, Any]:
        """Load knowledge graph YAML with pattern insights"""
        try:
            if not self.knowledge_graph.exists():
                return {}
                
            with open(self.knowledge_graph, 'r') as f:
                return yaml.safe_load(f) or {}
                
        except Exception as e:
            self.logger.error(f"Error loading knowledge graph: {e}")
            return {}

    def load_development_context(self) -> Dict[str, Any]:
        """Load development context with project metrics"""
        try:
            if not self.development_context.exists():
                return {}
                
            with open(self.development_context, 'r') as f:
                return yaml.safe_load(f) or {}
                
        except Exception as e:
            self.logger.error(f"Error loading development context: {e}")
            return {}

    def get_recent_corrections(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get recent corrections to learn from mistakes
        
        Args:
            days: Number of days to look back
            
        Returns:
            List of correction records
        """
        try:
            conn = self._get_connection("tier2-knowledge-graph")
            
            cutoff = (datetime.now() - timedelta(days=days)).isoformat()
            
            query = """
                SELECT correction_id, timestamp, error_type, error_description,
                       correction_applied, file_path, pattern_violated,
                       is_repeat_error, times_occurred
                FROM tier2_corrections 
                WHERE timestamp >= ?
                ORDER BY timestamp DESC
            """
            
            cursor = conn.execute(query, [cutoff])
            corrections = []
            
            for row in cursor.fetchall():
                corrections.append(dict(row))
                
            return corrections
            
        except Exception as e:
            self.logger.error(f"Error retrieving corrections: {e}")
            return []

    def record_documentation_quality(self, metrics: QualityMetrics):
        """
        Record quality metrics for documentation generation feedback
        
        Args:
            metrics: Quality metrics to record
        """
        try:
            # For now, log metrics - in full implementation would write to brain
            self.logger.info(f"Quality metrics recorded: {metrics.generation_id} -> {metrics.quality_score}")
            
            # TODO: Implement safe write to brain database for quality feedback
            # This would require careful transaction handling and write permissions
            
        except Exception as e:
            self.logger.error(f"Error recording quality metrics: {e}")

    def get_template_usage_patterns(self) -> Dict[str, Dict]:
        """
        Get patterns of template usage for adaptive template selection
        
        Returns:
            Dictionary of template usage statistics and patterns
        """
        knowledge = self.load_knowledge_graph()
        
        # Extract template-related patterns
        template_patterns = {}
        
        if 'patterns' in knowledge:
            for pattern_key, pattern_data in knowledge.items():
                if 'template' in pattern_key.lower() or 'documentation' in pattern_key.lower():
                    template_patterns[pattern_key] = pattern_data
                    
        return template_patterns

    def close(self):
        """Close all database connections"""
        for conn in self._connection_cache.values():
            conn.close()
        self._connection_cache.clear()
        
        self.logger.info("BrainConnector connections closed")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def create_brain_connector(brain_root: Optional[Path] = None) -> BrainConnector:
    """
    Factory function to create BrainConnector with error handling
    
    Args:
        brain_root: Optional path to cortex-brain directory
        
    Returns:
        BrainConnector instance or None if initialization fails
    """
    try:
        return BrainConnector(brain_root)
    except Exception as e:
        logging.getLogger(__name__).error(f"Failed to create BrainConnector: {e}")
        return None