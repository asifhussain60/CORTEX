"""Unit Tests for Minimal Plan Spine (Rolling Display)

Tests validate:
1. Current + next display (during execution)
2. Previous + current + next display (upon completion)
3. Single-line inline status for chat embedding
4. No history bloat (rolling window only)
"""

import pytest
from cortex.orchestrators.response.minimal_plan_spine import (
    MinimalPlanSpine,
    Phase,
    PhaseStatus,
)


class TestMinimalPlanSpine:
    """Test minimal rolling plan spine"""
    
    @pytest.fixture
    def spine(self):
        """Create spine with 4 phases"""
        phases = [
            "Phase 1 Schema",
            "Phase 2 KSESSIONS",
            "Phase 3 MCP gateway",
            "Phase 4 Architecture",
        ]
        return MinimalPlanSpine(phases)
    
    def test_initial_state_first_phase(self, spine):
        """Test: Initial state shows first phase as active + next"""
        # GIVEN: New spine (no activation yet)
        # WHEN: Get display phases
        display = spine.get_display_phases()
        
        # THEN: Shows phase 1 (active) + phase 2 (next)
        assert len(display) == 2
        assert display[0].name == "Phase 1 Schema"
        assert display[0].status == PhaseStatus.QUEUED  # Not yet activated
        assert display[1].name == "Phase 2 KSESSIONS"
        assert display[1].status == PhaseStatus.QUEUED
    
    def test_activate_phase_shows_current_and_next(self, spine):
        """Test: Activating phase shows current + next only"""
        # GIVEN: Spine
        # WHEN: Activate phase 2
        spine.activate_phase("Phase 2 KSESSIONS")
        display = spine.get_display_phases()
        
        # THEN: Shows phase 2 (active) + phase 3 (next), NOT phase 1
        assert len(display) == 2
        assert display[0].name == "Phase 2 KSESSIONS"
        assert display[0].status == PhaseStatus.ACTIVE
        assert display[1].name == "Phase 3 MCP gateway"
        assert display[1].status == PhaseStatus.QUEUED
    
    def test_complete_and_activate_shows_previous_current_next(self, spine):
        """Test: Upon completion, show previous → current → next (3 lines)"""
        # GIVEN: Spine with phase 2 active
        spine.activate_phase("Phase 2 KSESSIONS")
        
        # WHEN: Complete phase 2 and activate phase 3
        spine.complete_phase("Phase 2 KSESSIONS")
        spine.activate_phase("Phase 3 MCP gateway")
        display = spine.get_display_phases()
        
        # THEN: Shows phase 2 (completed) → phase 3 (active) → phase 4 (next)
        assert len(display) == 3
        assert display[0].name == "Phase 2 KSESSIONS"
        assert display[0].status == PhaseStatus.COMPLETED
        assert display[1].name == "Phase 3 MCP gateway"
        assert display[1].status == PhaseStatus.ACTIVE
        assert display[2].name == "Phase 4 Architecture"
        assert display[2].status == PhaseStatus.QUEUED
    
    def test_ascii_output_shows_only_display_phases(self, spine):
        """Test: ASCII output contains only display phases"""
        # GIVEN: Spine with phase 2 active
        spine.activate_phase("Phase 2 KSESSIONS")
        
        # WHEN: Render ASCII
        ascii_output = spine.to_minimal_ascii()
        
        # THEN: Only shows 2 phases (no phase 1 or 4)
        lines = ascii_output.split("\n")
        assert len(lines) == 2
        assert "Phase 1" not in ascii_output
        assert "Phase 2 KSESSIONS" in ascii_output
        assert "Phase 3 MCP gateway" in ascii_output
        assert "Phase 4" not in ascii_output
    
    def test_ascii_includes_status_labels(self, spine):
        """Test: ASCII includes status labels (active, completed, etc)"""
        # GIVEN: Spine with phase 2 active
        spine.activate_phase("Phase 2 KSESSIONS")
        
        # WHEN: Render ASCII
        ascii_output = spine.to_minimal_ascii()
        
        # THEN: Includes "(active)" label
        assert "(active)" in ascii_output
        # Next phase has no label
        assert "Phase 3 MCP gateway\n" in ascii_output or ascii_output.endswith("Phase 3 MCP gateway")
    
    def test_glyph_usage_correct(self, spine):
        """Test: Glyphs are correct [✓][→][ ]"""
        # GIVEN: Spine with phase 2 active
        spine.activate_phase("Phase 2 KSESSIONS")
        
        # WHEN: Render ASCII
        ascii_output = spine.to_minimal_ascii()
        
        # THEN: Shows [→] for active
        assert "[→]" in ascii_output
        # Shows [ ] for queued
        assert "[ ]" in ascii_output
    
    def test_inline_status_format(self, spine):
        """Test: Inline status uses pipe separator"""
        # GIVEN: Spine with phase 2 active
        spine.activate_phase("Phase 2 KSESSIONS")
        
        # WHEN: Get inline status
        inline = spine.to_inline_status()
        
        # THEN: Format is "[→] Phase 2 | [ ] Phase 3"
        assert " | " in inline
        assert "[→]" in inline
        assert "[ ]" in inline
        assert "Phase 2 KSESSIONS" in inline
        assert "Phase 3 MCP gateway" in inline
    
    def test_completion_transitions_to_3_phase_view(self, spine):
        """Test: Completion transitions from 2-phase to 3-phase view"""
        # GIVEN: Phase 2 active (showing 2 phases)
        spine.activate_phase("Phase 2 KSESSIONS")
        assert len(spine.get_display_phases()) == 2
        
        # WHEN: Complete and move to phase 3
        spine.complete_phase("Phase 2 KSESSIONS")
        spine.activate_phase("Phase 3 MCP gateway")
        
        # THEN: Now showing 3 phases (previous + current + next)
        assert len(spine.get_display_phases()) == 3
        
        inline = spine.to_inline_status()
        # Count pipes (n phases = n-1 pipes)
        assert inline.count(" | ") == 2
    
    def test_no_previous_phase_at_start(self, spine):
        """Test: First phase activation doesn't show previous"""
        # GIVEN: Spine
        # WHEN: Activate phase 1 (first)
        spine.activate_phase("Phase 1 Schema")
        display = spine.get_display_phases()
        
        # THEN: Shows only 2 phases (current + next, no previous)
        assert len(display) == 2
        assert display[0].status == PhaseStatus.ACTIVE
        assert display[1].status == PhaseStatus.QUEUED
    
    def test_no_next_phase_at_end(self, spine):
        """Test: Last phase completion doesn't show next"""
        # GIVEN: Spine with all previous completed
        spine.activate_phase("Phase 1 Schema")
        spine.complete_phase("Phase 1 Schema")
        spine.activate_phase("Phase 2 KSESSIONS")
        spine.complete_phase("Phase 2 KSESSIONS")
        spine.activate_phase("Phase 3 MCP gateway")
        spine.complete_phase("Phase 3 MCP gateway")
        spine.activate_phase("Phase 4 Architecture")
        
        # WHEN: Get display for last phase
        display = spine.get_display_phases()
        
        # THEN: Shows 2 phases (no next available)
        assert len(display) == 2
        assert display[-1].status == PhaseStatus.ACTIVE
    
    def test_rolling_window_never_shows_more_than_3(self, spine):
        """Test: Minimal spine never shows more than 3 phases"""
        # GIVEN: Spine with many phases
        all_phases = [f"Phase {i}" for i in range(1, 11)]
        many_phase_spine = MinimalPlanSpine(all_phases)
        
        # WHEN: Activate middle phase
        many_phase_spine.activate_phase("Phase 5")
        display = many_phase_spine.get_display_phases()
        
        # THEN: Still shows only 3 phases (rolling window)
        assert len(display) <= 3
        # Middle phase is active
        assert any(p.status == PhaseStatus.ACTIVE for p in display)


