"""Tests for ASCIIProgressBar - Visual Progress Indicators.

Authority: Phase 35 R2
"""

import pytest

from cortex.orchestrators.response.ascii_progress_bar import (
    ASCIIProgressBar,
    Phase,
)


class TestASCIIProgressBar:
    """Test suite for ASCIIProgressBar."""

    def test_generate_bar_empty(self):
        """Test empty progress bar."""
        bar = ASCIIProgressBar()
        result = bar.generate_bar(0.0)
        assert result == "[░░░░░░░░░░]"

    def test_generate_bar_full(self):
        """Test full progress bar."""
        bar = ASCIIProgressBar()
        result = bar.generate_bar(1.0)
        assert result == "[██████████]"

    def test_generate_bar_half(self):
        """Test half progress bar."""
        bar = ASCIIProgressBar()
        result = bar.generate_bar(0.5)
        assert result == "[█████░░░░░]"

    def test_generate_bar_80_percent(self):
        """Test 80% progress bar."""
        bar = ASCIIProgressBar()
        result = bar.generate_bar(0.8)
        assert result == "[████████░░]"

    def test_generate_bar_clamping_above(self):
        """Test progress clamping above 1.0."""
        bar = ASCIIProgressBar()
        result = bar.generate_bar(1.5)
        assert result == "[██████████]"

    def test_generate_bar_clamping_below(self):
        """Test progress clamping below 0.0."""
        bar = ASCIIProgressBar()
        result = bar.generate_bar(-0.5)
        assert result == "[░░░░░░░░░░]"

    def test_format_phase_progress_active(self):
        """Test formatting active phase progress (multiline format)."""
        bar = ASCIIProgressBar()
        phase = Phase(name="KSESSIONS Implementation", progress=0.8, status="active")
        result = bar.format_phase_progress(phase)

        # Check multiline format
        lines = result.split("\n")
        assert len(lines) == 2
        assert "KSESSIONS Implementation" in lines[0]
        assert "🔵" in lines[0]  # active status icon
        assert "[████████░░]" in lines[1]
        assert "80%" in lines[1]

    def test_format_phase_progress_completed(self):
        """Test formatting completed phase (multiline format)."""
        bar = ASCIIProgressBar()
        phase = Phase(name="Phase 1", progress=1.0, status="completed")
        result = bar.format_phase_progress(phase)

        lines = result.split("\n")
        assert len(lines) == 2
        assert "Phase 1" in lines[0]
        assert "✅" in lines[0]  # completed status icon
        assert "[██████████]" in lines[1]
        assert "100%" in lines[1]

    def test_format_phase_progress_queued(self):
        """Test formatting queued phase (multiline format)."""
        bar = ASCIIProgressBar()
        phase = Phase(name="Phase 3", progress=0.0, status="queued")
        result = bar.format_phase_progress(phase)

        lines = result.split("\n")
        assert len(lines) == 2
        assert "Phase 3" in lines[0]
        assert "⚪" in lines[0]  # queued status icon
        assert "[░░░░░░░░░░]" in lines[1]
        assert "0%" in lines[1]

    def test_format_phase_progress_blocked(self):
        """Test formatting blocked phase (multiline format)."""
        bar = ASCIIProgressBar()
        phase = Phase(name="Phase 4", progress=0.4, status="blocked")
        result = bar.format_phase_progress(phase)

        lines = result.split("\n")
        assert len(lines) == 2
        assert "Phase 4" in lines[0]
        assert "🔴" in lines[0]  # blocked status icon
        assert "[████░░░░░░]" in lines[1]
        assert "40%" in lines[1]

    def test_format_phase_progress_no_icon(self):
        """Test formatting without status icon (multiline format)."""
        bar = ASCIIProgressBar()
        phase = Phase(name="Test Phase", progress=0.5, status="active")
        result = bar.format_phase_progress(phase, show_status_icon=False)

        lines = result.split("\n")
        assert len(lines) == 2
        assert "Test Phase" in lines[0]
        assert "🔵" not in lines[0]  # no status icon
        assert "[█████░░░░░]" in lines[1]
        assert "50%" in lines[1]


