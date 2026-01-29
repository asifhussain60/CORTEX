"""Team Assumptions Loader - Capacity Planning Configuration.

Loads team estimation assumptions from YAML and generates transparent legends
for all capacity calculations.

Phase 12 Enhancement: Estimation Transparency
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
import yaml


logger = logging.getLogger(__name__)

# Default path to assumptions config
DEFAULT_CONFIG_PATH = Path(__file__).parent / "config" / "team_assumptions.yaml"


@dataclass
class SkillLevelConfig:
    """Configuration for a single skill level.
    
    Attributes:
        title: Display title (e.g., "Senior Engineer")
        hours_per_story_point: Productivity rate
        hourly_rate: Cost per hour
        annual_salary: Yearly compensation
        description: Role description
    """
    title: str
    hours_per_story_point: float
    hourly_rate: float
    annual_salary: float
    description: str = ""


@dataclass
class TeamAssumptions:
    """Team capacity estimation assumptions.
    
    Loaded from YAML configuration for transparent, version-controlled
    estimation basis.
    
    Attributes:
        version: Config version
        updated: Last update date
        skill_levels: Dict of skill level configurations
        schedule: Work schedule settings
        costs: Cost calculation settings
        legend_settings: Legend display preferences
    """
    version: str
    updated: str
    author: str
    skill_levels: Dict[str, SkillLevelConfig] = field(default_factory=dict)
    schedule: Dict[str, Any] = field(default_factory=dict)
    costs: Dict[str, Any] = field(default_factory=dict)
    legend_settings: Dict[str, bool] = field(default_factory=dict)
    
    def get_skill_config(self, skill_level: str) -> Optional[SkillLevelConfig]:
        """Get configuration for a skill level.
        
        Args:
            skill_level: Skill level key (junior, mid_level, senior, architect)
            
        Returns:
            SkillLevelConfig or None if not found
        """
        return self.skill_levels.get(skill_level.lower())
    
    def get_hourly_rate(self, skill_level: str) -> float:
        """Get hourly rate for skill level.
        
        Args:
            skill_level: Skill level key
            
        Returns:
            Hourly rate or 0 if not found
        """
        config = self.get_skill_config(skill_level)
        return config.hourly_rate if config else 0.0
    
    def get_hours_per_point(self, skill_level: str) -> float:
        """Get hours per story point for skill level.
        
        Args:
            skill_level: Skill level key
            
        Returns:
            Hours per story point or 0 if not found
        """
        config = self.get_skill_config(skill_level)
        return config.hours_per_story_point if config else 0.0
    
    def calculate_cost(self, hours: float, skill_level: str) -> float:
        """Calculate cost for hours at skill level.
        
        Args:
            hours: Number of hours
            skill_level: Skill level key
            
        Returns:
            Total cost including overhead
        """
        rate = self.get_hourly_rate(skill_level)
        overhead = self.costs.get("overhead_multiplier", 1.0)
        return hours * rate * overhead
    
    def generate_legend(self, skill_levels_used: Optional[list] = None) -> str:
        """Generate estimation basis legend.
        
        Args:
            skill_levels_used: Optional list of skill levels to include.
                             If None, includes all levels.
        
        Returns:
            Formatted legend string
        """
        lines = [
            f"📊 Estimation Basis (v{self.version}, updated {self.updated}):",
            f"   Author: {self.author}",
            ""
        ]
        
        # Skill levels
        levels_to_show = skill_levels_used or list(self.skill_levels.keys())
        
        lines.append("   Skill Levels:")
        for level_key in levels_to_show:
            config = self.skill_levels.get(level_key)
            if config:
                rate_info = f"${config.hourly_rate}/hr" if self.legend_settings.get("show_hourly_rates", True) else ""
                prod_info = f"@ {config.hours_per_story_point} hrs/story point" if self.legend_settings.get("show_productivity", True) else ""
                lines.append(f"   • {config.title}: {rate_info} {prod_info}")
        
        # Schedule info
        lines.append("")
        lines.append("   Schedule:")
        lines.append(f"   • Sprint: {self.schedule.get('sprint_days', 10)} days × {self.schedule.get('work_hours_per_day', 8)} hrs/day")
        lines.append(f"   • Productive time: {self.schedule.get('productive_hours_ratio', 0.75) * 100:.0f}% (accounts for meetings/admin)")
        
        # Cost info
        if self.legend_settings.get("show_overhead", True):
            lines.append("")
            lines.append("   Cost Factors:")
            lines.append(f"   • Overhead multiplier: {self.costs.get('overhead_multiplier', 1.3)}x (benefits, equipment)")
            lines.append(f"   • Contingency buffer: {self.costs.get('contingency_percent', 15)}%")
            lines.append(f"   • Currency: {self.costs.get('currency', 'USD')}")
        
        return "\n".join(lines)
    
    def generate_compact_legend(self, skill_level: str) -> str:
        """Generate compact single-line legend for a skill level.
        
        Args:
            skill_level: Skill level used in estimate
            
        Returns:
            Compact legend string
        """
        config = self.get_skill_config(skill_level)
        if not config:
            return f"⚠️ Unknown skill level: {skill_level}"
        
        return (
            f"Based on: {config.title} @ ${config.hourly_rate}/hr, "
            f"{config.hours_per_story_point} hrs/pt "
            f"(v{self.version}, {self.updated})"
        )


class TeamAssumptionsLoader:
    """Loader for team assumptions configuration.
    
    Loads YAML configuration and provides TeamAssumptions instance.
    Caches loaded configuration for efficiency.
    """
    
    _cache: Optional[TeamAssumptions] = None
    _cache_path: Optional[Path] = None
    
    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> TeamAssumptions:
        """Load team assumptions from YAML.
        
        Args:
            config_path: Path to config file. Uses default if None.
            
        Returns:
            TeamAssumptions instance
        """
        path = config_path or DEFAULT_CONFIG_PATH
        
        # Return cached if same path
        if cls._cache and cls._cache_path == path:
            return cls._cache
        
        if not path.exists():
            logger.warning(f"Config not found at {path}, using defaults")
            return cls._create_defaults()
        
        try:
            with open(path, 'r') as f:
                data = yaml.safe_load(f)
            
            assumptions = cls._parse_config(data)
            cls._cache = assumptions
            cls._cache_path = path
            
            logger.info(f"Loaded team assumptions v{assumptions.version} from {path}")
            return assumptions
            
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return cls._create_defaults()
    
    @classmethod
    def reload(cls, config_path: Optional[Path] = None) -> TeamAssumptions:
        """Force reload of configuration.
        
        Args:
            config_path: Path to config file
            
        Returns:
            Fresh TeamAssumptions instance
        """
        cls._cache = None
        cls._cache_path = None
        return cls.load(config_path)
    
    @classmethod
    def _parse_config(cls, data: Dict[str, Any]) -> TeamAssumptions:
        """Parse YAML data into TeamAssumptions.
        
        Args:
            data: Parsed YAML dictionary
            
        Returns:
            TeamAssumptions instance
        """
        skill_levels = {}
        for key, value in data.get("skill_levels", {}).items():
            skill_levels[key] = SkillLevelConfig(
                title=value.get("title", key.title()),
                hours_per_story_point=value.get("hours_per_story_point", 4.5),
                hourly_rate=value.get("hourly_rate", 100),
                annual_salary=value.get("annual_salary", 160000),
                description=value.get("description", ""),
            )
        
        return TeamAssumptions(
            version=data.get("version", "1.0"),
            updated=data.get("updated", "unknown"),
            author=data.get("author", "unknown"),
            skill_levels=skill_levels,
            schedule=data.get("schedule", {}),
            costs=data.get("costs", {}),
            legend_settings=data.get("legend", {}),
        )
    
    @classmethod
    def _create_defaults(cls) -> TeamAssumptions:
        """Create default assumptions when config unavailable.
        
        Returns:
            TeamAssumptions with sensible defaults
        """
        return TeamAssumptions(
            version="default",
            updated="N/A",
            author="system",
            skill_levels={
                "junior": SkillLevelConfig("Junior Engineer", 7, 75, 120000),
                "mid_level": SkillLevelConfig("Mid-Level Engineer", 4.5, 100, 160000),
                "senior": SkillLevelConfig("Senior Engineer", 2.5, 150, 240000),
                "architect": SkillLevelConfig("Staff/Architect", 1.5, 200, 320000),
            },
            schedule={"work_hours_per_day": 8, "sprint_days": 10, "productive_hours_ratio": 0.75},
            costs={"currency": "USD", "overhead_multiplier": 1.3, "contingency_percent": 15},
            legend_settings={"show_hourly_rates": True, "show_productivity": True, "show_overhead": True},
        )


# Convenience function
def get_team_assumptions(config_path: Optional[Path] = None) -> TeamAssumptions:
    """Get team assumptions configuration.
    
    Args:
        config_path: Optional path to config file
        
    Returns:
        TeamAssumptions instance
    """
    return TeamAssumptionsLoader.load(config_path)
