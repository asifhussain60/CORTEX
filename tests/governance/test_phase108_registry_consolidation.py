"""
tests/governance/test_phase108_registry_consolidation.py

Phase 108 — cortex-registry Consolidation acceptance tests.
GAPs: 108-03, 108-04, 108-05# ─────────────────────────────────────────────────────────────────────────────
# GAP-108-06  plans/ — SKIPPED: live runtime store (interaction_plan_store.py writes here)
# ─────────────────────────────────────────────────────────────────────────────
# plans/ contains only .gitkeep + README at commit time but is written at runtime
# by cortex/orchestrators/core/interaction_plan_store.py.
# GAP-108-06 marked SKIPPED — not a dead dir.
# ─────────────────────────────────────────────────────────────────────────────8-07, 108-08, 108-10

TDD: These tests are written RED-first, then made GREEN by the consolidation work.
Authority: SWEEP-108-REGISTRY-CONSOLIDATION | Phase 108-B/C/D
"""
from __future__ import annotations

import pathlib

import pytest

REGISTRY = pathlib.Path(__file__).parents[2] / "cortex-registry"


# ─────────────────────────────────────────────────────────────────────────────
# GAP-108-03  knowledge/ merged into knowledge/
# ─────────────────────────────────────────────────────────────────────────────

class TestKnowledgeNamespaceMerge:
    """GAP-108-03: knowledge-base/ renamed/absorbed into knowledge/."""

    def test_no_knowledge_base_dir(self) -> None:
        """knowledge-base/ (old name) must not exist after rename to knowledge/."""
        assert not (REGISTRY / "knowledge-base").exists(), (
            "cortex-registry/knowledge-base/ still exists — should have been renamed to knowledge/ (GAP-108-03)"
        )

    def test_knowledge_has_profiles(self) -> None:
        """knowledge/profiles/ must exist with content from knowledge/profiles/."""
        profiles = REGISTRY / "knowledge" / "profiles"
        assert profiles.exists(), "knowledge/profiles/ missing"
        yaml_files = list(profiles.glob("*.yaml"))
        assert len(yaml_files) >= 7, (
            f"Expected ≥7 profile YAMLs in knowledge/profiles/, got {len(yaml_files)}"
        )

    def test_knowledge_has_repositories(self) -> None:
        """knowledge/repositories/ must exist with content from knowledge/repositories/."""
        repos = REGISTRY / "knowledge" / "repositories"
        assert repos.exists(), "knowledge/repositories/ missing"
        yaml_files = list(repos.glob("*.yaml"))
        assert len(yaml_files) >= 3, (
            f"Expected ≥3 repo YAMLs in knowledge/repositories/, got {len(yaml_files)}"
        )

    def test_knowledge_security_has_owasp(self) -> None:
        """knowledge/security/ must contain owasp-top10.yaml (from knowledge/security/)."""
        owasp = REGISTRY / "knowledge" / "security" / "owasp-top10.yaml"
        assert owasp.exists(), "knowledge/security/owasp-top10.yaml missing after merge"

    def test_knowledge_security_has_cicd_hardening(self) -> None:
        """knowledge/security/ must contain cicd-hardening.yaml (from knowledge/security/)."""
        cicd = REGISTRY / "knowledge" / "security" / "cicd-hardening.yaml"
        assert cicd.exists(), "knowledge/security/cicd-hardening.yaml missing after merge"

    def test_knowledge_architecture_has_best_practices(self) -> None:
        """knowledge/architecture/ must contain architecture-best-practices.yaml."""
        arch = REGISTRY / "knowledge" / "architecture" / "architecture-best-practices.yaml"
        assert arch.exists(), "knowledge/architecture/architecture-best-practices.yaml missing"


# ─────────────────────────────────────────────────────────────────────────────
# GAP-108-04  governance triple-namespace → single governance/
# ─────────────────────────────────────────────────────────────────────────────

