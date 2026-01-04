"""Tests for Visual Progress Generator module.

Tests the centralized visual progress generation introduced in C50-06 Phase 2.

Author: Asif Hussain
Created: 2026-01-04
"""

import pytest
from src.orchestrators.shared.visual_progress_generator import VisualProgressGenerator


class TestBasicProgressBarGeneration:
    """Tests for generate_bar() method."""
    
    def test_zero_percent(self):
        """Test progress bar at 0%."""
        generator = VisualProgressGenerator()
        result = generator.generate_bar(0)
        assert result == '░░░░░░░░░░'
        assert len(result) == 10
    
    def test_fifty_percent(self):
        """Test progress bar at 50%."""
        generator = VisualProgressGenerator()
        result = generator.generate_bar(50)
        assert result == '█████░░░░░'
        assert len(result) == 10
    
    def test_hundred_percent(self):
        """Test progress bar at 100%."""
        generator = VisualProgressGenerator()
        result = generator.generate_bar(100)
        assert result == '██████████'
        assert len(result) == 10
    
    def test_custom_width(self):
        """Test progress bar with custom width."""
        generator = VisualProgressGenerator()
        result = generator.generate_bar(50, width=20)
        assert len(result) == 20
        assert result == '██████████░░░░░░░░░░'
    
    def test_clamp_over_100(self):
        """Test that percentage over 100 is clamped."""
        generator = VisualProgressGenerator()
        result = generator.generate_bar(150)
        assert result == '██████████'  # Should be same as 100%
    
    def test_clamp_negative(self):
        """Test that negative percentage is clamped to 0."""
        generator = VisualProgressGenerator()
        result = generator.generate_bar(-10)
        assert result == '░░░░░░░░░░'  # Should be same as 0%
    
    def test_fractional_percentage(self):
        """Test progress bar with fractional percentage."""
        generator = VisualProgressGenerator()
        result = generator.generate_bar(75.5)
        assert len(result) == 10
        # 75.5% of 10 = 7.55 → int() = 7 filled
        assert result == '███████░░░'


class TestLabeledProgressBars:
    """Tests for generate_with_label() method."""
    
    def test_with_percentage(self):
        """Test labeled bar with percentage display."""
        generator = VisualProgressGenerator()
        result = generator.generate_with_label("Setup", 100)
        assert result == 'Setup: ██████████ 100%'
    
    def test_without_percentage(self):
        """Test labeled bar without percentage display."""
        generator = VisualProgressGenerator()
        result = generator.generate_with_label("Execute", 50, show_percentage=False)
        assert result == 'Execute: █████░░░░░'
    
    def test_long_label(self):
        """Test with longer label text."""
        generator = VisualProgressGenerator()
        result = generator.generate_with_label("Data Validation Phase", 75)
        assert 'Data Validation Phase:' in result
        assert '███████░░░' in result
        assert '75%' in result


class TestMultiPhaseDisplay:
    """Tests for generate_multi_phase() method."""
    
    def test_three_phases(self):
        """Test multi-phase display with 3 phases."""
        generator = VisualProgressGenerator()
        phases = [
            {"name": "Setup", "status": "complete", "progress": 100},
            {"name": "Execute", "status": "in_progress", "progress": 50},
            {"name": "Validate", "status": "pending", "progress": 0}
        ]
        result = generator.generate_multi_phase(phases, current_phase=2)
        
        lines = result.split('\n')
        assert len(lines) == 3
        assert '✅' in lines[0]  # complete emoji
        assert '🔄' in lines[1]  # in_progress emoji
        assert '⏳' in lines[2]  # pending emoji
        assert '[CURRENT]' in lines[1]
        assert '[CURRENT]' not in lines[0]
        assert '[CURRENT]' not in lines[2]
    
    def test_without_emoji(self):
        """Test multi-phase display without status emoji."""
        generator = VisualProgressGenerator()
        phases = [
            {"name": "Phase1", "status": "complete", "progress": 100}
        ]
        result = generator.generate_multi_phase(phases, current_phase=1, show_status_emoji=False)
        
        assert '✅' not in result
        assert 'Phase1' in result
        assert '██████████' in result


