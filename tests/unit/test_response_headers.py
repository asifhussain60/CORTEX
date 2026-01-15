"""
Tests for Response Header Configuration and Injection System

Tests verify:
- Header configuration loading from YAML
- Singleton manager functionality
- Header/footer injection into responses
- Variable substitution
- Multi-domain header rendering
- Global modification impact
"""

import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

from src.core.response_header_config import (
    HeaderConfigurationManager,
    HeaderConfigLoader,
    AuthorInfo,
    CopyrightInfo,
)
from src.core.response_header_injector import ResponseHeaderInjector
from src.core.response_template_engine import (
    ResponseTemplateEngine,
    ResponseTemplateRegistry,
    TemplateDefinition,
    TemplateVariable,
)


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def header_config_yaml():
    """Minimal valid header configuration YAML."""
    return """
metadata:
  version: "1.0"
  created_at: "2026-01-15T00:00:00Z"
  
author:
  name: "Asif Hussain"
  github_handle: "asifhussain60"
  repository: "https://github.com/asifhussain60/CORTEX"
  github_pages: "https://github.com/asifhussain60/CORTEX"

copyright:
  start_year: 2025
  end_year: 2026
  holder: "Asif Hussain"
  notice: "Copyright © {start_year}-{end_year} {holder}. All rights reserved."
  license: "Source-Available"
  license_url: "https://github.com/asifhussain60/CORTEX/blob/main/LICENSE"

header:
  enabled: true
  position: "before_content"
  description: "CORTEX-4.0 style operational header"
  template: |
    ## 🧠 CORTEX {operation}
    **Author:** {author} | **Phase:** {phase} | **Orchestrator:** {orchestrator} ✅
  formatting:
    separator_before_header: false
    separator_after_header: true
    blank_line_after_header: true

copyright_section:
  enabled: true
  position: "after_header"
  description: "Mandatory copyright notice"
  template: |
    **{notice}**
  formatting:
    separator_before: true
    separator_after: true
    bold: true

footer:
  enabled: false
  position: "after_content"
  template: ""

variables:
  mandatory:
    - name: "operation"
      type: "string"
      example: "Governance Evaluation"
      description: "Current operation"
    - name: "phase"
      type: "string"
      example: "PHASE-02"
      description: "Current phase"
    - name: "orchestrator"
      type: "string"
      example: "Orchestrator"
      description: "Orchestrator name"
  auto_populated:
    - name: "author"
      source: "author.name"
      value: "Asif Hussain"
    - name: "notice"
      source: "copyright.notice"
      value: "Copyright © 2025-2026 Asif Hussain. All rights reserved."

enforcement:
  require_on_all_responses: true
  audit_missing_headers: true
  fail_on_missing_variable: false
"""


@pytest.fixture
def temp_config_file(header_config_yaml):
    """Create temporary config file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(header_config_yaml)
        f.flush()
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    if os.path.exists(temp_path):
        os.remove(temp_path)


@pytest.fixture
def header_config_manager(temp_config_file):
    """Create HeaderConfigurationManager instance with loaded config."""
    manager = HeaderConfigurationManager()
    manager.load_configuration(temp_config_file)
    yield manager
    manager.clear()


@pytest.fixture
def mock_template_engine():
    """Create mock ResponseTemplateEngine."""
    engine = Mock(spec=ResponseTemplateEngine)
    engine.render = Mock(return_value="Template rendered content here.")
    engine.render_by_id = Mock(return_value="Template rendered by ID.")
    return engine


@pytest.fixture
def header_injector(mock_template_engine, header_config_manager):
    """Create ResponseHeaderInjector instance."""
    return ResponseHeaderInjector(mock_template_engine, header_config_manager)


@pytest.fixture
def mock_context():
    """Standard context for header substitution."""
    return {
        "operation": "Governance Evaluation",
        "phase": "PHASE-02",
        "orchestrator": "GovernanceOrchestrator",
    }


# =============================================================================
# HEADER CONFIGURATION TESTS
# =============================================================================

class TestHeaderConfigLoader:
    """Tests for HeaderConfigLoader."""

    def test_load_valid_config(self, temp_config_file):
        """Test loading valid configuration file."""
        config = HeaderConfigLoader.load(temp_config_file)
        
        assert config is not None
        assert config.author.name == "Asif Hussain"
        assert config.copyright.start_year == 2025
        assert config.header.enabled is True

    def test_load_nonexistent_file(self):
        """Test loading nonexistent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            HeaderConfigLoader.load("/nonexistent/path/config.yaml")

    def test_author_info_parsed(self, temp_config_file):
        """Test author information is correctly parsed."""
        config = HeaderConfigLoader.load(temp_config_file)
        
        assert config.author.name == "Asif Hussain"
        assert config.author.github_handle == "asifhussain60"
        assert config.author.repository == "https://github.com/asifhussain60/CORTEX"

    def test_copyright_info_parsed(self, temp_config_file):
        """Test copyright information is correctly parsed."""
        config = HeaderConfigLoader.load(temp_config_file)
        
        assert config.copyright.start_year == 2025
        assert config.copyright.end_year == 2026
        assert config.copyright.holder == "Asif Hussain"
        assert config.copyright.license == "Source-Available"

    def test_header_template_parsed(self, temp_config_file):
        """Test header template is correctly parsed."""
        config = HeaderConfigLoader.load(temp_config_file)
        
        assert config.header.enabled is True
        assert "🧠 CORTEX {operation}" in config.header.template
        assert "{author}" in config.header.template


