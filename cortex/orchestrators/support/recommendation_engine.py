"""
RecommendationEngine - Advisory layer for best practices (Phase 8.4).

Provides security-first best practice recommendations for CORTEX operations.

Phase 8.4 Architecture (Decoupled from LENS):
- LENS analyzes code (fast, 1-2ms)
- Challenge Engine detects WHAT's problematic (HARD gates)
- **RecommendationEngine** suggests HOW to fix it (advisory, on-demand)

Loads tier3 best practice YAMLs selectively:
- SecurityAdvisor: Consults tier3/security/*.yaml
- PerformanceAdvisor: Consults tier3/performance/*.yaml  
- SolidAdvisor: Consults tier3/solid/*.yaml
- ComplianceAdvisor: Consults tier3/governance/*.yaml

AC-ID: AC-SECURITY-FRAMEWORK-001 (Phase 8.4)
Authority: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum
from pathlib import Path
import logging
import yaml

logger = logging.getLogger(__name__)


class AdvisorType(Enum):
    """Types of recommendation advisors."""
    SECURITY = "security"           # Security best practices
    PERFORMANCE = "performance"     # Performance patterns
    SOLID = "solid"                # SOLID principles
    COMPLIANCE = "compliance"       # Governance/compliance
    DOCUMENTATION = "documentation" # Documentation patterns


@dataclass
class Recommendation:
    """
    A single best practice recommendation.
    
    Attributes:
        advisor_type: Type of advisor providing recommendation
        pattern_id: ID from tier3 YAML pattern
        title: Short recommendation title
        description: Detailed recommendation
        severity: How important is this recommendation (HIGH, MEDIUM, LOW)
        pattern_reference: Reference to tier3 pattern file
        code_example: Example code showing best practice
        rationale: Why this pattern is recommended
    """
    advisor_type: AdvisorType
    pattern_id: str
    title: str
    description: str
    severity: str
    pattern_reference: str
    code_example: str = ""
    rationale: str = ""


@dataclass
class RecommendationResult:
    """
    Result from RecommendationEngine.
    
    Attributes:
        success: Whether recommendation generation succeeded
        recommendations: List of Recommendation objects
        summary: Human-readable summary
        error: Error message if failed
    """
    success: bool
    recommendations: List[Recommendation] = field(default_factory=list)
    summary: str = ""
    error: str = ""


class BaseAdvisor:
    """
    Base class for recommendation advisors.
    
    Each advisor loads and consults a specific set of best practice YAMLs
    from tier3 knowledge base.
    """
    
    def __init__(self, yaml_pattern: str = "*") -> None:
        """
        Initialize advisor.
        
        Args:
            yaml_pattern: Glob pattern for YAML files to load (e.g., "security/*.yaml")
        """
        self.yaml_pattern = yaml_pattern
        self.patterns: Dict[str, Dict[str, Any]] = {}
        self._load_patterns()
    
    def _load_patterns(self) -> None:
        """Load YAML patterns from tier3 knowledge base."""
        tier3_path = Path(__file__).parent.parent.parent / "tier3" / "knowledge"
        
        if not tier3_path.exists():
            logger.warning(f"Tier3 knowledge path does not exist: {tier3_path}")
            return
        
        # Search for matching YAML files
        search_path = tier3_path / self.yaml_pattern
        if "*" in str(search_path):
            # Glob search
            base_dir = tier3_path / self.yaml_pattern.split("*")[0].rstrip("/")
            pattern = self.yaml_pattern.split("/")[-1]
            
            if base_dir.exists():
                for yaml_file in base_dir.glob(pattern):
                    self._load_yaml_file(yaml_file)
        else:
            # Direct file
            if search_path.exists():
                self._load_yaml_file(search_path)
    
    def _load_yaml_file(self, file_path: Path) -> None:
        """Load a single YAML pattern file."""
        try:
            with open(file_path) as f:
                content = yaml.safe_load(f)
                if content:
                    pattern_id = content.get("pattern_id", file_path.stem)
                    self.patterns[pattern_id] = content
                    logger.debug(f"Loaded pattern: {pattern_id} from {file_path.name}")
        except Exception as e:
            logger.warning(f"Failed to load pattern from {file_path}: {str(e)}")


class SecurityAdvisor(BaseAdvisor):
    """
    Provides security best practice recommendations.
    
    Consults tier3/security/*.yaml patterns and provides recommendations
    for secure coding, threat mitigation, and CWE remediation.
    """
    
    def __init__(self) -> None:
        """Initialize SecurityAdvisor with security patterns."""
        super().__init__("security/*.yaml")
    
    def recommend(self, cwe_id: str, context: Dict[str, Any] = None) -> List[Recommendation]:
        """
        Generate security recommendations for a CWE.
        
        Args:
            cwe_id: CWE identifier (e.g., "CWE-94")
            context: Additional context (threat_description, code_snippet, etc.)
            
        Returns:
            List of Recommendation objects
        """
        recommendations = []
        context = context or {}
        
        # Find patterns matching this CWE
        for pattern_id, pattern in self.patterns.items():
            cwe_ids = pattern.get("cwe_ids", [])
            if cwe_id in cwe_ids:
                rec = Recommendation(
                    advisor_type=AdvisorType.SECURITY,
                    pattern_id=pattern_id,
                    title=pattern.get("title", "Security Pattern"),
                    description=pattern.get("description", ""),
                    severity=pattern.get("severity", "MEDIUM"),
                    pattern_reference=pattern.get("reference", ""),
                    code_example=pattern.get("code_example", ""),
                    rationale=pattern.get("rationale", "")
                )
                recommendations.append(rec)
        
        return recommendations


class SolidAdvisor(BaseAdvisor):
    """
    Provides SOLID principle recommendations.
    
    Recommends Single Responsibility, Open/Closed, Liskov Substitution,
    Interface Segregation, and Dependency Inversion patterns.
    """
    
    def __init__(self) -> None:
        """Initialize SolidAdvisor with SOLID patterns."""
        super().__init__("solid/*.yaml")
    
    def recommend(self, violation_type: str, context: Dict[str, Any] = None) -> List[Recommendation]:
        """
        Generate SOLID principle recommendations.
        
        Args:
            violation_type: Type of SOLID violation (e.g., "SRP", "OCP", "LSP", "ISP", "DIP")
            context: Additional context (class_name, method_name, etc.)
            
        Returns:
            List of Recommendation objects
        """
        recommendations = []
        context = context or {}
        
        # Find patterns matching this violation
        for pattern_id, pattern in self.patterns.items():
            violations = pattern.get("violations", [])
            if violation_type in violations:
                rec = Recommendation(
                    advisor_type=AdvisorType.SOLID,
                    pattern_id=pattern_id,
                    title=pattern.get("title", "SOLID Pattern"),
                    description=pattern.get("description", ""),
                    severity=pattern.get("severity", "MEDIUM"),
                    pattern_reference=pattern.get("reference", ""),
                    code_example=pattern.get("code_example", ""),
                    rationale=pattern.get("rationale", "")
                )
                recommendations.append(rec)
        
        return recommendations


class PerformanceAdvisor(BaseAdvisor):
    """Provides performance best practice recommendations."""
    
    def __init__(self) -> None:
        """Initialize PerformanceAdvisor with performance patterns."""
        super().__init__("performance/*.yaml")
    
    def recommend(self, pattern_name: str, context: Dict[str, Any] = None) -> List[Recommendation]:
        """Generate performance recommendations."""
        recommendations = []
        context = context or {}
        
        for pattern_id, pattern in self.patterns.items():
            if pattern_name in pattern.get("patterns", []):
                rec = Recommendation(
                    advisor_type=AdvisorType.PERFORMANCE,
                    pattern_id=pattern_id,
                    title=pattern.get("title", "Performance Pattern"),
                    description=pattern.get("description", ""),
                    severity=pattern.get("severity", "LOW"),
                    pattern_reference=pattern.get("reference", ""),
                )
                recommendations.append(rec)
        
        return recommendations


class ComplianceAdvisor(BaseAdvisor):
    """Provides governance and compliance recommendations."""
    
    def __init__(self) -> None:
        """Initialize ComplianceAdvisor with compliance patterns."""
        super().__init__("governance/*.yaml")
    
    def recommend(self, rule_name: str, context: Dict[str, Any] = None) -> List[Recommendation]:
        """Generate compliance recommendations."""
        recommendations = []
        context = context or {}
        
        for pattern_id, pattern in self.patterns.items():
            if rule_name in pattern.get("rules", []):
                rec = Recommendation(
                    advisor_type=AdvisorType.COMPLIANCE,
                    pattern_id=pattern_id,
                    title=pattern.get("title", "Compliance Pattern"),
                    description=pattern.get("description", ""),
                    severity=pattern.get("severity", "HIGH"),
                    pattern_reference=pattern.get("reference", ""),
                )
                recommendations.append(rec)
        
        return recommendations


class RecommendationEngine:
    """
    Advisory layer providing best practice recommendations (Phase 8.4).
    
    Decoupled from LENS analysis:
    - LENS runs first (fast, code analysis only)
    - Challenge Engine flags problems (binary gates)
    - RecommendationEngine suggests fixes (advisory, on-demand)
    
    Usage:
        >>> engine = RecommendationEngine()
        >>> 
        >>> # After security threat detected
        >>> recs = engine.recommend_for_security("CWE-94", {"threat": "eval injection"})
        >>> for rec in recs:
        >>>     print(f"Pattern: {rec.pattern_id}")
        >>>     print(f"Title: {rec.title}")
        >>>     print(f"Recommendation: {rec.description}")
        >>> 
        >>> # After SOLID violation
        >>> recs = engine.recommend_for_solid("SRP", {"class": "UserHandler"})
    """
    
    def __init__(self) -> None:
        """Initialize RecommendationEngine with all advisors."""
        self.security_advisor = SecurityAdvisor()
        self.solid_advisor = SolidAdvisor()
        self.performance_advisor = PerformanceAdvisor()
        self.compliance_advisor = ComplianceAdvisor()
        
        logger.info("RecommendationEngine initialized (Phase 8.4)")
    
    def recommend_for_security(
        self,
        cwe_id: str,
        context: Dict[str, Any] = None
    ) -> RecommendationResult:
        """
        Get security recommendations for a CWE.
        
        Args:
            cwe_id: CWE identifier (e.g., "CWE-94")
            context: Additional context
            
        Returns:
            RecommendationResult with security recommendations
        """
        try:
            recs = self.security_advisor.recommend(cwe_id, context)
            
            summary = f"Found {len(recs)} recommendation(s) for {cwe_id}"
            return RecommendationResult(
                success=True,
                recommendations=recs,
                summary=summary
            )
        except Exception as e:
            logger.error(f"Security recommendation failed: {str(e)}")
            return RecommendationResult(
                success=False,
                error=str(e)
            )
    
    def recommend_for_solid(
        self,
        violation_type: str,
        context: Dict[str, Any] = None
    ) -> RecommendationResult:
        """Get SOLID principle recommendations."""
        try:
            recs = self.solid_advisor.recommend(violation_type, context)
            
            summary = f"Found {len(recs)} recommendation(s) for {violation_type} violation"
            return RecommendationResult(
                success=True,
                recommendations=recs,
                summary=summary
            )
        except Exception as e:
            logger.error(f"SOLID recommendation failed: {str(e)}")
            return RecommendationResult(
                success=False,
                error=str(e)
            )
    
    def recommend_for_performance(
        self,
        pattern_name: str,
        context: Dict[str, Any] = None
    ) -> RecommendationResult:
        """Get performance recommendations."""
        try:
            recs = self.performance_advisor.recommend(pattern_name, context)
            
            summary = f"Found {len(recs)} performance recommendation(s)"
            return RecommendationResult(
                success=True,
                recommendations=recs,
                summary=summary
            )
        except Exception as e:
            logger.error(f"Performance recommendation failed: {str(e)}")
            return RecommendationResult(
                success=False,
                error=str(e)
            )
    
    def recommend_for_compliance(
        self,
        rule_name: str,
        context: Dict[str, Any] = None
    ) -> RecommendationResult:
        """Get compliance recommendations."""
        try:
            recs = self.compliance_advisor.recommend(rule_name, context)
            
            summary = f"Found {len(recs)} compliance recommendation(s)"
            return RecommendationResult(
                success=True,
                recommendations=recs,
                summary=summary
            )
        except Exception as e:
            logger.error(f"Compliance recommendation failed: {str(e)}")
            return RecommendationResult(
                success=False,
                error=str(e)
            )


# Singleton accessor for global use
_recommendation_engine_instance: Optional[RecommendationEngine] = None


def get_recommendation_engine() -> RecommendationEngine:
    """
    Factory function for RecommendationEngine singleton.
    
    Returns:
        RecommendationEngine instance
    """
    global _recommendation_engine_instance
    if _recommendation_engine_instance is None:
        _recommendation_engine_instance = RecommendationEngine()
    return _recommendation_engine_instance
