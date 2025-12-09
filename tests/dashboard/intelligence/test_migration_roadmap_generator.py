"""
Phase 9.1: Migration Roadmap Generator Tests

RED phase: TDD for migration roadmap generation system that detects outdated
technologies and generates prioritized, phased migration plans.
"""

import pytest
from src.dashboard.intelligence.migration_roadmap_generator import MigrationRoadmapGenerator


class TestMigrationMatrixLoading:
    """Test loading and parsing migration_path_matrix.yaml."""

    def test_load_migration_matrix(self):
        """Should load migration paths from YAML file."""
        generator = MigrationRoadmapGenerator()
        matrix = generator.load_migration_matrix()
        
        assert "migrations" in matrix
        assert len(matrix["migrations"]) > 0
        assert "priority_weights" in matrix

    def test_migration_entry_structure(self):
        """Migration entries should have required fields."""
        generator = MigrationRoadmapGenerator()
        matrix = generator.load_migration_matrix()
        
        first_migration = matrix["migrations"][0]
        assert "from" in first_migration
        assert "to" in first_migration
        assert "complexity" in first_migration
        assert "effort_per_project" in first_migration
        assert "steps" in first_migration

    def test_find_migration_path_for_dotnet_framework(self):
        """Should find migration path for .NET Framework 4.8."""
        generator = MigrationRoadmapGenerator()
        
        path = generator.find_migration_path(".NET Framework 4.8")
        
        assert path is not None
        assert path["from"] == ".NET Framework 4.8"
        assert path["to"] == ".NET 8"
        assert path["complexity"] == "HIGH"
        assert path["effort_per_project"] == 40

    def test_find_migration_path_case_insensitive(self):
        """Should match technology names case-insensitively."""
        generator = MigrationRoadmapGenerator()
        
        path = generator.find_migration_path(".net framework 4.8")
        
        assert path is not None
        assert path["from"] == ".NET Framework 4.8"

    def test_find_migration_path_returns_none_for_unknown(self):
        """Should return None for technologies without migration path."""
        generator = MigrationRoadmapGenerator()
        
        path = generator.find_migration_path("Unknown Framework 1.0")
        
        assert path is None


class TestOutdatedTechnologyDetection:
    """Test detecting outdated technologies from tech stack."""

    def test_detect_outdated_technologies(self):
        """Should identify outdated technologies."""
        tech_stack = {
            "backend": [
                {"name": ".NET Framework", "version": "4.8", "status": "outdated"},
                {"name": ".NET", "version": "8", "status": "current"}
            ]
        }
        
        generator = MigrationRoadmapGenerator()
        outdated = generator.detect_outdated_technologies(tech_stack)
        
        assert len(outdated) == 1
        assert outdated[0]["name"] == ".NET Framework"

    def test_detect_by_status_field(self):
        """Should detect using status field."""
        tech_stack = {
            "backend": [
                {"name": "log4net", "version": "2.0", "status": "outdated"},
                {"name": "Serilog", "version": "3.0", "status": "current"}
            ]
        }
        
        generator = MigrationRoadmapGenerator()
        outdated = generator.detect_outdated_technologies(tech_stack)
        
        assert len(outdated) == 1
        assert outdated[0]["name"] == "log4net"

    def test_detect_by_risk_score(self):
        """Should detect using high risk score (>60)."""
        tech_stack = {
            "backend": [
                {"name": ".NET Framework", "version": "4.7.2", "risk_score": 75},
                {"name": ".NET", "version": "8", "risk_score": 15}
            ]
        }
        
        generator = MigrationRoadmapGenerator()
        outdated = generator.detect_outdated_technologies(tech_stack)
        
        assert len(outdated) == 1
        assert outdated[0]["risk_score"] == 75

    def test_detect_handles_empty_stack(self):
        """Should handle empty tech stack gracefully."""
        generator = MigrationRoadmapGenerator()
        outdated = generator.detect_outdated_technologies({"backend": []})
        
        assert outdated == []


