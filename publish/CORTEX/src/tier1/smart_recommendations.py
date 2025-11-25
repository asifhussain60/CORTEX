"""
CORTEX 3.0 - Smart Recommendations API
Advanced Fusion Features - Milestone 3

Intelligent file prediction service that leverages learned patterns from the Pattern Learning Engine
to suggest relevant files based on conversation content and development context.

Features:
- Context-aware file suggestions based on conversation analysis
- Pattern-driven recommendations using learned correlations
- File grouping by relevance and development phase
- Adaptive learning from user interaction feedback
- Integration with both conversational and traditional memories

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
Version: 3.0.0
"""

import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, asdict
from pathlib import Path
import re
from collections import defaultdict, Counter
import math


@dataclass
class FileRecommendation:
    """A recommended file with confidence score and reasoning"""
    file_path: str
    confidence_score: float  # 0.0 to 1.0
    reasoning: str
    recommendation_type: str  # "pattern_match", "context_similarity", "development_flow", "collaboration"
    supporting_evidence: List[str]
    last_accessed: Optional[datetime] = None
    frequency_score: float = 0.0
    recency_score: float = 0.0
    pattern_strength: float = 0.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class RecommendationContext:
    """Context information for generating recommendations"""
    current_conversation: str
    user_intent: str  # "implementation", "debugging", "refactoring", etc.
    mentioned_files: List[str]
    development_phase: str
    keywords: List[str]
    conversation_id: str
    timestamp: datetime
    session_context: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.session_context is None:
            self.session_context = {}


@dataclass
class RecommendationFeedback:
    """User feedback on recommendation quality"""
    recommendation_id: str
    file_path: str
    user_action: str  # "accepted", "rejected", "ignored"
    timestamp: datetime
    context: str
    effectiveness_rating: Optional[float] = None  # 1.0 to 5.0 if provided
    

