"""Tests for pre-commit hooks (PHASE-DEPLOYMENT-001 AC-DEP-001-03).

This module tests the pre-commit integration for sanitization validation.
"""

import subprocess
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock, patch
import importlib.util

import pytest


@pytest.fixture
def temp_repo(tmp_path: Path) -> Generator[Path, None, None]:
    """Create a temporary git repository with pre-commit config.
    
    Args:
        tmp_path: Pytest temp path fixture.
        
    Yields:
        Path to the temporary repository.
    """
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    
    # Create pre-commit config
    precommit_config = repo_path / ".pre-commit-config.yaml"
    precommit_config.write_text("""
repos:
  - repo: local
    hooks:
      - id: cortex-sanitize-check
        name: CORTEX Sanitization Check
        entry: python scripts/deployment/validate_sanitization.py
        language: python
        always_run: true
""")
    
    # Create cortex_brain structure
    (repo_path / "cortex_brain" / "state").mkdir(parents=True)
    (repo_path / "cortex_brain" / "tier1" / "templates").mkdir(parents=True)
    (repo_path / "cortex_brain" / "tier2" / "templates").mkdir(parents=True)
    
    yield repo_path


@pytest.fixture
def precommit_module():
    """Import the pre-commit hook module.
    
    Returns:
        The validate_sanitization module.
    """
    module_path = Path(__file__).parent.parent.parent / "cortex" / "scripts-root-archive" / "deployment" / "validate_sanitization.py"
    spec = importlib.util.spec_from_file_location("validate_sanitization", module_path)
    validate_sanitization = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(validate_sanitization)
    return validate_sanitization


class TestPrecommitConfigValid:
    """Tests for pre-commit configuration validity."""
    
    def test_precommit_config_has_sanitize_hook(
        self, temp_repo: Path
    ) -> None:
        """Pre-commit config contains cortex-sanitize-check hook.
        
        Args:
            temp_repo: Path to temporary repository.
        """
        config_path = temp_repo / ".pre-commit-config.yaml"
        config_content = config_path.read_text()
        
        assert "cortex-sanitize-check" in config_content
        assert "validate_sanitization" in config_content
    
    def test_precommit_hook_always_runs(
        self, temp_repo: Path
    ) -> None:
        """Sanitization hook is set to always_run: true.
        
        Args:
            temp_repo: Path to temporary repository.
        """
        config_path = temp_repo / ".pre-commit-config.yaml"
        config_content = config_path.read_text()
        
        assert "always_run: true" in config_content


class TestPrecommitExitCodes:
    """Tests for pre-commit hook exit codes."""
    
    def test_precommit_exits_zero_on_clean(
        self, temp_repo: Path, precommit_module
    ) -> None:
        """Pre-commit hook exits 0 when sanitization passes.
        
        Args:
            temp_repo: Path to temporary repository.
            precommit_module: The validator module.
        """
        # Create clean state
        import sqlite3
        db_path = temp_repo / "cortex_brain" / "state" / "governance.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE audit_log (
                id INTEGER PRIMARY KEY,
                ac_id TEXT NOT NULL,
                is_production INTEGER DEFAULT 0
            )
        """)
        cursor.execute(
            "INSERT INTO audit_log (ac_id, is_production) VALUES (?, ?)",
            ("AC-CORE-001", 1)
        )
        conn.commit()
        conn.close()
        
        validator = precommit_module.SanitizationValidator(db_path)
        exit_code = validator.get_precommit_exit_code()
        
        assert exit_code == 0
    
    def test_precommit_exits_nonzero_on_dirty(
        self, temp_repo: Path, precommit_module
    ) -> None:
        """Pre-commit hook exits non-zero when sanitization fails.
        
        Args:
            temp_repo: Path to temporary repository.
            precommit_module: The validator module.
        """
        # Create dirty state
        import sqlite3
        db_path = temp_repo / "cortex_brain" / "state" / "governance.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE audit_log (
                id INTEGER PRIMARY KEY,
                ac_id TEXT NOT NULL,
                is_production INTEGER DEFAULT 0
            )
        """)
        cursor.execute(
            "INSERT INTO audit_log (ac_id, is_production) VALUES (?, ?)",
            ("TEST-DEV-001", 0)
        )
        conn.commit()
        conn.close()
        
        validator = precommit_module.SanitizationValidator(db_path)
        exit_code = validator.get_precommit_exit_code()
        
        assert exit_code != 0


class TestPrecommitIntegration:
    """Tests for full pre-commit integration."""
    
    def test_precommit_validates_full_repo(
        self, temp_repo: Path, precommit_module
    ) -> None:
        """Pre-commit validates governance.db, tier1, and tier2.
        
        Args:
            temp_repo: Path to temporary repository.
            precommit_module: The validator module.
        """
        import sqlite3
        
        # Setup governance.db (clean)
        db_path = temp_repo / "cortex_brain" / "state" / "governance.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE audit_log (
                id INTEGER PRIMARY KEY,
                ac_id TEXT NOT NULL,
                is_production INTEGER DEFAULT 0
            )
        """)
        conn.commit()
        conn.close()
        
        # Create tier templates
        tier1_template = temp_repo / "cortex_brain" / "tier1" / "templates" / "domain.yaml.template"
        tier1_template.write_text("# Domain template\nrules: []")
        
        tier2_template = temp_repo / "cortex_brain" / "tier2" / "templates" / "context.yaml.template"
        tier2_template.write_text("# Context template\nrules: []")
        
        validator = precommit_module.SanitizationValidator(
            db_path=db_path,
            tier1_path=temp_repo / "cortex_brain" / "tier1",
            tier2_path=temp_repo / "cortex_brain" / "tier2"
        )
        
        result = validator.validate_all()
        
        assert result.is_valid is True
        assert result.db_valid is True
        assert result.tier1_valid is True
        assert result.tier2_valid is True
