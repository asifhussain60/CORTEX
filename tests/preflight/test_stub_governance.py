"""Preflight: Stub and proxy governance checks (CORE-035).

Prevents three anti-patterns that caused repeated 'fix' runs in chat01.md:
1. Pure-proxy redirect files — non-__init__ files with only imports, no own code
2. 'GREEN phase — wire later' stub comments in production code
3. PHASE90_GATEWAY_ENABLED=True without @enforce_gateway on the entry method

Each test is fast (AST-only, no imports) — runs in < 5s.
Tier: T0 (preflight)
"""
import ast
import pathlib
import re
from typing import List, Tuple

import pytest

# Files explicitly allowed to be pure-import shims (Phase 60 compat shims with 90-day retention)
ALLOWED_COMPAT_SHIMS: frozenset = frozenset({
    "cortex/core/context_cache_layer.py",
    "cortex/core/knowledge/protocols.py",
    "cortex/intelligence/capability_matcher.py",
    "cortex/intelligence/domain_brain/optimistic_lock.py",
    "cortex/intelligence/execution_sandbox.py",
    "cortex/intelligence/memory/tier1_learned/orchestrators/cleaners/base.py",
    "cortex/intelligence/memory/tier1_learned/orchestrators/cleaners/interface.py",
    "cortex/lens/core.py",
    "cortex/orchestrators/documentation.py",
    "cortex/orchestrators/health/constants.py",
    "cortex/tools/toolkit/verify_mcp_tools.py",
})

CORTEX_ROOT = pathlib.Path(__file__).parents[2]


def _all_cortex_py_files() -> List[pathlib.Path]:
    """Return all non-pycache, non-__init__ Python files under cortex/."""
    return [
        f for f in (CORTEX_ROOT / "cortex").rglob("*.py")
        if "__pycache__" not in str(f) and f.name != "__init__.py"
    ]