class TestGovernanceNamespaceMerge:
    """GAP-108-04: core/governance/ and knowledge/governance/ merged into governance/."""

    def test_no_core_governance_dir(self) -> None:
        """core/governance/ must not exist after merge."""
        assert not (REGISTRY / "core" / "governance").exists(), (
            "cortex-registry/core/governance/ still exists — merge into governance/ (GAP-108-04)"
        )

    def test_governance_has_kernel(self) -> None:
        """governance/governance-kernel.yaml must exist (from core/governance/)."""
        kernel = REGISTRY / "governance" / "governance-kernel.yaml"
        assert kernel.exists(), "governance/governance-kernel.yaml missing after merge"

    def test_governance_has_violation_patterns(self) -> None:
        """governance/violation_patterns.yaml must exist (from core/governance/)."""
        vp = REGISTRY / "governance" / "violation_patterns.yaml"
        assert vp.exists(), "governance/violation_patterns.yaml missing after merge"

    def test_governance_has_duplicate_detection(self) -> None:
        """governance/duplicate_detection_schedule.yaml must exist (from core/governance/)."""
        dd = REGISTRY / "governance" / "duplicate_detection_schedule.yaml"
        assert dd.exists(), "governance/duplicate_detection_schedule.yaml missing after merge"

    def test_governance_has_compliance_rules(self) -> None:
        """governance/compliance-rules.yaml must exist (from knowledge/governance/)."""
        cr = REGISTRY / "governance" / "compliance-rules.yaml"
        assert cr.exists(), "governance/compliance-rules.yaml missing after merge"

    def test_governance_has_security_rules(self) -> None:
        """governance/security-rules.yaml must exist (from knowledge/governance/)."""
        sr = REGISTRY / "governance" / "security-rules.yaml"
        assert sr.exists(), "governance/security-rules.yaml missing after merge"

    def test_governance_has_data_rules(self) -> None:
        """governance/data-rules.yaml must exist (from knowledge/governance/)."""
        dr = REGISTRY / "governance" / "data-rules.yaml"
        assert dr.exists(), "governance/data-rules.yaml missing after merge"

    def test_no_knowledge_base_governance_dir(self) -> None:
        """knowledge/governance/ must not exist after merge."""
        assert not (REGISTRY / "knowledge" / "governance").exists(), (
            "cortex-registry/knowledge/governance/ still exists — merge into governance/ (GAP-108-04)"
        )


# ─────────────────────────────────────────────────────────────────────────────
# GAP-108-05  config/ + core/config/ → single config/
# ─────────────────────────────────────────────────────────────────────────────

class TestConfigNamespaceMerge:
    """GAP-108-05: core/config/ merged into config/."""

    def test_no_core_config_dir(self) -> None:
        """core/config/ must not exist after merge."""
        assert not (REGISTRY / "core" / "config").exists(), (
            "cortex-registry/core/config/ still exists — merge into config/ (GAP-108-05)"
        )

    def test_config_has_file_naming_rules(self) -> None:
        """config/file-naming-rules.yaml must exist (from core/config/)."""
        fnr = REGISTRY / "config" / "file-naming-rules.yaml"
        assert fnr.exists(), "config/file-naming-rules.yaml missing after merge"

    def test_config_has_feature_flags(self) -> None:
        """config/feature-flags.yaml must exist (from core/config/)."""
        ff = REGISTRY / "config" / "feature-flags.yaml"
        assert ff.exists(), "config/feature-flags.yaml missing after merge"

    def test_config_has_system_configuration(self) -> None:
        """config/system-configuration.yaml must exist (from core/config/)."""
        sc = REGISTRY / "config" / "system-configuration.yaml"
        assert sc.exists(), "config/system-configuration.yaml missing after merge"

    def test_config_has_original_files(self) -> None:
        """Original config/ files (architecture-constants, modes, proprietary_terms, response-format) remain."""
        for fname in ["architecture-constants.yaml", "modes.yaml", "proprietary_terms.yaml", "response-format.yaml"]:
            f = REGISTRY / "config" / fname
            assert f.exists(), f"config/{fname} missing — original file should not be removed"


# ─────────────────────────────────────────────────────────────────────────────
# GAP-108-06  plans/ — SKIPPED: live runtime store (interaction_plan_store.py writes here)
# ─────────────────────────────────────────────────────────────────────────────
# plans/ contains only .gitkeep + README at commit time but is written at runtime
# by cortex/orchestrators/core/interaction_plan_store.py.
# GAP-108-06 marked SKIPPED — not a dead dir.
# ─────────────────────────────────────────────────────────────────────────────


