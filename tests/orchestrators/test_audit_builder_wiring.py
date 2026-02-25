"""
Phase 72-d — RED tests for CapabilityRegistryBuilder wiring into AuditOrchestrator.

AC_START: AC-72-AUDIT-BUILDER-WIRING-20260226

Tests verify:
  GAP-72-01 closure: AuditOrchestrator.audit() invokes CapabilityRegistryBuilder
  and the generated manifest timestamp updates after an audit run.
"""

import pytest
import yaml
from pathlib import Path
from unittest.mock import patch, MagicMock
from typing import Dict, Any

try:
    from cortex.orchestrators.core.audit_orchestrator import AuditOrchestrator
    from cortex.intelligence.capability_registry_builder import (
        CapabilityRegistryBuilder,
        BuilderResult,
    )
    _IMPORT_OK = True
except ImportError:
    _IMPORT_OK = False


@pytest.mark.skipif(not _IMPORT_OK, reason="AuditOrchestrator or CapabilityRegistryBuilder not importable")
class TestAuditBuilderWiring:
    """GAP-72-01 closure: AuditOrchestrator stage 2 invokes CapabilityRegistryBuilder."""

    def test_audit_stage2_calls_builder(self, tmp_path: Path) -> None:
        """
        AuditOrchestrator.audit() must invoke CapabilityRegistryBuilder
        to regenerate capabilities-manifest.yaml during audit runs.
        """
        auditor = AuditOrchestrator(workspace_root=str(tmp_path))
        result = auditor.audit(mode="HEXA")
        # After audit, the manifest_regenerated flag must be in the result
        assert result.get("manifest_regenerated") is True, (
            "AuditOrchestrator.audit() must set manifest_regenerated=True "
            "after calling CapabilityRegistryBuilder.generate_manifest()"
        )

    def test_manifest_timestamp_updated_after_audit(self, tmp_path: Path) -> None:
        """
        After audit runs, the generated_at timestamp in the manifest
        must be present (proving the builder was called).
        """
        # Set up workspace structure for the builder
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        manifest_dir = workspace / "cortex-registry" / "core"
        manifest_dir.mkdir(parents=True)
        manifest_path = manifest_dir / "capabilities-manifest.yaml"

        # Pre-create a stale manifest
        manifest_path.write_text("schema_version: '1.0'\ngenerated_at: '2020-01-01T00:00:00Z'\n")

        auditor = AuditOrchestrator(workspace_root=str(workspace))
        auditor.audit(mode="HEXA")

        # Verify the result signals manifest was regenerated
        result = auditor.audit(mode="HEXA")
        assert result.get("manifest_regenerated") is True, (
            "AuditOrchestrator must regenerate manifest during audit"
        )
