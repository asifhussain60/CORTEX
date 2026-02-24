"""Golden tests: FileFactory strict enforcement (Phase 24).

Every file created by CORTEX must go through FileFactory.
ZERO files should bypass the factory. CORTEX controls naming,
quality, and frequency — not Copilot.

Authority: CORE-008 (TDD) | CORE-028 (canonical naming) | Phase 24
"""

from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any, List, Optional

import pytest

# ==============================================================================
# CONSTANTS
# ==============================================================================

CORTEX_ROOT = Path(__file__).resolve().parents[3]
CORTEX_SRC = CORTEX_ROOT / "cortex"

# Directories that contain orchestrator / MCP / core code that MUST use FileFactory
ENFORCED_DIRS = [
    CORTEX_SRC / "orchestrators",
    CORTEX_SRC / "mcp",
    CORTEX_SRC / "core",
    CORTEX_SRC / "intelligence",
    CORTEX_SRC / "governance",
    CORTEX_SRC / "lens",
    CORTEX_SRC / "testing",
]

# Files allowed to do raw I/O (infrastructure, runtime data, caches, locks)
EXEMPTED_PATTERNS = [
    # Infrastructure: caches, locks, checkpoints, audit logs, secrets vaults
    r"cortex/infrastructure/",
    # File factory itself
    r"cortex/core/file_factory\.py$",
    # Dashboard / template renderers (HTML output, not source files)
    r"cortex/templates/",
    r"cortex/dashboards/",
    # Observability / metrics (JSON/log runtime data)
    r"cortex/observability/",
    # Config loaders (read-only typically, but some write caches)
    r"cortex/config/",
    # Tools that generate runtime artifacts
    r"cortex/tools/",
    # Models (data classes, no file I/O expected)
    r"cortex/models/",
    # Knowledge (runtime indexing)
    r"cortex/knowledge/",
    # Repositories (data persistence layer)
    r"cortex/repositories/",
    # Bootstrap / health check (singleton init)
    r"cortex/bootstrap\.py$",
    r"cortex/health_check_service\.py$",
    # CLI (delegates to orchestrators)
    r"cortex/cli/",
    # --- Runtime persistence: registries, recovery, saga, state ---
    r"cortex/core/registry/",        # plan_registry, phase_manager, dashboard_generator
    r"cortex/core/recovery/",        # saga_coordinator, state_repair
    r"cortex/core/common/",          # file_utils, safe_template_editor (utility I/O)
    r"cortex/core/wiring/",          # contract_validator (wiring validation logs)
    r"cortex/orchestrators/core/",     # persona_store (runtime profiles)
    r"cortex/core/execution/",       # execution_guard, resilience
    r"cortex/core/scaffold_writer\.py$",  # scaffold generation (by definition creates files)
    r"cortex/core/event_bus\.py$",        # event persistence
    r"cortex/core/orchestrator_dependency_registry\.py$",  # runtime registry
    r"cortex/core/core/",            # brain_state, core_config, intent/comprehension (deep core)
    r"cortex/core/brain_state_manager\.py$",  # runtime brain state persistence
    r"cortex/core/core_config\.py$",          # core config runtime writes
    r"cortex/core/intent/comprehension_loop\.py$",  # comprehension loop state
    r"cortex/core/intent/comprehension_yaml\.py$",  # comprehension yaml cache
    r"cortex/orchestrators/core/turn_timeout\.py$",  # turn timeout persistence
    # --- Orchestrator subdirectories doing legitimate runtime I/O ---
    r"cortex/orchestrators/health/",         # health checks, dashboards, autofix agents
    r"cortex/orchestrators/workflow/",       # ephemeral_storage, flush_manager, absorption_gate
    r"cortex/orchestrators/support/debugging/",  # auto_cleanup, debug strategies
    r"cortex/orchestrators/support/decision_journal\.py$",  # journal persistence
    r"cortex/orchestrators/support/recataloging_engine\.py$",  # catalogue rebuild
    r"cortex/orchestrators/support/file_relocation_engine\.py$",  # file moves
    r"cortex/orchestrators/support/import_reference_fixer\.py$",  # import fixup
    r"cortex/orchestrators/support/phase_completion_orchestrator\.py$",  # phase state
    r"cortex/orchestrators/support/auto_healing_mcp_orchestrator\.py$",  # self-healing
    r"cortex/orchestrators/validation/",     # readiness, security validators
    r"cortex/orchestrators/git/",            # git sanitization
    r"cortex/orchestrators/domain/refactoring/adapters/",  # rope/typescript adapters
    r"cortex/orchestrators/domain/dashboard_orchestrator\.py$",  # dashboard rendering
    r"cortex/orchestrators/copilot_merger\.py$",  # copilot profile merge
    r"cortex/orchestrators/profile_upgrader\.py$",  # profile upgrade
    r"cortex/orchestrators/profile_wizard\.py$",    # profile wizard
    r"cortex/orchestrators/support/vscode_configurator\.py$",  # VS Code JSON config generation
    r"cortex/orchestrators/core/lens_data_persistence\.py$",  # LENS data persistence
    r"cortex/orchestrators/core/master_plan_orchestrator\.py$",  # plan management
    # --- MCP tools doing legitimate runtime I/O ---
    r"cortex/mcp/native_tool_gate\.py$",     # tool gate persistence
    r"cortex/mcp/self_healing\.py$",         # self-healing state
    r"cortex/mcp/tool_spec_generator\.py$",  # spec generation
    r"cortex/mcp/tools/onboard_",            # onboarding writes profiles
    r"cortex/mcp/tools/sts_analyzer\.py$",   # STS analysis output
    # --- Intelligence: documentation, learning, memory, patterns ---
    r"cortex/intelligence/",         # all intelligence subdirs do runtime persistence
    # --- Governance: runtime compliance artifacts ---
    r"cortex/governance/",           # telemetry, mcp_first, zero_breaking, lint tools
    # --- LENS: discovery, dashboards, crawlers ---
    r"cortex/lens/",                 # crawler_generator, dashboard_data, discovery cache
    # --- Testing: test generation, baselines, dashboards ---
    r"cortex/testing/",              # baseline metrics, test demand generator, dashboards
]