# =============================================================================
# HEADER CONFIGURATION MANAGER TESTS
# =============================================================================

class TestHeaderConfigurationManager:
    """Tests for HeaderConfigurationManager singleton."""

    def test_singleton_pattern(self, temp_config_file):
        """Test singleton returns same instance."""
        manager1 = HeaderConfigurationManager.get_instance()
        manager1.load_configuration(temp_config_file)
        
        manager2 = HeaderConfigurationManager.get_instance()
        
        assert manager1 is manager2
        assert manager2.is_loaded()

    def test_get_author_name(self, header_config_manager):
        """Test getting author name."""
        assert header_config_manager.get_author_name() == "Asif Hussain"

    def test_get_copyright_notice(self, header_config_manager):
        """Test getting copyright notice with substituted values."""
        notice = header_config_manager.get_copyright_notice()
        
        assert "2025-2026" in notice
        assert "Asif Hussain" in notice
        assert "All rights reserved" in notice

    def test_get_repository_url(self, header_config_manager):
        """Test getting repository URL."""
        url = header_config_manager.get_repository_url()
        assert url == "https://github.com/asifhussain60/CORTEX"

    def test_header_enabled(self, header_config_manager):
        """Test header enabled check."""
        assert header_config_manager.is_header_enabled() is True

    def test_copyright_enabled(self, header_config_manager):
        """Test copyright enabled check."""
        assert header_config_manager.is_copyright_enabled() is True

    def test_get_mandatory_variables(self, header_config_manager):
        """Test getting mandatory variable names."""
        mandatory = header_config_manager.get_mandatory_variables()
        
        assert "operation" in mandatory
        assert "phase" in mandatory
        assert "orchestrator" in mandatory

    def test_get_auto_populated_variables(self, header_config_manager):
        """Test getting auto-populated variables."""
        auto_vars = header_config_manager.get_auto_populated_variables()
        
        assert "author" in auto_vars
        assert auto_vars["author"] == "Asif Hussain"
        assert "notice" in auto_vars


# =============================================================================
# HEADER INJECTOR TESTS
# =============================================================================

