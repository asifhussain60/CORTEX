"""
Unit tests for testing framework discovery.

Task: DISC-006
Authority: PHASE-9-DISCOVERY-ORCHESTRATOR.yaml
"""

import json
import tempfile
import pytest
from pathlib import Path

from cortex.brain.discovery.testing_discovery import (
    TestingDiscovery,
    TestFramework,
    TestFileInfo,
)


class TestTestingDiscoveryInit:
    """Test testing discovery initialization."""
    
    def test_init_creates_discovery(self) -> None:
        """Test that discovery can be instantiated."""
        discovery = TestingDiscovery()
        assert discovery is not None
        assert hasattr(discovery, "discover")
    
    def test_supported_frameworks_defined(self) -> None:
        """Test that supported frameworks are defined."""
        discovery = TestingDiscovery()
        frameworks = discovery.get_supported_frameworks()
        assert len(frameworks) > 0
        assert "pytest" in frameworks
        assert "jest" in frameworks


class TestPytestDiscovery:
    """Test pytest framework discovery."""
    
    def test_detect_pytest_configuration(self, tmp_path: Path) -> None:
        """Test detecting pytest configuration."""
        pytest_ini = tmp_path / "pytest.ini"
        pytest_ini.write_text("""
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
""")
        
        discovery = TestingDiscovery()
        result = discovery.detect_pytest(tmp_path)
        
        assert result is not None
        assert result["framework"] == "pytest"
        assert "testpaths" in result["config"]
    
    def test_detect_pytest_fixtures(self, tmp_path: Path) -> None:
        """Test detecting pytest fixtures."""
        conftest = tmp_path / "conftest.py"
        conftest.write_text("""
import pytest

@pytest.fixture
def sample_data():
    return {"key": "value"}

@pytest.fixture(scope="module")
def db_connection():
    return "connection"
""")
        
        discovery = TestingDiscovery()
        result = discovery.scan_pytest_fixtures(tmp_path)
        
        assert result is not None
        assert len(result) >= 2
        assert "sample_data" in [f["name"] for f in result]


class TestJestDiscovery:
    """Test Jest framework discovery."""
    
    def test_detect_jest_configuration(self, tmp_path: Path) -> None:
        """Test detecting Jest configuration."""
        jest_config = tmp_path / "jest.config.js"
        jest_config.write_text("""
module.exports = {
  testEnvironment: 'node',
  coverageDirectory: 'coverage',
  testMatch: ['**/__tests__/**/*.js', '**/?(*.)+(spec|test).js'],
  collectCoverageFrom: ['src/**/*.js']
};
""")
        
        discovery = TestingDiscovery()
        result = discovery.detect_jest(tmp_path)
        
        assert result is not None
        assert result["framework"] == "jest"
        assert "config_file" in result
    
    def test_detect_jest_package_json(self, tmp_path: Path) -> None:
        """Test detecting Jest in package.json."""
        package_json = tmp_path / "package.json"
        package_json.write_text(json.dumps({
            "devDependencies": {
                "jest": "^29.0.0",
                "@testing-library/react": "^13.0.0"
            },
            "scripts": {
                "test": "jest",
                "test:coverage": "jest --coverage"
            }
        }))
        
        discovery = TestingDiscovery()
        result = discovery.detect_jest(tmp_path)
        
        assert result is not None
        assert result["framework"] == "jest"


class TestMochaDiscovery:
    """Test Mocha framework discovery."""
    
    def test_detect_mocha_configuration(self, tmp_path: Path) -> None:
        """Test detecting Mocha configuration."""
        mocharc = tmp_path / ".mocharc.json"
        mocharc.write_text(json.dumps({
            "require": ["@babel/register"],
            "spec": "test/**/*.spec.js",
            "timeout": 5000
        }))
        
        discovery = TestingDiscovery()
        result = discovery.detect_mocha(tmp_path)
        
        assert result is not None
        assert result["framework"] == "mocha"


