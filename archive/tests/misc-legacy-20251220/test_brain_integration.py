"""
Tests for CORTEX 4.0 Brain Integration

Comprehensive test suite for all brain tiers:
- Tier 0: Governance
- Tier 1: Working Memory
- Tier 2: Knowledge Graph
- Tier 3: Development Context
- BrainInterface integration

Author: Asif Hussain
Copyright: © 2025 Asif Hussain. All rights reserved.
"""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime

from src.brain import BrainInterface, create_brain
from src.brain.tier0 import GovernanceEngine, SkullRuleId, EnforcementLevel
from src.brain.tier1 import WorkingMemory
from src.brain.tier2 import KnowledgeGraph
from src.brain.tier3 import DevelopmentContext


@pytest.fixture
def temp_workspace(tmp_path):
    """Create temporary workspace directory."""
    workspace = tmp_path / "test-workspace"
    workspace.mkdir()
    return workspace


@pytest.fixture
def temp_shared_root(tmp_path):
    """Create temporary shared root directory."""
    shared = tmp_path / ".cortex" / "shared"
    shared.mkdir(parents=True)
    return shared


class TestBrainInterface:
    """Test suite for BrainInterface."""
    
    def test_brain_interface_initialization(self, temp_workspace):
        """Test brain interface initialization."""
        brain = BrainInterface(temp_workspace)
        
        assert brain.workspace_root == temp_workspace
        assert brain.config is not None
        assert brain.config.workspace_root == temp_workspace
    
    def test_factory_function(self, temp_workspace):
        """Test create_brain factory function."""
        brain = create_brain(temp_workspace)
        
        assert isinstance(brain, BrainInterface)
        assert brain.workspace_root == temp_workspace
    
    def test_tier0_lazy_loading(self, temp_workspace):
        """Test Tier 0 lazy initialization."""
        brain = BrainInterface(temp_workspace)
        
        # Tier 0 should be None initially
        assert brain._tier0 is None
        
        # Access should trigger initialization
        tier0 = brain.tier0
        assert tier0 is not None
        assert isinstance(tier0, GovernanceEngine)
    
    def test_tier1_lazy_loading(self, temp_workspace):
        """Test Tier 1 lazy initialization."""
        brain = BrainInterface(temp_workspace)
        
        # Tier 1 should be None initially
        assert brain._tier1 is None
        
        # Access should trigger initialization
        tier1 = brain.tier1
        assert tier1 is not None
        assert isinstance(tier1, WorkingMemory)
    
    def test_health_check(self, temp_workspace):
        """Test brain health check."""
        brain = BrainInterface(temp_workspace)
        
        health = brain.health_check()
        
        assert isinstance(health, dict)
        assert "tier0" in health
        assert "tier1" in health
        assert "tier2" in health
        assert "tier3" in health
    
    def test_get_stats(self, temp_workspace):
        """Test brain statistics retrieval."""
        brain = BrainInterface(temp_workspace)
        
        stats = brain.get_stats()
        
        assert isinstance(stats, dict)
        # Stats should include tier information
        assert len(stats) > 0


class TestTier0Governance:
    """Test suite for Tier 0: Governance."""
    
    def test_governance_initialization(self, temp_shared_root):
        """Test governance engine initialization."""
        rules_path = temp_shared_root / "skull_rules.yaml"
        governance = GovernanceEngine(rules_path)
        
        assert governance.rules_path == rules_path
        assert governance.rules is not None
    
    def test_tdd_phase_validation_green(self, temp_shared_root):
        """Test TDD phase validation: RED → GREEN."""
        rules_path = temp_shared_root / "skull_rules.yaml"
        governance = GovernanceEngine(rules_path)
        
        # Valid transition: tests run, tests failed in RED
        result = governance.validate_tdd_phase(
            target_phase="green",
            tests_run=["test_feature.py"],
            test_results={"all_passed": False}
        )
        
        assert result.passed is True
        assert result.rule_id == SkullRuleId.TDD_ENFORCEMENT
    
    def test_tdd_phase_validation_no_tests(self, temp_shared_root):
        """Test TDD phase validation failure: no tests run."""
        rules_path = temp_shared_root / "skull_rules.yaml"
        governance = GovernanceEngine(rules_path)
        
        # Invalid: no tests run
        result = governance.validate_tdd_phase(
            target_phase="green",
            tests_run=[]
        )
        
        assert result.passed is False
        assert result.enforcement == EnforcementLevel.BLOCKING
    
    def test_code_creation_validation(self, temp_shared_root, temp_workspace):
        """Test code creation validation."""
        rules_path = temp_shared_root / "skull_rules.yaml"
        governance = GovernanceEngine(rules_path)
        
        # Valid: search performed, no duplicates
        result = governance.validate_code_creation(
            file_path=temp_workspace / "new_feature.py",
            search_performed=True,
            duplicates_found=None
        )
        
        assert result.passed is True


