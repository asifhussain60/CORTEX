# clarification_orchestrator

Clarification Orchestrator

Manages the scope clarification workflow, including:
- Conditional activation based on validation results
- User interaction and prompt generation
- Response parsing and entity re-extraction
- Iterative clarification (maximum 2 rounds)
- Integration with ScopeInferenceEngine and ScopeValidator

This component ensures we only ask clarification questions when necessary
and stop after getting sufficient scope information.


## Table of Contents

### Classes
- [ClarificationOrchestrator](#clarificationorchestrator)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** re, src, typing


## Classes

### ClarificationOrchestrator

```python
class ClarificationOrchestrator
```

Orchestrates the scope clarification workflow


**Methods:**

  #### `should_clarify`

  ```python
  should_clarify(self, validator_result: Dict[str, Any]) -> bool
  ```

  Determine if clarification is needed based on validation results

Args:
    validator_result: Dictionary with validation results
        - confidence: float (0.0-1.0)
        - is_valid: bool
        - missing_elements: list of missing element types

Returns:
    bool: True if clarification is needed, False otherwise

  **Parameters:**

  - `self`
  - `validator_result` (Dict[str, Any]): Dictionary with validation results


  **Returns:** bool
    bool: True if clarification is needed, False otherwise


  #### `generate_clarification_prompt`

  ```python
  generate_clarification_prompt(self, validator_result: Dict[str, Any]) -> str
  ```

  Generate a user-friendly prompt asking for missing scope information

Args:
    validator_result: Dictionary with validation results including
                    clarification_questions list

Returns:
    str: Formatted prompt for user

  **Parameters:**

  - `self`
  - `validator_result` (Dict[str, Any]): Dictionary with validation results including clarification_questions list


  **Returns:** str
    str: Formatted prompt for user


  #### `parse_user_response`

  ```python
  parse_user_response(self, user_response: str) -> Dict[str, Any]
  ```

  Parse user's response to extract scope entities

Args:
    user_response: The user's text response to clarification questions

Returns:
    Dictionary with:
        - entities: Dict with extracted tables, files, services, dependencies
        - confidence: float (0.0-1.0)
        - is_vague: bool indicating if response is still vague

  **Parameters:**

  - `self`
  - `user_response` (str): The user's text response to clarification questions


  **Returns:** Dict[str, Any]
    Dictionary with: - entities: Dict with extracted tables, files, services, dependencies - confidence: float (0.0-1.0) - is_vague: bool indicating if response is still vague


  #### `increment_round`

  ```python
  increment_round(self)
  ```

  Increment the clarification round counter

  **Parameters:**

  - `self`


  #### `get_current_round`

  ```python
  get_current_round(self) -> int
  ```

  Get the current clarification round number

  **Parameters:**

  - `self`


  **Returns:** int


  #### `can_continue_clarification`

  ```python
  can_continue_clarification(self) -> bool
  ```

  Check if we can continue asking for clarification

Returns:
    bool: True if we haven't reached max rounds, False otherwise

  **Parameters:**

  - `self`


  **Returns:** bool
    bool: True if we haven't reached max rounds, False otherwise


  #### `should_stop_clarification`

  ```python
  should_stop_clarification(self, validator_result: Dict[str, Any]) -> bool
  ```

  Determine if we should stop the clarification process

Args:
    validator_result: Dictionary with validation results

Returns:
    bool: True if we should stop, False if we should continue

  **Parameters:**

  - `self`
  - `validator_result` (Dict[str, Any]): Dictionary with validation results


  **Returns:** bool
    bool: True if we should stop, False if we should continue


  #### `reset`

  ```python
  reset(self)
  ```

  Reset the orchestrator state for a new clarification workflow

  **Parameters:**

  - `self`


  #### `run_clarification_workflow`

  ```python
  run_clarification_workflow(self, initial_requirements: str, initial_validation: Dict[str, Any], max_iterations: Optional[int]) -> Dict[str, Any]
  ```

  Run the complete clarification workflow

Args:
    initial_requirements: The original requirements text
    initial_validation: Initial validation result from ScopeValidator
    max_iterations: Maximum iterations (defaults to self.max_rounds)

Returns:
    Dictionary with:
        - final_scope: The final extracted scope
        - final_confidence: Final confidence score
        - rounds_completed: Number of clarification rounds
        - prompts: List of prompts generated
        - success: bool indicating if threshold was met

  **Parameters:**

  - `self`
  - `initial_requirements` (str): The original requirements text
  - `initial_validation` (Dict[str, Any]): Initial validation result from ScopeValidator
  - `max_iterations` (Optional[int]) = `None`: Maximum iterations (defaults to self.max_rounds)


  **Returns:** Dict[str, Any]
    Dictionary with: - final_scope: The final extracted scope - final_confidence: Final confidence score - rounds_completed: Number of clarification rounds - prompts: List of prompts generated - success: bool indicating if threshold was met



---
