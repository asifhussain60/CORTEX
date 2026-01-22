"""Tests for sanitization validation (PHASE-DEPLOYMENT-001 AC-DEP-001-03).

This module tests the pre-commit hook validation that prevents
unsanitized commits to the main branch.
"""

import importlib.util
import sqlite3
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def temp_db_clean(tmp_path: Path) -> Generator[Path, None, None]:
    """Create a clean (sanitized) governance.db.
    
    Args:
        tmp_path: Pytest temp path fixture.
        
    Yields:
        Path to the temporary database.
    """
    db_path = tmp_path / "governance.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE audit_log (
            id INTEGER PRIMARY KEY,
            ac_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            operation TEXT NOT NULL,
            source TEXT,
            is_production INTEGER DEFAULT 0
        )
    """)
    
    # Only production entries - clean state
    cursor.execute(
        "INSERT INTO audit_log (ac_id, timestamp, operation, source, is_production) VALUES (?, ?, ?, ?, ?)",
        ("AC-CORE-001", "2026-01-15T10:00:00Z", "ENFORCE", "production", 1)
    )
    
    conn.commit()
    conn.close()
    
    yield db_path


@pytest.fixture
def temp_db_dirty(tmp_path: Path) -> Generator[Path, None, None]:
    """Create a dirty (unsanitized) governance.db.
    
    Args:
        tmp_path: Pytest temp path fixture.
        
    Yields:
        Path to the temporary database.
    """
    db_path = tmp_path / "governance.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE audit_log (
            id INTEGER PRIMARY KEY,
            ac_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            operation TEXT NOT NULL,
            source TEXT,
            is_production INTEGER DEFAULT 0
        )
    """)
    
    # Mix of dev and production entries - dirty state
    test_entries = [
        ("TEST-001", "2026-01-01T10:00:00Z", "VALIDATE", "dev", 0),
        ("AC-CORE-001", "2026-01-15T10:00:00Z", "ENFORCE", "production", 1),
    ]
    cursor.executemany(
        "INSERT INTO audit_log (ac_id, timestamp, operation, source, is_production) VALUES (?, ?, ?, ?, ?)",
        test_entries
    )
    
    conn.commit()
    conn.close()
    
    yield db_path


@pytest.fixture
def validator_module():
    """Import the validator module using dynamic loading.
    
    Returns:
        The validate_sanitization module.
    """
    module_path = Path(__file__).parent.parent.parent / "cortex" / "scripts-root-archive" / "deployment" / "validate_sanitization.py"
    spec = importlib.util.spec_from_file_location("validate_sanitization", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestPrecommitBlocksDevEntries:
    """Tests for pre-commit blocking unsanitized commits."""
    
    def test_precommit_blocks_dev_entries(
        self, temp_db_dirty: Path, validator_module
    ) -> None:
        """Pre-commit hook blocks when dev entries found in governance.db.
        
        Args:
            temp_db_dirty: Path to dirty database.
            validator_module: The validator module.
        """
        validator = validator_module.SanitizationValidator(temp_db_dirty)
        result = validator.validate()
        
        assert result.is_valid is False
        assert "dev" in result.reason.lower() or "test" in result.reason.lower()
    
    def test_precommit_passes_clean_db(
        self, temp_db_clean: Path, validator_module
    ) -> None:
        """Pre-commit hook passes when governance.db is clean.
        
        Args:
            temp_db_clean: Path to clean database.
            validator_module: The validator module.
        """
        validator = validator_module.SanitizationValidator(temp_db_clean)
        result = validator.validate()
        
        assert result.is_valid is True


class TestPrecommitBlocksNonTemplateRules:
    """Tests for blocking non-template tier1/tier2 rules."""
    
    def test_precommit_blocks_custom_tier1_rules(
        self, tmp_path: Path, validator_module
    ) -> None:
        """Pre-commit blocks custom tier1 rules (non-template).
        
        Args:
            tmp_path: Pytest temp path fixture.
            validator_module: The validator module.
        """
        # Create tier1 directory with custom rule
        tier1_path = tmp_path / "cortex_brain" / "tier1"
        tier1_path.mkdir(parents=True)
        
        custom_rule = tier1_path / "my-custom-rules.yaml"
        custom_rule.write_text("# Custom rules - should be blocked\nrules: []")
        
        # Create empty templates dir
        templates_path = tier1_path / "templates"
        templates_path.mkdir()
        
        validator = validator_module.SanitizationValidator(
            db_path=tmp_path / "governance.db",
            tier1_path=tier1_path
        )
        result = validator.validate_tier_rules()
        
        assert result.is_valid is False
        assert "template" in result.reason.lower() or "custom" in result.reason.lower()
    
    def test_precommit_allows_template_only(
        self, tmp_path: Path, validator_module
    ) -> None:
        """Pre-commit passes when only templates exist in tier1.
        
        Args:
            tmp_path: Pytest temp path fixture.
            validator_module: The validator module.
        """
        # Create tier1 templates only
        tier1_path = tmp_path / "cortex_brain" / "tier1"
        templates_path = tier1_path / "templates"
        templates_path.mkdir(parents=True)
        
        template = templates_path / "domain-rules.yaml.template"
        template.write_text("# Template - allowed\nrules: []")
        
        validator = validator_module.SanitizationValidator(
            db_path=tmp_path / "governance.db",
            tier1_path=tier1_path
        )
        result = validator.validate_tier_rules()
        
        assert result.is_valid is True


class TestReleaseTagTriggersSanitization:
    """Tests for release tag automation."""
    
    def test_release_tag_triggers_sanitization(
        self, tmp_path: Path, validator_module
    ) -> None:
        """Release tag (v1.0.0) triggers automatic sanitization.
        
        Args:
            tmp_path: Pytest temp path fixture.
            validator_module: The validator module.
        """
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="v1.0.0"
            )
            
            validator = validator_module.SanitizationValidator(
                db_path=tmp_path / "governance.db"
            )
            should_sanitize = validator.check_release_tag("v1.0.0")
            
            assert should_sanitize is True
    
    def test_non_release_tag_skips_sanitization(
        self, tmp_path: Path, validator_module
    ) -> None:
        """Non-release tags (dev-snapshot) skip sanitization.
        
        Args:
            tmp_path: Pytest temp path fixture.
            validator_module: The validator module.
        """
        validator = validator_module.SanitizationValidator(
            db_path=tmp_path / "governance.db"
        )
        should_sanitize = validator.check_release_tag("dev-snapshot-20260121")
        
        assert should_sanitize is False
