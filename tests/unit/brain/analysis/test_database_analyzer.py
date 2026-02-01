"""
Tests for DatabaseAnalyzer - Migration and schema analysis.

AC-ID: AC-LENS-V2-DATABASE-TEST-001
Authority: CORE-008 (TDD)
"""

import pytest
from pathlib import Path
from cortex.brain.analysis.database_analyzer import (
    DatabaseAnalyzer,
    get_database_analyzer,
    MigrationType,
    ColumnInfo,
    TableInfo,
    MigrationInfo,
    DatabaseAnalysisResult,
)


class TestDatabaseAnalyzer:
    """Test suite for DatabaseAnalyzer."""
    
    def test_initialization(self):
        """Test DatabaseAnalyzer initialization."""
        analyzer = DatabaseAnalyzer()
        assert analyzer is not None
    
    def test_singleton_pattern(self):
        """Test singleton pattern for get_database_analyzer()."""
        analyzer1 = get_database_analyzer()
        analyzer2 = get_database_analyzer()
        assert analyzer1 is analyzer2
    
    def test_migration_type_enum(self):
        """Test MigrationType enum values."""
        assert MigrationType.ALEMBIC.value == "alembic"
        assert MigrationType.FLYWAY.value == "flyway"
        assert MigrationType.DJANGO.value == "django"
        assert MigrationType.EF_CORE.value == "ef_core"
        assert MigrationType.UNKNOWN.value == "unknown"
    
    def test_column_info_dataclass(self):
        """Test ColumnInfo dataclass."""
        column = ColumnInfo(
            name="user_id",
            type="INTEGER",
            nullable=False,
            primary_key=True,
            foreign_key=None,
            default=None
        )
        assert column.name == "user_id"
        assert column.type == "INTEGER"
        assert not column.nullable
        assert column.primary_key
        assert column.foreign_key is None
    
    def test_table_info_dataclass(self):
        """Test TableInfo dataclass."""
        table = TableInfo(
            name="users",
            schema="public",
            columns=[
                ColumnInfo(name="id", type="INTEGER", primary_key=True, nullable=False),
                ColumnInfo(name="email", type="VARCHAR", nullable=False),
            ],
            primary_keys=["id"],
            foreign_keys={},
            indexes=["idx_email"]
        )
        assert table.name == "users"
        assert len(table.columns) == 2
        assert table.primary_keys == ["id"]
        assert table.indexes == ["idx_email"]
    
    def test_migration_info_dataclass(self):
        """Test MigrationInfo dataclass."""
        migration = MigrationInfo(
            file_path="/migrations/001_initial.py",
            version="001",
            description="Initial migration",
            migration_type=MigrationType.ALEMBIC,
            operations=["CREATE TABLE"],
            is_reversible=True
        )
        assert migration.version == "001"
        assert migration.description == "Initial migration"
        assert migration.migration_type == MigrationType.ALEMBIC
        assert migration.is_reversible
    
    def test_analyze_migrations_nonexistent_path(self):
        """Test analyze_migrations with nonexistent path."""
        analyzer = DatabaseAnalyzer()
        # Use a clearly nonexistent absolute path
        result = analyzer.analyze_migrations(Path("C:/___NONEXISTENT_XYZ_ABC___/path"))
        
        assert not result.success
        assert "not found" in result.error.lower()
        assert len(result.migrations) == 0
    
    def test_analyze_migrations_empty_directory(self, tmp_path):
        """Test analyze_migrations with empty directory."""
        analyzer = DatabaseAnalyzer()
        result = analyzer.analyze_migrations(tmp_path)
        
        assert result.success
        assert len(result.migrations) == 0
        assert result.analysis_time_ms > 0
    
    def test_detect_alembic_migration_type(self, tmp_path):
        """Test auto-detection of Alembic migrations."""
        # Create Alembic-style file
        (tmp_path / "alembic_version.py").write_text(
            'revision = "001"\ndown_revision = None'
        )
        
        analyzer = DatabaseAnalyzer()
        migration_type = analyzer._detect_migration_type(tmp_path)
        
        assert migration_type == MigrationType.ALEMBIC
    
    def test_detect_django_migration_type(self, tmp_path):
        """Test auto-detection of Django migrations."""
        # Create Django-style files
        (tmp_path / "__init__.py").write_text("")
        (tmp_path / "0001_initial.py").write_text(
            "dependencies = []\noperations = []"
        )
        
        analyzer = DatabaseAnalyzer()
        migration_type = analyzer._detect_migration_type(tmp_path)
        
        assert migration_type == MigrationType.DJANGO
    
    def test_detect_flyway_migration_type(self, tmp_path):
        """Test auto-detection of Flyway migrations."""
        # Create Flyway-style SQL file
        (tmp_path / "V001__initial.sql").write_text("CREATE TABLE users;")
        
        analyzer = DatabaseAnalyzer()
        migration_type = analyzer._detect_migration_type(tmp_path)
        
        assert migration_type == MigrationType.FLYWAY
    
    def test_parse_alembic_migration(self, tmp_path):
        """Test parsing Alembic migration file."""
        migration_content = '''"""Create users table"""
revision = "abc123"
down_revision = None

def upgrade():
    op.create_table("users")
    op.add_column("users", "email")

def downgrade():
    op.drop_table("users")
'''
        (tmp_path / "abc123_create_users.py").write_text(migration_content)
        
        analyzer = DatabaseAnalyzer()
        result = analyzer.analyze_migrations(tmp_path, MigrationType.ALEMBIC)
        
        assert result.success
        assert len(result.migrations) == 1
        
        migration = result.migrations[0]
        assert migration.version == "abc123"
        assert "Create users table" in migration.description
        assert migration.is_reversible
        assert "CREATE TABLE" in migration.operations
        assert "ADD COLUMN" in migration.operations
    
    def test_parse_django_migration(self, tmp_path):
        """Test parsing Django migration file."""
        migration_content = '''
dependencies = [("auth", "0001_initial")]

operations = [
    migrations.CreateModel(
        name="User",
        fields=[],
    ),
    migrations.AddField(
        model_name="user",
        name="email",
    ),
]
'''
        (tmp_path / "__init__.py").write_text("")
        (tmp_path / "0001_initial.py").write_text(migration_content)
        
        analyzer = DatabaseAnalyzer()
        result = analyzer.analyze_migrations(tmp_path, MigrationType.DJANGO)
        
        assert result.success
        assert len(result.migrations) == 1
        
        migration = result.migrations[0]
        assert migration.version == "0001_initial"
        assert migration.is_reversible  # Django migrations are reversible by default
        assert "CREATE MODEL" in migration.operations
        assert "ADD FIELD" in migration.operations
    
    def test_parse_flyway_migration(self, tmp_path):
        """Test parsing Flyway migration file."""
        migration_content = '''
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email VARCHAR(255) NOT NULL
);

CREATE INDEX idx_email ON users(email);
'''
        (tmp_path / "V001__create_users.sql").write_text(migration_content)
        
        analyzer = DatabaseAnalyzer()
        result = analyzer.analyze_migrations(tmp_path, MigrationType.FLYWAY)
        
        assert result.success
        assert len(result.migrations) == 1
        
        migration = result.migrations[0]
        assert migration.version == "001"
        assert "Create Users" in migration.description
        assert not migration.is_reversible  # Flyway not reversible by default
        assert "CREATE TABLE" in migration.operations
        assert "CREATE INDEX" in migration.operations
    
    def test_migration_recommendations_non_reversible(self, tmp_path):
        """Test recommendations for non-reversible migrations."""
        # Create non-reversible migration
        (tmp_path / "V001__initial.sql").write_text("CREATE TABLE users;")
        
        analyzer = DatabaseAnalyzer()
        result = analyzer.analyze_migrations(tmp_path, MigrationType.FLYWAY)
        
        assert result.success
        assert len(result.recommendations) > 0
        
        # Should recommend adding reversibility
        reversibility_rec = [
            r for r in result.recommendations 
            if r["category"] == "migration_reversibility"
        ]
        assert len(reversibility_rec) > 0
        assert reversibility_rec[0]["priority"] == "P2"
    
    def test_migration_recommendations_large_count(self, tmp_path):
        """Test recommendations for large number of migrations."""
        # Create 101 migration files
        for i in range(101):
            (tmp_path / f"V{i:03d}__migration.sql").write_text("SELECT 1;")
        
        analyzer = DatabaseAnalyzer()
        result = analyzer.analyze_migrations(tmp_path, MigrationType.FLYWAY)
        
        assert result.success
        assert len(result.migrations) == 101
        
        # Should recommend squashing
        consolidation_rec = [
            r for r in result.recommendations 
            if r["category"] == "migration_consolidation"
        ]
        assert len(consolidation_rec) > 0
        assert consolidation_rec[0]["priority"] == "P2"
    
    def test_extract_schema_nonexistent_path(self):
        """Test extract_schema_from_models with nonexistent path."""
        analyzer = DatabaseAnalyzer()
        result = analyzer.extract_schema_from_models(
            Path("/nonexistent/models"),
            framework="sqlalchemy"
        )
        
        assert not result.success
        assert "not found" in result.error.lower()
    
    def test_extract_schema_unsupported_framework(self, tmp_path):
        """Test extract_schema_from_models with unsupported framework."""
        analyzer = DatabaseAnalyzer()
        
        with pytest.raises(ValueError, match="Unsupported framework"):
            analyzer.extract_schema_from_models(tmp_path, framework="unknown")
    
    def test_generate_er_diagram_empty_tables(self):
        """Test ER diagram generation with empty table list."""
        analyzer = DatabaseAnalyzer()
        diagram = analyzer.generate_er_diagram([])
        
        assert diagram == ""
    
    def test_generate_er_diagram_single_table(self):
        """Test ER diagram generation with single table."""
        table = TableInfo(
            name="users",
            columns=[
                ColumnInfo(name="id", type="INTEGER", primary_key=True, nullable=False),
                ColumnInfo(name="email", type="VARCHAR", nullable=False),
            ],
            primary_keys=["id"]
        )
        
        analyzer = DatabaseAnalyzer()
        diagram = analyzer.generate_er_diagram([table])
        
        assert "erDiagram" in diagram
        assert "users {" in diagram
        assert "INTEGER id PK" in diagram
        assert "VARCHAR email" in diagram
    
    def test_generate_er_diagram_with_relationships(self):
        """Test ER diagram generation with foreign key relationships."""
        users_table = TableInfo(
            name="users",
            columns=[
                ColumnInfo(name="id", type="INTEGER", primary_key=True),
            ],
            primary_keys=["id"]
        )
        
        orders_table = TableInfo(
            name="orders",
            columns=[
                ColumnInfo(name="id", type="INTEGER", primary_key=True),
                ColumnInfo(name="user_id", type="INTEGER", foreign_key="users.id"),
            ],
            primary_keys=["id"],
            foreign_keys={"user_id": "users.id"}
        )
        
        analyzer = DatabaseAnalyzer()
        diagram = analyzer.generate_er_diagram([users_table, orders_table])
        
        assert "erDiagram" in diagram
        assert "orders ||--o{ users : references" in diagram
        assert "users {" in diagram
        assert "orders {" in diagram
        assert "FK" in diagram  # Foreign key marker
    
    def test_schema_recommendations_missing_primary_keys(self):
        """Test recommendations for tables without primary keys."""
        table_no_pk = TableInfo(
            name="logs",
            columns=[
                ColumnInfo(name="message", type="TEXT"),
            ],
            primary_keys=[]  # No primary key
        )
        
        analyzer = DatabaseAnalyzer()
        recommendations = analyzer._generate_schema_recommendations([table_no_pk])
        
        assert len(recommendations) > 0
        pk_rec = [r for r in recommendations if r["category"] == "missing_primary_key"]
        assert len(pk_rec) > 0
        assert pk_rec[0]["priority"] == "P1"
        assert "logs" in pk_rec[0]["affected_tables"]
    
    def test_migration_sorting_by_version(self, tmp_path):
        """Test that migrations are sorted by version."""
        # Create migrations out of order
        (tmp_path / "V003__third.sql").write_text("SELECT 3;")
        (tmp_path / "V001__first.sql").write_text("SELECT 1;")
        (tmp_path / "V002__second.sql").write_text("SELECT 2;")
        
        analyzer = DatabaseAnalyzer()
        result = analyzer.analyze_migrations(tmp_path, MigrationType.FLYWAY)
        
        assert result.success
        assert len(result.migrations) == 3
        assert result.migrations[0].version == "001"
        assert result.migrations[1].version == "002"
        assert result.migrations[2].version == "003"
    
    def test_analysis_result_timing(self, tmp_path):
        """Test that analysis tracks execution time."""
        analyzer = DatabaseAnalyzer()
        result = analyzer.analyze_migrations(tmp_path)
        
        assert result.analysis_time_ms >= 0
        assert result.analysis_time_ms < 10000  # Should complete in < 10s


