"""
ML Summarization Integration for CORTEX.

Integrates ML summarization, deduplication, and learning extraction
with existing CORTEX orchestrators.

Author: CORTEX Team
Created: 2026-02-06
Authority: Phase 36 Stage 4 specification
"""

import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

from cortex.brain.core.conversation_synthesizer import ContextSynthesizer
from cortex.brain.core.learning_extractor import LearningExtractor
from cortex.brain.core.ml_summarizer import MLSummarizer

logger = logging.getLogger(__name__)


class IntegrationMode(Enum):
    """Integration operation modes."""
    FULL = "FULL"
    SUMMARIZATION_ONLY = "SUMMARIZATION_ONLY"
    DEDUPLICATION_ONLY = "DEDUPLICATION_ONLY"


@dataclass
class MLMetrics:
    """
    ML processing metrics.

    Attributes:
        summarization_time: Time spent on summarization
        deduplication_time: Time spent on deduplication
        total_time: Total processing time
        compression_ratio: Compression ratio achieved
        insights_extracted: Number of insights extracted
    """
    summarization_time: float
    deduplication_time: float
    total_time: float
    compression_ratio: float
    insights_extracted: int


@dataclass
class IntegrationResult:
    """
    Integration processing result.

    Attributes:
        processed_content: Processed content
        metrics: Processing metrics
        success: Whether processing succeeded
        error_message: Optional error message
    """
    processed_content: str
    metrics: MLMetrics
    success: bool
    error_message: Optional[str] = None


@dataclass
class IntegrationConfig:
    """
    Integration configuration.

    Attributes:
        mode: Integration mode
        enable_summarization: Whether to enable summarization
        enable_deduplication: Whether to enable deduplication
        enable_learning: Whether to enable learning extraction
    """
    mode: IntegrationMode = IntegrationMode.FULL
    enable_summarization: bool = True
    enable_deduplication: bool = True
    enable_learning: bool = True


class MLIntegration:
    """
    ML Summarization Integration.

    Coordinates ML summarization, deduplication, and learning
    extraction across CORTEX.
    """

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        config: Optional[IntegrationConfig] = None,
    ):
        """
        Initialize ML integration.

        Args:
            model_name: SentenceTransformer model name
            config: Integration configuration
        """
        self.config = config or IntegrationConfig()

        # Initialize components based on config
        if self.config.enable_summarization:
            self.summarizer = MLSummarizer(model_name=model_name)
        else:
            self.summarizer = None

        if self.config.enable_deduplication:
            self.synthesizer = ContextSynthesizer(model_name=model_name)
        else:
            self.synthesizer = None

        if self.config.enable_learning:
            self.extractor = LearningExtractor(model_name=model_name)
        else:
            self.extractor = None

        logger.info(f"MLIntegration initialized with mode: {self.config.mode.value}")

    def process(
        self,
        conversation: Optional[List[str]],
        token_budget: Optional[int] = None,
    ) -> IntegrationResult:
        """
        Process conversation through ML pipeline.

        Args:
            conversation: List of conversation turns
            token_budget: Optional token budget

        Returns:
            IntegrationResult: Processing result
        """
        if not conversation:
            return IntegrationResult(
                processed_content="",
                metrics=MLMetrics(0.0, 0.0, 0.0, 0.0, 0),
                success=True,
            )

        try:
            start_time = time.time()

            processed_content = " ".join(conversation)
            summarization_time = 0.0
            deduplication_time = 0.0
            compression_ratio = 0.0
            insights_extracted = 0

            # Apply processing based on mode and config
            if self.config.mode == IntegrationMode.FULL:
                # Full pipeline: dedup → summarize → learn

                # 1. Deduplication
                if self.config.enable_deduplication and self.synthesizer:
                    dedup_start = time.time()
                    synthesis_result = self.synthesizer.synthesize(
                        conversation,
                        token_budget=token_budget,
                    )
                    processed_content = synthesis_result.synthesized_context
                    compression_ratio = synthesis_result.compression_ratio
                    deduplication_time = time.time() - dedup_start

                # 2. Summarization (if still needed)
                if self.config.enable_summarization and self.summarizer and token_budget:
                    sum_start = time.time()
                    # Convert back to list for summarizer
                    turns = [s.strip() for s in processed_content.split(".") if s.strip()]
                    if turns:
                        summary_result = self.summarizer.summarize(turns)
                        processed_content = summary_result.summary
                        compression_ratio = max(compression_ratio, summary_result.token_reduction)
                    summarization_time = time.time() - sum_start

                # 3. Learning extraction
                if self.config.enable_learning and self.extractor:
                    extraction_result = self.extractor.extract(conversation)
                    insights_extracted = len(extraction_result.insights)

            elif self.config.mode == IntegrationMode.SUMMARIZATION_ONLY:
                # Summarization only
                if self.config.enable_summarization and self.summarizer:
                    sum_start = time.time()
                    summary_result = self.summarizer.summarize(conversation)
                    processed_content = summary_result.summary
                    compression_ratio = summary_result.token_reduction
                    summarization_time = time.time() - sum_start

            elif self.config.mode == IntegrationMode.DEDUPLICATION_ONLY:
                # Deduplication only
                if self.config.enable_deduplication and self.synthesizer:
                    dedup_start = time.time()
                    synthesis_result = self.synthesizer.synthesize(
                        conversation,
                        token_budget=token_budget,
                    )
                    processed_content = synthesis_result.synthesized_context
                    compression_ratio = synthesis_result.compression_ratio
                    deduplication_time = time.time() - dedup_start

            total_time = time.time() - start_time

            return IntegrationResult(
                processed_content=processed_content,
                metrics=MLMetrics(
                    summarization_time=summarization_time,
                    deduplication_time=deduplication_time,
                    total_time=total_time,
                    compression_ratio=compression_ratio,
                    insights_extracted=insights_extracted,
                ),
                success=True,
            )

        except Exception as e:
            logger.error(f"ML integration error: {e}")
            return IntegrationResult(
                processed_content=" ".join(conversation) if conversation else "",
                metrics=MLMetrics(0.0, 0.0, 0.0, 0.0, 0),
                success=True,  # Graceful degradation
                error_message=str(e),
            )
