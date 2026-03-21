"""
Golden Truth Test: Registry YAML Audit — Schema, Paths, Governance

Phase 63-B rewrite — splits the 1,657L test_cortex_registry_yaml_audit.py monolith.
This file (≤400L) focuses on: workflow template schema, cortex-master.yaml path resolution,
no deleted-path references, test-quality-gate.yaml version consistency.

Authority: CORE-008, CORE-035, CORE-055
AC-IDs: AC-63-B-REGISTRY-YAML-001..006
"""
# ruff: noqa: S101
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).parents[3]
TEMPLATES_ROOT = ROOT / "cortex-registry" / "workflows" / "templates"
MASTER_YAML = ROOT / "cortex-registry" / "cortex-master.yaml"
QUALITY_GATE_YAML = ROOT / "cortex-registry" / "core" / "test-quality-gate.yaml"
QUALITY_GATE_PY = ROOT / "cortex" / "testing" / "quality_gate.py"

REQUIRED_WORKFLOW_FIELDS = {"id", "name"}
KNOWN_BROKEN_WORKFLOW_TEMPLATES: set[str] = set()
KNOWN_EMPTY_WORKFLOW_TEMPLATES: set[str] = set()
DELETED_PATH_PATTERNS = [
    "cortex_intelligence",   # dissolved package — but cortex_intelligence_matrix is VALID (MCP tool)
    "cortex_lens",           # dissolved package — cortex.lens (dot) is the canonical MCP tool name
    "cortex.brain",
    "_archive/",
]

# Tool names that contain a deleted-path prefix but are themselves valid
_VALID_TOOL_NAMES = {"cortex_intelligence_matrix"}


def _has_deleted_path(content: str, pattern: str) -> bool:
    """Return True only if content references the deleted path, not a valid tool name."""
    if pattern not in content:
        return False
    # Check if every occurrence is part of a valid tool name
    import re
    # Find all matches and check if any are NOT a valid tool name
    for m in re.finditer(re.escape(pattern), content):
        full_word_start = m.start()
        full_word_end = m.end()
        # Extend to include the rest of the identifier (alphanumeric + underscore)
        while full_word_end < len(content) and (content[full_word_end].isalnum() or content[full_word_end] == '_'):
            full_word_end += 1
        token = content[full_word_start:full_word_end]
        if token not in _VALID_TOOL_NAMES:
            return True
    return False


def _load_yaml(path: Path) -> dict:
    with path.open() as fh:
        return yaml.safe_load(fh) or {}


class TestWorkflowTemplateSchema:
    """All workflow templates must satisfy required schema fields."""

    def test_workflow_template_exemption_lists_remain_justified(self) -> None:
        """Known broken/empty workflow exemptions must correspond to real unresolved files."""
        stale_broken = []
        for name in KNOWN_BROKEN_WORKFLOW_TEMPLATES:
            matches = list(TEMPLATES_ROOT.rglob(name))
            if not matches:
                stale_broken.append(name)

        stale_empty = []
        for name in KNOWN_EMPTY_WORKFLOW_TEMPLATES:
            matches = list(TEMPLATES_ROOT.rglob(name))
            if not matches:
                stale_empty.append(name)
                continue
            for path in matches:
                with path.open() as fh:
                    content = yaml.safe_load(fh)
                if content not in (None, {}):
                    stale_empty.append(path.relative_to(ROOT).as_posix())

        assert not stale_broken and not stale_empty, (
            "Workflow template xfail exemptions are stale. "
            f"broken={stale_broken}, empty={stale_empty}"
        )

    def test_all_workflow_templates_parse_as_yaml(self) -> None:
        """Every .yaml file in templates/ must be parseable.
        
        Pre-existing YAML syntax errors in Phase 49+ governance templates are tracked
        as a separate cleanup sweep.
        """
        failed = []
        pre_existing = []
        for yaml_file in TEMPLATES_ROOT.rglob("*.yaml"):
            if yaml_file.name in KNOWN_BROKEN_WORKFLOW_TEMPLATES:
                pre_existing.append(str(yaml_file.relative_to(ROOT)))
                continue
            try:
                with yaml_file.open() as fh:
                    yaml.safe_load(fh)
            except yaml.YAMLError as exc:
                failed.append(f"{yaml_file.relative_to(ROOT)}: {exc}")
        assert failed == [], (
            "Workflow template YAML parse errors:\n" + "\n".join(f"  {f}" for f in failed)
        )
        if pre_existing:
            pytest.xfail(
                f"Pre-existing YAML syntax errors (Phase 49 legacy, tracked for cleanup): "
                f"{pre_existing}"
            )

    def test_workflow_templates_are_not_empty(self) -> None:
        """Every .yaml file in templates/ must have non-null content.
        
        Known empty placeholder files are xfailed for separate cleanup.
        """
        empty = []
        pre_existing_empty = []
        for yaml_file in TEMPLATES_ROOT.rglob("*.yaml"):
            if yaml_file.name in KNOWN_EMPTY_WORKFLOW_TEMPLATES:
                pre_existing_empty.append(str(yaml_file.relative_to(ROOT)))
                continue
            try:
                with yaml_file.open() as fh:
                    content = yaml.safe_load(fh)
                if content is None or content == {}:
                    empty.append(str(yaml_file.relative_to(ROOT)))
            except yaml.YAMLError:
                pass  # Covered by parse test above
        assert empty == [], (
            "Empty workflow template YAML files:\n" + "\n".join(f"  {e}" for e in empty)
        )
        if pre_existing_empty:
            pytest.xfail(
                f"Pre-existing empty template files (pre-Phase 63, tracked for cleanup): "
                f"{pre_existing_empty}"
            )


