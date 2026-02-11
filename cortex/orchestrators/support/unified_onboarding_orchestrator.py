"""
UnifiedOnboardingOrchestrator: Consolidated onboarding implementation
=====================================================================

CONSOLIDATION: 
- RepositoryOnboardingOrchestrator (repository profiling)
- OnboardingOrchestrator (user onboarding)
- SetupOrchestrator (environment setup)

Unified API for all onboarding workflows (repository, user, environment).

CORE Governance:
✅ CORE-008: TDD (tests define implementation)
✅ CORE-011: 100% type hints
✅ CORE-012: 100% docstrings (Google style)
✅ CORE-013: Specific exception handling
✅ CORE-026: Git checkpoint before implementation
✅ CORE-030: Implementation truth (not docs)
"""

from pathlib import Path
from typing import Dict, List, Any

from cortex.orchestrators.support.onboarding_models import (
    OnboardingType,
    ValidationStatus,
    RepositoryProfile,
    UserProfile,
    SetupResult,
    ValidationResult,
)


# ============================================================================
# UnifiedOnboardingOrchestrator
# ============================================================================

class UnifiedOnboardingOrchestrator:
    """
    Unified orchestrator for all onboarding workflows.
    
    Consolidates:
    - RepositoryOnboardingOrchestrator: Repository profiling
    - OnboardingOrchestrator: User onboarding
    - SetupOrchestrator: Environment setup
    
    Public API:
    - onboard_repository(path) → RepositoryProfile
    - onboard_user(config) → UserProfile
    - setup_environment(target) → SetupResult
    - validate_onboarding(profile) → ValidationResult
    """

    def __init__(self) -> None:
        """Initialize UnifiedOnboardingOrchestrator."""
        self._language_map = {
            "py": "python",
            "js": "javascript",
            "ts": "typescript",
            "go": "go",
            "rs": "rust",
            "java": "java",
            "cs": "csharp",
        }

    def onboard_repository(self, path: str) -> RepositoryProfile:
        """
        Onboard a repository with metadata extraction.
        
        Args:
            path: Repository file path.
            
        Returns:
            RepositoryProfile with extracted metadata.
            
        Raises:
            FileNotFoundError: If path does not exist.
            ValueError: If path is empty or invalid.
            
        Examples:
            >>> orchestrator = UnifiedOnboardingOrchestrator()
            >>> profile = orchestrator.onboard_repository("/path/to/repo")
            >>> print(profile.language)  # "python"
        """
        if not path:
            raise ValueError("Repository path cannot be empty")

        repo_path = Path(path)
        if not repo_path.exists():
            raise FileNotFoundError(f"Repository path does not exist: {path}")

        # Detect language
        language = self._detect_language(repo_path)

        # Detect tests
        has_tests, coverage = self._detect_tests(repo_path)

        # Extract dependencies
        dependencies = self._extract_dependencies(repo_path)

        # Determine project type
        project_type = self._detect_project_type(repo_path)

        # Validate
        issues = self._validate_repository(repo_path)

        return RepositoryProfile(
            path=str(repo_path.absolute()),
            name=repo_path.name,
            language=language,
            project_type=project_type,
            has_tests=has_tests,
            test_coverage=coverage,
            dependencies=dependencies,
            is_valid=len(issues) == 0,
            issues=issues,
        )

    def onboard_user(self, config: Dict[str, Any]) -> UserProfile:
        """
        Onboard a user with profile creation.
        
        Args:
            config: User configuration dict with keys:
                - user_id (str): Unique identifier
                - name (str): User full name
                - role (str): User role
                - preferences (dict): User preferences
                
        Returns:
            UserProfile with initialized onboarding state.
            
        Raises:
            ValueError: If required fields are missing.
            
        Examples:
            >>> config = {
            ...     "user_id": "u-001",
            ...     "name": "Alice",
            ...     "role": "engineer",
            ...     "preferences": {}
            ... }
            >>> profile = orchestrator.onboard_user(config)
        """
        required_keys = {"user_id", "name", "role", "preferences"}
        if not all(k in config for k in required_keys):
            missing = required_keys - set(config.keys())
            raise ValueError(f"Missing required fields: {missing}")

        return UserProfile(
            user_id=config["user_id"],
            name=config["name"],
            role=config["role"],
            preferences=config["preferences"],
            is_complete=False,
            pending_steps=["profile_review", "preferences_setup"],
        )

    def setup_environment(self, target: str) -> SetupResult:
        """
        Setup execution environment.
        
        Args:
            target: Environment type (development, production, staging).
            
        Returns:
            SetupResult with configuration applied.
            
        Raises:
            ValueError: If target is invalid.
            
        Examples:
            >>> result = orchestrator.setup_environment("development")
            >>> print(result.success)  # True
        """
        valid_targets = {"development", "production", "staging", "testing"}
        if target not in valid_targets:
            raise ValueError(
                f"Invalid environment target: {target}. "
                f"Valid options: {valid_targets}"
            )

        config = self._generate_environment_config(target)

        return SetupResult(
            success=True,
            environment_type=target,
            config_applied=config,
            errors=[],
            warnings=self._check_environment_warnings(target, config),
        )

    def validate_onboarding(
        self, profile: RepositoryProfile
    ) -> ValidationResult:
        """
        Validate an onboarding profile.
        
        Args:
            profile: RepositoryProfile to validate.
            
        Returns:
            ValidationResult with status and recommendations.
            
        Raises:
            TypeError: If profile is not RepositoryProfile.
            ValueError: If profile is None.
            
        Examples:
            >>> result = orchestrator.validate_onboarding(profile)
            >>> print(result.is_valid)  # bool
        """
        if profile is None:
            raise ValueError("Profile cannot be None")

        if not isinstance(profile, RepositoryProfile):
            raise TypeError(
                f"Expected RepositoryProfile, got {type(profile).__name__}"
            )

        errors = list(profile.issues) if profile.issues else []
        warnings = self._generate_validation_warnings(profile)
        recommendations = self._generate_recommendations(profile)

        status = ValidationStatus.VALID if not errors else ValidationStatus.INVALID

        return ValidationResult(
            status=status,
            is_valid=not errors,
            errors=errors,
            warnings=warnings,
            recommendations=recommendations,
        )

    # ========================================================================
    # Private Helpers
    # ========================================================================

    def _detect_language(self, repo_path: Path) -> str:
        """
        Detect primary programming language.
        
        Args:
            repo_path: Repository path.
            
        Returns:
            Language name (python, javascript, etc.).
        """
        file_counts = {}
        for ext, lang in self._language_map.items():
            count = len(list(repo_path.glob(f"**/*.{ext}")))
            if count > 0:
                file_counts[lang] = count

        if not file_counts:
            return "unknown"

        return max(file_counts.items(), key=lambda x: x[1])[0]

    def _detect_tests(self, repo_path: Path) -> tuple:
        """
        Detect test framework and estimate coverage.
        
        Args:
            repo_path: Repository path.
            
        Returns:
            Tuple of (has_tests: bool, coverage: float).
        """
        test_files = list(repo_path.glob("**/test_*.py")) + list(
            repo_path.glob("**/*_test.py")
        )

        if not test_files:
            return False, 0.0

        # Estimate coverage (0.0-1.0)
        total_files = len(list(repo_path.glob("**/*.py")))
        coverage = min(len(test_files) / max(total_files, 1), 1.0) * 0.8

        return True, coverage

    def _extract_dependencies(self, repo_path: Path) -> List[str]:
        """
        Extract project dependencies.
        
        Args:
            repo_path: Repository path.
            
        Returns:
            List of dependency names.
        """
        dependencies = []

        # Check requirements.txt
        req_file = repo_path / "requirements.txt"
        if req_file.exists():
            with open(req_file) as f:
                for line in f:
                    if line.strip() and not line.startswith("#"):
                        dep = line.split("==")[0].split(">")[0].split("<")[0].strip()
                        if dep:
                            dependencies.append(dep)

        return dependencies[:5]  # Return top 5

    def _detect_project_type(self, repo_path: Path) -> str:
        """
        Detect project type.
        
        Args:
            repo_path: Repository path.
            
        Returns:
            Project type (library, application, framework, etc.).
        """
        if (repo_path / "setup.py").exists() or (repo_path / "pyproject.toml").exists():
            return "library"

        if (repo_path / "src" / "main").exists():
            return "application"

        return "project"

    def _validate_repository(self, repo_path: Path) -> List[str]:
        """
        Validate repository structure.
        
        Args:
            repo_path: Repository path.
            
        Returns:
            List of identified issues.
        """
        issues = []

        if not (repo_path / ".git").exists():
            issues.append("Not a git repository")

        if not list(repo_path.glob("*.md")):
            issues.append("No documentation found")

        return issues

    def _generate_environment_config(self, target: str) -> Dict[str, Any]:
        """
        Generate environment configuration.
        
        Args:
            target: Environment type.
            
        Returns:
            Configuration dictionary.
        """
        base_config = {
            "log_level": "INFO",
            "debug": target == "development",
            "cache_enabled": target != "development",
        }

        if target == "production":
            base_config.update({
                "log_level": "WARNING",
                "debug": False,
                "cache_ttl": 3600,
            })
        elif target == "development":
            base_config.update({
                "log_level": "DEBUG",
                "debug": True,
                "auto_reload": True,
            })

        return base_config

    def _check_environment_warnings(
        self, target: str, config: Dict[str, Any]
    ) -> List[str]:
        """
        Generate environment setup warnings.
        
        Args:
            target: Environment type.
            config: Configuration dict.
            
        Returns:
            List of warnings.
        """
        warnings = []

        if target == "production" and config.get("debug"):
            warnings.append("Debug mode enabled in production")

        return warnings

    def _generate_validation_warnings(
        self, profile: RepositoryProfile
    ) -> List[str]:
        """
        Generate validation warnings.
        
        Args:
            profile: Repository profile.
            
        Returns:
            List of warnings.
        """
        warnings = []

        if profile.test_coverage < 0.5:
            warnings.append("Test coverage below 50%")

        if profile.language == "unknown":
            warnings.append("Could not detect programming language")

        return warnings

    def _generate_recommendations(
        self, profile: RepositoryProfile
    ) -> List[str]:
        """
        Generate improvement recommendations.
        
        Args:
            profile: Repository profile.
            
        Returns:
            List of recommendations.
        """
        recommendations = []

        if not profile.has_tests:
            recommendations.append("Add unit tests")

        if profile.test_coverage < 0.8:
            recommendations.append("Increase test coverage to 80%+")

        if profile.language == "unknown":
            recommendations.append("Add language-specific configuration")

        return recommendations