class TestEpicProgress:
    """Tests for generate_epic_progress() method."""
    
    def test_epic_progress_half(self):
        """Test epic progress at 50%."""
        generator = VisualProgressGenerator()
        result = generator.generate_epic_progress(5, 10)
        assert 'Epic:' in result
        assert '█████░░░░░' in result
        assert '50%' in result
        assert '(5/10 complete)' in result
    
    def test_epic_progress_custom_name(self):
        """Test epic progress with custom name."""
        generator = VisualProgressGenerator()
        result = generator.generate_epic_progress(8, 10, epic_name="CORTEX v5")
        assert 'CORTEX v5:' in result
        assert '████████░░' in result
        assert '80%' in result
        assert '(8/10 complete)' in result
    
    def test_epic_progress_zero_total(self):
        """Test epic progress with zero total (edge case)."""
        generator = VisualProgressGenerator()
        result = generator.generate_epic_progress(0, 0)
        assert '0%' in result
        assert '(0/0 complete)' in result


class TestStatusEmoji:
    """Tests for get_status_emoji() method."""
    
    def test_all_status_types(self):
        """Test all defined status types."""
        generator = VisualProgressGenerator()
        
        assert generator.get_status_emoji('complete') == '✅'
        assert generator.get_status_emoji('in_progress') == '🔄'
        assert generator.get_status_emoji('pending') == '⏳'
        assert generator.get_status_emoji('blocked') == '🔒'
        assert generator.get_status_emoji('failed') == '❌'
        assert generator.get_status_emoji('skipped') == '⏭️'
    
    def test_unknown_status(self):
        """Test unknown status returns default emoji."""
        generator = VisualProgressGenerator()
        assert generator.get_status_emoji('unknown') == '❓'


class TestPercentageCalculation:
    """Tests for calculate_percentage() method."""
    
    def test_fifty_percent_calculation(self):
        """Test 50% calculation."""
        generator = VisualProgressGenerator()
        assert generator.calculate_percentage(5, 10) == 50.0
    
    def test_hundred_percent_calculation(self):
        """Test 100% calculation."""
        generator = VisualProgressGenerator()
        assert generator.calculate_percentage(10, 10) == 100.0
    
    def test_zero_percent_calculation(self):
        """Test 0% calculation."""
        generator = VisualProgressGenerator()
        assert generator.calculate_percentage(0, 10) == 0.0
    
    def test_fractional_calculation(self):
        """Test fractional percentage calculation."""
        generator = VisualProgressGenerator()
        result = generator.calculate_percentage(7, 10)
        assert result == 70.0
    
    def test_zero_total_edge_case(self):
        """Test calculation with zero total (division by zero protection)."""
        generator = VisualProgressGenerator()
        result = generator.calculate_percentage(5, 0)
        assert result == 0.0


class TestCustomCharacters:
    """Tests for custom fill/empty characters."""
    
    def test_custom_filled_char(self):
        """Test with custom filled character."""
        generator = VisualProgressGenerator(filled_char='#', empty_char='-')
        result = generator.generate_bar(50)
        assert result == '#####-----'
    
    def test_custom_width_init(self):
        """Test initialization with custom width."""
        generator = VisualProgressGenerator(width=20)
        result = generator.generate_bar(50)
        assert len(result) == 20


class TestIntegrationScenarios:
    """Integration tests for real-world scenarios."""
    
    def test_planning_orchestrator_scenario(self):
        """Test typical planning orchestrator usage."""
        generator = VisualProgressGenerator()
        
        # Simulate 4-phase planning execution
        phases = [
            {"name": "Analysis", "status": "complete", "progress": 100},
            {"name": "Design", "status": "complete", "progress": 100},
            {"name": "Implementation", "status": "in_progress", "progress": 60},
            {"name": "Testing", "status": "pending", "progress": 0}
        ]
        
        result = generator.generate_multi_phase(phases, current_phase=3)
        lines = result.split('\n')
        
        assert len(lines) == 4
        assert lines[2].count('[CURRENT]') == 1  # Only phase 3 marked current
        assert '██████░░░░' in lines[2]  # 60% progress bar
    
    def test_epic_tracking_scenario(self):
        """Test epic-level progress tracking."""
        generator = VisualProgressGenerator()
        
        # Simulate C50 epic: 9/19 complete
        result = generator.generate_epic_progress(9, 19, epic_name="C50 CORTEX v5")
        
        assert 'C50 CORTEX v5:' in result
        assert '(9/19 complete)' in result
        # 9/19 = 47.37% → ~47%
        assert '47%' in result or '48%' in result  # Allow rounding variance


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
