"""
SqliteAppRepository - SQLite-Based Application Registry

Concrete implementation of ApplicationRepository using SQLite.
Stores registered applications with scan timestamps.

Author: Asif Hussain
"""
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List

from src.dashboard.domain.repositories.application_repository import ApplicationRepository
from src.dashboard.domain.entities.application import Application


class SqliteAppRepository(ApplicationRepository):
    """Repository for persisting applications to SQLite database"""
    
    def __init__(self, db_path: Path):
        """
        Initialize repository with database path.
        
        Args:
            db_path: Path to SQLite database file
        """
        self._db_path = Path(db_path)
        self._init_database()
    
    def get_by_id(self, app_id: str) -> Application:
        """
        Load application from database.
        
        Args:
            app_id: Application identifier
            
        Returns:
            Application entity
            
        Raises:
            FileNotFoundError: If application doesn't exist
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT app_id, app_name, app_type, data_path, last_scan FROM applications WHERE app_id = ?",
                (app_id,)
            )
            row = cursor.fetchone()
            
            if row is None:
                raise FileNotFoundError(f"Application not found for app_id='{app_id}'")
            
            return Application(
                app_id=row[0],
                app_name=row[1],
                app_type=row[2],
                data_path=row[3],
                last_scan=datetime.fromisoformat(row[4])
            )
        finally:
            conn.close()
    
    def save(self, application: Application) -> None:
        """
        Save application to database (upsert).
        
        Args:
            application: Application entity to persist
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO applications (app_id, app_name, app_type, data_path, last_scan)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(app_id) DO UPDATE SET
                    app_name = excluded.app_name,
                    app_type = excluded.app_type,
                    data_path = excluded.data_path,
                    last_scan = excluded.last_scan
                """,
                (
                    application.app_id,
                    application.app_name,
                    application.app_type,
                    application.data_path,
                    application.last_scan.isoformat()
                )
            )
            conn.commit()
        finally:
            conn.close()
    
    def register(self, app: Application) -> None:
        """
        Register application (alias for save).
        
        Args:
            app: Application entity to register
        """
        self.save(app)
    
    def get_all(self) -> List[Application]:
        """
        Get all registered applications.
        
        Returns:
            List of Application entities
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT app_id, app_name, app_type, data_path, last_scan FROM applications")
            rows = cursor.fetchall()
            
            return [
                Application(
                    app_id=row[0],
                    app_name=row[1],
                    app_type=row[2],
                    data_path=row[3],
                    last_scan=datetime.fromisoformat(row[4])
                )
                for row in rows
            ]
        finally:
            conn.close()
    
    def exists(self, app_id: str) -> bool:
        """
        Check if application exists.
        
        Args:
            app_id: Application identifier
            
        Returns:
            True if application exists, False otherwise
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT 1 FROM applications WHERE app_id = ? LIMIT 1",
                (app_id,)
            )
            return cursor.fetchone() is not None
        finally:
            conn.close()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        return sqlite3.connect(self._db_path)
    
    def _init_database(self) -> None:
        """Initialize database schema"""
        # Ensure parent directory exists
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS applications (
                    app_id TEXT PRIMARY KEY,
                    app_name TEXT NOT NULL,
                    app_type TEXT NOT NULL,
                    data_path TEXT NOT NULL,
                    last_scan TEXT NOT NULL
                )
                """
            )
            conn.commit()
        finally:
            conn.close()
