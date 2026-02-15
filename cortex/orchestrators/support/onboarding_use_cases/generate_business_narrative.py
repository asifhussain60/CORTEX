"""
AC-054A-S1-10,11,12: GenerateBusinessNarrativeUseCase Implementation

Use case for generating business-language narratives from repository analysis.

Author: Phase 54-A Implementation (TDD)
Created: 2026-02-15
"""

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class BusinessNarrative:
    """Business narrative model."""
    title: str
    summary: str
    key_insights: List[str]
    target_audience: str
    confidence_score: float  # 0.0-1.0


class GenerateBusinessNarrativeUseCase:
    """
    Generate business narrative from repository analysis.
    
    Transforms technical analysis into business-friendly language.
    """
    
    def __init__(self) -> None:
        """Initialize narrative generator."""
        pass
    
    def execute(self, repo_data: Dict[str, Any]) -> BusinessNarrative:
        """
        Execute narrative generation.
        
        Args:
            repo_data: Repository analysis data
        
        Returns:
            BusinessNarrative object
        """
        name = repo_data.get("name", "Unknown Repository")
        description = repo_data.get("description", "")
        language = repo_data.get("language", "Unknown")
        
        # Generate title
        title = f"{name}: Enterprise Software Analysis"
        
        # Generate summary
        summary = self._generate_summary(repo_data)
        
        # Generate key insights
        key_insights = self._generate_insights(repo_data)
        
        # Detect target audience
        target_audience = self._detect_audience(repo_data)
        
        # Calculate confidence
        confidence = self._calculate_confidence(repo_data)
        
        return BusinessNarrative(
            title=title,
            summary=summary,
            key_insights=key_insights,
            target_audience=target_audience,
            confidence_score=confidence
        )
    
    def _generate_summary(self, repo_data: Dict[str, Any]) -> str:
        """Generate executive summary."""
        name = repo_data.get("name", "repository")
        description = repo_data.get("description", "")
        if description:
            return f"{name}: {description}"
        return f"{name} is a software system providing core business capabilities"
    
    def _generate_insights(self, repo_data: Dict[str, Any]) -> List[str]:
        """Generate key business insights."""
        insights = []
        
        # Analyze metrics
        metrics = repo_data.get("metrics", {})
        if metrics.get("test_coverage", 0) > 0.8:
            insights.append("High test coverage indicates production readiness")
        
        if "dependencies" in repo_data:
            deps = repo_data["dependencies"]
            if isinstance(deps, list) and len(deps) > 0:
                insights.append(f"Leverages {len(deps)} third-party libraries")
        
        # Analyze activity
        stars = repo_data.get("stars", 0)
        if stars > 1000:
            insights.append("Strong community adoption")
        
        if not insights:
            insights.append("Active development project")
        
        return insights
    
    def _detect_audience(self, repo_data: Dict[str, Any]) -> str:
        """Detect target audience from code patterns."""
        language = repo_data.get("language", "").lower()
        key_files = repo_data.get("key_files", [])
        
        # Pattern matching
        if language == "python":
            if any("model" in f.lower() or "training" in f.lower() for f in key_files):
                return "Data Scientists"
            elif any("api" in f.lower() or "server" in f.lower() for f in key_files):
                return "Backend Engineers"
            else:
                return "Python Developers"
        elif language in ["javascript", "typescript"]:
            return "Frontend Developers"
        elif "ops" in " ".join(key_files).lower():
            return "DevOps"
        
        return "Software Engineers"
    
    def _calculate_confidence(self, repo_data: Dict[str, Any]) -> float:
        """Calculate confidence score for narrative."""
        score = 0.5  # Base score
        
        # Boost for having description
        if repo_data.get("description"):
            score += 0.2
        
        # Boost for having metrics
        if repo_data.get("metrics"):
            score += 0.2
        
        # Boost for having key files
        if repo_data.get("key_files"):
            score += 0.1
        
        return min(1.0, score)
