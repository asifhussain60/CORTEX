"""
Golden Permanence Tests — Phase 84: Stub Elimination + Business Rules Pipeline

PURPOSE:
    Structural permanence assertions that prevent stub regression.
    These tests verify the WIRING and ABSENCE OF STUBS — they do NOT
    test business logic (that's in sub-phase-specific test files).

    Once all 29 GAPs are closed, these tests lock the fix permanently.
    Any future commit that reintroduces a stub will fail CI.

AUTHORITY:
    - Phase 84 (phase-84-stub-elimination-business-rules-pipeline.yaml)
    - CORE-008 (TDD), CORE-064 (Sweep Completeness)
    - Golden test contract: tests here must NEVER be deleted or weakened

AC_START: AC-84-PERMANENCE-2026-02-26
TEST COUNT: 29 permanence assertions (1 per GAP)
"""

import ast
import importlib
import re
from pathlib import Path
from typing import List, Set

import pytest

# ── Project root ──────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parents[3]  # tests/golden/production/ → project root
CORTEX_SRC = PROJECT_ROOT / "cortex"
REGISTRY = PROJECT_ROOT / "cortex-registry"


# ═══════════════════════════════════════════════════════════════════════════════
# SWEEP 1 — Business Rules Pipeline (GAPs 1-5)
# ═══════════════════════════════════════════════════════════════════════════════

