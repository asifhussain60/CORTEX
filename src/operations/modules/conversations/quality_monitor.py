"""
CORTEX 3.0 - Real-Time Conversation Quality Monitor

Purpose: Monitor conversation quality in real-time to detect valuable conversations
         worthy of capture. Integrates with Smart Hint system to prompt users.

Architecture:
- Tracks conversation turns in real-time
- Analyzes quality using ConversationQualityAnalyzer
- Detects valuable conversations (≥7/10 quality score)
- Triggers Smart Hint generation when threshold met
- Learns from user acceptance/rejection patterns

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
"""

import logging
from typing import List, Tuple, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from src.tier1.conversation_quality import (
    ConversationQualityAnalyzer,
    QualityScore
)


logger = logging.getLogger(__name__)


@dataclass
class ConversationTurn:
    """A single conversation turn (user + assistant)."""
    user_message: str
    assistant_response: str
    timestamp: datetime
    turn_number: int


@dataclass
class MonitoringSession:
    """Active conversation monitoring session."""
    session_id: str
    turns: List[ConversationTurn]
    started_at: datetime
    last_quality_check: Optional[QualityScore] = None
    hint_shown: bool = False
    user_response: Optional[str] = None  # 'accepted', 'rejected', 'ignored'


class QualityMonitor:
    """
    Real-time conversation quality monitor.
    
    Detects valuable conversations and triggers Smart Hint prompts.
    
    Quality Thresholds:
    - EXCELLENT (≥19 points): Exceptional strategic value
    - GOOD (≥10 points): Solid strategic conversation
    - FAIR (≥2 points): Some value
    - LOW (<2 points): Minimal strategic content
    
    Default hint threshold: GOOD (≥10 points, maps to ~7/10 in roadmap docs)
    """
    
    def __init__(
        self,
        quality_analyzer: Optional[ConversationQualityAnalyzer] = None,
        min_turns_before_check: int = 5,
        quality_threshold: str = "GOOD"
    ):
        """
        Initialize quality monitor.
        
        Args:
            quality_analyzer: Optional custom analyzer instance
            min_turns_before_check: Minimum turns before checking quality
            quality_threshold: Minimum quality level to trigger hints (GOOD or EXCELLENT)
        """
        self.analyzer = quality_analyzer or ConversationQualityAnalyzer(
            show_hint_threshold=quality_threshold
        )
        self.min_turns_before_check = min_turns_before_check
        self.quality_threshold = quality_threshold
        
        # Active session tracking
        self.current_session: Optional[MonitoringSession] = None
        self.session_history: List[MonitoringSession] = []
        
        logger.info(
            f"QualityMonitor initialized: min_turns={min_turns_before_check}, "
            f"threshold={quality_threshold}"
        )
    
    def start_session(self, session_id: Optional[str] = None) -> str:
        """
        Start a new monitoring session.
        
        Args:
            session_id: Optional custom session ID
            
        Returns:
            Session ID
        """
        if not session_id:
            session_id = datetime.now().strftime("%Y%m%d-%H%M%S")
        
        self.current_session = MonitoringSession(
            session_id=session_id,
            turns=[],
            started_at=datetime.now()
        )
        
        logger.info(f"Started monitoring session: {session_id}")
        return session_id
    
    def add_turn(
        self,
        user_message: str,
        assistant_response: str
    ) -> Dict[str, Any]:
        """
        Add a conversation turn and check quality.
        
        Args:
            user_message: User's input
            assistant_response: CORTEX's response
            
        Returns:
            Dict with quality analysis and hint recommendation
        """
        if not self.current_session:
            self.start_session()
        
        turn_number = len(self.current_session.turns) + 1
        
        turn = ConversationTurn(
            user_message=user_message,
            assistant_response=assistant_response,
            timestamp=datetime.now(),
            turn_number=turn_number
        )
        
        self.current_session.turns.append(turn)
        
        logger.debug(f"Added turn {turn_number} to session {self.current_session.session_id}")
        
        # Check quality if enough turns have accumulated
        should_check = turn_number >= self.min_turns_before_check
        
        if should_check:
            return self._check_quality()
        
        return {
            'should_check_quality': False,
            'turn_count': turn_number,
            'session_id': self.current_session.session_id
        }
    
    def _check_quality(self) -> Dict[str, Any]:
        """
        Analyze current conversation quality.
        
        Returns:
            Dict with quality score and hint recommendation
        """
        if not self.current_session or not self.current_session.turns:
            return {
                'should_check_quality': False,
                'error': 'No active session or turns'
            }
        
        # Convert turns to format expected by analyzer
        turns_data = [
            (turn.user_message, turn.assistant_response)
            for turn in self.current_session.turns
        ]
        
        # Analyze quality
        quality_score = self.analyzer.analyze_multi_turn_conversation(turns_data)
        
        self.current_session.last_quality_check = quality_score
        
        logger.info(
            f"Quality check: {quality_score.level} "
            f"({quality_score.total_score} points) - "
            f"{quality_score.reasoning}"
        )
        
        # Determine if hint should be shown
        should_show_hint = (
            quality_score.should_show_hint and 
            not self.current_session.hint_shown
        )
        
        return {
            'should_check_quality': True,
            'quality_score': quality_score.total_score,
            'quality_level': quality_score.level,
            'reasoning': quality_score.reasoning,
            'should_show_hint': should_show_hint,
            'turn_count': len(self.current_session.turns),
            'session_id': self.current_session.session_id,
            'elements': {
                'multi_phase_planning': quality_score.elements.multi_phase_planning,
                'phase_count': quality_score.elements.phase_count,
                'challenge_accept_flow': quality_score.elements.challenge_accept_flow,
                'design_decisions': quality_score.elements.design_decisions,
                'file_references': quality_score.elements.file_references,
                'code_implementation': quality_score.elements.code_implementation,
                'architectural_discussion': quality_score.elements.architectural_discussion
            }
        }
    
    def record_user_response(self, response: str) -> None:
        """
        Record user's response to Smart Hint.
        
        Args:
            response: 'accepted', 'rejected', or 'ignored'
        """
        if not self.current_session:
            logger.warning("No active session to record user response")
            return
        
        self.current_session.user_response = response
        self.current_session.hint_shown = True
        
        logger.info(
            f"User response recorded: {response} "
            f"(session {self.current_session.session_id})"
        )
    
    def end_session(self) -> Optional[MonitoringSession]:
        """
        End current monitoring session.
        
        Returns:
            Completed session or None if no active session
        """
        if not self.current_session:
            return None
        
        session = self.current_session
        self.session_history.append(session)
        
        logger.info(
            f"Ended session {session.session_id}: "
            f"{len(session.turns)} turns, "
            f"quality={session.last_quality_check.level if session.last_quality_check else 'N/A'}"
        )
        
        self.current_session = None
        return session
    
    def get_current_quality(self) -> Optional[QualityScore]:
        """
        Get current session's quality score.
        
        Returns:
            Latest quality score or None if no session
        """
        if not self.current_session:
            return None
        
        return self.current_session.last_quality_check
    
    def get_session_stats(self) -> Dict[str, Any]:
        """
        Get statistics about monitoring sessions.
        
        Returns:
            Dict with session statistics
        """
        total_sessions = len(self.session_history)
        
        if total_sessions == 0:
            return {
                'total_sessions': 0,
                'hints_shown': 0,
                'acceptance_rate': 0.0,
                'average_turns': 0.0
            }
        
        hints_shown = sum(1 for s in self.session_history if s.hint_shown)
        accepted = sum(
            1 for s in self.session_history 
            if s.user_response == 'accepted'
        )
        
        total_turns = sum(len(s.turns) for s in self.session_history)
        avg_turns = total_turns / total_sessions
        
        acceptance_rate = (accepted / hints_shown * 100) if hints_shown > 0 else 0.0
        
        return {
            'total_sessions': total_sessions,
            'hints_shown': hints_shown,
            'acceptance_rate': acceptance_rate,
            'accepted_count': accepted,
            'average_turns': avg_turns,
            'total_turns': total_turns
        }


def create_monitor(config: Optional[Dict[str, Any]] = None) -> QualityMonitor:
    """
    Factory function to create quality monitor.
    
    Args:
        config: Optional configuration dict
            - min_turns_before_check: int (default: 5)
            - quality_threshold: str (default: "GOOD")
            
    Returns:
        Configured QualityMonitor instance
    """
    if not config:
        config = {}
    
    min_turns = config.get('min_turns_before_check', 5)
    threshold = config.get('quality_threshold', 'GOOD')
    
    return QualityMonitor(
        min_turns_before_check=min_turns,
        quality_threshold=threshold
    )
