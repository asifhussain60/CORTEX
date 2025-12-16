"""
Comprehensive tests for UnifiedPlanGenerator with detailed timing support.

Tests the cortex-3.9 style master plan generation with:
- Visual progress tracker with ASCII box
- Estimation methodology
- Detailed phase status table (Start/End/Actual/Elapsed/Sub-Plan)
- Business value calculations

Author: Asif Hussain
Version: 1.0.0
"""

import pytest
from pathlib import Path
from src.operations.modules.planning.unified_plan_generator import UnifiedPlanGenerator


class TestUnifiedPlanGeneratorComprehensive:
    """Test comprehensive master plan generation."""
    
    @pytest.fixture
    def generator(self):
        """Create generator instance."""
        return UnifiedPlanGenerator()
    
    @pytest.fixture
    def sample_phases_detailed(self):
        """Sample phases with detailed timing (cortex-3.9 style)."""
        return [
            {
                "id": 1,
                "name": "Foundation Setup",
                "status": "complete",
                "start_time": "05:35",
                "end_time": "05:45",
                "actual": "10 min",
                "elapsed": "0:10",
                "estimated": "2h",
                "sub_plan": "phase-01-foundation.md",
                "tokens_saved": "150"
            },
            {
                "id": 2,
                "name": "Core Implementation",
                "status": "complete",
                "start_time": "05:45",
                "end_time": "06:20",
                "actual": "35 min",
                "elapsed": "0:45",
                "estimated": "4h",
                "sub_plan": "phase-02-core.md",
                "tokens_saved": "320"
            },
            {
                "id": 3,
                "name": "Integration Testing",
                "status": "in-progress",
                "start_time": "06:20",
                "end_time": "-",
                "actual": "15 min",
                "elapsed": "1:00",
                "estimated": "3h",
                "sub_plan": "phase-03-testing.md",
                "tokens_saved": "180"
            },
            {
                "id": 4,
                "name": "Documentation",
                "status": "pending",
                "start_time": "-",
                "end_time": "-",
                "actual": "-",
                "elapsed": "-",
                "estimated": "2h",
                "sub_plan": "phase-04-docs.md",
                "tokens_saved": "-"
            }
        ]
    
    @pytest.fixture
    def sample_metadata(self):
        """Sample plan metadata."""
        return {
            "date": "December 16, 2025",
            "complexity_tier": 3,
            "summary": "Test plan for comprehensive master plan generation with detailed timing tracking.",
            "baseline_tokens": 50000,
            "current_tokens": 45000,
            "total_files": 25
        }
    
    def test_comprehensive_master_plan_generation(self, generator, sample_phases_detailed, sample_metadata):
        """Test complete master plan generation with all cortex-3.9 features."""
        master_plan = generator.generate_master_plan(
            plan_id="test-comprehensive-plan",
            phases=sample_phases_detailed,
            metadata=sample_metadata,
            include_token_tracking=True,
            include_visual_tracker=True,
            include_continuation_prompt=True,
            compressed=False
        )
        
        # Verify all required sections
        assert "Visual Progress Tracker" in master_plan
        assert "Overall Progress:" in master_plan
        assert "Total Actual Time:" in master_plan
        assert "Total Elapsed Time:" in master_plan
        assert "Senior Dev Estimate:" in master_plan
        assert "Estimation Methodology:" in master_plan
        assert "Testing overhead: x1.30" in master_plan
        assert "Documentation: x1.15" in master_plan
        assert "Rework/refinement: x1.10" in master_plan
        assert "Combined multiplier: 1.55x" in master_plan
        assert "Complexity buffer: +33%" in master_plan
    
    def test_detailed_phase_status_table(self, generator, sample_phases_detailed, sample_metadata):
        """Test detailed phase status table with all columns."""
        master_plan = generator.generate_master_plan(
            plan_id="test-phase-table",
            phases=sample_phases_detailed,
            metadata=sample_metadata,
            include_token_tracking=True,
            include_visual_tracker=True,
            include_continuation_prompt=True,
            compressed=False
        )
        
        # Verify table headers
        assert "Phase Status Table" in master_plan
        assert "| Phase | Name | Status | Start | End | Actual | Elapsed | Sub-Plan |" in master_plan
        
        # Verify phase data
        assert "Foundation Setup" in master_plan
        assert "Core Implementation" in master_plan
        assert "Integration Testing" in master_plan
        assert "Documentation" in master_plan
        
        # Verify timing data
        assert "05:35" in master_plan  # start_time
        assert "05:45" in master_plan  # end_time
        assert "10 min" in master_plan  # actual
        assert "0:10" in master_plan  # elapsed
        
        # Verify sub-plan links
        assert "[phase-01-foundation.md](phase-01-foundation.md)" in master_plan
        assert "[phase-02-core.md](phase-02-core.md)" in master_plan
        assert "[phase-03-testing.md](phase-03-testing.md)" in master_plan
        assert "[phase-04-docs.md](phase-04-docs.md)" in master_plan
    
    def test_status_emojis_and_legend(self, generator, sample_phases_detailed, sample_metadata):
        """Test status emojis and legend in phase table."""
        master_plan = generator.generate_master_plan(
            plan_id="test-status-emojis",
            phases=sample_phases_detailed,
            metadata=sample_metadata,
            include_token_tracking=True,
            include_visual_tracker=True,
            include_continuation_prompt=True,
            compressed=False
        )
        
        # Verify status emojis
        assert "✅ Complete" in master_plan
        assert "🟡 In Progress" in master_plan
        assert "⏳ Pending" in master_plan
        
        # Verify legend
        assert "**Legend:**" in master_plan
        assert "⏳ Pending - Not started" in master_plan
        assert "🟡 In Progress - Active development" in master_plan
        assert "✅ Complete - Finished and validated" in master_plan
        assert "⚠️ Blocked - Dependency or issue preventing progress" in master_plan
    
    def test_calculation_total_actual_minutes(self, generator, sample_phases_detailed):
        """Test calculation of total actual time in minutes."""
        total_minutes = generator._calculate_total_actual_minutes(sample_phases_detailed)
        
        # 10 min + 35 min + 15 min = 60 minutes (only completed and in-progress phases)
        assert total_minutes == 60
    
    def test_format_elapsed_time(self, generator, sample_phases_detailed):
        """Test formatting of elapsed time."""
        elapsed = generator._format_elapsed_time(sample_phases_detailed)
        
        # 0:10 + 0:45 + 1:00 = 1:55 (approximately, may be 1:54 due to rounding)
        assert elapsed in ["1:54", "1:55"]
    
    def test_senior_dev_estimate_calculations(self, generator, sample_phases_detailed, sample_metadata):
        """Test senior developer estimate calculations."""
        master_plan = generator.generate_master_plan(
            plan_id="test-estimates",
            phases=sample_phases_detailed,
            metadata=sample_metadata,
            include_token_tracking=True,
            include_visual_tracker=True,
            include_continuation_prompt=True,
            compressed=False
        )
        
        # Base hours: 2 + 4 + 3 + 2 = 11 hours
        # Min estimate: 11 * 1.55 = 17 hours
        # Max estimate: 11 * 2.05 = 22-23 hours
        assert "17-23 hours" in master_plan or "17-22 hours" in master_plan
        
        # Verify weeks calculation (17-23 hours / 40 hours/week)
        assert "weeks @ 40h/week baseline" in master_plan
    
    def test_progress_bar_rendering(self, generator, sample_phases_detailed, sample_metadata):
        """Test ASCII progress bar rendering."""
        master_plan = generator.generate_master_plan(
            plan_id="test-progress-bar",
            phases=sample_phases_detailed,
            metadata=sample_metadata,
            include_token_tracking=True,
            include_visual_tracker=True,
            include_continuation_prompt=True,
            compressed=False
        )
        
        # 2 complete out of 4 phases = 50%
        assert "50% (2/4 phases complete)" in master_plan
        
        # Verify ASCII box
        assert "+==============================================================================+" in master_plan
    
    def test_compressed_vs_detailed_format(self, generator, sample_phases_detailed, sample_metadata):
        """Test compressed format vs detailed format."""
        # Detailed format
        detailed = generator.generate_master_plan(
            plan_id="test-detailed",
            phases=sample_phases_detailed,
            metadata=sample_metadata,
            include_token_tracking=True,
            include_visual_tracker=True,
            include_continuation_prompt=True,
            compressed=False
        )
        
        # Compressed format
        compressed = generator.generate_master_plan(
            plan_id="test-compressed",
            phases=sample_phases_detailed,
            metadata=sample_metadata,
            include_token_tracking=True,
            include_visual_tracker=True,
            include_continuation_prompt=True,
            compressed=True
        )
        
        # Detailed should be significantly longer
        assert len(detailed) > len(compressed) * 2
        
        # Detailed should have full section names
        assert "Visual Progress Tracker" in detailed
        assert "Estimation Methodology:" in detailed
        
        # Compressed should have shorter format
        assert "## 📊 Progress" in compressed
    
    def test_continuation_prompt_with_phases_remaining(self, generator, sample_phases_detailed, sample_metadata):
        """Test continuation prompt when phases remain."""
        master_plan = generator.generate_master_plan(
            plan_id="test-continuation",
            phases=sample_phases_detailed,
            metadata=sample_metadata,
            include_token_tracking=True,
            include_visual_tracker=True,
            include_continuation_prompt=True,
            compressed=False
        )
        
        # Should have continuation prompt
        assert "Continuation Prompt" in master_plan
        assert "COPY-PASTE THIS TO RESUME WORK:" in master_plan
        assert "Continue `test-continuation`" in master_plan
        assert "Phase 4" in master_plan  # Next pending phase
    
    def test_no_continuation_prompt_when_complete(self, generator, sample_metadata):
        """Test no continuation prompt when all phases complete."""
        all_complete_phases = [
            {
                "id": 1,
                "name": "Phase 1",
                "status": "complete",
                "start_time": "05:35",
                "end_time": "05:45",
                "actual": "10 min",
                "elapsed": "0:10",
                "estimated": "2h",
                "sub_plan": "phase-01.md"
            },
            {
                "id": 2,
                "name": "Phase 2",
                "status": "complete",
                "start_time": "05:45",
                "end_time": "06:00",
                "actual": "15 min",
                "elapsed": "0:25",
                "estimated": "3h",
                "sub_plan": "phase-02.md"
            }
        ]
        
        master_plan = generator.generate_master_plan(
            plan_id="test-no-continuation",
            phases=all_complete_phases,
            metadata=sample_metadata,
            include_token_tracking=True,
            include_visual_tracker=True,
            include_continuation_prompt=True,
            compressed=False
        )
        
        # Should NOT have continuation prompt when complete
        assert "All phases done" in master_plan or "Continuation Prompt" not in master_plan


