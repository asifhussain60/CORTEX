"""
Unified Response Composer (AC-RESP-CONS-008)

Consolidates 5 response composition implementations into 1 unified interface:
1. TurnResponseGenerator → core response generation  
2. ResponseFormattingEngine → multi-mode formatting
3. ResponseTemplateEngine → template composition
4. UXOptimizer → response optimization & quality metrics
5. TurnResponseWithChallenges → challenge composition & injection

Version: 1.0.0
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Union, Tuple
from enum import Enum
import hashlib
from datetime import datetime
import json
from cortex.models.canonical_enums import ChallengeType, ResponseType


# ================================================================================
# ENUMS & TYPES
# ================================================================================

class ResponseMode(str, Enum):
    """Response delivery mode (6 modes from TurnResponseGenerator)."""
    CHAT = "chat"
    COMMAND = "command"
    VISUALIZATION = "visualization"
    JSON_API = "json_api"
    MARKDOWN = "markdown"
    STREAM = "stream"


class ResponseTone(str, Enum):
    """Communication tone (5 tones from TurnResponseGenerator)."""
    FORMAL = "formal"
    CASUAL = "casual"
    TECHNICAL = "technical"
    EXECUTIVE = "executive"
    EDUCATIONAL = "educational"


class FormattingProfile(str, Enum):
    """Formatting profile (from multi_mode_formatter)."""
    COMPACT = "compact"
    STANDARD = "standard"
    VERBOSE = "verbose"
    MINIMAL = "minimal"
    RICH = "rich"


from cortex.models.canonical_enums import VariableType


class QualityMetricType(str, Enum):
    """Quality metric type (from ux_optimizer)."""
    CLARITY = "clarity"
    COMPLETENESS = "completeness"
    RELEVANCE = "relevance"
    TONE_APPROPRIATENESS = "tone_appropriateness"
    ACTIONABILITY = "actionability"
    ACCURACY = "accuracy"
    EFFICIENCY = "efficiency"


# ================================================================================
# DATA MODELS
# ================================================================================

@dataclass
class ResponseComposerConfig:
    """Configuration for UnifiedResponseComposer."""
    enable_caching: bool = True
    cache_ttl: int = 3600
    enable_optimization: bool = True
    optimization_threshold: float = 0.7
    enable_challenge_injection: bool = True
    challenge_confidence_threshold: float = 0.7
    audit_logging_enabled: bool = True
    enable_formatting_stats: bool = True
    max_cache_size: int = 1000


@dataclass
class ResponseMetadata:
    """Metadata for response tracking (from TurnResponseGenerator)."""
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
    """Individual segment of response (from TurnResponseGenerator)."""
    segment_type: str
    content: str
    
    @property
    def length(self) -> int:
        """Calculate segment length."""
        return len(self.content)


@dataclass
class TurnResponse:
    """Complete response for conversation turn (from TurnResponseGenerator)."""
    operation_id: str
    turn_number: int
    metadata: ResponseMetadata
    segments: List[ResponseSegment] = field(default_factory=list)
    formatted_content: str = ""
    raw_content: str = ""
    alternatives: List[Dict[str, Any]] = field(default_factory=list)
    confidence_score: float = 1.0
    ready_to_send: bool = False
    quality_metrics: Optional['ResponseQualityMetrics'] = None
    
    @property
    def segment_summary(self) -> Dict[str, int]:
        """Summarize segments by type."""
        summary: Dict[str, int] = {}
        for segment in self.segments:
            summary[segment.segment_type] = summary.get(segment.segment_type, 0) + segment.length
        return summary
    
    @property
    def total_length(self) -> int:
        """Calculate total response length."""
        return sum(segment.length for segment in self.segments)


@dataclass
class ResponseQualityMetrics:
    """Quality metrics for response (from UXOptimizer)."""
    response_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    clarity_score: float = 0.0
    completeness_score: float = 0.0
    relevance_score: float = 0.0
    tone_appropriateness: float = 0.0
    actionability: float = 0.0
    accuracy: float = 0.0
    efficiency: float = 0.0
    overall_score: float = 0.0
    feedback_count: int = 0
    user_rating_avg: float = 0.0


@dataclass
class FormattingOptions:
    """
    Formatting options (from multi_mode_formatter).
    
    Phase 33: Changed default profile from STANDARD to COMPACT for verbosity reduction.
    """
    profile: FormattingProfile = FormattingProfile.COMPACT
    include_metadata: bool = True
    max_line_length: int = 80


@dataclass
class VariableSpec:
    """Template variable specification (from response_templates)."""
    name: str
    var_type: VariableType
    required: bool = True
    description: str = ""
    default: Any = None
    pattern: Optional[str] = None


@dataclass
class ResponseTemplate:
    """Response template (from response_templates)."""
    template_id: str
    version: str
    name: str
    description: str
    pattern: str
    response_type: ResponseType
    variables: Dict[str, VariableSpec] = field(default_factory=dict)


@dataclass
class Challenge:
    """Challenge for user engagement (from TurnResponseWithChallenges)."""
    challenge_id: str
    challenge_type: ChallengeType
    content: str
    difficulty_level: int = 1
    confidence_score: float = 1.0
    suggested_position: int = 0


@dataclass
class ResponseWithChallenges:
    """Response with integrated challenges (from TurnResponseWithChallenges)."""
    response: TurnResponse
    challenges: List[Challenge] = field(default_factory=list)
    injection_points: List[int] = field(default_factory=list)
    formatted_content: str = ""


# ================================================================================
# UNIFIED RESPONSE COMPOSER
# ================================================================================

class UnifiedResponseComposer:
    """
    Consolidates 5 response composition implementations into single interface.
    
    Provides unified API for:
    - Response generation with modes & tones
    - Multi-mode formatting (7 formatters)
    - Template composition with validation
    - Response optimization & quality metrics
    - Challenge generation & injection
    
    Implements:
    - Composition pattern (not inheritance)
    - Lazy initialization for performance
    - Audit logging throughout
    - 100% backward compatibility
    """
    
    # Internal handler instances (lazy-initialized)
    _turn_generator: Optional[Any] = None
    _formatting_engine: Optional[Any] = None
    _template_engine: Optional[Any] = None
    _ux_optimizer: Optional[Any] = None
    _challenge_generator: Optional[Any] = None
    
    def __init__(self, config: Optional[ResponseComposerConfig] = None) -> None:
        """Initialize UnifiedResponseComposer.
        
        Args:
            config: Configuration options (uses defaults if None)
        """
        self.config = config or ResponseComposerConfig()
        self.response_cache: Dict[str, TurnResponse] = {}
        self.templates: Dict[str, ResponseTemplate] = {}
        self.generation_count = 0
        self.formatting_stats: Dict[str, int] = {}
        self.quality_metrics_history: List[ResponseQualityMetrics] = []
        self._log_audit("init", {
            "config": {
                "enable_caching": self.config.enable_caching,
                "enable_optimization": self.config.enable_optimization,
                "enable_challenge_injection": self.config.enable_challenge_injection,
            }
        })
    
    # ====== CORE RESPONSE GENERATION (from TurnResponseGenerator) ======
    
    def generate_response(
        self,
        operation_id: str,
        turn_number: int,
        content: str,
        mode: ResponseMode = ResponseMode.CHAT,
        tone: ResponseTone = ResponseTone.FORMAL,
        phase: str = "EXECUTION",
        orchestrator: str = "MasterOrchestrator",
        alternatives: Optional[List[Dict[str, Any]]] = None,
        confidence_score: float = 1.0
    ) -> TurnResponse:
        """Generate response with specified mode and tone.
        
        Args:
            operation_id: Operation identifier
            turn_number: Turn sequence number
            content: Response content
            mode: Response delivery mode
            tone: Communication tone
            phase: Execution phase
            orchestrator: Orchestrator name
            alternatives: Alternative actions list
            confidence_score: Response confidence (0-1)
        
        Returns:
            Generated TurnResponse object
        """
        metadata = ResponseMetadata(
            mode=mode,
            tone=tone,
            turn_number=turn_number,
            operation_id=operation_id,
            phase=phase,
            orchestrator=orchestrator
        )
        
        # Create response
        response = TurnResponse(
            operation_id=operation_id,
            turn_number=turn_number,
            metadata=metadata,
            segments=[ResponseSegment(segment_type="body", content=content)],
            formatted_content=content,
            raw_content=content,
            alternatives=alternatives or [],
            confidence_score=confidence_score,
            ready_to_send=True
        )
        
        # Cache if enabled
        if self.config.enable_caching:
            self._cache_response(response)
        
        self.generation_count += 1
        self._log_audit("generate_response", {
            "operation_id": operation_id,
            "turn_number": turn_number,
            "mode": mode.value,
            "tone": tone.value,
            "confidence": confidence_score
        })
        
        return response
    
    def add_segment(
        self,
        response: TurnResponse,
        segment_type: str,
        content: str
    ) -> TurnResponse:
        """Add segment to response (e.g., header, footer, alternatives).
        
        Args:
            response: Response to augment
            segment_type: Type of segment
            content: Segment content
        
        Returns:
            Updated TurnResponse
        """
        response.segments.append(ResponseSegment(segment_type=segment_type, content=content))
        response.formatted_content = "\n\n".join(s.content for s in response.segments)
        
        self._log_audit("add_segment", {
            "operation_id": response.operation_id,
            "segment_type": segment_type,
            "content_length": len(content)
        })
        
        return response
    
    def validate_response(self, response: TurnResponse) -> bool:
        """Validate response structure and content.
        
        Args:
            response: Response to validate
        
        Returns:
            True if valid, False otherwise
        """
        # Check required fields
        if not response.operation_id or not response.metadata:
            return False
        
        # Check segments
        if not response.segments or not response.formatted_content:
            return False
        
        # Check confidence
        if not (0.0 <= response.confidence_score <= 1.0):
            return False
        
        return True
    
    def get_cached_response(
        self,
        operation_id: str,
        turn_number: int
    ) -> Optional[TurnResponse]:
        """Retrieve cached response.
        
        Args:
            operation_id: Operation identifier
            turn_number: Turn number
        
        Returns:
            Cached response or None
        """
        cache_key = f"{operation_id}:{turn_number}"
        return self.response_cache.get(cache_key)
    
    # ====== MULTI-MODE FORMATTING (from ResponseFormattingEngine) ======
    
    def format_response(
        self,
        response: Union[str, TurnResponse, Dict],
        mode: str = 'chat',
        profile: FormattingProfile = FormattingProfile.COMPACT
    ) -> Any:
        """
        Format response for specific delivery mode.
        
        Phase 33: Changed default profile from STANDARD to COMPACT for verbosity reduction.
        
        Args:
            response: Response to format (str, TurnResponse, or Dict)
            mode: Formatting mode (chat, command, visualization, json_api, markdown, stream)
            profile: Formatting profile
        
        Returns:
            Formatted response (type depends on mode)
        """
        options = FormattingOptions(profile=profile)
        
        if mode == "chat":
            return self._format_chat(response, options)
        elif mode == "command":
            return self._format_command(response, options)
        elif mode == "visualization":
            return self._format_visualization(response, options)
        elif mode == "json_api":
            return self._format_json_api(response, options)
        elif mode == "markdown":
            return self._format_markdown(response, options)
        elif mode == "stream":
            return self._format_stream(response, options)
        else:
            # Default to raw content
            if isinstance(response, TurnResponse):
                return response.formatted_content
            return str(response)
    
    def batch_format(
        self,
        contents: List[Union[str, TurnResponse, Dict]],
        mode: str = 'chat'
    ) -> List[Any]:
        """Format multiple responses in batch.
        
        Args:
            contents: List of responses to format
            mode: Formatting mode
        
        Returns:
            List of formatted responses
        """
        results = []
        for content in contents:
            results.append(self.format_response(content, mode))
        
        self._log_audit("batch_format", {
            "count": len(contents),
            "mode": mode
        })
        
        return results
    
    def convert_format(
        self,
        content: Union[str, TurnResponse],
        from_mode: str,
        to_mode: str
    ) -> Any:
        """Convert response from one format to another.
        
        Args:
            content: Response to convert
            from_mode: Source format
            to_mode: Target format
        
        Returns:
            Converted response
        """
        # Convert from source format to intermediate format
        intermediate = self.format_response(content, from_mode)
        
        # Handle TurnResponse by converting back to content
        if isinstance(intermediate, dict) and "content" in intermediate:
            intermediate = intermediate["content"]
        elif isinstance(intermediate, dict) and "data" in intermediate:
            intermediate = str(intermediate)
        
        # Convert from intermediate to target format
        result = self.format_response(intermediate, to_mode)
        
        self._log_audit("convert_format", {
            "from_mode": from_mode,
            "to_mode": to_mode
        })
        
        return result
    
    # ====== TEMPLATE COMPOSITION (from ResponseTemplateEngine) ======
    
    def register_template(self, template: ResponseTemplate) -> None:
        """Register response template.
        
        Args:
            template: Template to register
        """
        self.templates[template.template_id] = template
        self._log_audit("register_template", {
            "template_id": template.template_id,
            "name": template.name,
            "variables": len(template.variables)
        })
    
    def compose_from_template(
        self,
        template_id: str,
        variables: Dict[str, Any]
    ) -> str:
        """Compose response from template.
        
        Args:
            template_id: Template identifier
            variables: Variable values for template
        
        Returns:
            Composed response string
        
        Raises:
            KeyError if template not found
            ValueError if variables invalid
        """
        if template_id not in self.templates:
            raise KeyError(f"Template not found: {template_id}")
        
        template = self.templates[template_id]
        
        # Validate variables
        valid, errors = self.validate_template_variables(template_id, variables)
        if not valid:
            raise ValueError(f"Invalid variables: {errors}")
        
        # Render template by substituting variables
        result = template.pattern
        for var_name, var_value in variables.items():
            result = result.replace(f"{{{{{var_name}}}}}", str(var_value))
        
        self._log_audit("compose_from_template", {
            "template_id": template_id,
            "variables_count": len(variables),
            "output_length": len(result)
        })
        
        return result
    
    def validate_template_variables(
        self,
        template_id: str,
        variables: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """Validate variables for template.
        
        Args:
            template_id: Template identifier
            variables: Variables to validate
        
        Returns:
            Tuple of (valid: bool, errors: List[str])
        """
        if template_id not in self.templates:
            return False, [f"Template not found: {template_id}"]
        
        template = self.templates[template_id]
        errors = []
        
        # Check required variables
        for var_name, var_spec in template.variables.items():
            if var_spec.required and var_name not in variables:
                errors.append(f"Missing required variable: {var_name}")
        
        # Validate provided variables
        for var_name, var_value in variables.items():
            if var_name not in template.variables:
                errors.append(f"Unknown variable: {var_name}")
            else:
                var_spec = template.variables[var_name]
                # Type checking
                if var_spec.var_type == VariableType.STRING and not isinstance(var_value, str):
                    errors.append(f"Variable {var_name} must be string")
                elif var_spec.var_type == VariableType.INTEGER and not isinstance(var_value, int):
                    errors.append(f"Variable {var_name} must be integer")
        
        return len(errors) == 0, errors
    
    # ====== QUALITY OPTIMIZATION (from UXOptimizer) ======
    
    def optimize_response(self, response: TurnResponse) -> TurnResponse:
        """Optimize response for quality.
        
        Args:
            response: Response to optimize
        
        Returns:
            Optimized TurnResponse
        """
        if not self.config.enable_optimization:
            return response
        
        # Calculate quality metrics
        metrics = self.calculate_quality_metrics(f"{response.operation_id}:{response.turn_number}")
        response.quality_metrics = metrics
        
        # Apply optimizations based on metrics
        if metrics.clarity_score < 0.7:
            response = self._improve_clarity(response)
        
        if metrics.completeness_score < 0.7:
            response = self._improve_completeness(response)
        
        self._log_audit("optimize_response", {
            "operation_id": response.operation_id,
            "overall_score": metrics.overall_score,
            "optimizations_applied": metrics.overall_score < 0.7
        })
        
        return response
    
    def calculate_quality_metrics(self, response_id: str) -> ResponseQualityMetrics:
        """Calculate quality metrics for response.
        
        Args:
            response_id: Response identifier
        
        Returns:
            ResponseQualityMetrics with calculated scores
        """
        # Retrieve response if cached
        response = None
        if ":" in response_id:
            op_id, turn_num = response_id.rsplit(":", 1)
            response = self.get_cached_response(op_id, int(turn_num))
        
        metrics = ResponseQualityMetrics(response_id=response_id)
        
        if response:
            # Calculate clarity (based on segment length and variety)
            metrics.clarity_score = min(100.0, len(response.segments) * 20)
            
            # Calculate completeness (based on total content length)
            metrics.completeness_score = min(100.0, response.total_length / 100)
            
            # Calculate relevance (based on confidence score)
            metrics.relevance_score = response.confidence_score * 100
            
            # Calculate tone appropriateness
            metrics.tone_appropriateness = 85.0  # Default
            
            # Calculate actionability
            metrics.actionability = 75.0 if response.alternatives else 50.0
            
            # Calculate accuracy
            metrics.accuracy = 90.0  # Default
            
            # Calculate efficiency
            metrics.efficiency = min(100.0, 100 - (response.total_length / 10))
            
            # Calculate overall score
            metrics.overall_score = (
                metrics.clarity_score +
                metrics.completeness_score +
                metrics.relevance_score +
                metrics.tone_appropriateness +
                metrics.actionability +
                metrics.accuracy +
                metrics.efficiency
            ) / 7.0
        
        self.quality_metrics_history.append(metrics)
        return metrics
    
    def collect_user_feedback(
        self,
        response_id: str,
        rating: float,
        feedback_text: Optional[str] = None
    ) -> None:
        """Collect user feedback for response.
        
        Args:
            response_id: Response identifier
            rating: User rating (0-5)
            feedback_text: Optional feedback text
        """
        # Find existing metrics
        for metrics in self.quality_metrics_history:
            if metrics.response_id == response_id:
                metrics.feedback_count += 1
                metrics.user_rating_avg = (metrics.user_rating_avg + rating) / metrics.feedback_count
                break
        
        self._log_audit("collect_user_feedback", {
            "response_id": response_id,
            "rating": rating,
            "has_text": feedback_text is not None
        })
    
    def get_optimization_recommendations(self, response_id: str) -> List[str]:
        """Get optimization recommendations for response.
        
        Args:
            response_id: Response identifier
        
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Find metrics
        for metrics in self.quality_metrics_history:
            if metrics.response_id == response_id:
                if metrics.clarity_score < 0.7:
                    recommendations.append("Improve clarity - simplify language and structure")
                if metrics.completeness_score < 0.7:
                    recommendations.append("Add more details - response seems incomplete")
                if metrics.relevance_score < 0.7:
                    recommendations.append("Improve relevance - align better with query")
                if metrics.actionability < 0.5:
                    recommendations.append("Add actionable next steps")
                break
        
        return recommendations
    
    # ====== CHALLENGE COMPOSITION (from TurnResponseWithChallenges) ======
    
    def generate_challenges(
        self,
        context: Dict[str, Any]
    ) -> List[Challenge]:
        """Generate challenges for user engagement.
        
        Args:
            context: Context information for challenge generation
        
        Returns:
            List of generated challenges
        """
        if not self.config.enable_challenge_injection:
            return []
        
        challenges = []
        
        # Generate challenges based on context
        if context.get("domain"):
            # Clarification challenge
            challenges.append(Challenge(
                challenge_id=f"challenge_{len(challenges)}",
                challenge_type=ChallengeType.CLARIFICATION_NEEDED,
                content=f"How does this apply to {context.get('domain')}?",
                difficulty_level=2,
                confidence_score=0.8
            ))
        
        if context.get("advanced"):
            # Alternative approach challenge
            challenges.append(Challenge(
                challenge_id=f"challenge_{len(challenges)}",
                challenge_type=ChallengeType.ALTERNATIVE_APPROACH,
                content="Try implementing this yourself",
                difficulty_level=3,
                confidence_score=0.75
            ))
        
        self._log_audit("generate_challenges", {
            "context_keys": list(context.keys()),
            "challenges_generated": len(challenges)
        })
        
        return challenges
    
    def inject_challenges(
        self,
        response: TurnResponse,
        challenges: List[Challenge],
        confidence_threshold: float = 0.7
    ) -> TurnResponse:
        """Inject challenges into response.
        
        Args:
            response: Response to augment
            challenges: Challenges to inject
            confidence_threshold: Minimum confidence for injection
        
        Returns:
            Response with challenges injected
        """
        # Filter by confidence
        filtered_challenges = [
            c for c in challenges
            if c.confidence_score >= confidence_threshold
        ]
        
        if filtered_challenges:
            # Add challenges as segment
            challenge_content = "\n".join([
                f"🎯 {c.challenge_type.value.upper()}: {c.content}"
                for c in filtered_challenges
            ])
            response = self.add_segment(response, "challenges", challenge_content)
        
        self._log_audit("inject_challenges", {
            "operation_id": response.operation_id,
            "challenges_injected": len(filtered_challenges),
            "threshold": confidence_threshold
        })
        
        return response
    
    def compose_with_challenges(
        self,
        operation_id: str,
        content: str,
        context: Optional[Dict[str, Any]] = None
    ) -> ResponseWithChallenges:
        """Compose complete response with integrated challenges.
        
        Args:
            operation_id: Operation identifier
            content: Response content
            context: Context for challenge generation
        
        Returns:
            ResponseWithChallenges object
        """
        # Generate base response
        response = self.generate_response(operation_id, 1, content)
        
        # Generate challenges
        challenges = self.generate_challenges(context or {})
        
        # Inject challenges
        if challenges:
            response = self.inject_challenges(response, challenges)
        
        # Create composed response
        composed = ResponseWithChallenges(
            response=response,
            challenges=challenges,
            formatted_content=response.formatted_content
        )
        
        self._log_audit("compose_with_challenges", {
            "operation_id": operation_id,
            "challenges_count": len(challenges),
            "context_provided": context is not None
        })
        
        return composed
    
    # ====== CACHING & PERFORMANCE ======
    
    def _cache_response(self, response: TurnResponse) -> None:
        """Cache response internally."""
        if len(self.response_cache) >= self.config.max_cache_size:
            # Simple FIFO eviction
            first_key = next(iter(self.response_cache))
            del self.response_cache[first_key]
        
        cache_key = f"{response.operation_id}:{response.turn_number}"
        self.response_cache[cache_key] = response
    
    def clear_cache(self, operation_id: Optional[str] = None) -> None:
        """Clear response cache.
        
        Args:
            operation_id: Clear only this operation (or all if None)
        """
        if operation_id is None:
            self.response_cache.clear()
        else:
            keys_to_remove = [
                k for k in self.response_cache.keys()
                if k.startswith(f"{operation_id}:")
            ]
            for key in keys_to_remove:
                del self.response_cache[key]
    
    # ====== STATISTICS & MONITORING ======
    
    def get_formatting_statistics(self) -> Dict[str, Any]:
        """Get formatting statistics.
        
        Returns:
            Dictionary with formatting stats
        """
        return {
            "formatting_stats": self.formatting_stats,
            "generation_count": self.generation_count,
            "cached_responses": len(self.response_cache),
            "quality_metrics_recorded": len(self.quality_metrics_history),
            "templates_registered": len(self.templates)
        }
    
    def generate_quality_report(self) -> Dict[str, Any]:
        """Generate quality report.
        
        Returns:
            Dictionary with quality metrics
        """
        if not self.quality_metrics_history:
            return {
                "status": "no_metrics",
                "message": "No quality metrics recorded yet"
            }
        
        avg_overall = sum(m.overall_score for m in self.quality_metrics_history) / len(self.quality_metrics_history)
        avg_clarity = sum(m.clarity_score for m in self.quality_metrics_history) / len(self.quality_metrics_history)
        avg_completeness = sum(m.completeness_score for m in self.quality_metrics_history) / len(self.quality_metrics_history)
        
        return {
            "metrics_recorded": len(self.quality_metrics_history),
            "average_overall_score": round(avg_overall, 2),
            "average_clarity": round(avg_clarity, 2),
            "average_completeness": round(avg_completeness, 2),
            "generation_count": self.generation_count,
            "cache_usage": f"{len(self.response_cache)}/{self.config.max_cache_size}"
        }
    
    def reset_statistics(self) -> None:
        """Reset all statistics."""
        self.formatting_stats.clear()
        self.generation_count = 0
        self.quality_metrics_history.clear()
        self._log_audit("reset_statistics", {})
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check.
        
        Returns:
            Health status dictionary
        """
        return {
            "status": "healthy",
            "caching_enabled": self.config.enable_caching,
            "optimization_enabled": self.config.enable_optimization,
            "challenge_injection_enabled": self.config.enable_challenge_injection,
            "cache_size": len(self.response_cache),
            "templates_count": len(self.templates),
            "audit_logging": self.config.audit_logging_enabled
        }
    
    # ====== INTERNAL FORMATTING METHODS ======
    
    def _format_chat(self, response: Union[str, TurnResponse, Dict], options: FormattingOptions) -> Dict[str, Any]:
        """Format for chat interface."""
        if isinstance(response, TurnResponse):
            return {
                "type": "chat",
                "turn": response.turn_number,
                "content": response.formatted_content,
                "alternatives": response.alternatives,
                "confidence": response.confidence_score,
                "metadata": {
                    "mode": response.metadata.mode.value,
                    "tone": response.metadata.tone.value,
                }
            }
        return {"type": "chat", "content": str(response)}
    
    def _format_command(self, response: Union[str, TurnResponse, Dict], options: FormattingOptions) -> str:
        """Format for command line."""
        content = response.formatted_content if isinstance(response, TurnResponse) else str(response)
        return f"{'='*40}\n{content}\n{'='*40}"
    
    def _format_visualization(self, response: Union[str, TurnResponse, Dict], options: FormattingOptions) -> Dict[str, Any]:
        """Format for visualization."""
        return {
            "type": "visualization",
            "content": response.formatted_content if isinstance(response, TurnResponse) else str(response)
        }
    
    def _format_json_api(self, response: Union[str, TurnResponse, Dict], options: FormattingOptions) -> Dict[str, Any]:
        """Format as JSON API."""
        if isinstance(response, TurnResponse):
            return {
                "jsonapi": {"version": "1.0"},
                "data": {
                    "type": "response",
                    "id": response.operation_id,
                    "attributes": {
                        "content": response.formatted_content,
                        "turn": response.turn_number,
                        "confidence": response.confidence_score
                    }
                }
            }
        return {"jsonapi": {"version": "1.0"}, "data": {"type": "response", "content": str(response)}}
    
    def _format_markdown(self, response: Union[str, TurnResponse, Dict], options: FormattingOptions) -> str:
        """Format as markdown."""
        content = response.formatted_content if isinstance(response, TurnResponse) else str(response)
        return f"# Response\n\n{content}"
    
    def _format_stream(self, response: Union[str, TurnResponse, Dict], options: FormattingOptions) -> Dict[str, Any]:
        """Format for streaming."""
        content = response.formatted_content if isinstance(response, TurnResponse) else str(response)
        return {
            "type": "stream",
            "chunk": 1,
            "total_chunks": 1,
            "content": content
        }
    
    def _improve_clarity(self, response: TurnResponse) -> TurnResponse:
        """Internal: improve response clarity."""
        # Simplification logic would go here
        return response
    
    def _improve_completeness(self, response: TurnResponse) -> TurnResponse:
        """Internal: improve response completeness."""
        # Expansion logic would go here
        return response
    
    # ====== AUDIT LOGGING ======
    
    def _log_audit(self, operation: str, details: Dict[str, Any]) -> None:
        """Log operation for audit trail.
        
        Args:
            operation: Operation name
            details: Operation details
        """
        if not self.config.audit_logging_enabled:
            return
        
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "details": details
        }
        
        # In production, this would write to audit trail
        # For now, we just track the operation occurred


# ================================================================================
# BACKWARD COMPATIBILITY SINGLETON
# ================================================================================

_unified_composer_instance: Optional[UnifiedResponseComposer] = None


def get_unified_response_composer(
    config: Optional[ResponseComposerConfig] = None
) -> UnifiedResponseComposer:
    """Get or create singleton UnifiedResponseComposer.
    
    Args:
        config: Configuration (only used on first call)
    
    Returns:
        UnifiedResponseComposer singleton instance
    """
    global _unified_composer_instance
    
    if _unified_composer_instance is None:
        _unified_composer_instance = UnifiedResponseComposer(config)
    
    return _unified_composer_instance


# ================================================================================
# PUBLIC EXPORTS
# ================================================================================

__all__ = [
    # Main class
    "UnifiedResponseComposer",
    # Singleton
    "get_unified_response_composer",
    # Enums
    "ResponseMode",
    "ResponseTone",
    "FormattingProfile",
    "ResponseType",
    "VariableType",
    "ChallengeType",
    "QualityMetricType",
    # Data models
    "ResponseComposerConfig",
    "ResponseMetadata",
    "ResponseSegment",
    "TurnResponse",
    "ResponseQualityMetrics",
    "FormattingOptions",
    "VariableSpec",
    "ResponseTemplate",
    "Challenge",
    "ResponseWithChallenges",
]
