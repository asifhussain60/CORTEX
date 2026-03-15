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

from cortex.core.file_factory import get_file_factory
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
    """Stage 1: Role-aware turn extraction.

    Strategy (accuracy-first, BUG-DISTILL-003/004):
    - **User turns** (asifhussain60 / User / Human): full text → classify for
      GOAL / CONSTRAINT / DECISION.  Nothing truncated.
    - **Copilot turns** (GitHub Copilot / Agent / Assistant): strip all header
      / narration / tool lines; extract only confirmed outcome sentences.
    - Generic turns (no role prefix): keyword-classify as before.
    """

    # Role-prefix detection
    _USER_ROLE = re.compile(
        r"^(asifhussain60|user|human)\s*:",
        re.I,
    )
    _COPILOT_ROLE = re.compile(
        r"^(github copilot|agent|assistant)\s*:",
        re.I,
    )

    # CORTEX response header patterns — strip these lines from Copilot turns
    _HEADER_NOISE = re.compile(
        r"^(#\s*[🧠🛠️]?\s*CORTEX\b"          # # 🧠 CORTEX Building
        r"|>\s*\*[\"\']"                        # > *"quote"*
        r"|\*\*Author:\*\*"                     # **Author:** Asif Hussain
        r"|©\s*20"                              # © 2025
        r"|🧭\s*Orchestration:"                 # 🧭 Orchestration:
        r"|[-─]{3,}"                            # --- separator
        r"|\s*```"                              # code fence
        r"|\s*\|"                               # table row
        r"|Ran terminal command:"               # tool lines
        r"|Read \["
        r"|Searched"
        r"|Created \["
        r"|Made changes\."
        r"|Using \""
        r"|Summarized"
        r"|!\[)"                               # image ref
        ,
        re.M,
    )

    # Outcome lines in Copilot turns that carry real signal
    _OUTCOME_LINE = re.compile(
        r"(✅|❌|committed|pushed|merged|tests? (pass|fail|green|red)"
        r"|phase \w+ complete|all \d+ tests?|rewritten"
        r"|\d+ (pass|fail|error)|AC_COMPLETE|AC_START)",
        re.I,
    )

    # Code / shell lines to strip — these are never signal
    _CODE_LINE = re.compile(
        r"^\s*("
        r"(print|import|from|def |class |if |for |with |try:|except|raise|return)\b"  # Python
        r"|[a-z_][a-z_0-9]*\s*="          # assignment
        r"|\[.*\]$"                         # list literal line
        r"|```"                             # fenced code
        r"|\$\s"                            # shell prompt
        r")",
        re.I,
    )

    # Goal / constraint / decision classifiers for user turns
    _GOAL_RE = re.compile(
        r"\b(want|need|build|create|implement|add|develop|design|make|set up"
        r"|establish|goal|objective|would like|i want|we need|let me|let's build"
        r"|distill|digest|fix|refactor|audit|onboard|plan|sync|rca)\b",
        re.I,
    )
    _CONSTRAINT_RE = re.compile(
        r"\b(must|must not|should not|cannot|never|always|required"
        r"|mandatory|only|except|maximum|minimum|not allowed|forbidden"
        r"|do not|don'?t|no \w+ allowed|ensure|guarantee)\b",
        re.I,
    )
    # Decision: explicit agreement/confirmation by the user — requires deliberate wording
    _DECISION_RE = re.compile(
        r"\b(yes|agreed|confirmed|we will|shall|chosen|picked|selected"
        r"|go with|proceed|let'?s proceed|approve[sd]?)\b",
        re.I,
    )

    # Turn-boundary split — CORTEX and generic chat formats
    _TURN_SPLIT = re.compile(
        r"\n(?=(?:asifhussain60|GitHub Copilot|User|Agent|Human|Assistant)\s*:)",
        re.M,
    )

    def segment(self, conversation: str) -> List[ConversationSegment]:
        """Split *conversation* into classified :class:`ConversationSegment` objects."""
        segments: List[ConversationSegment] = []

        if self._TURN_SPLIT.search(conversation):
            turns = self._TURN_SPLIT.split(conversation)
        else:
            # Generic: split on blank lines
            turns = [t for t in re.split(r"\n{2,}", conversation) if t.strip()]

        for idx, raw_turn in enumerate(turns):
            raw_turn = raw_turn.strip()
            if not raw_turn:
                continue

            if self._USER_ROLE.match(raw_turn):
                # User turn — strip the role label, keep full text, classify
                body = self._USER_ROLE.sub("", raw_turn, count=1).strip()
                if not body:
                    continue
                seg_type, conf = self._classify_user_turn(body)
                segments.append(ConversationSegment(
                    text=body,
                    segment_type=seg_type,
                    confidence=conf,
                    turn_index=idx,
                ))

            elif self._COPILOT_ROLE.match(raw_turn):
                # Copilot turn — extract outcome lines only; skip narration
                body = self._COPILOT_ROLE.sub("", raw_turn, count=1).strip()
                outcome = self._extract_outcomes(body)
                if outcome:
                    segments.append(ConversationSegment(
                        text=outcome,
                        segment_type=SegmentType.DECISION,
                        confidence=0.7,
                        turn_index=idx,
                    ))
                # else: pure narration — silently drop (noise)

            else:
                # Generic turn — legacy keyword classification
                cleaned = self._strip_header_noise(raw_turn).strip()
                if not cleaned:
                    continue
                seg_type, conf = self._classify_user_turn(cleaned)
                segments.append(ConversationSegment(
                    text=cleaned,
                    segment_type=seg_type,
                    confidence=conf,
                    turn_index=idx,
                ))

        return segments

    def _extract_outcomes(self, copilot_body: str) -> str:
        """Return only outcome/result lines from a Copilot response; empty string if none."""
        lines = copilot_body.splitlines()
        outcome_lines = []
        for line in lines:
            # Skip header/noise/code lines
            if self._HEADER_NOISE.match(line.strip()):
                continue
            if self._CODE_LINE.match(line):
                continue
            # Keep outcome lines that signal a confirmed result
            if self._OUTCOME_LINE.search(line):
                outcome_lines.append(line.strip())
        return "\n".join(outcome_lines)

    def _classify_user_turn(self, text: str):
        """Classify a user turn as GOAL / CONSTRAINT / DECISION / CONTEXT.

        Priority (highest first):
          CONSTRAINT — any constraint keyword present
          GOAL       — goal keyword present (even if decision keywords also present)
          DECISION   — explicit agreement with no competing goal keywords
          CONTEXT    — fallback
        """
        g = len(self._GOAL_RE.findall(text))
        c = len(self._CONSTRAINT_RE.findall(text))
        d = len(self._DECISION_RE.findall(text))
        if c > 0:
            return SegmentType.CONSTRAINT, min(1.0, 0.6 + c * 0.1)
        if g > 0:
            return SegmentType.GOAL, min(1.0, 0.6 + g * 0.1)
        if d > 0:
            return SegmentType.DECISION, min(1.0, 0.6 + d * 0.1)
        return SegmentType.CONTEXT, 0.5

    @staticmethod
    def _strip_header_noise(text: str) -> str:
        """Remove CORTEX header, tool-execution, and code lines from generic turns."""
        lines = text.splitlines()
        kept = [
            line for line in lines
            if not re.match(
                r"^\s*(#\s*[🧠🛠️]?\s*CORTEX\b|>\s*\*[\"\']|\*\*Author:\*\*|©\s*20"
                r"|🧭|[-─]{3,}|```|!\[|Ran terminal command:|Read \[|Searched"
                r"|Created \[|Made changes\.|Using \"|Summarized"
                # code / shell lines
                r"|(print|import|from |def |class |if |for |with |try:|except|raise|return)\b"
                r"|[a-z_][a-z_0-9]*\s*="
                r"|\$\s)",
                line,
            )
        ]
        return "\n".join(kept)


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
        """Remove role prefixes from turn text (User:, Agent:, asifhussain60:, etc.)."""
        return re.sub(
            r"^(?:asifhussain60|github copilot|user|agent|human|assistant)\s*:\s*",
            "",
            text,
            flags=re.I,
        ).strip()


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
    """Stage 4: Compress IntentGraph into a dense, token-efficient signal block.

    Format contract (BUG-DISTILL-002/003):
    - No verbose markdown section headers (## Goals, ## Decisions Made, etc.)
    - No preamble / "Generated by" header
    - Inline label prefixes: G: D: C: CTX: — single line per item
    - Full item text preserved — NO truncation (accuracy > compression, BUG-DISTILL-003)
    - Compact, paste-ready as a continuation prompt
    """

    # Prefix tokens for each signal type — short, unambiguous
    _PREFIX = {
        "goal": "G:",
        "decision": "D:",
        "constraint": "C:",
        "context": "CTX:",
    }

    def synthesise(self, graph: IntentGraph) -> str:
        """Convert an :class:`IntentGraph` into a dense signal block."""
        lines: List[str] = []

        for item in graph.goals:
            lines.append(f"{self._PREFIX['goal']} {item.strip()}")
        for item in graph.constraints:
            lines.append(f"{self._PREFIX['constraint']} {item.strip()}")
        for item in graph.decisions:
            lines.append(f"{self._PREFIX['decision']} {item.strip()}")
        for item in graph.context_items:
            lines.append(f"{self._PREFIX['context']} {item.strip()}")

        return "\n".join(lines)


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

    def distill(self, conversation: str, file_path: Optional[str] = None) -> DistillationResult:
        """
        Distil *conversation* into an executable, context-dense prompt.

        Args:
            conversation: Raw multi-turn conversation text.
            file_path:    Optional path to the source file. When provided the
                          file is **overwritten in place** with the compressed
                          content (BUG-DISTILL-001 fix).

        Returns:
            :class:`DistillationResult` with ``distilled_prompt`` on success.
            ``metadata['file_written']`` is ``True`` when the file was rewritten.
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

            # In-place rewrite — BUG-DISTILL-001 fix
            file_written = False
            if file_path:
                try:
                    with open(file_path, "w", encoding="utf-8") as fh:
                        fh.write(final_prompt)
                    file_written = True
                except OSError as exc:
                    # Non-fatal: log in metadata, return result without failing
                    return DistillationResult(
                        success=False,
                        error_message=f"Distillation succeeded but file write failed: {exc}",
                        distilled_prompt=final_prompt,
                        segment_count=len(segments),
                        noise_ratio=graph.noise_ratio,
                    )

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
                    "file_written": file_written,
                    "file_path": file_path,
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
