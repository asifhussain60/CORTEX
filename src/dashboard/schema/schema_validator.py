"""
Schema Validator v2.0

Validates dashboard data against universal schema v2.0.
Supports backward compatibility with v1 schema.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ValidationResult:
    """Result of schema validation"""
    is_valid: bool
    errors: List[str]
    warnings: List[str] = None
    schema_version: str = "2.0.0"
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


class SchemaValidator:
    """Validator for universal schema v2.0"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def validate(self, data: Dict[str, Any], allow_v1: bool = False) -> ValidationResult:
        """
        Validate data against schema.
        
        Args:
            data: Dashboard data to validate
            allow_v1: Allow v1 schema format for backward compatibility
        
        Returns:
            ValidationResult with validation status and errors
        """
        self.errors = []
        self.warnings = []
        
        # Check schema version
        schema_version = data.get("schema_version", "1.0.0")
        
        if schema_version == "1.0.0" and allow_v1:
            return self._validate_v1_schema(data)
        elif schema_version == "2.0.0":
            return self._validate_v2_schema(data)
        else:
            self.errors.append(f"Unsupported schema version: {schema_version}")
            return ValidationResult(False, self.errors, self.warnings)
    
    def _validate_v1_schema(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate v1 schema format"""
        required_v1_sections = ["metadata", "health", "code_metrics", "code_quality"]
        
        for section in required_v1_sections:
            if section not in data:
                self.errors.append(f"Missing required v1 section: {section}")
        
        # Validate metadata
        if "metadata" in data:
            metadata = data["metadata"]
            required_metadata = ["repo_name", "branch", "commit_hash", "commit_date", "last_scan"]
            for field in required_metadata:
                if field not in metadata:
                    self.errors.append(f"Missing metadata field: {field}")
        
        is_valid = len(self.errors) == 0
        return ValidationResult(is_valid, self.errors, self.warnings, schema_version="1.0.0")
    
    def _validate_v2_schema(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate v2 schema format"""
        required_v2_sections = [
            "schema_version",
            "metadata",
            "architecture",
            "code_metrics",
            "security",
            "testing",
            "documentation",
            "health"
        ]
        
        for section in required_v2_sections:
            if section not in data:
                self.errors.append(f"Missing required v2 section: {section}")
        
        # Validate metadata
        if "metadata" in data:
            self._validate_metadata_v2(data["metadata"])
        
        # Validate health (required section)
        if "health" in data:
            self._validate_health(data["health"])
        
        # Optional sections (can be None)
        optional_sections = ["frontend", "backend", "database", "infrastructure", "business_domain"]
        for section in optional_sections:
            if section in data and data[section] is not None:
                self._validate_optional_section(section, data[section])
        
        is_valid = len(self.errors) == 0
        return ValidationResult(is_valid, self.errors, self.warnings, schema_version="2.0.0")
    
    def _validate_metadata_v2(self, metadata: Dict[str, Any]):
        """Validate metadata section"""
        required_fields = [
            "project_name",
            "project_type",
            "primary_languages",
            "repository_url",
            "branch",
            "scan_timestamp",
            "scan_duration_seconds",
            "total_files_scanned"
        ]
        
        for field in required_fields:
            if field not in metadata:
                self.errors.append(f"Metadata missing required field: {field}")
        
        # Validate project_type enum
        if "project_type" in metadata:
            valid_types = ["full_stack", "api", "frontend", "database", "microservices", "library", "unknown"]
            if metadata["project_type"] not in valid_types:
                self.errors.append(f"Invalid project_type: {metadata['project_type']}")
    
    def _validate_health(self, health: Dict[str, Any]):
        """Validate health section"""
        required_fields = ["overall_score", "trend", "status"]
        
        for field in required_fields:
            if field not in health:
                self.errors.append(f"Health missing required field: {field}")
        
        # Validate enums
        if "trend" in health:
            valid_trends = ["improving", "stable", "degrading"]
            if health["trend"] not in valid_trends:
                self.errors.append(f"Invalid trend value: {health['trend']}")
        
        if "status" in health:
            valid_statuses = ["healthy", "warning", "critical"]
            if health["status"] not in valid_statuses:
                self.errors.append(f"Invalid status value: {health['status']}")
        
        # Validate score range
        if "overall_score" in health:
            score = health["overall_score"]
            if not isinstance(score, int) or score < 0 or score > 100:
                self.errors.append(f"Invalid overall_score: {score} (must be 0-100)")
    
    def _validate_optional_section(self, section_name: str, section_data: Dict[str, Any]):
        """Validate optional sections (frontend, backend, database, etc.)"""
        # These sections can have any structure, just check they're dictionaries
        if not isinstance(section_data, dict):
            self.errors.append(f"Section {section_name} must be a dictionary or None")
