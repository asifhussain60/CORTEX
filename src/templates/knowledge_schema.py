"""
AC-TC-001-02: Knowledge Base Schema

Defines the schema for template structure and validation.
Provides JSON Schema export and compatibility checking.

Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Set
import json


@dataclass
class SchemaValidationResult:
    """Result of schema validation."""
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    path: Optional[str] = None


class KnowledgeBaseSchema:
    """
    Knowledge base schema for tier-2 templates.
    
    Defines the structure, validation rules, and compatibility
    requirements for template content.
    """
    
    SCHEMA_VERSION = "1.0"
    
    # Required metadata fields
    REQUIRED_METADATA_FIELDS = {'template_id', 'version', 'domain'}
    
    # Optional metadata fields
    OPTIONAL_METADATA_FIELDS = {
        'created_at', 'author', 'description', 'tier', 
        'category', 'tags', 'inherits_from'
    }
    
    # Section types
    SECTION_TYPES = {'header', 'body', 'footer', 'custom'}
    
    # Variable types
    VARIABLE_TYPES = {'string', 'int', 'float', 'bool', 'list', 'object', 'any'}
    
    def __init__(self):
        """Initialize knowledge base schema."""
        self._schema = self._build_schema()
    
    @property
    def schema_version(self) -> str:
        """Get schema version."""
        return self.SCHEMA_VERSION
    
    def _build_schema(self) -> Dict[str, Any]:
        """Build the complete schema definition."""
        return {
            '$schema': 'http://json-schema.org/draft-07/schema#',
            'type': 'object',
            'required': ['metadata', 'template'],
            'properties': {
                'metadata': {
                    'type': 'object',
                    'required': list(self.REQUIRED_METADATA_FIELDS),
                    'properties': {
                        'template_id': {'type': 'string', 'pattern': '^[a-z0-9-]+$'},
                        'version': {'type': 'string', 'pattern': '^\\d+\\.\\d+(\\.\\d+)?$'},
                        'domain': {'type': 'string'},
                        'created_at': {'type': 'string', 'format': 'date-time'},
                        'author': {'type': 'string'},
                        'description': {'type': 'string'},
                        'tier': {'type': 'integer', 'minimum': 0, 'maximum': 3},
                        'category': {'type': 'string'},
                        'tags': {'type': 'array', 'items': {'type': 'string'}},
                        'inherits_from': {'type': 'string'},
                    }
                },
                'template': {
                    'type': 'object',
                    'required': ['structure'],
                    'properties': {
                        'structure': {
                            'type': 'array',
                            'items': {
                                'type': 'object',
                                'required': ['section'],
                                'properties': {
                                    'section': {'type': 'string'},
                                    'source': {'type': 'string'},
                                    'required': {'type': 'boolean'},
                                    'format': {'type': 'string'},
                                    'variables': {'type': 'array', 'items': {'type': 'string'}},
                                }
                            }
                        }
                    }
                },
                'content': {
                    'type': 'object',
                    'additionalProperties': True
                }
            }
        }
    
    def get_template_structure(self) -> Dict[str, Any]:
        """
        Get template structure schema.
        
        Returns:
            Structure schema definition
        """
        return {
            'metadata': {
                'description': 'Template metadata',
                'required': list(self.REQUIRED_METADATA_FIELDS),
                'optional': list(self.OPTIONAL_METADATA_FIELDS),
            },
            'template': {
                'description': 'Template definition with structure',
                'required': ['structure'],
            },
            'content': {
                'description': 'Optional pre-filled content sections',
                'required': False,
            }
        }
    
    def get_metadata_schema(self) -> Dict[str, Any]:
        """
        Get metadata schema definition.
        
        Returns:
            Metadata schema
        """
        return {
            'required': list(self.REQUIRED_METADATA_FIELDS),
            'optional': list(self.OPTIONAL_METADATA_FIELDS),
            'properties': self._schema['properties']['metadata']['properties'],
        }
    
    def get_section_types(self) -> Set[str]:
        """
        Get supported section types.
        
        Returns:
            Set of section type names
        """
        return self.SECTION_TYPES.copy()
    
    def get_inheritance_rules(self) -> Dict[str, Any]:
        """
        Get template inheritance rules.
        
        Returns:
            Inheritance rules definition
        """
        return {
            'base_templates': ['base/success-response', 'base/error-response', 'base/warning-response'],
            'override_rules': {
                'metadata': 'merge',  # Merge with base metadata
                'template.structure': 'extend',  # Extend base structure
                'content': 'override',  # Override base content
            },
            'inheritance_depth': 3,  # Maximum inheritance depth
        }
    
    def get_variable_schema(self) -> Dict[str, Any]:
        """
        Get variable schema definition.
        
        Returns:
            Variable schema
        """
        return {
            'types': list(self.VARIABLE_TYPES),
            'syntax': '{variable_name}',
            'escape': '{{variable_name}}',  # Escaped syntax
            'default_type': 'string',
            'required_indicator': '*',  # {*required_var}
        }
    
    def validate(self, template: Dict[str, Any]) -> SchemaValidationResult:
        """
        Validate template against schema.
        
        Args:
            template: Template dictionary to validate
            
        Returns:
            Validation result
        """
        errors = []
        warnings = []
        
        # Check required top-level keys
        if 'metadata' not in template:
            errors.append("Missing required key: metadata")
        if 'template' not in template:
            errors.append("Missing required key: template")
        
        if errors:
            return SchemaValidationResult(valid=False, errors=errors)
        
        # Validate metadata
        metadata = template.get('metadata', {})
        for field in self.REQUIRED_METADATA_FIELDS:
            if field not in metadata:
                errors.append(f"Missing required metadata field: {field}")
        
        # Validate template_id format
        template_id = metadata.get('template_id', '')
        if template_id and not all(c.islower() or c.isdigit() or c == '-' for c in template_id):
            errors.append(f"Invalid template_id format: {template_id}")
        
        # Validate template structure
        template_def = template.get('template', {})
        if 'structure' not in template_def:
            errors.append("Missing required template key: structure")
        else:
            structure = template_def['structure']
            if not isinstance(structure, list):
                errors.append("template.structure must be a list")
            else:
                for i, section in enumerate(structure):
                    if 'section' not in section:
                        errors.append(f"Section {i} missing required key: section")
        
        return SchemaValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )
    
    def to_json_schema(self) -> Dict[str, Any]:
        """
        Export as JSON Schema.
        
        Returns:
            JSON Schema dictionary
        """
        return self._schema.copy()
    
    def is_compatible(self, version: str) -> bool:
        """
        Check if version is compatible with current schema.
        
        Args:
            version: Version string to check
            
        Returns:
            True if compatible
        """
        try:
            major, minor = version.split('.')[:2]
            current_major, current_minor = self.SCHEMA_VERSION.split('.')[:2]
            
            # Major version must match
            if int(major) != int(current_major):
                return False
            
            # Minor version must be <= current
            return int(minor) <= int(current_minor)
        except (ValueError, IndexError):
            return False
