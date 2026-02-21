"""
Enriched Context Model - Superset of CrystallizedContext.

Authority: Phase 90 Stage 3 - Context Synthesis Gateway
Purpose: Unified context with LENS + Tech Stack + YAMLs + Domain + Architecture

CORE Rules:
- CORE-011: Type hints required ✅
- CORE-012: Docstrings required ✅
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class EnrichedContext:
    """
    Enriched context from Context-Aware Synthesis Gateway.
    
    Extends CrystallizedContext with tech stack intelligence and
    knowledge YAML synthesis.
    
    Attributes:
        lens_analysis: LENS intelligence (git, AST, comments)
        tech_stack: Detected technology stack
        knowledge_yamls: Resolved knowledge YAML files
        domain_knowledge: Domain-specific patterns
        architecture_patterns: Detected architecture patterns
        company_overrides: Company precedence applied
        metadata: Synthesis metadata (timing, cache, confidence)
    
    Authority: AC-PHASE90-S3-001
    """
    
    # LENS intelligence
    lens_analysis: Dict[str, Any] = field(default_factory=dict)
    
    # Tech stack (from Stage 1)
    tech_stack: Dict[str, Any] = field(default_factory=dict)
    
    # Knowledge YAMLs (from Stage 2)
    knowledge_yamls: List[str] = field(default_factory=list)
    
    # Domain knowledge
    domain_knowledge: Dict[str, Any] = field(default_factory=dict)
    
    # Architecture patterns
    architecture_patterns: List[str] = field(default_factory=list)
    
    # Company precedence
    company_overrides: List[str] = field(default_factory=list)
    
    # Synthesis metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "lens_analysis": self.lens_analysis,
            "tech_stack": self.tech_stack,
            "knowledge_yamls": self.knowledge_yamls,
            "domain_knowledge": self.domain_knowledge,
            "architecture_patterns": self.architecture_patterns,
            "company_overrides": self.company_overrides,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls: object, data: Dict[str, Any]) -> "EnrichedContext":
        """Create EnrichedContext from dictionary."""
        return cls(
            lens_analysis=data.get("lens_analysis", {}),
            tech_stack=data.get("tech_stack", {}),
            knowledge_yamls=data.get("knowledge_yamls", []),
            domain_knowledge=data.get("domain_knowledge", {}),
            architecture_patterns=data.get("architecture_patterns", []),
            company_overrides=data.get("company_overrides", []),
            metadata=data.get("metadata", {}),
        )
    
    def get_synthesis_duration(self) -> Optional[float]:
        """Get synthesis duration in milliseconds."""
        return self.metadata.get("synthesis_duration_ms")
    
    def is_cache_hit(self) -> bool:
        """Check if this context was served from cache."""
        return self.metadata.get("cache_hit", False)
    
    def get_confidence_score(self) -> float:
        """Get overall synthesis confidence score."""
        return self.metadata.get("confidence_score", 0.0)


# AC_START: AC-PHASE90-S3-001
# Description: EnrichedContext model for synthesis gateway
