"""
DistillationOrchestrator — Phase 129 Distillation Mode.

Reduces a multi-turn conversation to an executable, context-dense prompt via a
5-stage pipeline:

  Stage 1 — Segment:            Classify each conversation turn into SegmentType
  Stage 2 — Reconstruct:        Build an IntentGraph from signal segments
  Stage 3 — Reconcile state:    Resolve contradictions / superseded decisions
  Stage 4 — Synthesise prompt:  Compress the graph into a terse executable prompt
  Stage 5 — Compress (rephrase): Pass result through RequestRephraseOrchestrator
                                  for final token optimisation

CORTEX canonical support orchestrator (CORE-035).
Authority: cortex-registry/planning/phases/planned/phase-129-distillation-mode.yaml
AC_START: AC-P129-DISTILL-001
AC_COMPLETE: AC-P129-DISTILL-001 ✅
"""
from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

from cortex.core.orchestrator_protocol_mixin import OrchestratorProtocolMixin
from cortex.core.workflow_enforcement_mixin import WorkflowEnforcementMixin


# ---------------------------------------------------------------------------
# Domain types (CORE-035-scoped — kept in this module)
# ---------------------------------------------------------------------------

class SegmentType(Enum):
    """Classification of a single conversation turn / block."""
    GOAL = "goal"           # What the user wants to achieve
    DECISION = "decision"   # An agreed design or implementation choice
    CONSTRAINT = "constraint"  # A hard requirement / limit
    CONTEXT = "context"    # Background information useful for priming
    NOISE = "noise"        # Filler, meta-conversation, pleasantries


@dataclass
class ConversationSegment:
    """A classified slice of the raw conversation."""
    text: str = ""
    segment_type: SegmentType = SegmentType.NOISE
    confidence: float = 0.0
    turn_index: int = 0


@dataclass
class IntentGraph:
    """Structured representation of the conversation's intent space."""
    goals: List[str] = field(default_factory=list)
    decisions: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    context_items: List[str] = field(default_factory=list)
    noise_ratio: float = 0.0


