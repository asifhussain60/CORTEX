# AC-ID: KN-003-01 - Knowledge Guidance Engine
"""
Knowledge Guidance Engine for TDD-Aware Module Implementation.

PHASE-REMEDIATION-07: TDD Orchestrator Knowledge Integration
AC-ID: KN-003-01 - Module-Specific Guidance Resolution

This module provides context-aware guidance for module implementation by:
1. Loading tier0/tier1/tier2 governance rules
2. Querying tier3 knowledge synthesis (cross-domain patterns)
3. Resolving domain-specific overrides (company rules > CORTEX rules)
4. Returning precedence-ordered guidance for TDD implementation

Core Responsibilities:
1. Resolve module path to domain context
2. Query applicable governance rules (tier precedence)
3. Load best practices patterns from knowledge registry
4. Synthesize cross-domain guidance from tier3
5. Apply domain overrides (highest precedence)
6. Return guidance with confidence scoring

Integration Points:
- MCP Tool: get_tdd_guidance_for_module (cortex/mcp/tools/knowledge/)
- KnowledgeRepository: Access best practices index
- GovernanceRegistry: Retrieve tier0/tier1/tier2 rules
- DomainBrain: Query tier3 synthesis for cross-domain patterns

CORE Governance:
  - CORE-008: TDD (tests first)
  - CORE-011: Type hints mandatory (100% coverage)
  - CORE-012: Google-style docstrings
  - CORE-013: Specific exception handling
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from cortex.intelligence.explainability.decision_logger import (
    DecisionTraceabilityLogger,
    DecisionType,
    DecisionOutcome,
)

# =============================================================================
# ENUMERATIONS & CONSTANTS
# =============================================================================

class TierLevel(Enum):  # CORE-035-scoped — domain-specific variant
    """Governance tier levels (highest to lowest precedence)."""

    DOMAIN_OVERRIDE = 0    # Company domain-specific (highest precedence)
    TIER_0 = 1             # Core immutable rules
    TIER_1 = 2             # Domain-specific governance
    TIER_2 = 3             # Engineering standards
    CORTEX_BEST_PRACTICES = 4  # CORTEX defaults (lowest precedence)


class GuidanceCategory(Enum):
    """Categories of implementation guidance."""

    TDD_DISCIPLINE = "tdd_discipline"
    TESTING_PATTERNS = "testing_patterns"
    SECURITY_PATTERNS = "security_patterns"
    PERFORMANCE_PATTERNS = "performance_patterns"
    GOVERNANCE_REQUIREMENTS = "governance_requirements"
    DOMAIN_PATTERNS = "domain_patterns"
    ANTI_PATTERNS = "anti_patterns"


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class GuidanceEntry:
    """Single piece of guidance from the knowledge base."""

    category: GuidanceCategory
    title: str
    description: str
    priority: int  # 1=critical, 2=high, 3=medium, 4=low
    tier: TierLevel
    source: str  # e.g., "cortex/knowledge/best-practices/tdd-best-practices.yaml"
    confidence: float = 1.0  # 0.0-1.0
    domain_specific: bool = False
    patterns: List[str] = field(default_factory=list)
    related_rules: List[str] = field(default_factory=list)


@dataclass
class ModuleGuidance:
    """Complete guidance for a module implementation."""

    module_path: str
    module_name: str
    domain: str
    guidance_entries: List[GuidanceEntry] = field(default_factory=list)
    domain_rules: List[str] = field(default_factory=list)
    tier_0_rules: List[str] = field(default_factory=list)
    tier_1_rules: List[str] = field(default_factory=list)
    tier_2_rules: List[str] = field(default_factory=list)
    best_practices_guides: List[str] = field(default_factory=list)
    synthesis_insights: Dict[str, Any] = field(default_factory=dict)
    generated_at: str = ""
    guidance_confidence: float = 1.0


# =============================================================================
# KNOWLEDGE GUIDANCE ENGINE
# =============================================================================

class KnowledgeGuidanceEngine:
    """
    Resolves module-specific implementation guidance from multi-tier knowledge sources.

    Precedence order (highest to lowest):
    1. Domain-specific overrides (company rules)
    2. TIER 0 governance (immutable core rules)
    3. TIER 1 governance (domain-specific)
    4. TIER 2 standards (engineering practices)
    5. CORTEX best practices (default patterns)
    """

    def __init__(
        self,
        knowledge_root: Optional[Path] = None,
        workspace_root: Optional[Path] = None,
    ) -> None:
        """
        Initialize guidance engine.

        Args:
            knowledge_root: Root path to knowledge repository.
                           Defaults to cortex/knowledge/
            workspace_root: Optional override for the registry root (used in tests
                            and when a per-repo ai-standards YAML must be resolved).
                            When provided, company/domains/{repo}-ai-standards.yaml
                            is resolved relative to this path.

        Raises:
            ValueError: If knowledge repository cannot be found
        """
        if knowledge_root is None:
            knowledge_root = Path(__file__).parent.parent / "knowledge"

        if not knowledge_root.exists():
            raise ValueError(f"Knowledge repository not found: {knowledge_root}")

        self.knowledge_root = knowledge_root
        self.best_practices_root = knowledge_root / "best-practices"
        # workspace_root is the registry base (default: two levels above cortex/)
        self._workspace_root: Path = workspace_root or Path(__file__).parent.parent.parent
        self._cache: Dict[str, ModuleGuidance] = {}
        self._decision_logger = DecisionTraceabilityLogger()
        self._load_tier_mappings()

    def _load_tier_mappings(self) -> None:
        """Load tier0/tier1/tier2 mappings from governance repository."""
        self.tier_0_rules: Dict[str, str] = {}
        self.tier_1_rules: Dict[str, Any] = {}
        self.tier_2_rules: Dict[str, Any] = {}

        brain_root = Path(__file__).parent.parent.parent / "cortex-registry"

        # Load TIER 0 rules (cortex-registry/core/tier0-skull/)
        tier0_path = brain_root / "core" / "tier0-skull" / "skull-rules.yaml"
        if tier0_path.exists():
            with open(tier0_path, 'r', encoding='utf-8') as f:
                tier0_content = yaml.safe_load(f) or {}
                self.tier_0_rules = tier0_content.get("rules", {})

        # Load TIER 1 rules from cortex-registry/core/tier1-project/
        tier1_gov = brain_root / "core" / "tier1-project"
        if tier1_gov.exists():
            for yaml_file in tier1_gov.glob("*.yaml"):
                try:
                    with open(yaml_file, 'r', encoding='utf-8') as f:
                        content = yaml.safe_load(f) or {}
                    domain = content.get("domain", yaml_file.stem)
                    for rule in content.get("rules", []):
                        rule_id = rule.get("id", "")
                        if rule_id:
                            self.tier_1_rules[rule_id] = {
                                "name": rule.get("name", rule_id),
                                "description": rule.get("description", ""),
                                "severity": rule.get("severity", "medium"),
                                "domain": domain,
                                "source": str(yaml_file.name),
                            }
                except (IOError, yaml.YAMLError):
                    pass

        # Load TIER 2 rules from cortex-registry/core/
        tier2_gov = brain_root / "core"
        if tier2_gov.exists():
            for yaml_file in tier2_gov.glob("*.yaml"):
                try:
                    with open(yaml_file, 'r', encoding='utf-8') as f:
                        content = yaml.safe_load(f) or {}
                    context = content.get("context", yaml_file.stem)
                    for rule in content.get("rules", []):
                        rule_id = rule.get("id", "")
                        if rule_id:
                            self.tier_2_rules[rule_id] = {
                                "name": rule.get("name", rule_id),
                                "description": rule.get("description", ""),
                                "severity": rule.get("severity", "medium"),
                                "context": context,
                                "source": str(yaml_file.name),
                            }
                except (IOError, yaml.YAMLError):
                    pass

    def get_guidance_for_module(
        self,
        module_path: str,
        context: Optional[Dict[str, Any]] = None,
        repo_name: Optional[str] = None,
    ) -> ModuleGuidance:
        """
        Get comprehensive guidance for module implementation.

        Args:
            module_path: Module path (e.g., "cortex.orchestrators.domain_brain")
            context: Optional execution context with domain, operation type, etc.
            repo_name: Optional repository name — when provided, AI-extracted
                       standards from company/domains/{repo_name}-ai-standards.yaml
                       are loaded at TierLevel.DOMAIN_OVERRIDE precedence.

        Returns:
            ModuleGuidance with all applicable patterns and rules

        Raises:
            ValueError: If module_path is invalid
        """
        if not module_path or not isinstance(module_path, str):
            raise ValueError("module_path must be non-empty string")

        # Check cache
        cache_key = f"{module_path}:{hash(str(context))}:{repo_name or ''}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Extract module info
        module_name = self._extract_module_name(module_path)
        domain = self._detect_domain(module_path, context)

        # Create guidance object
        guidance = ModuleGuidance(
            module_path=module_path,
            module_name=module_name,
            domain=domain,
            generated_at=datetime.now().isoformat()
        )

        # Load guidance from each tier
        self._load_tier_0_guidance(guidance)
        self._load_tier_1_guidance(guidance, domain)
        self._load_tier_2_guidance(guidance, domain)
        self._load_best_practices_guidance(guidance, domain, module_name)
        self._load_domain_overrides(guidance, domain)
        # Phase 121: load AI-extracted standards at DOMAIN_OVERRIDE tier
        self._load_ai_context_overrides(guidance, repo_name)
        self._synthesize_cross_domain_guidance(guidance)

        # Score overall confidence
        guidance.guidance_confidence = self._calculate_confidence(guidance)

        # Phase 143: emit decision traceability record (QW-006)
        self._decision_logger.log_decision(
            decision_type=DecisionType.RESOLUTION,
            context={
                "module_path": module_path,
                "domain": domain,
                "entries_count": len(guidance.guidance_entries),
                "repo_name": repo_name or "",
            },
            outcome=DecisionOutcome.APPROVED,
            rationale=(
                f"Resolved {len(guidance.guidance_entries)} guidance entries "
                f"for {domain}/{module_name}"
            ),
            confidence=guidance.guidance_confidence,
        )

        # Cache result
        self._cache[cache_key] = guidance
        return guidance

    def _extract_module_name(self, module_path: str) -> str:
        """Extract module name from path."""
        parts = module_path.split(".")
        return parts[-1] if parts else module_path

    def _detect_domain(
        self,
        module_path: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Detect domain from module path and context.

        Args:
            module_path: Module path
            context: Optional context with domain info

        Returns:
            Domain name (e.g., "orchestrators", "knowledge", "governance")
        """
        # Check context first
        if context and "domain" in context:
            return context["domain"]

        # Infer from module path
        if "orchestrators" in module_path:
            return "orchestrators"
        elif "knowledge" in module_path or "brain" in module_path:
            return "knowledge"
        elif "governance" in module_path:
            return "governance"
        elif "infrastructure" in module_path:
            return "infrastructure"
        elif "mcp" in module_path:
            return "mcp"
        else:
            return "general"

    def _load_tier_0_guidance(self, guidance: ModuleGuidance) -> None:
        """Load TIER 0 (immutable) governance guidance."""
        # CORE-008: TDD discipline
        if self.tier_0_rules:
            # Handle both dict and list formats for tier_0_rules
            if isinstance(self.tier_0_rules, dict):
                guidance.tier_0_rules = list(self.tier_0_rules.keys())
            elif isinstance(self.tier_0_rules, list):
                guidance.tier_0_rules = self.tier_0_rules
            else:
                guidance.tier_0_rules = []

            guidance.guidance_entries.append(
                GuidanceEntry(
                    category=GuidanceCategory.TDD_DISCIPLINE,
                    title="CORE-008: Test-Driven Development",
                    description="Tests must be written BEFORE implementation code",
                    priority=1,
                    tier=TierLevel.TIER_0,
                    source="cortex-registry/core/tier0-skull/skull-rules.yaml",
                    related_rules=["CORE-008", "CORE-027"]
                )
            )

        # CORE-011: Type hints
        guidance.guidance_entries.append(
            GuidanceEntry(
                category=GuidanceCategory.GOVERNANCE_REQUIREMENTS,
                title="CORE-011: Type Safety",
                description="100% type hints on all parameters and return values",
                priority=1,
                tier=TierLevel.TIER_0,
                source="cortex-registry/core/tier0-skull/skull-rules.yaml",
                related_rules=["CORE-011"]
            )
        )

        # CORE-012: Docstrings
        guidance.guidance_entries.append(
            GuidanceEntry(
                category=GuidanceCategory.GOVERNANCE_REQUIREMENTS,
                title="CORE-012: Documentation",
                description="Google-style docstrings on all public functions/classes",
                priority=1,
                tier=TierLevel.TIER_0,
                source="cortex-registry/core/tier0-skull/skull-rules.yaml",
                related_rules=["CORE-012"]
            )
        )

        # CORE-013: Exception handling
        guidance.guidance_entries.append(
            GuidanceEntry(
                category=GuidanceCategory.GOVERNANCE_REQUIREMENTS,
                title="CORE-013: Exception Handling",
                description="Specific exception handling - NO bare except: clauses",
                priority=1,
                tier=TierLevel.TIER_0,
                source="cortex-registry/core/tier0-skull/skull-rules.yaml",
                related_rules=["CORE-013"]
            )
        )

    def _load_tier_1_guidance(
        self,
        guidance: ModuleGuidance,
        domain: str
    ) -> None:
        """
        Load TIER 1 (domain-specific) governance guidance.

        Tier 1 rules come from ``cortex-registry/core/tier1-project/*.yaml``
        and are filtered by domain relevance.

        Args:
            guidance: Guidance object to populate.
            domain: Domain name for filtering.
        """
        if not self.tier_1_rules:
            guidance.tier_1_rules = []
            return

        matched_rules: List[str] = []
        for rule_id, rule_info in self.tier_1_rules.items():
            rule_domain = rule_info.get("domain", "")
            # Include rules from matching domain or general rules
            if rule_domain == domain or rule_domain == "general" or domain == "general":
                matched_rules.append(rule_id)

        guidance.tier_1_rules = matched_rules

        if matched_rules:
            guidance.guidance_entries.append(
                GuidanceEntry(
                    category=GuidanceCategory.GOVERNANCE_REQUIREMENTS,
                    title=f"Tier 1: {domain.title()} Domain Rules",
                    description=(
                        f"{len(matched_rules)} domain-specific governance rules "
                        f"from tier1 ({', '.join(matched_rules[:5])})"
                    ),
                    priority=2,
                    tier=TierLevel.TIER_1,
                    source="cortex-registry/core/tier1-project/",
                    related_rules=matched_rules[:10],
                )
            )

    def _load_tier_2_guidance(
        self,
        guidance: ModuleGuidance,
        domain: str
    ) -> None:
        """
        Load TIER 2 (engineering standards) guidance.

        Tier 2 rules come from ``cortex-registry/core/*.yaml``
        and represent team/project engineering standards.

        Args:
            guidance: Guidance object to populate.
            domain: Domain name for context matching.
        """
        if not self.tier_2_rules:
            guidance.tier_2_rules = []
            return

        matched_rules: List[str] = []
        for rule_id, rule_info in self.tier_2_rules.items():
            rule_context = rule_info.get("context", "")
            # Include rules from matching context or general standards
            if rule_context == domain or rule_context == "development" or domain == "general":
                matched_rules.append(rule_id)

        guidance.tier_2_rules = matched_rules

        if matched_rules:
            guidance.guidance_entries.append(
                GuidanceEntry(
                    category=GuidanceCategory.GOVERNANCE_REQUIREMENTS,
                    title=f"Tier 2: Engineering Standards ({domain.title()})",
                    description=(
                        f"{len(matched_rules)} engineering standard rules "
                        f"from tier2 ({', '.join(matched_rules[:5])})"
                    ),
                    priority=3,
                    tier=TierLevel.TIER_2,
                    source="cortex-registry/core/",
                    related_rules=matched_rules[:10],
                )
            )

    def _load_best_practices_guidance(
        self,
        guidance: ModuleGuidance,
        domain: str,
        module_name: str
    ) -> None:
        """
        Load best practices from cortex-registry/knowledge/.

        Args:
            guidance: Guidance object to populate
            domain: Domain name
            module_name: Module name (for pattern matching)
        """
        if not self.best_practices_root.exists():
            return

        # TDD best practices for all modules
        tdd_guide = self.best_practices_root / "testing" / "tdd-best-practices.yaml"
        if tdd_guide.exists():
            guidance.best_practices_guides.append(str(tdd_guide.relative_to(self.knowledge_root)))
            guidance.guidance_entries.append(
                GuidanceEntry(
                    category=GuidanceCategory.TDD_DISCIPLINE,
                    title="TDD Best Practices",
                    description="Kent Beck methodology: RED → GREEN → REFACTOR",
                    priority=1,
                    tier=TierLevel.CORTEX_BEST_PRACTICES,
                    source="cortex-registry/knowledge/testing/tdd-best-practices.yaml",
                    patterns=["red_phase", "green_phase", "refactor_phase", "test_isolation"]
                )
            )

        # Testing pyramid for all modules
        pyramid_guide = self.best_practices_root / "testing" / "testing-pyramid.yaml"
        if pyramid_guide.exists():
            guidance.best_practices_guides.append(str(pyramid_guide.relative_to(self.knowledge_root)))
            guidance.guidance_entries.append(
                GuidanceEntry(
                    category=GuidanceCategory.TESTING_PATTERNS,
                    title="Testing Pyramid",
                    description="70% unit, 20% integration, 10% E2E tests",
                    priority=2,
                    tier=TierLevel.CORTEX_BEST_PRACTICES,
                    source="cortex/knowledge/best-practices/testing-validation/testing-pyramid.yaml"
                )
            )

        # Domain-specific patterns
        if domain == "orchestrators":
            orchestrator_guide = self.best_practices_root / "architecture" / "ddd-bounded-contexts.yaml"
            if orchestrator_guide.exists():
                guidance.best_practices_guides.append(str(orchestrator_guide.relative_to(self.knowledge_root)))
        elif domain == "governance":
            security_guide = self.best_practices_root / "security" / "secure-coding-practices.yaml"
            if security_guide.exists():
                guidance.best_practices_guides.append(str(security_guide.relative_to(self.knowledge_root)))
                guidance.guidance_entries.append(
                    GuidanceEntry(
                        category=GuidanceCategory.SECURITY_PATTERNS,
                        title="Secure Coding Practices",
                        description="Security-first implementation for governance modules",
                        priority=1,
                        tier=TierLevel.CORTEX_BEST_PRACTICES,
                        source="cortex/knowledge/best-practices/security/secure-coding-practices.yaml"
                    )
                )
        elif domain == "infrastructure":
            perf_guide = self.best_practices_root / "performance-optimization" / "optimization-techniques.yaml"
            if perf_guide.exists():
                guidance.best_practices_guides.append(str(perf_guide.relative_to(self.knowledge_root)))

    def _load_domain_overrides(
        self,
        guidance: ModuleGuidance,
        domain: str
    ) -> None:
        """
        Load domain-specific overrides (highest precedence after tier0).

        Reads from cortex-registry/core/wiring/ for domain-specific policy overrides.

        Args:
            guidance: Guidance object to populate
            domain: Domain name
        """
        domain_override_root = (
            Path(__file__).parent.parent.parent / "cortex-registry" / "core" / "wiring"
        )

        if domain_override_root.exists():
            domain_file = domain_override_root / f"{domain}-policy.yaml"
            if domain_file.exists():
                try:
                    with open(domain_file, 'r', encoding='utf-8') as f:
                        domain_content = yaml.safe_load(f) or {}
                        guidance.domain_rules = domain_content.get("rules", [])
                        guidance.guidance_entries.append(
                            GuidanceEntry(
                                category=GuidanceCategory.DOMAIN_PATTERNS,
                                title=f"{domain.title()} Domain Overrides",
                                description="Policy-specific rules override CORTEX defaults",
                                priority=1,
                                tier=TierLevel.DOMAIN_OVERRIDE,
                                source=f"cortex-registry/core/wiring/{domain}-policy.yaml",
                                domain_specific=True
                            )
                        )
                except (IOError, yaml.YAMLError):
                    pass  # Domain override not available, continue with defaults

    def _load_ai_context_overrides(
        self,
        guidance: ModuleGuidance,
        repo_name: Optional[str],
    ) -> None:
        """
        Load AI-extracted standards as secondary domain overrides (Phase 121).

        Reads ``company/domains/{repo_name}-ai-standards.yaml`` produced by
        ``AIContextDisseminator`` and appends a ``DOMAIN_OVERRIDE`` tier entry
        when found.  Resolution order: hand-authored > AI-extracted > CORTEX defaults.

        Args:
            guidance: Guidance object to populate.
            repo_name: Repository name; if ``None`` or file missing, this is a no-op.
        """
        if not repo_name:
            return
        if self._workspace_root is None:
            return
        ai_standards_path = (
            self._workspace_root / "company" / "domains" / f"{repo_name}-ai-standards.yaml"
        )
        if not ai_standards_path.exists():
            return
        try:
            with open(ai_standards_path, "r", encoding="utf-8") as fh:
                data = yaml.safe_load(fh) or {}
            standards = data.get("standards", {})
            conventions = standards.get("coding_conventions", [])
            if conventions:
                guidance.guidance_entries.append(
                    GuidanceEntry(
                        category=GuidanceCategory.DOMAIN_PATTERNS,
                        title=f"{repo_name.title()} AI-Extracted Standards",
                        description=(
                            "Coding standards extracted from AI instruction files (Phase 121)"
                        ),
                        priority=1,
                        tier=TierLevel.DOMAIN_OVERRIDE,
                        source=f"company/domains/{repo_name}-ai-standards.yaml",
                        domain_specific=True,
                    )
                )
        except (IOError, yaml.YAMLError):
            pass  # AI context file not available — continue with defaults

    def _synthesize_cross_domain_guidance(self, guidance: ModuleGuidance) -> None:
        """
        Synthesize guidance from tier3 knowledge synthesis engine.

        Aggregates cross-domain patterns by examining which domains share
        rules and identifying common governance constraints. Uses data
        from ``cortex/intelligence/knowledge/`` when available.

        Args:
            guidance: Guidance object to populate.
        """
        tier3_knowledge_root = (
            Path(__file__).parent.parent.parent
            / "cortex" / "intelligence" / "knowledge"
        )

        cross_domain_patterns: List[str] = []
        domain_relationships: List[str] = []
        shared_constraints: List[str] = []

        # Scan tier3 knowledge for cross-domain patterns
        if tier3_knowledge_root.exists():
            for yaml_file in tier3_knowledge_root.glob("*.yaml"):
                try:
                    with open(yaml_file, 'r', encoding='utf-8') as f:
                        content = yaml.safe_load(f) or {}
                    # Extract patterns if the YAML has them
                    patterns = content.get("patterns", content.get("cross_domain_patterns", []))
                    if isinstance(patterns, list):
                        for pat in patterns:
                            label = pat.get("name", str(pat)) if isinstance(pat, dict) else str(pat)
                            cross_domain_patterns.append(label)
                    # Extract domain relationships
                    rels = content.get("domain_relationships", [])
                    if isinstance(rels, list):
                        domain_relationships.extend(str(r) for r in rels)
                except (IOError, yaml.YAMLError):
                    pass

        # Derive shared constraints from tier1/tier2 rule overlap
        tier1_ids = set(self.tier_1_rules.keys())
        tier2_ids = set(self.tier_2_rules.keys())
        # Domains that appear in both tiers share constraints
        for rule_id in tier1_ids:
            t1_domain = self.tier_1_rules[rule_id].get("domain", "")
            for t2_id in tier2_ids:
                t2_context = self.tier_2_rules[t2_id].get("context", "")
                if t1_domain and t1_domain == t2_context:
                    shared_constraints.append(
                        f"{t1_domain}: {rule_id} (tier1) ↔ {t2_id} (tier2)"
                    )

        guidance.synthesis_insights = {
            "cross_domain_patterns": cross_domain_patterns[:20],
            "domain_relationships": domain_relationships[:20],
            "shared_constraints": shared_constraints[:20],
        }

        if cross_domain_patterns:
            guidance.guidance_entries.append(
                GuidanceEntry(
                    category=GuidanceCategory.DOMAIN_PATTERNS,
                    title="Cross-Domain Synthesis",
                    description=(
                        f"Found {len(cross_domain_patterns)} cross-domain patterns "
                        f"and {len(shared_constraints)} shared constraints"
                    ),
                    priority=4,
                    tier=TierLevel.CORTEX_BEST_PRACTICES,
                    source="cortex/intelligence/knowledge/",
                    patterns=cross_domain_patterns[:5],
                )
            )

    def _calculate_confidence(self, guidance: ModuleGuidance) -> float:
        """
        Calculate confidence score for guidance quality.

        Factors:
        - Number of applicable rules (more = higher confidence)
        - Coverage of guidance categories (more = higher)
        - Presence of domain overrides (boosts confidence)
        - Tier precedence (tier0 > others)

        Args:
            guidance: Guidance object to score

        Returns:
            Confidence score (0.0-1.0)
        """
        if not guidance.guidance_entries:
            return 0.5

        base_score = 0.7
        entry_bonus = min(len(guidance.guidance_entries) * 0.05, 0.2)
        domain_bonus = 0.05 if guidance.domain_rules else 0.0

        return min(base_score + entry_bonus + domain_bonus, 1.0)

    def get_ordered_guidance(
        self,
        module_path: str,
        context: Optional[Dict[str, Any]] = None
    ) -> List[GuidanceEntry]:
        """
        Get guidance entries in precedence order (tier0 → tier3).

        Args:
            module_path: Module path
            context: Optional execution context

        Returns:
            List of guidance entries sorted by precedence and priority
        """
        guidance = self.get_guidance_for_module(module_path, context)

        # Sort by tier (lower tier value = higher precedence)
        # then by priority (lower value = higher priority)
        return sorted(
            guidance.guidance_entries,
            key=lambda x: (x.tier.value, x.priority)
        )

    def format_guidance_for_display(
        self,
        module_path: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Format guidance as human-readable string for console output.

        Args:
            module_path: Module path
            context: Optional execution context

        Returns:
            Formatted guidance string
        """
        guidance = self.get_guidance_for_module(module_path, context)
        entries = sorted(
            guidance.guidance_entries,
            key=lambda x: (x.tier.value, x.priority)
        )

        lines = [
            f"TDD Implementation Guidance for: {module_path}",
            f"Domain: {guidance.domain}",
            f"Confidence: {guidance.guidance_confidence:.1%}",
            "=" * 80,
            ""
        ]

        for entry in entries:
            lines.append(f"[{entry.tier.name}] {entry.title} (Priority: {entry.priority})")
            lines.append(f"  {entry.description}")
            if entry.related_rules:
                lines.append(f"  Rules: {', '.join(entry.related_rules)}")
            lines.append("")

        return "\n".join(lines)


# =============================================================================
# SINGLETON ACCESS
# =============================================================================

_engine_instance: Optional[KnowledgeGuidanceEngine] = None


def get_guidance_engine(
    knowledge_root: Optional[Path] = None,
    force_reload: bool = False
) -> KnowledgeGuidanceEngine:
    """
    Get or create singleton guidance engine instance.

    Args:
        knowledge_root: Knowledge repository root path
        force_reload: Force reload even if cached

    Returns:
        KnowledgeGuidanceEngine singleton

    Raises:
        ValueError: If knowledge repository cannot be found
    """
    global _engine_instance

    if _engine_instance is None or force_reload:
        _engine_instance = KnowledgeGuidanceEngine(knowledge_root)

    return _engine_instance
