"""
GAP-128-B-03: Inheritance chains (extends:) with broken termination.
GAP-128-B-04: Circular dependencies - inheritance-specific tests.

Focused inheritance chain tests separate from parser_type_detection.py.

Drift lock: check-43-registry-yaml-schema-cohesion-lock.yaml
"""

from pathlib import Path
from typing import Optional

import pytest
import yaml

REPO_ROOT = Path(__file__).parent.parent.parent.parent
REGISTRY_ROOT = REPO_ROOT / "cortex-registry"


def _load_yaml_safe(path: Path):
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return None


def _collect_extends_map() -> dict[str, str]:
    """Build mapping: file_rel_path -> extends_value for all registry YAMLs."""
    result = {}
    for f in REGISTRY_ROOT.rglob("*.yaml"):
        data = _load_yaml_safe(f)
        if not isinstance(data, dict):
            continue
        extends = data.get("extends")
        if extends and isinstance(extends, str):
            result[str(f.relative_to(REGISTRY_ROOT))] = extends
    return result


class TestInheritanceChains:
    """extends: chains must resolve and terminate without cycles."""

    def test_all_extends_targets_exist(self):
        """Every extends: value must point to an existing file."""
        extends_map = _collect_extends_map()
        broken = []
        for source, target in extends_map.items():
            source_path = REGISTRY_ROOT / source
            resolved = (source_path.parent / target).resolve()
            if not resolved.exists():
                resolved_root = (REGISTRY_ROOT / target).resolve()
                if not resolved_root.exists():
                    broken.append(f"{source} -> {target}")

        assert broken == [], (
            f"Found {len(broken)} unresolvable extends: reference(s):\n"
            + "\n".join(f"  {b}" for b in broken)
        )

    def test_no_circular_extends(self):
        """extends: chains must not form cycles."""
        extends_map = _collect_extends_map()

        def has_cycle(node: str, visited: set) -> bool:
            if node in visited:
                return True
            visited.add(node)
            target = extends_map.get(node)
            if target:
                # Normalize target relative to registry root
                target_key = None
                for k in extends_map:
                    if k.endswith(target) or k.endswith(Path(target).name):
                        target_key = k
                        break
                if target_key:
                    return has_cycle(target_key, visited)
            return False

        cycles = [k for k in extends_map if has_cycle(k, set())]
        assert cycles == [], (
            f"Circular extends: detected:\n"
            + "\n".join(f"  {c}" for c in cycles[:10])
        )

    def test_extends_chains_max_depth_five(self):
        """extends: chains must not exceed depth 5 (to prevent stack overflows)."""
        extends_map = _collect_extends_map()

        def chain_depth(node: str, depth: int = 0, seen: Optional[set] = None) -> int:
            if seen is None:
                seen = set()
            if depth > 10 or node in seen:
                return depth
            seen = seen | {node}
            target = extends_map.get(node)
            if not target:
                return depth
            target_key = next(
                (k for k in extends_map if k.endswith(Path(target).name)), None
            )
            if target_key:
                return chain_depth(target_key, depth + 1, seen)
            return depth

        deep_chains = []
        for k in extends_map:
            d = chain_depth(k)
            if d > 5:
                deep_chains.append((k, d))
        assert deep_chains == [], (
            f"extends: chains exceed depth 5:\n"
            + "\n".join(f"  {k} (depth={d})" for k, d in deep_chains)
        )
