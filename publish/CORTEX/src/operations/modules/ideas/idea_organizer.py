"""
CORTEX 3.0 - Feature 1: IDEA Capture System - Organization Module

Purpose: Smart organization system for captured ideas with categorization,
         tagging, priority management, and intelligent clustering.

Core Components:
- IdeaOrganizer: Main organization engine
- CategoryManager: Auto-categorization by project/component/type
- TagSystem: Flexible tagging with hierarchical relationships
- PriorityEngine: Dynamic priority scoring and management
- ClusteringEngine: Related idea detection and grouping

Performance Requirements:
- Organization processing: <50ms per idea
- Search queries: <100ms for 10,000+ ideas
- Batch processing: 1000+ ideas/second
- Memory efficient: <10MB for 100,000 ideas

Architecture Pattern:
- Event-driven: React to idea capture events
- Pluggable: Extensible categorization rules
- Cached: Intelligent caching for fast retrieval
- Async: Non-blocking background processing

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
"""

import sqlite3
import time
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Set, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from pathlib import Path
import re
import json
from collections import defaultdict, Counter
from concurrent.futures import ThreadPoolExecutor
import hashlib

from .idea_queue import IdeaCapture


@dataclass
class IdeaCategory:
    """Represents a category classification for an idea."""
    name: str
    confidence: float
    source: str  # 'auto', 'manual', 'ml'
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'confidence': self.confidence,
            'source': self.source,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'IdeaCategory':
        return cls(
            name=data['name'],
            confidence=data['confidence'],
            source=data['source'],
            created_at=datetime.fromisoformat(data['created_at'])
        )


@dataclass
class IdeaTag:
    """Represents a tag applied to an idea."""
    name: str
    category: Optional[str] = None  # e.g., 'technology', 'priority', 'status'
    confidence: float = 1.0
    source: str = 'manual'
    parent_tag: Optional[str] = None  # For hierarchical tags
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'category': self.category,
            'confidence': self.confidence,
            'source': self.source,
            'parent_tag': self.parent_tag,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'IdeaTag':
        return cls(
            name=data['name'],
            category=data.get('category'),
            confidence=data.get('confidence', 1.0),
            source=data.get('source', 'manual'),
            parent_tag=data.get('parent_tag'),
            created_at=datetime.fromisoformat(data['created_at'])
        )


@dataclass
class IdeaCluster:
    """Represents a cluster of related ideas."""
    cluster_id: str
    ideas: List[str]  # List of idea IDs
    similarity_threshold: float
    cluster_center: Optional[str] = None  # Central idea ID
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'cluster_id': self.cluster_id,
            'ideas': self.ideas,
            'similarity_threshold': self.similarity_threshold,
            'cluster_center': self.cluster_center,
            'tags': self.tags,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'IdeaCluster':
        return cls(
            cluster_id=data['cluster_id'],
            ideas=data['ideas'],
            similarity_threshold=data['similarity_threshold'],
            cluster_center=data.get('cluster_center'),
            tags=data.get('tags', []),
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at'])
        )


