"""Inquiry system data models.

AC-ID: INQUIRY-000
Purpose: Core data models for inquiry orchestrator system
Author: Asif Hussain
Date: 2026-01-27

Models:
- RepoType: Enum for repository classification
- RepoContext: Repository detection context
- EvidenceSource: Code evidence references
- InquiryCategory: Question category classification
- AssembledContext: Complete context for inquiry handlers
"""

import hashlib
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any


class RepoType(Enum):
    """Repository type classification."""
    CORTEX = "cortex"
    USER_REPO = "user_repo"
    UNKNOWN = "unknown"


class InquiryCategory(Enum):
    """Question category for specialized routing."""
    ARCHITECTURE = "architecture"
    FEATURE = "feature"
    BEST_PRACTICE = "best_practice"
    TROUBLESHOOTING = "troubleshooting"
    EVOLUTION = "evolution"


@dataclass
class RepoContext:
    """Repository context from detection.
    
    Attributes:
        repo_type: Classified repository type (CORTEX or USER_REPO)
        repo_path: Absolute path to repository root
        repo_name: Repository name (e.g., "CORTEX", "my-app")
        git_remote: Git remote URL (if available)
        detection_confidence: Confidence score 0.0-1.0
        detection_signals: Dict of detection signals fired
    """
    repo_type: RepoType
    repo_path: Path
    repo_name: str
    git_remote: Optional[str] = None
    detection_confidence: float = 0.0
    detection_signals: Dict[str, Any] = field(default_factory=dict)
    
    def is_cortex_repo(self) -> bool:
        """Check if this is CORTEX repository.
        
        Returns:
            True if CORTEX, False otherwise
        """
        return self.repo_type == RepoType.CORTEX
    
    def get_cache_key(self, question: str) -> str:
        """Generate repo-scoped cache key.
        
        Args:
            question: Question text
            
        Returns:
            Unique cache key scoped to repository
        """
        # Normalize question
        normalized = question.lower().strip()
        question_hash = hashlib.md5(normalized.encode()).hexdigest()[:8]
        
        # Repo-scoped key
        return f"{self.repo_name}:{question_hash}"


@dataclass
class EvidenceSource:
    """Code evidence source reference.
    
    Attributes:
        file_path: Relative path to file
        line_number: Line number in file
        content: Snippet of relevant code/text
        source_type: Type of evidence (code, test, doc, git)
    """
    file_path: str
    line_number: int
    content: str
    source_type: str = "code"
    
    def format_reference(self) -> str:
        """Format evidence as file:line reference.
        
        Returns:
            Formatted string like "file.py:123"
        """
        return f"{self.file_path}:{self.line_number}"


@dataclass
class AssembledContext:
    """Complete assembled context for inquiry handlers.
    
    Attributes:
        question: Original question text
        repo_context: Repository detection context
        category: Classified inquiry category
        evidence_sources: List of code evidence
        confidence: Overall confidence score 0.0-1.0
        tier3_knowledge: Applicable Tier3 YAML files (CORTEX-only)
        core_rules: Applicable CORE rules (CORTEX-only)
        cache_hit: Whether context from cache
        metadata: Additional context metadata
    """
    question: str
    repo_context: RepoContext
    category: InquiryCategory
    evidence_sources: List[EvidenceSource] = field(default_factory=list)
    confidence: float = 0.0
    tier3_knowledge: Optional[List[str]] = None
    core_rules: Optional[List[str]] = None
    cache_hit: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def has_high_confidence(self, threshold: float = 0.85) -> bool:
        """Check if confidence exceeds threshold.
        
        Args:
            threshold: Confidence threshold (default 0.85)
            
        Returns:
            True if confidence >= threshold
        """
        return self.confidence >= threshold
    
    def is_cortex_question(self) -> bool:
        """Check if question is about CORTEX.
        
        Returns:
            True if CORTEX repo detected
        """
        return self.repo_context.is_cortex_repo()
    
    def to_cacheable(self) -> Dict[str, Any]:
        """Serialize to cacheable dictionary.
        
        Converts AssembledContext to dictionary for cache storage.
        Excludes repo_context (provided at deserialization) and cache_hit flag.
        
        Returns:
            Dictionary suitable for JSON serialization
        """
        return {
            "question": self.question,
            "category": self.category.value,
            "confidence": self.confidence,
            "evidence_sources": [
                {
                    "file_path": ev.file_path,
                    "line_number": ev.line_number,
                    "content": ev.content,
                    "source_type": ev.source_type,
                }
                for ev in self.evidence_sources
            ],
            "tier3_knowledge": self.tier3_knowledge,
            "core_rules": self.core_rules,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_cache(
        cls,
        cached_data: Dict[str, Any],
        repo_context: RepoContext,
    ) -> "AssembledContext":
        """Deserialize from cached dictionary.
        
        Reconstructs AssembledContext from cached data. Sets cache_hit=True
        to indicate this context came from cache.
        
        Args:
            cached_data: Cached dictionary from to_cacheable()
            repo_context: Repository context (not cached)
            
        Returns:
            Reconstructed AssembledContext with cache_hit=True
        """
        # Reconstruct evidence sources
        evidence_sources = [
            EvidenceSource(
                file_path=ev["file_path"],
                line_number=ev["line_number"],
                content=ev["content"],
                source_type=ev["source_type"],
            )
            for ev in cached_data.get("evidence_sources", [])
        ]
        
        # Reconstruct category enum
        category = InquiryCategory(cached_data["category"])
        
        return cls(
            question=cached_data["question"],
            repo_context=repo_context,
            category=category,
            evidence_sources=evidence_sources,
            confidence=cached_data["confidence"],
            tier3_knowledge=cached_data.get("tier3_knowledge"),
            core_rules=cached_data.get("core_rules"),
            cache_hit=True,  # Mark as from cache
            metadata=cached_data.get("metadata", {}),
        )
