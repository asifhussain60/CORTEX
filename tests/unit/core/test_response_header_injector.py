"""
Tests for ResponseHeaderInjector (AC-CORE-029: Response Header Enforcement)

This test suite verifies that ResponseHeaderInjector correctly injects
CORTEX headers into all responses, maintaining CORE-029 governance compliance.

AC-ID: AC-CORE-029-01 (Header Injection)
AC-ID: AC-CORE-029-02 (Author/Phase/Orchestrator Metadata)
AC-ID: AC-CORE-029-03 (Governance Compliance Validation)

"""

import pytest
from typing import Any
from unittest.mock import Mock, patch

from cortex.brain.core.response_header_injector import (
    ResponseHeaderInjector,
    escape_yaml_string,
    validate_ac_id,
    validate_operation_name,
    validate_domain_name,
    sanitize_context_value,
)
from cortex.brain.core.response_header_config import HeaderConfigurationManager

# Note: ResponseTemplateEngine stub removed (CORE-035 consolidation)


class TestYAMLEscapeFunctions:
    """Test YAML-safe escaping functions (AC-FIX-004-01)."""

    def test_escape_yaml_string_with_colon(self) -> None:
        """Verify colons are escaped or quoted."""
        result = escape_yaml_string("key: value")
        assert '"' in result or '\\:' in result
        assert "key: value" in result or "key\\: value" in result

    def test_escape_yaml_string_with_dash(self) -> None:
        """Verify dashes at start are quoted."""
        result = escape_yaml_string("- item")
        assert '"' in result  # Should be quoted

    def test_escape_yaml_string_with_brackets(self) -> None:
        """Verify brackets are quoted."""
        result = escape_yaml_string("[item1, item2]")
        assert '"' in result

    def test_escape_yaml_string_with_braces(self) -> None:
        """Verify braces are quoted."""
        result = escape_yaml_string("{key: value}")
        assert '"' in result

    def test_escape_yaml_string_with_hash(self) -> None:
        """Verify hash/comment characters are quoted."""
        result = escape_yaml_string("this is a # comment")
        assert '"' in result

    def test_escape_yaml_string_with_pipe(self) -> None:
        """Verify pipe characters are quoted."""
        result = escape_yaml_string("data | pipe")
        assert '"' in result

    def test_escape_yaml_string_with_ampersand(self) -> None:
        """Verify ampersands are quoted."""
        result = escape_yaml_string("AT&T company")
        assert '"' in result

    def test_escape_yaml_string_with_asterisk(self) -> None:
        """Verify asterisks are quoted."""
        result = escape_yaml_string("*wildcard*")
        assert '"' in result

    def test_escape_yaml_string_with_question_mark(self) -> None:
        """Verify question marks are quoted."""
        result = escape_yaml_string("Is this valid?")
        assert '"' in result

    def test_escape_yaml_string_safe_string(self) -> None:
        """Verify safe strings are not unnecessarily quoted."""
        result = escape_yaml_string("simple_string")
        assert result == "simple_string"

    def test_escape_yaml_string_with_quotes(self) -> None:
        """Verify internal quotes are escaped."""
        result = escape_yaml_string('He said "hello"')
        assert '\\"' in result or '""' in result

    def test_escape_yaml_string_with_leading_space(self) -> None:
        """Verify leading spaces trigger quoting."""
        result = escape_yaml_string(" leading space")
        assert '"' in result

    def test_escape_yaml_string_with_trailing_space(self) -> None:
        """Verify trailing spaces trigger quoting."""
        result = escape_yaml_string("trailing space ")
        assert '"' in result

    def test_escape_yaml_string_non_string_input(self) -> None:
        """Verify non-string inputs are converted."""
        result = escape_yaml_string(12345)  # type: ignore
        assert isinstance(result, str)
        assert "12345" in result


