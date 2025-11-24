"""
CORTEX 3.0 Pattern Learning Engine
Advanced Fusion - Milestone 3

Learns from successful temporal correlations to improve future suggestions.
Core component of CORTEX's adaptive fusion layer.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
Repository: https://github.com/asifhussain60/CORTEX
"""

import json
import sqlite3
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import logging
import re
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class PatternType(Enum):
    """Types of patterns the learning engine can recognize and learn from"""
    FILE_MENTION = "file_mention"      # Files frequently mentioned together
    PLAN_SEQUENCE = "plan_sequence"    # Common implementation sequences  
    CONTEXT = "context"                # Keywords correlating to specific files
    TEMPORAL = "temporal"              # Optimal time windows for correlation types


@dataclass
class CorrelationPattern:
    """A learned pattern from successful correlations"""
    pattern_id: str
    pattern_type: PatternType
    pattern_data: Dict[str, Any]
    confidence: float = 0.5
    usage_count: int = 0
    success_rate: float = 0.0
    created_at: datetime = None
    last_used: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.pattern_id is None:
            self.pattern_id = f"pattern_{self.pattern_type.value}_{uuid.uuid4().hex[:8]}"


@dataclass
class LearningSession:
    """A session where patterns were learned from correlations"""
    session_id: str
    conversation_id: str
    patterns_learned: int = 0
    patterns_applied: int = 0
    improvement_score: float = 0.0
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.session_id is None:
            self.session_id = f"learning_session_{uuid.uuid4().hex[:8]}"


