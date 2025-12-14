"""
Request Validator & Enhancer - Main Implementation

This module provides the core request validation and enhancement functionality
for CORTEX 2.0. It analyzes user requests for viability, historical patterns,
and potential enhancements before routing to specialist agents.

Usage:
    from examples.request_validator import request_validator
    
    validator = request_validator.RequestValidator(tier1_api, tier2_kg, tier3_context)
    result = validator.validate_and_enhance(request, conversation_id)
    
    if result.decision == ValidationDecision.CHALLENGE:
        # Handle blocking issues
        pass
    elif result.decision == ValidationDecision.ENHANCE:
        # Show enhancements to user
        pass
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import time
import uuid
from datetime import datetime


class ValidationDecision(Enum):
    """Decision types for request validation."""
    APPROVE = "approve"
    CHALLENGE = "challenge"
    ENHANCE = "enhance"
    ADVISE = "advise"


@dataclass
class ValidationResult:
    """Result of validation analysis."""
    decision: ValidationDecision
    confidence: float
    
    viability_score: float
    viability_issues: List[Dict[str, Any]]
    
    similar_patterns: List[Dict[str, Any]]
    success_rate: Optional[float]
    
    enhancements: List[Dict[str, Any]]
    estimated_value: float
    
    message: str
    alternatives: List[str]
    requires_user_input: bool
    
    analysis_time_ms: float
    validation_id: str
    timestamp: str


class RequestValidator:
    """
    Main validator orchestrator.
    
    Coordinates viability, historical, and enhancement analysis to provide
    intelligent request validation and improvement suggestions.
    """
    
    def __init__(self, tier1_api, tier2_kg, tier3_context):
        """
        Initialize validator with CORTEX tier APIs.
        
        Args:
            tier1_api: Tier 1 Working Memory API
            tier2_kg: Tier 2 Knowledge Graph
            tier3_context: Tier 3 Context Intelligence
        """
        self.tier1 = tier1_api
        self.tier2 = tier2_kg
        self.tier3 = tier3_context
        
        # Initialize sub-analyzers
        from .viability_analyzer import ViabilityAnalyzer
        from .historical_analyzer import HistoricalAnalyzer
        from .enhancement_analyzer import EnhancementAnalyzer
        
        self.viability = ViabilityAnalyzer(tier2_kg, tier3_context)
        self.historical = HistoricalAnalyzer(tier1_api, tier2_kg)
        self.enhancement = EnhancementAnalyzer(tier2_kg)
    
    def validate_and_enhance(
        self,
        request,
        conversation_id: str,
        skip_checks: Optional[List[str]] = None
    ) -> ValidationResult:
        """
        Validate request and suggest enhancements.
        
        Args:
            request: Agent request to validate
            conversation_id: Current conversation ID
            skip_checks: List of checks to skip ('viability', 'historical', 'enhancement')
            
        Returns:
            ValidationResult with decision and recommendations
        """
        start_time = time.perf_counter()
        skip_checks = skip_checks or []
        
        validation_id = str(uuid.uuid4())
        
        # Run viability analysis first (fail fast on critical issues)
        viability_result = None
        if "viability" not in skip_checks:
            viability_result = self.viability.analyze(request)
            
            # Fail fast on critical issues
            if viability_result.get('has_critical_issues'):
                return self._create_blocking_challenge(
                    validation_id,
                    viability_result,
                    time.perf_counter() - start_time
                )
        
        # Run historical and enhancement analyses
        historical_result = None
        enhancement_result = None
        
        if "historical" not in skip_checks:
            historical_result = self.historical.analyze(request, conversation_id)
        
        if "enhancement" not in skip_checks:
            enhancement_result = self.enhancement.analyze(request)
        
        # Synthesize results
        validation_result = self._synthesize(
            validation_id,
            request,
            viability_result,
            historical_result,
            enhancement_result,
            time.perf_counter() - start_time
        )
        
        # Track for learning
        self._track_validation(validation_result, request, conversation_id)
        
        return validation_result
    
    def _synthesize(
        self,
        validation_id: str,
        request,
        viability,
        historical,
        enhancement,
        analysis_time: float
    ) -> ValidationResult:
        """Synthesize analysis results into recommendation."""
        
        # Priority 1: Critical viability issues (BLOCK)
        if viability and viability.get('has_critical_issues'):
            return ValidationResult(
                decision=ValidationDecision.CHALLENGE,
                confidence=viability['confidence'],
                viability_score=viability['confidence'],
                viability_issues=viability['issues'],
                similar_patterns=[],
                success_rate=None,
                enhancements=[],
                estimated_value=0.0,
                message=self._format_critical_message(viability),
                alternatives=viability['alternatives'],
                requires_user_input=True,
                analysis_time_ms=analysis_time * 1000,
                validation_id=validation_id,
                timestamp=datetime.now().isoformat()
            )
        
        # Priority 2: High viability issues with good alternatives (ADVISE)
        if viability and viability.get('issues'):
            high_issues = [i for i in viability['issues'] if i['severity'] == 'HIGH']
            if high_issues and historical and historical.get('recommended_workflow'):
                return ValidationResult(
                    decision=ValidationDecision.ADVISE,
                    confidence=0.85,
                    viability_score=viability['confidence'],
                    viability_issues=high_issues,
                    similar_patterns=historical.get('similar_patterns', []),
                    success_rate=historical.get('success_rate'),
                    enhancements=[],
                    estimated_value=0.0,
                    message=self._format_advisory_message(viability, historical),
                    alternatives=[historical['recommended_workflow']],
                    requires_user_input=True,
                    analysis_time_ms=analysis_time * 1000,
                    validation_id=validation_id,
                    timestamp=datetime.now().isoformat()
                )
        
        # Priority 3: Historical success pattern or enhancements available (ENHANCE)
        enhancements = []
        if historical and historical.get('reusable_components'):
            enhancements.append({
                'type': 'historical_pattern',
                'title': f"Reuse proven pattern: {historical['recommended_workflow']}",
                'value': 0.8,
                'time_saved_min': 10
            })
        
        if enhancement and enhancement.get('enhancements'):
            enhancements.extend(enhancement['enhancements'])
        
        if enhancements:
            return ValidationResult(
                decision=ValidationDecision.ENHANCE,
                confidence=0.9,
                viability_score=1.0,
                viability_issues=[],
                similar_patterns=historical.get('similar_patterns', []) if historical else [],
                success_rate=historical.get('success_rate') if historical else None,
                enhancements=enhancements,
                estimated_value=sum(e.get('value', 0) for e in enhancements),
                message=self._format_enhancement_message(historical, enhancement),
                alternatives=[],
                requires_user_input=True,
                analysis_time_ms=analysis_time * 1000,
                validation_id=validation_id,
                timestamp=datetime.now().isoformat()
            )
        
        # Priority 4: No issues, approve (APPROVE)
        return ValidationResult(
            decision=ValidationDecision.APPROVE,
            confidence=0.95,
            viability_score=1.0,
            viability_issues=[],
            similar_patterns=[],
            success_rate=None,
            enhancements=[],
            estimated_value=0.0,
            message="Request looks good! Ready to proceed.",
            alternatives=[],
            requires_user_input=False,
            analysis_time_ms=analysis_time * 1000,
            validation_id=validation_id,
            timestamp=datetime.now().isoformat()
        )
    
    def _create_blocking_challenge(
        self,
        validation_id: str,
        viability_result,
        analysis_time: float
    ) -> ValidationResult:
        """Create blocking challenge for critical issues."""
        return ValidationResult(
            decision=ValidationDecision.CHALLENGE,
            confidence=viability_result['confidence'],
            viability_score=viability_result['confidence'],
            viability_issues=viability_result['issues'],
            similar_patterns=[],
            success_rate=None,
            enhancements=[],
            estimated_value=0.0,
            message=self._format_critical_message(viability_result),
            alternatives=viability_result['alternatives'],
            requires_user_input=True,
            analysis_time_ms=analysis_time * 1000,
            validation_id=validation_id,
            timestamp=datetime.now().isoformat()
        )
    
    def _format_critical_message(self, viability_result) -> str:
        """Format message for critical issues."""
        issues = viability_result['issues']
        message = "⚠️ **Critical Issues Detected:**\n\n"
        for issue in issues:
            message += f"- **{issue['title']}**: {issue['description']}\n"
        message += "\n💡 Consider these alternatives:"
        return message
    
    def _format_advisory_message(self, viability_result, historical_result) -> str:
        """Format advisory message."""
        return f"💡 **Suggestion:** Based on historical patterns, consider using the {historical_result.get('recommended_workflow', 'proven workflow')} approach."
    
    def _format_enhancement_message(self, historical_result, enhancement_result) -> str:
        """Format enhancement message."""
        return "✨ **Enhancements Available:** I found some ways to improve this request."
    
    def _track_validation(self, result: ValidationResult, request, conversation_id: str):
        """Track validation for learning."""
        # Store validation result in Tier 1 for learning
        try:
            self.tier1.store_validation(
                validation_id=result.validation_id,
                conversation_id=conversation_id,
                decision=result.decision.value,
                confidence=result.confidence,
                timestamp=result.timestamp
            )
        except Exception as e:
            # Non-critical, just log
            print(f"Warning: Could not track validation: {e}")