class TestBusinessRulesPipelineWiring:
    """
    Permanence tests for the business rules extraction → persistence → enforcement pipeline.
    Verifies RuleExtractor is wired, business-rules.yaml is generated, and enforcement loop exists.
    """

    # ── GAP-84-01: RuleExtractor wired into LENS ──────────────────────────────
    def test_gap_01_rule_extractor_imported_by_lens(self) -> None:
        """
        GAP-84-01: RuleExtractor must be imported by at least one LENS module.

        Permanence: prevents RuleExtractor from being silently disconnected.
        Checks cortex/lens/ AND cortex/intelligence/lens/ for import of RuleExtractor.
        """
        lens_dirs = [
            CORTEX_SRC / "lens",
            CORTEX_SRC / "intelligence" / "lens",
        ]
        rule_extractor_imported = False

        for lens_dir in lens_dirs:
            if not lens_dir.exists():
                continue
            for py_file in lens_dir.rglob("*.py"):
                if py_file.name.startswith("__"):
                    continue
                content = py_file.read_text(encoding="utf-8", errors="ignore")
                if "RuleExtractor" in content and "import" in content:
                    # Verify it's a real import, not a comment
                    for line in content.splitlines():
                        stripped = line.strip()
                        if stripped.startswith("#"):
                            continue
                        if "RuleExtractor" in stripped and ("import" in stripped or "from" in stripped):
                            rule_extractor_imported = True
                            break
            if rule_extractor_imported:
                break

        assert rule_extractor_imported, (
            "GAP-84-01 REGRESSION: RuleExtractor is not imported by any LENS pipeline module. "
            "Expected: cortex/lens/ or cortex/intelligence/lens/ imports RuleExtractor "
            "from cortex.intelligence.lens.domain_inference.rule_extractor"
        )

    # ── GAP-84-02: Business rules persistence artifact ───────────────────────
    def test_gap_02_persistence_service_has_business_rules_generator(self) -> None:
        """
        GAP-84-02: KnowledgePersistenceService must have a business-rules artifact generator.

        Permanence: prevents business-rules.yaml generation from being removed.
        """
        persistence_file = (
            CORTEX_SRC / "intelligence" / "knowledge" / "persistence"
            / "knowledge_persistence_service.py"
        )
        assert persistence_file.exists(), f"Persistence service not found: {persistence_file}"

        content = persistence_file.read_text(encoding="utf-8")

        assert "business_rules" in content.lower() or "business-rules" in content, (
            "GAP-84-02 REGRESSION: KnowledgePersistenceService has no business-rules artifact generator. "
            "Expected: _generate_business_rules_artifact() method or 'business-rules' in artifact_generators."
        )

    # ── GAP-84-03: BusinessKnowledgeRepository not in-memory stub ────────────
    def test_gap_03_business_knowledge_repository_not_stub(self) -> None:
        """
        GAP-84-03: BusinessKnowledgeRepository must NOT be an in-memory dict stub.

        Permanence: prevents regression to PHASE-E unblocking stub.

        Phase 107 update: canonical location moved to
        cortex/intelligence/knowledge/business_knowledge_repository.py.
        The domain_brain version is now a compat shim re-exporting from there.
        We check the CANONICAL file for persistence, and the shim for delegation.
        """
        # Phase 107: canonical definition is in knowledge/
        canonical_file = (
            CORTEX_SRC / "intelligence" / "knowledge"
            / "business_knowledge_repository.py"
        )
        assert canonical_file.exists(), (
            f"Canonical BusinessKnowledgeRepository not found: {canonical_file}"
        )

        canonical_content = canonical_file.read_text(encoding="utf-8")

        # Canonical must NOT have the PHASE-E stub markers
        assert "PHASE-E" not in canonical_content and "Stub for" not in canonical_content, (
            "GAP-84-03 REGRESSION: BusinessKnowledgeRepository still has PHASE-E stub markers. "
            "Must be replaced with YAML-backed implementation."
        )

        # Canonical must reference YAML or file-based persistence
        has_persistence = any(
            keyword in canonical_content
            for keyword in ["yaml", "YAML", ".yaml", "Path", "pathlib", "open(", "read_text"]
        )
        assert has_persistence, (
            "GAP-84-03 REGRESSION: BusinessKnowledgeRepository appears to still be in-memory. "
            "Must use YAML or file-based persistence."
        )

        # Domain_brain shim must re-export from canonical (Phase 107)
        shim_file = (
            CORTEX_SRC / "intelligence" / "domain_brain"
            / "business_knowledge_repository.py"
        )
        if shim_file.exists():
            shim_content = shim_file.read_text(encoding="utf-8")
            assert "knowledge.business_knowledge_repository" in shim_content, (
                "domain_brain/business_knowledge_repository.py exists but does not "
                "delegate to knowledge/business_knowledge_repository.py"
            )

    # ── GAP-84-04: Enforcement loop for business rules ───────────────────────
    def test_gap_04_enforcement_orchestrator_has_business_rule_agent(self) -> None:
        """
        GAP-84-04: EnforcementOrchestrator must include a business rule enforcement agent.

        Permanence: prevents enforcement from silently dropping business rule validation.
        """
        enforcement_file = (
            CORTEX_SRC / "orchestrators" / "core" / "enforcement_orchestrator.py"
        )
        # Phase 103-e: enforcement_orchestrator is now a sub-package
        if not enforcement_file.exists():
            enforcement_file = (
                CORTEX_SRC / "orchestrators" / "core" / "enforcement_orchestrator" / "__init__.py"
            )
        assert enforcement_file.exists(), f"EnforcementOrchestrator not found: {enforcement_file}"

        content = enforcement_file.read_text(encoding="utf-8")

        assert "business_rule" in content.lower() or "BusinessRule" in content, (
            "GAP-84-04 REGRESSION: EnforcementOrchestrator has no business rule agent. "
            "Expected: BusinessRuleEnforcementAgent or business_rule_agent in agents list."
        )

    # ── GAP-84-05: INDEX.yaml has business-rules domain ──────────────────────
    def test_gap_05_index_yaml_has_business_rules_domain(self) -> None:
        """
        GAP-84-05: Knowledge INDEX.yaml must include a business-rules domain.

        Permanence: prevents business rules from being invisible to knowledge routing.
        """
        index_file = REGISTRY / "knowledge" / "INDEX.yaml"
        assert index_file.exists(), f"INDEX.yaml not found: {index_file}"

        content = index_file.read_text(encoding="utf-8")

        assert "business-rules" in content or "business_rules" in content, (
            "GAP-84-05 REGRESSION: INDEX.yaml has no business-rules domain entry. "
            "Must include business-rules domain with keywords for routing."
        )


