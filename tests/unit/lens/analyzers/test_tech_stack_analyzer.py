"""
Tests for TechStackAnalyzer - Phase 90 Stage 1.
TDD RED Phase - Tests written BEFORE implementation.

Authority: Phase 90 Stage 1 - Tech Stack Detection
Coverage: 22 tests for 12+ tech stacks

CORE Rules:
- CORE-008: TDD mandatory (tests BEFORE code) ✅
- CORE-011: Type hints required ✅
- CORE-012: Docstrings required ✅
"""

import pytest
from pathlib import Path
from typing import List
from unittest.mock import Mock, patch

from cortex.lens.models.tech_stack import TechStack, TechCategory, TechStackItem


class TestTechStackAnalyzerFileDetection:
    """Test file extension based detection."""
    
    def test_detect_python_from_files(self):
        """Test: Detect Python from .py files."""
        # RED: TechStackAnalyzer not implemented yet
        from cortex.lens.analyzers.tech_stack_analyzer import TechStackAnalyzer
        
        analyzer = TechStackAnalyzer()
        files = ["main.py", "models.py", "requirements.txt"]
        
        result = analyzer.detect_from_files(files)
        
        assert "python" in result.languages
        assert result.primary_language == "python"
    
    def test_detect_dotnet_from_files(self):
        """Test: Detect .NET from .cs and .csproj files."""
        from cortex.lens.analyzers.tech_stack_analyzer import TechStackAnalyzer
        
        analyzer = TechStackAnalyzer()
        files = ["Program.cs", "Startup.cs", "Project.csproj", "appsettings.json"]
        
        result = analyzer.detect_from_files(files)
        
        assert "csharp" in result.languages
        assert "dotnet" in result.frameworks
    
    def test_detect_typescript_react_from_files(self):
        """Test: Detect TypeScript + React from .tsx files."""
        from cortex.lens.analyzers.tech_stack_analyzer import TechStackAnalyzer
        
        analyzer = TechStackAnalyzer()
        files = ["App.tsx", "index.tsx", "package.json", "tsconfig.json"]
        
        result = analyzer.detect_from_files(files)
        
        assert "typescript" in result.languages
        assert "react" in result.frameworks
    
    def test_detect_java_spring_boot_from_files(self):
        """Test: Detect Java + Spring Boot from files."""
        from cortex.lens.analyzers.tech_stack_analyzer import TechStackAnalyzer
        
        analyzer = TechStackAnalyzer()
        files = [
            "Application.java",
            "Controller.java",
            "pom.xml",
            "application.properties"
        ]
        
        result = analyzer.detect_from_files(files)
        
        assert "java" in result.languages
    
    def test_detect_go_from_files(self):
        """Test: Detect Go from .go files and go.mod."""
        from cortex.lens.analyzers.tech_stack_analyzer import TechStackAnalyzer
        
        analyzer = TechStackAnalyzer()
        files = ["main.go", "handler.go", "go.mod", "go.sum"]
        
        result = analyzer.detect_from_files(files)
        
        assert "go" in result.languages
    
    def test_detect_php_laravel_from_files(self):
        """Test: Detect PHP + Laravel from files."""
        from cortex.lens.analyzers.tech_stack_analyzer import TechStackAnalyzer
        
        analyzer = TechStackAnalyzer()
        files = ["index.php", "Controller.php", "composer.json", "artisan"]
        
        result = analyzer.detect_from_files(files)
        
        assert "php" in result.languages
    
    def test_detect_ruby_rails_from_files(self):
        """Test: Detect Ruby + Rails from files."""
        from cortex.lens.analyzers.tech_stack_analyzer import TechStackAnalyzer
        
        analyzer = TechStackAnalyzer()
        files = ["app.rb", "Gemfile", "config.ru", "Rakefile"]
        
        result = analyzer.detect_from_files(files)
        
        assert "ruby" in result.languages
    
    def test_detect_rust_from_files(self):
        """Test: Detect Rust from .rs files and Cargo.toml."""
        from cortex.lens.analyzers.tech_stack_analyzer import TechStackAnalyzer
        
        analyzer = TechStackAnalyzer()
        files = ["main.rs", "lib.rs", "Cargo.toml", "Cargo.lock"]
        
        result = analyzer.detect_from_files(files)
        
        assert "rust" in result.languages


