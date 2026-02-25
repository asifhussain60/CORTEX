"""
Phase 72-a — RED tests for CapabilityRegistryBuilder.

AC_START: AC-72-CAPABILITY-REGISTRY-BUILDER-20260225

Tests verify:
  GAP-72-01: builder scans live orchestrator source and produces a valid manifest
  GAP-72-05: builder removes cortex-registry/.inventory/ (wrong location)

All tests are intentionally RED until phase-72-a implementation is complete.
"""

import os
import pytest
import yaml
from pathlib import Path
from datetime import datetime, timezone


# ─────────────────────────────────────────────────────────────────────────────
# Import guard — provides clear RED signal before implementation exists
# ─────────────────────────────────────────────────────────────────────────────
try:
    from cortex.intelligence.capability_registry_builder import (
        CapabilityRegistryBuilder,
        BuilderResult,
        OrchestratorEntry,
        WorkflowTemplateEntry,
    )
    _IMPORT_OK = True
except ImportError:
    _IMPORT_OK = False


@pytest.mark.skipif(not _IMPORT_OK, reason="capability_registry_builder not yet implemented — RED phase")
class TestCapabilityRegistryBuilderImport:
    """Verify the module is importable and public API is present."""

    def test_builder_class_importable(self) -> None:
        """CapabilityRegistryBuilder must be importable from cortex.intelligence."""
        assert _IMPORT_OK, (
            "cortex.intelligence.capability_registry_builder not found — implement phase-72-a"
        )

    def test_builder_result_dataclass_exists(self) -> None:
        """BuilderResult dataclass must exist and have expected fields."""
        result = BuilderResult(
            orchestrators=[],
            workflow_templates=[],
            mcp_tools=[],
            generated_at="2026-02-25T00:00:00Z",
            schema_version="2.0",
        )
        assert result.schema_version == "2.0"
        assert result.orchestrators == []

    def test_orchestrator_entry_dataclass_exists(self) -> None:
        """OrchestratorEntry must capture id, module, class_name, tier, health_check."""
        entry = OrchestratorEntry(
            id="master_orchestrator",
            module="cortex.orchestrators.core.master_orchestrator",
            class_name="MasterOrchestrator",
            tier="core",
            health_check=True,
        )
        assert entry.tier == "core"
        assert entry.health_check is True


@pytest.mark.skipif(not _IMPORT_OK, reason="capability_registry_builder not yet implemented — RED phase")
class TestCapabilityRegistryBuilderScan:
    """GAP-72-01: builder scans live cortex/orchestrators/ and finds wired orchestrators."""

    @pytest.fixture
    def builder(self) -> "CapabilityRegistryBuilder":
        """Builder pointed at real workspace root."""
        root = Path(__file__).parent.parent.parent  # /CORTEX
        return CapabilityRegistryBuilder(workspace_root=root)

    def test_builder_scans_orchestrators_returns_list(self, builder: "CapabilityRegistryBuilder") -> None:
        """scan_orchestrators() must return a non-empty list of OrchestratorEntry objects."""
        entries = builder.scan_orchestrators()
        assert isinstance(entries, list), "scan_orchestrators() must return a list"
        assert len(entries) > 0, "Must find at least one orchestrator in cortex/orchestrators/"

    def test_builder_finds_at_least_27_orchestrators(self, builder: "CapabilityRegistryBuilder") -> None:
        """Must discover ≥27 orchestrators — the wired count per architecture spec."""
        entries = builder.scan_orchestrators()
        assert len(entries) >= 27, (
            f"Expected ≥27 wired orchestrators, found {len(entries)}. "
            "Check that scan_orchestrators() reads from wiring specs, not raw file count."
        )

    def test_builder_finds_master_orchestrator(self, builder: "CapabilityRegistryBuilder") -> None:
        """MasterOrchestrator must be in the scanned entries."""
        entries = builder.scan_orchestrators()
        ids = [e.id for e in entries]
        assert "master_orchestrator" in ids, (
            f"master_orchestrator not found in scanned entries: {ids[:10]}"
        )

    def test_builder_finds_intent_router(self, builder: "CapabilityRegistryBuilder") -> None:
        """IntentRouter must be in the scanned entries."""
        entries = builder.scan_orchestrators()
        ids = [e.id for e in entries]
        assert "intent_router" in ids, f"intent_router not found in {ids[:10]}"

    def test_builder_entries_have_required_fields(self, builder: "CapabilityRegistryBuilder") -> None:
        """Every OrchestratorEntry must have non-empty id, module, class_name, tier."""
        entries = builder.scan_orchestrators()
        for entry in entries:
            assert entry.id, f"Entry has empty id: {entry}"
            assert entry.module, f"Entry {entry.id} has empty module"
            assert entry.class_name, f"Entry {entry.id} has empty class_name"
            assert entry.tier in ("core", "domain", "support"), (
                f"Entry {entry.id} has invalid tier '{entry.tier}'"
            )

    def test_builder_count_matches_wiring_spec(self, builder: "CapabilityRegistryBuilder") -> None:
        """
        validate_against_wiring_spec() must return True when generated count
        is consistent with the wiring specs in cortex-registry/core/specifications/.
        """
        entries = builder.scan_orchestrators()
        is_valid, discrepancies = builder.validate_against_wiring_spec(entries)
        assert is_valid, (
            f"Wiring spec validation failed. Discrepancies: {discrepancies}"
        )