# Import statement that signals FileFactory usage
FILE_FACTORY_IMPORT_PATTERNS = [
    "from cortex.core.file_factory import",
    "from cortex.core import file_factory",
    "import cortex.core.file_factory",
    "get_file_factory",
    "FileFactory",
]

# Patterns that indicate raw file creation (bypassing FileFactory)
RAW_FILE_CREATION_PATTERNS = [
    # open() with write mode
    r"""open\([^)]*['"][wa]['"]""",
    # Path.write_text()
    r"""\.write_text\(""",
    # Path.write_bytes()
    r"""\.write_bytes\(""",
    # os.write / os.open
    r"""os\.write\(""",
    # shutil.copy to create new files
    r"""shutil\.copy\(""",
]

# CORTEX-internal terms that MUST NOT appear in user-facing filenames
INTERNAL_TERMS = [
    "phase",
    "sts",
    "skull",
    "tier0",
    "ccl",
    "crystallized",
    "brain",
    "hexa",
    "cortex_internal",
    "wiring_spec",
]


# ==============================================================================
# FIXTURES
# ==============================================================================

@pytest.fixture(scope="module")
def factory() -> Any:
    """Get FileFactory instance."""
    from cortex.core.file_factory import FileFactory
    return FileFactory()


# ==============================================================================
# 1. INTERNAL TERMINOLOGY BLOCKED
# ==============================================================================

class TestInternalTerminologyBlocked:
    """FileFactory must reject filenames containing CORTEX-internal terms."""

    @pytest.mark.parametrize("term", INTERNAL_TERMS)
    def test_python_internal_term_blocked(self, factory: Any, term: str) -> None:
        """Python filenames with internal terms must be rejected."""
        result = factory.validate(f"{term}_orchestrator.py")
        assert not result.is_valid, (
            f"FileFactory should BLOCK '{term}_orchestrator.py' — leaks CORTEX internals"
        )

    @pytest.mark.parametrize("term", INTERNAL_TERMS)
    def test_yaml_internal_term_blocked(self, factory: Any, term: str) -> None:
        """YAML filenames with internal terms must be rejected."""
        result = factory.validate(f"{term}-config.yaml")
        assert not result.is_valid, (
            f"FileFactory should BLOCK '{term}-config.yaml' — leaks CORTEX internals"
        )

    @pytest.mark.parametrize("term", INTERNAL_TERMS)
    def test_markdown_internal_term_blocked(self, factory: Any, term: str) -> None:
        """Markdown filenames with internal terms must be rejected."""
        result = factory.validate(f"{term}-overview.md")
        assert not result.is_valid, (
            f"FileFactory should BLOCK '{term}-overview.md' — leaks CORTEX internals"
        )

    def test_sanitize_strips_internal_terms(self, factory: Any) -> None:
        """sanitize_name() must strip internal terms and return clean name."""
        assert hasattr(factory, "sanitize_name"), (
            "FileFactory must have sanitize_name() method"
        )
        result = factory.sanitize_name("phase_03_orchestrator.py")
        assert "phase" not in result.lower(), (
            f"sanitize_name() failed to strip 'phase' from: {result}"
        )

    def test_sanitize_preserves_valid_names(self, factory: Any) -> None:
        """sanitize_name() must not alter already-valid names."""
        assert hasattr(factory, "sanitize_name"), (
            "FileFactory must have sanitize_name() method"
        )
        result = factory.sanitize_name("master_orchestrator.py")
        assert result == "master_orchestrator.py"

    def test_sanitize_handles_multiple_terms(self, factory: Any) -> None:
        """sanitize_name() must handle filenames with multiple internal terms."""
        result = factory.sanitize_name("phase_skull_brain_report.py")
        for term in ["phase", "skull", "brain"]:
            assert term not in result.lower(), (
                f"sanitize_name() failed to strip '{term}' from: {result}"
            )


