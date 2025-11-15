"""
CORTEX 3.0 Dual-Channel Memory System
=====================================

Architecture: Two-channel memory with intelligent fusion layer
- Channel 1: Conversational (GitHub Copilot Chat interactions)
- Channel 2: Traditional (Direct programmatic execution)
- Fusion Layer: Unified narrative creation and intelligent routing

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime
from enum import Enum
import json
import logging
from pathlib import Path

from ..tier1.working_memory import WorkingMemory
from ..track_a.integrations.conversational_channel_adapter import ConversationalChannelAdapter


class ChannelType(Enum):
    """Types of memory channels"""
    CONVERSATIONAL = "conversational"  # GitHub Copilot Chat
    TRADITIONAL = "traditional"       # Direct execution
    FUSION = "fusion"                 # Unified narrative


@dataclass
class MemoryEvent:
    """Base class for memory events across channels"""
    timestamp: Optional[datetime] = None
    channel: Optional[ChannelType] = None
    content: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    correlation_id: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.content is None:
            self.content = {}


@dataclass
class ConversationalEvent(MemoryEvent):
    """Conversational channel event (GitHub Copilot Chat)"""
    user_message: str = ""
    assistant_response: str = ""
    intent: str = ""
    entities: List[str] = None
    context_references: List[str] = None  # "it", "that", etc.
    
    def __post_init__(self):
        super().__post_init__()
        if self.entities is None:
            self.entities = []
        if self.context_references is None:
            self.context_references = []


@dataclass
class TraditionalEvent(MemoryEvent):
    """Traditional channel event (direct execution)"""
    operation: str = ""
    parameters: Dict[str, Any] = None
    result: Dict[str, Any] = None
    execution_time_ms: int = 0
    success: bool = False
    
    def __post_init__(self):
        super().__post_init__()
        if self.parameters is None:
            self.parameters = {}
        if self.result is None:
            self.result = {}


class ConversationalChannel:
    """
    Manages conversational interactions (GitHub Copilot Chat)
    
    Phase 2 Update: Now uses ConversationalChannelAdapter for enhanced storage
    with quality filtering, semantic metadata, and better error handling.
    """
    
    def __init__(self, working_memory: WorkingMemory):
        self.working_memory = working_memory
        self.adapter = ConversationalChannelAdapter(working_memory)
        self.logger = logging.getLogger(__name__)
        
    def store_conversation(self, user_message: str, assistant_response: str, 
                         intent: str, entities: List[str] = None,
                         context_references: List[str] = None,
                         session_id: str = None) -> str:
        """
        Store a conversational interaction using ConversationalChannelAdapter.
        
        Phase 2: Enhanced with semantic metadata and quality assessment.
        """
        
        # Build conversation structure for adapter
        conversation = {
            "messages": [
                {
                    "role": "user",
                    "content": user_message,
                    "timestamp": datetime.now().isoformat()
                },
                {
                    "role": "assistant",
                    "content": assistant_response,
                    "timestamp": datetime.now().isoformat()
                }
            ],
            "semantic_data": {
                "intent": intent,
                "entities": entities or [],
                "context_references": context_references or [],
                "quality_score": self._assess_quality(user_message, assistant_response)
            },
            "metadata": {
                "session_id": session_id,
                "channel": "conversational"
            }
        }
        
        # Store via adapter
        result = self.adapter.store_conversation(
            conversation=conversation,
            source="dual_channel_memory"
        )
        
        if result.get("success"):
            conversation_id = result["conversation_id"]
            self.logger.info(f"Stored conversational event: {conversation_id}")
            return conversation_id
        else:
            self.logger.error(f"Failed to store conversation: {result.get('reason', 'unknown')}")
            raise RuntimeError(f"Conversation storage failed: {result.get('reason', 'unknown')}")
    
    def _assess_quality(self, user_message: str, assistant_response: str) -> float:
        """
        Simple quality assessment based on message characteristics.
        
        Returns score 0-10 based on:
        - Message length (more detail = higher quality)
        - Response structure (code blocks, lists = higher quality)
        - Completeness (both user and assistant present)
        """
        quality = 5.0  # Base quality
        
        # Bonus for detailed user message
        if len(user_message) > 100:
            quality += 1.0
        if len(user_message) > 300:
            quality += 1.0
        
        # Bonus for comprehensive assistant response
        if len(assistant_response) > 200:
            quality += 1.0
        if len(assistant_response) > 500:
            quality += 1.0
        
        # Bonus for code blocks
        if "```" in assistant_response:
            quality += 1.0
        
        return min(quality, 10.0)
        
    def get_conversation_context(self, conversation_id: str) -> Optional[Dict]:
        """
        Retrieve conversation context for continuity.
        
        Phase 2: Uses adapter's enhanced retrieval with semantic data.
        """
        result = self.adapter.retrieve_conversation(conversation_id)
        
        if result and result.get("success"):
            return result
        
        return None
        
    def search_conversations(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search conversational interactions.
        
        Phase 2: Uses adapter's entity-based search capabilities.
        """
        # Use adapter for better search functionality
        # For now, use simple approach - TODO: enhance with full-text search
        conversations_orm = self.working_memory.get_recent_conversations(limit * 2)
        
        results = []
        for conv in conversations_orm:
            # Simple search: check if query is in title, intent, or messages
            title = getattr(conv, 'title', '')
            intent = getattr(conv, 'intent', '')
            
            # Check title and intent first
            title_match = query.lower() in title.lower()
            intent_match = intent and query.lower() in intent.lower()
            
            # Also check message content
            message_match = False
            if not title_match and not intent_match:
                messages = self.working_memory.get_messages(conv.conversation_id)
                for msg in messages:
                    if query.lower() in msg["content"].lower():
                        message_match = True
                        break
            
            if title_match or intent_match or message_match:
                
                # Get full conversation details via adapter
                conv_data = self.adapter.retrieve_conversation(conv.conversation_id)
                if conv_data and conv_data.get("success"):
                    results.append(conv_data["conversation"])
                    
                if len(results) >= limit:
                    break
        
        return results
    
    def get_statistics(self) -> Dict:
        """Get conversation statistics via adapter."""
        return self.adapter.get_statistics()