# ═══════════════════════════════════════════════════════════════════════════════
# SWEEP 2 — False Positive Elimination (GAPs 6-11)
# ═══════════════════════════════════════════════════════════════════════════════

class TestFalsePositiveElimination:
    """
    Permanence tests verifying production-imported stubs have been replaced.
    Each test asserts the file does NOT contain hollow/always-pass behavior.
    """

    # ── GAP-84-06: GovernanceEnforcementAgent ────────────────────────────────
    def test_gap_06_governance_enforcement_agent_not_always_allowed(self) -> None:
        """
        GAP-84-06: GovernanceEnforcementAgent must NOT always return allowed=True.

        Permanence: prevents false-positive governance enforcement.
        """
        agent_file = CORTEX_SRC / "enforcement" / "governance_enforcement_agent.py"
        assert agent_file.exists(), f"Agent file not found: {agent_file}"

        content = agent_file.read_text(encoding="utf-8")
        lines = [l.strip() for l in content.splitlines() if l.strip() and not l.strip().startswith("#")]

        # A real implementation should have more than 25 lines of logic
        assert len(lines) > 25, (
            f"GAP-84-06 REGRESSION: GovernanceEnforcementAgent is still a stub "
            f"({len(lines)} non-blank non-comment lines). Must delegate to real enforcement."
        )

        # Must NOT have the always-pass pattern
        assert '"allowed": True' not in content or "if " in content, (
            "GAP-84-06 REGRESSION: GovernanceEnforcementAgent still unconditionally returns allowed=True. "
            "Must conditionally evaluate governance rules."
        )

    # ── GAP-84-07: GovernanceIntelligence ────────────────────────────────────
    def test_gap_07_governance_intelligence_not_empty(self) -> None:
        """
        GAP-84-07: GovernanceIntelligence.analyse() must NOT be an empty stub.
        """
        gi_file = CORTEX_SRC / "core" / "governance_intelligence.py"
        assert gi_file.exists(), f"File not found: {gi_file}"

        content = gi_file.read_text(encoding="utf-8")
        lines = [l.strip() for l in content.splitlines() if l.strip() and not l.strip().startswith("#")]

        assert len(lines) > 25, (
            f"GAP-84-07 REGRESSION: GovernanceIntelligence is still a stub "
            f"({len(lines)} lines). analyse() must delegate to real enforcement."
        )

    # ── GAP-84-08: KnowledgeComposer ────────────────────────────────────────
    def test_gap_08_knowledge_composer_not_empty(self) -> None:
        """
        GAP-84-08: KnowledgeComposer.compose() must NOT be an empty stub.
        """
        kc_file = CORTEX_SRC / "core" / "knowledge_composer.py"
        assert kc_file.exists(), f"File not found: {kc_file}"

        content = kc_file.read_text(encoding="utf-8")
        lines = [l.strip() for l in content.splitlines() if l.strip() and not l.strip().startswith("#")]

        assert len(lines) > 25, (
            f"GAP-84-08 REGRESSION: KnowledgeComposer is still a stub "
            f"({len(lines)} lines). compose() must delegate to KnowledgeSynthesisEngine."
        )

    # ── GAP-84-09: TierComposer ─────────────────────────────────────────────
    def test_gap_09_tier_composer_not_empty(self) -> None:
        """
        GAP-84-09: TierComposer.compose_tiers() must NOT be an empty stub.
        """
        tc_file = CORTEX_SRC / "core" / "tier_composer.py"
        assert tc_file.exists(), f"File not found: {tc_file}"

        content = tc_file.read_text(encoding="utf-8")
        lines = [l.strip() for l in content.splitlines() if l.strip() and not l.strip().startswith("#")]

        assert len(lines) > 20, (
            f"GAP-84-09 REGRESSION: TierComposer is still a stub "
            f"({len(lines)} lines). compose_tiers() must read wiring YAML specs."
        )

    # ── GAP-84-10: CortexIntelligenceIntegration ────────────────────────────
    def test_gap_10_intelligence_integration_not_empty(self) -> None:
        """
        GAP-84-10: CortexIntelligenceIntegration must NOT be an empty stub.
        """
        ii_file = CORTEX_SRC / "tools" / "cortex_intelligence_integration.py"
        assert ii_file.exists(), f"File not found: {ii_file}"

        content = ii_file.read_text(encoding="utf-8")
        lines = [l.strip() for l in content.splitlines() if l.strip() and not l.strip().startswith("#")]

        assert len(lines) > 25, (
            f"GAP-84-10 REGRESSION: CortexIntelligenceIntegration is still a stub "
            f"({len(lines)} lines). Must delegate to UnifiedIntelligenceProvider."
        )

    # ── GAP-84-11: RegistryBackedOrchestratorRegistry ───────────────────────
    def test_gap_11_registry_backed_registry_not_empty(self) -> None:
        """
        GAP-84-11: RegistryBackedOrchestratorRegistry must NOT be an empty stub.
        """
        rr_file = CORTEX_SRC / "core" / "wiring" / "registry_backed_orchestrator_registry.py"
        assert rr_file.exists(), f"File not found: {rr_file}"

        content = rr_file.read_text(encoding="utf-8")
        lines = [l.strip() for l in content.splitlines() if l.strip() and not l.strip().startswith("#")]

        assert len(lines) > 35, (
            f"GAP-84-11 REGRESSION: RegistryBackedOrchestratorRegistry is still a stub "
            f"({len(lines)} lines). Must load from cortex-registry/core/specifications/."
        )


