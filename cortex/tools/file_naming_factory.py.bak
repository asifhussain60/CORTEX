"""
CORTEX File Naming Factory & Validator
=====================================================

Enforces global file naming standards across CORTEX.
SSOT: .cortex/standards/file-naming-config.yaml
DOCS: cortex_brain/tier0/governance/file-naming-standards.md

Authority: CORE-035 (Single Canonical Implementation)
"""

import re
import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class FileType(Enum):
    """Supported file types with naming conventions."""
    
    DOCUMENTATION = "markdown"      # .md
    CONFIGURATION = "config"        # .yaml, .yml
    PYTHON_MODULE = "python"        # .py (snake_case)
    SHELL_SCRIPT = "shell"          # .sh
    YAML_PLAN = "yaml_plan"         # .yaml (kebab-case)
    TEST = "test"                   # test_*.py
    DOCKER = "docker"               # Dockerfile, docker-compose.yml


@dataclass
class FileNameConfig:
    """File naming configuration."""
    
    min_length: int = 8
    optimal_min: int = 16
    optimal_max: int = 32
    max_length: int = 55
    
    # Prohibited patterns
    prohibited_adjectives: List[str] = field(default_factory=lambda: [
        "new", "enhanced", "improved", "better", "advanced",
        "executive", "final", "draft", "complete", "old",
        "updated", "latest", "newest"
    ])
    prohibited_prefixes: List[str] = field(default_factory=lambda: [
        "v", "version", "date", "author", "status"
    ])


