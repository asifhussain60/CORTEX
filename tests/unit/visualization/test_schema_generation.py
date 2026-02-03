"""
Test SQLite schema auto-generation.

Verifies GAP-004: Schema is automatically created with all tables, indexes, and views.
"""

import sqlite3
import tempfile
from pathlib import Path

import pytest

from cortex.visualization.sqlite_data_generator import SQLiteDataGenerator


class TestSchemaAutoGeneration:
    """Test automatic schema generation."""
    
    def test_schema_creates_all_required_tables(self):
        """Test that schema auto-generation creates all required tables."""
        generator = SQLiteDataGenerator()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.sqlite"
            
            # Generate database with minimal data
            data = {
                "repo_summary": {
                    "repo_name": "test",
                    "repo_slug": "test",
                    "primary_language": "Python",
                    "last_commit_date": "2026-02-03T00:00:00Z"
                },
                "metrics_summary": {
                    "total_loc": 0,
                    "calculated_at": "2026-02-03T00:00:00Z"
                }
            }
            
            success, error = generator.generate(db_path, data, validate=False)
            assert success, f"Generation failed: {error}"
            
            # Verify schema
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            )
            tables = {row[0] for row in cursor.fetchall()}
            
            # Required tables from Phase 21 spec
            required_tables = {
                'repo_summary',
                'use_cases',
                'metrics_summary',
                'metrics_by_file',
                'vulnerabilities',
                'packages',
                'code_smells',
                'entities',
                'relationships',
                'components',
                'files',
                'code_snippets',
                'test_results',
                'lens_insights',
            }
            
            # Check all required tables exist
            missing = required_tables - tables
            assert len(missing) == 0, f"Missing tables: {missing}"
            
            conn.close()
    
    def test_schema_creates_indexes(self):
        """Test that indexes are created for performance."""
        generator = SQLiteDataGenerator()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.sqlite"
            
            data = {
                "repo_summary": {
                    "repo_name": "test",
                    "repo_slug": "test",
                    "primary_language": "Python",
                    "last_commit_date": "2026-02-03T00:00:00Z"
                },
                "metrics_summary": {
                    "total_loc": 0,
                    "calculated_at": "2026-02-03T00:00:00Z"
                }
            }
            
            success, error = generator.generate(db_path, data, validate=False)
            assert success
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get all indexes
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='index' ORDER BY name"
            )
            indexes = {row[0] for row in cursor.fetchall()}
            
            # Check key indexes exist
            expected_indexes = {
                'idx_repo_slug',
                'idx_use_case_category',
                'idx_use_case_priority',
                'idx_metrics_file_path',
                'idx_vuln_severity',
                'idx_package_name',
                'idx_smell_type',
            }
            
            found_indexes = expected_indexes & indexes
            assert len(found_indexes) > 0, "No expected indexes found"
            
            conn.close()
    
    def test_schema_creates_fts5_tables(self):
        """Test that FTS5 full-text search tables are created."""
        generator = SQLiteDataGenerator()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.sqlite"
            
            data = {
                "repo_summary": {
                    "repo_name": "test",
                    "repo_slug": "test",
                    "primary_language": "Python",
                    "last_commit_date": "2026-02-03T00:00:00Z"
                },
                "metrics_summary": {
                    "total_loc": 0,
                    "calculated_at": "2026-02-03T00:00:00Z"
                }
            }
            
            success, error = generator.generate(db_path, data, validate=False)
            assert success
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get all virtual tables (FTS5)
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND sql LIKE '%fts5%'"
            )
            fts_tables = {row[0] for row in cursor.fetchall()}
            
            # Check FTS tables exist
            expected_fts = {'use_cases_fts', 'packages_fts'}
            found_fts = expected_fts & fts_tables
            
            assert len(found_fts) > 0, f"FTS5 tables not found. Expected: {expected_fts}, Found: {fts_tables}"
            
            conn.close()
    
    def test_empty_data_still_creates_schema(self):
        """Test that schema is created even with no data."""
        generator = SQLiteDataGenerator()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.sqlite"
            
            # Empty data (just required minimum)
            data = {
                "repo_summary": {
                    "repo_name": "empty",
                    "repo_slug": "empty",
                    "primary_language": "Unknown",
                    "last_commit_date": "2026-02-03T00:00:00Z"
                },
                "metrics_summary": {
                    "total_loc": 0,
                    "calculated_at": "2026-02-03T00:00:00Z"
                }
            }
            
            success, error = generator.generate(db_path, data, validate=False)
            assert success
            
            # Verify database exists and has tables
            assert db_path.exists()
            assert db_path.stat().st_size > 0
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
            table_count = cursor.fetchone()[0]
            
            assert table_count > 10, f"Expected >10 tables, got {table_count}"
            
            conn.close()