class TraditionalChannel:
    """Manages traditional direct execution events"""
    
    def __init__(self, storage_path: Union[str, Path]):
        self.storage_path = Path(storage_path)
        self.events_file = self.storage_path / "traditional_events.jsonl"
        self.logger = logging.getLogger(__name__)
        
        # Ensure storage directory exists
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
    def store_execution(self, operation: str, parameters: Dict[str, Any],
                       result: Dict[str, Any], execution_time_ms: int,
                       success: bool, session_id: str = None) -> str:
        """Store a traditional execution event"""
        
        event = TraditionalEvent(
            timestamp=datetime.now(),
            channel=ChannelType.TRADITIONAL,
            content={
                "operation": operation,
                "parameters": parameters,
                "result": result,
                "execution_time_ms": execution_time_ms,
                "success": success
            },
            operation=operation,
            parameters=parameters,
            result=result,
            execution_time_ms=execution_time_ms,
            success=success,
            session_id=session_id
        )
        
        # Generate unique ID
        event_id = f"trad_{int(event.timestamp.timestamp() * 1000)}"
        
        # Store as JSONL
        with open(self.events_file, "a", encoding="utf-8") as f:
            event_data = {
                "id": event_id,
                "timestamp": event.timestamp.isoformat(),
                "channel": event.channel.value,
                "operation": operation,
                "parameters": parameters,
                "result": result,
                "execution_time_ms": execution_time_ms,
                "success": success,
                "session_id": session_id
            }
            f.write(json.dumps(event_data) + "\n")
            
        self.logger.info(f"Stored traditional event: {event_id}")
        return event_id
        
    def get_recent_executions(self, limit: int = 20) -> List[Dict]:
        """Get recent execution events"""
        events = []
        
        if not self.events_file.exists():
            return events
            
        with open(self.events_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        # Get most recent events
        for line in reversed(lines[-limit:]):
            try:
                event = json.loads(line.strip())
                events.append(event)
            except json.JSONDecodeError:
                continue
                
        return events


class IntelligentFusion:
    """Fusion layer that creates unified narratives from both channels"""
    
    def __init__(self, conversational_channel: ConversationalChannel,
                 traditional_channel: TraditionalChannel):
        self.conversational_channel = conversational_channel
        self.traditional_channel = traditional_channel
        self.logger = logging.getLogger(__name__)
        
    def correlate_channels(self, time_window_minutes: int = 30) -> List[Dict]:
        """Correlate events across channels within time window"""
        
        # Get recent events from both channels (ORM objects)
        conversations_orm = self.conversational_channel.working_memory.get_recent_conversations(20)
        executions = self.traditional_channel.get_recent_executions(20)
        
        correlated_narratives = []
        
        for conv_orm in conversations_orm:
            # Convert ORM object to dict for processing
            # Use getattr with defaults for optional fields
            
            # Fetch first user message for user_request
            messages = self.conversational_channel.working_memory.get_messages(conv_orm.conversation_id)
            user_message = ""
            assistant_response = ""
            if messages:
                for msg in messages:
                    if msg["role"] == "user" and not user_message:
                        user_message = msg["content"]
                    elif msg["role"] == "assistant" and not assistant_response:
                        assistant_response = msg["content"]
            
            # Extract intent from semantic_elements JSON if available
            intent = ''
            semantic_elements_str = getattr(conv_orm, 'semantic_elements', None)
            if semantic_elements_str:
                try:
                    semantic_data = json.loads(semantic_elements_str)
                    intent = semantic_data.get('intent', '')
                    self.logger.debug(f"Extracted intent '{intent}' from semantic_data: {semantic_data}")
                except (json.JSONDecodeError, TypeError) as e:
                    self.logger.warning(f"Failed to parse semantic_elements: {e}")
                    intent = ''
            else:
                self.logger.debug(f"No semantic_elements found for conversation {conv_orm.conversation_id}")
            
            conversation = {
                "conversation_id": conv_orm.conversation_id,
                "timestamp": conv_orm.created_at.isoformat() if hasattr(conv_orm.created_at, 'isoformat') else str(conv_orm.created_at),
                "title": getattr(conv_orm, 'title', 'Untitled'),
                "intent": intent,
                "user_message": user_message,
                "assistant_response": assistant_response,
                "workflow_state": getattr(conv_orm, 'workflow_state', '')
            }
            
            # Find executions within time window
            conv_time = datetime.fromisoformat(conversation["timestamp"])
            related_executions = []
            
            for execution in executions:
                exec_time = datetime.fromisoformat(execution["timestamp"])
                time_diff = abs((conv_time - exec_time).total_seconds() / 60)
                
                if time_diff <= time_window_minutes:
                    related_executions.append(execution)
                    
            # Create unified narrative
            if related_executions:
                narrative = self._create_unified_narrative(conversation, related_executions)
                correlated_narratives.append(narrative)
                
        return correlated_narratives
        
    def _create_unified_narrative(self, conversation: Dict, 
                                executions: List[Dict]) -> Dict:
        """Create a unified development narrative"""
        
        return {
            "type": "unified_narrative",
            "conversation_id": conversation.get("conversation_id"),
            "user_request": conversation.get("user_message"),
            "intent": conversation.get("intent"),
            "response": conversation.get("assistant_response"),
            "executions": executions,
            "timeline": sorted([
                {"time": conversation["timestamp"], "type": "conversation", "data": conversation},
                *[{"time": exec["timestamp"], "type": "execution", "data": exec} 
                  for exec in executions]
            ], key=lambda x: x["time"]),
            "outcome": self._determine_outcome(conversation, executions),
            "learning_value": self._assess_learning_value(conversation, executions)
        }
        
    def _determine_outcome(self, conversation: Dict, executions: List[Dict]) -> str:
        """Determine the overall outcome of the development narrative"""
        
        if not executions:
            return "conversation_only"
            
        success_count = sum(1 for exec in executions if exec.get("success", False))
        total_executions = len(executions)
        
        if success_count == total_executions:
            return "successful"
        elif success_count > 0:
            return "partially_successful"
        else:
            return "failed"
            
    def _assess_learning_value(self, conversation: Dict, executions: List[Dict]) -> str:
        """Assess the learning value of this narrative for Tier 2"""
        
        # High value: complex conversations with successful executions
        if (len(conversation.get("user_message", "").split()) > 10 and 
            executions and 
            all(exec.get("success", False) for exec in executions)):
            return "high"
            
        # Medium value: simple conversations with some execution
        if executions:
            return "medium"
            
        # Low value: conversation only
        return "low"


class DualChannelMemory:
    """Main dual-channel memory system for CORTEX 3.0"""
    
    def __init__(self, cortex_brain_path: Union[str, Path]):
        self.cortex_brain_path = Path(cortex_brain_path)
        
        # Initialize channels
        working_memory = WorkingMemory()
        self.conversational_channel = ConversationalChannel(working_memory)
        self.traditional_channel = TraditionalChannel(self.cortex_brain_path / "tier1" / "dual_channel")
        self.fusion_layer = IntelligentFusion(
            self.conversational_channel, 
            self.traditional_channel
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("CORTEX 3.0 Dual-Channel Memory System initialized")
        
    def store_conversation(self, user_message: str, assistant_response: str,
                         intent: str, **kwargs) -> str:
        """Store a conversational interaction"""
        return self.conversational_channel.store_conversation(
            user_message=user_message,
            assistant_response=assistant_response,
            intent=intent,
            **kwargs
        )
        
    def store_execution(self, operation: str, parameters: Dict[str, Any],
                       result: Dict[str, Any], **kwargs) -> str:
        """Store a traditional execution event"""
        return self.traditional_channel.store_execution(
            operation=operation,
            parameters=parameters,
            result=result,
            **kwargs
        )
        
    def get_unified_narrative(self, time_window_minutes: int = 30) -> List[Dict]:
        """Get unified development narratives"""
        return self.fusion_layer.correlate_channels(time_window_minutes)
        
    def search_memory(self, query: str, channel: Optional[str] = None) -> List[Dict]:
        """Search across both channels or specific channel"""
        
        results = []
        
        if not channel or channel == "conversational":
            conv_results = self.conversational_channel.search_conversations(query)
            results.extend([{"channel": "conversational", **result} for result in conv_results])
            
        if not channel or channel == "traditional":
            # Search traditional events (simple text matching for now)
            traditional_events = self.traditional_channel.get_recent_executions(100)
            for event in traditional_events:
                if query.lower() in json.dumps(event).lower():
                    results.append({"channel": "traditional", **event})
                    
        return results
        
    def get_development_context(self, conversation_id: str = None) -> Dict:
        """Get complete development context for continuity"""
        
        context = {
            "unified_narratives": self.get_unified_narrative(),
            "recent_conversations": self.conversational_channel.working_memory.get_recent_conversations(5),
            "recent_executions": self.traditional_channel.get_recent_executions(10)
        }
        
        if conversation_id:
            context["current_conversation"] = self.conversational_channel.get_conversation_context(conversation_id)
            
        return context