"""Turn-by-Turn Response Generation Engine (AC-RESP-001-01)."""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

class ResponseMode(Enum):
    """Supported response modes for different communication channels."""
    CHAT = "chat"                    # Chat/conversation interface
    COMMAND = "command"              # CLI command execution
    VISUALIZATION = "visualization"  # Graph/diagram output
    JSON_API = "json_api"           # Structured JSON
    MARKDOWN = "markdown"            # Documentation format
    STREAM = "stream"                # Real-time streaming

class ResponseTone(Enum):
    """Response tone/personality settings."""
    FORMAL = "formal"                # Professional, structured
    CASUAL = "casual"                # Friendly, conversational
    TECHNICAL = "technical"          # Developer-focused, detailed
    EXECUTIVE = "executive"          # High-level summary
    EDUCATIONAL = "educational"      # Explanatory, teaching

@dataclass
class ResponseMetadata:
    """Metadata about the response generation."""
    mode: ResponseMode
    tone: ResponseTone
    turn_number: int
    operation_id: str
    phase: str
    orchestrator: str
    timestamp: datetime = field(default_factory=datetime.now)
    context_hash: str = ""
    token_estimate: int = 0
    
    def __post_init__(self):
        """Compute context hash."""
        import hashlib
        context_str = (
            f"{self.operation_id}|{self.phase}|"
            f"{self.orchestrator}|{self.turn_number}"
        )
        self.context_hash = hashlib.md5(context_str.encode()).hexdigest()

@dataclass
class ResponseSegment:
    """A segment of a response (e.g., header, body, footer)."""
    segment_type: str  # "header", "body", "alternatives", "footer"
    content: str
    formatting: Dict[str, Any] = field(default_factory=dict)
    length: int = field(default=0)
    
    def __post_init__(self):
        """Calculate segment length."""
        self.length = len(self.content)

@dataclass
class TurnResponse:
    """Complete response for a single turn."""
    operation_id: str
    turn_number: int
    metadata: ResponseMetadata
    segments: List[ResponseSegment] = field(default_factory=list)
    raw_content: str = ""
    formatted_content: str = ""
    alternatives: List[Dict[str, Any]] = field(default_factory=list)
    confidence_score: float = 0.0
    ready_to_send: bool = False
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def total_length(self) -> int:
        """Get total response length across all segments."""
        return sum(seg.length for seg in self.segments)
    
    @property
    def segment_summary(self) -> Dict[str, int]:
        """Get summary of segments."""
        summary = {}
        for seg in self.segments:
            summary[seg.segment_type] = summary.get(seg.segment_type, 0) + seg.length
        return summary

