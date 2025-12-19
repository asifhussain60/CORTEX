# domain_classifier

Domain Classifier - Adaptive analysis depth based on domain criticality.

Purpose:
    Classifies code domains into CRITICAL, STANDARD, or SIMPLE tiers to adapt
    analysis depth: security/auth/financial → deep AST, UI → high-level, docs → surface.

Features:
    - 3-tier domain classification: CRITICAL, STANDARD, SIMPLE
    - Pattern-based domain detection (security, compliance, business logic)
    - Analysis depth routing: CRITICAL→deep AST, STANDARD→moderate, SIMPLE→light
    - Integration with ComplexityAnalyzer for risk scoring
    - OWASP Top 10 pattern library for security domain detection

Author: Asif Hussain
Date: December 2024
Version: 1.0.0
Phase: 02 of CORTEX Evolution v3.9


## Table of Contents

### Classes
- [DomainCriticality](#domaincriticality)
- [DomainClassification](#domainclassification)
- [DomainClassifier](#domainclassifier)


## Overview

- **Classes:** 3
- **Functions:** 0
- **Dependencies:** dataclasses, enum, logging, pathlib, re, typing


## Classes

### DomainCriticality

```python
class DomainCriticality(Enum)
```

Domain criticality tiers for analysis depth routing



---

### DomainClassification

```python
class DomainClassification
```

**Decorators:** `dataclass`

Result of domain classification


**Attributes:**

- `criticality`: DomainCriticality
- `domains`: List[str]
- `confidence`: float
- `analysis_depth`: str
- `rationale`: List[str]
- `security_patterns`: List[str]


**Methods:**

  #### `to_dict`

  ```python
  to_dict(self) -> Dict
  ```

  Convert to dictionary for serialization

  **Parameters:**

  - `self`


  **Returns:** Dict



---

### DomainClassifier

```python
class DomainClassifier
```

Classifies code domains for adaptive analysis depth.

Domain Tiers:
    CRITICAL (deep AST analysis):
        - Security: authentication, authorization, encryption, input validation
        - Compliance: PII handling, GDPR, HIPAA, PCI, audit trails
        - Financial: payment processing, calculations, rounding, transactions
        - Business Logic: core workflows, state machines, business rules
    
    STANDARD (high-level analysis):
        - UI Components: React/Vue/Angular components, templates
        - Utilities: helpers, formatters, converters
        - API Clients: HTTP clients, SDK wrappers
        - Middleware: logging, caching, error handling
    
    SIMPLE (surface-level analysis):
        - Documentation: READMEs, guides, comments
        - Configuration: JSON/YAML configs, env files
        - Scaffolding: boilerplate, templates
        - Test fixtures: mock data, test constants

Security Pattern Library (OWASP Top 10):
    - A01:2021 - Broken Access Control
    - A02:2021 - Cryptographic Failures
    - A03:2021 - Injection (SQL, XSS, Command)
    - A04:2021 - Insecure Design
    - A05:2021 - Security Misconfiguration
    - A06:2021 - Vulnerable Components
    - A07:2021 - Authentication Failures
    - A08:2021 - Software/Data Integrity
    - A09:2021 - Security Logging Failures
    - A10:2021 - Server-Side Request Forgery

Integration:
    - Called by ComplexityAnalyzer to boost risk scores
    - Used by AST Engine to determine analysis depth
    - Influences router tier classification (CRITICAL → Tier 4)


**Methods:**

  #### `classify`

  ```python
  classify(self, user_request: str, file_paths: Optional[List[str]], codebase_context: Optional[Dict]) -> DomainClassification
  ```

  Classify domain criticality for adaptive analysis depth.

Args:
    user_request: User's feature request or task description
    file_paths: Optional list of file paths being analyzed
    codebase_context: Optional codebase analysis from AST

Returns:
    DomainClassification with criticality tier and analysis depth

Example:
    >>> classifier = DomainClassifier()
    >>> result = classifier.classify("Add JWT authentication to API")
    >>> print(result.criticality)  # CRITICAL
    >>> print(result.analysis_depth)  # 'deep'
    >>> print(result.security_patterns)  # ['A07_authentication_failures']

  **Parameters:**

  - `self`
  - `user_request` (str): User's feature request or task description
  - `file_paths` (Optional[List[str]]) = `None`: Optional list of file paths being analyzed
  - `codebase_context` (Optional[Dict]) = `None`: Optional codebase analysis from AST


  **Returns:** DomainClassification
    DomainClassification with criticality tier and analysis depth


  #### `get_analysis_depth_config`

  ```python
  get_analysis_depth_config(self, classification: DomainClassification) -> Dict[str, any]
  ```

  Get analysis configuration based on domain classification.

Returns dict with:
    - ast_depth: 'deep', 'moderate', 'light'
    - enable_security_scan: bool
    - enable_compliance_check: bool
    - enable_business_logic_analysis: bool

  **Parameters:**

  - `self`
  - `classification` (DomainClassification)


  **Returns:** Dict[str, any]



---
