"""
Golden tests for production onboarding workflow (E2E).

Authority: Phase 29 S2 | Zero-Mock Philosophy
Test Count: 8 golden tests
"""
import pytest
from pathlib import Path
from cortex.infrastructure.repositories.onboarding_service import OnboardingService


class TestProductionOnboarding:
    """Golden test: Complete repository onboarding workflow."""
    
    def test_onboard_python_repository(self, tmp_path: Path) -> None:
        """Golden: Onboard Python repository end-to-end."""
        service = OnboardingService()
        
        # Create mock Python repo
        repo_path = tmp_path / "test-python-app"
        repo_path.mkdir()
        (repo_path / "main.py").write_text("def hello(): pass")
        (repo_path / "requirements.txt").write_text("pytest==8.0.0")
        
        # Onboard
        result = service.onboard_repository(repo_path)
        
        assert result.success is True
        assert result.language == "python"
        assert result.files_analyzed > 0
    
    def test_onboard_typescript_repository(self, tmp_path: Path) -> None:
        """Golden: Onboard TypeScript repository end-to-end."""
        service = OnboardingService()
        
        # Create mock TypeScript repo
        repo_path = tmp_path / "test-ts-app"
        repo_path.mkdir()
        (repo_path / "index.ts").write_text("export function hello() {}")
        (repo_path / "package.json").write_text('{"name": "test"}')
        
        result = service.onboard_repository(repo_path)
        
        assert result.success is True
        assert result.language == "typescript"
    
    def test_onboard_generates_security_report(self, tmp_path: Path) -> None:
        """Golden: Onboarding generates security scan report."""
        service = OnboardingService()
        
        repo_path = tmp_path / "test-app"
        repo_path.mkdir()
        (repo_path / "app.py").write_text("import os; password = 'hardcoded'")
        
        result = service.onboard_repository(repo_path)
        
        assert result.security_issues > 0
        assert "hardcoded" in str(result.security_report).lower()


class TestProductionAnalyze:
    """Golden test: Code analysis workflow."""
    
    def test_analyze_python_codebase(self, tmp_path: Path) -> None:
        """Golden: Analyze Python codebase for patterns."""
        from cortex.lens.analyzers.python_analyzer import PythonAnalyzer
        
        analyzer = PythonAnalyzer()
        
        code_path = tmp_path / "test.py"
        code_path.write_text("""
def calculate(x, y):
    return x + y

class Calculator:
    def add(self, a, b):
        return a + b
""")
        
        result = analyzer.analyze_file(code_path)
        
        assert result.functions_found >= 2
        assert result.classes_found >= 1
    
    def test_detect_patterns(self, tmp_path: Path) -> None:
        """Golden: Detect design patterns in code."""
        from cortex.core.core.intelligence.pattern_detector import PatternDetector
        from cortex.core.core.intelligence.ast_intelligence import ASTIntelligenceEngine
        
        detector = PatternDetector()
        ast_intel = ASTIntelligenceEngine()
        
        code_path = tmp_path / "singleton.py"
        code_path.write_text("""
class Singleton:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
""")
        
        parse_result = ast_intel.parse_file(code_path)
        patterns = detector.detect_patterns(parse_result)
        
        assert len(patterns) > 0
        assert any(p.pattern_type == "SINGLETON" for p in patterns)
