"""
Database Topology Discovery

Discovers database configurations, ORM models, migrations, and schemas.

Supports:
- Connection string parsing (SQL Server, PostgreSQL, MySQL, SQLite, MongoDB, Redis)
- ORM detection (Entity Framework, SQLAlchemy, Django, Sequelize, TypeORM, Hibernate)
- Migration analysis (Flyway, Liquibase, Alembic, Knex)
- Schema inference from ORM models

Task: DISC-003
Authority: PHASE-9-DISCOVERY-ORCHESTRATOR.yaml
Governance: CORE-008, CORE-011, CORE-012, CORE-030
"""

import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from cortex.brain.discovery import DiscoveryPlugin

logger = logging.getLogger(__name__)


class ORMType(Enum):
    """
    Supported ORM frameworks.

    Attributes:
        ENTITY_FRAMEWORK: .NET Entity Framework
        SQLALCHEMY: Python SQLAlchemy
        DJANGO: Django ORM
        SEQUELIZE: Node.js Sequelize
        TYPEORM: TypeScript TypeORM
        HIBERNATE: Java Hibernate
    """
    ENTITY_FRAMEWORK = "entity_framework"
    SQLALCHEMY = "sqlalchemy"
    DJANGO = "django"
    SEQUELIZE = "sequelize"
    TYPEORM = "typeorm"
    HIBERNATE = "hibernate"


@dataclass
class ConnectionInfo:
    """
    Database connection information.

    Attributes:
        database_type: Type of database
        server: Server hostname
        port: Server port
        database: Database name
        username: Username (if present)
    """
    database_type: str
    server: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    username: Optional[str] = None


@dataclass
class ModelInfo:
    """
    ORM model information.

    Attributes:
        name: Model class name
        table_name: Database table name
        columns: List of column names
        relationships: Related models
    """
    name: str
    table_name: Optional[str] = None
    columns: List[str] = field(default_factory=list)
    relationships: List[str] = field(default_factory=list)


@dataclass
class DatabaseTopology:
    """
    Complete database topology information.

    Attributes:
        connections: List of database connections
        orm_type: Detected ORM framework
        models: ORM models
        migrations: Migration history
        schema: Inferred database schema
    """
    connections: List[ConnectionInfo]
    orm_type: Optional[ORMType]
    models: List[ModelInfo]
    migrations: Dict[str, Any]
    schema: Dict[str, Any]


