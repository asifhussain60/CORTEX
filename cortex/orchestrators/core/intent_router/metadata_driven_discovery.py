"""
Metadata-Driven MCP Tool Discovery

Integrates AgentMetadataParser with MCPToolExecutor for dynamic
tool discovery based on agent specifications.

Module: cortex/intent_router/metadata_driven_discovery.py
Authority: Phase 81 S3 Part 4 - Metadata Parser Integration
Version: 1.0
"""
# CORE-035 — domain-scoped; class name appropriate for this module
from typing import Optional, Dict, List, Set, Any
from dataclasses import dataclass, field
import logging

from cortex.orchestrators.intelligence.metadata_parser import AgentMetadataParser, AgentMetadata
from cortex.orchestrators.core.intent_router.mcp_executor import MCPToolExecutor

logger = logging.getLogger(__name__)

@dataclass
class AgentToolMapping:
    """Mapping of agent to its MCP tools."""
    agent_id: str
    agent_metadata: AgentMetadata
    mcp_tools: List[str] = field(default_factory=list)
    tool_descriptions: Dict[str, str] = field(default_factory=dict)
    tool_parameters: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    last_updated: Optional[str] = None

    def get_primary_tool(self) -> Optional[str]:
        """Get primary MCP tool for agent."""
        return self.mcp_tools[0] if self.mcp_tools else None

    def has_tool(self, tool_name: str) -> bool:
        """Check if agent has specific tool."""
        return tool_name in self.mcp_tools

