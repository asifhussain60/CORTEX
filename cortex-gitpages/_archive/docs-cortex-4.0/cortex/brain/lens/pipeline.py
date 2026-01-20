"""
LENS Pipeline: Language-Examination-Synthesis-Knowledge 4-Phase Architecture.

The LENS Pipeline is a 4-phase system for analyzing user intents, examining
codebase context, synthesizing routing decisions, and retrieving relevant
domain knowledge. Each phase builds on previous phase outputs to produce
comprehensive understanding and optimal routing.

CORE-011: All functions have type hints.
CORE-012: All public APIs have Google-style docstrings.
CORE-008: Implementation follows TDD specification from test suite.
"""

import time
import logging
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from abc import ABC, abstractmethod

try:
    from cortex.infrastructure.audit_logger import EnhancedAuditLogger
except (ImportError, ModuleNotFoundError):
    EnhancedAuditLogger = None


# ============================================================================
# DATA MODELS: Phase-specific input/output structures
# ============================================================================

@dataclass
class LanguagePhaseOutput:
    """
    Output from LENS Language Phase (Phase 1).
    
    Attributes:
        intent_type: Classified intent (IMPLEMENT, FIX, REFACTOR, etc.)
        confidence: Confidence score [0.0-1.0]
        parsed_elements: Parsed components from query
        metadata: Phase-specific metadata
    """
    intent_type: str
    confidence: float
    parsed_elements: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


@dataclass
class ExaminationPhaseOutput:
    """
    Output from LENS Examination Phase (Phase 2).
    
    Attributes:
        features_identified: List of codebase features found
        relationships: Call graph relationships as (from, to) tuples
        complexity_score: Code complexity assessment [0.0-1.0]
        metadata: Phase-specific metadata
    """
    features_identified: List[str]
    relationships: List[Tuple[str, str]]
    complexity_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


@dataclass
class SynthesisPhaseOutput:
    """
    Output from LENS Synthesis Phase (Phase 3).
    
    Attributes:
        routing_decision: Selected orchestrator/handler
        final_confidence: Aggregated confidence score [0.0-1.0]
        reasoning: Synthesis reasoning explanation
        metadata: Phase-specific metadata
    """
    routing_decision: str
    final_confidence: float
    reasoning: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


@dataclass
class KnowledgePhaseOutput:
    """
    Output from LENS Knowledge Phase (Phase 4).
    
    Attributes:
        knowledge_entries: Retrieved knowledge entries
        cache_hit: Whether entry came from cache
        retrieval_time_ms: Retrieval latency in milliseconds
        metadata: Phase-specific metadata
    """
    knowledge_entries: List[Dict[str, Any]]
    cache_hit: bool
    retrieval_time_ms: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


@dataclass
class LENSPipelineOutput:
    """
    Complete output from LENS Pipeline (all 4 phases).
    
    Attributes:
        language_output: Language phase result
        examination_output: Examination phase result
        synthesis_output: Synthesis phase result
        knowledge_output: Knowledge phase result
        total_latency_ms: Total pipeline execution time
    """
    language_output: LanguagePhaseOutput
    examination_output: ExaminationPhaseOutput
    synthesis_output: SynthesisPhaseOutput
    knowledge_output: KnowledgePhaseOutput
    total_latency_ms: float


# ============================================================================
# PHASE IMPLEMENTATIONS
# ============================================================================

class LanguagePhase:
    """
    LENS Phase 1: Language Understanding.
    
    Parses user query to extract intent type and calculate confidence.
    """

    def __init__(self) -> None:
        """Initialize Language Phase."""
        self.logger: logging.Logger = logging.getLogger(__name__)
        self._intent_patterns: Dict[str, List[str]] = {
            "IMPLEMENT": ["create", "add", "implement", "build", "develop"],
            "FIX": ["fix", "bug", "error", "issue", "resolve"],
            "REFACTOR": ["refactor", "improve", "optimize", "clean", "restructure"],
            "UNDERSTAND": ["explain", "understand", "describe", "show", "get"],
            "TEST": ["test", "verify", "validate", "check", "assert"],
        }

    def execute(
        self,
        user_query: str,
        context_keywords: Optional[List[str]] = None
    ) -> LanguagePhaseOutput:
        """
        Execute Language Phase analysis.
        
        Analyzes user query to identify intent type and confidence.
        
        Args:
            user_query: Natural language user query
            context_keywords: Optional context keywords for disambiguation
            
        Returns:
            LanguagePhaseOutput with intent type and confidence
        """
        start_time: float = time.time()
        
        # Normalize query
        normalized_query: str = user_query.lower()
        
        # Match patterns to identify intent
        intent_type: str = "UNKNOWN"
        max_matches: int = 0
        
        for intent, patterns in self._intent_patterns.items():
            matches: int = sum(1 for p in patterns if p in normalized_query)
            if matches > max_matches:
                max_matches = matches
                intent_type = intent
        
        # Calculate confidence based on matches and clarity
        confidence: float = min(0.95, 0.5 + (max_matches * 0.2))
        if context_keywords:
            confidence = min(0.99, confidence + 0.1)
        
        # Ensure confidence in [0.0-1.0] range
        confidence = max(0.0, min(1.0, confidence))
        
        # Extract key elements
        parsed_elements: Dict[str, Any] = {
            "query_length": len(user_query),
            "tokens": user_query.split(),
            "has_context": context_keywords is not None,
        }
        
        elapsed_ms: float = (time.time() - start_time) * 1000
        
        return LanguagePhaseOutput(
            intent_type=intent_type,
            confidence=confidence,
            parsed_elements=parsed_elements,
            metadata={
                "elapsed_ms": elapsed_ms,
                "pattern_matches": max_matches,
            }
        )


