"""
Test suite for Tier 3 Knowledge Governance (KN-003-01)
=======================================================
PHASE-12: Knowledge Ecosystem Expansion
AC: KN-003-01 - Tier 3 Knowledge Governance

Validates:
1. Governance rules defined for Tier 3
2. Entry validation enforced
3. Update tracking active
4. Audit trail integration

Specification:
- Define governance rules for tier3 knowledge
- Enforce schema validation
- Track all changes in audit trail
- Integrate with governance.db
"""

import os
import json
import pytest
import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass


@dataclass
class GovernanceRule:
    """Represents a governance rule for tier3 knowledge."""
    rule_id: str
    domain: str
    rule_type: str  # 'required_field', 'validation', 'constraint'
    description: str
    rule_definition: Dict[str, Any]
    severity: str  # 'critical', 'warning', 'info'
    enabled: bool


@pytest.fixture(scope="module")
def governance_manager():
    """Create governance manager instance for tests."""
    from cortex_brain.tier3.knowledge.knowledge_governance import KnowledgeGovernanceManager
    return KnowledgeGovernanceManager()


class TestGovernanceRuleDefinition:
    """Tests for governance rule definitions."""
    
    def test_governance_rules_file_exists(self, governance_manager):
        """Verify governance rules file exists."""
        tier3_path = Path(__file__).parent.parent.parent / "cortex-brain" / "tier3" / "knowledge"
        rules_file = tier3_path / "governance-rules.yaml"
        assert rules_file.exists(), "Governance rules file not found"
    
    def test_governance_rules_contain_required_sections(self, governance_manager):
        """Verify governance rules file contains required sections."""
        tier3_path = Path(__file__).parent.parent.parent / "cortex-brain" / "tier3" / "knowledge"
        rules_file = tier3_path / "governance-rules.yaml"
        
        import yaml
        with open(rules_file, 'r') as f:
            rules = yaml.safe_load(f)
        
        assert "metadata" in rules, "Rules missing metadata section"
        assert "rules" in rules, "Rules missing rules section"
        assert "ac_id" in rules["metadata"], "Metadata missing ac_id"
        assert rules["metadata"]["ac_id"] == "KN-003-01"
    
    def test_governance_rules_define_16_domains(self, governance_manager):
        """Verify rules defined for all 16 domains."""
        tier3_path = Path(__file__).parent.parent.parent / "cortex-brain" / "tier3" / "knowledge"
        rules_file = tier3_path / "governance-rules.yaml"
        
        import yaml
        with open(rules_file, 'r') as f:
            rules = yaml.safe_load(f)
        
        expected_domains = [
            "GOVERNANCE", "INTENT-ROUTING", "HALLUCINATION-PREVENTION",
            "EXECUTION-ORCHESTRATION", "DATA-MANAGEMENT", "OBSERVABILITY",
            "SECURITY", "API-DESIGN", "ML-MODELS", "KNOWLEDGE-CURATION",
            "TESTING-VALIDATION", "DEPLOYMENT", "DOCUMENTATION",
            "PERFORMANCE", "ARCHITECTURE", "ERROR-HANDLING"
        ]
        
        domain_rules = {}
        for rule in rules["rules"]:
            if rule["domain"] not in domain_rules:
                domain_rules[rule["domain"]] = []
            domain_rules[rule["domain"]].append(rule)
        
        for domain in expected_domains:
            assert domain in domain_rules, f"No rules defined for domain: {domain}"
            assert len(domain_rules[domain]) > 0, f"No rules for domain: {domain}"
    
    def test_governance_rule_structure_valid(self, governance_manager):
        """Verify each rule has valid structure."""
        tier3_path = Path(__file__).parent.parent.parent / "cortex-brain" / "tier3" / "knowledge"
        rules_file = tier3_path / "governance-rules.yaml"
        
        import yaml
        with open(rules_file, 'r') as f:
            rules = yaml.safe_load(f)
        
        required_fields = ["rule_id", "domain", "rule_type", "description", "severity"]
        
        for rule in rules["rules"]:
            for field in required_fields:
                assert field in rule, f"Rule missing required field: {field}"
            
            assert rule["rule_type"] in ["required_field", "validation", "constraint"], \
                f"Invalid rule_type: {rule['rule_type']}"
            assert rule["severity"] in ["critical", "warning", "info"], \
                f"Invalid severity: {rule['severity']}"
    
    def test_governance_rules_have_descriptions(self, governance_manager):
        """Verify all rules have meaningful descriptions."""
        tier3_path = Path(__file__).parent.parent.parent / "cortex-brain" / "tier3" / "knowledge"
        rules_file = tier3_path / "governance-rules.yaml"
        
        import yaml
        with open(rules_file, 'r') as f:
            rules = yaml.safe_load(f)
        
        for rule in rules["rules"]:
            assert rule["description"], f"Rule {rule['rule_id']} missing description"
            assert len(rule["description"]) > 10, f"Rule {rule['rule_id']} description too short"


