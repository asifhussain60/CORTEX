# Quick Reference

## tdd_orchestrator_v4

### `TDDPhase`
 (inherits: Enum)




### `ValidationResult`




### `PhaseResult`




### `TechnologyProfile`




### `TDDPhaseStrategy`
 (inherits: ABC)


- `validate_dor(self, context: Dict[str, Any]) -> ValidationResult`
- `execute(self, context: Dict[str, Any]) -> PhaseResult`
- `validate_dod(self, context: Dict[str, Any]) -> ValidationResult`
- `rollback(self, context: Dict[str, Any]) -> bool`


### `TechnologyDiscoveryEngine`


- `discover_project_tech_stack(self, project_path: Path) -> TechnologyProfile`
- `learn_from_patterns(self, project_path: Path, pattern_type: str, pattern_data: Dict[str, Any]) -> int`
- `get_best_practices(self, language: str, framework: Optional[str]) -> Dict[str, Any]`


### `CleanCodeEnforcer`


- `analyze_code_quality(self, file_path: Path, code_content: str) -> Dict[str, Any]`


### `TDDOrchestratorV4`


- `register_strategy(self, phase: TDDPhase, strategy: TDDPhaseStrategy)`
- `execute_tdd_cycle(self, feature_name: str, acceptance_criteria: List[str], project_path: Path, context: Optional[Dict[str, Any]]) -> Dict[str, Any]`
- `get_orchestrator_metrics(self) -> Dict[str, Any]`




## __init__



## red_phase_strategy

### `REDPhaseStrategy`
 (inherits: TDDPhaseStrategy)


- `validate_dor(self, context: Dict[str, Any]) -> ValidationResult`
- `execute(self, context: Dict[str, Any]) -> PhaseResult`
- `validate_dod(self, context: Dict[str, Any]) -> ValidationResult`
- `rollback(self, context: Dict[str, Any]) -> bool`




## __init__



## refactor_phase_strategy

### `REFACTORPhaseStrategy`
 (inherits: TDDPhaseStrategy)


- `validate_dor(self, context: Dict[str, Any]) -> ValidationResult`
- `execute(self, context: Dict[str, Any]) -> PhaseResult`
- `validate_dod(self, context: Dict[str, Any]) -> ValidationResult`
- `rollback(self, context: Dict[str, Any]) -> bool`




## green_phase_strategy

### `GREENPhaseStrategy`
 (inherits: TDDPhaseStrategy)


- `validate_dor(self, context: Dict[str, Any]) -> ValidationResult`
- `execute(self, context: Dict[str, Any]) -> PhaseResult`
- `validate_dod(self, context: Dict[str, Any]) -> ValidationResult`
- `rollback(self, context: Dict[str, Any]) -> bool`



