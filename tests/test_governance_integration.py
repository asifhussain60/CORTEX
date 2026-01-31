"""
Integration test suite for Governance system.

Purpose:
    Test full system integration including database, registry, and audit logging.

Coverage:
    - Database + Registry integration
    - Audit logging + Database
    - Multi-operation workflows
    - Data consistency across components
    - Error handling and recovery

Author: Asif Hussain
Version: 1.0
"""

import pytest
import tempfile
from pathlib import Path
from cortex.orchestrators.core.governance_registry import GovernanceRegistry
from cortex.brain.core.governance_database import GovernanceDatabaseManager
from cortex.brain.core.governance_audit_logger import EnhancedGovernanceAuditLogger


class TestDatabaseAndRegistry:
    """Test database and registry working together."""

    def test_registry_initialization_with_tier0(self) -> None:
        """Test that registry properly initializes with Tier 0."""
        registry = GovernanceRegistry()
        result = registry.initialize()
        
        # Should succeed
        assert result is not None
        
        # Tier 0 should be populated
        all_rules = registry.get_all_rules()
        assert len(all_rules["tier0"]) > 0

    def test_database_and_registry_separate_instances(self) -> None:
        """Test database and registry can operate as separate instances."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            
            # Database instance
            mgr = GovernanceDatabaseManager(db_path=db_path)
            mgr.initialize()
            
            # Create a rule
            mgr.create_project_rule(
                rule_id="INT-001",
                name="Integration Test Rule",
                category="test",
                severity="info",
                description="Integration test",
                enforcement_point="test",
                audit_event="TEST",
                created_by="test_user",
            )
            
            # Registry instance (independent)
            registry = GovernanceRegistry()
            registry.initialize()
            
            # Both should work independently
            all_rules = registry.get_all_rules()
            assert len(all_rules["tier0"]) > 0
            
            mgr.close()

    def test_rule_creation_and_retrieval_cycle(self) -> None:
        """Test complete create-read-update cycle in database."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            mgr = GovernanceDatabaseManager(db_path=db_path)
            mgr.initialize()
            
            # Create
            mgr.create_project_rule(
                rule_id="CYCLE-001",
                name="Cycle Test Rule",
                category="security",
                severity="blocked",
                description="Test cycle",
                enforcement_point="test",
                audit_event="TEST",
                created_by="test_user",
            )
            
            # Read
            rule = mgr.get_rule("CYCLE-001")
            assert rule is not None
            assert rule.rule_id == "CYCLE-001"
            
            # Update using rule_id and kwargs
            mgr.update_rule("CYCLE-001", updated_by="test_user", name="Updated Cycle Rule")
            
            # Verify update
            updated_rule = mgr.get_rule("CYCLE-001")
            assert updated_rule is not None
            assert updated_rule.name == "Updated Cycle Rule"
            
            mgr.close()


class TestAuditLogging:
    """Test audit logging functionality."""

    def test_audit_logger_creation(self) -> None:
        """Test audit logger can be created."""
        logger = EnhancedGovernanceAuditLogger()
        assert logger is not None


class TestMultiComponentWorkflow:
    """Test workflows involving multiple components."""

    def test_database_registry_workflow(self) -> None:
        """Test workflow: create rule in DB, verify in registry."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            
            # Setup
            mgr = GovernanceDatabaseManager(db_path=db_path)
            mgr.initialize()
            registry = GovernanceRegistry()
            registry.initialize()
            
            # Create in database
            mgr.create_project_rule(
                rule_id="WORK-001",
                name="Workflow Test",
                category="test",
                severity="info",
                description="Workflow",
                enforcement_point="test",
                audit_event="TEST",
                created_by="test_user",
            )
            
            # Registry should still have Tier 0
            all_rules = registry.get_all_rules()
            assert len(all_rules["tier0"]) > 0
            
            # Database should have the rule
            rule = mgr.get_rule("WORK-001")
            assert rule is not None
            
            mgr.close()

    def test_database_consistency_across_operations(self) -> None:
        """Test database maintains consistency across multiple operations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            mgr = GovernanceDatabaseManager(db_path=db_path)
            mgr.initialize()
            
            # Create multiple rules
            for i in range(5):
                mgr.create_project_rule(
                    rule_id=f"CONS-{i:03d}",
                    name=f"Consistency Test {i}",
                    category="test",
                    severity="info",
                    description=f"Test {i}",
                    enforcement_point="test",
                    audit_event="TEST",
                    created_by="test_user",
                )
            
            # List all
            rules = mgr.list_rules()
            assert len(rules) >= 5
            
            # Update one
            rule_to_update = rules[0]
            mgr.update_rule(rule_to_update.rule_id, updated_by="test_user", name="Updated Rule")
            
            # Verify still 5 rules
            rules_after = mgr.list_rules()
            assert len(rules_after) >= 5
            
            mgr.close()


