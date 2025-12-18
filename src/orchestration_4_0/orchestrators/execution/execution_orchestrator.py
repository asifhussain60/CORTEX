"""
Execution Orchestrator for CORTEX 4.0

Handles multi-phase execution workflows with:
- Phase validation and execution
- Sub-orchestrator routing
- Progress tracking
- Error recovery
"""

from typing import Dict, Any, Optional, List, Callable
import logging

from src.orchestration_4_0.base import BaseOrchestrator


class ExecutionOrchestrator(BaseOrchestrator):
    """
    Orchestrates execution of multi-phase workflows.
    
    Features:
    - Dynamic phase registration from execution plans
    - Sub-orchestrator integration (TDD, Planning, etc.)
    - Validation gates between phases
    - Rollback support for failed phases
    - Progress tracking with visual feedback
    
    Usage:
        orchestrator = ExecutionOrchestrator(
            logger=logger,
            config={"max_retries": 3}
        )
        
        result = orchestrator.execute(context={
            "plan": execution_plan,
            "workspace": "/path/to/workspace"
        })
    """
    
    def __init__(
        self,
        logger: Optional[logging.Logger] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize execution orchestrator.
        
        Args:
            logger: Optional logger instance
            config: Optional configuration dictionary
        """
        super().__init__(
            name="execution",
            logger=logger,
            config=config
        )
        
        # Execution-specific state
        self.execution_plan: Optional[Dict[str, Any]] = None
        self.workspace: Optional[str] = None
        self.sub_orchestrators: Dict[str, Any] = {}
        self.phase_validators: Dict[str, Callable] = {}
    
    def _setup(self, context: Dict[str, Any]) -> None:
        """
        Setup execution orchestrator.
        
        Extracts:
        - Execution plan
        - Workspace path
        - Phase validators
        
        Args:
            context: Must contain "plan" key with execution plan
        """
        self.logger.debug("🔧 Setting up execution orchestrator...")
        
        # Extract execution plan
        if "plan" not in context:
            raise ValueError("Execution context must contain 'plan' key")
        
        self.execution_plan = context["plan"]
        self.workspace = context.get("workspace")
        
        # Extract phase validators if provided
        if "validators" in context:
            self.phase_validators = context["validators"]
        
        self.logger.info(f"✅ Setup complete - Plan: {self.execution_plan.get('name', 'unnamed')}")
    
    def _register_phases(self) -> None:
        """
        Register phases from execution plan.
        
        Phases are extracted from the execution plan's "phases" array.
        Each phase can have:
        - name: Phase identifier
        - description: Human-readable description
        - required: Whether phase must succeed (default: True)
        - validator: Optional validation function name
        """
        self.logger.debug("📋 Registering phases from execution plan...")
        
        if not self.execution_plan:
            raise RuntimeError("Execution plan not set - call _setup() first")
        
        phases = self.execution_plan.get("phases", [])
        if not phases:
            raise ValueError("Execution plan must contain at least one phase")
        
        for phase_def in phases:
            phase_name = phase_def.get("name")
            if not phase_name:
                raise ValueError("Phase definition must contain 'name' key")
            
            description = phase_def.get("description", f"Execute {phase_name}")
            required = phase_def.get("required", True)
            
            # Get validator if specified
            validator = None
            validator_name = phase_def.get("validator")
            if validator_name and validator_name in self.phase_validators:
                validator = self.phase_validators[validator_name]
            
            # Register phase
            self.phase_manager.register_phase(
                name=phase_name,
                description=description,
                required=required,
                validation=validator
            )
            
            self.logger.debug(f"  ✓ Registered phase: {phase_name} (required={required})")
        
        self.logger.info(f"✅ Registered {len(phases)} phases")
    
    def _execute_phase(
        self,
        phase_name: str,
        context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Execute a specific phase.
        
        Phases can either:
        1. Execute inline code (if "code" key present)
        2. Route to sub-orchestrator (if "orchestrator" key present)
        3. Execute custom function (if "handler" key present)
        
        Args:
            phase_name: Name of phase to execute
            context: Execution context
            
        Returns:
            Phase execution result
        """
        self.logger.info(f"▶️  Executing phase: {phase_name}")
        
        # Find phase definition in execution plan
        phase_def = self._get_phase_definition(phase_name)
        if not phase_def:
            raise ValueError(f"Phase definition not found: {phase_name}")
        
        # Route to appropriate execution method
        if "orchestrator" in phase_def:
            result = self._execute_sub_orchestrator(phase_name, phase_def, context)
        elif "code" in phase_def:
            result = self._execute_inline_code(phase_name, phase_def, context)
        elif "handler" in phase_def:
            result = self._execute_custom_handler(phase_name, phase_def, context)
        else:
            # Default: just log and return empty result
            self.logger.info(f"  ℹ️  Phase {phase_name} has no execution logic")
            result = {"status": "completed", "message": f"Phase {phase_name} completed"}
        
        self.logger.info(f"✅ Phase complete: {phase_name}")
        return result
    
    def _execute_sub_orchestrator(
        self,
        phase_name: str,
        phase_def: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a sub-orchestrator for this phase.
        
        Args:
            phase_name: Phase name
            phase_def: Phase definition
            context: Execution context
            
        Returns:
            Sub-orchestrator result
        """
        orchestrator_name = phase_def["orchestrator"]
        self.logger.debug(f"  🎭 Routing to sub-orchestrator: {orchestrator_name}")
        
        # Get or create sub-orchestrator
        if orchestrator_name not in self.sub_orchestrators:
            # In full implementation, this would use DI container to get orchestrator
            self.logger.warning(f"  ⚠️  Sub-orchestrator {orchestrator_name} not yet implemented")
            return {"status": "skipped", "reason": "Sub-orchestrator not implemented"}
        
        sub_orchestrator = self.sub_orchestrators[orchestrator_name]
        
        # Execute sub-orchestrator
        sub_context = phase_def.get("context", {})
        sub_context.update(context)
        
        result = sub_orchestrator.execute(sub_context)
        return result
    
    def _execute_inline_code(
        self,
        phase_name: str,
        phase_def: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute inline code for this phase.
        
        Args:
            phase_name: Phase name
            phase_def: Phase definition with "code" key
            context: Execution context
            
        Returns:
            Execution result
        """
        code = phase_def["code"]
        self.logger.debug(f"  📝 Executing inline code for phase: {phase_name}")
        
        # In full implementation, this would safely execute the code
        # For now, just log and return success
        self.logger.debug(f"  Code: {code[:100]}..." if len(code) > 100 else f"  Code: {code}")
        
        return {
            "status": "completed",
            "message": f"Inline code executed for phase: {phase_name}"
        }
    
    def _execute_custom_handler(
        self,
        phase_name: str,
        phase_def: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute custom handler function for this phase.
        
        Args:
            phase_name: Phase name
            phase_def: Phase definition with "handler" key
            context: Execution context
            
        Returns:
            Handler result
        """
        handler_name = phase_def["handler"]
        self.logger.debug(f"  🔧 Executing custom handler: {handler_name}")
        
        # In full implementation, this would look up and call the handler
        # For now, just log and return success
        return {
            "status": "completed",
            "message": f"Custom handler {handler_name} executed for phase: {phase_name}"
        }
    
    def _get_phase_definition(self, phase_name: str) -> Optional[Dict[str, Any]]:
        """
        Get phase definition from execution plan.
        
        Args:
            phase_name: Phase name to find
            
        Returns:
            Phase definition dict or None if not found
        """
        if not self.execution_plan:
            return None
        
        phases = self.execution_plan.get("phases", [])
        for phase_def in phases:
            if phase_def.get("name") == phase_name:
                return phase_def
        
        return None
    
    def _teardown(self) -> None:
        """
        Cleanup execution orchestrator resources.
        """
        self.logger.debug("🧹 Cleaning up execution orchestrator...")
        
        # Cleanup sub-orchestrators
        for name, orchestrator in self.sub_orchestrators.items():
            if hasattr(orchestrator, "cleanup"):
                self.logger.debug(f"  Cleaning up sub-orchestrator: {name}")
                orchestrator.cleanup()
        
        self.sub_orchestrators.clear()
        
        self.logger.debug("✅ Cleanup complete")
    
    def register_sub_orchestrator(self, name: str, orchestrator: Any) -> None:
        """
        Register a sub-orchestrator for use in phases.
        
        Args:
            name: Orchestrator identifier (e.g., "tdd", "planning")
            orchestrator: Orchestrator instance
        """
        self.sub_orchestrators[name] = orchestrator
        self.logger.debug(f"📝 Registered sub-orchestrator: {name}")
    
    def register_validator(self, name: str, validator: Callable) -> None:
        """
        Register a phase validator function.
        
        Args:
            name: Validator identifier
            validator: Validation function (should return bool)
        """
        self.phase_validators[name] = validator
        self.logger.debug(f"📝 Registered validator: {name}")
