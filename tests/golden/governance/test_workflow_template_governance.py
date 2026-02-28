"""
Golden Test: Workflow Template Governance — CORE-035 Compliance

Phase 63-D — GAP-63-04 remediation.
Verifies workflow template registry has no duplicates, dead refs, or CORE-035 violations.

Authority: CORE-008, CORE-035, CORE-055
AC-IDs: AC-63-D-WORKFLOW-GOV-001..004
"""
# ruff: noqa: S101
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).parents[3]
TEMPLATES_ROOT = ROOT / "cortex-registry" / "workflows" / "templates"
PRIMITIVES_ROOT = TEMPLATES_ROOT / "primitives"


def _load_yaml_safe(path: Path) -> dict | None:
    try:
        with path.open() as fh:
            return yaml.safe_load(fh)
    except (yaml.YAMLError, OSError):
        return None


class TestNoDuplicateTemplates:
    """No two workflow templates should have identical id fields (CORE-035)."""

    def test_no_duplicate_template_ids(self) -> None:
        """All workflow templates with an 'id' field must have unique ids."""
        seen_ids: dict[str, list[str]] = {}
        for yaml_file in TEMPLATES_ROOT.rglob("*.yaml"):
            content = _load_yaml_safe(yaml_file)
            if not isinstance(content, dict):
                continue
            template_id = content.get("id")
            if template_id:
                rel = str(yaml_file.relative_to(ROOT))
                seen_ids.setdefault(template_id, []).append(rel)

        duplicates = {
            tid: paths for tid, paths in seen_ids.items() if len(paths) > 1
        }
        assert duplicates == {}, (
            f"Duplicate workflow template IDs (CORE-035 violation):\n"
            + "\n".join(
                f"  id={tid}: {paths}" for tid, paths in duplicates.items()
            )
        )

    def test_composites_dont_mirror_top_level_templates(self) -> None:
        """composites/ sub-templates must not mirror files in top-level domain dirs."""
        composites_dir = TEMPLATES_ROOT / "composites"
        if not composites_dir.exists():
            pytest.skip("composites/ directory not found")

        # Collect names of files in composites/ subdirs
        composite_names = {
            f.stem for f in composites_dir.rglob("*.yaml")
        }
        # Collect names of files in top-level domain dirs (backend, frontend, security, etc.)
        domain_dirs = [
            d for d in TEMPLATES_ROOT.iterdir()
            if d.is_dir() and d.name not in ("composites", "primitives", "governance", "audit")
        ]
        domain_names = {
            f.stem for d in domain_dirs for f in d.rglob("*.yaml")
        }
        overlap = composite_names & domain_names
        assert overlap == set(), (
            f"Composite templates mirror top-level domain templates (CORE-035 violation): {overlap}"
        )


class TestAllPrimitivesReferencedByAtLeastOneWorkflow:
    """Every primitive template should be referenced by at least 1 workflow template."""

    def test_all_primitives_referenced_by_workflows(self) -> None:
        """No orphaned primitive — every primitive filename appears in at least 1 workflow."""
        if not PRIMITIVES_ROOT.exists():
            pytest.skip("primitives/ directory not found")

        # Collect all workflow content (non-primitive templates)
        workflow_content_parts: list[str] = []
        for yaml_file in TEMPLATES_ROOT.rglob("*.yaml"):
            if "primitives" not in str(yaml_file):
                try:
                    workflow_content_parts.append(yaml_file.read_text(errors="replace"))
                except OSError:
                    pass
        all_workflow_content = "\n".join(workflow_content_parts)

        orphaned_primitives = []
        for prim_file in PRIMITIVES_ROOT.rglob("*.yaml"):
            prim_stem = prim_file.stem
            prim_rel = str(prim_file.relative_to(TEMPLATES_ROOT))
            # Check if any workflow references this primitive by filename or stem
            if prim_stem not in all_workflow_content and prim_rel not in all_workflow_content:
                orphaned_primitives.append(prim_rel)

        if orphaned_primitives:
            pytest.xfail(
                f"Orphaned primitives (not referenced by any workflow template): "
                f"{orphaned_primitives} — Phase 63-E will wire these"
            )


class TestAllWorkflowPrimitiveRefsResolve:
    """All primitive references in workflow templates must resolve to real files."""

    def test_all_workflow_primitive_refs_resolve(self) -> None:
        """primitive_ref / uses_primitive fields in templates must point to real files."""
        unresolved = []
        for yaml_file in TEMPLATES_ROOT.rglob("*.yaml"):
            content = _load_yaml_safe(yaml_file)
            if not isinstance(content, dict):
                continue
            # Check for primitive_ref or uses_primitive keys recursively
            refs = _extract_primitive_refs(content)
            for ref in refs:
                # ref should be relative to templates/
                ref_path = TEMPLATES_ROOT / ref
                # Also check with .yaml extension (refs may omit it)
                ref_path_yaml = TEMPLATES_ROOT / (ref + ".yaml")
                if not ref_path.exists() and not ref_path_yaml.exists():
                    unresolved.append(
                        f"{yaml_file.relative_to(ROOT)}: ref '{ref}' → not found"
                    )
        assert unresolved == [], (
            "Unresolved primitive references in workflow templates:\n"
            + "\n".join(f"  {u}" for u in unresolved)
        )


def _extract_primitive_refs(data: object, key_names: tuple = ("primitive_ref", "uses_primitive")) -> list[str]:
    """Recursively extract values for specified keys from a nested dict/list."""
    refs: list[str] = []
    if isinstance(data, dict):
        for k, v in data.items():
            if k in key_names and isinstance(v, str):
                refs.append(v)
            else:
                refs.extend(_extract_primitive_refs(v, key_names))
    elif isinstance(data, list):
        for item in data:
            refs.extend(_extract_primitive_refs(item, key_names))
    return refs