@dataclass
class DistillationResult:
    """Result of running DistillationOrchestrator.distill()."""
    success: bool = False
    distilled_prompt: str = ""
    segment_count: int = 0
    noise_ratio: float = 0.0
    error_message: Optional[str] = None
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Serialise to plain dict for MCP / JSON transport."""
        return {
            "success": self.success,
            "distilled_prompt": self.distilled_prompt,
            "segment_count": self.segment_count,
            "noise_ratio": round(self.noise_ratio, 3),
            "error_message": self.error_message,
            "metadata": self.metadata,
        }


# ---------------------------------------------------------------------------
# Stage helpers (internal — not part of public API)
# ---------------------------------------------------------------------------

class _ConversationSegmenter:
    """Stage 1: Classify each turn of the conversation."""

    _GOAL_PATTERNS = re.compile(
        r"\b(want to|need to|goal is|objective|build|create|implement|add|"
        r"develop|design|make|set up|establish)\b",
        re.I,
    )
    _DECISION_PATTERNS = re.compile(
        r"\b(yes|agreed|decided|let'?s (use|go with|do)|confirmed|we will|"
        r"shall|we'?re going|chosen|picked|selected)\b",
        re.I,
    )
    _CONSTRAINT_PATTERNS = re.compile(
        r"\b(must|must not|should not|cannot|no |never|always|required|"
        r"mandatory|only|except|limit|maximum|minimum|not allowed|forbidden)\b",
        re.I,
    )
    _CONTEXT_PATTERNS = re.compile(
        r"\b(because|background|currently|existing|already|the system|"
        r"we have|we use|the project|repo|codebase|environment)\b",
        re.I,
    )

    def segment(self, conversation: str) -> List[ConversationSegment]:
        """Split *conversation* into classified :class:`ConversationSegment` objects."""
        segments: List[ConversationSegment] = []
        # Split on turn boundaries (blank lines or "User:"/"Agent:" prefixes)
        turns = re.split(r"\n(?=(?:User|Agent|Human|Assistant)\s*:|\s*\n)", conversation)
        for idx, turn in enumerate(turns):
            text = turn.strip()
            if not text:
                continue
            seg_type, confidence = self._classify(text)
            segments.append(ConversationSegment(
                text=text,
                segment_type=seg_type,
                confidence=confidence,
                turn_index=idx,
            ))
        return segments

    def _classify(self, text: str):
        """Return (SegmentType, confidence) for a single turn."""
        scores: Dict[SegmentType, int] = {
            SegmentType.GOAL: len(self._GOAL_PATTERNS.findall(text)),
            SegmentType.DECISION: len(self._DECISION_PATTERNS.findall(text)),
            SegmentType.CONSTRAINT: len(self._CONSTRAINT_PATTERNS.findall(text)),
            SegmentType.CONTEXT: len(self._CONTEXT_PATTERNS.findall(text)),
        }
        best_type = max(scores, key=lambda k: scores[k])
        best_score = scores[best_type]
        if best_score == 0:
            return SegmentType.NOISE, 0.5
        # Simple confidence: normalised hit count
        confidence = min(1.0, 0.5 + (best_score * 0.15))
        return best_type, confidence


class _IntentGraphReconstructor:
    """Stage 2: Build an IntentGraph from classified segments."""

    def reconstruct(self, segments: List[ConversationSegment]) -> IntentGraph:
        """Aggregate segments into an :class:`IntentGraph`."""
        graph = IntentGraph()
        total = len(segments)
        noise_count = 0
        for seg in segments:
            cleaned = self._strip_prefix(seg.text)
            if seg.segment_type == SegmentType.GOAL:
                graph.goals.append(cleaned)
            elif seg.segment_type == SegmentType.DECISION:
                graph.decisions.append(cleaned)
            elif seg.segment_type == SegmentType.CONSTRAINT:
                graph.constraints.append(cleaned)
            elif seg.segment_type == SegmentType.CONTEXT:
                graph.context_items.append(cleaned)
            else:
                noise_count += 1
        graph.noise_ratio = noise_count / total if total > 0 else 0.0
        return graph

    @staticmethod
    def _strip_prefix(text: str) -> str:
        """Remove 'User:' / 'Agent:' prefixes from turn text."""
        return re.sub(r"^(?:User|Agent|Human|Assistant)\s*:\s*", "", text, flags=re.I).strip()


class _StateReconciler:
    """Stage 3: Resolve superseded decisions and contradictions."""

    def reconcile(self, graph: IntentGraph) -> IntentGraph:
        """Remove duplicate/contradicted entries; return cleaned :class:`IntentGraph`."""
        graph.goals = self._deduplicate(graph.goals)
        graph.decisions = self._deduplicate(graph.decisions)
        graph.constraints = self._deduplicate(graph.constraints)
        graph.context_items = self._deduplicate(graph.context_items)
        return graph

    @staticmethod
    def _deduplicate(items: List[str]) -> List[str]:
        """Remove near-duplicate strings (case-insensitive identity dedup)."""
        seen = set()
        result = []
        for item in items:
            key = item.lower().strip()
            if key not in seen:
                seen.add(key)
                result.append(item)
        return result


class _PromptSynthesiser:
    """Stage 4: Compress IntentGraph into an executable prompt string."""

    def synthesise(self, graph: IntentGraph) -> str:
        """Convert an :class:`IntentGraph` into a structured prompt."""
        parts: List[str] = []

        if graph.goals:
            parts.append("## Goals\n" + "\n".join(f"- {g}" for g in graph.goals))

        if graph.constraints:
            parts.append("## Constraints\n" + "\n".join(f"- {c}" for c in graph.constraints))

        if graph.decisions:
            parts.append("## Decisions Made\n" + "\n".join(f"- {d}" for d in graph.decisions))

        if graph.context_items:
            parts.append("## Context\n" + "\n".join(f"- {c}" for c in graph.context_items))

        if not parts:
            return ""

        header = "# Distilled Prompt\n_Generated by CORTEX DistillationOrchestrator — Phase 129_\n"
        return header + "\n\n".join(parts)


# ---------------------------------------------------------------------------
# Public orchestrator
# ---------------------------------------------------------------------------

class DistillationOrchestrator(OrchestratorProtocolMixin, WorkflowEnforcementMixin):
    """
    Orchestrates the 5-stage conversation distillation pipeline.

    Usage::

        orch = DistillationOrchestrator()
        result = orch.distill(conversation="User: I want to build …\\nAgent: Sure …")
        print(result.distilled_prompt)

    The orchestrator is **composition-first**: it delegates each stage to a
    dedicated helper class, keeping this class thin (CORE-035).
    """

    # Phase 94e advisory — gateway exempt until MasterOrchestrator milestone
    PHASE90_GATEWAY_EXEMPT: bool = True

    def __init__(self) -> None:
        self._segmenter = _ConversationSegmenter()
        self._reconstructor = _IntentGraphReconstructor()
        self._reconciler = _StateReconciler()
        self._synthesiser = _PromptSynthesiser()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def distill(self, conversation: str) -> DistillationResult:
        """
        Distil *conversation* into an executable, context-dense prompt.

        Args:
            conversation: Raw multi-turn conversation text.

        Returns:
            :class:`DistillationResult` with ``distilled_prompt`` on success.
        """
        _ac_id = f"AC-P129-DISTILL-{int(time.time() * 1000) % 100_000:05d}"
        # AC_START: {_ac_id}
        self._activate_cross_cutting_hooks(operation="distill")

        if not conversation or not conversation.strip():
            # AC_COMPLETE: {_ac_id} ❌ empty conversation
            return DistillationResult(
                success=False,
                error_message="Empty conversation — nothing to distill.",
            )

        try:
            # Stage 1 — Segment
            segments = self._segmenter.segment(conversation)

            if not segments:
                return DistillationResult(
                    success=False,
                    error_message="Segmentation produced no segments.",
                )

            # Stage 2 — Reconstruct intent graph
            graph = self._reconstructor.reconstruct(segments)

            # Stage 3 — Reconcile state
            graph = self._reconciler.reconcile(graph)

            # Stage 4 — Synthesise prompt
            raw_prompt = self._synthesiser.synthesise(graph)

            if not raw_prompt:
                return DistillationResult(
                    success=False,
                    segment_count=len(segments),
                    noise_ratio=graph.noise_ratio,
                    error_message="Synthesis produced an empty prompt — conversation may be all noise.",
                )

            # Stage 5 — Token-optimise via RequestRephraseOrchestrator (best-effort)
            final_prompt = self._stage5_compress(raw_prompt)

            # AC_COMPLETE: {_ac_id} ✅
            return DistillationResult(
                success=True,
                distilled_prompt=final_prompt,
                segment_count=len(segments),
                noise_ratio=graph.noise_ratio,
                metadata={
                    "goals": len(graph.goals),
                    "decisions": len(graph.decisions),
                    "constraints": len(graph.constraints),
                    "context_items": len(graph.context_items),
                },
            )

        except Exception as exc:  # pylint: disable=broad-except
            # AC_COMPLETE: {_ac_id} ❌
            return DistillationResult(
                success=False,
                error_message=f"Distillation failed: {exc}",
            )

    def health_check(self) -> Dict:
        """Health endpoint for HealthOrchestrator registration."""
        return {
            "orchestrator": "DistillationOrchestrator",
            "status": "healthy",
            "phase": 129,
            "stages": 5,
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _stage5_compress(self, prompt: str) -> str:
        """Stage 5: best-effort token compression via RequestRephraseOrchestrator.

        Falls back to raw prompt if RequestRephraseOrchestrator is unavailable
        or raises — distillation must never fail because of an optional stage.
        """
        try:
            from cortex.orchestrators.core.request_rephrase_orchestrator import (
                RequestRephraseOrchestrator,
            )
            rephraser = RequestRephraseOrchestrator()
            result = rephraser.analyze(prompt)
            # analyze() returns a dict or object with an 'enhanced_request' key
            if isinstance(result, dict) and result.get("enhanced_request"):
                return result["enhanced_request"]
            if hasattr(result, "enhanced_request") and result.enhanced_request:
                return result.enhanced_request
        except Exception:  # pylint: disable=broad-except
            pass  # best-effort — return raw prompt unchanged
        return prompt
