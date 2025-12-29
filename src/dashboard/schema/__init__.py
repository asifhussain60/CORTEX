"""
Dashboard Schema Package

Universal schema v2.0 for multi-project dashboard support.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

from src.dashboard.schema.universal_schema import UniversalSchema, SCHEMA_VERSION
from src.dashboard.schema.schema_validator import SchemaValidator, ValidationResult
from src.dashboard.schema.project_type_detector import ProjectTypeDetector
from src.dashboard.schema.schema_migrator import SchemaMigrator

__all__ = [
    "UniversalSchema",
    "SCHEMA_VERSION",
    "SchemaValidator",
    "ValidationResult",
    "ProjectTypeDetector",
    "SchemaMigrator"
]