class ResponseBuilder:
    """Builds structured responses for a turn."""
    
    def __init__(self, operation_id: str, turn_number: int, mode: ResponseMode = ResponseMode.CHAT):
        """
        Initialize response builder.
        
        Args:
            operation_id: Operation ID for this turn
            turn_number: Sequential turn number
            mode: Response mode (default: CHAT)
        """
        self.operation_id = operation_id
        self.turn_number = turn_number
        self.mode = mode
        self.segments: List[ResponseSegment] = []
        self.raw_content = ""
        self.alternatives: List[Dict[str, Any]] = []
    
    def add_header(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> "ResponseBuilder":
        """Add header segment."""
        segment = ResponseSegment(
            segment_type="header",
            content=content,
            formatting=metadata or {}
        )
        self.segments.append(segment)
        return self
    
    def add_body(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> "ResponseBuilder":
        """Add body segment."""
        segment = ResponseSegment(
            segment_type="body",
            content=content,
            formatting=metadata or {}
        )
        self.segments.append(segment)
        return self
    
    def add_alternatives(self, alternatives: List[Dict[str, Any]]) -> "ResponseBuilder":
        """Add alternatives segment."""
        alt_content = "\n".join([
            f"  • {alt.get('name', 'Alternative')}: {alt.get('description', '')}"
            for alt in alternatives
        ])
        segment = ResponseSegment(
            segment_type="alternatives",
            content=alt_content,
            formatting={"count": len(alternatives)}
        )
        self.segments.append(segment)
        self.alternatives = alternatives
        return self
    
    def add_footer(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> "ResponseBuilder":
        """Add footer segment."""
        segment = ResponseSegment(
            segment_type="footer",
            content=content,
            formatting=metadata or {}
        )
        self.segments.append(segment)
        return self
    
    def build(self, metadata: ResponseMetadata) -> TurnResponse:
        """
        Build final response.
        
        Args:
            metadata: Response metadata
            
        Returns:
            Completed TurnResponse
        """
        # Combine segments into formatted content
        formatted = "\n".join([seg.content for seg in self.segments])
        
        response = TurnResponse(
            operation_id=self.operation_id,
            turn_number=self.turn_number,
            metadata=metadata,
            segments=self.segments,
            raw_content=formatted,
            formatted_content=formatted,
            alternatives=self.alternatives,
            confidence_score=0.95,  # Default confidence
            ready_to_send=True,
        )
        
        return response

class ResponseFormatter:
    """Formats responses for different output modes."""
    
    @staticmethod
    def format_chat(response: TurnResponse) -> Dict[str, Any]:
        """Format response for chat interface."""
        return {
            "type": "chat",
            "turn": response.turn_number,
            "operation": response.metadata.operation_id,
            "content": response.formatted_content,
            "alternatives": response.alternatives,
            "timestamp": response.timestamp.isoformat(),
            "confidence": response.confidence_score,
        }
    
    @staticmethod
    def format_command(response: TurnResponse) -> str:
        """Format response for CLI output."""
        lines = [
            f"[Turn {response.turn_number}] {response.metadata.orchestrator}",
            f"Operation: {response.metadata.operation_id}",
            "---",
            response.formatted_content,
        ]
        
        if response.alternatives:
            lines.append("\nAlternatives:")
            for alt in response.alternatives:
                lines.append(f"  • {alt.get('name')}: {alt.get('description')}")
        
        return "\n".join(lines)
    
    @staticmethod
    def format_json_api(response: TurnResponse) -> Dict[str, Any]:
        """Format response for JSON API."""
        return {
            "data": {
                "type": "response",
                "id": f"{response.operation_id}-{response.turn_number}",
                "attributes": {
                    "content": response.formatted_content,
                    "mode": response.metadata.mode.value,
                    "tone": response.metadata.tone.value,
                    "turn": response.turn_number,
                    "confidence": response.confidence_score,
                },
                "relationships": {
                    "operation": {
                        "data": {
                            "type": "operation",
                            "id": response.operation_id,
                        }
                    }
                }
            },
            "included": [
                {
                    "type": "alternative",
                    "id": f"alt-{i}",
                    "attributes": alt,
                }
                for i, alt in enumerate(response.alternatives)
            ]
        }
    
    @staticmethod
    def format_markdown(response: TurnResponse) -> str:
        """Format response as markdown."""
        lines = [
            f"# Turn {response.turn_number}: {response.metadata.orchestrator}",
            f"**Operation:** {response.metadata.operation_id}  \n",
            f"**Phase:** {response.metadata.phase}  \n",
            f"---",
            response.formatted_content,
        ]
        
        if response.alternatives:
            lines.append("\n## Alternatives\n")
            for alt in response.alternatives:
                lines.append(f"- **{alt.get('name')}**: {alt.get('description')}")
        
        return "\n".join(lines)

class TurnResponseGenerator:
    """Main engine for generating responses per turn."""
    
    def __init__(self):
        """Initialize response generator."""
        self.default_mode = ResponseMode.CHAT
        self.default_tone = ResponseTone.TECHNICAL
        self.response_cache: Dict[str, TurnResponse] = {}
        self.generation_count = 0
    
    def generate_response(
        self,
        operation_id: str,
        turn_number: int,
        content: str,
        mode: ResponseMode = None,
        tone: ResponseTone = None,
        phase: str = "UNKNOWN",
        orchestrator: str = "UNKNOWN",
        alternatives: Optional[List[Dict[str, Any]]] = None,
    ) -> TurnResponse:
        """
        Generate response for a turn.
        
        Args:
            operation_id: Operation ID
            turn_number: Turn number
            content: Response content
            mode: Response mode (defaults to CHAT)
            tone: Response tone (defaults to TECHNICAL)
            phase: Current phase
            orchestrator: Active orchestrator
            alternatives: Alternative responses/actions
            
        Returns:
            Generated TurnResponse
        """
        self.generation_count += 1
        
        # Use defaults if not specified
        mode = mode or self.default_mode
        tone = tone or self.default_tone
        
        # Create metadata
        metadata = ResponseMetadata(
            mode=mode,
            tone=tone,
            turn_number=turn_number,
            operation_id=operation_id,
            phase=phase,
            orchestrator=orchestrator,
        )
        
        # Build response
        builder = ResponseBuilder(operation_id, turn_number, mode)
        builder.add_header(f"Turn {turn_number} Response")
        builder.add_body(content)
        
        if alternatives:
            builder.add_alternatives(alternatives)
        
        builder.add_footer(f"Generated at {datetime.now().isoformat()}")
        
        response = builder.build(metadata)
        
        # Cache response
        cache_key = f"{operation_id}_{turn_number}"
        self.response_cache[cache_key] = response
        
        return response
    
    def format_response(
        self,
        response: TurnResponse,
        output_format: str = "chat",
    ) -> Any:
        """
        Format response for output.
        
        Args:
            response: Response to format
            output_format: Output format ("chat", "command", "json", "markdown")
            
        Returns:
            Formatted response
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
            # Default to chat
            return ResponseFormatter.format_chat(response)
    
    def get_cached_response(self, operation_id: str, turn_number: int) -> Optional[TurnResponse]:
        """Get cached response for a turn."""
        cache_key = f"{operation_id}_{turn_number}"
        return self.response_cache.get(cache_key)
    
    def clear_cache(self, operation_id: Optional[str] = None) -> None:
        """
        Clear response cache.
        
        Args:
            operation_id: If specified, clear only responses for this operation
        """
        if operation_id:
            to_delete = [k for k in self.response_cache.keys() if k.startswith(operation_id)]
            for k in to_delete:
                del self.response_cache[k]
        else:
            self.response_cache.clear()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get generator statistics."""
        return {
            "total_generations": self.generation_count,
            "cached_responses": len(self.response_cache),
            "cache_size_bytes": sum(
                len(str(r.formatted_content)) for r in self.response_cache.values()
            ),
        }
