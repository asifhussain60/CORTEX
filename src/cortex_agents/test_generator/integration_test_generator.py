"""
Integration & Performance Test Generator

Generates tests beyond unit testing:
1. API endpoint integration tests
2. Database integration tests  
3. External service integration tests
4. Performance/load tests for critical paths

Author: Asif Hussain
Date: 2025-11-21
"""

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set
from enum import Enum


class TestType(Enum):
    """Types of integration/performance tests"""
    API_ENDPOINT = "api_endpoint"
    DATABASE = "database"
    EXTERNAL_SERVICE = "external_service"
    PERFORMANCE = "performance"
    LOAD = "load"
    

@dataclass
class IntegrationTestSpec:
    """Specification for an integration test"""
    test_type: TestType
    name: str
    description: str
    test_code: str
    dependencies: List[str]
    estimated_duration_ms: int
    

class IntegrationTestGenerator:
    """
    Generates integration and performance tests
    
    Analyzes code for:
    - HTTP endpoints (FastAPI, Flask routes)
    - Database queries (SQLAlchemy, direct SQL)
    - External API calls (requests, httpx)
    - Performance-critical sections
    """
    
    def __init__(self):
        self.api_frameworks = {'fastapi', 'flask', 'django'}
        self.db_libraries = {'sqlalchemy', 'psycopg2', 'pymongo'}
        self.http_clients = {'requests', 'httpx', 'aiohttp'}
    
    def analyze_file_for_integrations(self, file_path: Path) -> Dict[TestType, List]:
        """
        Scan file for integration points
        
        Returns dict mapping test types to detected integration points
        """
        if not file_path.exists():
            return {}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                tree = ast.parse(f.read())
            except SyntaxError:
                return {}
        
        integrations = {test_type: [] for test_type in TestType}
        
        for node in ast.walk(tree):
            # API endpoints
            if self._is_api_endpoint(node):
                integrations[TestType.API_ENDPOINT].append(node)
            
            # Database operations
            elif self._is_database_operation(node):
                integrations[TestType.DATABASE].append(node)
            
            # External service calls
            elif self._is_external_call(node):
                integrations[TestType.EXTERNAL_SERVICE].append(node)
            
            # Performance-critical (loops with complexity)
            elif self._is_performance_critical(node):
                integrations[TestType.PERFORMANCE].append(node)
        
        return integrations
    
    def _is_api_endpoint(self, node: ast.AST) -> bool:
        """Check if node is an API endpoint definition"""
        if not isinstance(node, ast.FunctionDef):
            return False
        
        # FastAPI/Flask decorators
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Attribute):
                    # @app.get(), @router.post(), etc.
                    if decorator.func.attr in {'get', 'post', 'put', 'delete', 'patch'}:
                        return True
            elif isinstance(decorator, ast.Attribute):
                # @app.route()
                if decorator.attr == 'route':
                    return True
        
        return False
    
    def _is_database_operation(self, node: ast.AST) -> bool:
        """Check if node contains database operations"""
        if isinstance(node, ast.Call):
            # SQLAlchemy session methods
            if isinstance(node.func, ast.Attribute):
                db_methods = {'query', 'add', 'commit', 'delete', 'execute'}
                if node.func.attr in db_methods:
                    return True
        
        return False
    
    def _is_external_call(self, node: ast.AST) -> bool:
        """Check if node makes external HTTP calls"""
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                # requests.get(), httpx.post(), etc.
                http_methods = {'get', 'post', 'put', 'delete', 'request'}
                if node.func.attr in http_methods:
                    return True
        
        return False
    
    def _is_performance_critical(self, node: ast.AST) -> bool:
        """Check if node is performance-critical"""
        if isinstance(node, (ast.For, ast.While)):
            # Nested loops are performance-critical
            has_nested_loop = any(
                isinstance(child, (ast.For, ast.While))
                for child in ast.walk(node)
            )
            return has_nested_loop
        
        return False
    
    def generate_api_endpoint_test(
        self,
        func_node: ast.FunctionDef,
        http_method: str = "GET",
        path: str = "/api/test"
    ) -> IntegrationTestSpec:
        """
        Generate API endpoint integration test
        
        Tests:
        - Happy path (200 OK)
        - Invalid input (400 Bad Request)
        - Authentication (401 Unauthorized)
        - Not found (404)
        """
        func_name = func_node.name
        
        test_code = f'''
def test_{func_name}_happy_path(client):
    """Test {func_name} endpoint with valid data"""
    response = client.{http_method.lower()}("{path}", json={{"key": "value"}})
    
    assert response.status_code == 200
    assert response.json()["status"] == "success"


def test_{func_name}_invalid_input(client):
    """Test {func_name} endpoint with invalid data"""
    response = client.{http_method.lower()}("{path}", json={{"invalid": True}})
    
    assert response.status_code == 400
    assert "error" in response.json()


def test_{func_name}_authentication_required(client):
    """Test {func_name} endpoint requires authentication"""
    # No auth token
    response = client.{http_method.lower()}("{path}")
    
    assert response.status_code == 401
    assert "authentication" in response.json()["error"].lower()


def test_{func_name}_not_found(client):
    """Test {func_name} endpoint with invalid ID"""
    response = client.{http_method.lower()}("{path}/999999")
    
    assert response.status_code == 404
'''
        
        return IntegrationTestSpec(
            test_type=TestType.API_ENDPOINT,
            name=f"test_{func_name}_integration",
            description=f"Integration tests for {func_name} API endpoint",
            test_code=test_code.strip(),
            dependencies=['pytest', 'httpx' if 'async' in func_name else 'requests'],
            estimated_duration_ms=500
        )
    
    def generate_database_test(
        self,
        func_node: ast.FunctionDef,
        operation: str = "query"
    ) -> IntegrationTestSpec:
        """
        Generate database integration test
        
        Tests:
        - CRUD operations
        - Transaction rollback
        - Constraint violations
        - Connection handling
        """
        func_name = func_node.name
        
        test_code = f'''
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture
def db_session():
    """Create test database session"""
    engine = create_engine("sqlite:///:memory:")
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Create tables
    Base.metadata.create_all(engine)
    
    yield session
    
    session.close()


def test_{func_name}_database_operation(db_session):
    """Test {func_name} database integration"""
    # Arrange
    test_data = {{"name": "Test", "value": 123}}
    
    # Act
    result = {func_name}(db_session, **test_data)
    db_session.commit()
    
    # Assert
    assert result is not None
    assert result.name == test_data["name"]
    
    # Verify database state
    queried = db_session.query(Model).filter_by(name="Test").first()
    assert queried is not None


def test_{func_name}_transaction_rollback(db_session):
    """Test {func_name} handles transaction rollback"""
    try:
        # Force an error
        {func_name}(db_session, invalid_data=True)
        db_session.commit()
    except Exception:
        db_session.rollback()
    
    # Verify no data was committed
    count = db_session.query(Model).count()
    assert count == 0


def test_{func_name}_constraint_violation(db_session):
    """Test {func_name} handles constraint violations"""
    # Insert duplicate
    {func_name}(db_session, name="Duplicate")
    db_session.commit()
    
    # Try to insert again (should fail on unique constraint)
    with pytest.raises(Exception):  # IntegrityError
        {func_name}(db_session, name="Duplicate")
        db_session.commit()
'''
        
        return IntegrationTestSpec(
            test_type=TestType.DATABASE,
            name=f"test_{func_name}_database_integration",
            description=f"Database integration tests for {func_name}",
            test_code=test_code.strip(),
            dependencies=['pytest', 'sqlalchemy', 'psycopg2-binary'],
            estimated_duration_ms=200
        )
    
    def generate_external_service_test(
        self,
        func_node: ast.FunctionDef,
        service_name: str = "external_api"
    ) -> IntegrationTestSpec:
        """
        Generate external service integration test
        
        Tests:
        - Successful API call
        - Network timeout
        - Rate limiting
        - Service unavailable
        """
        func_name = func_node.name
        
        test_code = f'''
import pytest
from unittest.mock import patch, Mock


def test_{func_name}_successful_call():
    """Test {func_name} with successful API response"""
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {{"data": "success"}}
        mock_get.return_value = mock_response
        
        result = {func_name}()
        
        assert result["data"] == "success"
        mock_get.assert_called_once()


def test_{func_name}_network_timeout():
    """Test {func_name} handles network timeout"""
    with patch('requests.get', side_effect=requests.Timeout):
        with pytest.raises(TimeoutError):
            {func_name}()


def test_{func_name}_rate_limited():
    """Test {func_name} handles rate limiting (429)"""
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.headers = {{"Retry-After": "60"}}
        mock_get.return_value = mock_response
        
        with pytest.raises(RateLimitError):
            {func_name}()


def test_{func_name}_service_unavailable():
    """Test {func_name} handles service outage (503)"""
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.status_code = 503
        mock_get.return_value = mock_response
        
        result = {func_name}()
        
        assert result is None  # Graceful degradation
'''
        
        return IntegrationTestSpec(
            test_type=TestType.EXTERNAL_SERVICE,
            name=f"test_{func_name}_external_service",
            description=f"External service integration tests for {func_name}",
            test_code=test_code.strip(),
            dependencies=['pytest', 'requests', 'unittest.mock'],
            estimated_duration_ms=100
        )
    
    def generate_performance_test(
        self,
        func_node: ast.FunctionDef,
        max_duration_ms: int = 200
    ) -> IntegrationTestSpec:
        """
        Generate performance test
        
        Tests:
        - Response time under max threshold
        - Performance with large datasets
        - Memory usage
        - CPU usage
        """
        func_name = func_node.name
        
        test_code = f'''
import pytest
import time
from memory_profiler import profile


@pytest.mark.performance
def test_{func_name}_response_time():
    """Test {func_name} completes within {max_duration_ms}ms"""
    start = time.time()
    
    result = {func_name}(sample_data)
    
    duration = (time.time() - start) * 1000  # Convert to ms
    assert duration < {max_duration_ms}, f"Too slow: {{duration}}ms"


@pytest.mark.performance
def test_{func_name}_large_dataset():
    """Test {func_name} performance with large dataset"""
    large_dataset = generate_large_dataset(size=10000)
    
    start = time.time()
    result = {func_name}(large_dataset)
    duration = (time.time() - start) * 1000
    
    # Should scale linearly
    assert duration < {max_duration_ms * 10}, f"Doesn't scale: {{duration}}ms"
    assert len(result) == 10000


@pytest.mark.performance
@profile
def test_{func_name}_memory_usage():
    """Test {func_name} memory usage stays reasonable"""
    import tracemalloc
    
    tracemalloc.start()
    
    result = {func_name}(sample_data)
    
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    # Memory usage should be < 100MB
    assert peak < 100 * 1024 * 1024, f"Memory leak: {{peak // 1024 // 1024}}MB"


@pytest.mark.performance
def test_{func_name}_concurrent_load():
    """Test {func_name} handles concurrent requests"""
    from concurrent.futures import ThreadPoolExecutor, as_completed
    
    def run_test():
        return {func_name}(sample_data)
    
    # Simulate 50 concurrent requests
    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = [executor.submit(run_test) for _ in range(50)]
        
        results = [f.result() for f in as_completed(futures)]
    
    # All requests should succeed
    assert len(results) == 50
    assert all(r is not None for r in results)
'''
        
        return IntegrationTestSpec(
            test_type=TestType.PERFORMANCE,
            name=f"test_{func_name}_performance",
            description=f"Performance tests for {func_name}",
            test_code=test_code.strip(),
            dependencies=['pytest', 'memory-profiler', 'psutil'],
            estimated_duration_ms=max_duration_ms * 20  # Tests take longer
        )
    
    def generate_integration_test_suite(
        self,
        file_path: Path
    ) -> List[IntegrationTestSpec]:
        """
        Generate complete integration test suite for a file
        
        Returns list of all integration tests
        """
        integrations = self.analyze_file_for_integrations(file_path)
        tests = []
        
        # Generate tests for each integration type
        for test_type, nodes in integrations.items():
            for node in nodes:
                if not isinstance(node, ast.FunctionDef):
                    continue
                
                if test_type == TestType.API_ENDPOINT:
                    tests.append(self.generate_api_endpoint_test(node))
                elif test_type == TestType.DATABASE:
                    tests.append(self.generate_database_test(node))
                elif test_type == TestType.EXTERNAL_SERVICE:
                    tests.append(self.generate_external_service_test(node))
                elif test_type == TestType.PERFORMANCE:
                    tests.append(self.generate_performance_test(node))
        
        return tests