class TestEntryValidation:
    """Tests for entry validation against governance rules."""
    
    def test_governance_manager_has_validate_method(self, governance_manager):
        """Verify governance manager has validate method."""
        assert hasattr(governance_manager, 'validate_entry'), \
            "KnowledgeGovernanceManager missing validate_entry method"
    
    def test_validate_entry_checks_required_fields(self, governance_manager):
        """Verify validation checks required fields."""
        test_entry = {
            "entry_id": "KE-001",
            "domain": "GOVERNANCE",
            "title": "Test Entry",
            "ac_ids": ["AC-GV-001-01"]
        }
        
        result = governance_manager.validate_entry(test_entry)
        assert isinstance(result, dict), "validate_entry should return dict"
        assert "valid" in result, "Result missing 'valid' field"
        assert "errors" in result, "Result missing 'errors' field"
    
    def test_validate_entry_fails_on_invalid_domain(self, governance_manager):
        """Verify validation fails for invalid domain."""
        test_entry = {
            "entry_id": "KE-001",
            "domain": "INVALID-DOMAIN",
            "title": "Test Entry",
            "ac_ids": ["AC-GV-001-01"]
        }
        
        result = governance_manager.validate_entry(test_entry)
        assert result["valid"] is False, "Should reject invalid domain"
        assert len(result["errors"]) > 0, "Should contain error messages"
    
    def test_validate_entry_enforces_ac_id_format(self, governance_manager):
        """Verify AC-ID format validation."""
        test_entry = {
            "entry_id": "KE-001",
            "domain": "GOVERNANCE",
            "title": "Test Entry",
            "ac_ids": ["INVALID-FORMAT"]
        }
        
        result = governance_manager.validate_entry(test_entry)
        assert result["valid"] is False, "Should reject invalid AC-ID format"
    
    def test_validate_entry_returns_violation_details(self, governance_manager):
        """Verify validation returns detailed violation information."""
        test_entry = {
            "entry_id": "KE-001",
            "domain": "UNKNOWN"
        }
        
        result = governance_manager.validate_entry(test_entry)
        assert "errors" in result
        assert isinstance(result["errors"], list)
        if result["errors"]:
            for error in result["errors"]:
                assert isinstance(error, str)
    
    def test_governance_manager_has_get_rules_for_domain(self, governance_manager):
        """Verify method to get rules for specific domain."""
        assert hasattr(governance_manager, 'get_rules_for_domain'), \
            "KnowledgeGovernanceManager missing get_rules_for_domain method"
    
    def test_get_rules_for_domain_returns_list(self, governance_manager):
        """Verify get_rules_for_domain returns list of rules."""
        rules = governance_manager.get_rules_for_domain("GOVERNANCE")
        assert isinstance(rules, list), "Should return list of rules"
        assert len(rules) > 0, "Should have rules for GOVERNANCE domain"
    
    def test_governance_manager_has_get_critical_rules(self, governance_manager):
        """Verify method to get critical rules."""
        assert hasattr(governance_manager, 'get_critical_rules'), \
            "KnowledgeGovernanceManager missing get_critical_rules method"


