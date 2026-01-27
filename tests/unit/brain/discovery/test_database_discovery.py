"""
Tests for Database Topology Discovery.

Task: DISC-003
Authority: PHASE-9-DISCOVERY-ORCHESTRATOR.yaml
Governance: CORE-008 (TDD - tests before implementation)

Test Coverage:
1. Parse SQL Server connection strings
2. Parse PostgreSQL connection strings  
3. Detect Entity Framework models
4. Detect SQLAlchemy models
5. Scan Flyway migrations
6. Scan Alembic migrations
7. Infer schema from ORM models
8. Handle multiple databases in same repo
"""

import pytest
from pathlib import Path
from typing import Dict, Any

from cortex.brain.discovery.database_discovery import (
    DatabaseDiscovery,
    ConnectionInfo,
    ORMType,
    ModelInfo,
    DatabaseTopology,
)


class TestDatabaseDiscoveryInit:
    """Test DatabaseDiscovery initialization."""
    
    def test_init_creates_discovery(self) -> None:
        """Test discovery can be instantiated."""
        discovery = DatabaseDiscovery()
        assert discovery is not None
    
    def test_supported_databases_defined(self) -> None:
        """Test supported database types are defined."""
        discovery = DatabaseDiscovery()
        dbs = discovery.get_supported_databases()
        
        assert "postgresql" in dbs
        assert "mysql" in dbs
        assert "mssql" in dbs
        assert "sqlite" in dbs
        assert "mongodb" in dbs


class TestConnectionStringParsing:
    """Test connection string parsing."""
    
    def test_parse_sql_server_connection_string(self) -> None:
        """Test parsing SQL Server connection string."""
        conn_str = "Server=myserver;Database=mydb;User Id=sa;Password=secret"
        
        discovery = DatabaseDiscovery()
        info = discovery.parse_connection_string(conn_str)
        
        assert info.server == "myserver"
        assert info.database == "mydb"
        assert info.database_type == "mssql"
    
    def test_parse_postgresql_connection_string(self) -> None:
        """Test parsing PostgreSQL connection string."""
        conn_str = "postgresql://user:pass@localhost:5432/testdb"
        
        discovery = DatabaseDiscovery()
        info = discovery.parse_connection_string(conn_str)
        
        assert info.server == "localhost"
        assert info.database == "testdb"
        assert info.database_type == "postgresql"
        assert info.port == 5432
    
    def test_parse_mysql_connection_string(self) -> None:
        """Test parsing MySQL connection string."""
        conn_str = "mysql://root:password@localhost:3306/mydb"
        
        discovery = DatabaseDiscovery()
        info = discovery.parse_connection_string(conn_str)
        
        assert info.server == "localhost"
        assert info.database == "mydb"
        assert info.database_type == "mysql"
        assert info.port == 3306


class TestORMDetection:
    """Test ORM framework detection."""
    
    def test_detect_entity_framework(self, tmp_path: Path) -> None:
        """Test detecting Entity Framework models."""
        # Create DbContext file
        dbcontext_file = tmp_path / "ApplicationDbContext.cs"
        dbcontext_file.write_text(
            "public class ApplicationDbContext : DbContext\n"
            "{\n"
            "    public DbSet<User> Users { get; set; }\n"
            "}\n"
        )
        
        discovery = DatabaseDiscovery()
        orm_type = discovery.detect_orm_type(tmp_path)
        
        assert orm_type == ORMType.ENTITY_FRAMEWORK
    
    def test_detect_sqlalchemy(self, tmp_path: Path) -> None:
        """Test detecting SQLAlchemy models."""
        # Create SQLAlchemy model file
        model_file = tmp_path / "models.py"
        model_file.write_text(
            "from sqlalchemy import Column, Integer, String\n"
            "from sqlalchemy.ext.declarative import declarative_base\n"
            "Base = declarative_base()\n"
            "class User(Base):\n"
            "    __tablename__ = 'users'\n"
            "    id = Column(Integer, primary_key=True)\n"
        )
        
        discovery = DatabaseDiscovery()
        orm_type = discovery.detect_orm_type(tmp_path)
        
        assert orm_type == ORMType.SQLALCHEMY
    
    def test_detect_django_orm(self, tmp_path: Path) -> None:
        """Test detecting Django ORM."""
        # Create Django models file
        model_file = tmp_path / "models.py"
        model_file.write_text(
            "from django.db import models\n"
            "class User(models.Model):\n"
            "    name = models.CharField(max_length=100)\n"
        )
        
        discovery = DatabaseDiscovery()
        orm_type = discovery.detect_orm_type(tmp_path)
        
        assert orm_type == ORMType.DJANGO


