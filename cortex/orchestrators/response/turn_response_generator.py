"""Turn Response Generator - AC-RESP-001-01

Generates and formats multi-turn conversation responses with metadata tracking,
flexible formatting modes, and caching capabilities.

Author: CORTEX Framework
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from enum import Enum
import hashlib
from datetime import datetime
import sys


class ResponseMode(Enum):
    """Response delivery mode for different interfaces.
    
    Attributes:
        CHAT: Conversational chat interface
        COMMAND: Command-line interface
        VISUALIZATION: Visual/graphical representation
        JSON_API: JSON API response format
        MARKDOWN: Markdown document format
        STREAM: Streaming response format
    """
    CHAT = "chat"
    COMMAND = "command"
    VISUALIZATION = "visualization"
    JSON_API = "json_api"
    MARKDOWN = "markdown"
    STREAM = "stream"


class ResponseTone(Enum):
    """Response communication tone.
    
    Attributes:
        FORMAL: Professional formal tone
        CASUAL: Relaxed conversational tone
        TECHNICAL: Technical documentation tone
        EXECUTIVE: Executive summary tone
        EDUCATIONAL: Teaching/tutorial tone
    """
    FORMAL = "formal"
    CASUAL = "casual"
    TECHNICAL = "technical"
    EXECUTIVE = "executive"
    EDUCATIONAL = "educational"


@dataclass
class ResponseMetadata:
    """Metadata for response tracking and context.
    
    Attributes:
        mode: Response delivery mode
        tone: Communication tone
        turn_number: Turn sequence number
        operation_id: Associated operation ID
        phase: Execution phase identifier
        orchestrator: Orchestrator that generated response
        context_hash: MD5 hash of context (32 chars, auto-generated)
        timestamp: Generation timestamp (auto-generated)
        token_estimate: Estimated token count (default 0)
    """
    mode: ResponseMode
    tone: ResponseTone
    turn_number: int
    operation_id: str
    phase: str
    orchestrator: str
    context_hash: str = field(default="")
    timestamp: datetime = field(default_factory=datetime.now)
    token_estimate: int = 0
    
    def __post_init__(self) -> None:
        """Generate context hash if not provided."""
        if not self.context_hash:
            context_str = f"{self.operation_id}:{self.turn_number}:{self.phase}:{self.orchestrator}"
            self.context_hash = hashlib.md5(context_str.encode()).hexdigest()


@dataclass
class ResponseSegment:
    """Individual segment of a response.
    
    Attributes:
        segment_type: Type of segment (header, body, alternatives, footer, etc.)
        content: Segment content
        length: Character length (auto-calculated)
    """
    segment_type: str
    content: str
    
    @property
    def length(self) -> int:
        """Calculate segment length.
        
        Returns:
            Number of characters in content
        """
        return len(self.content)


@dataclass
class TurnResponse:
    """Complete response for a conversation turn.
    
    Attributes:
        operation_id: Associated operation ID
        turn_number: Turn sequence number
        metadata: Response metadata
        segments: List of response segments
        formatted_content: Formatted response text
        raw_content: Raw unformatted content
        alternatives: List of alternative actions/responses
        confidence_score: Response confidence (0.0-1.0)
        ready_to_send: Whether response is complete
    """
    operation_id: str
    turn_number: int
    metadata: ResponseMetadata
    segments: List[ResponseSegment] = field(default_factory=list)
    formatted_content: str = ""
    raw_content: str = ""
    alternatives: List[Dict[str, Any]] = field(default_factory=list)
    confidence_score: float = 1.0
    ready_to_send: bool = False
    
    @property
    def segment_summary(self) -> Dict[str, int]:
        """Summarize segments by type with their lengths.
        
        Returns:
            Dictionary mapping segment type to total length of that type
        """
        summary: Dict[str, int] = {}
        for segment in self.segments:
            summary[segment.segment_type] = summary.get(segment.segment_type, 0) + segment.length
        return summary
    
    @property
    def total_length(self) -> int:
        """Calculate total response length.
        
        Returns:
            Sum of all segment lengths
        """
        return sum(segment.length for segment in self.segments)


class ResponseBuilder:
    """Builder for constructing turn responses fluently.
    
    Attributes:
        operation_id: Associated operation ID
        turn_number: Turn sequence number
        mode: Response mode
        segments: List of segments being built
        alternatives: List of alternative actions
    """
    
    def __init__(self, operation_id: str, turn_number: int, mode: ResponseMode = ResponseMode.CHAT) -> None:
        """Initialize response builder.
        
        Args:
            operation_id: Operation identifier
            turn_number: Turn sequence number
            mode: Response mode (default CHAT)
        """
        self.operation_id = operation_id
        self.turn_number = turn_number
        self.mode = mode
        self.segments: List[ResponseSegment] = []
        self.alternatives: List[Dict[str, Any]] = []
    
    def add_header(self, content: str) -> "ResponseBuilder":
        """Add header segment.
        
        Args:
            content: Header text
            
        Returns:
            Self for chaining
        """
        self.segments.append(ResponseSegment(segment_type="header", content=content))
        return self
    
    def add_body(self, content: str) -> "ResponseBuilder":
        """Add body segment.
        
        Args:
            content: Body text
            
        Returns:
            Self for chaining
        """
        self.segments.append(ResponseSegment(segment_type="body", content=content))
        return self
    
    def add_alternatives(self, alternatives: List[Dict[str, Any]]) -> "ResponseBuilder":
        """Add alternatives segment.
        
        Args:
            alternatives: List of alternative actions
            
        Returns:
            Self for chaining
        """
        self.alternatives = alternatives
        content = "\n".join([f"- {alt.get('name', 'Unknown')}: {alt.get('description', '')}" 
                             for alt in alternatives])
        self.segments.append(ResponseSegment(segment_type="alternatives", content=content))
        return self
    
    def add_footer(self, content: str) -> "ResponseBuilder":
        """Add footer segment.
        
        Args:
            content: Footer text
            
        Returns:
            Self for chaining
        """
        self.segments.append(ResponseSegment(segment_type="footer", content=content))
        return self
    
    def build(self, metadata: ResponseMetadata) -> TurnResponse:
        """Build final response.
        
        Args:
            metadata: Response metadata
            
        Returns:
            Complete TurnResponse object
        """
        formatted_content = "\n\n".join(segment.content for segment in self.segments)
        
        return TurnResponse(
            operation_id=self.operation_id,
            turn_number=self.turn_number,
            metadata=metadata,
            segments=self.segments,
            formatted_content=formatted_content,
            alternatives=self.alternatives,
            ready_to_send=True
        )


class ResponseFormatter:
    """Format responses for different delivery modes.
    
    Provides static methods to convert TurnResponse objects into
    mode-specific formats (chat, command, JSON API, markdown).
    """
    
    @staticmethod
    def format_chat(response: TurnResponse) -> Dict[str, Any]:
        """Format response for chat interface.
        
        Args:
            response: Turn response to format
            
        Returns:
            Dictionary with chat-specific structure
        """
        return {
            "type": "chat",
            "turn": response.turn_number,
            "operation": response.operation_id,
            "content": response.formatted_content,
            "alternatives": response.alternatives,
            "confidence": response.confidence_score,
            "metadata": {
                "mode": response.metadata.mode.value,
                "tone": response.metadata.tone.value,
                "phase": response.metadata.phase,
                "orchestrator": response.metadata.orchestrator,
            }
        }
    
    @staticmethod
    def format_command(response: TurnResponse) -> str:
        """Format response for command-line interface.
        
        Args:
            response: Turn response to format
            
        Returns:
            Formatted command-line string
        """
        lines = [
            f"═══════════════════════════════════════════════",
            f"Turn {response.turn_number} | {response.metadata.orchestrator}",
            f"Operation: {response.operation_id}",
            f"═══════════════════════════════════════════════",
            "",
            response.formatted_content,
            "",
        ]
        
        if response.alternatives:
            lines.append("Alternatives:")
            for alt in response.alternatives:
                lines.append(f"  • {alt.get('name', 'Unknown')}: {alt.get('description', '')}")
            lines.append("")
        
        lines.append(f"Confidence: {response.confidence_score:.0%}")
        
        return "\n".join(lines)
    
    @staticmethod
    def format_json_api(response: TurnResponse) -> Dict[str, Any]:
        """Format response for JSON API.
        
        Args:
            response: Turn response to format
            
        Returns:
            JSON API v1.0 compliant structure
        """
        return {
            "data": {
                "type": "response",
                "id": f"{response.operation_id}:turn{response.turn_number}",
                "attributes": {
                    "content": response.formatted_content,
                    "turn_number": response.turn_number,
                    "confidence_score": response.confidence_score,
                    "alternatives": response.alternatives,
                    "segment_summary": response.segment_summary,
                    "total_length": response.total_length,
                },
                "meta": {
                    "mode": response.metadata.mode.value,
                    "tone": response.metadata.tone.value,
                    "phase": response.metadata.phase,
                    "orchestrator": response.metadata.orchestrator,
                    "context_hash": response.metadata.context_hash,
                    "timestamp": response.metadata.timestamp.isoformat(),
                }
            }
        }
    
    @staticmethod
    def format_markdown(response: TurnResponse) -> str:
        """Format response as markdown document.
        
        Args:
            response: Turn response to format
            
        Returns:
            Markdown-formatted string
        """
        lines = [
            f"# Turn {response.turn_number}",
            "",
            f"**Operation:** {response.operation_id}",
            f"**Orchestrator:** {response.metadata.orchestrator}",
            f"**Phase:** {response.metadata.phase}",
            "",
            "---",
            "",
            response.formatted_content,
            "",
        ]
        
        if response.alternatives:
            lines.append("## Alternatives")
            lines.append("")
            for alt in response.alternatives:
                lines.append(f"- **{alt.get('name', 'Unknown')}**: {alt.get('description', '')}")
            lines.append("")
        
        lines.append(f"*Confidence: {response.confidence_score:.0%}*")
        
        return "\n".join(lines)


class TurnResponseGenerator:
    """Generate and cache turn responses.
    
    Main engine for creating, formatting, and caching conversation turn responses
    with support for multiple modes and tones.
    
    Attributes:
        default_mode: Default response mode
        default_tone: Default communication tone
        response_cache: Cache of generated responses
        generation_count: Total number of responses generated
    """
    
    def __init__(
        self,
        default_mode: ResponseMode = ResponseMode.CHAT,
        default_tone: ResponseTone = ResponseTone.TECHNICAL
    ) -> None:
        """Initialize turn response generator.
        
        Args:
            default_mode: Default response mode
            default_tone: Default communication tone
        """
        self.default_mode = default_mode
        self.default_tone = default_tone
        self.response_cache: Dict[str, TurnResponse] = {}
        self.generation_count = 0
    
    def generate_response(
        self,
        operation_id: str,
        turn_number: int,
        content: str,
        mode: Optional[ResponseMode] = None,
        tone: Optional[ResponseTone] = None,
        phase: str = "UNKNOWN",
        orchestrator: str = "DefaultOrchestrator",
        alternatives: Optional[List[Dict[str, Any]]] = None,
        confidence_score: float = 1.0
    ) -> TurnResponse:
        """Generate a turn response.
        
        Args:
            operation_id: Operation identifier
            turn_number: Turn sequence number
            content: Response content
            mode: Response mode (uses default if None)
            tone: Communication tone (uses default if None)
            phase: Execution phase
            orchestrator: Orchestrator name
            alternatives: List of alternative actions
            confidence_score: Response confidence (0.0-1.0)
            
        Returns:
            Generated TurnResponse
        """
        use_mode = mode or self.default_mode
        use_tone = tone or self.default_tone
        use_alternatives = alternatives or []
        
        # Create metadata
        metadata = ResponseMetadata(
            mode=use_mode,
            tone=use_tone,
            turn_number=turn_number,
            operation_id=operation_id,
            phase=phase,
            orchestrator=orchestrator
        )
        
        # Build response
        builder = ResponseBuilder(operation_id, turn_number)
        builder.add_body(content)
        if use_alternatives:
            builder.add_alternatives(use_alternatives)
        
        response = builder.build(metadata)
        response.confidence_score = confidence_score
        response.raw_content = content
        
        # Cache response
        cache_key = f"{operation_id}:{turn_number}"
        self.response_cache[cache_key] = response
        self.generation_count += 1
        
        return response
    
    def get_cached_response(
        self,
        operation_id: str,
        turn_number: int
    ) -> Optional[TurnResponse]:
        """Retrieve cached response.
        
        Args:
            operation_id: Operation identifier
            turn_number: Turn sequence number
            
        Returns:
            Cached response or None if not found
        """
        cache_key = f"{operation_id}:{turn_number}"
        return self.response_cache.get(cache_key)
    
    def format_response(
        self,
        response: TurnResponse,
        output_format: str = "chat"
    ) -> Any:
        """Format response for specific delivery mode.
        
        Args:
            response: Response to format
            output_format: Format type (chat, command, json, markdown)
            
        Returns:
            Formatted response (type depends on output_format)
        """
        if output_format == "chat":
            return ResponseFormatter.format_chat(response)
        elif output_format == "command":
            return ResponseFormatter.format_command(response)
        elif output_format == "json":
            return ResponseFormatter.format_json_api(response)
        elif output_format == "markdown":
            return ResponseFormatter.format_markdown(response)
        else:
            return response.formatted_content
    
    def clear_cache(self, operation_id: Optional[str] = None) -> None:
        """Clear response cache.
        
        Args:
            operation_id: Clear only this operation's cache (or all if None)
        """
        if operation_id is None:
            self.response_cache.clear()
        else:
            keys_to_remove = [key for key in self.response_cache.keys() 
                              if key.startswith(f"{operation_id}:")]
            for key in keys_to_remove:
                del self.response_cache[key]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get generator statistics.
        
        Returns:
            Dictionary with generation statistics
        """
        cache_size = sys.getsizeof(self.response_cache)
        for response in self.response_cache.values():
            cache_size += sys.getsizeof(response)
        
        return {
            "total_generations": self.generation_count,
            "cached_responses": len(self.response_cache),
            "cache_size_bytes": cache_size,
        }


__all__ = [
    "ResponseMode",
    "ResponseTone",
    "ResponseMetadata",
    "ResponseSegment",
    "TurnResponse",
    "ResponseBuilder",
    "ResponseFormatter",
    "TurnResponseGenerator",
]
