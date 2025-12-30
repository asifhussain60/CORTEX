"""Tests for Progress Bar Helper Functions in Template Renderer.

Tests the visual progress bar generation capabilities added for 
Planner 2.0 Enhancements (Phase 1 - Progress Template Integration).

Author: Asif Hussain
Created: 2025-12-30
"""

import pytest
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from response_templates.template_renderer import TemplateRenderer


class TestProgressBarGeneration:
    """Tests for generate_progress_bar static method."""
    
    def test_zero_percent_progress(self):
        """Test progress bar at 0%."""
        result = TemplateRenderer.generate_progress_bar(0, width=10)
        assert result == "░░░░░░░░░░"
        assert len(result) == 10
    
    def test_fifty_percent_progress(self):
        """Test progress bar at 50%."""
        result = TemplateRenderer.generate_progress_bar(50, width=10)
        assert result == "█████░░░░░"
        assert len(result) == 10
    
    def test_hundred_percent_progress(self):
        """Test progress bar at 100%."""
        result = TemplateRenderer.generate_progress_bar(100, width=10)
        assert result == "██████████"
        assert len(result) == 10
    
    def test_custom_width(self):
        """Test progress bar with custom width."""
        result = TemplateRenderer.generate_progress_bar(50, width=20)
        assert len(result) == 20
        assert result.count('█') == 10
        assert result.count('░') == 10
    
    def test_custom_characters(self):
        """Test progress bar with custom fill characters."""
        result = TemplateRenderer.generate_progress_bar(60, width=10, filled_char='#', empty_char='-')
        assert result == "######----"
    
    def test_clamp_over_100(self):
        """Test that percentage over 100 is clamped."""
        result = TemplateRenderer.generate_progress_bar(150, width=10)
        assert result == "██████████"  # Should be full
    
    def test_clamp_negative(self):
        """Test that negative percentage is clamped to 0."""
        result = TemplateRenderer.generate_progress_bar(-25, width=10)
        assert result == "░░░░░░░░░░"  # Should be empty
    
    def test_fractional_percentage(self):
        """Test progress bar with fractional percentage."""
        result = TemplateRenderer.generate_progress_bar(33.33, width=10)
        # 33.33% of 10 = 3.333, should round to 3
        assert result.count('█') == 3
        assert result.count('░') == 7


class TestTDDStatusGeneration:
    """Tests for generate_tdd_status static method."""
    
    def test_all_pending(self):
        """Test TDD status when all phases are pending."""
        result = TemplateRenderer.generate_tdd_status()
        assert result == "R⏸️ G⏸️ F⏸️"
    
    def test_red_done(self):
        """Test TDD status when RED phase is done."""
        result = TemplateRenderer.generate_tdd_status(red_done=True)
        assert result == "R✅ G⏸️ F⏸️"
    
    def test_red_green_done(self):
        """Test TDD status when RED and GREEN phases are done."""
        result = TemplateRenderer.generate_tdd_status(red_done=True, green_done=True)
        assert result == "R✅ G✅ F⏸️"
    
    def test_all_done(self):
        """Test TDD status when all phases are complete."""
        result = TemplateRenderer.generate_tdd_status(red_done=True, green_done=True, refactor_done=True)
        assert result == "R✅ G✅ F✅"
    
    def test_only_refactor_done(self):
        """Test unusual case where only REFACTOR is marked done."""
        result = TemplateRenderer.generate_tdd_status(refactor_done=True)
        assert result == "R⏸️ G⏸️ F✅"


class TestElapsedTimeFormatting:
    """Tests for format_elapsed_time static method."""
    
    def test_seconds_only(self):
        """Test formatting time under 60 seconds."""
        assert TemplateRenderer.format_elapsed_time(30) == "30s"
        assert TemplateRenderer.format_elapsed_time(59) == "59s"
    
    def test_minutes_and_seconds(self):
        """Test formatting time in minutes and seconds."""
        assert TemplateRenderer.format_elapsed_time(90) == "1m 30s"
        assert TemplateRenderer.format_elapsed_time(125) == "2m 5s"
    
    def test_exact_minutes(self):
        """Test formatting exact minutes (no leftover seconds)."""
        assert TemplateRenderer.format_elapsed_time(120) == "2m"
        assert TemplateRenderer.format_elapsed_time(300) == "5m"
    
    def test_hours_and_minutes(self):
        """Test formatting time in hours and minutes."""
        assert TemplateRenderer.format_elapsed_time(3900) == "1h 5m"
        assert TemplateRenderer.format_elapsed_time(7200) == "2h"
    
    def test_exact_hour(self):
        """Test formatting exact hours."""
        assert TemplateRenderer.format_elapsed_time(3600) == "1h"


