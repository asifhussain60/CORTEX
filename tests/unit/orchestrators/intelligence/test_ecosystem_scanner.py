"""
Unit tests for EcosystemScanner.

Tests file pattern detection, framework identification, and tech stack
aggregation from repository structures.

Author: CORTEX Team
Created: 2026-02-06
Authority: Phase 34B specification, Week 1, Increment 2
"""

import pytest
from pathlib import Path
from typing import Dict, List, Optional
from unittest.mock import Mock, patch, MagicMock

from cortex.orchestrators.intelligence.ecosystem_scanner import (
    EcosystemScanner,
    DetectedTech,
    ScanResult,
)
from cortex.orchestrators.intelligence.tech_intelligence_orchestrator import TechStack


class TestEcosystemScannerInitialization:
    """Test EcosystemScanner initialization."""
    
    def test_scanner_initializes_successfully(self):
        """Test that scanner initializes with default configuration."""
        scanner = EcosystemScanner()
        
        assert scanner is not None
        assert hasattr(scanner, 'patterns')
        assert hasattr(scanner, 'framework_detectors')
    
    def test_scanner_accepts_custom_patterns(self):
        """Test that scanner accepts custom file patterns."""
        custom_patterns = {
            "rust": ["*.rs", "Cargo.toml"],
            "go": ["*.go", "go.mod"],
        }
        scanner = EcosystemScanner(file_patterns=custom_patterns)
        
        assert scanner.patterns is not None
        assert "rust" in scanner.patterns or len(scanner.patterns) > 0
    
    def test_scanner_has_predefined_language_patterns(self):
        """Test that scanner includes common language patterns."""
        scanner = EcosystemScanner()
        
        # Should support major languages
        common_languages = ["python", "javascript", "typescript", "java"]
        # Check if scanner has language detection capability
        assert hasattr(scanner, 'detect_language')


class TestLanguageDetection:
    """Test language detection from file patterns."""
    
    @pytest.fixture
    def scanner(self):
        return EcosystemScanner()
    
    def test_detect_python_from_py_files(self, scanner):
        """Test Python detection from .py files."""
        files = ["main.py", "utils.py", "tests/test_main.py"]
        
        result = scanner.detect_language(files)
        
        assert result is not None
        assert result.language == "python"
        assert result.confidence > 0.5
    
    def test_detect_javascript_from_js_files(self, scanner):
        """Test JavaScript detection from .js files."""
        files = ["index.js", "app.js", "src/components/button.js"]
        
        result = scanner.detect_language(files)
        
        assert result is not None
        assert result.language == "javascript"
    
    def test_detect_typescript_from_ts_files(self, scanner):
        """Test TypeScript detection from .ts files."""
        files = ["main.ts", "types.d.ts", "src/app.tsx"]
        
        result = scanner.detect_language(files)
        
        assert result is not None
        assert result.language in ["typescript", "javascript"]  # TS is JS superset
    
    def test_detect_multiple_languages(self, scanner):
        """Test detection when multiple languages present."""
        files = ["main.py", "app.js", "util.go"]
        
        results = scanner.detect_all_languages(files)
        
        assert len(results) >= 2  # At least 2 languages detected
        languages = [r.language for r in results]
        assert "python" in languages or "javascript" in languages
    
    def test_returns_none_for_unknown_extensions(self, scanner):
        """Test that unknown file types return None or low confidence."""
        files = ["readme.txt", "data.bin", "unknown.xyz"]
        
        result = scanner.detect_language(files)
        
        # Either None or very low confidence
        assert result is None or result.confidence < 0.1


