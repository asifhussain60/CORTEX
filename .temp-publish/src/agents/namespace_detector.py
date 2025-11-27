"""
CORTEX 3.0 - Namespace Detection Engine
======================================

Intelligent detection of conversation context to route questions correctly:
- cortex.* namespace: Questions about CORTEX framework itself
- workspace.* namespace: Questions about user's application code
- Eliminates confusion: "how is the code?" → proper routing

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

Feature: Quick Win #2 (Week 1)
Effort: 8 hours (namespace detection engine)
Target: ≥90% routing accuracy, <100ms response time
"""

from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import re
import logging
from collections import defaultdict


class NamespaceType(Enum):
    """Detected namespace types"""
    CORTEX_FRAMEWORK = "cortex"      # Questions about CORTEX itself
    WORKSPACE_CODE = "workspace"     # Questions about user's code
    AMBIGUOUS = "ambiguous"          # Unclear context, need clarification
    GENERAL = "general"              # General programming questions


@dataclass
class ContextCue:
    """A single context detection cue"""
    pattern: str
    namespace: NamespaceType
    weight: float = 1.0
    requires_confirmation: bool = False
    

@dataclass 
class NamespaceDetectionResult:
    """Result of namespace detection analysis"""
    primary_namespace: NamespaceType
    confidence: float
    contributing_factors: List[str]
    alternative_namespace: Optional[NamespaceType] = None
    requires_clarification: bool = False
    suggested_clarification: Optional[str] = None


