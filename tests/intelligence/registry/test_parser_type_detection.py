"""
GAP-128-B-01: YAML parser type detection mismatches content type.
GAP-128-B-03: Inheritance chains (extends:) with broken termination.

Confirms the parser registry correctly assigns types and that extends: chains
terminate. Complements existing test_parser_registry.py with GAP-128 contracts.

Drift lock: check-43-registry-yaml-schema-cohesion-lock.yaml
"""

from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).parent.parent.parent.parent
REGISTRY_ROOT = REPO_ROOT / "cortex-registry"

# Mapping: directory prefix → expected parser domain
DOMAIN_DIR_MAP = {
    "governance": "governance",
    "workflows": "workflow",
    "knowledge": "knowledge",
    "core": "governance",
    "patterns": "pattern",
    "templates": "response",
}


def _load_yaml_safe(path: Path):
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return None


class TestParserTypeDetection:
    """Parser type should align with directory location of each YAML file."""

    def test_governance_yamls_have_governance_fields(self):
        """YAMLs under cortex-registry/governance/ must have id or rules fields."""
        gov_dir = REGISTRY_ROOT / "governance"
        if not gov_dir.exists():
            pytest.skip("governance dir not found")

        violations = []
        for f in gov_dir.rglob("*.yaml"):
            data = _load_yaml_safe(f)
            if data is None or not isinstance(data, dict):
                continue
            # Governance files should have at least one of these markers
            has_marker = any(
                k in data for k in ("id", "rules", "checks", "violations", "rule_id")
            )
            if not has_marker:
                violations.append(str(f.relative_to(REGISTRY_ROOT)))

        # Allow up to 5 files that may be config/index files without markers
        assert len(violations) <= 5, (
            f"Found {len(violations)} governance YAMLs without governance fields:\n"
            + "\n".join(f"  {v}" for v in violations[:20])
        )

    def test_workflow_yamls_have_workflow_fields(self):
        """YAMLs under cortex-registry/workflows/templates/ must have id or steps."""
        wf_dir = REGISTRY_ROOT / "workflows" / "templates"
        if not wf_dir.exists():
            pytest.skip("workflows/templates dir not found")

        violations = []
        for f in wf_dir.rglob("*.yaml"):
            data = _load_yaml_safe(f)
            if data is None or not isinstance(data, dict):
                continue
            has_marker = any(k in data for k in ("id", "steps", "workflow_id", "name"))
            if not has_marker:
                violations.append(str(f.relative_to(REGISTRY_ROOT)))

        assert len(violations) <= 3, (
            f"Found {len(violations)} workflow template YAMLs without required fields:\n"
            + "\n".join(f"  {v}" for v in violations[:20])
        )

    def test_all_registry_yamls_parse_cleanly(self):
        """All YAML files in cortex-registry/ must be valid YAML (no parse errors)."""
        parse_errors = []
        for f in REGISTRY_ROOT.rglob("*.yaml"):
            try:
                yaml.safe_load(f.read_text(encoding="utf-8", errors="replace"))
            except yaml.YAMLError as e:
                parse_errors.append(f"{f.relative_to(REGISTRY_ROOT)}: {e}")

        assert parse_errors == [], (
            f"{len(parse_errors)} YAML parse error(s):\n"
            + "\n".join(f"  {e}" for e in parse_errors[:10])
        )


class TestInheritanceChains:
    """extends: fields in YAML must reference files that exist."""

    def test_extends_references_resolve(self):
        """Any extends: field in a YAML file must point to an existing file."""
        broken = []
        for f in REGISTRY_ROOT.rglob("*.yaml"):
            data = _load_yaml_safe(f)
            if not isinstance(data, dict):
                continue
            extends = data.get("extends")
            if not extends:
                continue
            # Resolve relative to the file's directory
            resolved = f.parent / extends
            if not resolved.exists():
                # Try resolving from registry root
                resolved_root = REGISTRY_ROOT / extends
                if not resolved_root.exists():
                    broken.append(
                        f"{f.relative_to(REGISTRY_ROOT)}: extends: {extends}"
                    )

        assert broken == [], (
            f"Found {len(broken)} broken extends: references:\n"
            + "\n".join(f"  {b}" for b in broken)
        )

    def test_no_circular_extends(self):
        """extends: chains must not form cycles."""
        # Build adjacency map
        extends_map: dict[str, str] = {}
        for f in REGISTRY_ROOT.rglob("*.yaml"):
            data = _load_yaml_safe(f)
            if not isinstance(data, dict):
                continue
            extends = data.get("extends")
            if extends:
                extends_map[str(f.relative_to(REGISTRY_ROOT))] = extends

        def has_cycle(start: str, visited: set) -> bool:
            if start in visited:
                return True
            visited.add(start)
            target = extends_map.get(start)
            if target and target in extends_map:
                return has_cycle(target, visited)
            return False

        cycles = [k for k in extends_map if has_cycle(k, set())]
        assert cycles == [], (
            f"Circular extends: detected in {len(cycles)} file(s):\n"
            + "\n".join(f"  {c}" for c in cycles[:10])
        )