class PatternLearningEngine:
    """
    CORTEX 3.0 Pattern Learning Engine
    
    Learns from successful temporal correlations to improve future suggestions.
    Builds patterns that help predict files, sequences, and optimal correlation windows.
    """
    
    def __init__(self, database_path: str):
        """
        Initialize the Pattern Learning Engine.
        
        Args:
            database_path: Path to SQLite database for pattern storage
        """
        self.database_path = database_path
        self._ensure_schema()
        
    def _ensure_schema(self) -> None:
        """Ensure database schema exists for pattern learning"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                # Create correlation_patterns table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS correlation_patterns (
                        pattern_id TEXT PRIMARY KEY,
                        pattern_type TEXT NOT NULL,
                        pattern_data TEXT NOT NULL,
                        confidence REAL DEFAULT 0.5,
                        usage_count INTEGER DEFAULT 0,
                        success_rate REAL DEFAULT 0.0,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        last_used DATETIME
                    )
                """)
                
                # Create pattern_learning_sessions table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS pattern_learning_sessions (
                        session_id TEXT PRIMARY KEY,
                        conversation_id TEXT NOT NULL,
                        patterns_learned INTEGER DEFAULT 0,
                        patterns_applied INTEGER DEFAULT 0,
                        improvement_score REAL DEFAULT 0.0,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create indexes for performance
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_patterns_type 
                    ON correlation_patterns(pattern_type)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_patterns_confidence 
                    ON correlation_patterns(confidence DESC)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_sessions_conversation 
                    ON pattern_learning_sessions(conversation_id)
                """)
                
                conn.commit()
                logger.info("Pattern learning database schema initialized")
                
        except sqlite3.Error as e:
            logger.error(f"Failed to initialize pattern learning schema: {e}")
            raise
    
    def learn_from_correlation(self, correlation_result: Dict[str, Any]) -> LearningSession:
        """
        Learn patterns from a successful temporal correlation result.
        
        Args:
            correlation_result: Result from TemporalCorrelator with correlation data
            
        Returns:
            LearningSession with details of what was learned
        """
        session = LearningSession(
            session_id=f"learning_{uuid.uuid4().hex[:8]}",
            conversation_id=correlation_result.get("conversation_id", "unknown")
        )
        
        try:
            # Extract and learn different types of patterns
            patterns_learned = []
            
            # Learn file mention patterns
            file_patterns = self._extract_file_mention_patterns(correlation_result)
            patterns_learned.extend(file_patterns)
            
            # Learn plan sequence patterns
            sequence_patterns = self._extract_plan_sequence_patterns(correlation_result)
            patterns_learned.extend(sequence_patterns)
            
            # Learn context patterns
            context_patterns = self._extract_context_patterns(correlation_result)
            patterns_learned.extend(context_patterns)
            
            # Learn temporal patterns
            temporal_patterns = self._extract_temporal_patterns(correlation_result)
            patterns_learned.extend(temporal_patterns)
            
            # Store learned patterns
            for pattern in patterns_learned:
                self._store_pattern(pattern)
            
            session.patterns_learned = len(patterns_learned)
            self._store_learning_session(session)
            
            logger.info(f"Learning session complete: {session.patterns_learned} patterns learned")
            return session
            
        except Exception as e:
            logger.error(f"Failed to learn from correlation: {e}")
            raise
    
    def _extract_file_mention_patterns(self, correlation_result: Dict[str, Any]) -> List[CorrelationPattern]:
        """Extract patterns about which files are mentioned together"""
        patterns = []
        
        try:
            file_mentions = correlation_result.get("file_mentions", [])
            correlations = correlation_result.get("correlations", [])
            
            if len(file_mentions) < 2:
                return patterns
            
            # Create co-occurrence patterns for files mentioned together
            for i in range(len(file_mentions)):
                for j in range(i + 1, len(file_mentions)):
                    file_a = file_mentions[i]
                    file_b = file_mentions[j]
                    
                    # Check if both files had correlations (indicating success)
                    if self._files_had_correlations(file_a, file_b, correlations):
                        pattern_data = {
                            "file_a": file_a,
                            "file_b": file_b,
                            "co_occurrence_type": "conversation_mention",
                            "confidence_boost": 0.15,  # Boost correlation confidence by 15%
                            "conversation_context": correlation_result.get("conversation_summary", "")
                        }
                        
                        pattern = CorrelationPattern(
                            pattern_id=None,  # Auto-generated
                            pattern_type=PatternType.FILE_MENTION,
                            pattern_data=pattern_data,
                            confidence=0.7,  # Start with moderate confidence
                            usage_count=1
                        )
                        patterns.append(pattern)
            
            return patterns
            
        except Exception as e:
            logger.error(f"Failed to extract file mention patterns: {e}")
            return []
    
    def _extract_plan_sequence_patterns(self, correlation_result: Dict[str, Any]) -> List[CorrelationPattern]:
        """Extract patterns about common implementation sequences"""
        patterns = []
        
        try:
            plan_mentions = correlation_result.get("plan_mentions", [])
            correlations = correlation_result.get("correlations", [])
            
            if len(plan_mentions) < 2:
                return patterns
            
            # Look for sequence patterns in plan phases
            for i in range(len(plan_mentions) - 1):
                current_phase = plan_mentions[i]
                next_phase = plan_mentions[i + 1]
                
                # Extract sequence pattern
                pattern_data = {
                    "phase_sequence": [current_phase, next_phase],
                    "sequence_type": "plan_to_implementation",
                    "confidence_boost": 0.12,
                    "typical_files": self._extract_files_from_correlations(correlations)
                }
                
                pattern = CorrelationPattern(
                    pattern_id=None,
                    pattern_type=PatternType.PLAN_SEQUENCE,
                    pattern_data=pattern_data,
                    confidence=0.6
                )
                patterns.append(pattern)
            
            return patterns
            
        except Exception as e:
            logger.error(f"Failed to extract plan sequence patterns: {e}")
            return []
    
    def _extract_context_patterns(self, correlation_result: Dict[str, Any]) -> List[CorrelationPattern]:
        """Extract patterns about keywords correlating to specific files"""
        patterns = []
        
        try:
            conversation_text = correlation_result.get("conversation_content", "")
            correlations = correlation_result.get("correlations", [])
            
            if not conversation_text or not correlations:
                return patterns
            
            # Extract keywords from conversation
            keywords = self._extract_keywords(conversation_text)
            
            # Group correlations by file
            files_with_correlations = {}
            for corr in correlations:
                file_path = corr.get("file_path", "")
                if file_path:
                    if file_path not in files_with_correlations:
                        files_with_correlations[file_path] = []
                    files_with_correlations[file_path].append(corr)
            
            # Create context patterns for keyword-file associations
            for file_path, file_correlations in files_with_correlations.items():
                if len(file_correlations) >= 2:  # File has multiple correlations = strong signal
                    pattern_data = {
                        "keywords": keywords,
                        "target_file": file_path,
                        "correlation_strength": len(file_correlations),
                        "confidence_boost": min(0.2, len(file_correlations) * 0.05)  # Max 20% boost
                    }
                    
                    pattern = CorrelationPattern(
                        pattern_id=None,
                        pattern_type=PatternType.CONTEXT,
                        pattern_data=pattern_data,
                        confidence=0.65
                    )
                    patterns.append(pattern)
            
            return patterns
            
        except Exception as e:
            logger.error(f"Failed to extract context patterns: {e}")
            return []
    
    def _extract_temporal_patterns(self, correlation_result: Dict[str, Any]) -> List[CorrelationPattern]:
        """Extract patterns about optimal time windows for correlations"""
        patterns = []
        
        try:
            correlations = correlation_result.get("correlations", [])
            conversation_timestamp = correlation_result.get("conversation_timestamp")
            
            if not correlations or not conversation_timestamp:
                return patterns
            
            # Analyze time deltas between conversation and file events
            time_deltas = []
            for corr in correlations:
                event_timestamp = corr.get("timestamp")
                if event_timestamp:
                    # Parse timestamps (assuming ISO format)
                    if isinstance(conversation_timestamp, str):
                        conv_time = datetime.fromisoformat(conversation_timestamp.replace('Z', '+00:00'))
                    else:
                        conv_time = conversation_timestamp
                        
                    if isinstance(event_timestamp, str):
                        event_time = datetime.fromisoformat(event_timestamp.replace('Z', '+00:00'))
                    else:
                        event_time = event_timestamp
                    
                    delta = abs((event_time - conv_time).total_seconds())
                    time_deltas.append(delta)
            
            if time_deltas:
                avg_delta = sum(time_deltas) / len(time_deltas)
                optimal_window = max(avg_delta * 1.5, 3600)  # At least 1 hour window
                
                pattern_data = {
                    "optimal_window_seconds": optimal_window,
                    "average_delta_seconds": avg_delta,
                    "correlation_count": len(correlations),
                    "window_confidence": min(0.9, len(correlations) / 10)  # More correlations = higher confidence
                }
                
                pattern = CorrelationPattern(
                    pattern_id=None,
                    pattern_type=PatternType.TEMPORAL,
                    pattern_data=pattern_data,
                    confidence=0.75
                )
                patterns.append(pattern)
            
            return patterns
            
        except Exception as e:
            logger.error(f"Failed to extract temporal patterns: {e}")
            return []
    
    def _files_had_correlations(self, file_a: str, file_b: str, correlations: List[Dict]) -> bool:
        """Check if both files had correlations in the result"""
        files_with_correlations = set()
        for corr in correlations:
            file_path = corr.get("file_path", "")
            if file_path:
                files_with_correlations.add(file_path)
        
        return file_a in files_with_correlations and file_b in files_with_correlations
    
    def _extract_files_from_correlations(self, correlations: List[Dict]) -> List[str]:
        """Extract unique file paths from correlation results"""
        files = set()
        for corr in correlations:
            file_path = corr.get("file_path", "")
            if file_path:
                files.add(file_path)
        return list(files)
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract significant keywords from conversation text"""
        # Simple keyword extraction (can be enhanced with NLP)
        # Remove common words and extract meaningful terms
        common_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'a', 'an', 'is', 'was', 'are', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should', 'could', 'can', 'may', 'might', 'must', 'shall', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
        
        # Extract words (alphanumeric, preserving common programming terms)
        words = re.findall(r'\b[a-zA-Z][a-zA-Z0-9_]*\b', text.lower())
        
        # Filter out common words and short words
        keywords = [word for word in words if len(word) > 3 and word not in common_words]
        
        # Return most frequent keywords (limit to avoid noise)
        from collections import Counter
        word_counts = Counter(keywords)
        return [word for word, count in word_counts.most_common(10)]
    
    def _store_pattern(self, pattern: CorrelationPattern) -> None:
        """Store a learned pattern in the database"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                # Check if similar pattern already exists
                existing_pattern = self._find_similar_pattern(pattern)
                
                if existing_pattern:
                    # Update existing pattern
                    self._merge_patterns(existing_pattern, pattern)
                else:
                    # Insert new pattern
                    cursor.execute("""
                        INSERT INTO correlation_patterns 
                        (pattern_id, pattern_type, pattern_data, confidence, usage_count, success_rate, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        pattern.pattern_id,
                        pattern.pattern_type.value,
                        json.dumps(pattern.pattern_data),
                        pattern.confidence,
                        pattern.usage_count,
                        pattern.success_rate,
                        pattern.created_at.isoformat()
                    ))
                
                conn.commit()
                
        except sqlite3.Error as e:
            logger.error(f"Failed to store pattern: {e}")
            raise
    
    def _store_learning_session(self, session: LearningSession) -> None:
        """Store a learning session record"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO pattern_learning_sessions 
                    (session_id, conversation_id, patterns_learned, patterns_applied, improvement_score, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    session.session_id,
                    session.conversation_id,
                    session.patterns_learned,
                    session.patterns_applied,
                    session.improvement_score,
                    session.created_at.isoformat()
                ))
                
                conn.commit()
                
        except sqlite3.Error as e:
            logger.error(f"Failed to store learning session: {e}")
            raise
    
    def _find_similar_pattern(self, pattern: CorrelationPattern) -> Optional[str]:
        """Find if a similar pattern already exists"""
        # For now, implement simple similarity based on pattern type and key data
        # Can be enhanced with more sophisticated similarity measures
        return None
    
    def _merge_patterns(self, existing_pattern_id: str, new_pattern: CorrelationPattern) -> None:
        """Merge a new pattern with an existing similar pattern"""
        # Update confidence and usage count for existing pattern
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE correlation_patterns 
                    SET usage_count = usage_count + 1,
                        confidence = (confidence + ?) / 2,
                        last_used = ?
                    WHERE pattern_id = ?
                """, (new_pattern.confidence, datetime.now().isoformat(), existing_pattern_id))
                
                conn.commit()
                
        except sqlite3.Error as e:
            logger.error(f"Failed to merge patterns: {e}")
            raise
    
    def suggest_files_for_conversation(self, conversation_text: str, conversation_metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Predict likely implementation files based on conversation content using learned patterns.
        
        Args:
            conversation_text: Text content of the conversation
            conversation_metadata: Optional metadata (timestamp, participants, etc.)
            
        Returns:
            List of file suggestions with confidence scores
        """
        suggestions = []
        
        try:
            # Extract keywords from conversation
            keywords = self._extract_keywords(conversation_text)
            
            # Get relevant patterns from database
            context_patterns = self._get_patterns_by_type(PatternType.CONTEXT)
            file_mention_patterns = self._get_patterns_by_type(PatternType.FILE_MENTION)
            
            # Score files based on context patterns
            file_scores = {}
            
            for pattern in context_patterns:
                pattern_keywords = pattern.get("pattern_data", {}).get("keywords", [])
                target_file = pattern.get("pattern_data", {}).get("target_file", "")
                
                if target_file:
                    # Calculate keyword overlap
                    keyword_overlap = len(set(keywords) & set(pattern_keywords))
                    if keyword_overlap > 0:
                        # Calculate confidence score with more generous scoring
                        overlap_ratio = keyword_overlap / min(len(keywords), len(pattern_keywords))
                        base_confidence = pattern.get("confidence", 0.5)
                        # Boost confidence for good keyword matches
                        confidence_multiplier = min(1.5, 1.0 + (overlap_ratio * 0.8))
                        suggestion_confidence = base_confidence * confidence_multiplier
                        
                        if target_file in file_scores:
                            file_scores[target_file] = max(file_scores[target_file], suggestion_confidence)
                        else:
                            file_scores[target_file] = suggestion_confidence
            
            # Apply file mention patterns for additional suggestions
            mentioned_files = self._extract_file_mentions_from_text(conversation_text)
            for mentioned_file in mentioned_files:
                for pattern in file_mention_patterns:
                    pattern_data = pattern.get("pattern_data", {})
                    file_a = pattern_data.get("file_a", "")
                    file_b = pattern_data.get("file_b", "")
                    
                    if mentioned_file in [file_a, file_b]:
                        # Suggest the other file
                        suggested_file = file_b if mentioned_file == file_a else file_a
                        confidence_boost = pattern_data.get("confidence_boost", 0.1)
                        base_confidence = pattern.get("confidence", 0.5)
                        
                        suggestion_confidence = base_confidence + confidence_boost
                        if suggested_file in file_scores:
                            file_scores[suggested_file] += suggestion_confidence
                        else:
                            file_scores[suggested_file] = suggestion_confidence
            
            # Convert to suggestion format
            for file_path, confidence in file_scores.items():
                suggestions.append({
                    "file_path": file_path,
                    "confidence": min(confidence, 0.95),  # Cap at 95%
                    "reasoning": "Pattern-based prediction from conversation analysis",
                    "pattern_types": ["context", "file_mention"]
                })
            
            # Sort by confidence
            suggestions.sort(key=lambda x: x["confidence"], reverse=True)
            
            return suggestions[:10]  # Return top 10 suggestions
            
        except Exception as e:
            logger.error(f"Failed to suggest files for conversation: {e}")
            return []
    
    def boost_confidence_from_patterns(self, correlation_candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Use learned patterns to boost correlation confidence scores.
        
        Args:
            correlation_candidates: List of potential correlations with base confidence
            
        Returns:
            Same list with updated confidence scores based on patterns
        """
        try:
            # Get all patterns for confidence boosting
            patterns = self._get_all_patterns()
            
            for candidate in correlation_candidates:
                file_path = candidate.get("file_path", "")
                timestamp = candidate.get("timestamp")
                base_confidence = candidate.get("confidence", 0.0)
                
                # Apply pattern-based confidence boosts
                confidence_boost = 0.0
                
                # Check file mention patterns
                for pattern in patterns:
                    if pattern.get("pattern_type") == PatternType.FILE_MENTION.value:
                        pattern_data = pattern.get("pattern_data", {})
                        if file_path in [pattern_data.get("file_a"), pattern_data.get("file_b")]:
                            boost = pattern_data.get("confidence_boost", 0.0)
                            pattern_confidence = pattern.get("confidence", 0.5)
                            confidence_boost += boost * pattern_confidence
                
                # Check temporal patterns
                for pattern in patterns:
                    if pattern.get("pattern_type") == PatternType.TEMPORAL.value:
                        pattern_data = pattern.get("pattern_data", {})
                        optimal_window = pattern_data.get("optimal_window_seconds", 3600)
                        window_confidence = pattern_data.get("window_confidence", 0.5)
                        
                        # If correlation is within optimal window, boost confidence
                        # (This would require conversation timestamp comparison)
                        # For now, apply a small boost to all correlations
                        confidence_boost += 0.05 * window_confidence
                
                # Update candidate confidence
                new_confidence = min(base_confidence + confidence_boost, 0.95)
                candidate["confidence"] = new_confidence
                candidate["pattern_boost"] = confidence_boost
                
                # Track pattern usage
                self._update_pattern_usage(file_path)
            
            return correlation_candidates
            
        except Exception as e:
            logger.error(f"Failed to boost confidence from patterns: {e}")
            return correlation_candidates
    
    def _extract_file_mentions_from_text(self, text: str) -> List[str]:
        """Extract file mentions from conversation text"""
        # Look for file patterns
        file_patterns = [
            r'\b\w+\.[a-zA-Z]{2,4}\b',  # Simple file extensions
            r'\b\w+Controller\b',        # Controller pattern
            r'\b\w+Service\b',          # Service pattern
            r'\b\w+Model\b',            # Model pattern
            r'\b\w+Tests?\b'            # Test pattern
        ]
        
        files = set()
        for pattern in file_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            files.update(matches)
        
        return list(files)
    
    def _get_patterns_by_type(self, pattern_type: PatternType) -> List[Dict[str, Any]]:
        """Get all patterns of a specific type from database"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT pattern_id, pattern_type, pattern_data, confidence, usage_count, success_rate
                    FROM correlation_patterns 
                    WHERE pattern_type = ?
                    ORDER BY confidence DESC, usage_count DESC
                """, (pattern_type.value,))
                
                patterns = []
                for row in cursor.fetchall():
                    pattern = {
                        "pattern_id": row[0],
                        "pattern_type": row[1],
                        "pattern_data": json.loads(row[2]),
                        "confidence": row[3],
                        "usage_count": row[4],
                        "success_rate": row[5]
                    }
                    patterns.append(pattern)
                
                return patterns
                
        except sqlite3.Error as e:
            logger.error(f"Failed to get patterns by type: {e}")
            return []
    
    def _get_all_patterns(self) -> List[Dict[str, Any]]:
        """Get all patterns from database"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT pattern_id, pattern_type, pattern_data, confidence, usage_count, success_rate
                    FROM correlation_patterns 
                    ORDER BY confidence DESC, usage_count DESC
                """)
                
                patterns = []
                for row in cursor.fetchall():
                    pattern = {
                        "pattern_id": row[0],
                        "pattern_type": row[1],
                        "pattern_data": json.loads(row[2]),
                        "confidence": row[3],
                        "usage_count": row[4],
                        "success_rate": row[5]
                    }
                    patterns.append(pattern)
                
                return patterns
                
        except sqlite3.Error as e:
            logger.error(f"Failed to get all patterns: {e}")
            return []
    
    def _update_pattern_usage(self, file_path: str) -> None:
        """Update pattern usage statistics when patterns are used"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                # Update usage count for patterns involving this file
                cursor.execute("""
                    UPDATE correlation_patterns 
                    SET usage_count = usage_count + 1,
                        last_used = ?
                    WHERE pattern_data LIKE ?
                """, (datetime.now().isoformat(), f"%{file_path}%"))
                
                conn.commit()
                
        except sqlite3.Error as e:
            logger.error(f"Failed to update pattern usage: {e}")
    
    def get_learning_statistics(self) -> Dict[str, Any]:
        """Get statistics about pattern learning progress"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                # Get pattern counts by type
                cursor.execute("""
                    SELECT pattern_type, COUNT(*) as count, AVG(confidence) as avg_confidence
                    FROM correlation_patterns 
                    GROUP BY pattern_type
                """)
                pattern_stats = {row[0]: {"count": row[1], "avg_confidence": row[2]} for row in cursor.fetchall()}
                
                # Get total patterns and usage
                cursor.execute("""
                    SELECT COUNT(*) as total_patterns, 
                           SUM(usage_count) as total_usage,
                           AVG(confidence) as overall_confidence
                    FROM correlation_patterns
                """)
                row = cursor.fetchone()
                total_stats = {
                    "total_patterns": row[0] or 0,
                    "total_usage": row[1] or 0,
                    "overall_confidence": row[2] or 0.0
                }
                
                # Get learning session stats
                cursor.execute("""
                    SELECT COUNT(*) as session_count,
                           AVG(patterns_learned) as avg_patterns_per_session,
                           SUM(patterns_learned) as total_learned
                    FROM pattern_learning_sessions
                """)
                row = cursor.fetchone()
                session_stats = {
                    "learning_sessions": row[0] or 0,
                    "avg_patterns_per_session": row[1] or 0.0,
                    "total_patterns_learned": row[2] or 0
                }
                
                return {
                    "pattern_statistics": pattern_stats,
                    "overall_statistics": total_stats,
                    "learning_statistics": session_stats,
                    "learning_engine_status": "operational"
                }
                
        except sqlite3.Error as e:
            logger.error(f"Failed to get learning statistics: {e}")
            return {"learning_engine_status": "error", "error": str(e)}
    
    def export_patterns(self, output_file: str) -> bool:
        """Export learned patterns to a JSON file for backup or analysis"""
        try:
            patterns = self._get_all_patterns()
            
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "pattern_count": len(patterns),
                "patterns": patterns
            }
            
            with open(output_file, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            logger.info(f"Exported {len(patterns)} patterns to {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export patterns: {e}")
            return False