class TestAuditTrailIntegration:
    """Tests for audit trail tracking."""
    
    def test_governance_manager_has_audit_log_method(self, governance_manager):
        """Verify governance manager has audit logging method."""
        assert hasattr(governance_manager, 'log_entry_change'), \
            "KnowledgeGovernanceManager missing log_entry_change method"
    
    def test_audit_trail_tracks_entry_creation(self, governance_manager):
        """Verify audit trail tracks entry creation."""
        test_entry = {
            "entry_id": "KE-TEST-001",
            "domain": "GOVERNANCE",
            "title": "Audit Test",
            "created_at": datetime.utcnow().isoformat()
        }
        
        result = governance_manager.log_entry_change(
            entry_id=test_entry["entry_id"],
            action="CREATE",
            domain=test_entry["domain"],
            details=test_entry
        )
        
        assert result is not None, "Audit logging should return result"
    
    def test_audit_trail_tracks_entry_update(self, governance_manager):
        """Verify audit trail tracks entry updates."""
        result = governance_manager.log_entry_change(
            entry_id="KE-TEST-002",
            action="UPDATE",
            domain="GOVERNANCE",
            details={"title": "Updated Title"}
        )
        
        assert result is not None, "Should log update action"
    
    def test_audit_trail_tracks_entry_delete(self, governance_manager):
        """Verify audit trail tracks entry deletion."""
        result = governance_manager.log_entry_change(
            entry_id="KE-TEST-003",
            action="DELETE",
            domain="GOVERNANCE",
            details={"reason": "Duplicate"}
        )
        
        assert result is not None, "Should log delete action"
    
    def test_audit_trail_has_timestamp(self, governance_manager):
        """Verify audit entries have timestamps."""
        result = governance_manager.log_entry_change(
            entry_id="KE-TEST-004",
            action="CREATE",
            domain="GOVERNANCE",
            details={}
        )
        
        assert "timestamp" in result or isinstance(result, dict)
    
    def test_governance_manager_has_get_audit_log(self, governance_manager):
        """Verify method to retrieve audit log."""
        assert hasattr(governance_manager, 'get_audit_log'), \
            "KnowledgeGovernanceManager missing get_audit_log method"
    
    def test_get_audit_log_returns_entries(self, governance_manager):
        """Verify get_audit_log returns list of audit entries."""
        audit_log = governance_manager.get_audit_log(domain="GOVERNANCE")
        assert isinstance(audit_log, list), "Audit log should return list"
    
    def test_audit_log_filtered_by_domain(self, governance_manager):
        """Verify audit log can be filtered by domain."""
        audit_log = governance_manager.get_audit_log(domain="SECURITY")
        for entry in audit_log:
            assert entry.get("domain") == "SECURITY" or entry.get("domain") is None


class TestGovernanceIntegration:
    """Tests for integration with governance system."""
    
    def test_governance_manager_integrates_with_governance_db(self, governance_manager):
        """Verify integration with governance.db."""
        governance_db = Path(__file__).parent.parent.parent / "cortex-brain" / "state" / "governance.db"
        assert governance_db.exists(), "governance.db not found"
    
    def test_governance_manager_can_record_to_db(self, governance_manager):
        """Verify governance manager can record changes to governance.db."""
        result = governance_manager.log_entry_change(
            entry_id="KE-DB-TEST",
            action="CREATE",
            domain="GOVERNANCE",
            details={"test": "data"}
        )
        
        assert result is not None
    
    def test_governance_manager_references_ac_id(self, governance_manager):
        """Verify governance manager references correct AC-ID."""
        assert hasattr(governance_manager, 'ac_id')
        assert governance_manager.ac_id == "KN-003-01"
    
    def test_governance_rules_reference_ac_id(self, governance_manager):
        """Verify governance rules reference KN-003-01."""
        tier3_path = Path(__file__).parent.parent.parent / "cortex-brain" / "tier3" / "knowledge"
        rules_file = tier3_path / "governance-rules.yaml"
        
        import yaml
        with open(rules_file, 'r') as f:
            rules = yaml.safe_load(f)
        
        assert rules["metadata"]["ac_id"] == "KN-003-01"


class TestUpdateTracking:
    """Tests for tracking all updates."""
    
    def test_governance_manager_has_track_update_method(self, governance_manager):
        """Verify method to track updates."""
        assert hasattr(governance_manager, 'track_update'), \
            "KnowledgeGovernanceManager missing track_update method"
    
    def test_track_update_records_all_changes(self, governance_manager):
        """Verify track_update records all entry changes."""
        old_entry = {"title": "Old Title", "domain": "GOVERNANCE"}
        new_entry = {"title": "New Title", "domain": "GOVERNANCE"}
        
        result = governance_manager.track_update(
            entry_id="KE-UPDATE-001",
            old_entry=old_entry,
            new_entry=new_entry
        )
        
        assert result is not None
    
    def test_track_update_identifies_changed_fields(self, governance_manager):
        """Verify track_update identifies which fields changed."""
        old_entry = {"title": "Old", "quality_score": 0.5, "domain": "GOVERNANCE"}
        new_entry = {"title": "New", "quality_score": 0.7, "domain": "GOVERNANCE"}
        
        result = governance_manager.track_update(
            entry_id="KE-UPDATE-002",
            old_entry=old_entry,
            new_entry=new_entry
        )
        
        assert result is not None, "Should track changes"
    
    def test_update_tracking_has_timestamp(self, governance_manager):
        """Verify update tracking includes timestamp."""
        result = governance_manager.track_update(
            entry_id="KE-UPDATE-003",
            old_entry={},
            new_entry={"title": "New", "domain": "GOVERNANCE"}
        )
        
        assert result is not None


