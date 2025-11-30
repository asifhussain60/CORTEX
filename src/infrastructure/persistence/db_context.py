"""
Database Context for managing database connections and transactions
"""

import aiosqlite
from typing import Optional
from pathlib import Path


class DatabaseContext:
    """
    Database context for SQLite with transaction support.
    
    Manages database connections, transactions, and session lifecycle.
    
    Example:
        async with DatabaseContext("cortex.db") as db:
            cursor = await db.execute("SELECT * FROM conversations")
            rows = await cursor.fetchall()
    """
    
    def __init__(self, database_path: str):
        """
        Initialize database context.
        
        Args:
            database_path: Path to SQLite database file
        """
        self.database_path = database_path
        self._connection: Optional[aiosqlite.Connection] = None
        self._in_transaction = False
    
    async def connect(self) -> None:
        """Establish database connection"""
        if self._connection is None:
            self._connection = await aiosqlite.connect(self.database_path)
            # Enable foreign keys
            await self._connection.execute("PRAGMA foreign_keys = ON")
            # Use Row factory for dict-like access
            self._connection.row_factory = aiosqlite.Row
    
    async def begin(self) -> None:
        """Begin a transaction"""
        if not self._in_transaction:
            await self.connect()
            await self._connection.execute("BEGIN TRANSACTION")
            self._in_transaction = True
    
    async def commit(self) -> None:
        """Commit the current transaction"""
        if self._in_transaction and self._connection:
            await self._connection.commit()
            self._in_transaction = False
    
    async def rollback(self) -> None:
        """Rollback the current transaction"""
        if self._in_transaction and self._connection:
            await self._connection.rollback()
            self._in_transaction = False
    
    async def execute(self, sql: str, parameters: tuple = ()):
        """
        Execute a SQL statement.
        
        Args:
            sql: SQL statement to execute
            parameters: Parameters for parameterized query
            
        Returns:
            Cursor object with results
        """
        await self.connect()
        return await self._connection.execute(sql, parameters)
    
    async def execute_many(self, sql: str, parameters_list: list):
        """
        Execute a SQL statement multiple times with different parameters.
        
        Args:
            sql: SQL statement to execute
            parameters_list: List of parameter tuples
        """
        await self.connect()
        await self._connection.executemany(sql, parameters_list)
    
    async def fetch_one(self, sql: str, parameters: tuple = ()):
        """
        Execute query and fetch one result.
        
        Args:
            sql: SQL query to execute
            parameters: Parameters for parameterized query
            
        Returns:
            Single row result or None
        """
        cursor = await self.execute(sql, parameters)
        return await cursor.fetchone()
    
    async def fetch_all(self, sql: str, parameters: tuple = ()):
        """
        Execute query and fetch all results.
        
        Args:
            sql: SQL query to execute
            parameters: Parameters for parameterized query
            
        Returns:
            List of row results
        """
        cursor = await self.execute(sql, parameters)
        return await cursor.fetchall()
    
    async def close(self) -> None:
        """Close database connection"""
        if self._connection:
            if self._in_transaction:
                await self.rollback()
            await self._connection.close()
            self._connection = None
    
    async def __aenter__(self):
        """Enter context manager"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager"""
        await self.close()


class ConnectionFactory:
    """
    Factory for creating database connections.
    
    Provides centralized connection configuration and pooling.
    """
    
    def __init__(self, database_path: str):
        """
        Initialize connection factory.
        
        Args:
            database_path: Path to SQLite database file
        """
        self.database_path = database_path
        self._ensure_database_exists()
    
    def _ensure_database_exists(self) -> None:
        """Create database file if it doesn't exist"""
        db_path = Path(self.database_path)
        if not db_path.exists():
            db_path.parent.mkdir(parents=True, exist_ok=True)
            db_path.touch()
    
    def create_context(self) -> DatabaseContext:
        """
        Create a new database context.
        
        Returns:
            DatabaseContext instance
        """
        return DatabaseContext(self.database_path)
    
    async def create_unit_of_work(self):
        """
        Create a new Unit of Work.
        
        Returns:
            UnitOfWork instance
        """
        from .unit_of_work import UnitOfWork
        context = self.create_context()
        return UnitOfWork(context)
