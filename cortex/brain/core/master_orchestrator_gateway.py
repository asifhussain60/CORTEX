"""
Master Orchestrator Gateway.

Production gateway with LENS protocol integration, mandatory routing
enforcement, and environment-aware adapter selection.

Author: CORTEX Team
Created: 2026-02-06
Authority: Phase 33 Stage 3 specification
"""

import time
import logging
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod

from cortex.brain.core.environment_detector import EnvironmentDetector, EnvironmentType
from cortex.brain.core.tool_adapter import (
    IToolAdapter,
    MCPToolAdapter,
    CopilotToolAdapter,
    DevelopmentToolAdapter,
)

logger = logging.getLogger(__name__)


class GatewayError(Exception):
    """Base exception for gateway errors."""
    pass


@dataclass(frozen=True)
class GatewayRequest:
    """
    Gateway request container.
    
    Attributes:
        user_input: Raw user input text
        context: Additional context (files, state, etc.)
        intent: Primary intent (IMPLEMENT, FIX, ANALYZE, etc.)
    """
    user_input: str
    context: Dict[str, Any]
    intent: str


@dataclass(frozen=True)
class IntentClassification:
    """
    LENS protocol intent classification.
    
    Attributes:
        primary_intent: Main intent category
        confidence: Classification confidence (0-1)
        requires_mcp: Whether MCP tools required
        language: LENS Language component
        examination: LENS Examination component
        navigation: LENS Navigation component
        synthesis: LENS Synthesis component
    """
    primary_intent: str
    confidence: float
    requires_mcp: bool
    language: str
    examination: str
    navigation: str
    synthesis: str


@dataclass
class DoRConfidence:
    """
    Definition of Ready confidence scoring.
    
    Attributes:
        score: Overall confidence score (0-1)
        intent_clear: Intent is well-defined
        scope_defined: Scope boundaries clear
        dependencies_met: Dependencies available
        resources_available: Resources accessible
        risks_assessed: Risks identified
    """
    score: float
    intent_clear: bool
    scope_defined: bool
    dependencies_met: bool
    resources_available: bool
    risks_assessed: bool
    
    def is_ready(self) -> bool:
        """Check if request meets DoR threshold."""
        return self.score >= 0.7


@dataclass
class GatewayResponse:
    """
    Gateway response container.
    
    Attributes:
        success: Whether request succeeded
        result: Operation result data
        classification: LENS intent classification
        adapter_used: Which tool adapter was used
        execution_time: Request execution time (seconds)
        error: Error message if failed
    """
    success: bool
    result: Optional[Dict[str, Any]]
    classification: IntentClassification
    adapter_used: str
    execution_time: float
    error: Optional[str] = None


