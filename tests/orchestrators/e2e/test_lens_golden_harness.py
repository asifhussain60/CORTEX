"""
CORTEX LENS Golden Test Harness - Extended Scenarios

Authority: AC-GOLDEN-LENS-001
Provides E2E validation for all CORTEX LENS capabilities with real file fixtures.

Features:
- Temp repository creation with realistic file structures
- LENS analyzer invocation and validation
- Audit trail verification
- Automatic cleanup
"""

import json
import shutil
import sqlite3
import subprocess
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

import pytest

from tests.orchestrators.e2e.test_golden_harness import (
    GoldenTestHarness,
    GoldenTestResult,
    ScenarioDefinition,
)


class TempRepoBuilder:
    """Builds temporary repository fixtures for LENS testing."""
    
    def __init__(self, base_path: Path):
        """
        Initialize temp repo builder.
        
        Args:
            base_path: Base directory for temp repos
        """
        self.base_path = base_path
        self.repos: List[Path] = []
    
    def create_repo(self, name: str, files: Dict[str, str]) -> Path:
        """
        Create temporary repository with files.
        
        Args:
            name: Repository name
            files: Dictionary mapping paths to content
        
        Returns:
            Path to created repository
        """
        repo_path = self.base_path / name
        repo_path.mkdir(parents=True, exist_ok=True)
        
        for file_path, content in files.items():
            full_path = repo_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)
        
        self.repos.append(repo_path)
        return repo_path
    
    def create_git_repo(self, name: str, files: Dict[str, str], commits: List[Dict[str, Any]]) -> Path:
        """
        Create temporary git repository with commit history.
        
        Args:
            name: Repository name
            files: Initial files
            commits: List of commit configurations
        
        Returns:
            Path to created git repository
        """
        repo_path = self.create_repo(name, files)
        
        # Initialize git
        subprocess.run(['git', 'init'], cwd=repo_path, check=True, capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'Test User'], cwd=repo_path, check=True)
        subprocess.run(['git', 'config', 'user.email', 'test@example.com'], cwd=repo_path, check=True)
        
        # Create commits
        for commit_config in commits:
            # Stage files
            for file in commit_config.get('files', []):
                subprocess.run(['git', 'add', file], cwd=repo_path, check=True)
            
            # Commit
            message = commit_config.get('message', 'Test commit')
            subprocess.run(['git', 'commit', '-m', message], cwd=repo_path, check=True, capture_output=True)
        
        return repo_path
    
    def cleanup(self):
        """Remove all created repositories."""
        for repo_path in self.repos:
            if repo_path.exists():
                shutil.rmtree(repo_path)
        self.repos.clear()


class LENSGoldenTestHarness(GoldenTestHarness):
    """Extended golden test harness for LENS scenarios."""
    
    def __init__(self, db_path: Optional[Path] = None, fixture_path: Optional[Path] = None):
        """
        Initialize LENS golden test harness.
        
        Args:
            db_path: Path to audit database
            fixture_path: Path to fixture base directory
        """
        super().__init__(db_path)
        
        if fixture_path is None:
            fixture_path = Path(__file__).parent / "fixtures" / "temp_repos"
        
        self.fixture_path = fixture_path
        self.fixture_path.mkdir(parents=True, exist_ok=True)
        self.repo_builder = TempRepoBuilder(self.fixture_path)
    
    def execute_lens_scenario(self, scenario_name: str) -> GoldenTestResult:
        """
        Execute LENS golden test scenario with file fixtures.
        
        Args:
            scenario_name: Scenario name (e.g., 'lens/core/golden_04_python_ast_analysis')
        
        Returns:
            GoldenTestResult
        """
        # Load scenario
        scenario = self.load_scenario(scenario_name)
        
        # Create temp repository with files
        temp_files = self._parse_temp_files(scenario)
        repo_path = self.repo_builder.create_repo(
            name=scenario.name,
            files=temp_files
        )
        
        # Handle git-specific scenarios
        if hasattr(scenario, 'git_setup') and scenario.git_setup:
            repo_path = self.repo_builder.create_git_repo(
                name=scenario.name,
                files=temp_files,
                commits=scenario.git_setup.get('commits', [])
            )
        
        # Execute LENS analysis (via orchestrator - to be wired)
        # TODO: Wire to LENSOrchestrator in Phase 2
        execution_completed = False  # Stub for now
        correlation_id = None
        
        # Capture audit events
        actual_events = self._get_audit_events(correlation_id)
        
        # Validate expectations
        diffs = self._compare_audit_events(scenario.expected_audit_events, actual_events)
        
        passed = execution_completed and len(diffs) == 0
        
        return GoldenTestResult(
            scenario_name=scenario_name,
            passed=passed,
            execution_completed=execution_completed,
            audit_events_matched=len(diffs) == 0,
            diffs=diffs,
            actual_events=actual_events
        )
    
    def _parse_temp_files(self, scenario: ScenarioDefinition) -> Dict[str, str]:
        """
        Parse temp_files from scenario definition.
        
        Args:
            scenario: Scenario definition
        
        Returns:
            Dictionary mapping file paths to content
        """
        temp_files = {}
        
        # Check if scenario has temp_files attribute
        if hasattr(scenario, 'temp_files'):
            for file_config in scenario.temp_files:
                path = file_config.get('path')
                content = file_config.get('content', '')
                if path:
                    temp_files[path] = content
        
        return temp_files
    
    def cleanup(self):
        """Clean up all temporary repositories."""
        self.repo_builder.cleanup()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        self.cleanup()


# Pytest fixtures for LENS golden tests

@pytest.fixture
def lens_harness(tmp_path: Path) -> LENSGoldenTestHarness:
    """
    Create LENS golden test harness with temp database.
    
    Args:
        tmp_path: Pytest temp path
    
    Returns:
        LENSGoldenTestHarness instance
    """
    db_path = tmp_path / "audit.db"
    
    # Apply schema
    schema_path = Path(__file__).parent.parent.parent.parent / "cortex" / "intelligence" / "audit" / "schema.sql"
    
    conn = sqlite3.connect(str(db_path))
    with open(schema_path, 'r') as f:
        conn.executescript(f.read())
    conn.close()
    
    fixture_path = tmp_path / "fixtures"
    harness = LENSGoldenTestHarness(db_path=db_path, fixture_path=fixture_path)
    
    yield harness
    
    # Cleanup
    harness.cleanup()


@pytest.fixture
def temp_repo_builder(tmp_path: Path) -> TempRepoBuilder:
    """
    Create temp repository builder.
    
    Args:
        tmp_path: Pytest temp path
    
    Returns:
        TempRepoBuilder instance
    """
    builder = TempRepoBuilder(tmp_path / "repos")
    
    yield builder
    
    # Cleanup
    builder.cleanup()
