"""
GAP-128-B-02: Cross-file $ref pointers that fail to resolve.
GAP-128-B-04: Circular dependencies in registry YAML graph.

Confirms reference resolution contracts. Complements existing
test_reference_resolver.py with GAP-128 specific contracts.

Drift lock: check-43-registry-yaml-schema-cohesion-lock.yaml
"""

from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).parent.parent.parent.parent
REGISTRY_ROOT = REPO_ROOT / "cortex-registry"


def _find_ref_values(obj, refs=None):
    """Recursively collect all $ref values from a YAML object."""
    if refs is None:
        refs = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "$ref" and isinstance(v, str):
                refs.append(v)
            else:
                _find_ref_values(v, refs)
    elif isinstance(obj, list):
        for item in obj:
            _find_ref_values(item, refs)
    return refs


def _load_yaml_safe(path: Path):
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return None


class TestReferenceResolution:
    """$ref cross-file pointers must resolve to existing files."""

    def test_all_dollar_ref_pointers_resolve(self):
        """Every $ref value in cortex-registry/ must resolve to an existing file."""
        broken = []
        for f in REGISTRY_ROOT.rglob("*.yaml"):
            data = _load_yaml_safe(f)
            if not isinstance(data, dict):
                continue
            refs = _find_ref_values(data)
            for ref in refs:
                # Strip fragment identifiers (#/definitions/...)
                ref_path = ref.split("#")[0]
                if not ref_path:
                    continue
                resolved = (f.parent / ref_path).resolve()
                if not resolved.exists():
                    broken.append(
                        f"{f.relative_to(REGISTRY_ROOT)}: $ref {ref}"
                    )

        assert broken == [], (
            f"Found {len(broken)} unresolvable $ref pointer(s):\n"
            + "\n".join(f"  {b}" for b in broken[:20])
        )

    def test_registry_yaml_count_is_stable(self):
        """Regression: cortex-registry must have >= 300 YAML files."""
        count = len(list(REGISTRY_ROOT.rglob("*.yaml")))
        assert count >= 300, f"Expected >=300 registry YAMLs, found {count}"


class TestDependencyCycles:
    """YAML dependency graphs must be acyclic."""

    def test_no_circular_imports_in_workflow_templates(self):
        """Workflow templates must not import each other in a cycle."""
        wf_dir = REGISTRY_ROOT / "workflows" / "templates"
        if not wf_dir.exists():
            pytest.skip("workflows/templates dir not found")

        # Build dependency graph based on $ref or include: fields
        dep_map: dict[str, list[str]] = {}
        for f in wf_dir.rglob("*.yaml"):
            data = _load_yaml_safe(f)
            if not isinstance(data, dict):
                continue
            deps = []
            refs = _find_ref_values(data)
            for ref in refs:
                ref_path = ref.split("#")[0]
                if ref_path and not ref_path.startswith("http"):
                    deps.append(ref_path)
            key = str(f.relative_to(wf_dir))
            dep_map[key] = deps

        def dfs(node: str, visiting: set, visited: set) -> bool:
            if node in visiting:
                return True  # cycle
            if node in visited:
                return False
            visiting.add(node)
            for dep in dep_map.get(node, []):
                dep_key = str(Path(dep).name)
                if dfs(dep_key, visiting, visited):
                    return True
            visiting.discard(node)
            visited.add(node)
            return False

        visited: set = set()
        cycles = []
        for node in dep_map:
            if node not in visited:
                if dfs(node, set(), visited):
                    cycles.append(node)

        assert cycles == [], (
            f"Circular dependencies detected in {len(cycles)} workflow template(s):\n"
            + "\n".join(f"  {c}" for c in cycles[:10])
        )

    def test_governance_yamls_no_self_reference(self):
        """No governance YAML should reference itself via $ref."""
        gov_dir = REGISTRY_ROOT / "governance"
        if not gov_dir.exists():
            pytest.skip("governance dir not found")

        violations = []
        for f in gov_dir.rglob("*.yaml"):
            data = _load_yaml_safe(f)
            if not isinstance(data, dict):
                continue
            for ref in _find_ref_values(data):
                ref_path = ref.split("#")[0]
                if ref_path and Path(ref_path).name == f.name:
                    violations.append(f"{f.relative_to(REGISTRY_ROOT)}: self-ref {ref}")

        assert violations == [], (
            f"Self-referencing $ref found:\n"
            + "\n".join(f"  {v}" for v in violations)
        )
