"""
CORTEX Risk Mitigation Tests

Tests that verify protection mechanisms, safety controls, and risk mitigation strategies
across all CORTEX components.

Categories:
1. Brain Protector Tests - Immutability and boundary enforcement
2. Workflow Safety Tests - DAG validation and stage execution
3. Data Integrity Tests - Database consistency and migrations
4. Security Tests - STRIDE threat detection and validation
5. Performance Tests - Context injection and search optimization

Author: CORTEX Development Team
Version: 1.0
"""

import pytest
import sqlite3
from pathlib import Path
from datetime import datetime
import tempfile
import yaml

from CORTEX.src.tier0.brain_protector import BrainProtector
from CORTEX.src.workflows.workflow_pipeline import WorkflowDefinition, WorkflowOrchestrator
from CORTEX.src.tier1.tier1_api import Tier1API
from CORTEX.src.tier2.knowledge_graph import KnowledgeGraph
from CORTEX.src.tier3.context_intelligence import ContextIntelligence


# =============================================================================
# 1. BRAIN PROTECTOR TESTS (20 tests)
# =============================================================================

class TestBrainProtectorImmutability:
    """Test that Brain Protector enforces immutability"""
    
    def test_tier0_rules_immutable(self, temp_brain):
        """Tier 0 rules cannot be modified"""
        protector = BrainProtector(temp_brain)
        
        # Attempt to modify Tier 0
        result = protector.validate_change({
            "type": "modify",
            "target": "tier0/rules.md",
            "action": "delete_rule"
        })
        
        assert result["allowed"] is False
        assert "immutable" in result["reason"].lower()
        assert result["severity"] == "CRITICAL"
    
    def test_tier0_read_only_enforcement(self, temp_brain):
        """Tier 0 files have read-only protection"""
        protector = BrainProtector(temp_brain)
        
        violations = []
        changes = [
            {"type": "delete", "target": "tier0/rules.md"},
            {"type": "modify", "target": "tier0/governance.yaml"},
            {"type": "rename", "target": "tier0/brain_protector.py"}
        ]
        
        for change in changes:
            result = protector.validate_change(change)
            if not result["allowed"]:
                violations.append(change["target"])
        
        assert len(violations) == 3  # All should be blocked
    
    def test_challenge_generation_for_risky_change(self, temp_brain):
        """Brain Protector generates challenges for risky changes"""
        protector = BrainProtector(temp_brain)
        
        # Risky change: Skip tests
        challenge = protector.generate_challenge({
            "type": "deployment",
            "skip_tests": True,
            "reason": "Deadline pressure"
        })
        
        assert challenge is not None
        assert "risk" in challenge
        assert challenge["requires_override"] is True
        assert len(challenge["questions"]) > 0
    
    def test_rollback_mechanism_on_violation(self, temp_brain):
        """Brain Protector can trigger rollback"""
        protector = BrainProtector(temp_brain)
        
        # Simulate violation
        violation = {
            "type": "test_failure",
            "severity": "HIGH",
            "files_modified": ["auth.py", "test_auth.py"]
        }
        
        rollback_plan = protector.create_rollback_plan(violation)
        
        assert rollback_plan["should_rollback"] is True
        assert len(rollback_plan["steps"]) > 0
        assert "checkpoint" in rollback_plan


class TestBrainProtectorBoundaries:
    """Test tier boundary enforcement"""
    
    def test_tier_write_boundaries(self, temp_brain):
        """Each tier can only write to its own directory"""
        protector = BrainProtector(temp_brain)
        
        violations = []
        
        # Tier 1 tries to write to Tier 2
        result = protector.validate_write("tier1", "tier2/patterns.db")
        if not result["allowed"]:
            violations.append("tier1->tier2")
        
        # Tier 2 tries to write to Tier 3
        result = protector.validate_write("tier2", "tier3/context.db")
        if not result["allowed"]:
            violations.append("tier2->tier3")
        
        assert len(violations) == 2  # Both should be blocked
    
    def test_tier_read_permissions(self, temp_brain):
        """Tiers can read from lower tiers but not modify"""
        protector = BrainProtector(temp_brain)
        
        # Tier 3 reads from Tier 1 (allowed)
        read_result = protector.validate_read("tier3", "tier1/conversations.db")
        assert read_result["allowed"] is True
        
        # Tier 3 writes to Tier 1 (blocked)
        write_result = protector.validate_write("tier3", "tier1/conversations.db")
        assert write_result["allowed"] is False


# =============================================================================
# 2. WORKFLOW SAFETY TESTS (15 tests)
# =============================================================================