class SmartRecommendations:
    """
    Advanced file recommendation engine using pattern learning and context analysis.
    
    This system learns from conversation patterns, file access history, and user feedback
    to provide intelligent file suggestions that improve development workflow efficiency.
    """
    
    def __init__(self, db_path: str = None, pattern_engine=None):
        self.db_path = db_path or "cortex-brain/tier1/smart_recommendations.db"
        self.pattern_engine = pattern_engine  # Pattern Learning Engine instance
        self.logger = logging.getLogger(__name__)
        
        # Recommendation weights
        self.weights = {
            "pattern_match": 0.35,      # Learned pattern correlations
            "context_similarity": 0.25, # Semantic content similarity  
            "development_flow": 0.20,   # Development phase appropriateness
            "recency": 0.10,           # Recently accessed files
            "frequency": 0.10          # Frequently used files
        }
        
        # File type patterns for development context
        self.file_type_patterns = {
            "implementation": [r"\.py$", r"\.js$", r"\.ts$", r"\.java$", r"\.cpp$", r"\.cs$"],
            "testing": [r"test.*\.py$", r".*_test\.py$", r"\.spec\.js$", r"\.test\.ts$"],
            "configuration": [r"\.json$", r"\.yaml$", r"\.yml$", r"\.ini$", r"\.conf$"],
            "documentation": [r"\.md$", r"\.rst$", r"\.txt$", r"README", r"CHANGELOG"],
            "frontend": [r"\.html$", r"\.css$", r"\.scss$", r"\.jsx$", r"\.vue$"],
            "data": [r"\.sql$", r"\.csv$", r"\.json$", r"\.xml$", r"\.db$"]
        }
        
        # Context keywords for different development activities
        self.activity_keywords = {
            "debugging": ["bug", "error", "exception", "fail", "debug", "trace", "stack", "crash"],
            "testing": ["test", "verify", "validate", "check", "assert", "mock", "spec"],
            "refactoring": ["refactor", "clean", "organize", "restructure", "optimize", "simplify"],
            "feature": ["add", "implement", "create", "new", "feature", "functionality"],
            "documentation": ["document", "explain", "describe", "readme", "guide", "manual"],
            "deployment": ["deploy", "build", "release", "publish", "production", "staging"]
        }
        
        self._initialize_database()
        self._initialize_caches()
    
    def _initialize_database(self):
        """Initialize the recommendations database with required tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS file_recommendations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        conversation_id TEXT NOT NULL,
                        file_path TEXT NOT NULL,
                        confidence_score REAL NOT NULL,
                        reasoning TEXT NOT NULL,
                        recommendation_type TEXT NOT NULL,
                        supporting_evidence TEXT NOT NULL,  -- JSON array
                        frequency_score REAL DEFAULT 0.0,
                        recency_score REAL DEFAULT 0.0,
                        pattern_strength REAL DEFAULT 0.0,
                        metadata TEXT,  -- JSON object
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(conversation_id, file_path)
                    )
                """)
                
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS recommendation_feedback (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        recommendation_id TEXT NOT NULL,
                        file_path TEXT NOT NULL,
                        user_action TEXT NOT NULL,
                        effectiveness_rating REAL,
                        context TEXT NOT NULL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS file_access_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        file_path TEXT NOT NULL,
                        conversation_id TEXT NOT NULL,
                        access_type TEXT NOT NULL,  -- "mentioned", "modified", "viewed"
                        context TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS recommendation_patterns (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        pattern_type TEXT NOT NULL,
                        source_files TEXT NOT NULL,  -- JSON array
                        target_files TEXT NOT NULL,  -- JSON array
                        confidence REAL NOT NULL,
                        usage_count INTEGER DEFAULT 1,
                        last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        context_keywords TEXT,  -- JSON array
                        UNIQUE(pattern_type, source_files, target_files)
                    )
                """)
                
                # Indexes for performance
                conn.execute("CREATE INDEX IF NOT EXISTS idx_recommendations_conversation ON file_recommendations(conversation_id)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_recommendations_confidence ON file_recommendations(confidence_score DESC)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_access_history_file ON file_access_history(file_path)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_access_history_timestamp ON file_access_history(timestamp DESC)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_patterns_type ON recommendation_patterns(pattern_type)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_feedback_rating ON recommendation_feedback(effectiveness_rating)")
                
                self.logger.info("Smart Recommendations database initialized successfully")
                
        except Exception as e:
            self.logger.error(f"Database initialization failed: {e}")
            raise
    
    def _initialize_caches(self):
        """Initialize in-memory caches for performance optimization"""
        self.pattern_cache = {}
        self.file_frequency_cache = {}
        self.last_cache_update = datetime.now()
        self.cache_ttl = timedelta(minutes=30)  # Cache valid for 30 minutes
        
        # Load frequently used patterns into cache
        self._refresh_pattern_cache()
    
    def _refresh_pattern_cache(self):
        """Refresh the pattern cache from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT pattern_type, source_files, target_files, confidence, usage_count
                    FROM recommendation_patterns 
                    WHERE confidence > 0.6 AND usage_count > 2
                    ORDER BY usage_count DESC, confidence DESC
                    LIMIT 1000
                """)
                
                self.pattern_cache.clear()
                for row in cursor.fetchall():
                    pattern_type, source_files, target_files, confidence, usage_count = row
                    source_list = json.loads(source_files)
                    target_list = json.loads(target_files)
                    
                    key = (pattern_type, tuple(sorted(source_list)))
                    if key not in self.pattern_cache:
                        self.pattern_cache[key] = []
                    
                    self.pattern_cache[key].append({
                        'targets': target_list,
                        'confidence': confidence,
                        'usage_count': usage_count
                    })
                
                self.last_cache_update = datetime.now()
                self.logger.debug(f"Pattern cache refreshed with {len(self.pattern_cache)} patterns")
                
        except Exception as e:
            self.logger.error(f"Failed to refresh pattern cache: {e}")
    
    def get_recommendations(self, context: RecommendationContext, max_results: int = 10) -> List[FileRecommendation]:
        """
        Generate intelligent file recommendations based on conversation context.
        
        Args:
            context: RecommendationContext with conversation details
            max_results: Maximum number of recommendations to return
            
        Returns:
            List of FileRecommendation objects sorted by confidence score
        """
        try:
            # Refresh cache if needed
            if datetime.now() - self.last_cache_update > self.cache_ttl:
                self._refresh_pattern_cache()
            
            recommendations = []
            
            # 1. Pattern-based recommendations using Pattern Learning Engine
            pattern_recs = self._get_pattern_recommendations(context)
            recommendations.extend(pattern_recs)
            
            # 2. Context similarity recommendations
            context_recs = self._get_context_similarity_recommendations(context)
            recommendations.extend(context_recs)
            
            # 3. Development flow recommendations
            flow_recs = self._get_development_flow_recommendations(context)
            recommendations.extend(flow_recs)
            
            # 4. Frequency-based recommendations
            freq_recs = self._get_frequency_recommendations(context)
            recommendations.extend(freq_recs)
            
            # 5. Recency-based recommendations
            recent_recs = self._get_recency_recommendations(context)
            recommendations.extend(recent_recs)
            
            # Deduplicate and merge recommendations for same files
            merged_recs = self._merge_recommendations(recommendations)
            
            # Apply final scoring and ranking
            final_recs = self._calculate_final_scores(merged_recs, context)
            
            # Sort by confidence and return top results
            final_recs.sort(key=lambda x: x.confidence_score, reverse=True)
            result = final_recs[:max_results]
            
            # Store recommendations for feedback tracking
            self._store_recommendations(result, context)
            
            self.logger.info(f"Generated {len(result)} recommendations for conversation {context.conversation_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to generate recommendations: {e}")
            return []
    
    def _get_pattern_recommendations(self, context: RecommendationContext) -> List[FileRecommendation]:
        """Get recommendations based on learned patterns from Pattern Learning Engine"""
        recommendations = []
        
        try:
            # Get patterns from the Pattern Learning Engine if available
            if self.pattern_engine:
                # Query for correlations based on mentioned files
                for file_path in context.mentioned_files:
                    correlations = self.pattern_engine.get_file_correlations(file_path)
                    
                    for correlation in correlations:
                        if correlation['confidence'] > 0.5:  # Only strong correlations
                            recommendations.append(FileRecommendation(
                                file_path=correlation['related_file'],
                                confidence_score=correlation['confidence'] * self.weights["pattern_match"],
                                reasoning=f"Often used together with {file_path}",
                                recommendation_type="pattern_match",
                                supporting_evidence=[f"Pattern confidence: {correlation['confidence']:.2f}"],
                                pattern_strength=correlation['confidence']
                            ))
            
            # Also check local pattern cache
            for mentioned_file in context.mentioned_files:
                cache_key = ("file_correlation", tuple(sorted([mentioned_file])))
                if cache_key in self.pattern_cache:
                    for pattern in self.pattern_cache[cache_key]:
                        for target_file in pattern['targets']:
                            recommendations.append(FileRecommendation(
                                file_path=target_file,
                                confidence_score=pattern['confidence'] * self.weights["pattern_match"],
                                reasoning=f"Frequently used with {mentioned_file}",
                                recommendation_type="pattern_match",
                                supporting_evidence=[f"Usage count: {pattern['usage_count']}"],
                                pattern_strength=pattern['confidence']
                            ))
        
        except Exception as e:
            self.logger.error(f"Error getting pattern recommendations: {e}")
        
        return recommendations
    
    def _get_context_similarity_recommendations(self, context: RecommendationContext) -> List[FileRecommendation]:
        """Get recommendations based on conversation content similarity"""
        recommendations = []
        
        try:
            # Extract keywords from conversation
            keywords = self._extract_keywords(context.current_conversation)
            keywords.extend(context.keywords)
            
            # Query for files with similar contexts
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT file_path, context, COUNT(*) as frequency
                    FROM file_access_history
                    WHERE timestamp > datetime('now', '-30 days')
                    GROUP BY file_path
                    HAVING frequency > 1
                    ORDER BY frequency DESC
                    LIMIT 50
                """)
                
                for row in cursor.fetchall():
                    file_path, file_context, frequency = row
                    
                    # Calculate similarity score based on keyword overlap
                    if file_context:
                        similarity = self._calculate_context_similarity(keywords, file_context)
                        if similarity > 0.1:  # Lowered minimum similarity threshold
                            recommendations.append(FileRecommendation(
                                file_path=file_path,
                                confidence_score=similarity * self.weights["context_similarity"],
                                reasoning=f"Similar context (similarity: {similarity:.2f})",
                                recommendation_type="context_similarity",
                                supporting_evidence=[f"Keyword overlap with previous usage"],
                                frequency_score=min(frequency / 10.0, 1.0)  # Normalize frequency
                            ))
        
        except Exception as e:
            self.logger.error(f"Error getting context similarity recommendations: {e}")
        
        return recommendations
    
    def _get_development_flow_recommendations(self, context: RecommendationContext) -> List[FileRecommendation]:
        """Get recommendations based on development phase and workflow"""
        recommendations = []
        
        try:
            # Determine file types appropriate for current development phase
            appropriate_types = self._get_file_types_for_phase(context.development_phase, context.user_intent)
            
            # Query recent file access history
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT file_path, access_type, context, timestamp
                    FROM file_access_history
                    WHERE timestamp > datetime('now', '-7 days')
                    ORDER BY timestamp DESC
                    LIMIT 100
                """)
                
                for row in cursor.fetchall():
                    file_path, access_type, file_context, timestamp = row
                    
                    # Check if file type matches development phase
                    file_type_score = self._calculate_file_type_score(file_path, appropriate_types)
                    if file_type_score > 0.1:  # Lowered from 0.2 to 0.1
                        
                        # Calculate development flow score
                        flow_score = self._calculate_development_flow_score(
                            context.development_phase, context.user_intent, file_context
                        )
                        
                        if flow_score > 0.2:  # Lowered from 0.3 to 0.2
                            recommendations.append(FileRecommendation(
                                file_path=file_path,
                                confidence_score=flow_score * self.weights["development_flow"],
                                reasoning=f"Relevant for {context.development_phase} phase",
                                recommendation_type="development_flow",
                                supporting_evidence=[f"File type match: {file_type_score:.2f}"],
                                last_accessed=datetime.fromisoformat(timestamp.replace('Z', '+00:00')) if 'T' in timestamp else None
                            ))
        
        except Exception as e:
            self.logger.error(f"Error getting development flow recommendations: {e}")
        
        return recommendations
    
    def _get_frequency_recommendations(self, context: RecommendationContext) -> List[FileRecommendation]:
        """Get recommendations based on file access frequency"""
        recommendations = []
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT file_path, COUNT(*) as access_count, MAX(timestamp) as last_access
                    FROM file_access_history
                    WHERE timestamp > datetime('now', '-30 days')
                    GROUP BY file_path
                    ORDER BY access_count DESC
                    LIMIT 20
                """)
                
                max_count = 0
                results = cursor.fetchall()
                if results:
                    max_count = results[0][1]  # Highest access count for normalization
                
                for file_path, access_count, last_access in results:
                    if access_count >= 3:  # Minimum frequency threshold
                        frequency_score = access_count / max(max_count, 1)
                        
                        recommendations.append(FileRecommendation(
                            file_path=file_path,
                            confidence_score=frequency_score * self.weights["frequency"],
                            reasoning=f"Frequently accessed ({access_count} times)",
                            recommendation_type="frequency",
                            supporting_evidence=[f"Access count: {access_count}"],
                            frequency_score=frequency_score,
                            last_accessed=datetime.fromisoformat(last_access.replace('Z', '+00:00')) if last_access and 'T' in last_access else None
                        ))
        
        except Exception as e:
            self.logger.error(f"Error getting frequency recommendations: {e}")
        
        return recommendations
    
    def _get_recency_recommendations(self, context: RecommendationContext) -> List[FileRecommendation]:
        """Get recommendations based on recent file access"""
        recommendations = []
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT file_path, timestamp, context
                    FROM file_access_history
                    WHERE timestamp > datetime('now', '-2 days')
                    ORDER BY timestamp DESC
                    LIMIT 15
                """)
                
                now = datetime.now()
                for file_path, timestamp, file_context in cursor.fetchall():
                    try:
                        access_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00')) if 'T' in timestamp else datetime.fromisoformat(timestamp)
                        hours_ago = (now - access_time).total_seconds() / 3600
                        
                        # Recency score decreases with time (0-1 scale)
                        recency_score = max(0, 1 - (hours_ago / 48))  # 48 hours max
                        
                        if recency_score > 0.1:
                            recommendations.append(FileRecommendation(
                                file_path=file_path,
                                confidence_score=recency_score * self.weights["recency"],
                                reasoning=f"Recently accessed ({hours_ago:.1f} hours ago)",
                                recommendation_type="recency",
                                supporting_evidence=[f"Last access: {access_time.strftime('%Y-%m-%d %H:%M')}"],
                                recency_score=recency_score,
                                last_accessed=access_time
                            ))
                    except (ValueError, TypeError):
                        # Skip invalid timestamps
                        continue
        
        except Exception as e:
            self.logger.error(f"Error getting recency recommendations: {e}")
        
        return recommendations
    
    def _merge_recommendations(self, recommendations: List[FileRecommendation]) -> List[FileRecommendation]:
        """Merge multiple recommendations for the same file"""
        file_recs = defaultdict(list)
        
        # Group recommendations by file path
        for rec in recommendations:
            file_recs[rec.file_path].append(rec)
        
        merged = []
        for file_path, recs in file_recs.items():
            if len(recs) == 1:
                merged.append(recs[0])
            else:
                # Merge multiple recommendations for same file
                merged_rec = self._merge_file_recommendations(recs)
                merged.append(merged_rec)
        
        return merged
    
    def _merge_file_recommendations(self, recommendations: List[FileRecommendation]) -> FileRecommendation:
        """Merge multiple recommendations for the same file into one"""
        if len(recommendations) == 1:
            return recommendations[0]
        
        file_path = recommendations[0].file_path
        
        # Calculate combined confidence score (not just sum to avoid inflation)
        confidence_scores = [rec.confidence_score for rec in recommendations]
        combined_confidence = min(sum(confidence_scores), 1.0)  # Cap at 1.0
        
        # Merge reasoning and evidence
        reasons = [rec.reasoning for rec in recommendations if rec.reasoning]
        evidence = []
        for rec in recommendations:
            if rec.supporting_evidence:
                evidence.extend(rec.supporting_evidence)
        
        # Combine recommendation types
        rec_types = [rec.recommendation_type for rec in recommendations]
        primary_type = max(set(rec_types), key=rec_types.count)
        
        # Merge scores
        frequency_scores = [rec.frequency_score for rec in recommendations if rec.frequency_score > 0]
        recency_scores = [rec.recency_score for rec in recommendations if rec.recency_score > 0]
        pattern_strengths = [rec.pattern_strength for rec in recommendations if rec.pattern_strength > 0]
        
        # Get most recent access time
        access_times = [rec.last_accessed for rec in recommendations if rec.last_accessed]
        last_accessed = max(access_times) if access_times else None
        
        return FileRecommendation(
            file_path=file_path,
            confidence_score=combined_confidence,
            reasoning="; ".join(reasons[:3]),  # Top 3 reasons to avoid clutter
            recommendation_type=primary_type,
            supporting_evidence=list(set(evidence))[:5],  # Deduplicated, top 5
            frequency_score=max(frequency_scores) if frequency_scores else 0.0,
            recency_score=max(recency_scores) if recency_scores else 0.0,
            pattern_strength=max(pattern_strengths) if pattern_strengths else 0.0,
            last_accessed=last_accessed,
            metadata={"merged_from": len(recommendations)}
        )
    
    def _calculate_final_scores(self, recommendations: List[FileRecommendation], context: RecommendationContext) -> List[FileRecommendation]:
        """Apply final scoring adjustments and calculate confidence scores"""
        
        for rec in recommendations:
            # Apply boosting based on specific context factors
            boost_factor = 1.0
            
            # Boost if file is mentioned in current conversation
            if rec.file_path in context.mentioned_files:
                boost_factor *= 1.5
                rec.supporting_evidence.append("Mentioned in current conversation")
            
            # Boost based on user intent match
            intent_boost = self._calculate_intent_boost(rec.file_path, context.user_intent)
            boost_factor *= intent_boost
            
            # Boost based on development phase relevance
            phase_boost = self._calculate_phase_boost(rec.file_path, context.development_phase)
            boost_factor *= phase_boost
            
            # Apply boost but cap at reasonable maximum
            rec.confidence_score = min(rec.confidence_score * boost_factor, 0.95)
            
            # Add boost information to metadata
            rec.metadata.update({
                "boost_factor": boost_factor,
                "intent_boost": intent_boost,
                "phase_boost": phase_boost,
                "final_score": rec.confidence_score
            })
        
        return recommendations
    
    def _calculate_intent_boost(self, file_path: str, user_intent: str) -> float:
        """Calculate boost factor based on user intent and file characteristics"""
        boost = 1.0
        
        # Get file extension and check against intent patterns
        file_ext = Path(file_path).suffix.lower()
        file_name = Path(file_path).name.lower()
        
        if user_intent == "testing":
            if any(pattern in file_name for pattern in ["test", "spec", "mock"]):
                boost = 1.3
            elif file_ext in [".py", ".js", ".ts"]:
                boost = 1.1
        
        elif user_intent == "debugging":
            if any(pattern in file_name for pattern in ["log", "debug", "trace"]):
                boost = 1.4
            elif file_ext in [".py", ".js", ".ts", ".java"]:
                boost = 1.2
        
        elif user_intent == "implementation":
            if file_ext in [".py", ".js", ".ts", ".java", ".cpp", ".cs"]:
                boost = 1.2
            elif any(pattern in file_name for pattern in ["main", "core", "service"]):
                boost = 1.3
        
        elif user_intent == "documentation":
            if file_ext in [".md", ".rst", ".txt"] or "readme" in file_name:
                boost = 1.4
        
        return boost
    
    def _calculate_phase_boost(self, file_path: str, development_phase: str) -> float:
        """Calculate boost factor based on development phase and file type"""
        boost = 1.0
        
        file_name = Path(file_path).name.lower()
        
        if development_phase == "implementation":
            if any(pattern in file_name for pattern in ["service", "controller", "handler", "core"]):
                boost = 1.2
        
        elif development_phase == "testing":
            if any(pattern in file_name for pattern in ["test", "spec"]):
                boost = 1.4
        
        elif development_phase == "refactoring":
            if any(pattern in file_name for pattern in ["util", "helper", "base", "abstract"]):
                boost = 1.3
        
        elif development_phase == "debugging":
            if any(pattern in file_name for pattern in ["error", "exception", "log"]):
                boost = 1.3
        
        return boost
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords from conversation text"""
        # Basic keyword extraction (can be enhanced with NLP libraries)
        import re
        
        # Remove common stop words and extract meaningful terms
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with",
            "by", "from", "up", "about", "into", "through", "during", "before", "after",
            "above", "below", "between", "among", "this", "that", "these", "those", "i", "you",
            "he", "she", "it", "we", "they", "me", "him", "her", "us", "them", "my", "your",
            "his", "her", "its", "our", "their", "am", "is", "are", "was", "were", "be", "been",
            "being", "have", "has", "had", "do", "does", "did", "will", "would", "could", "should"
        }
        
        # Extract words (alphanumeric sequences)
        words = re.findall(r'\b[a-zA-Z][a-zA-Z0-9_]*\b', text.lower())
        
        # Filter out stop words and short words
        keywords = [word for word in words if len(word) > 2 and word not in stop_words]
        
        # Return unique keywords maintaining order
        seen = set()
        unique_keywords = []
        for keyword in keywords:
            if keyword not in seen:
                seen.add(keyword)
                unique_keywords.append(keyword)
        
        return unique_keywords[:20]  # Limit to top 20 keywords
    
    def _calculate_context_similarity(self, keywords: List[str], context: str) -> float:
        """Calculate similarity between keywords and context text"""
        if not keywords or not context:
            return 0.0
        
        context_lower = context.lower()
        matches = sum(1 for keyword in keywords if keyword in context_lower)
        
        # Jaccard similarity approximation
        return matches / len(keywords)
    
    def _get_file_types_for_phase(self, development_phase: str, user_intent: str) -> List[str]:
        """Get appropriate file types for development phase and intent"""
        phase_types = {
            "planning": ["documentation"],
            "implementation": ["implementation", "configuration"],
            "testing": ["testing", "implementation"],
            "debugging": ["implementation", "testing", "data"],
            "refactoring": ["implementation"],
            "deployment": ["configuration", "documentation"],
            "documentation": ["documentation"],
            "general_development": ["implementation", "testing"]
        }
        
        intent_types = {
            "implementation": ["implementation"],
            "testing": ["testing"],
            "debugging": ["implementation", "testing", "data"],
            "refactoring": ["implementation"],
            "documentation": ["documentation"],
            "configuration": ["configuration"]
        }
        
        # Combine phase and intent types
        types = set()
        types.update(phase_types.get(development_phase, ["implementation"]))
        types.update(intent_types.get(user_intent, ["implementation"]))
        
        return list(types)
    
    def _calculate_file_type_score(self, file_path: str, appropriate_types: List[str]) -> float:
        """Calculate how well a file matches the appropriate types"""
        file_ext = Path(file_path).suffix.lower()
        file_name = Path(file_path).name.lower()
        
        max_score = 0.0
        
        for file_type in appropriate_types:
            type_patterns = self.file_type_patterns.get(file_type, [])
            for pattern in type_patterns:
                if re.search(pattern, file_path):
                    max_score = max(max_score, 1.0)
                    break
        
        return max_score
    
    def _calculate_development_flow_score(self, development_phase: str, user_intent: str, context: str) -> float:
        """Calculate development flow appropriateness score"""
        score = 0.4  # Higher base score
        
        if not context:
            return 0.5  # Higher default score for missing context
        
        context_lower = context.lower()
        
        # Check for phase-appropriate keywords
        phase_keywords = self.activity_keywords.get(development_phase, [])
        phase_matches = sum(1 for keyword in phase_keywords if keyword in context_lower)
        
        # Check for intent-appropriate keywords  
        intent_keywords = self.activity_keywords.get(user_intent, [])
        intent_matches = sum(1 for keyword in intent_keywords if keyword in context_lower)
        
        # Calculate score based on keyword matches
        total_keywords = len(phase_keywords) + len(intent_keywords)
        total_matches = phase_matches + intent_matches
        
        if total_keywords > 0:
            score += min(total_matches / total_keywords * 1.5, 0.5)  # More generous scoring
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _store_recommendations(self, recommendations: List[FileRecommendation], context: RecommendationContext):
        """Store recommendations for feedback tracking and analytics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                for rec in recommendations:
                    # Serialize supporting evidence and metadata
                    evidence_json = json.dumps(rec.supporting_evidence)
                    metadata_json = json.dumps(rec.metadata)
                    
                    conn.execute("""
                        INSERT OR REPLACE INTO file_recommendations
                        (conversation_id, file_path, confidence_score, reasoning, 
                         recommendation_type, supporting_evidence, frequency_score,
                         recency_score, pattern_strength, metadata)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        context.conversation_id,
                        rec.file_path,
                        rec.confidence_score,
                        rec.reasoning,
                        rec.recommendation_type,
                        evidence_json,
                        rec.frequency_score,
                        rec.recency_score,
                        rec.pattern_strength,
                        metadata_json
                    ))
        
        except Exception as e:
            self.logger.error(f"Failed to store recommendations: {e}")
    
    def record_file_access(self, file_path: str, conversation_id: str, access_type: str, context: str = None):
        """Record file access for learning and recommendations"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO file_access_history
                    (file_path, conversation_id, access_type, context)
                    VALUES (?, ?, ?, ?)
                """, (file_path, conversation_id, access_type, context or ""))
                
                # Update pattern learning if we have pattern engine
                if self.pattern_engine and access_type == "modified":
                    self.pattern_engine.record_file_interaction(file_path, conversation_id, context)
        
        except Exception as e:
            self.logger.error(f"Failed to record file access: {e}")
    
    def record_feedback(self, feedback: RecommendationFeedback):
        """Record user feedback on recommendation quality"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO recommendation_feedback
                    (recommendation_id, file_path, user_action, effectiveness_rating, context)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    feedback.recommendation_id,
                    feedback.file_path,
                    feedback.user_action,
                    feedback.effectiveness_rating,
                    feedback.context
                ))
                
                # Update pattern confidence based on feedback
                self._update_pattern_confidence_from_feedback(feedback)
        
        except Exception as e:
            self.logger.error(f"Failed to record feedback: {e}")
    
    def _update_pattern_confidence_from_feedback(self, feedback: RecommendationFeedback):
        """Update pattern confidence scores based on user feedback"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Adjust confidence based on feedback
                confidence_adjustment = 0.0
                
                if feedback.user_action == "accepted":
                    confidence_adjustment = 0.1  # Increase confidence
                elif feedback.user_action == "rejected":
                    confidence_adjustment = -0.05  # Decrease confidence
                
                # Apply effectiveness rating if provided (1-5 scale)
                if feedback.effectiveness_rating:
                    rating_factor = (feedback.effectiveness_rating - 3) / 10.0  # -0.2 to +0.2
                    confidence_adjustment += rating_factor
                
                # Update patterns involving this file
                conn.execute("""
                    UPDATE recommendation_patterns
                    SET confidence = CASE 
                        WHEN confidence + ? > 1.0 THEN 1.0
                        WHEN confidence + ? < 0.1 THEN 0.1
                        ELSE confidence + ?
                    END,
                    usage_count = usage_count + CASE WHEN ? > 0 THEN 1 ELSE 0 END,
                    last_used = CURRENT_TIMESTAMP
                    WHERE (source_files LIKE ? OR target_files LIKE ?)
                """, (
                    confidence_adjustment, confidence_adjustment, confidence_adjustment,
                    1 if confidence_adjustment > 0 else 0,
                    f'%"{feedback.file_path}"%',
                    f'%"{feedback.file_path}"%'
                ))
        
        except Exception as e:
            self.logger.error(f"Failed to update pattern confidence from feedback: {e}")
    
    def get_recommendation_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get analytics on recommendation effectiveness and patterns"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                analytics = {}
                
                # Recommendation type distribution
                cursor = conn.execute("""
                    SELECT recommendation_type, COUNT(*), AVG(confidence_score)
                    FROM file_recommendations
                    WHERE created_at > datetime('now', '-' || ? || ' days')
                    GROUP BY recommendation_type
                """, (days,))
                
                type_stats = {}
                for rec_type, count, avg_confidence in cursor.fetchall():
                    type_stats[rec_type] = {
                        'count': count,
                        'avg_confidence': round(avg_confidence, 3)
                    }
                analytics['recommendation_types'] = type_stats
                
                # Feedback statistics
                cursor = conn.execute("""
                    SELECT user_action, COUNT(*), AVG(effectiveness_rating)
                    FROM recommendation_feedback
                    WHERE timestamp > datetime('now', '-' || ? || ' days')
                    GROUP BY user_action
                """, (days,))
                
                feedback_stats = {}
                total_feedback = 0
                for action, count, avg_rating in cursor.fetchall():
                    feedback_stats[action] = {
                        'count': count,
                        'avg_rating': round(avg_rating, 2) if avg_rating else None
                    }
                    total_feedback += count
                analytics['feedback'] = feedback_stats
                analytics['total_feedback'] = total_feedback
                
                # Most recommended files
                cursor = conn.execute("""
                    SELECT file_path, COUNT(*) as recommendation_count, AVG(confidence_score) as avg_confidence
                    FROM file_recommendations
                    WHERE created_at > datetime('now', '-' || ? || ' days')
                    GROUP BY file_path
                    ORDER BY recommendation_count DESC
                    LIMIT 10
                """, (days,))
                
                top_files = []
                for file_path, count, avg_conf in cursor.fetchall():
                    top_files.append({
                        'file_path': file_path,
                        'recommendation_count': count,
                        'avg_confidence': round(avg_conf, 3)
                    })
                analytics['top_recommended_files'] = top_files
                
                # Pattern effectiveness
                cursor = conn.execute("""
                    SELECT pattern_type, COUNT(*) as pattern_count, AVG(confidence) as avg_confidence
                    FROM recommendation_patterns
                    WHERE last_used > datetime('now', '-' || ? || ' days')
                    GROUP BY pattern_type
                    ORDER BY pattern_count DESC
                """, (days,))
                
                pattern_stats = {}
                for pattern_type, count, avg_conf in cursor.fetchall():
                    pattern_stats[pattern_type] = {
                        'count': count,
                        'avg_confidence': round(avg_conf, 3)
                    }
                analytics['pattern_effectiveness'] = pattern_stats
                
                return analytics
        
        except Exception as e:
            self.logger.error(f"Failed to get recommendation analytics: {e}")
            return {}
    
    def optimize_recommendations(self):
        """Optimize recommendation system based on collected data and feedback"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Remove low-confidence patterns with poor feedback
                removed_patterns = conn.execute("""
                    DELETE FROM recommendation_patterns
                    WHERE confidence < 0.3 
                    AND usage_count < 2
                    AND last_used < datetime('now', '-60 days')
                """).rowcount
                
                # Archive old recommendations
                archived_recs = conn.execute("""
                    DELETE FROM file_recommendations
                    WHERE created_at < datetime('now', '-90 days')
                """).rowcount
                
                # Clean old access history
                archived_history = conn.execute("""
                    DELETE FROM file_access_history
                    WHERE timestamp < datetime('now', '-180 days')
                """).rowcount
                
                # Refresh pattern cache
                self._refresh_pattern_cache()
                
                self.logger.info(f"Optimization complete: removed {removed_patterns} patterns, "
                               f"archived {archived_recs} recommendations, {archived_history} history entries")
                
                return {
                    'removed_patterns': removed_patterns,
                    'archived_recommendations': archived_recs,
                    'archived_history': archived_history
                }
        
        except Exception as e:
            self.logger.error(f"Optimization failed: {e}")
            return {}