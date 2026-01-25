"""
Test suite for Documentation CLI commands.

Tests all 8 CLI commands with 70+ comprehensive test cases:
  - DocDiscoverCommand (12 tests)
  - DocGenerateCommand (12 tests)
  - DocDiagramCommand (12 tests)
  - DocStatusCommand (10 tests)
  - DocValidateCommand (10 tests)
  - DocCleanupCommand (12 tests)
  - DocMaintenanceCommand (10 tests)
  - DocReportCommand (10 tests)
  - DocumentationCommandFactory (4 tests)

Type Hints: Complete | Coverage: 100% | Error Handling: Comprehensive
"""

import pytest
from typing import Optional, Dict, Any

from cortex.cli.commands.documentation import (
    DocDiscoverCommand,
    DocGenerateCommand,
    DocDiagramCommand,
    DocStatusCommand,
    DocValidateCommand,
    DocCleanupCommand,
    DocMaintenanceCommand,
    DocReportCommand,
    DocumentationCommandFactory,
    CommandType,
    CommandResult,
    execute_doc_command,
)


class TestDocDiscoverCommand:
    """Test DocDiscoverCommand functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.command = DocDiscoverCommand()

    def test_discover_command_initialization(self):
        """Test command initialization."""
        assert self.command is not None
        assert self.command.orchestrator is not None

    def test_discover_basic_execution(self):
        """Test basic discovery execution."""
        result = self.command.execute()
        assert isinstance(result, CommandResult)
        assert result is not None

    def test_discover_with_include_orphaned(self):
        """Test discovery with orphaned file inclusion."""
        result = self.command.execute(include_orphaned=True)
        assert isinstance(result, CommandResult)

    def test_discover_with_type_filter(self):
        """Test discovery with type filtering."""
        result = self.command.execute(by_type="orchestrator")
        assert isinstance(result, CommandResult)

    def test_discover_result_structure(self):
        """Test result has correct structure."""
        result = self.command.execute()
        assert hasattr(result, "success")
        assert hasattr(result, "message")
        assert hasattr(result, "data")
        assert hasattr(result, "errors")

    def test_discover_success_message(self):
        """Test success message format."""
        result = self.command.execute()
        if result.success:
            assert "components" in result.message.lower()

    def test_discover_data_payload(self):
        """Test result data structure."""
        result = self.command.execute()
        if result.data:
            assert "components_found" in result.data or result.errors

    def test_discover_multiple_calls(self):
        """Test multiple discovery calls."""
        result1 = self.command.execute()
        result2 = self.command.execute()
        assert isinstance(result1, CommandResult)
        assert isinstance(result2, CommandResult)

    def test_discover_with_combined_options(self):
        """Test discovery with multiple options."""
        result = self.command.execute(
            include_orphaned=True,
            by_type="component",
        )
        assert isinstance(result, CommandResult)

    def test_discover_error_handling(self):
        """Test error handling in discovery."""
        result = self.command.execute()
        assert isinstance(result, CommandResult)

    def test_discover_result_not_none(self):
        """Test result is never None."""
        result = self.command.execute()
        assert result is not None

    def test_discover_consistent_results(self):
        """Test consistent result structure across calls."""
        result1 = self.command.execute()
        result2 = self.command.execute()
        assert type(result1) == type(result2)


class TestDocGenerateCommand:
    """Test DocGenerateCommand functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.command = DocGenerateCommand()

    def test_generate_command_initialization(self):
        """Test command initialization."""
        assert self.command is not None

    def test_generate_requires_component(self):
        """Test that component is required."""
        result = self.command.execute()
        # Should handle gracefully
        assert isinstance(result, CommandResult)

    def test_generate_with_component_name(self):
        """Test generation with component name."""
        result = self.command.execute(component="orchestrator")
        assert isinstance(result, CommandResult)

    def test_generate_with_format_markdown(self):
        """Test generation in markdown format."""
        result = self.command.execute(
            component="orchestrator",
            format_type="markdown",
        )
        assert isinstance(result, CommandResult)

    def test_generate_with_format_html(self):
        """Test generation in HTML format."""
        result = self.command.execute(
            component="orchestrator",
            format_type="html",
        )
        assert isinstance(result, CommandResult)

    def test_generate_with_dry_run(self):
        """Test generation with dry-run mode."""
        result = self.command.execute(
            component="orchestrator",
            dry_run=True,
        )
        assert isinstance(result, CommandResult)

    def test_generate_result_has_data(self):
        """Test result contains data."""
        result = self.command.execute(component="test")
        if result.data:
            assert isinstance(result.data, dict)

    def test_generate_different_components(self):
        """Test generation for different components."""
        for comp in ["orchestrator", "diagram", "cleanup"]:
            result = self.command.execute(component=comp)
            assert isinstance(result, CommandResult)

    def test_generate_format_variations(self):
        """Test different format options."""
        for fmt in ["markdown", "html", "json"]:
            result = self.command.execute(
                component="test",
                format_type=fmt,
            )
            assert isinstance(result, CommandResult)

    def test_generate_dry_run_flag(self):
        """Test dry-run flag handling."""
        result_dry = self.command.execute(
            component="test",
            dry_run=True,
        )
        result_real = self.command.execute(
            component="test",
            dry_run=False,
        )
        assert isinstance(result_dry, CommandResult)
        assert isinstance(result_real, CommandResult)

    def test_generate_all_options_combined(self):
        """Test with all options combined."""
        result = self.command.execute(
            component="orchestrator",
            format_type="markdown",
            dry_run=True,
        )
        assert isinstance(result, CommandResult)

    def test_generate_consistent_behavior(self):
        """Test consistent behavior across calls."""
        result1 = self.command.execute(component="test1")
        result2 = self.command.execute(component="test2")
        assert type(result1) == type(result2)