# ═══════════════════════════════════════════════════════════════════════════════
# SWEEP 3 — Stub Orchestrator Resolution (GAPs 12-17, 22-24)
# ═══════════════════════════════════════════════════════════════════════════════

class TestStubOrchestratorResolution:
    """
    Permanence tests verifying no orchestrator file has 'stub' in its docstring.
    Each test scans a specific directory for the pattern.
    """

    @staticmethod
    def _find_stub_docstrings(directory: Path) -> List[str]:
        """Find .py files in directory whose docstrings contain 'stub' (case-insensitive)."""
        stub_files: List[str] = []
        if not directory.exists():
            return stub_files

        for py_file in directory.rglob("*.py"):
            if py_file.name.startswith("__"):
                continue
            try:
                content = py_file.read_text(encoding="utf-8", errors="ignore")
                tree = ast.parse(content, filename=str(py_file))
            except (SyntaxError, UnicodeDecodeError):
                continue

            # Check module docstring
            docstring = ast.get_docstring(tree)
            if docstring and re.search(r"\bstub\b", docstring, re.IGNORECASE):
                stub_files.append(str(py_file.relative_to(PROJECT_ROOT)))

            # Check class docstrings
            for node in ast.walk(tree):
                if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                    ds = ast.get_docstring(node)
                    if ds and re.search(r"\bstub\b", ds, re.IGNORECASE):
                        rel = str(py_file.relative_to(PROJECT_ROOT))
                        if rel not in stub_files:
                            stub_files.append(rel)

        return stub_files

    # ── GAP-84-12 to GAP-84-17: Support/Domain/Intelligence orchestrators ──
    def test_gap_12_to_17_no_stub_orchestrators_in_support(self) -> None:
        """
        GAPs 12-14, 17: No orchestrator in cortex/orchestrators/support/ has 'stub' docstring.
        """
        stubs = self._find_stub_docstrings(CORTEX_SRC / "orchestrators" / "support")
        assert not stubs, (
            f"GAP-84-12/13/14/17 REGRESSION: {len(stubs)} stub orchestrator(s) in support/: {stubs}"
        )

    def test_gap_15_no_stub_orchestrators_in_intelligence(self) -> None:
        """
        GAP-84-15: No orchestrator in cortex/orchestrators/intelligence/ has 'stub' docstring.
        """
        stubs = self._find_stub_docstrings(CORTEX_SRC / "orchestrators" / "intelligence")
        assert not stubs, (
            f"GAP-84-15 REGRESSION: {len(stubs)} stub orchestrator(s) in intelligence/: {stubs}"
        )

    def test_gap_16_no_stub_orchestrators_in_domain(self) -> None:
        """
        GAP-84-16: No orchestrator in cortex/orchestrators/domain/ has 'stub' docstring.
        """
        stubs = self._find_stub_docstrings(CORTEX_SRC / "orchestrators" / "domain")
        assert not stubs, (
            f"GAP-84-16 REGRESSION: {len(stubs)} stub orchestrator(s) in domain/: {stubs}"
        )

    # ── GAP-84-22/23/24: Core support stubs ─────────────────────────────────
    def test_gap_22_semantic_ranking_not_stub(self) -> None:
        """GAP-84-22: SemanticRanking must not be labeled as stub."""
        sr_file = CORTEX_SRC / "orchestrators" / "core" / "semantic_ranking.py"
        if not sr_file.exists():
            pytest.skip("File removed (acceptable resolution)")
        content = sr_file.read_text(encoding="utf-8")
        lines = [l.strip() for l in content.splitlines() if l.strip() and not l.strip().startswith("#")]
        assert len(lines) > 25, (
            f"GAP-84-22 REGRESSION: SemanticRanking is still a stub ({len(lines)} lines)."
        )

    def test_gap_23_lens_context_provider_not_stub(self) -> None:
        """GAP-84-23: LensContextProvider must not be labeled as stub."""
        lcp_file = CORTEX_SRC / "orchestrators" / "core" / "lens_context_provider.py"
        if not lcp_file.exists():
            pytest.skip("File removed (acceptable resolution)")
        content = lcp_file.read_text(encoding="utf-8")
        lines = [l.strip() for l in content.splitlines() if l.strip() and not l.strip().startswith("#")]
        assert len(lines) > 30, (
            f"GAP-84-23 REGRESSION: LensContextProvider is still a stub ({len(lines)} lines)."
        )

    def test_gap_24_governance_principles_not_stub(self) -> None:
        """GAP-84-24: GovernancePrinciples must not be labeled as stub."""
        gp_file = CORTEX_SRC / "orchestrators" / "core" / "governance_principles.py"
        if not gp_file.exists():
            pytest.skip("File removed (acceptable resolution)")
        content = gp_file.read_text(encoding="utf-8")
        lines = [l.strip() for l in content.splitlines() if l.strip() and not l.strip().startswith("#")]
        assert len(lines) > 30, (
            f"GAP-84-24 REGRESSION: GovernancePrinciples is still a stub ({len(lines)} lines)."
        )


