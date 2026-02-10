"""
Edge cases and error handling test suite for Governance system.

Purpose:
    Test edge cases, boundary conditions, and error scenarios.

Coverage:
    - Empty database operations
    - Rule retrieval with special IDs
    - Concurrent access patterns
    - Invalid input handling
    - Boundary conditions
    - Recovery scenarios

Author: Asif Hussain
Version: 1.0
"""

import pytest
import tempfile
from pathlib import Path
from cortex.orchestrators.core.governance_registry import GovernanceRegistry
from cortex.brain.core.governance_database import GovernanceDatabaseManager


class TestEmptyDatabase:
    """Test operations on empty database."""

    def test_list_rules_on_empty_database(self) -> None:
        """Test listing rules on empty database."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            mgr = GovernanceDatabaseManager(db_path=db_path)
            mgr.initialize()
            
            # List should return empty
            rules = mgr.list_rules()
            assert len(rules) == 0
            
            mgr.close()

    def test_get_rule_on_empty_database(self) -> None:
        """Test getting rule on empty database."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            mgr = GovernanceDatabaseManager(db_path=db_path)
            mgr.initialize()
            
            # Get should return None
            rule = mgr.get_rule("NONEXISTENT")
            assert rule is None
            
            mgr.close()

    def test_registry_with_only_tier0(self) -> None:
        """Test registry with only Tier 0 (no database)."""
        registry = GovernanceRegistry()
        registry.initialize()
        
        all_rules = registry.get_all_rules()
        
        # Tier 0 should have rules
        assert len(all_rules["tier0"]) > 0
        
        # Tier 1 and 2 should be empty
        assert len(all_rules["tier1"]) == 0
        assert len(all_rules["tier2"]) == 0