class TestTier1WorkingMemory:
    """Test suite for Tier 1: Working Memory."""
    
    def test_working_memory_initialization(self, temp_workspace):
        """Test working memory initialization."""
        db_path = temp_workspace / "cortex-brain" / "tier1" / "conversations.db"
        memory = WorkingMemory(db_path, max_conversations=70)
        
        assert memory.db_path == db_path
        assert memory.max_conversations == 70
        assert db_path.exists()
    
    def test_create_conversation(self, temp_workspace):
        """Test conversation creation."""
        db_path = temp_workspace / "cortex-brain" / "tier1" / "conversations.db"
        memory = WorkingMemory(db_path)
        
        conv_id = memory.create_conversation(
            agent_id="test_agent",
            goal="Test goal"
        )
        
        assert conv_id is not None
        assert isinstance(conv_id, str)
    
    def test_add_message(self, temp_workspace):
        """Test adding message to conversation."""
        db_path = temp_workspace / "cortex-brain" / "tier1" / "conversations.db"
        memory = WorkingMemory(db_path)
        
        conv_id = memory.create_conversation(agent_id="test_agent")
        msg_id = memory.add_message(
            conversation_id=conv_id,
            role="user",
            content="Test message"
        )
        
        assert msg_id is not None
        
        # Verify message was stored
        messages = memory.get_messages(conv_id)
        assert len(messages) == 1
        assert messages[0].content == "Test message"
    
    def test_fifo_enforcement(self, temp_workspace):
        """Test FIFO queue enforcement."""
        db_path = temp_workspace / "cortex-brain" / "tier1" / "conversations.db"
        memory = WorkingMemory(db_path, max_conversations=5)
        
        # Create 10 conversations
        conv_ids = []
        for i in range(10):
            conv_id = memory.create_conversation(agent_id=f"agent_{i}")
            conv_ids.append(conv_id)
        
        # Should only have 5 conversations (FIFO)
        count = memory.get_conversation_count()
        assert count == 5
        
        # First 5 conversations should be deleted
        for i in range(5):
            conv = memory.get_conversation(conv_ids[i])
            assert conv is None
        
        # Last 5 should exist
        for i in range(5, 10):
            conv = memory.get_conversation(conv_ids[i])
            assert conv is not None


