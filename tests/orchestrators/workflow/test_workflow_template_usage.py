"""
GAP-128-D-01: Workflow templates referenced in workflow-composer-spec.yaml
must exist as actual files in cortex-registry/workflows/templates/.

The workflow composer spec defines intent routing — every workflow_ref must resolve
to a real .yaml file. Missing templates mean broken routing.

Drift lock: check-49-workflow-template-convergence-lock.yaml
"""

from pathlib import Path
from typing import List, Dict
import yaml
import pytest

REPO_ROOT = Path(__file__).parents[3]
SPEC_FILE = REPO_ROOT / "cortex-registry/workflows/workflow-composer-spec.yaml"
TEMPLATES_DIR = REPO_ROOT / "cortex-registry/workflows/templates"


def _load_spec() -> dict:
    if not SPEC_FILE.exists():
        return {}
    return yaml.safe_load(SPEC_FILE.read_text(encoding="utf-8")) or {}


def _collect_all_workflow_refs(spec: dict) -> List[tuple]:
    """Collect (intent, workflow_ref) from intent_routing in the spec."""
    refs = []
    intent_routing = spec.get("intent_routing", {}) or {}
    for intent, config in intent_routing.items():
        if not isinstance(config, dict):
            continue
        workflow_ref = config.get("workflow_ref")
        if workflow_ref:
            refs.append((intent, workflow_ref))
        pre_gate = config.get("pre_gate")
        if pre_gate:
            refs.append((f"{intent}/pre_gate", pre_gate))
        convergence = config.get("convergence")
        if convergence:
            refs.append((f"{intent}/convergence", convergence))
    return refs


def _resolve_ref(ref: str) -> Path:
    """Convert a spec ref like 'sdlc/implement-workflow' to a .yaml file path."""
    if not ref.endswith(".yaml"):
        ref = ref + ".yaml"
    return TEMPLATES_DIR / ref


class TestWorkflowTemplateUsage:
    """GAP-128-D-01: All workflow_ref values in spec resolve to real files."""

    def test_spec_file_exists(self):
        """workflow-composer-spec.yaml must exist."""
        assert SPEC_FILE.exists(), f"Workflow composer spec not found: {SPEC_FILE}"

    def test_spec_has_intent_routing(self):
        """Spec must define intent_routing with at least one entry."""
        spec = _load_spec()
        ir = spec.get("intent_routing", {})
        assert isinstance(ir, dict) and len(ir) > 0, (
            "workflow-composer-spec.yaml has no intent_routing entries"
        )

    def test_all_workflow_refs_exist(self):
        """Every workflow_ref in intent_routing must resolve to a real file."""
        spec = _load_spec()
        refs = [
            (intent, ref)
            for intent, ref in _collect_all_workflow_refs(spec)
            if "pre_gate" not in intent and "convergence" not in intent
        ]
        missing = []
        for intent, ref in refs:
            resolved = _resolve_ref(ref)
            if not resolved.exists():
                missing.append(f"Intent '{intent}': workflow_ref='{ref}' → {resolved.name} NOT FOUND")
        assert missing == [], (
            f"Broken workflow_ref entries in spec:\n"
            + "\n".join(f"  {m}" for m in missing)
        )

    def test_all_pre_gate_refs_exist(self):
        """Every pre_gate reference must resolve to a real primitive file."""
        spec = _load_spec()
        intent_routing = spec.get("intent_routing", {}) or {}
        missing = []
        for intent, config in intent_routing.items():
            if not isinstance(config, dict):
                continue
            pre_gate = config.get("pre_gate")
            if not pre_gate:
                continue
            resolved = _resolve_ref(pre_gate)
            if not resolved.exists():
                missing.append(f"Intent '{intent}': pre_gate='{pre_gate}' → {resolved.name} NOT FOUND")
        assert missing == [], (
            f"Broken pre_gate references in spec:\n"
            + "\n".join(f"  {m}" for m in missing)
        )

    def test_all_convergence_refs_exist(self):
        """Every convergence reference must resolve to a real primitive file."""
        spec = _load_spec()
        intent_routing = spec.get("intent_routing", {}) or {}
        missing = []
        for intent, config in intent_routing.items():
            if not isinstance(config, dict):
                continue
            convergence = config.get("convergence")
            if not convergence:
                continue
            resolved = _resolve_ref(convergence)
            if not resolved.exists():
                missing.append(f"Intent '{intent}': convergence='{convergence}' → {resolved.name} NOT FOUND")
        assert missing == [], (
            f"Broken convergence references in spec:\n"
            + "\n".join(f"  {m}" for m in missing)
        )

    def test_templates_dir_exists(self):
        """cortex-registry/workflows/templates/ directory must exist."""
        assert TEMPLATES_DIR.exists(), f"Templates directory not found: {TEMPLATES_DIR}"
