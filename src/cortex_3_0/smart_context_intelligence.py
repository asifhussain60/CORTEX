"""
CORTEX 3.0 Smart Context Intelligence System
===========================================

Intelligent context management with ML-based insights:
- Predictive Context Loading: Anticipate what context will be needed
- Adaptive Memory Management: Learn from usage patterns
- Cross-Session Context Continuity: Maintain context across sessions
- Intelligent Pattern Recognition: ML-enhanced pattern matching

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import logging
import math
import os
from collections import defaultdict, deque

from ..tier1.working_memory import WorkingMemory
from ..tier2.knowledge_graph import KnowledgeGraph
from ..tier3.context_intelligence import ContextIntelligence


class ContextType(Enum):
    """Types of context for intelligent management"""
    CONVERSATION = "conversation"
    FILE = "file"
    PROJECT = "project"
    WORKFLOW = "workflow"
    PATTERN = "pattern"
    SESSION = "session"


class PredictionConfidence(Enum):
    """Confidence levels for context predictions"""
    LOW = 0.3
    MEDIUM = 0.6
    HIGH = 0.8
    VERY_HIGH = 0.9


@dataclass
class ContextItem:
    """Individual context item with metadata"""
    context_id: str
    context_type: ContextType
    content: Dict[str, Any]
    relevance_score: float = 0.0
    last_accessed: datetime = field(default_factory=datetime.now)
    access_frequency: int = 0
    prediction_confidence: float = 0.0
    size_bytes: int = 0
    
    
@dataclass
class ContextPrediction:
    """Prediction about what context will be needed"""
    context_id: str
    predicted_need_time: datetime
    confidence: PredictionConfidence
    reasoning: str
    trigger_patterns: List[str] = field(default_factory=list)


@dataclass
class SessionContext:
    """Context maintained across a user session"""
    session_id: str
    user_intent: str
    active_files: List[str]
    current_workflow: Optional[str]
    context_history: List[str]
    learned_patterns: List[Dict[str, Any]]
    start_time: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)


class ContextUsagePattern:
    """Tracks and learns from context usage patterns"""
    
    def __init__(self):
        self.access_patterns = defaultdict(list)  # context_id -> access times
        self.co_access_patterns = defaultdict(set)  # context_id -> frequently co-accessed contexts
        self.temporal_patterns = defaultdict(list)  # time_of_day -> commonly accessed contexts
        self.sequence_patterns = deque(maxlen=100)  # recent access sequences
        
    def record_access(self, context_id: str, timestamp: datetime = None):
        """Record context access for pattern learning"""
        if timestamp is None:
            timestamp = datetime.now()
            
        self.access_patterns[context_id].append(timestamp)
        self.sequence_patterns.append((context_id, timestamp))
        
        # Track temporal patterns (hour of day)
        hour = timestamp.hour
        self.temporal_patterns[hour].append(context_id)
        
        # Track co-access patterns (within 5 minutes)
        recent_window = timestamp - timedelta(minutes=5)
        for other_context, other_time in list(self.sequence_patterns)[-10:]:
            if other_time > recent_window and other_context != context_id:
                self.co_access_patterns[context_id].add(other_context)
                self.co_access_patterns[other_context].add(context_id)
                
    def predict_next_context(self, current_context: str, current_time: datetime) -> List[ContextPrediction]:
        """Predict what context might be needed next"""
        predictions = []
        
        # Pattern 1: Co-access patterns
        for related_context in self.co_access_patterns.get(current_context, set()):
            confidence = self._calculate_co_access_confidence(current_context, related_context)
            predictions.append(ContextPrediction(
                context_id=related_context,
                predicted_need_time=current_time + timedelta(minutes=2),
                confidence=PredictionConfidence(confidence),
                reasoning=f"Frequently accessed together with {current_context}",
                trigger_patterns=["co_access"]
            ))
            
        # Pattern 2: Temporal patterns
        hour = current_time.hour
        common_contexts = self._get_common_contexts_for_hour(hour)
        for context_id, frequency in common_contexts:
            if context_id not in [p.context_id for p in predictions]:
                confidence = min(0.9, frequency * 0.1)
                predictions.append(ContextPrediction(
                    context_id=context_id,
                    predicted_need_time=current_time + timedelta(minutes=5),
                    confidence=PredictionConfidence(confidence),
                    reasoning=f"Commonly accessed at {hour}:00",
                    trigger_patterns=["temporal"]
                ))
                
        # Pattern 3: Sequential patterns
        sequence_predictions = self._predict_from_sequences(current_context, current_time)
        predictions.extend(sequence_predictions)
        
        # Sort by confidence and return top predictions
        predictions.sort(key=lambda p: p.confidence.value, reverse=True)
        return predictions[:5]
        
    def _calculate_co_access_confidence(self, context1: str, context2: str) -> float:
        """Calculate confidence for co-access prediction"""
        context1_accesses = len(self.access_patterns[context1])
        if context1_accesses == 0:
            return 0.0
            
        co_access_count = len([
            1 for time1 in self.access_patterns[context1]
            for time2 in self.access_patterns[context2]
            if abs((time1 - time2).total_seconds()) < 300  # Within 5 minutes
        ])
        
        return min(0.9, co_access_count / context1_accesses)
        
    def _get_common_contexts_for_hour(self, hour: int) -> List[Tuple[str, float]]:
        """Get commonly accessed contexts for a specific hour"""
        contexts = self.temporal_patterns[hour]
        context_counts = defaultdict(int)
        
        for context in contexts:
            context_counts[context] += 1
            
        total = len(contexts)
        if total == 0:
            return []
            
        return [(context, count/total) for context, count in context_counts.items()]
        
    def _predict_from_sequences(self, current_context: str, current_time: datetime) -> List[ContextPrediction]:
        """Predict next context based on historical sequences"""
        predictions = []
        
        # Find sequences where current_context appeared
        sequences = list(self.sequence_patterns)
        following_contexts = defaultdict(int)
        
        for i, (context, _) in enumerate(sequences[:-1]):
            if context == current_context:
                next_context, _ = sequences[i + 1]
                following_contexts[next_context] += 1
                
        total_sequences = sum(following_contexts.values())
        if total_sequences == 0:
            return predictions
            
        for next_context, count in following_contexts.items():
            confidence = count / total_sequences
            if confidence > 0.3:  # Only include confident predictions
                predictions.append(ContextPrediction(
                    context_id=next_context,
                    predicted_need_time=current_time + timedelta(minutes=1),
                    confidence=PredictionConfidence(confidence),
                    reasoning=f"Followed {current_context} in {count}/{total_sequences} sequences",
                    trigger_patterns=["sequence"]
                ))
                
        return predictions


class AdaptiveMemoryManager:
    """Manages memory allocation based on context usage patterns"""
    
    def __init__(self, max_memory_mb: int = 512):
        self.max_memory_mb = max_memory_mb
        self.current_memory_usage = 0
        self.cached_contexts = {}  # context_id -> ContextItem
        self.usage_patterns = ContextUsagePattern()
        self.logger = logging.getLogger(__name__)
        
    def cache_context(self, context: ContextItem, predicted: bool = False):
        """Add context to cache with adaptive management"""
        
        # Calculate context size
        size_mb = context.size_bytes / (1024 * 1024)
        
        # Check if we need to free memory
        if self.current_memory_usage + size_mb > self.max_memory_mb:
            self._evict_contexts(size_mb)
            
        # Cache the context
        self.cached_contexts[context.context_id] = context
        self.current_memory_usage += size_mb
        
        # Record access pattern
        if not predicted:
            self.usage_patterns.record_access(context.context_id)
            context.access_frequency += 1
            context.last_accessed = datetime.now()
            
        self.logger.debug(f"Cached context: {context.context_id} ({size_mb:.1f}MB)")
        
    def get_context(self, context_id: str) -> Optional[ContextItem]:
        """Retrieve context from cache"""
        
        context = self.cached_contexts.get(context_id)
        if context:
            # Update access patterns
            self.usage_patterns.record_access(context_id)
            context.access_frequency += 1
            context.last_accessed = datetime.now()
            
        return context
        
    def predict_and_preload(self, current_context: str):
        """Predict and preload likely needed contexts"""
        
        predictions = self.usage_patterns.predict_next_context(current_context, datetime.now())
        
        for prediction in predictions:
            if (prediction.context_id not in self.cached_contexts and
                prediction.confidence.value > 0.6):
                
                # Try to load predicted context
                predicted_context = self._load_context(prediction.context_id)
                if predicted_context:
                    predicted_context.prediction_confidence = prediction.confidence.value
                    self.cache_context(predicted_context, predicted=True)
                    
                    self.logger.info(
                        f"Preloaded context: {prediction.context_id} "
                        f"(confidence: {prediction.confidence.value:.2f})"
                    )
                    
    def _evict_contexts(self, required_mb: float):
        """Evict contexts to free up memory"""
        
        # Calculate eviction scores (lower = more likely to evict)
        scored_contexts = []
        for context in self.cached_contexts.values():
            score = self._calculate_eviction_score(context)
            scored_contexts.append((score, context))
            
        # Sort by score (lowest first)
        scored_contexts.sort(key=lambda x: x[0])
        
        # Evict contexts until we have enough space
        freed_space = 0
        contexts_to_evict = []
        
        for score, context in scored_contexts:
            if freed_space >= required_mb:
                break
                
            context_size = context.size_bytes / (1024 * 1024)
            contexts_to_evict.append(context.context_id)
            freed_space += context_size
            
        # Actually evict the contexts
        for context_id in contexts_to_evict:
            self._evict_context(context_id)
            
        self.logger.info(f"Evicted {len(contexts_to_evict)} contexts, freed {freed_space:.1f}MB")
        
    def _calculate_eviction_score(self, context: ContextItem) -> float:
        """Calculate eviction score (lower = more likely to evict)"""
        
        # Time-based decay
        hours_since_access = (datetime.now() - context.last_accessed).total_seconds() / 3600
        time_score = math.exp(-hours_since_access / 24)  # Decay over 24 hours
        
        # Frequency score
        freq_score = min(1.0, context.access_frequency / 10)  # Normalize to 0-1
        
        # Prediction confidence score
        pred_score = context.prediction_confidence
        
        # Combined score (higher = keep, lower = evict)
        return (time_score * 0.4) + (freq_score * 0.4) + (pred_score * 0.2)
        
    def _evict_context(self, context_id: str):
        """Remove context from cache"""
        
        context = self.cached_contexts.pop(context_id, None)
        if context:
            size_mb = context.size_bytes / (1024 * 1024)
            self.current_memory_usage -= size_mb
            
    def _load_context(self, context_id: str) -> Optional[ContextItem]:
        """Load context from storage (placeholder implementation)"""
        # This would integrate with actual context storage systems
        return None
        

class CrossSessionContextManager:
    """Manages context continuity across user sessions"""
    
    def __init__(self, storage_path: str):
        self.storage_path = storage_path
        self.active_sessions = {}  # session_id -> SessionContext
        self.logger = logging.getLogger(__name__)
        
    def start_session(self, user_request: str) -> str:
        """Start a new session with context continuity"""
        
        session_id = f"session_{int(datetime.now().timestamp())}"
        
        # Analyze request to understand intent
        intent = self._extract_intent(user_request)
        
        # Load relevant context from previous sessions
        previous_context = self._load_relevant_previous_context(intent, user_request)
        
        # Create session context
        session_context = SessionContext(
            session_id=session_id,
            user_intent=intent,
            active_files=previous_context.get("files", []),
            current_workflow=previous_context.get("workflow"),
            context_history=previous_context.get("history", []),
            learned_patterns=previous_context.get("patterns", [])
        )
        
        self.active_sessions[session_id] = session_context
        
        self.logger.info(f"Started session: {session_id} with intent: {intent}")
        return session_id
        
    def update_session_context(self, session_id: str, update: Dict[str, Any]):
        """Update session context with new information"""
        
        session = self.active_sessions.get(session_id)
        if not session:
            return
            
        # Update relevant fields
        if "files" in update:
            session.active_files.extend(update["files"])
            
        if "workflow" in update:
            session.current_workflow = update["workflow"]
            
        if "patterns" in update:
            session.learned_patterns.extend(update["patterns"])
            
        session.last_activity = datetime.now()
        
    def end_session(self, session_id: str):
        """End session and save context for future use"""
        
        session = self.active_sessions.pop(session_id, None)
        if not session:
            return
            
        # Save session context for future reference
        self._save_session_context(session)
        
        self.logger.info(f"Ended session: {session_id}")
        
    def _extract_intent(self, user_request: str) -> str:
        """Extract user intent from request"""
        # Simplified intent extraction - would use ML in full implementation
        
        request_lower = user_request.lower()
        
        if any(word in request_lower for word in ["implement", "create", "build", "add"]):
            return "implementation"
        elif any(word in request_lower for word in ["fix", "debug", "error", "bug"]):
            return "debugging"
        elif any(word in request_lower for word in ["test", "verify", "validate"]):
            return "testing"
        elif any(word in request_lower for word in ["refactor", "optimize", "improve"]):
            return "optimization"
        else:
            return "general"
            
    def _load_relevant_previous_context(self, intent: str, request: str) -> Dict[str, Any]:
        """Load relevant context from previous sessions"""
        # Placeholder implementation - would query stored session data
        
        return {
            "files": [],
            "workflow": None,
            "history": [],
            "patterns": []
        }
        
    def _save_session_context(self, session: SessionContext):
        """Save session context for future reference"""
        # Placeholder implementation - would save to persistent storage
        pass


class SmartContextIntelligence:
    """Main smart context intelligence system for CORTEX 3.0"""
    
    def __init__(self, cortex_brain_path: str, max_memory_mb: int = 512):
        self.cortex_brain_path = cortex_brain_path
        
        # Ensure directories exist
        os.makedirs(f"{cortex_brain_path}/tier1", exist_ok=True)
        os.makedirs(f"{cortex_brain_path}/tier2", exist_ok=True)
        os.makedirs(f"{cortex_brain_path}/tier3", exist_ok=True)
        
        # Initialize components
        self.memory_manager = AdaptiveMemoryManager(max_memory_mb)
        self.session_manager = CrossSessionContextManager(cortex_brain_path)
        
        # Initialize existing CORTEX systems
        self.tier1 = WorkingMemory(f"{cortex_brain_path}/tier1/working_memory.db")
        self.tier2 = KnowledgeGraph(f"{cortex_brain_path}/tier2")
        self.tier3 = ContextIntelligence(f"{cortex_brain_path}/tier3")
        
        self.logger = logging.getLogger(__name__)
        
    async def start_intelligent_session(self, user_request: str) -> str:
        """Start a new intelligent session with predictive context loading"""
        
        # Start session
        session_id = self.session_manager.start_session(user_request)
        
        # Predict and preload likely needed context
        await self._predictive_context_loading(user_request, session_id)
        
        return session_id
        
    async def get_intelligent_context(self, session_id: str, context_query: str) -> Dict[str, Any]:
        """Get intelligently assembled context for a query"""
        
        # Get relevant contexts from all tiers
        tier1_context = await self._get_tier1_context(context_query)
        tier2_context = await self._get_tier2_context(context_query)
        tier3_context = await self._get_tier3_context(context_query)
        
        # Predict what additional context might be needed
        if tier1_context:
            current_context = f"tier1_{tier1_context.get('conversation_id', 'unknown')}"
            self.memory_manager.predict_and_preload(current_context)
        
        # Assemble intelligent context
        intelligent_context = {
            "session_id": session_id,
            "query": context_query,
            "assembled_context": {
                "tier1": tier1_context,
                "tier2": tier2_context,
                "tier3": tier3_context
            },
            "predicted_needs": self._get_predicted_context_needs(context_query),
            "confidence_score": self._calculate_context_confidence(tier1_context, tier2_context, tier3_context),
            "recommendations": self._generate_context_recommendations(tier1_context, tier2_context, tier3_context)
        }
        
        return intelligent_context
        
    async def _predictive_context_loading(self, user_request: str, session_id: str):
        """Predictively load context based on request analysis"""
        
        # Analyze request for likely context needs
        predicted_contexts = self._analyze_request_for_context(user_request)
        
        # Preload high-confidence predictions
        for context_type, confidence in predicted_contexts.items():
            if confidence > 0.7:
                await self._preload_context_type(context_type, session_id)
                
    async def _get_tier1_context(self, query: str) -> Optional[Dict[str, Any]]:
        """Get relevant Tier 1 context"""
        try:
            return self.tier1.search_conversations(query, limit=3)
        except Exception as e:
            self.logger.error(f"Tier 1 context error: {e}")
            return None
            
    async def _get_tier2_context(self, query: str) -> Optional[Dict[str, Any]]:
        """Get relevant Tier 2 context"""
        try:
            return self.tier2.search_patterns(query, min_confidence=0.6)
        except Exception as e:
            self.logger.error(f"Tier 2 context error: {e}")
            return None
            
    async def _get_tier3_context(self, query: str) -> Optional[Dict[str, Any]]:
        """Get relevant Tier 3 context"""
        try:
            return self.tier3.analyze_relevant_context(query)
        except Exception as e:
            self.logger.error(f"Tier 3 context error: {e}")
            return None
            
    def _analyze_request_for_context(self, request: str) -> Dict[str, float]:
        """Analyze request to predict context needs"""
        
        predictions = {}
        request_lower = request.lower()
        
        # File context predictions
        if any(word in request_lower for word in ["file", "class", "method", "function"]):
            predictions["file_context"] = 0.8
            
        # Pattern context predictions
        if any(word in request_lower for word in ["similar", "pattern", "before", "previously"]):
            predictions["pattern_context"] = 0.9
            
        # Workflow context predictions
        if any(word in request_lower for word in ["continue", "next", "then", "after"]):
            predictions["workflow_context"] = 0.7
            
        return predictions
        
    async def _preload_context_type(self, context_type: str, session_id: str):
        """Preload a specific type of context"""
        # Placeholder implementation - would preload specific context types
        pass
        
    def _get_predicted_context_needs(self, query: str) -> List[str]:
        """Get predicted future context needs"""
        # Placeholder implementation
        return ["related_files", "similar_patterns", "workflow_continuation"]
        
    def _calculate_context_confidence(self, tier1: Any, tier2: Any, tier3: Any) -> float:
        """Calculate overall confidence in assembled context"""
        
        confidence_factors = []
        
        # Tier 1 confidence
        if tier1:
            confidence_factors.append(0.8)  # Recent conversations are reliable
        else:
            confidence_factors.append(0.3)
            
        # Tier 2 confidence
        if tier2 and tier2.get("confidence", 0) > 0.7:
            confidence_factors.append(tier2["confidence"])
        else:
            confidence_factors.append(0.4)
            
        # Tier 3 confidence
        if tier3:
            confidence_factors.append(0.7)  # Context analysis is moderately reliable
        else:
            confidence_factors.append(0.3)
            
        return sum(confidence_factors) / len(confidence_factors)
        
    def _generate_context_recommendations(self, tier1: Any, tier2: Any, tier3: Any) -> List[str]:
        """Generate recommendations for improving context"""
        
        recommendations = []
        
        if not tier1:
            recommendations.append("Consider starting conversation tracking for better context continuity")
            
        if not tier2 or (tier2 and tier2.get("confidence", 0) < 0.6):
            recommendations.append("More specific patterns could be learned with additional examples")
            
        if not tier3:
            recommendations.append("Project analysis could provide better development context")
            
        return recommendations