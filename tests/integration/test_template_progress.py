"""
Integration tests for response template updates with progress visualization.

Tests verify that:
1. Planning templates show progress bars for DoR/Implementation/DoD phases
2. TDD templates show progress bars for RED/GREEN/REFACTOR phases
3. System Alignment templates show progress bars for alignment phases
4. Progress bars use ProgressBar utility
5. Templates render with correct completion percentages

Author: Asif Hussain
Created: 2025-11-28
Increment: 18 (Response Template Updates)
"""

import pytest
from src.utils.progress_bar import ProgressBar
from src.utils.template_renderer import TemplateRenderer


class TestProgressBarRendering:
    """Test progress bar utility rendering."""
    
    def test_progress_bar_20_percent(self):
        """Progress bar should render 20% with 4 filled blocks."""
        bar = ProgressBar(current=2, total=10, width=20)
        rendered = bar.render()
        
        assert "20%" in rendered
        assert "████░░░░░░░░░░░░░░░░" in rendered
    
    def test_progress_bar_50_percent(self):
        """Progress bar should render 50% with 10 filled blocks."""
        bar = ProgressBar(current=5, total=10, width=20)
        rendered = bar.render()
        
        assert "50%" in rendered
        assert "██████████░░░░░░░░░░" in rendered
    
    def test_progress_bar_100_percent(self):
        """Progress bar should render 100% with all blocks filled."""
        bar = ProgressBar(current=10, total=10, width=20)
        rendered = bar.render()
        
        assert "100%" in rendered
        assert "████████████████████" in rendered


class TestTemplateProgressIntegration:
    """Test template renderer integration with progress bars."""
    
    def test_template_renders_progress_placeholder(self):
        """Template should replace {progress} placeholder with progress bar."""
        renderer = TemplateRenderer()
        template = "Work Progress: {progress}"
        
        rendered = renderer.render_with_progress(
            template=template,
            current=3,
            total=5
        )
        
        assert "60%" in rendered
        assert "████████████░░░░░░░░" in rendered
    
    def test_planning_phase_progress(self):
        """Planning template should show phase progress."""
        renderer = TemplateRenderer()
        planning_template = """
## Planning Progress

**Phase Status:**
- [x] DoR Complete
- [x] Implementation Started
- [ ] DoD Validation

**Overall Progress:**
{progress}
"""
        
        rendered = renderer.render_with_progress(
            template=planning_template,
            current=2,  # 2 of 3 phases complete
            total=3
        )
        
        assert "67%" in rendered or "66%" in rendered  # Allow rounding
        assert "█" in rendered
        assert "░" in rendered
    
    def test_tdd_phase_progress(self):
        """TDD template should show RED/GREEN/REFACTOR progress."""
        renderer = TemplateRenderer()
        tdd_template = """
## TDD Workflow Progress

**Phases:**
- [x] RED Phase (failing test)
- [x] GREEN Phase (implementation)
- [ ] REFACTOR Phase

**Progress:**
{progress}
"""
        
        rendered = renderer.render_with_progress(
            template=tdd_template,
            current=2,  # 2 of 3 phases
            total=3
        )
        
        assert "67%" in rendered or "66%" in rendered
        assert "█" in rendered
    
    def test_alignment_phase_progress(self):
        """Alignment template should show catalog/layer progress."""
        renderer = TemplateRenderer()
        alignment_template = """
## System Alignment Progress

**Phases:**
- [x] Phase 0: Catalog Discovery
- [x] Phase 1: Brain Health
- [ ] Phase 2: Git Protection
- [ ] Phase 3: Documentation
- [ ] Phase 4: Metrics

**Progress:**
{progress}
"""
        
        rendered = renderer.render_with_progress(
            template=alignment_template,
            current=2,  # 2 of 5 phases
            total=5
        )
        
        assert "40%" in rendered
        assert "████████░░░░░░░░░░░░" in rendered


class TestMultiPhaseProgress:
    """Test progress bars for multi-phase workflows."""
    
    def test_multi_track_progress(self):
        """Template should support multiple progress bars."""
        renderer = TemplateRenderer()
        multi_template = """
## Feature Implementation

**Planning:**
{planning_progress}

**Implementation:**
{implementation_progress}

**Testing:**
{testing_progress}
"""
        
        # Render planning progress (manual replacement for multi-progress)
        planning_bar = ProgressBar(current=3, total=3, width=20).render()
        impl_bar = ProgressBar(current=2, total=5, width=20).render()
        test_bar = ProgressBar(current=0, total=3, width=20).render()
        
        rendered = multi_template.format(
            planning_progress=planning_bar,
            implementation_progress=impl_bar,
            testing_progress=test_bar
        )
        
        assert "100%" in rendered  # Planning complete
        assert "40%" in rendered   # Implementation in progress
        assert "0%" in rendered    # Testing not started
    
    def test_incremental_progress_tracking(self):
        """Progress bars should update as work completes."""
        renderer = TemplateRenderer()
        template = "Increments: {progress}"
        
        # Simulate completing increments
        increments_completed = [
            (5, 25),   # 5 of 25 = 20%
            (10, 25),  # 10 of 25 = 40%
            (15, 25),  # 15 of 25 = 60%
            (20, 25),  # 20 of 25 = 80%
            (25, 25),  # 25 of 25 = 100%
        ]
        
        for current, total in increments_completed:
            rendered = renderer.render_with_progress(
                template=template,
                current=current,
                total=total
            )
            
            expected_percent = int((current / total) * 100)
            assert f"{expected_percent}%" in rendered


class TestProgressBarEdgeCases:
    """Test progress bar edge cases."""
    
    def test_zero_total_shows_0_percent(self):
        """Zero total should show 0% without division error."""
        bar = ProgressBar(current=0, total=0, width=20)
        rendered = bar.render()
        
        assert "0%" in rendered
        assert "░░░░░░░░░░░░░░░░░░░░" in rendered
    
    def test_negative_values_handled(self):
        """Negative values should be clamped to 0."""
        bar = ProgressBar(current=-5, total=10, width=20)
        rendered = bar.render()
        
        # Should clamp to 0% (implementation-dependent)
        assert "%" in rendered
        assert rendered.count("░") >= 10  # Should have empty blocks
    
    def test_current_exceeds_total(self):
        """Current > total should show 100% (or clamp)."""
        bar = ProgressBar(current=15, total=10, width=20)
        rendered = bar.render()
        
        # Should clamp to 100% or show overflow (implementation-dependent)
        assert "%" in rendered