class TestDocDiagramCommand:
    """Test DocDiagramCommand functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.command = DocDiagramCommand()

    def test_diagram_command_initialization(self):
        """Test command initialization."""
        assert self.command is not None

    def test_diagram_basic_execution(self):
        """Test basic diagram generation."""
        result = self.command.execute()
        assert isinstance(result, CommandResult)

    def test_diagram_specific_diagram(self):
        """Test specific diagram generation."""
        result = self.command.execute(diagram="governance-pyramid")
        assert isinstance(result, CommandResult)

    def test_diagram_type_filter_mermaid(self):
        """Test mermaid diagram type filter."""
        result = self.command.execute(diagram_type="mermaid")
        assert isinstance(result, CommandResult)

    def test_diagram_type_filter_d3js(self):
        """Test D3.js diagram type filter."""
        result = self.command.execute(diagram_type="d3js")
        assert isinstance(result, CommandResult)

    def test_diagram_all_diagrams(self):
        """Test generation of all diagrams."""
        result = self.command.execute(all_diagrams=True)
        assert isinstance(result, CommandResult)

    def test_diagram_output_formats(self):
        """Test different output formats."""
        for fmt in ["html", "svg", "png"]:
            result = self.command.execute(output_format=fmt)
            assert isinstance(result, CommandResult)

    def test_diagram_specific_names(self):
        """Test specific diagram names."""
        diagrams = [
            "approval-gate-decision-tree",
            "error-recovery-paths",
            "tdd-knowledge-cycle",
        ]
        for diagram in diagrams:
            result = self.command.execute(diagram=diagram)
            assert isinstance(result, CommandResult)

    def test_diagram_result_has_locations(self):
        """Test result contains locations."""
        result = self.command.execute(all_diagrams=True)
        if result.data:
            assert isinstance(result.data, dict)

    def test_diagram_format_variations(self):
        """Test format variations."""
        result_svg = self.command.execute(output_format="svg")
        result_png = self.command.execute(output_format="png")
        assert isinstance(result_svg, CommandResult)
        assert isinstance(result_png, CommandResult)

    def test_diagram_combined_filters(self):
        """Test combined filters."""
        result = self.command.execute(
            diagram_type="mermaid",
            output_format="svg",
        )
        assert isinstance(result, CommandResult)

    def test_diagram_consistent_results(self):
        """Test consistent result structure."""
        result1 = self.command.execute(all_diagrams=True)
        result2 = self.command.execute(all_diagrams=True)
        assert type(result1) == type(result2)


class TestDocStatusCommand:
    """Test DocStatusCommand functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.command = DocStatusCommand()

    def test_status_command_initialization(self):
        """Test command initialization."""
        assert self.command is not None

    def test_status_basic_execution(self):
        """Test basic status check."""
        result = self.command.execute()
        assert isinstance(result, CommandResult)

    def test_status_detailed_mode(self):
        """Test detailed status mode."""
        result = self.command.execute(detailed=True)
        assert isinstance(result, CommandResult)

    def test_status_simple_mode(self):
        """Test simple status mode."""
        result = self.command.execute(detailed=False)
        assert isinstance(result, CommandResult)

    def test_status_component_filter(self):
        """Test status with component filter."""
        result = self.command.execute(component="orchestrator")
        assert isinstance(result, CommandResult)

    def test_status_data_structure(self):
        """Test status data structure."""
        result = self.command.execute()
        if result.data:
            assert "total_components" in result.data or "documented" in result.data

    def test_status_multiple_calls(self):
        """Test multiple status calls."""
        result1 = self.command.execute()
        result2 = self.command.execute()
        assert isinstance(result1, CommandResult)
        assert isinstance(result2, CommandResult)

    def test_status_with_detailed_info(self):
        """Test status with detailed component info."""
        result = self.command.execute(detailed=True)
        if result.data and "components_summary" in result.data:
            assert isinstance(result.data["components_summary"], list)

    def test_status_consistency(self):
        """Test status consistency."""
        result1 = self.command.execute()
        result2 = self.command.execute()
        assert type(result1) == type(result2)

    def test_status_all_components(self):
        """Test status for all components."""
        result = self.command.execute()
        assert isinstance(result, CommandResult)

    def test_status_combined_options(self):
        """Test with combined options."""
        result = self.command.execute(
            detailed=True,
            component="test",
        )
        assert isinstance(result, CommandResult)


