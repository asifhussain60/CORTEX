"""
KSE engine — KnowledgeSynthesisEngine class + factory.

Phase 103-g: extracted from knowledge_synthesis_engine.py (1,567L) god-object.
"""
from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

from cortex.intelligence.knowledge.unified_intelligence_context import (
    CompanyKnowledge,
    CORTEXKnowledge,
    LENSIntelligence,
    SynthesisResult,
    UnifiedIntelligenceContext,
)
from cortex.intelligence.knowledge.knowledge_synthesis_engine.models import (
    KnowledgeSource,
    SynthesizedInstruction,
)
from cortex.intelligence.knowledge.knowledge_synthesis_engine.loaders import (
    load_cortex_best_practices,
    KNOWLEDGE_INDEX_PATH,
)
from cortex.intelligence.knowledge.knowledge_synthesis_engine.synthesizers import (
    extract_applicable_patterns,
    extract_anti_patterns,
    resolve_rule_conflicts,
    generate_citations,
    detect_violations,
    generate_guidance,
)

logger = logging.getLogger(__name__)


class KnowledgeSynthesisEngine:
    """Composes CORTEX + Company knowledge into final instructions."""

    # GAP-57-01: canonical path constant
    KNOWLEDGE_INDEX_PATH: str = KNOWLEDGE_INDEX_PATH

    def __init__(self) -> None:
        self._cache: Dict[str, SynthesizedInstruction] = {}
        # Phase 65 S1: (timestamp, practices) tuple
        self._cortex_knowledge_cache: Dict[str, Tuple[float, Dict[str, Any]]] = {}

    # =========================================================================
    # PHASE 20.5: UNIFIED INTELLIGENCE CONTEXT SYNTHESIS
    # =========================================================================

    def synthesize_unified_context(
        self,
        intent_type: str,
        lens_intelligence: Optional[LENSIntelligence] = None,
        company_knowledge: Optional[CompanyKnowledge] = None,
        file_path: Optional[str] = None,
    ) -> UnifiedIntelligenceContext:
        """Synthesize unified intelligence context combining all knowledge sources."""
        if lens_intelligence is None:
            lens_intelligence = LENSIntelligence(
                git_analysis={},
                ast_analysis={},
                comment_analysis={},
            )
        if company_knowledge is None:
            company_knowledge = CompanyKnowledge(
                domain_rules={},
                compliance_standards=[],
                precedence="OVERRIDE",
            )

        cortex_best_practices = self._load_cortex_best_practices(intent_type)
        applicable_patterns = extract_applicable_patterns(intent_type, cortex_best_practices)
        anti_patterns = extract_anti_patterns(cortex_best_practices)

        cortex_knowledge = CORTEXKnowledge(
            best_practices=cortex_best_practices,
            applicable_patterns=applicable_patterns,
            anti_patterns=anti_patterns,
            synthesis_metadata={
                "rules_loaded": len(cortex_best_practices),
                "intent_type": intent_type,
                "timestamp": time.time(),
            },
        )

        merged_rules = resolve_rule_conflicts(cortex_best_practices, company_knowledge.domain_rules)
        citations = generate_citations(merged_rules, intent_type)
        violations = detect_violations(merged_rules, lens_intelligence, company_knowledge)
        proactive_guidance = generate_guidance(intent_type, merged_rules, violations, lens_intelligence)

        synthesis_result = SynthesisResult(
            merged_rules=merged_rules,
            citations=citations,
            violations=violations,
            guidance=proactive_guidance,
        )

        return UnifiedIntelligenceContext(
            lens_intelligence=lens_intelligence,
            company_knowledge=company_knowledge,
            cortex_knowledge=cortex_knowledge,
            synthesis_result=synthesis_result,
            intent_type=intent_type,
            file_path=file_path,
            timestamp=time.time(),
        )

    # =========================================================================
    # INTERNAL — delegate to loaders module
    # =========================================================================

    def _load_cortex_best_practices(self, intent_type: str) -> Dict[str, Any]:
        """Load applicable CORTEX best practices (cached 5-min TTL).

        GAP-117-02 (Phase 117-a): pass self._cortex_knowledge_cache to loader
        so the signature matches load_cortex_best_practices(intent_type, cache, …).
        Previously called with only intent_type → TypeError swallowed silently
        → empty best_practices on every synthesize() call.
        """
        practices = load_cortex_best_practices(intent_type, self._cortex_knowledge_cache)
        return practices

    # =========================================================================
    # ORIGINAL PHASE 1 METHOD
    # =========================================================================

    def synthesize_for_intent(
        self,
        intent_type: str,
        company_context: Optional[Dict[str, Any]] = None,
    ) -> SynthesizedInstruction:
        """Synthesize instructions for a given intent."""
        try:
            from cortex.intelligence.knowledge.hybrid_loader import get_hybrid_loader

            loader = get_hybrid_loader()
            synthesis_rules = loader.get_synthesis_rules()
            applicable_rules = [
                r for r in synthesis_rules.values()
                if intent_type in r.applicable_intents
            ]

            if not applicable_rules:
                logger.warning(f"No synthesis rules found for intent: {intent_type}")
                return SynthesizedInstruction(
                    instruction="", sources=[], synthesis_confidence=0.0
                )

            sources: List[KnowledgeSource] = []
            instruction_parts: List[str] = []
            confidence_sum = 0.0

            for rule in applicable_rules:
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
                    confidence_sum += 0.9

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
                            confidence_sum += 0.7

            avg_confidence = confidence_sum / len(applicable_rules) if applicable_rules else 0.0
            instruction = " + ".join(instruction_parts) if instruction_parts else ""

            return SynthesizedInstruction(
                instruction=instruction,
                sources=sources,
                synthesis_confidence=avg_confidence,
                composition_rules_applied=[r.id for r in applicable_rules],
            )

        except Exception as exc:
            logger.error(f"Failed to synthesize instructions: {exc}")
            return SynthesizedInstruction(
                instruction="", sources=[], synthesis_confidence=0.0
            )

    def calculate_coverage(self, intent: str, loaded_yamls: List[str]) -> float:
        """Calculate knowledge base coverage for intent (0.0–1.0)."""
        try:
            cortex_practices = self._load_cortex_best_practices(intent)
            applicable_patterns = extract_applicable_patterns(intent, cortex_practices)

            if not applicable_patterns:
                return 0.0

            loaded_tech = {Path(y).stem for y in loaded_yamls
                           if Path(y).stem not in ("index", "readme", "config")}

            pattern_tech: set = set()
            for pattern in applicable_patterns:
                if hasattr(pattern, "keywords"):
                    pattern_tech.update(pattern.keywords)
                if hasattr(pattern, "domain"):
                    pattern_tech.add(pattern.domain.lower())

            if not pattern_tech:
                return 1.0

            covered = len(loaded_tech & pattern_tech)
            total = len(pattern_tech)
            return max(0.0, min(1.0, covered / total if total > 0 else 1.0))
        except Exception as exc:
            logger.error(f"Failed to calculate coverage: {exc}", exc_info=True)
            return 0.5

    def fill_gaps(self, coverage: float, intent: str, threshold: float = 0.8) -> List[str]:
        """Identify missing YAMLs to reach coverage threshold."""
        try:
            if coverage >= threshold:
                return []

            cortex_practices = self._load_cortex_best_practices(intent)
            applicable_patterns = extract_applicable_patterns(intent, cortex_practices)

            pattern_tech: set = set()
            for pattern in applicable_patterns:
                if hasattr(pattern, "keywords"):
                    pattern_tech.update(pattern.keywords)
                if hasattr(pattern, "domain"):
                    pattern_tech.add(pattern.domain.lower())

            recommendations: List[str] = []
            for tech in sorted(pattern_tech):
                recommendations.append(f"cortex-registry/company/domains/{tech}/best-practices.yaml")
            for tech in sorted(pattern_tech):
                recommendations.append(f"cortex/knowledge/domains/{tech}/{tech}-best-practices.yaml")
            for tech in sorted(pattern_tech):
                recommendations.append(f"cortex/knowledge/{tech}.yaml")

            return recommendations
        except Exception as exc:
            logger.error(f"Failed to fill gaps: {exc}", exc_info=True)
            return []

    def get_for_operation(
        self,
        operation_id: str,
        intent_type: str,
        company_context: Optional[Dict[str, Any]] = None,
    ) -> SynthesizedInstruction:
        """Get synthesized instructions with operation-level caching."""
        cache_key = f"{operation_id}:{intent_type}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        result = self.synthesize_for_intent(intent_type, company_context)
        self._cache[cache_key] = result
        return result

    # =========================================================================
    # PHASE 18 SUB-PHASE C: CROSS-DOMAIN SYNTHESIS
    # =========================================================================

    def synthesize_cross_domain_context(
        self, intent: str, context: str
    ) -> Dict[str, List[str]]:
        """Synthesize cross-domain knowledge from patterns, security, and testing YAMLs."""
        architecture: List[str] = []
        security: List[str] = []
        testing: List[str] = []

        registry_root = Path(__file__).parents[5] / "cortex-registry"

        # Architecture
        patterns_dir = registry_root / "patterns"
        if patterns_dir.exists():
            for p in sorted(patterns_dir.glob("*.yaml")):
                try:
                    raw = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
                    pattern_block = raw.get("pattern", {})
                    name = pattern_block.get("name", p.stem)
                    description = pattern_block.get("description", "")
                    when_to_use: List[str] = pattern_block.get("when_to_use", [])
                    if when_to_use:
                        architecture.append(f"{name}: {when_to_use[0]}")
                    elif description:
                        architecture.append(f"{name}: {description.strip().splitlines()[0]}")
                except Exception as exc:
                    logger.warning("Failed to parse pattern %s: %s", p.name, exc)

        if not architecture:
            architecture = [
                "Use Mediator pattern for orchestration (avoid direct module coupling)",
                "Apply Factory pattern for object creation (single responsibility)",
                "Use Strategy pattern for pluggable algorithms",
            ]

        # Security
        security_dir = registry_root / "knowledge-base" / "security"
        if security_dir.exists():
            for p in sorted(security_dir.glob("*.yaml")):
                try:
                    raw = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
                    for category, items in raw.get("standards", {}).items():
                        if isinstance(items, list):
                            for item in items[:2]:
                                security.append(f"[{category}] {item}")
                except Exception as exc:
                    logger.warning("Failed to parse security YAML %s: %s", p.name, exc)

        if not security:
            security = [
                "[authentication] Use OAuth 2.0 with PKCE for all auth flows",
                "[data-protection] Encrypt sensitive data at rest (AES-256)",
                "[authorization] Apply principle of least privilege (RBAC)",
            ]

        testing = [
            "CORE-008: TDD mandatory — write failing test (RED) before implementation",
            "CORE-064: Sweep Completeness — every FIX/REFACTOR exhausts its full issue catalogue",
            "Use pytest-xdist with -n auto for parallel test execution (CORTEX standard)",
            "Golden tests (tests/golden/) assert end-to-end truthfulness — add one per new feature",
        ]

        return {"architecture": architecture, "security": security, "testing": testing}

    def _load_architecture_patterns(self, intent: str) -> List[str]:
        """Load architecture recommendations from registry YAML."""
        registry_root = Path(__file__).parents[5] / "cortex-registry"
        arch_yaml = registry_root / "knowledge-base" / "architecture" / "architecture-best-practices.yaml"
        recommendations: List[str] = []

        if arch_yaml.exists():
            try:
                raw = yaml.safe_load(arch_yaml.read_text(encoding="utf-8")) or {}
                guidance = raw.get("guidance", {})
                key_map = {"IMPLEMENT": "implement_intents", "DESIGN": "design_intents", "REFACTOR": "refactor_intents"}
                guidance_key = key_map.get(intent.upper())
                if guidance_key and guidance.get(guidance_key):
                    recommendations = list(guidance[guidance_key])
                if not recommendations:
                    for pattern in raw.get("patterns", []):
                        name = pattern.get("name", "")
                        desc = str(pattern.get("description", "")).strip().splitlines()[0] if pattern.get("description") else ""
                        if name:
                            recommendations.append(f"{name}: {desc}" if desc else name)
            except Exception as exc:
                logger.warning("Failed to load architecture best-practices YAML: %s", exc)

        if not recommendations:
            recommendations = [
                "Apply Hexagonal Architecture (Ports & Adapters) to isolate domain logic",
                "Use Domain-Driven Design bounded contexts to contain new features",
                "Prefer Event-Driven Architecture for cross-service integration",
            ]
        return recommendations

    # =========================================================================
    # PHASE 83-e: URS INSTRUCTION OUTCOME TRACKING
    # =========================================================================

    def track_instruction_outcome(self, instruction_id: str, outcome: str) -> None:
        """Track the outcome of a synthesized instruction for URS feedback."""
        from cortex.intelligence.learning.reinforcement_signal import (
            ReinforcementEngine,
            SignalType,
        )

        signal_type = SignalType.MILD_REWARD if outcome == "used" else SignalType.NEUTRAL
        try:
            if not hasattr(self, "_urs_engine") or self._urs_engine is None:
                self._urs_engine = ReinforcementEngine()
            self._urs_engine.emit_signal(
                signal_type=signal_type,
                pattern_id=instruction_id,
                source_orchestrator="KnowledgeSynthesisEngine",
                context={"outcome": outcome},
            )
        except Exception as exc:
            logger.debug("KnSynth.track_instruction_outcome: non-fatal — %s", exc)

    # =========================================================================
    # PHASE 107 SUB-PHASE B: Absorbed tier3 SynthesisEngine capabilities
    # =========================================================================

    def synthesize_from_sources(
        self,
        query: str,
        sources: List[Dict[str, Any]],
        strategy: str = "merge",
    ) -> Any:
        """Synthesize knowledge from multiple sources to answer a query."""
        from cortex.intelligence.tier3.knowledge.synthesis_engine import KnowledgeSynthesisResult

        if not sources:
            return KnowledgeSynthesisResult(
                query=query, sources=[], synthesized_content="No sources available.", confidence=0.0
            )

        contents = [str(s.get("content", s.get("description", ""))) for s in sources]
        if strategy == "merge":
            content = "\n\n".join(c for c in contents if c)
        elif strategy == "first":
            content = contents[0] if contents else ""
        else:
            content = "\n".join(f"- {c}" for c in contents if c)

        return KnowledgeSynthesisResult(
            query=query,
            sources=sources,
            synthesized_content=content,
            confidence=min(1.0, 0.5 + len(sources) * 0.1),
        )

    def detect_source_conflicts(
        self, sources: List[Dict[str, Any]], sweep_id: Optional[str] = None
    ) -> List[str]:
        """Detect conflicting information across knowledge sources."""
        if len(sources) < 2:
            return []

        conflicts: List[str] = []
        contents = [(s.get("id", str(i)), str(s.get("content", ""))) for i, s in enumerate(sources)]
        _NEGATION_MARKERS = ("not", "deprecated", "instead", "replaced", "conflicts", "incorrect")
        seen: set = set()

        for i, (id_a, ca) in enumerate(contents):
            for j, (id_b, cb) in enumerate(contents):
                if i >= j:
                    continue
                key = f"{id_a}:{id_b}"
                if key in seen:
                    continue
                seen.add(key)
                wa, wb = set(ca.lower().split()), set(cb.lower().split())
                common = wa & wb
                if common and any(m in wa or m in wb for m in _NEGATION_MARKERS):
                    conflicts.append(
                        f"Conflict between '{id_a}' and '{id_b}': "
                        f"shared topic words {list(common)[:5]!r} with opposing signals."
                    )

        if conflicts and sweep_id:
            self._submit_source_conflicts_to_sweep(sweep_id=sweep_id, conflicts=conflicts)
        return conflicts

    def _submit_source_conflicts_to_sweep(self, sweep_id: str, conflicts: List[str]) -> None:
        try:
            from cortex.orchestrators.support.sweep_catalogue_orchestrator import SweepCatalogueOrchestrator
            catalogue = SweepCatalogueOrchestrator()
            for conflict in conflicts:
                catalogue.add_issue(sweep_id=sweep_id, file="KnowledgeSynthesisEngine", description=conflict)
        except Exception:
            pass


# ─── Singleton accessor ───────────────────────────────────────────────────────

_engine: Optional[KnowledgeSynthesisEngine] = None


def get_synthesis_engine() -> KnowledgeSynthesisEngine:
    """Get knowledge synthesis engine singleton instance."""
    global _engine
    if _engine is None:
        _engine = KnowledgeSynthesisEngine()
    return _engine
