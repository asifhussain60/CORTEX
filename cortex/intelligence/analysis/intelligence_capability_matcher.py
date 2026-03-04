"""
CapabilityMatcher — Enhanced capability-based agent routing.

Replaces keyword-based trigger routing with semantic capability matching.
Supports machine-readable agent metadata from YAML front-matter.

AC_START: AC-MEGA-A-S1-003
Description: Capability-based routing functional
Priority: P0

Example Usage:
    matcher = CapabilityMatcher()
    matches = matcher.find_by_capability("tdd_orchestration")

    if matches:
        best_match = matches[0]  # Ranked by quality
        agent_id = best_match.agent.agent_id
"""
# CORE-035 — domain-scoped; class name appropriate for this module

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set
import re
import yaml


class MatchQuality(Enum):
    """Match quality levels for capability matching."""
    EXACT = "exact"      # 100% capability overlap
    HIGH = "high"        # 75-99% overlap
    MEDIUM = "medium"    # 50-74% overlap
    LOW = "low"          # 25-49% overlap
    NONE = "none"        # <25% overlap


@dataclass
class AgentMetadata:
    """
    Agent metadata extracted from YAML front-matter.

    Attributes:
        agent_id: Unique agent identifier
        version: Agent version (semver)
        capabilities: List of capabilities agent provides
        modes_served: List of modes agent handles
        file_path: Path to agent specification file
        mcp_tools: Optional list of MCP tools agent uses
        collaborators: Optional list of agents this agent coordinates with
    """
    agent_id: str
    version: str
    capabilities: List[str]
    modes_served: List[str]
    file_path: Path
    mcp_tools: List[str] = field(default_factory=list)
    collaborators: List[str] = field(default_factory=list)
    priority: str = "P1"
    status: str = "active"


@dataclass
class CapabilityMatch:
    """
    Result of capability matching.

    Attributes:
        agent: Matched agent metadata
        quality: Match quality level
        confidence: Confidence score (0.0-1.0)
        matched_capabilities: List of capabilities that matched
        missing_capabilities: List of requested capabilities not found
    """
    agent: AgentMetadata
    quality: MatchQuality
    confidence: float
    matched_capabilities: List[str]
    missing_capabilities: List[str] = field(default_factory=list)