class TestSpecialIDs:
    """Test handling of special rule IDs."""

    def test_rule_id_with_numbers(self) -> None:
        """Test rule ID with all numbers."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            mgr = GovernanceDatabaseManager(db_path=db_path)
            mgr.initialize()
            
            # Create with numeric ID
            mgr.create_project_rule(
                rule_id="12345",
                name="Numeric ID Rule",
                category="test",
                severity="info",
                description="Numeric ID",
                enforcement_point="test",
                audit_event="TEST",
                created_by="test_user",
            )
            
            # Retrieve
            rule = mgr.get_rule("12345")
            assert rule is not None
            assert rule.rule_id == "12345"
            
            mgr.close()

    def test_rule_id_with_special_chars(self) -> None:
        """Test rule ID with hyphens and underscores."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            mgr = GovernanceDatabaseManager(db_path=db_path)
            mgr.initialize()
            
            # Create with special chars
            mgr.create_project_rule(
                rule_id="RULE-001_TEST",
                name="Special Chars ID Rule",
                category="test",
                severity="info",
                description="Special chars",
                enforcement_point="test",
                audit_event="TEST",
                created_by="test_user",
            )
            
            # Retrieve
            rule = mgr.get_rule("RULE-001_TEST")
            assert rule is not None
            assert rule.rule_id == "RULE-001_TEST"
            
            mgr.close()

    def test_very_long_rule_id(self) -> None:
        """Test very long rule ID."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            mgr = GovernanceDatabaseManager(db_path=db_path)
            mgr.initialize()
            
            # Very long ID
            long_id = "RULE-" + "X" * 100
            
            # Create
            mgr.create_project_rule(
                rule_id=long_id,
                name="Long ID Rule",
                category="test",
                severity="info",
                description="Long ID",
                enforcement_point="test",
                audit_event="TEST",
                created_by="test_user",
            )
            
            # Retrieve
            rule = mgr.get_rule(long_id)
            assert rule is not None
            assert rule.rule_id == long_id
            
            mgr.close()


class TestBoundaryConditions:
    """Test boundary conditions."""

    def test_rule_with_empty_description(self) -> None:
        """Test creating rule with empty description."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            mgr = GovernanceDatabaseManager(db_path=db_path)
            mgr.initialize()
            
            # Create with empty description
            mgr.create_project_rule(
                rule_id="EMPTY-DESC",
                name="Empty Description Rule",
                category="test",
                severity="info",
                description="",  # Empty
                enforcement_point="test",
                audit_event="TEST",
                created_by="test_user",
            )
            
            # Retrieve and verify
            rule = mgr.get_rule("EMPTY-DESC")
            assert rule is not None
            assert rule.description == ""
            
            mgr.close()

    def test_very_long_description(self) -> None:
        """Test rule with very long description."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            mgr = GovernanceDatabaseManager(db_path=db_path)
            mgr.initialize()
            
            # Very long description
            long_desc = "X" * 1000
            
            mgr.create_project_rule(
                rule_id="LONG-DESC",
                name="Long Description Rule",
                category="test",
                severity="info",
                description=long_desc,
                enforcement_point="test",
                audit_event="TEST",
                created_by="test_user",
            )
            
            # Retrieve and verify
            rule = mgr.get_rule("LONG-DESC")
            assert rule is not None
            assert rule.description == long_desc
            
            mgr.close()


class TestConcurrentAccess:
    """Test concurrent-like access patterns."""

    def test_rapid_sequential_creates(self) -> None:
        """Test rapid sequential rule creation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            mgr = GovernanceDatabaseManager(db_path=db_path)
            mgr.initialize()
            
            # Rapid creates
            for i in range(30):
                mgr.create_project_rule(
                    rule_id=f"RAPID-{i:03d}",
                    name=f"Rapid Rule {i}",
                    category="test",
                    severity="info",
                    description="Rapid",
                    enforcement_point="test",
                    audit_event="TEST",
                    created_by="test_user",
                )
            
            # Verify all were created
            rules = mgr.list_rules()
            assert len(rules) >= 30
            
            mgr.close()

    def test_interleaved_create_and_read(self) -> None:
        """Test interleaved create and read operations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            mgr = GovernanceDatabaseManager(db_path=db_path)
            mgr.initialize()
            
            # Create some rules
            for i in range(10):
                mgr.create_project_rule(
                    rule_id=f"INTRL-{i:03d}",
                    name=f"Interleaved Rule {i}",
                    category="test",
                    severity="info",
                    description="Interleaved",
                    enforcement_point="test",
                    audit_event="TEST",
                    created_by="test_user",
                )
            
            # Interleave creates and reads
            for i in range(10, 20):
                # Read
                rule = mgr.get_rule(f"INTRL-{(i-10) % 10:03d}")
                assert rule is not None
                
                # Create
                mgr.create_project_rule(
                    rule_id=f"INTRL-{i:03d}",
                    name=f"Interleaved Rule {i}",
                    category="test",
                    severity="info",
                    description="Interleaved",
                    enforcement_point="test",
                    audit_event="TEST",
                    created_by="test_user",
                )
            
            mgr.close()


class TestInvalidInput:
    """Test handling of invalid input."""

    def test_get_rule_with_empty_string(self) -> None:
        """Test getting rule with empty string ID."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            mgr = GovernanceDatabaseManager(db_path=db_path)
            mgr.initialize()
            
            # Get with empty string
            rule = mgr.get_rule("")
            assert rule is None
            
            mgr.close()


class TestRecovery:
    """Test error recovery scenarios."""

    def test_registry_multiple_initializations(self) -> None:
        """Test registry survives multiple initializations."""
        registry = GovernanceRegistry()
        
        # Initialize multiple times
        registry.initialize()
        rules1 = registry.get_all_rules()
        
        registry.initialize()
        rules2 = registry.get_all_rules()
        
        registry.initialize()
        rules3 = registry.get_all_rules()
        
        # All should be identical
        assert len(rules1["tier0"]) == len(rules2["tier0"]) == len(rules3["tier0"])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