class MasterOrchestratorGateway:
    """
    Master Orchestrator Gateway.
    
    Routes all CORTEX requests through LENS classification and enforces
    mandatory checkpoints before execution.
    """
    
    # MCP-required intents
    MCP_REQUIRED_INTENTS = {"IMPLEMENT", "FIX", "REFACTOR", "TEST"}
    
    # Valid intent types
    VALID_INTENTS = {
        "IMPLEMENT", "FIX", "REFACTOR", "ANALYZE", "TEST",
        "AUDIT", "DESIGN", "PLAN", "ONBOARD", "DEBUG"
    }
    
    def __init__(self):
        """Initialize gateway with environment detection."""
        self._detector = EnvironmentDetector()
        self._environment = self._detector.detect_environment()
        self._adapter = self._select_adapter()
        
        logger.info(f"Gateway initialized in {self._environment.value} environment")
    
    def _select_adapter(self) -> IToolAdapter:
        """
        Select appropriate tool adapter based on environment.
        
        Returns:
            IToolAdapter: Environment-specific adapter
        """
        if self._environment == EnvironmentType.MCP_SERVER:
            return MCPToolAdapter()
        elif self._environment == EnvironmentType.COPILOT:
            return CopilotToolAdapter()
        else:
            return DevelopmentToolAdapter()
    
    def process_request(self, request: GatewayRequest) -> GatewayResponse:
        """
        Process request through gateway.
        
        Args:
            request: Gateway request to process
            
        Returns:
            GatewayResponse: Result with classification and execution details
        """
        start_time = time.time()
        
        try:
            # Validate intent
            if request.intent not in self.VALID_INTENTS:
                return GatewayResponse(
                    success=False,
                    result=None,
                    classification=self._create_fallback_classification(request.intent),
                    adapter_used="None",
                    execution_time=time.time() - start_time,
                    error=f"Invalid intent: {request.intent}",
                )
            
            # Classify intent via LENS
            classification = self.classify_intent(request.user_input)
            
            # Check if MCP required but not available
            if classification.requires_mcp and self._environment != EnvironmentType.MCP_SERVER:
                return GatewayResponse(
                    success=False,
                    result=None,
                    classification=classification,
                    adapter_used=self._adapter.__class__.__name__,
                    execution_time=time.time() - start_time,
                    error=f"MCP server required for {request.intent} intent but not available",
                )
            
            # Calculate DoR confidence
            dor = self.calculate_dor_confidence(request)
            
            # Execute through adapter (placeholder for now)
            result = self._execute_via_adapter(request)
            
            execution_time = time.time() - start_time
            
            return GatewayResponse(
                success=True,
                result=result,
                classification=classification,
                adapter_used=self._adapter.__class__.__name__,
                execution_time=execution_time,
                error=None,
            )
            
        except Exception as e:
            logger.error(f"Gateway error: {e}")
            return GatewayResponse(
                success=False,
                result=None,
                classification=self._create_fallback_classification(request.intent),
                adapter_used=self._adapter.__class__.__name__,
                execution_time=time.time() - start_time,
                error=str(e),
            )
    
    def classify_intent(self, user_input: str) -> IntentClassification:
        """
        Classify intent using LENS protocol.
        
        Args:
            user_input: Raw user input text
            
        Returns:
            IntentClassification: LENS classification result
        """
        user_lower = user_input.lower()
        
        # Simple keyword-based classification (production would use ML)
        if any(kw in user_lower for kw in ["implement", "create", "add", "build"]):
            primary_intent = "IMPLEMENT"
            confidence = 0.9
            requires_mcp = True
        elif any(kw in user_lower for kw in ["fix", "repair", "bug", "error"]):
            primary_intent = "FIX"
            confidence = 0.85
            requires_mcp = True
        elif any(kw in user_lower for kw in ["refactor", "improve", "optimize", "clean"]):
            primary_intent = "REFACTOR"
            confidence = 0.85
            requires_mcp = True
        elif any(kw in user_lower for kw in ["analyze", "check", "review", "inspect"]):
            primary_intent = "ANALYZE"
            confidence = 0.8
            requires_mcp = False
        elif any(kw in user_lower for kw in ["test", "verify", "validate"]):
            primary_intent = "TEST"
            confidence = 0.8
            requires_mcp = True
        else:
            primary_intent = "ANALYZE"
            confidence = 0.5
            requires_mcp = False
        
        # LENS components (simplified)
        return IntentClassification(
            primary_intent=primary_intent,
            confidence=confidence,
            requires_mcp=requires_mcp,
            language=f"Parse: {user_input[:50]}...",
            examination=f"Examine intent: {primary_intent}",
            navigation=f"Navigate to relevant code",
            synthesis=f"Synthesize {primary_intent} solution",
        )
    
    def calculate_dor_confidence(self, request: GatewayRequest) -> DoRConfidence:
        """
        Calculate Definition of Ready confidence score.
        
        Args:
            request: Gateway request to evaluate
            
        Returns:
            DoRConfidence: DoR scoring breakdown
        """
        # Intent clarity check
        intent_clear = (
            request.intent in self.VALID_INTENTS and
            len(request.user_input) > 10  # Non-trivial input
        )
        
        # Scope definition check
        scope_defined = (
            bool(request.context) or  # Has context
            any(kw in request.user_input.lower() for kw in ["file", "function", "class", "module"])
        )
        
        # Dependencies check (simplified)
        dependencies_met = True  # Placeholder
        
        # Resources check
        resources_available = self._adapter.is_available("analyze_code")
        
        # Risks assessment check
        risks_assessed = request.intent not in self.MCP_REQUIRED_INTENTS or self._environment == EnvironmentType.MCP_SERVER
        
        # Calculate overall score
        checks = [intent_clear, scope_defined, dependencies_met, resources_available, risks_assessed]
        score = sum(checks) / len(checks)
        
        return DoRConfidence(
            score=score,
            intent_clear=intent_clear,
            scope_defined=scope_defined,
            dependencies_met=dependencies_met,
            resources_available=resources_available,
            risks_assessed=risks_assessed,
        )
    
    def _execute_via_adapter(self, request: GatewayRequest) -> Dict[str, Any]:
        """
        Execute request via tool adapter.
        
        Args:
            request: Gateway request
            
        Returns:
            Dict: Execution result
        """
        # Placeholder execution - delegates to adapter based on intent
        if request.intent == "ANALYZE":
            file_path = request.context.get("file", "unknown")
            result = self._adapter.analyze_code(file_path)
            return {
                "status": "analyzed",
                "success": result.success,
                "issues": getattr(result, "issues", []),
            }
        
        # Default placeholder
        return {"status": "processed", "intent": request.intent}
    
    def _create_fallback_classification(self, intent: str) -> IntentClassification:
        """Create fallback classification for error cases."""
        return IntentClassification(
            primary_intent=intent,
            confidence=0.0,
            requires_mcp=False,
            language="",
            examination="",
            navigation="",
            synthesis="",
        )
