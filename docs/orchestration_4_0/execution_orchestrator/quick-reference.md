# Quick Reference

## __init__



## execution_orchestrator

### `ExecutionOrchestrator`
 (inherits: BaseOrchestrator)


- `register_sub_orchestrator(self, name: str, orchestrator: Any) -> None`
- `register_validator(self, name: str, validator: Callable) -> None`




## base_orchestrator

### `BaseOrchestrator`
 (inherits: ABC)


- `execute(self, context: Optional[Dict[str, Any]]) -> Dict[str, Any]`
- `get_status(self) -> Dict[str, Any]`




## __init__



## error_handler

### `ErrorSeverity`
 (inherits: Enum)




### `RecoveryStrategy`
 (inherits: Enum)




### `OrchestratorError`




### `ErrorHandler`


- `handle_error(self, phase: str, exception: Exception, severity: ErrorSeverity, recovery_strategy: Optional[RecoveryStrategy], context: Optional[Dict[str, Any]]) -> OrchestratorError`
- `can_retry(self, phase: str) -> bool`
- `record_retry(self, phase: str) -> int`
- `reset_retries(self, phase: str) -> None`
- `get_error_summary(self) -> Dict[str, Any]`
- `has_critical_errors(self) -> bool`
- `clear_errors(self) -> None`




## phase_manager

### `PhaseStatus`
 (inherits: Enum)




### `Phase`




### `PhaseTransition`




### `PhaseManager`


- `register_phase(self, name: str, description: str, required: bool, validation: Optional[Callable[[], bool]], cleanup: Optional[Callable[[], None]]) -> Phase`
- `start_phase(self, phase_name: str) -> None`
- `complete_phase(self, phase_name: str, result: Optional[Dict[str, Any]]) -> None`
- `fail_phase(self, phase_name: str, error: str) -> None`
- `skip_phase(self, phase_name: str, reason: str) -> None`
- `get_progress(self) -> Dict[str, Any]`
- `get_phase_status(self, phase_name: str) -> PhaseStatus`
- `reset(self) -> None`