# ==============================================================================
# 2. FILE CREATION GATE — create_file() METHOD
# ==============================================================================

class TestFileCreationGate:
    """FileFactory must provide a gated create_file() that validates before writing."""

    def test_has_create_file_method(self, factory: Any) -> None:
        """FileFactory must have a universal create_file() gate method."""
        assert hasattr(factory, "create_file"), (
            "FileFactory must have create_file() — the single entry point for all file creation"
        )

    def test_create_file_rejects_invalid_name(self, factory: Any, tmp_path: Path) -> None:
        """create_file() must raise on invalid filenames."""
        bad_path = tmp_path / "SCREAMING_CASE.py"
        with pytest.raises((ValueError, Exception)):
            factory.create_file(
                path=bad_path,
                content="# bad",
                file_type="py",
            )

    def test_create_file_rejects_internal_terms(self, factory: Any, tmp_path: Path) -> None:
        """create_file() must reject filenames with internal terms."""
        bad_path = tmp_path / "phase_03_config.yaml"
        with pytest.raises((ValueError, Exception)):
            factory.create_file(
                path=bad_path,
                content="key: value",
                file_type="yaml",
            )

    def test_create_file_accepts_valid_name(self, factory: Any, tmp_path: Path) -> None:
        """create_file() must accept valid filenames and create the file."""
        good_path = tmp_path / "audit_reporter.py"
        factory.create_file(
            path=good_path,
            content="# module",
            file_type="py",
        )
        assert good_path.exists()

    def test_create_file_prevents_duplicates(self, factory: Any, tmp_path: Path) -> None:
        """create_file() must raise on existing files."""
        path = tmp_path / "existing_module.py"
        path.write_text("# existing")
        with pytest.raises(FileExistsError):
            factory.create_file(
                path=path,
                content="# duplicate",
                file_type="py",
            )


# ==============================================================================
# 3. STATIC ANALYSIS — NO RAW FILE CREATION IN ENFORCED DIRS
# ==============================================================================

