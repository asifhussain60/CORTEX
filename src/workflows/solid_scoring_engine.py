"""
SOLID Scoring Engine

Calculates 0-100 compliance scores for SOLID principles.
Provides per-principle subscores and actionable recommendations.

Author: Asif Hussain
Date: December 5, 2025
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Tuple
from enum import Enum

from src.workflows.refactoring_intelligence import CodeSmell, CodeSmellType


@dataclass
class SOLIDScore:
    """SOLID compliance score with breakdown."""
    
    overall_score: int              # 0-100
    srp_score: int                  # 0-100
    ocp_score: int                  # 0-100
    lsp_score: int                  # 0-100
    isp_score: int                  # 0-100
    dip_score: int                  # 0-100
    coupling_score: int = 100       # 0-100
    cohesion_score: int = 100       # 0-100
    violations: List[CodeSmell] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


class SOLIDScoringEngine:
    """
    Calculates SOLID compliance scores with violation deductions.
    
    Scoring Algorithm:
    - Base Score: 100 points
    - Deductions per violation:
      * SRP: -15 points
      * OCP: -12 points
      * LSP: -10 points
      * ISP: -8 points
      * DIP: -10 points
      * Coupling: -10 points
      * Cohesion: -8 points
    - Minimum Score: 0 (no negative)
    """
    
    # Deduction amounts
    DEDUCTION_SRP = 15
    DEDUCTION_OCP = 12
    DEDUCTION_LSP = 10
    DEDUCTION_ISP = 8
    DEDUCTION_DIP = 10
    DEDUCTION_COUPLING = 10
    DEDUCTION_COHESION = 8
    
    # Score thresholds
    THRESHOLD_EXCELLENT = 90
    THRESHOLD_GOOD = 70
    THRESHOLD_POOR = 50
    
    def __init__(self):
        """Initialize scoring engine."""
        self.deduction_map = {
            CodeSmellType.SRP_VIOLATION: self.DEDUCTION_SRP,
            CodeSmellType.OCP_VIOLATION: self.DEDUCTION_OCP,
            CodeSmellType.LSP_VIOLATION: self.DEDUCTION_LSP,
            CodeSmellType.ISP_VIOLATION: self.DEDUCTION_ISP,
            CodeSmellType.DIP_VIOLATION: self.DEDUCTION_DIP,
            CodeSmellType.TIGHT_COUPLING: self.DEDUCTION_COUPLING,
            CodeSmellType.LOW_COHESION: self.DEDUCTION_COHESION,
            CodeSmellType.SOLID_VIOLATION: 10,  # Generic SOLID violation
        }
    
    def score_file(self, file_path: Path, smells: List[CodeSmell]) -> SOLIDScore:
        """
        Calculate SOLID compliance score for a file.
        
        Args:
            file_path: Path to file being scored
            smells: List of detected code smells
            
        Returns:
            SOLIDScore with overall score, subscores, and recommendations
        """
        # Filter for SOLID-related smells
        solid_smells = [
            s for s in smells
            if s.smell_type in self.deduction_map
        ]
        
        # Calculate overall score
        overall_score = 100
        
        for smell in solid_smells:
            deduction = self.deduction_map.get(smell.smell_type, 0)
            overall_score -= deduction
        
        # Ensure minimum score is 0
        overall_score = max(0, overall_score)
        
        # Calculate per-principle subscores
        srp_score = self._calculate_principle_score(solid_smells, CodeSmellType.SRP_VIOLATION)
        ocp_score = self._calculate_principle_score(solid_smells, CodeSmellType.OCP_VIOLATION)
        lsp_score = self._calculate_principle_score(solid_smells, CodeSmellType.LSP_VIOLATION)
        isp_score = self._calculate_principle_score(solid_smells, CodeSmellType.ISP_VIOLATION)
        dip_score = self._calculate_principle_score(solid_smells, CodeSmellType.DIP_VIOLATION)
        coupling_score = self._calculate_principle_score(solid_smells, CodeSmellType.TIGHT_COUPLING)
        cohesion_score = self._calculate_principle_score(solid_smells, CodeSmellType.LOW_COHESION)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(solid_smells, overall_score)
        
        return SOLIDScore(
            overall_score=overall_score,
            srp_score=srp_score,
            ocp_score=ocp_score,
            lsp_score=lsp_score,
            isp_score=isp_score,
            dip_score=dip_score,
            coupling_score=coupling_score,
            cohesion_score=cohesion_score,
            violations=solid_smells,
            recommendations=recommendations
        )
    
    def _calculate_principle_score(
        self,
        smells: List[CodeSmell],
        principle_type: CodeSmellType
    ) -> int:
        """
        Calculate score for a specific principle.
        
        Args:
            smells: All SOLID smells
            principle_type: Specific principle to score
            
        Returns:
            Score for this principle (0-100)
        """
        score = 100
        
        # Find violations for this principle
        principle_violations = [
            s for s in smells
            if s.smell_type == principle_type
        ]
        
        # Deduct for each violation
        deduction = self.deduction_map.get(principle_type, 0)
        score -= (deduction * len(principle_violations))
        
        return max(0, score)
    
    def _generate_recommendations(
        self,
        smells: List[CodeSmell],
        overall_score: int
    ) -> List[str]:
        """
        Generate actionable recommendations based on violations.
        
        Args:
            smells: Detected SOLID violations
            overall_score: Overall score
            
        Returns:
            List of recommendations (prioritized by severity)
        """
        recommendations = []
        
        # Only generate recommendations if score is below good threshold
        if overall_score >= self.THRESHOLD_GOOD:
            return recommendations
        
        # Sort smells by severity (high -> medium -> low)
        severity_order = {"high": 0, "medium": 1, "low": 2}
        sorted_smells = sorted(
            smells,
            key=lambda s: (severity_order.get(s.severity, 3), -s.confidence)
        )
        
        # Generate recommendations for top violations
        seen_principles = set()
        
        for smell in sorted_smells[:5]:  # Top 5 max
            principle = self._get_principle_name(smell.smell_type)
            
            # Avoid duplicate recommendations for same principle
            if principle in seen_principles:
                continue
            
            seen_principles.add(principle)
            
            # Generate specific recommendation
            recommendation = self._create_recommendation(smell)
            recommendations.append(recommendation)
        
        return recommendations
    
    def _get_principle_name(self, smell_type: CodeSmellType) -> str:
        """Get principle name from smell type."""
        principle_map = {
            CodeSmellType.SRP_VIOLATION: "SRP",
            CodeSmellType.OCP_VIOLATION: "OCP",
            CodeSmellType.LSP_VIOLATION: "LSP",
            CodeSmellType.ISP_VIOLATION: "ISP",
            CodeSmellType.DIP_VIOLATION: "DIP",
            CodeSmellType.TIGHT_COUPLING: "Coupling",
            CodeSmellType.LOW_COHESION: "Cohesion",
        }
        return principle_map.get(smell_type, "SOLID")
    
    def _create_recommendation(self, smell: CodeSmell) -> str:
        """
        Create specific recommendation for a violation.
        
        Args:
            smell: Code smell to address
            
        Returns:
            Actionable recommendation string
        """
        recommendations_map = {
            CodeSmellType.SRP_VIOLATION: (
                "SRP Violation: Extract responsibilities into separate classes. "
                "Each class should have one reason to change."
            ),
            CodeSmellType.OCP_VIOLATION: (
                "OCP Violation: Use abstraction and polymorphism instead of modifying existing code. "
                "Extend behavior through inheritance or composition."
            ),
            CodeSmellType.LSP_VIOLATION: (
                "LSP Violation: Ensure subclasses can replace base class without breaking behavior. "
                "Review method overrides and contracts."
            ),
            CodeSmellType.ISP_VIOLATION: (
                "ISP Violation: Split large interfaces into smaller, focused ones. "
                "Clients should not depend on methods they don't use."
            ),
            CodeSmellType.DIP_VIOLATION: (
                "DIP Violation: Depend on abstractions, not concrete implementations. "
                "Use dependency injection and interface-based design."
            ),
            CodeSmellType.TIGHT_COUPLING: (
                "Tight Coupling: Reduce dependencies between modules. "
                "Use dependency injection, events, or mediator patterns."
            ),
            CodeSmellType.LOW_COHESION: (
                "Low Cohesion: Group related functionality together. "
                "Split unrelated functionality into separate modules."
            ),
        }
        
        base_recommendation = recommendations_map.get(
            smell.smell_type,
            "Review SOLID principles and refactor accordingly."
        )
        
        # Add location for context
        location = smell.location.split(":")[1] if ":" in smell.location else "unknown"
        
        return f"Line {location}: {base_recommendation}"
    
    def format_score_report(self, score: SOLIDScore) -> str:
        """
        Format score as human-readable report.
        
        Args:
            score: SOLID score to format
            
        Returns:
            Formatted report string
        """
        lines = []
        lines.append("=" * 60)
        lines.append("📊 SOLID Compliance Score Report")
        lines.append("=" * 60)
        
        # Overall score with emoji
        emoji = self._get_score_emoji(score.overall_score)
        lines.append(f"\nOverall Score: {score.overall_score}% {emoji}")
        
        # Score interpretation
        interpretation = self._interpret_score(score.overall_score)
        lines.append(f"Status: {interpretation}")
        
        # Per-principle breakdown
        lines.append("\n" + "-" * 60)
        lines.append("Per-Principle Scores:")
        lines.append("-" * 60)
        lines.append(f"  SRP (Single Responsibility):    {score.srp_score}%")
        lines.append(f"  OCP (Open/Closed):               {score.ocp_score}%")
        lines.append(f"  LSP (Liskov Substitution):       {score.lsp_score}%")
        lines.append(f"  ISP (Interface Segregation):     {score.isp_score}%")
        lines.append(f"  DIP (Dependency Inversion):      {score.dip_score}%")
        lines.append(f"  Coupling:                        {score.coupling_score}%")
        lines.append(f"  Cohesion:                        {score.cohesion_score}%")
        
        # Violations summary
        lines.append("\n" + "-" * 60)
        lines.append(f"Total Violations: {len(score.violations)}")
        lines.append("-" * 60)
        
        # Recommendations
        if score.recommendations:
            lines.append("\n" + "-" * 60)
            lines.append("💡 Top Recommendations:")
            lines.append("-" * 60)
            for i, rec in enumerate(score.recommendations, 1):
                lines.append(f"{i}. {rec}")
        
        lines.append("\n" + "=" * 60)
        
        return "\n".join(lines)
    
    def _get_score_emoji(self, score: int) -> str:
        """Get emoji for score level."""
        if score >= self.THRESHOLD_EXCELLENT:
            return "✅"
        elif score >= self.THRESHOLD_GOOD:
            return "⚠️"
        else:
            return "❌"
    
    def _interpret_score(self, score: int) -> str:
        """Interpret score level."""
        if score >= self.THRESHOLD_EXCELLENT:
            return "Excellent - Production ready"
        elif score >= self.THRESHOLD_GOOD:
            return "Good - Minor improvements recommended"
        elif score >= self.THRESHOLD_POOR:
            return "Fair - Refactoring needed"
        else:
            return "Poor - Significant refactoring required"