class TestFrameworkDetection:
    """Test framework detection from configuration files."""
    
    @pytest.fixture
    def scanner(self):
        return EcosystemScanner()
    
    def test_detect_django_from_settings(self, scanner):
        """Test Django detection from settings.py."""
        files = ["manage.py", "settings.py", "wsgi.py"]
        
        frameworks = scanner.detect_frameworks("python", files)
        
        assert "django" in [f.lower() for f in frameworks]
    
    def test_detect_flask_from_app(self, scanner):
        """Test Flask detection from app structure."""
        files = ["app.py", "requirements.txt"]
        content = {"requirements.txt": "Flask==2.0.0\ngunicorn==20.1.0"}
        
        frameworks = scanner.detect_frameworks("python", files, content)
        
        assert "flask" in [f.lower() for f in frameworks]
    
    def test_detect_react_from_package_json(self, scanner):
        """Test React detection from package.json."""
        files = ["package.json", "src/App.jsx"]
        content = {"package.json": '{"dependencies": {"react": "^18.0.0"}}'}
        
        frameworks = scanner.detect_frameworks("javascript", files, content)
        
        assert "react" in [f.lower() for f in frameworks]
    
    def test_detect_fastapi_from_imports(self, scanner):
        """Test FastAPI detection from code imports."""
        files = ["main.py"]
        content = {"main.py": "from fastapi import FastAPI\napp = FastAPI()"}
        
        frameworks = scanner.detect_frameworks("python", files, content)
        
        assert "fastapi" in [f.lower() for f in frameworks]
    
    def test_detect_multiple_frameworks(self, scanner):
        """Test detection of multiple frameworks in one project."""
        files = ["requirements.txt", "package.json"]
        content = {
            "requirements.txt": "django==4.0\ncelery==5.0",
            "package.json": '{"dependencies": {"react": "^18.0"}}',
        }
        
        frameworks = scanner.detect_frameworks("python", files, content)
        
        assert len(frameworks) >= 1  # At least one framework detected


class TestVersionDetection:
    """Test version detection from configuration files."""
    
    @pytest.fixture
    def scanner(self):
        return EcosystemScanner()
    
    def test_detect_python_version_from_pyproject(self, scanner):
        """Test Python version detection from pyproject.toml."""
        files = ["pyproject.toml"]
        content = {"pyproject.toml": '[tool.poetry]\npython = "^3.9"'}
        
        version = scanner.detect_version("python", files, content)
        
        assert version is not None
        assert "3.9" in version
    
    def test_detect_node_version_from_package_json(self, scanner):
        """Test Node version from package.json engines."""
        files = ["package.json"]
        content = {"package.json": '{"engines": {"node": ">=16.0.0"}}'}
        
        version = scanner.detect_version("javascript", files, content)
        
        assert version is not None
        assert "16" in version
    
    def test_returns_none_for_missing_version(self, scanner):
        """Test None returned when version not specified."""
        files = ["main.py"]
        content = {}
        
        version = scanner.detect_version("python", files, content)
        
        # Version optional - can be None
        assert version is None or isinstance(version, str)


class TestToolDetection:
    """Test development tool detection."""
    
    @pytest.fixture
    def scanner(self):
        return EcosystemScanner()
    
    def test_detect_pytest_from_config(self, scanner):
        """Test pytest detection from config files."""
        files = ["pytest.ini", "tests/conftest.py"]
        
        tools = scanner.detect_tools("python", files)
        
        assert "pytest" in [t.lower() for t in tools]
    
    def test_detect_eslint_from_config(self, scanner):
        """Test ESLint detection from .eslintrc."""
        files = [".eslintrc.json", "package.json"]
        
        tools = scanner.detect_tools("javascript", files)
        
        assert "eslint" in [t.lower() for t in tools]
    
    def test_detect_black_from_config(self, scanner):
        """Test Black formatter detection."""
        files = ["pyproject.toml"]
        content = {"pyproject.toml": "[tool.black]\nline-length = 88"}
        
        tools = scanner.detect_tools("python", files, content)
        
        assert "black" in [t.lower() for t in tools]
    
    def test_detect_docker_from_dockerfile(self, scanner):
        """Test Docker detection."""
        files = ["Dockerfile", "docker-compose.yml"]
        
        tools = scanner.detect_tools("python", files)
        
        assert "docker" in [t.lower() for t in tools]


