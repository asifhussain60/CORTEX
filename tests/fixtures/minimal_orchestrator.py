"""
Minimal Orchestrator Fixture - AC-FR-008-01

A minimal but complete orchestrator implementation for testing the full
orchestrator plugin ecosystem, including:
- Orchestrator registration
- Tier dependency declaration
- MCP tool exposure
- Audit trail capture
- Governance context access

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

from src.core.orchestrator_base import OrchestratorBase, OrchestrationContext
from src.core.decorators.orchestrator import orchestrator
from src.core.result import Result, Ok, Err


class MinimalOrchestratorStatus(str, Enum):
    """Status of minimal orchestrator execution."""
    STARTING = "STARTING"
    EXECUTING = "EXECUTING"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"


@dataclass
class MinimalOrchestratorTestContext:
    """Test context for minimal orchestrator (separate from OrchestrationContext)."""
    
    input_value: str
    tier_access_requested: List[int] = field(default_factory=list)
    audit_trail: List[Dict[str, Any]] = field(default_factory=list)
    governance_context: Dict[int, Any] = field(default_factory=dict)
    execution_status: MinimalOrchestratorStatus = MinimalOrchestratorStatus.STARTING


@orchestrator(
    orchestrator_id="minimal_orchestrator_001",
    tier_dependencies={0, 1, 2},
    required_rules=["test-naming", "test-coverage"],
    description="Minimal orchestrator for E2E testing"
)
class MinimalOrchestrator(OrchestratorBase):
    """
    Minimal but complete orchestrator for testing the plugin ecosystem.
    
    Demonstrates:
    - Registration via @orchestrator decorator
    - Tier dependency declaration
    - Governance context access
    - Audit trail capture
    - MCP tool exposure
    """
    
    # Class-level test context storage for tests
    _test_context: Optional[MinimalOrchestratorTestContext] = None
    
    def __init__(self, orchestration_context: OrchestrationContext,
                 test_context: Optional[MinimalOrchestratorTestContext] = None):
        """Initialize minimal orchestrator.
        
        Args:
            orchestration_context: OrchestrationContext from framework
            test_context: Optional test context for unit tests
        """
        super().__init__(orchestration_context)
        # Store test context at class level so decorator-wrapped init can access it
        MinimalOrchestrator._test_context = test_context or MinimalOrchestratorTestContext(input_value="test")
        self.execution_log: List[str] = []
    
    @property
    def test_context(self) -> MinimalOrchestratorTestContext:
        """Get test context."""
        if MinimalOrchestrator._test_context is None:
            MinimalOrchestrator._test_context = MinimalOrchestratorTestContext(input_value="test")
        return MinimalOrchestrator._test_context
    
    async def execute(self, input_data: Dict[str, Any]):
        """
        Execute the minimal orchestrator workflow.
        
        Args:
            input_data: Input containing:
                - 'input_value': String value to process
                - 'request_tiers': List of tier numbers to access (0-3)
        
        Returns:
            Result containing execution summary or error
        """
        try:
            self.log_entry("EXECUTE_START")
            
            # Extract input
            input_value = input_data.get("input_value", "test")
            request_tiers = input_data.get("request_tiers", [0, 1, 2])
            
            self.execution_log.append(f"Processing input: {input_value}")
            
            # Access governance context
            governance_data = {}
            for tier in request_tiers:
                try:
                    tier_context = await self.get_tier_access(tier)
                    governance_data[tier] = tier_context
                    self.execution_log.append(f"Accessed tier {tier}: {type(tier_context).__name__}")
                except Exception as e:
                    self.execution_log.append(f"Failed to access tier {tier}: {str(e)}")
            
            # Perform minimal transformation
            output_value = f"processed_{input_value}"
            
            # Validate context (hooks)
            validation_result = await self.validate_context()
            if not validation_result.is_ok():
                return Err(f"Context validation failed: {validation_result.error()}")
            
            # Call start hook
            await self.on_start()
            
            # Execute business logic
            result = {
                'status': 'SUCCESS',
                'output_value': output_value,
                'tiers_accessed': list(governance_data.keys()),
                'execution_log': self.execution_log,
                'governance_context_keys': list(governance_data.keys()),
            }
            
            # Call complete hook
            await self.on_complete(result)
            
            self.log_entry("EXECUTE_COMPLETE", result=result)
            
            return Ok(result)
        
        except Exception as e:
            error_msg = f"Execution failed: {str(e)}"
            self.execution_log.append(error_msg)
            self.log_entry("EXECUTE_ERROR", error=error_msg)
            return Err(error_msg)
    
    async def validate_context(self):
        """
        Validate execution context.
        
        Returns:
            Result indicating if context is valid
        """
        try:
            # Check that required tiers are accessible
            accessible_tiers = self.get_accessible_tiers()
            
            if not accessible_tiers:
                return Err("No tiers accessible")
            
            self.log_entry("CONTEXT_VALIDATION", tiers=accessible_tiers)
            return Ok(True)
        
        except Exception as e:
            return Err(f"Context validation error: {str(e)}")
    
    async def on_start(self) -> None:
        """Called before execute()."""
        self.execution_log.append("on_start hook called")
        self.log_entry("ON_START")
    
    async def on_complete(self, result: Dict[str, Any]) -> None:
        """Called after execute()."""
        self.execution_log.append(f"on_complete hook called with result keys: {list(result.keys())}")
        self.log_entry("ON_COMPLETE")
    
    def get_accessible_tiers(self) -> List[int]:
        """Get list of tiers accessible to this orchestrator."""
        # In real implementation, this would be set by @orchestrator decorator
        return [0, 1, 2]  # Return as list for compatibility
    
    async def get_tier_access(self, tier: int) -> Any:
        """
        Get access to specific tier.
        
        Args:
            tier: Tier number (0-3)
        
        Returns:
            Tier data/context
        """
        if tier not in self.get_accessible_tiers():
            raise ValueError(f"No access to tier {tier}")
        
        # Return mock tier data
        return {
            'tier': tier,
            'accessible': True,
            'rules': self._get_mock_tier_rules(tier),
        }
    
    def _get_mock_tier_rules(self, tier: int) -> List[str]:
        """Get mock rules for a tier."""
        tier_rules = {
            0: ["test-naming", "test-coverage", "assertion-patterns"],
            1: ["ac-completeness", "dependency-checking"],
            2: ["response-format", "template-inheritance"],
            3: ["knowledge-base", "pattern-library"],
        }
        return tier_rules.get(tier, [])
    
    def log_entry(self, event: str, **kwargs) -> None:
        """Log an event."""
        entry = {
            'event': event,
            'timestamp': self._get_timestamp(),
            **kwargs,
        }
        self.test_context.audit_trail.append(entry)
    
    @staticmethod
    def _get_timestamp() -> str:
        """Get current timestamp."""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()