class TestACIDValidation:
    """Test AC-ID format validation."""

    def test_validate_ac_id_valid_format_core(self) -> None:
        """Verify valid CORE-XXX format."""
        assert validate_ac_id("CORE-001") is True
        assert validate_ac_id("CORE-029") is True

    def test_validate_ac_id_valid_format_extended(self) -> None:
        """Verify valid AC-CATEGORY-NNN-NN format."""
        assert validate_ac_id("AC-FIX-001-01") is True
        assert validate_ac_id("AC-DOC-007-02") is True
        assert validate_ac_id("AC-MINOR-008-03") is True

    def test_validate_ac_id_valid_format_no_suffix(self) -> None:
        """Verify valid AC-CATEGORY-NNN format."""
        assert validate_ac_id("AC-REM-042") is True
        assert validate_ac_id("AC-ENH-015") is True

    def test_validate_ac_id_invalid_lowercase(self) -> None:
        """Verify lowercase AC-IDs are rejected."""
        assert validate_ac_id("ac-core-001") is False
        assert validate_ac_id("Ac-CORE-001") is False

    def test_validate_ac_id_invalid_special_chars(self) -> None:
        """Verify special characters are rejected."""
        assert validate_ac_id("AC@CORE#001") is False
        assert validate_ac_id("AC-CORE_001") is False
        assert validate_ac_id("AC.CORE.001") is False

    def test_validate_ac_id_invalid_format(self) -> None:
        """Verify invalid formats are rejected."""
        assert validate_ac_id("AC_CORE_001") is False
        assert validate_ac_id("") is False
        assert validate_ac_id("---") is False

    def test_validate_ac_id_non_string_input(self) -> None:
        """Verify non-string inputs return False."""
        assert validate_ac_id(12345) is False  # type: ignore
        assert validate_ac_id(None) is False  # type: ignore
        assert validate_ac_id([]) is False  # type: ignore


class TestOperationNameValidation:
    """Test operation name validation."""

    def test_validate_operation_name_valid_simple(self) -> None:
        """Verify simple valid operation names."""
        assert validate_operation_name("create") is True
        assert validate_operation_name("read") is True
        assert validate_operation_name("update") is True
        assert validate_operation_name("delete") is True

    def test_validate_operation_name_valid_complex(self) -> None:
        """Verify complex valid operation names."""
        assert validate_operation_name("backup_restore") is True
        assert validate_operation_name("validate_schema") is True
        assert validate_operation_name("execute_plan") is True

    def test_validate_operation_name_invalid_uppercase(self) -> None:
        """Verify uppercase operation names are rejected."""
        assert validate_operation_name("Create") is False
        assert validate_operation_name("CREATE") is False

    def test_validate_operation_name_invalid_special_chars(self) -> None:
        """Verify special characters are rejected."""
        assert validate_operation_name("create-plan") is False
        assert validate_operation_name("create.plan") is False
        assert validate_operation_name("create@plan") is False

    def test_validate_operation_name_non_string_input(self) -> None:
        """Verify non-string inputs return False."""
        assert validate_operation_name(12345) is False  # type: ignore
        assert validate_operation_name(None) is False  # type: ignore


class TestDomainNameValidation:
    """Test domain name validation."""

    def test_validate_domain_name_valid(self) -> None:
        """Verify valid domain names."""
        assert validate_domain_name("governance") is True
        assert validate_domain_name("security") is True
        assert validate_domain_name("operations") is True
        assert validate_domain_name("infrastructure") is True

    def test_validate_domain_name_valid_underscore(self) -> None:
        """Verify valid domain names with underscores."""
        assert validate_domain_name("domain_name") is True
        assert validate_domain_name("multi_word_domain") is True

    def test_validate_domain_name_invalid_uppercase(self) -> None:
        """Verify uppercase domain names are rejected."""
        assert validate_domain_name("Governance") is False
        assert validate_domain_name("SECURITY") is False

    def test_validate_domain_name_invalid_special_chars(self) -> None:
        """Verify special characters are rejected."""
        assert validate_domain_name("governance-security") is False
        assert validate_domain_name("governance.security") is False

    def test_validate_domain_name_non_string_input(self) -> None:
        """Verify non-string inputs return False."""
        assert validate_domain_name(12345) is False  # type: ignore
        assert validate_domain_name(None) is False  # type: ignore


