"""Tests for Team Assumptions and Estimation Legend.

Phase 12 Enhancement: Estimation Transparency
AC-CAP-2-05: Include estimation basis legend for transparency
"""

import pytest
from pathlib import Path

from cortex.capacity.team_assumptions import (
    TeamAssumptionsLoader,
    TeamAssumptions,
    SkillLevelConfig,
    get_team_assumptions,
)
from cortex.capacity.multi_model_estimation_engine import (
    MultiModelEstimationEngine,
    SkillLevel,
)


class TestTeamAssumptionsLoader:
    """Tests for TeamAssumptionsLoader."""
    
    def test_load_default_config(self):
        """Test loading default config file."""
        assumptions = get_team_assumptions()
        
        assert assumptions.version == "1.0"
        assert assumptions.author == "Asif Hussain"
        assert "senior" in assumptions.skill_levels
    
    def test_skill_level_config(self):
        """Test skill level configuration access."""
        assumptions = get_team_assumptions()
        
        senior = assumptions.get_skill_config("senior")
        assert senior is not None
        assert senior.title == "Senior Engineer"
        assert senior.hourly_rate == 150
        assert senior.hours_per_story_point == 2.5
    
    def test_get_hourly_rate(self):
        """Test getting hourly rate by skill level."""
        assumptions = get_team_assumptions()
        
        assert assumptions.get_hourly_rate("junior") == 75
        assert assumptions.get_hourly_rate("mid_level") == 100
        assert assumptions.get_hourly_rate("senior") == 150
        assert assumptions.get_hourly_rate("architect") == 200
    
    def test_get_hours_per_point(self):
        """Test getting hours per story point."""
        assumptions = get_team_assumptions()
        
        assert assumptions.get_hours_per_point("junior") == 7
        assert assumptions.get_hours_per_point("senior") == 2.5
    
    def test_calculate_cost_with_overhead(self):
        """Test cost calculation includes overhead."""
        assumptions = get_team_assumptions()
        
        # 10 hours at $150/hr with 1.3x overhead = $1950
        cost = assumptions.calculate_cost(10, "senior")
        assert cost == 10 * 150 * 1.3
    
    def test_unknown_skill_level_returns_zero(self):
        """Test unknown skill level returns 0."""
        assumptions = get_team_assumptions()
        
        assert assumptions.get_hourly_rate("nonexistent") == 0
        assert assumptions.get_hours_per_point("nonexistent") == 0


class TestLegendGeneration:
    """Tests for legend generation."""
    
    def test_generate_full_legend(self):
        """Test full legend generation."""
        assumptions = get_team_assumptions()
        
        legend = assumptions.generate_legend()
        
        assert "📊 Estimation Basis" in legend
        assert "v1.0" in legend
        assert "Senior Engineer" in legend
        assert "$150/hr" in legend
        assert "2.5 hrs/story point" in legend
        assert "Sprint:" in legend
    
    def test_generate_legend_specific_levels(self):
        """Test legend for specific skill levels only."""
        assumptions = get_team_assumptions()
        
        legend = assumptions.generate_legend(skill_levels_used=["senior"])
        
        assert "Senior Engineer" in legend
        assert "Junior Engineer" not in legend
    
    def test_generate_compact_legend(self):
        """Test compact single-line legend."""
        assumptions = get_team_assumptions()
        
        legend = assumptions.generate_compact_legend("senior")
        
        assert "Senior Engineer" in legend
        assert "$150/hr" in legend
        assert "2.5 hrs/pt" in legend
        assert "v1.0" in legend
    
    def test_compact_legend_unknown_level(self):
        """Test compact legend for unknown skill level."""
        assumptions = get_team_assumptions()
        
        legend = assumptions.generate_compact_legend("nonexistent")
        
        assert "⚠️ Unknown skill level" in legend


class TestEstimationEngineWithLegend:
    """Tests for MultiModelEstimationEngine with legend."""
    
    def test_estimate_includes_legend(self):
        """Test estimation result includes legend."""
        engine = MultiModelEstimationEngine()
        
        result = engine.estimate_task(
            task_id="TEST-001",
            optimistic=8,
            likely=12,
            pessimistic=20,
            story_points=5,
            skill_level=SkillLevel.SENIOR,
        )
        
        assert result.legend != ""
        assert "Senior Engineer" in result.legend
        assert "$150/hr" in result.legend
    
    def test_estimate_includes_cost(self):
        """Test estimation result includes cost."""
        engine = MultiModelEstimationEngine()
        
        result = engine.estimate_task(
            task_id="TEST-001",
            optimistic=8,
            likely=12,
            pessimistic=20,
            story_points=5,
            skill_level=SkillLevel.SENIOR,
        )
        
        assert result.estimated_cost > 0
        assert result.skill_level_used == "senior"
    
    def test_estimate_compact_legend(self):
        """Test estimation with compact legend."""
        engine = MultiModelEstimationEngine()
        
        result = engine.estimate_task(
            task_id="TEST-001",
            optimistic=8,
            likely=12,
            pessimistic=20,
            story_points=5,
            skill_level=SkillLevel.SENIOR,
            include_legend=False,
        )
        
        # Compact legend is single line
        assert result.legend.count("\n") == 0
    
    def test_summary_includes_cost_and_basis(self):
        """Test summary includes cost and estimation basis."""
        engine = MultiModelEstimationEngine()
        
        result = engine.estimate_task(
            task_id="TEST-001",
            optimistic=8,
            likely=12,
            pessimistic=20,
            story_points=5,
            skill_level=SkillLevel.SENIOR,
        )
        
        summary = engine.get_estimation_summary(result)
        
        assert "estimated_cost" in summary
        assert "USD" in summary["estimated_cost"]
        assert "estimation_basis" in summary
        assert "skill_level" in summary
        assert summary["skill_level"] == "senior"
    
    def test_get_assumptions_legend(self):
        """Test getting full assumptions legend from engine."""
        engine = MultiModelEstimationEngine()
        
        legend = engine.get_assumptions_legend()
        
        assert "📊 Estimation Basis" in legend
        assert "Junior Engineer" in legend
        assert "Senior Engineer" in legend
        assert "Architect" in legend


class TestDefaultFallback:
    """Tests for default fallback when config missing."""
    
    def test_create_defaults(self):
        """Test default assumptions creation."""
        defaults = TeamAssumptionsLoader._create_defaults()
        
        assert defaults.version == "default"
        assert len(defaults.skill_levels) == 4
        assert defaults.get_hourly_rate("senior") == 150
