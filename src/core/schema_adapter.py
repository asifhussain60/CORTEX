"""
Schema Adapter - Format Translation (AC-AR-008)

Handles schema adaptation and transformation:
- Audit log format follows established patterns (AC-AR-008-02)
- Schema validation and standardization
- Format versioning and migration
- Backward compatibility for audit data

Features:
- Audit log schema validation
- Hash chain verification
- Entry point standardization
- Metadata enrichment
- Legacy format support
- Schema evolution tracking

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Dict, Optional, List

from src.core.result import Result, Ok, Err


@dataclass
class AuditLogSchema:
    """Standard audit log schema."""
    audit_id: str                                  # Unique identifier
    created_at: str                               # ISO timestamp
    action_type: str                              # Type of action
    actor_id: Optional[str] = None                # Who performed action
    ac_id: Optional[str] = None                   # Associated AC
    phase_id: Optional[str] = None                # Associated Phase
    previous_hash: Optional[str] = None           # Hash chain
    status: str = "RECORDED"                      # Log status
    context_data: Dict[str, Any] = None          # Additional context
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class LegacyAuditLogSchema:
    """Legacy audit log schema (V1)."""
    log_id: str
    entry_time: str
    action: str
    actor: Optional[str] = None
    ac_ref: Optional[str] = None
    phase_ref: Optional[str] = None
    hash_chain: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class SchemaAdapter:
    """
    Adapts and validates schemas.
    
    Provides:
    - Audit log schema validation
    - Format normalization
    - Hash chain verification
    - Legacy format support
    - Schema standardization
    """
    
    def __init__(self):
        """Initialize schema adapter."""
        self._version_map = {
            "v1": "legacy",
            "v2": "current",
        }
    
    def validate_audit_log(
        self,
        log_data: Dict[str, Any],
    ) -> Result[AuditLogSchema]:
        """
        AC-AR-008-02: Validate audit log against schema.
        
        Args:
            log_data: Audit log data to validate
        
        Returns:
            Result containing validated schema
        """
        # Check required fields
        required = ["audit_id", "created_at", "action_type"]
        
        for field in required:
            if field not in log_data:
                return Err(f"Missing required field: {field}")
        
        try:
            # Validate timestamp format
            created_at = log_data["created_at"]
            if isinstance(created_at, str):
                datetime.fromisoformat(created_at)
            
            # Create schema object
            schema = AuditLogSchema(
                audit_id=str(log_data["audit_id"]),
                created_at=created_at if isinstance(created_at, str) 
                          else created_at.isoformat(),
                action_type=str(log_data["action_type"]),
                actor_id=log_data.get("actor_id"),
                ac_id=log_data.get("ac_id"),
                phase_id=log_data.get("phase_id"),
                previous_hash=log_data.get("previous_hash"),
                status=log_data.get("status", "RECORDED"),
                context_data=log_data.get("context_data"),
            )
            
            return Ok(schema)
        
        except (ValueError, TypeError) as e:
            return Err(f"Schema validation failed: {str(e)}")
    
    def validate_legacy_audit_log(
        self,
        log_data: Dict[str, Any],
    ) -> Result[LegacyAuditLogSchema]:
        """
        AC-AR-008-02: Validate legacy audit log format.
        
        Args:
            log_data: Legacy audit log data
        
        Returns:
            Result containing validated legacy schema
        """
        required = ["log_id", "entry_time", "action"]
        
        for field in required:
            if field not in log_data:
                return Err(f"Missing required field: {field}")
        
        try:
            # Validate timestamp
            entry_time = log_data["entry_time"]
            if isinstance(entry_time, str):
                datetime.fromisoformat(entry_time)
            
            schema = LegacyAuditLogSchema(
                log_id=str(log_data["log_id"]),
                entry_time=entry_time if isinstance(entry_time, str)
                          else entry_time.isoformat(),
                action=str(log_data["action"]),
                actor=log_data.get("actor"),
                ac_ref=log_data.get("ac_ref"),
                phase_ref=log_data.get("phase_ref"),
                hash_chain=log_data.get("hash_chain"),
                metadata=log_data.get("metadata"),
            )
            
            return Ok(schema)
        
        except (ValueError, TypeError) as e:
            return Err(f"Legacy schema validation failed: {str(e)}")
    
    def convert_legacy_to_current(
        self,
        legacy_log: LegacyAuditLogSchema,
    ) -> Result[AuditLogSchema]:
        """
        AC-AR-008-02: Convert legacy log to current schema.
        
        Args:
            legacy_log: Legacy audit log
        
        Returns:
            Result containing converted schema
        """
        # Map fields
        current = AuditLogSchema(
            audit_id=legacy_log.log_id,
            created_at=legacy_log.entry_time,
            action_type=legacy_log.action,
            actor_id=legacy_log.actor,
            ac_id=legacy_log.ac_ref,
            phase_id=legacy_log.phase_ref,
            previous_hash=legacy_log.hash_chain,
            status="MIGRATED",
            context_data=legacy_log.metadata or {},
        )
        
        return Ok(current)
    
    def convert_current_to_legacy(
        self,
        current_log: AuditLogSchema,
    ) -> Result[LegacyAuditLogSchema]:
        """
        Convert current schema to legacy format.
        
        Args:
            current_log: Current audit log
        
        Returns:
            Result containing converted legacy schema
        """
        legacy = LegacyAuditLogSchema(
            log_id=current_log.audit_id,
            entry_time=current_log.created_at,
            action=current_log.action_type,
            actor=current_log.actor_id,
            ac_ref=current_log.ac_id,
            phase_ref=current_log.phase_id,
            hash_chain=current_log.previous_hash,
            metadata=current_log.context_data,
        )
        
        return Ok(legacy)
    
    def verify_hash_chain(
        self,
        current_log: AuditLogSchema,
        previous_hash: Optional[str] = None,
    ) -> Result[bool]:
        """
        AC-AR-008-02: Verify audit log hash chain.
        
        Args:
            current_log: Current audit log
            previous_hash: Expected previous hash
        
        Returns:
            Result indicating if hash chain is valid
        """
        if current_log.previous_hash is None:
            # First entry in chain - always valid
            return Ok(True)
        
        if previous_hash is None:
            return Err("Previous hash required for verification")
        
        if current_log.previous_hash != previous_hash:
            return Err(f"Hash chain broken: expected {previous_hash}, "
                      f"got {current_log.previous_hash}")
        
        return Ok(True)
    
    def normalize_timestamps(
        self,
        log_data: Dict[str, Any],
    ) -> Result[Dict[str, Any]]:
        """
        Normalize timestamps to ISO format.
        
        Args:
            log_data: Log data with timestamps
        
        Returns:
            Result containing normalized data
        """
        normalized = log_data.copy()
        
        timestamp_fields = [
            "created_at",
            "entry_time",
            "timestamp",
            "created",
        ]
        
        for field in timestamp_fields:
            if field in normalized:
                try:
                    ts = normalized[field]
                    if isinstance(ts, str):
                        # Verify it's valid ISO format
                        datetime.fromisoformat(ts)
                    elif isinstance(ts, (int, float)):
                        # Convert from epoch
                        normalized[field] = datetime.fromtimestamp(
                            ts,
                            tz=timezone.utc
                        ).isoformat()
                    elif isinstance(ts, datetime):
                        normalized[field] = ts.isoformat()
                except (ValueError, TypeError) as e:
                    return Err(f"Failed to normalize timestamp {field}: {str(e)}")
        
        return Ok(normalized)
    
    def enrich_context(
        self,
        log: AuditLogSchema,
        additional_context: Optional[Dict[str, Any]] = None,
    ) -> Result[AuditLogSchema]:
        """
        AC-AR-008-02: Enrich audit log with context.
        
        Args:
            log: Audit log to enrich
            additional_context: Context to add
        
        Returns:
            Result containing enriched log
        """
        if log.context_data is None:
            log.context_data = {}
        
        if additional_context:
            log.context_data.update(additional_context)
        
        # Add timestamp if not present
        if "enriched_at" not in log.context_data:
            log.context_data["enriched_at"] = datetime.now(timezone.utc).isoformat()
        
        return Ok(log)
    
    def validate_schema_compatibility(
        self,
        log_data: Dict[str, Any],
        required_version: str = "v2",
    ) -> Result[bool]:
        """
        Validate log is compatible with required schema version.
        
        Args:
            log_data: Log data to validate
            required_version: Required version (v1 or v2)
        
        Returns:
            Result indicating compatibility
        """
        if required_version == "v1":
            # Try legacy schema
            result = self.validate_legacy_audit_log(log_data)
        elif required_version == "v2":
            # Try current schema
            result = self.validate_audit_log(log_data)
        else:
            return Err(f"Unknown version: {required_version}")
        
        if result.is_ok():
            return Ok(True)
        else:
            return Err(f"Not compatible with {required_version}: {result.unwrap_err()}")
    
    def get_schema_version(self, log_data: Dict[str, Any]) -> Result[str]:
        """
        Detect schema version of log data.
        
        Args:
            log_data: Log data to analyze
        
        Returns:
            Result containing detected version
        """
        # Try current schema first
        if self.validate_audit_log(log_data).is_ok():
            return Ok("v2")
        
        # Try legacy schema
        if self.validate_legacy_audit_log(log_data).is_ok():
            return Ok("v1")
        
        return Err("Unknown schema version")
    
    def standardize_log(
        self,
        log_data: Dict[str, Any],
    ) -> Result[AuditLogSchema]:
        """
        Standardize log to current schema.
        
        Args:
            log_data: Log data (any version)
        
        Returns:
            Result containing standardized log
        """
        # Try current schema
        result = self.validate_audit_log(log_data)
        if result.is_ok():
            return result
        
        # Try legacy schema and convert
        legacy_result = self.validate_legacy_audit_log(log_data)
        if legacy_result.is_ok():
            legacy_log = legacy_result.unwrap()
            return self.convert_legacy_to_current(legacy_log)
        
        return Err("Unable to standardize log data")
    
    def batch_standardize_logs(
        self,
        logs: List[Dict[str, Any]],
    ) -> Result[List[AuditLogSchema]]:
        """
        Standardize batch of logs.
        
        Args:
            logs: List of log data
        
        Returns:
            Result containing list of standardized logs
        """
        standardized = []
        
        for i, log_data in enumerate(logs):
            result = self.standardize_log(log_data)
            if result.is_err():
                return Err(f"Failed to standardize log {i}: {result.unwrap_err()}")
            standardized.append(result.unwrap())
        
        return Ok(standardized)
