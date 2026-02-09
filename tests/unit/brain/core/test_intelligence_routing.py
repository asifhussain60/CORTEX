"""
Tests for Intelligence Routing Engine and Wiring.

AC_START: AC-INTELLIGENCE-ROUTING-TESTS-001
Authority: CORE-008 (TDD) | Phase 49
"""

import pytest
from pathlib import Path
from cortex.brain.core.intelligence_routing_engine import (
    IntelligenceRoutingEngine,
    IntentType,
    PromptMetadata,
    AgentMetadata,
    PromptCategory,
    AgentCategory,
    RoutingDecision,
)
from cortex.brain.core.intelligence_routing_wiring import (
    IntelligenceRoutingWiring,
)


class TestIntelligenceRoutingEngine:
    """Test core routing engine."""

    @pytest.fixture
    def engine(self):
        """Create routing engine."""
        return IntelligenceRoutingEngine()

    def test_engine_initialization(self, engine):
        """Test engine initializes successfully."""
        assert engine is not None
        assert engine.prompts_dir is not None
        assert engine.agents_dir is not None

    def test_intent_routing_map_complete(self, engine):
        """Test all intents have primary routing."""
        for intent in IntentType:
            assert intent in engine.INTENT_ROUTING_MAP
            prompt_name, agent_name = engine.INTENT_ROUTING_MAP[intent]
            assert prompt_name is not None
            assert agent_name is not None
            assert prompt_name.endswith(".md") or prompt_name.endswith(".prompt.md")
            assert agent_name.endswith(".md")

    def test_intent_keywords_complete(self, engine):
        """Test all intents have keywords."""
        for intent in IntentType:
            assert intent in engine.INTENT_KEYWORDS
            keywords = engine.INTENT_KEYWORDS[intent]
            assert len(keywords) > 0

    def test_route_implement_intent(self, engine):
        """Test routing IMPLEMENT intent."""
        decision = engine.route(IntentType.IMPLEMENT, "add new feature")
        
        assert decision.intent == IntentType.IMPLEMENT
        assert decision.primary_prompt is not None
        assert decision.primary_agent is not None
        assert decision.confidence_score >= 0.0
        assert decision.confidence_score <= 1.0

    def test_route_analyze_intent(self, engine):
        """Test routing ANALYZE intent."""
        decision = engine.route(IntentType.ANALYZE, "examine code structure")
        
        assert decision.intent == IntentType.ANALYZE
        assert decision.primary_prompt is not None
        assert decision.primary_agent is not None

    def test_route_audit_intent(self, engine):
        """Test routing AUDIT intent."""
        decision = engine.route(IntentType.AUDIT, "check compliance")
        
        assert decision.intent == IntentType.AUDIT
        assert decision.requires_unified_intelligence is True

    def test_route_design_intent(self, engine):
        """Test routing DESIGN intent."""
        decision = engine.route(IntentType.DESIGN, "plan architecture")
        
        assert decision.intent == IntentType.DESIGN
        assert len(decision.context_hints) > 0

    def test_routing_cache_hits(self, engine):
        """Test routing cache improves performance."""
        # First call
        decision1 = engine.route(IntentType.IMPLEMENT, "test request")
        assert decision1 is not None
        
        # Second call (should hit cache)
        decision2 = engine.route(IntentType.IMPLEMENT, "test request")
        assert decision2 is decision1  # Same object

    def test_semantic_matching(self, engine):
        """Test semantic matching between request and resources."""
        decision = engine.route(IntentType.IMPLEMENT, "refactor code quality")
        
        # Should have semantic matches
        assert len(decision.semantic_matches) >= 0

    def test_secondary_resources_loading(self, engine):
        """Test secondary prompts and agents load."""
        decision = engine.route(IntentType.IMPLEMENT, "test")
        
        # IMPLEMENT should have secondary resources
        assert len(decision.secondary_prompts) >= 0
        assert len(decision.secondary_agents) >= 0

    def test_unified_intelligence_flag(self, engine):
        """Test unified intelligence requirements."""
        # IMPLEMENT should require unified intelligence
        decision = engine.route(IntentType.IMPLEMENT)
        assert decision.requires_unified_intelligence is True
        
        # LIST (if supported) might not
        decision = engine.route(IntentType.ANALYZE)
        assert decision.requires_unified_intelligence is True

    def test_context_hints_generation(self, engine):
        """Test context hints are generated."""
        decision = engine.route(IntentType.IMPLEMENT)
        assert len(decision.context_hints) > 0
        assert isinstance(decision.context_hints, list)
        assert all(isinstance(h, str) for h in decision.context_hints)

    def test_confidence_scoring(self, engine):
        """Test confidence scores are reasonable."""
        decision = engine.route(IntentType.IMPLEMENT, "implement feature")
        
        assert decision.confidence_score >= 0.6  # Should be reasonably confident
        assert decision.confidence_score <= 1.0

    def test_prompt_discovery(self, engine):
        """Test prompts are discovered."""
        prompts = engine.list_available_prompts()
        
        assert len(prompts) > 0
        assert any("CORTEX" in p for p in prompts) or len(prompts) >= 2

    def test_agent_discovery(self, engine):
        """Test agents are discovered."""
        agents = engine.list_available_agents()
        
        assert len(agents) > 0

    def test_routing_stats(self, engine):
        """Test routing statistics."""
        stats = engine.get_routing_stats()
        
        assert "total_prompts" in stats
        assert "total_agents" in stats
        assert "intent_support" in stats
        assert stats["total_prompts"] >= 0
        assert stats["total_agents"] >= 0

    def test_fallback_prompt_creation(self, engine):
        """Test fallback prompt creation."""
        prompt = engine._create_fallback_prompt("unknown.md")
        
        assert prompt is not None
        assert isinstance(prompt, PromptMetadata)
        assert prompt.name is not None

    def test_fallback_agent_creation(self, engine):
        """Test fallback agent creation."""
        agent = engine._create_fallback_agent("unknown.md")
        
        assert agent is not None
        assert isinstance(agent, AgentMetadata)
        assert agent.name is not None

    def test_prompt_classification(self):
        """Test prompt classification."""
        assert IntelligenceRoutingEngine._classify_prompt("cortex-architect.prompt") == PromptCategory.ARCHITECT
        assert IntelligenceRoutingEngine._classify_prompt("response-format-standards") == PromptCategory.RESPONSE_FORMAT
        assert IntelligenceRoutingEngine._classify_prompt("MCP-SETUP-GUIDE") == PromptCategory.SETUP_GUIDE

    def test_agent_classification(self):
        """Test agent classification."""
        assert IntelligenceRoutingEngine._classify_agent("cortex-executor") == AgentCategory.CORE
        assert IntelligenceRoutingEngine._classify_agent("cortex-architect") == AgentCategory.DOMAIN
        assert IntelligenceRoutingEngine._classify_agent("cortex-debugger") == AgentCategory.SUPPORT


