"""
RoutingCoreMixin — Phase 103-b GAP-103-02.

Core routing pipeline methods extracted from IntentRouter.

Responsibility: Intent detection, cache, keyword extraction, orchestrator lookup,
rule building, vacuum detection, complexity gate, YAML config loading.
SRP: Zero LENS enrichment, zero citations, zero registry intelligence — routing pipeline only.

CORE-011: Type hints on all functions.
CORE-012: Docstrings on all public APIs.
CORE-028: snake_case naming.
"""
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

from cortex.models.canonical_enums import IntentType
from cortex.orchestrators.core.routing_enforcement import (
    RoutingViolation,
)


class RoutingCoreMixin:
    """Mixin providing the core routing pipeline for IntentRouter.

    Designed for cooperative multiple inheritance. Assumes the following
    instance attributes are set by ``IntentRouter.__init__``:
        - self.logger             (EnhancedAuditLogger)
        - self.orchestrator_lookup (OrchestratorLookup)
        - self.enforcement_engine (RoutingEnforcementEngine)
        - self.intent_classifier  (IntentClassifier)
        - self.routing_rules      (Dict[Tuple, str])
        - self.routing_rules_config (Dict[str, Any])
        - self.operation_type_mappings (Dict[IntentType, List[str]])
        - self.vacuum_keywords    (List[str])
        - self.complexity_router  (WorkflowComplexityRouter)
        - self.golden_hammer_rules (GoldenHammerRules)
        - self.registry_agent     (Optional[...])

    Phase 137 (GAP-137-04): ``confidence_threshold`` controls URS emission.
    Routes with confidence below this value emit a MILD_PUNISHMENT URS signal
    so the closed-loop learning system can improve future routing.
    """

    # Phase 137 — GAP-137-04: configurable low-confidence threshold for URS emission
    confidence_threshold: float = 0.4

    # ------------------------------------------------------------------
    # Config loading
    # ------------------------------------------------------------------

    def _load_routing_config(self) -> Dict[str, Any]:
        """Load routing configuration from YAML file.

        AC-FUTURE-001: YAML-based rule loading.

        Returns:
            Dict[str, Any]: Configuration dict, or empty if YAML not found.
        """
        config_path = (
            Path(__file__).parent.parent.parent.parent.parent.parent
            / "cortex-registry" / "knowledge" / "intent-routing.yaml"
        )
        try:
            if config_path.exists():
                with open(config_path) as f:
                    raw = yaml.safe_load(f)
                    config: Dict[str, Any] = raw if isinstance(raw, dict) else {}
                self.logger.log_operation_complete(
                    ac_id="AC-FUTURE-001",
                    operation="YAML_ROUTING_CONFIG_LOADED",
                    success=True,
                    details={"path": str(config_path)},
                )
                return config
        except (FileNotFoundError, yaml.YAMLError) as e:
            self.logger.log_operation_complete(
                ac_id="AC-FUTURE-001",
                operation="YAML_ROUTING_CONFIG_LOAD_FAILED",
                success=False,
                details={"error": str(e), "using_fallback": True},
            )
        return {}

    def _build_routing_rules(
        self,
    ) -> Dict[Tuple[Optional[IntentType], Optional[str]], str]:
        """Build routing rules from YAML config or hardcoded fallback.

        AC-FUTURE-001: Support both YAML-driven and fallback routing.

        Returns:
            Dict mapping (IntentType, domain) → handler name.
        """
        rules: Dict[Tuple[Optional[IntentType], Optional[str]], str] = {}

        if "routing_rules" in self.routing_rules_config:
            yaml_rules = self.routing_rules_config.get("routing_rules", {})
            if isinstance(yaml_rules, dict):
                for intent_str, domain_rules in yaml_rules.items():
                    try:
                        intent = IntentType(intent_str)
                        if isinstance(domain_rules, dict):
                            for domain, rule_config in domain_rules.items():
                                handler_str: str = (
                                    str(rule_config.get("handler", ""))
                                    if isinstance(rule_config, dict)
                                    else str(rule_config)
                                )
                                if handler_str:
                                    domain_key = None if domain == "default" else domain
                                    rules[(intent, domain_key)] = handler_str
                    except (ValueError, KeyError) as e:
                        self.logger.log_operation_complete(
                            ac_id="AC-FUTURE-001",
                            operation="YAML_RULE_PARSE_ERROR",
                            success=False,
                            details={"error": str(e), "intent": intent_str},
                        )
            if rules:
                return rules

        # Hardcoded fallback (GAP-89-20: all 28+ IntentType values)
        return {
            (IntentType.IMPLEMENT, "orchestrators"): "ImplementationOrchestrator",
            (IntentType.IMPLEMENT, "core"): "CoreImplementationHandler",
            (IntentType.IMPLEMENT, "infrastructure"): "InfrastructureImplementationHandler",
            (IntentType.IMPLEMENT, None): "GeneralImplementationHandler",
            (IntentType.FIX, "orchestrators"): "OrchestratorFixOrchestrator",
            (IntentType.FIX, "core"): "CoreFixOrchestrator",
            (IntentType.FIX, "infrastructure"): "InfrastructureFixOrchestrator",
            (IntentType.FIX, None): "GeneralFixOrchestrator",
            (IntentType.REFACTOR, "orchestrators"): "RefactoringOrchestrator",
            (IntentType.REFACTOR, "core"): "CoreRefactoringHandler",
            (IntentType.REFACTOR, "infrastructure"): "InfrastructureRefactoringHandler",
            (IntentType.REFACTOR, None): "GeneralRefactoringHandler",
            (IntentType.DOCUMENT, "documentation"): "DocumentationOrchestrator",
            (IntentType.DOCUMENT, "governance"): "DocumentationOrchestrator",
            (IntentType.DOCUMENT, "reports"): "DocumentationOrchestrator",
            (IntentType.DOCUMENT, None): "DocumentationOrchestrator",
            (IntentType.PLAN, "registry"): "PlanOrchestrator",
            (IntentType.PLAN, "orchestrators"): "PlanOrchestrator",
            (IntentType.PLAN, "cortex"): "PlanOrchestrator",
            (IntentType.PLAN, None): "PlanOrchestrator",
            (IntentType.ANALYZE, None): "IntelligenceOrchestrator",
            (IntentType.TEST, None): "TDDOrchestrator",
            (IntentType.DEPLOY, None): "DeploymentOrchestrator",
            (IntentType.GOVERNANCE, None): "EnforcementOrchestrator",
            (IntentType.QUERY, None): "KnowledgeOrchestrator",
            (IntentType.VALIDATE, None): "ValidationOrchestrator",
            (IntentType.MIGRATE, None): "MigrationOrchestrator",
            (IntentType.ONBOARD, None): "OnboardOrchestrator",
            (IntentType.AUDIT, None): "AuditOrchestrator",
            (IntentType.DESIGN, None): "ChallengeOrchestrator",
            (IntentType.DIGEST, None): "DigestOrchestrator",
            (IntentType.REPHRASE, None): "RephraseOrchestrator",
            (IntentType.INVESTIGATE, None): "InvestigationOrchestrator",
            (IntentType.GOLDEN_TEST, None): "GoldenTestOrchestrator",
            (IntentType.VACUUM, None): "VacuumOrchestrator",
            (IntentType.DEBUG, None): "DebuggerOrchestrator",
            (IntentType.HEALTH, None): "HealthOrchestrator",
            (IntentType.SYNC, None): "SyncOrchestrator",
            (IntentType.TRAIN, None): "LearningOrchestrator",
            (IntentType.TOTALRECALL, None): "TotalRecallOrchestrator",
            (IntentType.RCA, None): "LearningOrchestrator",
            (IntentType.WORKFLOW_COMPOSE, None): "WorkflowComposer",
            (IntentType.INTRODUCE, None): "InteractionOrchestrator",
        }

    # ------------------------------------------------------------------
    # Intent detection
    # ------------------------------------------------------------------

    def detect_intent(self, context: Dict[str, Any]) -> IntentType:
        """Detect operation intent type from context using three-tier classifier.

        Pipeline (Phase 70 GAP-70-A4):
        1. Explicit ``intent`` field short-circuits all classification.
        2. Vacuum keyword check (dedicated pathway).
        3. Three-tier IntentClassifier (regex → keyword → LLM).
        4. Default: IMPLEMENT.

        Args:
            context: Context dict with description, user_request, keywords,
                operation, or intent keys.

        Returns:
            IntentType: Detected intent.

        Raises:
            ValueError: If context is None or invalid type.
        """
        try:
            if "intent" in context and isinstance(context.get("intent"), IntentType):
                return context["intent"]

            text_parts: List[str] = []
            if context.get("description"):
                text_parts.append(str(context["description"]))
            if context.get("user_request"):
                text_parts.append(str(context["user_request"]))
            if isinstance(context.get("keywords"), list):
                text_parts.extend(str(k) for k in context["keywords"])

            combined_text = " ".join(text_parts).lower()
            operation = str(context.get("operation", "")).lower().strip()

            if self._is_vacuum_operation(combined_text):
                context["is_vacuum_operation"] = True
                return IntentType.VACUUM

            clf_result = self.intent_classifier.classify(
                text=combined_text,
                operation=operation,
            )

            self.logger.log_operation_complete(
                ac_id="AC-70-INTENT-CLASSIFIER-001",
                operation="INTENT_CLASSIFIED",
                success=True,
                details={
                    "intent": clf_result.intent_type.value,
                    "confidence": clf_result.confidence,
                    "tier": clf_result.tier_used,
                    "reasoning": clf_result.reasoning,
                },
            )

            if clf_result.confidence < self.confidence_threshold or clf_result.intent_type == IntentType.UNKNOWN:
                self._log_routing_miss(combined_text, clf_result)
                self._emit_urs_low_confidence(clf_result.confidence)

            return clf_result.intent_type

        except (ValueError, TypeError, AttributeError) as e:
            self.logger.log_operation_complete(
                ac_id="AC-PROD-001-02",
                operation="INTENT_DETECTION_ERROR",
                success=False,
                details={"error": str(e), "context_type": type(context).__name__},
            )
            return IntentType.IMPLEMENT

    def _detect_intent_from_dict(self, context: Dict[str, Any]) -> IntentType:
        """Thin wrapper around detect_intent() for test/external API compatibility.

        Args:
            context: Dict with description, user_request, keywords, operation, or intent.

        Returns:
            IntentType: The detected intent type.
        """
        return self.detect_intent(context)

    def _is_vacuum_operation(self, combined_text: str) -> bool:
        """Detect if the operation is a VACUUM cleanup operation.

        Args:
            combined_text: Combined text from description, keywords, and operation.

        Returns:
            bool: True if vacuum operation detected.
        """
        try:
            for keyword in self.vacuum_keywords:
                if keyword.lower() in combined_text:
                    self.logger.log_operation_complete(
                        ac_id="VACUUM-DETECT-001",
                        operation="VACUUM_KEYWORD_DETECTED",
                        success=True,
                        details={"matched_keyword": keyword},
                    )
                    return True
            return False
        except Exception as e:
            self.logger.log_operation_complete(
                ac_id="VACUUM-DETECT-001",
                operation="VACUUM_DETECTION_ERROR",
                success=False,
                details={"error": str(e)},
            )
            return False

    def _log_routing_miss(self, text: str, clf_result: Any) -> None:
        """Log a routing miss for audit-driven keyword expansion.

        Phase 91: Low-confidence or UNKNOWN results are recorded so
        ``/audit fix`` can surface unclassified keywords as candidates.

        Args:
            text: Combined request text not confidently classified.
            clf_result: ClassificationResult from the 3-tier classifier.
        """
        try:
            self.logger.log_operation_complete(
                ac_id="AC-91-ROUTING-MISS-001",
                operation="ROUTING_MISS_DETECTED",
                success=True,
                details={
                    "unclassified_text": text[:200],
                    "fallback_intent": clf_result.intent_type.value,
                    "confidence": clf_result.confidence,
                    "tier": clf_result.tier_used,
                    "reasoning": clf_result.reasoning,
                },
            )
        except Exception:
            pass  # Non-blocking — must never break routing

    def _emit_urs_low_confidence(self, confidence: float) -> None:
        """Emit a URS MILD_PUNISHMENT signal for low-confidence routing.

        Called when routing confidence falls below ``confidence_threshold``.
        Low-confidence routes represent training data for the URS closed-loop
        learning system.  Emission is best-effort — failures are silently
        swallowed to prevent routing disruption.

        Args:
            confidence: The observed routing confidence score.

        Phase: 137 — GAP-137-04 (CORE-064: URS closed-loop learning signal)
        """
        try:
            from cortex.mcp.tools.cortex_learning import cortex_learning_tool  # type: ignore[import]
            cortex_learning_tool(
                op="emit",
                signal_type="MILD_PUNISHMENT",
                scope="intent_routing",
                context={"confidence": confidence, "reason": "low_confidence_routing"},
            )
        except Exception:
            pass  # Non-blocking — URS emission must never break routing

    # ------------------------------------------------------------------
    # Cache
    # ------------------------------------------------------------------

    def _get_cache_key(self, context: Dict[str, Any]) -> str:
        """Generate cache key for routing decision.

        LENS-002: Includes lens_context presence in key so LENS-enhanced
        and non-LENS decisions are cached separately.

        Args:
            context: Context dictionary.

        Returns:
            str: MD5 hash of relevant context fields.
        """
        try:
            key_fields = {
                "operation": context.get("operation"),
                "description": context.get("description"),
                "domain": context.get("domain"),
                "keywords": sorted(context.get("keywords", [])) if context.get("keywords") else None,
                "has_lens": bool(context.get("lens_context")),
            }
            return hashlib.md5(
                json.dumps(key_fields, sort_keys=True, default=str).encode()
            ).hexdigest()
        except Exception:
            return str(context.get("operation", "default"))

    # ------------------------------------------------------------------
    # Keyword extraction + orchestrator lookup
    # ------------------------------------------------------------------

    def _extract_keywords(self, context: Dict[str, Any]) -> List[str]:
        """Extract routing keywords from user request context.

        AC-PHASE-8.2-01: Parses description, operation, user_intent, and
        explicit keywords fields.

        Args:
            context: User request context.

        Returns:
            List[str]: Extracted keywords (lowercase, unique, stop-words removed).
        """
        keywords: List[str] = []
        try:
            stop_words = {"the", "a", "an", "is", "are", "to", "of", "for", "with", "in", "on"}

            for field, sep in [
                ("description", " "),
                ("operation", "_"),
                ("user_intent", " "),
            ]:
                value = context.get(field, "")
                if value:
                    tokens = str(value).lower().replace(":", " ").replace(",", " ").replace(sep, " ").split()
                    keywords.extend(tokens)

            unique = list(
                set(kw for kw in keywords if kw not in stop_words and len(kw) > 2)
            )

            explicit: list = context.get("keywords", [])
            if isinstance(explicit, list):
                lower_unique = [k.lower() for k in unique]
                for kw in explicit:
                    if isinstance(kw, str) and kw.lower() not in lower_unique:
                        unique.append(kw.lower())

            return unique
        except (TypeError, AttributeError) as e:
            self.logger.log_operation_complete(
                ac_id="AC-PHASE-8.2-01",
                operation="KEYWORD_EXTRACTION_ERROR",
                success=False,
                details={"error": str(e)},
            )
            return []

    def _lookup_orchestrators(
        self,
        keywords: List[str],
        intent: IntentType,
    ) -> List[Tuple[str, Any, float]]:
        """Lookup orchestrators matching extracted keywords.

        AC-PHASE-8.2-01: Query OrchestratorLookup registry.

        Args:
            keywords: Extracted keywords from user request.
            intent: Detected intent type for filtering.

        Returns:
            List of (name, instance, confidence) tuples.
        """
        candidates: List[Tuple[str, Any, float]] = []
        try:
            from cortex.orchestrators.core.orchestrator_lookup import OrchestratorLookup  # noqa: PLC0415
            lookup = OrchestratorLookup()
            matches = lookup.find_by_keywords(keywords, self.routing_rules_config)
            for name, confidence in matches:
                result = lookup.resolve_instance(name)
                if result.is_ok():
                    candidates.append((name, result.value, confidence))
                else:
                    self.logger.log_operation_complete(
                        ac_id="AC-PHASE-8.2-01",
                        operation="ORCHESTRATOR_RESOLVE_FAILED",
                        success=False,
                        details={"orchestrator": name, "error": result.error},
                    )
        except Exception as e:
            self.logger.log_operation_complete(
                ac_id="AC-PHASE-8.2-01",
                operation="ORCHESTRATOR_LOOKUP_ERROR",
                success=False,
                details={"error": str(e)},
            )
        return candidates

    def _rank_orchestrators(
        self, candidates: List[Tuple[str, Any, float]]
    ) -> List[Tuple[str, Any, float]]:
        """Rank orchestrator candidates by confidence score (descending).

        Args:
            candidates: List of (name, instance, confidence) tuples.

        Returns:
            List sorted by confidence descending.
        """
        try:
            ranked = sorted(candidates, key=lambda x: x[2], reverse=True)
            self.logger.log_operation_complete(
                ac_id="AC-PHASE-8.2-01",
                operation="ORCHESTRATOR_RANKING",
                success=True,
                details={
                    "candidate_count": len(ranked),
                    "top_candidate": ranked[0][0] if ranked else None,
                    "top_confidence": ranked[0][2] if ranked else 0.0,
                },
            )
            return ranked
        except Exception as e:
            self.logger.log_operation_complete(
                ac_id="AC-PHASE-8.2-01",
                operation="ORCHESTRATOR_RANKING_ERROR",
                success=False,
                details={"error": str(e)},
            )
            return candidates

    # ------------------------------------------------------------------
    # Complexity gate
    # ------------------------------------------------------------------

    def _map_operation_to_intent(self, operation_type: str) -> IntentType:
        """Map operation type string to IntentType enum.

        Args:
            operation_type: Lower-case operation name.

        Returns:
            IntentType corresponding to operation, defaulting to IMPLEMENT.
        """
        mapping = {
            "fix": IntentType.FIX,
            "create": IntentType.IMPLEMENT,
            "implement": IntentType.IMPLEMENT,
            "refactor": IntentType.REFACTOR,
            "clean": IntentType.REFACTOR,
            "clean_code": IntentType.REFACTOR,
            "cleanup": IntentType.REFACTOR,
            "improve": IntentType.REFACTOR,
            "optimize": IntentType.REFACTOR,
            "restructure": IntentType.REFACTOR,
            "simplify": IntentType.REFACTOR,
            "test": IntentType.IMPLEMENT,
            "document": IntentType.DOCUMENT,
            "security": IntentType.AUDIT,
            "migrate": IntentType.IMPLEMENT,
            "audit": IntentType.AUDIT,
            "design": IntentType.DESIGN,
            "plan": IntentType.PLAN,
            "investigate": IntentType.INVESTIGATE,
            "analyze": IntentType.ANALYZE,
            "digest": IntentType.DIGEST,
        }
        return mapping.get(operation_type, IntentType.IMPLEMENT)

    def _check_workflow_complexity(
        self, context: Dict[str, Any]
    ) -> Optional[Any]:
        """Check if workflow template should be used based on task complexity.

        WORKFLOW-COMPLEXITY-GATE-001: Stage 2a complexity-based routing.

        Args:
            context: Operation context.

        Returns:
            RoutingDecision if complexity routing applies, None to fall through.
        """
        try:
            from cortex.orchestrators.core.intent_router_impl import RoutingDecision  # noqa: PLC0415
            from cortex.orchestrators.core.intent_router import (  # noqa: PLC0415
                Intent as ComplexityIntent,
            )
            from cortex.orchestrators.core.intent_router.workflow_gate import (  # noqa: PLC0415
                RoutingStrategy as ComplexityRoutingStrategy,
            )

            operation = context.get("operation", "").lower()
            description = context.get("description", "").lower()
            user_request = context.get("user_request", "").lower()
            combined_text = f"{operation} {description} {user_request}".strip()

            clf_result = self.intent_classifier.classify(
                text=combined_text, operation=operation
            )
            _intent_to_op: Dict[IntentType, str] = {
                IntentType.FIX: "fix", IntentType.AUDIT: "audit",
                IntentType.REFACTOR: "refactor", IntentType.DESIGN: "design",
                IntentType.PLAN: "plan", IntentType.INVESTIGATE: "investigate",
                IntentType.ANALYZE: "analyze", IntentType.DIGEST: "digest",
                IntentType.IMPLEMENT: "implement", IntentType.DOCUMENT: "document",
                IntentType.ONBOARD: "onboard", IntentType.REPHRASE: "rephrase",
                IntentType.WORKFLOW_COMPOSE: "workflow_compose",
                IntentType.VACUUM: "refactor",
            }
            operation_type = _intent_to_op.get(clf_result.intent_type, "implement")

            target_files = context.get("target_files", [])
            if not target_files:
                file_pattern = r'\b[\w/.-]+\.(py|ts|js|yaml|yml|json|md|txt)\b'
                matches = re.findall(file_pattern, combined_text)
                target_files = [m[0] if isinstance(m, tuple) else m for m in matches]

            dependencies = context.get("dependencies", [])
            risk_level = context.get("risk_level", "MEDIUM").upper()
            if "critical" in combined_text or "production" in combined_text:
                risk_level = "CRITICAL"
            elif "high" in combined_text or "complex" in combined_text:
                risk_level = "HIGH"
            elif "low" in combined_text or "simple" in combined_text or "trivial" in combined_text:
                risk_level = "LOW"

            complexity_intent = ComplexityIntent(
                operation_type=operation_type,
                target_files=target_files,
                dependencies=dependencies,
                risk_level=risk_level,
                metadata=context,
            )

            complexity_routing = self.complexity_router.route(complexity_intent)
            self.golden_hammer_rules.validate_routing_decision(
                complexity_routing,
                override_rationale=context.get("override_rationale"),
            )

            self.logger.log_operation_complete(
                ac_id="WORKFLOW-COMPLEXITY-GATE-001",
                operation="COMPLEXITY_ROUTING_CHECK",
                success=True,
                details={
                    "complexity_score": complexity_routing.complexity,
                    "route": complexity_routing.route.value,
                    "rationale": complexity_routing.rationale,
                    "template_id": complexity_routing.template_id,
                    "orchestrator": complexity_routing.orchestrator,
                },
            )

            explicit_kw = [
                k.lower() for k in context.get("keywords", []) if isinstance(k, str)
            ]

            if complexity_routing.route == ComplexityRoutingStrategy.WORKFLOW_TEMPLATE:
                return RoutingDecision(
                    intent_type=IntentType.IMPLEMENT,
                    target_handler=f"WorkflowTemplate:{complexity_routing.template_id}",
                    confidence_score=complexity_routing.complexity,
                    reasoning=(
                        f"{operation_type} routed via workflow template: "
                        f"{complexity_routing.rationale}"
                    ),
                    keyword_matches=explicit_kw,
                    metadata={
                        "complexity_score": complexity_routing.complexity,
                        "template_id": complexity_routing.template_id,
                        "requires_confirmation": complexity_routing.requires_confirmation,
                        "governance_gate": complexity_routing.governance_gate,
                        "operation_type": operation_type,
                        "routing_source": "complexity_gate",
                        "domain": context.get("domain"),
                    },
                )
            elif complexity_routing.route == ComplexityRoutingStrategy.DIRECT_ORCHESTRATOR:
                return RoutingDecision(
                    intent_type=self._map_operation_to_intent(operation_type),
                    target_handler=complexity_routing.orchestrator,
                    confidence_score=1.0 - complexity_routing.complexity,
                    reasoning=(
                        f"{operation_type} routed directly to "
                        f"{complexity_routing.orchestrator}: {complexity_routing.rationale}"
                    ),
                    keyword_matches=explicit_kw,
                    metadata={
                        "complexity_score": complexity_routing.complexity,
                        "orchestrator": complexity_routing.orchestrator,
                        "requires_confirmation": complexity_routing.requires_confirmation,
                        "operation_type": operation_type,
                        "routing_source": "complexity_gate",
                        "domain": context.get("domain"),
                    },
                )
            return None

        except Exception as e:
            self.logger.log_operation_complete(
                ac_id="WORKFLOW-COMPLEXITY-GATE-001",
                operation="COMPLEXITY_ROUTING_ERROR",
                success=False,
                details={"error": str(e)},
            )
            return None

    # ------------------------------------------------------------------
    # Internal routing
    # ------------------------------------------------------------------

    def _route_internal(self, context: Dict[str, Any]) -> Any:
        """Internal routing implementation (logic only, no caching).

        AC-PHASE-8.2-01: Enhanced with keyword-based orchestrator lookup.

        Args:
            context: Context dict with operation details.

        Returns:
            RoutingDecision.

        Raises:
            ValueError: If routing cannot be determined or enforcement blocks.
        """
        try:
            from cortex.orchestrators.core.intent_router_impl import RoutingDecision  # noqa: PLC0415
            from cortex.orchestrators.core.intent_router_impl import CompositeIntentDetector  # noqa: PLC0415

            operation = context.get("operation", "unknown")
            domain = context.get("domain")

            intent_type = self.detect_intent(context)
            description = context.get("description", "")
            composite_intents = CompositeIntentDetector.detect_composite_intents(
                description, intent_type
            )

            keywords = self._extract_keywords(context)
            candidates = self._lookup_orchestrators(keywords, intent_type)
            ranked_candidates = self._rank_orchestrators(candidates)

            if ranked_candidates:
                target_name, target_orch, base_confidence = ranked_candidates[0]
                target_handler = target_name
                target_orchestrator = target_orch
                fallback_orchestrators = [o for _, o, _ in ranked_candidates[1:4]]

                confidence_breakdown: Dict[str, float] = {
                    "keyword_match": base_confidence,
                    "intent_detection": 0.2,
                }

                lens_context = context.get("lens_context")
                if lens_context:
                    git_pattern = self._extract_git_pattern(lens_context)
                    ast_complexity = self._calculate_ast_complexity(lens_context)

                    if git_pattern == intent_type:
                        confidence_breakdown["lens_git_exact"] = 0.15
                    elif git_pattern:
                        confidence_breakdown["lens_git_partial"] = 0.05

                    if ast_complexity > 75:
                        confidence_breakdown["lens_ast_very_high"] = 0.20
                    elif ast_complexity > 50:
                        confidence_breakdown["lens_ast_high"] = 0.15
                    elif ast_complexity > 25:
                        confidence_breakdown["lens_ast_medium"] = 0.10

                confidence = sum(confidence_breakdown.values())

            else:
                target_handler, target_orchestrator = self._handle_missing_orchestrator(
                    intent_type, keywords, context
                )
                if not target_orchestrator:
                    routing_key = (intent_type, domain)
                    if routing_key not in self.routing_rules:
                        routing_key = (intent_type, None)
                    target_handler = self.routing_rules.get(
                        routing_key,
                        f"{intent_type.value.capitalize()}OrchestrationHandler",
                    )
                    result = self.orchestrator_lookup.resolve_instance(target_handler)
                    target_orchestrator = result.value if result.is_ok() else None

                fallback_orchestrators = []
                ctx_kw = context.get("keywords", [])
                op_kw = self.operation_type_mappings[intent_type]
                matches = sum(
                    1
                    for kw in ctx_kw
                    if kw.lower() in [k.lower() for k in op_kw]
                )
                confidence = (
                    min(1.0, (matches / len(op_kw)) + 0.5) if op_kw else 0.75
                )
                confidence_breakdown = {"legacy_routing": confidence}
                ranked_candidates = []

            if len(composite_intents) > 1:
                target_handler = (
                    f"CompositeHandler_{'+'  .join([i.value for i in composite_intents])}"
                )
                confidence *= 0.95
                confidence_breakdown["composite_penalty"] = -0.05

            reasoning = (
                f"Routed '{context.get('operation')}' to {target_handler} "
                f"(confidence: {confidence:.2f}) based on "
                f"intent type '{intent_type.value}'"
            )
            if keywords:
                reasoning += f", keywords: {', '.join(keywords[:3])}"
            if len(composite_intents) > 1:
                reasoning += (
                    f". Detected composite intents: "
                    f"{', '.join([i.value for i in composite_intents])}"
                )

            if context.get("is_vacuum_operation"):
                reasoning = (
                    f"VACUUM operation detected for '{context.get('operation')}'. "
                    "Routing to VacuumOrchestrator for efficient CORTEX repository cleanup."
                )
                target_handler = "VacuumOrchestrator"
                vr = self.orchestrator_lookup.resolve_instance("VacuumOrchestrator")
                if vr.is_ok():
                    target_orchestrator = vr.value

            decision = RoutingDecision(
                intent_type=intent_type,
                target_handler=target_handler,
                confidence_score=min(1.0, confidence),
                reasoning=reasoning,
                metadata={
                    "operation": context.get("operation"),
                    "domain": domain,
                    "keywords_matched": len(keywords),
                    "total_keywords": len(keywords),
                    "composite_intents": len(composite_intents) > 1,
                    "candidates_found": len(ranked_candidates) if ranked_candidates else 0,
                },
                composite_intents=composite_intents,
                target_orchestrator=target_orchestrator,
                fallback_orchestrators=fallback_orchestrators,
                keyword_matches=keywords,
                confidence_breakdown=confidence_breakdown,
            )

            enforcement_result = self.enforcement_engine.validate_routing_decision(decision)
            if not enforcement_result.passed:
                self.logger.log_operation_complete(
                    ac_id="AC-PHASE-8.2-01",
                    operation="ROUTING_ENFORCEMENT_VIOLATION",
                    success=False,
                    details={
                        "violations": [v.value for v in enforcement_result.violations],
                        "target_handler": target_handler,
                        "confidence": confidence,
                    },
                )
                blocking = [
                    v for v in enforcement_result.violations
                    if v in [
                        RoutingViolation.ORCHESTRATOR_NOT_FOUND,
                        RoutingViolation.CONFIDENCE_TOO_LOW,
                        RoutingViolation.NOT_AUDITABLE,
                    ]
                ]
                if self.enforcement_engine.blocking_enabled and blocking:
                    raise ValueError(
                        f"Routing blocked by enforcement: "
                        f"{', '.join([v.value for v in blocking])}"
                    )

            return decision

        except (KeyError, ValueError, AttributeError) as e:
            raise ValueError(f"Routing failed: {str(e)}")
