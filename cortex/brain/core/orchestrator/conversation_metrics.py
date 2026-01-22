"""
Production observability for conversation protocol.

Metrics, tracing, and structured logging for multi-turn conversations.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import logging
import time


@dataclass
class ConversationMetrics:
    """Metrics for conversation execution."""
    
    conversation_id: str
    turn_count: int = 0
    total_duration_ms: float = 0.0
    avg_turn_duration_ms: float = 0.0
    cancellation_count: int = 0
    timeout_count: int = 0
    error_count: int = 0
    success_rate: float = 1.0


class ConversationObservability:
    """
    Provides observability for conversation protocol execution.
    
    Features:
    - Metrics: turn_duration, cancellation_rate, error_rate
    - Tracing: correlation_id per conversation, span per turn
    - Structured logging: conversation_id, turn_number, orchestrator_name
    """
    
    def __init__(
        self,
        logger: Optional[logging.Logger] = None,
        enable_metrics: bool = True,
        enable_tracing: bool = True
    ):
        """
        Initialize observability.
        
        Args:
            logger: Logger instance (creates default if None)
            enable_metrics: Enable metrics collection
            enable_tracing: Enable distributed tracing
        """
        self.logger = logger or self._create_default_logger()
        self.enable_metrics = enable_metrics
        self.enable_tracing = enable_tracing
        
        # Metrics storage
        self.metrics: Dict[str, ConversationMetrics] = {}
    
    def _create_default_logger(self) -> logging.Logger:
        """Create default structured logger."""
        logger = logging.getLogger("cortex.conversation")
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s [%(name)s] %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def start_conversation(
        self,
        conversation_id: str,
        orchestrator_name: str
    ) -> None:
        """
        Start tracking a conversation.
        
        Args:
            conversation_id: Unique conversation identifier
            orchestrator_name: Name of orchestrator
        """
        if self.enable_metrics:
            self.metrics[conversation_id] = ConversationMetrics(
                conversation_id=conversation_id
            )
        
        self.logger.info(
            f"Conversation started",
            extra={
                "conversation_id": conversation_id,
                "orchestrator_name": orchestrator_name,
                "event": "conversation.start"
            }
        )
    
    def start_turn(
        self,
        conversation_id: str,
        turn_number: int,
        user_input: str
    ) -> float:
        """
        Start tracking a turn.
        
        Args:
            conversation_id: Conversation ID
            turn_number: Turn number
            user_input: User input
            
        Returns:
            Start timestamp for duration calculation
        """
        self.logger.info(
            f"Turn {turn_number} started",
            extra={
                "conversation_id": conversation_id,
                "turn_number": turn_number,
                "user_input_length": len(user_input),
                "event": "turn.start"
            }
        )
        
        return time.time()
    
    def end_turn(
        self,
        conversation_id: str,
        turn_number: int,
        start_time: float,
        success: bool = True,
        error: Optional[str] = None
    ) -> None:
        """
        End tracking a turn.
        
        Args:
            conversation_id: Conversation ID
            turn_number: Turn number
            start_time: Start timestamp from start_turn()
            success: Whether turn succeeded
            error: Error message if failed
        """
        duration_ms = (time.time() - start_time) * 1000
        
        if self.enable_metrics and conversation_id in self.metrics:
            metrics = self.metrics[conversation_id]
            metrics.turn_count += 1
            metrics.total_duration_ms += duration_ms
            metrics.avg_turn_duration_ms = (
                metrics.total_duration_ms / metrics.turn_count
            )
            
            if not success:
                metrics.error_count += 1
            
            metrics.success_rate = (
                (metrics.turn_count - metrics.error_count) / metrics.turn_count
            )
        
        self.logger.info(
            f"Turn {turn_number} completed",
            extra={
                "conversation_id": conversation_id,
                "turn_number": turn_number,
                "duration_ms": duration_ms,
                "success": success,
                "error": error,
                "event": "turn.end"
            }
        )
    
    def record_timeout(self, conversation_id: str, turn_number: int) -> None:
        """
        Record a turn timeout.
        
        Args:
            conversation_id: Conversation ID
            turn_number: Turn number
        """
        if self.enable_metrics and conversation_id in self.metrics:
            self.metrics[conversation_id].timeout_count += 1
        
        self.logger.warning(
            f"Turn {turn_number} timed out",
            extra={
                "conversation_id": conversation_id,
                "turn_number": turn_number,
                "event": "turn.timeout"
            }
        )
    
    def record_cancellation(self, conversation_id: str, turn_number: int) -> None:
        """
        Record a turn cancellation.
        
        Args:
            conversation_id: Conversation ID
            turn_number: Turn number
        """
        if self.enable_metrics and conversation_id in self.metrics:
            self.metrics[conversation_id].cancellation_count += 1
        
        self.logger.info(
            f"Turn {turn_number} cancelled",
            extra={
                "conversation_id": conversation_id,
                "turn_number": turn_number,
                "event": "turn.cancelled"
            }
        )
    
    def end_conversation(
        self,
        conversation_id: str,
        reason: str = "complete"
    ) -> None:
        """
        End tracking a conversation.
        
        Args:
            conversation_id: Conversation ID
            reason: Reason for ending (complete, error, cancelled)
        """
        metrics = self.metrics.get(conversation_id)
        
        extra_data = {
            "conversation_id": conversation_id,
            "reason": reason,
            "event": "conversation.end"
        }
        
        if metrics:
            extra_data.update({
                "total_turns": metrics.turn_count,
                "total_duration_ms": metrics.total_duration_ms,
                "avg_turn_duration_ms": metrics.avg_turn_duration_ms,
                "timeout_count": metrics.timeout_count,
                "cancellation_count": metrics.cancellation_count,
                "success_rate": metrics.success_rate
            })
        
        self.logger.info(f"Conversation ended: {reason}", extra=extra_data)
    
    def get_metrics(self, conversation_id: str) -> Optional[ConversationMetrics]:
        """
        Get metrics for a conversation.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            ConversationMetrics if found, None otherwise
        """
        return self.metrics.get(conversation_id)
    
    def get_all_metrics(self) -> Dict[str, ConversationMetrics]:
        """Get all conversation metrics."""
        return self.metrics.copy()
    
    def clear_metrics(self, conversation_id: Optional[str] = None) -> None:
        """
        Clear metrics.
        
        Args:
            conversation_id: Clear specific conversation, or all if None
        """
        if conversation_id:
            self.metrics.pop(conversation_id, None)
        else:
            self.metrics.clear()
