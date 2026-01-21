"""Audit Query - PHASE-DEPLOYMENT-003-mcp-expansion.

Search governance.db by AC-ID, timestamp, phase.

Author: CORTEX Framework
"""

from typing import Dict, Any, List, Optional
from datetime import datetime


class AuditQuery:
    """Query governance audit database.
    
    Supports searching by AC-ID, timestamp range, and phase.
    """
    
    def __init__(self, db_path: str = "governance.db"):
        """Initialize audit query.
        
        Args:
            db_path: Path to governance database.
        """
        self.db_path = db_path
    
    def search(
        self,
        ac_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        phase: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Search audit entries.
        
        Args:
            ac_id: Filter by AC-ID (supports wildcards).
            start_date: Filter entries after this date (YYYY-MM-DD).
            end_date: Filter entries before this date (YYYY-MM-DD).
            phase: Filter by phase name.
            limit: Maximum results to return.
            
        Returns:
            List of matching audit entries.
        """
        # Build query based on parameters
        query = "SELECT * FROM audit_log WHERE 1=1"
        params = []
        
        if ac_id:
            if "*" in ac_id:
                query += " AND ac_id LIKE ?"
                params.append(ac_id.replace("*", "%"))
            else:
                query += " AND ac_id = ?"
                params.append(ac_id)
        
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date)
        
        if phase:
            query += " AND (phase = ? OR ac_id LIKE ?)"
            params.append(phase)
            params.append(f"%{phase}%")
        
        query += f" LIMIT {limit}"
        
        return self._execute_query(query, params)
    
    def _execute_query(self, query: str, params: List[Any]) -> List[Dict[str, Any]]:
        """Execute database query.
        
        Args:
            query: SQL query string.
            params: Query parameters.
            
        Returns:
            Query results as list of dictionaries.
        """
        import sqlite3
        from pathlib import Path
        
        if not Path(self.db_path).exists():
            return []
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            results = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return results
        except Exception:
            return []


__all__ = ["AuditQuery"]