class TestResponseHeaderInjector:
    """Tests for ResponseHeaderInjector."""

    def test_render_with_header(self, header_injector, mock_context):
        """Test rendering with header injection."""
        result = header_injector.render("governance", "evaluation", mock_context)
        
        # Should contain header
        assert "🧠 CORTEX" in result
        assert "Governance Evaluation" in result
        
        # Should contain copyright
        assert "Copyright" in result
        
        # Should contain template content
        assert "Template rendered content" in result

    def test_render_by_id_with_header(self, header_injector, mock_context):
        """Test render_by_id includes header."""
        result = header_injector.render_by_id("governance.evaluation", mock_context)
        
        assert "🧠 CORTEX" in result
        assert "Template rendered by ID" in result

    def test_header_section_built(self, header_injector, mock_context):
        """Test header section is properly built."""
        header = header_injector._build_header_section(mock_context)
        
        assert header is not None
        assert "Governance Evaluation" in header
        assert "PHASE-02" in header
        assert "GovernanceOrchestrator" in header

    def test_copyright_section_built(self, header_injector, mock_context):
        """Test copyright section is properly built."""
        copyright_section = header_injector._build_copyright_section(mock_context)
        
        assert copyright_section is not None
        assert "Copyright" in copyright_section
        assert "2025-2026" in copyright_section
        assert "Asif Hussain" in copyright_section

    def test_variable_substitution(self, header_injector, mock_context):
        """Test variable substitution in templates."""
        template = "Operation: {operation}, Phase: {phase}, Author: {author}"
        
        result = header_injector._substitute_variables(template, mock_context)
        
        assert result == "Operation: Governance Evaluation, Phase: PHASE-02, Author: Asif Hussain"

    def test_missing_mandatory_variable_handled(self, header_injector):
        """Test handling of missing mandatory variables."""
        incomplete_context = {
            "operation": "Test",
            # Missing phase and orchestrator
        }
        
        # Should not fail, should use empty string
        result = header_injector._substitute_variables(
            "Op: {operation}, Phase: {phase}",
            incomplete_context
        )
        
        assert "Op: Test" in result
        assert "Phase: " in result

    def test_sections_assembled_with_spacing(self, header_injector):
        """Test sections are assembled with proper spacing."""
        sections = ["Header", "Copyright", "Content"]
        
        result = header_injector._assemble_sections(sections)
        
        # Should have blank lines between sections
        assert "\n\n" in result
        assert "Header" in result
        assert "Copyright" in result
        assert "Content" in result

    def test_header_disabled(self, header_injector, mock_context):
        """Test behavior when header is disabled."""
        # Patch the specific check in _build_header_section
        with patch.object(header_injector.config_manager, 'is_header_enabled', return_value=False):
            header = header_injector._build_header_section(mock_context)
            
            assert header is None

    def test_copyright_disabled(self, header_injector, mock_context):
        """Test behavior when copyright is disabled."""
        # Patch the specific check in _build_copyright_section
        with patch.object(header_injector.config_manager, 'is_copyright_enabled', return_value=False):
            copyright_section = header_injector._build_copyright_section(mock_context)
            
            assert copyright_section is None


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestHeaderInjectionIntegration:
    """Integration tests for complete header injection flow."""

    def test_complete_response_with_headers(self, header_injector, mock_context):
        """Test complete response assembly."""
        result = header_injector.render("governance", "evaluation", mock_context)
        
        # Verify all sections present
        lines = result.split('\n')
        
        # Should have header
        assert any("🧠 CORTEX" in line for line in lines)
        # Should have separator
        assert any("---" in line for line in lines)
        # Should have copyright
        assert any("Copyright" in line for line in lines)
        # Should have template content
        assert any("Template rendered content" in line for line in lines)

    def test_header_global_modification(self, header_config_manager, mock_template_engine, mock_context):
        """Test that modifying configuration affects all renders."""
        injector1 = ResponseHeaderInjector(mock_template_engine, header_config_manager)
        injector2 = ResponseHeaderInjector(mock_template_engine, header_config_manager)
        
        # Both injectors share same configuration
        result1 = injector1.render("governance", "test", mock_context)
        result2 = injector2.render("audit", "test", mock_context)
        
        # Both should have same author
        assert "Asif Hussain" in result1
        assert "Asif Hussain" in result2

    def test_get_statistics(self, header_injector):
        """Test getting injector statistics."""
        stats = header_injector.get_statistics()
        
        assert "header_enabled" in stats
        assert "copyright_enabled" in stats
        assert "footer_enabled" in stats
        assert "author" in stats
        assert "repository" in stats
        assert stats["author"] == "Asif Hussain"
        assert "engine_statistics" in stats


# =============================================================================
# EDGE CASES
# =============================================================================

class TestHeaderInjectionEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_empty_context(self, header_injector):
        """Test rendering with empty context."""
        empty_context = {}
        
        # Should not crash, should use defaults
        result = header_injector._build_header_section(empty_context)
        
        assert result is not None

    def test_special_characters_in_variables(self, header_injector):
        """Test handling special characters in variable values."""
        context = {
            "operation": "Test & Verify (v2.0)",
            "phase": "PHASE-03|PHASE-04",
            "orchestrator": "Test/Orchestrator"
        }
        
        header = header_injector._build_header_section(context)
        
        assert "Test & Verify (v2.0)" in header
        assert "PHASE-03|PHASE-04" in header

    def test_unicode_in_variables(self, header_injector):
        """Test handling unicode characters."""
        context = {
            "operation": "评估 🚀",
            "phase": "PHASE-02",
            "orchestrator": "Orch™"
        }
        
        header = header_injector._build_header_section(context)
        
        assert "评估 🚀" in header

    def test_very_long_variable_values(self, header_injector):
        """Test handling very long variable values."""
        long_value = "x" * 1000
        context = {
            "operation": long_value,
            "phase": "PHASE-02",
            "orchestrator": "Orchestrator"
        }
        
        header = header_injector._build_header_section(context)
        
        assert long_value in header


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
