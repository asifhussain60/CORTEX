"""
TEST-006: No Database Files Tests.

Validates that no database files or SQLite dependencies remain.
All database-backed wiring should be replaced with Git-backed YAML.

Phase: 6 (Test Suite & Final Validation)
Author: Asif Hussain
Date: 2026-01-28

CORE-030: Docker-first architecture - no database files, only YAML.
"""

import ast
import sqlite3
from pathlib import Path

import pytest


class TestNoDatabaseFiles:
    """Verify that no database files or dependencies remain."""
    
    @pytest.fixture
    def cortex_root(self) -> Path:
        """Get CORTEX project root directory."""
        return Path(__file__).parent.parent.parent
    
    def test_no_db_files_in_repo(self, cortex_root: Path):
        """Test that no .db files exist in the repository."""
        # Search for .db files
        db_files = []
        for ext in ["*.db", "*.db-journal", "*.db-wal", "*.db-shm"]:
            db_files.extend(cortex_root.glob(f"**/{ext}"))
        
        # Filter out excluded directories
        excluded = {".venv", "node_modules", "__pycache__", ".git", ".tox"}
        db_files = [
            f for f in db_files
            if not any(exc in f.parts for exc in excluded)
        ]
        
        assert not db_files, (
            f"Found database files: {db_files}. "
            "All .db files should be deleted (Phase 2)."
        )
    
    def test_no_db_files_after_wiring(self, cortex_root: Path):
        """Test that importing cortex doesn't create database files."""
        # Get list of .db files before import
        db_before = set(cortex_root.glob("**/*.db"))
        
        # Import cortex
        try:
            import cortex
        except ImportError:
            pytest.skip("cortex module not importable")
        
        # Get list of .db files after import
        db_after = set(cortex_root.glob("**/*.db"))
        
        # Filter excluded directories
        excluded = {".venv", "node_modules", "__pycache__", ".git"}
        db_after = {
            f for f in db_after
            if not any(exc in f.parts for exc in excluded)
        }
        
        new_dbs = db_after - db_before
        
        assert not new_dbs, (
            f"Importing cortex created database files: {new_dbs}. "
            "Wiring should be YAML-based, not database-backed."
        )
    
    def test_no_sqlite_imports_in_wiring(self, cortex_root: Path):
        """Test that wiring-related files don't import sqlite3."""
        cortex_dir = cortex_root / "cortex"
        
        # Files to check (wiring, orchestrators, infrastructure)
        check_patterns = [
            "cortex/wiring/**/*.py",
            "cortex/orchestrators/**/*.py",
            "cortex/infrastructure/**/*.py",
        ]
        
        violations = []
        
        for pattern in check_patterns:
            for py_file in cortex_root.glob(pattern):
                if py_file.name.startswith("test_"):
                    continue  # Skip test files
                
                try:
                    content = py_file.read_text()
                    
                    # Check for sqlite3 imports
                    if "import sqlite3" in content or "from sqlite3" in content:
                        # Allow if it's a deprecated stub or comment
                        if "DEPRECATED" not in content and "backward compatibility" not in content:
                            violations.append((py_file, "sqlite3 import"))
                    
                    # Check for database_registry imports
                    if "database_registry" in content:
                        # Parse to see if it's in imports (not just comments)
                        try:
                            tree = ast.parse(content)
                            for node in ast.walk(tree):
                                if isinstance(node, ast.Import):
                                    for alias in node.names:
                                        if "database_registry" in alias.name:
                                            violations.append((py_file, f"import {alias.name}"))
                                elif isinstance(node, ast.ImportFrom):
                                    if node.module and "database_registry" in node.module:
                                        violations.append((py_file, f"from {node.module}"))
                        except SyntaxError:
                            pass  # Can't parse, skip
                
                except Exception:
                    pass  # Can't read file, skip
        
        assert not violations, (
            f"Found SQLite/database_registry imports in wiring files:\n"
            + "\n".join(f"  {file}: {reason}" for file, reason in violations)
        )
    
    def test_no_sqlite_usage_at_runtime(self):
        """Test that sqlite3 module is not used during normal operations."""
        # Check if sqlite3 has been imported
        import sys
        
        # Before importing cortex, sqlite3 should not be in sys.modules
        # (unless imported by other tests, so this is a soft check)
        sqlite_before = "sqlite3" in sys.modules
        
        # Import cortex
        try:
            import cortex
        except ImportError:
            pytest.skip("cortex module not importable")
        
        # Check again
        sqlite_after = "sqlite3" in sys.modules
        
        # If sqlite3 was imported by cortex (not by tests), that's a violation
        if not sqlite_before and sqlite_after:
            pytest.fail(
                "Importing cortex loaded sqlite3 module. "
                "Wiring should be YAML-based, not database-backed."
            )
    
    def test_wiring_is_file_based_only(self, cortex_root: Path):
        """Test that any wiring logic uses files, not databases."""
        cortex_dir = cortex_root / "cortex"
        
        # Look for wiring-related files
        wiring_files = []
        for pattern in ["**/wiring*.py", "**/bootstrap*.py", "**/registry*.py"]:
            wiring_files.extend(cortex_dir.glob(pattern))
        
        # Exclude test files and __pycache__
        wiring_files = [
            f for f in wiring_files
            if not f.name.startswith("test_")
            and "__pycache__" not in f.parts
        ]
        
        violations = []
        
        for wiring_file in wiring_files:
            try:
                content = wiring_file.read_text()
                
                # Check for database-related operations
                db_indicators = [
                    "CREATE TABLE",
                    "INSERT INTO",
                    "SELECT FROM",
                    "conn.execute",
                    "cursor.execute",
                    ".commit()",
                    "BEGIN TRANSACTION",
                ]
                
                for indicator in db_indicators:
                    if indicator.lower() in content.lower():
                        # Check if it's in a comment or docstring
                        lines = content.split("\n")
                        for i, line in enumerate(lines):
                            if indicator.lower() in line.lower():
                                # Skip if in comment
                                stripped = line.strip()
                                if not stripped.startswith("#") and not stripped.startswith('"""'):
                                    violations.append((wiring_file, f"Line {i+1}: {indicator}"))
                                    break
            
            except Exception:
                pass  # Can't read, skip
        
        assert not violations, (
            f"Found database operations in wiring files:\n"
            + "\n".join(f"  {file}: {reason}" for file, reason in violations)
        )
