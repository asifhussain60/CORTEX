"""
Phase 106-C: Stage 9 Test Tier Upgrade — Golden Tests (CORE-008 RED cycle)
Authority: GAP-106-03 — Stage 9 test gate runs preflight only, golden tests excluded
SSOT: cortex-registry/planning/phases/planned/phase-106-rca-guard-certification.yaml

Tests validate that audit-fix-pipeline.yaml Stage 9 uses T1_smoke (not T0_preflight)
and that test-tier-manifest.yaml reflects the updated Stage 9 tier.
"""
from pathlib import Path

import pytest

WORKSPACE = Path(__file__).resolve().parents[3]
PIPELINE_PATH = (
    WORKSPACE
    / "cortex-registry"
    / "workflows"
    / "templates"
    / "audit"
    / "audit-fix-pipeline.yaml"
)
TIER_MANIFEST_PATH = (
    WORKSPACE
    / "cortex-registry"
    / "workflows"
    / "templates"
    / "testing"
    / "test-tier-manifest.yaml"
)


class TestAuditStage9TierGolden:
    """Phase 106-C: 2 golden tests for Stage 9 test tier upgrade."""

    def test_stage_9_uses_smoke_tier(self) -> None:
        """GAP-106-03: audit-fix-pipeline.yaml Stage 9 must use 'smoke' not 'preflight'."""
        assert PIPELINE_PATH.exists(), f"Pipeline missing: {PIPELINE_PATH}"
        content = PIPELINE_PATH.read_text()

        # Find Stage 9 block
        assert "stage_id: 'stage_9'" in content or 'stage_id: "stage_9"' in content, (
            "Stage 9 block not found in audit-fix-pipeline.yaml"
        )

        stage9_idx = content.index("stage_id: 'stage_9'") if "stage_id: 'stage_9'" in content else content.index('stage_id: "stage_9"')
        # Read ~200 chars to find the test command
        stage9_block = content[stage9_idx : stage9_idx + 800]

        assert "run_tests.py smoke" in stage9_block or "scripts/run_tests.py smoke" in stage9_block, (
            "audit-fix-pipeline.yaml Stage 9 must use 'python3 scripts/run_tests.py smoke'.\n"
            f"Current Stage 9 block:\n{stage9_block[:300]}\n\n"
            "Phase 106-C: Change Stage 9 command from 'preflight' to 'smoke'."
        )

    def test_stage_9_includes_golden_dirs(self) -> None:
        """GAP-106-03: test-tier-manifest.yaml T1_smoke must include tests/golden/ directory."""
        assert TIER_MANIFEST_PATH.exists(), f"test-tier-manifest.yaml missing: {TIER_MANIFEST_PATH}"
        content = TIER_MANIFEST_PATH.read_text()

        import yaml  # type: ignore[import]
        manifest = yaml.safe_load(content)
        assert manifest is not None, "test-tier-manifest.yaml must not be empty"

        # Find T1_smoke tier
        tiers = manifest.get("tiers", manifest.get("test_tiers", {}))
        t1 = tiers.get("T1_smoke") or tiers.get("smoke")
        assert t1 is not None, "T1_smoke tier not found in test-tier-manifest.yaml"

        # T1_smoke must include tests/golden/
        t1_str = str(t1)
        assert "golden" in t1_str, (
            "T1_smoke tier in test-tier-manifest.yaml must include tests/golden/ directory.\n"
            f"Current T1_smoke: {t1_str[:300]}"
        )
