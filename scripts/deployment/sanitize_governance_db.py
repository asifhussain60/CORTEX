"""Governance DB sanitization for production deployments.

This module provides the GovernanceDBSanitizer class that removes development
entries from governance.db, ensuring clean production state.

PHASE-DEPLOYMENT-001: AC-DEP-001-01
"""

import sqlite3
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional


@dataclass
class SanitizeResult:
    """Result of sanitization operation.
    
    Attributes:
        removed_count: Number of entries removed.
        preserved_count: Number of entries preserved.
        removed_ac_ids: List of AC-IDs that were removed.
        report: Human-readable sanitization report.
        retention_policy: Description of what was preserved and why.
    """
    removed_count: int = 0
    preserved_count: int = 0
    removed_ac_ids: List[str] = field(default_factory=list)
    report: str = ""
    retention_policy: str = ""


class GovernanceDBSanitizer:
    """Sanitizes governance.db by removing development-only entries.
    
    Production deployments should not contain audit logs from development,
    testing, or debugging sessions. This class identifies and removes such
    entries while preserving production audit trails.
    
    Attributes:
        db_path: Path to the governance.db file.
    """
    
    # Patterns that indicate dev-only entries
    DEV_PATTERNS = [
        "TEST%",
        "DEV%",
        "DEBUG%",
        "TEMP%",
        "MOCK%",
        "DUMMY%",
        "SAMPLE%",
        "EXAMPLE%",
    ]
    
    # Patterns that should always be preserved
    PRESERVE_PATTERNS = [
        "AC-CORE%",
        "AC-PROD%",
        "CORE-%",
    ]
    
    def __init__(self, db_path: Path) -> None:
        """Initialize the sanitizer.
        
        Args:
            db_path: Path to the governance.db file.
        """
        self.db_path = Path(db_path)
    
    def get_dev_patterns(self) -> List[str]:
        """Return the list of patterns that identify dev-only entries.
        
        Returns:
            List of SQL LIKE patterns for dev entries.
        """
        return self.DEV_PATTERNS.copy()
    
    def get_preserve_patterns(self) -> List[str]:
        """Return the list of patterns that should always be preserved.
        
        Returns:
            List of SQL LIKE patterns for preserved entries.
        """
        return self.PRESERVE_PATTERNS.copy()
    
    def sanitize(self) -> SanitizeResult:
        """Remove development entries from governance.db.
        
        Removes entries matching dev patterns (TEST%, DEV%, etc.) while
        preserving:
        - Entries with is_production=1
        - Entries matching preserve patterns (AC-CORE%, etc.)
        
        Returns:
            SanitizeResult with details of what was removed/preserved.
        """
        result = SanitizeResult()
        
        if not self.db_path.exists():
            result.report = "Database does not exist"
            return result
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # First, identify entries to remove
            dev_conditions = " OR ".join(
                f"ac_id LIKE '{pattern}'" for pattern in self.DEV_PATTERNS
            )
            preserve_conditions = " OR ".join(
                f"ac_id LIKE '{pattern}'" for pattern in self.PRESERVE_PATTERNS
            )
            
            # Select entries to remove:
            # - Match dev patterns AND
            # - Not production AND
            # - Not matching preserve patterns
            select_query = f"""
                SELECT ac_id FROM audit_log
                WHERE ({dev_conditions})
                AND is_production = 0
                AND NOT ({preserve_conditions})
            """
            
            cursor.execute(select_query)
            entries_to_remove = cursor.fetchall()
            result.removed_ac_ids = [row[0] for row in entries_to_remove]
            result.removed_count = len(result.removed_ac_ids)
            
            # Delete the identified entries
            if result.removed_count > 0:
                delete_query = f"""
                    DELETE FROM audit_log
                    WHERE ({dev_conditions})
                    AND is_production = 0
                    AND NOT ({preserve_conditions})
                """
                cursor.execute(delete_query)
                conn.commit()
            
            # Count preserved entries
            cursor.execute("SELECT COUNT(*) FROM audit_log")
            result.preserved_count = cursor.fetchone()[0]
            
            # Generate report
            result.report = self._generate_report(result)
            result.retention_policy = self._get_retention_policy()
            
        finally:
            conn.close()
        
        return result
    
    def _generate_report(self, result: SanitizeResult) -> str:
        """Generate a human-readable sanitization report.
        
        Args:
            result: The sanitization result to report on.
            
        Returns:
            Formatted report string.
        """
        lines = [
            f"Sanitization Report - {datetime.now().isoformat()}",
            f"Database: {self.db_path}",
            f"Removed: {result.removed_count} dev entries",
            f"Preserved: {result.preserved_count} production entries",
            "",
            "Removed AC-IDs:" if result.removed_ac_ids else "No entries removed",
        ]
        
        for ac_id in result.removed_ac_ids[:10]:  # Limit to first 10
            lines.append(f"  - {ac_id}")
        
        if len(result.removed_ac_ids) > 10:
            lines.append(f"  ... and {len(result.removed_ac_ids) - 10} more")
        
        return "\n".join(lines)
    
    def _get_retention_policy(self) -> str:
        """Return the retention policy description.
        
        Returns:
            Description of retention policy.
        """
        return (
            "Retention Policy:\n"
            "- Production entries (is_production=1): ALWAYS preserved\n"
            "- AC-CORE, AC-PROD prefixes: ALWAYS preserved\n"
            "- TEST, DEV, DEBUG prefixes: ALWAYS removed\n"
            "- Other entries: Preserved unless explicitly dev-flagged"
        )
    
    def verify_sanitized(self) -> bool:
        """Verify that the database is in sanitized state.
        
        Returns:
            True if no dev entries remain, False otherwise.
        """
        if not self.db_path.exists():
            return True
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            dev_conditions = " OR ".join(
                f"ac_id LIKE '{pattern}'" for pattern in self.DEV_PATTERNS
            )
            
            query = f"""
                SELECT COUNT(*) FROM audit_log
                WHERE ({dev_conditions})
                AND is_production = 0
            """
            
            cursor.execute(query)
            dev_count = cursor.fetchone()[0]
            
            return dev_count == 0
            
        finally:
            conn.close()


def main() -> int:
    """CLI entry point for sanitization.
    
    Returns:
        Exit code (0 for success, 1 for failure).
    """
    import sys
    
    # Default path
    db_path = Path("cortex_brain/state/governance.db")
    
    if len(sys.argv) > 1:
        db_path = Path(sys.argv[1])
    
    sanitizer = GovernanceDBSanitizer(db_path)
    result = sanitizer.sanitize()
    
    print(result.report)
    
    if sanitizer.verify_sanitized():
        print("\n✅ Database is now in sanitized state")
        return 0
    else:
        print("\n❌ Sanitization incomplete - dev entries remain")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
