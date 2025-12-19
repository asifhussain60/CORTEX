# governance_tokens

CORTEX Governance Token Budget Validator

Validates token budget compliance for governance files to prevent
GitHub Copilot premature summarization.

Token Budgets (Updated 2025-12-03 for mature system):
    - CORTEX.prompt.md: 12,000 tokens (consolidated entry point)
    - brain-protection-rules.yaml: 35,000 tokens (5000+ governance rules)
    - response-templates.yaml: 25,000 tokens (30+ response templates)
    - copilot-instructions.md: 4,000 tokens (auto-discovery file)
    - TOTAL: 76,000 tokens (realistic for mature CORTEX system)

Commands:
    validate    - Check all governance files against token budgets
    analyze     - Identify content extraction candidates
    report      - Generate detailed token usage report
    optimize    - Apply automated token optimization (Phase 1)

Usage:
    # From command line
    python3 -m src.operations.modules.admin.governance_tokens validate
    
    # From Python code
    from src.operations.modules.admin.governance_tokens import validate_token_budgets
    result = validate_token_budgets()

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 2.0 (Realistic budgets for orchestrator migration completion)
Status: PRODUCTION
Created: 2025-12-01 (TOKEN_EFFICIENCY_ENFORCEMENT implementation)
Updated: 2025-12-03 (Budget adjustment for system maturity)


## Table of Contents

### Classes
- [GovernanceFile](#governancefile)
- [TokenValidationReport](#tokenvalidationreport)
- [GovernanceTokenValidator](#governancetokenvalidator)

### Functions
- [safe_print](#safe_print)
- [validate_token_budgets](#validate_token_budgets)
- [main](#main)


## Overview

- **Classes:** 3
- **Functions:** 3
- **Dependencies:** argparse, dataclasses, datetime, logging, pathlib, src, sys, time, typing


## Classes

### GovernanceFile

```python
class GovernanceFile
```

**Decorators:** `dataclass`

Governance file token budget configuration.


**Attributes:**

- `name`: str
- `path`: Path
- `max_tokens`: int
- `current_tokens`: int
- `char_count`: int
- `line_count`: int


**Methods:**

  #### `is_compliant`

  *Decorators:* `property`

  ```python
  is_compliant(self) -> bool
  ```

  Check if file is within token budget.

  **Parameters:**

  - `self`


  **Returns:** bool


  #### `overage_tokens`

  *Decorators:* `property`

  ```python
  overage_tokens(self) -> int
  ```

  Tokens over budget (negative if under).

  **Parameters:**

  - `self`


  **Returns:** int


  #### `overage_percent`

  *Decorators:* `property`

  ```python
  overage_percent(self) -> float
  ```

  Percentage over budget.

  **Parameters:**

  - `self`


  **Returns:** float


  #### `reduction_needed`

  *Decorators:* `property`

  ```python
  reduction_needed(self) -> float
  ```

  Percentage reduction needed to reach budget.

  **Parameters:**

  - `self`


  **Returns:** float



---

### TokenValidationReport

```python
class TokenValidationReport
```

**Decorators:** `dataclass`

Complete token validation report for all governance files.


**Attributes:**

- `timestamp`: datetime
- `files`: List[GovernanceFile]
- `execution_time`: float


**Methods:**

  #### `total_current_tokens`

  *Decorators:* `property`

  ```python
  total_current_tokens(self) -> int
  ```

  Total current token usage across all files.

  **Parameters:**

  - `self`


  **Returns:** int


  #### `total_budget_tokens`

  *Decorators:* `property`

  ```python
  total_budget_tokens(self) -> int
  ```

  Total token budget across all files.

  **Parameters:**

  - `self`


  **Returns:** int


  #### `total_overage_tokens`

  *Decorators:* `property`

  ```python
  total_overage_tokens(self) -> int
  ```

  Total tokens over budget.

  **Parameters:**

  - `self`


  **Returns:** int


  #### `is_compliant`

  *Decorators:* `property`

  ```python
  is_compliant(self) -> bool
  ```

  True if all files are within budget.

  **Parameters:**

  - `self`


  **Returns:** bool


  #### `compliant_count`

  *Decorators:* `property`

  ```python
  compliant_count(self) -> int
  ```

  Number of files within budget.

  **Parameters:**

  - `self`


  **Returns:** int


  #### `total_count`

  *Decorators:* `property`

  ```python
  total_count(self) -> int
  ```

  Total number of files checked.

  **Parameters:**

  - `self`


  **Returns:** int


  #### `format_console`

  ```python
  format_console(self) -> str
  ```

  Format report for console output.

  **Parameters:**

  - `self`


  **Returns:** str



---

### GovernanceTokenValidator

```python
class GovernanceTokenValidator
```

Validates token budgets for CORTEX governance files.


**Methods:**

  #### `estimate_tokens`

  ```python
  estimate_tokens(self, text: str) -> int
  ```

  Estimate token count from character count.

Uses simple heuristic: ~4 characters per token
This is consistent with GPT tokenization for English text.

Args:
    text: Text to estimate tokens for
    
Returns:
    Estimated token count

  **Parameters:**

  - `self`
  - `text` (str): Text to estimate tokens for


  **Returns:** int
    Estimated token count


  #### `count_lines`

  ```python
  count_lines(self, text: str) -> int
  ```

  Count non-empty lines in text.

  **Parameters:**

  - `self`
  - `text` (str)


  **Returns:** int


  #### `validate_file`

  ```python
  validate_file(self, name: str, config: Dict[str, Any]) -> GovernanceFile
  ```

  Validate a single governance file against its token budget.

Args:
    name: File name (e.g., "CORTEX.prompt.md")
    config: File configuration with path, max_tokens, char_to_token_ratio
    
Returns:
    GovernanceFile with validation results

  **Parameters:**

  - `self`
  - `name` (str): File name (e.g., "CORTEX.prompt.md")
  - `config` (Dict[str, Any]): File configuration with path, max_tokens, char_to_token_ratio


  **Returns:** GovernanceFile
    GovernanceFile with validation results


  #### `validate_all`

  ```python
  validate_all(self) -> TokenValidationReport
  ```

  Validate all governance files against token budgets.

Returns:
    TokenValidationReport with results for all files

  **Parameters:**

  - `self`


  **Returns:** TokenValidationReport
    TokenValidationReport with results for all files



---

## Functions

### safe_print

```python
safe_print(message: str) -> None
```

Print with Unicode fallback for Windows console encoding issues.


**Parameters:**

- `message` (str)


**Returns:** None


---

### validate_token_budgets

```python
validate_token_budgets(silent: bool) -> Dict[str, Any]
```

Validate all governance files against token budgets.

This is the primary entry point for 'align governance-tokens validate'.

Args:
    silent: If True, skip console output (useful for programmatic calls)

Returns:
    Dict with:
        - success (bool): True if all files within budget
        - message (str): Summary message
        - report_text (str): Full console output
        - report_data (dict): Structured validation data


**Parameters:**

- `silent` (bool) = `False`: If True, skip console output (useful for programmatic calls)


**Returns:** Dict[str, Any]
  Dict with: - success (bool): True if all files within budget - message (str): Summary message - report_text (str): Full console output - report_data (dict): Structured validation data


---

### main

```python
main()
```

CLI entry point for direct execution.


---
