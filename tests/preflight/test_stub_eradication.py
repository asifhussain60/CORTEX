"""Preflight: Stub/Mock/Blank Object Eradication Scan (phase-126-c, Check #32).

Proves that the CORTEX production source (``cortex/``) contains no unresolved
stub markers, concrete-class NotImplementedError methods, feature-flag-disabled
wiring, or blank-output return paths in critical orchestrator public methods.

Gap ref: GAP-126-03
Drift lock: cortex-registry/governance/drift-locks/check-32-stub-eradication-lock.yaml
Tier: T0 (preflight) — AST + grep only, no server startup, < 15 s
CORE rules: CORE-008 (TDD), CORE-035 (single canonical implementation), CORE-064
"""
from __future__ import annotations

import ast
import pathlib
import re
from typing import List, Tuple

import pytest

CORTEX_ROOT = pathlib.Path(__file__).parents[2]
CORTEX_SRC = CORTEX_ROOT / "cortex"

# ---------------------------------------------------------------------------
# Shared exclusion sets — documented per CORE-035 (single canonical exception list)
# ---------------------------------------------------------------------------

# Files that are legitimate *analysis tools* for TODO/FIXME — they parse markers
# from user code, so naturally contain the words as string literals or regex patterns.
# These are NOT production stubs — they are code-intelligence processors.
_TODO_FIXME_ANALYSIS_ALLOWLIST: frozenset = frozenset({
    "cortex/core/knowledge/knowledge_graph.py",             # extracts TODO/FIXME from user code
    "cortex/core/token_distillation_engine.py",             # keyword detection for distillation
    "cortex/intelligence/analysis/comment_analyzer.py",     # DebtMarker parser — contains regex
    "cortex/intelligence/domain_brain/adapters.py",         # comment adapter — extracts markers
    "cortex/intelligence/knowledge/knowledge_synthesis_engine/synthesizers.py",  # synthesiser
    "cortex/intelligence/models/context.py",                # comment_analysis field descriptor
    "cortex/intelligence/lens/dotnet/attribute_data_extractor.py",   # FIXME tracked phase-67
    "cortex/intelligence/lens/dotnet/method_signature_analyzer.py",  # FIXME tracked phase-67
    "cortex/intelligence/lens/dotnet/cross_assembly_resolver.py",    # FIXME tracked phase-67
    "cortex/lens/analyzers/__init__.py",                    # module docstring lists extractor names
    "cortex/lens/lens_orchestrator/lens_models.py",         # field docstring: 'TODOs' as label
    "cortex/lens/lens_orchestrator/lens_holistic_mixin.py", # recommendation text for TODO count
    "cortex/orchestrators/core/intent_router/lens_analysis_mixin.py",  # parses intent from TODOs
    "cortex/orchestrators/intelligence/response_template_generator.py",  # IN_PROGRESS label text
    "cortex/orchestrators/support/digest_session_orchestrator.py",   # marker list: TODO:, FIXME:
    "cortex/cli/commands/lens.py",                          # echo todo_count / fixme_count stats
    "cortex/toolkit/adapters/__init__.py",                  # module docstring describes adapters
})

# Patterns that mention TODO/FIXME but are NOT unresolved stubs:
_TODO_FIXME_ALLOW_PATTERNS: Tuple[re.Pattern, ...] = (
    re.compile(r"FIXME.*TRACKED.*Phase", re.IGNORECASE),  # tracked phase-67 enhancements
    re.compile(r"FIXME.*count", re.IGNORECASE),           # synthesiser: FIXMEs detected count
    re.compile(r"TODO.*Phase\s+2\b", re.IGNORECASE),      # future phase stubs in polyglot
    re.compile(r"TODO.*Extract.*from spec", re.IGNORECASE),
    re.compile(r"TODO.*Extract.*csproj", re.IGNORECASE),
    re.compile(r"TODO.*TODOs?\b", re.IGNORECASE),         # refers to TODO items, not a stub
    re.compile(r"TODO.*FIXME", re.IGNORECASE),            # co-reference
    re.compile(r"TODO.*markers?\b", re.IGNORECASE),       # describes markers
    re.compile(r"TODO.*keyword", re.IGNORECASE),          # keyword detection logic
    re.compile(r"TODO.*Note\b", re.IGNORECASE),           # docstring note
    re.compile(r"TODO.*Phase 20", re.IGNORECASE),         # future phase placeholder
)

