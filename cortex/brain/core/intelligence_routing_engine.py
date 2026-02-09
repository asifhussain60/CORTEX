"""
Intelligence Routing Engine: Prompt & Agent Orchestration.

Dynamically routes to appropriate prompts and agents based on intent,
providing semantic matching, caching, and holistic context synthesis.

AC_START: AC-INTELLIGENCE-ROUTING-001
Authority: Phase 49 | CORE-047 (No File Paths in Instructions) | CORE-035 (Single Source)
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import logging
import json
from datetime import datetime
import hashlib
import yaml

logger = logging.getLogger(__name__)


class IntentType(Enum):
    """Supported intent types for routing."""
    IMPLEMENT = "IMPLEMENT"
    FIX = "FIX"
    REFACTOR = "REFACTOR"
    ANALYZE = "ANALYZE"
    AUDIT = "AUDIT"
    DESIGN = "DESIGN"
    PLAN = "PLAN"
    ONBOARD = "ONBOARD"
    DEBUG = "DEBUG"
    DIGEST = "DIGEST"


class PromptCategory(Enum):
    """Prompt categories for semantic routing."""
    PRODUCTION_MASTER = "production_master"
    ARCHITECT = "architect"
    RESPONSE_FORMAT = "response_format"
    SETUP_GUIDE = "setup_guide"
    ACTIVATION_CHECKLIST = "activation_checklist"
    CONTEXTUAL = "contextual"


class AgentCategory(Enum):
    """Agent categories for semantic routing."""
    CORE = "core"
    DOMAIN = "domain"
    SUPPORT = "support"
    EDUCATION = "education"


@dataclass
class PromptMetadata:
    """Metadata for prompt files."""
    name: str
    path: str
    category: PromptCategory
    intent_keywords: List[str] = field(default_factory=list)
    min_tokens: int = 0
    max_tokens: int = 50000
    version: str = "1.0"
    last_updated: Optional[str] = None
    requires_context: List[str] = field(default_factory=list)
    cache_key: Optional[str] = None


@dataclass
class AgentMetadata:
    """Metadata for agent files."""
    name: str
    path: str
    category: AgentCategory
    intent_mapping: Dict[IntentType, float] = field(default_factory=dict)  # Intent -> confidence
    dependencies: List[str] = field(default_factory=list)
    capabilities: List[str] = field(default_factory=list)
    version: str = "1.0"
    last_updated: Optional[str] = None
    cache_key: Optional[str] = None


@dataclass
class RoutingDecision:
    """Decision output from intelligence routing."""
    intent: IntentType
    primary_prompt: PromptMetadata
    primary_agent: AgentMetadata
    secondary_prompts: List[PromptMetadata] = field(default_factory=list)
    secondary_agents: List[AgentMetadata] = field(default_factory=list)
    confidence_score: float = 0.0
    reasoning: str = ""
    semantic_matches: Dict[str, float] = field(default_factory=dict)  # File -> similarity score
    requires_unified_intelligence: bool = False
    context_hints: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class IntelligenceRoutingEngine:
    """
    Routes user intents to appropriate prompts and agents.
    
    Implements:
    - Semantic matching between intent and available resources
    - Intent-based agent/prompt discovery
    - Caching for performance
    - Context synthesis hints
    """

    # Intent → (Primary Prompt, Primary Agent) mapping
    INTENT_ROUTING_MAP = {
        IntentType.IMPLEMENT: ("CORTEX.prompt.md", "cortex-executor.md"),
        IntentType.FIX: ("CORTEX.prompt.md", "cortex-executor.md"),
        IntentType.REFACTOR: ("CORTEX.prompt.md", "cortex-architect.md"),
        IntentType.ANALYZE: ("CORTEX.prompt.md", "cortex-auditor.md"),
        IntentType.AUDIT: ("CORTEX.prompt.md", "cortex-auditor.md"),
        IntentType.DESIGN: ("cortex-architect.prompt.md", "cortex-architect.md"),
        IntentType.PLAN: ("cortex-architect.prompt.md", "cortex-phase-resolver.md"),
        IntentType.ONBOARD: ("CORTEX.prompt.md", "cortex-environment-setup.md"),
        IntentType.DEBUG: ("CORTEX.prompt.md", "cortex-debugger.md"),
        IntentType.DIGEST: ("CORTEX.prompt.md", "cortex-digest.md"),
    }

    # Intent → Secondary prompts/agents for context
    INTENT_SECONDARY_MAP = {
        IntentType.IMPLEMENT: {
            "prompts": ["response-format-standards.md"],
            "agents": ["cortex-holistic-validator.md"],
        },
        IntentType.FIX: {
            "prompts": ["response-format-standards.md"],
            "agents": ["cortex-debugger.md"],
        },
        IntentType.REFACTOR: {
            "prompts": ["response-format-standards.md"],
            "agents": ["cortex-holistic-validator.md"],
        },
        IntentType.ANALYZE: {
            "prompts": ["response-format-standards.md"],
            "agents": ["cortex-auditor.md"],
        },
        IntentType.AUDIT: {
            "prompts": ["response-format-standards.md"],
            "agents": ["cortex-auditor.md"],
        },
        IntentType.DESIGN: {
            "prompts": ["response-format-standards.md"],
            "agents": ["cortex-designer.md"],
        },
        IntentType.PLAN: {
            "prompts": ["response-format-standards.md"],
            "agents": ["cortex-interactive.md"],
        },
    }

    # Intent keywords for semantic matching
    INTENT_KEYWORDS = {
        IntentType.IMPLEMENT: ["implement", "add", "feature", "create", "build", "develop"],
        IntentType.FIX: ["fix", "bug", "issue", "error", "problem", "repair"],
        IntentType.REFACTOR: ["refactor", "improve", "clean", "optimize", "restructure"],
        IntentType.ANALYZE: ["analyze", "examine", "review", "inspect", "understand"],
        IntentType.AUDIT: ["audit", "governance", "compliance", "security", "health"],
        IntentType.DESIGN: ["design", "architecture", "plan", "structure", "organize"],
        IntentType.PLAN: ["plan", "phase", "stage", "schedule", "roadmap"],
        IntentType.ONBOARD: ["onboard", "setup", "initialize", "configure", "install"],
        IntentType.DEBUG: ["debug", "trace", "breakpoint", "investigate", "diagnose"],
        IntentType.DIGEST: ["digest", "summarize", "extract", "consolidate", "learn"],
    }

    def __init__(self, prompts_dir: Optional[Path] = None, agents_dir: Optional[Path] = None):
        """
        Initialize routing engine.
        
        Args:
            prompts_dir: Path to .github/prompts directory
            agents_dir: Path to .github/agents/core directory
        """
        self.prompts_dir = prompts_dir or self._resolve_prompts_dir()
        self.agents_dir = agents_dir or self._resolve_agents_dir()
        
        self._prompt_cache: Dict[str, PromptMetadata] = {}
        self._agent_cache: Dict[str, AgentMetadata] = {}
        self._routing_cache: Dict[str, RoutingDecision] = {}
        
        self._load_manifests()
        logger.info("IntelligenceRoutingEngine initialized")

    @staticmethod
    def _resolve_prompts_dir() -> Path:
        """Resolve .github/prompts directory."""
        # Try multiple resolution strategies
        cwd = Path.cwd()
        
        # Strategy 1: Current directory
        if (cwd / ".github" / "prompts").exists():
            return cwd / ".github" / "prompts"
        
        # Strategy 2: Parent directories (up to 5 levels)
        current = cwd
        for _ in range(5):
            prompts_path = current / ".github" / "prompts"
            if prompts_path.exists():
                return prompts_path
            current = current.parent
        
        # Fallback
        logger.warning("Could not resolve prompts directory, using default")
        return cwd / ".github" / "prompts"

    @staticmethod
    def _resolve_agents_dir() -> Path:
        """Resolve .github/agents/core directory."""
        cwd = Path.cwd()
        
        # Strategy 1: Current directory
        if (cwd / ".github" / "agents" / "core").exists():
            return cwd / ".github" / "agents" / "core"
        
        # Strategy 2: Parent directories
        current = cwd
        for _ in range(5):
            agents_path = current / ".github" / "agents" / "core"
            if agents_path.exists():
                return agents_path
            current = current.parent
        
        logger.warning("Could not resolve agents directory, using default")
        return cwd / ".github" / "agents" / "core"

    def _load_manifests(self) -> None:
        """Load manifest files if available."""
        # Try to load AGENT-INDEX.md and parse agent metadata
        agent_index_path = self.agents_dir.parent / "AGENT-INDEX.md"
        
        if agent_index_path.exists():
            try:
                with open(agent_index_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Parse agent metadata from markdown
                    self._parse_agent_index(content)
                logger.info(f"Loaded {len(self._agent_cache)} agents from manifest")
            except Exception as e:
                logger.warning(f"Error loading agent manifest: {e}")
        
        # Discover available prompts and agents
        self._discover_resources()

    def _parse_agent_index(self, content: str) -> None:
        """Parse agent index markdown."""
        # Simple parser for markdown agent index
        lines = content.split('\n')
        current_agent = None
        
        for line in lines:
            if line.startswith('## '):
                current_agent = line.replace('## ', '').strip()
            elif line.startswith('- ') and current_agent:
                # Parse agent properties
                pass

    def _discover_resources(self) -> None:
        """Discover available prompts and agents."""
        # Discover prompts
        if self.prompts_dir.exists():
            for prompt_file in self.prompts_dir.glob("*.md"):
                if prompt_file.name.startswith('.'):
                    continue
                
                metadata = PromptMetadata(
                    name=prompt_file.stem,
                    path=str(prompt_file),
                    category=self._classify_prompt(prompt_file.stem),
                    cache_key=self._generate_cache_key(str(prompt_file)),
                )
                self._prompt_cache[prompt_file.stem] = metadata
                logger.debug(f"Discovered prompt: {prompt_file.stem}")
        
        # Discover agents
        if self.agents_dir.exists():
            for agent_file in self.agents_dir.glob("*.md"):
                if agent_file.name.startswith('.'):
                    continue
                
                metadata = AgentMetadata(
                    name=agent_file.stem,
                    path=str(agent_file),
                    category=self._classify_agent(agent_file.stem),
                    cache_key=self._generate_cache_key(str(agent_file)),
                )
                self._agent_cache[agent_file.stem] = metadata
                logger.debug(f"Discovered agent: {agent_file.stem}")

    @staticmethod
    def _classify_prompt(name: str) -> PromptCategory:
        """Classify prompt by name."""
        name_lower = name.lower()
        
        if "architect" in name_lower:
            return PromptCategory.ARCHITECT
        elif "response" in name_lower or "format" in name_lower:
            return PromptCategory.RESPONSE_FORMAT
        elif "setup" in name_lower or "guide" in name_lower:
            return PromptCategory.SETUP_GUIDE
        elif "activation" in name_lower or "checklist" in name_lower:
            return PromptCategory.ACTIVATION_CHECKLIST
        elif "CORTEX.prompt" in name:
            return PromptCategory.PRODUCTION_MASTER
        else:
            return PromptCategory.CONTEXTUAL

    @staticmethod
    def _classify_agent(name: str) -> AgentCategory:
        """Classify agent by name."""
        name_lower = name.lower()
        
        if any(x in name_lower for x in ["executor", "orchestrator", "router"]):
            return AgentCategory.CORE
        elif any(x in name_lower for x in ["architect", "designer", "planner"]):
            return AgentCategory.DOMAIN
        elif any(x in name_lower for x in ["debugger", "vacuum", "validator"]):
            return AgentCategory.SUPPORT
        elif any(x in name_lower for x in ["ask", "coordinator", "storyteller"]):
            return AgentCategory.EDUCATION
        else:
            return AgentCategory.SUPPORT

    @staticmethod
    def _generate_cache_key(path: str) -> str:
        """Generate cache key for file."""
        return hashlib.md5(path.encode()).hexdigest()

    def route(self, intent: IntentType, request: str = "", context: Optional[Dict[str, Any]] = None) -> RoutingDecision:
        """
        Route intent to appropriate prompts and agents.
        
        Args:
            intent: Intent type
            request: User request text
            context: Optional context dict
        
        Returns:
            RoutingDecision with routing info
        """
        # Check cache
        cache_key = self._get_decision_cache_key(intent, request)
        if cache_key in self._routing_cache:
            logger.debug(f"Cache hit for routing decision: {cache_key}")
            return self._routing_cache[cache_key]
        
        # Get primary routing
        primary_prompt_name, primary_agent_name = self.INTENT_ROUTING_MAP.get(
            intent, 
            ("CORTEX.prompt.md", "cortex-executor.md")
        )
        
        primary_prompt = self._prompt_cache.get(
            primary_prompt_name.replace('.md', '').replace('.prompt', '')
        )
        primary_agent = self._agent_cache.get(
            primary_agent_name.replace('.md', '')
        )
        
        # Get secondary resources
        secondary_map = self.INTENT_SECONDARY_MAP.get(intent, {"prompts": [], "agents": []})
        secondary_prompts = [
            self._prompt_cache.get(p.replace('.md', ''))
            for p in secondary_map.get("prompts", [])
            if p.replace('.md', '') in self._prompt_cache
        ]
        secondary_agents = [
            self._agent_cache.get(a.replace('.md', ''))
            for a in secondary_map.get("agents", [])
            if a.replace('.md', '') in self._agent_cache
        ]
        
        # Compute semantic matches
        semantic_matches = self._compute_semantic_matches(intent, request)
        
        # Create decision
        decision = RoutingDecision(
            intent=intent,
            primary_prompt=primary_prompt or self._create_fallback_prompt(primary_prompt_name),
            primary_agent=primary_agent or self._create_fallback_agent(primary_agent_name),
            secondary_prompts=[p for p in secondary_prompts if p],
            secondary_agents=[a for a in secondary_agents if a],
            confidence_score=self._calculate_confidence(intent, request, semantic_matches),
            reasoning=f"Routed {intent.value} intent to primary prompt and agent",
            semantic_matches=semantic_matches,
            requires_unified_intelligence=self._should_use_unified_intelligence(intent),
            context_hints=self._generate_context_hints(intent, request, context),
        )
        
        # Cache decision
        self._routing_cache[cache_key] = decision
        
        logger.info(
            f"Routing decision: {intent.value} → "
            f"{decision.primary_prompt.name} + {decision.primary_agent.name} "
            f"(confidence: {decision.confidence_score:.2f})"
        )
        
        return decision

    def _get_decision_cache_key(self, intent: IntentType, request: str) -> str:
        """Generate cache key for routing decision."""
        key_input = f"{intent.value}:{request[:100]}"
        return hashlib.md5(key_input.encode()).hexdigest()

    def _compute_semantic_matches(self, intent: IntentType, request: str) -> Dict[str, float]:
        """Compute semantic similarity matches."""
        matches = {}
        request_lower = request.lower()
        
        # Match against intent keywords
        for filename, cache in list(self._prompt_cache.items()) + list(self._agent_cache.items()):
            similarity = 0.0
            
            # Keyword matching
            intent_keywords = self.INTENT_KEYWORDS.get(intent, [])
            for keyword in intent_keywords:
                if keyword in request_lower:
                    similarity += 0.3
            
            # Filename matching
            filename_lower = filename.lower()
            for word in request_lower.split():
                if len(word) > 3 and word in filename_lower:
                    similarity += 0.1
            
            if similarity > 0:
                matches[filename] = min(similarity, 1.0)
        
        return matches

    def _calculate_confidence(
        self, 
        intent: IntentType, 
        request: str, 
        semantic_matches: Dict[str, float]
    ) -> float:
        """Calculate confidence score."""
        base_confidence = 0.7  # Base confidence for known intents
        
        # Boost from semantic matches
        if semantic_matches:
            max_match = max(semantic_matches.values())
            base_confidence += max_match * 0.2
        
        return min(base_confidence, 1.0)

    def _should_use_unified_intelligence(self, intent: IntentType) -> bool:
        """Check if unified intelligence synthesis is needed."""
        return intent in [
            IntentType.IMPLEMENT,
            IntentType.FIX,
            IntentType.REFACTOR,
            IntentType.ANALYZE,
            IntentType.AUDIT,
        ]

    def _generate_context_hints(
        self, 
        intent: IntentType, 
        request: str, 
        context: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Generate hints for context loading."""
        hints = []
        
        if intent == IntentType.IMPLEMENT:
            hints.append("Load TDD patterns before implementation")
            hints.append("Fetch governance rules for enforcement")
        elif intent == IntentType.AUDIT:
            hints.append("Load governance rules for audit")
            hints.append("Fetch LENS analysis if available")
        elif intent == IntentType.DESIGN:
            hints.append("Load architecture patterns")
            hints.append("Prepare challenge generation")
        
        return hints

    def _create_fallback_prompt(self, name: str) -> PromptMetadata:
        """Create fallback prompt metadata."""
        return PromptMetadata(
            name=name.replace('.md', '').replace('.prompt', ''),
            path=str(self.prompts_dir / name),
            category=PromptCategory.PRODUCTION_MASTER,
            cache_key="fallback",
        )

    def _create_fallback_agent(self, name: str) -> AgentMetadata:
        """Create fallback agent metadata."""
        return AgentMetadata(
            name=name.replace('.md', ''),
            path=str(self.agents_dir / name),
            category=AgentCategory.SUPPORT,
            cache_key="fallback",
        )

    def get_prompt_content(self, prompt_name: str) -> Optional[str]:
        """
        Load prompt content.
        
        Args:
            prompt_name: Prompt name or path
        
        Returns:
            Prompt content or None
        """
        # Try direct path
        prompt_path = Path(prompt_name)
        if prompt_path.exists():
            try:
                with open(prompt_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                logger.error(f"Error reading prompt {prompt_name}: {e}")
                return None
        
        # Try in prompts directory
        prompt_path = self.prompts_dir / f"{prompt_name}.md"
        if prompt_path.exists():
            try:
                with open(prompt_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                logger.error(f"Error reading prompt {prompt_name}: {e}")
                return None
        
        logger.warning(f"Prompt not found: {prompt_name}")
        return None

    def get_agent_content(self, agent_name: str) -> Optional[str]:
        """
        Load agent content.
        
        Args:
            agent_name: Agent name or path
        
        Returns:
            Agent content or None
        """
        # Try direct path
        agent_path = Path(agent_name)
        if agent_path.exists():
            try:
                with open(agent_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                logger.error(f"Error reading agent {agent_name}: {e}")
                return None
        
        # Try in agents directory
        agent_path = self.agents_dir / f"{agent_name}.md"
        if agent_path.exists():
            try:
                with open(agent_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                logger.error(f"Error reading agent {agent_name}: {e}")
                return None
        
        logger.warning(f"Agent not found: {agent_name}")
        return None

    def list_available_prompts(self) -> List[str]:
        """List all available prompts."""
        return list(self._prompt_cache.keys())

    def list_available_agents(self) -> List[str]:
        """List all available agents."""
        return list(self._agent_cache.keys())

    def get_routing_stats(self) -> Dict[str, Any]:
        """Get routing statistics."""
        return {
            "total_prompts": len(self._prompt_cache),
            "total_agents": len(self._agent_cache),
            "cache_size_routing": len(self._routing_cache),
            "intent_support": [i.value for i in IntentType],
        }


# AC_COMPLETE: AC-INTELLIGENCE-ROUTING-001 ✅