class CategoryManager:
    """Manages automatic categorization of ideas."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Built-in categorization rules
        self.category_rules = {
            'feature': {
                'patterns': [
                    r'add\s+(?:new\s+)?feature',
                    r'implement\s+.*',
                    r'create\s+.*functionality',
                    r'build\s+.*component',
                    r'new\s+.*feature'
                ],
                'keywords': ['feature', 'functionality', 'component', 'module']
            },
            'bug': {
                'patterns': [
                    r'fix\s+.*bug',
                    r'resolve\s+.*issue',
                    r'debug\s+.*',
                    r'error\s+in\s+.*',
                    r'broken\s+.*'
                ],
                'keywords': ['bug', 'error', 'issue', 'broken', 'fix']
            },
            'improvement': {
                'patterns': [
                    r'improve\s+.*',
                    r'optimize\s+.*',
                    r'enhance\s+.*',
                    r'refactor\s+.*',
                    r'better\s+.*'
                ],
                'keywords': ['improve', 'optimize', 'enhance', 'refactor', 'performance']
            },
            'documentation': {
                'patterns': [
                    r'document\s+.*',
                    r'write\s+.*docs?',
                    r'update\s+.*documentation',
                    r'add\s+.*comments',
                    r'explain\s+.*'
                ],
                'keywords': ['documentation', 'docs', 'comments', 'readme', 'guide']
            },
            'testing': {
                'patterns': [
                    r'test\s+.*',
                    r'add\s+.*tests?',
                    r'unit\s+test',
                    r'integration\s+test',
                    r'validate\s+.*'
                ],
                'keywords': ['test', 'testing', 'validation', 'verify', 'check']
            },
            'security': {
                'patterns': [
                    r'security\s+.*',
                    r'auth.*',
                    r'permission.*',
                    r'encrypt.*',
                    r'secure\s+.*'
                ],
                'keywords': ['security', 'auth', 'permission', 'encrypt', 'secure']
            },
            'ui': {
                'patterns': [
                    r'ui\s+.*',
                    r'interface\s+.*',
                    r'frontend\s+.*',
                    r'design\s+.*',
                    r'layout\s+.*'
                ],
                'keywords': ['ui', 'interface', 'frontend', 'design', 'layout']
            },
            'api': {
                'patterns': [
                    r'api\s+.*',
                    r'endpoint\s+.*',
                    r'service\s+.*',
                    r'backend\s+.*',
                    r'server\s+.*'
                ],
                'keywords': ['api', 'endpoint', 'service', 'backend', 'server']
            }
        }
        
        # Component detection patterns
        self.component_patterns = {
            'auth': ['auth', 'login', 'register', 'user', 'permission'],
            'database': ['db', 'database', 'sql', 'query', 'schema'],
            'frontend': ['ui', 'interface', 'react', 'vue', 'angular', 'html', 'css'],
            'backend': ['api', 'server', 'service', 'endpoint', 'controller'],
            'testing': ['test', 'spec', 'mock', 'stub', 'unit', 'integration'],
            'deployment': ['deploy', 'docker', 'kubernetes', 'ci', 'cd', 'pipeline'],
            'monitoring': ['log', 'metric', 'alert', 'monitor', 'track'],
            'security': ['secure', 'encrypt', 'hash', 'token', 'certificate']
        }
    
    def categorize_idea(self, idea: IdeaCapture) -> List[IdeaCategory]:
        """Categorize an idea using built-in rules."""
        categories = []
        text = idea.raw_text.lower()
        
        # Check against category rules
        for category_name, rules in self.category_rules.items():
            confidence = self._calculate_category_confidence(text, rules)
            if confidence > 0.3:  # Minimum confidence threshold
                categories.append(IdeaCategory(
                    name=category_name,
                    confidence=confidence,
                    source='auto'
                ))
        
        # If no categories found, assign 'general'
        if not categories:
            categories.append(IdeaCategory(
                name='general',
                confidence=0.5,
                source='auto'
            ))
        
        return categories
    
    def _calculate_category_confidence(self, text: str, rules: Dict[str, List[str]]) -> float:
        """Calculate confidence score for a category."""
        pattern_score = 0.0
        keyword_score = 0.0
        
        # Check patterns
        for pattern in rules.get('patterns', []):
            if re.search(pattern, text, re.IGNORECASE):
                pattern_score = max(pattern_score, 0.8)
        
        # Check keywords
        keywords = rules.get('keywords', [])
        if keywords:
            found_keywords = sum(1 for keyword in keywords if keyword in text)
            keyword_score = min(found_keywords / len(keywords) * 0.6, 0.6)
        
        return max(pattern_score, keyword_score)
    
    def detect_component(self, idea: IdeaCapture) -> Optional[str]:
        """Detect the component/module this idea relates to."""
        text = idea.raw_text.lower()
        
        # Use file context if available
        if idea.active_file:
            file_path = idea.active_file.lower()
            for component, keywords in self.component_patterns.items():
                if any(keyword in file_path for keyword in keywords):
                    return component
        
        # Check text content
        component_scores = {}
        for component, keywords in self.component_patterns.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                component_scores[component] = score
        
        if component_scores:
            return max(component_scores, key=component_scores.get)
        
        return None


class TagSystem:
    """Manages flexible tagging system with hierarchical relationships."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self._init_database()
        
        # Common tag hierarchies
        self.tag_hierarchies = {
            'priority': ['critical', 'high', 'medium', 'low'],
            'status': ['new', 'active', 'paused', 'completed', 'archived'],
            'type': ['feature', 'bug', 'improvement', 'documentation', 'testing'],
            'complexity': ['simple', 'moderate', 'complex', 'very-complex'],
            'effort': ['quick-win', 'short-term', 'long-term', 'epic']
        }
    
    def _init_database(self):
        """Initialize tags database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS idea_tags (
                    idea_id TEXT,
                    tag_name TEXT,
                    tag_category TEXT,
                    confidence REAL,
                    source TEXT,
                    parent_tag TEXT,
                    created_at TEXT,
                    PRIMARY KEY (idea_id, tag_name)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tag_relationships (
                    parent_tag TEXT,
                    child_tag TEXT,
                    relationship_type TEXT,
                    PRIMARY KEY (parent_tag, child_tag)
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_idea_tags_idea_id ON idea_tags(idea_id)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_idea_tags_tag_name ON idea_tags(tag_name)
            """)
    
    def add_tag(self, idea_id: str, tag: IdeaTag) -> bool:
        """Add a tag to an idea."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO idea_tags
                    (idea_id, tag_name, tag_category, confidence, source, parent_tag, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    idea_id, tag.name, tag.category, tag.confidence,
                    tag.source, tag.parent_tag, tag.created_at.isoformat()
                ))
            return True
        except Exception as e:
            self.logger.error(f"Failed to add tag {tag.name} to idea {idea_id}: {e}")
            return False
    
    def get_tags(self, idea_id: str) -> List[IdeaTag]:
        """Get all tags for an idea."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT tag_name, tag_category, confidence, source, parent_tag, created_at
                    FROM idea_tags WHERE idea_id = ?
                """, (idea_id,))
                
                tags = []
                for row in cursor.fetchall():
                    tags.append(IdeaTag(
                        name=row[0],
                        category=row[1],
                        confidence=row[2],
                        source=row[3],
                        parent_tag=row[4],
                        created_at=datetime.fromisoformat(row[5])
                    ))
                return tags
        except Exception as e:
            self.logger.error(f"Failed to get tags for idea {idea_id}: {e}")
            return []
    
    def auto_tag_idea(self, idea: IdeaCapture) -> List[IdeaTag]:
        """Automatically generate tags for an idea."""
        tags = []
        text = idea.raw_text.lower()
        
        # Priority detection
        priority_keywords = {
            'critical': ['urgent', 'critical', 'asap', 'emergency'],
            'high': ['important', 'priority', 'soon', 'needed'],
            'low': ['later', 'someday', 'nice-to-have', 'optional']
        }
        
        for priority, keywords in priority_keywords.items():
            if any(keyword in text for keyword in keywords):
                tags.append(IdeaTag(
                    name=priority,
                    category='priority',
                    confidence=0.7,
                    source='auto'
                ))
                break
        
        # Technology detection
        tech_keywords = {
            'python': ['python', 'django', 'flask', 'fastapi'],
            'javascript': ['javascript', 'js', 'node', 'react', 'vue'],
            'database': ['sql', 'database', 'db', 'mysql', 'postgres'],
            'api': ['api', 'rest', 'graphql', 'endpoint'],
            'frontend': ['ui', 'frontend', 'interface', 'design'],
            'backend': ['backend', 'server', 'service']
        }
        
        for tech, keywords in tech_keywords.items():
            if any(keyword in text for keyword in keywords):
                tags.append(IdeaTag(
                    name=tech,
                    category='technology',
                    confidence=0.6,
                    source='auto'
                ))
        
        # Effort estimation
        effort_keywords = {
            'quick-win': ['quick', 'simple', 'easy', 'small'],
            'long-term': ['complex', 'major', 'large', 'epic', 'project']
        }
        
        for effort, keywords in effort_keywords.items():
            if any(keyword in text for keyword in keywords):
                tags.append(IdeaTag(
                    name=effort,
                    category='effort',
                    confidence=0.5,
                    source='auto'
                ))
                break
        
        return tags


class PriorityEngine:
    """Dynamic priority scoring and management."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Priority scoring weights
        self.scoring_weights = {
            'keyword_urgency': 0.3,
            'business_impact': 0.25,
            'technical_complexity': 0.2,
            'dependencies': 0.15,
            'time_decay': 0.1
        }
        
        # Urgency keywords
        self.urgency_keywords = {
            'critical': ['urgent', 'critical', 'asap', 'emergency', 'blocking'],
            'high': ['important', 'priority', 'soon', 'needed', 'required'],
            'medium': ['should', 'would', 'consider', 'improve'],
            'low': ['later', 'someday', 'nice-to-have', 'optional', 'enhancement']
        }
        
        # Business impact indicators
        self.impact_keywords = {
            'high': ['user', 'customer', 'revenue', 'performance', 'security'],
            'medium': ['efficiency', 'productivity', 'maintainability'],
            'low': ['convenience', 'polish', 'cosmetic']
        }
    
    def calculate_priority_score(self, idea: IdeaCapture) -> float:
        """Calculate dynamic priority score (0.0 to 1.0)."""
        score = 0.0
        text = idea.raw_text.lower()
        
        # Keyword urgency score
        urgency_score = self._calculate_urgency_score(text)
        score += urgency_score * self.scoring_weights['keyword_urgency']
        
        # Business impact score
        impact_score = self._calculate_impact_score(text)
        score += impact_score * self.scoring_weights['business_impact']
        
        # Technical complexity (inverse score - simpler = higher priority)
        complexity_score = 1.0 - self._calculate_complexity_score(text)
        score += complexity_score * self.scoring_weights['technical_complexity']
        
        # Time decay (newer ideas get slight boost)
        time_score = self._calculate_time_decay_score(idea.timestamp)
        score += time_score * self.scoring_weights['time_decay']
        
        return min(1.0, max(0.0, score))
    
    def _calculate_urgency_score(self, text: str) -> float:
        """Calculate urgency score from keywords."""
        for priority, keywords in self.urgency_keywords.items():
            if any(keyword in text for keyword in keywords):
                scores = {'critical': 1.0, 'high': 0.8, 'medium': 0.5, 'low': 0.2}
                return scores[priority]
        return 0.4  # Default medium urgency
    
    def _calculate_impact_score(self, text: str) -> float:
        """Calculate business impact score."""
        for impact, keywords in self.impact_keywords.items():
            if any(keyword in text for keyword in keywords):
                scores = {'high': 1.0, 'medium': 0.6, 'low': 0.3}
                return scores[impact]
        return 0.5  # Default medium impact
    
    def _calculate_complexity_score(self, text: str) -> float:
        """Calculate technical complexity score."""
        complexity_indicators = {
            'high': ['complex', 'architecture', 'refactor', 'migration', 'integration'],
            'medium': ['implement', 'build', 'create', 'develop'],
            'low': ['fix', 'update', 'change', 'adjust', 'configure']
        }
        
        for complexity, keywords in complexity_indicators.items():
            if any(keyword in text for keyword in keywords):
                scores = {'high': 1.0, 'medium': 0.6, 'low': 0.2}
                return scores[complexity]
        return 0.5  # Default medium complexity
    
    def _calculate_time_decay_score(self, captured_at: datetime) -> float:
        """Calculate time decay score (recent ideas get small boost)."""
        age_hours = (datetime.now() - captured_at).total_seconds() / 3600
        if age_hours < 1:
            return 1.0
        elif age_hours < 24:
            return 0.8
        elif age_hours < 168:  # 1 week
            return 0.6
        else:
            return 0.4
    
    def get_priority_label(self, score: float) -> str:
        """Convert priority score to human-readable label."""
        if score >= 0.8:
            return 'critical'
        elif score >= 0.6:
            return 'high'
        elif score >= 0.4:
            return 'medium'
        else:
            return 'low'