class TestEffortEstimation:
    """Test effort estimation for migrations."""

    def test_calculate_base_effort(self):
        """Should calculate effort: projects × effort_per_project."""
        migration_path = {
            "from": ".NET Framework 4.8",
            "to": ".NET 8",
            "effort_per_project": 40
        }
        
        generator = MigrationRoadmapGenerator()
        effort = generator.calculate_effort(
            migration_path=migration_path,
            project_count=5
        )
        
        assert effort == 200  # 5 × 40

    def test_calculate_effort_with_size_multiplier(self):
        """Should apply project size multiplier."""
        migration_path = {"effort_per_project": 40}
        
        generator = MigrationRoadmapGenerator()
        
        # Large project (1.5x)
        effort = generator.calculate_effort(
            migration_path=migration_path,
            project_count=1,
            project_size="large"
        )
        
        assert effort == 60  # 40 × 1.5

    def test_calculate_effort_with_test_coverage_multiplier(self):
        """Should apply test coverage multiplier."""
        migration_path = {"effort_per_project": 40}
        
        generator = MigrationRoadmapGenerator()
        
        # Low test coverage (1.3x)
        effort = generator.calculate_effort(
            migration_path=migration_path,
            project_count=1,
            test_coverage="low"
        )
        
        assert effort == 52  # 40 × 1.3

    def test_calculate_effort_with_team_experience_multiplier(self):
        """Should apply team experience multiplier."""
        migration_path = {"effort_per_project": 40}
        
        generator = MigrationRoadmapGenerator()
        
        # Expert team (0.7x)
        effort = generator.calculate_effort(
            migration_path=migration_path,
            project_count=1,
            team_experience="expert"
        )
        
        assert effort == 28  # 40 × 0.7

    def test_calculate_effort_with_all_multipliers(self):
        """Should apply all multipliers together."""
        migration_path = {"effort_per_project": 40}
        
        generator = MigrationRoadmapGenerator()
        effort = generator.calculate_effort(
            migration_path=migration_path,
            project_count=3,
            project_size="large",  # 1.5x
            test_coverage="low",  # 1.3x
            team_experience="beginner"  # 1.5x
        )
        
        # 40 × 3 × 1.5 × 1.3 × 1.5 = 351
        assert effort == 351


class TestPriorityCalculation:
    """Test priority calculation for sorting migrations."""

    def test_calculate_priority_score(self):
        """Should calculate weighted priority score."""
        tech = {
            "risk_score": 80,  # High risk
            "project_count": 10,  # Many projects
            "months_to_eol": 6  # EOL soon
        }
        migration_path = {"effort_per_project": 40}
        
        generator = MigrationRoadmapGenerator()
        priority = generator.calculate_priority(tech, migration_path, project_count=10)
        
        # Priority should be high (risk + project count + EOL urgency - effort)
        assert priority > 50

    def test_priority_weights_configuration(self):
        """Should use configured priority weights."""
        generator = MigrationRoadmapGenerator()
        weights = generator.get_priority_weights()
        
        assert "risk_score" in weights
        assert "project_count" in weights
        assert "effort" in weights
        assert "eol_urgency" in weights
        
        # Should sum to 1.0
        total = sum(weights.values())
        assert abs(total - 1.0) < 0.01

    def test_higher_risk_increases_priority(self):
        """Higher risk score should increase priority."""
        generator = MigrationRoadmapGenerator()
        migration_path = {"effort_per_project": 20}
        
        priority_low_risk = generator.calculate_priority(
            {"risk_score": 20, "months_to_eol": None},
            migration_path,
            project_count=5
        )
        
        priority_high_risk = generator.calculate_priority(
            {"risk_score": 90, "months_to_eol": None},
            migration_path,
            project_count=5
        )
        
        assert priority_high_risk > priority_low_risk

    def test_lower_effort_increases_priority(self):
        """Lower effort should increase priority (inverted)."""
        generator = MigrationRoadmapGenerator()
        tech = {"risk_score": 50, "months_to_eol": None}
        
        priority_high_effort = generator.calculate_priority(
            tech,
            {"effort_per_project": 50},
            project_count=5
        )
        
        priority_low_effort = generator.calculate_priority(
            tech,
            {"effort_per_project": 5},
            project_count=5
        )
        
        assert priority_low_effort > priority_high_effort


class TestPhasingAlgorithm:
    """Test grouping migrations into phases."""

    def test_group_migrations_into_phases(self):
        """Should group migrations into 3 phases by priority."""
        migrations = [
            {"technology": "Tech A", "priority": 90, "effort": 40},
            {"technology": "Tech B", "priority": 60, "effort": 20},
            {"technology": "Tech C", "priority": 30, "effort": 10}
        ]
        
        generator = MigrationRoadmapGenerator()
        phases = generator.group_into_phases(migrations)
        
        assert len(phases) == 3
        assert phases[0]["name"] == "Phase 1"
        assert phases[1]["name"] == "Phase 2"
        assert phases[2]["name"] == "Phase 3"

    def test_phase_1_contains_highest_priority(self):
        """Phase 1 should contain highest priority migrations."""
        migrations = [
            {"technology": "Critical", "priority": 95, "effort": 40},
            {"technology": "Medium", "priority": 50, "effort": 20},
            {"technology": "Low", "priority": 20, "effort": 10}
        ]
        
        generator = MigrationRoadmapGenerator()
        phases = generator.group_into_phases(migrations)
        
        phase_1_techs = [m["technology"] for m in phases[0]["migrations"]]
        assert "Critical" in phase_1_techs

    def test_phases_have_duration_estimates(self):
        """Phases should have duration in months."""
        migrations = [
            {"technology": "Tech A", "priority": 90, "effort": 100}
        ]
        
        generator = MigrationRoadmapGenerator()
        phases = generator.group_into_phases(migrations)
        
        assert "duration_months" in phases[0]
        assert phases[0]["duration_months"] > 0

    def test_phases_have_total_effort(self):
        """Phases should sum effort hours."""
        migrations = [
            {"technology": "Tech A", "priority": 90, "effort": 40},
            {"technology": "Tech B", "priority": 85, "effort": 30}
        ]
        
        generator = MigrationRoadmapGenerator()
        phases = generator.group_into_phases(migrations)
        
        assert "total_effort_hours" in phases[0]


