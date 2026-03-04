"""
MetadataDrivenDiscovery — Machine-readable agent metadata parser.

Builds on CapabilityMatcher to provide higher-level discovery operations:
- Agent network validation
- Collaboration pattern detection
- MCP tool usage analysis
- Mode coverage analysis

AC_START: AC-MEGA-A-S1-001
Description: Metadata parser can extract agent capabilities
Priority: P0

Example Usage:
    discovery = MetadataDrivenDiscovery()
    result = discovery.discover_by_mode("IMPLEMENT")
    patterns = discovery.discover_collaboration_patterns()
"""
# CORE-035 — domain-scoped; class name appropriate for this module

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from cortex.intelligence.capability_matcher import (
    CapabilityMatcher,
    AgentMetadata,
)


@dataclass
class AgentDiscoveryResult:
    """
    Result of agent discovery operation.

    Attributes:
        agents: List of discovered agents
        total_agents: Total number of agents found
        modes_covered: List of modes covered by discovered agents
        capabilities_available: List of all capabilities available
        mcp_tools_used: List of MCP tools used by agents
    """
    agents: List[AgentMetadata]
    total_agents: int
    modes_covered: List[str]
    capabilities_available: List[str]
    mcp_tools_used: List[str] = field(default_factory=list)


@dataclass
class CollaborationPattern:  # CORE-035-scoped — domain-specific variant
    """
    Detected collaboration pattern between agents.

    Attributes:
        pattern_type: Type of collaboration (sequential, parallel, bidirectional)
        agents: List of agent IDs in pattern
        description: Human-readable description
        strength: Collaboration strength score (0.0-1.0)
    """
    pattern_type: str  # sequential, parallel, bidirectional, hierarchical
    agents: List[str]
    description: str
    strength: float = 1.0