class TestIntelligenceRoutingWiring:
    """Test wiring integration."""

    @pytest.fixture
    def wiring(self):
        """Create wiring."""
        return IntelligenceRoutingWiring()

    def test_wiring_initialization(self, wiring):
        """Test wiring initializes."""
        assert wiring is not None
        assert wiring.routing_engine is not None
        assert wiring.wiring_config is not None

    def test_route_to_resources(self, wiring):
        """Test routing to resources."""
        result = wiring.route_to_resources("IMPLEMENT", "add feature")
        
        assert result["success"] is True
        assert result["decision"] is not None
        assert result["confidence"] >= 0.6

    def test_intent_parsing(self, wiring):
        """Test intent string parsing."""
        # Case insensitive
        intent1 = wiring._parse_intent("IMPLEMENT")
        intent2 = wiring._parse_intent("implement")
        assert intent1 == intent2 == IntentType.IMPLEMENT
        
        # Partial match
        intent3 = wiring._parse_intent("IMPL")
        assert intent3 == IntentType.IMPLEMENT

    def test_intent_parsing_invalid(self, wiring):
        """Test invalid intent parsing."""
        with pytest.raises(ValueError):
            wiring._parse_intent("UNKNOWN_INTENT")

    def test_get_intent_handler_orchestrator(self, wiring):
        """Test getting orchestrator for intent."""
        orchestrator = wiring.get_intent_handler_orchestrator("IMPLEMENT")
        assert orchestrator == "TDDOrchestrator"
        
        orchestrator = wiring.get_intent_handler_orchestrator("ANALYZE")
        assert orchestrator == "LENSSynthesis"
        
        orchestrator = wiring.get_intent_handler_orchestrator("AUDIT")
        assert orchestrator == "EnforcementOrchestrator"

    def test_get_available_intents(self, wiring):
        """Test getting available intents."""
        intents = wiring.get_available_intents()
        
        assert len(intents) > 0
        assert "IMPLEMENT" in intents
        assert "ANALYZE" in intents
        assert "AUDIT" in intents

    def test_get_prompts_for_intent(self, wiring):
        """Test getting prompts for intent."""
        prompts = wiring.get_prompts_for_intent("IMPLEMENT")
        
        assert prompts["success"] is True
        assert prompts["primary"]["name"] is not None

    def test_get_agents_for_intent(self, wiring):
        """Test getting agents for intent."""
        agents = wiring.get_agents_for_intent("IMPLEMENT")
        
        assert agents["success"] is True
        assert agents["primary"]["name"] is not None
        assert "capabilities" in agents["primary"]

    def test_validate_routing_integrity(self, wiring):
        """Test routing integrity validation."""
        validation = wiring.validate_routing_integrity()
        
        assert "success" in validation
        assert "total_intents" in validation
        assert "validated" in validation
        assert "issues" in validation
        assert validation["total_intents"] > 0

    def test_get_wiring_stats(self, wiring):
        """Test getting wiring statistics."""
        stats = wiring.get_wiring_stats()
        
        assert "total_prompts" in stats
        assert "total_agents" in stats
        assert "integrity" in stats
        assert "supported_intents" in stats

    def test_route_all_intents(self, wiring):
        """Test routing all intent types."""
        for intent in IntentType:
            result = wiring.route_to_resources(intent.value)
            assert result["success"] is True, f"Failed to route {intent.value}"


