"""
KnowledgeSynthesizer: Generates best practices, TDD patterns, and security rules.

Synthesizes knowledge from multiple sources (internal KB, GitHub, docs, community)
into actionable templates and configuration files.

Features:
- YAML generation for best practices
- TDD pattern template rendering
- Security rule generation (OWASP-aligned)
- Multi-source knowledge integration
- Thread-safe synthesis caching
- Multi-language support

Author: Asif Hussain (CORTEX Phase 34B)
"""

import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from cortex.orchestrators.intelligence.types import TechStack


class KnowledgeSource(Enum):
    """Knowledge source types."""
    INTERNAL = "internal"  # CORTEX knowledge base
    GITHUB = "github"  # GitHub repositories
    DOCS = "docs"  # Official documentation
    COMMUNITY = "community"  # Community resources


class TemplateType(Enum):
    """Template types for synthesis output."""
    BEST_PRACTICES = "best_practices"
    TDD_PATTERN = "tdd_pattern"
    SECURITY_RULES = "security_rules"


@dataclass
class SynthesisResult:
    """Result of knowledge synthesis operation."""
    content: str
    source: KnowledgeSource
    template_type: TemplateType
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


class KnowledgeSynthesizer:
    """
    Synthesizes actionable knowledge from multiple sources.

    Generates YAML configurations, TDD templates, and security rules
    tailored to specific tech stacks.
    """

    # Language-specific best practices knowledge base
    BEST_PRACTICES_KB = {
        "python": {
            "general": [
                "Use type hints for all function signatures",
                "Follow PEP 8 style guidelines",
                "Use dataclasses for data containers",
                "Prefer composition over inheritance",
                "Use context managers for resource management",
            ],
            "frameworks": {
                "django": [
                    "Use Django ORM for database operations",
                    "Implement custom user models early",
                    "Use Django forms for input validation",
                    "Enable CSRF protection on all forms",
                    "Use select_related/prefetch_related for query optimization",
                ],
                "fastapi": [
                    "Use Pydantic models for request/response validation",
                    "Implement dependency injection for shared resources",
                    "Use async/await for I/O operations",
                    "Enable CORS middleware for API endpoints",
                    "Use APIRouter for organizing endpoints",
                ],
                "flask": [
                    "Use blueprints for application structure",
                    "Implement proper error handlers",
                    "Use Flask-SQLAlchemy for database operations",
                    "Enable CSRF protection with Flask-WTF",
                    "Use application factory pattern",
                ],
            },
            "tools": {
                "pytest": ["Use fixtures for test setup", "Organize tests with classes"],
                "black": ["Configure line length in pyproject.toml"],
                "mypy": ["Enable strict mode for maximum type safety"],
            },
        },
        "javascript": {
            "general": [
                "Use const for immutable bindings",
                "Prefer arrow functions for callbacks",
                "Use async/await over promise chains",
                "Enable strict mode",
                "Use ES6+ features",
            ],
            "frameworks": {
                "react": [
                    "Use functional components with hooks",
                    "Implement proper key props in lists",
                    "Use useEffect for side effects",
                    "Lift state up when sharing between components",
                    "Use React.memo for performance optimization",
                ],
                "express": [
                    "Use middleware for cross-cutting concerns",
                    "Implement proper error handling middleware",
                    "Use helmet for security headers",
                    "Enable CORS with proper configuration",
                    "Use express-validator for input validation",
                ],
                "vue": [
                    "Use Composition API for complex components",
                    "Implement proper prop validation",
                    "Use computed properties for derived state",
                    "Emit custom events for parent communication",
                    "Use Vue Router for navigation",
                ],
            },
            "tools": {
                "jest": ["Use describe blocks for test organization"],
                "eslint": ["Extend recommended configurations"],
            },
        },
        "typescript": {
            "general": [
                "Enable strict mode in tsconfig.json",
                "Use interfaces for object shapes",
                "Prefer type inference where possible",
                "Use enums for fixed sets of values",
                "Avoid any type except for migration",
            ],
            "frameworks": {
                "angular": [
                    "Use services for business logic",
                    "Implement proper dependency injection",
                    "Use RxJS for async operations",
                    "Follow Angular style guide",
                    "Use lazy loading for feature modules",
                ],
                "nest": [
                    "Use decorators for metadata",
                    "Implement proper module organization",
                    "Use pipes for data transformation",
                    "Use guards for authorization",
                    "Implement proper exception filters",
                ],
            },
        },
        "java": {
            "general": [
                "Follow Java naming conventions",
                "Use interfaces for abstraction",
                "Implement proper exception handling",
                "Use streams for collection operations",
                "Follow SOLID principles",
            ],
        },
        "go": {
            "general": [
                "Use gofmt for consistent formatting",
                "Handle errors explicitly",
                "Use defer for cleanup",
                "Prefer composition over inheritance",
                "Use goroutines for concurrency",
            ],
        },
        "rust": {
            "general": [
                "Leverage the borrow checker",
                "Use Result for error handling",
                "Prefer ownership over cloning",
                "Use cargo for dependency management",
                "Follow Rust naming conventions",
            ],
        },
    }

    # TDD framework patterns
    TDD_PATTERNS = {
        "pytest": """# Pytest Pattern
import pytest

class Test{ClassName}:
    \"\"\"Test suite for {ClassName}.\"\"\"

    @pytest.fixture
    def {fixture_name}(self):
        \"\"\"Setup test fixture.\"\"\"
        return {ClassName}()

    def test_{method_name}_success(self, {fixture_name}):
        \"\"\"Test {method_name} succeeds with valid input.\"\"\"
        result = {fixture_name}.{method_name}()
        assert result is not None

    def test_{method_name}_handles_error(self, {fixture_name}):
        \"\"\"Test {method_name} handles errors gracefully.\"\"\"
        with pytest.raises(ValueError):
            {fixture_name}.{method_name}(invalid_input)
""",
        "jest": """// Jest Pattern
describe('{ClassName}', () => {{
    let instance;

    beforeEach(() => {{
        instance = new {ClassName}();
    }});

    test('{methodName} succeeds with valid input', () => {{
        const result = instance.{methodName}();
        expect(result).toBeDefined();
    }});

    test('{methodName} handles errors gracefully', () => {{
        expect(() => instance.{methodName}(invalidInput)).toThrow();
    }});
}});
""",
        "junit": """// JUnit 5 Pattern
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import static org.junit.jupiter.api.Assertions.*;

class {ClassName}Test {{
    private {ClassName} instance;

    @BeforeEach
    void setUp() {{
        instance = new {ClassName}();
    }}

    @Test
    void {methodName}_SucceedsWithValidInput() {{
        var result = instance.{methodName}();
        assertNotNull(result);
    }}

    @Test
    void {methodName}_HandlesErrorsGracefully() {{
        assertThrows(IllegalArgumentException.class,
            () -> instance.{methodName}(invalidInput));
    }}
}}
""",
    }

    # Security rules templates
    SECURITY_RULES = {
        "python": {
            "injection": [
                "Use parameterized queries for database operations",
                "Never use eval() or exec() with user input",
                "Validate and sanitize all user input",
            ],
            "authentication": [
                "Use bcrypt or argon2 for password hashing",
                "Implement proper session management",
                "Use JWT tokens with short expiration",
            ],
            "xss": [
                "Escape all user-provided content in templates",
                "Use Content Security Policy headers",
                "Validate and sanitize HTML input",
            ],
        },
        "javascript": {
            "injection": [
                "Use parameterized queries with ORMs",
                "Validate all input on both client and server",
                "Avoid using dangerouslySetInnerHTML in React",
            ],
            "authentication": [
                "Store tokens in httpOnly cookies",
                "Implement CSRF protection",
                "Use secure password hashing (bcrypt)",
            ],
        },
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize KnowledgeSynthesizer.

        Args:
            config: Optional configuration dictionary
        """
        config = config or {}
        self.cache_enabled = config.get("cache_enabled", True)
        self.template_dir = config.get("template_dir", None)
        self.max_cache_size = config.get("max_cache_size", 100)

        # Thread-safe caching
        self._cache: Dict[str, SynthesisResult] = {}
        self._cache_lock = threading.Lock()
        self._cache_hits = 0
        self._cache_misses = 0

    def synthesize_best_practices(
        self,
        tech_stack: Optional[TechStack],
        source: KnowledgeSource = KnowledgeSource.INTERNAL
    ) -> SynthesisResult:
        """
        Synthesize best practices YAML for tech stack.

        Args:
            tech_stack: Technology stack to generate practices for
            source: Knowledge source to use

        Returns:
            SynthesisResult with YAML content
        """
        if tech_stack is None:
            return self._create_empty_result(TemplateType.BEST_PRACTICES, source)

        # Check cache
        cache_key = f"bp_{tech_stack.language}_{','.join(tech_stack.frameworks)}"
        if self.cache_enabled:
            cached = self._get_from_cache(cache_key)
            if cached:
                return cached

        # Handle external sources with fallback
        original_source = source
        if source != KnowledgeSource.INTERNAL:
            try:
                result = self._fetch_from_external_source(tech_stack, source, TemplateType.BEST_PRACTICES)
                if result:
                    self._store_in_cache(cache_key, result)
                    return result
            except Exception:
                # Fallback to internal source
                source = KnowledgeSource.INTERNAL

        # Generate from internal knowledge base
        yaml_content = self._generate_best_practices_yaml(tech_stack)

        result = SynthesisResult(
            content=yaml_content,
            source=KnowledgeSource.INTERNAL,  # Mark as internal since we fell back
            template_type=TemplateType.BEST_PRACTICES,
            timestamp=datetime.now(),
            metadata={
                "language": tech_stack.language,
                "frameworks": tech_stack.frameworks,
                "fallback": original_source != KnowledgeSource.INTERNAL
            }
        )

        if self.cache_enabled:
            self._store_in_cache(cache_key, result)

        return result

    def generate_tdd_patterns(
        self,
        tech_stack: TechStack,
        source: KnowledgeSource = KnowledgeSource.INTERNAL
    ) -> SynthesisResult:
        """
        Generate TDD pattern templates for tech stack.

        Args:
            tech_stack: Technology stack to generate patterns for
            source: Knowledge source to use

        Returns:
            SynthesisResult with TDD pattern template
        """
        # Determine TDD framework from tools
        tdd_framework = self._detect_tdd_framework(tech_stack)

        # Get pattern template
        pattern = self.TDD_PATTERNS.get(tdd_framework, self.TDD_PATTERNS.get("pytest", ""))

        # Add framework-specific patterns if available
        framework_patterns = self._get_framework_tdd_patterns(tech_stack)
        if framework_patterns:
            pattern += f"\n\n# Framework-specific patterns:\n{framework_patterns}"

        result = SynthesisResult(
            content=pattern,
            source=source,
            template_type=TemplateType.TDD_PATTERN,
            timestamp=datetime.now(),
            metadata={
                "tdd_framework": tdd_framework,
                "language": tech_stack.language
            }
        )

        return result

    def generate_security_rules(
        self,
        tech_stack: TechStack,
        source: KnowledgeSource = KnowledgeSource.INTERNAL
    ) -> SynthesisResult:
        """
        Generate security rules for tech stack.

        Args:
            tech_stack: Technology stack to generate rules for
            source: Knowledge source to use

        Returns:
            SynthesisResult with security rules
        """
        language = tech_stack.language.lower()
        rules = self.SECURITY_RULES.get(language, {})

        # Build security rules document
        content_lines = [f"# Security Rules for {tech_stack.language}\n"]

        for category, rule_list in rules.items():
            content_lines.append(f"\n## {category.upper()}")
            for rule in rule_list:
                content_lines.append(f"- {rule}")

        # Add framework-specific rules
        framework_rules = self._get_framework_security_rules(tech_stack)
        if framework_rules:
            content_lines.append("\n## Framework-Specific Security")
            content_lines.extend(framework_rules)

        content = "\n".join(content_lines)

        result = SynthesisResult(
            content=content,
            source=source,
            template_type=TemplateType.SECURITY_RULES,
            timestamp=datetime.now(),
            metadata={"language": tech_stack.language}
        )

        return result

    def invalidate_cache(self):
        """Invalidate all cached synthesis results."""
        with self._cache_lock:
            self._cache.clear()
            self._cache_hits = 0
            self._cache_misses = 0

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with hits (int), misses (int), and hit_rate (float)
        """
        with self._cache_lock:
            total = self._cache_hits + self._cache_misses
            hit_rate = (self._cache_hits / total * 100) if total > 0 else 0.0

            return {
                "hits": self._cache_hits,
                "misses": self._cache_misses,
                "hit_rate": round(hit_rate, 2),
            }

    # Private helper methods

    def _generate_best_practices_yaml(self, tech_stack: TechStack) -> str:
        """Generate YAML content for best practices."""
        language = tech_stack.language.lower()
        practices_data = self.BEST_PRACTICES_KB.get(language, {})

        # Build YAML structure
        yaml_data = {
            "language": tech_stack.language,
            "version": tech_stack.version,
            "best_practices": {
                "general": practices_data.get("general", []),
            }
        }

        # Add framework-specific practices
        if tech_stack.frameworks and "frameworks" in practices_data:
            framework_practices = {}
            for framework in tech_stack.frameworks:
                if framework.lower() in practices_data["frameworks"]:
                    framework_practices[framework] = practices_data["frameworks"][framework.lower()]

            if framework_practices:
                yaml_data["frameworks"] = framework_practices

        # Note: TechStack no longer has tools attribute
        # Tools are now included in frameworks list

        return yaml.dump(yaml_data, default_flow_style=False, sort_keys=False)

    def _detect_tdd_framework(self, tech_stack: TechStack) -> str:
        """Detect TDD framework from tech stack frameworks list."""
        # Check frameworks list for TDD frameworks
        for framework in tech_stack.frameworks:
            framework_lower = framework.lower()
            if "pytest" in framework_lower:
                return "pytest"
            elif "jest" in framework_lower:
                return "jest"
            elif "junit" in framework_lower:
                return "junit"

        # Default based on language
        language_defaults = {
            "python": "pytest",
            "javascript": "jest",
            "typescript": "jest",
            "java": "junit",
        }

        return language_defaults.get(tech_stack.language.lower(), "pytest")

    def _get_framework_tdd_patterns(self, tech_stack: TechStack) -> str:
        """Get framework-specific TDD patterns."""
        patterns = []

        for framework in tech_stack.frameworks:
            framework_lower = framework.lower()
            if framework_lower == "django":
                patterns.append("# Use Django TestCase for database tests")
                patterns.append("# Use Django Client for view tests")
            elif framework_lower == "fastapi":
                patterns.append("# Use TestClient from fastapi.testclient")
                patterns.append("# Test async endpoints with pytest-asyncio")
            elif framework_lower == "react":
                patterns.append("# Use React Testing Library")
                patterns.append("# Test user interactions, not implementation")

        return "\n".join(patterns) if patterns else ""

    def _get_framework_security_rules(self, tech_stack: TechStack) -> List[str]:
        """Get framework-specific security rules."""
        rules = []

        for framework in tech_stack.frameworks:
            framework_lower = framework.lower()
            if framework_lower == "django":
                rules.append("- Enable Django's CSRF middleware")
                rules.append("- Use Django's built-in XSS protection")
                rules.append("- Configure SECURE_SSL_REDIRECT in production")
            elif framework_lower == "fastapi":
                rules.append("- Use OAuth2 with password flow for authentication")
                rules.append("- Enable CORS with specific origins")
                rules.append("- Use Pydantic for input validation")

        return rules

    def _fetch_from_external_source(
        self,
        tech_stack: TechStack,
        source: KnowledgeSource,
        template_type: TemplateType
    ) -> Optional[SynthesisResult]:
        """
        Fetch knowledge from external source.

        Note: This is a placeholder for future external API integration.
        """
        # Future: Implement GitHub API, docs scraping, etc.
        # For now, return None to trigger fallback to internal
        return None

    def _create_empty_result(
        self,
        template_type: TemplateType,
        source: KnowledgeSource
    ) -> SynthesisResult:
        """Create empty synthesis result for invalid input."""
        return SynthesisResult(
            content="# No content available\n",
            source=source,
            template_type=template_type,
            timestamp=datetime.now(),
            metadata={"error": "Invalid or missing tech stack"}
        )

    def _get_from_cache(self, key: str) -> Optional[SynthesisResult]:
        """Get result from cache."""
        with self._cache_lock:
            if key in self._cache:
                self._cache_hits += 1
                return self._cache[key]
            else:
                self._cache_misses += 1
                return None

    def _store_in_cache(self, key: str, result: SynthesisResult):
        """Store result in cache."""
        with self._cache_lock:
            # Simple LRU: if cache full, remove oldest (first) item
            if len(self._cache) >= self.max_cache_size:
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]

            self._cache[key] = result