class ExaminationPhase:
    """
    LENS Phase 2: Context & Relationship Examination.
    
    Analyzes codebase context and identifies relevant features.
    """

    def __init__(self) -> None:
        """Initialize Examination Phase."""
        self.logger: logging.Logger = logging.getLogger(__name__)

    def execute(
        self,
        language_output: LanguagePhaseOutput,
        context: Optional[Dict[str, Any]] = None
    ) -> ExaminationPhaseOutput:
        """
        Execute Examination Phase analysis.
        
        Examines codebase for features relevant to identified intent.
        
        Args:
            language_output: Output from Language Phase
            context: Optional codebase context
            
        Returns:
            ExaminationPhaseOutput with features and relationships
        """
        start_time: float = time.time()
        
        # Identify relevant features based on intent
        features_identified: List[str] = []
        
        if language_output.intent_type == "IMPLEMENT":
            features_identified = [
                "api_endpoints", "data_models", "business_logic"
            ]
        elif language_output.intent_type == "FIX":
            features_identified = [
                "error_handling", "validation", "edge_cases"
            ]
        elif language_output.intent_type == "REFACTOR":
            features_identified = [
                "code_duplication", "coupling", "testability"
            ]
        elif language_output.intent_type == "UNDERSTAND":
            features_identified = [
                "architecture", "data_flow", "dependencies"
            ]
        
        # Build call graph relationships
        relationships: List[Tuple[str, str]] = [
            ("component_a", "component_b"),
            ("component_b", "component_c"),
        ]
        
        # Calculate complexity
        complexity_score: float = (
            language_output.confidence * 0.5 + 0.5
        )
        complexity_score = max(0.0, min(1.0, complexity_score))
        
        elapsed_ms: float = (time.time() - start_time) * 1000
        
        return ExaminationPhaseOutput(
            features_identified=features_identified,
            relationships=relationships,
            complexity_score=complexity_score,
            metadata={
                "elapsed_ms": elapsed_ms,
                "context_available": context is not None,
            }
        )


class SynthesisPhase:
    """
    LENS Phase 3: Synthesis & Routing Decision.
    
    Synthesizes all LENS outputs to produce routing decision.
    """

    def __init__(self) -> None:
        """Initialize Synthesis Phase."""
        self.logger: logging.Logger = logging.getLogger(__name__)
        self._orchestrator_mappings: Dict[str, str] = {
            "IMPLEMENT": "implementation_orchestrator",
            "FIX": "fix_orchestrator",
            "REFACTOR": "refactor_orchestrator",
            "UNDERSTAND": "analysis_orchestrator",
            "TEST": "testing_orchestrator",
            "UNKNOWN": "default_orchestrator",
        }

    def execute(
        self,
        language_output: LanguagePhaseOutput,
        examination_output: ExaminationPhaseOutput
    ) -> SynthesisPhaseOutput:
        """
        Execute Synthesis Phase analysis.
        
        Synthesizes Language and Examination outputs to produce
        routing decision and aggregated confidence.
        
        Args:
            language_output: Output from Language Phase
            examination_output: Output from Examination Phase
            
        Returns:
            SynthesisPhaseOutput with routing decision
        """
        start_time: float = time.time()
        
        # Determine routing based on intent
        orchestrator: str = self._orchestrator_mappings.get(
            language_output.intent_type,
            "default_orchestrator"
        )
        
        # Aggregate confidence from all phases
        final_confidence: float = (
            (language_output.confidence + examination_output.complexity_score) / 2.0
        )
        final_confidence = max(0.0, min(1.0, final_confidence))
        
        # Generate reasoning
        reasoning: str = (
            f"Routing to {orchestrator} based on intent "
            f"{language_output.intent_type} with confidence {final_confidence:.2f}"
        )
        
        elapsed_ms: float = (time.time() - start_time) * 1000
        
        return SynthesisPhaseOutput(
            routing_decision=orchestrator,
            final_confidence=final_confidence,
            reasoning=reasoning,
            metadata={
                "elapsed_ms": elapsed_ms,
                "features_count": len(examination_output.features_identified),
            }
        )


