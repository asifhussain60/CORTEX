"""
Compatibility Tests - TDD for AC-AR-008

Tests for:
- AC-AR-008-01: Evidence bundle schema compatible with established patterns
- AC-AR-008-02: Audit log format follows established patterns
- AC-AR-008-03: Migration path documented for existing users

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
from src.core.compatibility_layer import (
    CompatibilityLayer,
    CompatibilityMode,
    SchemaVersion,
)
from src.core.schema_adapter import (
    SchemaAdapter,
    AuditLogSchema,
    LegacyAuditLogSchema,
)


class TestFormatDetection:
    """Test AC-AR-008-01: Format detection"""
    
    def test_detect_evidence_bundle_v1(self):
        """Should detect legacy evidence bundle format."""
        layer = CompatibilityLayer()
        
        data = {
            "bundle_id": "B-001",
            "timestamp": "2026-01-14T20:00:00+00:00",
            "artifacts": ["artifact1", "artifact2"],
        }
        
        result = layer.detect_format(data)
        
        assert result.is_ok()
        format_name, version = result.unwrap()
        assert format_name == "evidence_bundle_v1"
        assert version == SchemaVersion.V1_LEGACY
    
    def test_detect_evidence_bundle_v2(self):
        """Should detect current evidence bundle format."""
        layer = CompatibilityLayer()
        
        data = {
            "checkpoint_id": "CKP-001",
            "created_at": "2026-01-14T20:00:00+00:00",
            "state_snapshot": {"value": "data"},
        }
        
        result = layer.detect_format(data)
        
        assert result.is_ok()
        format_name, version = result.unwrap()
        assert format_name == "evidence_bundle_v2"
        assert version == SchemaVersion.V2_CURRENT
    
    def test_detect_audit_log_v1(self):
        """Should detect legacy audit log format."""
        layer = CompatibilityLayer()
        
        data = {
            "log_id": "L-001",
            "entry_time": "2026-01-14T20:00:00+00:00",
            "action": "CREATE",
        }
        
        result = layer.detect_format(data)
        
        assert result.is_ok()
        format_name, version = result.unwrap()
        assert format_name == "audit_log_v1"
        assert version == SchemaVersion.V1_LEGACY
    
    def test_detect_audit_log_v2(self):
        """Should detect current audit log format."""
        layer = CompatibilityLayer()
        
        data = {
            "audit_id": "A-001",
            "created_at": "2026-01-14T20:00:00+00:00",
            "action_type": "CREATE",
        }
        
        result = layer.detect_format(data)
        
        assert result.is_ok()
        format_name, version = result.unwrap()
        assert format_name == "audit_log_v2"
        assert version == SchemaVersion.V2_CURRENT
    
    def test_detect_unknown_format(self):
        """Should return error for unknown format."""
        layer = CompatibilityLayer()
        
        data = {"unknown": "field"}
        
        result = layer.detect_format(data)
        
        assert result.is_err()


class TestSchemaValidation:
    """Test AC-AR-008-01: Schema validation"""
    
    def test_validate_evidence_bundle_v2_valid(self):
        """Should validate correct evidence bundle v2."""
        layer = CompatibilityLayer()
        
        data = {
            "checkpoint_id": "CKP-001",
            "created_at": "2026-01-14T20:00:00+00:00",
            "state_snapshot": {"data": "value"},
        }
        
        result = layer.validate_schema(data, "evidence_bundle_v2")
        
        assert result.is_ok()
        assert result.unwrap() is True
    
    def test_validate_evidence_bundle_v2_missing_required(self):
        """Should reject evidence bundle v2 with missing required fields."""
        layer = CompatibilityLayer()
        
        data = {
            "checkpoint_id": "CKP-001",
            # Missing created_at
            "state_snapshot": {"data": "value"},
        }
        
        result = layer.validate_schema(data, "evidence_bundle_v2")
        
        assert result.is_err()
    
    def test_validate_audit_log_v2_valid(self):
        """Should validate correct audit log v2."""
        layer = CompatibilityLayer()
        
        data = {
            "audit_id": "A-001",
            "created_at": "2026-01-14T20:00:00+00:00",
            "action_type": "CREATE",
        }
        
        result = layer.validate_schema(data, "audit_log_v2")
        
        assert result.is_ok()
    
    def test_validate_strict_mode_rejects_extra_fields(self):
        """Should reject extra fields in STRICT mode."""
        layer = CompatibilityLayer(mode=CompatibilityMode.STRICT)
        
        data = {
            "audit_id": "A-001",
            "created_at": "2026-01-14T20:00:00+00:00",
            "action_type": "CREATE",
            "unknown_field": "value",
        }
        
        result = layer.validate_schema(data, "audit_log_v2")
        
        assert result.is_err()
    
    def test_validate_compatible_mode_allows_extra_fields(self):
        """Should allow extra fields in COMPATIBLE mode."""
        layer = CompatibilityLayer(mode=CompatibilityMode.COMPATIBLE)
        
        data = {
            "audit_id": "A-001",
            "created_at": "2026-01-14T20:00:00+00:00",
            "action_type": "CREATE",
            "extra_field": "value",
        }
        
        result = layer.validate_schema(data, "audit_log_v2")
        
        assert result.is_ok()


class TestFormatConversion:
    """Test AC-AR-008-01: Format conversion"""
    
    def test_convert_evidence_bundle_v1_to_v2(self):
        """Should convert evidence bundle v1 to v2."""
        layer = CompatibilityLayer()
        
        v1_data = {
            "bundle_id": "B-001",
            "timestamp": "2026-01-14T20:00:00+00:00",
            "artifacts": ["art1", "art2"],
            "ac_ref": "AC-TEST-001",
        }
        
        result = layer.convert_format(v1_data, "evidence_bundle_v1", "evidence_bundle_v2")
        
        assert result.is_ok()
        v2_data = result.unwrap()
        assert v2_data["checkpoint_id"] == "B-001"
        assert v2_data["created_at"] == "2026-01-14T20:00:00+00:00"
        assert v2_data["ac_id"] == "AC-TEST-001"
    
    def test_convert_audit_log_v1_to_v2(self):
        """Should convert audit log v1 to v2."""
        layer = CompatibilityLayer()
        
        v1_data = {
            "log_id": "L-001",
            "entry_time": "2026-01-14T20:00:00+00:00",
            "action": "CREATE",
            "actor": "USER-01",
            "ac_ref": "AC-TEST-001",
        }
        
        result = layer.convert_format(v1_data, "audit_log_v1", "audit_log_v2")
        
        assert result.is_ok()
        v2_data = result.unwrap()
        assert v2_data["audit_id"] == "L-001"
        assert v2_data["created_at"] == "2026-01-14T20:00:00+00:00"
        assert v2_data["action_type"] == "CREATE"
        assert v2_data["actor_id"] == "USER-01"


class TestAuditLogSchema:
    """Test AC-AR-008-02: Audit log schema validation"""
    
    def test_validate_audit_log_v2_schema(self):
        """Should validate current audit log schema."""
        adapter = SchemaAdapter()
        
        log_data = {
            "audit_id": "A-001",
            "created_at": "2026-01-14T20:00:00+00:00",
            "action_type": "CREATE",
            "actor_id": "USER-01",
            "ac_id": "AC-TEST-001",
        }
        
        result = adapter.validate_audit_log(log_data)
        
        assert result.is_ok()
        schema = result.unwrap()
        assert schema.audit_id == "A-001"
        assert schema.action_type == "CREATE"
    
    def test_validate_legacy_audit_log_schema(self):
        """Should validate legacy audit log schema."""
        adapter = SchemaAdapter()
        
        log_data = {
            "log_id": "L-001",
            "entry_time": "2026-01-14T20:00:00+00:00",
            "action": "CREATE",
            "actor": "USER-01",
        }
        
        result = adapter.validate_legacy_audit_log(log_data)
        
        assert result.is_ok()
        schema = result.unwrap()
        assert schema.log_id == "L-001"
        assert schema.action == "CREATE"
    
    def test_validate_audit_log_missing_required(self):
        """Should reject log missing required field."""
        adapter = SchemaAdapter()
        
        log_data = {
            "audit_id": "A-001",
            # Missing created_at
            "action_type": "CREATE",
        }
        
        result = adapter.validate_audit_log(log_data)
        
        assert result.is_err()


class TestSchemaConversion:
    """Test AC-AR-008-02: Schema conversion"""
    
    def test_convert_legacy_to_current_audit_log(self):
        """Should convert legacy audit log to current schema."""
        adapter = SchemaAdapter()
        
        # Create legacy schema
        legacy = LegacyAuditLogSchema(
            log_id="L-001",
            entry_time="2026-01-14T20:00:00+00:00",
            action="CREATE",
            actor="USER-01",
            ac_ref="AC-TEST-001",
        )
        
        result = adapter.convert_legacy_to_current(legacy)
        
        assert result.is_ok()
        current = result.unwrap()
        assert current.audit_id == "L-001"
        assert current.created_at == "2026-01-14T20:00:00+00:00"
        assert current.action_type == "CREATE"
        assert current.actor_id == "USER-01"
        assert current.ac_id == "AC-TEST-001"
    
    def test_convert_current_to_legacy_audit_log(self):
        """Should convert current audit log to legacy schema."""
        adapter = SchemaAdapter()
        
        # Create current schema
        current = AuditLogSchema(
            audit_id="A-001",
            created_at="2026-01-14T20:00:00+00:00",
            action_type="CREATE",
            actor_id="USER-01",
            ac_id="AC-TEST-001",
        )
        
        result = adapter.convert_current_to_legacy(current)
        
        assert result.is_ok()
        legacy = result.unwrap()
        assert legacy.log_id == "A-001"
        assert legacy.entry_time == "2026-01-14T20:00:00+00:00"
        assert legacy.action == "CREATE"


class TestHashChainVerification:
    """Test AC-AR-008-02: Hash chain verification"""
    
    def test_verify_hash_chain_valid(self):
        """Should verify valid hash chain."""
        adapter = SchemaAdapter()
        
        log = AuditLogSchema(
            audit_id="A-001",
            created_at="2026-01-14T20:00:00+00:00",
            action_type="CREATE",
            previous_hash="abc123",
        )
        
        result = adapter.verify_hash_chain(log, previous_hash="abc123")
        
        assert result.is_ok()
        assert result.unwrap() is True
    
    def test_verify_hash_chain_mismatch(self):
        """Should reject mismatched hash chain."""
        adapter = SchemaAdapter()
        
        log = AuditLogSchema(
            audit_id="A-001",
            created_at="2026-01-14T20:00:00+00:00",
            action_type="CREATE",
            previous_hash="abc123",
        )
        
        result = adapter.verify_hash_chain(log, previous_hash="xyz789")
        
        assert result.is_err()
    
    def test_verify_hash_chain_first_entry(self):
        """Should accept first entry without hash."""
        adapter = SchemaAdapter()
        
        log = AuditLogSchema(
            audit_id="A-001",
            created_at="2026-01-14T20:00:00+00:00",
            action_type="CREATE",
            previous_hash=None,
        )
        
        result = adapter.verify_hash_chain(log)
        
        assert result.is_ok()


class TestTimestampNormalization:
    """Test timestamp normalization"""
    
    def test_normalize_iso_timestamp(self):
        """Should keep valid ISO timestamps."""
        adapter = SchemaAdapter()
        
        data = {
            "created_at": "2026-01-14T20:00:00+00:00",
            "action": "CREATE",
        }
        
        result = adapter.normalize_timestamps(data)
        
        assert result.is_ok()
        normalized = result.unwrap()
        assert normalized["created_at"] == "2026-01-14T20:00:00+00:00"
    
    def test_normalize_epoch_timestamp(self):
        """Should convert epoch timestamps to ISO."""
        adapter = SchemaAdapter()
        
        data = {
            "entry_time": 1673740800.0,  # 2023-01-15 00:00:00 UTC
            "action": "CREATE",
        }
        
        result = adapter.normalize_timestamps(data)
        
        assert result.is_ok()
        normalized = result.unwrap()
        assert "T" in normalized["entry_time"]  # ISO format has T


class TestMigrationGuide:
    """Test AC-AR-008-03: Migration documentation"""
    
    def test_get_migration_guide_v1_to_v2(self):
        """Should provide migration guide."""
        layer = CompatibilityLayer()
        
        result = layer.get_migration_guide("audit_log_v1", "audit_log_v2")
        
        assert result.is_ok()
        guide = result.unwrap()
        assert "Migration Guide" in guide
        assert "audit_log_v1" in guide
        assert "audit_log_v2" in guide
    
    def test_migration_guide_contains_field_mappings(self):
        """Migration guide should contain field mappings."""
        layer = CompatibilityLayer()
        
        result = layer.get_migration_guide("evidence_bundle_v1", "evidence_bundle_v2")
        
        assert result.is_ok()
        guide = result.unwrap()
        assert "Field Mappings" in guide
    
    def test_migration_guide_contains_steps(self):
        """Migration guide should contain migration steps."""
        layer = CompatibilityLayer()
        
        result = layer.get_migration_guide("audit_log_v1", "audit_log_v2")
        
        assert result.is_ok()
        guide = result.unwrap()
        assert "Migration Steps" in guide


class TestFormatDifferences:
    """Test format difference analysis"""
    
    def test_list_format_differences(self):
        """Should list differences between formats."""
        layer = CompatibilityLayer()
        
        result = layer.list_format_differences("audit_log_v1", "audit_log_v2")
        
        assert result.is_ok()
        differences = result.unwrap()
        assert "common_fields" in differences
        assert "version_format1" in differences
        assert "version_format2" in differences


class TestCompatibilityIntegration:
    """Integration tests for compatibility"""
    
    def test_complete_compatibility_workflow(self):
        """Should handle complete compatibility workflow."""
        layer = CompatibilityLayer(mode=CompatibilityMode.COMPATIBLE)
        
        # Detect format
        v1_data = {
            "log_id": "L-001",
            "entry_time": "2026-01-14T20:00:00+00:00",
            "action": "CREATE",
        }
        
        detect_result = layer.detect_format(v1_data)
        assert detect_result.is_ok()
        
        # Validate against schema
        validate_result = layer.validate_schema(v1_data, "audit_log_v1")
        assert validate_result.is_ok()
        
        # Convert to new format
        convert_result = layer.convert_format(
            v1_data,
            "audit_log_v1",
            "audit_log_v2",
        )
        assert convert_result.is_ok()
        
        v2_data = convert_result.unwrap()
        
        # Validate new format
        validate_v2 = layer.validate_schema(v2_data, "audit_log_v2")
        assert validate_v2.is_ok()
    
    def test_schema_adapter_standardization(self):
        """Should standardize logs to current schema."""
        adapter = SchemaAdapter()
        
        v1_log = {
            "log_id": "L-001",
            "entry_time": "2026-01-14T20:00:00+00:00",
            "action": "CREATE",
        }
        
        result = adapter.standardize_log(v1_log)
        
        assert result.is_ok()
        standardized = result.unwrap()
        assert standardized.audit_id == "L-001"
        assert standardized.action_type == "CREATE"
    
    def test_batch_standardize_logs(self):
        """Should batch standardize logs."""
        adapter = SchemaAdapter()
        
        logs = [
            {
                "log_id": "L-001",
                "entry_time": "2026-01-14T20:00:00+00:00",
                "action": "CREATE",
            },
            {
                "log_id": "L-002",
                "entry_time": "2026-01-14T20:00:01+00:00",
                "action": "UPDATE",
            },
        ]
        
        result = adapter.batch_standardize_logs(logs)
        
        assert result.is_ok()
        standardized = result.unwrap()
        assert len(standardized) == 2
        assert standardized[0].audit_id == "L-001"
        assert standardized[1].audit_id == "L-002"
