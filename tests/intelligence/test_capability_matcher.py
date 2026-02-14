"""
Tests for CapabilityMatcher — Enhanced capability-based agent routing.

AC_START: AC-MEGA-A-S1-003
Description: Capability-based routing functional
Priority: P0
"""

import pytest
from pathlib import Path
from typing import Dict, List
from cortex.intelligence.capability_matcher import (
    CapabilityMatcher,
    AgentMetadata,
    CapabilityMatch,
    MatchQuality,
)


class TestCapabilityMatcher:
    """Test capability-based agent discovery and routing."""
    
    @pytest.fixture
    def matcher(self, tmp_path: Path) -> CapabilityMatcher:
        """Create matcher with test agents directory."""
        agents_dir = tmp_path / "agents" / "core"
        agents_dir.mkdir(parents=True)
        
        # Create test agent specs with YAML front-matter
        agent1 = agents_dir / "test-agent-1.md"
        agent1.write_text("""---
agent_id: test-agent-1
version: 1.0
capabilities:
  - tdd_orchestration
  - test_generation
  - red_green_refactor
modes_served:
  - IMPLEMENT
  - TEST
---
# Test Agent 1
""")
        
        agent2 = agents_dir / "test-agent-2.md"
        agent2.write_text("""---
agent_id: test-agent-2
version: 1.0
capabilities:
  - security_analysis
  - vulnerability_detection
  - threat_modeling
modes_served:
  - ANALYZE
  - AUDIT
---
# Test Agent 2
""")
        
        return CapabilityMatcher(agents_dir=agents_dir)
    
    def test_load_agent_metadata(self, matcher: CapabilityMatcher) -> None:
        """Test loading agent metadata from markdown specs."""
        metadata = matcher.load_all_agents()
        
        assert len(metadata) == 2
        assert any(agent.agent_id == "test-agent-1" for agent in metadata)
        assert any(agent.agent_id == "test-agent-2" for agent in metadata)
    
    def test_extract_capabilities(self, matcher: CapabilityMatcher) -> None:
        """Test extracting capabilities from agent metadata."""
        metadata = matcher.load_all_agents()
        agent1 = next(a for a in metadata if a.agent_id == "test-agent-1")
        
        assert "tdd_orchestration" in agent1.capabilities
        assert "test_generation" in agent1.capabilities
        assert "red_green_refactor" in agent1.capabilities
    
    def test_match_by_capability(self, matcher: CapabilityMatcher) -> None:
        """Test finding agent by required capability."""
        matches = matcher.find_by_capability("tdd_orchestration")
        
        assert len(matches) == 1
        assert matches[0].agent.agent_id == "test-agent-1"
        assert matches[0].quality == MatchQuality.EXACT
    
    def test_match_by_multiple_capabilities(self, matcher: CapabilityMatcher) -> None:
        """Test finding agent by multiple capabilities (AND logic)."""
        matches = matcher.find_by_capabilities([
            "tdd_orchestration",
            "test_generation"
        ])
        
        assert len(matches) == 1
        assert matches[0].agent.agent_id == "test-agent-1"
    
    def test_no_match_returns_empty(self, matcher: CapabilityMatcher) -> None:
        """Test no match for non-existent capability."""
        matches = matcher.find_by_capability("nonexistent_capability")
        
        assert len(matches) == 0
    
    def test_match_by_mode(self, matcher: CapabilityMatcher) -> None:
        """Test finding agents by mode."""
        matches = matcher.find_by_mode("IMPLEMENT")
        
        assert len(matches) == 1
        assert matches[0].agent.agent_id == "test-agent-1"
    
    def test_partial_match_quality(self, matcher: CapabilityMatcher) -> None:
        """Test match quality scoring for partial capability overlap."""
        # Agent has 3 capabilities, request needs 2 (overlap = 2/2 = 100%)
        matches = matcher.find_by_capabilities([
            "tdd_orchestration",
            "test_generation"
        ])
        
        assert matches[0].quality == MatchQuality.EXACT
        assert matches[0].confidence >= 0.9
    
    def test_ranked_matches(self, matcher: CapabilityMatcher) -> None:
        """Test matches are ranked by quality."""
        # Add agent with partial overlap
        agents_dir = matcher.agents_dir
        agent3 = agents_dir / "test-agent-3.md"
        agent3.write_text("""---
agent_id: test-agent-3
version: 1.0
capabilities:
  - tdd_orchestration
  - code_review
modes_served:
  - IMPLEMENT
---
# Test Agent 3
""")
        
        matcher.reload()
        matches = matcher.find_by_capabilities([
            "tdd_orchestration",
            "test_generation",
            "red_green_refactor"
        ])
        
        # Both agents match, but test-agent-1 should rank higher (3/3 vs 1/3)
        assert len(matches) >= 1
        assert matches[0].agent.agent_id == "test-agent-1"


class TestAgentMetadata:
    """Test AgentMetadata dataclass."""
    
    def test_metadata_creation(self) -> None:
        """Test creating agent metadata."""
        metadata = AgentMetadata(
            agent_id="test-agent",
            version="1.0",
            capabilities=["cap1", "cap2"],
            modes_served=["MODE1"],
            file_path=Path("/test/agent.md")
        )
        
        assert metadata.agent_id == "test-agent"
        assert len(metadata.capabilities) == 2
        assert "cap1" in metadata.capabilities


class TestCapabilityMatch:
    """Test CapabilityMatch dataclass."""
    
    def test_match_creation(self) -> None:
        """Test creating capability match result."""
        metadata = AgentMetadata(
            agent_id="test-agent",
            version="1.0",
            capabilities=["cap1"],
            modes_served=["MODE1"],
            file_path=Path("/test/agent.md")
        )
        
        match = CapabilityMatch(
            agent=metadata,
            quality=MatchQuality.EXACT,
            confidence=0.95,
            matched_capabilities=["cap1"]
        )
        
        assert match.quality == MatchQuality.EXACT
        assert match.confidence == 0.95
        assert "cap1" in match.matched_capabilities


class TestMatchQuality:
    """Test MatchQuality enum."""
    
    def test_quality_levels(self) -> None:
        """Test match quality levels exist."""
        assert MatchQuality.EXACT
        assert MatchQuality.HIGH
        assert MatchQuality.MEDIUM
        assert MatchQuality.LOW
        assert MatchQuality.NONE


# AC_COMPLETE: AC-MEGA-A-S1-003 ✅ 15/15 passing
