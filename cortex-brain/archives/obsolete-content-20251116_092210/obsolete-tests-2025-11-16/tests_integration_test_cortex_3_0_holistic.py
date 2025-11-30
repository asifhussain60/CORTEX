"""
CORTEX 3.0 Holistic Integration Test
Tests complete integration of all major components working together.
"""

import pytest
import sqlite3
from pathlib import Path
from datetime import datetime
import tempfile
import shutil


class TestCortex30HolisticIntegration:
    """Comprehensive integration tests for CORTEX 3.0 architecture."""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing."""
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / "test_memory.db"
        yield db_path
        shutil.rmtree(temp_dir)
    
    def test_tier0_protection_system_loads(self):
        """Test Tier 0: Brain Protection System loads correctly."""
        from src.tier0.brain_protector import BrainProtector
        
        bp = BrainProtector()
        
        # Verify YAML config loaded
        assert bp.rules_config is not None, "Rules config should be loaded"
        assert 'protection_layers' in bp.rules_config, "Should have protection layers"
        assert 'tier0_instincts' in bp.rules_config, "Should have tier0 instincts"
        
        # Verify critical rules present
        instincts = bp.TIER0_INSTINCTS
        assert 'TDD_ENFORCEMENT' in instincts, "TDD enforcement required"
        assert 'DEFINITION_OF_DONE' in instincts, "Definition of Done required"
        assert any('SKULL' in i for i in instincts), "SKULL rules required"
        
        print(f"✅ Tier 0: {len(bp.protection_layers)} layers, {len(instincts)} instincts")
    
    def test_tier1_working_memory_integration(self, temp_db):
        """Test Tier 1: Working Memory with CORTEX 3.0 features."""
        from src.tier1.working_memory import WorkingMemory
        
        # Initialize working memory
        wm = WorkingMemory(db_path=temp_db)
        
        # Test session management (CORTEX 3.0)
        assert wm.session_manager is not None, "Session manager should exist"
        assert wm.lifecycle_manager is not None, "Lifecycle manager should exist"
        assert wm.session_correlator is not None, "Session correlator should exist"
        
        # Test creating a session and conversation
        result = wm.handle_user_request(
            user_request="test implementation request",
            workspace_path="/test/workspace",
            assistant_response="implementing test"
        )
        
        assert result is not None, "Should return result"
        assert 'session_id' in result, "Should have session_id"
        assert 'conversation_id' in result, "Should have conversation_id"
        assert result['is_new_session'] is True, "Should be new session"
        
        print(f"✅ Tier 1: Session {result['session_id'][:8]}... created")
    
    def test_tier1_ambient_correlation(self, temp_db):
        """Test Tier 1: Ambient event correlation (CORTEX 3.0)."""
        from src.tier1.working_memory import WorkingMemory
        
        wm = WorkingMemory(db_path=temp_db)
        
        # Create session and conversation
        result = wm.handle_user_request(
            user_request="implement feature",
            workspace_path="/test/workspace",
            assistant_response="creating feature"
        )
        
        session_id = result['session_id']
        conversation_id = result['conversation_id']
        
        # Log ambient event
        event_id = wm.log_ambient_event(
            session_id=session_id,
            conversation_id=conversation_id,
            event_type="file_change",
            file_path="/test/file.py",
            pattern="FEATURE",
            score=90,
            summary="Created feature module"
        )
        
        assert event_id is not None, "Event should be logged"
        
        # Query events
        events = wm.get_session_events(session_id)
        assert len(events) > 0, "Should have events"
        assert events[0]['event_type'] == 'file_change', "Should be file change event"
        
        print(f"✅ Tier 1 Ambient: Logged event {event_id}")
    
    def test_tier2_knowledge_graph_accessible(self):
        """Test Tier 2: Knowledge Graph is accessible."""
        try:
            from src.tier2.knowledge_graph.knowledge_graph import KnowledgeGraph
            
            kg = KnowledgeGraph()
            
            # Test basic operations
            assert hasattr(kg, 'add_pattern'), "Should have add_pattern method"
            assert hasattr(kg, 'search'), "Should have search method"
            
            print("✅ Tier 2: Knowledge Graph accessible")
        except ImportError as e:
            pytest.skip(f"Tier 2 not available: {e}")
    
    def test_agent_coordination_intent_router(self):
        """Test Agent Coordination: Intent Router functional."""
        from src.cortex_agents.intent_router import IntentRouter
        from src.cortex_agents.base_agent import AgentRequest
        
        # Create intent router (minimal initialization)
        router = IntentRouter("test_router", None, None, None)
        
        # Test intent classification
        request = AgentRequest(
            intent="unknown",
            context={},
            user_message="plan a new authentication system"
        )
        
        classified_intent = router._classify_intent(request)
        assert classified_intent is not None, "Should classify intent"
        
        print(f"✅ Intent Router: Classified as {classified_intent.value}")
    
    def test_agent_coordination_investigation_router(self):
        """Test Agent Coordination: Investigation Router accessible."""
        from src.cortex_agents.intent_router import IntentRouter
        
        # Create intent router
        router = IntentRouter("test_router", None, None, None)
        
        # Check investigation router initialized
        assert hasattr(router, 'investigation_router'), "Should have investigation router"
        
        # Test investigation detection
        test_message = "investigate why the authentication is failing"
        is_investigation = router._is_investigation_request(test_message)
        
        assert is_investigation is True, "Should detect investigation request"
        
        print("✅ Investigation Router: Detection working")
    
    def test_holistic_workflow_simulation(self, temp_db):
        """Test complete workflow: User request → Session → Conversation → Ambient → Router."""
        from src.tier1.working_memory import WorkingMemory
        from src.cortex_agents.intent_router import IntentRouter
        from src.cortex_agents.base_agent import AgentRequest
        
        # 1. Initialize working memory
        wm = WorkingMemory(db_path=temp_db)
        
        # 2. Simulate user request
        user_request = "implement a purple button in the dashboard"
        workspace = "/test/app"
        
        result = wm.handle_user_request(
            user_request=user_request,
            workspace_path=workspace,
            assistant_response="I'll create the purple button component"
        )
        
        assert result['session_id'], "Should create session"
        assert result['conversation_id'], "Should create conversation"
        
        session_id = result['session_id']
        conversation_id = result['conversation_id']
        
        # 3. Route intent
        router = IntentRouter("router", None, None, None)
        request = AgentRequest(
            intent="unknown",
            context={},
            user_message=user_request,
            conversation_id=conversation_id
        )
        
        classified_intent = router._classify_intent(request)
        assert classified_intent.value in ['code', 'execute'], "Should route to execution"
        
        # 4. Log ambient event (file creation)
        event_id = wm.log_ambient_event(
            session_id=session_id,
            conversation_id=conversation_id,
            event_type="file_change",
            file_path="/test/app/components/PurpleButton.tsx",
            pattern="FEATURE",
            score=95,
            summary="Created purple button component"
        )
        
        assert event_id, "Should log ambient event"
        
        # 5. Generate narrative
        narrative = wm.generate_session_narrative(session_id)
        assert narrative, "Should generate narrative"
        assert "implement a purple button" in narrative.lower(), "Narrative should contain request"
        
        print("✅ Holistic Workflow: Complete integration successful")
        print(f"   Session: {session_id[:8]}...")
        print(f"   Conversation: {conversation_id[:8]}...")
        print(f"   Intent: {classified_intent.value}")
        print(f"   Event: {event_id}")
    
    def test_entry_points_exist(self):
        """Test Entry Points: CORTEX.prompt.md and copilot-instructions.md exist."""
        cortex_prompt = Path(".github/prompts/CORTEX.prompt.md")
        copilot_instructions = Path(".github/copilot-instructions.md")
        
        assert cortex_prompt.exists(), "CORTEX.prompt.md should exist"
        assert copilot_instructions.exists(), "copilot-instructions.md should exist"
        
        # Check for CORTEX 3.0 references
        content = cortex_prompt.read_text(encoding='utf-8')
        assert "Session" in content or "session" in content, "Should mention sessions"
        
        print("✅ Entry Points: CORTEX.prompt.md and copilot-instructions.md present")
    
    def test_health_check_system(self):
        """Test Health Check System: check_brain_health.py works."""
        import subprocess
        import sys
        
        result = subprocess.run(
            [sys.executable, "check_brain_health.py"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        assert result.returncode in [0, 1], "Health check should run (exit 0 or 1)"
        assert "CORTEX HEALTH REPORT" in result.stdout, "Should generate report"
        assert "Tier 0:" in result.stdout or "TIER 0:" in result.stdout, "Should check Tier 0"
        assert "Tier 1:" in result.stdout or "TIER 1:" in result.stdout, "Should check Tier 1"
        
        print("✅ Health Check System: Comprehensive diagnostics operational")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
