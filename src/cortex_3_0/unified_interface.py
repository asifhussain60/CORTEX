"""
CORTEX 3.0 Unified Interface
============================

Central coordination point for all CORTEX 3.0 capabilities:
- Dual-Channel Memory coordination
- Enhanced Agent orchestration  
- Smart Context Intelligence integration
- Backward compatibility with 2.0 operations

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import asyncio
import logging

from .dual_channel_memory import DualChannelMemory, ChannelType
from .enhanced_agents import EnhancedAgentSystem, MultiAgentOrchestrator, WorkflowPlan
from .smart_context_intelligence import SmartContextIntelligence

# Import existing 2.0 systems for backward compatibility
try:
    from ..operations.universal_operations import UniversalOperationsSystem
    from ..cortex_agents.intent_router import IntentRouter
except ImportError:
    # Fallback for development - will be replaced with actual imports
    class UniversalOperationsSystem:
        def __init__(self, brain_path): self.brain_path = brain_path
        def execute_operation(self, operation, params): 
            return {"success": True, "message": "2.0 compatibility placeholder"}
    
    class IntentRouter:
        def route_request(self, message): 
            return {"operation": "help", "agent": "universal_operations"}


class CortexMode(Enum):
    """CORTEX operation modes"""
    CORTEX_20_COMPATIBILITY = "2.0_compatibility"  # Use 2.0 systems only
    CORTEX_30_FULL = "3.0_full"  # Use all 3.0 capabilities
    CORTEX_30_HYBRID = "3.0_hybrid"  # Mix of 2.0 and 3.0 based on request


class RequestComplexity(Enum):
    """Request complexity levels for routing decisions"""
    SIMPLE = "simple"      # Single agent, basic operations
    MODERATE = "moderate"  # Multi-step, coordination needed
    COMPLEX = "complex"    # Multi-agent, long-term memory needed
    ADAPTIVE = "adaptive"  # ML-enhanced, predictive capabilities needed


@dataclass
class CortexRequest:
    """Unified request structure for CORTEX 3.0"""
    user_message: str
    request_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    complexity: Optional[RequestComplexity] = None
    preferred_mode: Optional[CortexMode] = None
    session_id: Optional[str] = None
    timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.request_id is None:
            self.request_id = f"req_{int(self.timestamp.timestamp())}"
        if self.context is None:
            self.context = {}


@dataclass 
class CortexResponse:
    """Unified response structure for CORTEX 3.0"""
    request_id: str
    success: bool
    response_message: str
    execution_details: Dict[str, Any] = None
    mode_used: CortexMode = None
    complexity_detected: RequestComplexity = None
    agents_involved: List[str] = None
    duration_seconds: float = 0.0
    context_used: Dict[str, Any] = None
    recommendations: List[str] = None
    session_id: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.execution_details is None:
            self.execution_details = {}
        if self.agents_involved is None:
            self.agents_involved = []
        if self.context_used is None:
            self.context_used = {}
        if self.recommendations is None:
            self.recommendations = []


class RequestAnalyzer:
    """Analyzes requests to determine optimal processing strategy"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def analyze_request(self, request: CortexRequest) -> Dict[str, Any]:
        """Analyze request to determine complexity and routing strategy"""
        
        complexity = self._determine_complexity(request.user_message)
        optimal_mode = self._determine_optimal_mode(complexity, request.context)
        required_capabilities = self._identify_required_capabilities(request.user_message)
        
        return {
            "complexity": complexity,
            "optimal_mode": optimal_mode,
            "required_capabilities": required_capabilities,
            "reasoning": self._generate_analysis_reasoning(complexity, optimal_mode, required_capabilities)
        }
        
    def _determine_complexity(self, user_message: str) -> RequestComplexity:
        """Determine request complexity based on content analysis"""
        
        message_lower = user_message.lower()
        
        # Complex indicators
        complex_indicators = [
            "plan", "design", "architecture", "workflow", "multiple",
            "integrate", "coordinate", "orchestrate", "manage", "analyze patterns"
        ]
        
        # Adaptive indicators (ML/prediction needed)
        adaptive_indicators = [
            "predict", "suggest", "recommend", "optimize", "learn",
            "anticipate", "intelligent", "smart", "adaptive", "continue from"
        ]
        
        # Simple indicators
        simple_indicators = [
            "create", "add", "modify", "update", "delete", "show", "get", "set"
        ]
        
        # Count indicators
        complex_count = sum(1 for indicator in complex_indicators if indicator in message_lower)
        adaptive_count = sum(1 for indicator in adaptive_indicators if indicator in message_lower)
        simple_count = sum(1 for indicator in simple_indicators if indicator in message_lower)
        
        # Determine complexity
        if adaptive_count > 0:
            return RequestComplexity.ADAPTIVE
        elif complex_count > 1 or (complex_count > 0 and len(message_lower.split()) > 10):
            return RequestComplexity.COMPLEX
        elif complex_count > 0 or simple_count > 1:
            return RequestComplexity.MODERATE
        else:
            return RequestComplexity.SIMPLE
            
    def _determine_optimal_mode(self, complexity: RequestComplexity, context: Dict[str, Any]) -> CortexMode:
        """Determine optimal CORTEX mode based on complexity and context"""
        
        # Check for explicit mode preference
        if "force_20" in context:
            return CortexMode.CORTEX_20_COMPATIBILITY
        elif "force_30" in context:
            return CortexMode.CORTEX_30_FULL
            
        # Auto-select based on complexity
        if complexity == RequestComplexity.ADAPTIVE:
            return CortexMode.CORTEX_30_FULL
        elif complexity == RequestComplexity.COMPLEX:
            return CortexMode.CORTEX_30_HYBRID
        elif complexity == RequestComplexity.MODERATE:
            return CortexMode.CORTEX_30_HYBRID
        else:
            return CortexMode.CORTEX_20_COMPATIBILITY
            
    def _identify_required_capabilities(self, user_message: str) -> List[str]:
        """Identify what capabilities are needed for this request"""
        
        capabilities = []
        message_lower = user_message.lower()
        
        if any(word in message_lower for word in ["remember", "recall", "previous", "continue", "context"]):
            capabilities.append("dual_channel_memory")
            
        if any(word in message_lower for word in ["coordinate", "multiple", "together", "workflow"]):
            capabilities.append("enhanced_agents")
            
        if any(word in message_lower for word in ["predict", "suggest", "intelligent", "smart", "optimize"]):
            capabilities.append("smart_context_intelligence")
            
        if any(word in message_lower for word in ["plan", "design", "architect", "strategy"]):
            capabilities.append("strategic_planning")
            
        return capabilities
        
    def _generate_analysis_reasoning(self, complexity: RequestComplexity, mode: CortexMode, 
                                   capabilities: List[str]) -> str:
        """Generate human-readable reasoning for the analysis"""
        
        return (f"Complexity: {complexity.value} - Mode: {mode.value} - "
                f"Capabilities: {', '.join(capabilities) if capabilities else 'none'}")


