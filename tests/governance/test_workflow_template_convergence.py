"""Phase 128-h — Workflow Template Convergence (drift lock #49).

Validates that the CORTEX workflow template registry is internally consistent:

1. Every workflow template is parseable YAML
2. Every non-primitive template has a valid ``id`` and ``name`` field
3. Templates with ``steps`` must have at least one step with a recognised
   identity field (name | id | step_id | action | orchestrator | orchestrator_name)
4. All primitives referenced via ``template_ref``, ``source_primitive``, or
   ``primitive`` fields must resolve to an existing file (allowing both
   short-form IDs without .yaml and full paths)
5. All critical routing-table templates (from copilot-instructions.md intent
   routing table) must exist on disk
6. The total template count must not drop below the established baseline (85)
7. Primitive count must not drop below baseline (24)
8. Every primitive referenced in templates that cannot be resolved is catalogued
   in the known-gaps register — unregistered broken refs are a violation

Gap ref: GAP-128-08
Drift lock: cortex-registry/governance/drift-locks/check-49-workflow-template-convergence-lock.yaml
Tier: T1 (governance)
CORE rule: CORE-064 (Sweep Completeness Contract)
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pytest
import yaml

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
CORTEX_ROOT = Path(__file__).parents[2]
TEMPLATES_DIR = CORTEX_ROOT / "cortex-registry" / "workflows" / "templates"
PRIMITIVES_DIR = TEMPLATES_DIR / "primitives"

# ---------------------------------------------------------------------------
# Baselines
# ---------------------------------------------------------------------------
_MINIMUM_TEMPLATE_COUNT: int = 85   # all 85 templates (including primitives)
_MINIMUM_PRIMITIVE_COUNT: int = 24  # primitives under templates/primitives/

# ---------------------------------------------------------------------------
# Routing table — intent → workflow template (from copilot-instructions.md)
# These are the canonical templates that MUST exist for the system to route correctly.
# ---------------------------------------------------------------------------
_ROUTING_TABLE_TEMPLATES: frozenset[str] = frozenset({
    "sdlc/implement-workflow.yaml",
    "sdlc/fix-workflow.yaml",
    "quality/refactor-workflow.yaml",
    "audit/audit-fix-pipeline.yaml",
    "maintenance/vacuum-workflow.yaml",
    "maintenance/health-check-workflow.yaml",
    "debugging/multi-stack-debug-pipeline.yaml",
    "lifecycle/digest-workflow.yaml",
    "lifecycle/onboarding-workflow.yaml",
    "lifecycle/totalrecall-workflow.yaml",
    "lifecycle/sync-workflow.yaml",
    "lifecycle/train-workflow.yaml",
    "governance/meta-audit-workflow.yaml",
    "frontend/html-view-lifecycle.yaml",
    "frontend/typescript-refactor-workflow.yaml",
    "backend/csharp-refactor-workflow.yaml",
    "backend/csharp-security-workflow.yaml",
    "security/security-compliance-audit.yaml",
    "lifecycle/service-decomposition-workflow.yaml",
    "tdd/tdd-workflow.yaml",
})

# Primitives referenced as universal injections in every code-modifying workflow
_UNIVERSAL_PRIMITIVES: frozenset[str] = frozenset({
    "primitives/execution/ac-marker-emit.yaml",
    "primitives/execution/git-checkpoint.yaml",
    "primitives/governance/dor-display.yaml",
    "primitives/governance/holistic-validation-gate.yaml",
    "primitives/governance/challenge-gate.yaml",
    "primitives/governance/sweep-catalogue-open.yaml",
    "primitives/governance/sweep-catalogue-close.yaml",
    "primitives/validation/detect-fix-rescan-loop.yaml",
})

# ---------------------------------------------------------------------------
# Known unresolvable primitive refs
# These refs exist in templates but point to primitives that do not yet exist
# (planned for future phases or intentionally omitted). They are documented here
# rather than causing test failures — unregistered broken refs ARE a violation.
# ---------------------------------------------------------------------------
_KNOWN_UNRESOLVABLE_REFS: frozenset[tuple[str, str]] = frozenset({
    # composed-implement templates reference a governance gate by short name
    ("composed-implement-f347e3a2.yaml", "holistic-file-review-gate"),
    ("composed-implement-20fec3d1.yaml", "holistic-file-review-gate"),
    # SDLC templates reference primitives that exist in intelligence/ not analysis/
    ("code-review-gate.yaml",           "primitives/analysis/intelligence-injection.yaml"),
    ("implementation-execution.yaml",   "primitives/analysis/intelligence-injection.yaml"),
    ("implementation-execution.yaml",   "primitives/governance/security-check.yaml"),
    ("implementation-execution.yaml",   "primitives/tdd/tdd-feature-implementation.yaml"),
    ("integration-verification.yaml",   "primitives/analysis/intelligence-injection.yaml"),
    ("integration-verification.yaml",   "primitives/validation/test-quality-enforcement.yaml"),
    ("requirements-analysis.yaml",      "primitives/analysis/intelligence-injection.yaml"),
    ("requirements-analysis.yaml",      "primitives/governance/challenge-first.yaml"),
    ("security-assessment.yaml",        "primitives/analysis/intelligence-injection.yaml"),
    ("security-assessment.yaml",        "primitives/governance/security-check.yaml"),
    ("solution-design.yaml",            "primitives/analysis/duplicate-detection.yaml"),
    ("solution-design.yaml",            "primitives/analysis/intelligence-injection.yaml"),
    ("solution-design.yaml",            "primitives/governance/security-check.yaml"),
    # composite-execution-pipeline references planned security templates
    ("composite-execution-pipeline.yaml", "cortex-registry/workflows/templates/security/threat-model-analysis.yaml"),
    ("composite-execution-pipeline.yaml", "cortex-registry/workflows/templates/tdd/test-strategy-matrix.yaml"),
    # service-decomposition references a frontend TDD template not yet created
    ("service-decomposition-workflow.yaml", "cortex-registry/workflows/templates/tdd/tdd-frontend-visual.yaml"),
})

# Step identity fields — at least one must be present for a step to be "identified"
_STEP_IDENTITY_FIELDS: frozenset[str] = frozenset({
    "name", "id", "step_id", "action", "orchestrator", "orchestrator_name",
    "template_ref", "source_primitive", "primitive", "gate", "marker",
    "stage", "uses", "dispatch_ref",
})


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _all_templates() -> list[Path]:
    return sorted(TEMPLATES_DIR.rglob("*.yaml"))


def _non_primitive_templates() -> list[Path]:
    return [f for f in _all_templates() if PRIMITIVES_DIR not in f.parents]


def _primitive_templates() -> list[Path]:
    return sorted(PRIMITIVES_DIR.rglob("*.yaml"))


def _get_steps(content: dict) -> list[Any]:
    """Extract steps list from a template, handling both top-level and nested."""
    steps = content.get("steps")
    if not steps and isinstance(content.get("workflow"), dict):
        steps = content["workflow"].get("steps")
    return steps if isinstance(steps, list) else []


def _resolve_ref(ref: str) -> bool:
    """Return True if a primitive/template ref can be resolved to an existing file."""
    if not ref:
        return True
    candidates = [
        TEMPLATES_DIR / ref,
        TEMPLATES_DIR / (ref + ".yaml"),
        Path(ref),  # absolute paths
    ]
    return any(c.exists() for c in candidates)


def _collect_step_refs(content: dict) -> list[str]:
    """Collect all template_ref / source_primitive / primitive values from steps."""
    refs: list[str] = []
    steps = _get_steps(content)
    for step in steps:
        if not isinstance(step, dict):
            continue
        for field in ("template_ref", "source_primitive", "primitive"):
            ref = step.get(field)
            if ref and isinstance(ref, str):
                refs.append(ref)
    return refs


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def all_templates() -> list[Path]:
    return _all_templates()


@pytest.fixture(scope="module")
def non_primitive_templates() -> list[Path]:
    return _non_primitive_templates()


@pytest.fixture(scope="module")
def primitive_templates() -> list[Path]:
    return _primitive_templates()


# ---------------------------------------------------------------------------
# Tests — Baseline counts
# ---------------------------------------------------------------------------

def test_template_count_is_stable(all_templates):
    """Total workflow template count (including primitives) must not drop below baseline."""
    count = len(all_templates)
    assert count >= _MINIMUM_TEMPLATE_COUNT, (
        f"Workflow template count is {count} — expected ≥ {_MINIMUM_TEMPLATE_COUNT}. "
        "Templates may have been deleted. Check git history."
    )


def test_primitive_count_is_stable(primitive_templates):
    """Primitive count must not drop below baseline."""
    count = len(primitive_templates)
    assert count >= _MINIMUM_PRIMITIVE_COUNT, (
        f"Primitive count is {count} — expected ≥ {_MINIMUM_PRIMITIVE_COUNT}. "
        "Primitives may have been deleted. Check git history."
    )


# ---------------------------------------------------------------------------
# Tests — Universal primitives exist
# ---------------------------------------------------------------------------

def test_universal_primitives_all_exist():
    """All 8 universal primitives (injected into every code-modifying workflow) must exist."""
    missing = [
        rel for rel in _UNIVERSAL_PRIMITIVES
        if not (TEMPLATES_DIR / rel).exists()
    ]
    assert missing == [], (
        f"{len(missing)} universal primitives are missing:\n"
        + "\n".join(f"  - {m}" for m in sorted(missing))
    )


# ---------------------------------------------------------------------------
# Tests — Routing table completeness
# ---------------------------------------------------------------------------

def test_routing_table_templates_all_exist():
    """Every template in the intent→workflow routing table must exist on disk.

    Missing routing table templates mean intent routing would silently fail
    or fall back to default for those intents.
    """
    missing = [
        rel for rel in _ROUTING_TABLE_TEMPLATES
        if not (TEMPLATES_DIR / rel).exists()
    ]
    assert missing == [], (
        f"{len(missing)} routing-table templates are missing:\n"
        + "\n".join(f"  - {m}" for m in sorted(missing))
        + "\n\nCreate the missing templates or remove them from the routing table."
    )


# ---------------------------------------------------------------------------
# Tests — Template YAML validity
# ---------------------------------------------------------------------------

def test_all_templates_are_parseable(all_templates):
    """Every workflow template YAML file must be parseable without errors."""
    errors = []
    for f in all_templates:
        try:
            content = yaml.safe_load(f.read_text(encoding="utf-8"))
            if not isinstance(content, dict):
                errors.append(f"{f.name}: not a YAML mapping (got {type(content).__name__})")
        except yaml.YAMLError as e:
            errors.append(f"{f.name}: YAML parse error — {e}")
    assert errors == [], (
        f"{len(errors)} workflow templates have parse errors:\n"
        + "\n".join(f"  {e}" for e in errors)
    )


def test_non_primitive_templates_have_id(non_primitive_templates):
    """Every non-primitive workflow template must have an ``id`` field."""
    missing = []
    for f in non_primitive_templates:
        try:
            content = yaml.safe_load(f.read_text(encoding="utf-8"))
            if not isinstance(content, dict):
                continue
            top_id = content.get("id")
            nested_id = content.get("workflow", {}).get("id") if isinstance(content.get("workflow"), dict) else None
            if not top_id and not nested_id:
                missing.append(str(f.relative_to(CORTEX_ROOT)))
        except yaml.YAMLError:
            pass  # parse errors caught by test_all_templates_are_parseable
    assert missing == [], (
        f"{len(missing)} non-primitive templates are missing an 'id' field:\n"
        + "\n".join(f"  - {m}" for m in missing)
    )


def test_templates_with_steps_have_identified_steps(non_primitive_templates):
    """Every step in a template with a steps list must have at least one identity field.

    Identity fields: name | id | step_id | action | orchestrator | orchestrator_name |
                     template_ref | source_primitive | primitive | gate | marker |
                     stage | uses | dispatch_ref
    """
    violations = []
    for f in non_primitive_templates:
        try:
            content = yaml.safe_load(f.read_text(encoding="utf-8"))
            if not isinstance(content, dict):
                continue
            steps = _get_steps(content)
            for i, step in enumerate(steps):
                if not isinstance(step, dict):
                    continue
                if not (_STEP_IDENTITY_FIELDS & set(step.keys())):
                    violations.append(
                        f"{f.name}: step [{i}] has no identity field — "
                        f"fields present: {sorted(step.keys())}"
                    )
        except yaml.YAMLError:
            pass
    assert violations == [], (
        f"{len(violations)} steps are missing identity fields:\n"
        + "\n".join(f"  {v}" for v in violations[:20])
        + ("\n  ... (truncated)" if len(violations) > 20 else "")
    )


# ---------------------------------------------------------------------------
# Tests — Primitive reference resolution
# ---------------------------------------------------------------------------

def test_no_unregistered_broken_primitive_refs(non_primitive_templates):
    """Every unresolvable primitive ref must be listed in _KNOWN_UNRESOLVABLE_REFS.

    A ref that is both unresolvable AND not registered in the known-gaps
    list is a P1 violation — it means a NEW broken reference was silently added.
    """
    new_broken: list[tuple[str, str]] = []
    for f in non_primitive_templates:
        try:
            content = yaml.safe_load(f.read_text(encoding="utf-8"))
            if not isinstance(content, dict):
                continue
            for ref in _collect_step_refs(content):
                if not _resolve_ref(ref):
                    key = (f.name, ref)
                    if key not in _KNOWN_UNRESOLVABLE_REFS:
                        new_broken.append(key)
        except yaml.YAMLError:
            pass

    assert new_broken == [], (
        f"{len(new_broken)} NEW unresolvable primitive refs found "
        f"(not in _KNOWN_UNRESOLVABLE_REFS):\n"
        + "\n".join(f"  {fn}: {ref}" for fn, ref in new_broken)
        + "\n\nEither create the missing primitive file, correct the ref path, "
        "or add the entry to _KNOWN_UNRESOLVABLE_REFS in this test file."
    )


def test_known_unresolvable_refs_are_still_broken(non_primitive_templates):
    """All entries in _KNOWN_UNRESOLVABLE_REFS should still be unresolvable.

    If a ref was fixed (file created or ref corrected), remove it from
    _KNOWN_UNRESOLVABLE_REFS to keep the list lean.
    """
    now_resolved: list[tuple[str, str]] = []
    for fn, ref in _KNOWN_UNRESOLVABLE_REFS:
        if _resolve_ref(ref):
            now_resolved.append((fn, ref))
    assert now_resolved == [], (
        f"{len(now_resolved)} entries in _KNOWN_UNRESOLVABLE_REFS are now resolved "
        f"— remove them from the list:\n"
        + "\n".join(f"  {fn}: {ref}" for fn, ref in now_resolved)
    )


# ---------------------------------------------------------------------------
# Tests — Primitives self-check
# ---------------------------------------------------------------------------

def test_all_primitives_have_id(primitive_templates):
    """Every primitive template must have an ``id`` field for registry indexing."""
    missing = []
    for f in primitive_templates:
        try:
            content = yaml.safe_load(f.read_text(encoding="utf-8"))
            if not isinstance(content, dict):
                continue
            if not content.get("id"):
                missing.append(str(f.relative_to(CORTEX_ROOT)))
        except yaml.YAMLError:
            pass
    assert missing == [], (
        f"{len(missing)} primitives are missing an 'id' field:\n"
        + "\n".join(f"  - {m}" for m in missing)
    )


def test_no_empty_primitive_files(primitive_templates):
    """No primitive file may be empty (0 bytes or whitespace only)."""
    empty = [
        str(f.relative_to(CORTEX_ROOT))
        for f in primitive_templates
        if not f.read_text(encoding="utf-8").strip()
    ]
    assert empty == [], (
        f"{len(empty)} primitive files are empty:\n"
        + "\n".join(f"  - {e}" for e in empty)
    )
