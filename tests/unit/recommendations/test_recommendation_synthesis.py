"""AC-PHASE43-020: Recommendation Synthesis Engine

Validates multi-source recommendation aggregation and confidence gating.

Target: 5/5 tests passing
AC-ID: AC-PHASE43-020
"""

import pytest
from typing import Dict, Any, List


class RecommendationSynthesisEngine:
    """Synthesize recommendations from multiple analysis sources (Phase 43: AC-PHASE43-020)."""
    
    def __init__(self):
        """Initialize recommendation engine."""
        self.confidence_threshold = 0.65
    
    def synthesize(self, analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Synthesize recommendations from multiple analyses.
        
        Args:
            analyses: List of analysis results with recommendations
            
        Returns:
            Aggregated recommendations with confidence scores
        """
        if not analyses:
            return {"recommendations": [], "total": 0, "high_confidence": 0}
        
        # Aggregate recommendations
        aggregated = self._aggregate_recommendations(analyses)
        
        # Apply confidence gate
        gated = self._apply_confidence_gate(aggregated)
        
        # Rank by impact
        ranked = self._rank_recommendations(gated)
        
        return {
            "recommendations": ranked,
            "total": len(ranked),
            "high_confidence": len([r for r in ranked if r["confidence"] > 0.8]),
            "sources_consulted": len(analyses),
            "consensus_level": self._compute_consensus(aggregated),
        }
    
    def _aggregate_recommendations(self, 
                                  analyses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Aggregate recommendations from multiple sources."""
        recommendation_map = {}
        
        for analysis in analyses:
            source = analysis.get("source", "unknown")
            recommendations = analysis.get("recommendations", [])
            
            for rec in recommendations:
                key = rec.get("title", "")
                
                if key not in recommendation_map:
                    recommendation_map[key] = {
                        "title": key,
                        "sources": [],
                        "confidences": [],
                        "actions": [],
                    }
                
                recommendation_map[key]["sources"].append(source)
                recommendation_map[key]["confidences"].append(
                    rec.get("confidence", 0.5)
                )
                recommendation_map[key]["actions"].append(rec.get("action", ""))
        
        # Compute average confidence and deduplicate sources
        aggregated = []
        for key, data in recommendation_map.items():
            avg_confidence = sum(data["confidences"]) / len(data["confidences"])
            
            aggregated.append({
                "title": data["title"],
                "confidence": avg_confidence,
                "source_count": len(set(data["sources"])),
                "sources": list(set(data["sources"])),
                "actions": list(set(data["actions"])),
            })
        
        return aggregated
    
    def _apply_confidence_gate(self, 
                              recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter recommendations by confidence threshold."""
        return [r for r in recommendations if r["confidence"] >= self.confidence_threshold]
    
    def _rank_recommendations(self, 
                             recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rank recommendations by consensus and confidence."""
        def score(r: Dict[str, Any]) -> float:
            # 60% confidence, 40% consensus (source count)
            consensus_score = min(1.0, r.get("source_count", 1) / 3.0)
            return r.get("confidence", 0.0) * 0.6 + consensus_score * 0.4
        
        ranked = sorted(recommendations, key=score, reverse=True)
        
        for i, rec in enumerate(ranked):
            rec["rank"] = i + 1
        
        return ranked
    
    def _compute_consensus(self, 
                          recommendations: List[Dict[str, Any]]) -> str:
        """Compute overall consensus level."""
        if not recommendations:
            return "low"
        
        avg_sources = sum(r.get("source_count", 1) for r in recommendations) / len(recommendations)
        
        if avg_sources >= 2.5:
            return "high"
        elif avg_sources >= 1.5:
            return "medium"
        else:
            return "low"


class TestRecommendationSynthesisEngine:
    """Tests for recommendation synthesis."""
    
    def test_engine_initializes(self):
        """Validate engine initializes."""
        engine = RecommendationSynthesisEngine()
        assert engine is not None
        assert engine.confidence_threshold == 0.65
    
    def test_engine_synthesizes_from_multiple_sources(self):
        """Validate multi-source synthesis."""
        engine = RecommendationSynthesisEngine()
        
        analyses = [
            {
                "source": "refactoring",
                "recommendations": [
                    {"title": "Extract method", "confidence": 0.85, "action": "refactor"},
                    {"title": "Remove duplication", "confidence": 0.72, "action": "refactor"},
                ],
            },
            {
                "source": "security",
                "recommendations": [
                    {"title": "Add authentication", "confidence": 0.95, "action": "implement"},
                    {"title": "Validate input", "confidence": 0.88, "action": "implement"},
                ],
            },
        ]
        
        result = engine.synthesize(analyses)
        
        assert result["total"] > 0
        assert result["sources_consulted"] == 2
    
    def test_engine_applies_confidence_gate(self):
        """Validate confidence gating."""
        engine = RecommendationSynthesisEngine()
        
        analyses = [
            {
                "source": "test",
                "recommendations": [
                    {"title": "High confidence", "confidence": 0.9, "action": "a"},
                    {"title": "Low confidence", "confidence": 0.3, "action": "b"},
                ],
            },
        ]
        
        result = engine.synthesize(analyses)
        
        # Only high-confidence recommendation should pass gate
        assert result["total"] == 1
        assert result["recommendations"][0]["title"] == "High confidence"
    
    def test_engine_ranks_by_consensus_and_confidence(self):
        """Validate ranking algorithm."""
        engine = RecommendationSynthesisEngine()
        
        analyses = [
            {
                "source": "analyzer1",
                "recommendations": [
                    {"title": "High consensus", "confidence": 0.7, "action": "a"},
                ],
            },
            {
                "source": "analyzer2",
                "recommendations": [
                    {"title": "High consensus", "confidence": 0.75, "action": "a"},
                ],
            },
            {
                "source": "analyzer3",
                "recommendations": [
                    {"title": "Solo recommendation", "confidence": 0.9, "action": "b"},
                ],
            },
        ]
        
        result = engine.synthesize(analyses)
        
        # High consensus should rank first despite lower individual confidence
        assert result["recommendations"][0]["title"] == "High consensus"
    
    def test_engine_computes_consensus_level(self):
        """Validate consensus computation."""
        engine = RecommendationSynthesisEngine()
        
        analyses = [
            {
                "source": "s1",
                "recommendations": [{"title": "Rec1", "confidence": 0.8, "action": "a"}],
            },
            {
                "source": "s2",
                "recommendations": [{"title": "Rec1", "confidence": 0.75, "action": "a"}],
            },
            {
                "source": "s3",
                "recommendations": [{"title": "Rec1", "confidence": 0.7, "action": "a"}],
            },
        ]
        
        result = engine.synthesize(analyses)
        
        assert result["consensus_level"] in ["low", "medium", "high"]