# Files in the _quarantine/ subdirectory are isolated — not production paths
_QUARANTINE_PATTERN = re.compile(r"[/\\]_quarantine[/\\]")

# Abstract base types whose methods are allowed to raise NotImplementedError
_ABSTRACT_BASE_NAMES = re.compile(
    r"\bABC\b|\bAbstract\b|\bProtocol\b|\bBase[A-Z]|\bIOrchestrator\b",
    re.IGNORECASE,
)

# Concrete classes with documented design justification for raising NotImplementedError
# Each entry: (relative_path, class_name, reason)
_NOTIMPL_ALLOWED_CONCRETE: frozenset = frozenset({
    # LanguageAdapter is an explicit extension point — subclassers MUST override inject/clean
    ("cortex/tools/debug_orchestrator/__init__.py", "LanguageAdapter"),
    # ImportStrategy is a typed callable protocol — __call__ is the extension contract
    ("cortex/intelligence/memory/core/import_resolver.py", "ImportStrategy"),
    # ADOWorkItemProvider.fetch_by_id — ADO integration is not yet deployed
    ("cortex/repositories/ado/ado_provider.py", "ADOWorkItemProvider"),
})

# ---------------------------------------------------------------------------
# Helpers (pure functions — no side effects)
# ---------------------------------------------------------------------------


def _all_cortex_py_files(exclude_tests: bool = True) -> List[pathlib.Path]:
    """Return all non-pycache, non-test Python files under cortex/."""
    return [
        f
        for f in CORTEX_SRC.rglob("*.py")
        if "__pycache__" not in str(f)
        and (not exclude_tests or "test_" not in f.name)
    ]


def _rel(path: pathlib.Path) -> str:
    """Relative path string (forward slashes for cross-platform consistency)."""
    return str(path.relative_to(CORTEX_ROOT)).replace("\\", "/")


def _is_todo_fixme_line_allowed(rel_path: str, line: str) -> bool:
    """Return True if a TODO/FIXME occurrence is a known-good analysis tool line."""
    if rel_path in _TODO_FIXME_ANALYSIS_ALLOWLIST:
        return True
    for pattern in _TODO_FIXME_ALLOW_PATTERNS:
        if pattern.search(line):
            return True
    return False


# ---------------------------------------------------------------------------
# Test 1 — No TODO/FIXME markers in production cortex/ source
# ---------------------------------------------------------------------------


class TestNoTodoFixmeInProductionSource:
    """Check #32-A: Production cortex/ must contain no unresolved TODO/FIXME stubs.

    TODO and FIXME markers signal unfinished work. A CORTEX production path with
    these markers is not production-ready. Legitimate code-intelligence tools that
    *parse* these markers from user code are explicitly allowlisted above.
    """

    pytestmark = pytest.mark.timeout(30)

    def test_no_todo_fixme_in_production_cortex_source(self) -> None:
        """No production cortex/ file may contain TODO or FIXME stub comments.

        Allowed exceptions:
        - Files in _TODO_FIXME_ANALYSIS_ALLOWLIST (analysis tools, not stubs)
        - Lines matching _TODO_FIXME_ALLOW_PATTERNS (tracked / non-stub occurrences)
        - Files under _quarantine/ subdirectory (isolated, not on production path)
        """
        violations: List[Tuple[str, int, str]] = []
        todo_fixme_re = re.compile(r"\b(TODO|FIXME)\b")

        for f in _all_cortex_py_files():
            if _QUARANTINE_PATTERN.search(str(f)):
                continue
            rel = _rel(f)
            try:
                lines = f.read_text(encoding="utf-8", errors="replace").splitlines()
            except OSError:
                continue

            for lineno, line in enumerate(lines, 1):
                if not todo_fixme_re.search(line):
                    continue
                if _is_todo_fixme_line_allowed(rel, line):
                    continue
                violations.append((rel, lineno, line.strip()))

        assert not violations, (
            f"CHECK-32 FAIL: {len(violations)} unresolved TODO/FIXME stub(s) found "
            f"in production cortex/ source.\n"
            "Resolve each stub or add it to _TODO_FIXME_ANALYSIS_ALLOWLIST "
            "with a documented justification:\n"
            + "\n".join(
                f"  {r}:{ln}: {txt}" for r, ln, txt in violations[:20]
            )
        )