class TestDatabaseAnalysisResult:
    """Test DatabaseAnalysisResult dataclass."""
    
    def test_default_values(self):
        """Test DatabaseAnalysisResult default values."""
        result = DatabaseAnalysisResult(success=True)
        
        assert result.success
        assert result.tables == []
        assert result.migrations == []
        assert result.er_diagram == ""
        assert result.recommendations == []
        assert result.error == ""
        assert result.analysis_time_ms == 0.0
    
    def test_with_all_fields(self):
        """Test DatabaseAnalysisResult with all fields populated."""
        table = TableInfo(name="users", columns=[])
        migration = MigrationInfo(
            file_path="/test.py",
            version="001",
            description="Test",
            migration_type=MigrationType.ALEMBIC
        )
        
        result = DatabaseAnalysisResult(
            success=True,
            tables=[table],
            migrations=[migration],
            er_diagram="erDiagram...",
            recommendations=[{"priority": "P1"}],
            error="",
            analysis_time_ms=42.5
        )
        
        assert result.success
        assert len(result.tables) == 1
        assert len(result.migrations) == 1
        assert result.er_diagram == "erDiagram..."
        assert len(result.recommendations) == 1
        assert result.analysis_time_ms == 42.5


class TestColumnInfo:
    """Test ColumnInfo dataclass."""
    
    def test_minimal_column(self):
        """Test ColumnInfo with minimal fields."""
        column = ColumnInfo(name="id", type="INTEGER")
        
        assert column.name == "id"
        assert column.type == "INTEGER"
        assert column.nullable  # Default True
        assert not column.primary_key  # Default False
        assert column.foreign_key is None
        assert column.default is None
    
    def test_full_column(self):
        """Test ColumnInfo with all fields."""
        column = ColumnInfo(
            name="user_id",
            type="INTEGER",
            nullable=False,
            primary_key=False,
            foreign_key="users.id",
            default="0"
        )
        
        assert column.name == "user_id"
        assert not column.nullable
        assert column.foreign_key == "users.id"
        assert column.default == "0"


class TestTableInfo:
    """Test TableInfo dataclass."""
    
    def test_minimal_table(self):
        """Test TableInfo with minimal fields."""
        table = TableInfo(name="users")
        
        assert table.name == "users"
        assert table.schema == "public"  # Default
        assert table.columns == []
        assert table.primary_keys == []
        assert table.foreign_keys == {}
        assert table.indexes == []
    
    def test_table_with_columns(self):
        """Test TableInfo with columns."""
        columns = [
            ColumnInfo(name="id", type="INTEGER", primary_key=True),
            ColumnInfo(name="name", type="VARCHAR"),
        ]
        
        table = TableInfo(
            name="users",
            schema="auth",
            columns=columns,
            primary_keys=["id"],
            foreign_keys={},
            indexes=["idx_name"]
        )
        
        assert table.name == "users"
        assert table.schema == "auth"
        assert len(table.columns) == 2
        assert table.primary_keys == ["id"]
        assert table.indexes == ["idx_name"]