@pytest.mark.skipif(not _IMPORT_OK, reason="capability_registry_builder not yet implemented — RED phase")
class TestCapabilityRegistryBuilderGenerate:
    """GAP-72-01: generate_manifest() produces valid, auto-generated YAML at canonical path."""

    @pytest.fixture
    def builder_with_tmp_output(self, tmp_path: Path) -> "CapabilityRegistryBuilder":
        """Builder with real workspace root but output directed to tmp for safety."""
        root = Path(__file__).parent.parent.parent
        return CapabilityRegistryBuilder(workspace_root=root, output_path=tmp_path / "capabilities-manifest.yaml")

    def test_generate_manifest_returns_builder_result(
        self, builder_with_tmp_output: "CapabilityRegistryBuilder"
    ) -> None:
        """generate_manifest() must return a BuilderResult instance."""
        result = builder_with_tmp_output.generate_manifest()
        assert isinstance(result, BuilderResult), (
            f"generate_manifest() must return BuilderResult, got {type(result)}"
        )

    def test_generate_manifest_writes_valid_yaml(
        self, builder_with_tmp_output: "CapabilityRegistryBuilder", tmp_path: Path
    ) -> None:
        """Output YAML must be parseable with yaml.safe_load()."""
        builder_with_tmp_output.generate_manifest()
        output = tmp_path / "capabilities-manifest.yaml"
        assert output.exists(), "generate_manifest() must write the output file"
        content = yaml.safe_load(output.read_text())
        assert isinstance(content, dict), "Output must be a valid YAML mapping"

    def test_generated_manifest_has_schema_version_2(
        self, builder_with_tmp_output: "CapabilityRegistryBuilder", tmp_path: Path
    ) -> None:
        """Generated manifest must declare schema_version: '2.0'."""
        builder_with_tmp_output.generate_manifest()
        output = tmp_path / "capabilities-manifest.yaml"
        content = yaml.safe_load(output.read_text())
        assert content.get("schema_version") == "2.0", (
            f"Expected schema_version '2.0', got: {content.get('schema_version')}"
        )

    def test_generated_manifest_has_auto_generated_flag(
        self, builder_with_tmp_output: "CapabilityRegistryBuilder", tmp_path: Path
    ) -> None:
        """Generated manifest must have auto_generated: true."""
        builder_with_tmp_output.generate_manifest()
        output = tmp_path / "capabilities-manifest.yaml"
        content = yaml.safe_load(output.read_text())
        assert content.get("auto_generated") is True, (
            "Generated manifest must declare auto_generated: true"
        )

    def test_generated_manifest_has_iso_timestamp(
        self, builder_with_tmp_output: "CapabilityRegistryBuilder", tmp_path: Path
    ) -> None:
        """Generated manifest must have a generated_at ISO timestamp."""
        builder_with_tmp_output.generate_manifest()
        output = tmp_path / "capabilities-manifest.yaml"
        content = yaml.safe_load(output.read_text())
        ts = content.get("generated_at")
        assert ts, "Generated manifest must have generated_at field"
        # Must be parseable as ISO 8601
        try:
            datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
        except ValueError:
            pytest.fail(f"generated_at '{ts}' is not a valid ISO 8601 timestamp")

    def test_generated_manifest_has_orchestrators_section(
        self, builder_with_tmp_output: "CapabilityRegistryBuilder", tmp_path: Path
    ) -> None:
        """Generated manifest must contain an orchestrators section with members."""
        builder_with_tmp_output.generate_manifest()
        output = tmp_path / "capabilities-manifest.yaml"
        content = yaml.safe_load(output.read_text())
        orchestrators = content.get("orchestrators", {})
        assert "total" in orchestrators, "orchestrators section must have 'total' key"
        assert orchestrators["total"] >= 27, (
            f"orchestrators.total must be ≥27, got {orchestrators['total']}"
        )

    def test_generate_manifest_is_idempotent(
        self, builder_with_tmp_output: "CapabilityRegistryBuilder", tmp_path: Path
    ) -> None:
        """Running generate_manifest() twice must produce identical YAML (idempotent)."""
        builder_with_tmp_output.generate_manifest()
        first = (tmp_path / "capabilities-manifest.yaml").read_text()

        builder_with_tmp_output.generate_manifest()
        second = (tmp_path / "capabilities-manifest.yaml").read_text()

        # Ignore generated_at timestamp for idempotency check (will differ by ms)
        first_parsed = yaml.safe_load(first)
        second_parsed = yaml.safe_load(second)
        first_parsed.pop("generated_at", None)
        second_parsed.pop("generated_at", None)

        assert first_parsed == second_parsed, (
            "generate_manifest() must be idempotent — second run must not add duplicate sections"
        )


