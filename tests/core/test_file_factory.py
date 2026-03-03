"""
FileFactory — Canonical File Naming (Phase 00, D2) — TDD RED.

Tests the single canonical FileFactory that replaces:
- cortex/governance/filename_factory.py (677 lines, CORE-028 kebab only)
- cortex/tools/file_naming_factory.py   (546 lines, multi-type support)

The new cortex/core/file_factory.py must pass ALL tests here.
YAML config drives all rules — no hardcoded patterns.

Authority: Phase 00, D2 — File Factory Canonical SSOT
TDD Stage: RED (cortex/core/file_factory.py does not exist yet)
CORE-008: Test-first
CORE-011: Type hints
CORE-012: Docstrings
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest
import yaml

# ==============================================================================
# IMPORT — will FAIL (RED) until cortex/core/file_factory.py is created
# ==============================================================================

try:
    from cortex.core.file_factory import FileFactory, FileFactoryConfig, NamingResult
    FILE_FACTORY_AVAILABLE = True
except ImportError:
    FILE_FACTORY_AVAILABLE = False
    FileFactory = None  # type: ignore[assignment,misc]
    FileFactoryConfig = None  # type: ignore[assignment,misc]
    NamingResult = None  # type: ignore[assignment,misc]

pytestmark = pytest.mark.skipif(
    not FILE_FACTORY_AVAILABLE,
    reason="cortex/core/file_factory.py not yet implemented (Phase 00 D2)"
)


CONFIG_PATH = Path(__file__).resolve().parents[2] / "cortex-registry/config/file-naming-rules.yaml"


# ==============================================================================
# FIXTURES
# ==============================================================================

@pytest.fixture(scope="module")
def factory() -> Any:
    """Canonical FileFactory instance."""
    return FileFactory()


@pytest.fixture(scope="module")
def config_driven_factory() -> Any:
    """FileFactory loaded from YAML config."""
    assert CONFIG_PATH.exists(), f"YAML config not found: {CONFIG_PATH}"
    return FileFactory.from_yaml(CONFIG_PATH)


# ==============================================================================
# 1. FACTORY EXISTENCE & CONFIG
# ==============================================================================

class TestFileFactoryExists:
    """Factory must be importable and configurable."""

    def test_file_factory_importable(self) -> None:
        """cortex.core.file_factory.FileFactory must be importable."""
        assert FileFactory is not None

    def test_file_factory_config_importable(self) -> None:
        """FileFactoryConfig must be importable."""
        assert FileFactoryConfig is not None

    def test_naming_result_importable(self) -> None:
        """NamingResult must be importable."""
        assert NamingResult is not None

    def test_yaml_config_exists_on_disk(self) -> None:
        """file-naming-rules.yaml must exist in cortex-registry/config/."""
        assert CONFIG_PATH.exists(), f"Missing: {CONFIG_PATH}"

    def test_yaml_config_is_valid_yaml(self) -> None:
        """Config YAML must be parseable."""
        data = yaml.safe_load(CONFIG_PATH.read_text())
        assert data is not None
        assert "file_naming" in data or "rules" in data, "Config missing file_naming/rules key"

    def test_from_yaml_classmethod(self) -> None:
        """FileFactory.from_yaml() must load config from file."""
        f = FileFactory.from_yaml(CONFIG_PATH)
        assert f is not None

    def test_factory_has_type_hints(self) -> None:
        """All public methods must have type hints (CORE-011)."""
        import inspect
        f = FileFactory()
        for name, method in inspect.getmembers(f, predicate=inspect.ismethod):
            if not name.startswith("_"):
                hints = method.__annotations__
                sig = inspect.signature(method)
                params = [p for p in sig.parameters if p != "self"]
                assert "return" in hints, f"{name}() missing return type hint"

    def test_factory_has_docstrings(self) -> None:
        """All public methods must have docstrings (CORE-012)."""
        import inspect
        f = FileFactory()
        for name, method in inspect.getmembers(f, predicate=inspect.ismethod):
            if not name.startswith("_"):
                assert method.__doc__, f"{name}() missing docstring"


# ==============================================================================
# 2. PYTHON MODULE NAMING (snake_case, PEP 8)
# ==============================================================================

class TestPythonModuleNaming:
    """Python modules: snake_case per PEP 8."""

    def test_python_module_basic(self, factory: Any) -> None:
        """Basic python module naming."""
        result = factory.python_module("orchestrator")
        assert result.filename == "orchestrator.py"
        assert result.is_valid

    def test_python_module_with_context(self, factory: Any) -> None:
        """Python module with context prefix."""
        result = factory.python_module("orchestrator", context="master")
        assert result.filename == "master_orchestrator.py"
        assert result.is_valid

    def test_python_test_file(self, factory: Any) -> None:
        """Test files use test_ prefix."""
        result = factory.python_test("file_factory")
        assert result.filename == "test_file_factory.py"
        assert result.is_valid

    def test_python_module_no_screaming_case(self, factory: Any) -> None:
        """SCREAMING_CASE must be blocked."""
        result = factory.python_module("ORCHESTRATOR")
        assert not result.is_valid
        assert any("SCREAMING" in str(v).upper() or "upper" in str(v).lower()
                   for v in result.violations)

    def test_python_module_no_version_suffix(self, factory: Any) -> None:
        """Version suffixes (v1, v2, _v1) must be blocked."""
        for bad in ["orchestrator_v1", "orchestrator_v2", "service_v3"]:
            result = factory.python_module(bad)
            assert not result.is_valid, f"Should be blocked: {bad}"

    def test_python_module_no_enhanced_prefix(self, factory: Any) -> None:
        """'enhanced_' prefix must be blocked."""
        result = factory.python_module("enhanced_orchestrator")
        assert not result.is_valid

    def test_python_module_max_length_configurable(self, factory: Any) -> None:
        """Max filename length must be configurable (default 55)."""
        assert factory.config.max_length_python >= 40
        long_name = "a" * (factory.config.max_length_python + 1)
        result = factory.python_module(long_name)
        assert not result.is_valid


# ==============================================================================
# 3. YAML / MARKDOWN NAMING (kebab-case)
# ==============================================================================

class TestYamlMarkdownNaming:
    """YAML and Markdown files: kebab-case."""

    def test_yaml_config_file(self, factory: Any) -> None:
        """YAML config files use kebab-case."""
        result = factory.yaml_config("sqlite-retention")
        assert result.filename == "sqlite-retention.yaml"
        assert result.is_valid

    def test_markdown_file(self, factory: Any) -> None:
        """Markdown files use kebab-case."""
        result = factory.markdown("architecture-overview")
        assert result.filename == "architecture-overview.md"
        assert result.is_valid

    def test_yaml_no_underscores(self, factory: Any) -> None:
        """YAML filenames must not use underscores."""
        result = factory.yaml_config("sqlite_retention")
        assert not result.is_valid
        assert any("underscore" in str(v).lower() or "kebab" in str(v).lower()
                   for v in result.violations)

    def test_yaml_no_version_suffix(self, factory: Any) -> None:
        """YAML files must not have version suffixes."""
        for bad in ["config-v1", "config-v2", "schema-v3"]:
            result = factory.yaml_config(bad)
            assert not result.is_valid, f"Should be blocked: {bad}"

    def test_yaml_no_uppercase(self, factory: Any) -> None:
        """YAML filenames must be all lowercase."""
        result = factory.yaml_config("SQLite-Retention")
        assert not result.is_valid

    def test_plan_yaml_in_cortex_registry(self, factory: Any) -> None:
        """Plan YAMLs with internal terms ('phase') are now blocked (Phase 24)."""
        result = factory.yaml_plan("phase-00-foundation")
        assert result.filename == "phase-00-foundation.yaml"
        # Phase 24: 'phase' is now a prohibited internal term
        assert not result.is_valid, (
            "'phase' is a CORTEX-internal term and must be blocked per Phase 24"
        )


# ==============================================================================
# 4. PROHIBITED PATTERNS (CORE-028)
# ==============================================================================

class TestProhibitedPatterns:
    """Prohibited naming patterns must all be blocked."""

    @pytest.mark.parametrize("bad_name,reason", [
        ("orchestrator_v1.py", "version suffix"),
        ("orchestrator_v2.py", "version suffix"),
        ("orchestrator_v10.py", "version suffix"),
        ("enhanced_orchestrator.py", "enhanced_ prefix"),
        ("new_orchestrator.py", "new_ prefix"),
        ("improved_service.py", "improved_ prefix"),
        ("final_report.py", "final_ prefix"),
        ("ORCHESTRATOR.py", "SCREAMING_CASE"),
        ("OrchestratorV2.py", "CamelCase + version"),
    ])
    def test_prohibited_pattern_blocked(
        self, factory: Any, bad_name: str, reason: str
    ) -> None:
        """Each prohibited pattern must be rejected."""
        result = factory.validate(bad_name)
        assert not result.is_valid, (
            f"Expected BLOCKED for '{bad_name}' ({reason}), but got VALID"
        )

    @pytest.mark.parametrize("good_name", [
        "orchestrator.py",
        "master_orchestrator.py",
        "test_file_factory.py",
        "audit_db.py",
        "token_optimizer.py",
        "interaction_plan_store.py",
    ])
    def test_valid_python_names_pass(
        self, factory: Any, good_name: str
    ) -> None:
        """Valid snake_case Python names must pass."""
        result = factory.validate(good_name)
        assert result.is_valid, (
            f"Expected VALID for '{good_name}', got violations: {result.violations}"
        )


# ==============================================================================
# 5. YAML CONFIG DRIVES ALL RULES
# ==============================================================================

class TestYamlConfigDrivesRules:
    """All rules must come from YAML config, not hardcoded."""

    def test_max_length_from_yaml(self, config_driven_factory: Any) -> None:
        """max_length must be loaded from YAML."""
        assert config_driven_factory.config.max_length_python > 0

    def test_prohibited_patterns_from_yaml(self, config_driven_factory: Any) -> None:
        """prohibited_patterns list must be loaded from YAML."""
        assert len(config_driven_factory.config.prohibited_patterns) > 0

    def test_prohibited_patterns_include_version(
        self, config_driven_factory: Any
    ) -> None:
        """Prohibited patterns must include version suffixes."""
        patterns = " ".join(str(p) for p in config_driven_factory.config.prohibited_patterns)
        assert "v1" in patterns or r"v\d" in patterns or "_v" in patterns

    def test_prohibited_patterns_include_enhanced(
        self, config_driven_factory: Any
    ) -> None:
        """Prohibited patterns must include 'enhanced_'."""
        patterns = " ".join(str(p) for p in config_driven_factory.config.prohibited_patterns)
        assert "enhanced" in patterns


# ==============================================================================
# 6. COMPATIBILITY — OLD FACTORY TESTS PASS
# ==============================================================================

class TestBackwardCompatibility:
    """New FileFactory must satisfy all existing factory contracts."""

    def test_validates_same_as_filename_factory(self, factory: Any) -> None:
        """Validation results match cortex/governance/filename_factory behaviour."""
        # Known-valid kebab-case YAML name
        result = factory.validate("cortex-audit-log.yaml")
        assert result.is_valid

        # Known-invalid: underscore in YAML
        result2 = factory.validate("cortex_audit_log.yaml")
        assert not result2.is_valid

    def test_generates_documentation_names(self, factory: Any) -> None:
        """Covers FileNameFactory.documentation() equivalent."""
        result = factory.markdown("architecture-overview")
        assert result.filename.endswith(".md")

    def test_generates_config_names(self, factory: Any) -> None:
        """Covers FileNameFactory.configuration() equivalent."""
        result = factory.yaml_config("prometheus")
        assert result.filename == "prometheus.yaml"

    def test_generates_script_names(self, factory: Any) -> None:
        """Covers FileNameFactory.script() equivalent."""
        result = factory.shell_script("deploy", "kubernetes")
        assert result.filename == "deploy-kubernetes.sh"
        assert result.is_valid

    def test_generates_python_module_names(self, factory: Any) -> None:
        """Covers FileNameFactory.python_module() equivalent."""
        result = factory.python_module("orchestrator", context="master")
        assert result.filename == "master_orchestrator.py"

    def test_generate_from_natural_language(self, factory: Any) -> None:
        """Covers FilenameFactory.generate() equivalent — natural language → filename."""
        result = factory.from_description("logging analysis utility", file_type="py")
        assert result.filename.endswith(".py")
        assert result.is_valid
        assert "_" in result.filename  # snake_case for Python

    def test_kebab_suggestion_for_invalid(self, factory: Any) -> None:
        """Invalid names get a kebab-case suggestion."""
        result = factory.validate("MyOrchestratorConfig.yaml")
        assert not result.is_valid
        assert result.suggestion is not None
        assert result.suggestion == result.suggestion.lower()


# ==============================================================================
# 7. RESULT TYPE CONTRACT
# ==============================================================================

class TestNamingResult:
    """NamingResult must have the expected interface."""

    def test_naming_result_has_filename(self, factory: Any) -> None:
        """NamingResult must have filename attribute."""
        result = factory.python_module("orchestrator")
        assert hasattr(result, "filename")

    def test_naming_result_has_is_valid(self, factory: Any) -> None:
        """NamingResult must have is_valid attribute."""
        result = factory.python_module("orchestrator")
        assert hasattr(result, "is_valid")
        assert isinstance(result.is_valid, bool)

    def test_naming_result_has_violations(self, factory: Any) -> None:
        """NamingResult must have violations list."""
        result = factory.python_module("BADNAME")
        assert hasattr(result, "violations")
        assert isinstance(result.violations, list)

    def test_naming_result_has_suggestion(self, factory: Any) -> None:
        """NamingResult must have suggestion field (may be None for valid names)."""
        result = factory.python_module("orchestrator")
        assert hasattr(result, "suggestion")
