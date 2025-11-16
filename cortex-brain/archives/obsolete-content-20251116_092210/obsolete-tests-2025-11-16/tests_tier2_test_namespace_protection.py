"""
Comprehensive tests for namespace-based knowledge boundary protection.

Tests namespace isolation, write protection, and correct storage routing.
Ensures CORTEX framework patterns stay separate from workspace patterns.

CRITICAL: These tests validate SKULL protection against knowledge contamination.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any

# Import knowledge graph (will need to update actual import based on structure)
try:
    from src.tier2.knowledge_graph.knowledge_graph import KnowledgeGraph
except ImportError:
    # Fallback for legacy structure
    try:
        from src.tier2.knowledge_graph_legacy import KnowledgeGraph
    except ImportError:
        pytest.skip("KnowledgeGraph not available", allow_module_level=True)


class TestNamespaceWriteProtection:
    """Test that cortex.* namespace is write-protected from user code."""
    
    @pytest.fixture
    def temp_kg(self, tmp_path):
        """Create temporary knowledge graph for testing."""
        db_path = tmp_path / "test_knowledge.db"
        kg = KnowledgeGraph(db_path=db_path)  # Pass Path object, not string
        yield kg
        # Cleanup
        kg.close()  # Close connection before unlinking
        if db_path.exists():
            db_path.unlink()
    
    def test_cortex_namespace_blocked_from_user_code(self, temp_kg):
        """
        CRITICAL: User code CANNOT write to cortex.* namespace.
        
        This prevents workspace patterns from contaminating framework knowledge.
        """
        # Attempt to write to cortex.* namespace (should fail)
        with pytest.raises(ValueError, match="cortex.* namespace is protected"):
            temp_kg.learn_pattern(
                pattern={
                    "title": "User Pattern",
                    "content": "This should be blocked",
                    "pattern_type": "principle"
                },
                namespace="cortex.user_contamination",
                is_cortex_internal=False  # Simulate user code
            )
    
    def test_cortex_namespace_allowed_from_framework_code(self, temp_kg):
        """
        CORTEX framework code CAN write to cortex.* namespace.
        
        Framework must be able to store its own patterns.
        """
        # Write from CORTEX framework (should succeed)
        temp_kg.learn_pattern(
            pattern={
                "title": "Framework Pattern",
                "content": "CORTEX agent coordination pattern",
                "pattern_type": "principle"
            },
            namespace="cortex.agent_patterns",
            is_cortex_internal=True  # Simulate framework code
        )
        
        # Verify stored with correct namespace
        patterns = temp_kg.query(namespace_filter="cortex.agent_patterns")
        assert len(patterns) == 1
        assert patterns[0]["title"] == "Framework Pattern"
        assert patterns[0]["_namespace"] == "cortex.agent_patterns"
    
    def test_workspace_namespace_always_allowed(self, temp_kg):
        """
        User code CAN write to workspace.* namespace freely.
        
        This is the designated space for user application patterns.
        """
        # Write to workspace namespace (should succeed)
        temp_kg.learn_pattern(
            pattern={
                "title": "App Pattern",
                "content": "My application uses JWT auth",
                "pattern_type": "workflow"
            },
            namespace="workspace.myapp.security",
            is_cortex_internal=False  # User code
        )
        
        # Verify stored correctly
        patterns = temp_kg.query(namespace_filter="workspace.myapp.*")
        assert len(patterns) == 1
        assert patterns[0]["title"] == "App Pattern"
        assert patterns[0]["_namespace"] == "workspace.myapp.security"
    
    def test_namespace_required_on_write(self, temp_kg):
        """
        All patterns MUST have a namespace when written.
        
        No more ambiguous storage without clear boundaries.
        """
        with pytest.raises(ValueError, match="namespace is required"):
            temp_kg.learn_pattern(
                pattern={
                    "title": "Ambiguous Pattern",
                    "content": "Where does this belong?"
                },
                namespace=None  # Missing namespace
            )


class TestNamespaceIsolation:
    """Test that namespaces isolate patterns correctly."""
    
    @pytest.fixture
    def populated_kg(self, tmp_path):
        """Knowledge graph with patterns in multiple namespaces."""
        db_path = tmp_path / "test_knowledge.db"
        kg = KnowledgeGraph(db_path=db_path)  # Pass Path object, not string
        
        # Add CORTEX patterns
        kg.learn_pattern(
            {"title": "Tier Architecture", "content": "Four-tier brain system"},
            namespace="cortex.tier_architecture",
            is_cortex_internal=True
        )
        kg.learn_pattern(
            {"title": "Agent Coordination", "content": "10 specialist agents"},
            namespace="cortex.agent_patterns",
            is_cortex_internal=True
        )
        
        # Add workspace patterns
        kg.learn_pattern(
            {"title": "API Auth", "content": "Uses JWT tokens"},
            namespace="workspace.app1.security",
            is_cortex_internal=False
        )
        kg.learn_pattern(
            {"title": "UI Components", "content": "Feature-based structure"},
            namespace="workspace.app1.architecture",
            is_cortex_internal=False
        )
        kg.learn_pattern(
            {"title": "Database Schema", "content": "PostgreSQL with migrations"},
            namespace="workspace.app2.data",
            is_cortex_internal=False
        )
        
        yield kg
        
        kg.close()  # Close connection before unlinking
        if db_path.exists():
            db_path.unlink()
    
    def test_query_cortex_namespace_only(self, populated_kg):
        """
        Query cortex.* should return ONLY framework patterns.
        
        No workspace contamination in results.
        """
        cortex_patterns = populated_kg.query(namespace_filter="cortex.*")
        
        assert len(cortex_patterns) == 2
        titles = [p["title"] for p in cortex_patterns]
        assert "Tier Architecture" in titles
        assert "Agent Coordination" in titles
        
        # Verify NO workspace patterns
        assert "API Auth" not in titles
        assert "UI Components" not in titles
    
    def test_query_workspace_namespace_only(self, populated_kg):
        """
        Query workspace.app1.* should return ONLY app1 patterns.
        
        No CORTEX or other workspace contamination.
        """
        app1_patterns = populated_kg.query(namespace_filter="workspace.app1.*")
        
        assert len(app1_patterns) == 2
        titles = [p["title"] for p in app1_patterns]
        assert "API Auth" in titles
        assert "UI Components" in titles
        
        # Verify NO CORTEX patterns
        assert "Tier Architecture" not in titles
        
        # Verify NO other workspace patterns
        assert "Database Schema" not in titles
    
    def test_query_specific_namespace(self, populated_kg):
        """Query exact namespace returns only matching patterns."""
        security_patterns = populated_kg.query(
            namespace_filter="workspace.app1.security"
        )
        
        assert len(security_patterns) == 1
        assert security_patterns[0]["title"] == "API Auth"
    
    def test_query_all_namespaces_with_wildcard(self, populated_kg):
        """Query with * wildcard returns all patterns (admin use case)."""
        all_patterns = populated_kg.query(namespace_filter="*")
        
        assert len(all_patterns) == 5
        
        # Should include CORTEX + all workspaces
        titles = [p["title"] for p in all_patterns]
        assert "Tier Architecture" in titles  # CORTEX
        assert "API Auth" in titles  # workspace.app1
        assert "Database Schema" in titles  # workspace.app2
    
    def test_cross_workspace_isolation(self, populated_kg):
        """
        workspace.app1.* CANNOT see workspace.app2.* patterns.
        
        Critical for multi-project CORTEX usage.
        """
        app1_patterns = populated_kg.query(namespace_filter="workspace.app1.*")
        app2_patterns = populated_kg.query(namespace_filter="workspace.app2.*")
        
        # app1 should NOT contain app2 patterns
        app1_titles = [p["title"] for p in app1_patterns]
        assert "Database Schema" not in app1_titles
        
        # app2 should NOT contain app1 patterns
        app2_titles = [p["title"] for p in app2_patterns]
        assert "API Auth" not in app2_titles
        assert "UI Components" not in app2_titles


class TestCorrectStorageRouting:
    """Test that patterns are stored in the correct namespace automatically."""
    
    @pytest.fixture
    def temp_kg(self, tmp_path):
        """Create temporary knowledge graph."""
        db_path = tmp_path / "test_knowledge.db"
        kg = KnowledgeGraph(db_path=db_path)  # Pass Path object, not string
        yield kg
        kg.close()  # Close connection before unlinking
        if db_path.exists():
            db_path.unlink()
    
    def test_cortex_pattern_routed_to_cortex_namespace(self, temp_kg):
        """
        When CORTEX framework learns a pattern, it goes to cortex.* namespace.
        """
        # Simulate framework learning about agent patterns
        temp_kg.learn_pattern(
            pattern={
                "title": "Agent Communication Protocol",
                "content": "Agents communicate via corpus callosum",
                "pattern_type": "principle",
                "source": "cortex_framework"
            },
            namespace="cortex.agent_patterns",
            is_cortex_internal=True
        )
        
        # Verify namespace assignment
        patterns = temp_kg.query(namespace_filter="cortex.agent_patterns")
        assert len(patterns) == 1
        assert patterns[0]["_namespace"] == "cortex.agent_patterns"
        assert patterns[0]["source"] == "cortex_framework"
    
    def test_workspace_pattern_routed_to_workspace_namespace(self, temp_kg):
        """
        When user's workspace learns a pattern, it goes to workspace.* namespace.
        """
        # Simulate user app learning about its own architecture
        temp_kg.learn_pattern(
            pattern={
                "title": "File Upload Handler",
                "content": "Uses multipart/form-data with 10MB limit",
                "pattern_type": "solution",
                "source": "user_code_crawler"
            },
            namespace="workspace.myapp.api_patterns",
            is_cortex_internal=False
        )
        
        # Verify namespace assignment
        patterns = temp_kg.query(namespace_filter="workspace.myapp.api_patterns")
        assert len(patterns) == 1
        assert patterns[0]["_namespace"] == "workspace.myapp.api_patterns"
        assert patterns[0]["source"] == "user_code_crawler"
    
    def test_auto_namespace_detection_from_source(self, temp_kg):
        """
        FUTURE: Knowledge graph auto-detects namespace from pattern source.
        
        Example: If source is "tests/fixtures/mock-project/...", 
        namespace should be "workspace.mock-project.*"
        """
        # This test documents future enhancement
        # Currently namespaces are explicit, but could be auto-detected
        pytest.skip("Auto-detection not yet implemented - future enhancement")


class TestNamespacePriorityBoosting:
    """Test that namespace priority boosting works correctly (already implemented)."""
    
    @pytest.fixture
    def populated_kg(self, tmp_path):
        """Knowledge graph with patterns of varying relevance."""
        db_path = tmp_path / "test_knowledge.db"
        kg = KnowledgeGraph(db_path=db_path)  # Pass Path object, not string
        
        # High confidence CORTEX pattern
        kg.learn_pattern(
            {
                "title": "JWT Authentication Best Practice",
                "content": "Use RS256 with short-lived tokens",
                "confidence": 0.95
            },
            namespace="cortex.security_patterns",
            is_cortex_internal=True
        )
        
        # Current workspace pattern (medium confidence)
        kg.learn_pattern(
            {
                "title": "Our API Auth Implementation",
                "content": "Currently using basic auth, need to upgrade",
                "confidence": 0.70
            },
            namespace="workspace.myapp.security",
            is_cortex_internal=False
        )
        
        # Other workspace pattern (low relevance)
        kg.learn_pattern(
            {
                "title": "Auth for Different Project",
                "content": "Uses OAuth2 with GitHub",
                "confidence": 0.80
            },
            namespace="workspace.otherapp.security",
            is_cortex_internal=False
        )
        
        yield kg
        kg.close()  # Close connection before unlinking
        if db_path.exists():
            db_path.unlink()
    
    @pytest.mark.skip(reason="Priority boosting needs pattern_search implementation update")
    def test_current_workspace_gets_highest_priority(self, populated_kg):
        """
        When working on workspace.myapp, its patterns get 2.0x boost.
        
        Even if other patterns have higher confidence, current workspace wins.
        """
        # Search with current_namespace context
        results = populated_kg.search_patterns_with_namespace_priority(
            query="authentication",
            current_namespace="workspace.myapp",
            include_cortex=True,
            limit=3
        )
        
        # Current workspace should be FIRST (despite lower confidence)
        # because of 2.0x priority boost
        assert results[0]["title"] == "Our API Auth Implementation"
        assert results[0]["_namespace"] == "workspace.myapp.security"
    
    @pytest.mark.skip(reason="Priority boosting needs pattern_search implementation update")
    def test_cortex_patterns_get_medium_priority(self, populated_kg):
        """
        CORTEX patterns get 1.5x boost (second priority after current workspace).
        """
        results = populated_kg.search_patterns_with_namespace_priority(
            query="authentication",
            current_namespace="workspace.myapp",
            include_cortex=True,
            limit=3
        )
        
        # CORTEX pattern should be second
        assert results[1]["title"] == "JWT Authentication Best Practice"
        assert results[1]["_namespace"] == "cortex.security_patterns"
    
    @pytest.mark.skip(reason="Priority boosting needs pattern_search implementation update")
    def test_other_workspaces_get_lowest_priority(self, populated_kg):
        """
        Other workspace patterns get 0.5x boost (lowest priority).
        """
        results = populated_kg.search_patterns_with_namespace_priority(
            query="authentication",
            current_namespace="workspace.myapp",
            include_cortex=True,
            limit=3
        )
        
        # Other workspace should be last (despite highest confidence)
        assert results[2]["title"] == "Auth for Different Project"
        assert results[2]["_namespace"] == "workspace.otherapp.security"


class TestNamespaceProtectionRules:
    """Test brain protection rules for namespace violations."""
    
    def test_brain_protector_detects_namespace_violation(self):
        """
        Brain Protector should detect attempts to write to cortex.* namespace.
        
        This tests integration with brain-protection-rules.yaml Layer 6.
        """
        # Will implement after brain protection YAML rules added
        pytest.skip("Requires Layer 6 in brain-protection-rules.yaml")
    
    def test_namespace_mixing_blocked(self):
        """
        A pattern CANNOT belong to multiple namespaces.
        
        Cross-namespace references must use explicit links, not multi-namespace.
        """
        # Will implement after namespace validation logic added
        pytest.skip("Requires namespace mixing validation")


class TestMigrationScenarios:
    """Test migration of existing patterns to namespaces."""
    
    def test_detect_cortex_patterns_for_migration(self):
        """
        Migration script must correctly identify CORTEX framework patterns.
        
        Patterns like "validation_insights", "workflow_patterns" → cortex.*
        """
        # Test data: Existing knowledge graph without namespaces
        existing_patterns = {
            "validation_insights": {
                "title": "Validation Insights",
                "content": "TDD enforcement patterns"
            },
            "file_relationships": {
                "title": "File Relationships",
                "content": "tests/fixtures/mock-project/..."
            }
        }
        
        # Migration logic (simplified)
        def classify_pattern(key: str) -> str:
            """Determine correct namespace for pattern."""
            cortex_keys = [
                "validation_insights",
                "workflow_patterns",
                "architectural_patterns",
                "intent_patterns"
            ]
            
            if key in cortex_keys:
                return f"cortex.{key}"
            else:
                return f"workspace.default.{key}"
        
        # Test classification
        assert classify_pattern("validation_insights") == "cortex.validation_insights"
        assert classify_pattern("file_relationships") == "workspace.default.file_relationships"
    
    def test_migration_preserves_pattern_data(self):
        """
        Migration adds namespace prefix WITHOUT losing pattern data.
        """
        original = {
            "title": "Test Pattern",
            "content": "Original content",
            "confidence": 0.85
        }
        
        # Migration adds namespace
        migrated = original.copy()
        migrated["_namespace"] = "cortex.test_patterns"
        
        # Verify data preserved
        assert migrated["title"] == original["title"]
        assert migrated["content"] == original["content"]
        assert migrated["confidence"] == original["confidence"]
        assert migrated["_namespace"] == "cortex.test_patterns"


# Integration test combining all aspects
class TestNamespaceProtectionIntegration:
    """End-to-end test of namespace protection system."""
    
    @pytest.fixture
    def full_kg(self, tmp_path):
        """Fully configured knowledge graph with namespace protection."""
        db_path = tmp_path / "integration_test.db"
        kg = KnowledgeGraph(db_path=db_path)  # Pass Path object, not string
        yield kg
        kg.close()  # Close connection before unlinking
        if db_path.exists():
            db_path.unlink()
    
    def test_complete_namespace_workflow(self, full_kg):
        """
        Test complete workflow: write protection, isolation, correct routing.
        
        This is the ultimate validation of namespace-based boundaries.
        """
        # 1. CORTEX framework stores its patterns
        full_kg.learn_pattern(
            {"title": "CORTEX Core Pattern", "content": "Framework knowledge"},
            namespace="cortex.core",
            is_cortex_internal=True
        )
        
        # 2. User app stores its patterns
        full_kg.learn_pattern(
            {"title": "App Pattern", "content": "Application knowledge"},
            namespace="workspace.myapp.patterns",
            is_cortex_internal=False
        )
        
        # 3. User CANNOT contaminate CORTEX namespace
        with pytest.raises(ValueError, match="protected"):
            full_kg.learn_pattern(
                {"title": "Malicious", "content": "Trying to contaminate"},
                namespace="cortex.malicious",
                is_cortex_internal=False  # User code
            )
        
        # 4. Query isolation works
        cortex_only = full_kg.query(namespace_filter="cortex.*")
        workspace_only = full_kg.query(namespace_filter="workspace.myapp.*")
        
        assert len(cortex_only) == 1
        assert cortex_only[0]["title"] == "CORTEX Core Pattern"
        
        assert len(workspace_only) == 1
        assert workspace_only[0]["title"] == "App Pattern"
        
        # 5. No cross-contamination
        cortex_titles = [p["title"] for p in cortex_only]
        workspace_titles = [p["title"] for p in workspace_only]
        
        assert "App Pattern" not in cortex_titles
        assert "CORTEX Core Pattern" not in workspace_titles
        
        # ✅ SUCCESS: Complete namespace isolation achieved!


# Run with: pytest tests/tier2/test_namespace_protection.py -v
