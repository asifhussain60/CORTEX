"""
Template Parser (AC-TT-001-01)

Parses orchestrator template files (YAML) into structured objects.
Supports:
- DomainTemplate YAML parsing
- ResponseTemplate parsing
- Validation of template structure
- Section extraction and analysis

This is the foundation for all template tooling.
"""

import re
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import yaml


class ParseError(Exception):
    """Error during template parsing."""

    def __init__(self, message: str, line: Optional[int] = None, column: Optional[int] = None):
        self.message = message
        self.line = line
        self.column = column
        location = f" at line {line}" if line else ""
        location += f", column {column}" if column else ""
        super().__init__(f"{message}{location}")


class SectionType(Enum):
    """Types of sections in a template."""
    METADATA = auto()
    PARAMETERS = auto()
    SCHEMA = auto()
    HOOKS = auto()
    INTEGRATIONS = auto()
    STAGES = auto()
    OUTPUTS = auto()
    ERROR_HANDLERS = auto()
    CUSTOM = auto()


@dataclass
class TemplateSection:
    """A parsed section of a template."""
    name: str
    type: SectionType
    content: Dict[str, Any]
    required_fields: Set[str] = field(default_factory=set)
    optional_fields: Set[str] = field(default_factory=set)
    line_start: Optional[int] = None
    line_end: Optional[int] = None

    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from section content."""
        return self.content.get(key, default)

    def has_field(self, field: str) -> bool:
        """Check if section has a field."""
        return field in self.content

    def validate_required(self) -> List[str]:
        """Validate all required fields are present."""
        missing = []
        for field in self.required_fields:
            if field not in self.content:
                missing.append(field)
        return missing


@dataclass
class ValidationResult:
    """Result of template validation."""
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    info: List[str] = field(default_factory=list)

    def add_error(self, message: str) -> None:
        """Add an error message."""
        self.errors.append(message)
        self.valid = False

    def add_warning(self, message: str) -> None:
        """Add a warning message."""
        self.warnings.append(message)

    def add_info(self, message: str) -> None:
        """Add an info message."""
        self.info.append(message)

    def merge(self, other: 'ValidationResult') -> None:
        """Merge another validation result."""
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        self.info.extend(other.info)
        if not other.valid:
            self.valid = False


@dataclass
class ParsedTemplate:
    """A fully parsed template."""
    name: str
    domain: str
    version: str
    description: str
    sections: Dict[str, TemplateSection] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    raw_content: str = ""
    source_path: Optional[Path] = None

    def get_section(self, name: str) -> Optional[TemplateSection]:
        """Get a section by name."""
        return self.sections.get(name)

    def has_section(self, name: str) -> bool:
        """Check if template has a section."""
        return name in self.sections

    def get_parameter_names(self) -> List[str]:
        """Get all parameter names."""
        params_section = self.sections.get('parameters')
        if params_section:
            return list(params_section.content.keys())
        return []

    def get_required_parameters(self) -> List[str]:
        """Get required parameter names."""
        params_section = self.sections.get('parameters')
        if not params_section:
            return []
        return [
            name for name, config in params_section.content.items()
            if isinstance(config, dict) and config.get('required', False)
        ]

    def get_hooks(self) -> List[str]:
        """Get all hook names."""
        hooks_section = self.sections.get('hooks')
        if hooks_section:
            return list(hooks_section.content.keys())
        return []

    def get_stages(self) -> List[Dict[str, Any]]:
        """Get all stages."""
        stages_section = self.sections.get('stages')
        if stages_section:
            return stages_section.content.get('stages', [])
        return []


class TemplateParser:
    """
    Parser for orchestrator templates.

    Parses YAML template files into structured ParsedTemplate objects.
    Supports DomainTemplate format and ResponseTemplate format.

    Example:
        parser = TemplateParser()
        template = parser.parse_file("templates/planning.yaml")
        print(template.name, template.domain)
    """

    # Standard section mappings
    SECTION_TYPES = {
        'metadata': SectionType.METADATA,
        'meta': SectionType.METADATA,
        'parameters': SectionType.PARAMETERS,
        'params': SectionType.PARAMETERS,
        'input_parameters': SectionType.PARAMETERS,
        'schema': SectionType.SCHEMA,
        'input_schema': SectionType.SCHEMA,
        'output_schema': SectionType.SCHEMA,
        'hooks': SectionType.HOOKS,
        'lifecycle_hooks': SectionType.HOOKS,
        'integrations': SectionType.INTEGRATIONS,
        'tool_integrations': SectionType.INTEGRATIONS,
        'stages': SectionType.STAGES,
        'pipeline_stages': SectionType.STAGES,
        'workflow_stages': SectionType.STAGES,
        'outputs': SectionType.OUTPUTS,
        'output_format': SectionType.OUTPUTS,
        'error_handlers': SectionType.ERROR_HANDLERS,
        'error_handling': SectionType.ERROR_HANDLERS,
    }

    # Required fields for each section type
    # Note: name/version are template-level fields, not metadata section fields
    REQUIRED_FIELDS = {
        SectionType.METADATA: set(),  # Metadata section is flexible (author, tier, tags, etc.)
        SectionType.PARAMETERS: set(),  # Parameters are flexible
        SectionType.SCHEMA: {'type'},
        SectionType.HOOKS: set(),
        SectionType.INTEGRATIONS: set(),
        SectionType.STAGES: {'stages'},
        SectionType.OUTPUTS: {'format'},
        SectionType.ERROR_HANDLERS: set(),
    }

    def __init__(self, strict: bool = False):
        """
        Initialize parser.

        Args:
            strict: If True, raise errors on warnings
        """
        self.strict = strict
        self._line_offsets: List[int] = []

    def parse_file(self, path: Union[str, Path]) -> ParsedTemplate:
        """
        Parse a template from a file.

        Args:
            path: Path to template file

        Returns:
            ParsedTemplate object

        Raises:
            ParseError: If parsing fails
            FileNotFoundError: If file doesn't exist
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Template file not found: {path}")

        content = path.read_text()
        template = self.parse_string(content)
        template.source_path = path
        return template

    def parse_string(self, content: str) -> ParsedTemplate:
        """
        Parse a template from a string.

        Args:
            content: YAML template content

        Returns:
            ParsedTemplate object

        Raises:
            ParseError: If parsing fails
        """
        self._build_line_offsets(content)

        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            raise ParseError(f"YAML parsing error: {e}")

        if not isinstance(data, dict):
            raise ParseError("Template must be a YAML mapping")

        return self._build_template(data, content)

    def _build_line_offsets(self, content: str) -> None:
        """Build line offset mapping for error reporting."""
        self._line_offsets = [0]
        for i, char in enumerate(content):
            if char == '\n':
                self._line_offsets.append(i + 1)

    def _get_line_number(self, offset: int) -> int:
        """Get line number from character offset."""
        for line_num, line_offset in enumerate(self._line_offsets):
            if line_offset > offset:
                return line_num
        return len(self._line_offsets)

    def _build_template(self, data: Dict[str, Any], raw_content: str) -> ParsedTemplate:
        """Build ParsedTemplate from parsed YAML data."""
        # Extract metadata
        name = data.get('name', data.get('template_name', 'unnamed'))
        domain = data.get('domain', data.get('template_domain', 'general'))
        version = str(data.get('version', data.get('template_version', '1.0.0')))
        description = data.get('description', data.get('template_description', ''))

        # Extract metadata section
        metadata = {}
        if 'metadata' in data:
            metadata = data['metadata']
        elif 'meta' in data:
            metadata = data['meta']
        else:
            # Build metadata from top-level fields
            for key in ['name', 'domain', 'version', 'description', 'author', 'tags', 'tier']:
                if key in data:
                    metadata[key] = data[key]

        # Parse sections
        sections = {}
        for key, value in data.items():
            section_type = self._get_section_type(key)
            if section_type and isinstance(value, dict):
                required = self.REQUIRED_FIELDS.get(section_type, set())
                section = TemplateSection(
                    name=key,
                    type=section_type,
                    content=value,
                    required_fields=required,
                )
                sections[key] = section

        return ParsedTemplate(
            name=name,
            domain=domain,
            version=version,
            description=description,
            sections=sections,
            metadata=metadata,
            raw_content=raw_content,
        )

    def _get_section_type(self, name: str) -> Optional[SectionType]:
        """Get section type from name."""
        name_lower = name.lower()
        if name_lower in self.SECTION_TYPES:
            return self.SECTION_TYPES[name_lower]
        return SectionType.CUSTOM

    def validate(self, template: ParsedTemplate) -> ValidationResult:
        """
        Validate a parsed template.

        Args:
            template: ParsedTemplate to validate

        Returns:
            ValidationResult with any errors/warnings
        """
        result = ValidationResult(valid=True)

        # Validate required top-level fields
        if not template.name or template.name == 'unnamed':
            result.add_warning("Template has no name specified")

        if not template.domain or template.domain == 'general':
            result.add_warning("Template has no domain specified")

        if not template.version:
            result.add_warning("Template has no version specified")

        # Validate sections
        for name, section in template.sections.items():
            section_result = self._validate_section(section)
            result.merge(section_result)

        # Validate inter-section dependencies
        self._validate_dependencies(template, result)

        return result

    def _validate_section(self, section: TemplateSection) -> ValidationResult:
        """Validate a single section."""
        result = ValidationResult(valid=True)

        # Check required fields
        missing = section.validate_required()
        for field in missing:
            result.add_error(f"Section '{section.name}' missing required field: {field}")

        # Section-specific validation
        if section.type == SectionType.PARAMETERS:
            self._validate_parameters(section, result)
        elif section.type == SectionType.STAGES:
            self._validate_stages(section, result)
        elif section.type == SectionType.HOOKS:
            self._validate_hooks(section, result)

        return result

    def _validate_parameters(self, section: TemplateSection, result: ValidationResult) -> None:
        """Validate parameters section."""
        for name, config in section.content.items():
            if not isinstance(config, dict):
                continue

            # Check parameter type
            if 'type' not in config:
                result.add_warning(f"Parameter '{name}' has no type specified")

            # Check for description
            if 'description' not in config:
                result.add_info(f"Parameter '{name}' has no description")

    def _validate_stages(self, section: TemplateSection, result: ValidationResult) -> None:
        """Validate stages section."""
        stages = section.content.get('stages', [])
        if not stages:
            result.add_warning("Stages section has no stages defined")
            return

        for i, stage in enumerate(stages):
            if not isinstance(stage, dict):
                result.add_error(f"Stage {i} is not a valid mapping")
                continue

            if 'name' not in stage:
                result.add_warning(f"Stage {i} has no name")

            if 'action' not in stage and 'handler' not in stage:
                result.add_warning(f"Stage {i} has no action or handler")

    def _validate_hooks(self, section: TemplateSection, result: ValidationResult) -> None:
        """Validate hooks section."""
        valid_hooks = {'pre_execute', 'post_execute', 'on_error', 'on_success', 'on_failure'}
        for hook_name in section.content.keys():
            if hook_name not in valid_hooks:
                result.add_info(f"Custom hook defined: {hook_name}")

    def _validate_dependencies(self, template: ParsedTemplate, result: ValidationResult) -> None:
        """Validate dependencies between sections."""
        # If stages reference parameters, verify they exist
        stages_section = template.get_section('stages')
        params_section = template.get_section('parameters')

        if stages_section and params_section:
            param_names = set(params_section.content.keys())
            stages = stages_section.content.get('stages', [])

            for stage in stages:
                if not isinstance(stage, dict):
                    continue

                # Check stage inputs reference valid parameters
                inputs = stage.get('inputs', {})
                for input_name, input_ref in inputs.items():
                    if isinstance(input_ref, str) and input_ref.startswith('$'):
                        ref_name = input_ref[1:].split('.')[0]
                        if ref_name == 'params' or ref_name == 'parameters':
                            param_ref = input_ref.split('.')[-1] if '.' in input_ref else None
                            if param_ref and param_ref not in param_names:
                                result.add_warning(
                                    f"Stage '{stage.get('name', 'unknown')}' "
                                    f"references unknown parameter: {param_ref}"
                                )

    def extract_variables(self, template: ParsedTemplate) -> Dict[str, Set[str]]:
        """
        Extract all variable references from a template.

        Returns dict mapping variable type to set of variable names.
        E.g., {'params': {'name', 'config'}, 'env': {'API_KEY'}}
        """
        variables: Dict[str, Set[str]] = {}

        def extract_from_value(value: Any) -> None:
            if isinstance(value, str):
                # Find $variable and ${variable} patterns
                matches = re.findall(r'\$\{?([a-zA-Z_][a-zA-Z0-9_.]*)\}?', value)
                for match in matches:
                    parts = match.split('.')
                    var_type = parts[0] if len(parts) > 1 else 'local'
                    var_name = parts[-1]
                    if var_type not in variables:
                        variables[var_type] = set()
                    variables[var_type].add(var_name)
            elif isinstance(value, dict):
                for v in value.values():
                    extract_from_value(v)
            elif isinstance(value, list):
                for item in value:
                    extract_from_value(item)

        for section in template.sections.values():
            extract_from_value(section.content)

        return variables

    def get_dependencies(self, template: ParsedTemplate) -> List[str]:
        """
        Get external dependencies referenced by the template.

        Returns list of module/package names that template depends on.
        """
        dependencies = []

        # Check integrations section
        integrations = template.get_section('integrations')
        if integrations:
            for name, config in integrations.content.items():
                if isinstance(config, dict):
                    module = config.get('module', config.get('package'))
                    if module:
                        dependencies.append(module)

        # Check hooks for import statements
        hooks = template.get_section('hooks')
        if hooks:
            for hook_name, hook_config in hooks.content.items():
                if isinstance(hook_config, dict):
                    handler = hook_config.get('handler', '')
                    if '.' in handler:
                        module = handler.rsplit('.', 1)[0]
                        dependencies.append(module)

        return list(set(dependencies))

    def to_dict(self, template: ParsedTemplate) -> Dict[str, Any]:
        """Convert ParsedTemplate back to dict for serialization."""
        result = {
            'name': template.name,
            'domain': template.domain,
            'version': template.version,
            'description': template.description,
        }

        if template.metadata:
            result['metadata'] = template.metadata

        for name, section in template.sections.items():
            result[name] = section.content

        return result

    def to_yaml(self, template: ParsedTemplate) -> str:
        """Convert ParsedTemplate to YAML string."""
        return yaml.dump(self.to_dict(template), default_flow_style=False, sort_keys=False)
