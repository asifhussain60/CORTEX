"""
Optimized Context Loader

Purpose: Integration layer between CORTEX orchestrator and context optimizer.
Provides optimized context loading with 30% token reduction.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Phase: Phase 4.3 - Context Optimization
"""

from typing import Dict, List, Optional, Any
from pathlib import Path
import json

from .context_optimizer import (
    ContextOptimizer,
    PatternRelevanceScorer,
    ContextCompressor
)


class OptimizedContextLoader:
    """
    Loads and optimizes context for CORTEX orchestrator.
    
    Features:
    - Selective tier loading (only what's needed)
    - Pattern relevance scoring (best matches first)
    - Context compression (30% reduction)
    - Dynamic sizing (adjust to query)
    
    Usage:
        loader = OptimizedContextLoader(brain_dir)
        context = loader.load_optimized_context(
            intent="PLAN",
            query="refactor authentication module",
            available_tiers={
                "tier0": instinct_handler,
                "tier1": working_memory,
                "tier2": knowledge_graph,
                "tier3": dev_context
            }
        )
    """
    
    def __init__(self, brain_dir: Path):
        """
        Initialize optimized context loader.
        
        Args:
            brain_dir: Path to cortex-brain directory
        """
        self.brain_dir = Path(brain_dir)
        self.optimizer = ContextOptimizer()
        self.scorer = PatternRelevanceScorer()
        self.compressor = ContextCompressor()
        
        # Performance metrics
        self.metrics = {
            "loads": 0,
            "total_original_size": 0,
            "total_optimized_size": 0,
            "avg_reduction_percent": 0
        }
    
    def load_optimized_context(self,
                              intent: str,
                              query: str,
                              available_tiers: Dict[str, Any],
                              compression_enabled: bool = True) -> Dict[str, Any]:
        """
        Load optimized context for given intent and query.
        
        Args:
            intent: User intent (PLAN, EXECUTE, TEST, etc.)
            query: User query text
            available_tiers: Dict of available tier instances
            compression_enabled: Enable compression (default True)
        
        Returns:
            Optimized context dict with metadata
        """
        # Use context optimizer to get optimized structure
        optimized_structure = self.optimizer.optimize_context(
            intent, query, available_tiers
        )
        
        # Load actual data from tiers
        context = self._load_tier_data(optimized_structure, available_tiers, query)
        
        # Apply compression if enabled
        if compression_enabled:
            compressed, stats = self.compressor.compress(context, target_reduction=0.30)
            
            # Update metrics
            self._update_metrics(stats)
            
            # Add stats to context
            compressed["optimization_stats"] = stats
            
            return compressed
        else:
            return context
    
    def _load_tier_data(self,
                       structure: Dict[str, Any],
                       tiers: Dict[str, Any],
                       query: str) -> Dict[str, Any]:
        """
        Load actual data from tiers based on optimized structure.
        
        Args:
            structure: Optimized structure from ContextOptimizer
            tiers: Available tier instances
            query: User query
        
        Returns:
            Context with loaded data
        """
        context = {
            "tiers_loaded": structure["tiers_loaded"],
            "query": query,
            "data": {}
        }
        
        # Load Tier 0: Instincts
        if "tier0" in structure["tiers_loaded"] and "tier0" in tiers:
            context["data"]["instincts"] = self._load_tier0(tiers["tier0"])
        
        # Load Tier 1: Recent Memory
        if "tier1" in structure["tiers_loaded"] and "tier1" in tiers:
            # Get limit from structure
            limit = structure["components"].get("recent_memory", {}).get("conversation_count", 5)
            context["data"]["recent_memory"] = self._load_tier1(tiers["tier1"], limit)
        
        # Load Tier 2: Knowledge Graph with relevance scoring
        if "tier2" in structure["tiers_loaded"] and "tier2" in tiers:
            # Get limit from structure
            limit = structure["components"].get("patterns", {}).get("pattern_count", 10)
            context["data"]["patterns"] = self._load_tier2(tiers["tier2"], query, limit)
        
        # Load Tier 3: Development Context
        if "tier3" in structure["tiers_loaded"] and "tier3" in tiers:
            context["data"]["dev_context"] = self._load_tier3(tiers["tier3"])
        
        return context
    
    def _load_tier0(self, tier0_instance: Any) -> Dict[str, Any]:
        """
        Load Tier 0 (Instincts) - always lightweight.
        
        Args:
            tier0_instance: Tier 0 instance
        
        Returns:
            Instinct data
        """
        # Tier 0 is always small, just load essential rules
        return {
            "core_principles": ["TDD", "DoR", "DoD", "SOLID", "DRY"],
            "protection_rules": ["no_monoliths", "test_first", "brain_protection"],
            "size_estimate": 200
        }
    
    def _load_tier1(self, tier1_instance: Any, limit: int = 5) -> Dict[str, Any]:
        """
        Load Tier 1 (Working Memory) - recent conversations only.
        
        Args:
            tier1_instance: Tier 1 instance
            limit: Max conversations to load
        
        Returns:
            Recent conversation data
        """
        # Load only last N conversations
        try:
            # Assuming tier1 has get_recent_conversations method
            if hasattr(tier1_instance, 'get_recent_conversations'):
                conversations = tier1_instance.get_recent_conversations(limit)
            else:
                # Fallback: load from JSONL file
                conversations = self._load_conversations_from_file(limit)
            
            return {
                "conversations": conversations,
                "count": len(conversations),
                "size_estimate": len(json.dumps(conversations))
            }
        except Exception as e:
            return {
                "conversations": [],
                "count": 0,
                "error": str(e),
                "size_estimate": 0
            }
    
    def _load_tier2(self, 
                   tier2_instance: Any,
                   query: str,
                   limit: int = 10) -> Dict[str, Any]:
        """
        Load Tier 2 (Knowledge Graph) with relevance scoring.
        
        Args:
            tier2_instance: Tier 2 instance
            query: User query for relevance scoring
            limit: Max patterns to return
        
        Returns:
            Scored and ranked patterns
        """
        try:
            # Get all patterns from tier2
            if hasattr(tier2_instance, 'get_patterns'):
                all_patterns = tier2_instance.get_patterns()
            else:
                # Fallback: load from file
                all_patterns = self._load_patterns_from_file()
            
            # Score and rank by relevance
            scored_patterns = self.scorer.score_patterns(
                all_patterns,
                query,
                limit
            )
            
            return {
                "patterns": scored_patterns,
                "count": len(scored_patterns),
                "total_available": len(all_patterns),
                "scored_by_relevance": True,
                "size_estimate": len(json.dumps(scored_patterns))
            }
        except Exception as e:
            return {
                "patterns": [],
                "count": 0,
                "error": str(e),
                "size_estimate": 0
            }
    
    def _load_tier3(self, tier3_instance: Any) -> Dict[str, Any]:
        """
        Load Tier 3 (Development Context) - summary only.
        
        Args:
            tier3_instance: Tier 3 instance
        
        Returns:
            Development context summary
        """
        try:
            # Get summary, not full history
            if hasattr(tier3_instance, 'get_summary'):
                summary = tier3_instance.get_summary()
            else:
                # Fallback: create minimal summary
                summary = {
                    "current_branch": "unknown",
                    "recent_commits": 0,
                    "changed_files": []
                }
            
            return {
                "summary": summary,
                "full_history": False,  # Don't load full git history
                "size_estimate": len(json.dumps(summary))
            }
        except Exception as e:
            return {
                "summary": {},
                "error": str(e),
                "size_estimate": 0
            }
    
    def _load_conversations_from_file(self, limit: int = 5) -> List[Dict]:
        """Fallback: Load conversations from JSONL file"""
        conv_file = self.brain_dir / "conversation-history.jsonl"
        
        if not conv_file.exists():
            return []
        
        conversations = []
        with open(conv_file, 'r') as f:
            lines = f.readlines()
            # Get last N lines
            for line in lines[-limit:]:
                try:
                    conversations.append(json.loads(line))
                except:
                    continue
        
        return conversations
    
    def _load_patterns_from_file(self) -> List[Dict]:
        """Fallback: Load patterns from knowledge graph file"""
        kg_file = self.brain_dir / "knowledge-graph.yaml"
        
        if not kg_file.exists():
            return []
        
        # For now, return empty (would need YAML parsing)
        return []
    
    def _update_metrics(self, stats: Dict):
        """Update performance metrics"""
        self.metrics["loads"] += 1
        self.metrics["total_original_size"] += stats["original_size"]
        self.metrics["total_optimized_size"] += stats["compressed_size"]
        
        # Calculate average reduction
        if self.metrics["total_original_size"] > 0:
            self.metrics["avg_reduction_percent"] = (
                (self.metrics["total_original_size"] - self.metrics["total_optimized_size"]) /
                self.metrics["total_original_size"] * 100
            )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        return self.metrics.copy()
    
    def reset_metrics(self):
        """Reset performance metrics"""
        self.metrics = {
            "loads": 0,
            "total_original_size": 0,
            "total_optimized_size": 0,
            "avg_reduction_percent": 0
        }


# Export
__all__ = ["OptimizedContextLoader"]