class TestCoverageDiscovery:
    """Test coverage configuration discovery."""
    
    def test_detect_coverage_py(self, tmp_path: Path) -> None:
        """Test detecting coverage.py configuration."""
        coveragerc = tmp_path / ".coveragerc"
        coveragerc.write_text("""
[run]
source = src
omit = */tests/*

[report]
precision = 2
show_missing = True
""")
        
        discovery = TestingDiscovery()
        result = discovery.detect_coverage_config(tmp_path)
        
        assert result is not None
        assert result["tool"] == "coverage.py"
        assert "source" in result["config"]
    
    def test_detect_istanbul_coverage(self, tmp_path: Path) -> None:
        """Test detecting Istanbul coverage."""
        nyc_config = tmp_path / ".nycrc"
        nyc_config.write_text(json.dumps({
            "all": True,
            "include": ["src/**/*.js"],
            "reporter": ["html", "text"]
        }))
        
        discovery = TestingDiscovery()
        result = discovery.detect_coverage_config(tmp_path)
        
        assert result is not None
        assert result["tool"] == "istanbul"


class TestTestFileScanning:
    """Test test file pattern scanning."""
    
    def test_scan_python_test_files(self, tmp_path: Path) -> None:
        """Test scanning Python test files."""
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        
        (tests_dir / "test_example.py").write_text("""
def test_something():
    assert True

def test_another():
    assert 1 + 1 == 2
""")
        
        (tests_dir / "test_more.py").write_text("""
class TestExample:
    def test_method(self):
        pass
""")
        
        discovery = TestingDiscovery()
        result = discovery.scan_test_files(tmp_path)
        
        assert result is not None
        assert len(result) >= 2
        assert any("test_example.py" in f["path"] for f in result)
    
    def test_scan_javascript_test_files(self, tmp_path: Path) -> None:
        """Test scanning JavaScript test files."""
        tests_dir = tmp_path / "__tests__"
        tests_dir.mkdir()
        
        (tests_dir / "example.test.js").write_text("""
describe('Example', () => {
  test('should work', () => {
    expect(true).toBe(true);
  });
});
""")
        
        discovery = TestingDiscovery()
        result = discovery.scan_test_files(tmp_path)
        
        assert result is not None
        assert len(result) >= 1


class TestMockDiscovery:
    """Test mock/stub discovery."""
    
    def test_detect_python_mocks(self, tmp_path: Path) -> None:
        """Test detecting Python mock usage."""
        test_file = tmp_path / "test_mocks.py"
        test_file.write_text("""
from unittest.mock import Mock, patch, MagicMock

@patch('module.function')
def test_with_patch(mock_func):
    pass

def test_with_mock():
    mock_obj = Mock()
""")
        
        discovery = TestingDiscovery()
        result = discovery.detect_mocks(tmp_path)
        
        assert result is not None
        assert result["python_mocks"] >= 1
    
    def test_detect_javascript_mocks(self, tmp_path: Path) -> None:
        """Test detecting JavaScript mock usage."""
        test_file = tmp_path / "example.test.js"
        test_file.write_text("""
jest.mock('./module');
const mockFn = jest.fn();

test('with mock', () => {
  const spy = jest.spyOn(obj, 'method');
});
""")
        
        discovery = TestingDiscovery()
        result = discovery.detect_mocks(tmp_path)
        
        assert result is not None
        assert result["javascript_mocks"] >= 1


class TestFullTestingDiscovery:
    """Test complete testing discovery."""
    
    def test_discover_complete_testing_setup(self, tmp_path: Path) -> None:
        """Test discovering complete testing configuration."""
        # Create pytest config
        (tmp_path / "pytest.ini").write_text("[pytest]\ntestpaths = tests\n")
        
        # Create test files
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_example.py").write_text("def test_x(): pass")
        
        # Create coverage config
        (tmp_path / ".coveragerc").write_text("[run]\nsource = src\n")
        
        discovery = TestingDiscovery()
        result = discovery.discover(tmp_path)
        
        assert result is not None
        assert "pytest" in result["frameworks"]
        assert result["total_test_files"] >= 1
        assert "coverage_config" in result
    
    def test_discover_handles_no_tests(self, tmp_path: Path) -> None:
        """Test discovery with no testing configuration."""
        discovery = TestingDiscovery()
        result = discovery.discover(tmp_path)
        
        assert result is not None
        assert result["total_test_files"] == 0
        assert len(result["frameworks"]) == 0