# ═══════════════════════════════════════════════════════════════════════════════
# SWEEP 4 — Silent Degradation & Feature Gaps (GAPs 18-21, 25-29)
# ═══════════════════════════════════════════════════════════════════════════════

class TestSilentDegradationFixes:
    """
    Permanence tests for observability and domain brain adapter implementations.
    """

    # ── GAP-84-18: AuditTrail persistence ────────────────────────────────────
    def test_gap_18_audit_trail_has_persistence(self) -> None:
        """GAP-84-18: AuditTrail must persist to SQLite, not just in-memory list."""
        at_file = CORTEX_SRC / "observability" / "audit_trail.py"
        assert at_file.exists(), f"AuditTrail not found: {at_file}"

        content = at_file.read_text(encoding="utf-8")

        has_persistence = any(
            keyword in content
            for keyword in ["sqlite3", "sqlite", "db_path", ".db", "database", "connect("]
        )
        assert has_persistence, (
            "GAP-84-18 REGRESSION: AuditTrail has no SQLite persistence. "
            "Events are lost on restart. Must persist to .cortex-runtime/."
        )

    # ── GAP-84-19: HealthMonitor real checks ─────────────────────────────────
    def test_gap_19_health_monitor_not_hardcoded_healthy(self) -> None:
        """GAP-84-19: HealthMonitor must NOT unconditionally return healthy."""
        hm_file = CORTEX_SRC / "observability" / "health_monitor.py"
        assert hm_file.exists(), f"HealthMonitor not found: {hm_file}"

        content = hm_file.read_text(encoding="utf-8")
        lines = [l.strip() for l in content.splitlines() if l.strip() and not l.strip().startswith("#")]

        assert len(lines) > 25, (
            f"GAP-84-19 REGRESSION: HealthMonitor is still a stub ({len(lines)} lines). "
            "Must perform real health checks."
        )

        # Should not have hardcoded healthy return
        hardcoded = (
            '"status": "healthy"' in content
            and "latency_ms" in content
            and content.count("return") <= 2  # Only 1-2 returns means always-pass
        )
        assert not hardcoded, (
            "GAP-84-19 REGRESSION: HealthMonitor still returns hardcoded healthy status."
        )

    # ── GAP-84-20: NLP package exports ───────────────────────────────────────
    def test_gap_20_nlp_package_not_empty(self) -> None:
        """GAP-84-20: cortex.intelligence.nlp must export at least one symbol."""
        nlp_init = CORTEX_SRC / "intelligence" / "nlp" / "__init__.py"
        if not nlp_init.exists():
            pytest.skip("NLP package removed (acceptable if capability moved)")

        content = nlp_init.read_text(encoding="utf-8")

        # __all__ should not be empty
        assert "__all__ = []" not in content, (
            "GAP-84-20 REGRESSION: cortex.intelligence.nlp.__all__ is empty. "
            "Must export at least EmbeddingCache or equivalent."
        )

    # ── GAP-84-21: Domain brain adapters ─────────────────────────────────────
    def test_gap_21_domain_brain_adapters_not_all_empty(self) -> None:
        """GAP-84-21: Domain brain adapters must NOT all return empty lists."""
        adapters_file = CORTEX_SRC / "intelligence" / "domain_brain" / "adapters.py"
        if not adapters_file.exists():
            pytest.skip("Adapters file removed (acceptable if consolidated)")

        content = adapters_file.read_text(encoding="utf-8")

        # Count "return []" occurrences — if all adapters return [], that's a stub
        empty_returns = content.count("return []")
        assert empty_returns <= 4, (
            f"GAP-84-21 REGRESSION: domain_brain/adapters.py has {empty_returns} 'return []' statements. "
            "Adapters must delegate to real data sources."
        )


