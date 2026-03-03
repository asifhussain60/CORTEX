"""
RegistryIntelligenceMixin — Phase 103-b GAP-103-02.

Capability registry, governance registry, and missing-orchestrator discovery
methods extracted from IntentRouter.

Responsibility: Intelligent orchestrator discovery + governance complexity inflation.
SRP: Zero keyword logic, zero LENS — registry intelligence only.

CORE-011: Type hints on all functions.
CORE-012: Docstrings on all public APIs.
CORE-028: snake_case naming.
"""
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class RegistryIntelligenceMixin:
    """Mixin providing registry intelligence for IntentRouter.

    Designed for cooperative multiple inheritance. Assumes the following
    instance attributes are set by ``IntentRouter.__init__``:
        - self.registry_agent  (Optional[RegistryIntelligenceAgent])
        - self.orchestrator_lookup  (OrchestratorLookup)
        - self.logger  (EnhancedAuditLogger)
        - self._governance_registry  (Optional[GovernanceAuditor])
    """

    def _init_governance_registry(self) -> Optional[Any]:
        """Initialise GovernanceRegistry reference for complexity inflation.

        Phase 71-B ES-003: violations inflate complexity scores so the router
        promotes flagged work to higher-priority orchestrators.

        Returns:
            GovernanceAuditor instance or None (graceful degradation).
        """
        try:
            from cortex.governance.governance_auditor import GovernanceAuditor  # noqa: PLC0415
            return GovernanceAuditor()
        except Exception:
            return None

    def _get_governance_violations(self) -> List[Dict[str, Any]]:
        """Return active governance violations from the GovernanceRegistry.

        Returns:
            List of violation dicts with at least ``severity`` and ``rule`` keys.
            Empty list when no registry is available.
        """
        if self._governance_registry is None:
            return []
        try:
            return list(self._governance_registry.get_active_violations())
        except Exception:
            return []

    def compute_complexity(self, request: Dict[str, Any]) -> float:
        """Compute a complexity score for *request*, inflated by active P0 violations.

        Phase 71-B ES-003: active P0 governance violations raise the base score
        so that the router prefers heavyweight orchestrators for flagged work.

        Args:
            request: Request dict (must contain at least ``intent`` key).

        Returns:
            Float complexity score.  Higher values indicate more complex requests.
        """
        intent_str = str(request.get("intent", ""))
        base_score: float = min(len(intent_str) / 10.0, 5.0)

        violations = self._get_governance_violations()
        for violation in violations:
            severity = str(violation.get("severity", "")).upper()
            if severity == "P0":
                base_score += 3.0
            elif severity == "P1":
                base_score += 1.0

        return base_score

    def _init_capability_registry(self) -> Optional[Any]:
        """Initialise CapabilityMatcher from generated capabilities-manifest.yaml.

        Graceful degradation: returns None if manifest is absent or imports fail.

        Returns:
            CapabilityMatcher instance or None.
        """
        try:
            from cortex.intelligence.intelligence_capability_matcher import CapabilityMatcher  # noqa: PLC0415
            manifest_path = (
                Path(__file__).parent.parent.parent.parent.parent.parent
                / "cortex-registry" / "core" / "capabilities-manifest.yaml"
            )
            if manifest_path.exists():
                return CapabilityMatcher.load_from_manifest(manifest_path)
        except Exception:
            pass
        return None

    def _handle_missing_orchestrator(
        self,
        intent_type: Any,
        keywords: List[str],
        context: Dict[str, Any],
    ) -> Tuple[str, Optional[Any]]:
        """Handle missing orchestrator via intelligent discovery.

        Args:
            intent_type: Detected IntentType.
            keywords: Extracted keywords from request.
            context: Full request context.

        Returns:
            Tuple of (handler_name, orchestrator_instance_or_None).
        """
        if not self.registry_agent:
            return f"{intent_type.value.capitalize()}Handler", None

        try:
            discoveries = self.registry_agent.scan_for_orchestrators(force_rescan=True)

            matching = []
            for disc in discoveries:
                if not disc.is_registered:
                    overlap = disc.keywords & set(kw.lower() for kw in keywords)
                    if overlap:
                        matching.append((disc, len(overlap)))

            if matching:
                matching.sort(key=lambda x: x[1], reverse=True)
                best = matching[0][0]

                self.registry_agent.learn_from_intent_gap(
                    user_intent=(
                        context.get("description", "") or context.get("operation", "")
                    ),
                    missing_orchestrator=best.name,
                )

                gaps = self.registry_agent.detect_registry_gaps([best])
                if gaps:
                    fix_results = self.registry_agent.auto_fix_gaps(gaps, dry_run=False)
                    if fix_results["fixed"]:
                        result = self.orchestrator_lookup.resolve_instance(best.name)
                        if result.is_ok():
                            return best.name, result.value

                return best.name, None

            return f"{intent_type.value.capitalize()}Handler", None

        except Exception as e:
            self.logger.log_operation_complete(
                ac_id="REGISTRY-INTELLIGENCE-001",
                operation="MISSING_ORCHESTRATOR_DISCOVERY",
                success=False,
                details={"error": str(e), "intent": intent_type.value},
            )
            return f"{intent_type.value.capitalize()}Handler", None
