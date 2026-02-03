"""
Unified Intelligence Context - Phase 20.5 Component #1

Single context object combining LENS + Company + CORTEX knowledge.
Eliminates knowledge silos by providing unified intelligence for routing decisions.

Authority: AC-KNOWLEDGE-SYNTHESIS-001 (Phase 20.5)
Rule: CORE-011 (Type Hints)
"""

import time
from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional


@dataclass
class LENSIntelligence:
    """
    LENS intelligence from Phase 20.
    
    Combines git, AST, and comment analysis for holistic code understanding.
    """
    
    git_analysis: Dict[str, Any]  # Change patterns, hotspots, commit history
    ast_analysis: Dict[str, Any]  # Complexity, functions, classes, dead code
    comment_analysis: Dict[str, Any]  # TODOs, FIXMEs, docstrings


@dataclass
class CompanyKnowledge:
    """
    Company-specific knowledge from Phase 20.
    
    Domain rules and compliance standards with OVERRIDE precedence.
    Company rules take precedence over CORTEX best practices.
    """
    
    domain_rules: Dict[str, Any]  # Company-specific rules from company/domains/
    compliance_standards: List[str]  # PCI-DSS, HIPAA, SOC2 detection
    precedence: str  # "OVERRIDE" - company rules override CORTEX


@dataclass
class CORTEXKnowledge:
    """
    CORTEX best practices from 45+ knowledge YAMLs.
    
    Best practices, patterns, anti-patterns from cortex_brain/tier3/knowledge/.
    """
    
    best_practices: Dict[str, Any]  # 45+ YAMLs from cortex_brain/tier3/knowledge/
    applicable_patterns: List[str]  # Patterns matching current intent
    anti_patterns: List[str]  # Anti-patterns to avoid
    synthesis_metadata: Dict[str, Any]  # Which rules applied, conflicts resolved


@dataclass
class SynthesisResult:
    """
    Synthesis result from KnowledgeSynthesisEngine.
    
    Merged rules with precedence resolution, citations, violations, and guidance.
    """
    
    merged_rules: Dict[str, Any]  # Precedence-resolved final ruleset
    citations: List[str]  # Rule IDs cited in decision
    violations: List[str]  # Rules violated (if any)
    guidance: List[str]  # Proactive suggestions for engineer


@dataclass
class UnifiedIntelligenceContext:
    """
    Unified intelligence context combining all knowledge sources.
    
    Single context object that eliminates silos by combining:
    - LENS intelligence (git, AST, comments)
    - Company knowledge (domain rules, compliance)
    - CORTEX knowledge (45+ best practices YAMLs)
    - Synthesis result (merged rules, citations, violations, guidance)
    
    This context flows through MasterOrchestrator Stage 2 to provide
    proactive guidance during intent classification and routing.
    
    Usage:
        >>> lens = LENSIntelligence(git_analysis={...}, ast_analysis={...}, comment_analysis={...})
        >>> company = CompanyKnowledge(domain_rules={...}, compliance_standards=[...], precedence="OVERRIDE")
        >>> cortex = CORTEXKnowledge(best_practices={...}, applicable_patterns=[...], ...)
        >>> synthesis = SynthesisResult(merged_rules={...}, citations=[...], violations=[...], guidance=[...])
        >>> context = UnifiedIntelligenceContext(
        ...     lens_intelligence=lens,
        ...     company_knowledge=company,
        ...     cortex_knowledge=cortex,
        ...     synthesis_result=synthesis,
        ...     intent_type="IMPLEMENT",
        ...     file_path="/path/to/file.py",
        ...     timestamp=time.time()
        ... )
        >>> if context.has_violations():
        ...     print("Violations detected:", context.synthesis_result.violations)
    
    Authority: AC-KNOWLEDGE-SYNTHESIS-001 (Phase 20.5 Component #1)
    """
    
    # Intelligence sources
    lens_intelligence: LENSIntelligence
    company_knowledge: CompanyKnowledge
    cortex_knowledge: CORTEXKnowledge
    synthesis_result: SynthesisResult
    
    # Metadata
    intent_type: str  # IMPLEMENT, FIX, REFACTOR, ANALYZE, etc.
    file_path: Optional[str]  # File being analyzed (None for non-file operations)
    timestamp: float  # Unix timestamp when context created
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert context to dictionary for serialization.
        
        Returns:
            Dictionary representation of context
        """
        return {
            "lens_intelligence": asdict(self.lens_intelligence),
            "company_knowledge": asdict(self.company_knowledge),
            "cortex_knowledge": asdict(self.cortex_knowledge),
            "synthesis_result": asdict(self.synthesis_result),
            "intent_type": self.intent_type,
            "file_path": self.file_path,
            "timestamp": self.timestamp,
        }
    
    def has_violations(self) -> bool:
        """
        Check if synthesis detected any rule violations.
        
        Returns:
            True if violations detected, False otherwise
        """
        return len(self.synthesis_result.violations) > 0
    
    def get_cited_rules(self) -> List[str]:
        """
        Get list of rules cited in synthesis decision.
        
        Returns:
            List of rule IDs (e.g., ["CORE-008", "COMPANY-001"])
        """
        return self.synthesis_result.citations.copy()
    
    def get_guidance(self) -> List[str]:
        """
        Get proactive guidance for engineer.
        
        Returns:
            List of guidance strings
        """
        return self.synthesis_result.guidance.copy()
    
    def get_violations(self) -> List[str]:
        """
        Get list of detected violations.
        
        Returns:
            List of violation strings
        """
        return self.synthesis_result.violations.copy()
    
    @classmethod
    def create_empty(cls, intent_type: str, file_path: Optional[str] = None) -> "UnifiedIntelligenceContext":
        """
        Create empty context with no intelligence loaded.
        
        Useful for fallback scenarios when knowledge loading fails.
        
        Args:
            intent_type: Intent type
            file_path: Optional file path
        
        Returns:
            Empty UnifiedIntelligenceContext
        """
        return cls(
            lens_intelligence=LENSIntelligence(
                git_analysis={},
                ast_analysis={},
                comment_analysis={}
            ),
            company_knowledge=CompanyKnowledge(
                domain_rules={},
                compliance_standards=[],
                precedence="OVERRIDE"
            ),
            cortex_knowledge=CORTEXKnowledge(
                best_practices={},
                applicable_patterns=[],
                anti_patterns=[],
                synthesis_metadata={}
            ),
            synthesis_result=SynthesisResult(
                merged_rules={},
                citations=[],
                violations=[],
                guidance=[]
            ),
            intent_type=intent_type,
            file_path=file_path,
            timestamp=time.time()
        )
