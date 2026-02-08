"""AC-PHASE43-019: Challenge Generation Engine

Validates multi-criteria challenge creation and ranking.

Target: 6/6 tests passing
AC-ID: AC-PHASE43-019
"""

import pytest
from typing import Dict, Any, List


class ChallengeGenerationEngine:
    """Generate challenges for design validation (Phase 43: AC-PHASE43-019)."""
    
    def __init__(self):
        """Initialize challenge engine."""
        self.challenge_count = 0
    
    def generate_challenges(self, design: Dict[str, Any],
                           context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate challenges for design validation.
        
        Args:
            design: Design specification
            context: Domain context
            
        Returns:
            Ranked list of challenges
        """
        self.challenge_count = 0
        
        challenges = []
        
        # Generate architectural challenges
        arch_challenges = self._generate_architectural_challenges(design)
        challenges.extend(arch_challenges)
        
        # Generate security challenges
        sec_challenges = self._generate_security_challenges(design, context)
        challenges.extend(sec_challenges)
        
        # Generate performance challenges
        perf_challenges = self._generate_performance_challenges(design)
        challenges.extend(perf_challenges)
        
        # Generate scalability challenges
        scale_challenges = self._generate_scalability_challenges(design)
        challenges.extend(scale_challenges)
        
        # Rank by impact
        ranked = self._rank_challenges(challenges)
        self.challenge_count = len(ranked)
        
        return {
            "total_challenges": len(ranked),
            "challenges": ranked,
            "critical_count": len([c for c in ranked if c["severity"] == "critical"]),
            "summary": self._summarize(ranked),
        }
    
    def _generate_architectural_challenges(self, 
                                          design: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate architectural challenges."""
        challenges = []
        
        if design.get("components", 0) > 10:
            challenges.append({
                "type": "architectural",
                "severity": "high",
                "title": "High component count",
                "description": "Design has many components; review coupling",
                "impact_score": 0.7,
            })
        
        if design.get("layers", 0) > 5:
            challenges.append({
                "type": "architectural",
                "severity": "medium",
                "title": "Many architectural layers",
                "description": "Review layer separation and communication",
                "impact_score": 0.6,
            })
        
        return challenges
    
    def _generate_security_challenges(self, design: Dict[str, Any],
                                     context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate security challenges."""
        challenges = []
        
        if design.get("authentication") != "oauth":
            challenges.append({
                "type": "security",
                "severity": "critical",
                "title": "Non-standard authentication",
                "description": "Use OAuth2 or similar for security",
                "impact_score": 0.95,
            })
        
        if not design.get("encryption_at_rest", False):
            challenges.append({
                "type": "security",
                "severity": "critical",
                "title": "Missing encryption at rest",
                "description": "Implement encryption for sensitive data",
                "impact_score": 0.9,
            })
        
        return challenges
    
    def _generate_performance_challenges(self, 
                                        design: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate performance challenges."""
        challenges = []
        
        if design.get("caching_strategy") == "none":
            challenges.append({
                "type": "performance",
                "severity": "high",
                "title": "No caching strategy",
                "description": "Implement caching for frequently accessed data",
                "impact_score": 0.75,
            })
        
        if design.get("database_optimization", False) is False:
            challenges.append({
                "type": "performance",
                "severity": "medium",
                "title": "Database not optimized",
                "description": "Review indexes and query patterns",
                "impact_score": 0.65,
            })
        
        return challenges
    
    def _generate_scalability_challenges(self, 
                                        design: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate scalability challenges."""
        challenges = []
        
        if design.get("horizontal_scaling") != "yes":
            challenges.append({
                "type": "scalability",
                "severity": "high",
                "title": "Not horizontally scalable",
                "description": "Design should support horizontal scaling",
                "impact_score": 0.8,
            })
        
        return challenges
    
    def _rank_challenges(self, challenges: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rank challenges by impact."""
        severity_scores = {
            "critical": 1.0,
            "high": 0.8,
            "medium": 0.6,
            "low": 0.3,
        }
        
        def score_challenge(c: Dict[str, Any]) -> float:
            severity = severity_scores.get(c.get("severity", "medium"), 0.5)
            impact = c.get("impact_score", 0.5)
            return severity * impact
        
        ranked = sorted(challenges, key=score_challenge, reverse=True)
        
        # Add ranking
        for i, challenge in enumerate(ranked):
            challenge["rank"] = i + 1
        
        return ranked
    
    def _summarize(self, challenges: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Summarize challenges."""
        critical = len([c for c in challenges if c["severity"] == "critical"])
        high = len([c for c in challenges if c["severity"] == "high"])
        medium = len([c for c in challenges if c["severity"] == "medium"])
        low = len([c for c in challenges if c["severity"] == "low"])
        
        return {
            "critical": critical,
            "high": high,
            "medium": medium,
            "low": low,
            "total": len(challenges),
            "risk_level": "critical" if critical > 0 else ("high" if high > 0 else "medium"),
        }


class TestChallengeGenerationEngine:
    """Tests for challenge generation."""
    
    def test_engine_initializes(self):
        """Validate engine initializes."""
        engine = ChallengeGenerationEngine()
        assert engine is not None
        assert engine.challenge_count == 0
    
    def test_engine_generates_challenges(self):
        """Validate challenge generation."""
        engine = ChallengeGenerationEngine()
        
        design = {
            "components": 15,
            "layers": 6,
            "authentication": "custom",
            "encryption_at_rest": False,
            "caching_strategy": "none",
            "horizontal_scaling": "no",
        }
        
        result = engine.generate_challenges(design, {})
        
        assert result["total_challenges"] > 0
        assert len(result["challenges"]) == result["total_challenges"]
    
    def test_engine_ranks_by_severity(self):
        """Validate challenge ranking."""
        engine = ChallengeGenerationEngine()
        
        design = {
            "authentication": "custom",
            "encryption_at_rest": False,
        }
        
        result = engine.generate_challenges(design, {})
        challenges = result["challenges"]
        
        # First challenge should be highest severity
        assert challenges[0]["severity"] in ["critical", "high"]
    
    def test_engine_counts_critical_issues(self):
        """Validate critical issue counting."""
        engine = ChallengeGenerationEngine()
        
        design = {
            "authentication": "custom",
            "encryption_at_rest": False,
        }
        
        result = engine.generate_challenges(design, {})
        
        assert result["critical_count"] >= 2  # At least 2 critical security issues
    
    def test_engine_summarizes_challenges(self):
        """Validate challenge summary."""
        engine = ChallengeGenerationEngine()
        
        design = {"components": 20}  # Will trigger high severity challenge
        
        result = engine.generate_challenges(design, {})
        summary = result["summary"]
        
        assert summary["total"] >= 0
        assert "risk_level" in summary
    
    def test_engine_detects_unsafe_design(self):
        """Validate detection of unsafe design."""
        engine = ChallengeGenerationEngine()
        
        design = {
            "authentication": "basic",
            "encryption_at_rest": False,
            "components": 20,
            "horizontal_scaling": "no",
        }
        
        result = engine.generate_challenges(design, {})
        
        assert result["summary"]["risk_level"] == "critical"
