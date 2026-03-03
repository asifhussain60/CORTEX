"""
LensAnalysisMixin — Phase 103-b GAP-103-02.

LENS intelligence enhancement methods extracted from IntentRouter.

Responsibility: Compute confidence boosts from Git history, AST complexity,
and comment-hint analysis, and apply them to RoutingDecision objects.
SRP: Zero keyword logic, zero routing rules — LENS analysis only.

CORE-011: Type hints on all functions.
CORE-012: Docstrings on all public APIs.
CORE-028: snake_case naming.
"""
from typing import Any, Dict, List, Optional

from cortex.models.canonical_enums import IntentType


class LensAnalysisMixin:
    """Mixin providing LENS intelligence analysis for IntentRouter.

    Designed for cooperative multiple inheritance — assumes no specific
    base class; uses only ``self`` attributes set by ``IntentRouter.__init__``.
    """

    def _extract_git_pattern(
        self, lens_context: Dict[str, Any]
    ) -> Optional[IntentType]:
        """Extract predominant intent type from Git commit history.

        LENS-002: Analyze Git commit messages to identify patterns
        that validate or contradict the detected intent.

        Args:
            lens_context: LENS analyzer data (flexible format):
                - git_history.commits OR git_analysis.recent_commits

        Returns:
            IntentType: Predominant intent from Git history, or None.
        """
        try:
            git_data = (
                lens_context.get("git_history")
                or lens_context.get("git_analysis", {})
            )
            commits = git_data.get("commits") or git_data.get("recent_commits", [])
            if not commits:
                return None

            intent_counts: Dict[IntentType, int] = {
                IntentType.FIX: 0,
                IntentType.IMPLEMENT: 0,
                IntentType.REFACTOR: 0,
                IntentType.DOCUMENT: 0,
            }
            fix_kw = {"fix", "bug", "issue", "resolve", "patch"}
            impl_kw = {"add", "implement", "feature", "create", "new"}
            refactor_kw = {"refactor", "cleanup", "improve", "optimize", "restructure"}
            doc_kw = {"doc", "documentation", "comment", "readme"}

            for commit in commits:
                message = (
                    commit.get("message", "").lower()
                    if isinstance(commit, dict)
                    else str(commit).lower()
                )
                if any(kw in message for kw in fix_kw):
                    intent_counts[IntentType.FIX] += 1
                if any(kw in message for kw in impl_kw):
                    intent_counts[IntentType.IMPLEMENT] += 1
                if any(kw in message for kw in refactor_kw):
                    intent_counts[IntentType.REFACTOR] += 1
                if any(kw in message for kw in doc_kw):
                    intent_counts[IntentType.DOCUMENT] += 1

            if max(intent_counts.values()) > 0:
                return max(intent_counts.items(), key=lambda x: x[1])[0]
            return None

        except (KeyError, TypeError, AttributeError):
            return None

    def _calculate_ast_complexity(self, lens_context: Dict[str, Any]) -> int:
        """Calculate code complexity from AST analysis data.

        LENS-002: Complexity score drives refactor-intent confidence boosts.

        Args:
            lens_context: LENS analyzer data with ast_analysis sub-dict.

        Returns:
            int: Complexity score clamped to [0, 100].
        """
        try:
            ast_analysis = lens_context.get("ast_analysis", {})
            function_count = ast_analysis.get("function_count", 0) or len(
                ast_analysis.get("functions", [])
            )
            class_count = ast_analysis.get("class_count", 0) or len(
                ast_analysis.get("classes", [])
            )
            complexity = (class_count * 10) + (function_count * 2)
            return min(100, complexity)
        except (KeyError, TypeError, AttributeError):
            return 0

    def _analyze_comment_hints(
        self, lens_context: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """Analyze TODO/FIXME comments for intent hints.

        LENS-002: Extract comment-based signals for fix/refactor/implement work.

        Args:
            lens_context: LENS analyzer data with comment_analysis sub-dict.

        Returns:
            Dict with keys ``refactor_hints``, ``fix_hints``, ``implement_hints``.
        """
        hints: Dict[str, List[str]] = {
            "refactor_hints": [],
            "fix_hints": [],
            "implement_hints": [],
        }
        try:
            comment_analysis = lens_context.get("comment_analysis", {})
            todos = comment_analysis.get("todos", [])
            fixmes = comment_analysis.get("fixmes", [])

            refactor_kw = {"refactor", "cleanup", "improve", "optimize", "technical debt"}
            fix_kw = {"fix", "bug", "issue", "broken", "error"}
            impl_kw = {"add", "implement", "feature", "create", "support"}

            for comment in todos + fixmes:
                if isinstance(comment, dict):
                    text = (
                        comment.get("text")
                        or comment.get("content")
                        or comment.get("message")
                        or ""
                    ).lower()
                else:
                    text = str(comment).lower()

                if any(kw in text for kw in refactor_kw):
                    hints["refactor_hints"].append(text)
                elif any(kw in text for kw in fix_kw):
                    hints["fix_hints"].append(text)
                elif any(kw in text for kw in impl_kw):
                    hints["implement_hints"].append(text)

        except (KeyError, TypeError, AttributeError):
            pass
        return hints

    def _calculate_lens_boost(
        self, intent_type: IntentType, lens_context: Dict[str, Any]
    ) -> float:
        """Calculate confidence boost from LENS evidence.

        LENS-002: Composite boost capped at 0.4.

        Args:
            intent_type: Detected intent type.
            lens_context: LENS analyzer data.

        Returns:
            float: Confidence boost in [0.0, 0.4].
        """
        boost = 0.0

        git_pattern = self._extract_git_pattern(lens_context)
        if git_pattern == intent_type:
            boost += 0.15
        elif git_pattern is not None:
            boost += 0.05

        if intent_type == IntentType.REFACTOR:
            complexity = self._calculate_ast_complexity(lens_context)
            if complexity >= 80:
                boost += 0.20
            elif complexity > 40:
                boost += 0.15
            elif complexity > 20:
                boost += 0.10
            elif complexity > 10:
                boost += 0.05

        hints = self._analyze_comment_hints(lens_context)
        hint_key = f"{intent_type.value}_hints"
        if hints.get(hint_key):
            boost += 0.05

        return min(0.4, boost)

    def _enhance_with_lens(self, decision: Any, lens_context: Dict[str, Any]) -> Any:
        """Enhance routing decision with LENS intelligence.

        LENS-002: Apply boost + enrich metadata.

        Args:
            decision: Original RoutingDecision.
            lens_context: LENS analyzer data.

        Returns:
            RoutingDecision: Enhanced decision (or original on error).
        """
        try:
            # Import here to avoid circular dependency at module level
            from cortex.orchestrators.core.intent_router_impl import RoutingDecision  # noqa: PLC0415

            lens_boost = self._calculate_lens_boost(decision.intent_type, lens_context)
            new_confidence = min(1.0, decision.confidence_score + lens_boost)

            enhanced_metadata = {
                **decision.metadata,
                "lens_enhanced": True,
                "lens_confidence_boost": lens_boost,
                "original_confidence": decision.confidence_score,
            }

            git_pattern = self._extract_git_pattern(lens_context)
            if git_pattern:
                enhanced_metadata["lens_git_pattern"] = git_pattern.value

            complexity = self._calculate_ast_complexity(lens_context)
            if complexity > 0:
                enhanced_metadata["lens_ast_complexity"] = complexity
                enhanced_metadata["ast_complexity_detected"] = True

            hints = self._analyze_comment_hints(lens_context)
            if any(hints.values()):
                enhanced_metadata["lens_comment_hints"] = sum(
                    len(v) for v in hints.values()
                )
                if hints.get("refactor_hints"):
                    enhanced_metadata["todo_refactor_hints"] = len(
                        hints["refactor_hints"]
                    )
                if hints.get("fix_hints"):
                    enhanced_metadata["todo_fix_hints"] = len(hints["fix_hints"])
                if hints.get("implement_hints"):
                    enhanced_metadata["todo_implement_hints"] = len(
                        hints["implement_hints"]
                    )

            return RoutingDecision(
                intent_type=decision.intent_type,
                target_handler=decision.target_handler,
                confidence_score=new_confidence,
                reasoning=decision.reasoning + f" (LENS boost: +{lens_boost:.2f})",
                metadata=enhanced_metadata,
                composite_intents=decision.composite_intents,
            )
        except Exception:
            return decision
