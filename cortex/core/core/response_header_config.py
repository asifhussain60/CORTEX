"""
Response Header Configuration Loader

Loads and manages global response header configuration from YAML.
Follows singleton pattern to match ResponseTemplateRegistry design.

Classes:
    HeaderConfig: Dataclass representing header configuration
    HeaderConfigLoader: Loads YAML configuration
    HeaderConfigurationManager: Singleton for managing header settings
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class AuthorInfo:
    """Author and attribution information."""
    name: str
    github_handle: str
    repository: str
    github_pages: str


@dataclass
class CopyrightInfo:
    """Copyright information."""
    start_year: int
    end_year: int
    holder: str
    notice: str
    license: str
    license_url: str


@dataclass
class HeaderTemplate:
    """Header template configuration."""
    enabled: bool
    position: str  # "before_content", "after_content", "none"
    description: str
    template: str  # Template string with {variable} placeholders
    formatting: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CopyrightSection:
    """Copyright section configuration."""
    enabled: bool
    position: str  # Usually "after_header"
    description: str
    template: str
    formatting: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FooterTemplate:
    """Footer template configuration (optional)."""
    enabled: bool
    position: str
    description: str
    template: str


@dataclass
class VariableDefinition:
    """Template variable definition."""
    name: str
    type: str
    example: Optional[str] = None
    description: Optional[str] = None


@dataclass
class VariableConfig:
    """Variable configuration with mandatory and auto-populated."""
    mandatory: List[VariableDefinition] = field(default_factory=list)
    auto_populated: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class EnforcementConfig:
    """Header enforcement rules."""
    require_on_all_responses: bool = True
    audit_missing_headers: bool = True
    log_header_injection: bool = False
    validate_all_variables: bool = True
    fail_on_missing_variable: bool = False


@dataclass
class HeaderConfiguration:
    """Complete header configuration."""
    metadata: Dict[str, Any]
    author: AuthorInfo
    copyright: CopyrightInfo
    header: HeaderTemplate
    copyright_section: CopyrightSection
    footer: Optional[FooterTemplate] = None
    variables: Optional[VariableConfig] = None
    domain_overrides: Optional[Dict[str, Any]] = None
    enforcement: Optional[EnforcementConfig] = None
    audit: Optional[Dict[str, Any]] = None


# =============================================================================
# CONFIGURATION LOADER
# =============================================================================

class HeaderConfigLoader:
    """Loads header configuration from YAML files."""

    @staticmethod
    def load(yaml_path: str) -> HeaderConfiguration:
        """
        Load header configuration from YAML file.

        Args:
            yaml_path: Path to response-headers.yaml

        Returns:
            HeaderConfiguration object

        Raises:
            FileNotFoundError: If YAML file not found
            yaml.YAMLError: If YAML parsing fails
            ValueError: If configuration is invalid
        """
        if not os.path.exists(yaml_path):
            raise FileNotFoundError(f"Header configuration file not found: {yaml_path}")

        with open(yaml_path, 'r') as f:
            try:
                data = yaml.safe_load(f)
            except yaml.YAMLError as e:
                raise yaml.YAMLError(f"Error parsing header configuration YAML: {e}")

        if not data:
            raise ValueError("Empty header configuration file")

        return HeaderConfigLoader._parse_configuration(data)

    @staticmethod
    def _parse_configuration(data: Dict[str, Any]) -> HeaderConfiguration:
        """Parse raw YAML data into HeaderConfiguration."""

        # Parse author section
        author_data = data.get('author', {})
        author = AuthorInfo(
            name=author_data.get('name', 'Unknown'),
            github_handle=author_data.get('github_handle', ''),
            repository=author_data.get('repository', ''),
            github_pages=author_data.get('github_pages', '')
        )

        # Parse copyright section
        copyright_data = data.get('copyright', {})
        copyright = CopyrightInfo(
            start_year=copyright_data.get('start_year', 2025),
            end_year=copyright_data.get('end_year', 2026),
            holder=copyright_data.get('holder', 'Asif Hussain'),
            notice=copyright_data.get('notice', ''),
            license=copyright_data.get('license', 'Source-Available'),
            license_url=copyright_data.get('license_url', '')
        )

        # Parse header template
        header_data = data.get('header', {})
        header = HeaderTemplate(
            enabled=header_data.get('enabled', True),
            position=header_data.get('position', 'before_content'),
            description=header_data.get('description', ''),
            template=header_data.get('template', ''),
            formatting=header_data.get('formatting', {})
        )

        # Parse copyright section
        copyright_section_data = data.get('copyright_section', {})
        copyright_section = CopyrightSection(
            enabled=copyright_section_data.get('enabled', True),
            position=copyright_section_data.get('position', 'after_header'),
            description=copyright_section_data.get('description', ''),
            template=copyright_section_data.get('template', ''),
            formatting=copyright_section_data.get('formatting', {})
        )

        # Parse footer template (optional)
        footer_data = data.get('footer')
        footer = None
        if footer_data:
            footer = FooterTemplate(
                enabled=footer_data.get('enabled', False),
                position=footer_data.get('position', 'after_content'),
                description=footer_data.get('description', ''),
                template=footer_data.get('template', '')
            )

        # Parse variables
        variables_data = data.get('variables')
        variables = None
        if variables_data:
            mandatory_vars = []
            for var_data in variables_data.get('mandatory', []):
                mandatory_vars.append(VariableDefinition(
                    name=var_data.get('name', ''),
                    type=var_data.get('type', 'string'),
                    example=var_data.get('example'),
                    description=var_data.get('description')
                ))

            variables = VariableConfig(
                mandatory=mandatory_vars,
                auto_populated=variables_data.get('auto_populated', [])
            )

        # Parse enforcement
        enforcement_data = data.get('enforcement', {})
        enforcement = EnforcementConfig(
            require_on_all_responses=enforcement_data.get('require_on_all_responses', True),
            audit_missing_headers=enforcement_data.get('audit_missing_headers', True),
            log_header_injection=enforcement_data.get('log_header_injection', False),
            validate_all_variables=enforcement_data.get('validate_all_variables', True),
            fail_on_missing_variable=enforcement_data.get('fail_on_missing_variable', False)
        )

        return HeaderConfiguration(
            metadata=data.get('metadata', {}),
            author=author,
            copyright=copyright,
            header=header,
            copyright_section=copyright_section,
            footer=footer,
            variables=variables,
            domain_overrides=data.get('domain_overrides'),
            enforcement=enforcement,
            audit=data.get('audit')
        )


# =============================================================================
# CONFIGURATION MANAGER (SINGLETON)
# =============================================================================

class HeaderConfigurationManager:
    """
    Singleton manager for header configuration.

    Follows same pattern as ResponseTemplateRegistry to maintain
    architectural consistency.
    """

    _instance: Optional['HeaderConfigurationManager'] = None
    _config: Optional[HeaderConfiguration] = None

    def __init__(self):
        """Initialize manager (singleton)."""
        self._loaded = False

    @classmethod
    def get_instance(cls) -> 'HeaderConfigurationManager':
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def load_configuration(self, yaml_path: str) -> None:
        """
        Load header configuration from YAML file.

        Args:
            yaml_path: Path to response-headers.yaml
        """
        self._config = HeaderConfigLoader.load(yaml_path)
        self._loaded = True

    def get_configuration(self) -> Optional[HeaderConfiguration]:
        """Get loaded configuration."""
        return self._config

    def is_loaded(self) -> bool:
        """Check if configuration is loaded."""
        return self._loaded

    def get_author_name(self) -> str:
        """Get author name."""
        if not self._config:
            return "Unknown"
        return self._config.author.name

    def get_copyright_notice(self) -> str:
        """Get formatted copyright notice."""
        if not self._config:
            return ""

        notice = self._config.copyright.notice
        # Replace placeholders in notice
        notice = notice.replace('{start_year}', str(self._config.copyright.start_year))
        notice = notice.replace('{end_year}', str(self._config.copyright.end_year))
        notice = notice.replace('{holder}', self._config.copyright.holder)
        return notice

    def get_repository_url(self) -> str:
        """Get repository URL."""
        if not self._config:
            return ""
        return self._config.author.repository

    def get_github_pages_url(self) -> str:
        """Get GitHub Pages URL."""
        if not self._config:
            return ""
        return self._config.author.github_pages

    def get_header_template(self) -> Optional[str]:
        """Get header template string."""
        if not self._config:
            return None
        return self._config.header.template

    def get_copyright_template(self) -> Optional[str]:
        """Get copyright template string."""
        if not self._config:
            return None
        return self._config.copyright_section.template

    def is_header_enabled(self) -> bool:
        """Check if headers are enabled."""
        if not self._config:
            return True
        return self._config.header.enabled

    def is_copyright_enabled(self) -> bool:
        """Check if copyright section is enabled."""
        if not self._config:
            return True
        return self._config.copyright_section.enabled

    def is_footer_enabled(self) -> bool:
        """Check if footer is enabled."""
        if not self._config or not self._config.footer:
            return False
        return self._config.footer.enabled

    def get_enforcement_config(self) -> Optional[EnforcementConfig]:
        """Get enforcement configuration."""
        if not self._config:
            return None
        return self._config.enforcement

    def get_header_formatting(self) -> Dict[str, Any]:
        """Get header formatting rules."""
        if not self._config:
            return {}
        return self._config.header.formatting

    def get_copyright_formatting(self) -> Dict[str, Any]:
        """Get copyright formatting rules."""
        if not self._config:
            return {}
        return self._config.copyright_section.formatting

    def get_mandatory_variables(self) -> List[str]:
        """Get list of mandatory variable names."""
        if not self._config or not self._config.variables:
            return []
        return [v.name for v in self._config.variables.mandatory]

    def get_auto_populated_variables(self) -> Dict[str, Any]:
        """Get auto-populated variables as dict."""
        if not self._config or not self._config.variables:
            return {}

        auto_vars = {}
        for var_data in self._config.variables.auto_populated:
            name = var_data.get('name')
            value = var_data.get('value')
            if name and value:
                auto_vars[name] = value

        return auto_vars

    def clear(self) -> None:
        """Clear configuration (mainly for testing)."""
        self._config = None
        self._loaded = False