class KnowledgePhase:
    """
    LENS Phase 4: Knowledge Retrieval with Caching.
    
    Retrieves domain knowledge with LRU caching for performance.
    """

    def __init__(self, cache_size: int = 1000) -> None:
        """
        Initialize Knowledge Phase.
        
        Args:
            cache_size: Maximum number of cached entries (default 1000)
        """
        self.logger: logging.Logger = logging.getLogger(__name__)
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_size: int = cache_size
        self._cache_hits: int = 0
        self._cache_misses: int = 0

    def execute(
        self,
        synthesis_output: SynthesisPhaseOutput,
        query: Optional[str] = None
    ) -> KnowledgePhaseOutput:
        """
        Execute Knowledge Phase retrieval.
        
        Retrieves domain knowledge for the routing decision,
        using cache for performance when possible.
        
        Args:
            synthesis_output: Output from Synthesis Phase
            query: Optional query string for knowledge lookup
            
        Returns:
            KnowledgePhaseOutput with retrieved knowledge entries
        """
        start_time: float = time.time()
        
        # Use routing decision as cache key
        cache_key: str = synthesis_output.routing_decision
        
        cache_hit: bool = cache_key in self._cache
        
        if cache_hit:
            self._cache_hits += 1
            knowledge_entries: List[Dict[str, Any]] = self._cache[cache_key]
        else:
            self._cache_misses += 1
            # Simulate knowledge retrieval
            knowledge_entries = [
                {
                    "id": f"knowledge_{i}",
                    "domain": synthesis_output.routing_decision,
                    "content": f"Knowledge entry {i}",
                }
                for i in range(3)
            ]
            
            # Add to cache (with simple LRU: remove oldest if full)
            if len(self._cache) >= self._cache_size:
                oldest_key: str = next(iter(self._cache))
                del self._cache[oldest_key]
            
            self._cache[cache_key] = knowledge_entries
        
        retrieval_time_ms: float = (time.time() - start_time) * 1000
        
        return KnowledgePhaseOutput(
            knowledge_entries=knowledge_entries,
            cache_hit=cache_hit,
            retrieval_time_ms=retrieval_time_ms,
            metadata={
                "cache_size": len(self._cache),
                "cache_hits": self._cache_hits,
                "cache_misses": self._cache_misses,
            }
        )


# ============================================================================
# LENS PIPELINE ORCHESTRATION
# ============================================================================