class TestPhaseRowGeneration:
    """Tests for generate_phase_rows method."""
    
    @pytest.fixture
    def renderer(self):
        """Create a TemplateRenderer instance for testing."""
        return TemplateRenderer()
    
    def test_single_completed_phase(self, renderer):
        """Test generating row for a single completed phase."""
        phases = [{
            'phase_num': 1,
            'phase_name': 'Setup',
            'status': 'completed',
            'percentage': 100,
            'tdd_enabled': True,
            'red_done': True,
            'green_done': True,
            'refactor_done': True,
            'completed_tasks': 3,
            'total_tasks': 3,
            'elapsed_time': 120
        }]
        result = renderer.generate_phase_rows(phases)
        
        assert '✅' in result
        assert '**Setup**' in result
        assert 'Done' in result
        assert '100%' in result
        assert '3/3' in result
        assert '2m' in result
    
    def test_in_progress_phase(self, renderer):
        """Test generating row for an in-progress phase."""
        phases = [{
            'phase_num': 2,
            'phase_name': 'Implementation',
            'status': 'in_progress',
            'percentage': 50,
            'tdd_enabled': True,
            'red_done': True,
            'green_done': False,
            'refactor_done': False,
            'completed_tasks': 2,
            'total_tasks': 4,
            'elapsed_time': 300
        }]
        result = renderer.generate_phase_rows(phases)
        
        assert '⏳' in result
        assert '**Implementation**' in result
        assert 'Active' in result
        assert '50%' in result
        assert '2/4' in result
    
    def test_not_started_phase(self, renderer):
        """Test generating row for a not-started phase."""
        phases = [{
            'phase_num': 3,
            'phase_name': 'Testing',
            'status': 'not_started',
            'percentage': 0,
            'tdd_enabled': False,
            'completed_tasks': 0,
            'total_tasks': 5,
            'elapsed_time': 0
        }]
        result = renderer.generate_phase_rows(phases)
        
        assert '⏸️' in result
        assert '**Testing**' in result
        assert 'Pending' in result
        assert '0%' in result
        assert 'N/A' in result  # TDD disabled
    
    def test_multiple_phases(self, renderer):
        """Test generating rows for multiple phases."""
        phases = [
            {'phase_num': 1, 'phase_name': 'Phase 1', 'status': 'completed', 'percentage': 100, 
             'tdd_enabled': True, 'red_done': True, 'green_done': True, 'refactor_done': True,
             'completed_tasks': 2, 'total_tasks': 2, 'elapsed_time': 60},
            {'phase_num': 2, 'phase_name': 'Phase 2', 'status': 'in_progress', 'percentage': 25,
             'tdd_enabled': True, 'red_done': True, 'green_done': False, 'refactor_done': False,
             'completed_tasks': 1, 'total_tasks': 4, 'elapsed_time': 30},
            {'phase_num': 3, 'phase_name': 'Phase 3', 'status': 'not_started', 'percentage': 0,
             'tdd_enabled': False, 'completed_tasks': 0, 'total_tasks': 3, 'elapsed_time': 0}
        ]
        result = renderer.generate_phase_rows(phases)
        
        # Should have 3 rows
        assert result.count('|') >= 21  # 7 columns * 3 rows = 21+ pipe chars
        assert 'Phase 1' in result
        assert 'Phase 2' in result
        assert 'Phase 3' in result


