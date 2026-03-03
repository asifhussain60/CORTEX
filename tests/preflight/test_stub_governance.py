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
    # Phase 107 Sub-Phase A — 90-day compat shims (expiry: 2026-06-01)
    # Canonical definitions moved to cortex/intelligence/models/
    # These re-export for zero-breaking-change backward compatibility (GAP-107-01, GAP-107-02)
    "cortex/intelligence/base.py",
    "cortex/intelligence/base_engine.py",
    "cortex/intelligence/knowledge/unified_intelligence_context.py",
})

CORTEX_ROOT = pathlib.Path(__file__).parents[2]


def _all_cortex_py_files() -> List[pathlib.Path]:
    """Return all non-pycache, non-__init__, non-__main__ Python files under cortex/."""
    return [
        f for f in (CORTEX_ROOT / "cortex").rglob("*.py")
        if "__pycache__" not in str(f)
        and f.name != "__init__.py"
        and f.name != "__main__.py"  # __main__.py files are entry points by design
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


# ============================================================================
# NEW: P0 HARDENED CHECKS — added after audit/fix missed these (Phase 108)
# ============================================================================

# ── Concrete classes that are legitimate abstract bases / Protocols ──────────
# These ARE allowed to contain raise NotImplementedError in their methods.
# Rule: the class must inherit from Protocol, ABC, or a known base class.
_ABSTRACT_BASE_SUFFIXES = (
    "Protocol", "ABC", "Base", "Strategy", "Backend",
    "Mixin", "Interface", "Handler", "Adapter",
)

# Files explicitly excluded from the concrete-stub scan:
#   - Protocol/ABC definition files (by design)
#   - Test files (stubs are fine in test doubles)
#   - Known compat-shim / migration files
_CONCRETE_STUB_EXCLUDED_FILES: frozenset = frozenset({
    "cortex/infrastructure/crash_recovery.py",           # StateManager(Protocol)
    "cortex/core/common/state_repair.py",                # HashChainManager(Protocol)
    "cortex/lens/cache.py",                              # CacheBackend(Protocol)
    "cortex/lens/cache/lens_cache.py",                   # LENSCache abstract base
    "cortex/observability/metrics_collector.py",         # StorageBackend(Protocol)
    "cortex/core/knowledge/ingestion_pipeline.py",       # 5 Protocols
    "cortex/orchestrators/intelligence/interaction_patterns.py",  # AgentProtocol
    "cortex/core/common/core_progress_reporter.py",      # ProgressCallback(Protocol)
    "cortex/intelligence/crawler/walker.py",             # RepositoryWalker base
    "cortex/orchestrators/domain/business/plugins.py",   # DomainPlugin(ABC)
    "cortex/infrastructure/graceful_degradation.py",     # FallbackStrategy base
    "cortex/tools/debug_orchestrator/__init__.py",       # BaseInjectionStrategy
    "cortex/lens/discovery/__init__.py",                 # Discovery plugin base
    "cortex/intelligence/memory/tier2_adaptive/resilience.py",    # abstract
    "cortex/intelligence/memory/core/import_resolver.py",         # abstract
    "cortex/repositories/ado/ado_provider.py",           # abstract provider
})


class TestNoConcreteClassStubs:
    """Hardened audit/fix check: concrete (non-abstract) class methods must not raise NotImplementedError.

    Root cause of Phase 108 gap: audit/fix only detected Protocol/ABC bodies
    (legitimate) but missed concrete implementations that were inadvertently
    left as stubs (P0 governance violations).

    This test uses AST to detect:
      - Methods in concrete classes (not Protocol/ABC/Base) that have a body
        consisting solely of `raise NotImplementedError(...)`.
      - Methods that are effectively dead stubs: `pass` as the only statement
        in a concrete class with a non-trivial class name.

    Allowlist: _CONCRETE_STUB_EXCLUDED_FILES covers known abstract bases.
    """

    pytestmark = pytest.mark.timeout(60)

    def test_no_concrete_class_notimplemented_stubs(self) -> None:
        """Concrete class methods must not raise NotImplementedError.

        A method body that consists of ONLY a raise NotImplementedError
        statement in a class that is NOT abstract (Protocol/ABC/Base/Strategy/
        Backend/Mixin/Interface/Handler/Adapter) is a P0 stub violation.
        """
        violations: List[Tuple[str, str, str, int]] = []  # (file, class, method, line)

        for f in _all_cortex_py_files():
            rel = str(f.relative_to(CORTEX_ROOT))
            if rel in _CONCRETE_STUB_EXCLUDED_FILES:
                continue
            if "test_" in f.name or "_test.py" in f.name:
                continue
            try:
                source = f.read_text(encoding="utf-8", errors="ignore")
                tree = ast.parse(source)
            except (SyntaxError, Exception):
                continue

            for node in ast.walk(tree):
                if not isinstance(node, ast.ClassDef):
                    continue

                # Determine if this class is an abstract base / protocol
                base_names = []
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        base_names.append(base.id)
                    elif isinstance(base, ast.Attribute):
                        base_names.append(base.attr)

                is_abstract = any(
                    node.name.endswith(sfx) or any(b.endswith(sfx) for b in base_names)
                    for sfx in _ABSTRACT_BASE_SUFFIXES
                )
                if is_abstract:
                    continue

                # Inspect each method in the concrete class
                for item in node.body:
                    if not isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        continue

                    # Filter body: skip docstring-only prefix
                    real_body = [
                        s for s in item.body
                        if not (isinstance(s, ast.Expr)
                                and isinstance(s.value, ast.Constant)
                                and isinstance(s.value.value, str))
                    ]

                    if len(real_body) != 1:
                        continue  # More than one real statement → not a pure stub

                    stmt = real_body[0]
                    if isinstance(stmt, ast.Raise) and stmt.exc is not None:
                        # Check if it's a NotImplementedError raise
                        exc = stmt.exc
                        exc_name = None
                        if isinstance(exc, ast.Name):
                            exc_name = exc.id
                        elif isinstance(exc, ast.Call):
                            fn = exc.func
                            if isinstance(fn, ast.Name):
                                exc_name = fn.id
                            elif isinstance(fn, ast.Attribute):
                                exc_name = fn.attr
                        if exc_name == "NotImplementedError":
                            violations.append((rel, node.name, item.name, item.lineno))

        assert not violations, (
            f"P0 STUB VIOLATION: {len(violations)} concrete class method(s) raise "
            f"NotImplementedError. These must be implemented or moved to an abstract base:\n"
            + "\n".join(
                f"  {r}:{ln}  {cls}.{mth}()"
                for r, cls, mth, ln in violations
            )
        )

    def test_no_always_true_scalability_check(self) -> None:
        """check_scalability() must not be a pass-through that always returns passed=True.

        Detected in Phase 108 audit: the method contained a single 'Simplified: Always pass'
        comment and returned CheckResult(passed=True) without any analysis.
        """
        src = (
            CORTEX_ROOT
            / "cortex/orchestrators/validation/pre_implementation_checklist.py"
        )
        text = src.read_text()
        # The stub always returned True with no conditional logic at all.
        # After the fix, the method must contain at least one if-statement.
        tree = ast.parse(text)
        method_body = None
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for item in node.body:
                    if (isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
                            and item.name == "check_scalability"):
                        method_body = item.body
                        break

        assert method_body is not None, "check_scalability() method not found"
        has_conditional = any(isinstance(s, ast.If) for s in ast.walk(
            ast.Module(body=method_body, type_ignores=[])
        ))
        assert has_conditional, (
            "check_scalability() must contain real conditional logic — "
            "not a stub that always returns passed=True"
        )

    def test_meta_auditor_tdd_check_is_real(self) -> None:
        """_check_tdd_compliance() must perform a real file-system check, not hardcode True.

        Phase 108 finding: the method always returned True ('Assume false positive
        for golden test') without checking for a corresponding test file.
        """
        src = (
            CORTEX_ROOT
            / "cortex/orchestrators/intelligence/meta_auditor_agent.py"
        )
        text = src.read_text()
        tree = ast.parse(text)
        method_body = None
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for item in node.body:
                    if (isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
                            and item.name == "_check_tdd_compliance"):
                        method_body = item.body
                        break

        assert method_body is not None, "_check_tdd_compliance() not found"

        # Must contain a loop or conditional path that actually inspects the filesystem
        has_for = any(isinstance(s, ast.For) for s in ast.walk(
            ast.Module(body=method_body, type_ignores=[])
        ))
        has_if = any(isinstance(s, ast.If) for s in ast.walk(
            ast.Module(body=method_body, type_ignores=[])
        ))
        # After fix: method checks candidate paths via .exists()
        has_exists_call = "exists()" in text[text.find("def _check_tdd_compliance"):
                                              text.find("def _check_tdd_compliance") + 2000]
        assert has_if and has_exists_call, (
            "_check_tdd_compliance() must perform a real filesystem check for test files — "
            "not return True unconditionally"
        )

    def test_meta_auditor_type_hint_check_is_real(self) -> None:
        """_check_type_hints() must use AST inspection, not hardcode False.

        Phase 108 finding: the method always returned False ('Simplified for golden test')
        without parsing the source file.
        """
        src = (
            CORTEX_ROOT
            / "cortex/orchestrators/intelligence/meta_auditor_agent.py"
        )
        text = src.read_text()
        tree = ast.parse(text)
        method_body = None
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for item in node.body:
                    if (isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
                            and item.name == "_check_type_hints"):
                        method_body = item.body
                        break

        assert method_body is not None, "_check_type_hints() not found"

        # Must import ast and call ast.parse (or equivalent)
        method_src = text[text.find("def _check_type_hints"):
                          text.find("def _check_type_hints") + 3000]
        assert "ast.parse" in method_src or "ast.walk" in method_src, (
            "_check_type_hints() must use AST analysis — not return False unconditionally"
        )

    def test_console_metrics_exporter_shutdown_is_noop(self) -> None:
        """ConsoleMetricsExporter.shutdown() must not raise NotImplementedError.

        Phase 108 finding: the method raised NotImplementedError instead of no-op.
        The test_shutdown_noop test in test_metrics_exporter.py already covers this,
        but this preflight ensures the audit/fix pipeline catches it statically too.
        """
        src = (
            CORTEX_ROOT
            / "cortex/infrastructure/metrics_exporter.py"
        )
        text = src.read_text()
        # Find the ConsoleMetricsExporter class section
        class_start = text.find("class ConsoleMetricsExporter")
        assert class_start != -1, "ConsoleMetricsExporter not found"
        # Find its shutdown method
        shutdown_start = text.find("def shutdown", class_start)
        assert shutdown_start != -1, "ConsoleMetricsExporter.shutdown() not found"
        # Grab until next method
        next_def = text.find("\n    def ", shutdown_start + 10)
        shutdown_body = text[shutdown_start: next_def if next_def != -1 else shutdown_start + 300]
        assert "NotImplementedError" not in shutdown_body, (
            "ConsoleMetricsExporter.shutdown() must not raise NotImplementedError — "
            "it should be a no-op (nothing to flush for console output)"
        )

    def test_checkpoint_manager_initialize_db_is_noop(self) -> None:
        """CheckpointManager._initialize_db() must not raise NotImplementedError.

        Phase 108 finding: the singleton's __init__ called _initialize_db() which raised,
        making CheckpointManager.instance() crash at runtime.
        """
        # Functional test: constructing the singleton must not raise
        from cortex.core.checkpoint_manager import CheckpointManager
        CheckpointManager.reset_instance()
        try:
            mgr = CheckpointManager.instance()
            assert mgr is not None
        finally:
            CheckpointManager.reset_instance()

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