# ─────────────────────────────────────────────────────────────────────────────
# GAP-108-08  integration/ merged into patterns/
# ─────────────────────────────────────────────────────────────────────────────

class TestIntegrationMerge:
    """GAP-108-08: integration/patterns/ (2 YAML files) merged into patterns/."""

    def test_no_integration_dir(self) -> None:
        """integration/ must not exist after merge."""
        assert not (REGISTRY / "integration").exists(), (
            "cortex-registry/integration/ still exists — merge 2 files into patterns/ (GAP-108-08)"
        )

    def test_patterns_has_registry(self) -> None:
        """patterns/_registry.yaml must exist (moved from integration/patterns/)."""
        reg = REGISTRY / "patterns" / "_registry.yaml"
        assert reg.exists(), "patterns/_registry.yaml missing after integration merge"

    def test_patterns_has_test_orchestrator(self) -> None:
        """patterns/test_orchestrator.yaml must exist (moved from integration/patterns/)."""
        to = REGISTRY / "patterns" / "test_orchestrator.yaml"
        assert to.exists(), "patterns/test_orchestrator.yaml missing after integration merge"


# ─────────────────────────────────────────────────────────────────────────────
# GAP-108-10  Python path references updated
# ─────────────────────────────────────────────────────────────────────────────

class TestPythonPathReferences:
    """GAP-108-10: No Python file may reference moved paths after consolidation."""

    def _python_files(self) -> list[pathlib.Path]:
        cortex_src = pathlib.Path(__file__).parents[2] / "cortex"
        return [
            f for f in cortex_src.rglob("*.py")
            if "__pycache__" not in str(f)
        ]

    def test_no_knowledge_base_runtime_refs(self) -> None:
        """No Python file may use the old cortex-registry/knowledge-base/ path (renamed to knowledge/)."""
        violations = []
        for f in self._python_files():
            text = f.read_text(encoding="utf-8", errors="ignore")
            lines = text.splitlines()
            for i, line in enumerate(lines, 1):
                stripped = line.strip()
                # Skip pure comments
                if stripped.startswith("#"):
                    continue
                if "cortex-registry/knowledge-base" in line:
                    violations.append(f"{f.relative_to(pathlib.Path(__file__).parents[2])}:{i}: {stripped}")
        assert not violations, (
            f"GAP-108-10: {len(violations)} runtime ref(s) to old cortex-registry/knowledge-base/ must be updated to cortex-registry/knowledge/:\n"
            + "\n".join(violations)
        )

    def test_no_core_config_runtime_refs(self) -> None:
        """No Python file may use cortex-registry/core/config/ as a runtime path constant."""
        violations = []
        for f in self._python_files():
            text = f.read_text(encoding="utf-8", errors="ignore")
            lines = text.splitlines()
            for i, line in enumerate(lines, 1):
                stripped = line.strip()
                if stripped.startswith("#"):
                    continue
                if "cortex-registry/core/config" in line:
                    violations.append(f"{f.relative_to(pathlib.Path(__file__).parents[2])}:{i}: {stripped}")
        assert not violations, (
            f"GAP-108-10: {len(violations)} runtime ref(s) to cortex-registry/core/config/ must be updated to cortex-registry/config/:\n"
            + "\n".join(violations)
        )

    def test_no_integration_patterns_runtime_refs(self) -> None:
        """No Python file may use cortex-registry/integration/patterns/ as a runtime path constant."""
        violations = []
        for f in self._python_files():
            text = f.read_text(encoding="utf-8", errors="ignore")
            lines = text.splitlines()
            for i, line in enumerate(lines, 1):
                stripped = line.strip()
                if stripped.startswith("#"):
                    continue
                if "cortex-registry/integration" in line:
                    violations.append(f"{f.relative_to(pathlib.Path(__file__).parents[2])}:{i}: {stripped}")
        assert not violations, (
            f"GAP-108-10: {len(violations)} runtime ref(s) to cortex-registry/integration/ must be updated to cortex-registry/patterns/:\n"
            + "\n".join(violations)
        )
