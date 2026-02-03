"""
SQLite Data Generator for Dashboard v3.0
=========================================

Purpose: Convert LENS analysis data into dashboard.sqlite with proper schema
Created: 2026-02-03
Authority: PHASE-21-ENTERPRISE-REPOSITORY-INTELLIGENCE.yaml
Governance: CORE-011 (type hints), CORE-012 (docstrings), CORE-035 (single canonical)

Architecture:
- Takes aggregated LENS data (dict/Pydantic models)
- Creates dashboard.sqlite with full schema (tables, indexes, views, FTS5)
- Handles JSON serialization for array fields
- Validates data against schema v3.0
- Transaction-based for data integrity
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from cortex.models.dashboard_schema_v3 import (
    SQLiteSchemaGenerator,
    validate_dashboard_data,
)


class SQLiteDataGenerator:
    """
    Generate dashboard.sqlite from LENS analysis data.

    Features:
    - Creates complete SQLite database with schema v3.0
    - Handles JSON serialization for arrays/objects
    - Transaction-based writes (rollback on error)
    - Data validation before insertion
    - Automatic timestamp conversion to ISO8601

    Example:
        generator = SQLiteDataGenerator()
        generator.generate(
            output_path="company/dashboards/repos/cortex/dashboard.sqlite",
            data={
                "repo_summary": {...},
                "use_cases": [...],
                ...
            }
        )
    """

    def __init__(self):
        """Initialize generator."""
        self.schema_generator = SQLiteSchemaGenerator()

    def generate(
        self,
        output_path: Union[str, Path],
        data: Dict[str, Any],
        validate: bool = True,
        backup: bool = True,
    ) -> tuple[bool, Optional[str]]:
        """
        Generate dashboard.sqlite from data.

        Args:
            output_path: Path to output dashboard.sqlite file
            data: Dictionary with table names as keys
            validate: Whether to validate data against schema (default True)
            backup: Whether to backup existing file (default True)

        Returns:
            Tuple of (success: bool, error_message: Optional[str])

        Example:
            success, error = generator.generate(
                output_path="dashboard.sqlite",
                data={"repo_summary": {...}, ...}
            )
            if not success:
                print(f"Generation failed: {error}")
        """
        output_path = Path(output_path)

        # Validate data before proceeding
        if validate:
            valid, errors = validate_dashboard_data(data)
            if not valid:
                error_msg = f"Data validation failed: {'; '.join(errors)}"
                return False, error_msg

        # Backup existing file
        if backup and output_path.exists():
            backup_path = output_path.with_suffix(".sqlite.backup")
            backup_path.write_bytes(output_path.read_bytes())

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            # Create database with schema
            conn = sqlite3.connect(str(output_path))
            conn.row_factory = sqlite3.Row

            try:
                # Begin transaction
                conn.execute("BEGIN")

                # Create schema
                schema_sql = self.schema_generator.generate_full_schema()
                conn.executescript(schema_sql)

                # Insert data
                self._insert_repo_summary(conn, data.get("repo_summary"))
                self._insert_use_cases(conn, data.get("use_cases", []))
                self._insert_metrics_summary(conn, data.get("metrics_summary"))
                self._insert_metrics_by_file(conn, data.get("metrics_by_file", []))
                self._insert_vulnerabilities(conn, data.get("vulnerabilities", []))
                self._insert_packages(conn, data.get("packages", []))
                self._insert_code_smells(conn, data.get("code_smells", []))
                self._insert_entities(conn, data.get("entities", []))
                self._insert_relationships(conn, data.get("relationships", []))
                self._insert_components(conn, data.get("components", []))
                self._insert_files(conn, data.get("files", []))
                self._insert_code_snippets(conn, data.get("code_snippets", []))
                self._insert_test_results(conn, data.get("test_results", []))
                self._insert_lens_insights(conn, data.get("lens_insights", []))

                # Populate FTS5 tables
                self._populate_fts_tables(conn)

                # Commit transaction
                conn.commit()

                return True, None

            except Exception as e:
                # Rollback on error
                conn.rollback()
                raise e

            finally:
                conn.close()

        except Exception as e:
            return False, f"Database generation failed: {str(e)}"

    # =========================================================================
    # TABLE INSERTION METHODS
    # =========================================================================

    def _insert_repo_summary(self, conn: sqlite3.Connection, data: Optional[Dict]):
        """Insert repo_summary (singleton table)."""
        if not data:
            return

        conn.execute(
            """
            INSERT INTO repo_summary (
                id, repo_name, repo_slug, description, primary_language,
                tech_stack, total_loc, file_count, contributor_count,
                health_score, last_commit_date, created_at, llm_overview
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data.get("id", 1),
                data["repo_name"],
                data["repo_slug"],
                data.get("description"),
                data["primary_language"],
                json.dumps(data.get("tech_stack", [])),
                data.get("total_loc", 0),
                data.get("file_count", 0),
                data.get("contributor_count", 0),
                data.get("health_score", 0),
                self._to_iso8601(data["last_commit_date"]),
                self._to_iso8601(data.get("created_at", datetime.utcnow())),
                data.get("llm_overview"),
            ),
        )

    def _insert_use_cases(self, conn: sqlite3.Connection, data: List[Dict]):
        """Insert use_cases with FTS5 support."""
        for item in data:
            conn.execute(
                """
                INSERT INTO use_cases (
                    title, category, business_value, user_stories,
                    acceptance_criteria, priority, implementation_status,
                    related_files, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item["title"],
                    item["category"],
                    item.get("business_value"),
                    json.dumps(item.get("user_stories", [])),
                    json.dumps(item.get("acceptance_criteria", [])),
                    item.get("priority", "medium"),
                    item.get("implementation_status", "planned"),
                    json.dumps(item.get("related_files", [])),
                    self._to_iso8601(item.get("created_at", datetime.utcnow())),
                ),
            )

    def _insert_metrics_summary(self, conn: sqlite3.Connection, data: Optional[Dict]):
        """Insert metrics_summary (singleton table)."""
        if not data:
            return

        conn.execute(
            """
            INSERT INTO metrics_summary (
                id, total_loc, code_loc, comment_loc, avg_complexity,
                max_complexity, maintainability_index, technical_debt_hours,
                calculated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data.get("id", 1),
                data.get("total_loc", 0),
                data.get("code_loc", 0),
                data.get("comment_loc", 0),
                data.get("avg_complexity", 0.0),
                data.get("max_complexity", 0),
                data.get("maintainability_index", 0.0),
                data.get("technical_debt_hours", 0),
                self._to_iso8601(data.get("calculated_at", datetime.utcnow())),
            ),
        )

    def _insert_metrics_by_file(self, conn: sqlite3.Connection, data: List[Dict]):
        """Insert metrics_by_file for drill-down."""
        for item in data:
            conn.execute(
                """
                INSERT INTO metrics_by_file (
                    file_path, language, loc, complexity, maintainability,
                    churn_count, last_modified
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item["file_path"],
                    item["language"],
                    item.get("loc", 0),
                    item.get("complexity", 0),
                    item.get("maintainability", 0.0),
                    item.get("churn_count", 0),
                    self._to_iso8601(item.get("last_modified", datetime.utcnow())),
                ),
            )

    def _insert_vulnerabilities(self, conn: sqlite3.Connection, data: List[Dict]):
        """Insert security vulnerabilities."""
        for item in data:
            conn.execute(
                """
                INSERT INTO vulnerabilities (
                    cve_id, severity, package_name, package_version,
                    fixed_version, description, file_path, line_number,
                    remediation, detected_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item.get("cve_id"),
                    item["severity"],
                    item["package_name"],
                    item["package_version"],
                    item.get("fixed_version"),
                    item["description"],
                    item.get("file_path"),
                    item.get("line_number"),
                    item.get("remediation"),
                    self._to_iso8601(item.get("detected_at", datetime.utcnow())),
                ),
            )

    def _insert_packages(self, conn: sqlite3.Connection, data: List[Dict]):
        """Insert package dependencies with tree structure."""
        for item in data:
            conn.execute(
                """
                INSERT INTO packages (
                    package_name, package_version, package_type, license,
                    size_kb, vulnerability_count, parent_package_id, installed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item["package_name"],
                    item["package_version"],
                    item.get("package_type", "direct"),
                    item.get("license"),
                    item.get("size_kb", 0),
                    item.get("vulnerability_count", 0),
                    item.get("parent_package_id"),
                    self._to_iso8601(item.get("installed_at", datetime.utcnow())),
                ),
            )

    def _insert_code_smells(self, conn: sqlite3.Connection, data: List[Dict]):
        """Insert code quality issues."""
        for item in data:
            conn.execute(
                """
                INSERT INTO code_smells (
                    smell_type, category, severity, file_path, line_number,
                    code_snippet, explanation, remediation, effort_hours, detected_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item["smell_type"],
                    item["category"],
                    item["severity"],
                    item["file_path"],
                    item["line_number"],
                    item.get("code_snippet"),
                    item.get("explanation"),
                    item.get("remediation"),
                    item.get("effort_hours", 1),
                    self._to_iso8601(item.get("detected_at", datetime.utcnow())),
                ),
            )

    def _insert_entities(self, conn: sqlite3.Connection, data: List[Dict]):
        """Insert domain model entities."""
        for item in data:
            conn.execute(
                """
                INSERT INTO entities (
                    name, type, description, file_path, line_range,
                    attributes, methods, stereotypes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item["name"],
                    item["type"],
                    item.get("description"),
                    item["file_path"],
                    item["line_range"],
                    json.dumps(item.get("attributes", [])),
                    json.dumps(item.get("methods", [])),
                    json.dumps(item.get("stereotypes", [])),
                ),
            )

    def _insert_relationships(self, conn: sqlite3.Connection, data: List[Dict]):
        """Insert entity relationships."""
        for item in data:
            conn.execute(
                """
                INSERT INTO relationships (
                    source_entity, target_entity, relationship_type,
                    cardinality, label, bidirectional
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    item["source_entity"],
                    item["target_entity"],
                    item["relationship_type"],
                    item["cardinality"],
                    item.get("label"),
                    1 if item.get("bidirectional", False) else 0,
                ),
            )

    def _insert_components(self, conn: sqlite3.Connection, data: List[Dict]):
        """Insert architecture components."""
        for item in data:
            conn.execute(
                """
                INSERT INTO components (
                    name, type, description, dependencies, api_count, loc, layer
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item["name"],
                    item["type"],
                    item.get("description"),
                    json.dumps(item.get("dependencies", [])),
                    item.get("api_count", 0),
                    item.get("loc", 0),
                    item["layer"],
                ),
            )

    def _insert_files(self, conn: sqlite3.Connection, data: List[Dict]):
        """Insert file tree with FTS5 support."""
        for item in data:
            conn.execute(
                """
                INSERT INTO files (
                    file_path, file_name, file_type, parent_path, language,
                    loc, complexity, last_modified, churn_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item["file_path"],
                    item["file_name"],
                    item["file_type"],
                    item.get("parent_path"),
                    item.get("language"),
                    item.get("loc", 0),
                    item.get("complexity", 0),
                    self._to_iso8601(item.get("last_modified", datetime.utcnow())),
                    item.get("churn_count", 0),
                ),
            )

    def _insert_code_snippets(self, conn: sqlite3.Connection, data: List[Dict]):
        """Insert highlighted code snippets."""
        for item in data:
            conn.execute(
                """
                INSERT INTO code_snippets (
                    title, file_path, start_line, end_line, language,
                    code, explanation, category
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item["title"],
                    item["file_path"],
                    item["start_line"],
                    item["end_line"],
                    item["language"],
                    item["code"],
                    item.get("explanation"),
                    item["category"],
                ),
            )

    def _insert_test_results(self, conn: sqlite3.Connection, data: List[Dict]):
        """Insert test execution results."""
        for item in data:
            conn.execute(
                """
                INSERT INTO test_results (
                    test_name, test_type, status, duration_ms, file_path,
                    failure_message, run_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item["test_name"],
                    item["test_type"],
                    item["status"],
                    item.get("duration_ms", 0),
                    item["file_path"],
                    item.get("failure_message"),
                    self._to_iso8601(item.get("run_at", datetime.utcnow())),
                ),
            )

    def _insert_lens_insights(self, conn: sqlite3.Connection, data: List[Dict]):
        """Insert LENS analysis insights."""
        for item in data:
            conn.execute(
                """
                INSERT INTO lens_insights (
                    insight_type, category, description, evidence,
                    impact, confidence, detected_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item["insight_type"],
                    item["category"],
                    item["description"],
                    json.dumps(item.get("evidence", [])),
                    item["impact"],
                    item.get("confidence", 0),
                    self._to_iso8601(item.get("detected_at", datetime.utcnow())),
                ),
            )

    def _populate_fts_tables(self, conn: sqlite3.Connection):
        """
        Populate FTS5 full-text search tables.

        Triggers would normally handle this, but manual population
        ensures data is immediately searchable.
        """
        # Populate use_cases_fts
        conn.execute(
            """
            INSERT INTO use_cases_fts(rowid, title, business_value)
            SELECT id, title, COALESCE(business_value, '') FROM use_cases
            """
        )

        # Populate packages_fts
        conn.execute(
            """
            INSERT INTO packages_fts(rowid, package_name)
            SELECT id, package_name FROM packages
            """
        )

        # Populate files_fts
        conn.execute(
            """
            INSERT INTO files_fts(rowid, file_path, file_name)
            SELECT id, file_path, file_name FROM files
            """
        )

    # =========================================================================
    # UTILITY METHODS
    # =========================================================================

    def _to_iso8601(self, value: Union[str, datetime]) -> str:
        """
        Convert datetime to ISO8601 string for SQLite storage.

        Args:
            value: datetime object or ISO8601 string

        Returns:
            ISO8601 formatted string
        """
        if isinstance(value, datetime):
            return value.isoformat()
        elif isinstance(value, str):
            # Assume already ISO8601
            return value
        else:
            # Default to current time
            return datetime.utcnow().isoformat()

    def query_database(
        self, db_path: Union[str, Path], query: str, params: tuple = ()
    ) -> List[Dict[str, Any]]:
        """
        Query dashboard.sqlite and return results.

        Args:
            db_path: Path to dashboard.sqlite
            query: SQL query string
            params: Query parameters (for prepared statements)

        Returns:
            List of result dictionaries

        Example:
            results = generator.query_database(
                "dashboard.sqlite",
                "SELECT * FROM use_cases WHERE priority = ?",
                ("high",)
            )
        """
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row

        try:
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def get_database_stats(self, db_path: Union[str, Path]) -> Dict[str, int]:
        """
        Get table row counts from database.

        Args:
            db_path: Path to dashboard.sqlite

        Returns:
            Dictionary of table names to row counts

        Example:
            stats = generator.get_database_stats("dashboard.sqlite")
            # {"use_cases": 25, "vulnerabilities": 8, ...}
        """
        tables = [
            "repo_summary",
            "use_cases",
            "metrics_summary",
            "metrics_by_file",
            "vulnerabilities",
            "packages",
            "code_smells",
            "entities",
            "relationships",
            "components",
            "files",
            "code_snippets",
            "test_results",
            "lens_insights",
        ]

        stats = {}
        conn = sqlite3.connect(str(db_path))

        try:
            for table in tables:
                try:
                    cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    stats[table] = count
                except sqlite3.Error:
                    # Table doesn't exist or error
                    stats[table] = 0
        finally:
            conn.close()

        return stats


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


def generate_dashboard_sqlite(
    output_path: Union[str, Path],
    data: Dict[str, Any],
    validate: bool = True,
    backup: bool = True,
) -> tuple[bool, Optional[str]]:
    """
    Convenience function to generate dashboard.sqlite.

    Args:
        output_path: Path to output file
        data: Dashboard data dictionary
        validate: Whether to validate data (default True)
        backup: Whether to backup existing file (default True)

    Returns:
        Tuple of (success: bool, error_message: Optional[str])

    Example:
        success, error = generate_dashboard_sqlite(
            "company/dashboards/repos/cortex/dashboard.sqlite",
            {"repo_summary": {...}, ...}
        )
    """
    generator = SQLiteDataGenerator()
    return generator.generate(output_path, data, validate, backup)
