"""
Crawler Template Generator for CORTEX LENS CDF.

Generates custom analyzers from templates:
1. Jinja2-based code generation
2. BaseAnalyzer inheritance validation
3. Automatic test generation
4. Sandbox validation (no eval, exec, dangerous imports)
5. Wiring integration

AC_START: AC-CDF-Generator-002
"""

import ast
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from cortex.lens.capability_discovery import CrawlerSpec

logger = logging.getLogger(__name__)


# ==============================================================================
# Exceptions
# ==============================================================================

class TemplateNotFoundError(Exception):
    """Template file not found."""
    pass


class CodeValidationError(Exception):
    """Generated code failed validation."""
    pass


# ==============================================================================
# Data Models
# ==============================================================================

@dataclass
class GeneratedCode:
    """Generated code with metadata."""

    content: str
    file_path: Path
    spec: CrawlerSpec
    validated: bool = False

    def __len__(self) -> int:
        """Get content length."""
        return len(self.content)


# ==============================================================================
# Crawler Template Generator
# ==============================================================================

class CrawlerTemplateGenerator:
    """Generates custom crawlers from Jinja2 templates."""

    # Dangerous patterns to detect in code
    DANGEROUS_PATTERNS = [
        r'\beval\s*\(',
        r'\bexec\s*\(',
        r'\b__import__\s*\(',
        r'\bcompile\s*\(',
        r'os\.system\s*\(',
        r'subprocess\.call\s*\(',
        r'subprocess\.Popen\s*\(',
        r'\brm\s+-rf\s+/',
        r'DROP\s+TABLE',
        r'DELETE\s+FROM',
    ]

    def __init__(self, template_dir: Optional[Path] = None):
        """
        Initialize generator.

        Args:
            template_dir: Path to templates directory (default: cortex/lens/templates/)
        """
        if template_dir is None:
            template_dir = Path(__file__).parent / "templates"

        self.template_dir = Path(template_dir)

        # Initialize Jinja2 environment
        if self.template_dir.exists():
            self.env = Environment(
                loader=FileSystemLoader(str(self.template_dir)),
                trim_blocks=True,
                lstrip_blocks=True,
            )
        else:
            logger.warning(f"Template directory not found: {self.template_dir}")
            self.env = None

    # ==========================================================================
    # Template Loading
    # ==========================================================================

    def load_template(self, template_name: str):
        """
        Load Jinja2 template.

        Args:
            template_name: Name of template file

        Returns:
            Jinja2 Template object

        Raises:
            TemplateNotFoundError: Template file not found
        """
        if self.env is None:
            raise TemplateNotFoundError(f"Template directory not initialized: {self.template_dir}")

        try:
            return self.env.get_template(template_name)
        except TemplateNotFound as e:
            raise TemplateNotFoundError(f"Template not found: {template_name}") from e

    def list_templates(self) -> List[str]:
        """
        List all available templates.

        Returns:
            List of template filenames
        """
        if not self.template_dir.exists():
            return []

        templates = []
        for file in self.template_dir.glob("*.jinja2"):
            templates.append(file.name)

        return sorted(templates)

    # ==========================================================================
    # Code Generation
    # ==========================================================================

    def generate_analyzer(self, spec: CrawlerSpec) -> GeneratedCode:
        """
        Generate analyzer code from spec.

        Args:
            spec: Crawler specification

        Returns:
            GeneratedCode with analyzer implementation
        """
        template = self.load_template("analyzer_template.py.jinja2")

        # Sanitize crawler name for class name
        sanitized_name = self._sanitize_class_name(spec.crawler_name)

        # Prepare template context
        context = {
            "crawler_name": sanitized_name,
            "description": spec.description,
            "module_path": spec.module_path,
            "base_class": spec.base_class,
            "required_methods": spec.required_methods,
            "dependencies": spec.dependencies,
            "priority": spec.priority,
        }

        # Render template
        content = template.render(**context)

        # Generate file path
        snake_case = self._to_snake_case(spec.crawler_name)
        file_path = Path(f"{snake_case}.py")

        code = GeneratedCode(
            content=content,
            file_path=file_path,
            spec=spec,
        )

        # Validate generated code
        if not self.validate_syntax(content):
            raise CodeValidationError(f"Generated code has syntax errors: {spec.crawler_name}")

        code.validated = True
        logger.info(f"Generated analyzer: {spec.crawler_name}")
        return code

    def generate_test(self, spec: CrawlerSpec) -> GeneratedCode:
        """
        Generate test code from spec.

        Args:
            spec: Crawler specification

        Returns:
            GeneratedCode with test implementation
        """
        template = self.load_template("test_template.py.jinja2")

        # Prepare template context
        context = {
            "crawler_name": spec.crawler_name,
            "description": spec.description,
            "module_path": spec.module_path,
            "test_scenarios": spec.test_scenarios,
        }

        # Render template
        content = template.render(**context)

        # Generate file path
        snake_case = self._to_snake_case(spec.crawler_name)
        file_path = Path(f"test_{snake_case}.py")

        code = GeneratedCode(
            content=content,
            file_path=file_path,
            spec=spec,
        )

        # Validate generated code
        if not self.validate_syntax(content):
            raise CodeValidationError(f"Generated test has syntax errors: {spec.crawler_name}")

        code.validated = True
        logger.info(f"Generated test: test_{snake_case}.py")
        return code

    # ==========================================================================
    # Code Validation
    # ==========================================================================

    def validate_syntax(self, code: str) -> bool:
        """
        Validate Python syntax.

        Args:
            code: Python code to validate

        Returns:
            True if syntax is valid
        """
        try:
            ast.parse(code)
            return True
        except SyntaxError as e:
            logger.error(f"Syntax error in generated code: {e}")
            return False

    def validate_base_class(self, code: str, base_class: str) -> bool:
        """
        Validate class inherits from expected base class.

        Args:
            code: Python code to validate
            base_class: Expected base class name

        Returns:
            True if inheritance is correct
        """
        try:
            tree = ast.parse(code)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    for base in node.bases:
                        if isinstance(base, ast.Name) and base.id == base_class:
                            return True

            return False
        except Exception as e:
            logger.error(f"Error validating base class: {e}")
            return False

    def validate_method_exists(self, code: str, method_name: str) -> bool:
        """
        Validate method exists in generated code.

        Args:
            code: Python code to validate
            method_name: Method name to check

        Returns:
            True if method exists
        """
        try:
            tree = ast.parse(code)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name == method_name:
                    return True

            return False
        except Exception as e:
            logger.error(f"Error validating method: {e}")
            return False

    def sandbox_validate(self, code: str) -> bool:
        """
        Validate code is safe (no dangerous patterns).

        Args:
            code: Python code to validate

        Returns:
            True if code is safe
        """
        # Check for dangerous patterns
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, code, re.IGNORECASE):
                logger.warning(f"Dangerous pattern detected: {pattern}")
                return False

        # Additional checks
        try:
            tree = ast.parse(code)

            # Check for dangerous imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name in ['subprocess', 'os']:
                            # Allow but log
                            logger.info(f"Potentially dangerous import: {alias.name}")
        except Exception as e:
            logger.error(f"Error in sandbox validation: {e}")
            return False

        return True

    # ==========================================================================
    # File Operations
    # ==========================================================================

    def write_code(
        self,
        code: GeneratedCode,
        output_dir: Path,
        overwrite: bool = False
    ) -> Path:
        """
        Write generated code to file.

        Args:
            code: Generated code
            output_dir: Output directory
            overwrite: Allow overwriting existing files

        Returns:
            Path to written file

        Raises:
            FileExistsError: File exists and overwrite=False
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        output_path = output_dir / code.file_path.name

        if output_path.exists() and not overwrite:
            raise FileExistsError(f"File already exists: {output_path}")

        output_path.write_text(code.content)
        logger.info(f"Wrote code to: {output_path}")

        return output_path

    # ==========================================================================
    # Wiring Integration
    # ==========================================================================

    def generate_wiring_entry(self, spec: CrawlerSpec) -> Dict[str, Any]:
        """
        Generate wiring configuration entry.

        Args:
            spec: Crawler specification

        Returns:
            Wiring configuration dictionary
        """
        return {
            "name": spec.crawler_name,
            "module": spec.module_path,
            "class": spec.crawler_name,
            "priority": spec.priority,
            "dependencies": spec.dependencies,
        }

    def append_to_wiring(self, spec: CrawlerSpec, wiring_file: Path) -> None:
        """
        Append entry to wiring.yaml.

        Args:
            spec: Crawler specification
            wiring_file: Path to wiring.yaml
        """
        if not wiring_file.exists():
            logger.warning(f"Wiring file not found: {wiring_file}")
            return

        try:
            # Load existing wiring
            wiring = yaml.safe_load(wiring_file.read_text())

            if "analyzers" not in wiring:
                wiring["analyzers"] = []

            # Generate entry
            entry = self.generate_wiring_entry(spec)

            # Check for duplicates
            for existing in wiring["analyzers"]:
                if existing.get("name") == spec.crawler_name:
                    logger.info(f"Analyzer already in wiring: {spec.crawler_name}")
                    return

            # Append entry
            wiring["analyzers"].append(entry)

            # Write back
            wiring_file.write_text(yaml.dump(wiring, default_flow_style=False, sort_keys=False))
            logger.info(f"Added {spec.crawler_name} to wiring.yaml")

        except Exception as e:
            logger.error(f"Error updating wiring file: {e}")

    # ==========================================================================
    # Utilities
    # ==========================================================================

    def _to_snake_case(self, name: str) -> str:
        """
        Convert CamelCase to snake_case.

        Args:
            name: CamelCase string

        Returns:
            snake_case string
        """
        # Remove special characters
        name = re.sub(r'[^a-zA-Z0-9]', '', name)

        # Insert underscores before uppercase letters
        snake = re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()

        return snake

    def _sanitize_class_name(self, name: str) -> str:
        """
        Sanitize class name to valid Python identifier.

        Args:
            name: Class name with potential special characters

        Returns:
            Valid Python class name
        """
        # Remove special characters, replace with empty string
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '', name)

        # Ensure it doesn't start with a digit
        if sanitized and sanitized[0].isdigit():
            sanitized = '_' + sanitized

        return sanitized


# AC_COMPLETE: AC-CDF-Generator-002

__all__ = [
    "CrawlerTemplateGenerator",
    "GeneratedCode",
    "TemplateNotFoundError",
    "CodeValidationError",
]
