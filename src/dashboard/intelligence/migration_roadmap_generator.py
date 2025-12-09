"""
Phase 9.1: Migration Roadmap Generator

Detects outdated technologies and generates prioritized, phased migration roadmaps
based on risk scores, project counts, effort estimates, and EOL urgency.
"""

import os
from typing import Dict, List, Optional, Any
import yaml


class MigrationRoadmapGenerator:
    """
    Generates migration roadmaps for outdated technologies.
    
    Features:
    - Loads migration paths from YAML configuration
    - Detects outdated technologies by status or risk score
    - Calculates effort with size/coverage/experience multipliers
    - Prioritizes migrations using weighted scoring
    - Groups migrations into 3 phases over 18 months
    """
    
    def __init__(self):
        """Initialize generator and load migration matrix."""
        self.matrix = None
        self.priority_weights = None
        self._load_configuration()
    
    def _load_configuration(self):
        """Load migration matrix and priority weights from YAML."""
        config_path = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "..",
            "cortex-brain", "config", "migration_path_matrix.yaml"
        )
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self.matrix = yaml.safe_load(f)
        
        self.priority_weights = self.matrix.get("priority_weights", {
            "risk_score": 0.4,
            "project_count": 0.3,
            "effort": 0.2,
            "eol_urgency": 0.1
        })
    
    def load_migration_matrix(self) -> Dict[str, Any]:
        """
        Load migration matrix from YAML configuration.
        
        Returns:
            Dictionary containing migrations and priority weights
        """
        return self.matrix
    
    def find_migration_path(self, technology_name: str) -> Optional[Dict[str, Any]]:
        """
        Find migration path for a technology.
        
        Args:
            technology_name: Name of technology to find path for
            
        Returns:
            Migration path dictionary or None if not found
        """
        tech_lower = technology_name.lower()
        
        for migration in self.matrix.get("migrations", []):
            if migration["from"].lower() == tech_lower:
                return migration
        
        return None
    
    def detect_outdated_technologies(self, tech_stack: Dict[str, List[Dict]]) -> List[Dict]:
        """
        Detect outdated technologies from tech stack.
        
        Args:
            tech_stack: Dictionary with categories (backend, frontend, etc.)
            
        Returns:
            List of outdated technology dictionaries
        """
        outdated = []
        
        for category, technologies in tech_stack.items():
            # Skip if not a list (could be metadata fields)
            if not isinstance(technologies, list):
                continue
                
            for tech in technologies:
                # Skip if tech is a string (simple format)
                if isinstance(tech, str):
                    continue
                    
                # Check status field
                if tech.get("status") == "outdated":
                    outdated.append(tech)
                # Check risk score (>60 is high risk)
                elif tech.get("risk_score", 0) > 60:
                    outdated.append(tech)
        
        return outdated
    
    def calculate_effort(
        self,
        migration_path: Dict[str, Any],
        project_count: int,
        project_size: str = "medium",
        test_coverage: str = "medium",
        team_experience: str = "intermediate"
    ) -> int:
        """
        Calculate migration effort with multipliers.
        
        Args:
            migration_path: Migration path dictionary
            project_count: Number of projects to migrate
            project_size: "small" (0.7x), "medium" (1.0x), or "large" (1.5x)
            test_coverage: "high" (0.8x), "medium" (1.0x), or "low" (1.3x)
            team_experience: "expert" (0.7x), "intermediate" (1.0x), or "beginner" (1.5x)
            
        Returns:
            Total effort in hours
        """
        base_effort = migration_path.get("effort_per_project", 0)
        
        # Size multipliers
        size_multipliers = {"small": 0.7, "medium": 1.0, "large": 1.5}
        size_mult = size_multipliers.get(project_size, 1.0)
        
        # Test coverage multipliers
        coverage_multipliers = {"high": 0.8, "medium": 1.0, "low": 1.3}
        coverage_mult = coverage_multipliers.get(test_coverage, 1.0)
        
        # Team experience multipliers
        experience_multipliers = {"expert": 0.7, "intermediate": 1.0, "beginner": 1.5}
        experience_mult = experience_multipliers.get(team_experience, 1.0)
        
        # Calculate total effort
        effort = base_effort * project_count * size_mult * coverage_mult * experience_mult
        
        return int(effort)
    
    def get_priority_weights(self) -> Dict[str, float]:
        """
        Get priority weights configuration.
        
        Returns:
            Dictionary of priority weights
        """
        return self.priority_weights
    
    def calculate_priority(
        self,
        technology: Dict[str, Any],
        migration_path: Dict[str, Any],
        project_count: int
    ) -> float:
        """
        Calculate migration priority using weighted scoring.
        
        Formula:
            priority = risk_score(40%) + project_count(30%) - effort(20%) + eol_urgency(10%)
        
        Args:
            technology: Technology dictionary with risk_score, months_to_eol
            migration_path: Migration path dictionary
            project_count: Number of projects affected
            
        Returns:
            Priority score (0-100, higher is more urgent)
        """
        # Risk score component (0-100) × 40%
        risk_score = technology.get("risk_score", 50)
        risk_component = risk_score * self.priority_weights["risk_score"]
        
        # Project count component (normalized to 0-100) × 30%
        # Assume max 20 projects for normalization
        project_normalized = min(project_count / 20.0 * 100, 100)
        project_component = project_normalized * self.priority_weights["project_count"]
        
        # Effort component (inverted - lower effort = higher priority) × 20%
        base_effort = migration_path.get("effort_per_project", 0)
        total_effort = base_effort * project_count
        # Normalize: 0 hours = 100, 500+ hours = 0
        effort_normalized = max(0, min(100, 100 - (total_effort / 500.0 * 100)))
        effort_component = effort_normalized * self.priority_weights["effort"]
        
        # EOL urgency component (0-100) × 10%
        months_to_eol = technology.get("months_to_eol")
        if months_to_eol is not None:
            # 0 months = 100 (urgent), 24+ months = 0 (not urgent)
            eol_urgency = max(0, min(100, 100 - (months_to_eol / 24.0 * 100)))
        else:
            eol_urgency = 0
        eol_component = eol_urgency * self.priority_weights["eol_urgency"]
        
        # Total priority
        priority = risk_component + project_component + effort_component + eol_component
        
        return round(priority, 2)
    
    def group_into_phases(self, migrations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Group migrations into 3 phases over 18 months.
        
        Phasing strategy:
        - Phase 1 (0-6 months): High priority, quick wins
        - Phase 2 (6-12 months): Medium priority, moderate effort
        - Phase 3 (12-18 months): Lower priority, large efforts
        
        Args:
            migrations: List of migration dictionaries with priority and effort
            
        Returns:
            List of 3 phase dictionaries with migrations, duration, and effort
        """
        if not migrations:
            return [
                {"name": "Phase 1", "duration_months": 6, "migrations": [], "total_effort_hours": 0},
                {"name": "Phase 2", "duration_months": 6, "migrations": [], "total_effort_hours": 0},
                {"name": "Phase 3", "duration_months": 6, "migrations": [], "total_effort_hours": 0}
            ]
        
        # Sort by priority (highest first)
        sorted_migrations = sorted(migrations, key=lambda m: m["priority"], reverse=True)
        
        # Initialize phases
        phases = [
            {"name": "Phase 1", "duration_months": 6, "migrations": [], "total_effort_hours": 0},
            {"name": "Phase 2", "duration_months": 6, "migrations": [], "total_effort_hours": 0},
            {"name": "Phase 3", "duration_months": 6, "migrations": [], "total_effort_hours": 0}
        ]
        
        # Distribute migrations across phases
        # Strategy: Alternate between phases to balance workload
        phase_idx = 0
        for migration in sorted_migrations:
            phases[phase_idx]["migrations"].append(migration)
            # Handle both "effort_hours" and "effort" keys for flexibility
            effort = migration.get("effort_hours", migration.get("effort", 0))
            phases[phase_idx]["total_effort_hours"] += effort
            
            # Move to next phase (round-robin)
            phase_idx = (phase_idx + 1) % 3
        
        return phases
    
    def generate_roadmap(self, tech_stack: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """
        Generate complete migration roadmap from tech stack.
        
        Args:
            tech_stack: Dictionary with technology categories
            
        Returns:
            Roadmap dictionary with migrations, phases, and summary
        """
        # Detect outdated technologies
        outdated_techs = self.detect_outdated_technologies(tech_stack)
        
        if not outdated_techs:
            return {
                "migrations": [],
                "phases": self.group_into_phases([]),
                "summary": {
                    "total_migrations": 0,
                    "total_effort_hours": 0,
                    "total_duration_months": 18
                }
            }
        
        # Build migration list
        migrations = []
        total_effort = 0
        
        for tech in outdated_techs:
            # Find migration path
            tech_name = tech.get("name", "")
            version = tech.get("version", "")
            tech_full = f"{tech_name} {version}".strip() if version else tech_name
            
            migration_path = self.find_migration_path(tech_name) or self.find_migration_path(tech_full)
            
            if not migration_path:
                # No migration path available
                migrations.append({
                    "technology": tech_name,
                    "from_version": version,
                    "to_version": "No path available",
                    "complexity": "UNKNOWN",
                    "effort_hours": 0,
                    "priority": 0,
                    "steps": [],
                    "blockers": []
                })
                continue
            
            # Calculate effort
            project_count = tech.get("project_count", 1)
            effort = self.calculate_effort(migration_path, project_count)
            total_effort += effort
            
            # Calculate priority
            priority = self.calculate_priority(tech, migration_path, project_count)
            
            # Build migration entry
            migrations.append({
                "technology": tech_name,
                "from_version": version or migration_path["from"],
                "to_version": migration_path["to"],
                "complexity": migration_path["complexity"],
                "effort_hours": effort,
                "priority": priority,
                "steps": migration_path.get("steps", []),
                "blockers": migration_path.get("blockers", []),
                "benefits": migration_path.get("benefits", [])
            })
        
        # Sort by priority (highest first)
        migrations.sort(key=lambda m: m["priority"], reverse=True)
        
        # Group into phases
        phases = self.group_into_phases(migrations)
        
        # Build summary
        summary = {
            "total_migrations": len(migrations),
            "total_effort_hours": total_effort,
            "total_duration_months": 18
        }
        
        return {
            "migrations": migrations,
            "phases": phases,
            "summary": summary
        }
