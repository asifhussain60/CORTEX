"""
Unit Tests for Help Enhancement - Sprint 1 Day 2

Tests governance section integration in help system.

Test Coverage:
- Governance section display (3 tests)
- Compliance status retrieval (2 tests)
- Help table format (2 tests)
- Backward compatibility (2 tests)
- Integration (1 test)

Target Coverage: ≥80%

SPRINT 1 DAY 2: Help Enhancement Unit Tests
Author: Asif Hussain (CORTEX Enhancement System)
Date: November 28, 2025
"""

import pytest
import tempfile
import os
import sqlite3
from unittest.mock import patch, MagicMock
from pathlib import Path

from src.utils.compliance_summary import (
    get_compliance_summary,
    compliance_summary_for_template,
    get_detailed_compliance_status,
    _get_compliance_icon,
    _estimate_compliance_from_health
)


# ============================================================================
# GOVERNANCE SECTION DISPLAY TESTS (3)
# ============================================================================

def test_help_template_has_governance_section():
    """Test that help_table template includes governance section."""
    import yaml
    
    template_path = Path(__file__).parent.parent / "cortex-brain" / "response-templates.yaml"
    
    with open(template_path, 'r') as f:
        templates = yaml.safe_load(f)
    
    help_table = templates.get("templates", {}).get("help_table")
    
    assert help_table is not None
    response_content = help_table.get("response_content", "")
    
    # Check for governance section
    assert "Governance" in response_content or "governance" in response_content
    assert "Quick Governance Commands" in response_content or "Quick Commands" in response_content


def test_governance_commands_listed():
    """Test that all 5 governance commands are listed in help template."""
    import yaml
    
    template_path = Path(__file__).parent.parent / "cortex-brain" / "response-templates.yaml"
    
    with open(template_path, 'r') as f:
        templates = yaml.safe_load(f)
    
    help_table = templates.get("templates", {}).get("help_table")
    response_content = help_table.get("response_content", "")
    
    # Check for all 5 commands
    assert "show rules" in response_content
    assert "rulebook" in response_content
    assert "compliance" in response_content
    assert "dor" in response_content
    assert "dod" in response_content


def test_compliance_placeholder_in_template():
    """Test that compliance summary placeholder exists in template."""
    import yaml
    
    template_path = Path(__file__).parent.parent / "cortex-brain" / "response-templates.yaml"
    
    with open(template_path, 'r') as f:
        templates = yaml.safe_load(f)
    
    help_table = templates.get("templates", {}).get("help_table")
    response_content = help_table.get("response_content", "")
    
    # Check for compliance summary placeholder
    assert "{compliance_summary}" in response_content or "Compliance" in response_content


# ============================================================================
# COMPLIANCE STATUS RETRIEVAL TESTS (2)
# ============================================================================

def test_get_compliance_summary_returns_string():
    """Test that get_compliance_summary returns a formatted string."""
    summary = get_compliance_summary(quick=True)
    
    assert isinstance(summary, str)
    assert len(summary) > 0
    # Should contain some indicator of compliance status
    assert any(icon in summary for icon in ["✅", "⚠️", "🔶", "❌", "Compliance", "compliant"])


def test_compliance_summary_for_template():
    """Test template-specific compliance summary function."""
    summary = compliance_summary_for_template()
    
    assert isinstance(summary, str)
    assert len(summary) > 0
    # Should be suitable for template injection (no newlines, reasonable length)
    assert "\n\n" not in summary  # No double newlines
    assert len(summary) < 200  # Reasonable length for help display


# ============================================================================
# HELP TABLE FORMAT TESTS (2)
# ============================================================================

def test_help_template_structure():
    """Test that help_table template maintains proper structure."""
    import yaml
    
    template_path = Path(__file__).parent.parent / "cortex-brain" / "response-templates.yaml"
    
    with open(template_path, 'r') as f:
        templates = yaml.safe_load(f)
    
    help_table = templates.get("templates", {}).get("help_table")
    
    # Check required fields
    assert "name" in help_table
    assert "triggers" in help_table
    assert "response_type" in help_table
    assert "response_content" in help_table
    
    # Check triggers include 'help'
    assert "help" in help_table["triggers"]


def test_governance_table_format():
    """Test that governance commands are formatted as table in template."""
    import yaml
    
    template_path = Path(__file__).parent.parent / "cortex-brain" / "response-templates.yaml"
    
    with open(template_path, 'r') as f:
        templates = yaml.safe_load(f)
    
    help_table = templates.get("templates", {}).get("help_table")
    response_content = help_table.get("response_content", "")
    
    # Check for markdown table format
    assert "|" in response_content  # Table separator
    # Should have headers like Command, Description, Example
    assert "Command" in response_content or "command" in response_content


