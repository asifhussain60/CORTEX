"""
CORTEX Deployment Sanitizer

Sanitizes governance.db and validates data integrity before deployment.

AC_START: AC-CORTEX-ALIGN-002
Description: Sanitization tool for governance.db
Authority: PHASE-DEPLOYMENT-001
"""

from typing import Dict, Any, List
from pathlib import Path
import sqlite3


class Sanitizer:
    """Sanitize governance.db for deployment."""
    
    def __init__(self, db_path: str = "cortex_intelligence/governance/governance.db") -> None:
        """Initialize sanitizer.
        
        Args:
            db_path: Path to governance.db file
        """
        self.db_path = Path(db_path)
    
    def sanitize(self) -> Dict[str, Any]:
        """Run sanitization on governance.db.
        
        Returns:
            Dictionary with removed_entries, preserved_entries, patterns_matched
        """
        return self._run_sanitization()
    
    def validate(self) -> Dict[str, Any]:
        """Validate sanitization completeness.
        
        Returns:
            Dictionary with valid flag and any issues found
        """
        return self._validate_sanitization()
    
    def _run_sanitization(self) -> Dict[str, Any]:
        """Execute sanitization logic.
        
        Returns:
            Sanitization results
        """
        removed_entries = 0
        preserved_entries = 0
        patterns_matched: List[str] = []
        
        if not self.db_path.exists():
            return {
                "removed_entries": 0,
                "preserved_entries": 0,
                "patterns_matched": [],
                "message": "Database file not found"
            }
        
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Get total entries
            cursor.execute("SELECT COUNT(*) FROM audit_trail")
            total = cursor.fetchone()[0]
            
            # Patterns to remove (test/dev data)
            patterns = ["TEST%", "DEV%", "MOCK%"]
            
            for pattern in patterns:
                cursor.execute(
                    "SELECT COUNT(*) FROM audit_trail WHERE ac_marker LIKE ?",
                    (pattern,)
                )
                count = cursor.fetchone()[0]
                
                if count > 0:
                    patterns_matched.append(pattern)
                    cursor.execute(
                        "DELETE FROM audit_trail WHERE ac_marker LIKE ?",
                        (pattern,)
                    )
                    removed_entries += count
            
            conn.commit()
            
            # Get remaining entries
            cursor.execute("SELECT COUNT(*) FROM audit_trail")
            preserved_entries = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                "removed_entries": removed_entries,
                "preserved_entries": preserved_entries,
                "patterns_matched": patterns_matched
            }
            
        except Exception as e:
            return {
                "removed_entries": 0,
                "preserved_entries": 0,
                "patterns_matched": [],
                "error": str(e)
            }
    
    def _validate_sanitization(self) -> Dict[str, Any]:
        """Validate sanitization results.
        
        Returns:
            Validation results with valid flag and issues
        """
        issues: List[str] = []
        
        if not self.db_path.exists():
            issues.append("Database file not found")
            return {"valid": False, "issues": issues}
        
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Check for any test/dev patterns
            test_patterns = ["TEST%", "DEV%", "MOCK%"]
            
            for pattern in test_patterns:
                cursor.execute(
                    "SELECT COUNT(*) FROM audit_trail WHERE ac_marker LIKE ?",
                    (pattern,)
                )
                count = cursor.fetchone()[0]
                
                if count > 0:
                    issues.append(f"Found {count} entries matching {pattern}")
            
            conn.close()
            
            return {
                "valid": len(issues) == 0,
                "issues": issues
            }
            
        except Exception as e:
            issues.append(f"Validation error: {str(e)}")
            return {"valid": False, "issues": issues}