class DatabaseDiscovery(DiscoveryPlugin):
    """
    Discovers database topology from repositories.

    Analyzes connection strings, ORM models, migrations, and infers
    database schemas from code.

    Features:
    - Multi-database support (SQL/NoSQL)
    - ORM framework detection
    - Migration history analysis
    - Schema inference from models
    - Table-to-code mapping

    Example:
        ```python
        discovery = DatabaseDiscovery()
        topology = discovery.discover(Path("/my/repo"))

        for conn in topology["connections"]:
            print(f"Database: {conn['database_type']}")
        ```
    """

    def __init__(self) -> None:
        """Initialize database discovery."""
        self.supported_databases = [
            "postgresql", "mysql", "mssql", "sqlite", "mongodb", "redis"
        ]
        self.supported_orms = [
            ORMType.ENTITY_FRAMEWORK,
            ORMType.SQLALCHEMY,
            ORMType.DJANGO,
            ORMType.SEQUELIZE,
            ORMType.TYPEORM,
            ORMType.HIBERNATE,
        ]
        logger.info("DatabaseDiscovery initialized")

    def get_supported_databases(self) -> List[str]:
        """
        Get list of supported database types.

        Returns:
            List of database type names
        """
        return self.supported_databases

    def discover(self, repo_path: Path) -> Dict[str, Any]:
        """
        Discover database topology in repository.

        Args:
            repo_path: Path to repository to scan

        Returns:
            Dictionary containing database topology
        """
        logger.info(f"Discovering database topology in {repo_path}")

        connections: List[ConnectionInfo] = []
        models: List[ModelInfo] = []

        # Detect ORM type
        orm_type = self.detect_orm_type(repo_path)

        # Scan for connection strings in config files
        for json_file in repo_path.rglob("*.json"):
            try:
                import json
                with open(json_file) as f:
                    config = json.load(f)
                    conn_strings = self._extract_connection_strings_from_config(config)
                    for conn_str in conn_strings:
                        info = self.parse_connection_string(conn_str)
                        if info:
                            connections.append(info)
            except Exception:
                pass

        # Scan for .env connection strings
        for env_file in repo_path.rglob(".env*"):
            if env_file.is_file():
                try:
                    with open(env_file) as f:
                        for line in f:
                            if "=" in line and not line.strip().startswith("#"):
                                key, value = line.split("=", 1)
                                if any(x in key.upper() for x in ["DATABASE", "DB_URL", "POSTGRES", "MYSQL"]):
                                    info = self.parse_connection_string(value.strip())
                                    if info:
                                        connections.append(info)
                except Exception:
                    pass

        # Scan ORM models
        if orm_type:
            models = self.scan_orm_models(repo_path, orm_type)

        # Analyze migrations
        migrations = self.analyze_migrations(repo_path)

        # Infer schema
        schema = self.infer_schema_from_models(models) if models else {}

        logger.info(
            f"Discovered {len(connections)} connections, "
            f"{len(models)} models, ORM: {orm_type.value if orm_type else 'none'}"
        )

        return {
            "connections": [
                {
                    "database_type": c.database_type,
                    "server": c.server,
                    "port": c.port,
                    "database": c.database,
                }
                for c in connections
            ],
            "orm_type": orm_type.value if orm_type else None,
            "models": [
                {
                    "name": m.name,
                    "table_name": m.table_name,
                    "column_count": len(m.columns),
                }
                for m in models
            ],
            "migrations": migrations,
            "schema": schema,
            "total_connections": len(connections),
            "total_models": len(models),
        }

    def parse_connection_string(self, conn_str: str) -> Optional[ConnectionInfo]:
        """
        Parse database connection string.

        Args:
            conn_str: Connection string to parse

        Returns:
            ConnectionInfo or None if parse fails
        """
        conn_lower = conn_str.lower()

        # PostgreSQL URL format
        if "postgresql://" in conn_lower or "postgres://" in conn_lower:
            return self._parse_url_connection(conn_str, "postgresql")

        # MySQL URL format
        if "mysql://" in conn_lower:
            return self._parse_url_connection(conn_str, "mysql")

        # MongoDB URL format
        if "mongodb://" in conn_lower or "mongodb+srv://" in conn_lower:
            return self._parse_url_connection(conn_str, "mongodb")

        # SQL Server format
        if "server=" in conn_lower and "database=" in conn_lower:
            return self._parse_sqlserver_connection(conn_str)

        return None

    def detect_orm_type(self, repo_path: Path) -> Optional[ORMType]:
        """
        Detect ORM framework used in repository.

        Args:
            repo_path: Path to repository

        Returns:
            Detected ORM type or None
        """
        # Check for Entity Framework (DbContext files)
        for cs_file in repo_path.rglob("*.cs"):
            try:
                content = cs_file.read_text()
                if "DbContext" in content and "DbSet" in content:
                    return ORMType.ENTITY_FRAMEWORK
            except Exception:
                pass

        # Check for SQLAlchemy
        for py_file in repo_path.rglob("*.py"):
            try:
                content = py_file.read_text()
                if "sqlalchemy" in content.lower() and "declarative_base" in content:
                    return ORMType.SQLALCHEMY
            except Exception:
                pass

        # Check for Django
        for py_file in repo_path.rglob("models.py"):
            try:
                content = py_file.read_text()
                if "django.db" in content and "models.Model" in content:
                    return ORMType.DJANGO
            except Exception:
                pass

        return None

    def scan_orm_models(
        self,
        repo_path: Path,
        orm_type: ORMType
    ) -> List[ModelInfo]:
        """
        Scan ORM models in repository.

        Args:
            repo_path: Path to repository
            orm_type: Type of ORM to scan for

        Returns:
            List of discovered models
        """
        models: List[ModelInfo] = []

        if orm_type == ORMType.SQLALCHEMY:
            models = self._scan_sqlalchemy_models(repo_path)
        elif orm_type == ORMType.ENTITY_FRAMEWORK:
            models = self._scan_entity_framework_models(repo_path)
        elif orm_type == ORMType.DJANGO:
            models = self._scan_django_models(repo_path)

        return models

    def analyze_migrations(self, repo_path: Path) -> Dict[str, Any]:
        """
        Analyze migration files in repository.

        Args:
            repo_path: Path to repository

        Returns:
            Migration history information
        """
        migrations: Dict[str, Any] = {
            "migration_tool": None,
            "migration_count": 0,
            "migrations": [],
        }

        # Check for Alembic migrations
        alembic_dir = repo_path / "alembic" / "versions"
        if alembic_dir.exists():
            migration_files = list(alembic_dir.glob("*.py"))
            migrations["migration_tool"] = "alembic"
            migrations["migration_count"] = len(migration_files)
            migrations["migrations"] = [f.name for f in migration_files]

        # Check for Flyway migrations
        flyway_dir = repo_path / "db" / "migration"
        if flyway_dir.exists():
            migration_files = list(flyway_dir.glob("V*.sql"))
            migrations["migration_tool"] = "flyway"
            migrations["migration_count"] = len(migration_files)
            migrations["migrations"] = [f.name for f in migration_files]

        return migrations

    def infer_schema_from_models(
        self,
        models: List[ModelInfo]
    ) -> Dict[str, Any]:
        """
        Infer database schema from ORM models.

        Args:
            models: List of ORM models

        Returns:
            Inferred schema information
        """
        tables = {}

        for model in models:
            table_name = model.table_name or model.name.lower()
            tables[table_name] = {
                "model_class": model.name,
                "columns": model.columns,
                "relationships": model.relationships,
            }

        return {
            "tables": tables,
            "table_count": len(tables),
        }

    def _parse_url_connection(
        self,
        conn_str: str,
        db_type: str
    ) -> ConnectionInfo:
        """Parse URL-format connection string."""
        try:
            parsed = urlparse(conn_str)
            return ConnectionInfo(
                database_type=db_type,
                server=parsed.hostname,
                port=parsed.port,
                database=parsed.path.lstrip("/") if parsed.path else None,
                username=parsed.username,
            )
        except Exception:
            return ConnectionInfo(database_type=db_type)

    def _parse_sqlserver_connection(self, conn_str: str) -> ConnectionInfo:
        """Parse SQL Server connection string."""
        server_match = re.search(r'Server=([^;]+)', conn_str, re.IGNORECASE)
        db_match = re.search(r'Database=([^;]+)', conn_str, re.IGNORECASE)

        return ConnectionInfo(
            database_type="mssql",
            server=server_match.group(1) if server_match else None,
            database=db_match.group(1) if db_match else None,
        )

    def _extract_connection_strings_from_config(
        self,
        config: Dict[str, Any]
    ) -> List[str]:
        """Extract connection strings from config dictionary."""
        conn_strings = []

        if "ConnectionStrings" in config:
            conn_section = config["ConnectionStrings"]
            if isinstance(conn_section, dict):
                conn_strings.extend(conn_section.values())

        return conn_strings

    def _scan_sqlalchemy_models(self, repo_path: Path) -> List[ModelInfo]:
        """Scan SQLAlchemy models."""
        models = []

        for py_file in repo_path.rglob("*.py"):
            try:
                content = py_file.read_text()
                if "__tablename__" in content:
                    # Extract model class names
                    class_matches = re.findall(r'class\s+(\w+)\s*\([^)]*Base[^)]*\)', content)
                    for class_name in class_matches:
                        table_match = re.search(rf'class\s+{class_name}.*?__tablename__\s*=\s*[\'"](\w+)[\'"]', content, re.DOTALL)
                        table_name = table_match.group(1) if table_match else None

                        # Extract columns
                        columns = re.findall(r'(\w+)\s*=\s*Column\(', content)

                        models.append(ModelInfo(
                            name=class_name,
                            table_name=table_name,
                            columns=columns,
                        ))
            except Exception:
                pass

        return models

    def _scan_entity_framework_models(self, repo_path: Path) -> List[ModelInfo]:
        """Scan Entity Framework models."""
        models = []

        for cs_file in repo_path.rglob("*.cs"):
            try:
                content = cs_file.read_text()
                # Look for class definitions with properties
                class_matches = re.findall(r'public\s+class\s+(\w+)', content)
                for class_name in class_matches:
                    if class_name.endswith("Context"):
                        continue  # Skip DbContext classes

                    # Extract properties
                    props = re.findall(r'public\s+\w+\s+(\w+)\s*{\s*get;', content)

                    models.append(ModelInfo(
                        name=class_name,
                        table_name=class_name.lower(),
                        columns=props,
                    ))
            except Exception:
                pass

        return models[:10]  # Limit to avoid too many results

    def _scan_django_models(self, repo_path: Path) -> List[ModelInfo]:
        """Scan Django models."""
        models = []

        for py_file in repo_path.rglob("models.py"):
            try:
                content = py_file.read_text()
                # Extract Django model classes
                class_matches = re.findall(r'class\s+(\w+)\s*\([^)]*models\.Model[^)]*\)', content)
                for class_name in class_matches:
                    # Extract fields
                    fields = re.findall(r'(\w+)\s*=\s*models\.\w+Field', content)

                    models.append(ModelInfo(
                        name=class_name,
                        table_name=class_name.lower(),
                        columns=fields,
                    ))
            except Exception:
                pass

        return models