class ClusteringEngine:
    """Engine for detecting and clustering related ideas."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self._init_database()
        
        # Similarity thresholds
        self.similarity_threshold = 0.6
        self.min_cluster_size = 2
        self.max_cluster_size = 20
    
    def _init_database(self):
        """Initialize clustering database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS idea_clusters (
                    cluster_id TEXT PRIMARY KEY,
                    similarity_threshold REAL,
                    cluster_center TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cluster_members (
                    cluster_id TEXT,
                    idea_id TEXT,
                    similarity_score REAL,
                    added_at TEXT,
                    PRIMARY KEY (cluster_id, idea_id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cluster_tags (
                    cluster_id TEXT,
                    tag_name TEXT,
                    frequency INTEGER,
                    PRIMARY KEY (cluster_id, tag_name)
                )
            """)
    
    def calculate_similarity(self, idea1: IdeaCapture, idea2: IdeaCapture) -> float:
        """Calculate similarity between two ideas."""
        # Simple text similarity using common words
        words1 = set(self._extract_keywords(idea1.raw_text.lower()))
        words2 = set(self._extract_keywords(idea2.raw_text.lower()))
        
        if not words1 or not words2:
            return 0.0
        
        # Jaccard similarity
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        text_similarity = intersection / union if union > 0 else 0.0
        
        # Context similarity bonus
        context_bonus = 0.0
        if (idea1.component and idea2.component and 
            idea1.component == idea2.component):
            context_bonus = 0.2
        
        return min(1.0, text_similarity + context_bonus)
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords from text."""
        # Remove common stop words and extract meaningful terms
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 
            'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'could', 'should', 'this', 'that', 'these', 'those'
        }
        
        # Extract words (3+ characters, not stop words)
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text)
        return [word for word in words if word.lower() not in stop_words]
    
    def find_clusters(self, ideas: List[IdeaCapture]) -> List[IdeaCluster]:
        """Find clusters of related ideas."""
        if len(ideas) < self.min_cluster_size:
            return []
        
        clusters = []
        processed_ideas = set()
        
        for i, idea1 in enumerate(ideas):
            if idea1.idea_id in processed_ideas:
                continue
            
            cluster_ideas = [idea1.idea_id]
            processed_ideas.add(idea1.idea_id)
            
            # Find similar ideas
            for j, idea2 in enumerate(ideas[i+1:], i+1):
                if idea2.idea_id in processed_ideas:
                    continue
                
                similarity = self.calculate_similarity(idea1, idea2)
                if similarity >= self.similarity_threshold:
                    cluster_ideas.append(idea2.idea_id)
                    processed_ideas.add(idea2.idea_id)
            
            # Create cluster if we have enough ideas
            if len(cluster_ideas) >= self.min_cluster_size:
                cluster_id = self._generate_cluster_id(cluster_ideas)
                cluster = IdeaCluster(
                    cluster_id=cluster_id,
                    ideas=cluster_ideas,
                    similarity_threshold=self.similarity_threshold,
                    cluster_center=idea1.idea_id  # Use first idea as center
                )
                clusters.append(cluster)
        
        return clusters
    
    def _generate_cluster_id(self, idea_ids: List[str]) -> str:
        """Generate unique cluster ID."""
        content = ''.join(sorted(idea_ids))
        return hashlib.md5(content.encode()).hexdigest()[:8]


class IdeaOrganizer:
    """Main organization engine that coordinates all organization components."""
    
    def __init__(self, db_path: str, enable_clustering: bool = True):
        self.db_path = db_path
        self.enable_clustering = enable_clustering
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.category_manager = CategoryManager()
        self.tag_system = TagSystem(db_path)
        self.priority_engine = PriorityEngine()
        self.clustering_engine = ClusteringEngine(db_path) if enable_clustering else None
        
        # Performance tracking
        self.processing_stats = {
            'total_processed': 0,
            'avg_processing_time': 0.0,
            'categorization_time': 0.0,
            'tagging_time': 0.0,
            'priority_time': 0.0,
            'clustering_time': 0.0
        }
        
        # Background processing
        self._executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix='idea-org')
        self._processing_queue = []
        self._queue_lock = threading.Lock()
    
    def organize_idea(self, idea: IdeaCapture, async_processing: bool = True) -> Dict[str, Any]:
        """Organize a newly captured idea."""
        start_time = time.time()
        
        if async_processing:
            # Queue for background processing
            with self._queue_lock:
                self._processing_queue.append(idea)
            
            # Start background processing
            future = self._executor.submit(self._process_idea_organization, idea)
            
            return {
                'idea_id': idea.idea_id,
                'status': 'queued',
                'processing_time': (time.time() - start_time) * 1000
            }
        else:
            # Process immediately
            return self._process_idea_organization(idea)
    
    def _process_idea_organization(self, idea: IdeaCapture) -> Dict[str, Any]:
        """Process idea organization (internal method)."""
        start_time = time.time()
        results = {
            'idea_id': idea.idea_id,
            'categories': [],
            'tags': [],
            'priority_score': 0.0,
            'priority_label': 'medium',
            'component': None,
            'status': 'processed'
        }
        
        try:
            # Categorization
            cat_start = time.time()
            categories = self.category_manager.categorize_idea(idea)
            results['categories'] = [cat.to_dict() for cat in categories]
            cat_time = (time.time() - cat_start) * 1000
            
            # Component detection
            component = self.category_manager.detect_component(idea)
            results['component'] = component
            if component:
                idea.component = component  # Update idea object
            
            # Auto-tagging
            tag_start = time.time()
            auto_tags = self.tag_system.auto_tag_idea(idea)
            for tag in auto_tags:
                self.tag_system.add_tag(idea.idea_id, tag)
            results['tags'] = [tag.to_dict() for tag in auto_tags]
            tag_time = (time.time() - tag_start) * 1000
            
            # Priority calculation
            priority_start = time.time()
            priority_score = self.priority_engine.calculate_priority_score(idea)
            priority_label = self.priority_engine.get_priority_label(priority_score)
            results['priority_score'] = priority_score
            results['priority_label'] = priority_label
            
            # Update idea priority
            idea.priority = priority_label
            priority_time = (time.time() - priority_start) * 1000
            
            # Update processing stats
            total_time = (time.time() - start_time) * 1000
            self._update_processing_stats(total_time, cat_time, tag_time, priority_time)
            
            results['processing_time'] = total_time
            
            self.logger.info(
                f"Organized idea {idea.idea_id}: "
                f"categories={len(categories)}, tags={len(auto_tags)}, "
                f"priority={priority_label}, time={total_time:.1f}ms"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to organize idea {idea.idea_id}: {e}")
            results['status'] = 'error'
            results['error'] = str(e)
        
        return results
    
    def _update_processing_stats(self, total_time: float, cat_time: float, 
                                tag_time: float, priority_time: float):
        """Update processing performance statistics."""
        self.processing_stats['total_processed'] += 1
        count = self.processing_stats['total_processed']
        
        # Running averages
        self.processing_stats['avg_processing_time'] = (
            (self.processing_stats['avg_processing_time'] * (count - 1) + total_time) / count
        )
        self.processing_stats['categorization_time'] = (
            (self.processing_stats['categorization_time'] * (count - 1) + cat_time) / count
        )
        self.processing_stats['tagging_time'] = (
            (self.processing_stats['tagging_time'] * (count - 1) + tag_time) / count
        )
        self.processing_stats['priority_time'] = (
            (self.processing_stats['priority_time'] * (count - 1) + priority_time) / count
        )
    
    def batch_organize_ideas(self, ideas: List[IdeaCapture]) -> Dict[str, Any]:
        """Organize multiple ideas in batch for efficiency."""
        start_time = time.time()
        
        results = {
            'total_ideas': len(ideas),
            'processed': 0,
            'failed': 0,
            'clusters': []
        }
        
        # Process ideas individually
        for idea in ideas:
            try:
                self._process_idea_organization(idea)
                results['processed'] += 1
            except Exception as e:
                self.logger.error(f"Failed to organize idea {idea.idea_id}: {e}")
                results['failed'] += 1
        
        # Find clusters if enabled
        if self.clustering_engine and len(ideas) >= 2:
            cluster_start = time.time()
            clusters = self.clustering_engine.find_clusters(ideas)
            results['clusters'] = [cluster.to_dict() for cluster in clusters]
            cluster_time = (time.time() - cluster_start) * 1000
            self.processing_stats['clustering_time'] = cluster_time
        
        results['processing_time'] = (time.time() - start_time) * 1000
        
        return results
    
    def get_organization_stats(self) -> Dict[str, Any]:
        """Get organization processing statistics."""
        return {
            'processing_stats': self.processing_stats.copy(),
            'queue_size': len(self._processing_queue),
            'components_enabled': {
                'categorization': True,
                'tagging': True,
                'priority_engine': True,
                'clustering': self.clustering_engine is not None
            }
        }
    
    def shutdown(self):
        """Shutdown the organizer and cleanup resources."""
        self.logger.info("Shutting down IdeaOrganizer...")
        self._executor.shutdown(wait=True)


def create_idea_organizer(db_path: str, enable_clustering: bool = True) -> IdeaOrganizer:
    """Factory function to create an IdeaOrganizer instance."""
    return IdeaOrganizer(db_path, enable_clustering)