"""
Relevance Scorer for Tier 1 Working Memory

Scores conversations based on relevance to current user request and context.
Enables intelligent context loading (load most relevant conversations, not just most recent).

Scoring Factors:
1. Entity Overlap (40%): Files, classes, methods mentioned in both contexts
2. Temporal Proximity (20%): Recent conversations score higher
3. Topic Similarity (30%): Keyword/intent matching
4. Work Continuity (10%): Same feature/bug context

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta
import re
from collections import Counter


class RelevanceScorer:
    """
    Scores conversation relevance for intelligent context loading.
    
    Responsibilities:
    1. Calculate entity overlap between conversations and current request
    2. Apply temporal decay (recent = higher score)
    3. Match topics and intents
    4. Detect work continuity (same feature/component)
    5. Return normalized relevance score (0.0-1.0)
    """
    
    # Weight factors for scoring
    ENTITY_OVERLAP_WEIGHT = 0.4
    TEMPORAL_PROXIMITY_WEIGHT = 0.2
    TOPIC_SIMILARITY_WEIGHT = 0.3
    WORK_CONTINUITY_WEIGHT = 0.1
    
    # Temporal decay parameters
    RECENT_THRESHOLD_HOURS = 24  # Last 24 hours = full temporal score
    DECAY_HALF_LIFE_DAYS = 7  # Score halves every 7 days
    
    # Topic keywords by category
    TOPIC_KEYWORDS = {
        'authentication': ['auth', 'login', 'password', 'jwt', 'token', 'session', 'oauth'],
        'ui': ['button', 'form', 'dialog', 'modal', 'component', 'style', 'layout', 'ui'],
        'database': ['database', 'query', 'sql', 'schema', 'migration', 'entity', 'table'],
        'api': ['api', 'endpoint', 'rest', 'graphql', 'request', 'response', 'http'],
        'testing': ['test', 'unit', 'integration', 'mock', 'fixture', 'assert', 'coverage'],
        'performance': ['performance', 'optimize', 'slow', 'cache', 'memory', 'cpu', 'speed'],
        'bug': ['bug', 'error', 'issue', 'crash', 'exception', 'fail', 'broken'],
        'refactor': ['refactor', 'clean', 'improve', 'restructure', 'simplify'],
    }
    
    def __init__(self):
        """Initialize relevance scorer."""
        pass
    
    def score_conversation_relevance(
        self,
        conversation: Dict,
        current_request: str,
        current_file: Optional[str] = None,
        active_entities: Optional[Dict[str, List[str]]] = None
    ) -> float:
        """
        Calculate relevance score for a conversation.
        
        Args:
            conversation: Conversation dict with metadata
            current_request: User's current request text
            current_file: Currently open file path (optional)
            active_entities: Currently active entities dict (optional)
            
        Returns:
            Relevance score (0.0-1.0)
        """
        # Extract conversation data
        conv_entities = self._extract_conversation_entities(conversation)
        conv_text = self._get_conversation_text(conversation)
        conv_timestamp = conversation.get('created_at') or conversation.get('updated_at')
        
        # Calculate component scores
        entity_score = self._calculate_entity_overlap(
            conv_entities,
            current_request,
            current_file,
            active_entities
        )
        
        temporal_score = self._calculate_temporal_proximity(conv_timestamp)
        
        topic_score = self._calculate_topic_similarity(
            conv_text,
            current_request
        )
        
        continuity_score = self._calculate_work_continuity(
            conversation,
            current_request,
            current_file
        )
        
        # Weighted final score
        final_score = (
            entity_score * self.ENTITY_OVERLAP_WEIGHT +
            temporal_score * self.TEMPORAL_PROXIMITY_WEIGHT +
            topic_score * self.TOPIC_SIMILARITY_WEIGHT +
            continuity_score * self.WORK_CONTINUITY_WEIGHT
        )
        
        return min(1.0, max(0.0, final_score))
    
    def _extract_conversation_entities(self, conversation: Dict) -> Dict[str, Set[str]]:
        """
        Extract entities from conversation metadata.
        
        Args:
            conversation: Conversation dict
            
        Returns:
            Dict with entity sets (files, classes, methods, ui_components)
        """
        entities = {
            'files': set(),
            'classes': set(),
            'methods': set(),
            'ui_components': set()
        }
        
        # Get entities from metadata if available
        metadata = conversation.get('metadata', {})
        if isinstance(metadata, dict):
            for entity_type in entities.keys():
                entity_list = metadata.get(entity_type, [])
                if isinstance(entity_list, list):
                    entities[entity_type].update(entity_list)
        
        # Also extract from tags
        tags = conversation.get('tags', [])
        if isinstance(tags, str):
            tags = tags.split(',')
        
        for tag in tags:
            tag = tag.strip()
            if '.' in tag:  # Likely a file
                entities['files'].add(tag)
            elif tag and tag[0].isupper():  # PascalCase - likely class
                entities['classes'].add(tag)
        
        return entities
    
    def _get_conversation_text(self, conversation: Dict) -> str:
        """
        Get conversation text for analysis.
        
        Args:
            conversation: Conversation dict
            
        Returns:
            Combined text from title, summary, and messages
        """
        text_parts = []
        
        # Add title and summary
        if conversation.get('title'):
            text_parts.append(conversation['title'])
        if conversation.get('summary'):
            text_parts.append(conversation['summary'])
        
        # Add messages if available
        messages = conversation.get('messages', [])
        for msg in messages:
            if isinstance(msg, dict) and msg.get('content'):
                text_parts.append(msg['content'])
        
        return ' '.join(text_parts)
    
    def _calculate_entity_overlap(
        self,
        conv_entities: Dict[str, Set[str]],
        current_request: str,
        current_file: Optional[str],
        active_entities: Optional[Dict[str, List[str]]]
    ) -> float:
        """
        Calculate entity overlap score (0.0-1.0).
        
        Measures how many entities from the conversation appear in:
        - Current request text
        - Currently open file
        - Active entities from recent work
        
        Args:
            conv_entities: Entities from conversation
            current_request: Current user request
            current_file: Currently open file
            active_entities: Active entities dict
            
        Returns:
            Entity overlap score (0.0-1.0)
        """
        if not conv_entities:
            return 0.0
        
        # Count total entities in conversation
        total_entities = sum(len(entities) for entities in conv_entities.values())
        if total_entities == 0:
            return 0.0
        
        matches = 0
        
        # Check file matches
        if current_file:
            current_file_name = current_file.split('/')[-1]
            for conv_file in conv_entities['files']:
                conv_file_name = conv_file.split('/')[-1]
                if current_file_name == conv_file_name:
                    matches += 2  # Files are very strong signals
        
        # Check entity matches in current request
        current_request_lower = current_request.lower()
        for entity_type, entity_set in conv_entities.items():
            for entity in entity_set:
                if entity.lower() in current_request_lower:
                    matches += 1
        
        # Check entity matches in active entities
        if active_entities:
            for entity_type, active_list in active_entities.items():
                conv_set = conv_entities.get(entity_type, set())
                active_set = set(active_list) if active_list else set()
                matches += len(conv_set & active_set)
        
        # Normalize score (cap at 1.0)
        score = min(1.0, matches / max(1, total_entities))
        return score
    
    def _calculate_temporal_proximity(self, conv_timestamp: Optional[str]) -> float:
        """
        Calculate temporal proximity score with exponential decay.
        
        Recent conversations score higher. Decay function:
        - Last 24 hours: 1.0 (full score)
        - After 24h: Exponential decay with 7-day half-life
        
        Args:
            conv_timestamp: Conversation timestamp (ISO format or datetime object)
            
        Returns:
            Temporal score (0.0-1.0)
        """
        if not conv_timestamp:
            return 0.0
        
        # Parse timestamp
        if isinstance(conv_timestamp, str):
            try:
                conv_time = datetime.fromisoformat(conv_timestamp.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                return 0.0
        elif isinstance(conv_timestamp, datetime):
            conv_time = conv_timestamp
        else:
            return 0.0
        
        # Calculate age
        now = datetime.now(conv_time.tzinfo) if conv_time.tzinfo else datetime.now()
        age = now - conv_time
        age_hours = age.total_seconds() / 3600
        
        # Full score for recent conversations
        if age_hours <= self.RECENT_THRESHOLD_HOURS:
            return 1.0
        
        # Exponential decay after threshold
        age_days = age.total_seconds() / 86400
        decay_factor = 0.5 ** (age_days / self.DECAY_HALF_LIFE_DAYS)
        
        return max(0.0, decay_factor)
    
    def _calculate_topic_similarity(self, conv_text: str, current_request: str) -> float:
        """
        Calculate topic similarity using keyword matching.
        
        Args:
            conv_text: Conversation text
            current_request: Current user request
            
        Returns:
            Topic similarity score (0.0-1.0)
        """
        if not conv_text or not current_request:
            return 0.0
        
        conv_text_lower = conv_text.lower()
        request_lower = current_request.lower()
        
        # Extract keywords from both texts
        conv_keywords = self._extract_keywords(conv_text_lower)
        request_keywords = self._extract_keywords(request_lower)
        
        if not request_keywords:
            return 0.0
        
        # Calculate keyword overlap
        common_keywords = conv_keywords & request_keywords
        keyword_score = len(common_keywords) / len(request_keywords)
        
        # Check for topic category matches
        conv_topics = self._detect_topics(conv_text_lower)
        request_topics = self._detect_topics(request_lower)
        
        topic_overlap = len(conv_topics & request_topics)
        topic_score = topic_overlap / max(1, len(request_topics))
        
        # Combine scores (keyword matching + topic matching)
        final_score = 0.6 * keyword_score + 0.4 * topic_score
        
        return min(1.0, final_score)
    
    def _extract_keywords(self, text: str) -> Set[str]:
        """
        Extract meaningful keywords from text.
        
        Args:
            text: Input text
            
        Returns:
            Set of keywords
        """
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
            'do', 'does', 'did', 'will', 'would', 'could', 'should', 'can', 'may',
            'i', 'you', 'he', 'she', 'it', 'we', 'they', 'this', 'that', 'these', 'those'
        }
        
        # Extract words (alphanumeric sequences)
        words = re.findall(r'\b[a-z][a-z0-9]*\b', text)
        
        # Filter out stop words and short words
        keywords = {w for w in words if len(w) >= 3 and w not in stop_words}
        
        return keywords
    
    def _detect_topics(self, text: str) -> Set[str]:
        """
        Detect topic categories in text.
        
        Args:
            text: Input text
            
        Returns:
            Set of detected topic names
        """
        detected_topics = set()
        
        for topic, keywords in self.TOPIC_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    detected_topics.add(topic)
                    break  # One match per topic is enough
        
        return detected_topics
    
    def _calculate_work_continuity(
        self,
        conversation: Dict,
        current_request: str,
        current_file: Optional[str]
    ) -> float:
        """
        Calculate work continuity score.
        
        Detects if conversation is part of the same feature/bug/component.
        
        Args:
            conversation: Conversation dict
            current_request: Current user request
            current_file: Currently open file
            
        Returns:
            Work continuity score (0.0-1.0)
        """
        score = 0.0
        
        # Check if same file is involved
        conv_entities = self._extract_conversation_entities(conversation)
        if current_file:
            current_file_name = current_file.split('/')[-1]
            for conv_file in conv_entities['files']:
                if current_file_name in conv_file:
                    score += 0.5
                    break
        
        # Check for continuation phrases
        continuation_patterns = [
            r'\bcontinue\b',
            r'\bresume\b',
            r'\bfinish\b',
            r'\bcomplete\b',
            r'\bkeep\s+working\b',
            r'\bpick\s+up\s+where\b'
        ]
        
        request_lower = current_request.lower()
        for pattern in continuation_patterns:
            if re.search(pattern, request_lower):
                score += 0.5
                break
        
        return min(1.0, score)
    
    def rank_conversations(
        self,
        conversations: List[Dict],
        current_request: str,
        current_file: Optional[str] = None,
        active_entities: Optional[Dict[str, List[str]]] = None,
        top_n: int = 5
    ) -> List[tuple]:
        """
        Rank conversations by relevance and return top N.
        
        Args:
            conversations: List of conversation dicts
            current_request: Current user request
            current_file: Currently open file
            active_entities: Active entities dict
            top_n: Number of top conversations to return
            
        Returns:
            List of (conversation, score) tuples, sorted by score descending
        """
        scored_conversations = []
        
        for conv in conversations:
            score = self.score_conversation_relevance(
                conv,
                current_request,
                current_file,
                active_entities
            )
            scored_conversations.append((conv, score))
        
        # Sort by score descending
        scored_conversations.sort(key=lambda x: x[1], reverse=True)
        
        # Return top N
        return scored_conversations[:top_n]
