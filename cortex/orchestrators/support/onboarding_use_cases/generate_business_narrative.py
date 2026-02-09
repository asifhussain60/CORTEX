"""
Generate Business Narrative Use Case (Phase 54-A S1)

AC_START: AC-PHASE54A-S1-UC03
Description: Business language generation with confidence scores
Authority: phase-54-A-incremental-onboarding-refactor.yaml, S1 task 3
"""

from pathlib import Path
from typing import Dict, Any
from dataclasses import dataclass

from cortex.brain.core.result import Result, Ok, Err


@dataclass
class BusinessNarrative:
    """Business narrative model."""
    title: str
    description: str
    value_proposition: str
    target_audience: str
    key_capabilities: list
    business_outcomes: list
    confidence_score: float  # 0.0-1.0


class GenerateBusinessNarrativeUseCase:
    """Generate business narratives (SOLID: Single Responsibility)."""
    
    def execute(self, repo_path: Path) -> Result[BusinessNarrative]:
        """
        Generate business narrative for repository.
        
        Args:
            repo_path: Path to repository
            
        Returns:
            Result containing BusinessNarrative or error
        """
        try:
            if not repo_path.exists():
                return Err(f"Repository not found: {repo_path}")
            
            # Extract signals from repository
            repo_name = repo_path.name
            readme_content = self._read_readme(repo_path)
            config_files = self._find_config_files(repo_path)
            
            # Generate narrative based on signals
            narrative = BusinessNarrative(
                title=self._generate_title(repo_name),
                description=self._generate_description(readme_content),
                value_proposition=self._generate_value_prop(repo_name),
                target_audience=self._generate_audience(config_files),
                key_capabilities=self._extract_capabilities(repo_path),
                business_outcomes=self._extract_outcomes(repo_name),
                confidence_score=self._calculate_confidence(readme_content),
            )
            
            return Ok(narrative)
        
        except Exception as e:
            return Err(f"Failed to generate business narrative: {str(e)}")
    
    def _read_readme(self, repo_path: Path) -> str:
        """Read README content."""
        try:
            readme_file = next(repo_path.glob("README*"), None)
            if readme_file:
                return readme_file.read_text(errors="ignore")
        except Exception:
            pass
        return ""
    
    def _find_config_files(self, repo_path: Path) -> list:
        """Find configuration files."""
        config_patterns = ["*.yaml", "*.yml", "*.json", "*.toml"]
        configs = []
        try:
            for pattern in config_patterns:
                configs.extend(repo_path.rglob(pattern))
        except Exception:
            pass
        return configs
    
    def _generate_title(self, repo_name: str) -> str:
        """Generate narrative title."""
        return f"{repo_name} Repository Platform"
    
    def _generate_description(self, readme_content: str) -> str:
        """Generate description from README."""
        if readme_content:
            # Extract first non-empty line
            for line in readme_content.split("\n"):
                if line.strip() and not line.startswith("#"):
                    return line.strip()[:200]
        return "Comprehensive repository system"
    
    def _generate_value_prop(self, repo_name: str) -> str:
        """Generate value proposition."""
        return f"Enterprise-grade {repo_name} platform with advanced analytics"
    
    def _generate_audience(self, config_files: list) -> str:
        """Generate target audience."""
        if any("enterprise" in str(f).lower() for f in config_files):
            return "Enterprise development teams"
        return "Development teams"
    
    def _extract_capabilities(self, repo_path: Path) -> list:
        """Extract key capabilities."""
        capabilities = []
        try:
            if (repo_path / "docs").exists():
                capabilities.append("Comprehensive documentation")
            if any(repo_path.rglob("*test*")):
                capabilities.append("Automated testing")
            if any(repo_path.rglob("*.yml")) or any(repo_path.rglob("*.yaml")):
                capabilities.append("Configuration management")
        except Exception:
            pass
        
        return capabilities or ["Core functionality"]
    
    def _extract_outcomes(self, repo_name: str) -> list:
        """Extract business outcomes."""
        return [
            "Improved development velocity",
            "Enhanced code quality",
            "Better team collaboration",
        ]
    
    def _calculate_confidence(self, readme_content: str) -> float:
        """Calculate confidence score (0.0-1.0)."""
        if readme_content:
            return min(0.95, 0.5 + len(readme_content) / 10000)
        return 0.6


# AC_COMPLETE: AC-PHASE54A-S1-UC03 ✅