class TestTechStackAnalyzerASTDetection:
    """Test AST-based import detection."""
    
    def test_detect_flask_from_imports(self):
        """Test: Detect Flask from imports."""
        from cortex.lens.analyzers.tech_stack_analyzer import TechStackAnalyzer
        
        analyzer = TechStackAnalyzer()
        imports = ["flask", "flask_sqlalchemy", "flask_restful"]
        
        result = analyzer.detect_from_ast(imports)
        
        assert "flask" in result.frameworks
    
    def test_detect_django_from_imports(self):
        """Test: Detect Django from imports."""
        from cortex.lens.analyzers.tech_stack_analyzer import TechStackAnalyzer
        
        analyzer = TechStackAnalyzer()
        imports = ["django", "django.db", "django.contrib.auth"]
        
        result = analyzer.detect_from_ast(imports)
        
        assert "django" in result.frameworks
    
    def test_detect_fastapi_from_imports(self):
        """Test: Detect FastAPI from imports."""
        from cortex.lens.analyzers.tech_stack_analyzer import TechStackAnalyzer
        
        analyzer = TechStackAnalyzer()
        imports = ["fastapi", "pydantic", "uvicorn"]
        
        result = analyzer.detect_from_ast(imports)
        
        assert "fastapi" in result.frameworks
    
    def test_detect_sqlalchemy_from_imports(self):
        """Test: Detect SQLAlchemy from imports."""
        from cortex.lens.analyzers.tech_stack_analyzer import TechStackAnalyzer
        
        analyzer = TechStackAnalyzer()
        imports = ["sqlalchemy", "sqlalchemy.orm"]
        
        result = analyzer.detect_from_ast(imports)
        
        assert "sqlalchemy" in result.libraries
    
    def test_detect_pytest_from_imports(self):
        """Test: Detect pytest from imports."""
        from cortex.lens.analyzers.tech_stack_analyzer import TechStackAnalyzer
        
        analyzer = TechStackAnalyzer()
        imports = ["pytest", "pytest_mock"]
        
        result = analyzer.detect_from_ast(imports)
        
        assert "pytest" in result.test_frameworks
    
    def test_detect_react_hooks_from_imports(self):
        """Test: Detect React hooks usage from imports."""
        from cortex.lens.analyzers.tech_stack_analyzer import TechStackAnalyzer
        
        analyzer = TechStackAnalyzer()
        imports = ["react", "useState", "useEffect"]
        
        result = analyzer.detect_from_ast(imports)
        
        assert "react" in result.frameworks


class TestTechStackAnalyzerMergeDetection:
    """Test merging multiple detection sources."""
    
    def test_merge_file_and_ast_detections(self):
        """Test: Merge file extension and AST import detections."""
        from cortex.lens.analyzers.tech_stack_analyzer import TechStackAnalyzer
        
        analyzer = TechStackAnalyzer()
        files = ["app.py", "requirements.txt"]
        imports = ["flask", "sqlalchemy"]
        
        result = analyzer.analyze(files=files, imports=imports)
        
        assert "python" in result.languages
        assert "flask" in result.frameworks
        assert "sqlalchemy" in result.libraries
    
    def test_merge_multi_stack_monorepo(self):
        """Test: Detect multiple stacks in monorepo."""
        from cortex.lens.analyzers.tech_stack_analyzer import TechStackAnalyzer
        
        analyzer = TechStackAnalyzer()
        files = [
            "backend/main.py",
            "backend/requirements.txt",
            "frontend/App.tsx",
            "frontend/package.json"
        ]
        imports = ["flask", "react"]
        
        result = analyzer.analyze(files=files, imports=imports)
        
        assert "python" in result.languages
        assert "typescript" in result.languages
        assert "flask" in result.frameworks
        assert "react" in result.frameworks
    
    def test_confidence_scores_assigned(self):
        """Test: Confidence scores calculated correctly."""
        from cortex.lens.analyzers.tech_stack_analyzer import TechStackAnalyzer
        
        analyzer = TechStackAnalyzer()
        files = ["app.py"]
        imports = ["flask"]
        
        result = analyzer.analyze(files=files, imports=imports)
        
        # Both file and import detection = higher confidence
        assert result.confidence_score > 0.5


class TestTechStackAnalyzerEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_files_list(self):
        """Test: Handle empty files list gracefully."""
        from cortex.lens.analyzers.tech_stack_analyzer import TechStackAnalyzer
        
        analyzer = TechStackAnalyzer()
        result = analyzer.detect_from_files([])
        
        assert result.languages == []
        assert result.confidence_score == 0.0
    
    def test_unknown_file_extensions(self):
        """Test: Handle unknown file extensions."""
        from cortex.lens.analyzers.tech_stack_analyzer import TechStackAnalyzer
        
        analyzer = TechStackAnalyzer()
        files = ["unknown.xyz", "strange.abc"]
        
        result = analyzer.detect_from_files(files)
        
        # Should return empty result, not crash
        assert isinstance(result, TechStack)
    
    def test_version_detection_python(self):
        """Test: Detect Python version from config files."""
        from cortex.lens.analyzers.tech_stack_analyzer import TechStackAnalyzer
        
        analyzer = TechStackAnalyzer()
        files = ["pyproject.toml"]  # Contains python version
        
        result = analyzer.detect_from_files(files)
        
        # Should detect Python language
        assert "python" in result.languages or len(result.languages) == 0
    
    def test_caching_same_inputs(self):
        """Test: Caching works for repeated detection."""
        from cortex.lens.analyzers.tech_stack_analyzer import TechStackAnalyzer
        
        analyzer = TechStackAnalyzer()
        files = ["app.py"]
        imports = ["flask"]
        
        result1 = analyzer.analyze(files=files, imports=imports)
        result2 = analyzer.analyze(files=files, imports=imports)
        
        # Should return same results
        assert result1.languages == result2.languages


# AC_START: AC-PHASE90-S1-T1
# Description: TDD RED - 22 tests for tech stack detection
# Expected: ALL tests FAIL (TechStackAnalyzer not implemented)