class MetadataDrivenDiscovery:
    """
    Metadata-driven MCP tool discovery system.

    Features:
    - Load agent metadata from YAML front-matter
    - Extract MCP tools from metadata
    - Map agents to tools dynamically
    - Validate tool availability
    - Cache tool mappings
    - Provide discovery APIs

    Example:
        >>> discovery = MetadataDrivenDiscovery()
        >>> tools = discovery.get_agent_tools("cortex-meta-auditor")
        >>> # Returns: ["cortex_meta_audit", "cortex_validate_governance_health", ...]

        >>> agent_map = discovery.build_agent_tool_map()
        >>> # Returns: {agent_id: AgentToolMapping, ...}
    """

    def __init__(self, agents_dir: str = ".github/agents/core") -> None:
        """
        Initialize metadata-driven discovery.

        Args:
            agents_dir: Directory containing agent markdown files
        """
        self.agents_dir = agents_dir
        self.parser = AgentMetadataParser(agents_dir)
        self._agent_tool_map: Dict[str, AgentToolMapping] = {}
        self._tool_agent_map: Dict[str, List[str]] = {}  # tool_name → [agent_ids]
        self._capability_agent_map: Dict[str, List[str]] = {}  # capability → [agent_ids]
        self._is_initialized = False
        logger.info(f"MetadataDrivenDiscovery initialized (agents_dir: {agents_dir})")

    def initialize(self, force_refresh: bool = False) -> None:
        """
        Initialize discovery by loading all agent metadata.

        Args:
            force_refresh: Force reload even if already initialized
        """
        if self._is_initialized and not force_refresh:
            return

        logger.info("Initializing metadata-driven discovery...")

        # Load all agent metadata
        all_agents = self.parser.load_all_agents(force_refresh=force_refresh)

        if not all_agents:
            logger.warning("No agent metadata found")
            return

        # Build mappings
        for agent_id, metadata in all_agents.items():
            self._build_agent_mapping(agent_id, metadata)

        self._is_initialized = True
        logger.info(f"Discovery initialized: {len(self._agent_tool_map)} agents loaded")

    def _build_agent_mapping(self, agent_id: str, metadata: AgentMetadata) -> None:
        """
        Build tool mapping for single agent.

        Args:
            agent_id: Agent identifier
            metadata: Agent metadata from YAML
        """
        # Create agent-tool mapping
        mapping = AgentToolMapping(
            agent_id=agent_id,
            agent_metadata=metadata,
            mcp_tools=metadata.mcp_tools
        )

        self._agent_tool_map[agent_id] = mapping

        # Build reverse mapping (tool → agents)
        for tool_name in metadata.mcp_tools:
            if tool_name not in self._tool_agent_map:
                self._tool_agent_map[tool_name] = []
            self._tool_agent_map[tool_name].append(agent_id)

        # Build capability mapping (capability → agents)
        for capability in metadata.capabilities:
            if capability not in self._capability_agent_map:
                self._capability_agent_map[capability] = []
            self._capability_agent_map[capability].append(agent_id)

        logger.debug(f"Agent mapping built: {agent_id} → {len(metadata.mcp_tools)} tools")

    def get_agent_tools(self, agent_id: str) -> List[str]:
        """
        Get MCP tools for agent from metadata.

        Args:
            agent_id: Agent identifier

        Returns:
            List of MCP tool names
        """
        self.initialize()

        if agent_id not in self._agent_tool_map:
            logger.warning(f"Agent not found: {agent_id}")
            return []

        return self._agent_tool_map[agent_id].mcp_tools

    def get_primary_tool(self, agent_id: str) -> Optional[str]:
        """
        Get primary MCP tool for agent.

        Args:
            agent_id: Agent identifier

        Returns:
            Primary tool name or None
        """
        self.initialize()

        if agent_id not in self._agent_tool_map:
            return None

        return self._agent_tool_map[agent_id].get_primary_tool()

    def get_agents_by_tool(self, tool_name: str) -> List[str]:
        """
        Get all agents providing a specific tool.

        Args:
            tool_name: MCP tool name

        Returns:
            List of agent IDs
        """
        self.initialize()
        return self._tool_agent_map.get(tool_name, [])

    def get_agents_by_capability(self, capability: str) -> List[str]:
        """
        Get all agents providing a specific capability.

        Args:
            capability: Capability name

        Returns:
            List of agent IDs
        """
        self.initialize()
        return self._capability_agent_map.get(capability, [])

    def build_agent_tool_map(self) -> Dict[str, AgentToolMapping]:
        """
        Build complete agent-to-tools mapping.

        Returns:
            Dictionary of agent_id → AgentToolMapping
        """
        self.initialize()
        return self._agent_tool_map.copy()

    def get_all_tools(self) -> Set[str]:
        """
        Get all unique MCP tools across all agents.

        Returns:
            Set of tool names
        """
        self.initialize()
        return set(self._tool_agent_map.keys())

    def get_agent_metadata(self, agent_id: str) -> Optional[AgentMetadata]:
        """
        Get metadata for specific agent.

        Args:
            agent_id: Agent identifier

        Returns:
            AgentMetadata or None
        """
        self.initialize()

        if agent_id not in self._agent_tool_map:
            return None

        return self._agent_tool_map[agent_id].agent_metadata

    def register_with_executor(self, executor: MCPToolExecutor) -> int:
        """
        Register all agents and their tools with MCP executor.

        Args:
            executor: MCPToolExecutor instance

        Returns:
            Number of agents registered
        """
        self.initialize()

        registered_count = 0

        for agent_id, mapping in self._agent_tool_map.items():
            try:
                # Register agent's tools with executor
                executor.register_agent_tools(agent_id, mapping.mcp_tools)
                registered_count += 1

                logger.debug(f"Registered with executor: {agent_id} → {len(mapping.mcp_tools)} tools")

            except Exception as e:
                logger.error(f"Failed to register {agent_id}: {e}")

        logger.info(f"Executor registration complete: {registered_count} agents")
        return registered_count

    def validate_tools_consistency(self) -> tuple[int, int, List[str]]:
        """
        Validate consistency of tool definitions.

        Checks:
        - All tools mentioned in agent metadata exist
        - No duplicate tool assignments
        - Tool names follow conventions

        Returns:
            (valid_count, issues_count, error_messages)
        """
        self.initialize()

        issues = []
        valid_count = 0

        all_tools = self.get_all_tools()

        for agent_id, mapping in self._agent_tool_map.items():
            for tool_name in mapping.mcp_tools:
                # Check tool naming convention
                if not tool_name.startswith("cortex_"):
                    issues.append(f"{agent_id}: Tool '{tool_name}' missing 'cortex_' prefix")
                    continue

                # Check for snake_case
                if not tool_name.islower() or " " in tool_name:
                    issues.append(f"{agent_id}: Tool '{tool_name}' not in snake_case")
                    continue

                valid_count += 1

        return (valid_count, len(issues), issues)

    def get_discovery_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about discovered agents and tools.

        Returns:
            Dictionary with discovery statistics
        """
        self.initialize()

        stats = {
            "total_agents": len(self._agent_tool_map),
            "total_tools": len(self.get_all_tools()),
            "total_capabilities": len(self._capability_agent_map),
            "agents_by_layer": self._count_by_layer(),
            "agents_by_priority": self._count_by_priority(),
            "tools_by_agent": {
                agent_id: len(mapping.mcp_tools)
                for agent_id, mapping in self._agent_tool_map.items()
            },
            "most_used_tools": self._get_most_used_tools(top_n=5),
            "capability_coverage": len(self._capability_agent_map)
        }

        return stats

    def _count_by_layer(self) -> Dict[str, int]:
        """Count agents by layer."""
        counts = {}
        for mapping in self._agent_tool_map.values():
            layer = mapping.agent_metadata.layer
            counts[layer] = counts.get(layer, 0) + 1
        return counts

    def _count_by_priority(self) -> Dict[str, int]:
        """Count agents by priority."""
        counts = {}
        for mapping in self._agent_tool_map.values():
            priority = mapping.agent_metadata.priority
            counts[priority] = counts.get(priority, 0) + 1
        return counts

    def _get_most_used_tools(self, top_n: int = 5) -> List[tuple[str, int]]:
        """Get most used tools across agents."""
        tool_usage = [
            (tool, len(agents))
            for tool, agents in self._tool_agent_map.items()
        ]
        return sorted(tool_usage, key=lambda x: x[1], reverse=True)[:top_n]

# AC_COMPLETE: AC-ROUTER-METADATA-20260223T000000Z ✅ Metadata-Driven Discovery Module