class TestModelScanning:
    """Test ORM model scanning."""
    
    def test_scan_sqlalchemy_models(self, tmp_path: Path) -> None:
        """Test scanning SQLAlchemy models."""
        model_file = tmp_path / "models.py"
        model_file.write_text(
            "from sqlalchemy import Column, Integer, String\n"
            "class User(Base):\n"
            "    __tablename__ = 'users'\n"
            "    id = Column(Integer, primary_key=True)\n"
            "    name = Column(String)\n"
        )
        
        discovery = DatabaseDiscovery()
        models = discovery.scan_orm_models(tmp_path, ORMType.SQLALCHEMY)
        
        assert len(models) > 0
        assert any(m.name == "User" for m in models)
    
    def test_scan_entity_framework_models(self, tmp_path: Path) -> None:
        """Test scanning Entity Framework models."""
        model_file = tmp_path / "User.cs"
        model_file.write_text(
            "public class User\n"
            "{\n"
            "    public int Id { get; set; }\n"
            "    public string Name { get; set; }\n"
            "}\n"
        )
        
        discovery = DatabaseDiscovery()
        models = discovery.scan_orm_models(tmp_path, ORMType.ENTITY_FRAMEWORK)
        
        assert len(models) > 0


class TestMigrationAnalysis:
    """Test migration file analysis."""
    
    def test_analyze_alembic_migrations(self, tmp_path: Path) -> None:
        """Test analyzing Alembic migrations."""
        migrations_dir = tmp_path / "alembic" / "versions"
        migrations_dir.mkdir(parents=True)
        
        (migrations_dir / "001_initial.py").write_text(
            "def upgrade():\n    op.create_table('users')\n"
        )
        (migrations_dir / "002_add_email.py").write_text(
            "def upgrade():\n    op.add_column('users', 'email')\n"
        )
        
        discovery = DatabaseDiscovery()
        history = discovery.analyze_migrations(tmp_path)
        
        assert history["migration_count"] >= 2
        assert history["migration_tool"] == "alembic"
    
    def test_analyze_flyway_migrations(self, tmp_path: Path) -> None:
        """Test analyzing Flyway migrations."""
        migrations_dir = tmp_path / "db" / "migration"
        migrations_dir.mkdir(parents=True)
        
        (migrations_dir / "V1__initial.sql").write_text("CREATE TABLE users;")
        (migrations_dir / "V2__add_email.sql").write_text("ALTER TABLE users ADD email VARCHAR;")
        
        discovery = DatabaseDiscovery()
        history = discovery.analyze_migrations(tmp_path)
        
        assert history["migration_count"] >= 2
        assert history["migration_tool"] == "flyway"


class TestSchemaInference:
    """Test schema inference from models."""
    
    def test_infer_schema_from_models(self) -> None:
        """Test inferring database schema from ORM models."""
        models = [
            ModelInfo(name="User", table_name="users", columns=["id", "name", "email"]),
            ModelInfo(name="Post", table_name="posts", columns=["id", "user_id", "title"]),
        ]
        
        discovery = DatabaseDiscovery()
        schema = discovery.infer_schema_from_models(models)
        
        assert "users" in schema["tables"]
        assert "posts" in schema["tables"]
        assert len(schema["tables"]) == 2


class TestFullDiscovery:
    """Test complete database discovery."""
    
    def test_discover_multiple_databases(self, tmp_path: Path) -> None:
        """Test discovering multiple databases in repo."""
        # Create config with multiple connections
        config_file = tmp_path / "appsettings.json"
        config_file.write_text(
            '{"ConnectionStrings": {'
            '"PostgresDB": "postgresql://localhost/db1",'
            '"MySQLDB": "mysql://localhost/db2"'
            '}}'
        )
        
        discovery = DatabaseDiscovery()
        topology = discovery.discover(tmp_path)
        
        assert isinstance(topology, dict)
        assert "databases" in topology or "connections" in topology
    
    def test_discover_handles_no_databases(self, tmp_path: Path) -> None:
        """Test discovery handles repos with no databases."""
        # Empty directory
        discovery = DatabaseDiscovery()
        topology = discovery.discover(tmp_path)
        
        assert isinstance(topology, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