class TestCLIAndProviderGaps:
    """
    Permanence tests for CLI commands and provider stubs.
    """

    # ── GAP-84-25: CLI onboard ───────────────────────────────────────────────
    def test_gap_25_cli_onboard_no_not_implemented(self) -> None:
        """GAP-84-25: CLI onboard command must not raise NotImplementedError."""
        onboard_file = CORTEX_SRC / "cli" / "commands" / "onboard.py"
        if not onboard_file.exists():
            pytest.skip("CLI onboard command not present")

        content = onboard_file.read_text(encoding="utf-8")
        assert "NotImplementedError" not in content, (
            "GAP-84-25 REGRESSION: CLI onboard command still raises NotImplementedError."
        )

    # ── GAP-84-26: CLI lens ──────────────────────────────────────────────────
    def test_gap_26_cli_lens_no_not_implemented(self) -> None:
        """GAP-84-26: CLI lens command must not raise NotImplementedError."""
        lens_file = CORTEX_SRC / "cli" / "commands" / "lens.py"
        if not lens_file.exists():
            pytest.skip("CLI lens command not present")

        content = lens_file.read_text(encoding="utf-8")
        assert "NotImplementedError" not in content, (
            "GAP-84-26 REGRESSION: CLI lens command still raises NotImplementedError."
        )

    # ── GAP-84-27: CLI governance ────────────────────────────────────────────
    def test_gap_27_cli_governance_no_not_implemented(self) -> None:
        """GAP-84-27: CLI governance command must not raise NotImplementedError."""
        # Could be in __main__.py or commands/governance.py
        cli_main = CORTEX_SRC / "cli" / "__main__.py"
        if not cli_main.exists():
            pytest.skip("CLI __main__ not present")

        content = cli_main.read_text(encoding="utf-8")
        # Check for NotImplementedError near 'governance'
        lines = content.splitlines()
        for i, line in enumerate(lines):
            if "governance" in line.lower() and i + 5 < len(lines):
                context = "\n".join(lines[i : i + 5])
                assert "NotImplementedError" not in context, (
                    "GAP-84-27 REGRESSION: CLI governance command still raises NotImplementedError."
                )

    # ── GAP-84-28: WorkItemProvider ──────────────────────────────────────────
    def test_gap_28_work_item_provider_no_not_implemented(self) -> None:
        """GAP-84-28: WorkItemProvider must not raise NotImplementedError from public methods."""
        wip_file = CORTEX_SRC / "repositories" / "work_item_provider.py"
        if not wip_file.exists():
            pytest.skip("WorkItemProvider not present")

        content = wip_file.read_text(encoding="utf-8")
        not_impl_count = content.count("NotImplementedError")

        assert not_impl_count == 0, (
            f"GAP-84-28 REGRESSION: WorkItemProvider has {not_impl_count} NotImplementedError raises. "
            "Public methods must return empty results with log warning."
        )

    # ── GAP-84-29: Secrets provider docstrings ───────────────────────────────
    def test_gap_29_secrets_providers_no_stub_docstrings(self) -> None:
        """GAP-84-29: Secrets providers must not have 'stub' in docstrings."""
        providers_dir = CORTEX_SRC / "infrastructure" / "secrets" / "providers"
        if not providers_dir.exists():
            pytest.skip("Secrets providers directory not present")

        stub_providers: List[str] = []
        for py_file in providers_dir.glob("*.py"):
            if py_file.name.startswith("__"):
                continue
            content = py_file.read_text(encoding="utf-8", errors="ignore")
            if re.search(r"\bstub\b", content, re.IGNORECASE):
                stub_providers.append(py_file.name)

        assert not stub_providers, (
            f"GAP-84-29 REGRESSION: Secrets providers still labeled as stubs: {stub_providers}. "
            "Remove 'stub' from docstrings."
        )


