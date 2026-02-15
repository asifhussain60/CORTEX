# Testing & Quality Assurance

> **Summary:** Test patterns, coverage requirements, and continuous quality validation  
> **Authority:** cortex/testing/ + tests/ | **Last Updated:** 2026-01-22

---

## Overview

Comprehensive testing strategy with 7000+ tests covering unit, integration, and end-to-end scenarios.

**Test Categories:**
- Unit tests (cortex/*/test_*.py)
- Integration tests (tests/unit/*/test_integration_*.py)
- End-to-end tests (tests/e2e/)
- Acceptance criteria tests (tests/ac_*/test_*.py)
- Performance tests (scripts/)

---

## Test Architecture

```mermaid
graph TD
  A["Source Code"] -->|unit tests| B["Unit Test<br/>Coverage"]
  B -->|integration tests| C["Module Integration<br/>Coverage"]
  C -->|e2e tests| D["End-to-End<br/>Coverage"]
  D -->|acceptance tests| E["Acceptance Criteria<br/>Coverage"]
  
  B & C & D & E -->|aggregate| F["Test Report<br/>pytest"]
  F -->|CI/CD| G["Build Pipeline"]
  
  style F fill:#2196f3,stroke:#1565c0,color:#fff,stroke-width:2px
```

---

## See Also

- [Test Execution Strategy](../docs/TEST-EXECUTION-STRATEGY.md)
- [Source: tests/](../../../tests/)
- [Source: cortex/testing/](../../../cortex/testing/)

---

**Author:** CORTEX Documentation Engine  
**Generated:** 2026-01-22