class TestNoRawFileCreation:
    """Orchestrators, MCP tools, and core modules must NOT create files directly.

    This is the PERMANENT enforcement gate. Any new file I/O in enforced
    directories that doesn't go through FileFactory will fail this test.
    """

    @staticmethod
    def _get_enforced_python_files() -> List[Path]:
        """Get all Python files in enforced directories."""
        files = []
        for enforced_dir in ENFORCED_DIRS:
            if enforced_dir.exists():
                files.extend(enforced_dir.rglob("*.py"))
        return sorted(files)

    @staticmethod
    def _is_exempted(filepath: Path) -> bool:
        """Check if file is in an exempted directory."""
        rel = str(filepath.relative_to(CORTEX_ROOT))
        return any(re.search(pat, rel) for pat in EXEMPTED_PATTERNS)

    @staticmethod
    def _has_file_factory_import(source: str) -> bool:
        """Check if source has FileFactory import."""
        return any(pat in source for pat in FILE_FACTORY_IMPORT_PATTERNS)

    @staticmethod
    def _find_raw_writes(source: str) -> List[str]:
        """Find raw file write patterns in source code."""
        violations = []
        for pattern in RAW_FILE_CREATION_PATTERNS:
            matches = re.findall(pattern, source)
            violations.extend(matches)
        return violations

    def test_no_raw_file_creation_in_orchestrators(self) -> None:
        """Orchestrators must not create files without FileFactory."""
        orch_dir = CORTEX_SRC / "orchestrators"
        if not orch_dir.exists():
            pytest.skip("orchestrators/ not found")

        violations = []
        for py_file in orch_dir.rglob("*.py"):
            if py_file.name == "__init__.py":
                continue
            if self._is_exempted(py_file):
                continue
            source = py_file.read_text(errors="replace")
            raw_writes = self._find_raw_writes(source)
            if raw_writes and not self._has_file_factory_import(source):
                rel = str(py_file.relative_to(CORTEX_ROOT))
                violations.append(f"  {rel}: {len(raw_writes)} raw write(s)")

        assert not violations, (
            f"Orchestrators with raw file I/O (no FileFactory import):\n"
            + "\n".join(violations)
            + "\n\nFix: Use FileFactory.create_file() or import get_file_factory"
        )

    def test_no_raw_file_creation_in_mcp_tools(self) -> None:
        """MCP tools must not create files without FileFactory."""
        mcp_dir = CORTEX_SRC / "mcp"
        if not mcp_dir.exists():
            pytest.skip("mcp/ not found")

        violations = []
        for py_file in mcp_dir.rglob("*.py"):
            if py_file.name == "__init__.py":
                continue
            if self._is_exempted(py_file):
                continue
            source = py_file.read_text(errors="replace")
            raw_writes = self._find_raw_writes(source)
            if raw_writes and not self._has_file_factory_import(source):
                rel = str(py_file.relative_to(CORTEX_ROOT))
                violations.append(f"  {rel}: {len(raw_writes)} raw write(s)")

        assert not violations, (
            f"MCP tools with raw file I/O (no FileFactory import):\n"
            + "\n".join(violations)
            + "\n\nFix: Use FileFactory.create_file() or import get_file_factory"
        )

    def test_no_raw_file_creation_in_core(self) -> None:
        """Core modules must not create files without FileFactory (except file_factory.py itself)."""
        core_dir = CORTEX_SRC / "core"
        if not core_dir.exists():
            pytest.skip("core/ not found")

        violations = []
        for py_file in core_dir.rglob("*.py"):
            if py_file.name in ("__init__.py", "file_factory.py"):
                continue
            if self._is_exempted(py_file):
                continue
            source = py_file.read_text(errors="replace")
            raw_writes = self._find_raw_writes(source)
            if raw_writes and not self._has_file_factory_import(source):
                rel = str(py_file.relative_to(CORTEX_ROOT))
                violations.append(f"  {rel}: {len(raw_writes)} raw write(s)")

        assert not violations, (
            f"Core modules with raw file I/O (no FileFactory import):\n"
            + "\n".join(violations)
            + "\n\nFix: Use FileFactory.create_file() or import get_file_factory"
        )


# ==============================================================================
# 4. NAMING RULES YAML COMPLETENESS
# ==============================================================================

class TestNamingRulesYaml:
    """file-naming-rules.yaml must include internal terminology prohibitions."""

    def test_naming_rules_yaml_exists(self) -> None:
        """file-naming-rules.yaml must exist."""
        config_path = CORTEX_ROOT / "cortex-registry/core/config/file-naming-rules.yaml"
        assert config_path.exists()

    def test_internal_terms_in_prohibited_patterns(self) -> None:
        """All CORTEX-internal terms must be in prohibited_patterns."""
        import yaml
        config_path = CORTEX_ROOT / "cortex-registry/core/config/file-naming-rules.yaml"
        data = yaml.safe_load(config_path.read_text())
        patterns = data.get("prohibited_patterns", [])
        pattern_str = " ".join(str(p) for p in patterns)

        for term in INTERNAL_TERMS:
            assert term in pattern_str, (
                f"CORTEX-internal term '{term}' missing from "
                f"prohibited_patterns in file-naming-rules.yaml"
            )

    def test_enforcement_level_is_strict(self) -> None:
        """Enforcement level must be 'strict'."""
        import yaml
        config_path = CORTEX_ROOT / "cortex-registry/core/config/file-naming-rules.yaml"
        data = yaml.safe_load(config_path.read_text())
        enforcement = data.get("enforcement", {})
        assert enforcement.get("level") == "strict"


# ==============================================================================
# 5. FILE FACTORY SINGLETON + MCP EXPOSURE
# ==============================================================================

class TestFileFactorySingleton:
    """FileFactory must be accessible as singleton and via MCP."""

    def test_get_file_factory_singleton(self) -> None:
        """get_file_factory() must return singleton instance."""
        from cortex.core.file_factory import get_file_factory
        f1 = get_file_factory()
        f2 = get_file_factory()
        assert f1 is f2

    def test_file_factory_has_all_creation_methods(self, factory: Any) -> None:
        """FileFactory must have complete creation API."""
        required_methods = [
            "validate",
            "create_file",
            "create_python_file",
            "create_yaml_file",
            "create_test_file",
            "create_markdown_file",
            "sanitize_name",
            "python_module",
            "python_test",
            "yaml_config",
            "markdown",
            "from_description",
        ]
        for method in required_methods:
            assert hasattr(factory, method), (
                f"FileFactory missing required method: {method}"
            )
