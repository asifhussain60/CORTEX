"""
tests/preflight/test_dependency_dag.py — Phase 114-b RED→GREEN

Enforces the strict layering DAG:
  models/ (L0) → core/ (L1) → intelligence/+lens/ (L2) → orchestrators/ (L3) → mcp/ (L4)

Acceptance criteria from GAP-114-02 and GAP-114-03:
  - core/ has ZERO module-level imports from orchestrators/ (function-body lazy allowed)
  - infrastructure/ has ZERO module-level imports from orchestrators/ (function-body lazy allowed)
  - models/ has ZERO module-level imports from core/ or above (except via lazy helper)

Governance: CORE-008 (TDD), CORE-064 (sweep), CORE-068 (convergence gate)
Phase: 114-b
"""
import ast
import pathlib
import pytest


CORTEX_ROOT = pathlib.Path("cortex")


def _get_module_level_imports(directory: pathlib.Path) -> list[tuple[str, str, int]]:
    """Return (file, imported_module, line) for MODULE-LEVEL imports only.

    Skips:
    - Imports inside function bodies (lazy imports — legitimate pattern)
    - Imports inside TYPE_CHECKING blocks (static analysis only)
    - _quarantine/ directory
    """
    results = []
    for f in directory.rglob("*.py"):
        if "__pycache__" in str(f) or "_quarantine" in str(f):
            continue
        try:
            source = f.read_text(errors="ignore")
            tree = ast.parse(source)
        except Exception:
            continue

        # Collect only module-level statement nodes (direct children of Module)
        for node in ast.iter_child_nodes(tree):
            # Skip TYPE_CHECKING guards
            if isinstance(node, ast.If):
                test = node.test
                is_tc = (
                    (isinstance(test, ast.Name) and test.id == "TYPE_CHECKING")
                    or (isinstance(test, ast.Attribute) and test.attr == "TYPE_CHECKING")
                )
                if is_tc:
                    continue  # TYPE_CHECKING blocks are acceptable (static analysis)
                # Non-TYPE_CHECKING if blocks — scan their imports
                for child in ast.walk(node):
                    if isinstance(child, ast.ImportFrom) and child.module:
                        results.append((str(f), child.module, child.lineno))
                    elif isinstance(child, ast.Import):
                        for alias in child.names:
                            results.append((str(f), alias.name, child.lineno))
                continue

            # Direct module-level import statements
            if isinstance(node, ast.ImportFrom) and node.module:
                results.append((str(f), node.module, node.lineno))
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    results.append((str(f), alias.name, node.lineno))
            # Function/class defs — skip (lazy imports inside them are fine)

    return results


def test_core_does_not_import_orchestrators():
    """core/ must not have any module-level imports from cortex.orchestrators.*

    TYPE_CHECKING-guarded imports are acceptable.
    Function-body lazy imports (PLC0415) are acceptable — they break circular cycles.
    Only direct module-level `from cortex.orchestrators import ...` are violations.
    """
    violations = []
    core_dir = CORTEX_ROOT / "core"
    for filepath, module, lineno in _get_module_level_imports(core_dir):
        if "cortex.orchestrators" in module:
            violations.append(f"  {filepath}:{lineno} → {module}")

    if violations:
        violation_text = "\n".join(violations[:20])
        pytest.fail(
            f"core/ has {len(violations)} module-level imports from orchestrators/ "
            f"(DAG violation — L1 must not module-level import L3):\n{violation_text}"
        )


def test_infrastructure_does_not_import_orchestrators():
    """infrastructure/ must not have module-level imports from cortex.orchestrators.*

    infrastructure/ is a SUPPORT layer — may only import from L0-L2 at module level.
    Function-body lazy imports are allowed (already the pattern in pre_commit_validator.py).
    """
    violations = []
    infra_dir = CORTEX_ROOT / "infrastructure"
    for filepath, module, lineno in _get_module_level_imports(infra_dir):
        if "cortex.orchestrators" in module:
            violations.append(f"  {filepath}:{lineno} → {module}")

    if violations:
        violation_text = "\n".join(violations[:20])
        pytest.fail(
            f"infrastructure/ has {len(violations)} module-level imports from orchestrators/ "
            f"(DAG violation — SUPPORT must not module-level import L3):\n{violation_text}"
        )


def test_models_does_not_import_above_layer_0():
    """models/ (L0) must not have module-level imports from cortex.core or above.

    TYPE_CHECKING-guarded imports and lazy-helper patterns are acceptable.
    """
    violations = []
    models_dir = CORTEX_ROOT / "models"
    forbidden_prefixes = (
        "cortex.core",
        "cortex.orchestrators",
        "cortex.intelligence",
        "cortex.lens",
        "cortex.mcp",
        "cortex.infrastructure",
        "cortex.governance",
    )
    for filepath, module, lineno in _get_module_level_imports(models_dir):
        if any(module.startswith(fp) for fp in forbidden_prefixes):
            violations.append(f"  {filepath}:{lineno} → {module}")

    if violations:
        violation_text = "\n".join(violations[:20])
        pytest.fail(
            f"models/ has {len(violations)} module-level upward imports (L0 must not import L1+):\n{violation_text}"
        )
