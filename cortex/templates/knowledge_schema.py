"""
CORTEX Templates - Knowledge Base Schema

Schema definitions and validation for template structures.

Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum


class VariableType(Enum):
    """Template variable types."""
    STRING = "string"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    LIST = "list"
    OBJECT = "object"
    OPTIONAL = "optional"


@dataclass
class ValidationResult:
    """Schema validation result."""
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class KnowledgeBaseSchema:
    """Knowledge base schema for template validation.
    
    Defines structure, metadata, and validation rules for templates.
    """
    
    def __init__(self) -> None:
        """Initialize knowledge base schema."""
        self.schema_version = "1.0.0"
        self._template_structure = self._define_template_structure()
        self._metadata_schema = self._define_metadata_schema()
        self._section_types = self._define_section_types()
        self._variable_schema = self._define_variable_schema()
        self._inheritance_rules = self._define_inheritance_rules()
    
    def _define_template_structure(self) -> Dict[str, Any]:
        """Define template structure schema.
        
        Returns:
            Template structure definition.
        """
        return {
            'metadata': {
                'type': 'object',
                'required': True,
            },
            'template': {
                'type': 'object',
                'required': True,
            },
            'content': {
                'type': 'object',
                'required': False,
            },
        }
    
    def _define_metadata_schema(self) -> Dict[str, Any]:
        """Define metadata schema.
        
        Returns:
            Metadata schema definition.
        """
        return {
            'required': ['template_id', 'version', 'domain'],
            'optional': ['category', 'tags', 'author', 'created_at'],
            'fields': {
                'template_id': {'type': 'string'},
                'version': {'type': 'string'},
                'domain': {'type': 'string'},
                'category': {'type': 'string'},
                'tags': {'type': 'list'},
                'author': {'type': 'string'},
                'created_at': {'type': 'string'},
            },
        }
    
    def _define_section_types(self) -> Dict[str, Dict[str, Any]]:
        """Define content section types.
        
        Returns:
            Section types definition.
        """
        return {
            'header': {
                'required': False,
                'type': 'string',
            },
            'body': {
                'required': True,
                'type': 'string',
            },
            'footer': {
                'required': False,
                'type': 'string',
            },
        }
    
    def _define_variable_schema(self) -> Dict[str, Any]:
        """Define variable schema.
        
        Returns:
            Variable schema definition.
        """
        return {
            'types': {
                'string': {
                    'validation': 'regex',
                    'default': '',
                },
                'integer': {
                    'validation': 'range',
                    'default': 0,
                },
                'boolean': {
                    'validation': 'none',
                    'default': False,
                },
                'list': {
                    'validation': 'length',
                    'default': [],
                },
                'object': {
                    'validation': 'schema',
                    'default': {},
                },
            },
        }
    
    def _define_inheritance_rules(self) -> Dict[str, Any]:
        """Define template inheritance rules.
        
        Returns:
            Inheritance rules definition.
        """
        return {
            'base_templates': {
                'allowed': True,
                'max_depth': 3,
            },
            'override_rules': {
                'metadata': 'merge',
                'template': 'replace',
                'content': 'merge',
            },
        }
    
    def get_template_structure(self) -> Dict[str, Any]:
        """Get template structure schema.
        
        Returns:
            Template structure definition.
        """
        return self._template_structure
    
    def get_metadata_schema(self) -> Dict[str, Any]:
        """Get metadata schema.
        
        Returns:
            Metadata schema definition.
        """
        return self._metadata_schema
    
    def get_section_types(self) -> Dict[str, Dict[str, Any]]:
        """Get content section types.
        
        Returns:
            Section types definition.
        """
        return self._section_types
    
    def get_variable_schema(self) -> Dict[str, Any]:
        """Get variable schema.
        
        Returns:
            Variable schema definition.
        """
        return self._variable_schema
    
    def get_inheritance_rules(self) -> Dict[str, Any]:
        """Get inheritance rules.
        
        Returns:
            Inheritance rules definition.
        """
        return self._inheritance_rules
    
    def validate(self, template: Dict[str, Any]) -> ValidationResult:
        """Validate template against schema.
        
        Args:
            template: Template to validate.
            
        Returns:
            Validation result.
        """
        errors = []
        
        # Check required top-level keys
        for key, spec in self._template_structure.items():
            if spec.get('required') and key not in template:
                errors.append(f"Missing required key: {key}")
        
        # Validate metadata if present
        if 'metadata' in template:
            metadata = template['metadata']
            required_fields = self._metadata_schema['required']
            for field in required_fields:
                if field not in metadata:
                    errors.append(f"Missing required metadata field: {field}")
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
        )
    
    def to_json_schema(self) -> Dict[str, Any]:
        """Export as JSON schema.
        
        Returns:
            JSON schema representation.
        """
        return {
            '$schema': 'http://json-schema.org/draft-07/schema#',
            'type': 'object',
            'properties': {
                'metadata': {
                    'type': 'object',
                    'required': self._metadata_schema['required'],
                },
                'template': {
                    'type': 'object',
                },
                'content': {
                    'type': 'object',
                },
            },
            'required': ['metadata', 'template'],
        }
    
    def is_compatible(self, version: str) -> bool:
        """Check if schema is compatible with version.
        
        Args:
            version: Version string to check.
            
        Returns:
            True if compatible.
        """
        # Simple version compatibility check
        major_version = self.schema_version.split('.')[0]
        target_major = version.split('.')[0]
        return major_version == target_major
