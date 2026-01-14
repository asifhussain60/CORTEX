"""
Compatibility Layer - Legacy Pattern Adaptation (AC-AR-008)

Implements schema and pattern compatibility for:
- Evidence bundle schema compatible with established patterns (AC-AR-008-01)
- Audit log format follows established patterns (AC-AR-008-02)
- Migration path documented for existing users (AC-AR-008-03)

Features:
- Schema validation against legacy patterns
- Format conversion and translation layers
- Backward compatibility guarantees
- Migration documentation
- Version detection and handling
- Fallback mechanisms for legacy formats

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Dict, Optional, List, Tuple

from src.core.result import Result, Ok, Err


class SchemaVersion(Enum):
    """Schema version tracking."""
    V1_LEGACY = "1.0"      # Original/legacy format
    V2_CURRENT = "2.0"     # Current CORTEX format
    V3_FUTURE = "3.0"      # Reserved for future


class CompatibilityMode(Enum):
    """Compatibility execution modes."""
    STRICT = auto()        # Reject incompatible formats
    COMPATIBLE = auto()    # Accept and convert
    LEGACY_ONLY = auto()   # Accept only legacy formats


@dataclass
class SchemaMapping:
    """Maps legacy field names to new schema."""
    legacy_field: str
    new_field: str
    transformer: Optional[callable] = None  # Optional conversion function
    required: bool = False
    default_value: Optional[Any] = None


@dataclass
class FormatProfile:
    """Profile for a supported format."""
    format_name: str
    version: SchemaVersion
    description: str
    field_mappings: List[SchemaMapping]
    required_fields: List[str]
    optional_fields: List[str]


class CompatibilityLayer:
    """
    Compatibility layer for legacy pattern support.
    
    Provides:
    - Schema validation and conversion
    - Format detection and translation
    - Migration assistance
    - Backward compatibility guarantees
    """
    
    def __init__(self, mode: CompatibilityMode = CompatibilityMode.COMPATIBLE):
        """
        Initialize compatibility layer.
        
        Args:
            mode: Compatibility mode (STRICT, COMPATIBLE, LEGACY_ONLY)
        """
        self._mode = mode
        self._format_profiles: Dict[str, FormatProfile] = {}
        self._version_registry: Dict[str, SchemaVersion] = {}
        self._migration_guides: Dict[str, str] = {}
        
        # Register default formats
        self._register_default_formats()
    
    def _register_default_formats(self) -> None:
        """Register built-in format profiles."""
        # Legacy Evidence Bundle Format (V1)
        legacy_evidence = FormatProfile(
            format_name="evidence_bundle_v1",
            version=SchemaVersion.V1_LEGACY,
            description="Original evidence bundle format",
            field_mappings=[
                SchemaMapping("bundle_id", "checkpoint_id", required=True),
                SchemaMapping("timestamp", "created_at", required=True),
                SchemaMapping("artifacts", "state_snapshot", required=True),
                SchemaMapping("ac_ref", "ac_id", required=False),
            ],
            required_fields=["bundle_id", "timestamp", "artifacts"],
            optional_fields=["ac_ref", "metadata"],
        )
        self._format_profiles["evidence_bundle_v1"] = legacy_evidence
        
        # Current Evidence Bundle Format (V2)
        current_evidence = FormatProfile(
            format_name="evidence_bundle_v2",
            version=SchemaVersion.V2_CURRENT,
            description="Current CORTEX evidence bundle format",
            field_mappings=[
                SchemaMapping("checkpoint_id", "checkpoint_id", required=True),
                SchemaMapping("created_at", "created_at", required=True),
                SchemaMapping("state_snapshot", "state_snapshot", required=True),
                SchemaMapping("ac_id", "ac_id", required=False),
            ],
            required_fields=["checkpoint_id", "created_at", "state_snapshot"],
            optional_fields=["ac_id", "metadata_json"],
        )
        self._format_profiles["evidence_bundle_v2"] = current_evidence
        
        # Legacy Audit Format (V1)
        legacy_audit = FormatProfile(
            format_name="audit_log_v1",
            version=SchemaVersion.V1_LEGACY,
            description="Original audit log format",
            field_mappings=[
                SchemaMapping("log_id", "audit_id", required=True),
                SchemaMapping("entry_time", "created_at", required=True),
                SchemaMapping("action", "action_type", required=True),
                SchemaMapping("actor", "actor_id", required=False),
                SchemaMapping("hash_chain", "previous_hash", required=False),
            ],
            required_fields=["log_id", "entry_time", "action"],
            optional_fields=["actor", "hash_chain", "metadata"],
        )
        self._format_profiles["audit_log_v1"] = legacy_audit
        
        # Current Audit Format (V2)
        current_audit = FormatProfile(
            format_name="audit_log_v2",
            version=SchemaVersion.V2_CURRENT,
            description="Current CORTEX audit log format",
            field_mappings=[
                SchemaMapping("audit_id", "audit_id", required=True),
                SchemaMapping("created_at", "created_at", required=True),
                SchemaMapping("action_type", "action_type", required=True),
                SchemaMapping("actor_id", "actor_id", required=False),
                SchemaMapping("previous_hash", "previous_hash", required=False),
            ],
            required_fields=["audit_id", "created_at", "action_type"],
            optional_fields=["actor_id", "previous_hash", "context_data"],
        )
        self._format_profiles["audit_log_v2"] = current_audit
    
    def detect_format(self, data: Dict[str, Any]) -> Result[Tuple[str, SchemaVersion]]:
        """
        AC-AR-008-01: Detect data format and version.
        
        Args:
            data: Data to analyze
        
        Returns:
            Result containing (format_name, version)
        """
        # Check for evidence bundle indicators
        if "bundle_id" in data:
            # V1 uses bundle_id
            return Ok(("evidence_bundle_v1", SchemaVersion.V1_LEGACY))
        elif "checkpoint_id" in data and "state_snapshot" in data:
            # V2 uses checkpoint_id and state_snapshot
            return Ok(("evidence_bundle_v2", SchemaVersion.V2_CURRENT))
        elif "artifacts" in data and "timestamp" in data:
            # V1 evidence bundle indicators
            return Ok(("evidence_bundle_v1", SchemaVersion.V1_LEGACY))
        
        # Check for audit log indicators
        if "log_id" in data:
            # V1 uses log_id
            return Ok(("audit_log_v1", SchemaVersion.V1_LEGACY))
        elif "audit_id" in data and "action_type" in data:
            # V2 uses audit_id and action_type
            return Ok(("audit_log_v2", SchemaVersion.V2_CURRENT))
        elif "entry_time" in data and "action" in data:
            # V1 audit log indicators
            return Ok(("audit_log_v1", SchemaVersion.V1_LEGACY))
        elif "created_at" in data and ("action_type" in data or "action" in data):
            # Could be v2 (created_at) or try to distinguish
            if "action_type" in data:
                return Ok(("audit_log_v2", SchemaVersion.V2_CURRENT))
            else:
                return Ok(("audit_log_v1", SchemaVersion.V1_LEGACY))
        
        return Err("Unable to detect format from data")
    
    def validate_schema(
        self,
        data: Dict[str, Any],
        format_name: str,
    ) -> Result[bool]:
        """
        AC-AR-008-01: Validate data against schema.
        
        Args:
            data: Data to validate
            format_name: Expected format name
        
        Returns:
            Result indicating if data is valid
        """
        if format_name not in self._format_profiles:
            return Err(f"Unknown format: {format_name}")
        
        profile = self._format_profiles[format_name]
        
        # Check required fields
        for required_field in profile.required_fields:
            if required_field not in data:
                return Err(f"Missing required field: {required_field}")
        
        # Check field types (basic validation)
        for field in data:
            if field not in profile.required_fields and field not in profile.optional_fields:
                if self._mode == CompatibilityMode.STRICT:
                    return Err(f"Unknown field: {field}")
        
        return Ok(True)
    
    def convert_format(
        self,
        data: Dict[str, Any],
        from_format: str,
        to_format: str,
    ) -> Result[Dict[str, Any]]:
        """
        AC-AR-008-01: Convert data between formats.
        
        Args:
            data: Data to convert
            from_format: Source format name
            to_format: Target format name
        
        Returns:
            Result containing converted data
        """
        # Validate source format
        if from_format not in self._format_profiles:
            return Err(f"Unknown source format: {from_format}")
        
        if to_format not in self._format_profiles:
            return Err(f"Unknown target format: {to_format}")
        
        from_profile = self._format_profiles[from_format]
        to_profile = self._format_profiles[to_format]
        
        # Build reverse mapping from source
        reverse_mapping = {}
        for mapping in from_profile.field_mappings:
            reverse_mapping[mapping.legacy_field if from_format.endswith("_v1") 
                          else mapping.new_field] = mapping.new_field
        
        # Convert fields
        converted = {}
        for source_field, source_value in data.items():
            # Find mapping
            target_field = None
            transformer = None
            
            for mapping in from_profile.field_mappings:
                legacy = mapping.legacy_field
                new = mapping.new_field
                
                if (from_format.endswith("_v1") and source_field == legacy) or \
                   (from_format.endswith("_v2") and source_field == new):
                    target_field = new
                    transformer = mapping.transformer
                    break
            
            if target_field:
                # Apply transformer if exists
                if transformer:
                    converted[target_field] = transformer(source_value)
                else:
                    converted[target_field] = source_value
            else:
                # Pass through unknown fields if compatible mode
                if self._mode == CompatibilityMode.COMPATIBLE:
                    converted[source_field] = source_value
        
        # Add defaults for missing fields
        for mapping in to_profile.field_mappings:
            if mapping.required and mapping.new_field not in converted:
                if mapping.default_value is not None:
                    converted[mapping.new_field] = mapping.default_value
        
        return Ok(converted)
    
    def get_format_profile(self, format_name: str) -> Result[FormatProfile]:
        """
        Get profile for a format.
        
        Args:
            format_name: Format name to retrieve
        
        Returns:
            Result containing format profile
        """
        if format_name not in self._format_profiles:
            return Err(f"Unknown format: {format_name}")
        
        return Ok(self._format_profiles[format_name])
    
    def register_format(self, profile: FormatProfile) -> Result[str]:
        """
        Register a custom format profile.
        
        Args:
            profile: Format profile to register
        
        Returns:
            Result containing registration confirmation
        """
        self._format_profiles[profile.format_name] = profile
        return Ok(f"Format {profile.format_name} registered")
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported formats."""
        return list(self._format_profiles.keys())
    
    def get_migration_guide(self, from_format: str, to_format: str) -> Result[str]:
        """
        AC-AR-008-03: Get migration documentation.
        
        Args:
            from_format: Source format
            to_format: Target format
        
        Returns:
            Result containing migration guide
        """
        key = f"{from_format}->{to_format}"
        
        if key not in self._migration_guides:
            # Generate basic migration guide
            guide = self._generate_migration_guide(from_format, to_format)
            self._migration_guides[key] = guide
        
        return Ok(self._migration_guides[key])
    
    def _generate_migration_guide(self, from_format: str, to_format: str) -> str:
        """Generate migration guide between formats."""
        from_profile = self._format_profiles.get(from_format)
        to_profile = self._format_profiles.get(to_format)
        
        if not from_profile or not to_profile:
            return "Unable to generate guide for unknown formats"
        
        guide = f"""
# Migration Guide: {from_format} → {to_format}

## Overview
Migrating from {from_profile.description} to {to_profile.description}.

## Field Mappings
"""
        
        for mapping in from_profile.field_mappings:
            guide += f"- {mapping.legacy_field} → {mapping.new_field}\n"
        
        guide += f"""
## Required Fields
{', '.join(to_profile.required_fields)}

## Optional Fields
{', '.join(to_profile.optional_fields)}

## Migration Steps
1. Use compatibility layer's convert_format() method
2. Validate converted data with to_profile
3. Test compatibility with target system
4. Update system configuration if needed

## Backward Compatibility
This migration maintains backward compatibility through the compatibility layer.
Legacy data can still be processed using COMPATIBLE mode.
"""
        
        return guide
    
    def list_format_differences(
        self,
        format1: str,
        format2: str,
    ) -> Result[Dict[str, Any]]:
        """
        List differences between two formats.
        
        Args:
            format1: First format name
            format2: Second format name
        
        Returns:
            Result containing differences
        """
        if format1 not in self._format_profiles:
            return Err(f"Unknown format: {format1}")
        if format2 not in self._format_profiles:
            return Err(f"Unknown format: {format2}")
        
        profile1 = self._format_profiles[format1]
        profile2 = self._format_profiles[format2]
        
        # Get field names from both
        fields1 = {m.new_field for m in profile1.field_mappings}
        fields2 = {m.new_field for m in profile2.field_mappings}
        
        differences = {
            "only_in_format1": list(fields1 - fields2),
            "only_in_format2": list(fields2 - fields1),
            "common_fields": list(fields1 & fields2),
            "version_format1": profile1.version.value,
            "version_format2": profile2.version.value,
        }
        
        return Ok(differences)
    
    def set_mode(self, mode: CompatibilityMode) -> Result[str]:
        """
        Set compatibility mode.
        
        Args:
            mode: New compatibility mode
        
        Returns:
            Result with confirmation
        """
        self._mode = mode
        return Ok(f"Compatibility mode set to {mode.name}")
    
    def get_mode(self) -> CompatibilityMode:
        """Get current compatibility mode."""
        return self._mode
