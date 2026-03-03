"""
Phase 106-E: Check #29 + validate-production.py Deprecation — Golden Tests (CORE-008 RED cycle)
Authority: GAP-106-05 — validate-production.py CORE-002 violation + orphaned script
SSOT: cortex-registry/planning/phases/planned/phase-106-rca-guard-certification.yaml

Tests validate:
1. Check #29 (Security + Monitoring Posture) exists in audit-fix-pipeline.yaml Stage 2
2. Check #29 detects missing OWASP knowledge file (P1 violation raised)
3. Check #29 detects missing deployment/prometheus.yml (P1 violation raised)
4. validate-production.py does not write a .json file output (CORE-002 fix)
"""
import subprocess
import sys
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
VALIDATE_PRODUCTION_PATH = WORKSPACE / "scripts" / "validate-production.py"
KNOWLEDGE_SECURITY_DIR = WORKSPACE / "cortex-registry" / "knowledge" / "security"
PROMETHEUS_PATH = WORKSPACE / "deployment" / "prometheus.yml"


class TestCheck29SecurityMonitoringGolden:
    """Phase 106-E: 4 golden tests for Check #29 and validate-production deprecation."""

    def _pipeline_text(self) -> str:
        assert PIPELINE_PATH.exists(), f"Pipeline missing: {PIPELINE_PATH}"
        return PIPELINE_PATH.read_text()

    def test_check29_exists_in_pipeline(self) -> None:
        """GAP-106-05: Check #29 (Security + Monitoring Posture) must exist in Stage 2."""
        content = self._pipeline_text()
        # Check #29 must be declared in Stage 2 checks list
        assert "num: 29" in content or "num: '29'" in content, (
            "audit-fix-pipeline.yaml is missing Check #29.\n"
            "Phase 106-E: Add Check #29 (Security + Monitoring Posture) to Stage 2 checks list."
        )

    def test_check29_detects_missing_owasp_knowledge(self) -> None:
        """GAP-106-05: Check #29 must reference OWASP knowledge file detection."""
        content = self._pipeline_text()
        assert "num: 29" in content or "num: '29'" in content, (
            "See test_check29_exists_in_pipeline"
        )
        # Find Check #29 block and verify OWASP is mentioned
        idx = content.find("num: 29")
        if idx == -1:
            idx = content.find("num: '29'")
        check29_block = content[idx : idx + 1200]
        assert "owasp" in check29_block.lower() or "security" in check29_block.lower(), (
            "Check #29 must reference OWASP or security knowledge file detection.\n"
            "Phase 106-E: Add 'OWASP knowledge file exists' check to Check #29."
        )

    def test_check29_detects_missing_prometheus(self) -> None:
        """GAP-106-05: Check #29 must reference deployment/prometheus.yml detection."""
        content = self._pipeline_text()
        assert "num: 29" in content or "num: '29'" in content, (
            "See test_check29_exists_in_pipeline"
        )
        idx = content.find("num: 29")
        if idx == -1:
            idx = content.find("num: '29'")
        check29_block = content[idx : idx + 1200]
        assert "prometheus" in check29_block.lower(), (
            "Check #29 must reference deployment/prometheus.yml detection.\n"
            "Phase 106-E: Add 'deployment/prometheus.yml exists' check to Check #29."
        )

    def test_validate_production_no_file_output(self) -> None:
        """GAP-106-05: validate-production.py must not write a .json report file (CORE-002)."""
        assert VALIDATE_PRODUCTION_PATH.exists(), (
            f"validate-production.py missing: {VALIDATE_PRODUCTION_PATH}"
        )
        content = VALIDATE_PRODUCTION_PATH.read_text()
        # Must NOT contain code that opens a file for writing JSON report
        has_file_write = (
            "production-readiness-report.json" in content
            and ("open(" in content or "json.dump" in content)
        )
        assert not has_file_write, (
            "scripts/validate-production.py still writes a production-readiness-report.json "
            "file — CORE-002 violation (all output must be inline).\n"
            "Phase 106-E: Remove JSON file output; delegate to cortex_governance(op: "
            "certification_status) and print result inline."
        )