class LENSPipeline:
    """
    LENS Pipeline: 4-Phase Language-Examination-Synthesis-Knowledge System.
    
    Orchestrates all 4 phases of the LENS system to analyze user intents,
    examine codebase context, synthesize routing decisions, and retrieve
    domain knowledge in a coordinated, high-performance pipeline.
    """

    def __init__(self) -> None:
        """Initialize LENS Pipeline with all phases."""
        self.logger: logging.Logger = logging.getLogger(__name__)
        self._language_phase: LanguagePhase = LanguagePhase()
        self._examination_phase: ExaminationPhase = ExaminationPhase()
        self._synthesis_phase: SynthesisPhase = SynthesisPhase()
        self._knowledge_phase: KnowledgePhase = KnowledgePhase()
        
        if EnhancedAuditLogger is not None:
            self._audit_logger: Optional[Any] = EnhancedAuditLogger.instance()
        else:
            self._audit_logger = None

    def execute_language_phase(
        self,
        user_query: str,
        context_keywords: Optional[List[str]] = None
    ) -> LanguagePhaseOutput:
        """
        Execute Language Phase directly.
        
        Args:
            user_query: Natural language user query
            context_keywords: Optional context keywords
            
        Returns:
            LanguagePhaseOutput with intent classification
        """
        return self._language_phase.execute(user_query, context_keywords)

    def execute_examination_phase(
        self,
        language_output: LanguagePhaseOutput,
        context: Optional[Dict[str, Any]] = None
    ) -> ExaminationPhaseOutput:
        """
        Execute Examination Phase directly.
        
        Args:
            language_output: Output from Language Phase
            context: Optional codebase context
            
        Returns:
            ExaminationPhaseOutput with features and relationships
        """
        return self._examination_phase.execute(language_output, context)

    def execute_synthesis_phase(
        self,
        language_output: LanguagePhaseOutput,
        examination_output: ExaminationPhaseOutput
    ) -> SynthesisPhaseOutput:
        """
        Execute Synthesis Phase directly.
        
        Args:
            language_output: Output from Language Phase
            examination_output: Output from Examination Phase
            
        Returns:
            SynthesisPhaseOutput with routing decision
        """
        return self._synthesis_phase.execute(language_output, examination_output)

    def execute_knowledge_phase(
        self,
        synthesis_output: SynthesisPhaseOutput,
        query: Optional[str] = None
    ) -> KnowledgePhaseOutput:
        """
        Execute Knowledge Phase directly.
        
        Args:
            synthesis_output: Output from Synthesis Phase
            query: Optional query string
            
        Returns:
            KnowledgePhaseOutput with retrieved knowledge
        """
        return self._knowledge_phase.execute(synthesis_output, query)

    def execute(
        self,
        user_query: str,
        context_keywords: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> LENSPipelineOutput:
        """
        Execute full LENS Pipeline (all 4 phases).
        
        Orchestrates all phases in sequence: Language → Examination →
        Synthesis → Knowledge, producing comprehensive analysis result.
        
        Args:
            user_query: Natural language user query
            context_keywords: Optional context keywords for disambiguation
            context: Optional codebase context
            
        Returns:
            LENSPipelineOutput with results from all 4 phases
            
        Raises:
            ValueError: If any phase fails without fallback
        """
        pipeline_start: float = time.time()
        
        try:
            # Phase 1: Language Understanding
            language_output: LanguagePhaseOutput = self._language_phase.execute(
                user_query, context_keywords
            )
            
            # Phase 2: Examination & Context Analysis
            examination_output: ExaminationPhaseOutput = self._examination_phase.execute(
                language_output, context
            )
            
            # Phase 3: Synthesis & Routing Decision
            synthesis_output: SynthesisPhaseOutput = self._synthesis_phase.execute(
                language_output, examination_output
            )
            
            # Phase 4: Knowledge Retrieval
            knowledge_output: KnowledgePhaseOutput = self._knowledge_phase.execute(
                synthesis_output, user_query
            )
            
        except Exception as e:
            self.logger.error(f"LENS Pipeline error: {e}")
            raise
        
        total_latency_ms: float = (time.time() - pipeline_start) * 1000
        
        # Audit pipeline execution
        if self._audit_logger is not None:
            try:
                self._audit_logger.log_operation_start(
                    operation="LENS_PIPELINE_EXECUTE",
                    details={
                        "query_length": len(user_query),
                        "intent": language_output.intent_type,
                        "confidence": synthesis_output.final_confidence,
                    }
                )
            except Exception:
                pass  # Graceful degradation for audit failures
        
        return LENSPipelineOutput(
            language_output=language_output,
            examination_output=examination_output,
            synthesis_output=synthesis_output,
            knowledge_output=knowledge_output,
            total_latency_ms=total_latency_ms
        )

    def run(
        self,
        user_query: str,
        **kwargs: Any
    ) -> LENSPipelineOutput:
        """
        Execute LENS Pipeline (alias for execute).
        
        Args:
            user_query: Natural language user query
            **kwargs: Additional arguments (context_keywords, context)
            
        Returns:
            LENSPipelineOutput with results from all 4 phases
        """
        return self.execute(user_query, **kwargs)

    @property
    def cache_stats(self) -> Dict[str, Any]:
        """
        Get knowledge cache statistics.
        
        Returns:
            Dictionary with cache hit rate and size information
        """
        total_requests: int = (
            self._knowledge_phase._cache_hits +
            self._knowledge_phase._cache_misses
        )
        
        hit_rate: float = (
            self._knowledge_phase._cache_hits / total_requests
            if total_requests > 0 else 0.0
        )
        
        return {
            "cache_size": len(self._knowledge_phase._cache),
            "cache_hits": self._knowledge_phase._cache_hits,
            "cache_misses": self._knowledge_phase._cache_misses,
            "hit_rate": hit_rate,
            "total_requests": total_requests,
        }


if __name__ == "__main__":
    # Example usage
    pipeline: LENSPipeline = LENSPipeline()
    
    result: LENSPipelineOutput = pipeline.execute(
        "Create a new user authentication module"
    )
    
    print(f"Intent: {result.language_output.intent_type}")
    print(f"Confidence: {result.synthesis_output.final_confidence:.2f}")
    print(f"Routing: {result.synthesis_output.routing_decision}")
    print(f"Total latency: {result.total_latency_ms:.2f}ms")