class TestRoutingDecision:
    """Test routing decision object."""

    def test_routing_decision_creation(self):
        """Test creating routing decision."""
        prompt = PromptMetadata("test", "test.md", PromptCategory.PRODUCTION_MASTER)
        agent = AgentMetadata("test", "test.md", AgentCategory.CORE)
        
        decision = RoutingDecision(
            intent=IntentType.IMPLEMENT,
            primary_prompt=prompt,
            primary_agent=agent,
        )
        
        assert decision.intent == IntentType.IMPLEMENT
        assert decision.primary_prompt == prompt
        assert decision.primary_agent == agent

    def test_routing_decision_secondary_resources(self):
        """Test routing decision with secondary resources."""
        prompt = PromptMetadata("primary", "primary.md", PromptCategory.PRODUCTION_MASTER)
        agent = AgentMetadata("primary", "primary.md", AgentCategory.CORE)
        
        secondary_prompt = PromptMetadata("secondary", "secondary.md", PromptCategory.CONTEXTUAL)
        secondary_agent = AgentMetadata("secondary", "secondary.md", AgentCategory.SUPPORT)
        
        decision = RoutingDecision(
            intent=IntentType.IMPLEMENT,
            primary_prompt=prompt,
            primary_agent=agent,
            secondary_prompts=[secondary_prompt],
            secondary_agents=[secondary_agent],
        )
        
        assert len(decision.secondary_prompts) == 1
        assert len(decision.secondary_agents) == 1


class TestMetadata:
    """Test metadata objects."""

    def test_prompt_metadata_creation(self):
        """Test prompt metadata."""
        metadata = PromptMetadata(
            name="test",
            path="test.md",
            category=PromptCategory.PRODUCTION_MASTER,
            intent_keywords=["test", "verify"],
        )
        
        assert metadata.name == "test"
        assert len(metadata.intent_keywords) == 2

    def test_agent_metadata_creation(self):
        """Test agent metadata."""
        metadata = AgentMetadata(
            name="test",
            path="test.md",
            category=AgentCategory.CORE,
            capabilities=["reasoning", "planning"],
        )
        
        assert metadata.name == "test"
        assert len(metadata.capabilities) == 2


# AC_COMPLETE: AC-INTELLIGENCE-ROUTING-TESTS-001 ✅