class FileNameFactory:
    """
    Factory for generating standards-compliant filenames.
    
    This is the SINGLE location where all file naming is determined.
    All tools, generators, and scripts use this factory.
    
    SSOT: .cortex/standards/file-naming-config.yaml
    """
    
    def __init__(self, config: Optional[FileNameConfig] = None):
        """Initialize factory with config."""
        self.config = config or FileNameConfig()
        self._validate_config()
    
    def _validate_config(self) -> None:
        """Validate configuration parameters."""
        if self.config.min_length < 1:
            raise ValueError("min_length must be >= 1")
        if self.config.optimal_min < self.config.min_length:
            raise ValueError("optimal_min must be >= min_length")
        if self.config.optimal_max < self.config.optimal_min:
            raise ValueError("optimal_max must be >= optimal_min")
        if self.config.max_length < self.config.optimal_max:
            raise ValueError("max_length must be >= optimal_max")
    
    def documentation(self, purpose: str, context: str = "") -> str:
        """
        Generate markdown documentation filename.
        
        Pattern: {purpose}-{context}.md
        
        Examples:
            - documentation("guide", "deployment") → deployment-guide.md
            - documentation("reference", "api") → api-reference.md
            - documentation("inventory", "component") → component-inventory.md
        
        Args:
            purpose: What the document does (guide, reference, summary, etc.)
            context: What it's about (docker, wiring, deployment, etc.)
        
        Returns:
            str: Standards-compliant markdown filename
        
        Raises:
            ValueError: If parameters violate naming standards
        """
        if context:
            # context-purpose.md
            parts = [context.lower(), purpose.lower()]
            base = "-".join(filter(None, parts))
        else:
            base = purpose.lower()
        
        filename = f"{base}.md"
        self._validate_filename(filename)
        return filename
    
    def configuration(self, service: str, environment: str = "", filetype: str = "yaml") -> str:
        """
        Generate configuration filename.
        
        Pattern: {service}-config.yaml (default) or {service}-{env}-config.yaml
        
        Examples:
            - configuration("docker") → docker-config.yaml
            - configuration("prometheus", "production") → prometheus-production-config.yaml
            - configuration("database", filetype="yml") → database-config.yml
        
        Args:
            service: Service/component name (docker, prometheus, database, etc.)
            environment: Optional environment (production, staging, dev, etc.)
            filetype: File extension (yaml, yml - default: yaml)
        
        Returns:
            str: Standards-compliant configuration filename
        
        Raises:
            ValueError: If parameters violate naming standards
        """
        service = service.lower().strip()
        if not service:
            raise ValueError("service name cannot be empty")
        
        if environment:
            environment = environment.lower().strip()
            base = f"{service}-{environment}-config"
        else:
            base = f"{service}-config"
        
        # Validate extension
        if filetype not in ["yaml", "yml", "conf", "cfg"]:
            raise ValueError(f"Invalid filetype: {filetype}")
        
        filename = f"{base}.{filetype}"
        self._validate_filename(filename)
        return filename
    
    def script(self, verb: str, noun: str) -> str:
        """
        Generate shell script filename.
        
        Pattern: {verb}-{noun}.sh
        
        Examples:
            - script("deploy", "kubernetes") → deploy-kubernetes.sh
            - script("migrate", "docker") → migrate-docker.sh
            - script("validate", "syntax") → validate-syntax.sh
        
        Args:
            verb: Action verb (deploy, migrate, validate, check, etc.)
            noun: Target noun (kubernetes, docker, config, etc.)
        
        Returns:
            str: Standards-compliant shell script filename
        
        Raises:
            ValueError: If parameters violate naming standards
        """
        verb = verb.lower().strip()
        noun = noun.lower().strip()
        
        if not verb or not noun:
            raise ValueError("verb and noun cannot be empty")
        
        filename = f"{verb}-{noun}.sh"
        self._validate_filename(filename)
        return filename
    
    def python_module(self, noun: str, verb: str = "") -> str:
        """
        Generate Python module filename (snake_case per PEP 8).
        
        Pattern: {noun}_{verb}.py or {noun}.py
        
        Examples:
            - python_module("orchestrator", "migration") → migration_orchestrator.py
            - python_module("validator", "wiring") → wiring_validator.py
            - python_module("config", "docker") → docker_config.py
        
        Args:
            noun: What the module is/does (orchestrator, validator, config, etc.)
            verb: Optional modifier/context (migration, wiring, docker, etc.)
        
        Returns:
            str: Standards-compliant Python filename (snake_case)
        
        Raises:
            ValueError: If parameters violate naming standards
        
        Note:
            Python files use snake_case per PEP 8, not kebab-case!
        """
        noun = noun.lower().strip()
        verb = verb.lower().strip()
        
        if not noun:
            raise ValueError("noun cannot be empty")
        
        if verb:
            # verb_noun.py
            base = f"{verb}_{noun}"
        else:
            base = noun
        
        filename = f"{base}.py"
        # Python uses underscores, so adjust validation
        self._validate_filename(filename, allow_underscores=True)
        return filename
    
    def test(self, noun: str, context: str = "") -> str:
        """
        Generate test filename (pytest convention).
        
        Pattern: test_{noun}.py or test_{context}_{noun}.py
        
        Examples:
            - test("orchestrator", "migration") → test_migration_orchestrator.py
            - test("integration", "wiring") → test_wiring_integration.py
            - test("api", "rest") → test_rest_api.py
        
        Args:
            noun: What's being tested (orchestrator, api, validator, etc.)
            context: Optional test context (integration, unit, wiring, etc.)
        
        Returns:
            str: Standards-compliant test filename
        
        Raises:
            ValueError: If parameters violate naming standards
        
        Note:
            Tests follow pytest conventions (test_ prefix).
        """
        noun = noun.lower().strip()
        context = context.lower().strip() if context else ""
        
        if not noun:
            raise ValueError("noun cannot be empty")
        
        if context:
            # test_context_noun.py
            base = f"test_{context}_{noun}"
        else:
            # test_noun.py
            base = f"test_{noun}"
        
        filename = f"{base}.py"
        self._validate_filename(filename, allow_underscores=True)
        return filename
    
    def plan(self, purpose: str, topic: str = "") -> str:
        """
        Generate plan/architecture YAML filename.
        
        Pattern: {purpose}-{topic}-plan.yaml or {purpose}-plan.yaml
        
        Examples:
            - plan("migration", "phases") → migration-phases-plan.yaml
            - plan("architecture", "deployment") → architecture-deployment-plan.yaml
            - plan("roadmap", "project") → project-roadmap-plan.yaml
        
        Args:
            purpose: Plan purpose (migration, architecture, roadmap, etc.)
            topic: Optional specific topic
        
        Returns:
            str: Standards-compliant YAML plan filename
        
        Raises:
            ValueError: If parameters violate naming standards
        """
        purpose = purpose.lower().strip()
        topic = topic.lower().strip() if topic else ""
        
        if not purpose:
            raise ValueError("purpose cannot be empty")
        
        if topic:
            # {topic}-{purpose}-plan.yaml
            base = f"{topic}-{purpose}-plan"
        else:
            # {purpose}-plan.yaml
            base = f"{purpose}-plan"
        
        filename = f"{base}.yaml"
        self._validate_filename(filename)
        return filename
    
    def _validate_filename(self, filename: str, allow_underscores: bool = False) -> None:
        """
        Validate filename against standards.
        
        Checks:
        - Length (min/max)
        - Case style (kebab-case except Python)
        - No prohibited patterns
        - No special characters
        - Proper extension
        
        Args:
            filename: Filename to validate
            allow_underscores: If True, allows underscores (for Python/tests)
        
        Raises:
            ValueError: If filename violates standards
        """
        # Length check
        if len(filename) < self.config.min_length:
            raise ValueError(
                f"Filename too short ({len(filename)} chars, min: {self.config.min_length}): {filename}"
            )
        
        if len(filename) > self.config.max_length:
            raise ValueError(
                f"Filename too long ({len(filename)} chars, max: {self.config.max_length}): {filename}"
            )
        
        # Warning for names outside optimal range
        if len(filename) < self.config.optimal_min or len(filename) > self.config.optimal_max:
            logger.warning(
                f"Filename outside optimal range ({self.config.optimal_min}-{self.config.optimal_max}): "
                f"{filename} ({len(filename)} chars)"
            )
        
        # Extract base name (without extension)
        base_name = filename.rsplit(".", 1)[0] if "." in filename else filename
        
        # Check for prohibited patterns
        parts = re.split(r"[-_]", base_name.lower())
        for part in parts:
            if part in self.config.prohibited_adjectives:
                raise ValueError(
                    f"Prohibited adjective '{part}' in filename: {filename}"
                )
        
        # Case style check (unless underscores allowed for Python)
        if not allow_underscores:
            # kebab-case: only lowercase, digits, hyphens
            if not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*\.[a-z0-9]+$", filename):
                raise ValueError(
                    f"Filename must use kebab-case: {filename}\n"
                    f"Pattern: lowercase-words-separated-by-hyphens.ext"
                )
        else:
            # snake_case allowed: only lowercase, digits, underscores (Python/tests)
            if not re.match(r"^[a-z0-9]+(_[a-z0-9]+)*\.[a-z0-9]+$", filename):
                raise ValueError(
                    f"Filename must use snake_case: {filename}\n"
                    f"Pattern: lowercase_words_separated_by_underscores.ext"
                )
        
        logger.info(f"✓ Filename valid: {filename}")
    
    def validate_existing(self, filename: str) -> Dict[str, Any]:
        """
        Validate an existing filename against standards.
        
        Returns detailed validation report.
        
        Args:
            filename: Filename to validate
        
        Returns:
            dict: Validation report with is_valid, issues, suggestions
        """
        issues: List[str] = []
        suggestions: List[str] = []
        
        # Length check
        if len(filename) < self.config.min_length:
            issues.append(f"Too short ({len(filename)} < {self.config.min_length})")
        elif len(filename) > self.config.max_length:
            issues.append(f"Too long ({len(filename)} > {self.config.max_length})")
        
        if len(filename) < self.config.optimal_min or len(filename) > self.config.optimal_max:
            suggestions.append(
                f"Length {len(filename)} outside optimal {self.config.optimal_min}-{self.config.optimal_max}"
            )
        
        # Check for prohibited patterns
        base_name = filename.rsplit(".", 1)[0] if "." in filename else filename
        parts = base_name.lower().split("-")
        
        for part in parts:
            if part in self.config.prohibited_adjectives:
                issues.append(f"Contains prohibited adjective: {part}")
                suggestions.append(f"Remove '{part}' or use more descriptive term")
        
        # Case style check
        if not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*\..*$", filename.lower()):
            if not re.match(r"^[a-z0-9]+(_[a-z0-9]+)*\.py$", filename):
                issues.append("Not in kebab-case or snake_case format")
                suggestions.append("Use lowercase-words-separated-by-hyphens")
        
        return {
            "filename": filename,
            "is_valid": len(issues) == 0,
            "issues": issues,
            "suggestions": suggestions,
            "length": len(filename),
            "optimal_range": f"{self.config.optimal_min}-{self.config.optimal_max}"
        }


