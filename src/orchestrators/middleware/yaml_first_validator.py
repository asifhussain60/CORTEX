"""
YAMLFirstValidator Middleware - Enforce CORE-018 Governance Rule

CORE-018: YAML-First Design Mandatory
  - ALL configuration MUST be specified in YAML first
  - Code generation from YAML (not vice versa)
  - Prevents ad-hoc code-first decisions
  - Ensures governance is baked into system design

Author: CORTEX Governance System
Version: 1.0.0
Created: 2026-01-12
"""

import yaml
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class YAMLDesignSpec:
    """YAML-first design specification."""

    component_name: str
    component_type: str  # 'orchestrator', 'middleware', 'service', etc.
    description: str
    requirements: List[str]
    interfaces: Dict[str, str]  # method_name: description
    config: Dict  # Configuration structure


class YAMLFirstValidator:
    """Middleware to enforce CORE-018 YAML-first design requirements."""

    # Allowed components that can be defined
    COMPONENT_TYPES = {
        'orchestrator',
        'middleware',
        'service',
        'utility',
        'integration',
        'orchestration_system',
    }

    # Required YAML fields for component specs
    REQUIRED_YAML_FIELDS = {
        'component_name',
        'component_type',
        'description',
        'requirements',
    }

    @classmethod
    def validate_yaml_design_spec(
        cls, yaml_content: str, component_name: str
    ) -> Tuple[bool, List[str]]:
        """
        Validate that a component has a proper YAML design spec.

        Args:
            yaml_content: YAML content
            component_name: Name of component

        Returns:
            Tuple of (is_valid: bool, issues: List[str])
        """
        issues = []

        try:
            spec = yaml.safe_load(yaml_content)

            if not spec:
                issues.append("YAML spec is empty")
                return False, issues

            # Check required fields
            for field in cls.REQUIRED_YAML_FIELDS:
                if field not in spec:
                    issues.append(f"Missing required field: {field}")

            # Check component type
            if 'component_type' in spec:
                comp_type = spec['component_type']
                if comp_type not in cls.COMPONENT_TYPES:
                    issues.append(
                        f"Invalid component_type '{comp_type}'. "
                        f"Must be one of: {', '.join(cls.COMPONENT_TYPES)}"
                    )

            # Check description quality
            if 'description' in spec:
                desc = spec['description']
                if len(desc) < 10:
                    issues.append("Description too short (minimum 10 characters)")

            # Check requirements are a list
            if 'requirements' in spec:
                reqs = spec['requirements']
                if not isinstance(reqs, list):
                    issues.append("Requirements must be a list")
                elif len(reqs) == 0:
                    issues.append("Requirements list cannot be empty")

        except yaml.YAMLError as e:
            issues.append(f"YAML parsing error: {str(e)}")

        return len(issues) == 0, issues

    @classmethod
    def design_spec_exists(cls, component_name: str) -> bool:
        """
        Check if a design spec YAML file exists for a component.

        Args:
            component_name: Name of component

        Returns:
            True if spec file exists
        """
        spec_path = Path(
            f'cortex-brain/manifests/design-specs/{component_name}-spec.yaml'
        )
        return spec_path.exists()

    @classmethod
    def get_design_spec_path(cls, component_name: str) -> Path:
        """Get expected path for a component's design spec."""
        return Path(
            f'cortex-brain/manifests/design-specs/{component_name}-spec.yaml'
        )

    @classmethod
    def validate_yaml_first_priority(
        cls, component_name: str, yaml_path: str, code_path: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate that YAML spec exists and predates code.

        Args:
            component_name: Component name
            yaml_path: Path to YAML spec
            code_path: Path to code implementation

        Returns:
            Tuple of (is_valid: bool, reason: str or None)
        """
        yaml_file = Path(yaml_path)
        code_file = Path(code_path)

        # YAML must exist first
        if not yaml_file.exists():
            return (
                False,
                f"CORE-018 VIOLATION: YAML spec missing for '{component_name}'. "
                f"Create {yaml_path} FIRST before implementing code.",
            )

        # If code exists, YAML should predate it
        if code_file.exists():
            yaml_mtime = yaml_file.stat().st_mtime
            code_mtime = code_file.stat().st_mtime

            if yaml_mtime > code_mtime:
                logger.warning(
                    f"⚠️  Code updated after YAML. Ensure YAML was the source of truth."
                )

        return True, None

    @classmethod
    def get_yaml_first_workflow(cls, component_name: str) -> List[str]:
        """
        Get the YAML-first development workflow for a component.

        Args:
            component_name: Component name

        Returns:
            List of workflow steps
        """
        return [
            f"1. Create design spec: cortex-brain/manifests/design-specs/{component_name}-spec.yaml",
            f"2. Define requirements, interfaces, and configuration in YAML",
            f"3. Get design review and approval",
            f"4. Generate code skeleton from YAML (via code generator)",
            f"5. Implement code following YAML specification",
            f"6. Update YAML if requirements change",
        ]

    @classmethod
    def audit_design_specs(cls, root_dir: str = '.') -> Dict[str, bool]:
        """
        Audit which components have design specs.

        Args:
            root_dir: Root directory to scan

        Returns:
            Dictionary of {component_name: has_spec}
        """
        spec_dir = Path('cortex-brain/manifests/design-specs')
        components = {}

        if not spec_dir.exists():
            logger.warning(f"Design specs directory not found: {spec_dir}")
            return components

        for spec_file in spec_dir.glob('*-spec.yaml'):
            component_name = spec_file.name.replace('-spec.yaml', '')
            components[component_name] = True

        return components

    @classmethod
    def missing_design_specs(cls, component_list: List[str]) -> List[str]:
        """
        Identify which components are missing design specs.

        Args:
            component_list: List of component names to check

        Returns:
            List of components missing specs
        """
        missing = []

        for component in component_list:
            if not cls.design_spec_exists(component):
                missing.append(component)

        return missing


class YAMLFirstViolation(Exception):
    """Exception raised when YAML-first design requirement is violated."""

    pass


# Public API
def validate_yaml_first_design(
    yaml_path: str, component_name: str
) -> Tuple[bool, str]:
    """
    Validate YAML-first design for a component.

    Args:
        yaml_path: Path to YAML spec
        component_name: Component name

    Returns:
        Tuple of (is_valid: bool, message: str)
    """
    if not Path(yaml_path).exists():
        return False, f"Design spec not found: {yaml_path}"

    yaml_content = Path(yaml_path).read_text()
    is_valid, issues = YAMLFirstValidator.validate_yaml_design_spec(
        yaml_content, component_name
    )

    if is_valid:
        return True, f"✅ YAML design spec valid for '{component_name}'"
    else:
        return False, f"Design spec issues: {'; '.join(issues)}"


def get_yaml_first_workflow(component_name: str) -> List[str]:
    """Get YAML-first workflow steps."""
    return YAMLFirstValidator.get_yaml_first_workflow(component_name)
