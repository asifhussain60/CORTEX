"""
OnboardingService — repository onboarding with security scanning.

Authority: Phase 29 S2 | Production Verification
Purpose: E2E onboarding workflow for golden tests
"""
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class OnboardingResult:
    """Result of repository onboarding."""
    success: bool
    language: str
    files_analyzed: int
    security_issues: int
    security_report: str


class OnboardingService:
    """
    Repository onboarding service with security scanning.
    
    Workflow:
    1. Detect primary language
    2. Analyze file structure
    3. Run security scan
    4. Generate onboarding report
    
    Example:
        service = OnboardingService()
        result = service.onboard_repository(Path("/path/to/repo"))
    """
    
    def __init__(self) -> None:
        """Initialize onboarding service."""
        self.supported_languages = ["python", "typescript", "javascript", "csharp"]
    
    def onboard_repository(self, repo_path: Path) -> OnboardingResult:
        """
        Onboard repository with security scanning.
        
        Args:
            repo_path: Path to repository
            
        Returns:
            OnboardingResult with analysis data
        """
        # Detect language
        language = self._detect_language(repo_path)
        
        # Analyze files
        files = list(repo_path.rglob("*"))
        files_analyzed = len([f for f in files if f.is_file()])
        
        # Security scan
        security_issues, security_report = self._run_security_scan(repo_path)
        
        return OnboardingResult(
            success=True,
            language=language,
            files_analyzed=files_analyzed,
            security_issues=security_issues,
            security_report=security_report
        )
    
    def _detect_language(self, repo_path: Path) -> str:
        """Detect primary language from file extensions."""
        if list(repo_path.glob("*.py")) or (repo_path / "requirements.txt").exists():
            return "python"
        elif list(repo_path.glob("*.ts")) or (repo_path / "package.json").exists():
            return "typescript"
        elif list(repo_path.glob("*.js")):
            return "javascript"
        elif list(repo_path.glob("*.cs")) or (repo_path / "*.csproj"):
            return "csharp"
        return "unknown"
    
    def _run_security_scan(self, repo_path: Path) -> tuple[int, str]:
        """Run security scan on repository."""
        issues = []
        
        # Scan Python files for hardcoded secrets
        for py_file in repo_path.rglob("*.py"):
            content = py_file.read_text()
            if "password" in content.lower() and "=" in content:
                issues.append(f"Potential hardcoded password in {py_file.name}")
        
        return len(issues), "\n".join(issues) if issues else "No security issues detected"