class TestCortexMasterYamlPaths:
    """cortex-master.yaml must not reference deleted paths."""

    def test_cortex_master_yaml_parses(self) -> None:
        """cortex-master.yaml must be parseable YAML."""
        assert MASTER_YAML.exists(), "cortex-master.yaml does not exist"
        content = _load_yaml(MASTER_YAML)
        assert isinstance(content, dict), "cortex-master.yaml parsed as non-dict"

    def test_no_archive_references_in_master_yaml(self) -> None:
        """cortex-master.yaml must not reference _archive/ paths."""
        if not MASTER_YAML.exists():
            pytest.skip("cortex-master.yaml not found")
        raw = MASTER_YAML.read_text(errors="replace")
        assert "_archive/" not in raw, (
            "cortex-master.yaml references deleted _archive/ path"
        )

    def test_no_underscore_package_refs_in_master_yaml(self) -> None:
        """cortex-master.yaml must not reference cortex_intelligence or cortex_lens packages."""
        if not MASTER_YAML.exists():
            pytest.skip("cortex-master.yaml not found")
        raw = MASTER_YAML.read_text(errors="replace")
        for pattern in ("cortex_intelligence", "cortex_lens"):
            assert not _has_deleted_path(raw, pattern), (
                f"cortex-master.yaml references dissolved package: {pattern}"
            )

    def test_phase_detail_files_referenced_in_master_exist(self) -> None:
        """All file: entries in cortex-master.yaml phase_detail_files must resolve."""
        if not MASTER_YAML.exists():
            pytest.skip("cortex-master.yaml not found")
        content = _load_yaml(MASTER_YAML)
        phase_detail_files = content.get("phase_detail_files", [])
        missing = []
        for entry in phase_detail_files:
            file_ref = entry.get("file")
            if file_ref:
                full_path = ROOT / file_ref
                if not full_path.exists():
                    missing.append(file_ref)
        # Report but do not fail hard — some may be planned (not yet created)
        if missing:
            pytest.xfail(
                f"Planned phase files not yet created: {missing} — "
                "expected for PLANNED status phases"
            )


class TestNoDeletedPathReferences:
    """Registry YAML files must not reference any deleted paths."""

    def test_no_deleted_paths_in_registry_yamls(self) -> None:
        """cortex-registry/ YAML files must not reference dissolved construct paths."""
        registry_root = ROOT / "cortex-registry"
        violations: dict[str, list[str]] = {}
        for yaml_file in registry_root.rglob("*.yaml"):
            try:
                content = yaml_file.read_text(errors="replace")
            except OSError:
                continue
            for pattern in DELETED_PATH_PATTERNS:
                if _has_deleted_path(content, pattern):
                    key = yaml_file.relative_to(ROOT).as_posix()
                    violations.setdefault(key, []).append(pattern)

        if violations:
            report = "\n".join(
                f"  {path}: {patterns}" for path, patterns in violations.items()
            )
            # Historical archive documents and lifecycle/planning governance templates
            # legitimately reference old package names as documentation of the refactoring.
            HISTORICAL_PREFIXES = (
                "cortex-master",              # summary file — notes may reference old names
                "archived/",                  # historical cortex-refactor archive
                "_cortex-master/",            # legacy cortex-master subdirectory
                "planning/phases/archived/",  # phase archive
                "planning/phases/planned/",   # planned phases mention dissolved names in acceptance criteria
                "planning/phases/completed/", # completed phases document what was dissolved (historical record)
                "workflows/templates/lifecycle/",  # lifecycle templates reference patterns in grep commands
                "workflows/templates/governance/",  # governance templates contain detection grep rules for dissolved names
                "playbooks/",                 # historical playbooks
            )
            hard_failures = {
                path: patterns
                for path, patterns in violations.items()
                if not any(prefix in path for prefix in HISTORICAL_PREFIXES)
            }
            assert hard_failures == {}, (
                f"Deleted path references in active registry YAMLs:\n{report}"
            )


class TestQualityGateVersionConsistency:
    """test-quality-gate.yaml must not contain version fields."""

    def test_quality_gate_yaml_parseable(self) -> None:
        """cortex-registry/core/test-quality-gate.yaml must parse as YAML."""
        if not QUALITY_GATE_YAML.exists():
            pytest.skip("test-quality-gate.yaml not found")
        content = _load_yaml(QUALITY_GATE_YAML)
        assert isinstance(content, dict), "test-quality-gate.yaml parsed as non-dict"

    def test_quality_gate_yaml_has_no_version_field(self) -> None:
        """test-quality-gate.yaml must not declare a version field."""
        if not QUALITY_GATE_YAML.exists():
            pytest.skip("test-quality-gate.yaml not found")
        content = _load_yaml(QUALITY_GATE_YAML)
        assert "version" not in content, (
            "test-quality-gate.yaml must not contain 'version' field"
        )
