"""
Response Engine Adapter - Non-invasive integration with OrchestratorBaseProtocol.

Provides backward-compatible injection of UnifiedResponseEngine into orchestrator
response flow without modifying the base protocol.

Architecture:
- Mixin pattern: Add response composition without changing inheritance
- Post-domain-logic hook: Intercepts result before return
- Feature flag system: Gradual rollout per orchestrator
- Fallback mechanism: Graceful degradation if engine unavailable

Module: cortex.orchestrators.response.response_engine_adapter
Author: Asif Hussain
Created: 2026-02-12
Version: 1.0.0
Authority: ENH-082 Wave 2 Stage 3
AC-ID: AC-ENH082-W2-S3-001
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional

from cortex.core.result import Ok, Result
from cortex.models.canonical_enums import IntentType
from cortex.orchestrators.response.unified_response_engine import (
    ResponseEngineConfig,
    UnifiedResponseEngine,
)


logger = logging.getLogger(__name__)


# ============================================================================
# RESPONSE ENGINE CONFIGURATION PER ORCHESTRATOR
# ============================================================================


@dataclass
class OrchestratorResponseConfig:
    """Configuration for response engine integration per orchestrator.
    
    Attributes:
        enable_response_engine: Feature flag for this orchestrator
        intent_type: Default intent type for role detection
        orchestrator_name: Name for template selection
        fallback_to_default: Use default response if engine fails
        log_composition: Enable debug logging for composition
    """
    
    enable_response_engine: bool = False  # Disabled by default (safety)
    intent_type: IntentType = IntentType.UNKNOWN
    orchestrator_name: str = ""
    fallback_to_default: bool = True
    log_composition: bool = False


# ============================================================================
# RESPONSE ENGINE MIXIN
# ============================================================================


class ResponseEngineMixin:
    """Mixin to add UnifiedResponseEngine support to orchestrators.
    
    Add this mixin to orchestrators to enable template-based response composition:
    
    Example:
        class TDDOrchestrator(OrchestratorBaseProtocol, ResponseEngineMixin):
            def __init__(self):
                super().__init__()
                self._init_response_engine(
                    intent_type=IntentType.IMPLEMENT,
                    orchestrator_name="TDDOrchestrator",
                    enable=True  # Enable for this orchestrator
                )
    
    This provides:
    - Automatic response composition via UnifiedResponseEngine
    - Feature flag control per orchestrator
    - Graceful fallback if engine unavailable
    - Non-invasive: Does NOT modify base protocol
    """
    
    def _init_response_engine(
        self,
        intent_type: IntentType = IntentType.UNKNOWN,
        orchestrator_name: str = "",
        enable: bool = False
    ) -> None:
        """Initialize response engine for this orchestrator.
        
        Args:
            intent_type: Intent type for role detection
            orchestrator_name: Name for template selection
            enable: Enable response engine for this orchestrator
        """
        # Store configuration
        self._response_config = OrchestratorResponseConfig(
            enable_response_engine=enable,
            intent_type=intent_type,
            orchestrator_name=orchestrator_name or self.__class__.__name__,
        )
        
        # Initialize engine (global instance shared across orchestrators)
        global_config = ResponseEngineConfig(
            feature_flag_enabled=enable,
            fallback_to_orchestrator=True,
        )
        self._response_engine = UnifiedResponseEngine(global_config)
        
        if enable:
            logger.info(
                f"{orchestrator_name}: Response engine ENABLED "
                f"(intent={intent_type.value})"
            )
        else:
            logger.debug(
                f"{orchestrator_name}: Response engine disabled (fallback mode)"
            )
    
    def _compose_response(
        self,
        domain_result,  # Remove type hint to avoid Result[Any] issue
        context: Dict[str, Any]
    ):  # Remove return type hint
        """Compose response using UnifiedResponseEngine.
        
        This is the injection point for response composition.
        Call this AFTER domain logic execution to transform
        raw domain output into template-based response.
        
        Args:
            domain_result: Result from domain logic execution
            context: Request context (for variable binding)
            
        Returns:
            Result with composed response or original result
        """
        # If response engine disabled, return original result
        if not self._response_config.enable_response_engine:
            return domain_result
        
        # If domain failed, don't compose (return error as-is)
        if hasattr(domain_result, 'is_err') and domain_result.is_err():
            return domain_result
        
        try:
            # Extract domain output
            domain_output = getattr(domain_result, 'value', domain_result)
            
            # Add domain output to context for variable binding
            if isinstance(domain_output, dict):
                composition_context = {**context, **domain_output}
            else:
                composition_context = context
            
            # Compose response via UnifiedResponseEngine
            composed = self._response_engine.compose(
                intent=self._response_config.intent_type,
                orchestrator_name=self._response_config.orchestrator_name,
                context=composition_context
            )
            
            if self._response_config.log_composition:
                logger.debug(
                    f"{self._response_config.orchestrator_name}: "
                    f"Response composed via UnifiedResponseEngine"
                )
            
            # Wrap composed response in Result
            return Ok({
                "response": composed,
                "domain_output": domain_output,
                "composed_via": "UnifiedResponseEngine",
            })
            
        except Exception as e:
            # Fallback: Return original result on error
            logger.warning(
                f"{self._response_config.orchestrator_name}: "
                f"Response composition failed: {e}, using fallback"
            )
            return domain_result


# ============================================================================
# ORCHESTRATOR EXTENSION METHODS
# ============================================================================


def enable_response_engine_for_orchestrator(
    orchestrator_class: type,
    intent_type: IntentType,
    orchestrator_name: Optional[str] = None
) -> type:
    """Class decorator to enable response engine for an orchestrator.
    
    Adds ResponseEngineMixin to orchestrator and auto-configures.
    
    Usage:
        @enable_response_engine_for_orchestrator(
            intent_type=IntentType.IMPLEMENT,
            orchestrator_name="TDDOrchestrator"
        )
        class TDDOrchestrator(OrchestratorBaseProtocol):
            pass
    
    Args:
        orchestrator_class: Orchestrator class to enhance
        intent_type: Intent type for role detection
        orchestrator_name: Optional orchestrator name
        
    Returns:
        Enhanced orchestrator class
    """
    # Create new class with mixin instead of modifying __bases__
    # (Python doesn't allow runtime __bases__ modification)
    
    class EnhancedOrchestrator(ResponseEngineMixin, orchestrator_class):  # type: ignore
        """Enhanced orchestrator with ResponseEngineMixin."""
        
        def __init__(self, *args, **kwargs):
            """Initialize with response engine configuration."""
            # Call original init
            orchestrator_class.__init__(self, *args, **kwargs)
            
            # Initialize response engine
            self._init_response_engine(
                intent_type=intent_type,
                orchestrator_name=orchestrator_name or orchestrator_class.__name__,
                enable=True  # Enable for decorated orchestrators
            )
    
    # Preserve metadata
    EnhancedOrchestrator.__name__ = orchestrator_class.__name__
    EnhancedOrchestrator.__qualname__ = orchestrator_class.__qualname__
    EnhancedOrchestrator.__module__ = orchestrator_class.__module__
    
    return EnhancedOrchestrator


# ============================================================================
# MIGRATION HELPER
# ============================================================================


def migrate_orchestrator_to_response_engine(
    orchestrator_instance: Any,
    intent_type: IntentType,
    enable: bool = False
) -> None:
    """Runtime migration helper for existing orchestrator instances.
    
    Adds response engine support to an existing orchestrator instance
    without modifying the class definition.
    
    Args:
        orchestrator_instance: Existing orchestrator instance
        intent_type: Intent type for role detection
        enable: Enable response engine
    """
    # Add mixin methods to instance
    orchestrator_instance._init_response_engine = (
        ResponseEngineMixin._init_response_engine.__get__(
            orchestrator_instance,
            orchestrator_instance.__class__
        )
    )
    orchestrator_instance._compose_response = (
        ResponseEngineMixin._compose_response.__get__(
            orchestrator_instance,
            orchestrator_instance.__class__
        )
    )
    
    # Initialize
    orchestrator_instance._init_response_engine(
        intent_type=intent_type,
        orchestrator_name=orchestrator_instance.__class__.__name__,
        enable=enable
    )


# ============================================================================
# EXPORTS
# ============================================================================


__all__ = [
    "ResponseEngineMixin",
    "OrchestratorResponseConfig",
    "enable_response_engine_for_orchestrator",
    "migrate_orchestrator_to_response_engine",
]