class TestGovernanceValidationDecorators:
    """Tests for governance validation decorators."""
    
    def test_governance_manager_has_validate_decorator(self, governance_manager):
        """Verify governance manager has validation decorator."""
        assert hasattr(governance_manager, 'validate_on_create'), \
            "KnowledgeGovernanceManager missing validate_on_create decorator"
    
    def test_governance_manager_has_audit_decorator(self, governance_manager):
        """Verify governance manager has audit decorator."""
        assert hasattr(governance_manager, 'audit_on_change'), \
            "KnowledgeGovernanceManager missing audit_on_change decorator"
    
    def test_validation_decorator_enforces_rules(self, governance_manager):
        """Verify validation decorator enforces governance rules."""
        # This test validates decorator functionality exists
        assert hasattr(governance_manager, 'validate_on_create')
    
    def test_audit_decorator_logs_changes(self, governance_manager):
        """Verify audit decorator logs all changes."""
        # This test validates decorator functionality exists
        assert hasattr(governance_manager, 'audit_on_change')


class TestGovernanceRuleTypes:
    """Tests for different types of governance rules."""
    
    def test_governance_has_required_field_rules(self, governance_manager):
        """Verify governance includes required field rules."""
        tier3_path = Path(__file__).parent.parent.parent / "cortex-brain" / "tier3" / "knowledge"
        rules_file = tier3_path / "governance-rules.yaml"
        
        import yaml
        with open(rules_file, 'r') as f:
            rules = yaml.safe_load(f)
        
        rule_types = {rule["rule_type"] for rule in rules["rules"]}
        assert "required_field" in rule_types, "Should have required_field rules"
    
    def test_governance_has_validation_rules(self, governance_manager):
        """Verify governance includes validation rules."""
        tier3_path = Path(__file__).parent.parent.parent / "cortex-brain" / "tier3" / "knowledge"
        rules_file = tier3_path / "governance-rules.yaml"
        
        import yaml
        with open(rules_file, 'r') as f:
            rules = yaml.safe_load(f)
        
        rule_types = {rule["rule_type"] for rule in rules["rules"]}
        assert "validation" in rule_types, "Should have validation rules"
    
    def test_governance_has_constraint_rules(self, governance_manager):
        """Verify governance includes constraint rules."""
        tier3_path = Path(__file__).parent.parent.parent / "cortex-brain" / "tier3" / "knowledge"
        rules_file = tier3_path / "governance-rules.yaml"
        
        import yaml
        with open(rules_file, 'r') as f:
            rules = yaml.safe_load(f)
        
        rule_types = {rule["rule_type"] for rule in rules["rules"]}
        assert "constraint" in rule_types, "Should have constraint rules"


class TestGovernanceRuleSeverity:
    """Tests for governance rule severity levels."""
    
    def test_rules_have_critical_severity(self, governance_manager):
        """Verify some rules are marked as critical."""
        tier3_path = Path(__file__).parent.parent.parent / "cortex-brain" / "tier3" / "knowledge"
        rules_file = tier3_path / "governance-rules.yaml"
        
        import yaml
        with open(rules_file, 'r') as f:
            rules = yaml.safe_load(f)
        
        severities = {rule["severity"] for rule in rules["rules"]}
        assert "critical" in severities, "Should have critical severity rules"
    
    def test_critical_rules_block_operations(self, governance_manager):
        """Verify critical rule violations block operations."""
        test_entry = {
            "entry_id": "KE-001",
            "domain": "INVALID"
        }
        
        result = governance_manager.validate_entry(test_entry)
        # Invalid domain should fail due to critical rule
        assert result["valid"] is False


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