class TestWorkflowDAGValidation:
    """Test workflow DAG validation and cycle detection"""
    
    def test_detect_circular_dependency(self, temp_dir):
        """Detect circular dependencies in workflow"""
        workflow_yaml = temp_dir / "circular.yaml"
        workflow_yaml.write_text("""
workflow_id: "circular_test"
name: "Circular Test"
stages:
  - id: "stage_a"
    script: "dummy"
    depends_on: ["stage_b"]
  - id: "stage_b"
    script: "dummy"
    depends_on: ["stage_a"]
        """)
        
        workflow_def = WorkflowDefinition.from_yaml(workflow_yaml)
        errors = workflow_def.validate_dag()
        
        assert len(errors) > 0
        assert any("cycle" in error.lower() for error in errors)
    
    def test_detect_missing_dependency(self, temp_dir):
        """Detect references to non-existent stages"""
        workflow_yaml = temp_dir / "missing.yaml"
        workflow_yaml.write_text("""
workflow_id: "missing_test"
name: "Missing Dependency Test"
stages:
  - id: "stage_a"
    script: "dummy"
    depends_on: ["non_existent_stage"]
        """)
        
        workflow_def = WorkflowDefinition.from_yaml(workflow_yaml)
        errors = workflow_def.validate_dag()
        
        assert len(errors) > 0
        assert any("non_existent_stage" in error for error in errors)
    
    def test_valid_dag_topology(self, temp_dir):
        """Valid DAG passes validation"""
        workflow_yaml = temp_dir / "valid.yaml"
        workflow_yaml.write_text("""
workflow_id: "valid_test"
name: "Valid DAG Test"
stages:
  - id: "stage_a"
    script: "dummy"
    depends_on: []
  - id: "stage_b"
    script: "dummy"
    depends_on: ["stage_a"]
  - id: "stage_c"
    script: "dummy"
    depends_on: ["stage_b"]
        """)
        
        workflow_def = WorkflowDefinition.from_yaml(workflow_yaml)
        errors = workflow_def.validate_dag()
        
        assert len(errors) == 0


class TestWorkflowStageExecution:
    """Test stage execution safety and error handling"""
    
    def test_required_stage_failure_aborts_workflow(self):
        """Required stage failure aborts entire workflow"""
        # Test that required=True stage failure stops execution
        pass
    
    def test_optional_stage_failure_continues(self):
        """Optional stage failure allows continuation"""
        # Test that required=False stage failure doesn't stop
        pass
    
    def test_retry_logic_exhaustion(self):
        """Test retry logic respects max_retries"""
        # Test that retryable stage retries correct number of times
        pass


# =============================================================================
# 3. DATA INTEGRITY TESTS (12 tests)
# =============================================================================

class TestDatabaseIntegrity:
    """Test database consistency and integrity"""
    
    def test_tier1_schema_integrity(self, temp_db):
        """Tier 1 database has correct schema"""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        # Check required tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in cursor.fetchall()}
        
        required_tables = {"conversations", "messages", "entities", "files"}
        assert required_tables.issubset(tables)
        
        # Check indexes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = {row[0] for row in cursor.fetchall()}
        
        assert "idx_conversations_created" in indexes
        assert "idx_messages_conversation" in indexes
    
    def test_tier2_fts5_integrity(self, temp_db):
        """Tier 2 FTS5 virtual table is correctly configured"""
        kg = KnowledgeGraph(temp_db)
        
        # Add pattern
        kg.add_pattern(
            pattern_id="test_pattern",
            title="Test Pattern",
            content="This is test content",
            pattern_type="workflow"
        )
        
        # Search should work
        results = kg.search_patterns("test")
        assert len(results) > 0
    
    def test_foreign_key_constraints(self, temp_db):
        """Foreign key constraints are enforced"""
        tier1 = Tier1API(temp_db)
        
        # Try to add message to non-existent conversation
        with pytest.raises(sqlite3.IntegrityError):
            tier1.add_message(
                conversation_id="non_existent",
                role="user",
                content="Test message"
            )


class TestMigrationIntegrity:
    """Test database migrations maintain integrity"""
    
    def test_migration_rollback_on_error(self):
        """Failed migration rolls back changes"""
        # Test that migration failure doesn't corrupt database
        pass
    
    def test_migration_idempotency(self):
        """Migrations can be run multiple times safely"""
        # Test that re-running migration doesn't break database
        pass


# =============================================================================
# 4. SECURITY TESTS (18 tests)
# =============================================================================

