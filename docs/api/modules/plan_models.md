# plan_models

## Table of Contents

### Classes
- [Meta](#meta)
- [Artifacts](#artifacts)
- [PlanLedgerEntry](#planledgerentry)
- [PlanLedger](#planledger)
- [FeaturePlan](#featureplan)
- [ArchitecturePlan](#architectureplan)
- [RefactorPlan](#refactorplan)
- [ActivePlans](#activeplans)
- [Decision](#decision)
- [DecisionGraph](#decisiongraph)
- [ReasoningChainEntry](#reasoningchainentry)
- [RequiredTests](#requiredtests)
- [TestAlignmentItem](#testalignmentitem)
- [TestAlignment](#testalignment)
- [PlanForecast](#planforecast)
- [MetricsForecast](#metricsforecast)

### Functions


## Overview

- **Classes:** 16
- **Functions:** 1
- **Dependencies:** __future__, dataclasses, datetime, typing


## Classes

### Meta

```python
class Meta
```

**Decorators:** `dataclass`

**Attributes:**

- `schema_version`: str
- `last_updated`: datetime
- `generator_version`: Optional[str]
- `validation_status`: Optional[Literal['unknown', 'valid', 'invalid']]



---

### Artifacts

```python
class Artifacts
```

**Decorators:** `dataclass`

**Attributes:**

- `tasks`: List[str]
- `risks`: List[str]
- `decisions`: List[str]
- `constraints`: List[str]
- `metrics_estimates`: Dict[str, Any]



---

### PlanLedgerEntry

```python
class PlanLedgerEntry
```

**Decorators:** `dataclass`

**Attributes:**

- `id`: str
- `timestamp`: datetime
- `actor`: str
- `plan_type`: Literal['feature', 'arch', 'refactor']
- `status`: Literal['draft', 'approved', 'superseded']
- `supersedes`: Optional[str]
- `reasoning_refs`: List[str]
- `artifacts`: Artifacts
- `confidence`: float


**Methods:**


---

### PlanLedger

```python
class PlanLedger
```

**Decorators:** `dataclass`

**Attributes:**

- `meta`: Meta
- `entries`: List[PlanLedgerEntry]


**Methods:**


---

### FeaturePlan

```python
class FeaturePlan
```

**Decorators:** `dataclass`

**Attributes:**

- `id`: str
- `summary`: str
- `current_revision`: str
- `linked_operation`: Optional[str]
- `modules`: List[str]
- `acceptance_criteria`: List[str]
- `test_matrix_ref`: Optional[str]



---

### ArchitecturePlan

```python
class ArchitecturePlan
```

**Decorators:** `dataclass`

**Attributes:**

- `id`: str
- `context`: str
- `boundaries`: List[str]
- `patterns`: List[str]
- `tradeoffs`: Optional[str]
- `approved_revision`: Optional[str]



---

### RefactorPlan

```python
class RefactorPlan
```

**Decorators:** `dataclass`

**Attributes:**

- `id`: str
- `target_module`: str
- `smells_detected`: List[str]
- `objectives`: List[str]
- `impact_scope`: Optional[str]
- `rollback_strategy`: Optional[str]



---

### ActivePlans

```python
class ActivePlans
```

**Decorators:** `dataclass`

**Attributes:**

- `meta`: Meta
- `feature_plans`: List[FeaturePlan]
- `architecture_plans`: List[ArchitecturePlan]
- `refactor_plans`: List[RefactorPlan]



---

### Decision

```python
class Decision
```

**Decorators:** `dataclass`

**Attributes:**

- `id`: str
- `question`: str
- `options`: List[str]
- `chosen_option`: str
- `justification`: str
- `supporting_evidence`: List[str]
- `risk_profile`: Optional[str]
- `revisit_trigger`: Optional[str]


**Methods:**


---

### DecisionGraph

```python
class DecisionGraph
```

**Decorators:** `dataclass`

**Attributes:**

- `meta`: Meta
- `decisions`: List[Decision]



---

### ReasoningChainEntry

```python
class ReasoningChainEntry
```

**Decorators:** `dataclass`

**Attributes:**

- `plan_id`: str
- `step_index`: int
- `model_version`: str
- `input_context_hash`: str
- `output_summary`: str
- `tokens_in`: int
- `tokens_out`: int


**Methods:**


---

### RequiredTests

```python
class RequiredTests
```

**Decorators:** `dataclass`

**Attributes:**

- `unit`: List[str]
- `integration`: List[str]
- `e2e`: List[str]
- `visual`: List[str]
- `performance`: List[str]



---

### TestAlignmentItem

```python
class TestAlignmentItem
```

**Decorators:** `dataclass`

**Attributes:**

- `plan_id`: str
- `required_tests`: RequiredTests
- `coverage_targets`: Dict[str, float]
- `enforcement_status`: Literal['none', 'warn', 'block']



---

### TestAlignment

```python
class TestAlignment
```

**Decorators:** `dataclass`

**Attributes:**

- `meta`: Meta
- `plans`: List[TestAlignmentItem]



---

### PlanForecast

```python
class PlanForecast
```

**Decorators:** `dataclass`

**Attributes:**

- `plan_id`: str
- `predicted_complexity`: float
- `uncertainty_band`: Optional[List[float]]
- `historical_similarity_refs`: List[str]
- `variance_from_actual`: Optional[float]


**Methods:**


---

### MetricsForecast

```python
class MetricsForecast
```

**Decorators:** `dataclass`

**Attributes:**

- `meta`: Meta
- `forecasts`: List[PlanForecast]



---

## Functions
