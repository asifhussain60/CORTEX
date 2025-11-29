"""
Tests for Database Context
"""

import pytest
import tempfile
import os
from pathlib import Path

from src.infrastructure.persistence.db_context import DatabaseContext, ConnectionFactory


class TestDatabaseContext:
    """Test suite for DatabaseContext"""
    
    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.db') as f:
            db_path = f.name
        
        yield db_path
        
        # Cleanup
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    @pytest.mark.asyncio
    async def test_database_context_creation(self, temp_db):
        """Test creating a database context"""
        context = DatabaseContext(temp_db)
        
        assert context.database_path == temp_db
        assert context._connection is None
        assert context._in_transaction is False
    
    @pytest.mark.asyncio
    async def test_connect_establishes_connection(self, temp_db):
        """Test connect establishes database connection"""
        context = DatabaseContext(temp_db)
        
        await context.connect()
        
        assert context._connection is not None
        
        await context.close()
    
    @pytest.mark.asyncio
    async def test_begin_transaction(self, temp_db):
        """Test beginning a transaction"""
        context = DatabaseContext(temp_db)
        
        await context.begin()
        
        assert context._in_transaction is True
        assert context._connection is not None
        
        await context.close()
    
    @pytest.mark.asyncio
    async def test_commit_transaction(self, temp_db):
        """Test committing a transaction"""
        context = DatabaseContext(temp_db)
        
        await context.begin()
        await context.commit()
        
        assert context._in_transaction is False
        
        await context.close()
    
    @pytest.mark.asyncio
    async def test_rollback_transaction(self, temp_db):
        """Test rolling back a transaction"""
        context = DatabaseContext(temp_db)
        
        await context.begin()
        await context.rollback()
        
        assert context._in_transaction is False
        
        await context.close()
    
    @pytest.mark.asyncio
    async def test_execute_sql(self, temp_db):
        """Test executing SQL statement"""
        context = DatabaseContext(temp_db)
        
        # Create test table
        await context.execute("""
            CREATE TABLE test_table (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            )
        """)
        
        # Insert data
        await context.execute(
            "INSERT INTO test_table (id, name) VALUES (?, ?)",
            (1, "Test")
        )
        
        await context.close()
    
    @pytest.mark.asyncio
    async def test_fetch_one(self, temp_db):
        """Test fetching one result"""
        context = DatabaseContext(temp_db)
        
        # Create and populate table
        await context.execute("""
            CREATE TABLE test_table (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            )
        """)
        
        await context.execute(
            "INSERT INTO test_table (id, name) VALUES (?, ?)",
            (1, "Test")
        )
        
        # Fetch one
        result = await context.fetch_one("SELECT * FROM test_table WHERE id = ?", (1,))
        
        assert result is not None
        assert result['id'] == 1
        assert result['name'] == "Test"
        
        await context.close()
    
    @pytest.mark.asyncio
    async def test_fetch_all(self, temp_db):
        """Test fetching all results"""
        context = DatabaseContext(temp_db)
        
        # Create and populate table
        await context.execute("""
            CREATE TABLE test_table (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            )
        """)
        
        await context.execute_many(
            "INSERT INTO test_table (id, name) VALUES (?, ?)",
            [(1, "Test1"), (2, "Test2"), (3, "Test3")]
        )
        
        # Fetch all
        results = await context.fetch_all("SELECT * FROM test_table")
        
        assert len(results) == 3
        assert results[0]['name'] == "Test1"
        assert results[1]['name'] == "Test2"
        assert results[2]['name'] == "Test3"
        
        await context.close()
    
    @pytest.mark.asyncio
    async def test_context_manager(self, temp_db):
        """Test using context as context manager"""
        async with DatabaseContext(temp_db) as context:
            assert context._connection is not None
            
            await context.execute("""
                CREATE TABLE test_table (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL
                )
            """)
        
        # Connection should be closed after exiting context
        assert context._connection is None
    
    @pytest.mark.asyncio
    async def test_close_closes_connection(self, temp_db):
        """Test close closes the database connection"""
        context = DatabaseContext(temp_db)
        
        await context.connect()
        assert context._connection is not None
        
        await context.close()
        assert context._connection is None


class TestConnectionFactory:
    """Test suite for ConnectionFactory"""
    
    @pytest.fixture
    def temp_db_path(self):
        """Get temporary database path"""
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "test.db")
        
        yield db_path
        
        # Cleanup
        if os.path.exists(db_path):
            os.unlink(db_path)
        os.rmdir(temp_dir)
    
    def test_connection_factory_creation(self, temp_db_path):
        """Test creating a connection factory"""
        factory = ConnectionFactory(temp_db_path)
        
        assert factory.database_path == temp_db_path
        assert os.path.exists(temp_db_path)
    
    def test_create_context(self, temp_db_path):
        """Test creating database context from factory"""
        factory = ConnectionFactory(temp_db_path)
        
        context = factory.create_context()
        
        assert context is not None
        assert isinstance(context, DatabaseContext)
        assert context.database_path == temp_db_path
    
    @pytest.mark.asyncio
    async def test_create_unit_of_work(self, temp_db_path):
        """Test creating Unit of Work from factory"""
        factory = ConnectionFactory(temp_db_path)
        
        uow = await factory.create_unit_of_work()
        
        assert uow is not None
        from src.infrastructure.persistence.unit_of_work import UnitOfWork
        assert isinstance(uow, UnitOfWork)
