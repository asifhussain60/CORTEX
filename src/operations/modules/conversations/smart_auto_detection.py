"""
CORTEX 3.0 - Feature 5.3: Smart Auto-Detection Integration

Purpose: Integrates Quality Monitor and Smart Hint Generator with response 
         template system for real-time conversation quality detection.

Architecture:
- Monitors conversation quality in real-time 
- Detects valuable conversations (≥7/10 quality score)
- Automatically generates Smart Hints in response templates
- Integrates with Tier 2 for learning user preferences

Week 4 Deliverable:
- Real-time quality monitoring
- Smart hint insertion in responses
- User feedback learning loop

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
"""

import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

from src.operations.modules.conversations.quality_monitor import QualityMonitor
from src.operations.modules.conversations.smart_hint_generator import SmartHintGenerator
from src.tier1.conversation_quality import ConversationQualityAnalyzer


logger = logging.getLogger(__name__)


class SmartAutoDetection:
    """
    Feature 5.3: Smart Auto-Detection System
    
    Automatically detects valuable conversations and prompts users
    with Smart Hints for conversation capture.
    
    Quality Thresholds (mapped to /10 scale for users):
    - EXCELLENT (≥19 internal): 9-10/10 → "exceptional strategic value"
    - GOOD (≥10 internal): 7-8/10 → "solid strategic conversation" 
    - FAIR (≥2 internal): 4-6/10 → "some value"
    - LOW (<2 internal): 1-3/10 → "minimal strategic content"
    
    Default hint threshold: GOOD (≥7/10 user scale, ≥10 internal)
    """
    
    def __init__(
        self,
        quality_threshold: str = "GOOD",
        min_turns_before_check: int = 5,
        enable_learning: bool = True
    ):
        """
        Initialize Smart Auto-Detection system.
        
        Args:
            quality_threshold: Quality level to trigger hints (GOOD or EXCELLENT)
            min_turns_before_check: Minimum conversation turns before checking
            enable_learning: Enable learning from user feedback
        """
        self.quality_threshold = quality_threshold
        self.enable_learning = enable_learning
        
        # Initialize components
        self.quality_monitor = QualityMonitor(
            min_turns_before_check=min_turns_before_check,
            quality_threshold=quality_threshold
        )
        
        self.hint_generator = SmartHintGenerator(
            quality_threshold=quality_threshold,
            enable_hints=True
        )
        
        # Statistics tracking
        self.stats = {
            'conversations_monitored': 0,
            'hints_generated': 0,
            'user_accepted': 0,
            'user_rejected': 0,
            'user_ignored': 0,
            'false_positives': 0
        }
        
        logger.info(
            f"SmartAutoDetection initialized: threshold={quality_threshold}, "
            f"min_turns={min_turns_before_check}, learning={enable_learning}"
        )
    
    def start_conversation_monitoring(self, session_id: Optional[str] = None) -> str:
        """
        Start monitoring a new conversation session.
        
        Args:
            session_id: Optional session ID (auto-generated if not provided)
            
        Returns:
            Session ID for tracking
        """
        session_id = self.quality_monitor.start_session(session_id)
        self.stats['conversations_monitored'] += 1
        
        logger.info(f"Started monitoring conversation: {session_id}")
        return session_id
    
    def process_conversation_turn(
        self,
        user_message: str,
        assistant_response: str
    ) -> Dict[str, Any]:
        """
        Process a conversation turn and check for Smart Hint opportunity.
        
        Args:
            user_message: User's input message
            assistant_response: CORTEX's response
            
        Returns:
            Dict containing:
            - should_show_hint: bool
            - hint_content: str (if applicable) 
            - quality_info: dict with score details
            - session_info: dict with session details
        """
        # Add turn to quality monitor
        monitor_result = self.quality_monitor.add_turn(
            user_message=user_message,
            assistant_response=assistant_response
        )
        
        result = {
            'should_show_hint': False,
            'hint_content': '',
            'quality_info': {},
            'session_info': {
                'session_id': monitor_result.get('session_id', ''),
                'turn_count': monitor_result.get('turn_count', 0)
            }
        }
        
        # Check if quality analysis was performed
        if not monitor_result.get('should_check_quality', False):
            logger.debug(
                f"Quality check skipped: turn {monitor_result.get('turn_count', 0)}"
            )
            return result
        
        # Get quality score from monitor
        quality_score = self.quality_monitor.get_current_quality()
        if not quality_score:
            logger.warning("Quality score not available after check")
            return result
        
        # Generate hint if quality meets threshold
        hint = self.hint_generator.generate_hint(
            quality_score=quality_score,
            hint_already_shown=monitor_result.get('hint_shown', False)
        )
        
        if hint.should_display:
            self.stats['hints_generated'] += 1
            
            logger.info(
                f"Smart Hint generated: {hint.quality_level} "
                f"({hint.quality_score} internal points)"
            )
        
        result.update({
            'should_show_hint': hint.should_display,
            'hint_content': hint.content,
            'quality_info': {
                'score': hint.quality_score,
                'level': hint.quality_level,
                'reasoning': hint.reasoning,
                'user_display_score': self._map_to_user_scale(hint.quality_score)
            }
        })
        
        return result
    
    def record_user_feedback(
        self,
        feedback: str,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Record user's response to Smart Hint.
        
        Args:
            feedback: User response ('accepted', 'rejected', 'ignored', 'skip')
            session_id: Session ID (optional if current session active)
            
        Returns:
            Dict with confirmation and updated statistics
        """
        # Normalize feedback
        normalized_feedback = self._normalize_feedback(feedback)
        
        # Record in quality monitor
        self.quality_monitor.record_user_response(normalized_feedback)
        
        # Update statistics
        self.stats[f'user_{normalized_feedback}'] += 1
        
        # Learn from feedback if enabled
        if self.enable_learning:
            self._learn_from_feedback(normalized_feedback)
        
        logger.info(f"User feedback recorded: {normalized_feedback}")
        
        return {
            'feedback_recorded': normalized_feedback,
            'session_id': session_id or self.quality_monitor.current_session.session_id,
            'stats': self.get_statistics(),
            'confirmation_message': self._get_feedback_confirmation(normalized_feedback)
        }
    
    def end_conversation_monitoring(self) -> Optional[Dict[str, Any]]:
        """
        End current conversation monitoring session.
        
        Returns:
            Session summary or None if no active session
        """
        session = self.quality_monitor.end_session()
        
        if not session:
            return None
        
        summary = {
            'session_id': session.session_id,
            'duration': (datetime.now() - session.started_at).total_seconds(),
            'turn_count': len(session.turns),
            'hint_shown': session.hint_shown,
            'user_response': session.user_response,
            'final_quality': {
                'score': session.last_quality_check.total_score if session.last_quality_check else None,
                'level': session.last_quality_check.level if session.last_quality_check else None
            }
        }
        
        logger.info(
            f"Ended conversation monitoring: {session.session_id} "
            f"({len(session.turns)} turns, quality={summary['final_quality']['level']})"
        )
        
        return summary
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get system performance statistics.
        
        Returns:
            Dict with detection and user interaction statistics
        """
        total_feedback = (
            self.stats['user_accepted'] + 
            self.stats['user_rejected'] + 
            self.stats['user_ignored']
        )
        
        acceptance_rate = (
            (self.stats['user_accepted'] / total_feedback * 100) 
            if total_feedback > 0 else 0.0
        )
        
        hint_rate = (
            (self.stats['hints_generated'] / self.stats['conversations_monitored'] * 100)
            if self.stats['conversations_monitored'] > 0 else 0.0
        )
        
        return {
            'conversations_monitored': self.stats['conversations_monitored'],
            'hints_generated': self.stats['hints_generated'],
            'hint_generation_rate': round(hint_rate, 1),
            'user_feedback': {
                'accepted': self.stats['user_accepted'],
                'rejected': self.stats['user_rejected'],
                'ignored': self.stats['user_ignored'],
                'total_responses': total_feedback,
                'acceptance_rate': round(acceptance_rate, 1)
            },
            'quality_thresholds': {
                'current_threshold': self.quality_threshold,
                'false_positives': self.stats['false_positives']
            }
        }
    
    def _map_to_user_scale(self, internal_score: int) -> int:
        """
        Map internal quality score to user-friendly /10 scale.
        
        Args:
            internal_score: Internal scoring system (0-30+)
            
        Returns:
            Score on /10 scale
        """
        if internal_score >= 19:
            return min(10, 9 + (internal_score - 19) // 6)
        elif internal_score >= 10:
            return 8 if internal_score >= 14 else 7
        elif internal_score >= 2:
            return min(6, 4 + (internal_score - 2) // 3)
        else:
            return max(1, internal_score + 1)
    
    def _normalize_feedback(self, feedback: str) -> str:
        """
        Normalize user feedback to standard values.
        
        Args:
            feedback: Raw user input
            
        Returns:
            Normalized feedback ('accepted', 'rejected', 'ignored')
        """
        feedback_lower = feedback.lower().strip()
        
        accept_terms = ['yes', 'accept', 'accepted', 'ok', 'okay', 'capture', 'save']
        reject_terms = ['no', 'reject', 'rejected', 'skip', 'dismiss', 'not now']
        
        if any(term in feedback_lower for term in accept_terms):
            return 'accepted'
        elif any(term in feedback_lower for term in reject_terms):
            return 'rejected'
        else:
            return 'ignored'
    
    def _learn_from_feedback(self, feedback: str) -> None:
        """
        Learn from user feedback to improve future detection.
        
        Args:
            feedback: Normalized feedback ('accepted', 'rejected', 'ignored')
        """
        current_quality = self.quality_monitor.get_current_quality()
        
        if not current_quality:
            return
        
        # TODO: Integrate with Tier 2 learning system
        # This would store patterns about what quality elements users value
        # and adjust scoring weights accordingly
        
        if feedback == 'rejected' and current_quality.total_score >= 10:
            # User rejected a GOOD quality conversation
            # Could indicate this type of conversation is not valuable to them
            self.stats['false_positives'] += 1
        
        logger.debug(
            f"Learning from feedback: {feedback} for "
            f"{current_quality.level} conversation ({current_quality.total_score} points)"
        )
    
    def _get_feedback_confirmation(self, feedback: str) -> str:
        """
        Get confirmation message for user feedback.
        
        Args:
            feedback: Normalized feedback
            
        Returns:
            Confirmation message
        """
        messages = {
            'accepted': "Great! Use '/CORTEX Capture this conversation' to save it.",
            'rejected': "Noted. I'll adjust my detection patterns based on your feedback.",
            'ignored': "No worries. I'll continue monitoring for valuable conversations."
        }
        
        return messages.get(feedback, "Feedback received.")


def create_smart_auto_detection(config: Optional[Dict[str, Any]] = None) -> SmartAutoDetection:
    """
    Factory function to create Smart Auto-Detection system.
    
    Args:
        config: Optional configuration dict
            - quality_threshold: str (default: "GOOD")
            - min_turns_before_check: int (default: 5)
            - enable_learning: bool (default: True)
            
    Returns:
        Configured SmartAutoDetection instance
    """
    if not config:
        config = {}
    
    threshold = config.get('quality_threshold', 'GOOD')
    min_turns = config.get('min_turns_before_check', 5)
    learning = config.get('enable_learning', True)
    
    return SmartAutoDetection(
        quality_threshold=threshold,
        min_turns_before_check=min_turns,
        enable_learning=learning
    )