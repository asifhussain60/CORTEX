"""
Tests for Planning Migration CLI - TDD RED Phase

Tests command-line interface for planning artifacts migration.

Author: GitHub Copilot
Created: 2025-12-14
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
import sys

from src.workflows.planning_migration_cli import (
    PlanningMigrationCLI,
    main
)
from src.workflows.planning_migration_engine import MigrationStatus


@pytest.fixture
def cli(tmp_path):
    """Fixture for PlanningMigrationCLI with temp directories."""
    source_dir = tmp_path / "source"
    target_dir = tmp_path / "target"
    source_dir.mkdir()
    target_dir.mkdir()
    
    return PlanningMigrationCLI(
        source_directory=source_dir,
        target_directory=target_dir
    )


@pytest.fixture
def sample_plans(tmp_path):
    """Create sample plans for CLI testing."""
    plans_dir = tmp_path / "plans"
    plans_dir.mkdir()
    
    # Master plan
    (plans_dir / "PLAN-2025-12-14-master-plan-feature.yaml").write_text("""
plan_id: "PLAN-2025-12-14-feature"
title: "Feature Implementation"
status: "active"
""")
    
    return plans_dir


class TestCLIInit:
    """Test CLI initialization."""
    
    def test_cli_initialization(self, cli):
        """Test CLI can be initialized."""
        assert cli is not None
        assert cli.engine is not None
    
    def test_cli_validates_directories(self, tmp_path):
        """Test CLI validates directory paths."""
        nonexistent = tmp_path / "nonexistent"
        
        with pytest.raises(ValueError):
            PlanningMigrationCLI(
                source_directory=nonexistent,
                target_directory=tmp_path
            )


class TestDiscoverCommand:
    """Test discover command."""
    
    def test_discover_shows_plan_count(self, cli, sample_plans, capsys):
        """Test discover command shows plan count."""
        cli.engine.source_directory = sample_plans
        
        cli.cmd_discover()
        
        captured = capsys.readouterr()
        assert "Discovered" in captured.out
        assert "master plan" in captured.out.lower()
    
    def test_discover_shows_details(self, cli, sample_plans, capsys):
        """Test discover command shows plan details."""
        cli.engine.source_directory = sample_plans
        
        cli.cmd_discover(verbose=True)
        
        captured = capsys.readouterr()
        assert "PLAN-2025-12-14-feature" in captured.out


class TestMigrateCommand:
    """Test migrate command."""
    
    def test_migrate_single_plan(self, cli, sample_plans, capsys):
        """Test migrating single plan."""
        cli.engine.source_directory = sample_plans
        
        cli.cmd_migrate(plan_id="PLAN-2025-12-14-feature")
        
        captured = capsys.readouterr()
        assert "SUCCESS" in captured.out or "success" in captured.out.lower()
    
    def test_migrate_all_plans(self, cli, sample_plans, capsys):
        """Test migrating all plans."""
        cli.engine.source_directory = sample_plans
        
        cli.cmd_migrate_all()
        
        captured = capsys.readouterr()
        assert "migrat" in captured.out.lower()
    
    def test_migrate_with_dry_run(self, cli, sample_plans, capsys):
        """Test migrate with dry-run flag."""
        cli.engine.source_directory = sample_plans
        
        cli.cmd_migrate(plan_id="PLAN-2025-12-14-feature", dry_run=True)
        
        captured = capsys.readouterr()
        assert "DRY RUN" in captured.out or "dry run" in captured.out.lower()


class TestRollbackCommand:
    """Test rollback command."""
    
    def test_rollback_single_plan(self, cli, sample_plans, capsys):
        """Test rolling back single plan."""
        cli.engine.source_directory = sample_plans
        
        # First migrate
        cli.cmd_migrate(plan_id="PLAN-2025-12-14-feature")
        
        # Then rollback
        cli.cmd_rollback(plan_id="PLAN-2025-12-14-feature")
        
        captured = capsys.readouterr()
        assert "rolling back" in captured.out.lower() or "success" in captured.out.lower()
    
    def test_rollback_all(self, cli, sample_plans, capsys):
        """Test rolling back all migrations."""
        cli.engine.source_directory = sample_plans
        
        # First migrate
        cli.cmd_migrate_all()
        
        # Then rollback
        cli.cmd_rollback_all()
        
        captured = capsys.readouterr()
        assert "rolling back" in captured.out.lower() or "rolled back" in captured.out.lower()


class TestStatusCommand:
    """Test status command."""
    
    def test_status_shows_migration_state(self, cli, sample_plans, capsys):
        """Test status command shows migration state."""
        cli.engine.source_directory = sample_plans
        
        cli.cmd_status()
        
        captured = capsys.readouterr()
        assert "Migration Status" in captured.out or "status" in captured.out.lower()
    
    def test_status_shows_migrated_plans(self, cli, sample_plans, capsys):
        """Test status shows migrated plans."""
        cli.engine.source_directory = sample_plans
        
        # Migrate first
        cli.cmd_migrate(plan_id="PLAN-2025-12-14-feature")
        
        # Check status
        cli.cmd_status()
        
        captured = capsys.readouterr()
        assert "PLAN-2025-12-14-feature" in captured.out


class TestValidateCommand:
    """Test validate command."""
    
    def test_validate_single_plan(self, cli, sample_plans, capsys):
        """Test validating single plan."""
        cli.engine.source_directory = sample_plans
        
        # Migrate first
        cli.cmd_migrate(plan_id="PLAN-2025-12-14-feature")
        
        # Validate
        cli.cmd_validate(plan_id="PLAN-2025-12-14-feature")
        
        captured = capsys.readouterr()
        assert "valid" in captured.out.lower()
    
    def test_validate_all(self, cli, sample_plans, capsys):
        """Test validating all migrations."""
        cli.engine.source_directory = sample_plans
        
        # Migrate first
        cli.cmd_migrate_all()
        
        # Validate
        cli.cmd_validate_all()
        
        captured = capsys.readouterr()
        assert "validat" in captured.out.lower()


class TestListCommand:
    """Test list command."""
    
    def test_list_shows_migrated_plans(self, cli, sample_plans, capsys):
        """Test list command shows migrated plans."""
        cli.engine.source_directory = sample_plans
        
        # Migrate first
        cli.cmd_migrate(plan_id="PLAN-2025-12-14-feature")
        
        # List
        cli.cmd_list()
        
        captured = capsys.readouterr()
        assert "PLAN-2025-12-14-feature" in captured.out
    
    def test_list_shows_empty_when_no_migrations(self, cli, capsys):
        """Test list shows message when no migrations."""
        cli.cmd_list()
        
        captured = capsys.readouterr()
        assert "No migrated plans" in captured.out or "0" in captured.out


class TestMainFunction:
    """Test main CLI entry point."""
    
    def test_main_with_discover(self, tmp_path, monkeypatch, capsys):
        """Test main function with discover command."""
        source = tmp_path / "source"
        target = tmp_path / "target"
        source.mkdir()
        target.mkdir()
        
        # Create test plan
        (source / "PLAN-2025-12-14-master-plan-test.yaml").write_text("plan_id: test")
        
        # Mock sys.argv
        test_args = [
            "planning_migration_cli.py",
            "discover",
            "--source", str(source),
            "--target", str(target)
        ]
        monkeypatch.setattr(sys, "argv", test_args)
        
        # Run main
        try:
            main()
        except SystemExit:
            pass  # main() may call sys.exit()
        
        captured = capsys.readouterr()
        assert "Discovered" in captured.out or "discover" in captured.out.lower()
    
    def test_main_with_migrate(self, tmp_path, monkeypatch, capsys):
        """Test main function with migrate command."""
        source = tmp_path / "source"
        target = tmp_path / "target"
        source.mkdir()
        target.mkdir()
        
        # Create test plan
        (source / "PLAN-2025-12-14-master-plan-test.yaml").write_text("""