# Convenience functions for direct use
_factory = FileNameFactory()


def documentation(purpose: str, context: str = "") -> str:
    """Generate markdown filename."""
    return _factory.documentation(purpose, context)


def configuration(service: str, environment: str = "", filetype: str = "yaml") -> str:
    """Generate configuration filename."""
    return _factory.configuration(service, environment, filetype)


def script(verb: str, noun: str) -> str:
    """Generate shell script filename."""
    return _factory.script(verb, noun)


def python_module(noun: str, verb: str = "") -> str:
    """Generate Python module filename."""
    return _factory.python_module(noun, verb)


def test(noun: str, context: str = "") -> str:
    """Generate test filename."""
    return _factory.test(noun, context)


def plan(purpose: str, topic: str = "") -> str:
    """Generate plan YAML filename."""
    return _factory.plan(purpose, topic)


def validate(filename: str) -> Dict[str, Any]:
    """Validate existing filename."""
    return _factory.validate_existing(filename)


if __name__ == "__main__":
    """Example usage and validation."""
    
    factory = FileNameFactory()
    
    print("=" * 70)
    print("CORTEX FILE NAMING FACTORY - EXAMPLE USAGE")
    print("=" * 70)
    print()
    
    # Documentation examples
    print("📄 DOCUMENTATION FILES:")
    print(f"  deployment guide:    {factory.documentation('guide', 'deployment')}")
    print(f"  api reference:       {factory.documentation('reference', 'api')}")
    print(f"  component inventory: {factory.documentation('inventory', 'component')}")
    print()
    
    # Configuration examples
    print("⚙️  CONFIGURATION FILES:")
    print(f"  docker config:       {factory.configuration('docker')}")
    print(f"  prometheus prod:     {factory.configuration('prometheus', 'production')}")
    print(f"  database staging:    {factory.configuration('database', 'staging', 'yml')}")
    print()
    
    # Script examples
    print("🔧 SHELL SCRIPTS:")
    print(f"  deploy kubernetes:   {factory.script('deploy', 'kubernetes')}")
    print(f"  migrate docker:      {factory.script('migrate', 'docker')}")
    print(f"  validate syntax:     {factory.script('validate', 'syntax')}")
    print()
    
    # Python module examples
    print("🐍 PYTHON MODULES:")
    print(f"  orchestrator:        {factory.python_module('orchestrator', 'migration')}")
    print(f"  validator:           {factory.python_module('validator', 'wiring')}")
    print(f"  config:              {factory.python_module('config', 'docker')}")
    print()
    
    # Test examples
    print("✅ TEST FILES:")
    print(f"  orchestrator tests:  {factory.test('orchestrator', 'integration')}")
    print(f"  validator tests:     {factory.test('validator', 'wiring')}")
    print()
    
    # Plan examples
    print("📊 PLAN FILES:")
    print(f"  migration phases:    {factory.plan('migration', 'phases')}")
    print(f"  project roadmap:     {factory.plan('roadmap', 'project')}")
    print()
    
    # Validation examples
    print("🔍 VALIDATION EXAMPLES:")
    print()
    
    test_files = [
        "good-deployment-guide.md",
        "bad_file_name.md",
        "new-docker-config.yaml",
        "migration-summary.md",
    ]
    
    for test_file in test_files:
        result = factory.validate_existing(test_file)
        status = "✅ VALID" if result["is_valid"] else "❌ INVALID"
        print(f"{status}: {result['filename']}")
        if result["issues"]:
            for issue in result["issues"]:
                print(f"  ⚠️  {issue}")
        if result["suggestions"]:
            for suggestion in result["suggestions"]:
                print(f"  💡 {suggestion}")
        print()
    
    print("=" * 70)
    print("SSOT: .cortex/standards/file-naming-config.yaml")
    print("DOCS: cortex_brain/tier0/governance/file-naming-standards.md")
    print("=" * 70)
