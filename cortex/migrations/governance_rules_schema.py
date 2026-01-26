"""
Governance Rules Database Schema Initialization

Purpose:
    Initialize SQLite database schema for governance rules persistence.
    Creates tables, indexes, and validates schema integrity.

Migration Strategy:
    - Phase 1 → Phase 2: Initialize database from scratch
    - Future migrations: Use version tracking for schema evolution

Tables:
    - project_rules: Tier 1 rules (project-level governance)
    - team_rules: Tier 2 rules (team-level, multi-tenant)
    - governance_audit_log: Audit trail for compliance
    - rule_versions: Version history for rules

Author: Asif Hussain
Version: 1.0
"""

from cortex.brain.core.governance_database import GovernanceDatabaseManager
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def initialize_governance_database(db_path: Optional[Path] = None) -> bool:
    """
    Initialize governance database schema.

    Args:
        db_path: Optional path to database file

    Returns:
        True if initialization successful, False otherwise

    Raises:
        Exception: If schema creation fails
    """
    try:
        manager = GovernanceDatabaseManager(db_path)
        manager.initialize()
        logger.info("✅ Governance database schema initialized successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to initialize governance database: {e}")
        raise


def verify_schema_integrity() -> bool:
    """
    Verify database schema integrity.

    Returns:
        True if schema is valid, False otherwise
    """
    try:
        manager = GovernanceDatabaseManager.instance()
        manager.initialize()

        if not manager.verify_schema():
            logger.error("❌ Required tables missing from database")
            return False

        logger.info("✅ Schema integrity check passed")
        return True

    except Exception as e:
        logger.error(f"❌ Schema integrity check failed: {e}")
        return False


if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO)

    try:
        initialize_governance_database()
        if verify_schema_integrity():
            print("✅ Governance database schema initialized and verified")
            sys.exit(0)
        else:
            print("❌ Schema verification failed")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        sys.exit(1)