# ═══════════════════════════════════════════════════════════════════════════════
# META-CHECK — Overall Stub Count Guard
# ═══════════════════════════════════════════════════════════════════════════════

class TestStubCountGuard:
    """
    Meta-check that prevents stub count from growing.
    Counts files with 'stub' in docstrings across production code.
    """

    ALLOWED_STUB_PATTERNS: Set[str] = {
        # These are LEGITIMATE stub references (e.g., test_stub_generator, StubAutoFixAgent)
        "testing/",  # Test framework may reference stubs
        "tests/",  # Test files may reference stubs
    }

    def test_production_stub_docstring_count_zero(self) -> None:
        """
        META-CHECK: After Phase 84, zero production files should have 'stub' in docstrings.

        This is the aggregate guard — individual GAP tests above catch specific files,
        this catches any NEW stubs introduced after Phase 84.
        """
        stub_files: List[str] = []

        for py_file in CORTEX_SRC.rglob("*.py"):
            if py_file.name.startswith("__"):
                continue

            rel_path = str(py_file.relative_to(PROJECT_ROOT))

            # Skip allowed patterns (test infrastructure)
            if any(pattern in rel_path for pattern in self.ALLOWED_STUB_PATTERNS):
                continue

            try:
                content = py_file.read_text(encoding="utf-8", errors="ignore")
                tree = ast.parse(content, filename=str(py_file))
            except (SyntaxError, UnicodeDecodeError):
                continue

            docstring = ast.get_docstring(tree)
            if docstring and re.search(r"\bstub\b", docstring, re.IGNORECASE):
                # Exclude files that DETECT stubs (e.g., StubAutoFixAgent)
                if "autofix" in py_file.name or "detector" in py_file.name:
                    continue
                stub_files.append(rel_path)

        assert not stub_files, (
            f"META-CHECK REGRESSION: {len(stub_files)} production file(s) still have 'stub' in module docstrings: "
            f"{stub_files[:10]}{'...' if len(stub_files) > 10 else ''}"
        )