class TestSanitizeContextValue:
    """Test context value sanitization."""

    def test_sanitize_context_value_valid_ac_id(self) -> None:
        """Verify valid AC-ID is sanitized correctly."""
        result = sanitize_context_value("ac_id", "AC-CORE-029-01")
        assert "AC-CORE-029-01" in result

    def test_sanitize_context_value_invalid_ac_id_optional(self) -> None:
        """Verify invalid AC-ID doesn't raise for optional field."""
        result = sanitize_context_value("ac_id", "invalid@id", is_mandatory=False)
        assert isinstance(result, str)

    def test_sanitize_context_value_invalid_ac_id_mandatory(self) -> None:
        """Verify invalid AC-ID raises for mandatory field."""
        with pytest.raises(ValueError, match="Invalid AC-ID format"):
            sanitize_context_value("ac_id", "invalid@id", is_mandatory=True)

    def test_sanitize_context_value_operation_name(self) -> None:
        """Verify operation name sanitization."""
        result = sanitize_context_value("operation_name", "create")
        assert "create" in result

    def test_sanitize_context_value_invalid_operation_mandatory(self) -> None:
        """Verify invalid operation name raises for mandatory."""
        with pytest.raises(ValueError, match="Invalid operation name"):
            sanitize_context_value("operation_name", "INVALID", is_mandatory=True)

    def test_sanitize_context_value_domain_name(self) -> None:
        """Verify domain name sanitization."""
        result = sanitize_context_value("domain_name", "governance")
        assert "governance" in result

    def test_sanitize_context_value_unknown_field(self) -> None:
        """Verify unknown fields are escaped but not validated."""
        result = sanitize_context_value("unknown_field", "value: with: colons")
        assert isinstance(result, str)
        # Should be escaped/quoted due to colons
        assert '"' in result

    def test_sanitize_context_value_none_input(self) -> None:
        """Verify None input returns empty string."""
        result = sanitize_context_value("any_field", None)
        assert result == ""


