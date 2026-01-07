"""
Database Layer - DELIBERATELY FLAWED
Contains: SEC-03, SEC-14, PERF-01, SOL-09 (SQL injection, no connection pooling, N+1 queries)
"""
import sqlite3
from typing import Dict, List, Optional, Any


class Database:
    """
    Database access layer with multiple flaws
    FLAW SOL-09: Concrete class instantiated directly (DIP violation)
    """
    
    def __init__(self, db_path: str = "sts_ecommerce.db"):
        # FLAW PERF-04: No connection pooling
        self.db_path = db_path
        self.connection = None
        self._connect()
    
    def _connect(self):
        """Establish database connection"""
        try:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row
        except Exception as e:
            # FLAW CQ-14: Silently swallows errors
            pass
    
    def is_connected(self) -> bool:
        """Check if database is connected"""
        return self.connection is not None
    
    def execute(self, query: str, params: tuple = None) -> Optional[List[Dict]]:
        """
        Execute SQL query
        FLAW SEC-03: SQL injection via string concatenation (CRITICAL)
        FLAW CQ-13: No error handling
        """
        try:
            cursor = self.connection.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                # FLAW: Query passed as-is, vulnerable to injection
                cursor.execute(query)
            
            if query.strip().upper().startswith('SELECT'):
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
            else:
                self.connection.commit()
                return [{"affected_rows": cursor.rowcount}]
        except Exception as e:
            # FLAW: Swallow exception
            return None
    
    def execute_many(self, query: str, params_list: List[tuple]) -> bool:
        """Execute query with multiple parameter sets"""
        try:
            cursor = self.connection.cursor()
            cursor.executemany(query, params_list)
            self.connection.commit()
            return True
        except Exception:
            return False
    
    def get_one(self, query: str, params: tuple = None) -> Optional[Dict]:
        """Get single row"""
        results = self.execute(query, params)
        return results[0] if results else None
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None


class Repository:
    """
    Base repository with SQL injection vulnerabilities
    FLAW SOL-05: Child classes throw NotImplementedError (LSP violation)
    """
    
    def __init__(self, db: Database):
        self.db = db
    
    def find_by_id(self, table: str, id: int) -> Optional[Dict]:
        """
        Find record by ID
        FLAW SEC-03: SQL injection via f-string (CRITICAL)
        """
        # FLAW: f-string allows injection
        query = f"SELECT * FROM {table} WHERE id = {id}"
        return self.db.get_one(query)
    
    def find_all(self, table: str, conditions: Dict = None) -> List[Dict]:
        """
        Find all records with optional conditions
        FLAW SEC-03: SQL injection via string concatenation
        FLAW PERF-02: No pagination, loads everything
        """
        query = f"SELECT * FROM {table}"
        
        if conditions:
            # FLAW: Building WHERE clause with string concatenation
            where_parts = []
            for key, value in conditions.items():
                if isinstance(value, str):
                    where_parts.append(f"{key} = '{value}'")
                else:
                    where_parts.append(f"{key} = {value}")
            
            if where_parts:
                query += " WHERE " + " AND ".join(where_parts)
        
        return self.db.execute(query) or []
    
    def insert(self, table: str, data: Dict) -> int:
        """
        Insert new record
        FLAW SEC-03: SQL injection vulnerability
        """
        columns = ', '.join(data.keys())
        
        # FLAW: String formatting allows injection
        values = ', '.join([f"'{v}'" if isinstance(v, str) else str(v) for v in data.values()])
        
        query = f"INSERT INTO {table} ({columns}) VALUES ({values})"
        self.db.execute(query)
        
        # Get last inserted ID
        result = self.db.get_one("SELECT last_insert_rowid() as id")
        return result['id'] if result else 0
    
    def update(self, table: str, id: int, data: Dict) -> bool:
        """
        Update record
        FLAW SEC-03: SQL injection vulnerability
        """
        # FLAW: Building SET clause with string concatenation
        set_parts = []
        for key, value in data.items():
            if isinstance(value, str):
                set_parts.append(f"{key} = '{value}'")
            else:
                set_parts.append(f"{key} = {value}")
        
        query = f"UPDATE {table} SET {', '.join(set_parts)} WHERE id = {id}"
        result = self.db.execute(query)
        return result is not None
    
    def delete(self, table: str, id: int) -> bool:
        """
        Delete record
        FLAW SEC-03: SQL injection via f-string
        """
        query = f"DELETE FROM {table} WHERE id = {id}"
        result = self.db.execute(query)
        return result is not None


# FLAW CQ-09: Dead code - unused class
class LegacyDatabase:
    """Old database class - no longer used but not removed"""
    pass
