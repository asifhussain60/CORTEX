"""
Tests for DatabaseSchemaInferenceEngine

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
import tempfile
from pathlib import Path

from src.crawlers.database_inference_engine import (
    DatabaseSchemaInferenceEngine,
    TableInfo
)


@pytest.fixture
def mock_cf_app():
    """Create a mock ColdFusion application"""
    with tempfile.TemporaryDirectory() as tmpdir:
        app_path = Path(tmpdir)
        
        # Create ColdFusion files with queries
        (app_path / 'users.cfm').write_text('''
            <cfquery name="getUsers" datasource="mydb">
                SELECT user_id, username, email, created_at
                FROM users
                WHERE active = 1
            </cfquery>
            
            <cfquery name="insertUser" datasource="mydb">
                INSERT INTO users (username, email, password)
                VALUES (#username#, #email#, #password#)
            </cfquery>
        ''')
        
        (app_path / 'transactions.cfm').write_text('''
            <cfquery name="getTransactions" datasource="mydb">
                SELECT t.transaction_id, t.amount, t.date, u.username
                FROM transactions t
                JOIN users u ON t.user_id = u.user_id
                WHERE t.date > #startDate#
            </cfquery>
        ''')
        
        # Create ORM entity
        (app_path / 'Product.cfc').write_text('''
            component persistent="true" table="products" {
                property name="product_id" fieldtype="id" generator="native";
                property name="product_name" type="string";
                property name="price" type="numeric";
                property name="category_id" type="numeric";
                
                property name="category" fieldtype="many-to-one" cfc="Category" fkcolumn="category_id";
            }
        ''')
        
        yield app_path


def test_database_inference_init(mock_cf_app):
    """Test database inference engine initialization"""
    engine = DatabaseSchemaInferenceEngine(mock_cf_app)
    assert engine.app_path == mock_cf_app
    assert isinstance(engine.tables, dict)


def test_parse_cfquery_tags(mock_cf_app):
    """Test parsing ColdFusion query tags"""
    engine = DatabaseSchemaInferenceEngine(mock_cf_app)
    engine._parse_cfquery_tags()
    
    # Should have found users and transactions tables
    assert 'users' in engine.tables
    assert 'transactions' in engine.tables
    
    # Check users table
    users_table = engine.tables['users']
    assert 'SELECT' in users_table.operations
    assert 'INSERT' in users_table.operations
    assert len(users_table.file_references) > 0


def test_extract_table_names():
    """Test table name extraction from SQL"""
    engine = DatabaseSchemaInferenceEngine(Path('/tmp'))
    
    # Test SELECT
    sql = "SELECT * FROM users WHERE id = 1"
    tables = engine._extract_table_names(sql)
    assert 'users' in tables
    
    # Test JOIN
    sql = "SELECT u.*, o.* FROM users u JOIN orders o ON u.id = o.user_id"
    tables = engine._extract_table_names(sql)
    assert 'users' in tables
    assert 'orders' in tables
    
    # Test INSERT
    sql = "INSERT INTO products (name, price) VALUES ('Test', 10.00)"
    tables = engine._extract_table_names(sql)
    assert 'products' in tables
    
    # Test UPDATE
    sql = "UPDATE customers SET status = 'active' WHERE id = 1"
    tables = engine._extract_table_names(sql)
    assert 'customers' in tables


def test_detect_query_type():
    """Test SQL query type detection"""
    engine = DatabaseSchemaInferenceEngine(Path('/tmp'))
    
    assert engine._detect_query_type("SELECT * FROM users") == 'SELECT'
    assert engine._detect_query_type("INSERT INTO users VALUES (1)") == 'INSERT'
    assert engine._detect_query_type("UPDATE users SET name = 'test'") == 'UPDATE'
    assert engine._detect_query_type("DELETE FROM users WHERE id = 1") == 'DELETE'


def test_extract_column_names():
    """Test column name extraction from SQL"""
    engine = DatabaseSchemaInferenceEngine(Path('/tmp'))
    
    # Test SELECT with explicit columns
    sql = "SELECT user_id, username, email FROM users"
    columns = engine._extract_column_names(sql, 'SELECT')
    assert 'user_id' in columns
    assert 'username' in columns
    assert 'email' in columns
    
    # Test INSERT with column list
    sql = "INSERT INTO users (username, email, password) VALUES (?, ?, ?)"
    columns = engine._extract_column_names(sql, 'INSERT')
    assert 'username' in columns
    assert 'email' in columns
    assert 'password' in columns


def test_analyze_orm_models(mock_cf_app):
    """Test ORM model analysis"""
    engine = DatabaseSchemaInferenceEngine(mock_cf_app)
    engine._analyze_orm_models()
    
    # Should have found products table from ORM
    assert 'products' in engine.tables
    
    products = engine.tables['products']
    assert products.confidence == 0.95  # ORM = high confidence
    assert 'product_id' in products.columns
    assert 'product_name' in products.columns
    assert products.primary_key == 'product_id'
    assert len(products.relationships) > 0


def test_parse_orm_entity():
    """Test parsing individual ORM entity"""
    engine = DatabaseSchemaInferenceEngine(Path('/tmp'))
    
    content = '''
        component persistent="true" table="orders" {
            property name="order_id" fieldtype="id";
            property name="customer_id" type="numeric";
            property name="order_date" type="date";
            property name="total_amount" type="numeric";
            
            property name="customer" fieldtype="many-to-one" cfc="Customer" fkcolumn="customer_id";
        }
    '''
    
    engine._parse_orm_entity(content, 'Order.cfc')
    
    assert 'orders' in engine.tables
    orders = engine.tables['orders']
    assert orders.primary_key == 'order_id'
    assert 'customer_id' in orders.columns
    assert len(orders.relationships) == 1


def test_infer_schema_complete(mock_cf_app):
    """Test complete schema inference"""
    engine = DatabaseSchemaInferenceEngine(mock_cf_app)
    schema = engine.infer_schema()
    
    assert 'tables' in schema
    assert 'total_tables' in schema
    assert 'high_confidence_tables' in schema
    
    # Should have found multiple tables
    assert schema['total_tables'] >= 3
    
    # Products from ORM should be high confidence
    assert schema['high_confidence_tables'] >= 1


def test_confidence_scoring(mock_cf_app):
    """Test confidence score calculation"""
    engine = DatabaseSchemaInferenceEngine(mock_cf_app)
    engine.infer_schema()
    
    # ORM-based table should have highest confidence
    products = engine.tables.get('products')
    if products:
        assert products.confidence >= 0.95
    
    # Query-based tables should have medium confidence
    users = engine.tables.get('users')
    if users:
        assert 0.5 <= users.confidence < 0.95


def test_get_table_info(mock_cf_app):
    """Test retrieving specific table info"""
    engine = DatabaseSchemaInferenceEngine(mock_cf_app)
    engine.infer_schema()
    
    users_info = engine.get_table_info('users')
    assert users_info is not None
    assert users_info.name == 'users'
    assert len(users_info.columns) > 0


def test_get_high_confidence_tables(mock_cf_app):
    """Test retrieving high confidence tables"""
    engine = DatabaseSchemaInferenceEngine(mock_cf_app)
    engine.infer_schema()
    
    high_conf_tables = engine.get_high_confidence_tables()
    assert isinstance(high_conf_tables, list)
    
    # All should have confidence >= 0.8
    for table in high_conf_tables:
        assert table.confidence >= 0.8


def test_table_info_to_dict():
    """Test TableInfo to dictionary conversion"""
    table = TableInfo(
        name='test_table',
        columns={'col1', 'col2', 'col3'},
        primary_key='col1',
        relationships=[{'type': 'one-to-many', 'target': 'other_table'}],
        operations=['SELECT', 'INSERT'],
        file_references=['file1.cfm', 'file2.cfm'],
        confidence=0.85
    )
    
    table_dict = table.to_dict()
    
    assert table_dict['name'] == 'test_table'
    assert len(table_dict['columns']) == 3
    assert table_dict['primary_key'] == 'col1'
    assert table_dict['confidence'] == 0.85


def test_empty_application():
    """Test inference on empty application"""
    with tempfile.TemporaryDirectory() as tmpdir:
        engine = DatabaseSchemaInferenceEngine(Path(tmpdir))
        schema = engine.infer_schema()
        
        assert schema['total_tables'] == 0
        assert schema['high_confidence_tables'] == 0


def test_detect_datasources(mock_cf_app):
    """Test datasource detection"""
    # Add Application.cfc with datasource
    (mock_cf_app / 'Application.cfc').write_text('''
        component {
            this.name = "TestApp";
            this.datasource = "myOracleDB";
        }
    ''')
    
    engine = DatabaseSchemaInferenceEngine(mock_cf_app)
    schema = engine.infer_schema()
    
    assert len(schema['datasources']) > 0
    assert any(ds['name'] == 'myOracleDB' for ds in schema['datasources'])


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
