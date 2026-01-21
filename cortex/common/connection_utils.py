"""
cortex/common/connection_utils.py

Unified connection management utilities with context managers and decorators.

AC-REM-002-02: Consolidates connection cleanup patterns across codebase.
"""

import functools
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Iterator, List, Optional, Tuple, TypeVar, Union


T = TypeVar('T')


class ConnectionContext:
    """Context manager for SQLite database operations.
    
    Provides a clean interface for database operations with automatic
    commit on success and rollback on failure.
    
    Example:
        with ConnectionContext(db_path) as ctx:
            ctx.execute("INSERT INTO table (col) VALUES (?)", ("value",))
            results = ctx.query("SELECT * FROM table")
    """
    
    def __init__(
        self,
        database_path: Union[str, Path],
        isolation_level: Optional[str] = None,
        timeout: float = 30.0,
    ) -> None:
        """Initialize connection context.
        
        Args:
            database_path: Path to SQLite database
            isolation_level: Transaction isolation level
            timeout: Connection timeout in seconds
        """
        self.database_path = Path(database_path)
        self.isolation_level = isolation_level
        self.timeout = timeout
        self._connection: Optional[sqlite3.Connection] = None
        self._cursor: Optional[sqlite3.Cursor] = None
    
    def __enter__(self) -> 'ConnectionContext':
        """Enter context, open connection."""
        self._connection = sqlite3.connect(
            str(self.database_path),
            isolation_level=self.isolation_level,
            timeout=self.timeout,
        )
        self._cursor = self._connection.cursor()
        return self
    
    def __exit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[Exception],
        exc_tb: Optional[Any],
    ) -> bool:
        """Exit context, commit or rollback."""
        if self._cursor:
            self._cursor.close()
            self._cursor = None
        
        if self._connection:
            if exc_type is None:
                # No exception - commit
                self._connection.commit()
            else:
                # Exception occurred - rollback
                self._connection.rollback()
            self._connection.close()
            self._connection = None
        
        return False  # Don't suppress exceptions
    
    def execute(
        self,
        sql: str,
        parameters: Optional[Tuple[Any, ...]] = None,
    ) -> sqlite3.Cursor:
        """Execute SQL statement.
        
        Args:
            sql: SQL statement
            parameters: Optional parameters tuple
            
        Returns:
            Cursor with results
        """
        if self._cursor is None:
            raise RuntimeError("ConnectionContext not entered")
        
        if parameters:
            return self._cursor.execute(sql, parameters)
        return self._cursor.execute(sql)
    
    def executemany(
        self,
        sql: str,
        parameters: List[Tuple[Any, ...]],
    ) -> sqlite3.Cursor:
        """Execute SQL with multiple parameter sets.
        
        Args:
            sql: SQL statement with placeholders
            parameters: List of parameter tuples
            
        Returns:
            Cursor
        """
        if self._cursor is None:
            raise RuntimeError("ConnectionContext not entered")
        
        return self._cursor.executemany(sql, parameters)
    
    def query(
        self,
        sql: str,
        parameters: Optional[Tuple[Any, ...]] = None,
    ) -> List[Tuple[Any, ...]]:
        """Execute query and return all results.
        
        Args:
            sql: SELECT statement
            parameters: Optional parameters
            
        Returns:
            List of result tuples
        """
        cursor = self.execute(sql, parameters)
        return cursor.fetchall()
    
    def query_one(
        self,
        sql: str,
        parameters: Optional[Tuple[Any, ...]] = None,
    ) -> Optional[Tuple[Any, ...]]:
        """Execute query and return first result.
        
        Args:
            sql: SELECT statement
            parameters: Optional parameters
            
        Returns:
            Single result tuple or None
        """
        cursor = self.execute(sql, parameters)
        return cursor.fetchone()


class TransactionContext(ConnectionContext):
    """Extended connection context with explicit transaction control.
    
    Provides savepoint support and explicit commit/rollback methods.
    
    Example:
        with TransactionContext(db_path, auto_commit=False) as tx:
            tx.execute("INSERT ...")
            tx.savepoint("sp1")
            tx.execute("UPDATE ...")
            tx.rollback_to_savepoint("sp1")
            tx.commit()
    """
    
    def __init__(
        self,
        database_path: Union[str, Path],
        auto_commit: bool = True,
        isolation_level: Optional[str] = None,
        timeout: float = 30.0,
    ) -> None:
        """Initialize transaction context.
        
        Args:
            database_path: Path to SQLite database
            auto_commit: If True, commit on successful exit
            isolation_level: Transaction isolation level
            timeout: Connection timeout
        """
        super().__init__(database_path, isolation_level, timeout)
        self.auto_commit = auto_commit
        self._committed = False
        self._rolledback = False
    
    def __exit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[Exception],
        exc_tb: Optional[Any],
    ) -> bool:
        """Exit context with conditional commit."""
        if self._cursor:
            self._cursor.close()
            self._cursor = None
        
        if self._connection:
            if exc_type is None and self.auto_commit and not self._committed and not self._rolledback:
                self._connection.commit()
            elif exc_type is not None and not self._rolledback:
                self._connection.rollback()
            self._connection.close()
            self._connection = None
        
        return False
    
    def commit(self) -> None:
        """Explicitly commit transaction."""
        if self._connection:
            self._connection.commit()
            self._committed = True
    
    def rollback(self) -> None:
        """Explicitly rollback transaction."""
        if self._connection:
            self._connection.rollback()
            self._rolledback = True
    
    def savepoint(self, name: str) -> None:
        """Create a savepoint.
        
        Args:
            name: Savepoint name
        """
        self.execute(f"SAVEPOINT {name}")
    
    def rollback_to_savepoint(self, name: str) -> None:
        """Rollback to a savepoint.
        
        Args:
            name: Savepoint name to rollback to
        """
        self.execute(f"ROLLBACK TO SAVEPOINT {name}")
    
    def release_savepoint(self, name: str) -> None:
        """Release a savepoint.
        
        Args:
            name: Savepoint name to release
        """
        self.execute(f"RELEASE SAVEPOINT {name}")


def managed_connection(
    database_path: Union[str, Path],
    auto_commit: bool = True,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator for functions that need a database cursor.
    
    Provides cursor as first argument, handles connection lifecycle.
    
    Args:
        database_path: Path to SQLite database
        auto_commit: If True, commit on success
        
    Returns:
        Decorator function
        
    Example:
        @managed_connection(Path("db.sqlite"))
        def insert_record(cursor, value):
            cursor.execute("INSERT INTO table (col) VALUES (?)", (value,))
            return cursor.lastrowid
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            db_path = Path(database_path)
            
            with sqlite3.connect(str(db_path)) as conn:
                cursor = conn.cursor()
                try:
                    result = func(cursor, *args, **kwargs)
                    if auto_commit:
                        conn.commit()
                    return result
                except Exception:
                    conn.rollback()
                    raise
                finally:
                    cursor.close()
        
        return wrapper
    return decorator


@contextmanager
def database_connection(
    database_path: Union[str, Path],
    isolation_level: Optional[str] = None,
) -> Iterator[sqlite3.Connection]:
    """Context manager yielding raw SQLite connection.
    
    For cases where full Connection control is needed.
    
    Args:
        database_path: Path to database
        isolation_level: Transaction isolation level
        
    Yields:
        SQLite connection object
    """
    conn = sqlite3.connect(str(database_path), isolation_level=isolation_level)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
