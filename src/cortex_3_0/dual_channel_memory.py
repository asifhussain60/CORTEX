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
    """Manages conversational interactions (GitHub Copilot Chat)"""
    
    def __init__(self, working_memory: WorkingMemory):
        self.working_memory = working_memory
        self.logger = logging.getLogger(__name__)
        
    def store_conversation(self, user_message: str, assistant_response: str, 
                         intent: str, entities: List[str] = None,
                         context_references: List[str] = None,
                         session_id: str = None) -> str:
        """Store a conversational interaction"""
        
        event = ConversationalEvent(
            timestamp=datetime.now(),
            channel=ChannelType.CONVERSATIONAL,
            content={
                "user_message": user_message,
                "assistant_response": assistant_response,
                "intent": intent,
                "entities": entities or [],
                "context_references": context_references or []
            },
            user_message=user_message,
            assistant_response=assistant_response,
            intent=intent,
            entities=entities or [],
            context_references=context_references or [],
            session_id=session_id
        )
        
        # Store in Tier 1 working memory
        conversation_id = self.working_memory.store_conversation(
            user_message=user_message,
            assistant_response=assistant_response,
            intent=intent,
            context={
                "channel": "conversational",
                "entities": entities or [],
                "context_references": context_references or [],
                "session_id": session_id
            }
        )
        
        self.logger.info(f"Stored conversational event: {conversation_id}")
        return conversation_id
        
    def get_conversation_context(self, conversation_id: str) -> Optional[Dict]:
        """Retrieve conversation context for continuity"""
        return self.working_memory.get_conversation_context(conversation_id)
        
    def search_conversations(self, query: str, limit: int = 10) -> List[Dict]:
        """Search conversational interactions"""
        return self.working_memory.search_conversations(
            query=query,
            filters={"channel": "conversational"},
            limit=limit
        )


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
        
        # Get recent events from both channels
        conversations = self.conversational_channel.working_memory.get_recent_conversations(20)
        executions = self.traditional_channel.get_recent_executions(20)
        
        correlated_narratives = []
        
        for conversation in conversations:
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