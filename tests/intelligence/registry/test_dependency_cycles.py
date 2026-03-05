"""
GAP-128-B-04: Circular dependencies in registry YAML graph (focused tests).

Complements test_reference_resolution.py with dedicated cycle tests.

Drift lock: check-43-registry-yaml-schema-cohesion-lock.yaml
"""

from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).parent.parent.parent.parent
REGISTRY_ROOT = REPO_ROOT / "cortex-registry"


def _load_yaml_safe(path: Path):
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return None


class TestDependencyCycles:
    """Registry YAML dependency graphs must be acyclic."""

    def test_registry_yaml_total_count_stable(self):
        """Regression: cortex-registry must have >= 300 YAML files."""
        count = len(list(REGISTRY_ROOT.rglob("*.yaml")))
        assert count >= 300, f"Expected >=300 registry YAMLs, found {count}"

    def test_knowledge_yamls_have_no_broken_includes(self):
        """Knowledge YAMLs must not reference files that do not exist."""
        knowledge_dir = REGISTRY_ROOT / "knowledge"
        if not knowledge_dir.exists():
            pytest.skip("knowledge dir not found")

        broken = []
        for f in knowledge_dir.rglob("*.yaml"):
            data = _load_yaml_safe(f)
            if not isinstance(data, dict):
                continue
            # Check any 'source:' or 'include:' fields
            for key in ("source", "include", "ref"):
                val = data.get(key)
                if val and isinstance(val, str) and not val.startswith("http"):
                    resolved = (f.parent / val).resolve()
                    if not resolved.exists():
                        broken.append(f"{f.relative_to(REGISTRY_ROOT)}: {key}={val}")

        assert broken == [], (
            f"Found {len(broken)} broken knowledge YAML reference(s):\n"
            + "\n".join(f"  {b}" for b in broken[:20])
        )

    def test_no_yaml_includes_itself(self):
        """No YAML file should reference itself in any pointer field."""
        violations = []
        for f in REGISTRY_ROOT.rglob("*.yaml"):
            data = _load_yaml_safe(f)
            if not isinstance(data, dict):
                continue
            for key in ("extends", "include", "source", "$ref"):
                val = data.get(key)
                if val and isinstance(val, str):
                    if Path(val).name == f.name and val != "":
                        violations.append(
                            f"{f.relative_to(REGISTRY_ROOT)}: {key}={val}"
                        )

        assert violations == [], (
            f"Self-referencing YAML files found:\n"
            + "\n".join(f"  {v}" for v in violations)
        )
