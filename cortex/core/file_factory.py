"""
FileFactory — Canonical file creation & naming validation (Phase 00, D2).

Unifies two legacy 1200+ line factories:
  - cortex/governance/filename_factory.py (677 lines, CORE-028 kebab only)
  - cortex/tools/file_naming_factory.py   (546 lines, multi-type support)

YAML config drives ALL rules per CORE-028. Returns NamingResult with violations.

Authority: CORE-008 (TDD) | CORE-011 (type hints) | CORE-012 (docstrings)
"""

from pathlib import Path
from typing import Optional, Dict, Any, List, Union
from dataclasses import dataclass, field
from datetime import datetime
import textwrap
import re
import yaml


@dataclass
class FileTemplate:
    """Template for file creation."""
    
    name: str
    extension: str
    header: str
    body: str
    footer: Optional[str] = None


@dataclass
class NamingResult:
    """Result of file naming validation.
    
    Attributes:
        filename: The generated or validated filename.
        is_valid: Whether the filename passes all rules.
        violations: List of violation descriptions.
        suggestion: Suggested corrected filename (None if valid).
    """
    
    filename: str
    is_valid: bool
    violations: List[str] = field(default_factory=list)
    suggestion: Optional[str] = None


@dataclass
class FileFactoryConfig:
    """Configuration for file naming rules (loaded from YAML).
    
    Attributes:
        max_length_python: Maximum length for Python filenames.
        max_length_yaml: Maximum length for YAML filenames.
        max_length_markdown: Maximum length for Markdown filenames.
        prohibited_patterns: Regex patterns that always violate naming rules.
        rules: Full rule set from YAML config.
    """
    
    max_length_python: int = 55
    max_length_yaml: int = 60
    max_length_markdown: int = 60
    prohibited_patterns: List[str] = field(default_factory=list)
    rules: Dict[str, Any] = field(default_factory=dict)