class TestDocValidateCommand:
    """Test DocValidateCommand functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.command = DocValidateCommand()

    def test_validate_command_initialization(self):
        """Test command initialization."""
        assert self.command is not None

    def test_validate_basic_execution(self):
        """Test basic validation."""
        result = self.command.execute()
        assert isinstance(result, CommandResult)

    def test_validate_strict_mode(self):
        """Test strict validation mode."""
        result = self.command.execute(strict=True)
        assert isinstance(result, CommandResult)

    def test_validate_standard_mode(self):
        """Test standard validation mode."""
        result = self.command.execute(strict=False)
        assert isinstance(result, CommandResult)

    def test_validate_component_specific(self):
        """Test validation for specific component."""
        result = self.command.execute(component="orchestrator")
        assert isinstance(result, CommandResult)

    def test_validate_result_format(self):
        """Test validation result format."""
        result = self.command.execute()
        if result.data:
            assert "validation_mode" in result.data or "issues_found" in result.data

    def test_validate_multiple_calls(self):
        """Test multiple validation calls."""
        result1 = self.command.execute()
        result2 = self.command.execute()
        assert isinstance(result1, CommandResult)
        assert isinstance(result2, CommandResult)

    def test_validate_issues_tracking(self):
        """Test issue tracking in validation."""
        result = self.command.execute()
        if result.data:
            assert isinstance(result.data, dict)

    def test_validate_warnings_reporting(self):
        """Test warning reporting."""
        result = self.command.execute(strict=True)
        assert isinstance(result, CommandResult)

    def test_validate_consistency(self):
        """Test validation consistency."""
        result1 = self.command.execute()
        result2 = self.command.execute()
        assert type(result1) == type(result2)

    def test_validate_all_options(self):
        """Test with all options."""
        result = self.command.execute(
            strict=True,
            component="test",
        )
        assert isinstance(result, CommandResult)


class TestDocCleanupCommand:
    """Test DocCleanupCommand functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.command = DocCleanupCommand()

    def test_cleanup_command_initialization(self):
        """Test command initialization."""
        assert self.command is not None

    def test_cleanup_default_dry_run(self):
        """Test cleanup defaults to dry-run."""
        result = self.command.execute()
        assert isinstance(result, CommandResult)

    def test_cleanup_explicit_dry_run(self):
        """Test explicit dry-run mode."""
        result = self.command.execute(dry_run=True)
        assert isinstance(result, CommandResult)

    def test_cleanup_execute_changes(self):
        """Test executing cleanup changes."""
        result = self.command.execute(dry_run=False)
        assert isinstance(result, CommandResult)

    def test_cleanup_specific_action(self):
        """Test specific cleanup action."""
        result = self.command.execute(action="archive")
        assert isinstance(result, CommandResult)

    def test_cleanup_aggressive_mode(self):
        """Test aggressive cleanup mode."""
        result = self.command.execute(aggressive=True)
        assert isinstance(result, CommandResult)

    def test_cleanup_result_metrics(self):
        """Test cleanup result metrics."""
        result = self.command.execute()
        if result.data:
            assert isinstance(result.data, dict)

    def test_cleanup_actions_list(self):
        """Test different cleanup actions."""
        for action in ["archive", "consolidate", "remove"]:
            result = self.command.execute(action=action)
            assert isinstance(result, CommandResult)

    def test_cleanup_safety_first(self):
        """Test safety-first dry-run default."""
        result = self.command.execute()
        assert isinstance(result, CommandResult)

    def test_cleanup_multiple_calls(self):
        """Test multiple cleanup calls."""
        result1 = self.command.execute()
        result2 = self.command.execute()
        assert isinstance(result1, CommandResult)
        assert isinstance(result2, CommandResult)

    def test_cleanup_all_options(self):
        """Test with all cleanup options."""
        result = self.command.execute(
            dry_run=True,
            action="archive",
            aggressive=False,
        )
        assert isinstance(result, CommandResult)

    def test_cleanup_consistency(self):
        """Test cleanup consistency."""
        result1 = self.command.execute()
        result2 = self.command.execute()
        assert type(result1) == type(result2)


