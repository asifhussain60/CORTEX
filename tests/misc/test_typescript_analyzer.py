"""
Comprehensive unit tests for TypeScriptAnalyzer.
"""

import pytest
from pathlib import Path
from src.dashboard.analyzers import TypeScriptAnalyzer


@pytest.fixture
def analyzer():
    """Create TypeScriptAnalyzer instance."""
    return TypeScriptAnalyzer()


@pytest.fixture
def sample_file():
    """Path to sample TypeScript file."""
    return Path(__file__).parent / 'fixtures' / 'sample.ts'


def test_analyzer_initialization(analyzer):
    """Test analyzer initializes correctly."""
    assert analyzer is not None
    assert analyzer.encoding == 'utf-8'
    assert len(analyzer.errors) == 0


def test_supports_file(analyzer):
    """Test file extension support."""
    assert analyzer.supports_file(Path('test.ts'))
    assert analyzer.supports_file(Path('Test.TS'))
    assert not analyzer.supports_file(Path('test.txt'))
    assert not analyzer.supports_file(Path('test.js'))


def test_extract_classes(analyzer, sample_file):
    """Test class extraction."""
    result = analyzer.analyze(sample_file)
    
    assert len(result.classes) >= 2  # UserListComponent + UserService
    
    # Check UserListComponent
    component = next((c for c in result.classes if 'UserListComponent' in c['name']), None)
    assert component is not None
    assert component['type'] == 'class'


def test_extract_methods(analyzer, sample_file):
    """Test method extraction."""
    result = analyzer.analyze(sample_file)
    
    assert len(result.methods) >= 3  # ngOnInit, selectUser, loadUserDetails
    
    # Check ngOnInit
    ng_on_init = next((m for m in result.methods if m['name'] == 'ngOnInit'), None)
    assert ng_on_init is not None
    assert ng_on_init['visibility'] == 'public' or ng_on_init['visibility'] is None


def test_detect_component(analyzer, sample_file):
    """Test Angular component detection."""
    result = analyzer.analyze(sample_file)
    
    component_patterns = result.patterns['component']
    assert component_patterns['is_component'] is True
    assert component_patterns['selector'] == 'app-user-list'
    assert component_patterns['template_url'] == './user-list.component.html'
    assert len(component_patterns['inputs']) >= 1
    assert len(component_patterns['outputs']) >= 1
    assert component_patterns['standalone'] is True


def test_detect_service(analyzer, sample_file):
    """Test Angular service detection."""
    result = analyzer.analyze(sample_file)
    
    service_patterns = result.patterns['service']
    assert service_patterns['is_service'] is True
    assert service_patterns['provided_in'] == 'root'
    assert len(service_patterns['injected_dependencies']) >= 1


def test_detect_rxjs(analyzer, sample_file):
    """Test RxJS pattern detection."""
    result = analyzer.analyze(sample_file)
    
    rxjs_patterns = result.patterns['rxjs']
    assert rxjs_patterns['has_rxjs'] is True
    assert rxjs_patterns['observable_count'] >= 2
    
    # Check for operators (sample has debounceTime)
    assert len(rxjs_patterns['operators']) >= 1
    operator_names = [op['name'] for op in rxjs_patterns['operators']]
    assert 'debounceTime' in operator_names or 'map' in operator_names or 'filter' in operator_names


def test_detect_ngrx(analyzer, sample_file):
    """Test NgRx state management detection."""
    result = analyzer.analyze(sample_file)
    
    ngrx_patterns = result.patterns['ngrx']
    assert ngrx_patterns['has_ngrx'] is True
    assert ngrx_patterns['has_store'] is True
    # Actions may not be defined in component file
    assert 'has_actions' in ngrx_patterns


def test_detect_http_calls(analyzer, sample_file):
    """Test HTTP client detection."""
    result = analyzer.analyze(sample_file)
    
    http_patterns = result.patterns['http']
    assert http_patterns['has_http'] is True
    assert len(http_patterns['calls']) >= 2
    
    # Check HTTP methods
    methods = [call['method'] for call in http_patterns['calls']]
    assert 'GET' in methods


def test_extract_dependencies(analyzer, sample_file):
    """Test import statement extraction."""
    result = analyzer.analyze(sample_file)
    
    assert len(result.dependencies) > 0
    assert '@angular/core' in result.dependencies
    assert 'rxjs' in result.dependencies


def test_calculate_metrics(analyzer, sample_file):
    """Test metrics calculation."""
    result = analyzer.analyze(sample_file)
    
    assert result.metrics['loc'] > 0
    assert result.metrics['sloc'] > 0
    assert result.metrics['class_count'] >= 2
    assert result.metrics['method_count'] >= 3


def test_empty_file(analyzer, tmp_path):
    """Test handling of empty file."""
    empty_file = tmp_path / 'empty.ts'
    empty_file.write_text('')
    
    result = analyzer.analyze(empty_file)
    
    assert result.language == 'typescript'
    assert len(result.classes) == 0
    assert len(result.methods) == 0


def test_interface_extraction(analyzer):
    """Test interface extraction."""
    interface_code = """
export interface User {
    id: number;
    username: string;
    email: string;
}

export interface UserService {
    getUsers(): Observable<User[]>;
    getUser(id: number): Observable<User>;
}
"""
    
    temp_file = Path('temp_interface.ts')
    temp_file.write_text(interface_code)
    
    try:
        result = analyzer.analyze(temp_file)
        
        assert result.metrics['interface_count'] >= 2
    finally:
        if temp_file.exists():
            temp_file.unlink()


def test_routing_detection(analyzer):
    """Test Angular routing detection."""
    routing_code = """
import { RouterModule, Routes } from '@angular/router';
import { UserListComponent } from './user-list.component';
import { UserDetailComponent } from './user-detail.component';

const routes: Routes = [
  { path: 'users', component: UserListComponent },
  { path: 'users/:id', component: UserDetailComponent }
];

export const routing = RouterModule.forRoot(routes);
"""
    
    temp_file = Path('temp_routing.ts')
    temp_file.write_text(routing_code)
    
    try:
        result = analyzer.analyze(temp_file)
        
        routing_patterns = result.patterns['routing']
        assert routing_patterns['has_routing'] is True
        assert len(routing_patterns['routes']) >= 2
    finally:
        if temp_file.exists():
            temp_file.unlink()