class FileFactory:
    """Canonical factory for file creation & naming validation.
    
    - Validates filenames against CORE-028 governance rules
    - Creates files with proper structure and headers
    - Returns NamingResult with violation reasons
    """
    
    def __init__(self, config: Optional[FileFactoryConfig] = None) -> None:
        """Initialize FileFactory with optional config.
        
        If no config provided, attempts to load from standard config file location.
        
        Args:
            config: FileFactoryConfig instance (default: load from YAML).
        """
        if config is None:
            # Try to load from standard location
            config_path = (
                Path(__file__).resolve().parents[2] /
                "cortex-registry/core/config/file-naming-rules.yaml"
            )
            if config_path.exists():
                try:
                    config = self._load_config_from_yaml(config_path)
                except Exception:
                    # Fall back to empty config if YAML load fails
                    config = FileFactoryConfig()
            else:
                config = FileFactoryConfig()
        
        self.config = config
        self.templates: Dict[str, FileTemplate] = self._load_templates()
    
    @staticmethod
    def _load_config_from_yaml(config_path: Path) -> FileFactoryConfig:
        """Load FileFactoryConfig from YAML file.
        
        Args:
            config_path: Path to file-naming-rules.yaml.
            
        Returns:
            FileFactoryConfig instance.
        """
        data = yaml.safe_load(config_path.read_text())
        
        # Extract configuration
        file_naming = data.get("file_naming", {})
        python_config = file_naming.get("python", {})
        yaml_config = file_naming.get("yaml", {})
        markdown_config = file_naming.get("markdown", {})
        prohibited = data.get("prohibited_patterns", [])
        
        return FileFactoryConfig(
            max_length_python=python_config.get("max_length", 55),
            max_length_yaml=yaml_config.get("max_length", 60),
            max_length_markdown=markdown_config.get("max_length", 60),
            prohibited_patterns=prohibited,
            rules=file_naming,
        )
    
    @classmethod
    def from_yaml(cls: object, config_path: Union[str, Path]) -> "FileFactory":
        """Load FileFactory configuration from YAML file.
        
        Args:
            config_path: Path to file-naming-rules.yaml.
            
        Returns:
            FileFactory instance configured from YAML.
        """
        config_path = Path(config_path) if isinstance(config_path, str) else config_path
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        config = cls._load_config_from_yaml(config_path)
        return cls(config=config)
    
    def _load_templates(self) -> Dict[str, FileTemplate]:
        """Load standard file templates.
        
        Returns:
            Dictionary mapping template names to FileTemplate instances.
        """
        return {
            "python": self._template_python(),
            "yaml": self._template_yaml(),
            "markdown": self._template_markdown(),
            "test": self._template_test(),
        }
    
    @staticmethod
    def _template_python() -> FileTemplate:
        """Create Python file template with docstring and type hints."""
        return FileTemplate(
            name="python",
            extension=".py",
            header='"""Module docstring.\n\nAuthority: CORE-008 (TDD) | CORE-011 (type hints) | CORE-012 (docstrings)\n"""\n\n',
            body="",
            footer="\n\nif __name__ == '__main__':\n    pass\n",
        )
    
    @staticmethod
    def _template_yaml() -> FileTemplate:
        """Create YAML file template."""
        return FileTemplate(
            name="yaml",
            extension=".yaml",
            header="# ============================================================================\n# YAML Configuration\n# ============================================================================\n\n",
            body="",
            footer=None,
        )
    
    @staticmethod
    def _template_markdown() -> FileTemplate:
        """Create Markdown file template."""
        return FileTemplate(
            name="markdown",
            extension=".md",
            header="# Title\n\n",
            body="",
            footer=None,
        )
    
    @staticmethod
    def _template_test() -> FileTemplate:
        """Create test file template with pytest structure."""
        return FileTemplate(
            name="test",
            extension=".py",
            header='"""Test suite.\n\nAuthority: CORE-008 (TDD mandatory)\n"""\n\nimport pytest\n\n',
            body="",
            footer="\n\nif __name__ == '__main__':\n    pytest.main([__file__, '-v'])\n",
        )
    
    # ========================================================================
    # NAMING METHODS — Core file naming factory contracts
    # ========================================================================
    
    def python_module(
        self,
        noun: str,
        context: str = "",
    ) -> NamingResult:
        """Generate Python module filename (snake_case).
        
        Args:
            noun: Module name (core noun).
            context: Optional context prefix (e.g., "master").
            
        Returns:
            NamingResult with filename, is_valid, violations, suggestion.
        """
        if context:
            filename = f"{context}_{noun}.py"
        else:
            filename = f"{noun}.py"
        
        return self.validate(filename)
    
    def python_test(self, noun: str, context: str = "") -> NamingResult:
        """Generate test filename with test_ prefix.
        
        Args:
            noun: Test subject name (core noun).
            context: Optional context.
            
        Returns:
            NamingResult with test_*.py filename.
        """
        if context:
            filename = f"test_{context}_{noun}.py"
        else:
            filename = f"test_{noun}.py"
        
        return self.validate(filename)
    
    def yaml_config(self, service: str, environment: str = "") -> NamingResult:
        """Generate YAML config filename (kebab-case).
        
        Args:
            service: Service/config name.
            environment: Optional environment suffix (staging, prod).
            
        Returns:
            NamingResult with filename.yaml.
        """
        if environment:
            filename = f"{service}-{environment}.yaml"
        else:
            filename = f"{service}.yaml"
        
        return self.validate(filename)
    
    def yaml_plan(self, purpose: str, topic: str = "") -> NamingResult:
        """Generate plan YAML filename.
        
        Args:
            purpose: Plan purpose (e.g., "phase-00-foundation").
            topic: Optional topic.
            
        Returns:
            NamingResult with .yaml filename.
        """
        if topic:
            filename = f"{purpose}-{topic}.yaml"
        else:
            filename = f"{purpose}.yaml"
        
        return self.validate(filename)
    
    def markdown(self, topic: str, context: str = "") -> NamingResult:
        """Generate Markdown filename (kebab-case).
        
        Args:
            topic: Document topic.
            context: Optional context.
            
        Returns:
            NamingResult with .md filename.
        """
        if context:
            filename = f"{context}-{topic}.md"
        else:
            filename = f"{topic}.md"
        
        return self.validate(filename)
    
    def shell_script(self, verb: str, noun: str) -> NamingResult:
        """Generate shell script filename (kebab-case).
        
        Args:
            verb: Action verb (deploy, migrate).
            noun: Target noun (kubernetes, docker).
            
        Returns:
            NamingResult with .sh filename.
        """
        filename = f"{verb}-{noun}.sh"
        return self.validate(filename)
    
    def from_description(
        self,
        description: str,
        file_type: str = "py",
    ) -> NamingResult:
        """Generate filename from natural language description.
        
        Args:
            description: Natural language description.
            file_type: File type (py, yaml, md, sh).
            
        Returns:
            NamingResult with generated filename.
        """
        # Simple snake_case conversion for Python, kebab for others
        words = description.lower().split()
        if file_type == "py":
            name = "_".join(words)
            filename = f"{name}.py"
        elif file_type in ("yaml", "yml"):
            name = "-".join(words)
            filename = f"{name}.yaml"
        elif file_type == "md":
            name = "-".join(words)
            filename = f"{name}.md"
        elif file_type == "sh":
            name = "-".join(words)
            filename = f"{name}.sh"
        else:
            filename = f"{'-'.join(words)}.{file_type}"
        
        return self.validate(filename)
    
    def validate(self, filename: str) -> NamingResult:
        """Validate filename against all naming rules.
        
        Args:
            filename: Filename to validate.
            
        Returns:
            NamingResult with is_valid, violations, and suggestion.
        """
        violations: List[str] = []
        
        # Check prohibited patterns first (universal blacklist)
        # Patterns should match STEM not full filename
        name_stem = Path(filename).stem
        for pattern_str in self.config.prohibited_patterns:
            try:
                if re.search(pattern_str, name_stem):
                    violations.append(
                        f"Prohibited pattern matches: {pattern_str}"
                    )
            except re.error:
                pass
        
        # Determine file type and apply type-specific rules
        ext = Path(filename).suffix
        
        if filename.startswith("test_") and filename.endswith(".py"):
            violations.extend(
                self._validate_python_test(filename)
            )
        elif ext == ".py":
            violations.extend(
                self._validate_python_module(filename)
            )
        elif ext in (".yaml", ".yml"):
            violations.extend(
                self._validate_yaml(filename)
            )
        elif ext == ".md":
            violations.extend(
                self._validate_markdown(filename)
            )
        elif ext == ".sh":
            violations.extend(
                self._validate_shell(filename)
            )
        
        is_valid = len(violations) == 0
        suggestion = None
        
        if not is_valid:
            # Generate suggestion (convert to kebab-case as default)
            name_only = Path(filename).stem
            ext_part = Path(filename).suffix
            suggested = re.sub(r"[_\s]+", "-", name_only).lower()
            suggestion = f"{suggested}{ext_part}"
        
        return NamingResult(
            filename=filename,
            is_valid=is_valid,
            violations=violations,
            suggestion=suggestion,
        )
    
    def validate_existing(self, filename: str) -> Dict[str, Any]:
        """Validate existing filename (backward compat method).
        
        Args:
            filename: Filename to validate.
            
        Returns:
            Dictionary with validation result (legacy format).
        """
        result = self.validate(filename)
        return {
            "filename": result.filename,
            "is_valid": result.is_valid,
            "violations": result.violations,
            "suggestion": result.suggestion,
        }
    
    # ========================================================================
    # VALIDATION HELPERS — Type-specific rule enforcement
    # ========================================================================
    
    def _validate_python_module(self, filename: str) -> List[str]:
        """Validate Python module filename (snake_case).
        
        Args:
            filename: Filename to validate.
            
        Returns:
            List of violation messages (empty if valid).
        """
        violations: List[str] = []
        
        if len(filename) > self.config.max_length_python:
            violations.append(
                f"Exceeds max length {self.config.max_length_python}: {len(filename)}"
            )
        
        # Python modules: snake_case (lowercase, underscores, no uppercase)
        pattern = r"^[a-z][a-z0-9]*(_[a-z0-9]+)*\.py$"
        if not re.match(pattern, filename):
            if re.search(r"[A-Z]", filename):
                violations.append("Contains uppercase characters (use lowercase)")
            elif filename[0].isupper() or not re.match(r"^[a-z]", filename):
                violations.append("Must start with lowercase letter")
            else:
                violations.append("Invalid format (must match: ^[a-z][a-z0-9]*(_[a-z0-9]+)*\\.py$)")
        
        return violations
    
    def _validate_python_test(self, filename: str) -> List[str]:
        """Validate test filename (test_* prefix required).
        
        Args:
            filename: Filename to validate.
            
        Returns:
            List of violation messages.
        """
        violations: List[str] = []
        
        if len(filename) > self.config.max_length_python:
            violations.append(
                f"Exceeds max length {self.config.max_length_python}: {len(filename)}"
            )
        
        pattern = r"^test_[a-z][a-z0-9]*(_[a-z0-9]+)*\.py$"
        if not re.match(pattern, filename):
            if not filename.startswith("test_"):
                violations.append("Test files must start with 'test_'")
            elif re.search(r"[A-Z]", filename):
                violations.append("Contains uppercase characters")
            else:
                violations.append("Invalid test filename format")
        
        return violations
    
    def _validate_yaml(self, filename: str) -> List[str]:
        """Validate YAML filename (kebab-case).
        
        Args:
            filename: Filename to validate.
            
        Returns:
            List of violation messages.
        """
        violations: List[str] = []
        
        if len(filename) > self.config.max_length_yaml:
            violations.append(
                f"Exceeds max length {self.config.max_length_yaml}: {len(filename)}"
            )
        
        # YAML files: kebab-case (lowercase, hyphens, NO underscores)
        pattern = r"^[a-z][a-z0-9]*(-[a-z0-9]+)*\.ya?ml$"
        if not re.match(pattern, filename):
            if "_" in filename:
                violations.append("YAML filenames must use hyphens, not underscores")
            elif re.search(r"[A-Z]", filename):
                violations.append("Contains uppercase characters (use lowercase)")
            else:
                violations.append("Invalid YAML filename format (use kebab-case)")
        
        return violations
    
    def _validate_markdown(self, filename: str) -> List[str]:
        """Validate Markdown filename (kebab-case).
        
        Args:
            filename: Filename to validate.
            
        Returns:
            List of violation messages.
        """
        violations: List[str] = []
        
        if len(filename) > self.config.max_length_markdown:
            violations.append(
                f"Exceeds max length {self.config.max_length_markdown}: {len(filename)}"
            )
        
        # Markdown: kebab-case
        pattern = r"^[a-z][a-z0-9]*(-[a-z0-9]+)*\.md$"
        if not re.match(pattern, filename):
            if "_" in filename:
                violations.append("Markdown filenames must use hyphens, not underscores")
            elif re.search(r"[A-Z]", filename):
                violations.append("Contains uppercase characters")
            else:
                violations.append("Invalid Markdown filename format")
        
        return violations
    
    def _validate_shell(self, filename: str) -> List[str]:
        """Validate shell script filename (kebab-case).
        
        Args:
            filename: Filename to validate.
            
        Returns:
            List of violation messages.
        """
        violations: List[str] = []
        
        # Shell scripts: kebab-case
        pattern = r"^[a-z][a-z0-9]*(-[a-z0-9]+)*\.sh$"
        if not re.match(pattern, filename):
            violations.append("Shell scripts must use kebab-case format")
        
        return violations
    
    # ========================================================================
    # SANITIZATION — Strip CORTEX-internal terms from filenames
    # ========================================================================

    def sanitize_name(self, filename: str) -> str:
        """Sanitize filename by removing CORTEX-internal terminology.

        Strips prohibited internal terms (phase, sts, skull, tier0, ccl,
        crystallized, brain, hexa, cortex_internal, wiring_spec) from
        filenames while preserving valid structure.

        Args:
            filename: Filename to sanitize.

        Returns:
            Cleaned filename with internal terms removed. If the result
            would be empty or just an extension, returns original filename.
        """
        ext = Path(filename).suffix
        stem = Path(filename).stem

        # Internal terms to strip (subset of prohibited_patterns that are
        # literal terms, not regex anchors like ^enhanced_)
        internal_terms = [
            "phase", "sts", "skull", "tier0", "ccl",
            "crystallized", "brain", "hexa", "cortex_internal",
            "wiring_spec",
        ]

        # Determine separator (underscore for .py, hyphen for yaml/md/sh)
        if ext == ".py":
            sep = "_"
        else:
            sep = "-"

        # Split stem into parts
        parts = re.split(r"[_\-]+", stem)

        # Filter out parts that match internal terms
        cleaned_parts = [
            p for p in parts
            if p.lower() not in internal_terms
            # Also strip numeric-only parts that follow removed terms
            # e.g., "phase_03_orchestrator" → remove "phase", keep "03" only
            # if adjacent to kept parts
        ]

        # Strip leading/trailing numeric parts left orphaned
        while cleaned_parts and cleaned_parts[0].isdigit():
            cleaned_parts.pop(0)

        if not cleaned_parts:
            # All parts were internal terms — return original
            return filename

        result = sep.join(cleaned_parts) + ext
        return result

    # ========================================================================
    # UNIVERSAL FILE CREATION GATE
    # ========================================================================

    def create_file(
        self,
        path: Union[str, Path],
        content: str = "",
        file_type: str = "py",
    ) -> None:
        """Universal gated file creation — validates before writing.

        This is THE single entry point for all CORTEX file creation.
        Validates filename against CORE-028 rules, prohibited patterns,
        and internal terminology before writing.

        Args:
            path: File path to create.
            content: File content to write.
            file_type: File type hint (py, yaml, md, sh).

        Raises:
            ValueError: If filename fails validation (prohibited pattern,
                internal term, format violation).
            FileExistsError: If file already exists.
        """
        path = Path(path) if isinstance(path, str) else path

        if path.exists():
            raise FileExistsError(f"File already exists: {path}")

        # Validate the filename
        result = self.validate(path.name)
        if not result.is_valid:
            raise ValueError(
                f"Filename '{path.name}' violates CORE-028 naming rules: "
                f"{'; '.join(result.violations)}"
                + (f" — suggestion: {result.suggestion}" if result.suggestion else "")
            )

        # Create parent directories
        path.parent.mkdir(parents=True, exist_ok=True)

        # Write content
        path.write_text(content)

    # ========================================================================
    # FILE CREATION — Standard template-based file generation
    # ========================================================================
    
    def create_python_file(
        self,
        path: Union[str, Path],
        module_docstring: str = "Module docstring.",
        imports: Optional[List[str]] = None,
        content: str = "",
    ) -> None:
        """Create a Python file with optional imports and content.
        
        Args:
            path: File path to create.
            module_docstring: Module docstring (CORE-012).
            imports: List of import statements.
            content: Module body content.
            
        Raises:
            FileExistsError: If file already exists.
        """
        path = Path(path) if isinstance(path, str) else path
        if path.exists():
            raise FileExistsError(f"File already exists: {path}")
        
        path.parent.mkdir(parents=True, exist_ok=True)
        
        lines = [
            f'"""Module: {module_docstring}',
            "",
            "Authority: CORE-008 (TDD) | CORE-011 (type hints) | CORE-012 (docstrings)",
            '"""',
            "",
        ]
        
        if imports:
            lines.extend(imports)
            lines.append("")
        
        if content:
            lines.append(content)
        
        lines.append("")
        
        path.write_text("\n".join(lines))
    
    def create_yaml_file(
        self,
        path: Union[str, Path],
        metadata: Optional[Dict[str, Any]] = None,
        content: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Create a YAML file with metadata and content.
        
        Args:
            path: File path to create.
            metadata: Optional metadata dictionary.
            content: YAML content dictionary.
            
        Raises:
            FileExistsError: If file already exists.
        """
        path = Path(path) if isinstance(path, str) else path
        if path.exists():
            raise FileExistsError(f"File already exists: {path}")
        
        path.parent.mkdir(parents=True, exist_ok=True)
        
        import yaml
        
        data = {}
        if metadata:
            data["metadata"] = metadata
        if content:
            data.update(content)
        
        yaml_str = yaml.dump(data, default_flow_style=False, sort_keys=False)
        path.write_text(yaml_str)
    
    def create_test_file(
        self,
        path: Union[str, Path],
        test_class_name: str = "TestModule",
        test_methods: Optional[List[str]] = None,
    ) -> None:
        """Create a test file with pytest structure.
        
        Args:
            path: File path to create.
            test_class_name: Name of test class (CORE-028 PascalCase).
            test_methods: List of test method names.
            
        Raises:
            FileExistsError: If file already exists.
        """
        path = Path(path) if isinstance(path, str) else path
        if path.exists():
            raise FileExistsError(f"File already exists: {path}")
        
        path.parent.mkdir(parents=True, exist_ok=True)
        
        lines = [
            '"""Test suite.',
            "",
            "Authority: CORE-008 (TDD mandatory) | CORE-011 (type hints) | CORE-012 (docstrings)",
            '"""',
            "",
            "import pytest",
            "",
            "",
            f"class {test_class_name}:",
            f'    """Test class for module testing."""',
            "",
        ]
        
        if test_methods:
            for method_name in test_methods:
                lines.extend([
                    f"    def test_{method_name}(self) -> None:",
                    f'        """Test: {method_name}."""',
                    "        assert True, 'Test placeholder'",
                    "",
                ])
        else:
            lines.extend([
                "    def test_placeholder(self) -> None:",
                '        """Placeholder test."""',
                "        assert True",
                "",
            ])
        
        lines.extend([
            "",
            "if __name__ == '__main__':",
            "    pytest.main([__file__, '-v'])",
            "",
        ])
        
        path.write_text("\n".join(lines))
    
    def create_markdown_file(
        self,
        path: Union[str, Path],
        title: str,
        sections: Optional[List[tuple[str, str]]] = None,
    ) -> None:
        """Create a Markdown file with sections.
        
        Args:
            path: File path to create.
            title: Document title (becomes H1).
            sections: List of (section_title, section_content) tuples.
            
        Raises:
            FileExistsError: If file already exists.
        """
        path = Path(path) if isinstance(path, str) else path
        if path.exists():
            raise FileExistsError(f"File already exists: {path}")
        
        path.parent.mkdir(parents=True, exist_ok=True)
        
        lines = [f"# {title}", ""]
        
        if sections:
            for section_title, section_content in sections:
                lines.append(f"## {section_title}")
                lines.append("")
                lines.append(section_content)
                lines.append("")
        
        path.write_text("\n".join(lines))


# Singleton instance
_factory_instance: Optional[FileFactory] = None


def get_file_factory() -> FileFactory:
    """Get or create the singleton FileFactory instance.
    
    Returns:
        FileFactory: The singleton instance.
    """
    global _factory_instance
    if _factory_instance is None:
        _factory_instance = FileFactory()
    return _factory_instance
