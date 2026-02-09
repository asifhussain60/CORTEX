"""
Knowledge Synthesis Engine - Compose CORTEX + Company knowledge into instructions

Authority: AC-HYBRID-KNOWLEDGE-004, AC-KNOWLEDGE-SYNTHESIS-001 (Phase 20.5)
Version: 2.0
Date: 2026-02-03

This engine:
1. Retrieves applicable CORTEX best practices
2. Overlays/merges with Company knowledge domains
3. Applies composition rules
4. Generates final instruction sets for Master Orchestrator
5. [Phase 20.5] Creates UnifiedIntelligenceContext for Stage 2 routing

Integration:
- Called by Master Orchestrator during stage 3 (knowledge synthesis)
- [Phase 20.5] Auto-invoked at Stage 2 for unified intelligence
- Returns explicit source attribution (CORTEX + Company layers)
- Supports caching for performance

CORE Governance:
- CORE-008: TDD (tests before implementation)
- CORE-011: Type hints mandatory
- CORE-012: Google-style docstrings
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

# Phase 20.5: Unified Intelligence Context
from cortex.brain.knowledge.unified_intelligence_context import (
    UnifiedIntelligenceContext,
    LENSIntelligence,
    CompanyKnowledge,
    CORTEXKnowledge,
    SynthesisResult,
)

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
        self._cortex_knowledge_cache: Dict[str, Dict[str, Any]] = {}
    
    # =========================================================================
    # PHASE 20.5: UNIFIED INTELLIGENCE CONTEXT SYNTHESIS
    # Authority: AC-KNOWLEDGE-SYNTHESIS-001
    # =========================================================================
    
    def synthesize_unified_context(
        self,
        intent_type: str,
        lens_intelligence: Optional[LENSIntelligence] = None,
        company_knowledge: Optional[CompanyKnowledge] = None,
        file_path: Optional[str] = None,
    ) -> UnifiedIntelligenceContext:
        """
        Synthesize unified intelligence context combining all knowledge sources.
        
        This is the main Phase 20.5 entry point for MasterOrchestrator Stage 2.
        Combines LENS + Company + CORTEX knowledge into single context with:
        - Precedence resolution (Company > CORTEX)
        - Rule citations
        - Violation detection
        - Proactive guidance
        
        Args:
            intent_type: Intent type (IMPLEMENT, FIX, REFACTOR, ANALYZE, etc.)
            lens_intelligence: Optional LENS intelligence from Phase 20
            company_knowledge: Optional company knowledge from Phase 20
            file_path: Optional file path being analyzed
        
        Returns:
            UnifiedIntelligenceContext with all intelligence sources synthesized
        
        Example:
            >>> engine = KnowledgeSynthesisEngine()
            >>> lens = LENSIntelligence(git_analysis={...}, ast_analysis={...}, comment_analysis={...})
            >>> company = CompanyKnowledge(domain_rules={...}, compliance_standards=[...], precedence="OVERRIDE")
            >>> context = engine.synthesize_unified_context("IMPLEMENT", lens, company, "/src/main.py")
            >>> if context.has_violations():
            ...     print("Violations:", context.get_violations())
        
        Authority: AC-KNOWLEDGE-SYNTHESIS-001 (Phase 20.5 Component #2)
        """
        # Use empty defaults if not provided (graceful degradation)
        if lens_intelligence is None:
            lens_intelligence = LENSIntelligence(
                git_analysis={},
                ast_analysis={},
                comment_analysis={}
            )
        
        if company_knowledge is None:
            company_knowledge = CompanyKnowledge(
                domain_rules={},
                compliance_standards=[],
                precedence="OVERRIDE"
            )
        
        # Load CORTEX best practices (45+ YAMLs)
        cortex_best_practices = self._load_cortex_best_practices(intent_type)
        applicable_patterns = self._extract_applicable_patterns(intent_type, cortex_best_practices)
        anti_patterns = self._extract_anti_patterns(cortex_best_practices)
        
        cortex_knowledge = CORTEXKnowledge(
            best_practices=cortex_best_practices,
            applicable_patterns=applicable_patterns,
            anti_patterns=anti_patterns,
            synthesis_metadata={
                "rules_loaded": len(cortex_best_practices),
                "intent_type": intent_type,
                "timestamp": time.time(),
            }
        )
        
        # Resolve precedence conflicts (Company > CORTEX)
        merged_rules = self._resolve_rule_conflicts(
            cortex_best_practices,
            company_knowledge.domain_rules
        )
        
        # Generate citations (rules that will be cited)
        citations = self._generate_citations(merged_rules, intent_type)
        
        # Detect violations (rules violated based on LENS intelligence)
        violations = self._detect_violations(
            merged_rules,
            lens_intelligence,
            company_knowledge
        )
        
        # Generate proactive guidance
        guidance = self._generate_guidance(
            intent_type,
            merged_rules,
            violations,
            lens_intelligence
        )
        
        # Create synthesis result
        synthesis_result = SynthesisResult(
            merged_rules=merged_rules,
            citations=citations,
            violations=violations,
            guidance=guidance
        )
        
        # Create unified context
        return UnifiedIntelligenceContext(
            lens_intelligence=lens_intelligence,
            company_knowledge=company_knowledge,
            cortex_knowledge=cortex_knowledge,
            synthesis_result=synthesis_result,
            intent_type=intent_type,
            file_path=file_path,
            timestamp=time.time()
        )
    
    def _load_cortex_best_practices(self, intent_type: str) -> Dict[str, Any]:
        """
        Load applicable CORTEX best practices from 45+ YAMLs.
        
        Args:
            intent_type: Intent type to filter applicable practices
        
        Returns:
            Dictionary of best practices keyed by rule ID
        """
        # Check cache first
        cache_key = f"cortex_practices_{intent_type}"
        if cache_key in self._cortex_knowledge_cache:
            return self._cortex_knowledge_cache[cache_key]
        
        practices = {}
        
        try:
            # TODO: Load from cortex_brain/tier3/knowledge/*.yaml
            # For now, return common CORE rules
            practices = {
                "CORE-008": "TDD First - Write tests before implementation",
                "CORE-011": "Type Hints - All functions must have type annotations",
                "CORE-012": "Google-style Docstrings - Document all public methods",
                "CORE-013": "No Bare Except - Always specify exception types",
                "CORE-026": "Git Checkpoint - Commit before major changes",
                "CORE-027": "Audit Trail - Log AC_START and AC_COMPLETE",
                "CORE-029": "Response Header - Include CORTEX header in responses",
                "CORE-030": "Implementation Truth - Verify code, not docs",
                "CORE-035": "Single Implementation - One canonical implementation",
                "CORE-036": "Industry Standards - Comply with 12-Factor, SOLID, Clean Code, OWASP",
            }
            
            # Filter by intent type (all CORE rules apply to all intents for now)
            # In full implementation, load YAMLs and filter by intent
            
            self._cortex_knowledge_cache[cache_key] = practices
            
        except Exception as e:
            logger.error(f"Failed to load CORTEX best practices: {e}")
        
        return practices
    
    def _extract_applicable_patterns(
        self,
        intent_type: str,
        best_practices: Dict[str, Any]
    ) -> List[str]:
        """
        Extract applicable patterns for intent type.
        
        Args:
            intent_type: Intent type
            best_practices: Best practices dict
        
        Returns:
            List of applicable pattern names
        """
        patterns = []
        
        # Intent-specific patterns
        if intent_type == "IMPLEMENT":
            patterns = ["Repository Pattern", "Factory Pattern", "TDD Pattern"]
        elif intent_type == "FIX":
            patterns = ["Root Cause Analysis", "Defensive Programming"]
        elif intent_type == "REFACTOR":
            patterns = ["Extract Method", "Introduce Parameter Object", "Replace Conditional with Polymorphism"]
        elif intent_type == "ANALYZE":
            patterns = ["Code Metrics", "Dependency Analysis", "Complexity Analysis"]
        
        return patterns
    
    def _extract_anti_patterns(self, best_practices: Dict[str, Any]) -> List[str]:
        """
        Extract anti-patterns to avoid.
        
        Args:
            best_practices: Best practices dict
        
        Returns:
            List of anti-pattern names
        """
        return [
            "God Object",
            "Spaghetti Code",
            "Copy-Paste Programming",
            "Magic Numbers",
            "Premature Optimization",
        ]
    
    def _resolve_rule_conflicts(
        self,
        cortex_rules: Dict[str, Any],
        company_rules: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Resolve conflicts between CORTEX and company rules.
        
        Company rules have OVERRIDE precedence.
        
        Args:
            cortex_rules: CORTEX best practices
            company_rules: Company domain rules
        
        Returns:
            Merged rules with conflicts resolved
        """
        merged = cortex_rules.copy()
        
        # Company rules override CORTEX rules
        for rule_key, rule_value in company_rules.items():
            if rule_key in merged:
                logger.info(f"Company rule overrides CORTEX rule: {rule_key}")
            merged[rule_key] = rule_value
        
        return merged
    
    def _generate_citations(
        self,
        merged_rules: Dict[str, Any],
        intent_type: str
    ) -> List[str]:
        """
        Generate list of rule IDs to cite in routing decision.
        
        Args:
            merged_rules: Merged ruleset
            intent_type: Intent type
        
        Returns:
            List of rule IDs to cite
        """
        citations = []
        
        # Always cite these CORE rules
        always_cite = ["CORE-008", "CORE-011", "CORE-012"]
        for rule_id in always_cite:
            if rule_id in merged_rules:
                citations.append(rule_id)
        
        # Cite intent-specific rules
        if intent_type == "IMPLEMENT":
            if "CORE-026" in merged_rules:
                citations.append("CORE-026")
        elif intent_type == "FIX":
            if "CORE-013" in merged_rules:
                citations.append("CORE-013")
        
        return citations
    
    def _detect_violations(
        self,
        merged_rules: Dict[str, Any],
        lens_intelligence: LENSIntelligence,
        company_knowledge: CompanyKnowledge
    ) -> List[str]:
        """
        Detect rule violations based on LENS intelligence.
        
        Args:
            merged_rules: Merged ruleset
            lens_intelligence: LENS analysis
            company_knowledge: Company knowledge
        
        Returns:
            List of violation strings
        """
        violations = []
        
        # Check complexity violations
        ast_analysis = lens_intelligence.ast_analysis
        if ast_analysis.get("complexity", 0) > 20:
            violations.append("CORTEX: High complexity detected (>20), refactoring recommended")
        
        # Check TODO/FIXME violations
        comment_analysis = lens_intelligence.comment_analysis
        if comment_analysis.get("fixmes", 0) > 5:
            violations.append("CORTEX: Excessive FIXMEs detected (>5), technical debt accumulating")
        
        # Check compliance violations
        if "PCI-DSS" in company_knowledge.compliance_standards:
            # Check if file handles payment data (simplified check)
            if lens_intelligence.git_analysis.get("payment_related", False):
                violations.append("COMPANY: PCI-DSS compliance check required for payment data")
        
        return violations
    
    def _generate_guidance(
        self,
        intent_type: str,
        merged_rules: Dict[str, Any],
        violations: List[str],
        lens_intelligence: LENSIntelligence
    ) -> List[str]:
        """
        Generate proactive guidance for engineer.
        
        Args:
            intent_type: Intent type
            merged_rules: Merged ruleset
            violations: Detected violations
            lens_intelligence: LENS intelligence
        
        Returns:
            List of guidance strings
        """
        guidance = []
        
        # Intent-specific guidance
        if intent_type == "IMPLEMENT":
            if "CORE-008" in merged_rules:
                guidance.append("Start with TDD: Write test first, then implement")
            if "CORE-011" in merged_rules:
                guidance.append("Add type hints to all function signatures")
        
        # Violation-based guidance
        if violations:
            guidance.append(f"Address {len(violations)} violation(s) before proceeding")
        
        # LENS-based guidance
        complexity = lens_intelligence.ast_analysis.get("complexity", 0)
        if complexity > 15:
            guidance.append(f"Consider refactoring to reduce complexity (current: {complexity})")
        
        return guidance

    # =========================================================================
    # ORIGINAL METHODS (Phase 1)
    # =========================================================================

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

    def calculate_coverage(
        self,
        intent: str,
        loaded_yamls: List[str],
    ) -> float:
        """
        Calculate knowledge base coverage for intent.

        Measures percentage of applicable patterns/rules available in knowledge
        base for given intent. Returns 0.0-1.0 where 1.0 = complete coverage.

        Args:
            intent: Intent type (IMPLEMENT, FIX, REFACTOR, etc.)
            loaded_yamls: Knowledge YAML files already loaded

        Returns:
            Coverage percentage (0.0-1.0), 1.0 = 100% coverage
        
        Authority: Phase 54 S2 - Gap-filling enhancement
        """
        try:
            # Load all applicable patterns for intent
            cortex_practices = self._load_cortex_best_practices(intent)
            applicable_patterns = self._extract_applicable_patterns(intent, cortex_practices)

            if not applicable_patterns:
                logger.warning(f"No applicable patterns found for intent: {intent}")
                return 0.0

            # Extract covered tech from loaded YAMLs
            loaded_tech = set()
            for yaml_path in loaded_yamls:
                path = Path(yaml_path)
                stem = path.stem
                if stem and stem not in ["index", "readme", "config"]:
                    loaded_tech.add(stem)

            # Extract tech from patterns
            pattern_tech = set()
            for pattern in applicable_patterns:
                # Heuristic: extract tech from pattern description/sources
                if hasattr(pattern, 'keywords'):
                    pattern_tech.update(pattern.keywords)
                if hasattr(pattern, 'domain'):
                    pattern_tech.add(pattern.domain.lower())

            if not pattern_tech:
                # No identifiable tech in patterns, assume covered
                return 1.0

            # Calculate coverage as intersection / union
            covered = len(loaded_tech & pattern_tech)
            total = len(pattern_tech)

            coverage = covered / total if total > 0 else 1.0
            logger.info(
                f"AC_PHASE54-S2-001: Coverage calculated | "
                f"Intent={intent} | Coverage={coverage:.2%} | "
                f"Covered={covered}/{total}"
            )

            return max(0.0, min(1.0, coverage))  # Clamp to [0.0, 1.0]

        except Exception as e:
            logger.error(f"Failed to calculate coverage: {e}", exc_info=True)
            return 0.5  # Return mid-range on failure

    def fill_gaps(
        self,
        coverage: float,
        intent: str,
        threshold: float = 0.8,
    ) -> List[str]:
        """
        Identify missing YAMLs to reach coverage threshold.

        Analyzes knowledge base gaps and recommends which YAML files should be
        created/loaded to reach desired coverage level. Follows layered approach:
        Company > Domain > CORTEX.

        Args:
            coverage: Current coverage (0.0-1.0) from calculate_coverage()
            intent: Intent type (IMPLEMENT, FIX, REFACTOR, etc.)
            threshold: Target coverage threshold (default 0.8 = 80%)

        Returns:
            List of recommended YAML file paths to fill gaps
        
        Authority: Phase 54 S2 - Gap-filling enhancement
        """
        try:
            if coverage >= threshold:
                logger.info(
                    f"AC_PHASE54-S2-002: Coverage adequate | "
                    f"Current={coverage:.2%} >= Target={threshold:.2%}"
                )
                return []

            # Load all CORTEX best practices
            cortex_practices = self._load_cortex_best_practices(intent)
            applicable_patterns = self._extract_applicable_patterns(intent, cortex_practices)

            # Extract tech from patterns
            pattern_tech = set()
            for pattern in applicable_patterns:
                if hasattr(pattern, 'keywords'):
                    pattern_tech.update(pattern.keywords)
                if hasattr(pattern, 'domain'):
                    pattern_tech.add(pattern.domain.lower())

            # Recommended YAMLs (layered precedence)
            recommendations = []

            # Layer 1: Company domains (highest priority)
            for tech in sorted(pattern_tech):
                recommendations.append(f"company/domains/{tech}/best-practices.yaml")

            # Layer 2: Domain-specific CORTEX
            for tech in sorted(pattern_tech):
                recommendations.append(f"cortex/knowledge/domains/{tech}/{tech}-best-practices.yaml")

            # Layer 3: CORTEX generic
            for tech in sorted(pattern_tech):
                recommendations.append(f"cortex/knowledge/{tech}.yaml")

            logger.info(
                f"AC_PHASE54-S2-003: Gap-filling recommendations | "
                f"Intent={intent} | Current={coverage:.2%} | "
                f"Target={threshold:.2%} | Recommended={len(recommendations)} files"
            )

            return recommendations

        except Exception as e:
            logger.error(f"Failed to fill gaps: {e}", exc_info=True)
            return []

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