class TestNoNewProxyRedirectStubs:
    """CORE-035: No new pure-proxy redirect files may be added outside the allowed shim list.

    A pure-proxy file has: only import statements, no function/class definitions.
    These accumulate during module migrations and violate the single canonical
    implementation rule — callers can't tell which path is authoritative.
    """

    # AST-scans 1000+ files — run in a single worker to avoid xdist OOM crashes
    pytestmark = pytest.mark.timeout(60)

    def test_no_new_pure_proxy_files(self) -> None:
        """No non-__init__ cortex/ file may consist entirely of import statements.

        Allowed exceptions: ALLOWED_COMPAT_SHIMS (Phase 60, 90-day retention).
        Any new proxy file must update ALLOWED_COMPAT_SHIMS with a documented expiry.
        """
        violations: List[str] = []

        for f in _all_cortex_py_files():
            rel = str(f.relative_to(CORTEX_ROOT))
            if rel in ALLOWED_COMPAT_SHIMS:
                continue
            try:
                tree = ast.parse(f.read_text())
            except SyntaxError:
                continue

            funcs = [n for n in ast.walk(tree)
                     if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
            classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
            imports = [n for n in ast.walk(tree)
                       if isinstance(n, (ast.Import, ast.ImportFrom))]

            if not funcs and not classes and imports:
                violations.append(rel)

        assert not violations, (
            f"CORE-035: {len(violations)} pure-proxy redirect file(s) found outside "
            f"ALLOWED_COMPAT_SHIMS. Either add own code or move to ALLOWED_COMPAT_SHIMS "
            f"with a documented 90-day expiry:\n  " + "\n  ".join(violations)
        )


class TestNoWireeLaterStubs:
    """Prevent 'GREEN phase — wire later' stubs from persisting indefinitely.

    The WorkflowComposer._get_orchestrator() returning None for 9+ phases
    (chat01.md root cause #2) was caused by comments deferring wiring that
    never happened. This test catches that pattern.
    """

    # Comment patterns that indicate intentionally-deferred wiring
    DEFERRED_PATTERNS = [
        r"GREEN phase.*simplified.*REFACTOR",
        r"wire.*later",
        r"full.*integration.*REFACTOR phase",
        r"simplified.*implementation.*full.*in REFACTOR",
        r"simplified.*REFACTOR",
    ]

    # Files known to have these comments for valid reasons (document why)
    ALLOWED_DEFERRED: frozenset = frozenset({
        # None currently — all deferred stubs have been resolved (Phase 99)
    })

    def test_no_deferred_wiring_comments(self) -> None:
        """No production cortex/ file may contain 'GREEN phase — wire later' comments.

        This pattern caused the WorkflowComposer to return None from
        _get_orchestrator() for the entire lifespan of Phases 89-99.
        """
        combined = re.compile(
            "|".join(self.DEFERRED_PATTERNS), re.IGNORECASE
        )
        violations: List[Tuple[str, int, str]] = []

        for f in _all_cortex_py_files():
            rel = str(f.relative_to(CORTEX_ROOT))
            if rel in self.ALLOWED_DEFERRED:
                continue
            try:
                text = f.read_text()
            except Exception:
                continue
            for i, line in enumerate(text.splitlines(), 1):
                if combined.search(line) and line.strip().startswith("#"):
                    violations.append((rel, i, line.strip()))

        assert not violations, (
            f"Deferred-wiring stub comments found in {len(violations)} location(s). "
            f"Either wire it now or document in ALLOWED_DEFERRED with a phase target:\n"
            + "\n".join(f"  {r}:{ln}: {txt}" for r, ln, txt in violations)
        )


class TestGatewayDecoratorCoverage:
    """ENABLED=True orchestrators must have @enforce_gateway on their primary entry method.

    This was the Phase 98 gap — 4 orchestrators had ENABLED=True but no decorator,
    so the flag was set but never intercepted.
    """

    def test_enabled_orchestrators_have_decorator(self) -> None:
        """Every orchestrator with PHASE90_GATEWAY_ENABLED=True must have @enforce_gateway."""
        violations: List[str] = []

        orchestrators_dir = CORTEX_ROOT / "cortex" / "orchestrators"
        for f in orchestrators_dir.rglob("*.py"):
            if "__pycache__" in str(f) or f.name == "__init__.py":
                continue
            try:
                text = f.read_text()
            except Exception:
                continue

            if "PHASE90_GATEWAY_ENABLED: bool = True" in text:
                if "@enforce_gateway" not in text:
                    violations.append(str(f.relative_to(CORTEX_ROOT)))

        assert not violations, (
            f"PHASE90_GATEWAY_ENABLED=True but no @enforce_gateway in {len(violations)} file(s). "
            f"Apply @enforce_gateway to the primary entry method:\n  "
            + "\n  ".join(violations)
        )


class TestGatewayChainIntegrity:
    """The gateway → composer → template chain must remain importable and non-broken."""

    def test_workflow_gateway_importable(self) -> None:
        """WorkflowGateway must be importable without errors."""
        from cortex.orchestrators.workflow.workflow_gateway import WorkflowGateway
        assert WorkflowGateway is not None

    def test_workflow_composer_importable(self) -> None:
        """WorkflowComposer must be importable without errors."""
        from cortex.orchestrators.workflow.workflow_composer import WorkflowComposer
        assert WorkflowComposer is not None

    def test_enforce_gateway_importable(self) -> None:
        """enforce_gateway decorator must be importable."""
        from cortex.core.workflow_enforcement_mixin import enforce_gateway
        assert callable(enforce_gateway)

    def test_get_orchestrator_not_always_none(self) -> None:
        """WorkflowComposer._get_orchestrator must not always return None.

        This was the core Break #1 from chat01.md Phase 99 analysis.
        The method is permitted to return None when no registry is wired,
        but it must not be a hardcoded stub that always returns None.
        """
        from cortex.orchestrators.workflow.workflow_composer import WorkflowComposer

        # Parse the source file directly (avoids dedent issues with inspect.getsource)
        composer_src = (
            pathlib.Path(__file__).parents[2]
            / "cortex/orchestrators/workflow/workflow_composer.py"
        )
        tree = ast.parse(composer_src.read_text())

        # Find _get_orchestrator method in WorkflowComposer class
        method_body = None
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "WorkflowComposer":
                for item in node.body:
                    if (
                        isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
                        and item.name == "_get_orchestrator"
                    ):
                        method_body = item.body
                        break

        assert method_body is not None, (
            "WorkflowComposer._get_orchestrator() method not found"
        )

        # Collect all return statements
        returns = [n for n in ast.walk(ast.Module(body=method_body, type_ignores=[]))
                   if isinstance(n, ast.Return)]
        none_returns = [
            r for r in returns
            if isinstance(r.value, ast.Constant) and r.value.value is None
        ]
        non_none_returns = [r for r in returns if r not in none_returns]

        assert non_none_returns or len(none_returns) < len(returns), (
            "WorkflowComposer._get_orchestrator() is a hardcoded stub that always "
            "returns None. Wire an orchestrator registry before this can pass."
        )