@pytest.mark.skipif(not _IMPORT_OK, reason="capability_registry_builder not yet implemented — RED phase")
class TestCapabilityRegistryBuilderInventoryCleanup:
    """GAP-72-05: builder removes cortex-registry/.inventory/ (wrong location)."""

    def test_remove_inventory_folder_when_exists(self, tmp_path: Path) -> None:
        """remove_inventory_folder() must delete the folder when it exists."""
        inventory = tmp_path / ".inventory"
        inventory.mkdir()
        assert inventory.exists()

        builder = CapabilityRegistryBuilder(workspace_root=tmp_path)
        builder.remove_inventory_folder()

        assert not inventory.exists(), (
            "remove_inventory_folder() must delete cortex-registry/.inventory/ when present"
        )

    def test_remove_inventory_folder_is_safe_when_absent(self, tmp_path: Path) -> None:
        """remove_inventory_folder() must not raise when folder is already absent."""
        builder = CapabilityRegistryBuilder(workspace_root=tmp_path)
        try:
            builder.remove_inventory_folder()  # must not raise
        except Exception as exc:
            pytest.fail(f"remove_inventory_folder() raised unexpectedly: {exc}")

    def test_remove_inventory_folder_only_removes_empty_inventory(self, tmp_path: Path) -> None:
        """
        Safety guard: remove_inventory_folder() must only target
        cortex-registry/.inventory/ — not any other directory.
        A non-.inventory folder adjacent must be untouched.
        """
        inventory = tmp_path / ".inventory"
        inventory.mkdir()
        sibling = tmp_path / "core"
        sibling.mkdir()

        builder = CapabilityRegistryBuilder(workspace_root=tmp_path)
        builder.remove_inventory_folder()

        assert not inventory.exists(), ".inventory/ must be removed"
        assert sibling.exists(), "core/ sibling must NOT be touched"


# ─────────────────────────────────────────────────────────────────────────────
# Standalone RED signal — runs even before import succeeds
# ─────────────────────────────────────────────────────────────────────────────
class TestPhase72RedSignal:
    """
    These tests always run and fail until the module is created.
    They are the canonical RED signal for Phase 72-a (CORE-008).
    """

    def test_capability_registry_builder_module_exists(self) -> None:
        """
        cortex/intelligence/capability_registry_builder.py must exist.
        This is the RED gate — fails until phase-72-a implementation is written.
        """
        module_path = (
            Path(__file__).parent.parent.parent
            / "cortex" / "intelligence" / "capability_registry_builder.py"
        )
        assert module_path.exists(), (
            f"Phase 72-a RED: {module_path} does not exist yet. "
            "Write the implementation to turn this GREEN."
        )

    def test_capability_registry_builder_importable(self) -> None:
        """
        from cortex.intelligence.capability_registry_builder import CapabilityRegistryBuilder
        must succeed without ImportError.
        """
        assert _IMPORT_OK, (
            "Phase 72-a RED: CapabilityRegistryBuilder cannot be imported. "
            "Implement cortex/intelligence/capability_registry_builder.py."
        )