class TestTier2KnowledgeGraph:
    """Test suite for Tier 2: Knowledge Graph."""
    
    def test_knowledge_graph_initialization(self, temp_shared_root):
        """Test knowledge graph initialization."""
        db_path = temp_shared_root / "tier2" / "knowledge-graph.db"
        kg = KnowledgeGraph(db_path, namespace="test")
        
        assert kg.db_path == db_path
        assert kg.namespace == "test"
        assert db_path.exists()
    
    def test_store_pattern(self, temp_shared_root):
        """Test pattern storage."""
        db_path = temp_shared_root / "tier2" / "knowledge-graph.db"
        kg = KnowledgeGraph(db_path, namespace="test")
        
        pattern_id = kg.store_pattern(
            title="Test Pattern",
            pattern_type="workflow",
            context={"key": "value"},
            confidence=0.8
        )
        
        assert pattern_id is not None
        assert isinstance(pattern_id, str)
    
    def test_search_patterns(self, temp_shared_root):
        """Test pattern search."""
        db_path = temp_shared_root / "tier2" / "knowledge-graph.db"
        kg = KnowledgeGraph(db_path, namespace="test")
        
        # Store patterns
        kg.store_pattern(
            title="TDD Workflow",
            pattern_type="workflow",
            context={"phases": ["red", "green", "refactor"]}
        )
        
        # Search
        patterns = kg.search_patterns("TDD")
        
        assert len(patterns) > 0
        assert patterns[0].title == "TDD Workflow"
    
    def test_namespace_isolation(self, temp_shared_root):
        """Test namespace isolation between projects."""
        db_path = temp_shared_root / "tier2" / "knowledge-graph.db"
        
        # Create two knowledge graphs with different namespaces
        kg1 = KnowledgeGraph(db_path, namespace="project1")
        kg2 = KnowledgeGraph(db_path, namespace="project2")
        
        # Store pattern in project1
        kg1.store_pattern(
            title="Project1 Pattern",
            pattern_type="workflow",
            context={}
        )
        
        # Store pattern in project2
        kg2.store_pattern(
            title="Project2 Pattern",
            pattern_type="workflow",
            context={}
        )
        
        # Search in project1 - should only see project1 pattern
        patterns1 = kg1.search_patterns("Pattern")
        assert len(patterns1) == 1
        assert patterns1[0].title == "Project1 Pattern"
        
        # Search in project2 - should only see project2 pattern
        patterns2 = kg2.search_patterns("Pattern")
        assert len(patterns2) == 1
        assert patterns2[0].title == "Project2 Pattern"


class TestTier3DevelopmentContext:
    """Test suite for Tier 3: Development Context."""
    
    def test_dev_context_initialization(self, temp_workspace):
        """Test development context initialization."""
        db_path = temp_workspace / "cortex-brain" / "tier3" / "metrics.db"
        context = DevelopmentContext(db_path)
        
        assert context.db_path == db_path
        assert db_path.exists()
    
    def test_store_git_metrics(self, temp_workspace):
        """Test storing git metrics."""
        db_path = temp_workspace / "cortex-brain" / "tier3" / "metrics.db"
        context = DevelopmentContext(db_path)
        
        metrics = {
            "commits": 150,
            "hotspots": ["src/main.py", "src/utils.py"]
        }
        
        context.store_git_metrics(metrics)
        
        # Retrieve metrics
        stored = context.get_metrics("git")
        assert stored["commits"] == 150
        assert len(stored["hotspots"]) == 2
    
    def test_store_ide_context(self, temp_workspace):
        """Test storing IDE context."""
        db_path = temp_workspace / "cortex-brain" / "tier3" / "metrics.db"
        context = DevelopmentContext(db_path)
        
        context.store_ide_context("vscode", {"version": "1.85"})
        
        # Retrieve IDE context
        ide = context.get_ide_context()
        assert ide == "vscode"


class TestIntegration:
    """Integration tests for brain tiers."""
    
    def test_end_to_end_workflow(self, temp_workspace):
        """Test complete brain workflow."""
        brain = BrainInterface(temp_workspace)
        
        # Tier 0: Validate TDD phase
        governance_result = brain.tier0.validate_tdd_phase(
            target_phase="green",
            tests_run=["test.py"],
            test_results={"all_passed": False}
        )
        assert governance_result.passed
        
        # Tier 1: Create conversation
        conv_id = brain.tier1.create_conversation(agent_id="test")
        brain.tier1.add_message(conv_id, role="user", content="Test")
        
        # Tier 2: Store pattern
        pattern_id = brain.tier2.store_pattern(
            title="Test Pattern",
            pattern_type="workflow",
            context={}
        )
        assert pattern_id is not None
        
        # Tier 3: Store metrics
        brain.tier3.store_git_metrics({"commits": 100})
        brain.tier3.store_ide_context("vscode")
        
        # Verify all tiers operational
        health = brain.health_check()
        assert all(health.values())
        
        # Clean up
        brain.close()
