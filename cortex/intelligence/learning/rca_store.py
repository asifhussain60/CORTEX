"""
Phase 87 — RCA Store
SQLite persistence layer for RCA artefacts: analyses, prevention rules,
recurrence signatures, and recurrence incidents.

Database location: .cortex-runtime/rca/rca_store.db (default)
Custom path may be supplied via constructor for testing.

CORE-011: Type hints on all functions
CORE-012: Docstrings on all public APIs
CORE-028: snake_case filename
CORE-035: Single canonical implementation
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from cortex.intelligence.learning.rca_models import (
    GateLevel,
    PreventionRule,
    RCAAnalysis,
    RCACategory,
    RCATemplate,
)

_DEFAULT_DB_PATH = ".cortex-runtime/rca/rca_store.db"

_DDL = """
CREATE TABLE IF NOT EXISTS rca_analyses (
    id                   TEXT PRIMARY KEY,
    failure_id           TEXT NOT NULL,
    methodology          TEXT NOT NULL,
    category             TEXT NOT NULL,
    root_cause           TEXT NOT NULL,
    confidence           REAL NOT NULL,
    analysis_data        TEXT NOT NULL DEFAULT '{}',
    recurrence_signature TEXT,
    created_at           TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS prevention_rules (
    id                  TEXT PRIMARY KEY,
    rca_id              TEXT NOT NULL,
    rule_text           TEXT NOT NULL,
    gate_level          TEXT NOT NULL,
    active              INTEGER NOT NULL DEFAULT 1,
    trigger_count       INTEGER NOT NULL DEFAULT 0,
    false_positive_count INTEGER NOT NULL DEFAULT 0,
    created_at          TEXT NOT NULL,
    FOREIGN KEY (rca_id) REFERENCES rca_analyses(id)
);

CREATE TABLE IF NOT EXISTS recurrence_signatures (
    id          TEXT PRIMARY KEY,
    rca_id      TEXT NOT NULL,
    signature   TEXT NOT NULL UNIQUE,
    created_at  TEXT NOT NULL,
    FOREIGN KEY (rca_id) REFERENCES rca_analyses(id)
);

CREATE TABLE IF NOT EXISTS recurrence_incidents (
    id              TEXT PRIMARY KEY,
    signature_id    TEXT NOT NULL,
    failure_id      TEXT NOT NULL,
    similarity      REAL NOT NULL,
    detected_at     TEXT NOT NULL,
    FOREIGN KEY (signature_id) REFERENCES recurrence_signatures(id)
);
"""


class RCAStore:
    """Persist and retrieve RCA artefacts in a local SQLite database.

    All four tables (rca_analyses, prevention_rules, recurrence_signatures,
    recurrence_incidents) are created on initialize().

    Args:
        db_path: Filesystem path for the SQLite file.  Defaults to the
                 canonical CORTEX runtime location.
    """

    def __init__(self, db_path: str = _DEFAULT_DB_PATH) -> None:
        """Initialise the store with a database path (does NOT open the DB yet).

        Args:
            db_path: Absolute or relative path to the SQLite file.
        """
        self._db_path = Path(db_path)

    # ------------------------------------------------------------------
    # Schema
    # ------------------------------------------------------------------

    def initialize(self) -> None:
        """Create parent directories and all four RCA tables (idempotent).

        Safe to call multiple times — uses CREATE TABLE IF NOT EXISTS.
        """
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as con:
            con.executescript(_DDL)

    # ------------------------------------------------------------------
    # rca_analyses
    # ------------------------------------------------------------------

    def save_analysis(self, rca: RCAAnalysis) -> None:
        """Persist an RCAAnalysis to the rca_analyses table.

        Args:
            rca: The RCAAnalysis to persist.
        """
        sql = """
        INSERT OR REPLACE INTO rca_analyses
            (id, failure_id, methodology, category, root_cause, confidence,
             analysis_data, recurrence_signature, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        with self._connect() as con:
            con.execute(sql, (
                rca.id,
                rca.failure_id,
                rca.methodology.value,
                rca.category.value,
                rca.root_cause,
                rca.confidence,
                json.dumps(rca.analysis_data),
                rca.recurrence_signature,
                rca.created_at,
            ))

    def get_analysis(self, rca_id: str) -> Optional[RCAAnalysis]:
        """Retrieve a single RCAAnalysis by its id.

        Args:
            rca_id: The unique RCA identifier.

        Returns:
            The matching RCAAnalysis, or None if not found.
        """
        sql = "SELECT * FROM rca_analyses WHERE id = ?"
        with self._connect() as con:
            row = con.execute(sql, (rca_id,)).fetchone()
        return self._row_to_analysis(row) if row else None

    def list_analyses(self, failure_id: Optional[str] = None) -> List[RCAAnalysis]:
        """Return all stored analyses, optionally filtered by failure_id.

        Args:
            failure_id: Optional filter; when set, only analyses for this
                        failure event are returned.

        Returns:
            A list of RCAAnalysis objects (may be empty).
        """
        if failure_id:
            sql = "SELECT * FROM rca_analyses WHERE failure_id = ? ORDER BY created_at DESC"
            params = (failure_id,)
        else:
            sql = "SELECT * FROM rca_analyses ORDER BY created_at DESC"
            params = ()
        with self._connect() as con:
            rows = con.execute(sql, params).fetchall()
        return [self._row_to_analysis(r) for r in rows if r]

    # ------------------------------------------------------------------
    # prevention_rules
    # ------------------------------------------------------------------

    def save_rule(self, rule: PreventionRule) -> None:
        """Persist a PreventionRule to the prevention_rules table.

        Args:
            rule: The PreventionRule to persist.
        """
        sql = """
        INSERT OR REPLACE INTO prevention_rules
            (id, rca_id, rule_text, gate_level, active,
             trigger_count, false_positive_count, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        with self._connect() as con:
            con.execute(sql, (
                rule.id,
                rule.rca_id,
                rule.rule_text,
                rule.gate_level.value,
                1 if rule.active else 0,
                rule.trigger_count,
                rule.false_positive_count,
                rule.created_at,
            ))

    def list_rules(self, rca_id: Optional[str] = None) -> List[PreventionRule]:
        """Return all stored prevention rules, optionally filtered by rca_id.

        Args:
            rca_id: Optional filter; when set, only rules linked to this
                    RCA id are returned.

        Returns:
            A list of PreventionRule objects (may be empty).
        """
        if rca_id:
            sql = "SELECT * FROM prevention_rules WHERE rca_id = ? ORDER BY created_at DESC"
            params = (rca_id,)
        else:
            sql = "SELECT * FROM prevention_rules ORDER BY created_at DESC"
            params = ()
        with self._connect() as con:
            rows = con.execute(sql, params).fetchall()
        return [self._row_to_rule(r) for r in rows if r]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _connect(self) -> sqlite3.Connection:
        """Open a SQLite connection with row_factory set to Row.

        Returns:
            A sqlite3.Connection instance.
        """
        con = sqlite3.connect(str(self._db_path))
        con.row_factory = sqlite3.Row
        return con

    @staticmethod
    def _row_to_analysis(row: sqlite3.Row) -> RCAAnalysis:
        """Convert a sqlite3.Row from rca_analyses into an RCAAnalysis.

        Args:
            row: A sqlite3.Row from the rca_analyses table.

        Returns:
            A populated RCAAnalysis dataclass.
        """
        return RCAAnalysis(
            id=row["id"],
            failure_id=row["failure_id"],
            methodology=RCATemplate(row["methodology"]),
            category=RCACategory(row["category"]),
            root_cause=row["root_cause"],
            confidence=float(row["confidence"]),
            analysis_data=json.loads(row["analysis_data"] or "{}"),
            recurrence_signature=row["recurrence_signature"],
            created_at=row["created_at"],
        )

    @staticmethod
    def _row_to_rule(row: sqlite3.Row) -> PreventionRule:
        """Convert a sqlite3.Row from prevention_rules into a PreventionRule.

        Args:
            row: A sqlite3.Row from the prevention_rules table.

        Returns:
            A populated PreventionRule dataclass.
        """
        return PreventionRule(
            id=row["id"],
            rca_id=row["rca_id"],
            rule_text=row["rule_text"],
            gate_level=GateLevel(row["gate_level"]),
            active=bool(row["active"]),
            trigger_count=int(row["trigger_count"]),
            false_positive_count=int(row["false_positive_count"]),
            created_at=row["created_at"],
        )
