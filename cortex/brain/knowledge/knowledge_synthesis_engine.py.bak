"""
Knowledge Synthesis Engine - Compose CORTEX + Company knowledge into instructions

Authority: AC-HYBRID-KNOWLEDGE-004
Version: 1.0
Date: 2026-01-26

This engine:
1. Retrieves applicable CORTEX best practices
2. Overlays/merges with Company knowledge domains
3. Applies composition rules
4. Generates final instruction sets for Master Orchestrator

Integration:
- Called by Master Orchestrator during stage 3 (knowledge synthesis)
- Returns explicit source attribution (CORTEX + Company layers)
- Supports caching for performance

CORE Governance:
- CORE-008: TDD (tests before implementation)
- CORE-011: Type hints mandatory
- CORE-012: Google-style docstrings
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


# =============================================================================
# Data Models
# =============================================================================

@dataclass
class KnowledgeSource:
    """Attribution for a knowledge source."""
    layer: str  # "CORTEX" or "Company"
    domain: str  # e.g., "TESTING-VALIDATION", "PRODUCT-ENGINEERING"
    priority: Optional[str] = None
    yaml_files: List[str] = field(default_factory=list)


@dataclass
class SynthesizedInstruction:
    """Final synthesized instruction set with source attribution."""
    instruction: str
    sources: List[KnowledgeSource]
    synthesis_confidence: float  # 0.0-1.0
    composition_rules_applied: List[str] = field(default_factory=list)


# =============================================================================
# Knowledge Synthesis Engine
# =============================================================================

class KnowledgeSynthesisEngine:
    """Composes CORTEX + Company knowledge into final instructions."""

    def __init__(self):
        """Initialize synthesis engine."""
        self._cache: Dict[str, SynthesizedInstruction] = {}

    def synthesize_for_intent(
        self,
        intent_type: str,
        company_context: Optional[Dict[str, Any]] = None,
    ) -> SynthesizedInstruction:
        """
        Synthesize instructions for a given intent.

        Args:
            intent_type: Intent type (IMPLEMENT, FIX, REFACTOR, TEST, etc.)
            company_context: Optional company-specific context

        Returns:
            SynthesizedInstruction with explicit source attribution.
        """
        try:
            from cortex.brain.knowledge.hybrid_loader import get_hybrid_loader

            loader = get_hybrid_loader()

            # Get applicable synthesis rules for this intent
            synthesis_rules = loader.get_synthesis_rules()
            applicable_rules = [
                rule for rule in synthesis_rules.values()
                if intent_type in rule.applicable_intents
            ]

            if not applicable_rules:
                logger.warning(f"No synthesis rules found for intent: {intent_type}")
                return SynthesizedInstruction(
                    instruction="",
                    sources=[],
                    synthesis_confidence=0.0,
                )

            # Compose instructions from applicable rules
            sources = []
            instruction_parts = []
            confidence_sum = 0.0

            for rule in applicable_rules:
                # Get CORTEX domain guidance
                cortex_domains = loader.get_cortex_domains()
                if rule.cortex_domain in cortex_domains:
                    domain = cortex_domains[rule.cortex_domain]
                    sources.append(
                        KnowledgeSource(
                            layer="CORTEX",
                            domain=rule.cortex_domain,
                            yaml_files=[domain.path],
                        )
                    )
                    instruction_parts.append(f"CORTEX {rule.cortex_domain}: {domain.description}")
                    confidence_sum += 0.9  # High confidence for CORTEX sources

                # Get Company domain guidance (if applicable)
                if rule.composition in ("overlay", "merge"):
                    company_domains = loader.get_company_domains()
                    for company_domain_name in rule.company_domains:
                        if company_domain_name in company_domains:
                            domain = company_domains[company_domain_name]
                            sources.append(
                                KnowledgeSource(
                                    layer="Company",
                                    domain=company_domain_name,
                                    priority=domain.priority,
                                    yaml_files=[domain.path],
                                )
                            )
                            instruction_parts.append(
                                f"{rule.composition.upper()} {company_domain_name}: {domain.description}"
                            )
                            confidence_sum += 0.7  # Good confidence for company sources

            # Aggregate confidence
            avg_confidence = confidence_sum / len(applicable_rules) if applicable_rules else 0.0

            instruction = " + ".join(instruction_parts) if instruction_parts else ""

            return SynthesizedInstruction(
                instruction=instruction,
                sources=sources,
                synthesis_confidence=avg_confidence,
                composition_rules_applied=[rule.id for rule in applicable_rules],
            )

        except Exception as e:
            logger.error(f"Failed to synthesize instructions: {e}")
            return SynthesizedInstruction(
                instruction="",
                sources=[],
                synthesis_confidence=0.0,
            )

    def get_for_operation(
        self,
        operation_id: str,
        intent_type: str,
        company_context: Optional[Dict[str, Any]] = None,
    ) -> SynthesizedInstruction:
        """
        Get synthesized instructions with caching.

        Args:
            operation_id: Unique operation ID for caching
            intent_type: Intent type
            company_context: Optional company context

        Returns:
            SynthesizedInstruction from cache or newly synthesized.
        """
        cache_key = f"{operation_id}:{intent_type}"

        if cache_key in self._cache:
            logger.debug(f"Synthesized instructions retrieved from cache: {cache_key}")
            return self._cache[cache_key]

        result = self.synthesize_for_intent(intent_type, company_context)
        self._cache[cache_key] = result
        logger.debug(f"Synthesized instructions cached: {cache_key}")
        return result


# Singleton accessor
_engine: Optional[KnowledgeSynthesisEngine] = None


def get_synthesis_engine() -> KnowledgeSynthesisEngine:
    """Get knowledge synthesis engine instance."""
    global _engine
    if _engine is None:
        _engine = KnowledgeSynthesisEngine()
    return _engine