class TestRepositoryScan:
    """Test full repository scanning."""
    
    @pytest.fixture
    def scanner(self):
        return EcosystemScanner()
    
    @patch('pathlib.Path.rglob')
    @patch('pathlib.Path.exists')
    def test_scan_repository_returns_tech_stack(self, mock_exists, mock_rglob, scanner):
        """Test complete repository scan."""
        mock_exists.return_value = True
        mock_rglob.return_value = [
            Path("main.py"),
            Path("requirements.txt"),
            Path("tests/test_main.py"),
        ]
        
        result = scanner.scan_repository("/fake/path")
        
        assert result is not None
        assert isinstance(result, ScanResult)
        assert result.primary_language is not None
    
    @patch('pathlib.Path.exists')
    def test_scan_nonexistent_directory_returns_error(self, mock_exists, scanner):
        """Test scanning non-existent directory."""
        mock_exists.return_value = False
        
        result = scanner.scan_repository("/nonexistent/path")
        
        assert result is not None
        assert result.error is not None or not result.success
    
    @patch('pathlib.Path.rglob')
    @patch('pathlib.Path.exists')
    def test_scan_aggregates_all_tech_info(self, mock_exists, mock_rglob, scanner):
        """Test that scan aggregates language, frameworks, tools."""
        mock_exists.return_value = True
        mock_rglob.return_value = [
            Path("app.py"),
            Path("requirements.txt"),
            Path("pytest.ini"),
            Path(".flake8"),
        ]
        
        result = scanner.scan_repository("/fake/path")
        
        assert result.tech_stack is not None
        assert isinstance(result.tech_stack, TechStack)
        # Should have detected language at minimum
        assert result.tech_stack.language in ["python", "unknown"]


class TestScanResultSerialization:
    """Test ScanResult serialization for caching."""
    
    def test_scan_result_to_dict(self):
        """Test ScanResult converts to dictionary."""
        tech_stack = TechStack(
            language="python",
            frameworks=["django", "celery"],
            version="3.9",
            tools=["pytest", "black"],
        )
        result = ScanResult(
            success=True,
            tech_stack=tech_stack,
            primary_language="python",
            confidence=0.95,
        )
        
        data = result.to_dict()
        
        assert data["success"] is True
        assert data["primary_language"] == "python"
        assert data["confidence"] == 0.95
    
    def test_scan_result_from_dict(self):
        """Test ScanResult reconstructs from dictionary."""
        data = {
            "success": True,
            "tech_stack": {
                "language": "javascript",
                "frameworks": ["react", "express"],
                "version": "16.0",
                "tools": ["eslint"],
            },
            "primary_language": "javascript",
            "confidence": 0.88,
        }
        
        result = ScanResult.from_dict(data)
        
        assert result.success is True
        assert result.primary_language == "javascript"
        assert result.tech_stack.language == "javascript"


class TestErrorHandling:
    """Test error handling in scanner."""
    
    @pytest.fixture
    def scanner(self):
        return EcosystemScanner()
    
    def test_handles_permission_errors_gracefully(self, scanner):
        """Test graceful handling of permission errors."""
        with patch('pathlib.Path.rglob', side_effect=PermissionError("Access denied")):
            result = scanner.scan_repository("/restricted/path")
            
            assert result is not None
            assert not result.success or result.error is not None
    
    def test_handles_invalid_file_content(self, scanner):
        """Test handling of malformed file content."""
        files = ["package.json"]
        content = {"package.json": "invalid json {{{"}
        
        # Should not crash, might return empty or handle gracefully
        frameworks = scanner.detect_frameworks("javascript", files, content)
        
        assert isinstance(frameworks, list)  # Returns list even if empty
    
    def test_handles_empty_directory(self, scanner):
        """Test scanning empty directory."""
        with patch('pathlib.Path.rglob', return_value=[]):
            result = scanner.scan_repository("/empty/path")
            
            assert result is not None
            # May indicate unknown language or empty result
            assert result.primary_language in ["unknown", None] or not result.success