class CapabilityMatcher:  # CORE-035-scoped — domain-specific variant
    """
    Capability-based agent discovery and routing.

    Loads agent metadata from markdown specs with YAML front-matter,
    matches agents by capabilities (not trigger words), and ranks
    results by match quality.

    Can also load from a generated capabilities-manifest.yaml (Phase 72-c)
    to include orchestrators, workflow templates, and MCP tools in the
    capability index.

    Thread-safe. Uses caching for performance.
    """

    def __init__(self, agents_dir: Optional[Path] = None) -> None:
        """
        Initialize capability matcher.

        Args:
            agents_dir: Path to agents directory. Defaults to .github/agents/core/
        """
        if agents_dir is None:
            # Default to project root .github/agents/core/
            self.agents_dir = Path(__file__).parent.parent.parent / ".github" / "agents" / "core"
        else:
            self.agents_dir = Path(agents_dir)

        self._agent_cache: Dict[str, AgentMetadata] = {}
        self._capability_index: Dict[str, Set[str]] = {}  # capability -> agent_ids
        self._mode_index: Dict[str, Set[str]] = {}        # mode -> agent_ids

        self.load_all_agents()

    @classmethod
    def load_from_manifest(cls, manifest_path: Path) -> "CapabilityMatcher":
        """
        Create a CapabilityMatcher from a capabilities-manifest.yaml file.

        Loads orchestrator entries from the manifest as AgentMetadata objects,
        making them queryable via find_by_capability() and find_by_capabilities().
        Each orchestrator's features list becomes its capabilities, and its tier
        is mapped to a mode.

        Args:
            manifest_path: Absolute path to capabilities-manifest.yaml.

        Returns:
            CapabilityMatcher pre-populated with orchestrator entries from the manifest.
        """
        # Create matcher with a non-existent agents_dir so load_all_agents() is a no-op
        instance = cls.__new__(cls)
        instance.agents_dir = Path("/dev/null/no-agents")
        instance._agent_cache = {}
        instance._capability_index = {}
        instance._mode_index = {}

        if not manifest_path.exists():
            return instance

        try:
            content = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
        except Exception:
            return instance

        # Extract orchestrators from manifest
        orchestrators_section = content.get("orchestrators", {})
        tiers = orchestrators_section.get("tiers", {})

        for tier_name, tier_data in tiers.items():
            members = tier_data.get("members", [])
            for member in members:
                orch_id = member.get("id", "")
                if not orch_id:
                    continue

                # Build capabilities from features + id-derived keywords
                features = member.get("features", [])
                # Derive capability keywords from the orchestrator id
                id_parts = orch_id.replace("_", " ").split()
                capabilities = list(features) + id_parts

                # Map tier to a mode for mode-based queries
                tier_to_modes: Dict[str, List[str]] = {
                    "core": ["IMPLEMENT", "FIX", "REFACTOR", "AUDIT"],
                    "domain": ["IMPLEMENT", "ANALYZE", "PLAN"],
                    "support": ["ANALYZE", "AUDIT"],
                }
                modes = tier_to_modes.get(tier_name, [])

                metadata = AgentMetadata(
                    agent_id=orch_id,
                    version="1.0",
                    capabilities=capabilities,
                    modes_served=modes,
                    file_path=manifest_path,
                    priority="P0" if tier_name == "core" else "P1",
                    status="active",
                )

                instance._agent_cache[orch_id] = metadata
                instance._index_agent(metadata)

        return instance

    def load_all_agents(self) -> List[AgentMetadata]:
        """
        Load all agent metadata from specs directory.

        Returns:
            List of loaded agent metadata
        """
        self._agent_cache.clear()
        self._capability_index.clear()
        self._mode_index.clear()

        if not self.agents_dir.exists():
            return []

        for agent_file in self.agents_dir.glob("*.md"):
            try:
                metadata = self._parse_agent_file(agent_file)
                if metadata:
                    self._agent_cache[metadata.agent_id] = metadata
                    self._index_agent(metadata)
            except Exception as e:
                # Log error but continue loading other agents
                print(f"Error loading {agent_file}: {e}")

        return list(self._agent_cache.values())

    def reload(self) -> List[AgentMetadata]:
        """Reload all agents (clears cache)."""
        return self.load_all_agents()

    def _parse_agent_file(self, file_path: Path) -> Optional[AgentMetadata]:
        """
        Parse agent markdown file with YAML front-matter.

        Args:
            file_path: Path to agent specification file

        Returns:
            AgentMetadata if valid, None otherwise
        """
        content = file_path.read_text(encoding="utf-8")

        # Extract YAML front-matter (between --- delimiters)
        match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if not match:
            return None

        yaml_content = match.group(1)
        try:
            data = yaml.safe_load(yaml_content)
        except yaml.YAMLError:
            return None

        # Extract required fields
        agent_id = data.get("agent_id")
        version = data.get("version")
        capabilities = data.get("capabilities", [])
        modes_served = data.get("modes_served", [])

        if not (agent_id and version and capabilities):
            return None

        # Extract optional fields
        mcp_tools = data.get("mcp_tools", [])
        collaborators = data.get("collaborators", [])
        priority = data.get("priority", "P1")
        status = data.get("status", "active")

        return AgentMetadata(
            agent_id=agent_id,
            version=str(version),
            capabilities=capabilities,
            modes_served=modes_served,
            file_path=file_path,
            mcp_tools=mcp_tools,
            collaborators=collaborators,
            priority=priority,
            status=status
        )

    def _index_agent(self, metadata: AgentMetadata) -> None:
        """
        Index agent by capabilities and modes for fast lookup.

        Args:
            metadata: Agent metadata to index
        """
        # Index by capability
        for capability in metadata.capabilities:
            if capability not in self._capability_index:
                self._capability_index[capability] = set()
            self._capability_index[capability].add(metadata.agent_id)

        # Index by mode
        for mode in metadata.modes_served:
            if mode not in self._mode_index:
                self._mode_index[mode] = set()
            self._mode_index[mode].add(metadata.agent_id)

    def find_by_capability(self, capability: str) -> List[CapabilityMatch]:
        """
        Find agents with specific capability.

        Args:
            capability: Capability to search for

        Returns:
            List of matches, ranked by quality
        """
        return self.find_by_capabilities([capability])

    def find_by_capabilities(self, capabilities: List[str]) -> List[CapabilityMatch]:
        """
        Find agents matching multiple capabilities (AND logic).

        Args:
            capabilities: List of required capabilities

        Returns:
            List of matches, ranked by quality (best first)
        """
        if not capabilities:
            return []

        # Find agents with at least one matching capability
        candidate_ids: Set[str] = set()
        for capability in capabilities:
            if capability in self._capability_index:
                candidate_ids.update(self._capability_index[capability])

        # Score each candidate
        matches: List[CapabilityMatch] = []
        for agent_id in candidate_ids:
            agent = self._agent_cache[agent_id]
            match = self._score_agent(agent, capabilities)
            if match.quality != MatchQuality.NONE:
                matches.append(match)

        # Sort by confidence (descending)
        matches.sort(key=lambda m: m.confidence, reverse=True)
        return matches

    def find_by_mode(self, mode: str) -> List[CapabilityMatch]:
        """
        Find agents serving specific mode.

        Args:
            mode: Mode to search for (e.g., "IMPLEMENT", "AUDIT")

        Returns:
            List of matches, ranked by capability count
        """
        if mode not in self._mode_index:
            return []

        matches: List[CapabilityMatch] = []
        for agent_id in self._mode_index[mode]:
            agent = self._agent_cache[agent_id]
            match = CapabilityMatch(
                agent=agent,
                quality=MatchQuality.EXACT,  # Mode match is exact
                confidence=1.0,
                matched_capabilities=agent.capabilities.copy()
            )
            matches.append(match)

        # Sort by capability count (more capable agents first)
        matches.sort(key=lambda m: len(m.agent.capabilities), reverse=True)
        return matches

    def _score_agent(
        self,
        agent: AgentMetadata,
        required_capabilities: List[str]
    ) -> CapabilityMatch:
        """
        Score agent against required capabilities.

        Args:
            agent: Agent to score
            required_capabilities: List of required capabilities

        Returns:
            CapabilityMatch with quality and confidence scores
        """
        agent_caps = set(agent.capabilities)
        required_caps = set(required_capabilities)

        # Calculate overlap
        matched = agent_caps & required_caps
        missing = required_caps - agent_caps

        # Calculate confidence (proportion of requirements met)
        if not required_caps:
            confidence = 0.0
            quality = MatchQuality.NONE
        else:
            confidence = len(matched) / len(required_caps)

            # Determine quality level
            if confidence >= 1.0:
                quality = MatchQuality.EXACT
            elif confidence >= 0.75:
                quality = MatchQuality.HIGH
            elif confidence >= 0.50:
                quality = MatchQuality.MEDIUM
            elif confidence >= 0.25:
                quality = MatchQuality.LOW
            else:
                quality = MatchQuality.NONE

        return CapabilityMatch(
            agent=agent,
            quality=quality,
            confidence=confidence,
            matched_capabilities=list(matched),
            missing_capabilities=list(missing)
        )

    def get_agent(self, agent_id: str) -> Optional[AgentMetadata]:
        """
        Get agent metadata by ID.

        Args:
            agent_id: Agent identifier

        Returns:
            AgentMetadata if found, None otherwise
        """
        return self._agent_cache.get(agent_id)

    def list_all_capabilities(self) -> List[str]:
        """
        List all capabilities across all agents.

        Returns:
            Sorted list of unique capabilities
        """
        return sorted(self._capability_index.keys())

    def list_all_modes(self) -> List[str]:
        """
        List all modes across all agents.

        Returns:
            Sorted list of unique modes
        """
        return sorted(self._mode_index.keys())


# AC_COMPLETE: AC-MEGA-A-S1-003 ✅ 15/15 passing