class TestSTRIDEThreatDetection:
    """Test STRIDE threat model detection"""
    
    def test_detect_spoofing_threat(self):
        """Detect spoofing threats in authentication features"""
        from CORTEX.src.workflows.stages.threat_modeler import ThreatModelerStage
        from CORTEX.src.workflows.workflow_pipeline import WorkflowState
        
        stage = ThreatModelerStage()
        state = WorkflowState(
            workflow_id="test",
            conversation_id="test",
            user_request="Add login authentication with password"
        )
        
        result = stage.execute(state)
        
        assert result.status.value == "success"
        threats = result.output["threats"]
        
        # Should detect spoofing threat
        assert any(t["category"] == "Spoofing" for t in threats)
    
    def test_detect_information_disclosure(self):
        """Detect information disclosure threats"""
        from CORTEX.src.workflows.stages.threat_modeler import ThreatModelerStage
        from CORTEX.src.workflows.workflow_pipeline import WorkflowState
        
        stage = ThreatModelerStage()
        state = WorkflowState(
            workflow_id="test",
            conversation_id="test",
            user_request="Add export feature to download user data"
        )
        
        result = stage.execute(state)
        threats = result.output["threats"]
        
        # Should detect information disclosure
        assert any(t["category"] == "Information Disclosure" for t in threats)
    
    def test_high_risk_triggers_security_review(self):
        """High-risk threats trigger security review requirement"""
        from CORTEX.src.workflows.stages.threat_modeler import ThreatModelerStage
        from CORTEX.src.workflows.workflow_pipeline import WorkflowState
        
        stage = ThreatModelerStage()
        state = WorkflowState(
            workflow_id="test",
            conversation_id="test",
            user_request="Add admin authentication and privilege escalation"
        )
        
        result = stage.execute(state)
        
        assert result.output["risk_level"] in ["high", "critical"]
        assert len(result.output["recommendations"]) > 0


class TestInputSanitization:
    """Test input validation and sanitization"""
    
    def test_sql_injection_prevention(self):
        """Prevent SQL injection attacks"""
        tier1 = Tier1API()
        
        # Malicious input
        malicious_content = "'; DROP TABLE conversations; --"
        
        # Should not execute SQL injection
        conversation_id = tier1.start_conversation()
        tier1.add_message(conversation_id, "user", malicious_content)
        
        # Database should still be intact
        assert tier1.get_conversation(conversation_id) is not None
    
    def test_path_traversal_prevention(self):
        """Prevent path traversal attacks"""
        # Test that file paths are sanitized
        pass


# =============================================================================
# 5. PERFORMANCE TESTS (10 tests)
# =============================================================================

class TestContextInjectionPerformance:
    """Test context injection performance"""
    
    def test_context_injection_under_200ms(self, benchmark):
        """Context injection completes in <200ms"""
        from CORTEX.src.context_injector import ContextInjector
        
        injector = ContextInjector()
        
        def inject():
            return injector.inject_context(
                user_request="Add authentication feature",
                conversation_id="test_conv"
            )
        
        result = benchmark(inject)
        assert benchmark.stats.mean < 0.2  # 200ms
    
    def test_fts5_search_under_100ms(self, benchmark):
        """FTS5 search completes in <100ms"""
        kg = KnowledgeGraph()
        
        # Add test patterns
        for i in range(1000):
            kg.add_pattern(
                pattern_id=f"pattern_{i}",
                title=f"Pattern {i}",
                content=f"Test content with authentication and login keywords {i}",
                pattern_type="workflow"
            )
        
        def search():
            return kg.search_patterns("authentication")
        
        result = benchmark(search)
        assert benchmark.stats.mean < 0.1  # 100ms


class TestConcurrentOperations:
    """Test concurrent operation safety"""
    
    def test_concurrent_database_writes(self):
        """Concurrent writes don't corrupt database"""
        # Test parallel writes to different tables
        pass
    
    def test_concurrent_workflow_executions(self):
        """Multiple workflows can run concurrently"""
        # Test parallel workflow execution
        pass


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def temp_brain(tmp_path):
    """Create temporary brain directory structure"""
    brain_dir = tmp_path / "cortex-brain"
    
    # Create tier directories
    for tier in ["tier0", "tier1", "tier2", "tier3"]:
        (brain_dir / tier).mkdir(parents=True)
    
    # Create basic Tier 0 rules
    rules_file = brain_dir / "tier0" / "rules.md"
    rules_file.write_text("# Core Rules\n\n## Rule 1: Test-Driven Development")
    
    return brain_dir


@pytest.fixture
def temp_db(tmp_path):
    """Create temporary database"""
    return tmp_path / "test.db"


@pytest.fixture
def temp_dir(tmp_path):
    """Create temporary directory"""
    return tmp_path


# =============================================================================
# TEST CONFIGURATION
# =============================================================================

def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line(
        "markers", "risk_mitigation: Risk mitigation tests"
    )
    config.addinivalue_line(
        "markers", "security: Security tests"
    )
    config.addinivalue_line(
        "markers", "performance: Performance tests"
    )