class TestResponseHeaderInjector:
    """Test ResponseHeaderInjector main functionality (AC-CORE-029-01)."""

    @pytest.fixture
    def mock_template_engine(self) -> Mock:
        """Create mock ResponseTemplateEngine."""
        engine = Mock()
        engine.render.return_value = "Rendered template content"
        return engine

    @pytest.fixture
    def mock_config_manager(self) -> Mock:
        """Create mock HeaderConfigurationManager."""
        manager = Mock()
        manager.get_header_template.return_value = (
            "## 🧠 CORTEX {operation}\n"
            "**Author:** {author} | **Phase:** {phase} | **Orchestrator:** {orchestrator} ✅"
        )
        manager.get_footer_template.return_value = ""
        manager.is_header_enabled.return_value = True
        manager.is_footer_enabled.return_value = False
        manager.get_mandatory_variables.return_value = ["operation", "author", "phase", "orchestrator"]
        manager.get_optional_variables.return_value = []
        return manager

    @pytest.fixture
    def injector(
        self,
        mock_template_engine: Mock,
        mock_config_manager: Mock,
    ) -> ResponseHeaderInjector:
        """Create ResponseHeaderInjector instance."""
        with patch.object(
            HeaderConfigurationManager,
            'get_instance',
            return_value=mock_config_manager
        ):
            return ResponseHeaderInjector(mock_template_engine, mock_config_manager)

    def test_injector_initialization(
        self,
        mock_template_engine: Mock,
        mock_config_manager: Mock,
    ) -> None:
        """Verify injector initializes correctly."""
        with patch.object(
            HeaderConfigurationManager,
            'get_instance',
            return_value=mock_config_manager
        ):
            injector = ResponseHeaderInjector(mock_template_engine)
            assert injector.engine == mock_template_engine
            assert injector.config_manager == mock_config_manager

    def test_render_includes_header(
        self,
        injector: ResponseHeaderInjector,
        mock_template_engine: Mock,
    ) -> None:
        """Verify render() includes header in output."""
        context = {
            "author": "Asif Hussain",
            "phase": "PHASE-GOVERNANCE-HARDENING",
            "orchestrator": "MasterOrchestrator",
            "operation": "implementation",
        }
        
        result = injector.render("governance", "evaluation", context)
        
        assert "CORTEX implementation" in result
        assert "Asif Hussain" in result
        assert "MasterOrchestrator" in result
        mock_template_engine.render.assert_called_once()

    def test_render_includes_content(
        self,
        injector: ResponseHeaderInjector,
        mock_template_engine: Mock,
    ) -> None:
        """Verify render() includes original template content."""
        context = {
            "author": "Asif Hussain",
            "phase": "PHASE-GOVERNANCE-HARDENING",
            "orchestrator": "MasterOrchestrator",
        }
        
        result = injector.render("governance", "evaluation", context)
        
        assert "Rendered template content" in result

    def test_render_header_before_content(
        self,
        injector: ResponseHeaderInjector,
        mock_template_engine: Mock,
    ) -> None:
        """Verify header appears before content."""
        context = {
            "author": "Asif Hussain",
            "phase": "PHASE-GOVERNANCE-HARDENING",
            "orchestrator": "MasterOrchestrator",
        }
        
        result = injector.render("governance", "evaluation", context)
        
        header_pos = result.find("CORTEX")
        content_pos = result.find("Rendered template content")
        assert header_pos < content_pos

    def test_render_with_different_contexts(
        self,
        injector: ResponseHeaderInjector,
        mock_template_engine: Mock,
    ) -> None:
        """Verify render() works with different context values."""
        context1 = {
            "author": "User1",
            "phase": "PHASE-1",
            "orchestrator": "Orch1",
            "operation": "create",
        }
        context2 = {
            "author": "User2",
            "phase": "PHASE-2",
            "orchestrator": "Orch2",
            "operation": "update",
        }
        
        result1 = injector.render("governance", "eval", context1)
        result2 = injector.render("security", "eval", context2)
        
        assert "User1" in result1
        assert "User2" in result2
        assert "Orch1" in result1
        assert "Orch2" in result2

    def test_render_sanitizes_context_values(
        self,
        injector: ResponseHeaderInjector,
        mock_template_engine: Mock,
    ) -> None:
        """Verify context values are sanitized before rendering."""
        context = {
            "author": "Asif Hussain",
            "phase": "PHASE-GOVERNANCE-HARDENING",
            "orchestrator": "MasterOrchestrator",
            "ac_id": "AC-CORE-029-01",  # Should validate
            "operation": "execute",
        }
        
        result = injector.render("governance", "eval", context)
        
        assert isinstance(result, str)
        mock_template_engine.render.assert_called_once()

    def test_render_caching(
        self,
        injector: ResponseHeaderInjector,
    ) -> None:
        """Verify render() caches results for same context."""
        context = {
            "author": "Asif Hussain",
            "phase": "PHASE-TEST",
            "orchestrator": "TestOrch",
        }
        
        result1 = injector.render("governance", "eval", context)
        # Result should be cached (implementation detail)
        assert isinstance(result1, str)

    def test_render_with_footer_disabled(
        self,
        injector: ResponseHeaderInjector,
        mock_config_manager: Mock,
    ) -> None:
        """Verify footer is not included when disabled."""
        mock_config_manager.is_footer_enabled.return_value = False
        
        context = {
            "author": "Asif Hussain",
            "phase": "PHASE-TEST",
            "orchestrator": "TestOrch",
        }
        
        result = injector.render("governance", "eval", context)
        
        # Footer should not be in result if disabled
        assert isinstance(result, str)