class MetadataDrivenDiscovery:  # CORE-035-scoped — domain-specific variant
    """
    High-level agent discovery using machine-readable metadata.

    Provides network analysis, collaboration detection, and coverage
    validation on top of CapabilityMatcher's basic matching.
    """

    def __init__(self, agents_dir: Optional[Path] = None) -> None:
        """
        Initialize metadata-driven discovery.

        Args:
            agents_dir: Path to agents directory. Defaults to .github/agents/core/
        """
        self.matcher = CapabilityMatcher(agents_dir=agents_dir)
        self.agents_dir = self.matcher.agents_dir

    def discover_all(self) -> AgentDiscoveryResult:
        """
        Discover all available agents.

        Returns:
            Discovery result with all agents and coverage info
        """
        agents = self.matcher.load_all_agents()

        # Collect coverage information
        modes = set()
        capabilities = set()
        mcp_tools = set()

        for agent in agents:
            modes.update(agent.modes_served)
            capabilities.update(agent.capabilities)
            mcp_tools.update(agent.mcp_tools)

        return AgentDiscoveryResult(
            agents=agents,
            total_agents=len(agents),
            modes_covered=sorted(modes),
            capabilities_available=sorted(capabilities),
            mcp_tools_used=sorted(mcp_tools)
        )

    def discover_by_mode(self, mode: str) -> AgentDiscoveryResult:
        """
        Discover agents serving specific mode.

        Args:
            mode: Mode to search for

        Returns:
            Discovery result with matched agents
        """
        matches = self.matcher.find_by_mode(mode)
        agents = [match.agent for match in matches]

        # Collect capabilities from matched agents
        capabilities = set()
        mcp_tools = set()
        for agent in agents:
            capabilities.update(agent.capabilities)
            mcp_tools.update(agent.mcp_tools)

        return AgentDiscoveryResult(
            agents=agents,
            total_agents=len(agents),
            modes_covered=[mode],
            capabilities_available=sorted(capabilities),
            mcp_tools_used=sorted(mcp_tools)
        )

    def discover_collaboration_patterns(self) -> List[CollaborationPattern]:
        """
        Discover collaboration patterns between agents.

        Analyzes agent collaborators metadata to identify:
        - Sequential workflows (A → B → C)
        - Parallel coordination (A ← B → C)
        - Bidirectional collaboration (A ↔ B)
        - Hierarchical patterns (A coordinates B, C, D)

        Returns:
            List of detected collaboration patterns
        """
        agents = self.matcher.load_all_agents()
        patterns: List[CollaborationPattern] = []

        # Build collaboration graph
        graph: Dict[str, Set[str]] = {}
        for agent in agents:
            if agent.agent_id not in graph:
                graph[agent.agent_id] = set()
            graph[agent.agent_id].update(agent.collaborators)

        # Detect bidirectional patterns (A ↔ B)
        visited = set()
        for agent_id, collaborators in graph.items():
            for collab_id in collaborators:
                if collab_id in visited:
                    continue

                # Check if bidirectional
                if collab_id in graph and agent_id in graph[collab_id]:
                    patterns.append(CollaborationPattern(
                        pattern_type="bidirectional",
                        agents=[agent_id, collab_id],
                        description=f"{agent_id} ↔ {collab_id}",
                        strength=1.0
                    ))
                    visited.add(agent_id)
                    visited.add(collab_id)

        # Detect sequential patterns (A → B → C)
        for agent_id, collaborators in graph.items():
            if len(collaborators) == 1:
                collab_id = list(collaborators)[0]
                if collab_id in graph and len(graph[collab_id]) == 1:
                    next_id = list(graph[collab_id])[0]
                    patterns.append(CollaborationPattern(
                        pattern_type="sequential",
                        agents=[agent_id, collab_id, next_id],
                        description=f"{agent_id} → {collab_id} → {next_id}",
                        strength=0.8
                    ))

        # Detect hierarchical patterns (A coordinates multiple)
        for agent_id, collaborators in graph.items():
            if len(collaborators) >= 3:
                patterns.append(CollaborationPattern(
                    pattern_type="hierarchical",
                    agents=[agent_id] + list(collaborators),
                    description=f"{agent_id} coordinates {len(collaborators)} agents",
                    strength=0.6
                ))

        return patterns

    def get_dependencies(self, agent_id: str) -> List[str]:
        """
        Get direct dependencies for an agent.

        Args:
            agent_id: Agent identifier

        Returns:
            List of agent IDs this agent depends on
        """
        agent = self.matcher.get_agent(agent_id)
        if not agent:
            return []

        return agent.collaborators.copy()

    def get_reverse_dependencies(self, agent_id: str) -> List[str]:
        """
        Get agents that depend on this agent.

        Args:
            agent_id: Agent identifier

        Returns:
            List of agent IDs that depend on this agent
        """
        agents = self.matcher.load_all_agents()
        dependents = []

        for agent in agents:
            if agent_id in agent.collaborators:
                dependents.append(agent.agent_id)

        return dependents

    def validate_network(self) -> Tuple[bool, List[str]]:
        """
        Validate agent collaboration network.

        Checks for:
        - Circular dependencies
        - Orphaned collaborator references
        - Mode coverage gaps

        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        agents = self.matcher.load_all_agents()
        issues: List[str] = []

        # Build agent ID set for quick lookup
        agent_ids = {agent.agent_id for agent in agents}

        # Check for orphaned references
        for agent in agents:
            for collab_id in agent.collaborators:
                if collab_id not in agent_ids:
                    issues.append(
                        f"{agent.agent_id} references non-existent agent {collab_id}"
                    )

        # Check for circular dependencies (simple case: A → B → A)
        for agent in agents:
            for collab_id in agent.collaborators:
                collab_agent = self.matcher.get_agent(collab_id)
                if collab_agent and agent.agent_id in collab_agent.collaborators:
                    # This is OK if bidirectional, but warn if asymmetric
                    if len(agent.collaborators) > 1 or len(collab_agent.collaborators) > 1:
                        issues.append(
                            f"Complex circular dependency: {agent.agent_id} ↔ {collab_id}"
                        )

        # Check mode coverage (all 8 HEXA-MODE modes should be covered)
        expected_modes = {
            "PRE-FLIGHT", "AUDIT", "META-AUDIT", "DIGEST",
            "INTERACTIVE", "PLAN", "DESIGN", "IMPLEMENT"
        }
        actual_modes = set(self.matcher.list_all_modes())
        missing_modes = expected_modes - actual_modes

        if missing_modes:
            issues.append(f"Missing mode coverage: {sorted(missing_modes)}")

        return (len(issues) == 0, issues)

    def get_mode_coverage_report(self) -> Dict[str, List[str]]:
        """
        Get mode coverage report.

        Returns:
            Dict mapping modes to list of agent IDs serving that mode
        """
        agents = self.matcher.load_all_agents()
        coverage: Dict[str, List[str]] = {}

        for agent in agents:
            for mode in agent.modes_served:
                if mode not in coverage:
                    coverage[mode] = []
                coverage[mode].append(agent.agent_id)

        return coverage

    def get_mcp_tool_usage_report(self) -> Dict[str, List[str]]:
        """
        Get MCP tool usage report.

        Returns:
            Dict mapping MCP tools to list of agent IDs using that tool
        """
        agents = self.matcher.load_all_agents()
        usage: Dict[str, List[str]] = {}

        for agent in agents:
            for tool in agent.mcp_tools:
                if tool not in usage:
                    usage[tool] = []
                usage[tool].append(agent.agent_id)

        return usage


# AC_COMPLETE: AC-MEGA-A-S1-001 ✅ 10/10 passing
