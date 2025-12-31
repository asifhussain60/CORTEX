"""
Brain Interface - Unified Access Layer for CORTEX 4.0 Brain

Provides consistent access to all brain tiers with:
- Automatic path resolution (shared vs per-repo)
- Lazy initialization (tiers loaded on demand)
- Error handling and logging
- Configuration management

Design Principles:
1. Orchestrators access brain ONLY through this interface
2. Tiers are isolated from each other
3. Storage location handled automatically (hybrid centralization)
4. Graceful degradation (missing tiers don't crash system)
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class BrainConfig:
    """Configuration for brain initialization."""
    workspace_root: Path
    shared_root: Optional[Path] = None  # ~/.cortex/shared/
    enable_tier0: bool = True
    enable_tier1: bool = True
    enable_tier2: bool = True
    enable_tier3: bool = True
    max_conversations: int = 70
    pattern_confidence_threshold: float = 0.5
    
    def __post_init__(self):
        """Set defaults for shared root."""
        if self.shared_root is None:
            self.shared_root = Path.home() / ".cortex" / "shared"


class BrainInterface:
    """
    Unified interface to all CORTEX brain tiers.
    
    Architecture:
        Tier 0 (Governance): {workspace}/cortex-brain/brain-protection-rules.yaml (BrainProtector)
        Tier 1 (Working Memory): {workspace}/cortex-brain/tier1/conversations.db (per-repo)
        Tier 2 (Knowledge Graph): ~/.cortex/shared/tier2/knowledge-graph.db (centralized with namespaces)
        Tier 3 (Dev Context): {workspace}/cortex-brain/tier3/metrics.db (per-repo)
    
    Usage:
        brain = BrainInterface(workspace_root)
        
        # Tier 0: Governance (SKULL protection)
        brain.tier0.check_protection(...)
        
        # Tier 1: Working Memory
        brain.tier1.store_conversation(...)
        
        # Tier 2: Knowledge Graph
        brain.tier2.store_pattern(...)
        
        # Tier 3: Dev Context
        brain.tier3.get_git_metrics(...)
    """
    
    def __init__(self, workspace_root: Path, config: Optional[Dict[str, Any]] = None):
        """
        Initialize brain interface.
        
        Args:
            workspace_root: Root directory of the workspace
            config: Optional configuration overrides
        """
        self.workspace_root = Path(workspace_root)
        self.logger = logging.getLogger(__name__)
        
        # Build configuration
        config_dict = config or {}
        self.config = BrainConfig(
            workspace_root=self.workspace_root,
            shared_root=config_dict.get("shared_root"),
            enable_tier0=config_dict.get("enable_tier0", True),
            enable_tier1=config_dict.get("enable_tier1", True),
            enable_tier2=config_dict.get("enable_tier2", True),
            enable_tier3=config_dict.get("enable_tier3", True),
            max_conversations=config_dict.get("max_conversations", 70),
            pattern_confidence_threshold=config_dict.get("pattern_confidence_threshold", 0.5)
        )
        
        # Lazy-loaded tier instances
        self._tier0 = None
        self._tier1 = None
        self._tier2 = None
        self._tier3 = None
        
        self.logger.info(f"Brain interface initialized for workspace: {workspace_root}")
    
    @property
    def tier0(self):
        """
        Tier 0: Governance (SKULL rules enforcement via BrainProtector).
        
        Storage: {workspace}/cortex-brain/brain-protection-rules.yaml
        """
        if self._tier0 is None and self.config.enable_tier0:
            from src.tier0.brain_protector import BrainProtector
            
            # BrainProtector auto-resolves paths via resource_resolver
            self._tier0 = BrainProtector()
            self.logger.debug("Tier 0 (BrainProtector) initialized")
        
        return self._tier0
    
    @property
    def tier1(self):
        """
        Tier 1: Working Memory (conversation history).
        
        Storage: {workspace}/cortex-brain/tier1/conversations.db (per-repo)
        Capacity: 70 conversations (FIFO)
        """
        if self._tier1 is None and self.config.enable_tier1:
            from .tier1.working_memory import WorkingMemory
            
            db_path = self.workspace_root / "cortex-brain" / "tier1" / "conversations.db"
            self._tier1 = WorkingMemory(
                db_path=db_path,
                max_conversations=self.config.max_conversations
            )
            self.logger.debug("Tier 1 (Working Memory) initialized")
        
        return self._tier1
    
    @property
    def tier2(self):
        """
        Tier 2: Knowledge Graph (pattern learning).
        
        Storage: ~/.cortex/shared/tier2/knowledge-graph.db (centralized with namespaces)
        Features: FTS5 search, pattern decay, cross-project insights
        """
        if self._tier2 is None and self.config.enable_tier2:
            from .tier2.knowledge_graph import KnowledgeGraph
            
            db_path = self.config.shared_root / "tier2" / "knowledge-graph.db"
            namespace = self._get_namespace()
            
            self._tier2 = KnowledgeGraph(
                db_path=db_path,
                namespace=namespace,
                confidence_threshold=self.config.pattern_confidence_threshold
            )
            self.logger.debug(f"Tier 2 (Knowledge Graph) initialized with namespace: {namespace}")
        
        return self._tier2
    
    @property
    def tier3(self):
        """
        Tier 3: Development Context (git metrics, repository context).
        
        Storage: {workspace}/cortex-brain/tier3/metrics.db (per-repo)
        Features: Git metrics, hotspot detection, IDE context
        """
        if self._tier3 is None and self.config.enable_tier3:
            from .tier3.dev_context import DevelopmentContext
            
            db_path = self.workspace_root / "cortex-brain" / "tier3" / "metrics.db"
            self._tier3 = DevelopmentContext(db_path=db_path)
            self.logger.debug("Tier 3 (Dev Context) initialized")
        
        return self._tier3
    
    def _get_namespace(self) -> str:
        """
        Get namespace for Tier 2 knowledge graph.
        
        Uses workspace directory name as namespace for isolation.
        
        Returns:
            Namespace string (e.g., "cortex", "my-project")
        """
        return self.workspace_root.name.lower()
    
    def health_check(self) -> Dict[str, bool]:
        """
        Check health of all brain tiers.
        
        Returns:
            Dictionary of tier health status
        """
        health = {}
        
        if self.config.enable_tier0:
            try:
                self.tier0  # Trigger lazy initialization
                health["tier0"] = True
            except Exception as e:
                self.logger.error(f"Tier 0 health check failed: {e}")
                health["tier0"] = False
        
        if self.config.enable_tier1:
            try:
                self.tier1
                health["tier1"] = True
            except Exception as e:
                self.logger.error(f"Tier 1 health check failed: {e}")
                health["tier1"] = False
        
        if self.config.enable_tier2:
            try:
                self.tier2
                health["tier2"] = True
            except Exception as e:
                self.logger.error(f"Tier 2 health check failed: {e}")
                health["tier2"] = False
        
        if self.config.enable_tier3:
            try:
                self.tier3
                health["tier3"] = True
            except Exception as e:
                self.logger.error(f"Tier 3 health check failed: {e}")
                health["tier3"] = False
        
        return health
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics from all brain tiers.
        
        Returns:
            Dictionary of tier statistics
        """
        stats = {}
        
        if self.tier0:
            stats["tier0"] = {"status": "active"}
        
        if self.tier1:
            stats["tier1"] = {
                "conversation_count": self.tier1.get_conversation_count(),
                "max_conversations": self.config.max_conversations
            }
        
        if self.tier2:
            stats["tier2"] = {
                "pattern_count": self.tier2.get_pattern_count(),
                "namespace": self._get_namespace()
            }
        
        if self.tier3:
            stats["tier3"] = {
                "metrics_available": True
            }
        
        return stats
    
    def close(self):
        """Close all brain tier connections."""
        if self._tier1:
            self._tier1.close()
        if self._tier2:
            self._tier2.close()
        if self._tier3:
            self._tier3.close()
        
        self.logger.info("Brain interface closed")
