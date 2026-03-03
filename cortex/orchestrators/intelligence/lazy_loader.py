"""
Lazy Loading System for Agent Architecture (phase-81 S1).

Implements intent-based agent loading to reduce token consumption from 245k to ~30k at initialization.

Authority: cortex-registry/_cortex-master/index.yaml WAVE-L
Created: 2026-02-12
AC-ID: AC-WAVE-L-001
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set
import yaml


class IntentType(str, Enum):  # noqa: CORE-035-scoped — lazy loader uses uppercase routing values
    """User intent classifications."""
    IMPLEMENT = "IMPLEMENT"
    FIX = "FIX"
    REFACTOR = "REFACTOR"
    ANALYZE = "ANALYZE"
    AUDIT = "AUDIT"
    DESIGN = "DESIGN"
    PLAN = "PLAN"
    DIGEST = "DIGEST"
    QUERY = "QUERY"


@dataclass
class AgentMetadata:
    """Metadata for a single agent."""

    name: str
    file_path: Path
    capabilities: Set[str] = field(default_factory=set)
    intents: Set[IntentType] = field(default_factory=set)
    token_cost: int = 0  # Estimated token cost when loaded
    priority: int = 0  # Load priority (lower = higher priority)

    def __hash__(self):
        """Make hashable for set operations."""
        return hash(self.name)


class IntentAgentMapper:
    """
    Maps intents to required agents for lazy loading.

    Token Savings:
    - Eager loading: 245k tokens (all 11 agents at session start)
    - Intent-based: ~30k tokens (load only what's needed)
    - Reduction: 88% token savings
    """

    # Intent → Agent mapping (based on capability analysis)
    INTENT_AGENT_MAP: Dict[IntentType, Set[str]] = {
        IntentType.IMPLEMENT: {
            "cortex-executor",
            "cortex-architect",
            "cortex-holistic-validator",
        },
        IntentType.FIX: {
            "cortex-executor",
            "cortex-auditor",
            "cortex-holistic-validator",
        },
        IntentType.REFACTOR: {
            "cortex-executor",
            "cortex-architect",
            "cortex-auditor",
        },
        IntentType.ANALYZE: {
            "cortex-auditor",
            "cortex-holistic-validator",
            "cortex-meta-auditor",
        },
        IntentType.AUDIT: {
            "cortex-auditor",
            "cortex-meta-auditor",
            "cortex-master-plan-auditor",
        },
        IntentType.DESIGN: {
            "cortex-designer",
            "cortex-architect",
            "cortex-holistic-validator",
        },
        IntentType.PLAN: {
            "cortex-phase-resolver",
            "master-planner",
            "cortex-master-plan-auditor",
        },
        IntentType.DIGEST: {
            "cortex-digest",
            "cortex-meta-auditor",
        },
        IntentType.QUERY: {
            "cortex-storyteller",
            "cortex-documentation-architect",
        },
    }

    def __init__(self, agents_dir: Optional[Path] = None) -> None:
        """
        Initialize the mapper.

        Args:
            agents_dir: Path to .github/agents/core/ directory
        """
        if agents_dir is None:
            # Default to .github/agents/core/ relative to project root
            agents_dir = Path(__file__).parent.parent.parent / ".github" / "agents" / "core"

        self.agents_dir = agents_dir
        self.agent_registry: Dict[str, AgentMetadata] = {}
        self._build_registry()

    def _build_registry(self) -> None:
        """Build agent registry from filesystem."""
        if not self.agents_dir.exists():
            return

        for agent_file in self.agents_dir.glob("*.md"):
            agent_name = agent_file.stem

            # Skip internal files
            if agent_name.upper() == agent_name:  # ALL CAPS = internal doc
                continue

            # Parse metadata from file (if YAML frontmatter exists)
            metadata = self._parse_agent_metadata(agent_file)

            if metadata:
                self.agent_registry[agent_name] = metadata

    def _parse_agent_metadata(self, file_path: Path) -> Optional[AgentMetadata]:
        """
        Parse agent metadata from markdown file.

        Args:
            file_path: Path to agent markdown file

        Returns:
            AgentMetadata if parsable, None otherwise
        """
        try:
            content = file_path.read_text()

            # Try to extract YAML frontmatter
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    try:
                        frontmatter = yaml.safe_load(parts[1])
                        if frontmatter:
                            return AgentMetadata(
                                name=file_path.stem,
                                file_path=file_path,
                                capabilities=set(frontmatter.get("capabilities", [])),
                                intents=set(
                                    IntentType(i) for i in frontmatter.get("intents", [])
                                    if i in IntentType.__members__
                                ),
                                token_cost=frontmatter.get("token_cost", 15000),
                                priority=frontmatter.get("priority", 50),
                            )
                    except yaml.YAMLError:
                        pass

            # Fallback: create basic metadata
            return AgentMetadata(
                name=file_path.stem,
                file_path=file_path,
                token_cost=15000,  # Conservative estimate
                priority=50,
            )

        except Exception:
            return None

    def get_agents_for_intent(self, intent: IntentType) -> List[AgentMetadata]:
        """
        Get required agents for a given intent.

        Args:
            intent: User intent type

        Returns:
            List of agent metadata, sorted by priority
        """
        agent_names = self.INTENT_AGENT_MAP.get(intent, set())

        agents = [
            self.agent_registry[name]
            for name in agent_names
            if name in self.agent_registry
        ]

        # Sort by priority (lower = higher priority)
        return sorted(agents, key=lambda a: a.priority)

    def get_token_cost(self, intent: IntentType) -> int:
        """
        Calculate total token cost for loading agents for an intent.

        Args:
            intent: User intent type

        Returns:
            Total token cost
        """
        agents = self.get_agents_for_intent(intent)
        return sum(a.token_cost for a in agents)

    def get_all_agents(self) -> List[AgentMetadata]:
        """
        Get all registered agents.

        Returns:
            List of all agent metadata, sorted by priority
        """
        return sorted(self.agent_registry.values(), key=lambda a: a.priority)

    def get_token_savings(self, intent: IntentType) -> Dict[str, float]:
        """
        Calculate token savings from lazy loading.

        Args:
            intent: User intent type

        Returns:
            Dictionary with token metrics
        """
        all_agents_cost = sum(a.token_cost for a in self.agent_registry.values())
        intent_agents_cost = self.get_token_cost(intent)

        return {
            "eager_loading": float(all_agents_cost),
            "lazy_loading": float(intent_agents_cost),
            "savings": float(all_agents_cost - intent_agents_cost),
            "savings_percent": round(
                ((all_agents_cost - intent_agents_cost) / all_agents_cost) * 100, 1
            ) if all_agents_cost > 0 else 0.0,
        }


def load_agents_for_intent(
    intent: IntentType,
    agents_dir: Optional[Path] = None
) -> List[AgentMetadata]:
    """
    Load agents required for a specific intent (lazy loading).

    Args:
        intent: User intent type
        agents_dir: Optional custom agents directory

    Returns:
        List of agent metadata required for the intent

    Example:
        >>> agents = load_agents_for_intent(IntentType.IMPLEMENT)
        >>> print(f"Loaded {len(agents)} agents")
        Loaded 3 agents
    """
    mapper = IntentAgentMapper(agents_dir=agents_dir)
    return mapper.get_agents_for_intent(intent)