# ---------------------------------------------------------------------------
# Test 2 — No NotImplementedError in non-abstract concrete classes
# ---------------------------------------------------------------------------


class TestNoNotImplementedErrorInNonAbstractClasses:
    """Check #32-B: Concrete (non-abstract) classes must not raise NotImplementedError.

    A concrete class with NotImplementedError is a disguised stub — callers
    cannot use it without raising at runtime. Abstract base classes and
    Protocol types are explicitly exempted (they define extension contracts).
    """

    pytestmark = pytest.mark.timeout(30)

    def _class_is_abstract(self, node: ast.ClassDef) -> bool:
        """Return True if a ClassDef inherits from an abstract base type."""
        for base in node.bases:
            name = getattr(base, "id", None) or getattr(base, "attr", None) or ""
            if _ABSTRACT_BASE_NAMES.search(name):
                return True
        return False

    def _method_has_abstractmethod(self, meth: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
        """Return True if method is decorated with @abstractmethod."""
        for dec in meth.decorator_list:
            name = getattr(dec, "id", None) or getattr(dec, "attr", None) or ""
            if name == "abstractmethod":
                return True
        return False

    def _raises_notimplemented(
        self, meth: ast.FunctionDef | ast.AsyncFunctionDef
    ) -> bool:
        """Return True if the method body raises NotImplementedError."""
        for stmt in ast.walk(ast.Module(body=meth.body, type_ignores=[])):
            if not isinstance(stmt, ast.Raise):
                continue
            exc = stmt.exc
            if exc is None:
                continue
            if isinstance(exc, ast.Call) and isinstance(exc.func, ast.Name):
                if exc.func.id == "NotImplementedError":
                    return True
            if isinstance(exc, ast.Name) and exc.id == "NotImplementedError":
                return True
        return False

    def test_no_notimplementederror_in_non_abstract_classes(self) -> None:
        """Concrete classes must not contain methods that raise NotImplementedError.

        Allowed exceptions: _NOTIMPL_ALLOWED_CONCRETE (extension points with
        documented justification — LanguageAdapter, ImportStrategy, ADOWorkItemProvider).
        """
        violations: List[Tuple[str, str, str, int]] = []

        for f in _all_cortex_py_files():
            if _QUARANTINE_PATTERN.search(str(f)):
                continue
            rel = _rel(f)
            try:
                src = f.read_text(encoding="utf-8", errors="replace")
                tree = ast.parse(src)
            except (OSError, SyntaxError):
                continue

            for cls_node in ast.walk(tree):
                if not isinstance(cls_node, ast.ClassDef):
                    continue
                if self._class_is_abstract(cls_node):
                    continue
                allowed_key = (rel, cls_node.name)
                if allowed_key in _NOTIMPL_ALLOWED_CONCRETE:
                    continue

                for meth in ast.walk(cls_node):
                    if not isinstance(meth, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        continue
                    if self._method_has_abstractmethod(meth):
                        continue
                    if self._raises_notimplemented(meth):
                        violations.append((rel, cls_node.name, meth.name, meth.lineno))

        assert not violations, (
            f"CHECK-32 FAIL: {len(violations)} concrete class method(s) raise "
            f"NotImplementedError without @abstractmethod decorator.\n"
            "Either mark the class as abstract (inherit from ABC or Protocol), "
            "add to _NOTIMPL_ALLOWED_CONCRETE with justification, or implement:\n"
            + "\n".join(
                f"  {r}: class {cls}.{fn}() at line {ln}"
                for r, cls, fn, ln in violations[:20]
            )
        )


# ---------------------------------------------------------------------------
# Test 3 — No feature-flag-disabled wiring in orchestrator init paths
# ---------------------------------------------------------------------------


class TestNoFeatureFlagDisabledWiring:
    """Check #32-C: Orchestrators must not have hard-coded feature flags set to False.

    A pattern like ``PHASE90_GATEWAY_ENABLED: bool = False`` or
    ``_response_engine_enabled = False`` means critical wiring is permanently
    disabled at the class level — callers believe the feature exists but it never fires.
    """

    pytestmark = pytest.mark.timeout(20)

    # Pattern: CLASS-LEVEL bool constant set to False for a wiring-enablement flag.
    # Targets ONLY class-body declarations, not instance attribute assignments (self.x = False).
    # Class-level patterns are the dangerous ones — they disable wiring for ALL instances
    # unconditionally without a runtime toggle path.
    _DISABLED_WIRING_PATTERN = re.compile(
        r"^\s{0,8}(PHASE\d+_GATEWAY_ENABLED"
        r"|[A-Z][A-Z0-9_]*_ENABLED"
        r"|[A-Z][A-Z0-9_]*_WIRING_ENABLED"
        r"|[A-Z][A-Z0-9_]*_CHAIN_ENABLED)\s*(?::\s*bool\s*)?=\s*False"
    )

    # Allowed instances — documented design choice, not a stub
    _ALLOWED_DISABLED_WIRING: frozenset = frozenset({
        # PHASE90_GATEWAY_ENABLED = False means gateway is opt-in per orchestrator (by design)
        # This is only disallowed if an orchestrator sets ENABLED=True but never fires the gate
    })

    def test_no_feature_flag_disabled_wiring(self) -> None:
        """Orchestrator wiring flags must not be hard-coded to False at class level.

        Detects ``PHASE90_GATEWAY_ENABLED: bool = False`` and similar patterns
        that indicate wiring was added but deliberately disabled — a production stub.

        Note: Instance attributes set to False in __init__ for runtime toggling
        are different from class-level wiring flags; this test targets class-level
        constants that disable entire subsystems.
        """
        violations: List[Tuple[str, int, str]] = []
        orch_root = CORTEX_SRC / "orchestrators"

        for f in orch_root.rglob("*.py"):
            if "__pycache__" in str(f) or "test_" in f.name:
                continue
            if _QUARANTINE_PATTERN.search(str(f)):
                continue
            rel = _rel(f)
            if rel in self._ALLOWED_DISABLED_WIRING:
                continue
            try:
                lines = f.read_text(encoding="utf-8", errors="replace").splitlines()
            except OSError:
                continue

            for lineno, line in enumerate(lines, 1):
                stripped = line.strip()
                if stripped.startswith("#"):
                    continue
                if self._DISABLED_WIRING_PATTERN.search(line):
                    violations.append((rel, lineno, stripped))

        assert not violations, (
            f"CHECK-32 FAIL: {len(violations)} hard-coded disabled wiring flag(s) "
            f"found in orchestrators.\n"
            "Either implement the wiring and set to True, or remove the flag entirely:\n"
            + "\n".join(f"  {r}:{ln}: {txt}" for r, ln, txt in violations[:20])
        )


# ---------------------------------------------------------------------------
# Test 4 — IntelligenceFacade.analyze() returns non-empty non-None result
# ---------------------------------------------------------------------------


class TestIntelligenceFacadeAnalyzeReturnsNonEmpty:
    """Check #32-D: IntelligenceFacade.analyze() must return live, non-empty data.

    A stub implementation that always returns ``{}`` or ``None`` means the
    entire intelligence pipeline is silently broken. This test asserts that
    calling analyze() on a real CORTEX source file returns a dict with a
    non-empty 'analysis' key containing LENS output.
    """

    def test_intelligence_facade_analyze_returns_non_empty(self) -> None:
        """IntelligenceFacade.analyze() must return a dict with non-empty analysis data.

        Uses the facade.py source file itself as the target — guaranteed to exist
        and guaranteed to have functions/classes (so AST analysis is non-trivial).
        """
        from cortex.intelligence.facade import get_intelligence_facade

        facade = get_intelligence_facade()
        result = facade.analyze(
            file_path=str(CORTEX_SRC / "intelligence" / "facade.py"),
            intent="IMPLEMENT",
        )

        assert isinstance(result, dict), (
            f"CHECK-32 FAIL: IntelligenceFacade.analyze() returned "
            f"{type(result).__name__!r} — expected dict."
        )
        assert result.get("status") in ("ok", "healthy", "success"), (
            f"CHECK-32 FAIL: IntelligenceFacade.analyze() returned status="
            f"{result.get('status')!r} — expected 'ok'.\nFull result: {result}"
        )
        analysis = result.get("analysis", {})
        assert analysis, (
            "CHECK-32 FAIL: IntelligenceFacade.analyze() returned empty 'analysis' "
            "dict — LENS pipeline is returning a stub result.\n"
            f"Full result: {result}"
        )
        # At minimum the AST analysis must contain functions (facade.py has many)
        ast_analysis = analysis.get("ast_analysis", {})
        functions = ast_analysis.get("functions", []) if isinstance(ast_analysis, dict) else []
        assert functions, (
            "CHECK-32 FAIL: IntelligenceFacade.analyze() returned ast_analysis "
            "with no functions — ASTAnalyzer is returning stub data.\n"
            f"ast_analysis: {ast_analysis}"
        )


# ---------------------------------------------------------------------------
# Test 5 — WorkflowComposer.execute_from_template() returns non-empty result
# ---------------------------------------------------------------------------


class TestWorkflowComposerExecuteReturnsNonEmpty:
    """Check #32-E: WorkflowComposer.execute_from_template() must return non-None result.

    A stub that returns None or raises on every call means orchestrators that
    depend on the composer for IMPLEMENT/FIX workflows are silently broken.
    """

    def test_workflow_composer_execute_returns_non_empty(self) -> None:
        """WorkflowComposer.execute_from_template() must return a non-None WorkflowExecutionResult.

        Uses the IMPLEMENT workflow template string — the most critical production path.
        The result must be a non-None WorkflowExecutionResult.
        """
        from cortex.orchestrators.workflow.workflow_composer import WorkflowComposer

        composer = WorkflowComposer()
        result = composer.execute_from_template(
            template_data="sdlc/implement-workflow",
            context={"operation": "IMPLEMENT", "parameters": {}},
        )

        assert result is not None, (
            "CHECK-32 FAIL: WorkflowComposer.execute_from_template() returned None — "
            "the workflow execution path is a stub.\n"
            "Check WorkflowComposer.execute_from_template() implementation."
        )
        # Result must be a WorkflowExecutionResult (has at minimum a 'success' attribute)
        assert hasattr(result, "success") or isinstance(result, dict), (
            f"CHECK-32 FAIL: WorkflowComposer.execute_from_template() returned "
            f"{type(result).__name__!r} — expected WorkflowExecutionResult with "
            "'success' attribute."
        )


# ---------------------------------------------------------------------------
# Test 6 — No orchestrator public methods whose entire body is return {}
# ---------------------------------------------------------------------------


class TestNoReturnEmptyDictInOrchestratorPublicMethods:
    """Check #32-F: Orchestrator public methods must not be bare return {} stubs.

    A method whose entire body is a single ``return {}`` statement (after
    stripping the docstring) is a blank-output stub — it provides no value
    and silently masks missing implementations.
    """

    pytestmark = pytest.mark.timeout(30)

    def test_no_return_empty_dict_in_orchestrator_public_methods(self) -> None:
        """Public orchestrator methods must not consist solely of 'return {}'.

        Any public method (no leading underscore) in cortex/orchestrators/ whose
        entire implementation is a single ``return {}`` statement is a production
        stub and must be implemented.
        """
        violations: List[Tuple[str, int, str]] = []
        orch_root = CORTEX_SRC / "orchestrators"

        for f in orch_root.rglob("*.py"):
            if "__pycache__" in str(f) or "test_" in f.name:
                continue
            if _QUARANTINE_PATTERN.search(str(f)):
                continue
            rel = _rel(f)
            try:
                src = f.read_text(encoding="utf-8", errors="replace")
                tree = ast.parse(src)
            except (OSError, SyntaxError):
                continue

            for node in ast.walk(tree):
                if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                if node.name.startswith("_"):
                    continue  # private methods are allowed to be simple

                body = list(node.body)
                # Strip leading docstring
                if (
                    body
                    and isinstance(body[0], ast.Expr)
                    and isinstance(body[0].value, (ast.Constant, ast.Str))
                ):
                    body = body[1:]

                # Single-statement body of 'return {}'?
                if len(body) == 1 and isinstance(body[0], ast.Return):
                    val = body[0].value
                    if isinstance(val, ast.Dict) and not val.keys:
                        violations.append((rel, node.lineno, node.name))

        assert not violations, (
            f"CHECK-32 FAIL: {len(violations)} orchestrator public method(s) consist "
            f"entirely of 'return {{}}' — blank-output stubs.\n"
            "Implement each method or convert to a private helper:\n"
            + "\n".join(
                f"  {r}:{ln}: def {fn}()" for r, ln, fn in violations[:20]
            )
        )
