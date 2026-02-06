"""
Conversation Synthesis Engine for CORTEX.

Provides conversation context tracking, continuity analysis,
and context compression for token budget management.

Author: CORTEX Team
Created: 2026-02-06
Authority: Phase 36 Stage 2 specification
"""

import logging
from typing import List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False
    SentenceTransformer = None  # type: ignore
    cosine_similarity = None  # type: ignore
    np = None  # type: ignore

from cortex.brain.core.ml_summarizer import MLSummarizer

logger = logging.getLogger(__name__)


class ContinuityScore(Enum):
    """Conversation continuity levels."""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass
class ContextWindow:
    """
    Context window for conversation turns.
    
    Attributes:
        turns: List of conversation turns
        start_index: Starting index in full conversation
        end_index: Ending index in full conversation
        token_count: Estimated token count
        summary: Optional window summary
    """
    turns: List[str]
    start_index: int
    end_index: int
    token_count: int
    summary: Optional[str] = None


@dataclass
class SynthesisResult:
    """
    Context synthesis result.
    
    Attributes:
        synthesized_context: Synthesized context text
        continuity_score: Conversation continuity score
        token_count: Total token count
        compression_ratio: Compression ratio (0-1)
        context_windows: Optional list of context windows
    """
    synthesized_context: str
    continuity_score: ContinuityScore
    token_count: int
    compression_ratio: float
    context_windows: Optional[List[ContextWindow]] = None


@dataclass
class CompressionConfig:
    """
    Compression configuration.
    
    Attributes:
        target_ratio: Target compression ratio (0-1)
        min_continuity: Minimum continuity threshold
        preserve_recent: Whether to preserve recent turns
    """
    target_ratio: float = 0.5
    min_continuity: float = 0.6
    preserve_recent: bool = True


@dataclass
class TokenBudget:
    """
    Token budget tracker.
    
    Attributes:
        total_budget: Total token budget
        used_tokens: Tokens already used
    """
    total_budget: int
    used_tokens: int
    
    @property
    def remaining(self) -> int:
        """Calculate remaining tokens."""
        return self.total_budget - self.used_tokens


class ContextSynthesizer:
    """
    Context synthesis engine.
    
    Tracks conversation context, analyzes continuity,
    and compresses context to fit token budgets.
    """
    
    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        config: Optional[CompressionConfig] = None,
    ):
        """
        Initialize context synthesizer.
        
        Args:
            model_name: SentenceTransformer model name
            config: Compression configuration
            
        Raises:
            ImportError: If dependencies not installed
        """
        if not DEPENDENCIES_AVAILABLE:
            raise ImportError(
                "Required dependencies not installed. "
                "Install with: pip install sentence-transformers scikit-learn"
            )
        
        self.model = SentenceTransformer(model_name)
        self.summarizer = MLSummarizer(model_name=model_name)
        self.config = config or CompressionConfig()
        
        logger.info(f"ContextSynthesizer initialized with model: {model_name}")
    
    def synthesize(
        self,
        turns: List[str],
        token_budget: Optional[int] = None,
    ) -> SynthesisResult:
        """
        Synthesize conversation context.
        
        Args:
            turns: List of conversation turns
            token_budget: Optional token budget
            
        Returns:
            SynthesisResult: Synthesis result
        """
        if not turns:
            return SynthesisResult(
                synthesized_context="",
                continuity_score=ContinuityScore.LOW,
                token_count=0,
                compression_ratio=0.0,
            )
        
        # Estimate original token count (words * 1.3)
        original_text = " ".join(turns)
        original_tokens = int(len(original_text.split()) * 1.3)
        
        # Check if compression needed
        if token_budget and original_tokens > token_budget:
            # Compress to fit budget
            target_ratio = min(0.9, token_budget / original_tokens)
            synthesized = self.compress(original_text, target_ratio=target_ratio)
        else:
            synthesized = original_text
        
        # Calculate final token count
        final_tokens = int(len(synthesized.split()) * 1.3)
        
        # Analyze continuity
        continuity = self.analyze_continuity(turns)
        
        # Calculate compression ratio
        compression_ratio = 1 - (final_tokens / max(original_tokens, 1))
        
        return SynthesisResult(
            synthesized_context=synthesized,
            continuity_score=continuity,
            token_count=final_tokens,
            compression_ratio=max(0.0, compression_ratio),
        )
    
    def analyze_continuity(self, turns: List[str]) -> ContinuityScore:
        """
        Analyze conversation continuity.
        
        Args:
            turns: List of conversation turns
            
        Returns:
            ContinuityScore: Continuity level
        """
        if len(turns) < 2:
            return ContinuityScore.LOW
        
        # Generate embeddings
        embeddings = self.model.encode(turns)
        
        # Calculate pairwise similarities between consecutive turns
        similarities = []
        for i in range(len(embeddings) - 1):
            sim = cosine_similarity([embeddings[i]], [embeddings[i + 1]])[0][0]
            similarities.append(float(sim))
        
        # Average similarity indicates continuity
        avg_similarity = sum(similarities) / len(similarities)
        
        if avg_similarity >= 0.7:
            return ContinuityScore.HIGH
        elif avg_similarity >= 0.5:
            return ContinuityScore.MEDIUM
        else:
            return ContinuityScore.LOW
    
    def create_windows(
        self,
        turns: List[str],
        window_size: int = 5,
        overlap: int = 0,
    ) -> List[ContextWindow]:
        """
        Create context windows from conversation turns.
        
        Args:
            turns: List of conversation turns
            window_size: Size of each window
            overlap: Number of overlapping turns
            
        Returns:
            List[ContextWindow]: Context windows
        """
        if not turns:
            return []
        
        windows = []
        stride = max(1, window_size - overlap)
        
        for i in range(0, len(turns), stride):
            end_idx = min(i + window_size, len(turns))
            window_turns = turns[i:end_idx]
            
            # Estimate token count
            window_text = " ".join(window_turns)
            token_count = int(len(window_text.split()) * 1.3)
            
            window = ContextWindow(
                turns=window_turns,
                start_index=i,
                end_index=end_idx,
                token_count=token_count,
            )
            windows.append(window)
            
            if end_idx >= len(turns):
                break
        
        return windows
    
    def compress(
        self,
        context: str,
        target_ratio: float = 0.5,
    ) -> str:
        """
        Compress context text.
        
        Args:
            context: Context text to compress
            target_ratio: Target compression ratio (0-1)
            
        Returns:
            str: Compressed context
        """
        if not context:
            return ""
        
        # Split into sentences
        sentences = [s.strip() for s in context.split(".") if s.strip()]
        
        if len(sentences) <= 1:
            return context
        
        # Use ML summarizer for semantic compression
        summary_result = self.summarizer.summarize(sentences)
        
        # If summary is too long, truncate
        target_length = int(len(context) * target_ratio)
        if len(summary_result.summary) > target_length:
            # Truncate at word boundary
            words = summary_result.summary.split()
            target_words = int(len(words) * target_ratio)
            compressed = " ".join(words[:target_words])
            
            # Add ellipsis if truncated
            if target_words < len(words):
                compressed += "..."
            
            return compressed
        
        return summary_result.summary
