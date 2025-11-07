"""
SessionResumer Agent

Restores conversation context from Tier 1 working memory.
Reconstructs conversation history, context, and state to resume work
after interruptions or session changes.

The SessionResumer helps CORTEX overcome "amnesia" by retrieving and
reconstructing previous conversation context.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from CORTEX.src.cortex_agents.base_agent import BaseAgent, AgentRequest, AgentResponse
from CORTEX.src.cortex_agents.agent_types import IntentType
from CORTEX.src.cortex_agents.utils import safe_get, format_duration


class SessionResumer(BaseAgent):
    """
    Restores conversation context from Tier 1 working memory.
    
    The SessionResumer retrieves conversation history from Tier 1 and
    reconstructs the full context needed to continue work seamlessly
    after interruptions or session changes.
    
    Features:
    - Conversation history retrieval from Tier 1
    - Context reconstruction from conversation messages
    - File and entity extraction from conversation
    - Timeline reconstruction for work resumption
    - Multi-turn conversation support
    
    Example:
        resumer = SessionResumer(name="Resumer", tier1_api, tier2_kg, tier3_context)
        
        request = AgentRequest(
            intent="resume",
            context={"conversation_id": "conv-123"},
            user_message="Resume previous conversation about authentication"
        )
        
        response = resumer.execute(request)
        # Returns: {
        #   "conversation_id": "conv-123",
        #   "messages": [...],
        #   "summary": "Working on authentication feature",
        #   "files_discussed": ["auth.py", "user.py"],
        #   "entities": ["User", "Auth", "JWT"]
        # }
    """
    
    def __init__(self, name: str, tier1_api, tier2_kg, tier3_context):
        """
        Initialize SessionResumer.
        
        Args:
            name: Agent name
            tier1_api: Tier 1 conversation manager API
            tier2_kg: Tier 2 knowledge graph API
            tier3_context: Tier 3 context intelligence API
        """
        super().__init__(name, tier1_api, tier2_kg, tier3_context)
        self.supported_intents = [
            IntentType.RESUME.value,
            "restore_session",
            "continue_conversation"
        ]
    
    def can_handle(self, request: AgentRequest) -> bool:
        """
        Check if this agent can handle the request.
        
        Args:
            request: The agent request to evaluate
            
        Returns:
            True if intent is resume/restore/continue, False otherwise
        """
        return request.intent in self.supported_intents
    
    def execute(self, request: AgentRequest) -> AgentResponse:
        """
        Restore conversation context from Tier 1.
        
        Args:
            request: Agent request with conversation_id in context
            
        Returns:
            AgentResponse with conversation history and reconstructed context
        """
        start_time = datetime.now()
        
        try:
            # Extract conversation ID from request
            conversation_id = self._get_conversation_id(request)
            if not conversation_id:
                return self._error_response(
                    "No conversation_id provided in request",
                    start_time
                )
            
            # Retrieve conversation from Tier 1
            conversation = self._retrieve_conversation(conversation_id)
            if not conversation:
                return self._error_response(
                    f"Conversation {conversation_id} not found in Tier 1",
                    start_time
                )
            
            # Reconstruct context from conversation
            context = self._reconstruct_context(conversation)
            
            # Build response
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            return AgentResponse(
                success=True,
                result={
                    "conversation_id": conversation_id,
                    "messages": conversation.get("messages", []),
                    "summary": context.get("summary", ""),
                    "files_discussed": context.get("files", []),
                    "entities": context.get("entities", []),
                    "timeline": context.get("timeline", []),
                    "last_activity": conversation.get("updated_at", "")
                },
                message=f"Restored conversation {conversation_id} with {len(conversation.get('messages', []))} messages",
                agent_name=self.name,
                duration_ms=duration_ms,
                next_actions=[
                    "Review conversation history",
                    "Continue from last message",
                    "Execute next planned task"
                ]
            )
            
        except Exception as e:
            self.logger.error(f"Session resumption failed: {e}", exc_info=True)
            return self._error_response(str(e), start_time)
    
    def _get_conversation_id(self, request: AgentRequest) -> Optional[str]:
        """
        Extract conversation ID from request.
        
        Args:
            request: Agent request
            
        Returns:
            Conversation ID or None
        """
        # Check request.conversation_id first
        if request.conversation_id:
            return request.conversation_id
        
        # Check context
        return safe_get(request.context, "conversation_id")
    
    def _retrieve_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve conversation from Tier 1.
        
        Args:
            conversation_id: ID of conversation to retrieve
            
        Returns:
            Conversation data or None if not found
        """
        try:
            # Query Tier 1 for conversation
            result = self.tier1.get_conversation(conversation_id)
            
            if not result or not result.get("success"):
                return None
            
            return result.get("conversation")
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve conversation {conversation_id}: {e}")
            return None
    
    def _reconstruct_context(self, conversation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Reconstruct context from conversation history.
        
        Args:
            conversation: Conversation data from Tier 1
            
        Returns:
            Reconstructed context with summary, files, entities, timeline
        """
        context = {
            "summary": "",
            "files": [],
            "entities": [],
            "timeline": []
        }
        
        messages = conversation.get("messages", [])
        if not messages:
            return context
        
        # Extract summary from conversation metadata
        context["summary"] = conversation.get("summary", "")
        
        # Extract files from messages
        files = set()
        for msg in messages:
            # Check message metadata for files
            msg_metadata = msg.get("metadata", {})
            if isinstance(msg_metadata, dict):
                msg_files = msg_metadata.get("files", [])
                if isinstance(msg_files, list):
                    files.update(msg_files)
            
            # Check message content for file mentions
            content = msg.get("content", "")
            if isinstance(content, str):
                # Simple file pattern matching (basic implementation)
                # Could be enhanced with more sophisticated parsing
                import re
                file_pattern = r'`([^`]+\.(py|md|json|yaml|txt|js|ts))`'
                matches = re.findall(file_pattern, content)
                files.update([m[0] for m in matches])
        
        context["files"] = sorted(list(files))
        
        # Extract entities from metadata
        entities = set()
        for msg in messages:
            msg_metadata = msg.get("metadata", {})
            if isinstance(msg_metadata, dict):
                msg_entities = msg_metadata.get("entities", [])
                if isinstance(msg_entities, list):
                    entities.update(msg_entities)
        
        context["entities"] = sorted(list(entities))
        
        # Build timeline from messages
        timeline = []
        for msg in messages:
            timeline.append({
                "timestamp": msg.get("timestamp", ""),
                "role": msg.get("role", ""),
                "summary": msg.get("content", "")[:100] + "..." if len(msg.get("content", "")) > 100 else msg.get("content", "")
            })
        
        context["timeline"] = timeline
        
        return context
    
    def _error_response(self, error_msg: str, start_time: datetime) -> AgentResponse:
        """
        Create error response.
        
        Args:
            error_msg: Error message
            start_time: Request start time
            
        Returns:
            AgentResponse with error details
        """
        duration_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        return AgentResponse(
            success=False,
            result={},
            message=f"Session resumption failed: {error_msg}",
            agent_name=self.name,
            duration_ms=duration_ms,
            metadata={"error": error_msg}
        )