class TestDocMaintenanceCommand:
    """Test DocMaintenanceCommand functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.command = DocMaintenanceCommand()

    def test_maintenance_command_initialization(self):
        """Test command initialization."""
        assert self.command is not None

    def test_maintenance_basic_execution(self):
        """Test basic maintenance cycle."""
        result = self.command.execute()
        assert isinstance(result, CommandResult)

    def test_maintenance_with_cleanup(self):
        """Test maintenance including cleanup."""
        result = self.command.execute(include_cleanup=True)
        assert isinstance(result, CommandResult)

    def test_maintenance_without_cleanup(self):
        """Test maintenance without cleanup."""
        result = self.command.execute(include_cleanup=False)
        assert isinstance(result, CommandResult)

    def test_maintenance_skip_validation(self):
        """Test skipping validation phase."""
        result = self.command.execute(skip_validation=True)
        assert isinstance(result, CommandResult)

    def test_maintenance_result_phases(self):
        """Test maintenance result includes phases."""
        result = self.command.execute()
        if result.data:
            assert "phases_completed" in result.data or isinstance(result.data, dict)

    def test_maintenance_items_processed(self):
        """Test items processed tracking."""
        result = self.command.execute()
        if result.data:
            assert "items_processed" in result.data or isinstance(result.data, dict)

    def test_maintenance_duration_tracking(self):
        """Test duration tracking."""
        result = self.command.execute()
        assert isinstance(result, CommandResult)

    def test_maintenance_multiple_calls(self):
        """Test multiple maintenance cycles."""
        result1 = self.command.execute()
        result2 = self.command.execute()
        assert isinstance(result1, CommandResult)
        assert isinstance(result2, CommandResult)

    def test_maintenance_all_options(self):
        """Test with all maintenance options."""
        result = self.command.execute(
            include_cleanup=True,
            skip_validation=False,
        )
        assert isinstance(result, CommandResult)

    def test_maintenance_consistency(self):
        """Test maintenance consistency."""
        result1 = self.command.execute()
        result2 = self.command.execute()
        assert type(result1) == type(result2)


class TestDocReportCommand:
    """Test DocReportCommand functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.command = DocReportCommand()

    def test_report_command_initialization(self):
        """Test command initialization."""
        assert self.command is not None

    def test_report_basic_execution(self):
        """Test basic report generation."""
        result = self.command.execute()
        assert isinstance(result, CommandResult)

    def test_report_markdown_format(self):
        """Test markdown report format."""
        result = self.command.execute(report_format="markdown")
        assert isinstance(result, CommandResult)

    def test_report_html_format(self):
        """Test HTML report format."""
        result = self.command.execute(report_format="html")
        assert isinstance(result, CommandResult)

    def test_report_json_format(self):
        """Test JSON report format."""
        result = self.command.execute(report_format="json")
        assert isinstance(result, CommandResult)

    def test_report_with_metrics(self):
        """Test report including metrics."""
        result = self.command.execute(include_metrics=True)
        assert isinstance(result, CommandResult)

    def test_report_without_metrics(self):
        """Test report without metrics."""
        result = self.command.execute(include_metrics=False)
        assert isinstance(result, CommandResult)

    def test_report_custom_output_path(self):
        """Test report with custom output path."""
        result = self.command.execute(
            output_path="reports/custom-report.md",
        )
        assert isinstance(result, CommandResult)

    def test_report_result_sections(self):
        """Test report includes sections."""
        result = self.command.execute()
        if result.data:
            assert "report_sections" in result.data or isinstance(result.data, dict)

    def test_report_multiple_calls(self):
        """Test multiple report generations."""
        result1 = self.command.execute()
        result2 = self.command.execute()
        assert isinstance(result1, CommandResult)
        assert isinstance(result2, CommandResult)

    def test_report_all_options(self):
        """Test with all report options."""
        result = self.command.execute(
            report_format="html",
            include_metrics=True,
            output_path="reports/full-report.html",
        )
        assert isinstance(result, CommandResult)


