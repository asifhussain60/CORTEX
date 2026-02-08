"""AC-PHASE43-018: LENS Protocol Integration

Validates Language→Examination→Navigation→Synthesis integration.

Target: 5/5 tests passing
AC-ID: AC-PHASE43-018
"""

import pytest
from typing import Dict, Any, List


class LENSProtocolIntegrator:
    """Integrate LENS protocol with Phase 43 (Phase 43: AC-PHASE43-018)."""
    
    def __init__(self):
        """Initialize LENS integrator."""
        self.protocol_version = "1.0"
    
    def process_request(self, user_request: str, 
                       codebase_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process user request through LENS protocol.
        
        Args:
            user_request: User's input request
            codebase_context: Repository/codebase context
            
        Returns:
            Structured LENS analysis result
        """
        return {
            "language": self._language(user_request),
            "examination": self._examination(user_request, codebase_context),
            "navigation": self._navigation(codebase_context),
            "synthesis": self._synthesis(
                self._language(user_request),
                self._examination(user_request, codebase_context),
                self._navigation(codebase_context)
            ),
        }
    
    def _language(self, request: str) -> Dict[str, Any]:
        """Language phase: Parse and classify request."""
        request_lower = request.lower()
        
        intent_map = {
            "analyze": "analysis",
            "refactor": "refactoring",
            "implement": "implementation",
            "test": "testing",
            "fix": "debugging",
            "document": "documentation",
        }
        
        detected_intent = "unknown"
        for keyword, intent_type in intent_map.items():
            if keyword in request_lower:
                detected_intent = intent_type
                break
        
        return {
            "raw_request": request,
            "intent": detected_intent,
            "keywords": request.split(),
            "confidence": 0.85 if detected_intent != "unknown" else 0.3,
        }
    
    def _examination(self, request: str, 
                    context: Dict[str, Any]) -> Dict[str, Any]:
        """Examination phase: Analyze request in code context."""
        # Count contextual matches
        request_words = set(request.lower().split())
        context_matches = 0
        
        if "primary_language" in context:
            context_matches += 1
        if "file_count" in context:
            context_matches += 1
        
        return {
            "context_relevance": context_matches / 2.0,
            "scope": "broad" if len(request) > 50 else "narrow",
            "complexity": "high" if context.get("file_count", 0) > 100 else "medium",
        }
    
    def _navigation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Navigation phase: Identify relevant code paths."""
        file_count = context.get("file_count", 0)
        primary_lang = context.get("primary_language", "Unknown")
        
        # Estimate number of relevant files
        relevance_score = min(1.0, file_count / 50.0)
        
        return {
            "estimated_scope_files": int(file_count * 0.3),  # 30% of files are relevant
            "entry_points": ["main.py", "api.py", "core.py"] if primary_lang == "Python" else ["index.js"],
            "relevance_score": relevance_score,
            "navigation_depth": "shallow" if file_count < 20 else "deep",
        }
    
    def _synthesis(self, language: Dict[str, Any],
                   examination: Dict[str, Any],
                   navigation: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesis phase: Combine LENS results into action plan."""
        overall_confidence = (
            language.get("confidence", 0.0) * 0.4 +
            examination.get("context_relevance", 0.0) * 0.3 +
            navigation.get("relevance_score", 0.0) * 0.3
        )
        
        action_plan = []
        intent = language.get("intent", "unknown")
        
        if intent != "unknown":
            action_plan = [
                f"Analyze {intent} request",
                f"Determine scope (relevance: {examination.get('scope')})",
                f"Identify entry points ({len(navigation.get('entry_points', []))} found)",
                "Generate recommendations",
                "Execute plan",
            ]
        
        return {
            "overall_confidence": min(1.0, overall_confidence),
            "recommended_action": intent if intent != "unknown" else "gather_more_info",
            "action_plan": action_plan,
            "ready_for_execution": overall_confidence > 0.6,
        }


class TestLENSProtocolIntegrator:
    """Tests for LENS protocol integration."""
    
    def test_integrator_initializes(self):
        """Validate integrator initializes."""
        integrator = LENSProtocolIntegrator()
        assert integrator is not None
        assert integrator.protocol_version == "1.0"
    
    def test_lens_parses_intent(self):
        """Validate intent parsing."""
        integrator = LENSProtocolIntegrator()
        
        result = integrator.process_request(
            "analyze the codebase",
            {"file_count": 50}
        )
        
        assert result["language"]["intent"] == "analysis"
        assert result["language"]["confidence"] > 0.7
    
    def test_lens_examines_context(self):
        """Validate context examination."""
        integrator = LENSProtocolIntegrator()
        
        result = integrator.process_request(
            "refactor main module",
            {"primary_language": "Python", "file_count": 100}
        )
        
        assert result["examination"]["context_relevance"] > 0
        assert result["examination"]["complexity"] in ["low", "medium", "high"]
    
    def test_lens_navigates_codebase(self):
        """Validate navigation phase."""
        integrator = LENSProtocolIntegrator()
        
        result = integrator.process_request(
            "implement new feature",
            {"file_count": 30, "primary_language": "Python"}
        )
        
        nav = result["navigation"]
        assert nav["estimated_scope_files"] > 0
        assert len(nav["entry_points"]) > 0
    
    def test_lens_synthesizes_recommendations(self):
        """Validate synthesis of recommendations."""
        integrator = LENSProtocolIntegrator()
        
        result = integrator.process_request(
            "implement authentication",
            {"file_count": 75, "primary_language": "Python"}
        )
        
        synthesis = result["synthesis"]
        assert "overall_confidence" in synthesis
        assert synthesis["recommended_action"] != "unknown"
        assert len(synthesis["action_plan"]) > 0
