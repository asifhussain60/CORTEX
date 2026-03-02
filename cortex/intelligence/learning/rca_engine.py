"""
Phase 87 — RCA Engine
Dispatches root cause analysis across four methodologies: Five-Whys, Fishbone,
Fault-Tree, and Causal-Chain.  Generates an initial PreventionRule (ADVISORY by
default) for every completed RCAAnalysis.

CORE-011: Type hints on all functions
CORE-012: Docstrings on all public APIs
CORE-028: snake_case filename
CORE-035: Single canonical implementation
"""

from __future__ import annotations

import uuid
from typing import Dict, List, Optional

from cortex.intelligence.learning.rca_models import (
    GateLevel,
    PreventionRule,
    RCAAnalysis,
    RCACategory,
    RCATemplate,
)

# ---------------------------------------------------------------------------
# Category → default methodology mapping
# ---------------------------------------------------------------------------
_CATEGORY_METHODOLOGY_MAP: Dict[RCACategory, RCATemplate] = {
    RCACategory.TECHNOLOGY: RCATemplate.FIVE_WHYS,
    RCACategory.PROCESS: RCATemplate.FISHBONE,
    RCACategory.PEOPLE: RCATemplate.FISHBONE,
    RCACategory.DATA: RCATemplate.CAUSAL_CHAIN,
}

# Fishbone cause categories (Ishikawa standard set)
_FISHBONE_CATEGORIES: List[str] = [
    "Method",
    "Machine",
    "Material",
    "Measurement",
    "Man",
    "Environment",
]


