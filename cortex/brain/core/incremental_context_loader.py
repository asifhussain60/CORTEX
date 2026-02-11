"""
Incremental Context Loader (ENH-046 Phase 1.6)

Purpose: Load context on-demand with minimal initial footprint
Architecture: Let GitHub Copilot pull context as needed (not pre-synthesis)
Target: ≤250 tokens at initialization, ≤500 tokens per incremental load

Key Insight (from chat01.txt):
  "1 reference loaded vs 14" when using minimal context
  - WRONG: Pre-load AGENT-INDEX.md + agents (3-5k tokens)
  - RIGHT: Load ONLY header + mode logic (250 tokens)
  - Let GitHub Copilot use semantic search on-demand (93% reduction)

Author: CORTEX Architect
Created: 2026-02-06
Version: 1.0.0
"""

import hashlib
import logging
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


@dataclass
class LoadedContext:
    """Container for loaded context with metadata"""
    content: str
    tokens: int
    source: str
    relevance: float
    timestamp: float


class IncrementalContextLoader:
    """
    Lazy context loader that minimizes initial footprint

    Design Principles:
    1. Initial load: ONLY response header + mode determination (≤250 tokens)
    2. On-demand load: Semantic search for relevant context (≤500 tokens/load)
    3. Cache-aware: Avoid re-loading same content
    4. Budget-enforcing: Respect token limits per load

    Integration:
      User Request → Minimal Header (250 tokens)
                          ↓
                GitHub Copilot (semantic search as needed)
                          ↓
                [If execution required] → CORTEX MCP Gateway
                          ↓
                IncrementalContextLoader (load 1-3 relevant files)
    """

    def __init__(self, workspace_root: Optional[Path] = None):
        """
        Initialize loader with minimal footprint

        Args:
            workspace_root: Root directory of CORTEX workspace
        """
        from cortex.brain.core.context_cache_layer import ContextCacheLayer

        self.workspace_root = workspace_root or Path.cwd()
        self._loaded_agents: Dict[str, Any] = {}
        self._loaded_yamls: Dict[str, Any] = {}
        self._cache = ContextCacheLayer(max_entries=1000, default_ttl=600)

        logger.debug("IncrementalContextLoader initialized (minimal footprint)")

    def get_initial_context(self) -> Dict[str, Any]:
        """
        Get minimal initial context (≤250 tokens)

        Returns ONLY:
          - Response header template (50 tokens)
          - Mode determination logic (200 tokens)

        Returns:
            Dict with response_header and mode_determination
        """
        return {
            "response_header": self._get_response_header_template(),
            "mode_determination": self._get_mode_determination_logic(),
            "tokens": 250  # Pre-calculated to ensure budget
        }

    def _get_response_header_template(self) -> str:
        """Get response header template (50 tokens)"""
        return """## 🧠 CORTEX {operation}
**Author:** Asif Hussain | **Orchestrator:** {orchestrator} ✅

---"""

    def _get_mode_determination_logic(self) -> str:
        """Get minimal mode determination logic (200 tokens)"""
        return """# Mode Classification (LENS)
AUDIT: health check, violations, P0/P1/P2/P3
DESIGN: architecture, challenge, alternatives
IMPLEMENT: TDD RED→GREEN→REFACTOR
FIX: bug resolution
REFACTOR: code improvement
ANALYZE: LENS analysis, metrics
TEST: test execution
ONBOARD: repository setup + security scan
"""

    def get_loaded_agents(self) -> List[str]:
        """Get list of currently loaded agent filenames"""
        return list(self._loaded_agents.keys())

    def get_loaded_yamls(self) -> List[str]:
        """Get list of currently loaded YAML filenames"""
        return list(self._loaded_yamls.keys())

    def load_for_intent(self, intent: str, request: str) -> Dict[str, Any]:
        """
        Load context on-demand based on intent (≤500 tokens)

        Uses semantic search to find relevant content:
          - AUDIT: cortex-auditor.md + governance rules
          - DESIGN: cortex-architect.md + challenge engine
          - IMPLEMENT: TDD orchestrator + best practices

        Args:
            intent: User intent (AUDIT, DESIGN, IMPLEMENT, etc.)
            request: User request text for semantic matching

        Returns:
            Dict with loaded context (≤500 tokens)
        """
        # Map intent to relevant files
        intent_map = {
            "AUDIT": ["cortex-auditor.md", "enforcement-orchestrator.md"],
            "DESIGN": ["cortex-architect.md", "challenge-engine.md"],
            "IMPLEMENT": ["tdd-orchestrator.md", "best-practices.yaml"],
            "FIX": ["debugging-agent.md", "tdd-orchestrator.md"],
            "REFACTOR": ["refactoring-orchestrator.md", "code-quality.yaml"],
            "ANALYZE": ["lens-analysis.md", "metrics-agent.md"],
            "TEST": ["test-orchestrator.md", "tdd-guidelines.yaml"],
            "ONBOARD": ["onboarding-orchestrator.md", "security-scan.yaml"],
        }

        relevant_files = intent_map.get(intent, [])
        loaded_context = []
        total_tokens = 0

        for filename in relevant_files:
            # Check budget before loading
            if total_tokens >= 500:
                logger.warning(f"Budget reached, skipping {filename}")
                break

            # Check cache first
            if filename.endswith(".md"):
                context = self._load_agent(filename)
                if context:
                    self._loaded_agents[filename] = context
                    loaded_context.append(context)
                    total_tokens += context.get("tokens", 0)
            elif filename.endswith(".yaml"):
                context = self._load_yaml(filename)
                if context:
                    self._loaded_yamls[filename] = context
                    loaded_context.append(context)
                    total_tokens += context.get("tokens", 0)

        return {
            "intent": intent,
            "loaded_files": [ctx.get("source", "") for ctx in loaded_context],
            "total_tokens": total_tokens,
            "content": loaded_context
        }

    def semantic_search(
        self,
        query: str,
        top_k: int = 3,
        min_relevance: float = 0.8
    ) -> List[Dict[str, Any]]:
        """
        Semantic search for relevant context (placeholder)

        In production, this would use embeddings + cosine similarity.
        For Phase 1.6, we use keyword matching as proxy.

        Args:
            query: Search query
            top_k: Max results to return
            min_relevance: Minimum relevance score (0-1)

        Returns:
            List of results with relevance scores
        """
        # Simplified keyword-based search (placeholder for embedding-based search)
        results = []

        # Search in agents directory
        agents_dir = self.workspace_root / ".github" / "agents" / "core"
        if agents_dir.exists():
            for agent_file in agents_dir.glob("*.md"):
                content = agent_file.read_text()
                relevance = self._calculate_relevance(query, content)

                if relevance >= min_relevance:
                    results.append({
                        "file": agent_file.name,
                        "relevance": relevance,
                        "type": "agent"
                    })

        # Sort by relevance and return top_k
        results.sort(key=lambda x: x["relevance"], reverse=True)
        return results[:top_k]

    def _calculate_relevance(self, query: str, content: str) -> float:
        """
        Calculate relevance score (simplified keyword matching)

        In production, this would use cosine similarity of embeddings.
        For now, we use keyword overlap as proxy.

        Args:
            query: Search query
            content: Content to match against

        Returns:
            Relevance score (0-1)
        """
        # Normalize and tokenize
        query_terms = set(re.findall(r'\w+', query.lower()))
        content_terms = set(re.findall(r'\w+', content.lower()))

        if not query_terms:
            return 0.0

        # Calculate Jaccard similarity
        intersection = query_terms & content_terms
        union = query_terms | content_terms

        return len(intersection) / len(union) if union else 0.0

    def load_incremental(self, request: str) -> Dict[str, Any]:
        """
        Load additional context incrementally (≤500 tokens per call)

        Args:
            request: User request needing additional context

        Returns:
            Dict with incremental context (≤500 tokens)
        """
        # Use semantic search to find relevant content
        results = self.semantic_search(request, top_k=2)

        loaded_context = []
        total_tokens = 0

        for result in results:
            if total_tokens >= 500:
                break

            filename = result["file"]
            context = self._load_agent(filename)

            if context:
                loaded_context.append(context)
                total_tokens += context.get("tokens", 0)

        return {
            "loaded_files": [ctx.get("source", "") for ctx in loaded_context],
            "total_tokens": total_tokens,
            "content": loaded_context
        }

    def _load_agent(self, filename: str) -> Dict[str, Any]:
        """
        Load agent file with cache check

        Args:
            filename: Agent filename (e.g., "cortex-architect.md")

        Returns:
            Dict with agent content summary
        """
        cache_key = f"agent:{filename}"

        # Check cache first
        if self._cache:
            cached = self._cache.get(cache_key)
            if cached:
                logger.debug(f"Cache hit: {filename}")
                return cached

        # Load from file
        agent_path = self.workspace_root / ".github" / "agents" / "core" / filename

        if not agent_path.exists():
            logger.warning(f"Agent file not found: {agent_path}")
            return {}

        try:
            content = agent_path.read_text()

            # Extract summary (title + purpose, ~50 tokens)
            lines = content.split('\n')
            title = lines[0] if lines else ""
            purpose = next((l for l in lines if "Purpose:" in l or "Mode:" in l), "")

            summary = f"{title}\n{purpose}"
            tokens = self.estimate_tokens(summary)

            result = {
                "source": filename,
                "summary": summary,
                "tokens": tokens,
                "full_path": str(agent_path)
            }

            # Cache result
            if self._cache:
                self._cache.set(cache_key, result)

            return result

        except Exception as e:
            logger.error(f"Error loading agent {filename}: {e}")
            return {}

    def _load_yaml(self, filename: str) -> Dict[str, Any]:
        """
        Load YAML file with cache check

        Args:
            filename: YAML filename

        Returns:
            Dict with YAML content summary
        """
        cache_key = f"yaml:{filename}"

        # Check cache first
        if self._cache:
            cached = self._cache.get(cache_key)
            if cached:
                return cached

        # Load from file (simplified for Phase 1.6)
        # In production, would parse and filter YAML
        return {
            "source": filename,
            "summary": f"YAML: {filename}",
            "tokens": 50  # Placeholder
        }

    def _read_file(self, path: Path) -> str:
        """Read file content (with error handling)"""
        try:
            return path.read_text()
        except Exception as e:
            logger.error(f"Error reading {path}: {e}")
            return ""

    def _embed(self, text: str) -> List[float]:
        """
        Generate embedding for text (placeholder)

        In production, this would use sentence-transformers or OpenAI embeddings.
        For Phase 1.6, we return empty list (keyword search used instead).

        Args:
            text: Text to embed

        Returns:
            Embedding vector (empty placeholder)
        """
        return []

    def estimate_tokens(self, content: Union[str, Dict[str, Any], List[Any]]) -> int:
        """
        Estimate token count (improved heuristic)

        Uses improved heuristic: ~0.75 tokens per word.
        In production, would use tiktoken for GPT-exact accuracy.

        Handles:
        - str: Direct word counting
        - dict: Recursively count all string values
        - list: Recursively count all items

        Args:
            content: Content to estimate tokens for (str, dict, or list)

        Returns:
            Estimated token count
        """
        if content is None:
            return 0

        # Handle dict with pre-calculated tokens
        if isinstance(content, dict):
            if "tokens" in content:
                return content["tokens"]

            # Recursively count tokens in all dict values
            total = 0
            for value in content.values():
                if isinstance(value, str):
                    total += self.estimate_tokens(value)
                elif isinstance(value, (dict, list)):
                    total += self.estimate_tokens(value)
            return total

        # Handle list
        if isinstance(content, list):
            return sum(self.estimate_tokens(item) for item in content)

        # Handle string
        if isinstance(content, str):
            if not content:
                return 0

            # Count words (split on whitespace)
            words = len(content.split())

            # Average: 0.75 tokens per word for English
            return int(words * 0.75)

        # Fallback: convert to string
        return self.estimate_tokens(str(content))

    def discover_agents(self) -> List[str]:
        """
        Discover available agents in workspace

        Returns:
            List of agent filenames
        """
        agents_dir = self.workspace_root / ".github" / "agents" / "core"

        if not agents_dir.exists():
            return []

        return [f.name for f in agents_dir.glob("*.md")]