class TestAutonomousProgressRendering:
    """Tests for render_autonomous_progress method."""
    
    @pytest.fixture
    def renderer(self):
        """Create a TemplateRenderer instance for testing."""
        return TemplateRenderer()
    
    @pytest.fixture
    def sample_phases(self):
        """Sample phases for testing."""
        return [
            {'phase_num': 1, 'phase_name': 'Setup', 'status': 'completed', 'percentage': 100,
             'tdd_enabled': True, 'red_done': True, 'green_done': True, 'refactor_done': True,
             'completed_tasks': 3, 'total_tasks': 3, 'elapsed_time': 120},
            {'phase_num': 2, 'phase_name': 'Implementation', 'status': 'in_progress', 'percentage': 50,
             'tdd_enabled': True, 'red_done': True, 'green_done': False, 'refactor_done': False,
             'completed_tasks': 2, 'total_tasks': 4, 'elapsed_time': 180}
        ]
    
    def test_basic_progress_render(self, renderer, sample_phases):
        """Test basic autonomous progress rendering."""
        result = renderer.render_autonomous_progress(
            plan_name="Test Plan",
            current_phase=2,
            total_phases=4,
            current_phase_name="Implementation",
            current_task="Writing unit tests",
            overall_percentage=37.5,
            phases=sample_phases,
            elapsed_seconds=300,
            estimated_remaining_seconds=500
        )
        
        # Check header
        assert "## 🧠 CORTEX Plan Execution" in result
        assert "Asif Hussain" in result
        assert "Test Plan" in result
        
        # Check progress box
        assert "╔" in result
        assert "╚" in result
        # 37.5% rounds to 38% in the display
        assert "38%" in result or "37%" in result
        assert "Phase 2/4" in result
        
        # Check phase table
        assert "| # | Phase | Status |" in result
        assert "Setup" in result
        assert "Implementation" in result
    
    def test_progress_with_threat_analysis(self, renderer, sample_phases):
        """Test progress rendering with threat analysis section."""
        threat_analysis = {
            'enabled': True,
            'threat_count': 12,
            'critical_count': 2,
            'high_count': 4,
            'medium_count': 6,
            'stride_categories': 'S, T, R, I, D, E',
            'mitigations_done': 4,
            'mitigations_total': 6
        }
        
        result = renderer.render_autonomous_progress(
            plan_name="Security Feature",
            current_phase=1,
            total_phases=3,
            current_phase_name="Setup",
            current_task="Threat modeling",
            overall_percentage=25,
            phases=sample_phases,
            threat_analysis=threat_analysis
        )
        
        assert "### 🔒 Security Analysis" in result
        assert "12" in result  # threat count
        assert "2 Critical" in result
        assert "4 High" in result
        assert "STRIDE" in result
        assert "4/6" in result  # mitigations
    
    def test_progress_with_validation_status(self, renderer, sample_phases):
        """Test progress rendering with DoR/DoD validation."""
        result = renderer.render_autonomous_progress(
            plan_name="Validated Plan",
            current_phase=1,
            total_phases=2,
            current_phase_name="Validation",
            current_task="Running checks",
            overall_percentage=50,
            phases=sample_phases,
            dor_status={'passed': True, 'violations': 0},
            dod_status={'passed': False, 'remaining': 3}
        )
        
        assert "### ✅ Validation Status" in result
        assert "Definition of Ready" in result
        assert "✅ Passed" in result  # DoR passed
        assert "Definition of Done" in result
        assert "3 remaining" in result  # DoD not passed
    
    def test_status_emoji_progression(self, renderer, sample_phases):
        """Test that status emoji changes based on progress."""
        # 0% - should show start emoji
        result_0 = renderer.render_autonomous_progress(
            plan_name="Test", current_phase=1, total_phases=4,
            current_phase_name="Start", current_task="Task",
            overall_percentage=0, phases=sample_phases
        )
        assert "🏁" in result_0
        
        # 50% - should show progress emoji
        result_50 = renderer.render_autonomous_progress(
            plan_name="Test", current_phase=2, total_phases=4,
            current_phase_name="Middle", current_task="Task",
            overall_percentage=50, phases=sample_phases
        )
        assert "📈" in result_50
        
        # 100% - should show completion emoji
        result_100 = renderer.render_autonomous_progress(
            plan_name="Test", current_phase=4, total_phases=4,
            current_phase_name="Done", current_task="Complete",
            overall_percentage=100, phases=sample_phases
        )
        assert "🎉" in result_100


class TestProgressBarIntegration:
    """Integration tests for progress bar in composed templates."""
    
    @pytest.fixture
    def renderer(self):
        """Create a TemplateRenderer instance for testing."""
        return TemplateRenderer()
    
    def test_progress_bar_in_context(self, renderer):
        """Test that progress bar can be used in template context."""
        # Generate a progress bar and verify it can be used as context value
        bar = renderer.generate_progress_bar(75, width=20)
        
        # Verify the bar has correct structure
        assert len(bar) == 20
        assert bar.count('█') == 15
        assert bar.count('░') == 5
        
        # Verify it can be embedded in template context
        context = {
            'progress_bar': bar,
            'percentage': 75
        }
        
        template_str = "Progress: [{{progress_bar}}] {{percentage}}%"
        # Manual substitution for this test
        result = template_str.replace('{{progress_bar}}', context['progress_bar'])
        result = result.replace('{{percentage}}', str(context['percentage']))
        
        assert "████████████████████░░░░░" not in result  # Wrong
        assert bar in result  # Correct bar is present
        assert "75%" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
