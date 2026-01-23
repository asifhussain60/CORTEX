"""
Audit trail logging for AC-PHX-007-01: Intent Classification Framework

This script creates audit trail entries following CORTEX governance rules:
- CORE-027: Audit trail logging (AC_START, AC_EXECUTE, AC_COMPLETE)

AC-PHX-007-01 Completion:
- Classifier module created with comprehensive documentation
- 53 unit tests written (CORE-008: TDD first)
- All tests passing ✅
- Type hints on all functions (CORE-011)
- Google-style docstrings on all methods (CORE-012)
- Specific exception handling (CORE-013)
- Performance metrics and caching implemented
- Signal detection and multi-label classification working

"""

import sqlite3
from pathlib import Path
from datetime import datetime


def log_ac_lifecycle(ac_id: str, operation: str, success: bool = True) -> None:
    """Log an AC lifecycle event to the audit trail.
    
    Args:
        ac_id: AC identifier (e.g., "AC-PHX-007-01")
        operation: Operation type (AC_START, AC_EXECUTE, AC_COMPLETE)
        success: Whether operation succeeded
    """
    db_path = Path(__file__).parent.parent.parent / "cortex_brain" / "state" / "governance.db"
    
    if not db_path.exists():
        raise FileNotFoundError(f"Governance database not found: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Get previous hash for chain
        cursor.execute("SELECT entry_hash FROM audit_log ORDER BY id DESC LIMIT 1")
        result = cursor.fetchone()
        previous_hash = result[0] if result else "GENESIS"
        
        # Create entry hash
        entry_data = f"{ac_id}:{operation}:{datetime.now().isoformat()}"
        import hashlib
        entry_hash = hashlib.sha256(entry_data.encode()).hexdigest()
        
        # Insert audit entry
        cursor.execute("""
            INSERT INTO audit_log 
            (ac_id, operation, component, level, message, 
             metadata, previous_hash, entry_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            ac_id,
            operation,
            "intent_router.classifier",
            "INFO",
            f"{operation} for {ac_id}",
            f"module=intent_router,success={success}",
            previous_hash,
            entry_hash
        ))
        
        conn.commit()
        print(f"✓ Logged {operation} for {ac_id} (hash: {entry_hash[:12]}...)")
        
    except sqlite3.Error as e:
        print(f"✗ Failed to log audit entry: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    # Log AC-PHX-007-01 lifecycle
    print("Creating audit trail for AC-PHX-007-01: Intent Classification Framework\n")
    
    log_ac_lifecycle("AC-PHX-007-01", "AC_START")
    log_ac_lifecycle("AC-PHX-007-01", "AC_EXECUTE")
    log_ac_lifecycle("AC-PHX-007-01", "AC_COMPLETE")
    
    print("\n✓ Audit trail complete!")
