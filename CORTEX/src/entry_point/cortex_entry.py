"""
CORTEX Main Entry Point

This module provides the unified entry point for all CORTEX interactions.
It coordinates request parsing, agent routing, and response formatting.

Usage:
    from CORTEX.src.entry_point import CortexEntry
    
    entry = CortexEntry()
    response = entry.process("Add authentication to the login page")
    print(response)
"""

from typing import Optional, Dict, Any
from datetime import datetime
import logging
from pathlib import Path

from ..cortex_agents.base_agent import AgentRequest, AgentResponse
from ..cortex_agents.intent_router import IntentRouter
from .request_parser import RequestParser
from .response_formatter import ResponseFormatter
from ..session_manager import SessionManager
from ..tier1.tier1_api import Tier1API
from ..tier2.knowledge_graph import KnowledgeGraph
from ..tier3.context_intelligence import ContextIntelligence
from ..config import config


class CortexEntry:
    """
    Main entry point for CORTEX system.
    
    Coordinates all components:
    - Request parsing (natural language → AgentRequest)
    - Session management (conversation tracking)
    - Agent routing (request → appropriate specialist)
    - Response formatting (AgentResponse → user-friendly output)
    - Tier integration (Tier 1, 2, 3 APIs)
    
    Example:
        entry = CortexEntry()
        
        # Process single request
        response = entry.process("Create tests for auth.py")
        print(response)
        
        # Process with session continuity
        response = entry.process(
            "Make the button purple",
            resume_session=True  # References previous conversation
        )
    """
    
    def __init__(
        self,
        brain_path: Optional[str] = None,
        enable_logging: bool = True
    ):
        """
        Initialize CORTEX entry point.
        
        Args:
            brain_path: Path to CORTEX brain directory
                       (default: auto-detected from config)
            enable_logging: Whether to enable detailed logging
        """
        # Set brain path (use config if not provided)
        if brain_path is None:
            brain_path = config.brain_path
        self.brain_path = Path(brain_path)
        
        # Ensure brain directory structure exists
        config.ensure_paths_exist()
        
        # Setup logging
        self.logger = self._setup_logging(enable_logging)
        
        # Initialize tier APIs
        self.tier1 = Tier1API(
            self.brain_path / "tier1" / "conversations.db",
            self.brain_path / "tier1" / "requests.log"
        )
        self.tier2 = KnowledgeGraph(str(self.brain_path / "tier2" / "knowledge_graph.db"))
        self.tier3 = ContextIntelligence(str(self.brain_path / "tier3" / "context.db"))
        
        # Initialize components
        self.parser = RequestParser()
        self.formatter = ResponseFormatter()
        self.session_manager = SessionManager()
        
        # Initialize router with tier APIs
        self.router = IntentRouter(
            name="IntentRouter",
            tier1_api=self.tier1,
            tier2_kg=self.tier2,
            tier3_context=self.tier3
        )
        
        self.logger.info("CORTEX entry point initialized")
    
    def process(
        self,
        user_message: str,
        resume_session: bool = True,
        format_type: str = "text",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Process a user request through CORTEX.
        
        Args:
            user_message: Natural language request from user
            resume_session: Whether to resume previous session
                           (uses 30-min boundary per Rule #11)
            format_type: Output format ("text", "json", "markdown")
            metadata: Optional additional metadata
            
        Returns:
            Formatted response string
        """
        try:
            # Get or create session
            conversation_id = self._get_conversation_id(resume_session)
            
            # Log request to Tier 1
            self.tier1.process_message(
                conversation_id,
                role="user",
                content=user_message
            )
            
            # Parse request
            request = self.parser.parse(
                user_message,
                conversation_id=conversation_id,
                metadata=metadata
            )
            
            self.logger.info(
                f"Processing request: intent={request.intent}, "
                f"conv_id={conversation_id}"
            )
            
            # Route to appropriate agent(s)
            response = self.router.execute(request)
            
            # Log response to Tier 1
            self.tier1.process_message(
                conversation_id,
                role="assistant",
                content=response.message
            )
            
            # Format response
            formatted = self.formatter.format(
                response,
                format_type=format_type
            )
            
            self.logger.info(
                f"Request completed: success={response.success}, "
                f"duration={response.duration_ms}ms"
            )
            
            return formatted
            
        except Exception as e:
            self.logger.error(f"Error processing request: {e}", exc_info=True)
            return self.formatter.format_error(
                e,
                context={"user_message": user_message}
            )
    
    def process_batch(
        self,
        messages: list[str],
        resume_session: bool = True,
        format_type: str = "text"
    ) -> str:
        """
        Process multiple requests in sequence.
        
        Args:
            messages: List of user messages
            resume_session: Whether to use same session for all
            format_type: Output format
            
        Returns:
            Formatted batch response
        """
        responses = []
        conversation_id = None
        
        if resume_session:
            conversation_id = self._get_conversation_id(True)
        
        for message in messages:
            if not resume_session:
                conversation_id = self._get_conversation_id(False)
            
            try:
                # Parse and route
                request = self.parser.parse(message, conversation_id)
                response = self.router.execute(request)
                responses.append(response)
                
                # Log to Tier 1
                self.tier1.process_message(conversation_id, "user", message)
                self.tier1.process_message(conversation_id, "assistant", response.message)
                
            except Exception as e:
                # Create error response
                error_response = AgentResponse(
                    success=False,
                    result=None,
                    message=str(e),
                    agent_name="CortexEntry",
                    metadata={"error": True}
                )
                responses.append(error_response)
        
        return self.formatter.format_batch(
            responses,
            format_type=format_type
        )
    
    def get_session_info(self) -> Optional[Dict[str, Any]]:
        """
        Get information about current active session.
        
        Returns:
            Session info dict or None if no active session
        """
        conversation_id = self.session_manager.get_active_session()
        if not conversation_id:
            return None
        
        return self.session_manager.get_session_info(conversation_id)
    
    def end_session(self) -> None:
        """
        Explicitly end current session.
        
        Useful for starting fresh conversation.
        """
        conversation_id = self.session_manager.get_active_session()
        if conversation_id:
            self.session_manager.end_session(conversation_id)
            self.tier1.end_conversation(conversation_id)
            self.logger.info(f"Session ended: {conversation_id}")
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get CORTEX system health status.
        
        Returns:
            Health status dict with tier statuses
        """
        health = {
            "timestamp": datetime.now().isoformat(),
            "tiers": {},
            "agents": {},
            "overall_status": "healthy"
        }
        
        # Check Tier 1
        try:
            summary = self.tier1.get_summary()
            health["tiers"]["tier1"] = {
                "status": "healthy",
                "conversations": summary.get("total_conversations", 0),
                "messages": summary.get("total_messages", 0)
            }
        except Exception as e:
            health["tiers"]["tier1"] = {"status": "error", "error": str(e)}
            health["overall_status"] = "degraded"
        
        # Check Tier 2
        try:
            stats = self.tier2.get_statistics()
            health["tiers"]["tier2"] = {
                "status": "healthy",
                "patterns": stats.get("total_patterns", 0),
                "relationships": stats.get("total_relationships", 0)
            }
        except Exception as e:
            health["tiers"]["tier2"] = {"status": "error", "error": str(e)}
            health["overall_status"] = "degraded"
        
        # Check Tier 3
        try:
            summary = self.tier3.get_context_summary()
            health["tiers"]["tier3"] = {
                "status": "healthy",
                "velocity": summary.get("velocity", {}).get("trend", "unknown")
            }
        except Exception as e:
            health["tiers"]["tier3"] = {"status": "error", "error": str(e)}
            health["overall_status"] = "degraded"
        
        # Router status
        health["agents"]["router"] = "operational"
        
        return health
    
    def _get_conversation_id(self, resume: bool) -> str:
        """
        Get conversation ID for request.
        
        Args:
            resume: Whether to resume existing session
            
        Returns:
            Conversation ID (UUID)
        """
        if resume:
            # Try to resume active session
            conversation_id = self.session_manager.get_active_session()
            if conversation_id:
                return conversation_id
        
        # Start new session
        conversation_id = self.session_manager.start_session()
        return conversation_id
    
    def _setup_logging(self, enable: bool) -> logging.Logger:
        """Setup logging for entry point."""
        logger = logging.getLogger("cortex.entry_point")
        
        if enable and not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        
        return logger
