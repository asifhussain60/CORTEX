"""Unit Tests — naming.py

Phase: PHASE-51
CORE: CORE-008 (TDD — tests first), CORE-028 (naming conventions)
"""

import pytest


class TestToKebabCase:
    """to_kebab_case() — convert filenames to kebab-case."""

    def test_screaming_case(self) -> None:
        from cortex.orchestrators.health.naming import to_kebab_case

        assert to_kebab_case("AUDIT_REPORT.txt") == "audit-report.txt"

    def test_snake_case(self) -> None:
        from cortex.orchestrators.health.naming import to_kebab_case

        assert to_kebab_case("my_document.md") == "my-document.md"

    def test_already_kebab(self) -> None:
        from cortex.orchestrators.health.naming import to_kebab_case

        assert to_kebab_case("already-kebab.yaml") == "already-kebab.yaml"

    def test_mixed_case_with_underscores(self) -> None:
        from cortex.orchestrators.health.naming import to_kebab_case

        assert to_kebab_case("My_Mixed_File.txt") == "my-mixed-file.txt"

    def test_consecutive_separators_collapsed(self) -> None:
        from cortex.orchestrators.health.naming import to_kebab_case

        assert to_kebab_case("foo__bar--baz.txt") == "foo-bar-baz.txt"

    def test_preserves_extension(self) -> None:
        from cortex.orchestrators.health.naming import to_kebab_case

        assert to_kebab_case("REPORT.TAR.GZ") == "report.tar.gz"

    def test_dot_prefix_preserved(self) -> None:
        from cortex.orchestrators.health.naming import to_kebab_case

        assert to_kebab_case(".MY_CONFIG") == ".my-config"


class TestToSnakeCase:
    """to_snake_case() — convert Python filenames to snake_case."""

    def test_kebab_to_snake(self) -> None:
        from cortex.orchestrators.health.naming import to_snake_case

        assert to_snake_case("my-module.py") == "my_module.py"

    def test_already_snake(self) -> None:
        from cortex.orchestrators.health.naming import to_snake_case

        assert to_snake_case("already_snake.py") == "already_snake.py"

    def test_screaming_to_snake(self) -> None:
        from cortex.orchestrators.health.naming import to_snake_case

        assert to_snake_case("AUDIT_REPORT.py") == "audit_report.py"

    def test_mixed_case(self) -> None:
        from cortex.orchestrators.health.naming import to_snake_case

        assert to_snake_case("MyModule.py") == "my_module.py"


class TestIsScreaming:
    """is_screaming() — detect SCREAMING_CASE filenames."""

    def test_screaming(self) -> None:
        from cortex.orchestrators.health.naming import is_screaming

        assert is_screaming("AUDIT_REPORT.txt") is True

    def test_not_screaming(self) -> None:
        from cortex.orchestrators.health.naming import is_screaming

        assert is_screaming("audit-report.txt") is False

    def test_single_word_upper(self) -> None:
        from cortex.orchestrators.health.naming import is_screaming

        assert is_screaming("README.md") is True

    def test_allowed_screaming_excluded(self) -> None:
        """README, CHANGELOG, LICENSE are conventionally uppercase — not violations."""
        from cortex.orchestrators.health.naming import is_screaming

        # Still returns True — caller decides policy
        assert is_screaming("README.md") is True


class TestValidPythonName:
    """is_valid_python_name() — enforce snake_case for .py files."""

    def test_valid(self) -> None:
        from cortex.orchestrators.health.naming import is_valid_python_name

        assert is_valid_python_name("my_module.py") is True

    def test_dunder_valid(self) -> None:
        from cortex.orchestrators.health.naming import is_valid_python_name

        assert is_valid_python_name("__init__.py") is True

    def test_kebab_invalid(self) -> None:
        from cortex.orchestrators.health.naming import is_valid_python_name

        assert is_valid_python_name("my-module.py") is False

    def test_uppercase_invalid(self) -> None:
        from cortex.orchestrators.health.naming import is_valid_python_name

        assert is_valid_python_name("MyModule.py") is False


class TestClassifyNamingViolation:
    """classify_naming_violation() — categorize naming issues."""

    def test_python_file_with_kebab(self) -> None:
        from cortex.orchestrators.health.naming import classify_naming_violation

        result = classify_naming_violation("my-module.py")
        assert result is not None
        assert result.violation_type == "non_snake_case"
        assert result.suggested_name == "my_module.py"

    def test_yaml_with_underscore(self) -> None:
        from cortex.orchestrators.health.naming import classify_naming_violation

        result = classify_naming_violation("my_config.yaml")
        assert result is not None
        assert result.violation_type == "non_kebab_case"
        assert result.suggested_name == "my-config.yaml"

    def test_compliant_python(self) -> None:
        from cortex.orchestrators.health.naming import classify_naming_violation

        result = classify_naming_violation("valid_module.py")
        assert result is None

    def test_compliant_yaml(self) -> None:
        from cortex.orchestrators.health.naming import classify_naming_violation

        result = classify_naming_violation("valid-config.yaml")
        assert result is None