class TestDataConsistency:
    """Test data consistency guarantees."""

    def test_registry_tier0_immutability(self) -> None:
        """Test that registry maintains Tier 0 immutability."""
        registry1 = GovernanceRegistry()
        registry1.initialize()
        rules1 = registry1.get_all_rules()
        tier0_1 = rules1["tier0"]
        
        registry2 = GovernanceRegistry()
        registry2.initialize()
        rules2 = registry2.get_all_rules()
        tier0_2 = rules2["tier0"]
        
        # Same size
        assert len(tier0_1) == len(tier0_2)
        
        # Same IDs
        ids1 = set()
        ids2 = set()
        for r in tier0_1:
            ids1.add(r.rule_id)
        for r in tier0_2:
            ids2.add(r.rule_id)
        assert ids1 == ids2

    def test_database_transaction_consistency(self) -> None:
        """Test database transactions maintain consistency."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            mgr = GovernanceDatabaseManager(db_path=db_path)
            mgr.initialize()
            
            # Create rule
            mgr.create_project_rule(
                rule_id="TRANS-001",
                name="Transaction Test",
                category="test",
                severity="info",
                description="Transaction",
                enforcement_point="test",
                audit_event="TEST",
                created_by="test_user",
            )
            
            # Verify creation
            rule1 = mgr.get_rule("TRANS-001")
            assert rule1 is not None
            
            # Update
            mgr.update_rule("TRANS-001", updated_by="test_user", name="Updated Transaction Test")
            
            # Verify update persists
            rule2 = mgr.get_rule("TRANS-001")
            assert rule2 is not None
            assert rule2.name == "Updated Transaction Test"
            
            mgr.close()


class TestErrorHandling:
    """Test error handling in integrated scenarios."""

    def test_get_nonexistent_rule_returns_none(self) -> None:
        """Test getting nonexistent rule returns None."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            mgr = GovernanceDatabaseManager(db_path=db_path)
            mgr.initialize()
            
            # Try to get nonexistent rule
            rule = mgr.get_rule("NONEXISTENT-001")
            assert rule is None
            
            mgr.close()

    def test_create_duplicate_rule_fails(self) -> None:
        """Test creating duplicate rule raises exception."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            mgr = GovernanceDatabaseManager(db_path=db_path)
            mgr.initialize()
            
            # Create rule
            mgr.create_project_rule(
                rule_id="DUP-001",
                name="Duplicate Test",
                category="test",
                severity="info",
                description="Test",
                enforcement_point="test",
                audit_event="TEST",
                created_by="test_user",
            )
            
            # Try to create duplicate - should raise IntegrityError
            import sqlite3
            try:
                mgr.create_project_rule(
                    rule_id="DUP-001",
                    name="Duplicate Attempt",
                    category="test",
                    severity="info",
                    description="Test",
                    enforcement_point="test",
                    audit_event="TEST",
                    created_by="test_user",
                )
                # If we get here, test fails
                assert False, "Should have raised IntegrityError"
            except sqlite3.IntegrityError:
                # Expected behavior
                pass
            
            mgr.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