class TestHelperMethods:
    """Test helper calculation methods."""
    
    @pytest.fixture
    def generator(self):
        """Create generator instance."""
        return UnifiedPlanGenerator()
    
    def test_parse_time_to_hours(self, generator):
        """Test time string parsing."""
        assert generator._parse_time_to_hours("4h") == 4.0
        assert generator._parse_time_to_hours("2d") == 16.0
        assert generator._parse_time_to_hours("16h (2d)") == 16.0
        assert generator._parse_time_to_hours("1h 30m") == 1.5
        assert generator._parse_time_to_hours("2h 15m") == 2.25
        assert generator._parse_time_to_hours("3d 4h") == 28.0
        assert generator._parse_time_to_hours("-") == 0.0
        assert generator._parse_time_to_hours("") == 0.0
    
    def test_calculate_efficiency(self, generator):
        """Test efficiency calculation."""
        # 10 hours estimated, 8 hours actual = 20% efficiency
        efficiency = generator._calculate_efficiency(10.0, 8.0)
        assert efficiency == 20.0
        
        # 10 hours estimated, 12 hours actual = -20% efficiency (slower)
        efficiency = generator._calculate_efficiency(10.0, 12.0)
        assert efficiency == -20.0
        
        # Edge cases
        assert generator._calculate_efficiency(0.0, 5.0) == 0.0
        assert generator._calculate_efficiency(10.0, 0.0) == 0.0
    
    def test_format_work_hours(self, generator):
        """Test work hours formatting."""
        assert generator._format_work_hours(1.5) == "1:30h"
        assert generator._format_work_hours(4.0) == "4h"
        assert generator._format_work_hours(40.0) == "40h (5.0d)"
        assert generator._format_work_hours(0.0) == "-"
    
    def test_format_elapsed_hours(self, generator):
        """Test elapsed hours formatting."""
        assert generator._format_elapsed_hours(1.5) == "1:30h"
        assert generator._format_elapsed_hours(4.0) == "4h"
        assert generator._format_elapsed_hours(40.0) == "40h (5.0d)"
        assert generator._format_elapsed_hours(0.0) == "-"