class TestMinimalPlanSpineIntegration:
    """Integration tests for rolling display workflow"""
    
    def test_full_workflow_4_phases(self):
        """Test: Complete workflow through 4 phases"""
        phases = [
            "Phase 1 Schema",
            "Phase 2 KSESSIONS", 
            "Phase 3 MCP",
            "Phase 4 Architecture",
        ]
        spine = MinimalPlanSpine(phases)
        
        # Step 1: Start phase 1
        spine.activate_phase(phases[0])
        display = spine.get_display_phases()
        assert len(display) == 2
        assert display[0].status == PhaseStatus.ACTIVE
        print("Step 1:", spine.to_inline_status())
        
        # Step 2: Complete phase 1, start phase 2
        spine.complete_phase(phases[0])
        spine.activate_phase(phases[1])
        display = spine.get_display_phases()
        assert len(display) == 3  # Now showing previous+current+next
        print("Step 2:", spine.to_inline_status())
        
        # Step 3: Complete phase 2, start phase 3
        spine.complete_phase(phases[1])
        spine.activate_phase(phases[2])
        display = spine.get_display_phases()
        assert len(display) == 3
        print("Step 3:", spine.to_inline_status())
        
        # Step 4: Complete phase 3, start phase 4 (last phase - no next available)
        spine.complete_phase(phases[2])
        spine.activate_phase(phases[3])
        display = spine.get_display_phases()
        # Phase 4 is last - no next available, so shows previous + current only
        assert len(display) == 2
        print("Step 4:", spine.to_inline_status())
        
        # Step 5: Complete phase 4 (final - all done)
        spine.complete_phase(phases[3])
        display = spine.get_display_phases()
        # All phases completed - shows last 2 completed phases
        assert len(display) == 2
        print("Step 5 (final):", spine.to_inline_status())
    
    def test_minimal_vs_verbose_comparison(self):
        """Test: Show difference between minimal and verbose display"""
        all_phases = [
            "Phase 1 Schema",
            "Phase 2 KSESSIONS",
            "Phase 3 MCP gateway",
            "Phase 4 Architecture",
        ]
        spine = MinimalPlanSpine(all_phases)
        spine.activate_phase("Phase 2 KSESSIONS")
        
        # Minimal display (what we want)
        minimal = spine.to_minimal_ascii()
        
        # Verbose display (what we want to avoid)
        # Would show all 4 phases with their states
        
        print("\n✅ MINIMAL (2 lines):")
        print(minimal)
        print("\n❌ VERBOSE (4 lines - what we're avoiding):")
        print("├─ [ ] Phase 1 Schema")
        print("├─ [→] Phase 2 KSESSIONS (active)")
        print("├─ [ ] Phase 3 MCP gateway")
        print("└─ [ ] Phase 4 Architecture")
        
        # Verify minimal is actually minimal
        assert len(minimal.split("\n")) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