class NamespaceDetector:
    """
    Intelligent namespace detection for question routing.
    
    Analyzes user questions to determine if they're asking about:
    - CORTEX framework (brain health, agent performance, etc.)
    - User's workspace code (their application, bugs, features)
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._initialize_detection_patterns()
        
    def _initialize_detection_patterns(self):
        """Initialize regex patterns and keywords for namespace detection"""
        
        # CORTEX framework indicators
        self.cortex_patterns = [
            # Direct CORTEX references
            ContextCue(r"\bcortex\b", NamespaceType.CORTEX_FRAMEWORK, weight=2.0),
            ContextCue(r"\bbrain\b", NamespaceType.CORTEX_FRAMEWORK, weight=1.5),
            ContextCue(r"\btier[123]\b", NamespaceType.CORTEX_FRAMEWORK, weight=2.0),
            ContextCue(r"\bagent[s]?\b", NamespaceType.CORTEX_FRAMEWORK, weight=1.2),
            ContextCue(r"\bmemory system\b", NamespaceType.CORTEX_FRAMEWORK, weight=1.5),
            
            # CORTEX operations
            ContextCue(r"\bresponse template", NamespaceType.CORTEX_FRAMEWORK, weight=1.8),
            ContextCue(r"\bknowledge graph", NamespaceType.CORTEX_FRAMEWORK, weight=1.8),
            ContextCue(r"\bconversation tracking", NamespaceType.CORTEX_FRAMEWORK, weight=1.5),
            ContextCue(r"\btoken optimization", NamespaceType.CORTEX_FRAMEWORK, weight=1.5),
            
            # CORTEX health questions  
            ContextCue(r"\bhow is cortex", NamespaceType.CORTEX_FRAMEWORK, weight=2.5),
            ContextCue(r"\bcortex status", NamespaceType.CORTEX_FRAMEWORK, weight=2.0),
            ContextCue(r"\bbrain health", NamespaceType.CORTEX_FRAMEWORK, weight=2.0),
            ContextCue(r"\bmemory status", NamespaceType.CORTEX_FRAMEWORK, weight=1.8),
            
            # File path indicators
            ContextCue(r"\bcortex-brain/", NamespaceType.CORTEX_FRAMEWORK, weight=2.0),
            ContextCue(r"\bsrc/tier", NamespaceType.CORTEX_FRAMEWORK, weight=2.0),
            ContextCue(r"\bprompts/", NamespaceType.CORTEX_FRAMEWORK, weight=1.5),
        ]
        
        # Workspace/application code indicators
        self.workspace_patterns = [
            # User's application references
            ContextCue(r"\bmy code\b", NamespaceType.WORKSPACE_CODE, weight=2.0),
            ContextCue(r"\bmy application\b", NamespaceType.WORKSPACE_CODE, weight=2.0),
            ContextCue(r"\bmy project\b", NamespaceType.WORKSPACE_CODE, weight=1.8),
            ContextCue(r"\bour code\b", NamespaceType.WORKSPACE_CODE, weight=1.8),
            ContextCue(r"\bthe project\b", NamespaceType.WORKSPACE_CODE, weight=1.5),
            ContextCue(r"\bthe application\b", NamespaceType.WORKSPACE_CODE, weight=1.5),
            ContextCue(r"\bthe codebase\b", NamespaceType.WORKSPACE_CODE, weight=1.5),
            
            # Testing and quality indicators (clearly about user's workspace)
            ContextCue(r"\btest coverage\b", NamespaceType.WORKSPACE_CODE, weight=2.0),
            ContextCue(r"\bcode coverage\b", NamespaceType.WORKSPACE_CODE, weight=2.0),
            ContextCue(r"\bunit test", NamespaceType.WORKSPACE_CODE, weight=1.8),
            ContextCue(r"\bintegration test", NamespaceType.WORKSPACE_CODE, weight=1.8),
            ContextCue(r"\bcode quality\b", NamespaceType.WORKSPACE_CODE, weight=2.0),
            ContextCue(r"\bcode smell", NamespaceType.WORKSPACE_CODE, weight=1.8),
            ContextCue(r"\bbuild error", NamespaceType.WORKSPACE_CODE, weight=1.8),
            ContextCue(r"\bbuild status\b", NamespaceType.WORKSPACE_CODE, weight=1.8),
            ContextCue(r"\bcompilation error", NamespaceType.WORKSPACE_CODE, weight=1.8),
            ContextCue(r"\bproject health\b", NamespaceType.WORKSPACE_CODE, weight=1.8),
            
            # Authentication/business logic (common user features)
            ContextCue(r"\bauthentication\b", NamespaceType.WORKSPACE_CODE, weight=1.5),
            ContextCue(r"\blogin\b", NamespaceType.WORKSPACE_CODE, weight=1.2),
            ContextCue(r"\bdatabase\b", NamespaceType.WORKSPACE_CODE, weight=1.0),
            ContextCue(r"\bapi endpoint", NamespaceType.WORKSPACE_CODE, weight=1.5),
            ContextCue(r"\bbusiness logic", NamespaceType.WORKSPACE_CODE, weight=1.5),
            
            # Bug/issue indicators (usually about user's code)
            ContextCue(r"\bbug in\b", NamespaceType.WORKSPACE_CODE, weight=1.8),
            ContextCue(r"\berror in\b", NamespaceType.WORKSPACE_CODE, weight=1.5),
            ContextCue(r"\bnot working\b", NamespaceType.WORKSPACE_CODE, weight=1.3),
            ContextCue(r"\bfailing test", NamespaceType.WORKSPACE_CODE, weight=1.5),
            
            # Implementation questions
            ContextCue(r"\bhow do I implement", NamespaceType.WORKSPACE_CODE, weight=1.8),
            ContextCue(r"\bcan you help me add", NamespaceType.WORKSPACE_CODE, weight=1.5),
            ContextCue(r"\bI need to create", NamespaceType.WORKSPACE_CODE, weight=1.5),
        ]
        
        # Ambiguous patterns (need clarification)
        self.ambiguous_patterns = [
            # These could go either way
            ContextCue(r"^how is the code\?$", NamespaceType.AMBIGUOUS, weight=2.0,
                      requires_confirmation=True),
            ContextCue(r"^status\s*\??$", NamespaceType.AMBIGUOUS, weight=1.5,
                      requires_confirmation=True),
            ContextCue(r"^health\s*\??$", NamespaceType.AMBIGUOUS, weight=1.5,
                      requires_confirmation=True),
            ContextCue(r"\bhow is everything\b", NamespaceType.AMBIGUOUS, weight=2.0,
                      requires_confirmation=True),
            ContextCue(r"\bhow are things\b", NamespaceType.AMBIGUOUS, weight=1.8,
                      requires_confirmation=True),
            ContextCue(r"^what's the status\b", NamespaceType.AMBIGUOUS, weight=1.8,
                      requires_confirmation=True),
            ContextCue(r"\bthe system\b", NamespaceType.AMBIGUOUS, weight=1.0),
            ContextCue(r"\boverall\b", NamespaceType.AMBIGUOUS, weight=1.2),
        ]
        
    def detect_namespace(self, user_message: str, 
                        conversation_history: Optional[List[str]] = None,
                        current_files: Optional[List[str]] = None) -> NamespaceDetectionResult:
        """
        Detect the namespace of a user question.
        
        Args:
            user_message: The user's question/message
            conversation_history: Recent conversation for context
            current_files: Files currently open/discussed
            
        Returns:
            NamespaceDetectionResult with detected namespace and confidence
        """
        self.logger.debug(f"Analyzing message: {user_message[:100]}...")
        
        # Normalize message for analysis
        message_lower = user_message.lower()
        
        # Score each namespace
        scores = defaultdict(list)  # namespace -> list of (weight, factor)
        
        # Check against all pattern sets
        self._score_patterns(message_lower, self.cortex_patterns, scores)
        self._score_patterns(message_lower, self.workspace_patterns, scores) 
        self._score_patterns(message_lower, self.ambiguous_patterns, scores)
        
        # Add contextual scoring
        self._add_contextual_scores(user_message, conversation_history, 
                                  current_files, scores)
        
        # Calculate final scores
        final_scores = {}
        contributing_factors = []
        
        for namespace, score_list in scores.items():
            total_score = sum(weight for weight, factor in score_list)
            final_scores[namespace] = total_score
            contributing_factors.extend(factor for weight, factor in score_list)
        
        # Determine primary namespace
        if not final_scores:
            # No specific indicators found - default to general
            return NamespaceDetectionResult(
                primary_namespace=NamespaceType.GENERAL,
                confidence=0.5,
                contributing_factors=["No specific namespace indicators found"]
            )
        
        # Get top scoring namespace
        primary_namespace = max(final_scores.keys(), key=final_scores.get)
        primary_score = final_scores[primary_namespace]
        
        # Get second highest for comparison
        remaining_scores = {k: v for k, v in final_scores.items() 
                          if k != primary_namespace}
        second_score = max(remaining_scores.values()) if remaining_scores else 0
        
        # Calculate confidence based on score difference
        confidence = self._calculate_confidence(primary_score, second_score)
        
        # Check if clarification needed
        needs_clarification = (
            primary_namespace == NamespaceType.AMBIGUOUS or
            confidence < 0.7 or
            self._has_conflicting_signals(final_scores)
        )
        
        # Generate clarification suggestion if needed
        clarification = None
        if needs_clarification:
            clarification = self._generate_clarification_question(
                user_message, final_scores
            )
        
        return NamespaceDetectionResult(
            primary_namespace=primary_namespace,
            confidence=confidence,
            contributing_factors=contributing_factors[:5],  # Top 5 factors
            alternative_namespace=max(remaining_scores.keys()) if remaining_scores else None,
            requires_clarification=needs_clarification,
            suggested_clarification=clarification
        )
        
    def _score_patterns(self, message: str, patterns: List[ContextCue], 
                       scores: Dict[NamespaceType, List[Tuple[float, str]]]):
        """Score message against a set of patterns"""
        for cue in patterns:
            if re.search(cue.pattern, message, re.IGNORECASE):
                scores[cue.namespace].append((
                    cue.weight, 
                    f"Pattern match: {cue.pattern}"
                ))
                
    def _add_contextual_scores(self, message: str,
                             conversation_history: Optional[List[str]],
                             current_files: Optional[List[str]],
                             scores: Dict[NamespaceType, List[Tuple[float, str]]]):
        """Add contextual scoring based on conversation and file context"""
        
        # File context scoring
        if current_files:
            cortex_files = [f for f in current_files 
                          if 'cortex' in f.lower() or 'brain' in f.lower()]
            workspace_files = [f for f in current_files 
                             if f.endswith(('.cs', '.py', '.js', '.tsx', '.vue'))]
            
            if cortex_files:
                scores[NamespaceType.CORTEX_FRAMEWORK].append((
                    1.0, f"CORTEX files in context: {len(cortex_files)}"
                ))
            
            if workspace_files and not cortex_files:
                scores[NamespaceType.WORKSPACE_CODE].append((
                    1.5, f"Workspace files in context: {len(workspace_files)}"
                ))
        
        # Conversation context scoring
        if conversation_history:
            recent_messages = conversation_history[-3:]  # Last 3 messages
            cortex_mentions = sum(1 for msg in recent_messages 
                                if 'cortex' in msg.lower() or 'brain' in msg.lower())
            
            if cortex_mentions > 0:
                scores[NamespaceType.CORTEX_FRAMEWORK].append((
                    1.2, f"Recent CORTEX discussion ({cortex_mentions} mentions)"
                ))
                
    def _calculate_confidence(self, primary_score: float, second_score: float) -> float:
        """Calculate confidence based on score difference"""
        if second_score == 0:
            return min(0.9, 0.5 + (primary_score / 10))
        
        score_ratio = primary_score / (primary_score + second_score)
        
        if score_ratio > 0.8:
            return 0.95
        elif score_ratio > 0.7:
            return 0.85
        elif score_ratio > 0.6:
            return 0.75
        else:
            return 0.60
            
    def _has_conflicting_signals(self, final_scores: Dict[NamespaceType, float]) -> bool:
        """Check if there are strong conflicting signals"""
        if len(final_scores) < 2:
            return False
            
        scores = list(final_scores.values())
        scores.sort(reverse=True)
        
        # If top two scores are very close, there's conflict
        return len(scores) >= 2 and scores[1] / scores[0] > 0.8
        
    def _generate_clarification_question(self, message: str, 
                                       scores: Dict[NamespaceType, float]) -> str:
        """Generate appropriate clarification question"""
        
        if "how is the code" in message.lower():
            return ("I can check either:\n"
                   "- **CORTEX framework health** (brain performance, agent status)\n"
                   "- **Your workspace code quality** (build status, test coverage, issues)\n\n"
                   "Which would you like me to analyze?")
        
        if "status" in message.lower():
            return ("I can provide status for:\n"
                   "- **CORTEX system status** (memory tiers, agents, operations)\n"  
                   "- **Your project status** (build health, implementation progress)\n\n"
                   "Which status report would you like?")
        
        # Generic clarification
        cortex_score = scores.get(NamespaceType.CORTEX_FRAMEWORK, 0)
        workspace_score = scores.get(NamespaceType.WORKSPACE_CODE, 0)
        
        if cortex_score > 0 and workspace_score > 0:
            return ("Your question could relate to either:\n"
                   "- **CORTEX framework** (system internals, brain health)\n"
                   "- **Your workspace code** (application logic, implementation)\n\n"
                   "Could you clarify which context you're asking about?")
        
        return "Could you provide a bit more context about what you're asking?"

    def detect(self, user_message: str, context: Dict = None) -> 'NamespaceResult':
        """
        Compatibility method for test suite.
        Maps to detect_namespace with simplified result format.
        """
        # Extract context parameters if provided
        conversation_history = context.get('conversation_history') if context else None
        current_files = context.get('current_files') if context else None
        
        # Get full detection result
        full_result = self.detect_namespace(user_message, conversation_history, current_files)
        
        # Convert to expected format for tests
        return NamespaceResult(
            namespace=full_result.primary_namespace.value,
            confidence=full_result.confidence,
            indicators=full_result.contributing_factors,
            reasoning=f"Primary: {full_result.primary_namespace.value}, "
                     f"Confidence: {full_result.confidence:.2f}, "
                     f"Factors: {len(full_result.contributing_factors)}"
        )


@dataclass
class NamespaceResult:
    """Simplified result format for compatibility with test suite"""
    namespace: str
    confidence: float
    indicators: List[str]
    reasoning: str


# Export for use in question routing
__all__ = ['NamespaceDetector', 'NamespaceType', 'NamespaceDetectionResult', 'NamespaceResult']