class TestRoadmapGeneration:
    """Test complete roadmap generation."""

    def test_generate_roadmap_from_tech_stack(self):
        """Should generate complete migration roadmap."""
        tech_stack = {
            "backend": [
                {
                    "name": ".NET Framework",
                    "version": "4.8",
                    "status": "outdated",
                    "risk_score": 75,
                    "project_count": 5
                },
                {
                    "name": "log4net",
                    "version": "2.0",
                    "status": "outdated",
                    "risk_score": 50,
                    "project_count": 3
                }
            ]
        }
        
        generator = MigrationRoadmapGenerator()
        roadmap = generator.generate_roadmap(tech_stack)
        
        assert "migrations" in roadmap
        assert "phases" in roadmap
        assert "summary" in roadmap
        assert len(roadmap["migrations"]) == 2

    def test_roadmap_migrations_sorted_by_priority(self):
        """Migrations should be sorted by priority (high to low)."""
        tech_stack = {
            "backend": [
                {"name": ".NET Framework", "version": "4.8", "status": "outdated", "risk_score": 90},
                {"name": "log4net", "version": "2.0", "status": "outdated", "risk_score": 40}
            ]
        }
        
        generator = MigrationRoadmapGenerator()
        roadmap = generator.generate_roadmap(tech_stack)
        
        priorities = [m["priority"] for m in roadmap["migrations"]]
        assert priorities == sorted(priorities, reverse=True)

    def test_roadmap_includes_migration_details(self):
        """Each migration should include complete details."""
        tech_stack = {
            "backend": [
                {"name": ".NET Framework", "version": "4.8", "status": "outdated", "risk_score": 75}
            ]
        }
        
        generator = MigrationRoadmapGenerator()
        roadmap = generator.generate_roadmap(tech_stack)
        
        migration = roadmap["migrations"][0]
        assert "technology" in migration
        assert "from_version" in migration
        assert "to_version" in migration
        assert "complexity" in migration
        assert "effort_hours" in migration
        assert "priority" in migration
        assert "steps" in migration
        assert "blockers" in migration

    def test_roadmap_summary_statistics(self):
        """Summary should contain aggregate statistics."""
        tech_stack = {
            "backend": [
                {"name": ".NET Framework", "version": "4.8", "status": "outdated"},
                {"name": "log4net", "version": "2.0", "status": "outdated"}
            ]
        }
        
        generator = MigrationRoadmapGenerator()
        roadmap = generator.generate_roadmap(tech_stack)
        
        summary = roadmap["summary"]
        assert "total_migrations" in summary
        assert "total_effort_hours" in summary
        assert "total_duration_months" in summary
        assert summary["total_migrations"] == 2

    def test_generate_roadmap_handles_no_outdated_techs(self):
        """Should handle tech stack with no outdated technologies."""
        tech_stack = {
            "backend": [
                {"name": ".NET", "version": "8", "status": "current"}
            ]
        }
        
        generator = MigrationRoadmapGenerator()
        roadmap = generator.generate_roadmap(tech_stack)
        
        assert roadmap["migrations"] == []
        assert roadmap["summary"]["total_migrations"] == 0


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_handles_technology_without_migration_path(self):
        """Should skip technologies without defined migration path."""
        tech_stack = {
            "backend": [
                {"name": "CustomFramework", "version": "1.0", "status": "outdated"}
            ]
        }
        
        generator = MigrationRoadmapGenerator()
        roadmap = generator.generate_roadmap(tech_stack)
        
        # Should skip or mark as "no path available"
        assert len(roadmap["migrations"]) == 0 or roadmap["migrations"][0]["to_version"] == "No path available"

    def test_handles_missing_project_count(self):
        """Should use default project count when missing."""
        tech_stack = {
            "backend": [
                {"name": ".NET Framework", "version": "4.8", "status": "outdated"}
                # No project_count field
            ]
        }
        
        generator = MigrationRoadmapGenerator()
        roadmap = generator.generate_roadmap(tech_stack)
        
        assert len(roadmap["migrations"]) > 0
        assert roadmap["migrations"][0]["effort_hours"] > 0

    def test_handles_missing_risk_score(self):
        """Should use default risk score when missing."""
        tech_stack = {
            "backend": [
                {"name": ".NET Framework", "version": "4.8", "status": "outdated"}
                # No risk_score field
            ]
        }
        
        generator = MigrationRoadmapGenerator()
        roadmap = generator.generate_roadmap(tech_stack)
        
        assert len(roadmap["migrations"]) > 0
        assert "priority" in roadmap["migrations"][0]

    def test_handles_empty_tech_stack(self):
        """Should handle empty tech stack gracefully."""
        generator = MigrationRoadmapGenerator()
        roadmap = generator.generate_roadmap({"backend": [], "frontend": []})
        
        assert roadmap["migrations"] == []
        assert roadmap["summary"]["total_migrations"] == 0