# ============================================================================
# BACKWARD COMPATIBILITY TESTS (2)
# ============================================================================

def test_help_triggers_unchanged():
    """Test that original help triggers are preserved."""
    import yaml
    
    template_path = Path(__file__).parent.parent / "cortex-brain" / "response-templates.yaml"
    
    with open(template_path, 'r') as f:
        templates = yaml.safe_load(f)
    
    help_table = templates.get("templates", {}).get("help_table")
    triggers = help_table.get("triggers", [])
    
    # Check original triggers still present
    assert "help" in triggers
    assert "help_table" in triggers


def test_context_summary_template_preserved():
    """Test that context_summary_template field is preserved."""
    import yaml
    
    template_path = Path(__file__).parent.parent / "cortex-brain" / "response-templates.yaml"
    
    with open(template_path, 'r') as f:
        templates = yaml.safe_load(f)
    
    help_table = templates.get("templates", {}).get("help_table")
    
    # Check context_summary_template exists
    assert "context_summary_template" in help_table
    context_template = help_table["context_summary_template"]
    
    # Should contain context-related placeholders
    assert "{conversation_count}" in context_template
    assert "{quality_score}" in context_template


# ============================================================================
# COMPLIANCE ICON TESTS (2)
# ============================================================================

def test_compliance_icon_ranges():
    """Test that compliance icons are correctly assigned based on percentage."""
    assert _get_compliance_icon(95) == "✅"
    assert _get_compliance_icon(90) == "✅"
    assert _get_compliance_icon(85) == "⚠️"
    assert _get_compliance_icon(75) == "⚠️"
    assert _get_compliance_icon(60) == "🔶"
    assert _get_compliance_icon(50) == "🔶"
    assert _get_compliance_icon(40) == "❌"
    assert _get_compliance_icon(0) == "❌"


def test_estimate_compliance_from_health_fallback():
    """Test that estimate_compliance_from_health provides fallback."""
    estimate = _estimate_compliance_from_health()
    
    assert isinstance(estimate, str)
    assert len(estimate) > 0
    # Should indicate it's active or estimated
    assert "Governance" in estimate or "active" in estimate or "compliant" in estimate


# ============================================================================
# INTEGRATION TEST
# ============================================================================

def test_full_help_enhancement_workflow():
    """Test complete workflow: get compliance summary and format for help display."""
    # Step 1: Get compliance summary (quick mode)
    summary_quick = get_compliance_summary(quick=True)
    
    assert isinstance(summary_quick, str)
    assert len(summary_quick) > 0
    
    # Step 2: Get template-ready summary
    template_summary = compliance_summary_for_template()
    
    assert isinstance(template_summary, str)
    assert len(template_summary) > 0
    
    # Step 3: Verify help template integration
    import yaml
    
    template_path = Path(__file__).parent.parent / "cortex-brain" / "response-templates.yaml"
    
    with open(template_path, 'r') as f:
        templates = yaml.safe_load(f)
    
    help_table = templates.get("templates", {}).get("help_table")
    response_content = help_table.get("response_content", "")
    
    # Verify governance section exists
    assert "Governance" in response_content or "governance" in response_content
    
    # Verify all 5 commands present
    commands = ["show rules", "rulebook", "compliance", "dor", "dod"]
    for cmd in commands:
        assert cmd in response_content, f"Command '{cmd}' not found in help template"
    
    # Verify compliance placeholder or section
    assert "{compliance_summary}" in response_content or "Compliance At-A-Glance" in response_content


# ============================================================================
# ERROR HANDLING TEST
# ============================================================================

def test_compliance_summary_error_handling():
    """Test that compliance summary handles errors gracefully."""
    # Even with no compliance system, should return a valid string
    summary = get_compliance_summary(quick=True)
    
    assert isinstance(summary, str)
    assert len(summary) > 0
    # Should not raise exceptions
    
    # Test detailed status error handling
    detailed = get_detailed_compliance_status()
    
    assert isinstance(detailed, dict)
    # Should have success key even on error
    assert "success" in detailed or "error" in detailed


# ============================================================================
# MOCK-BASED TESTS FOR FUTURE COMPLIANCE CHECKER
# ============================================================================

def test_compliance_summary_with_checker():
    """Test compliance summary when ComplianceChecker would be available."""
    # This test validates the fallback path since ComplianceChecker doesn't exist yet
    # Once implemented, the code is ready to use it
    
    summary = get_compliance_summary(quick=False)
    
    assert isinstance(summary, str)
    assert len(summary) > 0
    # Should return a valid summary even without ComplianceChecker
    assert any(word in summary for word in ["compliant", "Compliance", "Governance", "active"])
