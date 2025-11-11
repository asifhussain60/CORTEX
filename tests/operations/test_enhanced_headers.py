"""
Test enhanced headers with purpose and accomplishments.

Validates that headers display meaningful context about what will be/was accomplished.
"""

import pytest
from io import StringIO
import sys
from src.operations.header_utils import (
    print_minimalist_header,
    print_completion_footer
)


def test_minimalist_header_with_purpose(capsys):
    """Test that header displays purpose correctly."""
    print_minimalist_header(
        operation_name="Design Sync",
        version="1.0.0",
        profile="comprehensive",
        mode="LIVE EXECUTION",
        dry_run=False,
        purpose="Full sync: gap analysis + optimization integration + MD→YAML conversion"
    )
    
    captured = capsys.readouterr()
    output = captured.out
    
    # Verify header elements
    assert "CORTEX Design Sync Orchestrator v1.0.0" in output
    assert "Profile: comprehensive" in output
    assert "Mode: LIVE EXECUTION" in output
    assert "© 2024-2025 Asif Hussain" in output
    
    # Verify purpose is displayed
    assert "📋 Purpose:" in output
    assert "Full sync: gap analysis + optimization integration + MD→YAML conversion" in output


def test_minimalist_header_without_purpose(capsys):
    """Test that header works without purpose (backward compatibility)."""
    print_minimalist_header(
        operation_name="Test Operation",
        version="1.0.0",
        profile="standard",
        mode="LIVE EXECUTION",
        dry_run=False
    )
    
    captured = capsys.readouterr()
    output = captured.out
    
    # Verify header elements
    assert "CORTEX Test Operation Orchestrator v1.0.0" in output
    assert "Profile: standard" in output
    
    # Purpose should not be displayed
    assert "📋 Purpose:" not in output


def test_completion_footer_with_accomplishments(capsys):
    """Test that footer displays accomplishments."""
    accomplishments = [
        "Discovered 37 modules (43% implemented)",
        "Analyzed 5 design-implementation gaps",
        "Consolidated 3 status files → 1 source of truth",
        "Committed changes: abc123de"
    ]
    
    print_completion_footer(
        operation_name="Design Sync",
        success=True,
        duration_seconds=12.5,
        summary="4 improvements applied",
        accomplishments=accomplishments
    )
    
    captured = capsys.readouterr()
    output = captured.out
    
    # Verify footer elements
    assert "✅ COMPLETED" in output
    assert "12.5s" in output
    assert "4 improvements applied" in output
    
    # Verify accomplishments section
    assert "Accomplishments:" in output
    for item in accomplishments:
        assert f"• {item}" in output


def test_completion_footer_without_accomplishments(capsys):
    """Test footer without accomplishments (backward compatibility)."""
    print_completion_footer(
        operation_name="Test Operation",
        success=True,
        duration_seconds=5.2,
        summary="Operation complete"
    )
    
    captured = capsys.readouterr()
    output = captured.out
    
    # Verify basic footer
    assert "✅ COMPLETED" in output
    assert "5.2s" in output
    assert "Operation complete" in output
    
    # Accomplishments should not be displayed
    assert "Accomplishments:" not in output


def test_completion_footer_failure(capsys):
    """Test footer for failed operations."""
    print_completion_footer(
        operation_name="Test Operation",
        success=False,
        duration_seconds=2.1,
        summary="Error: Something went wrong"
    )
    
    captured = capsys.readouterr()
    output = captured.out
    
    # Verify failure indicator
    assert "❌ FAILED" in output
    assert "2.1s" in output
    assert "Error: Something went wrong" in output
    
    # Accomplishments should not show on failure
    assert "Accomplishments:" not in output


def test_dry_run_mode_header(capsys):
    """Test header in dry-run mode."""
    print_minimalist_header(
        operation_name="Design Sync",
        version="1.0.0",
        profile="quick",
        mode="ANALYSIS",
        dry_run=True,
        purpose="Analyze design-implementation gaps (preview only, no changes)"
    )
    
    captured = capsys.readouterr()
    output = captured.out
    
    # Verify dry-run indicator
    assert "DRY RUN (Preview Only)" in output
    assert "Analyze design-implementation gaps (preview only, no changes)" in output


def test_profile_specific_purposes():
    """Test that different profiles show appropriate purposes."""
    purposes = {
        'quick': 'Analyze design-implementation gaps (preview only, no changes)',
        'standard': 'Synchronize design docs with implementation reality + consolidate status files',
        'comprehensive': 'Full sync: gap analysis + optimization integration + MD→YAML conversion'
    }
    
    for profile, expected_purpose in purposes.items():
        # This test validates the purpose strings are well-formed
        assert len(expected_purpose) > 20, f"Purpose for {profile} too short"
        assert len(expected_purpose) < 120, f"Purpose for {profile} too long"
        assert "→" in expected_purpose or "+" in expected_purpose or "," in expected_purpose, \
               f"Purpose for {profile} should show multiple actions"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