plan_id: "PLAN-2025-12-14-test"
title: "Test"
""")
        
        # Mock sys.argv
        test_args = [
            "planning_migration_cli.py",
            "migrate",
            "--source", str(source),
            "--target", str(target),
            "--plan-id", "PLAN-2025-12-14-test"
        ]
        monkeypatch.setattr(sys, "argv", test_args)
        
        # Run main
        try:
            main()
        except SystemExit:
            pass
        
        captured = capsys.readouterr()
        assert "migrat" in captured.out.lower()


class TestCLIHelpers:
    """Test CLI helper methods."""
    
    def test_format_discovery_output(self, cli, sample_plans):
        """Test formatting discovery output."""
        cli.engine.source_directory = sample_plans
        discovery = cli.engine.discover_plans()
        
        output = cli._format_discovery(discovery)
        
        assert isinstance(output, str)
        assert "master plan" in output.lower()
    
    def test_format_migration_result(self, cli):
        """Test formatting migration result."""
        from src.workflows.planning_migration_engine import MigrationResult
        
        result = MigrationResult(
            plan_id="test",
            status=MigrationStatus.SUCCESS,
            message="Success",
            files_migrated=5
        )
        
        output = cli._format_result(result)
        
        assert isinstance(output, str)
        assert "SUCCESS" in output or "success" in output.lower()
        assert "5" in output


class TestCLIErrorHandling:
    """Test CLI error handling."""
    
    def test_handles_nonexistent_plan(self, cli, capsys):
        """Test handling of nonexistent plan."""
        cli.cmd_migrate(plan_id="nonexistent-plan")
        
        captured = capsys.readouterr()
        assert "not found" in captured.out.lower() or "failed" in captured.out.lower()
    
    def test_handles_invalid_source_dir(self, tmp_path, capsys):
        """Test handling of invalid source directory."""
        target = tmp_path / "target"
        target.mkdir()
        
        try:
            cli = PlanningMigrationCLI(
                source_directory=tmp_path / "nonexistent",
                target_directory=target
            )
            assert False, "Should raise ValueError"
        except ValueError as e:
            assert "does not exist" in str(e).lower()


class TestCLIInteractive:
    """Test interactive CLI features."""
    
    def test_confirm_prompt_yes(self, cli, monkeypatch):
        """Test confirmation prompt with yes."""
        monkeypatch.setattr('builtins.input', lambda _: 'y')
        
        result = cli._confirm("Proceed?")
        
        assert result is True
    
    def test_confirm_prompt_no(self, cli, monkeypatch):
        """Test confirmation prompt with no."""
        monkeypatch.setattr('builtins.input', lambda _: 'n')
        
        result = cli._confirm("Proceed?")
        
        assert result is False
