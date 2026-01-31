"""
Phase 8.4: Synonym Expansion Service

Provides synonym expansion for routing keywords with configurable synonym groups.
Integrates with SemanticRankingEngine for improved routing accuracy.

AC-ID: AC-PHASE-8.4-02 (Task NLP-002)

CORE Governance:
  - CORE-008: TDD - Tests provided first
  - CORE-011: Type hints on all methods
  - CORE-012: Google-style docstrings
  - CORE-013: Specific exception handling
  - CORE-027: Audit trail logging

Author: Asif Hussain
Created: 2026-01-30
"""

from typing import List, Set, Dict, Any, Optional
from dataclasses import dataclass
from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger


@dataclass
class SynonymExpansion:
    """
    Result of synonym expansion.
    
    Attributes:
        original: Original keyword
        synonyms: Expanded synonyms
        groups: Synonym groups matched
        expansion_count: Number of synonyms found
    """
    original: str
    synonyms: Set[str]
    groups: List[str]
    expansion_count: int


class SynonymExpansionService:
    """
    Provides synonym expansion for routing keywords.
    
    Integrates with SemanticRankingEngine to improve routing accuracy
    by expanding user keywords to include semantic equivalents.
    
    Synonym Groups (Configurable):
    - create/build/implement/setup
    - analyze/inspect/review/examine
    - fix/repair/resolve/debug
    - refactor/cleanup/optimize/improve
    - test/validate/verify/check
    - deploy/launch/release/publish
    - document/describe/explain/annotate
    - configure/setup/initialize/prepare
    - onboard/start/begin/bootstrap
    - monitor/observe/track/watch
    
    Example:
        service = SynonymExpansionService()
        
        # Expand single keyword
        result = service.expand("implement")
        # result.synonyms = {"implement", "create", "build", "setup"}
        
        # Expand multiple keywords
        expanded = service.expand_keywords(["fix", "analyze"])
        # expanded = {"fix", "repair", "resolve", "debug",
        #             "analyze", "inspect", "review", "examine"}
    """
    
    def __init__(self, custom_groups: Optional[Dict[str, Set[str]]] = None) -> None:
        """
        Initialize synonym expansion service.
        
        Args:
            custom_groups: Optional custom synonym groups (overrides defaults)
        """
        self.logger = EnhancedAuditLogger.instance()
        
        # Default synonym groups
        self.synonym_groups: Dict[str, Set[str]] = {
            "creation": {"create", "build", "implement", "setup", "generate"},
            "analysis": {"analyze", "inspect", "review", "examine", "investigate"},
            "fixing": {"fix", "repair", "resolve", "debug", "correct"},
            "refactoring": {"refactor", "cleanup", "optimize", "improve", "restructure"},
            "testing": {"test", "validate", "verify", "check", "assert"},
            "deployment": {"deploy", "launch", "release", "publish", "rollout"},
            "documentation": {"document", "describe", "explain", "annotate", "record"},
            "configuration": {"configure", "setup", "initialize", "prepare", "provision"},
            "onboarding": {"onboard", "start", "begin", "bootstrap", "kickstart"},
            "monitoring": {"monitor", "observe", "track", "watch", "measure"},
        }
        
        # Override with custom groups if provided
        if custom_groups:
            self.synonym_groups.update(custom_groups)
        
        # Build reverse index: word -> group names
        self.word_to_groups: Dict[str, List[str]] = {}
        for group_name, words in self.synonym_groups.items():
            for word in words:
                if word not in self.word_to_groups:
                    self.word_to_groups[word] = []
                self.word_to_groups[word].append(group_name)
        
        self.logger.log_operation_complete(
            ac_id="AC-PHASE-8.4-02",
            operation="SYNONYM_SERVICE_INIT",
            success=True,
            details={
                "synonym_groups": len(self.synonym_groups),
                "total_words": len(self.word_to_groups),
            },
        )
    
    def expand(self, keyword: str) -> SynonymExpansion:
        """
        Expand single keyword to synonyms.
        
        AC-PHASE-8.4-02: Synonym expansion lookup
        
        Args:
            keyword: Keyword to expand
        
        Returns:
            SynonymExpansion: Expansion result
        """
        keyword_lower = keyword.lower()
        
        # Find matching groups
        matched_groups = self.word_to_groups.get(keyword_lower, [])
        
        # Collect all synonyms from matched groups
        synonyms: Set[str] = set()
        for group_name in matched_groups:
            synonyms.update(self.synonym_groups[group_name])
        
        # Always include original
        synonyms.add(keyword_lower)
        
        return SynonymExpansion(
            original=keyword,
            synonyms=synonyms,
            groups=matched_groups,
            expansion_count=len(synonyms) - 1,  # Exclude original
        )
    
    def expand_keywords(self, keywords: List[str]) -> Set[str]:
        """
        Expand multiple keywords to synonym set.
        
        AC-PHASE-8.4-02: Batch synonym expansion
        
        Args:
            keywords: List of keywords to expand
        
        Returns:
            Set[str]: Expanded keyword set (includes originals)
        """
        expanded: Set[str] = set()
        
        for keyword in keywords:
            result = self.expand(keyword)
            expanded.update(result.synonyms)
        
        return expanded
    
    def get_synonym_group(self, group_name: str) -> Set[str]:
        """
        Get specific synonym group.
        
        Args:
            group_name: Name of synonym group
        
        Returns:
            Set[str]: Synonyms in group
        
        Raises:
            KeyError: If group doesn't exist
        """
        if group_name not in self.synonym_groups:
            raise KeyError(f"Synonym group '{group_name}' not found")
        
        return self.synonym_groups[group_name].copy()
    
    def add_synonym_group(self, group_name: str, synonyms: Set[str]) -> None:
        """
        Add or update synonym group.
        
        Args:
            group_name: Name of synonym group
            synonyms: Set of synonyms
        """
        self.synonym_groups[group_name] = synonyms
        
        # Update reverse index
        for word in synonyms:
            if word not in self.word_to_groups:
                self.word_to_groups[word] = []
            if group_name not in self.word_to_groups[word]:
                self.word_to_groups[word].append(group_name)
        
        self.logger.log_operation_complete(
            ac_id="AC-PHASE-8.4-02",
            operation="SYNONYM_GROUP_ADD",
            success=True,
            details={
                "group_name": group_name,
                "synonym_count": len(synonyms),
            },
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get service statistics.
        
        Returns:
            Dict: Service stats
        """
        return {
            "synonym_groups": len(self.synonym_groups),
            "total_unique_words": len(self.word_to_groups),
            "groups": list(self.synonym_groups.keys()),
        }