class CortexUnifiedInterface:
    """Main unified interface for CORTEX 3.0"""
    
    def __init__(self, cortex_brain_path: str, config: Dict[str, Any] = None):
        self.cortex_brain_path = cortex_brain_path
        self.config = config or {}
        
        # Initialize analyzers
        self.request_analyzer = RequestAnalyzer()
        
        # Initialize 3.0 systems
        self.dual_channel_memory = DualChannelMemory(cortex_brain_path)
        self.enhanced_agents = EnhancedAgentSystem()
        self.smart_context = SmartContextIntelligence(cortex_brain_path)
        
        # Initialize 2.0 systems for compatibility
        self.universal_operations = UniversalOperationsSystem(cortex_brain_path)
        self.intent_router = IntentRouter()
        
        # Active sessions
        self.active_sessions = {}  # session_id -> session_data
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("CORTEX 3.0 Unified Interface initialized")
        
    async def process_request(self, user_message: str, context: Dict[str, Any] = None,
                            session_id: Optional[str] = None) -> CortexResponse:
        """Process a request through the unified CORTEX 3.0 interface"""
        
        start_time = datetime.now()
        context = context or {}
        
        # Create unified request
        request = CortexRequest(
            request_id=f"req_{int(start_time.timestamp())}",
            user_message=user_message,
            context=context,
            session_id=session_id
        )
        
        try:
            # Analyze request to determine processing strategy
            analysis = self.request_analyzer.analyze_request(request)
            request.complexity = analysis["complexity"]
            request.preferred_mode = analysis["optimal_mode"]
            
            self.logger.info(f"Processing request {request.request_id}: {analysis['reasoning']}")
            
            # Route request based on analysis
            if request.preferred_mode == CortexMode.CORTEX_20_COMPATIBILITY:
                response_data = await self._process_with_20_compatibility(request)
            elif request.preferred_mode == CortexMode.CORTEX_30_FULL:
                response_data = await self._process_with_30_full(request)
            else:  # CORTEX_30_HYBRID
                response_data = await self._process_with_30_hybrid(request)
                
            # Create unified response
            duration = (datetime.now() - start_time).total_seconds()
            
            response = CortexResponse(
                request_id=request.request_id,
                success=response_data.get("success", True),
                response_message=response_data.get("message", "Request processed successfully"),
                execution_details=response_data.get("details", {}),
                mode_used=request.preferred_mode,
                complexity_detected=request.complexity,
                agents_involved=response_data.get("agents_involved", []),
                duration_seconds=duration,
                context_used=response_data.get("context_used", {}),
                recommendations=response_data.get("recommendations", []),
                session_id=session_id
            )
            
            # Update session if applicable
            if session_id:
                await self._update_session_context(session_id, request, response)
                
            return response
            
        except Exception as e:
            self.logger.error(f"Request processing failed: {e}")
            
            duration = (datetime.now() - start_time).total_seconds()
            
            return CortexResponse(
                request_id=request.request_id,
                success=False,
                response_message=f"Processing failed: {str(e)}",
                execution_details={"error": str(e)},
                mode_used=CortexMode.CORTEX_20_COMPATIBILITY,  # Fallback
                complexity_detected=RequestComplexity.SIMPLE,
                agents_involved=[],
                duration_seconds=duration,
                context_used={},
                recommendations=["Check system logs for details"],
                session_id=session_id
            )
            
    async def _process_with_20_compatibility(self, request: CortexRequest) -> Dict[str, Any]:
        """Process request using CORTEX 2.0 compatibility mode"""
        
        self.logger.debug(f"Processing with 2.0 compatibility: {request.request_id}")
        
        # Route through existing 2.0 intent router
        intent_result = self.intent_router.route_request(request.user_message)
        
        # Execute through universal operations system
        operation_result = self.universal_operations.execute_operation(
            operation=intent_result.get("operation", "help"),
            params={"request": request.user_message, "context": request.context}
        )
        
        return {
            "success": operation_result.get("success", True),
            "message": operation_result.get("message", "Processed with CORTEX 2.0 compatibility"),
            "details": operation_result,
            "agents_involved": [intent_result.get("agent", "universal_operations")],
            "context_used": {"mode": "2.0_compatibility"},
            "recommendations": ["Consider using CORTEX 3.0 features for enhanced capabilities"]
        }
        
    async def _process_with_30_full(self, request: CortexRequest) -> Dict[str, Any]:
        """Process request using full CORTEX 3.0 capabilities"""
        
        self.logger.debug(f"Processing with 3.0 full capabilities: {request.request_id}")
        
        # Start intelligent session if not exists
        if not request.session_id:
            request.session_id = await self.smart_context.start_intelligent_session(request.user_message)
            
        # Get intelligent context
        context = await self.smart_context.get_intelligent_context(
            request.session_id, request.user_message
        )
        
        # Create unified narrative through dual-channel memory
        narrative = await self.dual_channel_memory.create_unified_narrative(
            conversational_context={"request": request.user_message, "session": request.session_id},
            traditional_context=context["assembled_context"],
            fusion_strategy="intelligent"
        )
        
        # Execute enhanced workflow
        workflow_result = await self.enhanced_agents.execute_enhanced_workflow(request.user_message)
        
        return {
            "success": workflow_result.get("success", True),
            "message": f"Processed with CORTEX 3.0: {narrative.get('summary', 'Request completed')}",
            "details": {
                "narrative": narrative,
                "workflow": workflow_result,
                "context": context
            },
            "agents_involved": workflow_result.get("agents_involved", []),
            "context_used": context,
            "recommendations": context.get("recommendations", [])
        }
        
    async def _process_with_30_hybrid(self, request: CortexRequest) -> Dict[str, Any]:
        """Process request using hybrid 2.0/3.0 approach"""
        
        self.logger.debug(f"Processing with 3.0 hybrid mode: {request.request_id}")
        
        # Start with 2.0 intent routing for stability
        intent_result = self.intent_router.route_request(request.user_message)
        
        # Enhanced with 3.0 context intelligence if beneficial
        enhanced_context = {}
        if request.complexity in [RequestComplexity.MODERATE, RequestComplexity.COMPLEX]:
            if not request.session_id:
                request.session_id = await self.smart_context.start_intelligent_session(request.user_message)
                
            enhanced_context = await self.smart_context.get_intelligent_context(
                request.session_id, request.user_message
            )
        
        # Execute with universal operations but enhanced context
        operation_result = self.universal_operations.execute_operation(
            operation=intent_result.get("operation", "help"),
            params={
                "request": request.user_message, 
                "context": request.context,
                "enhanced_context": enhanced_context
            }
        )
        
        return {
            "success": operation_result.get("success", True),
            "message": f"Processed with CORTEX 3.0 hybrid: {operation_result.get('message', 'Request completed')}",
            "details": {
                "operation_result": operation_result,
                "enhanced_context": enhanced_context
            },
            "agents_involved": [intent_result.get("agent", "universal_operations")],
            "context_used": enhanced_context,
            "recommendations": enhanced_context.get("recommendations", [])
        }
        
    async def _update_session_context(self, session_id: str, request: CortexRequest, 
                                    response: CortexResponse):
        """Update session context with request/response data"""
        
        if session_id not in self.active_sessions:
            self.active_sessions[session_id] = {
                "started": datetime.now(),
                "requests": [],
                "context": {}
            }
            
        session = self.active_sessions[session_id]
        session["requests"].append({
            "request": request,
            "response": response,
            "timestamp": datetime.now()
        })
        
        # Update session in smart context manager
        self.smart_context.session_manager.update_session_context(session_id, {
            "last_request": request.user_message,
            "mode_used": response.mode_used.value,
            "complexity": response.complexity_detected.value
        })
        
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status for all CORTEX components"""
        
        return {
            "cortex_version": "3.0",
            "unified_interface": {
                "status": "operational",
                "active_sessions": len(self.active_sessions),
                "supported_modes": [mode.value for mode in CortexMode]
            },
            "dual_channel_memory": {
                "status": "operational",
                "channels": ["conversational", "traditional"],
                "fusion_strategies": ["simple", "weighted", "intelligent"]
            },
            "enhanced_agents": {
                "status": "operational", 
                "primary_agents": len(self.enhanced_agents.orchestrator.primary_agents),
                "sub_agents": len(self.enhanced_agents.orchestrator.sub_agents)
            },
            "smart_context_intelligence": {
                "status": "operational",
                "memory_usage_mb": self.smart_context.memory_manager.current_memory_usage,
                "max_memory_mb": self.smart_context.memory_manager.max_memory_mb
            },
            "compatibility": {
                "cortex_20": "full_compatibility",
                "universal_operations": "integrated"
            }
        }
        
    async def shutdown(self):
        """Gracefully shutdown all CORTEX 3.0 systems"""
        
        self.logger.info("Shutting down CORTEX 3.0 Unified Interface")
        
        # Close active sessions
        for session_id in list(self.active_sessions.keys()):
            self.smart_context.session_manager.end_session(session_id)
            
        # Clean up resources
        await self.dual_channel_memory.cleanup()
        
        self.logger.info("CORTEX 3.0 shutdown complete")