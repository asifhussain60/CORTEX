# legacy_spec_generator

Legacy API Specification Generator - CORTEX Lens Capability

Analyzes legacy C# code and generates:
- PM/BA-readable specifications
- OpenAPI 3.0 specifications
- Cross-check test fixtures

Part of CORTEX Lens for comprehensive legacy API reverse engineering.

Author: CORTEX
Version: 3.0.0 (OpenAPI Generation)
Date: December 15, 2025


## Table of Contents

### Classes
- [MethodInfo](#methodinfo)
- [BusinessRule](#businessrule)
- [ValidationRule](#validationrule)
- [DatabaseOperation](#databaseoperation)
- [OpenAPIEndpoint](#openapiendpoint)
- [PropertySchema](#propertyschema)
- [LegacySpecGenerator](#legacyspecgenerator)

### Functions
- [main](#main)


## Overview

- **Classes:** 7
- **Functions:** 1
- **Dependencies:** core, dataclasses, datetime, importlib, json, pathlib, re, sys, typing, yaml


## Classes

### MethodInfo

```python
class MethodInfo
```

**Decorators:** `dataclass`

Represents a method extracted from legacy code.


**Attributes:**

- `name`: str
- `return_type`: str
- `parameters`: List[str]
- `line_start`: int
- `line_end`: int
- `body`: str



---

### BusinessRule

```python
class BusinessRule
```

**Decorators:** `dataclass`

Represents a business rule extracted from code.


**Attributes:**

- `rule_id`: int
- `name`: str
- `description`: str
- `condition`: str
- `action`: str
- `line_number`: int
- `layer`: str



---

### ValidationRule

```python
class ValidationRule
```

**Decorators:** `dataclass`

Represents a validation rule.


**Attributes:**

- `field`: str
- `rule_type`: str
- `message`: str
- `line_number`: int



---

### DatabaseOperation

```python
class DatabaseOperation
```

**Decorators:** `dataclass`

Represents a database operation.


**Attributes:**

- `operation_type`: str
- `table`: str
- `line_number`: int
- `purpose`: str



---

### OpenAPIEndpoint

```python
class OpenAPIEndpoint
```

**Decorators:** `dataclass`

Represents an inferred REST endpoint.


**Attributes:**

- `path`: str
- `method`: str
- `operation_id`: str
- `summary`: str
- `request_schema`: Optional[Dict[str, Any]]
- `response_schema`: Optional[Dict[str, Any]]
- `parameters`: List[Dict[str, Any]]
- `errors`: List[Dict[str, Any]]



---

### PropertySchema

```python
class PropertySchema
```

**Decorators:** `dataclass`

Represents a property schema for OpenAPI.


**Attributes:**

- `name`: str
- `type`: str
- `required`: bool
- `validation`: Optional[Dict[str, Any]]
- `description`: str



---

### LegacySpecGenerator

```python
class LegacySpecGenerator
```

Generates specifications from legacy C# code - CORTEX Lens Capability.


**Methods:**

  #### `analyze`

  ```python
  analyze(self)
  ```

  Perform complete AST-like analysis of legacy code.

  **Parameters:**

  - `self`


  #### `generate_openapi_spec`

  ```python
  generate_openapi_spec(self) -> str
  ```

  CORTEX Lens: Generate OpenAPI 3.0 specification in YAML format.
Returns formatted YAML string ready for file output.

  **Parameters:**

  - `self`


  **Returns:** str


  #### `generate_openapi_json`

  ```python
  generate_openapi_json(self) -> str
  ```

  CORTEX Lens: Generate OpenAPI 3.0 specification in JSON format.
Returns formatted JSON string ready for file output.

  **Parameters:**

  - `self`


  **Returns:** str


  #### `generate_cross_check_fixtures`

  ```python
  generate_cross_check_fixtures(self) -> Dict[str, Any]
  ```

  CORTEX Lens: Generate test fixtures for cross-checking legacy vs modern implementation.
Returns test cases with inputs and expected validation behavior.

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]


  #### `generate_business_spec`

  ```python
  generate_business_spec(self) -> str
  ```

  Generate business specification document.

  **Parameters:**

  - `self`


  **Returns:** str


  #### `generate_test_scenarios`

  ```python
  generate_test_scenarios(self) -> str
  ```

  Generate test scenarios document organized by priority (P0, P1, P2).

P0: Critical path - Core business logic that must work
P1: Happy path variations - Normal usage scenarios with different inputs
P2: Edge cases - Boundary conditions, error handling, unusual scenarios

  **Parameters:**

  - `self`


  **Returns:** str


  #### `generate_traceability_matrix`

  ```python
  generate_traceability_matrix(self) -> str
  ```

  Generate traceability matrix.

  **Parameters:**

  - `self`


  **Returns:** str


  #### `generate_flow_diagram`

  ```python
  generate_flow_diagram(self) -> str
  ```

  Public wrapper for flowchart generation.

  **Parameters:**

  - `self`


  **Returns:** str


  #### `generate_sequence_diagram`

  ```python
  generate_sequence_diagram(self) -> str
  ```

  Public wrapper for sequence diagram generation.

  **Parameters:**

  - `self`


  **Returns:** str


  #### `generate_dependency_diagram`

  ```python
  generate_dependency_diagram(self) -> str
  ```

  Public wrapper for dependency diagram generation.

  **Parameters:**

  - `self`


  **Returns:** str


  #### `generate_all`

  ```python
  generate_all(self)
  ```

  Generate all specification documents.

  **Parameters:**

  - `self`



---

## Functions

### main

```python
main()
```

Example usage.


---