class TestDisplayAllPhases:
    """Test suite for display_all_phases."""

    def test_display_multiple_phases(self):
        """Test displaying multiple phases (multiline format with blank lines)."""
        bar = ASCIIProgressBar()
        phases = [
            Phase(name="Phase 1", progress=1.0, status="completed"),
            Phase(name="Phase 2", progress=0.8, status="active"),
            Phase(name="Phase 3", progress=0.0, status="queued"),
        ]

        result = bar.display_all_phases(phases)
        lines = result.split("\n")

        # Each phase takes 2 lines + blank line separator = 3 lines per phase (except last)
        # Phase 1: title + bar (2 lines) + blank (1) = 3
        # Phase 2: title + bar (2 lines) + blank (1) = 3  
        # Phase 3: title + bar (2 lines) = 2
        # Total: 8 lines
        assert len(lines) == 8
        
        # Check Phase 1
        assert "Phase 1" in lines[0]
        assert "✅" in lines[0]
        assert "[██████████]" in lines[1]
        assert "100%" in lines[1]
        
        # Check Phase 2 (after blank line)
        assert "Phase 2" in lines[3]
        assert "🔵" in lines[3]
        assert "[████████░░]" in lines[4]
        assert "80%" in lines[4]
        
        # Check Phase 3 (after blank line)
        assert "Phase 3" in lines[6]
        assert "⚪" in lines[6]
        assert "[░░░░░░░░░░]" in lines[7]
        assert "0%" in lines[7]

    def test_display_empty_phases(self):
        """Test displaying empty phase list."""
        bar = ASCIIProgressBar()
        result = bar.display_all_phases([])
        assert result == ""


class TestCompletionSummary:
    """Test suite for format_completion_summary."""

    def test_completion_summary_partial(self):
        """Test partial completion summary."""
        bar = ASCIIProgressBar()
        phases = [
            Phase(name="Phase 1", progress=1.0, status="completed"),
            Phase(name="Phase 2", progress=1.0, status="completed"),
            Phase(name="Phase 3", progress=0.5, status="active"),
        ]

        result = bar.format_completion_summary(phases)
        assert "2/3" in result
        assert "66%" in result  # Fixed: int rounding

    def test_completion_summary_all_complete(self):
        """Test all phases completed."""
        bar = ASCIIProgressBar()
        phases = [
            Phase(name="Phase 1", progress=1.0, status="completed"),
            Phase(name="Phase 2", progress=1.0, status="completed"),
        ]

        result = bar.format_completion_summary(phases)
        assert "2/2" in result
        assert "100%" in result

    def test_completion_summary_none_complete(self):
        """Test no phases completed."""
        bar = ASCIIProgressBar()
        phases = [
            Phase(name="Phase 1", progress=0.0, status="queued"),
            Phase(name="Phase 2", progress=0.0, status="queued"),
        ]

        result = bar.format_completion_summary(phases)
        assert "0/2" in result
        assert "0%" in result

    def test_completion_summary_empty(self):
        """Test empty phase list."""
        bar = ASCIIProgressBar()
        result = bar.format_completion_summary([])
        assert "No phases" in result


class TestSubtleSpine:
    """Test suite for format_subtle_spine."""

    def test_subtle_spine_with_next(self):
        """Test subtle spine with next phase."""
        result = ASCIIProgressBar.format_subtle_spine("Phase 2", "Phase 3")
        assert result == "[→] Phase 2 | [ ] Phase 3"

    def test_subtle_spine_without_next(self):
        """Test subtle spine without next phase."""
        result = ASCIIProgressBar.format_subtle_spine("Phase 2")
        assert result == "[→] Phase 2"


class TestModeHeader:
    """Test suite for format_mode_header."""

    def test_mode_header_multiple_phases(self):
        """Test mode header with multiple phases."""
        phases = [
            Phase(name="Phase 1", progress=1.0, status="completed"),
            Phase(name="Phase 2", progress=0.5, status="active"),
        ]

        result = ASCIIProgressBar.format_mode_header("IMPLEMENT", phases)
        assert "IMPLEMENT Mode" in result
        assert "2 phases" in result

    def test_mode_header_single_phase(self):
        """Test mode header with single phase."""
        phases = [Phase(name="Phase 1", progress=0.5, status="active")]

        result = ASCIIProgressBar.format_mode_header("TDD", phases)
        assert "TDD Mode" in result
        assert "1 phase" in result  # singular
