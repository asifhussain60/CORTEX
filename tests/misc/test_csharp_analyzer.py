"""
Comprehensive unit tests for CSharpAnalyzer.
"""

import pytest
from pathlib import Path
from src.dashboard.analyzers import CSharpAnalyzer


@pytest.fixture
def analyzer():
    """Create CSharpAnalyzer instance."""
    return CSharpAnalyzer()


@pytest.fixture
def sample_file():
    """Path to sample C# file."""
    return Path(__file__).parent / 'fixtures' / 'sample.cs'


def test_analyzer_initialization(analyzer):
    """Test analyzer initializes correctly."""
    assert analyzer is not None
    assert analyzer.encoding == 'utf-8'
    assert len(analyzer.errors) == 0


def test_supports_file(analyzer):
    """Test file extension support."""
    assert analyzer.supports_file(Path('test.cs'))
    assert analyzer.supports_file(Path('Test.CS'))
    assert not analyzer.supports_file(Path('test.txt'))
    assert not analyzer.supports_file(Path('test.py'))


def test_extract_classes(analyzer, sample_file):
    """Test class extraction."""
    result = analyzer.analyze(sample_file)
    
    assert len(result.classes) >= 2  # UserController + AppDbContext
    
    # Check UserController
    controller = next((c for c in result.classes if c['name'] == 'UserController'), None)
    assert controller is not None
    assert controller['type'] == 'class'
    assert controller['visibility'] == 'public'
    assert 'ControllerBase' in controller.get('base_classes', [])


def test_extract_methods(analyzer, sample_file):
    """Test method extraction."""
    result = analyzer.analyze(sample_file)
    
    assert len(result.methods) >= 5  # GetUsers, GetUser, CreateUser, UpdateUser, DeleteUser
    
    # Check GetUsers method
    get_users = next((m for m in result.methods if m['name'] == 'GetUsers'), None)
    assert get_users is not None
    assert get_users['visibility'] == 'public'
    assert get_users['is_async'] is True


def test_detect_api_controller(analyzer, sample_file):
    """Test Web API controller detection."""
    result = analyzer.analyze(sample_file)
    
    api_patterns = result.patterns['web_api']
    assert api_patterns['is_api_controller'] is True
    assert len(api_patterns['endpoints']) >= 5
    
    # Check HTTP methods
    methods = [ep['method'] for ep in api_patterns['endpoints']]
    assert 'Get' in methods
    assert 'Post' in methods
    assert 'Put' in methods
    assert 'Delete' in methods


def test_detect_dependency_injection(analyzer, sample_file):
    """Test dependency injection pattern detection."""
    result = analyzer.analyze(sample_file)
    
    di_patterns = result.patterns['dependency_injection']
    assert di_patterns['has_constructor_injection'] is True
    assert len(di_patterns['injected_services']) >= 2
    assert 'IUserService' in di_patterns['injected_services']


def test_detect_entity_framework(analyzer, sample_file):
    """Test Entity Framework detection."""
    result = analyzer.analyze(sample_file)
    
    ef_patterns = result.patterns['entity_framework']
    assert ef_patterns['has_dbcontext'] is True
    assert ef_patterns['dbcontext_name'] == 'AppDbContext'
    assert len(ef_patterns['dbsets']) >= 2


def test_detect_linq(analyzer, sample_file):
    """Test LINQ query detection."""
    result = analyzer.analyze(sample_file)
    
    linq_patterns = result.patterns['linq']
    assert linq_patterns['has_linq'] is True
    assert linq_patterns['query_count'] >= 3
    
    # Check for common operators
    operators = [op['name'] for op in linq_patterns['operators']]
    assert 'Where' in operators
    assert 'Select' in operators or 'OrderBy' in operators


def test_detect_async_patterns(analyzer, sample_file):
    """Test async/await pattern detection."""
    result = analyzer.analyze(sample_file)
    
    async_patterns = result.patterns['async_await']
    assert async_patterns['has_async'] is True
    assert async_patterns['async_method_count'] >= 5
    assert async_patterns['await_count'] >= 5


def test_calculate_complexity(analyzer, sample_file):
    """Test complexity calculation."""
    result = analyzer.analyze(sample_file)
    
    assert 'cyclomatic' in result.complexity
    assert 'avg_method_complexity' in result.complexity
    assert result.complexity['cyclomatic'] > 0


def test_extract_dependencies(analyzer, sample_file):
    """Test using statement extraction."""
    result = analyzer.analyze(sample_file)
    
    assert len(result.dependencies) > 0
    assert 'System' in result.dependencies
    assert any('Microsoft.AspNetCore.Mvc' in d for d in result.dependencies)


def test_calculate_metrics(analyzer, sample_file):
    """Test metrics calculation."""
    result = analyzer.analyze(sample_file)
    
    assert result.metrics['loc'] > 0
    assert result.metrics['sloc'] > 0
    assert result.metrics['class_count'] >= 2
    assert result.metrics['method_count'] >= 5
    assert result.metrics['public_method_count'] >= 5
    assert result.metrics['async_method_count'] >= 5


def test_empty_file(analyzer, tmp_path):
    """Test handling of empty file."""
    empty_file = tmp_path / 'empty.cs'
    empty_file.write_text('')
    
    result = analyzer.analyze(empty_file)
    
    assert result.language == 'csharp'
    assert len(result.classes) == 0
    assert len(result.methods) == 0


def test_nonexistent_file(analyzer):
    """Test handling of nonexistent file."""
    result = analyzer.analyze(Path('nonexistent.cs'))
    
    assert result.language == 'csharp'
    assert len(result.errors) > 0


def test_mvc_pattern_detection(analyzer):
    """Test MVC controller pattern detection."""
    mvc_code = """
using Microsoft.AspNetCore.Mvc;

public class HomeController : Controller
{
    public ActionResult Index()
    {
        return View();
    }
    
    [HttpPost]
    public ActionResult Create(CreateDto dto)
    {
        return RedirectToAction("Index");
    }
}
"""
    
    temp_file = Path('temp_mvc.cs')
    temp_file.write_text(mvc_code)
    
    try:
        result = analyzer.analyze(temp_file)
        
        mvc_patterns = result.patterns['mvc']
        assert mvc_patterns['is_controller'] is True
        assert mvc_patterns['controller_name'] == 'HomeController'
        assert len(mvc_patterns['actions']) >= 2
    finally:
        if temp_file.exists():
            temp_file.unlink()