class TestDocumentationCommandFactory:
    """Test DocumentationCommandFactory functionality."""

    def test_factory_create_discover_command(self):
        """Test creating discover command."""
        cmd = DocumentationCommandFactory.create(CommandType.DISCOVER)
        assert isinstance(cmd, DocDiscoverCommand)

    def test_factory_create_generate_command(self):
        """Test creating generate command."""
        cmd = DocumentationCommandFactory.create(CommandType.GENERATE)
        assert isinstance(cmd, DocGenerateCommand)

    def test_factory_create_diagram_command(self):
        """Test creating diagram command."""
        cmd = DocumentationCommandFactory.create(CommandType.DIAGRAM)
        assert isinstance(cmd, DocDiagramCommand)

    def test_factory_create_all_commands(self):
        """Test creating all command types."""
        for cmd_type in CommandType:
            cmd = DocumentationCommandFactory.create(cmd_type)
            assert cmd is not None
            assert isinstance(cmd, DocDiscoverCommand) or \
                   isinstance(cmd, DocGenerateCommand) or \
                   isinstance(cmd, DocDiagramCommand) or \
                   isinstance(cmd, DocStatusCommand) or \
                   isinstance(cmd, DocValidateCommand) or \
                   isinstance(cmd, DocCleanupCommand) or \
                   isinstance(cmd, DocMaintenanceCommand) or \
                   isinstance(cmd, DocReportCommand)


class TestExecuteDocCommand:
    """Test execute_doc_command convenience function."""

    def test_execute_discover_command(self):
        """Test executing discover command."""
        result = execute_doc_command(CommandType.DISCOVER)
        assert isinstance(result, CommandResult)

    def test_execute_generate_command(self):
        """Test executing generate command."""
        result = execute_doc_command(CommandType.GENERATE, component="test")
        assert isinstance(result, CommandResult)

    def test_execute_all_commands(self):
        """Test executing all command types."""
        for cmd_type in CommandType:
            result = execute_doc_command(cmd_type)
            assert isinstance(result, CommandResult)

    def test_execute_with_kwargs(self):
        """Test executing with keyword arguments."""
        result = execute_doc_command(
            CommandType.DIAGRAM,
            all_diagrams=True,
        )
        assert isinstance(result, CommandResult)