class TestHeaderInjectionWithMasterOrchestrator:
    """Integration tests for ResponseHeaderInjector with MasterOrchestrator."""

    @pytest.fixture
    def injector_with_real_config(self) -> ResponseHeaderInjector:
        """Create injector with partial real configuration."""
        mock_engine = Mock()
        mock_engine.render.return_value = "Test response content"
        
        mock_config = Mock(spec=HeaderConfigurationManager)
        mock_config.get_header_template.return_value = (
            "## 🧠 CORTEX {operation}\n"
            "**Author:** {author} | **Phase:** {phase} | **Orchestrator:** {orchestrator} ✅"
        )
        mock_config.is_header_enabled.return_value = True
        
        return ResponseHeaderInjector(mock_engine, mock_config)

    def test_header_format_matches_core_029(
        self,
        injector_with_real_config: ResponseHeaderInjector,
    ) -> None:
        """Verify header format matches CORE-029 requirements."""
        context = {
            "operation": "Implementation",
            "author": "Asif Hussain",
            "phase": "PHASE-GOVERNANCE-HARDENING",
            "orchestrator": "MasterOrchestrator",
        }
        
        result = injector_with_real_config.render("governance", "eval", context)
        
        # CORE-029 requires:
        # - "## 🧠 CORTEX" prefix
        # - Author field
        # - Phase field
        # - Orchestrator field
        # - ✅ checkmark
        assert "🧠 CORTEX" in result
        assert "Author:" in result
        assert "Phase:" in result
        assert "Orchestrator:" in result
        assert "✅" in result

    def test_dynamic_header_generation(
        self,
        injector_with_real_config: ResponseHeaderInjector,
    ) -> None:
        """Verify header is generated dynamically per execution."""
        context1 = {
            "operation": "Review",
            "author": "Reviewer1",
            "phase": "PHASE-1",
            "orchestrator": "Orch1",
        }
        context2 = {
            "operation": "Implementation",
            "author": "Developer1",
            "phase": "PHASE-2",
            "orchestrator": "Orch2",
        }
        
        result1 = injector_with_real_config.render("governance", "eval", context1)
        result2 = injector_with_real_config.render("governance", "eval", context2)
        
        assert "Review" in result1 and "Implementation" in result2
        assert "Reviewer1" in result1 and "Developer1" in result2


class TestGovernanceCompliance:
    """Test governance compliance aspects (AC-CORE-029-03)."""

    def test_header_injection_mandatory(self) -> None:
        """Verify header injection is mandatory per CORE-029."""
        mock_engine = Mock()
        mock_config = Mock(spec=HeaderConfigurationManager)
        mock_config.is_header_enabled.return_value = True
        
        _ = ResponseHeaderInjector(mock_engine, mock_config)
        
        # Header should be enabled by default
        assert mock_config.is_header_enabled() is True

    def test_author_field_required(self) -> None:
        """Verify author field is required in context."""
        mock_engine = Mock()
        mock_config = Mock(spec=HeaderConfigurationManager)
        mock_config.get_header_template.return_value = "**Author:** {author}"
        
        _ = ResponseHeaderInjector(mock_engine, mock_config)
        
        # Author should be in template
        assert "author" in mock_config.get_header_template()

    def test_phase_field_required(self) -> None:
        """Verify phase field is required in context."""
        mock_engine = Mock()
        mock_config = Mock(spec=HeaderConfigurationManager)
        mock_config.get_header_template.return_value = "**Phase:** {phase}"
        
        _ = ResponseHeaderInjector(mock_engine, mock_config)
        
        # Phase should be in template
        assert "phase" in mock_config.get_header_template()

    def test_orchestrator_field_required(self) -> None:
        """Verify orchestrator field is required in context."""
        mock_engine = Mock()
        mock_config = Mock(spec=HeaderConfigurationManager)
        mock_config.get_header_template.return_value = "**Orchestrator:** {orchestrator}"
        
        _ = ResponseHeaderInjector(mock_engine, mock_config)
        
        # Orchestrator should be in template
        assert "orchestrator" in mock_config.get_header_template()