class RCAEngine:
    """Orchestrates root cause analysis across four structured methodologies.

    Responsibilities:
    - Auto-select the best methodology given a failure category.
    - Dispatch to the appropriate analysis routine.
    - Generate an initial PreventionRule for each completed RCAAnalysis.
    - Return a fully populated RCAAnalysis dataclass ready for persistence.
    """

    # ------------------------------------------------------------------
    # Methodology selection
    # ------------------------------------------------------------------

    def select_methodology(self, category: RCACategory) -> RCATemplate:
        """Return the default RCATemplate for the given failure category.

        Args:
            category: The high-level failure category.

        Returns:
            The recommended RCATemplate for that category.
        """
        return _CATEGORY_METHODOLOGY_MAP.get(category, RCATemplate.FIVE_WHYS)

    # ------------------------------------------------------------------
    # Top-level dispatcher
    # ------------------------------------------------------------------

    def analyze(
        self,
        failure_id: str,
        symptom: str,
        category: RCACategory,
        methodology: Optional[RCATemplate] = None,
    ) -> RCAAnalysis:
        """Run RCA with the given (or auto-selected) methodology.

        Args:
            failure_id: Unique identifier of the originating failure event.
            symptom: Human-readable description of the failure symptom.
            category: High-level failure category driving methodology selection.
            methodology: Explicit methodology override; None for auto-selection.

        Returns:
            A fully populated RCAAnalysis dataclass.
        """
        chosen = methodology if methodology is not None else self.select_methodology(category)

        if chosen == RCATemplate.FIVE_WHYS:
            return self.analyze_five_whys(failure_id=failure_id, symptom=symptom, category=category)
        if chosen == RCATemplate.FISHBONE:
            return self.analyze_fishbone(failure_id=failure_id, symptom=symptom, category=category)
        if chosen == RCATemplate.FAULT_TREE:
            return self._analyze_fault_tree(failure_id=failure_id, symptom=symptom, category=category)
        # CAUSAL_CHAIN
        return self._analyze_causal_chain(failure_id=failure_id, symptom=symptom, category=category)

    # ------------------------------------------------------------------
    # Five-Whys
    # ------------------------------------------------------------------

    def analyze_five_whys(
        self,
        failure_id: str,
        symptom: str,
        category: RCACategory,
    ) -> RCAAnalysis:
        """Perform a Five-Whys analysis and return a structured RCAAnalysis.

        Generates a sequential chain of why-questions derived from the symptom,
        estimating the root cause as the deepest level reached.

        Args:
            failure_id: Unique identifier of the originating failure event.
            symptom: Human-readable description of the observed failure.
            category: Failure category (used to populate the RCAAnalysis).

        Returns:
            RCAAnalysis with methodology=FIVE_WHYS and analysis_data['whys'] populated.
        """
        whys = self._generate_why_chain(symptom, depth=5)
        root_cause = whys[-1]["answer"] if whys else f"Undetermined root cause for: {symptom}"
        confidence = min(0.5 + len(whys) * 0.08, 0.92)

        rca = RCAAnalysis(
            id=self._new_id(),
            failure_id=failure_id,
            methodology=RCATemplate.FIVE_WHYS,
            category=category,
            root_cause=root_cause,
            confidence=confidence,
            analysis_data={"whys": whys, "symptom": symptom},
        )
        rca.prevention_rule = self.generate_prevention_rule(rca)
        return rca

    # ------------------------------------------------------------------
    # Fishbone (Ishikawa)
    # ------------------------------------------------------------------

    def analyze_fishbone(
        self,
        failure_id: str,
        symptom: str,
        category: RCACategory,
    ) -> RCAAnalysis:
        """Perform a Fishbone (Ishikawa) analysis and return an RCAAnalysis.

        Distributes contributing factors across the six standard Ishikawa
        cause categories (Method, Machine, Material, Measurement, Man, Environment).

        Args:
            failure_id: Unique identifier of the originating failure event.
            symptom: Human-readable description of the observed failure.
            category: Failure category (used to populate the RCAAnalysis).

        Returns:
            RCAAnalysis with methodology=FISHBONE and analysis_data['categories'] populated.
        """
        categories: Dict[str, List[str]] = self._generate_fishbone_categories(symptom)
        primary_category = _FISHBONE_CATEGORIES[0]
        factors = categories.get(primary_category, [])
        root_cause = (
            factors[0]
            if factors
            else f"Multiple contributing factors identified for: {symptom}"
        )
        confidence = 0.75

        rca = RCAAnalysis(
            id=self._new_id(),
            failure_id=failure_id,
            methodology=RCATemplate.FISHBONE,
            category=category,
            root_cause=root_cause,
            confidence=confidence,
            analysis_data={"categories": categories, "symptom": symptom},
        )
        rca.prevention_rule = self.generate_prevention_rule(rca)
        return rca

    # ------------------------------------------------------------------
    # Prevention Rule generation
    # ------------------------------------------------------------------

    def generate_prevention_rule(self, rca: RCAAnalysis) -> PreventionRule:
        """Generate an initial PreventionRule for a completed RCAAnalysis.

        The generated rule defaults to ADVISORY gate level.  The gate level
        escalates to WARNING or BLOCKING only after the rule accumulates
        recurrence evidence (handled by PreventionGate and RecurrenceEngine).

        Args:
            rca: The completed RCAAnalysis to derive the rule from.

        Returns:
            A PreventionRule linked to the supplied RCAAnalysis.
        """
        rule_text = self._build_rule_text(rca)
        return PreventionRule(
            id=self._new_id(),
            rca_id=rca.id,
            rule_text=rule_text,
            gate_level=GateLevel.ADVISORY,
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _analyze_fault_tree(
        self,
        failure_id: str,
        symptom: str,
        category: RCACategory,
    ) -> RCAAnalysis:
        """Fault-tree analysis (top-down decomposition of failure events).

        Args:
            failure_id: Unique identifier of the originating failure event.
            symptom: Human-readable description of the observed failure.
            category: Failure category.

        Returns:
            RCAAnalysis with methodology=FAULT_TREE.
        """
        tree = {
            "top_event": symptom,
            "gates": [
                {
                    "type": "OR",
                    "events": [
                        f"Primary path: {symptom} (immediate trigger)",
                        f"Contributing path: environmental factor for {symptom}",
                    ],
                }
            ],
        }
        root_cause = tree["gates"][0]["events"][0] if tree["gates"] else symptom
        rca = RCAAnalysis(
            id=self._new_id(),
            failure_id=failure_id,
            methodology=RCATemplate.FAULT_TREE,
            category=category,
            root_cause=root_cause,
            confidence=0.70,
            analysis_data={"tree": tree, "symptom": symptom},
        )
        rca.prevention_rule = self.generate_prevention_rule(rca)
        return rca

    def _analyze_causal_chain(
        self,
        failure_id: str,
        symptom: str,
        category: RCACategory,
    ) -> RCAAnalysis:
        """Causal-chain analysis (ordered sequence of cause → effect links).

        Args:
            failure_id: Unique identifier of the originating failure event.
            symptom: Human-readable description of the observed failure.
            category: Failure category.

        Returns:
            RCAAnalysis with methodology=CAUSAL_CHAIN.
        """
        chain = [
            {"step": 1, "cause": f"Initial condition enabling {symptom}", "effect": symptom},
            {"step": 2, "cause": "Propagation through dependent component", "effect": "Secondary impact"},
            {"step": 3, "cause": "Missing validation gate", "effect": "Observable failure"},
        ]
        root_cause = chain[0]["cause"] if chain else symptom
        rca = RCAAnalysis(
            id=self._new_id(),
            failure_id=failure_id,
            methodology=RCATemplate.CAUSAL_CHAIN,
            category=category,
            root_cause=root_cause,
            confidence=0.78,
            analysis_data={"chain": chain, "symptom": symptom},
        )
        rca.prevention_rule = self.generate_prevention_rule(rca)
        return rca

    @staticmethod
    def _new_id() -> str:
        """Generate a new unique RCA identifier prefixed with 'RCA-'.

        Returns:
            A string identifier in the form 'RCA-<uuid8>'.
        """
        return f"RCA-{uuid.uuid4().hex[:8].upper()}"

    @staticmethod
    def _generate_why_chain(symptom: str, depth: int = 5) -> List[Dict[str, str]]:
        """Build a synthetic Five-Whys chain from the given symptom.

        In production this delegates to the host LLM via the Orchestration Layer;
        here we produce a deterministic chain suitable for testing and bootstrap.

        Args:
            symptom: The observable failure symptom to probe.
            depth: Number of why iterations to generate (default 5).

        Returns:
            A list of dicts, each with 'why' (question) and 'answer' (response).
        """
        chain: List[Dict[str, str]] = []
        current = symptom
        why_starters = [
            "Why did «{prev}» occur?",
            "Why was «{prev}» not caught earlier?",
            "Why did the system allow «{prev}»?",
            "Why was there no safeguard against «{prev}»?",
            "Why was «{prev}» not addressed in design?",
        ]
        answers = [
            f"Because the upstream component failed silently ({symptom})",
            "Because the validation layer was not enforced at runtime",
            "Because the error boundary was not wired correctly",
            "Because the governance rule was not applied to this path",
            "Because the design did not account for this edge case",
        ]
        for i in range(min(depth, len(why_starters))):
            question = why_starters[i].format(prev=current)
            answer = answers[i]
            chain.append({"why": question, "answer": answer})
            current = answer
        return chain

    @staticmethod
    def _generate_fishbone_categories(symptom: str) -> Dict[str, List[str]]:
        """Distribute failure factors across Ishikawa cause categories.

        Args:
            symptom: The observable failure symptom.

        Returns:
            A dict mapping each Ishikawa category to a list of contributing factors.
        """
        return {
            "Method": [f"Inadequate procedure for handling {symptom}"],
            "Machine": [f"System resource constraint contributing to {symptom}"],
            "Material": [f"Dependency version mismatch linked to {symptom}"],
            "Measurement": [f"Insufficient observability to detect {symptom} early"],
            "Man": [f"Knowledge gap around edge case that triggered {symptom}"],
            "Environment": [f"Configuration drift in environment causing {symptom}"],
        }

    @staticmethod
    def _build_rule_text(rca: RCAAnalysis) -> str:
        """Construct a human-readable prevention rule text from an RCAAnalysis.

        Args:
            rca: The completed RCAAnalysis to derive the rule from.

        Returns:
            A non-empty string describing the prevention rule.
        """
        return (
            f"[{rca.category.value.upper()}] Prevent recurrence of '{rca.root_cause}' "
            f"(methodology: {rca.methodology.value}, confidence: {rca.confidence:.2f}). "
            f"Review and enforce pre-operation checks for failure_id={rca.failure_id}."
        )
